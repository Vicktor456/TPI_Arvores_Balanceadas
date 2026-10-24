# Trabalho Prático I - Árvores Balanceadas

Aplicação do **Sistema Acadêmico** para a disciplina de Algoritmos e Estruturas de Dados II. O projeto implementa e compara duas árvores binárias de busca balanceadas:

- Árvore AVL;
- Árvore Rubro-Negra.

Cada estrutura armazena registros de alunos e utiliza a **matrícula institucional** como chave única de ordenação.

## Registro armazenado

Cada aluno possui os seguintes atributos:

| Atributo | Descrição |
| --- | --- |
| `matricula` | Chave única e número inteiro positivo usado para ordenar a árvore. |
| `nome` | Nome do aluno. |
| `curso` | Curso do aluno. |
| `periodo` | Período atual do aluno. |

Não são permitidas matrículas duplicadas. Uma tentativa de cadastrar uma matrícula já existente não altera a árvore.

## Funcionalidades

As duas árvores disponibilizam:

- inserção, busca e remoção por matrícula;
- obtenção do aluno com menor e maior matrícula;
- caminhamentos em pré-ordem, em ordem e pós-ordem;
- altura atual e quantidade de nós;
- validação das propriedades da estrutura;
- visualização gráfica da árvore na interface.

A AVL também mantém a altura dos nós, calcula o fator de balanceamento e contabiliza rotações.

A Rubro-Negra utiliza nós vermelhos e pretos, folha sentinela `NIL`, rotações, recolorações e contadores separados para rotações e recolorações.

A interface permite acompanhar a busca, inserção, remoção e os eventos de rebalanceamento. As rotações da AVL e as rotações/recolorações da Rubro-Negra são mostradas passo a passo.

## Requisitos

- Python 3.10 ou superior;
- Tkinter, normalmente incluído na instalação padrão do Python para Windows;
- Git, apenas para clonar e enviar alterações ao GitHub.

Confira a versão instalada:

```powershell
py --version
```

Para verificar se o Tkinter está disponível:

```powershell
py -m tkinter
```

Se uma pequena janela de teste abrir, o Tkinter está instalado.

## Como executar

### 1. Clonar o repositório

No PowerShell ou terminal do VS Code:

```powershell
git clone https://github.com/Vicktor456/TPI_Arvores_Balanceadas.git
cd TPI_Arvores_Balanceadas
```

Se o projeto já estiver clonado, abra a pasta do repositório no VS Code e use o terminal integrado nela.

### 2. Iniciar a interface

Na raiz do projeto, execute:

```powershell
py -m src.ui.menu
```

Caso o comando `py` não esteja disponível, tente:

```powershell
python -m src.ui.menu
```

A janela inicial permite escolher a Árvore AVL ou a Árvore Rubro-Negra.

## Uso da interface

1. Escolha a estrutura desejada.
2. Preencha matrícula, nome, curso e período.
3. Clique em **Cadastrar**.
4. Use o campo de matrícula para buscar ou remover alunos.
5. Use os botões de operações para consultar menor chave, maior chave, caminhamentos, validação e estatísticas.
6. Observe a área de visualização para acompanhar a estrutura e os rebalanceamentos.

As árvores permanecem armazenadas enquanto o programa estiver aberto. Ao fechar o programa, os dados cadastrados em memória são descartados.

## Estrutura do projeto

```text
src/
├── models/
│   └── aluno.py              # Modelo do registro Aluno
├── trees/
│   ├── avl.py                # Implementação da Árvore AVL
│   └── rubro_negra.py        # Implementação da Árvore Rubro-Negra
└── ui/
    ├── menu.py               # Tela inicial
    ├── avl_window.py         # Operações e visualização da AVL
    └── rubro_negra_window.py # Operações e visualização da Rubro-Negra
```

## Equipe

- Davi Vitor Santos Mota
- Isabely Cristina Barbosa Beça
- Thiago Silva dos Santos
- Vicktor Eduardo Almeida Pinheiro
