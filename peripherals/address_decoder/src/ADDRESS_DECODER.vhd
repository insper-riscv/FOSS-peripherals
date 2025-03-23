library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

library WORK;
use work.GENERICS.all;

entity soc_top is
  port (
    clk      : in  std_logic;
    reset    : in  std_logic;
    -- System bus signals:
    address  : in  std_logic_vector(31 downto 0);
    data_in  : in  std_logic_vector(31 downto 0);
    data_out : out std_logic_vector(31 downto 0)
  );
end entity soc_top;

architecture Behavioral of soc_top is

  constant NUM_PERIPHERALS : natural := 5;

  -- Signal for the chip-select outputs from the address decoder.
  signal cs_signals : std_logic_vector(NUM_PERIPHERALS-1 downto 0);

  -- Signals to collect each peripheral's data output and acknowledge.
  signal ram_data_out   : std_logic_vector(31 downto 0);
  signal uart_data_out  : std_logic_vector(31 downto 0);
  signal pwm_data_out   : std_logic_vector(31 downto 0);
  signal gpio_data_out  : std_logic_vector(31 downto 0);
  signal timer_data_out : std_logic_vector(31 downto 0);

  signal ram_ack   : std_logic;
  signal uart_ack  : std_logic;
  signal pwm_ack   : std_logic;
  signal gpio_ack  : std_logic;
  signal timer_ack : std_logic;

  -- Component declarations:
  component addr_decoder is
    generic (
      ADDR_WIDTH : natural := 32;
      NUM_SLAVES : natural := 4;
      BASE_ADDR  : t_std_logic_array(0 to NUM_SLAVES-1);
      MASK       : t_std_logic_array(0 to NUM_SLAVES-1)
    );
    port (
      address : in  std_logic_vector(ADDR_WIDTH-1 downto 0);
      cs      : out std_logic_vector(NUM_SLAVES-1 downto 0)
    );
  end component;

  component generic_peripheral is
    generic (
      PERIPHERAL_ID : natural := 0;
      DATA_WIDTH    : natural := 32
    );
    port (
      clk      : in  std_logic;
      reset    : in  std_logic;
      cs       : in  std_logic;
      data_in  : in  std_logic_vector(DATA_WIDTH-1 downto 0);
      data_out : out std_logic_vector(DATA_WIDTH-1 downto 0);
      ack      : out std_logic
    );
  end component;

begin

  -----------------------------------------------------------------------------
  -- Instantiate the address decoder for 5 peripherals.
  -----------------------------------------------------------------------------
  addr_dec_inst : addr_decoder
    generic map (
      ADDR_WIDTH => 32,
      NUM_SLAVES => NUM_PERIPHERALS,
      BASE_ADDR  => (
         0 => x"00000000", -- RAM base address
         1 => x"00001000", -- UART base address
         2 => x"00002000", -- PWM base address
         3 => x"00003000", -- GPIO base address
         4 => x"00004000"  -- Timer base address
      ),
      MASK       => (
         0 => x"FFFFF000",
         1 => x"FFFFF000",
         2 => x"FFFFF000",
         3 => x"FFFFF000",
         4 => x"FFFFF000"
      )
    )
    port map (
      address => address,
      cs      => cs_signals
    );

  -----------------------------------------------------------------------------
  -- Instantiate the RAM peripheral.
  -----------------------------------------------------------------------------
  ram_inst : generic_peripheral
    generic map (
      PERIPHERAL_ID => 0,
      DATA_WIDTH    => 32
    )
    port map (
      clk      => clk,
      reset    => reset,
      cs       => cs_signals(0),
      data_in  => data_in,
      data_out => ram_data_out,
      ack      => ram_ack
    );

  -----------------------------------------------------------------------------
  -- Instantiate the UART peripheral.
  -----------------------------------------------------------------------------
  uart_inst : generic_peripheral
    generic map (
      PERIPHERAL_ID => 1,
      DATA_WIDTH    => 32
    )
    port map (
      clk      => clk,
      reset    => reset,
      cs       => cs_signals(1),
      data_in  => data_in,
      data_out => uart_data_out,
      ack      => uart_ack
    );

  -----------------------------------------------------------------------------
  -- Instantiate the PWM peripheral.
  -----------------------------------------------------------------------------
  pwm_inst : generic_peripheral
    generic map (
      PERIPHERAL_ID => 2,
      DATA_WIDTH    => 32
    )
    port map (
      clk      => clk,
      reset    => reset,
      cs       => cs_signals(2),
      data_in  => data_in,
      data_out => pwm_data_out,
      ack      => pwm_ack
    );

  -----------------------------------------------------------------------------
  -- Instantiate the GPIO peripheral.
  -----------------------------------------------------------------------------
  gpio_inst : generic_peripheral
    generic map (
      PERIPHERAL_ID => 3,
      DATA_WIDTH    => 32
    )
    port map (
      clk      => clk,
      reset    => reset,
      cs       => cs_signals(3),
      data_in  => data_in,
      data_out => gpio_data_out,
      ack      => gpio_ack
    );

  -----------------------------------------------------------------------------
  -- Instantiate the Timer peripheral.
  -----------------------------------------------------------------------------
  timer_inst : generic_peripheral
    generic map (
      PERIPHERAL_ID => 4,
      DATA_WIDTH    => 32
    )
    port map (
      clk      => clk,
      reset    => reset,
      cs       => cs_signals(4),
      data_in  => data_in,
      data_out => timer_data_out,
      ack      => timer_ack
    );

  -----------------------------------------------------------------------------
  -- Example Bus Read Multiplexer:
  -- This process selects which peripheral's data is forwarded to the system bus
  -- based on which device acknowledges the access.
  -----------------------------------------------------------------------------
  process(ram_ack, uart_ack, pwm_ack, gpio_ack, timer_ack,
          ram_data_out, uart_data_out, pwm_data_out, gpio_data_out, timer_data_out)
  begin
    if ram_ack = '1' then
      data_out <= ram_data_out;
    elsif uart_ack = '1' then
      data_out <= uart_data_out;
    elsif pwm_ack = '1' then
      data_out <= pwm_data_out;
    elsif gpio_ack = '1' then
      data_out <= gpio_data_out;
    elsif timer_ack = '1' then
      data_out <= timer_data_out;
    else
      data_out <= (others => '0');
    end if;
  end process;

end architecture Behavioral;
