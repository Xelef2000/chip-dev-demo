module breathing_led #(
    parameter CLK_FREQ = 1_000_000  // default 1 MHz clock
)(
    input  wire clk,
    input  wire rst_n,
    input  wire enable,
    output wire led_out
);
  localparam PWM_BITS = 8;       // PWM resolution (8-bit = 256 steps)
  localparam PARAM1_SPEED = CLK_FREQ / 512; // adjust for visible speed
  
  reg [PWM_BITS-1:0] pwm_counter = 0;
  reg [PWM_BITS-1:0] brightness = 0;
  reg                direction = 1'b1; // 1 = increasing, 0 = decreasing
  reg [$clog2(PARAM1_SPEED):0] div_counter = 0;
  
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      div_counter <= 0;
      brightness  <= 0;
      direction   <= 1'b1;
    end else if (enable) begin
      if (div_counter == PARAM1_SPEED - 1) begin
        div_counter <= 0;
        
        if (direction) begin
          if (brightness == {PWM_BITS{1'b1}}) begin
            direction <= 1'b0;
          end else begin
            brightness <= brightness + 1;
          end
        end else begin
          if (brightness == 0) begin
            direction <= 1'b1;
          end else begin
            brightness <= brightness - 1;
          end
        end
        
      end else begin
        div_counter <= div_counter + 1;
      end
    end else begin
      brightness <= 0;
      div_counter <= 0;
      direction <= 1'b1;
    end
  end
  
  // Simple PWM generator
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
      pwm_counter <= 0;
    else
      pwm_counter <= pwm_counter + 1;
  end
  
  assign led_out = enable && (pwm_counter < brightness);
endmodule