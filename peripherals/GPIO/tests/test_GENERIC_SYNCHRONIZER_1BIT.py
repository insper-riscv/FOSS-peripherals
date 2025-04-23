import random
import pytest
from cocotb.binary import BinaryValue

import lib


# -----------------------------------------------------------------------------
# Toplevel Synchronizer Wrapper
# -----------------------------------------------------------------------------
class GENERIC_SYNCHRONIZER_1BIT(lib.Entity):
    """Maps to the VHDL entity GENERIC_SYNCHRONIZER_1BIT, a single-bit, N-stage pipeline."""
    clock    = lib.Entity.Input_pin
    async_in = lib.Entity.Input_pin
    sync_out = lib.Entity.Output_pin


# -----------------------------------------------------------------------------
# Functional Test: Shift through known fixed patterns
# -----------------------------------------------------------------------------
@GENERIC_SYNCHRONIZER_1BIT.testcase
async def tb_SYNCHRONIZER_1BIT_case_1(dut, trace):
    """Applies fixed single-bit patterns and waits N cycles to check output."""
    N = int(dut.N)
    dut._log.info(f"Running manual test for 1-bit synchronizer with N = {N}")

    patterns = [("zero", "0"), ("one", "1")]

    for label, bit in patterns:
        dut._log.info(f"Applying pattern: {label} -> {bit}")
        dut.async_in.value = BinaryValue(bit)
        for _ in range(N):
            await trace.cycle()
        yield trace.check(
            dut.sync_out,
            bit,
            f"sync_out should be {bit} after {N} cycles ({label})"
        )

    dut._log.info("Fixed pattern test completed successfully.")


# -----------------------------------------------------------------------------
# Stress Test: Random bit patterns
# -----------------------------------------------------------------------------
@GENERIC_SYNCHRONIZER_1BIT.testcase
async def tb_SYNCHRONIZER_1BIT_stress(dut, trace):
    """Random test for 1-bit synchronizer.
    Validates delayed propagation of random bits after N cycles.
    """
    trace.disable()
    N = int(dut.N)
    dut._log.info(f"Running stress test with N={N}")

    in_history = []
    NUM_CYCLES = 50

    for i in range(NUM_CYCLES):
        await trace.cycle()
        rand_bit = str(random.getrandbits(1))

        dut.async_in.value = BinaryValue(rand_bit)
        in_history.append(rand_bit)

        if i >= N:
            expected = in_history[i - N]
            yield trace.check(
                dut.sync_out,
                expected,
                f"Cycle {i}: Expected={expected}, got={dut.sync_out.value}"
            )

    dut._log.info("Stress test completed successfully.")


# -----------------------------------------------------------------------------
# Synthesis test
# -----------------------------------------------------------------------------
@pytest.mark.synthesis
def test_SYNCHRONIZER_1BIT_synthesis():
    GENERIC_SYNCHRONIZER_1BIT.build_vhd()
    GENERIC_SYNCHRONIZER_1BIT.build_netlistsvg()



# -----------------------------------------------------------------------------
# Manual test execution (for specific N values)
# -----------------------------------------------------------------------------
@pytest.mark.testcases
def test_SYNCHRONIZER_1BIT_testcases():
    GENERIC_SYNCHRONIZER_1BIT.test_with(tb_SYNCHRONIZER_1BIT_case_1, {"N": 2})
    GENERIC_SYNCHRONIZER_1BIT.test_with(tb_SYNCHRONIZER_1BIT_case_1, {"N": 4})


# -----------------------------------------------------------------------------
# Stress test execution
# -----------------------------------------------------------------------------
@pytest.mark.coverage
def test_SYNCHRONIZER_1BIT_coverage():
    GENERIC_SYNCHRONIZER_1BIT.test_with(tb_SYNCHRONIZER_1BIT_stress, {"N": 2})
    GENERIC_SYNCHRONIZER_1BIT.test_with(tb_SYNCHRONIZER_1BIT_stress, {"N": 4})


# -----------------------------------------------------------------------------
# Run standalone
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    lib.run_test(__file__)
