library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use IEEE.MATH_REAL.ALL;

entity generic_uart_tx_fifo is
    generic (
        DATA_BITS     : integer := 8;
        FIFO_DEPTH    : natural := 16;
        TX_THRESHOLD  : natural := 4    -- Configurable TX threshold
    );
    port (
        clk            : in  std_logic;
        reset          : in  std_logic;
        
        -- CPU Interface
        tx_data_i      : in  std_logic_vector(DATA_BITS-1 downto 0);
        write_strobe_i : in  std_logic;
        
        -- UART Interface
        baud_tick_i    : in  std_logic;
        tx_o           : out std_logic;
        
        -- Status
        tx_busy_o      : out std_logic;  -- Transmitter is sending
        tx_empty_o     : out std_logic;  -- FIFO is empty
        tx_full_o      : out std_logic;  -- FIFO is full
        tx_almost_full_o : out std_logic; -- FIFO almost full (flow control)
        
        -- Enhanced status for interrupts
        tx_threshold_o : out std_logic   -- FIFO below threshold (interrupt trigger)
    );
end entity generic_uart_tx_fifo;

architecture Structural of generic_uart_tx_fifo is
    -- Calculate count width based on FIFO depth
    constant COUNT_WIDTH : natural := integer(ceil(log2(real(FIFO_DEPTH+1))));
    
    -- Validate threshold parameter
    constant VALIDATED_THRESHOLD : natural := 
        TX_THRESHOLD when TX_THRESHOLD <= FIFO_DEPTH else FIFO_DEPTH;
    
    -- FIFO signals
    signal fifo_rd_en     : std_logic;
    signal fifo_rd_data   : std_logic_vector(DATA_BITS-1 downto 0);
    signal fifo_empty     : std_logic;
    signal fifo_full      : std_logic;
    signal fifo_almost_full : std_logic;
    signal fifo_count     : std_logic_vector(COUNT_WIDTH-1 downto 0);
    
    -- TX core signals
    signal tx_core_ready  : std_logic;
    signal tx_core_start  : std_logic;
    signal tx_core_busy   : std_logic;
    
    -- State machine for FIFO to TX core interface
    type tx_ctrl_state_t is (IDLE, LOAD_TX, WAIT_TX);
    signal tx_ctrl_state : tx_ctrl_state_t := IDLE;
    
begin
    -- Status outputs
    tx_empty_o <= fifo_empty;
    tx_full_o <= fifo_full;
    tx_almost_full_o <= fifo_almost_full;
    tx_busy_o <= tx_core_busy;
    
    -- Configurable threshold detection (trigger interrupt when FIFO has threshold or fewer items)
    tx_threshold_o <= '1' when unsigned(fifo_count) <= VALIDATED_THRESHOLD else '0';
    
    -- FIFO instance
    tx_fifo : entity work.generic_fifo
        generic map (
            DATA_WIDTH => DATA_BITS,
            FIFO_DEPTH => FIFO_DEPTH
        )
        port map (
            clk         => clk,
            reset       => reset,
            wr_en       => write_strobe_i,
            wr_data     => tx_data_i,
            rd_en       => fifo_rd_en,
            rd_data     => fifo_rd_data,
            empty       => fifo_empty,
            full        => fifo_full,
            almost_empty=> open,
            almost_full => fifo_almost_full,
            count       => fifo_count
        );
    
    -- Original TX core (reused)
    tx_core : entity work.generic_uart_tx
        generic map (
            DATA_BITS => DATA_BITS
        )
        port map (
            clk            => clk,
            reset          => reset,
            tx_data_i      => fifo_rd_data,
            write_strobe_i => tx_core_start,
            baud_tick_i    => baud_tick_i,
            tx_o           => tx_o,
            tx_ready_o     => tx_core_ready
        );
    
    tx_core_busy <= not tx_core_ready;
    
    -- Control FSM: manages data flow from FIFO to TX core
    process(clk)
    begin
        if rising_edge(clk) then
            if reset = '1' then
                tx_ctrl_state <= IDLE;
                fifo_rd_en <= '0';
                tx_core_start <= '0';
            else
                -- Default values
                fifo_rd_en <= '0';
                tx_core_start <= '0';
                
                case tx_ctrl_state is
                    when IDLE =>
                        -- Start transmission if FIFO has data and TX core is ready
                        if fifo_empty = '0' and tx_core_ready = '1' then
                            fifo_rd_en <= '1';  -- Read from FIFO
                            tx_ctrl_state <= LOAD_TX;
                        end if;
                        
                    when LOAD_TX =>
                        -- FIFO data is now available, start TX core
                        tx_core_start <= '1';
                        tx_ctrl_state <= WAIT_TX;
                        
                    when WAIT_TX =>
                        -- Wait for TX core to complete
                        if tx_core_ready = '1' then
                            tx_ctrl_state <= IDLE;
                        end if;
                end case;
            end if;
        end if;
    end process;
    
end architecture Structural; 