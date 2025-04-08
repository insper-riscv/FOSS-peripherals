library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use work.types.all;

entity generic_address_decoder is
  generic (
    -- Width of the address bus
    ADDR_WIDTH      : natural := 32;
    -- Number of peripherals to decode
    NUM_PERIPHERALS : natural := 4;
    -- Base addresses for peripherals (as a matrix)
    BASE_ADDRESSES  : addr_matrix(0 to NUM_PERIPHERALS-1)(ADDR_WIDTH-1 downto 0) := (others => (others => '0'));
    -- Address range for each peripheral (in bytes, must be power of 2)
    ADDR_RANGES     : natural_vector(0 to NUM_PERIPHERALS-1) := (others => 4096)
  );
  port (
    -- Input address to decode
    address : in  std_logic_vector(ADDR_WIDTH-1 downto 0);
    -- Chip select outputs (one for each peripheral)
    cs      : out std_logic_vector(NUM_PERIPHERALS-1 downto 0)
  );
end entity generic_address_decoder;

architecture Behavioral of generic_address_decoder is
  -- Generate masks based on address ranges
  signal mask_array : addr_matrix(0 to NUM_PERIPHERALS-1)(ADDR_WIDTH-1 downto 0) := generate_masks(ADDR_RANGES, ADDR_WIDTH);
  
begin
  
  -- Debugging process to report base addresses and masks
  process
  begin
    wait for 1 ns;
    for i in 0 to NUM_PERIPHERALS-1 loop
      report "Base address " & integer'image(i) & ": " & to_string(BASE_ADDRESSES(i));
      report "Mask " & integer'image(i) & ": " & to_string(mask_array(i));
    end loop;
    wait;
  end process;

  -- Address decoding process
  process(address)
    variable addr_masked : std_logic_vector(ADDR_WIDTH-1 downto 0);
    variable base_masked : std_logic_vector(ADDR_WIDTH-1 downto 0);
  begin
    -- Initialize chip selects to all 0s
    cs <= (others => '0');

    -- Decode the address
    for i in 0 to NUM_PERIPHERALS-1 loop
      -- Apply mask to input address
      addr_masked := address and mask_array(i);
      -- Apply same mask to base address
      base_masked := BASE_ADDRESSES(i) and mask_array(i);

      -- Check if masked address matches masked base address
      if addr_masked = base_masked then
        cs(i) <= '1';  -- Assert chip select for matching peripheral
      end if;
    end loop;
  end process;
end architecture Behavioral;
