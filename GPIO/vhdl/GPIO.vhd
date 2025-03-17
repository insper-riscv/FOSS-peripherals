library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

library WORK;


entity GPIO is
    generic (
        --! Largura dos vetores de dados
        DATA_WIDTH : integer := 32
    );
    port (
        --! Clock do Processador
        clock       : in  std_logic;
        --! Reset Sincrono dos Registradores
        clear     : in  std_logic; 
        --! Vetor de dados de Entrada
        data_in  : in  STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0);
        --! Flag de Habilita Direção
        dir_enable   : in  STD_LOGIC;
        --! Flag de Habilita Escrita
        write_enable   : in  STD_LOGIC;
        --! Flag de Habilita Leitura
        read_enable   : in  STD_LOGIC;
        --! Vetor de dados de Saída
        data_out : out STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0);
        --! Pinos da GPIO
        gpio_pins : inout std_logic_vector(DATA_WIDTH-1 downto 0)
    );

end GPIO;

architecture RTL of GPIO is
    --! Controla each a direção de cada pino ('1' = output, '0' = input)
    signal dir_reg : std_logic_vector(DATA_WIDTH - 1 downto 0) := (others => '0');
    --! Guarda os valores de saída dos pinos
    signal out_reg : std_logic_vector(DATA_WIDTH-1 downto 0) := (others => '0');

begin

    --! Registrador que armazena a direção de cada pino.
    REG_DIR : GENERIC_REGISTER
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            clock       => clock,
            clear       => clear,
            enable      => dir_enable,
            source      => data_in,
            destination => dir_reg
        );

    --! Registrador que armazena os valores de saida de cada pino.
    REG_OUT : GENERIC_REGISTER
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            clock       => clock,
            clear       => clear,
            enable      => write_enable,
            source      => data_in,
            destination => out_reg
        );

    --! Registrador que armazena os valores de entrada de cada pino.
    REG_IN : GENERIC_REGISTER
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            clock       => clock,
            clear       => clear,
            enable      => read_enable,
            source      => gpio_pins,
            destination => data_out
        );
    
    --! Registrador que armazena os valores de entrada de cada pino.
    TRISTATE_BUFFER_GPIO : GENERIC_TRISTATE_BUFFER
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            data_in       => out_reg,
            enable       => dir_reg,
            data_out      => gpio_pins
        );
end architecture;