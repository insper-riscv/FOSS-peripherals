library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use IEEE.MATH_REAL.ALL;

entity generic_uart_rx_fifo is
    generic (
        DATA_BITS     : integer := 8;
        FIFO_DEPTH    : natural := 16;
        RX_THRESHOLD  : natural := 4    -- Configurable RX threshold
    );
    port (
        clk            : in  std_logic;
        reset          : in  std_logic;
        
        -- UART Interface
        rx_i           : in  std_logic;
        baud_tick_i    : in  std_logic;
        
        -- CPU Interface
        rx_data_o      : out std_logic_vector(DATA_BITS-1 downto 0);
        read_strobe_i  : in  std_logic;
        
        -- Status
        rx_empty_o     : out std_logic;  -- FIFO is empty
        rx_full_o      : out std_logic;  -- FIFO is full (overrun condition)
        rx_almost_full_o : out std_logic; -- FIFO almost full
        rx_data_ready_o : out std_logic; -- Data available to read
        
        -- Error flags
        parity_error_o : out std_logic;  -- Latest parity error
        frame_error_o  : out std_logic;  -- Latest frame error  
        overrun_error_o: out std_logic;  -- FIFO overrun occurred
        
        -- Enhanced status for interrupts
        rx_threshold_o : out std_logic   -- FIFO above threshold (interrupt trigger)
    );
end entity generic_uart_rx_fifo;

architecture Structural of generic_uart_rx_fifo is
    -- Calculate count width based on FIFO depth
    constant COUNT_WIDTH : natural := integer(ceil(log2(real(FIFO_DEPTH+1))));
    
    -- Validate threshold parameter
    constant VALIDATED_THRESHOLD : natural := 
        RX_THRESHOLD when RX_THRESHOLD <= FIFO_DEPTH else FIFO_DEPTH;
    
    -- FIFO signals
    signal fifo_wr_en     : std_logic;
    signal fifo_wr_data   : std_logic_vector(DATA_BITS-1 downto 0);
    signal fifo_empty     : std_logic;
    signal fifo_full      : std_logic;
    signal fifo_almost_full : std_logic;
    signal fifo_count     : std_logic_vector(COUNT_WIDTH-1 downto 0);
    
    -- RX core signals
    signal rx_core_data   : std_logic_vector(DATA_BITS-1 downto 0);
    signal rx_core_ready  : std_logic;
    signal rx_core_parity_error : std_logic;
    
    -- Error handling
    signal overrun_error  : std_logic := '0';
    signal frame_error    : std_logic := '0';
    
    -- Edge detection for rx_core_ready
    signal rx_ready_prev  : std_logic := '0';
    signal rx_ready_edge  : std_logic;
    
begin
    -- Status outputs
    rx_empty_o <= fifo_empty;
    rx_full_o <= fifo_full;
    rx_almost_full_o <= fifo_almost_full;
    rx_data_ready_o <= not fifo_empty;
    
    -- Error outputs
    parity_error_o <= rx_core_parity_error;
    frame_error_o <= frame_error;
    overrun_error_o <= overrun_error;
    
    -- Configurable threshold detection (trigger interrupt when FIFO has threshold or more items)
    rx_threshold_o <= '1' when unsigned(fifo_count) >= VALIDATED_THRESHOLD else '0';
    
    -- Edge detection for new received data
    rx_ready_edge <= rx_core_ready and not rx_ready_prev;
    
    -- FIFO write control
    fifo_wr_en <= rx_ready_edge and not fifo_full;
    fifo_wr_data <= rx_core_data;
    
    -- FIFO instance
    rx_fifo : entity work.generic_fifo
        generic map (
            DATA_WIDTH => DATA_BITS,
            FIFO_DEPTH => FIFO_DEPTH
        )
        port map (
            clk         => clk,
            reset       => reset,
            wr_en       => fifo_wr_en,
            wr_data     => fifo_wr_data,
            rd_en       => read_strobe_i,
            rd_data     => rx_data_o,
            empty       => fifo_empty,
            full        => fifo_full,
            almost_empty=> open,
            almost_full => fifo_almost_full,
            count       => fifo_count
        );
    
    -- Original RX core (reused)
    rx_core : entity work.generic_uart_rx
        generic map (
            DATA_BITS => DATA_BITS
        )
        port map (
            clk            => clk,
            reset          => reset,
            rx_i           => rx_i,
            baud_tick_i    => baud_tick_i,
            rx_data_o      => rx_core_data,
            rx_ready_o     => rx_core_ready,
            read_strobe_i  => '0',  -- We handle the data automatically
            parity_error_o => rx_core_parity_error
        );
    
    -- Error detection and edge detection process
    process(clk)
    begin
        if rising_edge(clk) then
            if reset = '1' then
                rx_ready_prev <= '0';
                overrun_error <= '0';
                frame_error <= '0';
            else
                -- Edge detection
                rx_ready_prev <= rx_core_ready;
                
                -- Overrun error: new data arrived but FIFO is full
                if rx_ready_edge = '1' and fifo_full = '1' then
                    overrun_error <= '1';
                end if;
                
                -- Frame error detection (could be enhanced with stop bit checking)
                -- For now, we'll keep it simple and let the core RX handle it
                
                -- Clear overrun error when read
                if read_strobe_i = '1' then
                    overrun_error <= '0';
                end if;
            end if;
        end if;
    end process;
    
end architecture Structural; 