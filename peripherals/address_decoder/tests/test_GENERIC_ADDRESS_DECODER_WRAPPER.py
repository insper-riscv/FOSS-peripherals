import pytest
from cocotb.binary import BinaryValue
from cocotb.triggers import Timer
from lib.entity import Entity
import lib
import copy
from test_TYPES_package import TYPES
from test_GENERIC_ADDRESS_DECODER import GENERIC_ADDRESS_DECODER


class GENERIC_ADDRESS_DECODER_WRAPPER(Entity):
    """Wrapper for the Generic Address Decoder with individual generic parameters"""
    
    _package = TYPES
    
    # Define pins - only address input and cs output
    address = Entity.Input_pin
    cs = Entity.Output_pin

    child = GENERIC_ADDRESS_DECODER
    
    # Use the original configure method but change the classname in references
    @classmethod
    def configure(cls, addr_width=32, num_peripherals=4, base_addresses=None, addr_ranges=None):
        """
        Configure the wrapper with the same parameters as GENERIC_ADDRESS_DECODER
        
        Args:
            addr_width: Width of the address bus
            num_peripherals: Number of peripherals to decode
            base_addresses: List of base addresses for each peripheral
            addr_ranges: List of address ranges (in bytes) for each peripheral
        """
        cls.ADDR_WIDTH = addr_width
        cls.NUM_PERIPHERALS = num_peripherals

        # Default base addresses if none provided
        if base_addresses is None:
            base_addresses = [
                0x00000000,  # Peripheral 0 at 0x00000000
                0x00001000,  # Peripheral 1 at 0x00001000
                0x00002000,  # Peripheral 2 at 0x00002000
                0x00003000   # Peripheral 3 at 0x00003000
            ]

        # Ensure base_addresses has exactly num_peripherals entries
        if len(base_addresses) < num_peripherals:
            # Extend with additional addresses
            last_addr = base_addresses[-1] if base_addresses else 0
            step = 0x1000  # Default 4KB step
            for i in range(len(base_addresses), num_peripherals):
                base_addresses.append(last_addr + step * (i - len(base_addresses) + 1))

        # Truncate if too many
        base_addresses = base_addresses[:num_peripherals]

        # Default address ranges if none provided
        if addr_ranges is None:
            addr_ranges = [4096] * num_peripherals  # Default 4KB address space for each

        # Ensure addr_ranges has exactly num_peripherals entries
        if len(addr_ranges) < num_peripherals:
            addr_ranges.extend([addr_ranges[-1] if addr_ranges else 4096] * (num_peripherals - len(addr_ranges)))

        # Truncate if too many
        addr_ranges = addr_ranges[:num_peripherals]

        # Store for use in tests
        cls.BASE_ADDRESSES = base_addresses
        cls.ADDR_RANGES = addr_ranges

        return cls
    
    @classmethod
    def test_with(cls, testcase, parameters=None):
        """
        Run test with specified parameters, converting array generics to individual parameters
        that GHDL can handle properly via command line
        """

        if parameters is None:
            parameters = {
                "ADDR_WIDTH": cls.ADDR_WIDTH,
                "NUM_PERIPHERALS": cls.NUM_PERIPHERALS,
                "BASE_ADDRESSES": cls.BASE_ADDRESSES,
                "ADDR_RANGES": cls.ADDR_RANGES
            }
        
        # Create a new parameters dictionary without array parameters
        fixed_params = copy.deepcopy(parameters)
        
        # Remove the array parameters and replace with individual parameters
        if "BASE_ADDRESSES" in fixed_params and isinstance(fixed_params["BASE_ADDRESSES"], list):
            base_addresses = fixed_params.pop("BASE_ADDRESSES")
            # Add each base address as its own parameter (up to 8 supported)
            for i, addr in enumerate(base_addresses):
                if i < fixed_params["NUM_PERIPHERALS"]:
                    fixed_params[f"BASE_ADDR_{i}"] = addr
            
            # Add extras with default values in case NUM_PERIPHERALS is not known
            for i in range(len(base_addresses), 8): # Support up to 8 peripherals
                fixed_params[f"BASE_ADDR_{i}"] = 0x1000 * i
        
        if "ADDR_RANGES" in fixed_params and isinstance(fixed_params["ADDR_RANGES"], list):
            addr_ranges = fixed_params.pop("ADDR_RANGES")
            # Add each address range as its own parameter
            for i, size in enumerate(addr_ranges):
                if i < fixed_params["NUM_PERIPHERALS"]:
                    fixed_params[f"ADDR_RANGE_{i}"] = size
            
            # Add extras with default values
            for i in range(len(addr_ranges), 8):
                fixed_params[f"ADDR_RANGE_{i}"] = 4096
        
        # Call parent class test_with with modified parameters
        super().test_with(testcase, parameters=fixed_params)

@GENERIC_ADDRESS_DECODER_WRAPPER.testcase
async def tb_address_decoder_base_addresses_wrapper(dut, trace: lib.Waveform):
    """Test chip select assertion for exact base addresses using wrapper"""
    # Test each base address - should select exactly one peripheral
    num_peripherals = int(dut.NUM_PERIPHERALS.value)
    addr_width = int(dut.ADDR_WIDTH.value)
    
    for i in range(num_peripherals):
        # Get base address from individual generic parameters
        base_addr_attr = getattr(dut, f"BASE_ADDR_{i}")
        addr_value = int(base_addr_attr.value)
        
        dut.address.value = BinaryValue(value=addr_value, n_bits=addr_width, bigEndian=False)
        await Timer(10, units="ns")

        # Create expected one-hot chip select pattern
        expected_cs = 1 << i  # Set only bit i
        yield trace.check(dut.cs, BinaryValue(value=expected_cs, n_bits=num_peripherals, bigEndian=False))

@GENERIC_ADDRESS_DECODER_WRAPPER.testcase
async def tb_address_decoder_offset_addresses_wrapper(dut, trace: lib.Waveform):
    """Test chip select with offset addresses within each peripheral's range using wrapper"""
    # For each peripheral, test address with offset that should still select the peripheral
    num_peripherals = int(dut.NUM_PERIPHERALS.value)  # Convert to int
    addr_width = int(dut.ADDR_WIDTH.value)  # Convert to int
    
    for i in range(num_peripherals):
        # Base address for this peripheral - get from individual generic
        base = int(getattr(dut, f"BASE_ADDR_{i}").value)
        
        # Calculate appropriate mask based on address range
        range_value = int(getattr(dut, f"ADDR_RANGE_{i}").value)
        mask_bits = 0
        while (2**mask_bits < range_value):
            mask_bits += 1
        
        mask = ~((1 << mask_bits) - 1) & ((1 << addr_width) - 1)
        
        # Create address with offset that doesn't affect masked bits
        offset = range_value // 4  # Small offset within the range
        addr_value = base + offset

        # Ensure the offset address still matches base address when masked
        if (addr_value & mask) == (base & mask):
            dut.address.value = addr_value  # Assign directly, not BinaryValue
            await Timer(10, units="ns")

            # Create expected one-hot chip select pattern
            expected_cs = 1 << i
            yield trace.check(dut.cs, BinaryValue(value=expected_cs, n_bits=num_peripherals, bigEndian=False))

@GENERIC_ADDRESS_DECODER_WRAPPER.testcase
async def tb_address_decoder_out_of_range_wrapper(dut, trace: lib.Waveform):
    """Test addresses that are outside any peripheral's range using wrapper"""
    num_peripherals = int(dut.NUM_PERIPHERALS.value)
    addr_width = int(dut.ADDR_WIDTH.value)
    
    # Generate a definitely out-of-range address - beyond all peripherals
    # Use the last peripheral's base address + its range + some extra
    last_base = int(getattr(dut, f"BASE_ADDR_{num_peripherals-1}").value)
    last_range = int(getattr(dut, f"ADDR_RANGE_{num_peripherals-1}").value)
    out_of_range_addr = last_base + last_range * 2
    
    # Set the address and check that no chip select is active
    dut.address.value = BinaryValue(value=out_of_range_addr, n_bits=addr_width, bigEndian=False)
    await Timer(10, units="ns")
    
    # None of the chip selects should be active
    expected_cs = 0
    yield trace.check(dut.cs, BinaryValue(value=expected_cs, n_bits=num_peripherals, bigEndian=False))
    
    # Add a second test point to ensure enough data for waveform generation
    # Try an address with high bits set that shouldn't match any peripheral
    far_addr = 0xF0000000
    dut.address.value = BinaryValue(value=far_addr, n_bits=addr_width, bigEndian=False)
    await Timer(10, units="ns")
    yield trace.check(dut.cs, BinaryValue(value=expected_cs, n_bits=num_peripherals, bigEndian=False))

@GENERIC_ADDRESS_DECODER_WRAPPER.testcase
async def tb_address_decoder_variable_peripherals_wrapper(dut, trace: lib.Waveform):
    """Test with a variable number of peripherals using wrapper"""
    # Test each peripheral with its base address
    num_peripherals = int(dut.NUM_PERIPHERALS.value)  # Convert to int
    
    for i in range(num_peripherals):
        addr_value = int(getattr(dut, f"BASE_ADDR_{i}").value)
        dut.address.value = addr_value  # Assign directly
        await Timer(10, units="ns")

        # Create expected one-hot chip select pattern
        expected_cs = 1 << i
        yield trace.check(dut.cs, BinaryValue(value=expected_cs, n_bits=num_peripherals, bigEndian=False))

@pytest.mark.synthesis
def test_GENERIC_PERIPHERAL_synthesis():
    """Test the GENERIC_PERIPHERAL synthesis"""
    GENERIC_ADDRESS_DECODER_WRAPPER.build_vhd()

@pytest.mark.testcases
def test_GENERIC_ADDRESS_DECODER_WRAPPER_testcases():
    """Run testcases for GENERIC_ADDRESS_DECODER_WRAPPER with different numbers of peripherals"""
    # Test with different peripheral counts
    for num_peripherals in [2, 4, 8]:
        decoder = GENERIC_ADDRESS_DECODER_WRAPPER.configure(
            addr_width=32,
            num_peripherals=num_peripherals,
            base_addresses=[i * 0x1000 for i in range(num_peripherals)],
            addr_ranges=[4096] * num_peripherals
        )

        # Then run the test cases
        decoder.test_with(tb_address_decoder_base_addresses_wrapper)
        decoder.test_with(tb_address_decoder_offset_addresses_wrapper)
        decoder.test_with(tb_address_decoder_out_of_range_wrapper)
        decoder.test_with(tb_address_decoder_variable_peripherals_wrapper)

if __name__ == "__main__":
    lib.run_tests(__file__)