library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use work.types.all;

entity generic_address_decoder is
    generic (
        DATA_WIDTH        : natural := 32;  -- Width of the data bus
        ADDR_WIDTH        : natural := 32; -- Width of the address bus
        -- Number of peripherals to decode
        NUM_PERIPHERALS   : natural := 4;
        -- Base addresses for peripherals (as a matrix)
        BASE_ADDRESSES    : addr_matrix(0 to NUM_PERIPHERALS-1)(ADDR_WIDTH-1 downto 0) := (others => (others => '0'));
        -- Address range for each peripheral (in bytes, must be power of 2)
        ADDR_RANGES       : natural_vector(0 to NUM_PERIPHERALS-1) := (others => 4096);
        -- Whether to combine interrupts into a single signal or pass them through as a vector
        COMBINE_INTERRUPTS : boolean := true;
        -- Whether to enable debug reporting
        ENABLE_DEBUG      : boolean := false
    );
    port (
        -- CPU interface
        data_i            : in std_logic_vector(DATA_WIDTH-1 downto 0);  -- Data input from CPU   
        address           : in std_logic_vector(ADDR_WIDTH-1 downto 0); -- Address input from CPU
        data_o            : out std_logic_vector(DATA_WIDTH-1 downto 0); -- Data output to CPU
        wr                : in std_logic;  -- Write enable signal from CPU
        rd                : in std_logic;  -- Read enable signal from CPU
        interrupt_o       : out std_logic_vector(0 to NUM_PERIPHERALS-1); -- Interrupt output to CPU (width depends on COMBINE_INTERRUPTS)

        -- Peripheral interface
        data_o_peripheral : out std_logic_vector(DATA_WIDTH-1 downto 0); -- Data output to peripherals
        data_i_peripheral : in data_matrix(0 to NUM_PERIPHERALS-1)(DATA_WIDTH-1 downto 0); -- Data input from peripherals (as a matrix)
        wr_peripheral     : out std_logic_vector(NUM_PERIPHERALS-1 downto 0); -- Write enable signal to peripherals
        rd_peripheral     : out std_logic_vector(NUM_PERIPHERALS-1 downto 0); -- Read enable signal to peripherals
        interrupt_i       : in std_logic_vector(NUM_PERIPHERALS-1 downto 0) -- Interrupt signal from peripherals
    );
end entity generic_address_decoder;

architecture Behavioral of generic_address_decoder is
  -- Generate masks based on address ranges
  signal mask_array : addr_matrix(0 to NUM_PERIPHERALS-1)(ADDR_WIDTH-1 downto 0) := generate_masks(ADDR_RANGES, ADDR_WIDTH);
  signal cs : std_logic_vector(NUM_PERIPHERALS-1 downto 0);
  signal combined_interrupt : std_logic;
  
begin
  -- Debugging process - only active when ENABLE_DEBUG is true
  g_debug: if ENABLE_DEBUG generate
    process
    begin
      wait for 1 ns;
      for i in 0 to NUM_PERIPHERALS-1 loop
        report "Base address " & integer'image(i) & ": " & to_string(BASE_ADDRESSES(i));
        report "Mask " & integer'image(i) & ": " & to_string(mask_array(i));
      end loop;
      wait;
    end process;
  end generate;

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
  
  -- Generate write and read enable signals for peripherals
  process(cs, wr, rd)
  begin
    wr_peripheral <= (others => '0');
    rd_peripheral <= (others => '0');
    
    for i in 0 to NUM_PERIPHERALS-1 loop
      if cs(i) = '1' then
        wr_peripheral(i) <= wr;
        rd_peripheral(i) <= rd;
      end if;
    end loop;
  end process;
  
  -- Data routing from CPU to peripherals
  data_o_peripheral <= data_i;
  
  -- Data routing from peripherals to CPU
  process(cs, data_i_peripheral)
    variable temp_data : std_logic_vector(DATA_WIDTH-1 downto 0);
  begin
    temp_data := (others => '0');
    
    for i in 0 to NUM_PERIPHERALS-1 loop
      if cs(i) = '1' then
        -- With matrix representation, we can directly access the peripheral's data
        temp_data := data_i_peripheral(i);
      end if;
    end loop;
    
    data_o <= temp_data;
  end process;
  
  -- Interrupt handling - based on COMBINE_INTERRUPTS flag
  process(interrupt_i)
    variable temp_interrupt : std_logic;
  begin
    temp_interrupt := '0';
    
    for i in 0 to NUM_PERIPHERALS-1 loop
      temp_interrupt := temp_interrupt or interrupt_i(i);
    end loop;
    
    combined_interrupt <= temp_interrupt;
  end process;
  
  -- Interrupt output selection based on COMBINE_INTERRUPTS flag
  g_combined_int: if COMBINE_INTERRUPTS generate
    interrupt_o(0) <= combined_interrupt;
  end generate;
  
  g_separate_int: if not COMBINE_INTERRUPTS generate
    interrupt_o <= interrupt_i;
  end generate;
  
end architecture Behavioral;
