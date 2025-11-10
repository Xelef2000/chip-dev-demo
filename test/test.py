# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, FallingEdge
from cocotb.result import TestFailure


async def reset_dut(dut, cycles=5):
    """Reset helper."""
    dut.rst_n.value = 0
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    await ClockCycles(dut.clk, cycles)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)


@cocotb.test()
async def test_basic_adder(dut):
    """Test that ui_in[3:0] + ui_in[7:4] = uo_out[3:0] with overflow on uo_out[4]."""
    dut._log.info("=== Basic adder test ===")

    clock = Clock(dut.clk, 1, units="us")
    cocotb.start_soon(clock.start())

    await reset_dut(dut)

    # Test all combinations of lower and upper nibbles
    for upper in range(16):
        for lower in range(16):
            dut.ui_in.value = (upper << 4) | lower
            await ClockCycles(dut.clk, 1)
            sum_val = lower + upper
            expected = sum_val & 0xF
            overflow = (sum_val >> 4) & 0x1

            assert dut.uo_out.value.integer & 0xF == expected, \
                f"Adder mismatch: {lower}+{upper} => got {dut.uo_out.value.integer & 0xF}, expected {expected}"

            assert ((dut.uo_out.value.integer >> 4) & 1) == overflow, \
                f"Overflow mismatch: {lower}+{upper} => got {overflow}"

    dut._log.info("Adder tests passed ✅")


@cocotb.test()
async def test_breathing_led_activation(dut):
    """Test that the breathing LED only activates when overflow bit is high."""
    dut._log.info("=== Breathing LED activation test ===")

    clock = Clock(dut.clk, 1, units="us")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)

    # Case 1: No overflow
    dut.ui_in.value = 0x11  # 1 + 1 = 2, no overflow
    await ClockCycles(dut.clk, 10)
    assert dut.uo_out.value.integer & (1 << 5) == 0, "LED should be off when no overflow."

    # Case 2: Overflow
    dut.ui_in.value = 0xF8  # 8 + 15 = 23 (overflow)
    await ClockCycles(dut.clk, 10)
    led_on = bool(dut.uo_out.value.integer & (1 << 5))
    assert led_on, "LED should activate when overflow bit is set."

    dut._log.info("Breathing LED activation test passed ✅")


@cocotb.test()
async def test_breathing_led_pwm(dut):
    """Test LED breathing pattern over time."""
    dut._log.info("=== Breathing LED PWM dynamics ===")

    clock = Clock(dut.clk, 1, units="us")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)

    # Trigger overflow
    dut.ui_in.value = 0xF8
    await ClockCycles(dut.clk, 1)

    # Sample LED states over time to confirm it "breathes"
    led_values = []
    for _ in range(1000):  # sample 1000 cycles
        await ClockCycles(dut.clk, 1)
        led_values.append(int(bool(dut.uo_out.value.integer & (1 << 5))))

    transitions = sum(led_values[i] != led_values[i-1] for i in range(1, len(led_values)))
    dut._log.info(f"LED toggled {transitions} times during test")

    assert transitions > 5, "LED should be changing brightness (PWM pattern detected)"
    dut._log.info("Breathing LED PWM test passed ✅")


@cocotb.test()
async def test_reset_behavior(dut):
    """Ensure module resets correctly (LED off, outputs cleared)."""
    dut._log.info("=== Reset behavior test ===")

    clock = Clock(dut.clk, 1, units="us")
    cocotb.start_soon(clock.start())

    await reset_dut(dut)
    dut.ui_in.value = 0xFF
    await ClockCycles(dut.clk, 10)

    # Force reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    assert dut.uo_out.value.integer == 0, "All outputs should reset to 0"
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    dut._log.info("Reset behavior test passed ✅")
