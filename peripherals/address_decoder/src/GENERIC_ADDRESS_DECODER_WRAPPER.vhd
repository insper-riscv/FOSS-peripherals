library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use work.types.all;

----------------------------------------------------------------------------------
-- Generic Address Decoder Wrapper
-- 
-- This wrapper provides a simpler interface to the generic_address_decoder
-- by converting individual generic parameters for base addresses and ranges
-- into the matrix and vector formats required by the decoder, so GHDL can
-- simulate it.
----------------------------------------------------------------------------------

entity generic_address_decoder_wrapper is
  generic (
    -- Bus width configuration
    DATA_WIDTH      : natural := 32;  -- Width of the data bus in bits
    ADDR_WIDTH      : natural := 32;  -- Width of the address bus in bits
    
    -- Number of peripherals
    NUM_PERIPHERALS : natural := 4;   -- Number of peripherals to connect
    
    -- Base address for each peripheral (can specify up to 8)
    BASE_ADDR_0     : natural := 0;      -- Base address for peripheral 0
    BASE_ADDR_1     : natural := 4096;   -- Base address for peripheral 1
    BASE_ADDR_2     : natural := 8192;   -- Base address for peripheral 2
    BASE_ADDR_3     : natural := 12288;  -- Base address for peripheral 3
    BASE_ADDR_4     : natural := 16384;  -- Base address for peripheral 4
    BASE_ADDR_5     : natural := 20480;  -- Base address for peripheral 5
    BASE_ADDR_6     : natural := 24576;  -- Base address for peripheral 6
    BASE_ADDR_7     : natural := 28672;  -- Base address for peripheral 7
    
    -- Memory range for each peripheral (in bytes, must be power of 2)
    ADDR_RANGE_0    : natural := 4096;   -- Address range for peripheral 0
    ADDR_RANGE_1    : natural := 4096;   -- Address range for peripheral 1
    ADDR_RANGE_2    : natural := 4096;   -- Address range for peripheral 2
    ADDR_RANGE_3    : natural := 4096;   -- Address range for peripheral 3
    ADDR_RANGE_4    : natural := 4096;   -- Address range for peripheral 4
    ADDR_RANGE_5    : natural := 4096;   -- Address range for peripheral 5
    ADDR_RANGE_6    : natural := 4096;   -- Address range for peripheral 6
    ADDR_RANGE_7    : natural := 4096;   -- Address range for peripheral 7
    
    -- Feature configuration
    COMBINE_INTERRUPTS : boolean := true;   -- True: combine all interrupts, False: keep separate
    ENABLE_DEBUG    : boolean := false      -- True: enable debug reporting in simulation
  );
  port (
    -- CPU interface
    data_i      : in  std_logic_vector(DATA_WIDTH-1 downto 0);  -- Data input from CPU
    address     : in  std_logic_vector(ADDR_WIDTH-1 downto 0);  -- Address from CPU
    data_o      : out std_logic_vector(DATA_WIDTH-1 downto 0);  -- Data output to CPU
    wr          : in  std_logic;                                -- Write enable from CPU
    rd          : in  std_logic;                                -- Read enable from CPU
    interrupt_o : out std_logic_vector(0 to NUM_PERIPHERALS-1); -- Interrupt output to CPU

    -- Peripheral interface
    data_o_peripheral : out std_logic_vector(DATA_WIDTH-1 downto 0);                      -- Data to peripherals
    data_i_peripheral : in  DATA_MATRIX_T(0 to NUM_PERIPHERALS-1)(DATA_WIDTH-1 downto 0);   -- Data from peripherals
    wr_peripheral     : out std_logic_vector(NUM_PERIPHERALS-1 downto 0);                 -- Write enable to peripherals
    rd_peripheral     : out std_logic_vector(NUM_PERIPHERALS-1 downto 0);                 -- Read enable to peripherals
    interrupt_i       : in  std_logic_vector(NUM_PERIPHERALS-1 downto 0)                  -- Interrupts from peripherals
  );
end entity generic_address_decoder_wrapper;

architecture Behavioral of generic_address_decoder_wrapper is
  -- Convert individual base address generics to std_logic_vector constants
  constant BASE_ADDR_0_VEC : std_logic_vector(ADDR_WIDTH-1 downto 0) := std_logic_vector(to_unsigned(BASE_ADDR_0, ADDR_WIDTH));
  constant BASE_ADDR_1_VEC : std_logic_vector(ADDR_WIDTH-1 downto 0) := std_logic_vector(to_unsigned(BASE_ADDR_1, ADDR_WIDTH));
  constant BASE_ADDR_2_VEC : std_logic_vector(ADDR_WIDTH-1 downto 0) := std_logic_vector(to_unsigned(BASE_ADDR_2, ADDR_WIDTH));
  constant BASE_ADDR_3_VEC : std_logic_vector(ADDR_WIDTH-1 downto 0) := std_logic_vector(to_unsigned(BASE_ADDR_3, ADDR_WIDTH));
  constant BASE_ADDR_4_VEC : std_logic_vector(ADDR_WIDTH-1 downto 0) := std_logic_vector(to_unsigned(BASE_ADDR_4, ADDR_WIDTH));
  constant BASE_ADDR_5_VEC : std_logic_vector(ADDR_WIDTH-1 downto 0) := std_logic_vector(to_unsigned(BASE_ADDR_5, ADDR_WIDTH));
  constant BASE_ADDR_6_VEC : std_logic_vector(ADDR_WIDTH-1 downto 0) := std_logic_vector(to_unsigned(BASE_ADDR_6, ADDR_WIDTH));
  constant BASE_ADDR_7_VEC : std_logic_vector(ADDR_WIDTH-1 downto 0) := std_logic_vector(to_unsigned(BASE_ADDR_7, ADDR_WIDTH));

  -- Assemble base addresses into a matrix for the address decoder
  signal base_addresses : ADDR_MATRIX_T(0 to 7)(ADDR_WIDTH-1 downto 0) := (
    0 => BASE_ADDR_0_VEC,
    1 => BASE_ADDR_1_VEC,
    2 => BASE_ADDR_2_VEC,
    3 => BASE_ADDR_3_VEC,
    4 => BASE_ADDR_4_VEC,
    5 => BASE_ADDR_5_VEC,
    6 => BASE_ADDR_6_VEC,
    7 => BASE_ADDR_7_VEC
  );
  
  -- Assemble address ranges into a vector for the address decoder
  signal addr_ranges : NATURAL_ARRAY_T(0 to 7) := (
    0 => ADDR_RANGE_0,
    1 => ADDR_RANGE_1,
    2 => ADDR_RANGE_2,
    3 => ADDR_RANGE_3,
    4 => ADDR_RANGE_4,
    5 => ADDR_RANGE_5,
    6 => ADDR_RANGE_6,
    7 => ADDR_RANGE_7
  );
  
  -- Component declaration for the generic address decoder
  component generic_address_decoder is
    generic (
      DATA_WIDTH        : natural := 32;
      ADDR_WIDTH        : natural := 32;
      NUM_PERIPHERALS   : natural := 4;
      BASE_ADDRESSES    : ADDR_MATRIX_T;
      ADDR_RANGES       : NATURAL_ARRAY_T;
      COMBINE_INTERRUPTS : boolean := true;
      ENABLE_DEBUG      : boolean := false
    );
    port (
      -- CPU interface
      data_i            : in  std_logic_vector(DATA_WIDTH-1 downto 0);
      address           : in  std_logic_vector(ADDR_WIDTH-1 downto 0);
      data_o            : out std_logic_vector(DATA_WIDTH-1 downto 0);
      wr                : in  std_logic;
      rd                : in  std_logic;
      interrupt_o       : out std_logic_vector(0 to NUM_PERIPHERALS-1);

      -- Peripheral interface
      data_o_peripheral : out std_logic_vector(DATA_WIDTH-1 downto 0);
      data_i_peripheral : in  DATA_MATRIX_T(0 to NUM_PERIPHERALS-1)(DATA_WIDTH-1 downto 0);
      wr_peripheral     : out std_logic_vector(NUM_PERIPHERALS-1 downto 0);
      rd_peripheral     : out std_logic_vector(NUM_PERIPHERALS-1 downto 0);
      interrupt_i       : in  std_logic_vector(NUM_PERIPHERALS-1 downto 0)
    );
  end component;
  
begin
  -- Instantiate the address decoder with the configured parameters
  decoder: generic_address_decoder
    generic map (
      -- Pass through basic configuration
      DATA_WIDTH        => DATA_WIDTH,
      ADDR_WIDTH        => ADDR_WIDTH,
      NUM_PERIPHERALS   => NUM_PERIPHERALS,
      
      -- Map constructed matrices/vectors to decoder generics
      BASE_ADDRESSES    => base_addresses(0 to NUM_PERIPHERALS-1),
      ADDR_RANGES       => addr_ranges(0 to NUM_PERIPHERALS-1),
      
      -- Pass through feature configuration
      COMBINE_INTERRUPTS => COMBINE_INTERRUPTS,
      ENABLE_DEBUG      => ENABLE_DEBUG
    )
    port map (
      -- CPU interface connections
      data_i            => data_i,
      address           => address,
      data_o            => data_o,
      wr                => wr,
      rd                => rd,
      interrupt_o       => interrupt_o,
      
      -- Peripheral interface connections
      data_o_peripheral => data_o_peripheral,
      data_i_peripheral => data_i_peripheral,
      wr_peripheral     => wr_peripheral,
      rd_peripheral     => rd_peripheral,
      interrupt_i       => interrupt_i
    );
  
end architecture Behavioral;