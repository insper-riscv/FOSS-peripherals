library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity generic_peripheral is
  generic (
    -- An identifier for this peripheral; used for generating a unique response.
    PERIPHERAL_ID : natural := 0;
    -- Width of the data bus.
    DATA_WIDTH    : natural := 32
  );
  port (
    clk      : in  std_logic;
    reset    : in  std_logic;
    -- Chip-select input from the address decoder.
    cs       : in  std_logic;
    -- Data input bus (if writing is required in a real design).
    data_in  : in  std_logic_vector(DATA_WIDTH-1 downto 0);
    -- Data output bus (used when reading from the peripheral).
    data_out : out std_logic_vector(DATA_WIDTH-1 downto 0);
    -- Acknowledge signal to indicate a successful access.
    ack      : out std_logic
  );
end entity generic_peripheral;

architecture Behavioral of generic_peripheral is
begin
  -- This process demonstrates a simple behavior:
  -- When reset is active, outputs are cleared.
  -- On a rising clock edge, if the chip-select is asserted,
  -- the peripheral produces a response that encodes its PERIPHERAL_ID.
  process(clk, reset)
  begin
    if reset = '1' then
      data_out <= (others => '0');
      ack      <= '0';
    elsif rising_edge(clk) then
      if cs = '1' then
        ack      <= '1';
        -- Output a constant value based on the peripheral ID.
        data_out <= std_logic_vector(to_unsigned(PERIPHERAL_ID, DATA_WIDTH));
      else
        ack      <= '0';
        data_out <= (others => '0');
      end if;
    end if;
  end process;
  
end architecture Behavioral;
