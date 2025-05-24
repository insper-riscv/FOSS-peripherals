library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

----------------------------------------------------------------------------------
-- Address Decoder Types Package
-- 
-- Defines custom types and utility functions used by the address decoder
-- components to handle memory mapping and peripheral communication.
----------------------------------------------------------------------------------

package types is
  -- Vector of natural numbers (used for address ranges)
  type NATURAL_ARRAY_T is array (natural range <>) of natural;
  
  -- Matrix of addresses (array of std_logic_vector)
  type ADDR_MATRIX_T is array (natural range <>) of std_logic_vector;
  
  -- Matrix of data (for peripheral data inputs/outputs)
  type DATA_MATRIX_T is array (natural range <>) of std_logic_vector;
  
  -- Function to generate address masks based on peripheral address ranges
  function generate_masks(ranges: NATURAL_ARRAY_T; addr_width: natural) return ADDR_MATRIX_T;
  
  -- Function to convert std_logic_vector to string for debugging
  function to_string(slv: std_logic_vector) return string;
end package types;

package body types is
  -- Implementation of generate_masks function
  -- Calculates bit masks for each peripheral's address range
  function generate_masks(ranges: NATURAL_ARRAY_T; addr_width: natural)
    return ADDR_MATRIX_T is
    variable result: ADDR_MATRIX_T(ranges'range)(addr_width-1 downto 0);
    variable mask_bits: natural;
  begin
    for i in ranges'range loop
      -- Calculate how many bits to mask (log2 of range)
      mask_bits := 0;
      while (2**mask_bits < ranges(i)) loop
        mask_bits := mask_bits + 1;
      end loop;
      
      -- Generate mask with 1's in upper bits (address bits that matter)
      result(i) := (others => '0');
      for j in mask_bits to addr_width-1 loop
        result(i)(j) := '1';
      end loop;
    end loop;
    return result;
  end function;
  
  -- Implementation of to_string function
  -- Converts a std_logic_vector to a human-readable string
  function to_string(slv: std_logic_vector) return string is
    variable result: string(1 to slv'length);
  begin
    for i in slv'range loop
      case slv(i) is
        when '0' => result(i+1) := '0';
        when '1' => result(i+1) := '1';
        when others => result(i+1) := 'X';
      end case;
    end loop;
    return result;
  end function;
end package body types;
