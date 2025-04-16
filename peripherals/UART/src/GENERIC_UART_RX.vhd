library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity generic_uart_rx is
    generic (
        DATA_BITS : integer := 8;
    );
    port (
        clk            : in  std_logic;
        reset          : in  std_logic;
        rx_i           : in  std_logic;
        baud_tick_i    : in  std_logic;
        rx_data_o      : out std_logic_vector(DATA_BITS-1 downto 0);
        rx_ready_o     : out std_logic;
        read_strobe_i  : in  std_logic;
        parity_error_o : out std_logic
    );
end entity generic_uart_rx;

architecture Behavioral of generic_uart_rx is
    type rx_state_t is (IDLE, START, DATA, PARITY ,STOP);
    signal rx_state     : rx_state_t := IDLE;
    signal bit_index    : integer range 0 to DATA_BITS-1 := 0;
    signal rx_shift_reg : std_logic_vector(DATA_BITS-1 downto 0) := (others => '0');
    signal rx_data_buf  : std_logic_vector(DATA_BITS-1 downto 0) := (others => '0');
    signal rx_ready     : std_logic := '0';
    signal parity_bit   : std_logic := '0';
    signal parity_error : std_logic := '0';
begin
    rx_data_o <= rx_data_buf;
    rx_ready_o <= rx_ready;
    parity_error_o <= parity_error;

    process(clk)
    begin
        if rising_edge(clk) then
            if reset = '1' then
                rx_state     <= IDLE;
                bit_index    <= 0;
                rx_shift_reg <= (others => '0');
                rx_data_buf  <= (others => '0');
                rx_ready     <= '0';
            elsif read_strobe_i = '1' then
                rx_ready <= '0';
            elsif baud_tick_i = '1' then
                case rx_state is
                    when IDLE =>
                        if rx_i = '0' then -- Start bit detected
                            rx_state <= START;
                        end if;
                    when START =>
                        -- Wait for the start bit to stabilize
                        if rx_i = '0' then
                            bit_index <= 0;
                            parity_bit <= '0';
                            rx_state <= DATA;
                        else
                            rx_state <= IDLE; -- False start bit
                        end if;
                    when DATA =>
                        rx_shift_reg(bit_index) <= rx_i;
                        parity_bit <= parity_bit xor rx_i; -- Calculate parity
                        if bit_index = DATA_BITS-1 then
                            rx_state <= PARITY;
                        else
                            bit_index <= bit_index + 1;
                        end if;
                    when PARITY =>
                        -- Even parity check
                        if rx_i /= parity_bit then
                            parity_error <= '1'; -- Parity error detected
                        else
                            parity_error <= '0'; -- No parity error
                        end if;
                        rx_state <= STOP; -- Move to STOP state
                    when STOP =>
                        if rx_i = '1' then -- Valid stop bit
                            rx_data_buf <= rx_shift_reg;
                            rx_ready <= '1';
                        end if;
                        rx_state <= IDLE; -- Go back to IDLE state
                end case;
            end if;
        end if;
    end process;
end architecture Behavioral;