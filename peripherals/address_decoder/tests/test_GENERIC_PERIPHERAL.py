import pytest
from cocotb.binary import BinaryValue
import lib

class GENERIC_PERIPHERAL(lib.Entity):

    clk         = lib.Entity.Input_pin
    reset       = lib.Entity.Input_pin
    wr          = lib.Entity.Input_pin
    rd          = lib.Entity.Input_pin
    opcode      = lib.Entity.Input_pin
    data_i      = lib.Entity.Input_pin
    data_o      = lib.Entity.Output_pin
    interrupt_o = lib.Entity.Output_pin

    # Class variables to store parameters for testing
    DATA_WIDTH = 32
    OPERATION_CODE_WIDTH = 4

    @classmethod
    def configure(cls, operation_code_width, data_width=None):
        """Configure the class with generic parameters"""
        if data_width is not None:
            cls.DATA_WIDTH = data_width
        if operation_code_width is not None:
            cls.OPERATION_CODE_WIDTH = operation_code_width
        return cls

    @classmethod
    def test_with(cls, testcase):
        """Override test_with to include generics"""
        parameters = {
            "DATA_WIDTH": cls.DATA_WIDTH,
            "OPERATION_CODE_WIDTH": cls.OPERATION_CODE_WIDTH,
        }

        # Call parent method with parameters
        super().test_with(testcase, parameters=parameters)
       
@GENERIC_PERIPHERAL.testcase
async def tb_GENERIC_PERIPHERAL(dut, trace: lib.Waveform):
    """Test the GENERIC_PERIPHERAL """
    trace.disable()

    # Apply reset
    dut.reset.value = 1
    await trace.cycle()

    # Now check outputs during reset
    zero_data_bus = BinaryValue(0, n_bits=GENERIC_PERIPHERAL.DATA_WIDTH, bigEndian=False)
    yield trace.check(dut.interrupt_o, BinaryValue(0, n_bits=1))
    yield trace.check(dut.data_o, zero_data_bus)

    # Release reset
    dut.reset.value = 0
    dut.opcode.value = 0
    await trace.cycle()

    # Check outputs after reset, with cs=0
    yield trace.check(dut.interrupt_o, BinaryValue(0, n_bits=1))
    yield trace.check(dut.data_o, zero_data_bus)

    # Now try with opcode = 1
    dut.opcode.value = 1
    await trace.cycle()

    # Check if interrupt and data_o are set
    max_int_data_width = BinaryValue(4294967295, n_bits=GENERIC_PERIPHERAL.DATA_WIDTH, bigEndian=False)
    yield trace.check(dut.interrupt_o, BinaryValue(value=1, n_bits=1))
    yield trace.check(dut.data_o, max_int_data_width.binstr)

@pytest.mark.synthesis
def test_GENERIC_PERIPHERAL_synthesis():
    """Test the GENERIC_PERIPHERAL synthesis"""
    GENERIC_PERIPHERAL.build_vhd()

@pytest.mark.testcases
def test_GENERIC_PERIPHERAL_testcases():
    """Test the GENERIC_PERIPHERAL testcases"""
    GENERIC_PERIPHERAL.configure(1, 32)
    GENERIC_PERIPHERAL.test_with(tb_GENERIC_PERIPHERAL)

if __name__ == "__main__":
    lib.run_tests(__file__)