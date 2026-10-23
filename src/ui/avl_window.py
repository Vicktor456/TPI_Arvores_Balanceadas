"""Tela de operações da árvore AVL do sistema acadêmico."""

import tkinter as tk
import sys
from pathlib import Path
from tkinter import messagebox, ttk

# Permite executar este arquivo diretamente ou como módulo a partir do projeto.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.trees.avl import Aluno, ArvoreAVL


class JanelaAVL:
    def __init__(self, janela: tk.Misc, arvore: ArvoreAVL | None = None) -> None:
        self.janela = janela
        self.arvore = arvore if arvore is not None else ArvoreAVL()
        self.animando = False
        self.etapas_rotacao: list[dict] = []
        self.indice_etapa_rotacao = 0
        self.estado_visual_atual: dict | None = None

        self.janela.title("Sistema Acadêmico - Árvore AVL")
        self.janela.geometry("1250x700")
        self.janela.minsize(1000, 560)

        principal = ttk.Frame(self.janela, padding=16)
        principal.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            principal,
            text="Operações da Árvore AVL",
            font=("Arial", 17, "bold"),
        ).pack(anchor=tk.W, pady=(0, 12))

        conteudo = ttk.Panedwindow(principal, orient=tk.HORIZONTAL)
        conteudo.pack(fill=tk.BOTH, expand=True)

        painel_operacoes = ttk.Frame(conteudo, padding=(0, 0, 8, 0))
        painel_arvore = ttk.LabelFrame(conteudo, text="Visualização da árvore AVL", padding=8)
        conteudo.add(painel_operacoes, weight=3)
        conteudo.add(painel_arvore, weight=2)

        cadastro = ttk.LabelFrame(painel_operacoes, text="Cadastrar aluno", padding=12)
        cadastro.pack(fill=tk.X, pady=(0, 12))

        self.campo_matricula = self._adicionar_campo(cadastro, "Matrícula:", 0, 0)
        self.campo_nome = self._adicionar_campo(cadastro, "Nome:", 0, 2)
        self.campo_curso = self._adicionar_campo(cadastro, "Curso:", 1, 0)
        self.campo_periodo = self._adicionar_campo(cadastro, "Período:", 1, 2)

        self.botao_cadastrar = ttk.Button(
            cadastro,
            text="Cadastrar",
            command=self.cadastrar,
        )
        self.botao_cadastrar.grid(row=2, column=0, columnspan=4, sticky=tk.E, pady=(10, 0))

        operacoes = ttk.LabelFrame(painel_operacoes, text="Buscar ou remover", padding=12)
        operacoes.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(operacoes, text="Matrícula:").grid(row=0, column=0, sticky=tk.W)
        self.campo_chave = ttk.Entry(operacoes, width=28)
        self.campo_chave.grid(row=0, column=1, sticky=tk.W, padx=(8, 12))
        self.campo_chave.bind("<Return>", lambda _evento: self.buscar())

        self.botao_buscar = ttk.Button(operacoes, text="Buscar", command=self.buscar)
        self.botao_buscar.grid(row=0, column=2, padx=4)
        self.botao_remover = ttk.Button(operacoes, text="Remover", command=self.remover)
        self.botao_remover.grid(row=0, column=3, padx=4)

        self.rotulo_resultado = ttk.Label(operacoes, text="")
        self.rotulo_resultado.grid(
            row=1, column=0, columnspan=4, sticky=tk.W, pady=(10, 0)
        )

        lista = ttk.LabelFrame(painel_operacoes, text="Alunos em ordem de matrícula", padding=8)
        lista.pack(fill=tk.BOTH, expand=True)

        colunas = ("matricula", "nome", "curso", "periodo")
        self.tabela = ttk.Treeview(lista, columns=colunas, show="headings", height=10)
        self.tabela.heading("matricula", text="Matrícula")
        self.tabela.heading("nome", text="Nome")
        self.tabela.heading("curso", text="Curso")
        self.tabela.heading("periodo", text="Período")
        self.tabela.column("matricula", width=140, anchor=tk.W)
        self.tabela.column("nome", width=260, anchor=tk.W)
        self.tabela.column("curso", width=220, anchor=tk.W)
        self.tabela.column("periodo", width=90, anchor=tk.CENTER)

        barra = ttk.Scrollbar(lista, orient=tk.VERTICAL, command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=barra.set)
        self.tabela.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        barra.pack(side=tk.RIGHT, fill=tk.Y)

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
            painel_arvore,
            background="white",
            highlightthickness=0,
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
        self.botao_avancar_rotacao = ttk.Button(
            painel_arvore,
            text="Avançar rotação",
            command=self.avancar_rotacao,
            state=tk.DISABLED,
        )
        self.botao_avancar_rotacao.grid(
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

        try:
            if not matricula_texto.isdecimal():
                raise ValueError
            matricula = int(matricula_texto)
            if matricula <= 0:
                raise ValueError
        except ValueError:
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
        estado_intermediario, pivo, caso_rotacao = self._simular_insercao(
            estado_anterior, matricula
        )
        rotacoes_antes = self.arvore.rotacoes

        aluno = Aluno(matricula=matricula, nome=nome, curso=curso, periodo=periodo)
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
        ocorreu_rotacao = self.arvore.rotacoes > rotacoes_antes
        self.animando = True
        self._definir_botoes_ativos(False)

        if ocorreu_rotacao and caso_rotacao is not None:
            self.etapas_rotacao = self._criar_etapas_rotacao(
                estado_intermediario,
                estado_final,
                pivo,
                caso_rotacao,
            )
            self.indice_etapa_rotacao = 0

            self._animar_transicao(
                estado_anterior,
                estado_intermediario,
                ao_finalizar=lambda: self._aguardar_avanco_rotacao(
                    estado_intermediario, pivo, caso_rotacao
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
        matricula_texto = self.campo_chave.get().strip()
        if not matricula_texto:
            messagebox.showwarning(
                "Matrícula necessária",
                "Informe a matrícula para realizar a busca.",
                parent=self.janela,
            )
            return

        try:
            if not matricula_texto.isdecimal():
                raise ValueError
            matricula = int(matricula_texto)
            if matricula <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Matrícula inválida",
                "Informe a matrícula como um número inteiro positivo.",
                parent=self.janela,
            )
            return

        self._iniciar_percurso(matricula, "buscar")

    def remover(self) -> None:
        if self.animando:
            return
        matricula_texto = self.campo_chave.get().strip()
        if not matricula_texto:
            messagebox.showwarning(
                "Matrícula necessária",
                "Informe a matrícula para remover um aluno.",
                parent=self.janela,
            )
            return

        try:
            if not matricula_texto.isdecimal():
                raise ValueError
            matricula = int(matricula_texto)
            if matricula <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Matrícula inválida",
                "Informe a matrícula como um número inteiro positivo.",
                parent=self.janela,
            )
            return

        self._iniciar_percurso(matricula, "remover")

    def _iniciar_percurso(self, matricula: int, acao: str) -> None:
        caminho = []
        no = self.arvore.raiz
        while no is not None:
            chave_atual = no.aluno.matricula
            caminho.append(chave_atual)
            if matricula == chave_atual:
                break
            no = no.esquerda if matricula < chave_atual else no.direita

        if not caminho:
            self.rotulo_resultado.config(text=f"Nenhum aluno encontrado para {matricula}.")
            return

        self.animando = True
        self._definir_botoes_ativos(False)
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
            self.janela.after(900, self._finalizar_animacao)
            return

        chave_atual = caminho[indice]
        estado = self._capturar_estado()

        if chave_atual == matricula:
            self._desenhar_estado(
                estado,
                pivo=chave_atual,
                cor_pivo="#2e7d32",
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
                self.janela.after(900, self._finalizar_animacao)
            else:
                self.rotulo_resultado.config(
                    text=f"Matrícula {matricula} encontrada. Preparando remoção..."
                )
                self.janela.after(
                    900,
                    lambda: self._executar_remocao_animada(matricula),
                )
            return

        direcao = "esquerda" if matricula < chave_atual else "direita"
        acao_texto = "Buscando" if acao == "buscar" else "Removendo"
        self.rotulo_resultado.config(
            text=f"{acao_texto} {matricula}: comparando com {chave_atual}; seguindo à {direcao}."
        )
        self._desenhar_estado(
            estado,
            pivo=chave_atual,
            cor_pivo="#f9a825",
            mensagem=f"Comparando matrícula {matricula} com {chave_atual}",
        )
        self.janela.after(
            500,
            lambda: self._animar_etapa_percurso(
                caminho,
                indice + 1,
                matricula,
                acao,
            ),
        )

    def _executar_remocao_animada(self, matricula: int) -> None:
        estado_anterior = self._capturar_estado()
        if not self.arvore.remover(matricula):
            self.rotulo_resultado.config(text=f"Nenhum aluno encontrado para {matricula}.")
            self._finalizar_animacao()
            return

        self.rotulo_resultado.config(text=f"Aluno {matricula} removido com sucesso.")
        self.atualizar_lista(atualizar_visualizacao=False)
        estado_final = self._capturar_estado()
        eventos = list(self.arvore.eventos_rotacao)

        if eventos:
            estado_sem_rotacao, etapas = self._reconstruir_etapas_remocao(
                estado_final, eventos
            )
            self.etapas_rotacao = etapas
            self.indice_etapa_rotacao = 0
            primeiro = etapas[0]
            self._animar_transicao(
                estado_anterior,
                estado_sem_rotacao,
                ao_finalizar=lambda: self._aguardar_avanco_rotacao(
                    estado_sem_rotacao,
                    primeiro["pivo"],
                    "remoção",
                    mensagem_inicial=(
                        f"Remoção concluída; desbalanceamento detectado. "
                        f"Próxima: {primeiro['rotulo']}. Clique para avançar."
                    ),
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

        quantidade = self.arvore.obter_quantidade_nos()
        self.rotulo_contagem.config(text=f"Quantidade de alunos: {quantidade}")
        if atualizar_visualizacao:
            self.atualizar_visualizacao_arvore()

    def atualizar_visualizacao_arvore(self) -> None:
        self._desenhar_estado(self._capturar_estado())

    def _capturar_estado(self) -> dict:
        nos = {}

        def copiar(no):
            if no is None:
                return None

            chave = no.aluno.matricula
            esquerda = copiar(no.esquerda)
            direita = copiar(no.direita)
            nos[chave] = {
                "esquerda": esquerda,
                "direita": direita,
                "fator": self.arvore._fator_balanceamento(no),
            }
            return chave

        raiz = copiar(self.arvore.raiz)
        return {"raiz": raiz, "nos": nos}

    def _simular_insercao(self, estado: dict, matricula: int) -> tuple[dict, int | None, str | None]:
        """Monta apenas para a animação o estado BST antes da rotação AVL."""
        nos = {
            chave: dados.copy()
            for chave, dados in estado["nos"].items()
        }
        raiz = estado["raiz"]

        if raiz is None:
            nos[matricula] = {"esquerda": None, "direita": None, "fator": 0}
            return {"raiz": matricula, "nos": nos}, None, None

        caminho = []
        atual = raiz
        while atual is not None:
            caminho.append(atual)
            if matricula < atual:
                proximo = nos[atual]["esquerda"]
                if proximo is None:
                    nos[atual]["esquerda"] = matricula
                    break
                atual = proximo
            else:
                proximo = nos[atual]["direita"]
                if proximo is None:
                    nos[atual]["direita"] = matricula
                    break
                atual = proximo

        nos[matricula] = {"esquerda": None, "direita": None, "fator": 0}
        caminho.append(matricula)

        def altura(chave) -> int:
            if chave is None:
                return 0
            esquerda = altura(nos[chave]["esquerda"])
            direita = altura(nos[chave]["direita"])
            nos[chave]["fator"] = esquerda - direita
            return 1 + max(esquerda, direita)

        altura(raiz)
        pivo = next((chave for chave in reversed(caminho) if abs(nos[chave]["fator"]) > 1), None)
        caso = None
        if pivo is not None:
            fator = nos[pivo]["fator"]
            if fator > 1:
                caso = "LL" if matricula < nos[pivo]["esquerda"] else "LR"
            else:
                caso = "RR" if matricula > nos[pivo]["direita"] else "RL"

        return {"raiz": raiz, "nos": nos}, pivo, caso

    def _criar_etapas_rotacao(
        self,
        estado_intermediario: dict,
        estado_final: dict,
        pivo: int,
        caso: str,
    ) -> list[dict]:
        if caso == "LL":
            operacoes = [("Rotação simples à direita (caso LL)", pivo, "direita")]
        elif caso == "RR":
            operacoes = [("Rotação simples à esquerda (caso RR)", pivo, "esquerda")]
        elif caso == "LR":
            filho = estado_intermediario["nos"][pivo]["esquerda"]
            operacoes = [
                ("1ª rotação: esquerda no filho (caso LR)", filho, "esquerda"),
                ("2ª rotação: direita no nó desbalanceado (caso LR)", pivo, "direita"),
            ]
        else:  # RL
            filho = estado_intermediario["nos"][pivo]["direita"]
            operacoes = [
                ("1ª rotação: direita no filho (caso RL)", filho, "direita"),
                ("2ª rotação: esquerda no nó desbalanceado (caso RL)", pivo, "esquerda"),
            ]

        estado_atual = estado_intermediario
        etapas = []
        for indice, (rotulo, pivo_rotacao, direcao) in enumerate(operacoes):
            if indice == len(operacoes) - 1:
                proximo_estado = estado_final
            else:
                proximo_estado = self._rotacionar_estado(
                    estado_atual, pivo_rotacao, direcao
                )
            etapas.append(
                {
                    "rotulo": rotulo,
                    "pivo": pivo_rotacao,
                    "estado": proximo_estado,
                }
            )
            estado_atual = proximo_estado
        return etapas

    def _rotacionar_estado(self, estado: dict, pivo: int, direcao: str) -> dict:
        """Aplica uma rotação simples a uma cópia do estado visual da árvore."""
        nos = {chave: dados.copy() for chave, dados in estado["nos"].items()}
        raiz = estado["raiz"]

        # Encontra o pai antes de religar os nós; depois da rotação o novo pivô
        # também aponta para o pivô antigo e poderia ser confundido com o pai.
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
            subarvore_transferida = nos[novo_pivo]["esquerda"]
            nos[pivo]["direita"] = subarvore_transferida
            nos[novo_pivo]["esquerda"] = pivo
        else:
            novo_pivo = nos[pivo]["esquerda"]
            subarvore_transferida = nos[novo_pivo]["direita"]
            nos[pivo]["esquerda"] = subarvore_transferida
            nos[novo_pivo]["direita"] = pivo

        if pai is None:
            raiz = novo_pivo
        elif nos[pai]["esquerda"] == pivo:
            nos[pai]["esquerda"] = novo_pivo
        else:
            nos[pai]["direita"] = novo_pivo

        def atualizar_fatores(chave) -> int:
            if chave is None:
                return 0
            altura_esquerda = atualizar_fatores(nos[chave]["esquerda"])
            altura_direita = atualizar_fatores(nos[chave]["direita"])
            nos[chave]["fator"] = altura_esquerda - altura_direita
            return 1 + max(altura_esquerda, altura_direita)

        atualizar_fatores(raiz)
        return {"raiz": raiz, "nos": nos}

    def _reconstruir_etapas_remocao(
        self,
        estado_final: dict,
        eventos: list[tuple[str, int]],
    ) -> tuple[dict, list[dict]]:
        """Reverte as rotações registradas para mostrar a exclusão antes do balanceamento."""
        estados_reversos = [estado_final]
        estado_atual = estado_final

        for direcao, pivo in reversed(eventos):
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
                    f"Não foi possível reconstruir a rotação registrada no nó {pivo}."
                )

            direcao_inversa = "direita" if direcao == "esquerda" else "esquerda"
            estado_atual = self._rotacionar_estado(
                estado_atual, pai, direcao_inversa
            )
            estados_reversos.append(estado_atual)

        estados = list(reversed(estados_reversos))
        total = len(eventos)
        etapas = []
        for indice, (direcao, pivo) in enumerate(eventos):
            sentido = "à esquerda" if direcao == "esquerda" else "à direita"
            etapas.append(
                {
                    "rotulo": f"Rotação {indice + 1}/{total} {sentido} no nó {pivo}",
                    "pivo": pivo,
                    "estado": estados[indice + 1],
                }
            )

        return estados[0], etapas

    def _aguardar_avanco_rotacao(
        self,
        estado: dict,
        pivo: int,
        caso: str,
        mensagem_inicial: str | None = None,
    ) -> None:
        self.estado_visual_atual = estado
        etapa = self.etapas_rotacao[self.indice_etapa_rotacao]
        if self.indice_etapa_rotacao == 0:
            mensagem = mensagem_inicial or (
                f"Desbalanceamento em {pivo} (caso {caso}). Clique para avançar."
            )
        else:
            mensagem = (
                f"Rotação {self.indice_etapa_rotacao} concluída. "
                f"Próxima: {etapa['rotulo']}."
            )

        self._desenhar_estado(
            estado,
            pivo=etapa["pivo"],
            mensagem=mensagem,
        )
        self.botao_avancar_rotacao.config(
            text=f"Avançar rotação ({self.indice_etapa_rotacao + 1}/{len(self.etapas_rotacao)})",
            state=tk.NORMAL,
        )

    def avancar_rotacao(self) -> None:
        if not self.animando or self.indice_etapa_rotacao >= len(self.etapas_rotacao):
            return

        etapa = self.etapas_rotacao[self.indice_etapa_rotacao]
        self.indice_etapa_rotacao += 1
        self.botao_avancar_rotacao.config(state=tk.DISABLED)
        self._animar_transicao(
            self.estado_visual_atual,
            etapa["estado"],
            ao_finalizar=lambda: self._apos_etapa_rotacao(etapa["estado"]),
            mensagem=etapa["rotulo"],
        )

    def _apos_etapa_rotacao(self, estado: dict) -> None:
        self.estado_visual_atual = estado
        if self.indice_etapa_rotacao < len(self.etapas_rotacao):
            proxima = self.etapas_rotacao[self.indice_etapa_rotacao]
            self._aguardar_avanco_rotacao(estado, proxima["pivo"], "dupla")
        else:
            self._finalizar_animacao()

    @staticmethod
    def _calcular_posicoes(estado: dict) -> dict:
        posicoes = {}
        indice = 0
        maior_nivel = 0

        def visitar(chave, nivel: int) -> None:
            nonlocal indice, maior_nivel
            if chave is None:
                return

            no = estado["nos"][chave]
            visitar(no["esquerda"], nivel + 1)
            posicoes[chave] = (60 + indice * 100, 90 + nivel * 100, no["fator"])
            indice += 1
            maior_nivel = max(maior_nivel, nivel)
            visitar(no["direita"], nivel + 1)

        visitar(estado["raiz"], 0)
        return posicoes

    def _desenhar_estado(
        self,
        estado: dict,
        posicoes: dict | None = None,
        pivo: int | None = None,
        cor_pivo: str = "#f57c00",
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
        altura = max(400, 180 + max(y for _, y, _ in posicoes.values()))
        canvas.configure(scrollregion=(0, 0, largura, altura))

        for chave, no in estado["nos"].items():
            x_pai, y_pai, _ = posicoes[chave]
            for filho in (no["esquerda"], no["direita"]):
                if filho is not None and filho in posicoes:
                    x_filho, y_filho, _ = posicoes[filho]
                    canvas.create_line(x_pai, y_pai, x_filho, y_filho, fill="#616161", width=2)

        raio = 30
        for chave, (x, y, fator) in posicoes.items():
            selecionado = chave == pivo
            if selecionado:
                canvas.create_oval(
                    x - raio - 6, y - raio - 6, x + raio + 6, y + raio + 6,
                    outline=cor_pivo, width=3,
                )
            cor = "#d32f2f" if abs(fator) > 1 else "#1976d2"
            canvas.create_oval(
                x - raio, y - raio, x + raio, y + raio,
                fill=cor, outline="#0d47a1", width=2,
            )
            canvas.create_text(
                x, y, text=chave, fill="white", font=("Arial", 9, "bold"), width=52
            )
            canvas.create_text(
                x, y - raio - 12, text=f"FB: {fator}", fill="#424242", font=("Arial", 8)
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
            self._posicoes_inicio_animacao = {
                chave: posicoes_origem.get(
                    chave,
                    (posicoes_destino[chave][0], posicoes_destino[chave][1] - 55, 0),
                )[:2]
                for chave in posicoes_destino
            }

        progresso = (passo + 1) / total_passos
        suave = progresso * progresso * (3 - 2 * progresso)
        interpoladas = {}
        for chave, (x_final, y_final, fator) in posicoes_destino.items():
            x_inicio, y_inicio = self._posicoes_inicio_animacao[chave]
            interpoladas[chave] = (
                x_inicio + (x_final - x_inicio) * suave,
                y_inicio + (y_final - y_inicio) * suave,
                fator,
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

    def _definir_botoes_ativos(self, ativos: bool) -> None:
        estado = tk.NORMAL if ativos else tk.DISABLED
        for botao in self.botoes_operacao:
            botao.config(state=estado)

    def _finalizar_animacao(self) -> None:
        self.atualizar_visualizacao_arvore()
        self.animando = False
        self.etapas_rotacao = []
        self.indice_etapa_rotacao = 0
        self.estado_visual_atual = None
        self.botao_avancar_rotacao.config(
            text="Avançar rotação",
            state=tk.DISABLED,
        )
        self._definir_botoes_ativos(True)


def main() -> None:
    janela = tk.Tk()
    JanelaAVL(janela)
    janela.mainloop()


if __name__ == "__main__":
    main()
