// SPDX-License-Identifier: LicenseRef-Proprietary
// SPDX-FileCopyrightText: Copyright (c) 2026 Tim Paket Kulit 12k, Telkom University. All rights reserved.
// rule_engine.v - Deterministic Rule Engine: anti-replay per klien + velocity
//                 Count-Min Sketch (fail-safe) + ambang nominal
//
// Hanya dijalankan SETELAH Integrity Gate lolos, sehingga rekaman palsu tidak
// pernah dapat mengubah state. Seluruh field (klien, nonce, akun, nominal,
// timestamp) berasal dari rekaman yang sudah terautentikasi HMAC.
//
// Aturan:
//   CLIENT      : id klien di luar 0..15 -> tolak (fail-closed). Satu chip
//                 melayani maks. 16 institusi; slot = id, sehingga tidak ada
//                 tabrakan, penggusuran, atau perebutan slot antarklien.
//   REPLAY      : nonce = nomor urut per klien. Jendela geser 64 nonce
//                 (gaya IPsec): nonce <= hi-64, atau nonce yang sudah terlihat
//                 di bitmap -> tolak. Transaksi yang datang tidak berurutan
//                 tetap diterima selama masih di dalam jendela.
//   VELOCITY    : Count-Min Sketch 4 baris x 2^IDX_BITS penghitung. Indeks tiap
//                 baris = potongan H_Kidx(akun) (dihitung screener_top dengan
//                 kunci rahasia chip). Tiap penghitung menyimpan {epoch, cur,
//                 prev}; perkiraan = cur + prev, lalu MINIMUM antar baris.
//                 Epoch = timestamp >> cfg_win_shift. Perkiraan tidak pernah
//                 lebih kecil dari jumlah transaksi akun dalam jendela
//                 2^cfg_win_shift detik terakhir: tabrakan hanya menaikkan
//                 perkiraan (FLAG berlebih), tidak pernah meloloskan.
//   OVER_AMOUNT : nominal > cfg_amount_limit
//
// Setelah reset, seluruh sketch dihapus oleh penyapu internal (2^IDX_BITS
// cycle, 82 us @ 50 MHz); selama itu `ready` = 0 dan permintaan ditahan.
// Latensi: 4 cycle (pipeline: latch, tahap A, tahap B, keputusan + tulis).
// SystemVerilog (IEEE 1800-2017) — padanan fungsional rtl/rule_engine.v; diverifikasi
// dengan testbench & golden model yang sama (lihat docs/verifikasi_sv.md).

`default_nettype none

module rule_engine #(
    parameter IDX_BITS = 12
) (
    input  logic                  clk,
    input  logic                  rst_n,
    input  logic                  start,
    input  logic [15:0]           client,
    input  logic [63:0]           nonce,
    input  logic [63:0]           amount,
    input  logic [31:0]           tstamp,
    input  logic [4*IDX_BITS-1:0] row_idx,      // {idx0, idx1, idx2, idx3}
    input  logic [4:0]            cfg_win_shift,
    input  logic [15:0]           cfg_vel_limit,
    input  logic [63:0]           cfg_amount_limit,
    output logic                   done,
    output logic                   replay,
    output logic                   client_rej,
    output logic                   velocity,
    output logic                   over_amount,
    output logic                  ready
);
  localparam N = (1 << IDX_BITS);

  // ------------------------------------------------ Count-Min Sketch (M10K)
  // entri 48 bit = {epoch[15:0], cur[15:0], prev[15:0]}
  logic [47:0] sk0 [0:N-1];
  logic [47:0] sk1 [0:N-1];
  logic [47:0] sk2 [0:N-1];
  logic [47:0] sk3 [0:N-1];

  // penyapu: hapus seluruh sketch setelah reset
  logic                clr;
  logic [IDX_BITS-1:0] clr_a;
  assign ready = ~clr;

  wire [IDX_BITS-1:0] i0 = row_idx[4*IDX_BITS-1 -: IDX_BITS];
  wire [IDX_BITS-1:0] i1 = row_idx[3*IDX_BITS-1 -: IDX_BITS];
  wire [IDX_BITS-1:0] i2 = row_idx[2*IDX_BITS-1 -: IDX_BITS];
  wire [IDX_BITS-1:0] i3 = row_idx[1*IDX_BITS-1 -: IDX_BITS];

  logic [47:0] r0, r1, r2, r3;           // port baca sinkron
  logic        we;
  logic [IDX_BITS-1:0] wa0, wa1, wa2, wa3;
  logic [47:0] wd0, wd1, wd2, wd3;

  wire                p_we = we | clr;
  wire [IDX_BITS-1:0] p0 = clr ? clr_a : wa0;
  wire [IDX_BITS-1:0] p1 = clr ? clr_a : wa1;
  wire [IDX_BITS-1:0] p2 = clr ? clr_a : wa2;
  wire [IDX_BITS-1:0] p3 = clr ? clr_a : wa3;

  always_ff @(posedge clk) begin
    if (p_we) begin
      sk0[p0] <= clr ? 48'd0 : wd0; sk1[p1] <= clr ? 48'd0 : wd1;
      sk2[p2] <= clr ? 48'd0 : wd2; sk3[p3] <= clr ? 48'd0 : wd3;
    end
    r0 <= sk0[i0]; r1 <= sk1[i1]; r2 <= sk2[i2]; r3 <= sk3[i3];
  end

  // ------------------------------------------------ tabel klien (register)
  logic [15:0] cl_valid;
  logic [63:0] cl_hi [0:15];
  logic [63:0] cl_bm [0:15];

  wire [3:0]  cs      = client[3:0];

  // ------------------------------------------------ pipeline 4 fase
  // ph0: start -> latch epoch & entri klien (RAM sketch dibaca pada edge ini)
  // ph1: tahap A  - pembaruan tiap baris sketch; perbandingan nonce 64-bit
  // ph2: tahap B  - minimum antar baris; keputusan replay; bitmap baru
  // ph3: keputusan akhir + tulis RAM/tabel klien, done
  logic [15:0] ep_r, epm1_r;
  logic        e_valid;
  logic [63:0] e_hi, e_bm;
  logic        c_rej_r;

  function automatic logic [64:0] upd;                 // {est[16:0], entri baru[47:0]}
    input [47:0] e; input [15:0] ep_n; input [15:0] ep_p;
    logic [15:0] cur, prv, ncur;
    begin
      cur  = (e[47:32] == ep_n) ? e[31:16] : 16'd0;
      prv  = (e[47:32] == ep_n) ? e[15:0]  : ((e[47:32] == ep_p) ? e[31:16] : 16'd0);
      ncur = (cur == 16'hFFFF) ? cur : cur + 16'd1;
      upd  = {{1'b0, ncur} + {1'b0, prv}, ep_n, ncur, prv};
    end
  endfunction

  // tahap A (kombinasional pada ph1)
  wire [31:0] ep32  = tstamp >> cfg_win_shift;
  wire [64:0] u0 = upd(r0, ep_r, epm1_r);
  wire [64:0] u1 = upd(r1, ep_r, epm1_r);
  wire [64:0] u2 = upd(r2, ep_r, epm1_r);
  wire [64:0] u3 = upd(r3, ep_r, epm1_r);
  wire        newer_c = !e_valid || (nonce > e_hi);
  wire [63:0] d_up    = nonce - e_hi;
  wire [63:0] off     = e_hi - nonce;

  logic [64:0] ua0, ua1, ua2, ua3;
  logic        newer_a, dge_a, oge_a;
  logic [5:0]  d6_a, o6_a;

  // tahap B (kombinasional pada ph2)
  wire [16:0] m01 = (ua0[64:48] < ua1[64:48]) ? ua0[64:48] : ua1[64:48];
  wire [16:0] m23 = (ua2[64:48] < ua3[64:48]) ? ua2[64:48] : ua3[64:48];
  wire [16:0] est = (m01 < m23) ? m01 : m23;
  wire        too_old = !newer_a && oge_a;
  wire        seen    = !newer_a && !oge_a && e_bm[o6_a];
  wire        is_rep  = !c_rej_r && (too_old || seen);
  wire [63:0] new_bm  = !e_valid ? 64'd1 :
                        newer_a  ? (dge_a ? 64'd1 : ((e_bm << d6_a) | 64'd1)) :
                                   (e_bm | (64'd1 << o6_a));

  logic [16:0] est_b;
  logic        rep_b, ok_b;
  logic [63:0] hi_b, bm_b;

  logic [1:0] ph;
  logic       pend;
  int j;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      ph <= 2'd0; done <= 1'b0; pend <= 1'b0;
      clr <= 1'b1; clr_a <= {IDX_BITS{1'b0}};
      replay <= 1'b0; client_rej <= 1'b0; velocity <= 1'b0; over_amount <= 1'b0;
      we <= 1'b0;
      wa0 <= {IDX_BITS{1'b0}}; wa1 <= {IDX_BITS{1'b0}};
      wa2 <= {IDX_BITS{1'b0}}; wa3 <= {IDX_BITS{1'b0}};
      wd0 <= 48'd0; wd1 <= 48'd0; wd2 <= 48'd0; wd3 <= 48'd0;
      ep_r <= 16'd0; epm1_r <= 16'd0; e_valid <= 1'b0; e_hi <= 64'd0; e_bm <= 64'd0;
      c_rej_r <= 1'b0;
      ua0 <= 65'd0; ua1 <= 65'd0; ua2 <= 65'd0; ua3 <= 65'd0;
      newer_a <= 1'b0; dge_a <= 1'b0; oge_a <= 1'b0; d6_a <= 6'd0; o6_a <= 6'd0;
      est_b <= 17'd0; rep_b <= 1'b0; ok_b <= 1'b0; hi_b <= 64'd0; bm_b <= 64'd0;
      cl_valid <= 16'd0;
      for (j = 0; j < 16; j = j + 1) begin
        cl_hi[j] <= 64'd0; cl_bm[j] <= 64'd0;
      end
    end else begin
      done <= 1'b0;
      we   <= 1'b0;
      if (clr) begin
        clr_a <= clr_a + 1'b1;
        if (&clr_a) clr <= 1'b0;
      end
      if (start) pend <= 1'b1;
      case (ph)
        2'd0: if ((start || pend) && !clr) begin   // RAM dibaca pada edge yang sama
          ep_r    <= ep32[15:0];
          epm1_r  <= ep32[15:0] - 16'd1;
          e_valid <= cl_valid[cs];
          e_hi    <= cl_hi[cs];
          e_bm    <= cl_bm[cs];
          c_rej_r <= |client[15:4];
          ph <= 2'd1; pend <= 1'b0;
        end
        2'd1: begin                               // tahap A
          ua0 <= u0; ua1 <= u1; ua2 <= u2; ua3 <= u3;
          newer_a <= newer_c;
          dge_a   <= |d_up[63:6];
          oge_a   <= |off[63:6];
          d6_a    <= d_up[5:0];
          o6_a    <= off[5:0];
          ph <= 2'd2;
        end
        2'd2: begin                               // tahap B
          est_b <= est;
          rep_b <= is_rep;
          ok_b  <= !c_rej_r && !is_rep;
          hi_b  <= newer_a ? nonce : e_hi;
          bm_b  <= new_bm;
          ph <= 2'd3;
        end
        default: begin                            // keputusan + tulis
          client_rej  <= c_rej_r;
          replay      <= rep_b;
          velocity    <= ok_b && (est_b > {1'b0, cfg_vel_limit});
          over_amount <= ok_b && (amount > cfg_amount_limit);
          if (ok_b) begin
            cl_valid[cs] <= 1'b1;
            cl_hi[cs]    <= hi_b;
            cl_bm[cs]    <= bm_b;
            we  <= 1'b1;
            wa0 <= i0; wa1 <= i1; wa2 <= i2; wa3 <= i3;
            wd0 <= ua0[47:0]; wd1 <= ua1[47:0]; wd2 <= ua2[47:0]; wd3 <= ua3[47:0];
          end
          done <= 1'b1;
          ph   <= 2'd0;
        end
      endcase
    end
  end
endmodule

`default_nettype wire
