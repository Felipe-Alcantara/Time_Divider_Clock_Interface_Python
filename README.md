# Divisão de Atividades em um Relógio com Interface Gráfica

Este projeto em Python permite visualizar a distribuição de atividades em um relógio analógico, utilizando uma interface gráfica amigável desenvolvida com Tkinter. O programa ajuda a planejar e gerenciar o tempo de forma eficiente, representando graficamente o tempo alocado para cada atividade dentro de um período especificado.

## Índice

- [Introdução](#introdução)
- [Como Funciona](#como-funciona)
- [Requisitos](#requisitos)
- [Instalação e Uso](#instalação-e-uso)
- [Exemplo de Uso](#exemplo-de-uso)
- [Como o Projeto Foi Desenvolvido](#como-o-projeto-foi-desenvolvido)
- [Utilidade do Projeto](#utilidade-do-projeto)
- [Possíveis Melhorias Futuras](#possíveis-melhorias-futuras)
- [Licença](#licença)
- [Agradecimentos](#agradecimentos)

## Introdução

Gerenciar o tempo é essencial para aumentar a produtividade e alcançar um equilíbrio entre as diversas atividades do dia a dia. Este programa oferece uma forma visual e interativa de planejar o seu tempo, permitindo que você divida um período específico entre várias atividades e visualize essa divisão em um relógio analógico.

## Como Funciona

### Interface Gráfica

- **Tkinter**: A interface gráfica é construída usando a biblioteca Tkinter, que é a biblioteca padrão do Python para GUI.
- **Campos de Entrada**:
  - **Horário de Início**: Campo para inserir o horário de início no formato `HH:MM`. Se deixado em branco, o programa usa o horário atual.
  - **Tempo Total Disponível**: Campo para inserir o tempo total disponível no formato `HH:MM`. O usuário pode inserir apenas as horas (`H`), apenas os minutos (`:MM`), ou ambos.
  - **Atividades**: Campo para inserir a lista de atividades, separadas por vírgula.

### Processamento dos Dados

1. **Validação de Entradas**:
   - **Horário de Início**: Verifica se está no formato correto `HH:MM`.
   - **Tempo Total Disponível**: Converte o tempo total para horas decimais, aceitando entradas como `1:30` (1 hora e 30 minutos).
   - **Atividades**: Garante que pelo menos uma atividade foi inserida e que não há atividades duplicadas.

2. **Cálculo do Tempo por Atividade**:
   - O tempo total disponível é dividido igualmente entre as atividades inseridas.
   - Calcula os horários de início e término para cada atividade.

3. **Conversão de Horário para Ângulo**:
   - Cada horário é convertido em um ângulo para ser representado no relógio.
   - Utiliza a função `hora_para_angulo_graus` para converter o horário em graus, considerando que o relógio avança no sentido horário.

### Geração do Gráfico

- **Desenho do Relógio**:
  - Utiliza o `matplotlib` para desenhar um relógio analógico.
  - Marcações das horas e números são adicionados para maior clareza.

- **Representação das Atividades**:
  - Cada atividade é representada por um setor colorido correspondente ao tempo alocado.
  - Cores distintas são geradas automaticamente para cada atividade utilizando um mapa de cores (`colormap`).

- **Anotações**:
  - Os nomes das atividades e seus horários de início e término são exibidos ao redor do relógio.
  - Uma legenda é adicionada para identificar as cores correspondentes a cada atividade.

- **Exibição e Salvamento**:
  - O gráfico é exibido em uma janela separada.
  - Opcionalmente, o gráfico é salvo como uma imagem PNG com um timestamp no nome do arquivo.

## Requisitos

- **Python 3.x**
- **Bibliotecas Python**:
  - `matplotlib`
  - `numpy`
  - `tkinter` (já incluído na instalação padrão do Python)

## Instalação e Uso

1. **Clone ou Baixe o Repositório**.

2. **Instale as Dependências**:
   ```bash
   pip install matplotlib numpy
   ```
   *Observação*: A biblioteca `tkinter` geralmente já está incluída na instalação padrão do Python. Se estiver usando Linux e não tiver o `tkinter`, instale-o via gerenciador de pacotes:
   - **Ubuntu/Debian**:
     ```bash
     sudo apt-get install python3-tk
     ```
   - **Fedora**:
     ```bash
     sudo dnf install python3-tkinter
     ```

3. **Execute o Script**:
   ```bash
   python nome_do_script.py
   ```
   *Substitua `nome_do_script.py` pelo nome real do arquivo que contém o código.*

4. **Utilize a Interface Gráfica**:
   - **Horário de Início (HH:MM)**:
     - Insira o horário de início no formato `HH:MM`.
     - Se deixado em branco, o programa utilizará o horário atual.
   - **Tempo Total Disponível (HH:MM)**:
     - Insira o tempo total disponível no formato `HH:MM`.
     - Você pode inserir apenas as horas (`H`), apenas os minutos (`:MM`), ou ambos.
     - Exemplo: `2:30` para 2 horas e 30 minutos.
   - **Atividades (separadas por vírgula)**:
     - Insira a lista de atividades separadas por vírgula.
     - Exemplo: `Estudar, Exercício, Lazer`.

5. **Gere o Gráfico**:
   - Clique no botão **"Gerar Gráfico"**.
   - O gráfico será exibido em uma nova janela, e uma imagem será salva no diretório atual com o nome `divisao_tempo_relogio_YYYY-MM-DD_HH-MM-SS.png`.

## Exemplo de Uso

Suponha que você queira planejar um período de 3 horas, dividindo-o igualmente entre três atividades: `Estudar`, `Exercício` e `Lazer`.

1. **Horário de Início**: `14:00`
2. **Tempo Total Disponível**: `3:00`
3. **Atividades**: `Estudar, Exercício, Lazer`

Após clicar em **"Gerar Gráfico"**, o programa exibirá um relógio mostrando cada atividade ocupando uma hora, com setores coloridos e horários anotados.

## Como o Projeto Foi Desenvolvido

### Conceito e Planejamento

- **Objetivo**: Criar uma ferramenta visual e interativa para auxiliar no gerenciamento do tempo, facilitando o planejamento de atividades.
- **Abordagem**: Desenvolver uma interface gráfica simples e intuitiva que permita ao usuário inserir os dados necessários e visualizar a distribuição do tempo em um relógio analógico.

### Desenvolvimento

#### Interface Gráfica (Tkinter)

- **Layout**:
  - Utiliza `ttk` para widgets com um estilo moderno.
  - Organiza os elementos em um `Frame` com labels e campos de entrada.
  - Adiciona dicas e exemplos ao lado dos campos de entrada para orientar o usuário.

- **Componentes Principais**:
  - **Entrada de Horário de Início**: Permite ao usuário inserir o horário de início ou deixar em branco para usar o horário atual.
  - **Entrada de Tempo Total Disponível**: Aceita o tempo total no formato `HH:MM`.
  - **Entrada de Atividades**: Campo para inserir as atividades separadas por vírgula.
  - **Botão "Gerar Gráfico"**: Inicia o processamento dos dados e gera o gráfico.

#### Processamento dos Dados

- **Validação**:
  - Utiliza estruturas `try-except` para capturar e informar erros ao usuário de forma amigável.
  - Verifica se os campos estão preenchidos corretamente e se os valores são válidos.

- **Cálculos**:
  - Converte o tempo total disponível em horas decimais.
  - Divide o tempo total igualmente entre as atividades.
  - Calcula os horários de início e término para cada atividade usando `datetime.timedelta`.

- **Conversão de Horário para Ângulo**:
  - Cada hora no relógio corresponde a 30 graus (360 graus / 12 horas).
  - A função `hora_para_angulo_graus` ajusta o horário ao formato de 12 horas e calcula o ângulo correspondente, considerando o sentido horário do relógio.

#### Geração do Gráfico (Matplotlib)

- **Desenho do Relógio**:
  - Desenha um círculo representando o relógio.
  - Adiciona marcações e números das horas.

- **Representação das Atividades**:
  - Utiliza a classe `Wedge` para desenhar setores correspondentes às atividades.
  - Os setores são desenhados com base nos ângulos calculados para os horários de início e término.
  - Cores são atribuídas a cada atividade usando um mapa de cores (`colormap`), garantindo distinção entre elas.

- **Anotações e Legenda**:
  - Os nomes das atividades e seus horários são posicionados ao redor do relógio, próximos aos setores correspondentes.
  - Uma legenda é adicionada para facilitar a identificação das atividades e suas cores.

- **Exibição e Salvamento**:
  - O gráfico é exibido em uma janela separada usando `plt.show()`.
  - O gráfico é salvo automaticamente com um nome que inclui a data e hora atuais para evitar sobrescrever arquivos anteriores.

### Testes e Validação

- O programa foi testado com diferentes cenários, incluindo:
  - Horários de início variados.
  - Diferentes formatos de tempo total (apenas horas, apenas minutos, horas e minutos).
  - Listas de atividades com quantidades variadas.
  - Entradas inválidas para garantir que as validações estão funcionando corretamente.

## Utilidade do Projeto

- **Planejamento Pessoal**: Auxilia indivíduos a organizar seu tempo de forma visual, facilitando o equilíbrio entre trabalho, estudo e lazer.
- **Ferramenta Educacional**: Pode ser usado em contextos educacionais para ensinar sobre gerenciamento de tempo e representação gráfica de dados.
- **Gestão de Projetos**: Equipes podem utilizar o programa para visualizar a alocação de tempo em diferentes tarefas ou fases de um projeto.
- **Análise de Rotina**: Permite identificar como o tempo está sendo distribuído e onde podem ser feitas otimizações para melhorar a produtividade.

## Possíveis Melhorias Futuras

- **Alocação Personalizada de Tempo**:
  - Permitir que o usuário defina tempos específicos para cada atividade, em vez de dividir o tempo total igualmente.
  - Adicionar sliders ou campos de entrada para ajustar o tempo de cada atividade.

- **Salvamento e Carregamento de Planos**:
  - Implementar funcionalidade para salvar planos de atividades e carregá-los posteriormente.

- **Customização Adicional**:
  - Permitir que o usuário escolha as cores associadas a cada atividade.
  - Adicionar opções para alterar o estilo e layout do gráfico.

- **Compatibilidade com Períodos Maiores**:
  - Adaptar o relógio para representar períodos superiores a 12 horas, talvez através de múltiplas rotações ou uma representação diferente.

- **Exportação Aprimorada**:
  - Fornecer opções para exportar o gráfico em diferentes formatos e resoluções.
  - Incluir a possibilidade de copiar o gráfico para a área de transferência.