import pytest
from cocotb.binary import BinaryValue
from cocotb.triggers import Timer
import cocotb
from lib.entity import Entity
import lib
import copy
from test_TYPES_package import TYPES
from peripherals.UART.tests.test_GENERIC_OPERATION_DECODER_package import GENERIC_OPERATION_DECODER


class GENERIC_OPERATION_DECODER_WRAPPER(Entity):
    """Wrapper for the Generic Operation Decoder Wrapper with individual generic parameters"""
    
    _package = [TYPES, GENERIC_OPERATION_DECODER]
    
    # Define pins
    operation = Entity.Input_pin
    control_signal = Entity.Output_pin

    child = GENERIC_OPERATION_DECODER

    # Default generics
    OP_WIDTH = 3
    CONTROL_SIGNAL_WIDTH = 2
    OPERATION_CONTROL_SIGNAL_COUNT = 4

    OP_0 = 0
    OP_1 = 1
    OP_2 = 2
    OP_3 = 3

    CTRL_0 = 1
    CTRL_1 = 2
    CTRL_2 = 3
    CTRL_3 = 0

    DEFAULT_CTRL = 0

    @classmethod
    def configure(cls, op_width=3, ctrl_width=2, map_count=4,
                  op_vals=None, ctrl_vals=None, default_ctrl=0):
        cls.OP_WIDTH = op_width
        cls.CONTROL_SIGNAL_WIDTH = ctrl_width
        cls.OPERATION_CONTROL_SIGNAL_COUNT = map_count

        # Allow custom mapping if needed
        if op_vals is not None:
            cls.OP_0, cls.OP_1, cls.OP_2, cls.OP_3 = op_vals
        if ctrl_vals is not None:
            cls.CTRL_0, cls.CTRL_1, cls.CTRL_2, cls.CTRL_3 = ctrl_vals
        cls.DEFAULT_CTRL = default_ctrl
        return cls

    @classmethod
    def test_with(cls, testcase, parameters=None):
        if parameters is None:
            parameters = {
                "OP_WIDTH": cls.OP_WIDTH,
                "CONTROL_SIGNAL_WIDTH": cls.CONTROL_SIGNAL_WIDTH,
                "OPERATION_CONTROL_SIGNAL_COUNT": cls.OPERATION_CONTROL_SIGNAL_COUNT,
                "OP_0": cls.OP_0,
                "OP_1": cls.OP_1,
                "OP_2": cls.OP_2,
                "OP_3": cls.OP_3,
                "CTRL_0": cls.CTRL_0,
                "CTRL_1": cls.CTRL_1,
                "CTRL_2": cls.CTRL_2,
                "CTRL_3": cls.CTRL_3,
                "DEFAULT_CTRL": cls.DEFAULT_CTRL
            }
        super().test_with(testcase, parameters=parameters)

@GENERIC_OPERATION_DECODER_WRAPPER.testcase
async def tb_decoder_basic(dut, trace: lib.Waveform):
    """
    Test that the decoder maps operations to control signals as expected.
    """
    trace.disable()
    # Mapping from GENERIC_OPERATION_DECODER_WRAPPER.vhd generics
    op_to_ctrl = {
        0: 1,
        1: 2,
        2: 3,
        3: 0
    }
    ctrl_width = int(dut.control_signal.value.n_bits)
    # Test all mapped operations
    print(op_to_ctrl.items())
    for op, ctrl in op_to_ctrl.items():
        dut.operation.value = op
        await trace.cycle()
        yield trace.check(dut.control_signal, BinaryValue(ctrl, n_bits=ctrl_width, bigEndian=False))
    # Test unmapped operation (should get default)
    dut.operation.value = 7  # Not in map
    await trace.cycle()
    yield trace.check(dut.control_signal, BinaryValue(0, n_bits=ctrl_width))

@GENERIC_OPERATION_DECODER_WRAPPER.testcase
async def tb_decoder_default_output(dut, trace: lib.Waveform):
    """
    Test that the decoder outputs the default control signal for unmapped operations.
    """
    trace.disable()
    ctrl_width = int(dut.control_signal.value.n_bits)
    # Use an operation value not in the map
    dut.operation.value = 6
    await trace.cycle()
    yield trace.check(dut.control_signal, BinaryValue(0, n_bits=ctrl_width))

@pytest.mark.synthesis
def test_GENERIC_OPERATION_DECODER_WRAPPER_synthesis():
    """Test the GENERIC_OPERATION_DECODER_WRAPPER synthesis"""
    GENERIC_OPERATION_DECODER_WRAPPER.build_vhd()

@pytest.mark.testcases
def test_GENERIC_OPERATION_DECODER_WRAPPER_testcases():
    """Run testcases for GENERIC_OPERATION_DECODER_WRAPPER with different parameters"""
    dec = GENERIC_OPERATION_DECODER_WRAPPER.configure(op_width=3, ctrl_width=2, map_count=4)
    dec.test_with(tb_decoder_basic)
    dec.test_with(tb_decoder_default_output)

if __name__ == "__main__":
    lib.run_tests(__file__)