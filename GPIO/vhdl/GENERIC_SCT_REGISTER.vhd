library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

library WORK;
use WORK.ALL;

entity GENERIC_SCT_REGISTER is
    generic (
        --! Largura dos vetores de dados
        DATA_WIDTH : natural := 8
    );
    port (
        --! Sinal de clock
        clock        : in  std_logic;
        --! Limpeza síncrona
        clear        : in  std_logic := '1';
        --! Habilita o registrador
        enable       : in  std_logic := '0';
        --! Flag Load (Write)
        write_enable : in  std_logic := '0';
        --! Dado de entrada
        source       : in  std_logic_vector(DATA_WIDTH-1 downto 0) := (others => '0');
        --! Operações bitwise
        set_enable    : in  std_logic := '0';
        clear_enable  : in  std_logic := '0';
        toggle_enable : in  std_logic := '0';
        --! Saída
        destination   : out std_logic_vector(DATA_WIDTH-1 downto 0)
    );
end entity GENERIC_SCT_REGISTER;

architecture RTL of GENERIC_SCT_REGISTER is

    --! Registrador interno
    signal reg_value : std_logic_vector(DATA_WIDTH-1 downto 0) := (others => '0');

    --! Seletor para o multiplexador 4x1
    signal sel : std_logic_vector(1 downto 0) := "00";

    --! Sinais de entrada para o MUX
    signal mux_input_1 : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal mux_input_2 : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal mux_input_3 : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal mux_input_4 : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal mux_output  : std_logic_vector(DATA_WIDTH-1 downto 0);

begin
    --! Saída do registrador
    destination <= reg_value;

    --! Definir os valores das entradas do MUX
    mux_input_1 <= source;               --! LOAD (00)
    mux_input_2 <= reg_value OR source;  --! SET (01)
    mux_input_3 <= reg_value AND NOT source; --! CLEAR (10)
    mux_input_4 <= reg_value XOR source; --! TOGGLE (11)

    sel(1) <= toggle_enable or clear_enable;
    sel(0) <= toggle_enable or set_enable;

    -- Instância do MUX 4x1
    MUX_INST: entity WORK.GENERIC_MUX_4X1
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            selector   => sel,
            source_1   => mux_input_1,
            source_2   => mux_input_2,
            source_3   => mux_input_3,
            source_4   => mux_input_4,
            destination => mux_output
        );

    -- Atualização do registrador no clock
    process(clock)
    begin
        if rising_edge(clock) then
            if enable = '1' then
                if clear = '1' then
                    reg_value <= (others => '0'); -- Reset
                else
                    reg_value <= mux_output; -- MUX Output
                end if;
            end if;
        end if;
    end process;

end architecture RTL;
