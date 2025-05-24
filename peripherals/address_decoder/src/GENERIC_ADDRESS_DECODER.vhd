library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use work.types.all;

----------------------------------------------------------------------------------
-- Generic Address Decoder
-- 
-- This component decodes CPU addresses to select appropriate peripherals and 
-- routes data between the CPU and peripherals. It handles read/write operations
-- and interrupt management.
----------------------------------------------------------------------------------

entity generic_address_decoder is
    generic (
        -- Bus width parameters
        DATA_WIDTH        : natural := 32;  -- Width of the data bus in bits
        ADDR_WIDTH        : natural := 32;  -- Width of the address bus in bits
        
        -- Peripheral configuration
        NUM_PERIPHERALS   : natural := 4;   -- Number of peripherals to decode
        
        -- Memory mapping configuration
        BASE_ADDRESSES    : ADDR_MATRIX_T(0 to NUM_PERIPHERALS-1)(ADDR_WIDTH-1 downto 0) := (others => (others => '0')); -- Base addresses for each peripheral
        ADDR_RANGES       : NATURAL_ARRAY_T(0 to NUM_PERIPHERALS-1) := (others => 4096); -- Address range for each peripheral (bytes, power of 2)
        
        -- Feature configuration flags
        COMBINE_INTERRUPTS : boolean := true;  -- True: OR all interrupts to a single line, False: pass through individual interrupts
        ENABLE_DEBUG      : boolean := false   -- True: enable debug messages during simulation
    );
    port (
        -- CPU interface
        data_i            : in  std_logic_vector(DATA_WIDTH-1 downto 0);  -- Data input from CPU   
        address           : in  std_logic_vector(ADDR_WIDTH-1 downto 0);  -- Address input from CPU
        data_o            : out std_logic_vector(DATA_WIDTH-1 downto 0);  -- Data output to CPU
        wr                : in  std_logic;  -- Write enable signal from CPU
        rd                : in  std_logic;  -- Read enable signal from CPU
        interrupt_o       : out std_logic_vector(0 to NUM_PERIPHERALS-1); -- Interrupt output to CPU (size depends on COMBINE_INTERRUPTS)

        -- Peripheral interface
        data_o_peripheral : out std_logic_vector(DATA_WIDTH-1 downto 0);                      -- Data output to all peripherals (broadcast)
        data_i_peripheral : in  DATA_MATRIX_T(0 to NUM_PERIPHERALS-1)(DATA_WIDTH-1 downto 0);   -- Data input from each peripheral
        wr_peripheral     : out std_logic_vector(NUM_PERIPHERALS-1 downto 0);                 -- Write enable signals to peripherals
        rd_peripheral     : out std_logic_vector(NUM_PERIPHERALS-1 downto 0);                 -- Read enable signals to peripherals
        interrupt_i       : in  std_logic_vector(NUM_PERIPHERALS-1 downto 0)                  -- Interrupt signals from peripherals
    );
end entity generic_address_decoder;

architecture Behavioral of generic_address_decoder is
  -- Address masks generated based on peripheral address ranges
  signal addr_masks       : ADDR_MATRIX_T(0 to NUM_PERIPHERALS-1)(ADDR_WIDTH-1 downto 0) := generate_masks(ADDR_RANGES, ADDR_WIDTH);
  -- Chip select signals (one per peripheral)
  signal chip_select      : std_logic_vector(NUM_PERIPHERALS-1 downto 0);
  -- Combined interrupt signal (OR of all peripheral interrupts)
  signal combined_int     : std_logic;
  
begin
  -- Debug reporting process - only active when ENABLE_DEBUG is true
  g_debug: if ENABLE_DEBUG generate
    process
    begin
      report "Address Decoder Configuration:" severity note;
      report "- Number of peripherals: " & integer'image(NUM_PERIPHERALS) severity note;
      
      wait for 1 ns;
      for i in 0 to NUM_PERIPHERALS-1 loop
        report "Peripheral " & integer'image(i) & ":" severity note;
        report "  Base address: " & to_string(BASE_ADDRESSES(i)) severity note;
        report "  Address mask: " & to_string(addr_masks(i)) severity note;
        report "  Range: " & integer'image(ADDR_RANGES(i)) & " bytes" severity note;
      end loop;
      wait;
    end process;
  end generate g_debug;

  -- Address decoding process: Determines which peripheral is being addressed
  -- by comparing masked address with masked base addresses
  process(address)
    variable addr_masked : std_logic_vector(ADDR_WIDTH-1 downto 0);
    variable base_masked : std_logic_vector(ADDR_WIDTH-1 downto 0);
  begin
    -- Initialize chip selects to all 0s (no peripheral selected by default)
    chip_select <= (others => '0');

    -- Check each peripheral's address range
    for i in 0 to NUM_PERIPHERALS-1 loop
      -- Apply mask to input address (keep only significant address bits)
      addr_masked := address and addr_masks(i);
      -- Apply same mask to base address
      base_masked := BASE_ADDRESSES(i) and addr_masks(i);

      -- Check if masked address matches masked base address
      if addr_masked = base_masked then
        chip_select(i) <= '1';  -- Select peripheral if address is in its range
      end if;
    end loop;
  end process;
  
  -- Read/Write signal routing to peripherals
  -- Only routes signals to the selected peripheral
  process(chip_select, wr, rd)
  begin
    -- Default: no peripheral is enabled for write/read
    wr_peripheral <= (others => '0');
    rd_peripheral <= (others => '0');
    
    -- Route signals to the selected peripheral
    for i in 0 to NUM_PERIPHERALS-1 loop
      if chip_select(i) = '1' then
        wr_peripheral(i) <= wr;  -- Forward write enable to selected peripheral
        rd_peripheral(i) <= rd;  -- Forward read enable to selected peripheral
      end if;
    end loop;
  end process;
  
  -- Data routing from CPU to peripherals (broadcast)
  -- All peripherals receive the same data, but only selected ones act on it
  data_o_peripheral <= data_i;
  
  -- Data routing from peripherals to CPU
  -- Only data from the selected peripheral is forwarded to the CPU
  process(chip_select, data_i_peripheral)
    variable selected_data : std_logic_vector(DATA_WIDTH-1 downto 0);
  begin
    -- Default: no data (zeros)
    selected_data := (others => '0');
    
    -- Select data from the addressed peripheral
    for i in 0 to NUM_PERIPHERALS-1 loop
      if chip_select(i) = '1' then
        selected_data := data_i_peripheral(i);
      end if;
    end loop;
    
    data_o <= selected_data;
  end process;
  
  -- Interrupt handling - OR all peripheral interrupts into a single signal
  process(interrupt_i)
    variable temp_int : std_logic;
  begin
    temp_int := '0';
    
    for i in 0 to NUM_PERIPHERALS-1 loop
      temp_int := temp_int or interrupt_i(i);
    end loop;
    
    combined_int <= temp_int;
  end process;
  
  -- Interrupt output configuration based on COMBINE_INTERRUPTS flag
  g_combined_int: if COMBINE_INTERRUPTS generate
    -- When interrupts are combined, only the first bit is used
    interrupt_o(0) <= combined_int;
  end generate g_combined_int;
  
  g_separate_int: if not COMBINE_INTERRUPTS generate
    -- When interrupts are separate, forward all peripheral interrupts directly
    interrupt_o <= interrupt_i;
  end generate g_separate_int;
  
end architecture Behavioral;
