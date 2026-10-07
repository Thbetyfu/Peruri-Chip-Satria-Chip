// SPDX-License-Identifier: LicenseRef-Proprietary
// SPDX-FileCopyrightText: Copyright (c) 2026 Tim Paket Kulit 12k, Telkom University. All rights reserved.
// audit_log.v - log keputusan tamper-evident (hash-chain) di memori on-chip.
//
// Setiap entri: {seq, verdict, reasons, token}. token = HMAC(K, ... || prev_token)
// dihitung di screener_top, sehingga entri membentuk rantai: mengubah,
// menghapus, menyisipkan, atau menukar urutan entri memutus rantai.
// Host HANYA memiliki port baca; tidak ada jalur tulis dari bus host.
// Buffer cincin 2^DEPTH_BITS entri; entri lama ditimpa tetapi seq & head
// tetap monoton sehingga ekspor periodik dapat diverifikasi berkesinambungan.
// SystemVerilog (IEEE 1800-2017) — padanan fungsional rtl/audit_log.v; diverifikasi
// dengan testbench & golden model yang sama (lihat docs/verifikasi_sv.md).

`default_nettype none

module audit_log #(
    parameter DEPTH_BITS = 8
) (
    input  logic                  clk,
    input  logic                  rst_n,
    input  logic                  append,
    input  logic [7:0]            verdict,
    input  logic [15:0]           reasons,
    input  logic [255:0]          token,
    output logic  [31:0]           count,     // = seq entri berikutnya
    output logic  [255:0]          head,      // token terakhir (kepala rantai)
    input  logic [DEPTH_BITS-1:0] rd_idx,
    output logic  [31:0]           rd_seq,
    output logic  [31:0]           rd_meta,   // {8'h0, verdict, reasons}
    output logic  [255:0]          rd_token
);
  localparam D = (1 << DEPTH_BITS);
  logic [319:0] mem [0:D-1];
  logic [319:0] rd;

  always_ff @(posedge clk) begin
    if (append) mem[count[DEPTH_BITS-1:0]] <= {count, 8'h00, verdict, reasons, token};
    rd <= mem[rd_idx];
  end

  assign rd_seq   = rd[319:288];
  assign rd_meta  = rd[287:256];
  assign rd_token = rd[255:0];

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      count <= 32'd0; head <= 256'd0;
    end else if (append) begin
      count <= count + 32'd1; head <= token;
    end
  end
endmodule

`default_nettype wire
