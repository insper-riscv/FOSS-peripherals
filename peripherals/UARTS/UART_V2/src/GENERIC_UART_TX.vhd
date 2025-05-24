library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity generic_uart_tx is
    generic (
        DATA_BITS : integer := 8
    );
    port (
        clk            : in  std_logic;
        reset          : in  std_logic;
        tx_data_i      : in  std_logic_vector(DATA_BITS-1 downto 0);
        write_strobe_i : in  std_logic;
        baud_tick_i    : in  std_logic;
        tx_o           : out std_logic;
        tx_ready_o     : out std_logic
    );
end entity generic_uart_tx;

architecture Behavioral of generic_uart_tx is
    type tx_state_t is (IDLE, START, DATA, PARITY, STOP);
    signal tx_state     : tx_state_t := IDLE;
    signal tx_reg       : std_logic_vector(DATA_BITS-1 downto 0) := (others => '0');
    signal bit_index    : integer range 0 to DATA_BITS-1 := 0;
    signal parity_bit   : std_logic := '0';
    signal tx_line      : std_logic := '1'; -- UART idle state is high
    signal tx_ready     : std_logic := '1'; -- Ready to send data
begin
    tx_o <= tx_line;
    tx_ready_o <= tx_ready;

    process(clk)
    begin
        if rising_edge(clk) then
            if reset = '1' then
                tx_state     <= IDLE;
                tx_reg       <= (others => '0');
                bit_index    <= 0;
                parity_bit   <= '0';
                tx_line      <= '1';
                tx_ready     <= '1';
            elsif write_strobe_i = '1' and tx_ready = '1' then
                -- Load data into the shift register
                tx_reg     <= tx_data_i;
                parity_bit <= '0';
                bit_index  <= 0;
                tx_ready   <= '0';
                tx_state   <= START;
            elsif baud_tick_i = '1' then
                case tx_state is
                    when START =>
                        tx_line <= '0'; -- Start bit
                        tx_state <= DATA;
                    when DATA =>
                        tx_line <= tx_reg(bit_index);
                        parity_bit <= parity_bit xor tx_reg(bit_index);
                        if bit_index = DATA_BITS-1 then
                            tx_state <= PARITY;
                        else
                            bit_index <= bit_index + 1;
                        end if;
                    when PARITY =>
                        tx_line <= parity_bit; -- Parity bit
                        tx_state <= STOP;
                    when STOP =>
                        tx_line <= '1'; -- Stop bit
                        tx_ready <= '1'; -- Ready for next data
                        tx_state <= IDLE;
                    when others =>
                        tx_state <= IDLE;
                end case;
            end if;
        end if;
    end process;
end architecture Behavioral;