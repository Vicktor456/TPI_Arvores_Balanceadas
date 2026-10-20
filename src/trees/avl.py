from dataclasses import dataclass
from typing import Optional


@dataclass
class Aluno:
    matricula: str
    nome: str
    curso: str
    periodo: int


class NoAVL:
    def __init__(self, aluno: Aluno):
        self.aluno = aluno
        self.esquerda: Optional[NoAVL] = None
        self.direita: Optional[NoAVL] = None
        self.altura = 1


class ArvoreAVL:
    def __init__(self):
        self.raiz: Optional[NoAVL] = None
        self.quantidade_nos = 0
        self.rotacoes = 0

    def _altura(self, no: Optional[NoAVL]) -> int:
        return no.altura if no else 0

    def _atualizar_altura(self, no: NoAVL) -> None:
        no.altura = 1 + max(
            self._altura(no.esquerda),
            self._altura(no.direita)
        )

    def _fator_balanceamento(self, no: Optional[NoAVL]) -> int:
        if no is None:
            return 0

        return self._altura(no.esquerda) - self._altura(no.direita)

    def _rotacao_direita(self, no_desbalanceado: NoAVL) -> NoAVL:
        novo_pai = no_desbalanceado.esquerda
        subarvore_transferida = novo_pai.direita

        novo_pai.direita = no_desbalanceado
        no_desbalanceado.esquerda = subarvore_transferida

        self._atualizar_altura(no_desbalanceado)
        self._atualizar_altura(novo_pai)

        self.rotacoes += 1
        return novo_pai

    def _rotacao_esquerda(self, no_desbalanceado: NoAVL) -> NoAVL:
        novo_pai = no_desbalanceado.direita
        subarvore_transferida = novo_pai.esquerda

        novo_pai.esquerda = no_desbalanceado
        no_desbalanceado.direita = subarvore_transferida

        self._atualizar_altura(no_desbalanceado)
        self._atualizar_altura(novo_pai)

        self.rotacoes += 1
        return novo_pai

    def inserir(self, aluno: Aluno) -> bool:
        """
        Insere um aluno pela matrícula.
        Retorna True se inseriu.
        Retorna False se a matrícula já existir.
        """
        self.raiz, inserido = self._inserir(self.raiz, aluno)

        if inserido:
            self.quantidade_nos += 1

        return inserido

    def _inserir(self, no: Optional[NoAVL], aluno: Aluno) -> tuple[NoAVL, bool]:
        if no is None:
            return NoAVL(aluno), True

        if aluno.matricula < no.aluno.matricula:
            no.esquerda, inserido = self._inserir(no.esquerda, aluno)

        elif aluno.matricula > no.aluno.matricula:
            no.direita, inserido = self._inserir(no.direita, aluno)

        else:
            return no, False  # Matrícula duplicada

        self._atualizar_altura(no)
        balanceamento = self._fator_balanceamento(no)

        # Caso LL
        if balanceamento > 1 and aluno.matricula < no.esquerda.aluno.matricula:
            return self._rotacao_direita(no), inserido

        # Caso RR
        if balanceamento < -1 and aluno.matricula > no.direita.aluno.matricula:
            return self._rotacao_esquerda(no), inserido

        # Caso LR
        if balanceamento > 1 and aluno.matricula > no.esquerda.aluno.matricula:
            no.esquerda = self._rotacao_esquerda(no.esquerda)
            return self._rotacao_direita(no), inserido

        # Caso RL
        if balanceamento < -1 and aluno.matricula < no.direita.aluno.matricula:
            no.direita = self._rotacao_direita(no.direita)
            return self._rotacao_esquerda(no), inserido

        return no, inserido

    def buscar(self, matricula: str) -> Aluno | None:
        """
        Busca um aluno pela matrícula.

        Retorna o objeto Aluno caso encontre.
        Retorna None caso a matrícula não exista.
        """
        no_atual = self.raiz

        while no_atual is not None:
            if matricula == no_atual.aluno.matricula:
                return no_atual.aluno

            if matricula < no_atual.aluno.matricula:
                no_atual = no_atual.esquerda
            else:
                no_atual = no_atual.direita

        return None

    def remover(self, matricula: str) -> bool:
        """
        Remove um aluno pela matrícula.

        Retorna True se removeu.
        Retorna False se a matrícula não existir.
        """
        self.raiz, removido = self._remover(self.raiz, matricula)

        if removido:
            self.quantidade_nos -= 1

        return removido

    def _remover(
        self,
        no: Optional[NoAVL],
        matricula: str
    ) -> tuple[Optional[NoAVL], bool]:

        if no is None:
            return None, False

        if matricula < no.aluno.matricula:
            no.esquerda, removido = self._remover(no.esquerda, matricula)

        elif matricula > no.aluno.matricula:
            no.direita, removido = self._remover(no.direita, matricula)

        else:
            removido = True

            # Caso 1: nó sem filho à esquerda
            if no.esquerda is None:
                return no.direita, removido

            # Caso 2: nó sem filho à direita
            if no.direita is None:
                return no.esquerda, removido

            # Caso 3: nó com dois filhos.
            # Substitui pelo sucessor: menor nó da subárvore direita.
            sucessor = self._menor_no(no.direita)
            no.aluno = sucessor.aluno

            # Remove o sucessor sem alterar quantidade_nos novamente.
            no.direita, _ = self._remover(
                no.direita,
                sucessor.aluno.matricula
            )

        # Atualiza a altura e verifica o balanceamento.
        self._atualizar_altura(no)
        balanceamento = self._fator_balanceamento(no)

        # Caso LL
        if balanceamento > 1 and self._fator_balanceamento(no.esquerda) >= 0:
            return self._rotacao_direita(no), removido

        # Caso LR
        if balanceamento > 1 and self._fator_balanceamento(no.esquerda) < 0:
            no.esquerda = self._rotacao_esquerda(no.esquerda)
            return self._rotacao_direita(no), removido

        # Caso RR
        if balanceamento < -1 and self._fator_balanceamento(no.direita) <= 0:
            return self._rotacao_esquerda(no), removido

        # Caso RL
        if balanceamento < -1 and self._fator_balanceamento(no.direita) > 0:
            no.direita = self._rotacao_direita(no.direita)
            return self._rotacao_esquerda(no), removido

        return no, removido

    def _menor_no(self, no: NoAVL) -> NoAVL:
        """Retorna o nó de menor matrícula a partir de um nó."""
        atual = no

        while atual.esquerda is not None:
            atual = atual.esquerda

        return atual

    def obter_menor(self) -> Aluno | None:
        """
        Retorna o aluno com a menor matrícula da árvore.

        Retorna None se a árvore estiver vazia.
        """
        if self.raiz is None:
            return None

        no_atual = self.raiz

        while no_atual.esquerda is not None:
            no_atual = no_atual.esquerda

        return no_atual.aluno

    def obter_maior(self) -> Aluno | None:
        """
        Retorna o aluno com a maior matrícula da árvore.
        Retorna None se a árvore estiver vazia.
        """
        if self.raiz is None:
            return None

        no_atual = self.raiz

        while no_atual.direita is not None:
            no_atual = no_atual.direita

        return no_atual.aluno