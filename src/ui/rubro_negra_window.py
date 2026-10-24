"""Tela de operações e visualização da árvore Rubro-Negra."""

import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.models.aluno import Aluno
from src.trees.rubro_negra import PRETO, VERMELHO, ArvoreRubroNegra


class JanelaRubroNegra:
    def __init__(
        self,
        janela: tk.Misc,
        arvore: ArvoreRubroNegra | None = None,
    ) -> None:
        self.janela = janela
        self.arvore = arvore if arvore is not None else ArvoreRubroNegra()
        self.animando = False
        self.etapas_balanceamento: list[dict] = []
        self.indice_etapa = 0
        self.estado_visual_atual: dict | None = None

        self.janela.title("Sistema Acadêmico - Árvore Rubro-Negra")
        self.janela.geometry("1250x700")
        self.janela.minsize(1000, 560)

        principal = ttk.Frame(self.janela, padding=16)
        principal.pack(fill=tk.BOTH, expand=True)
        ttk.Label(
            principal,
            text="Operações da Árvore Rubro-Negra",
            font=("Arial", 17, "bold"),
        ).pack(anchor=tk.W, pady=(0, 12))

        conteudo = ttk.Panedwindow(principal, orient=tk.HORIZONTAL)
        conteudo.pack(fill=tk.BOTH, expand=True)
        painel_operacoes = ttk.Frame(conteudo, padding=(0, 0, 8, 0))
        painel_arvore = ttk.LabelFrame(
            conteudo, text="Visualização da árvore Rubro-Negra", padding=8
        )
        conteudo.add(painel_operacoes, weight=3)
        conteudo.add(painel_arvore, weight=2)

        cadastro = ttk.LabelFrame(painel_operacoes, text="Cadastrar aluno", padding=12)
        cadastro.pack(fill=tk.X, pady=(0, 12))
        self.campo_matricula = self._adicionar_campo(cadastro, "Matrícula:", 0, 0)
        self.campo_nome = self._adicionar_campo(cadastro, "Nome:", 0, 2)
        self.campo_curso = self._adicionar_campo(cadastro, "Curso:", 1, 0)
        self.campo_periodo = self._adicionar_campo(cadastro, "Período:", 1, 2)
        self.botao_cadastrar = ttk.Button(
            cadastro, text="Cadastrar", command=self.cadastrar
        )
        self.botao_cadastrar.grid(
            row=2, column=0, columnspan=4, sticky=tk.E, pady=(10, 0)
        )

        operacoes = ttk.LabelFrame(
            painel_operacoes, text="Buscar ou remover", padding=12
        )
        operacoes.pack(fill=tk.X, pady=(0, 12))
        ttk.Label(operacoes, text="Matrícula:").grid(row=0, column=0, sticky=tk.W)
        self.campo_chave = ttk.Entry(operacoes, width=28)
        self.campo_chave.grid(row=0, column=1, sticky=tk.W, padx=(8, 12))
        self.campo_chave.bind("<Return>", lambda _evento: self.buscar())
        self.botao_buscar = ttk.Button(
            operacoes, text="Buscar", command=self.buscar
        )
        self.botao_buscar.grid(row=0, column=2, padx=4)
        self.botao_remover = ttk.Button(
            operacoes, text="Remover", command=self.remover
        )
        self.botao_remover.grid(row=0, column=3, padx=4)
        self.rotulo_resultado = ttk.Label(operacoes, text="")
        self.rotulo_resultado.grid(
            row=1, column=0, columnspan=4, sticky=tk.W, pady=(10, 0)
        )

        acoes_extras = ttk.Frame(operacoes)
        acoes_extras.grid(
            row=2, column=0, columnspan=4, sticky=tk.W, pady=(10, 0)
        )
        
        self.botao_menor = ttk.Button(
            acoes_extras,
            text="Menor matrícula",
            command=self.mostrar_menor,
        )
        self.botao_menor.pack(side=tk.LEFT, padx=(0, 6))
        
        self.botao_maior = ttk.Button(
            acoes_extras,
            text="Maior matrícula",
            command=self.mostrar_maior,
        )
        self.botao_maior.pack(side=tk.LEFT, padx=6)
        
        self.botao_pre_ordem = ttk.Button(
            acoes_extras,
            text="Pré-ordem",
            command=self.mostrar_pre_ordem,
        )
        self.botao_pre_ordem.pack(side=tk.LEFT, padx=6)
        
        self.botao_pos_ordem = ttk.Button(
            acoes_extras,
            text="Pós-ordem",
            command=self.mostrar_pos_ordem,
        )
        self.botao_pos_ordem.pack(side=tk.LEFT, padx=6)

        self.botao_validar = ttk.Button(
            acoes_extras,
            text="Validar Rubro-Negra",
            command=self.validar_arvore,
        )
        self.botao_validar.pack(side=tk.LEFT, padx=6)
        
        self.botao_estatisticas = ttk.Button(
            acoes_extras,
            text="Estatísticas",
            command=self.mostrar_estatisticas,
        )
        self.botao_estatisticas.pack(side=tk.LEFT, padx=6)

        lista = ttk.LabelFrame(
            painel_operacoes, text="Alunos em ordem de matrícula", padding=8
        )
        lista.pack(fill=tk.BOTH, expand=True)
        colunas = ("matricula", "nome", "curso", "periodo")
        self.tabela = ttk.Treeview(lista, columns=colunas, show="headings", height=10)
        for coluna, titulo in zip(
            colunas, ("Matrícula", "Nome", "Curso", "Período")
        ):
            self.tabela.heading(coluna, text=titulo)
        self.tabela.column("matricula", width=120, anchor=tk.W)
        self.tabela.column("nome", width=220, anchor=tk.W)
        self.tabela.column("curso", width=180, anchor=tk.W)
        self.tabela.column("periodo", width=80, anchor=tk.CENTER)
        barra_tabela = ttk.Scrollbar(
            lista, orient=tk.VERTICAL, command=self.tabela.yview
        )
        self.tabela.configure(yscrollcommand=barra_tabela.set)
        self.tabela.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        barra_tabela.pack(side=tk.RIGHT, fill=tk.Y)

        rodape = ttk.Frame(painel_operacoes)
        rodape.pack(fill=tk.X, pady=(8, 0))
        self.rotulo_contagem = ttk.Label(rodape)
        self.rotulo_contagem.pack(side=tk.LEFT)
        self.botao_atualizar = ttk.Button(
            rodape, text="Atualizar lista", command=self.atualizar_lista
        )
        self.botao_atualizar.pack(side=tk.RIGHT)
        self.botoes_operacao = (
            self.botao_cadastrar,
            self.botao_buscar,
            self.botao_remover,
            self.botao_atualizar,
            self.botao_menor,
            self.botao_maior,
            self.botao_pre_ordem,
            self.botao_pos_ordem,
        )

        painel_arvore.columnconfigure(0, weight=1)
        painel_arvore.rowconfigure(1, weight=1)
        self.rotulo_visualizacao = ttk.Label(
            painel_arvore,
            text="",
            anchor=tk.W,
            justify=tk.LEFT,
            foreground="#b71c1c",
            font=("Arial", 9, "bold"),
        )
        self.rotulo_visualizacao.grid(
            row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6)
        )
        painel_arvore.bind(
            "<Configure>",
            lambda evento: self.rotulo_visualizacao.configure(
                wraplength=max(180, evento.width - 24)
            ),
        )
        self.canvas_arvore = tk.Canvas(
            painel_arvore, background="white", highlightthickness=0
        )
        barra_vertical = ttk.Scrollbar(
            painel_arvore, orient=tk.VERTICAL, command=self.canvas_arvore.yview
        )
        barra_horizontal = ttk.Scrollbar(
            painel_arvore, orient=tk.HORIZONTAL, command=self.canvas_arvore.xview
        )
        self.canvas_arvore.configure(
            yscrollcommand=barra_vertical.set,
            xscrollcommand=barra_horizontal.set,
        )
        self.canvas_arvore.grid(row=1, column=0, sticky="nsew")
        barra_vertical.grid(row=1, column=1, sticky="ns")
        barra_horizontal.grid(row=2, column=0, sticky="ew")
        self.botao_avancar = ttk.Button(
            painel_arvore,
            text="Avançar",
            command=self.avancar_etapa,
            state=tk.DISABLED,
        )
        self.botao_avancar.grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )
        self.atualizar_lista()

    @staticmethod
    def _adicionar_campo(
        quadro: ttk.LabelFrame,
        rotulo: str,
        linha: int,
        coluna: int,
    ) -> ttk.Entry:
        ttk.Label(quadro, text=rotulo).grid(
            row=linha, column=coluna, sticky=tk.W, padx=(0, 6), pady=4
        )
        campo = ttk.Entry(quadro, width=30)
        campo.grid(row=linha, column=coluna + 1, sticky=tk.EW, padx=(0, 14), pady=4)
        quadro.columnconfigure(coluna + 1, weight=1)
        return campo

    @staticmethod
    def _ler_matricula(campo: ttk.Entry) -> int | None:
        texto = campo.get().strip()
        if not texto or not texto.isdecimal():
            return None
        matricula = int(texto)
        return matricula if matricula > 0 else None

    def cadastrar(self) -> None:
        if self.animando:
            return
        matricula_texto = self.campo_matricula.get().strip()
        nome = self.campo_nome.get().strip()
        curso = self.campo_curso.get().strip()
        periodo_texto = self.campo_periodo.get().strip()
        if not all((matricula_texto, nome, curso, periodo_texto)):
            messagebox.showwarning(
                "Cadastro incompleto",
                "Preencha matrícula, nome, curso e período.",
                parent=self.janela,
            )
            return

        matricula = self._ler_matricula(self.campo_matricula)
        if matricula is None:
            messagebox.showwarning(
                "Matrícula inválida",
                "Informe a matrícula como um número inteiro positivo.",
                parent=self.janela,
            )
            return
        try:
            periodo = int(periodo_texto)
            if periodo < 1:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Período inválido",
                "Informe um período como número inteiro positivo.",
                parent=self.janela,
            )
            return

        estado_anterior = self._capturar_estado()
        aluno = Aluno(matricula, nome, curso, periodo)
        if not self.arvore.inserir(aluno):
            messagebox.showwarning(
                "Matrícula já cadastrada",
                f"Já existe um aluno com a matrícula {matricula}.",
                parent=self.janela,
            )
            return

        for campo in (
            self.campo_matricula,
            self.campo_nome,
            self.campo_curso,
            self.campo_periodo,
        ):
            campo.delete(0, tk.END)
        self.rotulo_resultado.config(text=f"Aluno {nome} cadastrado com sucesso.")
        self.atualizar_lista(atualizar_visualizacao=False)

        estado_final = self._capturar_estado()
        eventos = list(self.arvore.eventos_balanceamento)
        self._iniciar_animacao_operacao()
        if eventos:
            estado_inicial, etapas = self._reconstruir_etapas(estado_final, eventos)
            self.etapas_balanceamento = etapas
            self.indice_etapa = 0
            self._animar_transicao(
                estado_anterior,
                estado_inicial,
                ao_finalizar=lambda: self._aguardar_etapa(
                    estado_inicial,
                    mensagem="Nó inserido. A correção Rubro-Negra está pendente.",
                ),
            )
        else:
            self._animar_transicao(
                estado_anterior,
                estado_final,
                ao_finalizar=self._finalizar_animacao,
            )

    def buscar(self) -> None:
        if self.animando:
            return
        matricula = self._ler_matricula(self.campo_chave)
        if matricula is None:
            messagebox.showwarning(
                "Matrícula inválida",
                "Informe uma matrícula numérica positiva para buscar.",
                parent=self.janela,
            )
            return
        self._iniciar_percurso(matricula, "buscar")

    def remover(self) -> None:
        if self.animando:
            return
        matricula = self._ler_matricula(self.campo_chave)
        if matricula is None:
            messagebox.showwarning(
                "Matrícula inválida",
                "Informe uma matrícula numérica positiva para remover.",
                parent=self.janela,
            )
            return
        self._iniciar_percurso(matricula, "remover")

    def _iniciar_percurso(self, matricula: int, acao: str) -> None:
        caminho = []
        no = self.arvore.raiz
        while no != self.arvore.NIL:
            chave = no.aluno.matricula
            caminho.append(chave)
            if chave == matricula:
                break
            no = no.esquerda if matricula < chave else no.direita

        if not caminho:
            self.rotulo_resultado.config(text=f"Nenhum aluno encontrado para {matricula}.")
            return
        self._iniciar_animacao_operacao()
        self._animar_etapa_percurso(caminho, 0, matricula, acao)

    def _animar_etapa_percurso(
        self,
        caminho: list[int],
        indice: int,
        matricula: int,
        acao: str,
    ) -> None:
        if indice >= len(caminho):
            self.rotulo_resultado.config(text=f"Nenhum aluno encontrado para {matricula}.")
            self.janela.after(800, self._finalizar_animacao)
            return

        chave = caminho[indice]
        estado = self._capturar_estado()
        if chave == matricula:
            self.rotulo_resultado.config(
                text=f"Matrícula {matricula} encontrada; nó destacado em verde."
            )
            self._desenhar_estado(
                estado, destaque=chave, cor_destaque="#2e7d32",
                mensagem=f"Matrícula {matricula} encontrada",
            )
            if acao == "buscar":
                aluno = self.arvore.buscar(matricula)
                if aluno is not None:
                    self.rotulo_resultado.config(
                        text=(
                            f"Encontrado: {aluno.nome} | Curso: {aluno.curso} | "
                            f"Período: {aluno.periodo}"
                        )
                    )
                self.janela.after(850, self._finalizar_animacao)
            else:
                self.rotulo_resultado.config(
                    text=f"Matrícula {matricula} encontrada. Preparando remoção..."
                )
                self.janela.after(
                    850, lambda: self._executar_remocao(matricula)
                )
            return

        direcao = "esquerda" if matricula < chave else "direita"
        verbo = "Buscando" if acao == "buscar" else "Removendo"
        self.rotulo_resultado.config(
            text=f"{verbo} {matricula}: comparando com {chave}; seguindo à {direcao}."
        )
        self._desenhar_estado(
            estado,
            destaque=chave,
            cor_destaque="#f9a825",
            mensagem=f"Comparando matrícula {matricula} com {chave}",
        )
        self.janela.after(
            500,
            lambda: self._animar_etapa_percurso(
                caminho, indice + 1, matricula, acao
            ),
        )

    def _executar_remocao(self, matricula: int) -> None:
        estado_anterior = self._capturar_estado()
        if not self.arvore.remover(matricula):
            self.rotulo_resultado.config(text=f"Nenhum aluno encontrado para {matricula}.")
            self._finalizar_animacao()
            return

        self.rotulo_resultado.config(text=f"Aluno {matricula} removido.")
        self.atualizar_lista(atualizar_visualizacao=False)
        estado_final = self._capturar_estado()
        eventos = list(self.arvore.eventos_balanceamento)
        if eventos:
            estado_inicial, etapas = self._reconstruir_etapas(estado_final, eventos)
            self.etapas_balanceamento = etapas
            self.indice_etapa = 0
            self._animar_transicao(
                estado_anterior,
                estado_inicial,
                ao_finalizar=lambda: self._aguardar_etapa(
                    estado_inicial,
                    mensagem="Nó removido. A correção Rubro-Negra está pendente.",
                ),
            )
        else:
            self._animar_transicao(
                estado_anterior,
                estado_final,
                ao_finalizar=self._finalizar_animacao,
            )

    def atualizar_lista(self, atualizar_visualizacao: bool = True) -> None:
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        for aluno in self.arvore.em_ordem():
            self.tabela.insert(
                "",
                tk.END,
                values=(aluno.matricula, aluno.nome, aluno.curso, aluno.periodo),
            )
        self.rotulo_contagem.config(
            text=(
                f"Quantidade: {self.arvore.obter_quantidade_nos()} | "
                f"Altura: {self.arvore.obter_altura()}"
            )
        )
        if atualizar_visualizacao:
            self.atualizar_visualizacao()

    def _capturar_estado(self) -> dict:
        nos = {}

        def copiar(no):
            if no == self.arvore.NIL:
                return None
            chave = no.aluno.matricula
            esquerda = copiar(no.esquerda)
            direita = copiar(no.direita)
            nos[chave] = {
                "esquerda": esquerda,
                "direita": direita,
                "cor": no.cor,
            }
            return chave

        return {"raiz": copiar(self.arvore.raiz), "nos": nos}

    def _reconstruir_etapas(self, estado_final: dict, eventos: list[tuple]) -> tuple[dict, list[dict]]:
        estados_reversos = [estado_final]
        estado_atual = estado_final
        for evento in reversed(eventos):
            if evento[0] == "recolorir":
                _, chave, cor_anterior, _cor_nova = evento
                nos = {k: v.copy() for k, v in estado_atual["nos"].items()}
                nos[chave]["cor"] = cor_anterior
                estado_atual = {"raiz": estado_atual["raiz"], "nos": nos}
            else:
                _, direcao, pivo = evento
                pai = next(
                    (
                        chave
                        for chave, dados in estado_atual["nos"].items()
                        if dados["esquerda"] == pivo or dados["direita"] == pivo
                    ),
                    None,
                )
                if pai is None:
                    raise RuntimeError(
                        f"Não foi possível reconstruir a rotação no nó {pivo}."
                    )
                inversa = "direita" if direcao == "esquerda" else "esquerda"
                estado_atual = self._rotacionar_estado(estado_atual, pai, inversa)
            estados_reversos.append(estado_atual)

        estados = list(reversed(estados_reversos))
        etapas = []
        for indice, evento in enumerate(eventos):
            if evento[0] == "recolorir":
                _, chave, cor_anterior, cor_nova = evento
                rotulo = (
                    f"Recolorir nó {chave}: {cor_anterior} para {cor_nova}"
                )
                tipo = "recolorir"
            else:
                _, direcao, chave = evento
                sentido = "à esquerda" if direcao == "esquerda" else "à direita"
                rotulo = f"Rotação {sentido} no nó {chave}"
                tipo = "rotacao"
            etapas.append(
                {
                    "tipo": tipo,
                    "rotulo": rotulo,
                    "chave": evento[1] if tipo == "recolorir" else evento[2],
                    "estado": estados[indice + 1],
                }
            )
        return estados[0], etapas

    def _rotacionar_estado(self, estado: dict, pivo: int, direcao: str) -> dict:
        nos = {chave: dados.copy() for chave, dados in estado["nos"].items()}
        raiz = estado["raiz"]
        pai = next(
            (
                chave
                for chave, dados in nos.items()
                if chave != pivo
                and (dados["esquerda"] == pivo or dados["direita"] == pivo)
            ),
            None,
        )
        if direcao == "esquerda":
            novo_pivo = nos[pivo]["direita"]
            nos[pivo]["direita"] = nos[novo_pivo]["esquerda"]
            nos[novo_pivo]["esquerda"] = pivo
        else:
            novo_pivo = nos[pivo]["esquerda"]
            nos[pivo]["esquerda"] = nos[novo_pivo]["direita"]
            nos[novo_pivo]["direita"] = pivo
        if pai is None:
            raiz = novo_pivo
        elif nos[pai]["esquerda"] == pivo:
            nos[pai]["esquerda"] = novo_pivo
        else:
            nos[pai]["direita"] = novo_pivo
        return {"raiz": raiz, "nos": nos}

    def _aguardar_etapa(self, estado: dict, mensagem: str | None = None) -> None:
        self.estado_visual_atual = estado
        etapa = self.etapas_balanceamento[self.indice_etapa]
        if etapa["tipo"] == "recolorir":
            instrucoes = f"Antes da recoloração: {etapa['rotulo']}. Clique para aplicar."
            texto_botao = "Avançar recoloração"
        else:
            instrucoes = f"Próxima ação: {etapa['rotulo']}. Clique para avançar."
            texto_botao = "Avançar rotação"
        if mensagem:
            instrucoes = f"{mensagem} {instrucoes}"
        self.rotulo_resultado.config(text=instrucoes)
        self._desenhar_estado(
            estado,
            destaque=etapa["chave"],
            cor_destaque="#f9a825",
            mensagem=instrucoes,
        )
        self.botao_avancar.config(
            text=f"{texto_botao} ({self.indice_etapa + 1}/{len(self.etapas_balanceamento)})",
            state=tk.NORMAL,
        )

    def avancar_etapa(self) -> None:
        if not self.animando or self.indice_etapa >= len(self.etapas_balanceamento):
            return
        etapa = self.etapas_balanceamento[self.indice_etapa]
        self.indice_etapa += 1
        self.botao_avancar.config(state=tk.DISABLED)
        if etapa["tipo"] == "rotacao":
            self._animar_transicao(
                self.estado_visual_atual,
                etapa["estado"],
                ao_finalizar=lambda: self._apos_etapa(etapa["estado"]),
                mensagem=etapa["rotulo"],
            )
        else:
            self._desenhar_estado(
                etapa["estado"],
                destaque=etapa["chave"],
                cor_destaque="#2e7d32",
                mensagem=f"Recoloração aplicada: {etapa['rotulo']}",
            )
            self.janela.after(700, lambda: self._apos_etapa(etapa["estado"]))

    def _apos_etapa(self, estado: dict) -> None:
        if self.indice_etapa < len(self.etapas_balanceamento):
            self._aguardar_etapa(estado)
        else:
            self._finalizar_animacao()

    @staticmethod
    def _calcular_posicoes(estado: dict) -> dict:
        posicoes = {}
        indice = 0

        def visitar(chave, nivel: int) -> None:
            nonlocal indice
            if chave is None:
                return
            no = estado["nos"][chave]
            visitar(no["esquerda"], nivel + 1)
            posicoes[chave] = (60 + indice * 100, 90 + nivel * 100)
            indice += 1
            visitar(no["direita"], nivel + 1)

        visitar(estado["raiz"], 0)
        return posicoes

    def atualizar_visualizacao(self) -> None:
        self._desenhar_estado(self._capturar_estado())

    def _desenhar_estado(
        self,
        estado: dict,
        posicoes: dict | None = None,
        destaque: int | None = None,
        cor_destaque: str = "#f57c00",
        mensagem: str | None = None,
    ) -> None:
        canvas = self.canvas_arvore
        canvas.delete("all")
        self.rotulo_visualizacao.config(text=mensagem or "")
        posicoes = posicoes or self._calcular_posicoes(estado)
        if not posicoes:
            canvas.configure(scrollregion=(0, 0, 600, 400))
            canvas.create_text(
                300, 210, text="A árvore está vazia", fill="#666666", font=("Arial", 12)
            )
            return
        largura = max(600, 120 + (len(posicoes) - 1) * 100)
        altura = max(400, 180 + max(y for _, y in posicoes.values()))
        canvas.configure(scrollregion=(0, 0, largura, altura))
        for chave, no in estado["nos"].items():
            x1, y1 = posicoes[chave]
            for filho in (no["esquerda"], no["direita"]):
                if filho is not None and filho in posicoes:
                    x2, y2 = posicoes[filho]
                    canvas.create_line(x1, y1, x2, y2, fill="#616161", width=2)
        raio = 30
        for chave, (x, y) in posicoes.items():
            no = estado["nos"][chave]
            if chave == destaque:
                canvas.create_oval(
                    x - raio - 6, y - raio - 6, x + raio + 6, y + raio + 6,
                    outline=cor_destaque, width=3,
                )
            vermelho = no["cor"] == VERMELHO
            canvas.create_oval(
                x - raio, y - raio, x + raio, y + raio,
                fill="#d32f2f" if vermelho else "#212121",
                outline="#b71c1c" if vermelho else "#000000",
                width=2,
            )
            canvas.create_text(
                x, y, text=chave, fill="white", font=("Arial", 9, "bold"), width=52
            )

    def _animar_transicao(
        self,
        origem: dict,
        destino: dict,
        ao_finalizar,
        mensagem: str | None = None,
        passo: int = 0,
        total_passos: int = 28,
    ) -> None:
        posicoes_origem = self._calcular_posicoes(origem)
        posicoes_destino = self._calcular_posicoes(destino)
        if passo == 0:
            self._posicoes_inicio = {
                chave: posicoes_origem.get(
                    chave,
                    (posicoes_destino[chave][0], posicoes_destino[chave][1] - 55),
                )
                for chave in posicoes_destino
            }
        progresso = (passo + 1) / total_passos
        suave = progresso * progresso * (3 - 2 * progresso)
        interpoladas = {}
        for chave, (x_final, y_final) in posicoes_destino.items():
            x_inicio, y_inicio = self._posicoes_inicio[chave]
            interpoladas[chave] = (
                x_inicio + (x_final - x_inicio) * suave,
                y_inicio + (y_final - y_inicio) * suave,
            )
        self._desenhar_estado(destino, interpoladas, mensagem=mensagem)
        if passo + 1 < total_passos:
            self.janela.after(
                18,
                lambda: self._animar_transicao(
                    origem,
                    destino,
                    ao_finalizar,
                    mensagem=mensagem,
                    passo=passo + 1,
                    total_passos=total_passos,
                ),
            )
        else:
            self._desenhar_estado(destino, posicoes_destino, mensagem=mensagem)
            ao_finalizar()

    def _iniciar_animacao_operacao(self) -> None:
        self.animando = True
        for botao in self.botoes_operacao:
            botao.config(state=tk.DISABLED)
        self.botao_avancar.config(state=tk.DISABLED)

    def _finalizar_animacao(self) -> None:
        self.atualizar_visualizacao()
        self.animando = False
        self.etapas_balanceamento = []
        self.indice_etapa = 0
        self.estado_visual_atual = None
        self.botao_avancar.config(text="Avançar", state=tk.DISABLED)
        for botao in self.botoes_operacao:
            botao.config(state=tk.NORMAL)

    def mostrar_menor(self) -> None:
        aluno = self.arvore.obter_menor()
    
        if aluno is None:
            self.rotulo_resultado.config(text="A árvore está vazia.")
            return
    
        texto = (
            f"Menor matrícula: {aluno.matricula}\n"
            f"Nome: {aluno.nome}\n"
            f"Curso: {aluno.curso}\n"
            f"Período: {aluno.periodo}"
        )
    
        self.rotulo_resultado.config(
            text=f"Menor matrícula encontrada: {aluno.matricula}."
        )
    
        messagebox.showinfo(
            "Aluno com menor matrícula",
            texto,
            parent=self.janela,
        )

    def mostrar_maior(self) -> None:
        aluno = self.arvore.obter_maior()
    
        if aluno is None:
            self.rotulo_resultado.config(text="A árvore está vazia.")
            return
    
        texto = (
            f"Maior matrícula: {aluno.matricula}\n"
            f"Nome: {aluno.nome}\n"
            f"Curso: {aluno.curso}\n"
            f"Período: {aluno.periodo}"
        )
    
        self.rotulo_resultado.config(
            text=f"Maior matrícula encontrada: {aluno.matricula}."
        )
    
        messagebox.showinfo(
            "Aluno com maior matrícula",
            texto,
            parent=self.janela,
        )

    def mostrar_pre_ordem(self) -> None:
        alunos = self.arvore.pre_ordem()
        self._mostrar_caminhamento("Pré-ordem", alunos)

    def mostrar_pos_ordem(self) -> None:
        alunos = self.arvore.pos_ordem()
        self._mostrar_caminhamento("Pós-ordem", alunos)

    def _mostrar_caminhamento(self, titulo: str, alunos: list) -> None:
        if not alunos:
            self.rotulo_resultado.config(text="A árvore está vazia.")
            return
    
        matriculas = " → ".join(
            str(aluno.matricula) for aluno in alunos
        )
    
        self.rotulo_resultado.config(
            text=f"Caminhamento {titulo} exibido."
        )
    
        messagebox.showinfo(
            f"Caminhamento {titulo}",
            matriculas,
            parent=self.janela,
        )

def main() -> None:
    janela = tk.Tk()
    JanelaRubroNegra(janela)
    janela.mainloop()


if __name__ == "__main__":
    main()
