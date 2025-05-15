library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use work.types.all;

entity generic_address_decoder_wrapper is
  generic (
    -- Data bus width
    DATA_WIDTH      : natural := 32;
    -- Width of the address bus
    ADDR_WIDTH      : natural := 32;
    -- Number of peripherals to decode
    NUM_PERIPHERALS : natural := 4;
    -- Individual base addresses (up to 8 peripherals)
    BASE_ADDR_0     : natural := 0;
    BASE_ADDR_1     : natural := 4096;
    BASE_ADDR_2     : natural := 8192;
    BASE_ADDR_3     : natural := 12288;
    BASE_ADDR_4     : natural := 16384;
    BASE_ADDR_5     : natural := 20480;
    BASE_ADDR_6     : natural := 24576;
    BASE_ADDR_7     : natural := 28672;
    -- Individual address ranges
    ADDR_RANGE_0    : natural := 4096;
    ADDR_RANGE_1    : natural := 4096;
    ADDR_RANGE_2    : natural := 4096;
    ADDR_RANGE_3    : natural := 4096;
    ADDR_RANGE_4    : natural := 4096;
    ADDR_RANGE_5    : natural := 4096;
    ADDR_RANGE_6    : natural := 4096;
    ADDR_RANGE_7    : natural := 4096;
    -- Whether to combine interrupts into a single signal
    COMBINE_INTERRUPTS : boolean := true;
    -- Whether to enable debug reporting
    ENABLE_DEBUG    : boolean := false
  );
  port (
    -- CPU interface
    data_i      : in  std_logic_vector(DATA_WIDTH-1 downto 0);  -- Data input from CPU
    address     : in  std_logic_vector(ADDR_WIDTH-1 downto 0);  -- Address from CPU
    data_o      : out std_logic_vector(DATA_WIDTH-1 downto 0);  -- Data output to CPU
    wr          : in  std_logic;                              -- Write enable from CPU
    rd          : in  std_logic;                              -- Read enable from CPU
    interrupt_o : out std_logic_vector(0 to NUM_PERIPHERALS-1); -- Interrupt output to CPU

    -- Peripheral interface
    data_o_peripheral : out std_logic_vector(DATA_WIDTH-1 downto 0);                  -- Data to peripherals
    data_i_peripheral : in  data_matrix(0 to NUM_PERIPHERALS-1)(DATA_WIDTH-1 downto 0);  -- Data from peripherals
    wr_peripheral     : out std_logic_vector(NUM_PERIPHERALS-1 downto 0);             -- Write enable to peripherals
    rd_peripheral     : out std_logic_vector(NUM_PERIPHERALS-1 downto 0);             -- Read enable to peripherals
    interrupt_i       : in  std_logic_vector(NUM_PERIPHERALS-1 downto 0)              -- Interrupts from peripherals
  );
end entity generic_address_decoder_wrapper;

architecture Behavioral of generic_address_decoder_wrapper is
  constant base_addr_0_vec : std_logic_vector(ADDR_WIDTH-1 downto 0) := std_logic_vector(to_unsigned(BASE_ADDR_0, ADDR_WIDTH));
  constant base_addr_1_vec : std_logic_vector(ADDR_WIDTH-1 downto 0) := std_logic_vector(to_unsigned(BASE_ADDR_1, ADDR_WIDTH));
  constant base_addr_2_vec : std_logic_vector(ADDR_WIDTH-1 downto 0) := std_logic_vector(to_unsigned(BASE_ADDR_2, ADDR_WIDTH));
  constant base_addr_3_vec : std_logic_vector(ADDR_WIDTH-1 downto 0) := std_logic_vector(to_unsigned(BASE_ADDR_3, ADDR_WIDTH));
  constant base_addr_4_vec : std_logic_vector(ADDR_WIDTH-1 downto 0) := std_logic_vector(to_unsigned(BASE_ADDR_4, ADDR_WIDTH));
  constant base_addr_5_vec : std_logic_vector(ADDR_WIDTH-1 downto 0) := std_logic_vector(to_unsigned(BASE_ADDR_5, ADDR_WIDTH));
  constant base_addr_6_vec : std_logic_vector(ADDR_WIDTH-1 downto 0) := std_logic_vector(to_unsigned(BASE_ADDR_6, ADDR_WIDTH));
  constant base_addr_7_vec : std_logic_vector(ADDR_WIDTH-1 downto 0) := std_logic_vector(to_unsigned(BASE_ADDR_7, ADDR_WIDTH));

  signal base_addresses : addr_matrix(0 to 7)(ADDR_WIDTH-1 downto 0) := (
    0 => base_addr_0_vec,
    1 => base_addr_1_vec,
    2 => base_addr_2_vec,
    3 => base_addr_3_vec,
    4 => base_addr_4_vec,
    5 => base_addr_5_vec,
    6 => base_addr_6_vec,
    7 => base_addr_7_vec
  );
  
  -- Initialize address ranges directly
  signal addr_ranges : natural_vector(0 to 7) := (
    0 => ADDR_RANGE_0,
    1 => ADDR_RANGE_1,
    2 => ADDR_RANGE_2,
    3 => ADDR_RANGE_3,
    4 => ADDR_RANGE_4,
    5 => ADDR_RANGE_5,
    6 => ADDR_RANGE_6,
    7 => ADDR_RANGE_7
  );
  
  component generic_address_decoder is
    generic (
      DATA_WIDTH        : natural := 32;
      ADDR_WIDTH        : natural := 32;
      NUM_PERIPHERALS   : natural := 4;
      BASE_ADDRESSES    : addr_matrix;
      ADDR_RANGES       : natural_vector;
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
      data_i_peripheral : in  data_matrix(0 to NUM_PERIPHERALS-1)(DATA_WIDTH-1 downto 0);
      wr_peripheral     : out std_logic_vector(NUM_PERIPHERALS-1 downto 0);
      rd_peripheral     : out std_logic_vector(NUM_PERIPHERALS-1 downto 0);
      interrupt_i       : in  std_logic_vector(NUM_PERIPHERALS-1 downto 0)
    );
  end component;
  
begin
  -- Instantiate the actual decoder with the constructed arrays
  decoder: generic_address_decoder
    generic map (
      DATA_WIDTH        => DATA_WIDTH,
      ADDR_WIDTH        => ADDR_WIDTH,
      NUM_PERIPHERALS   => NUM_PERIPHERALS,
      BASE_ADDRESSES    => base_addresses(0 to NUM_PERIPHERALS-1),
      ADDR_RANGES       => addr_ranges(0 to NUM_PERIPHERALS-1),
      COMBINE_INTERRUPTS => COMBINE_INTERRUPTS,
      ENABLE_DEBUG      => ENABLE_DEBUG
    )
    port map (
      data_i            => data_i,
      address           => address,
      data_o            => data_o,
      wr                => wr,
      rd                => rd,
      interrupt_o       => interrupt_o,
      
      data_o_peripheral => data_o_peripheral,
      data_i_peripheral => data_i_peripheral,
      wr_peripheral     => wr_peripheral,
      rd_peripheral     => rd_peripheral,
      interrupt_i       => interrupt_i
    );
  
end architecture Behavioral;