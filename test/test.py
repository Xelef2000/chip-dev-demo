import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

async def reset_dut(dut, cycles=5):
    dut.rst_n.value = 0
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    await ClockCycles(dut.clk, cycles)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)


@cocotb.test()
async def test_adder_lower_bits(dut):
    """Check that uo_out[3:0] = lower 4 bits + upper 4 bits."""
    clock = Clock(dut.clk, 1, units="us")
    cocotb.start_soon(clock.start())

    await reset_dut(dut)

    for upper in range(16):
        for lower in range(16):
            dut.ui_in.value = (upper << 4) | lower
            await ClockCycles(dut.clk, 1)
            expected = (lower + upper) & 0xF
            assert dut.uo_out.value.integer & 0xF == expected, \
                f"Adder mismatch: {lower}+{upper} => got {dut.uo_out.value.integer & 0xF}, expected {expected}"


@cocotb.test()
async def test_breathing_led_pwm(dut):
    """Check that uo_out[4] toggles for PWM when overflow occurs."""
    clock = Clock(dut.clk, 1, units="us")
    cocotb.start_soon(clock.start())

    await reset_dut(dut)

    # Trigger overflow
    dut.ui_in.value = 0xF8  # 8 + 15 = 23 -> overflow bit = 1
    await ClockCycles(dut.clk, 1)

    # Sample uo_out[4] over time to check for PWM toggling
    led_values = []
    for _ in range(200):
        await ClockCycles(dut.clk, 1)
        led_values.append(dut.uo_out.value.integer >> 4 & 0x1)

    transitions = sum(led_values[i] != led_values[i-1] for i in range(1, len(led_values)))
    assert transitions > 5, "Breathing LED did not toggle; expected PWM pattern."


@cocotb.test()
async def test_led_off_without_overflow(dut):
    """Check that uo_out[4] stays off if no overflow (LED not enabled)."""
    clock = Clock(dut.clk, 1, units="us")
    cocotb.start_soon(clock.start())

    await reset_dut(dut)

    dut.ui_in.value = 0x11  # 1+1 = 2 -> no overflow
    await ClockCycles(dut.clk, 10)
    led_state = dut.uo_out.value.integer >> 4 & 0x1
    assert led_state == 0, "Breathing LED should be off if overflow bit not set."


@cocotb.test()
async def test_reset_behavior(dut):
    """Ensure reset clears uo_out and LED."""
    clock = Clock(dut.clk, 1, units="us")
    cocotb.start_soon(clock.start())

    dut.ui_in.val_
