from dataclasses import dataclass
from typing import Optional


VERMELHO = "VERMELHO"
PRETO = "PRETO"


@dataclass
class Aluno:
    matricula: str
    nome: str
    curso: str
    periodo: int


class NoRubroNegra:
    def __init__(
        self,
        aluno: Optional[Aluno] = None,
        cor: str = VERMELHO
    ):
        self.aluno = aluno
        self.cor = cor
        self.esquerda = None
        self.direita = None
        self.pai = None


class ArvoreRubroNegra:
    def __init__(self):
        # Folha NIL única, sempre preta.
        self.NIL = NoRubroNegra(cor=PRETO)
        self.NIL.esquerda = self.NIL
        self.NIL.direita = self.NIL
        self.NIL.pai = self.NIL

        self.raiz = self.NIL
        self.quantidade_nos = 0
        self.rotacoes = 0
        self.recoloracoes = 0

    def _recolorir(self, no: NoRubroNegra, nova_cor: str) -> None:
	    """Altera a cor de um nó real e contabiliza a recoloração."""
	    if no != self.NIL and no.cor != nova_cor:
	        no.cor = nova_cor
	        self.recoloracoes += 1

    def _rotacao_esquerda(self, no_desbalanceado: NoRubroNegra) -> None:
        novo_pai = no_desbalanceado.direita

        no_desbalanceado.direita = novo_pai.esquerda

        if novo_pai.esquerda != self.NIL:
            novo_pai.esquerda.pai = no_desbalanceado

        novo_pai.pai = no_desbalanceado.pai

        if no_desbalanceado.pai == self.NIL:
            self.raiz = novo_pai

        elif no_desbalanceado == no_desbalanceado.pai.esquerda:
            no_desbalanceado.pai.esquerda = novo_pai

        else:
            no_desbalanceado.pai.direita = novo_pai

        novo_pai.esquerda = no_desbalanceado
        no_desbalanceado.pai = novo_pai

        self.rotacoes += 1

    def _rotacao_direita(self, no_desbalanceado: NoRubroNegra) -> None:
        novo_pai = no_desbalanceado.esquerda

        no_desbalanceado.esquerda = novo_pai.direita

        if novo_pai.direita != self.NIL:
            novo_pai.direita.pai = no_desbalanceado

        novo_pai.pai = no_desbalanceado.pai

        if no_desbalanceado.pai == self.NIL:
            self.raiz = novo_pai

        elif no_desbalanceado == no_desbalanceado.pai.direita:
            no_desbalanceado.pai.direita = novo_pai

        else:
            no_desbalanceado.pai.esquerda = novo_pai

        novo_pai.direita = no_desbalanceado
        no_desbalanceado.pai = novo_pai

        self.rotacoes += 1

    def inserir(self, aluno: Aluno) -> bool:
        """
        Insere um aluno pela matrícula.

        Retorna True se inseriu.
        Retorna False se a matrícula já existir.
        """
        pai = self.NIL
        atual = self.raiz

        # Busca a posição adequada e impede matrícula duplicada.
        while atual != self.NIL:
            pai = atual

            if aluno.matricula < atual.aluno.matricula:
                atual = atual.esquerda

            elif aluno.matricula > atual.aluno.matricula:
                atual = atual.direita

            else:
                return False

        novo_no = NoRubroNegra(aluno, VERMELHO)
        novo_no.esquerda = self.NIL
        novo_no.direita = self.NIL
        novo_no.pai = pai

        if pai == self.NIL:
            self.raiz = novo_no

        elif aluno.matricula < pai.aluno.matricula:
            pai.esquerda = novo_no

        else:
            pai.direita = novo_no

        self._corrigir_insercao(novo_no)
        self.quantidade_nos += 1

        return True

    def _corrigir_insercao(self, no: NoRubroNegra) -> None:
        """Restaura as propriedades Rubro-Negras após inserir um nó."""
        while no.pai.cor == VERMELHO:

            # Pai está na subárvore esquerda do avô.
            if no.pai == no.pai.pai.esquerda:
                tio = no.pai.pai.direita

                # Caso 1: tio vermelho.
                if tio.cor == VERMELHO:
                    self._recolorir(no.pai, PRETO)
                    self._recolorir(tio, PRETO)
                    self._recolorir(no.pai.pai, VERMELHO)
                    no = no.pai.pai

                else:
                    # Caso 2: nó é filho direito.
                    if no == no.pai.direita:
                        no = no.pai
                        self._rotacao_esquerda(no)

                    # Caso 3: nó é filho esquerdo.
                    self._recolorir(no.pai, PRETO)
                    self._recolorir(no.pai.pai, VERMELHO)
                    self._rotacao_direita(no.pai.pai)

            # Pai está na subárvore direita do avô.
            else:
                tio = no.pai.pai.esquerda

                # Caso 1 espelhado: tio vermelho.
                if tio.cor == VERMELHO:
                    self._recolorir(no.pai, PRETO)
                    self._recolorir(tio, PRETO)
                    self._recolorir(no.pai.pai, VERMELHO)
                    no = no.pai.pai

                else:
                    # Caso 2 espelhado: nó é filho esquerdo.
                    if no == no.pai.esquerda:
                        no = no.pai
                        self._rotacao_direita(no)

                    # Caso 3 espelhado: nó é filho direito.
                    self._recolorir(no.pai, PRETO)
                    self._recolorir(no.pai.pai, VERMELHO)
                    self._rotacao_esquerda(no.pai.pai)

        # A raiz deve ser sempre preta.
        self._recolorir(self.raiz, PRETO)
