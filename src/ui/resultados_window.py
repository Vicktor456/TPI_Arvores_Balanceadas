"""Janela para consultar os resultados já gerados pelos experimentos."""
import csv
import json
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import messagebox, ttk


ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "testes" / "resultados"


class JanelaResultados:
    def __init__(self, janela: tk.Toplevel) -> None:
        self.janela = janela
        self.janela.title("Resultados dos testes - Árvores Balanceadas")
        self.janela.geometry("1180x690")
        self.janela.minsize(900, 560)

        self.linhas: list[dict[str, str]] = []
        self.metadados: dict = {}
        self.validacao: dict = {}
        self.arquivos_ok = False

        self.tamanho_var = tk.StringVar(value="Todos")
        self.ordem_var = tk.StringVar(value="Todas")
        self.percentual_var = tk.StringVar(value="Todos")

        self._criar_interface()
        self.carregar_resultados()

    def _criar_interface(self) -> None:
        conteudo = ttk.Frame(self.janela, padding=14)
        conteudo.pack(fill=tk.BOTH, expand=True)
        conteudo.columnconfigure(0, weight=1)
        conteudo.rowconfigure(3, weight=1)

        ttk.Label(
            conteudo,
            text="Resultados dos experimentos",
            font=("Arial", 17, "bold"),
        ).grid(row=0, column=0, sticky="w")

        self.rotulo_validacao = ttk.Label(
            conteudo, text="Carregando resultados...", wraplength=1100
        )
        self.rotulo_validacao.grid(row=1, column=0, sticky="w", pady=(5, 10))

        filtros = ttk.LabelFrame(conteudo, text="Filtros", padding=(8, 5))
        filtros.grid(row=2, column=0, sticky="ew", pady=(0, 9))

        ttk.Label(filtros, text="Tamanho:").pack(side=tk.LEFT, padx=(0, 5))
        tamanho = ttk.Combobox(
            filtros,
            textvariable=self.tamanho_var,
            values=("Todos", "100", "1000", "10000"),
            state="readonly",
            width=9,
        )
        tamanho.pack(side=tk.LEFT, padx=(0, 14))
        tamanho.bind("<<ComboboxSelected>>", self._aplicar_filtros)

        ttk.Label(filtros, text="Ordem:").pack(side=tk.LEFT, padx=(0, 5))
        ordem = ttk.Combobox(
            filtros,
            textvariable=self.ordem_var,
            values=("Todas", "Crescente", "Aleatória"),
            state="readonly",
            width=12,
        )
        ordem.pack(side=tk.LEFT, padx=(0, 14))
        ordem.bind("<<ComboboxSelected>>", self._aplicar_filtros)

        ttk.Label(filtros, text="Remoção:").pack(side=tk.LEFT, padx=(0, 5))
        percentual = ttk.Combobox(
            filtros,
            textvariable=self.percentual_var,
            values=("Todos", "10%", "30%", "50%"),
            state="readonly",
            width=9,
        )
        percentual.pack(side=tk.LEFT, padx=(0, 12))
        percentual.bind("<<ComboboxSelected>>", self._aplicar_filtros)

        ttk.Button(filtros, text="Atualizar", command=self.carregar_resultados).pack(
            side=tk.LEFT, padx=(0, 12)
        )
        ttk.Button(filtros, text="Relatório HTML", command=self.abrir_html).pack(
            side=tk.RIGHT, padx=(5, 0)
        )
        ttk.Button(filtros, text="Relatório PDF", command=self.abrir_pdf).pack(
            side=tk.RIGHT
        )

        self.abas = ttk.Notebook(conteudo)
        self.abas.grid(row=3, column=0, sticky="nsew")
        self.tabelas: dict[str, ttk.Treeview] = {}

        self._criar_aba(
            "Resumo",
            "Inserção e busca (medianas)",
            (
                ("n", "Tamanho", 75, "int"),
                ("ordem", "Ordem", 100, "order"),
                ("arvore", "Árvore", 135, "text"),
                ("altura_antes", "Altura", 75, "int"),
                ("rotacoes_insercao", "Rotações inserção", 115, "int"),
                ("recoloracoes_insercao", "Recolorações inserção", 145, "int_na"),
                ("media_visitas_total", "Média de visitas", 110, "float"),
                ("tempo_insercao_ms", "Inserção (ms)", 100, "float"),
                ("tempo_busca_total_ms", "Busca (ms)", 100, "float"),
            ),
        )
        self._criar_aba(
            "Inserção",
            "Altura, rebalanceamento e tempo de inserção",
            (
                ("n", "Tamanho", 85, "int"),
                ("ordem", "Ordem", 110, "order"),
                ("arvore", "Árvore", 145, "text"),
                ("altura_antes", "Altura final", 95, "int"),
                ("rotacoes_insercao", "Rotações", 110, "int"),
                ("recoloracoes_insercao", "Recolorações", 115, "int_na"),
                ("tempo_insercao_ms", "Tempo (ms)", 110, "float"),
            ),
        )
        self._criar_aba(
            "Busca",
            "Consultas existentes e inexistentes",
            (
                ("n", "Tamanho", 85, "int"),
                ("ordem", "Ordem", 110, "order"),
                ("arvore", "Árvore", 145, "text"),
                ("media_visitas_existentes", "Visitas existentes", 130, "float"),
                ("media_visitas_inexistentes", "Visitas inexistentes", 140, "float"),
                ("media_visitas_total", "Média geral", 105, "float"),
                ("tempo_busca_existente_ms", "Existentes (ms)", 115, "float"),
                ("tempo_busca_inexistente_ms", "Inexistentes (ms)", 125, "float"),
                ("tempo_busca_total_ms", "Total (ms)", 100, "float"),
            ),
        )
        self._criar_aba(
            "Remoção",
            "Altura, rotações, recolorações e tempo de remoção",
            (
                ("n", "Tamanho", 80, "int"),
                ("ordem", "Ordem", 100, "order"),
                ("percentual_remocao", "Remoção", 90, "percent"),
                ("arvore", "Árvore", 130, "text"),
                ("altura_antes", "Altura antes", 95, "int"),
                ("altura_depois", "Altura depois", 100, "int"),
                ("rotacoes_remocao", "Rotações", 95, "int"),
                ("recoloracoes_remocao", "Recolorações", 115, "int_na"),
                ("tempo_remocao_ms", "Tempo (ms)", 105, "float"),
            ),
        )

        self.rotulo_status = ttk.Label(conteudo, text="", anchor="w")
        self.rotulo_status.grid(row=4, column=0, sticky="ew", pady=(7, 0))

    def _criar_aba(self, nome: str, descricao: str, colunas) -> None:
        quadro = ttk.Frame(self.abas, padding=8)
        quadro.columnconfigure(0, weight=1)
        quadro.rowconfigure(1, weight=1)
        ttk.Label(quadro, text=descricao).grid(row=0, column=0, sticky="w", pady=(0, 6))

        identificadores = [coluna[0] for coluna in colunas]
        tabela = ttk.Treeview(
            quadro,
            columns=identificadores,
            show="headings",
            height=16,
        )
        for identificador, titulo, largura, _tipo in colunas:
            tabela.heading(identificador, text=titulo)
            tabela.column(identificador, width=largura, minwidth=60, anchor=tk.CENTER)

        barra_y = ttk.Scrollbar(quadro, orient=tk.VERTICAL, command=tabela.yview)
        barra_x = ttk.Scrollbar(quadro, orient=tk.HORIZONTAL, command=tabela.xview)
        tabela.configure(yscrollcommand=barra_y.set, xscrollcommand=barra_x.set)
        tabela.grid(row=1, column=0, sticky="nsew")
        barra_y.grid(row=1, column=1, sticky="ns")
        barra_x.grid(row=2, column=0, sticky="ew")
        self.abas.add(quadro, text=nome)
        self.tabelas[nome] = tabela

    def carregar_resultados(self) -> None:
        try:
            with (RESULTS_DIR / "resumo.csv").open(
                "r", encoding="utf-8-sig", newline=""
            ) as arquivo:
                self.linhas = list(csv.DictReader(arquivo))
            with (RESULTS_DIR / "metadados.json").open(
                "r", encoding="utf-8"
            ) as arquivo:
                self.metadados = json.load(arquivo)
            with (RESULTS_DIR / "validacao.json").open(
                "r", encoding="utf-8"
            ) as arquivo:
                self.validacao = json.load(arquivo)
        except (OSError, json.JSONDecodeError, csv.Error) as erro:
            self.arquivos_ok = False
            self._limpar_tabelas()
            self.rotulo_validacao.config(
                text="Não foi possível carregar os resultados. Confira a pasta testes/resultados.",
                foreground="#a12622",
            )
            self.rotulo_status.config(text=str(erro))
            return

        self.arquivos_ok = bool(self.linhas)
        estado = self.validacao.get("status", "Sem validação")
        operacoes = self._formatar_inteiro(
            self.validacao.get("operacoes_mistas_verificadas", "—")
        )
        gerado = self.metadados.get("data_utc", "data não informada")
        commit = self.metadados.get("commit_execucao") or "não registrado"
        cor = "#1b5e20" if estado == "APROVADO" else "#a12622"
        self.rotulo_validacao.config(
            text=f"Validação: {estado} · {operacoes} operações mistas · Gerado (UTC): {gerado} · Commit: {commit[:10]}",
            foreground=cor,
        )
        self.rotulo_status.config(
            text=f"{len(self.linhas)} linhas de resumo carregadas de {RESULTS_DIR}"
        )
        self._preencher_tabelas()

    def _preencher_tabelas(self) -> None:
        if not self.arquivos_ok:
            return

        linhas_resumo = [
            linha
            for linha in self.linhas
            if self._corresponde_filtros(linha, incluir_percentual=False)
        ]
        linhas_remocao = [
            linha for linha in self.linhas if self._corresponde_filtros(linha)
        ]
        resumo = [linha for linha in linhas_resumo if linha["percentual_remocao"] == "10"]

        self._preencher(
            "Resumo",
            resumo,
            (
                ("n", "int"), ("ordem", "order"), ("arvore", "text"),
                ("altura_antes", "int"), ("rotacoes_insercao", "int"),
                ("recoloracoes_insercao", "int_na"), ("media_visitas_total", "float"),
                ("tempo_insercao_ms", "float"), ("tempo_busca_total_ms", "float"),
            ),
        )
        self._preencher(
            "Inserção",
            resumo,
            (
                ("n", "int"), ("ordem", "order"), ("arvore", "text"),
                ("altura_antes", "int"), ("rotacoes_insercao", "int"),
                ("recoloracoes_insercao", "int_na"), ("tempo_insercao_ms", "float"),
            ),
        )
        self._preencher(
            "Busca",
            resumo,
            (
                ("n", "int"), ("ordem", "order"), ("arvore", "text"),
                ("media_visitas_existentes", "float"), ("media_visitas_inexistentes", "float"),
                ("media_visitas_total", "float"), ("tempo_busca_existente_ms", "float"),
                ("tempo_busca_inexistente_ms", "float"), ("tempo_busca_total_ms", "float"),
            ),
        )
        self._preencher(
            "Remoção",
            linhas_remocao,
            (
                ("n", "int"), ("ordem", "order"), ("percentual_remocao", "percent"),
                ("arvore", "text"), ("altura_antes", "int"), ("altura_depois", "int"),
                ("rotacoes_remocao", "int"), ("recoloracoes_remocao", "int_na"),
                ("tempo_remocao_ms", "float"),
            ),
        )

    def _preencher(self, nome: str, linhas, campos) -> None:
        tabela = self.tabelas[nome]
        itens = tabela.get_children()
        if itens:
            tabela.delete(*itens)
        for linha in linhas:
            valores = [self._formatar(linha[campo], tipo) for campo, tipo in campos]
            tabela.insert("", tk.END, values=valores)

    def _corresponde_filtros(
        self, linha: dict[str, str], incluir_percentual: bool = True
    ) -> bool:
        tamanho = self.tamanho_var.get()
        ordem = self.ordem_var.get()
        percentual = self.percentual_var.get()
        if tamanho != "Todos" and linha["n"] != tamanho:
            return False
        valor_ordem = {"Crescente": "crescente", "Aleatória": "aleatoria"}.get(ordem)
        if ordem != "Todas" and linha["ordem"] != valor_ordem:
            return False
        if (
            incluir_percentual
            and percentual != "Todos"
            and linha["percentual_remocao"] != percentual.rstrip("%")
        ):
            return False
        return True

    def _aplicar_filtros(self, _evento=None) -> None:
        self._preencher_tabelas()

    def _formatar(self, valor: str, tipo: str) -> str:
        if tipo == "order":
            return {"crescente": "Crescente", "aleatoria": "Aleatória"}.get(valor, valor)
        if tipo == "percent":
            return f"{valor}%"
        if tipo == "int_na" and valor in ("", "0", None):
            return "—"
        if tipo in ("int", "int_na"):
            return self._formatar_inteiro(valor)
        if tipo == "float":
            try:
                return f"{float(valor):.3f}".replace(".", ",")
            except (TypeError, ValueError):
                return str(valor)
        return str(valor)

    @staticmethod
    def _formatar_inteiro(valor) -> str:
        try:
            return f"{int(float(valor)):,}".replace(",", ".")
        except (TypeError, ValueError):
            return str(valor)

    def _limpar_tabelas(self) -> None:
        for tabela in self.tabelas.values():
            itens = tabela.get_children()
            if itens:
                tabela.delete(*itens)

    def abrir_html(self) -> None:
        self._abrir_relatorio("Relatorio_Experimentos.html")

    def abrir_pdf(self) -> None:
        self._abrir_relatorio("Relatorio_Experimentos.pdf")

    @staticmethod
    def _abrir_relatorio(nome: str) -> None:
        caminho = ROOT / "testes" / nome
        if caminho.is_file():
            webbrowser.open(caminho.resolve().as_uri())
        else:
            messagebox.showerror(
                "Relatório não encontrado",
                f"O arquivo {nome} não foi encontrado na pasta testes.",
            )
