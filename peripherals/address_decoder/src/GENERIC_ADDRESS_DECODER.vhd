library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

-- Include the package with the helper functions.
library WORK;
use work.GENERICS.all;

entity generic_address_decoder is
  generic (
    -- Define the width of the address bus.
    ADDR_WIDTH : natural := 32;
    -- Number of peripherals (slave devices) to decode.
    NUM_SLAVES : natural := 4;
    -- Array of base addresses for each peripheral.
    BASE_ADDR : t_std_logic_array(0 to NUM_SLAVES-1) := (
      x"00000000", -- Peripheral 0 base address
      x"00001000", -- Peripheral 1 base address
      x"00002000", -- Peripheral 2 base address
      x"00003000"  -- Peripheral 3 base address
    );
    -- Array of address masks. This mask selects which bits are relevant.
    MASK : t_std_logic_array(0 to NUM_SLAVES-1) := (
      x"FFFFF000", -- Mask for Peripheral 0
      x"FFFFF000", -- Mask for Peripheral 1
      x"FFFFF000", -- Mask for Peripheral 2
      x"FFFFF000"  -- Mask for Peripheral 3
    )
  );
  port (
    -- Input address from the bus.
    address : in std_logic_vector(ADDR_WIDTH-1 downto 0);
    -- Chip-select outputs for each peripheral.
    cs      : out std_logic_vector(NUM_SLAVES-1 downto 0)
  );
end entity generic_address_decoder;

architecture Behavioral of addr_decoder is
begin
  -- For each peripheral, generate a comparison that asserts the chip-select
  -- if the masked input address equals the masked base address.
  gen_dec: for i in 0 to NUM_SLAVES-1 generate
  begin
    cs(i) <= is_equal(address and MASK(i), BASE_ADDR(i) and MASK(i));
  end generate;
  
end architecture Behavioral;
