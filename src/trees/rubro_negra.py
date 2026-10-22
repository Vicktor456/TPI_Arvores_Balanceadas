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

	def buscar(self, matricula: str) -> Aluno | None:
	    """
	    Busca um aluno pela matrícula.
	
	    Retorna o objeto Aluno caso encontre.
	    Retorna None se a matrícula não existir.
	    """
	    atual = self.raiz
	
	    while atual != self.NIL:
	        if matricula == atual.aluno.matricula:
	            return atual.aluno
	
	        if matricula < atual.aluno.matricula:
	            atual = atual.esquerda
	        else:
	            atual = atual.direita
	
	    return None

	def remover(self, matricula: str) -> bool:
	    """
	    Remove um aluno pela matrícula.
	
	    Retorna True se removeu.
	    Retorna False se a matrícula não existir.
	    """
	    no_removido = self.raiz
	
	    while no_removido != self.NIL:
	        if matricula == no_removido.aluno.matricula:
	            break
	
	        if matricula < no_removido.aluno.matricula:
	            no_removido = no_removido.esquerda
	        else:
	            no_removido = no_removido.direita
	
	    if no_removido == self.NIL:
	        return False
	
	    no_que_saiu = no_removido
	    cor_original = no_que_saiu.cor
	
	    if no_removido.esquerda == self.NIL:
	        no_para_corrigir = no_removido.direita
	        self._transplantar(no_removido, no_removido.direita)
	
	    elif no_removido.direita == self.NIL:
	        no_para_corrigir = no_removido.esquerda
	        self._transplantar(no_removido, no_removido.esquerda)
	
	    else:
	        # Sucessor: menor nó da subárvore direita.
	        no_que_saiu = self._menor_no(no_removido.direita)
	        cor_original = no_que_saiu.cor
	        no_para_corrigir = no_que_saiu.direita
	
	        if no_que_saiu.pai == no_removido:
	            no_para_corrigir.pai = no_que_saiu
	        else:
	            self._transplantar(no_que_saiu, no_que_saiu.direita)
	
	            no_que_saiu.direita = no_removido.direita
	            no_que_saiu.direita.pai = no_que_saiu
	
	        self._transplantar(no_removido, no_que_saiu)
	
	        no_que_saiu.esquerda = no_removido.esquerda
	        no_que_saiu.esquerda.pai = no_que_saiu
	        no_que_saiu.cor = no_removido.cor
	
	    # Só é necessário corrigir se um nó preto saiu.
	    if cor_original == PRETO:
	        self._corrigir_remocao(no_para_corrigir)
	
	    self.quantidade_nos -= 1
	    return True
	    
	def _transplantar(
		self,
		no_antigo: NoRubroNegra,
		no_novo: NoRubroNegra
	) -> None:
		"""Substitui uma subárvore por outra."""
		if no_antigo.pai == self.NIL:
			self.raiz = no_novo
	
		elif no_antigo == no_antigo.pai.esquerda:
			no_antigo.pai.esquerda = no_novo
	
		else:
			no_antigo.pai.direita = no_novo
	
		no_novo.pai = no_antigo.pai
		
	def _menor_no(self, no: NoRubroNegra) -> NoRubroNegra:
		"""Retorna o nó com a menor matrícula da subárvore."""
		while no.esquerda != self.NIL:
			no = no.esquerda
	
		return no
		
	def _corrigir_remocao(self, no: NoRubroNegra) -> None:
		"""Restaura as propriedades Rubro-Negras após uma remoção."""
		while no != self.raiz and no.cor == PRETO:
	
			if no == no.pai.esquerda:
				irmao = no.pai.direita
	
				# Caso 1: irmão vermelho.
				if irmao.cor == VERMELHO:
					self._recolorir(irmao, PRETO)
					self._recolorir(no.pai, VERMELHO)
					self._rotacao_esquerda(no.pai)
					irmao = no.pai.direita
	
				# Caso 2: irmão preto com filhos pretos.
				if irmao.esquerda.cor == PRETO and irmao.direita.cor == PRETO:
					self._recolorir(irmao, VERMELHO)
					no = no.pai
	
				else:
					# Caso 3: filho direito do irmão é preto.
					if irmao.direita.cor == PRETO:
						self._recolorir(irmao.esquerda, PRETO)
						self._recolorir(irmao, VERMELHO)
						self._rotacao_direita(irmao)
						irmao = no.pai.direita
	
					# Caso 4: filho direito do irmão é vermelho.
					self._recolorir(irmao, no.pai.cor)
					self._recolorir(no.pai, PRETO)
					self._recolorir(irmao.direita, PRETO)
					self._rotacao_esquerda(no.pai)
					no = self.raiz
	
			else:
				# Casos espelhados: no está à direita.
				irmao = no.pai.esquerda
	
				if irmao.cor == VERMELHO:
					self._recolorir(irmao, PRETO)
					self._recolorir(no.pai, VERMELHO)
					self._rotacao_direita(no.pai)
					irmao = no.pai.esquerda
	
				if irmao.direita.cor == PRETO and irmao.esquerda.cor == PRETO:
					self._recolorir(irmao, VERMELHO)
					no = no.pai
	
				else:
					if irmao.esquerda.cor == PRETO:
						self._recolorir(irmao.direita, PRETO)
						self._recolorir(irmao, VERMELHO)
						self._rotacao_esquerda(irmao)
						irmao = no.pai.esquerda
	
					self._recolorir(irmao, no.pai.cor)
					self._recolorir(no.pai, PRETO)
					self._recolorir(irmao.esquerda, PRETO)
					self._rotacao_direita(no.pai)
					no = self.raiz
	
		self._recolorir(no, PRETO)

	def obter_menor(self) -> Aluno | None:
	    """
	    Retorna o aluno com a menor matrícula da árvore.
	
	    Retorna None se a árvore estiver vazia.
	    """
	    if self.raiz == self.NIL:
	        return None
	
	    return self._menor_no(self.raiz).aluno

	def obter_maior(self) -> Aluno | None:
	    """
	    Retorna o aluno com a maior matrícula da árvore.
	
	    Retorna None se a árvore estiver vazia.
	    """
	    if self.raiz == self.NIL:
	        return None
	
	    no_atual = self.raiz
	
	    while no_atual.direita != self.NIL:
	        no_atual = no_atual.direita
	
	    return no_atual.aluno

	def pre_ordem(self) -> list[Aluno]:
	    """Retorna os alunos no caminhamento pré-ordem."""
	    alunos = []
	    self._pre_ordem(self.raiz, alunos)
	    return alunos
	
	
	def _pre_ordem(self, no: NoRubroNegra, alunos: list[Aluno]) -> None:
	    if no != self.NIL:
	        alunos.append(no.aluno)              # Raiz
	        self._pre_ordem(no.esquerda, alunos) # Esquerda
	        self._pre_ordem(no.direita, alunos)  # Direita
	
	def em_ordem(self) -> list[Aluno]:
	    """Retorna os alunos no caminhamento em ordem crescente de matrícula."""
	    alunos = []
	    self._em_ordem(self.raiz, alunos)
	    return alunos
	
	
	def _em_ordem(self, no: NoRubroNegra, alunos: list[Aluno]) -> None:
	    if no != self.NIL:
	        self._em_ordem(no.esquerda, alunos)  # Esquerda
	        alunos.append(no.aluno)              # Raiz
	        self._em_ordem(no.direita, alunos)   # Direita
	
	def pos_ordem(self) -> list[Aluno]:
	    """Retorna os alunos no caminhamento pós-ordem."""
	    alunos = []
	    self._pos_ordem(self.raiz, alunos)
	    return alunos
	
	
	def _pos_ordem(self, no: NoRubroNegra, alunos: list[Aluno]) -> None:
	    if no != self.NIL:
	        self._pos_ordem(no.esquerda, alunos)  # Esquerda
	        self._pos_ordem(no.direita, alunos)   # Direita
	        alunos.append(no.aluno)               # Raiz

	def obter_altura(self) -> int:
	    """
	    Retorna a altura atual da árvore.
	
	    Retorna 0 se a árvore estiver vazia.
	    Uma árvore com apenas a raiz possui altura 1.
	    """
	    return self._altura(self.raiz)
	
	def _altura(self, no: NoRubroNegra) -> int:
    """Calcula a altura da subárvore, ignorando folhas NIL."""
    if no == self.NIL:
        return 0

    return 1 + max(
        self._altura(no.esquerda),
        self._altura(no.direita)
    )

	def obter_quantidade_nos(self) -> int:
	    """
	    Retorna a quantidade atual de alunos armazenados na árvore.
	    """
	    return self.quantidade_nos
		
		    return 1 + max(
		        self._altura(no.esquerda),
		        self._altura(no.direita)
		    )
