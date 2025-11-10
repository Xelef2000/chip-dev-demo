/*
 * Copyright (c) 2025 Felix Niederer
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none
`include "ips/breathing_led.v"


module tt_um_example (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // Result can be up to 5 bits (since 4-bit + 4-bit = up to 8 + 8 = 16)
  wire [4:0] result;

  // Add lower 4 bits and upper 4 bits of ui_in
  assign result = ui_in[3:0] + ui_in[7:4];

  // Assign the lower 4 bits of result to the lower 4 bits of uo_out
  assign uo_out[3:0] = result[3:0];

  wire led_breath;

  // Instantiate breathing LED, enabled when overflow bit is high

  breathing_led #(
      .CLK_FREQ(1_000_000)
  ) led_inst (
      .clk(clk),
      .rst_n(rst_n),
      .enable(result[4]),
      .led_out(led_breath)
  );

  assign uo_out[4] = led_breath;

  // Unused upper bits of uo_out are set to 0
  assign uo_out[7:5] = 3'b000;

  // We don't use IO pins
  assign uio_out = 0;
  assign uio_oe  = 0;

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, clk, rst_n, 1'b0};

endmodule
