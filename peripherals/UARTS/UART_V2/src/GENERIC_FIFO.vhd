library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use IEEE.MATH_REAL.ALL;

entity generic_fifo is
    generic (
        DATA_WIDTH : natural := 8;
        FIFO_DEPTH : natural := 16  -- Must be power of 2
    );
    port (
        clk         : in  std_logic;
        reset       : in  std_logic;
        
        -- Write interface
        wr_en       : in  std_logic;
        wr_data     : in  std_logic_vector(DATA_WIDTH-1 downto 0);
        
        -- Read interface  
        rd_en       : in  std_logic;
        rd_data     : out std_logic_vector(DATA_WIDTH-1 downto 0);
        
        -- Status flags
        empty       : out std_logic;
        full        : out std_logic;
        almost_empty: out std_logic;  -- 1 item left
        almost_full : out std_logic;  -- 1 slot left
        
        -- Count (for debugging/monitoring)
        count       : out std_logic_vector(integer(ceil(log2(real(FIFO_DEPTH+1))))-1 downto 0)
    );
end entity generic_fifo;

architecture Behavioral of generic_fifo is
    constant ADDR_WIDTH : natural := integer(ceil(log2(real(FIFO_DEPTH))));
    
    type memory_type is array (0 to FIFO_DEPTH-1) of std_logic_vector(DATA_WIDTH-1 downto 0);
    signal memory : memory_type := (others => (others => '0'));
    
    signal wr_ptr : unsigned(ADDR_WIDTH-1 downto 0) := (others => '0');
    signal rd_ptr : unsigned(ADDR_WIDTH-1 downto 0) := (others => '0');
    signal fifo_count : unsigned(integer(ceil(log2(real(FIFO_DEPTH+1))))-1 downto 0) := (others => '0');
    
    signal empty_i : std_logic;
    signal full_i  : std_logic;
    
begin
    empty_i <= '1' when fifo_count = 0 else '0';
    full_i  <= '1' when fifo_count = FIFO_DEPTH else '0';
    
    empty <= empty_i;
    full  <= full_i;
    almost_empty <= '1' when fifo_count = 1 else '0';
    almost_full  <= '1' when fifo_count = (FIFO_DEPTH-1) else '0';
    count <= std_logic_vector(fifo_count);
    
    -- Memory read (combinatorial)
    rd_data <= memory(to_integer(rd_ptr));
    
    process(clk)
    begin
        if rising_edge(clk) then
            if reset = '1' then
                wr_ptr <= (others => '0');
                rd_ptr <= (others => '0');
                fifo_count <= (others => '0');
            else
                -- Handle write
                if wr_en = '1' and full_i = '0' then
                    memory(to_integer(wr_ptr)) <= wr_data;
                    wr_ptr <= wr_ptr + 1;
                end if;
                
                -- Handle read
                if rd_en = '1' and empty_i = '0' then
                    rd_ptr <= rd_ptr + 1;
                end if;
                
                -- Update count
                if (wr_en = '1' and full_i = '0') and (rd_en = '1' and empty_i = '0') then
                    -- Simultaneous read and write - count stays same
                    fifo_count <= fifo_count;
                elsif wr_en = '1' and full_i = '0' then
                    -- Write only
                    fifo_count <= fifo_count + 1;
                elsif rd_en = '1' and empty_i = '0' then
                    -- Read only
                    fifo_count <= fifo_count - 1;
                end if;
            end if;
        end if;
    end process;
    
end architecture Behavioral; 