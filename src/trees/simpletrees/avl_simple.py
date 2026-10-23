import tkinter as tk
from tkinter import messagebox

class No:
    def __init__(self, chave):
        self.chave = chave
        self.esquerda = None
        self.direita = None
        self.altura = 1

class ArvoreAVL:
    def __init__(self):
        # Armazena a última rotação na forma: ("Nome da Rotação", chave_do_no)
        self.msg_rotacao = None 

    def get_altura(self, no):
        if not no:
            return 0
        return no.altura

    def get_fator_balanceamento(self, no):
        if not no:
            return 0
        return self.get_altura(no.esquerda) - self.get_altura(no.direita)

    def rotacao_direita(self, z):
        y = z.esquerda
        T3 = y.direita

        y.direita = z
        z.esquerda = T3

        z.altura = 1 + max(self.get_altura(z.esquerda), self.get_altura(z.direita))
        y.altura = 1 + max(self.get_altura(y.esquerda), self.get_altura(y.direita))
        return y

    def rotacao_esquerda(self, z):
        y = z.direita
        T2 = y.esquerda

        y.esquerda = z
        z.direita = T2

        z.altura = 1 + max(self.get_altura(z.esquerda), self.get_altura(z.direita))
        y.altura = 1 + max(self.get_altura(y.esquerda), self.get_altura(y.direita))
        return y

    def inserir(self, raiz, chave):
        if not raiz:
            return No(chave)
        elif chave < raiz.chave:
            raiz.esquerda = self.inserir(raiz.esquerda, chave)
        elif chave > raiz.chave:
            raiz.direita = self.inserir(raiz.direita, chave)
        else:
            return raiz

        raiz.altura = 1 + max(self.get_altura(raiz.esquerda), self.get_altura(raiz.direita))
        fb = self.get_fator_balanceamento(raiz)

        # Verificando desbalanceamentos e registrando a rotação
        if fb > 1 and self.get_fator_balanceamento(raiz.esquerda) >= 0:
            if not self.msg_rotacao: self.msg_rotacao = ("Rotação à Direita (LL)", raiz.chave)
            return self.rotacao_direita(raiz)

        if fb > 1 and self.get_fator_balanceamento(raiz.esquerda) < 0:
            if not self.msg_rotacao: self.msg_rotacao = ("Rotação Esq-Dir (LR)", raiz.chave)
            raiz.esquerda = self.rotacao_esquerda(raiz.esquerda)
            return self.rotacao_direita(raiz)

        if fb < -1 and self.get_fator_balanceamento(raiz.direita) <= 0:
            if not self.msg_rotacao: self.msg_rotacao = ("Rotação à Esquerda (RR)", raiz.chave)
            return self.rotacao_esquerda(raiz)

        if fb < -1 and self.get_fator_balanceamento(raiz.direita) > 0:
            if not self.msg_rotacao: self.msg_rotacao = ("Rotação Dir-Esq (RL)", raiz.chave)
            raiz.direita = self.rotacao_direita(raiz.direita)
            return self.rotacao_esquerda(raiz)

        return raiz

    def get_menor_valor_no(self, no):
        atual = no
        while atual.esquerda is not None:
            atual = atual.esquerda
        return atual

    def remover(self, raiz, chave):
        if not raiz:
            return raiz

        if chave < raiz.chave:
            raiz.esquerda = self.remover(raiz.esquerda, chave)
        elif chave > raiz.chave:
            raiz.direita = self.remover(raiz.direita, chave)
        else:
            if raiz.esquerda is None:
                temp = raiz.direita
                raiz = None
                return temp
            elif raiz.direita is None:
                temp = raiz.esquerda
                raiz = None
                return temp

            temp = self.get_menor_valor_no(raiz.direita)
            raiz.chave = temp.chave
            raiz.direita = self.remover(raiz.direita, temp.chave)

        if raiz is None:
            return raiz

        raiz.altura = 1 + max(self.get_altura(raiz.esquerda), self.get_altura(raiz.direita))
        fb = self.get_fator_balanceamento(raiz)

        if fb > 1 and self.get_fator_balanceamento(raiz.esquerda) >= 0:
            if not self.msg_rotacao: self.msg_rotacao = ("Rotação à Direita (LL)", raiz.chave)
            return self.rotacao_direita(raiz)

        if fb > 1 and self.get_fator_balanceamento(raiz.esquerda) < 0:
            if not self.msg_rotacao: self.msg_rotacao = ("Rotação Esq-Dir (LR)", raiz.chave)
            raiz.esquerda = self.rotacao_esquerda(raiz.esquerda)
            return self.rotacao_direita(raiz)

        if fb < -1 and self.get_fator_balanceamento(raiz.direita) <= 0:
            if not self.msg_rotacao: self.msg_rotacao = ("Rotação à Esquerda (RR)", raiz.chave)
            return self.rotacao_esquerda(raiz)

        if fb < -1 and self.get_fator_balanceamento(raiz.direita) > 0:
            if not self.msg_rotacao: self.msg_rotacao = ("Rotação Dir-Esq (RL)", raiz.chave)
            raiz.direita = self.rotacao_direita(raiz.direita)
            return self.rotacao_esquerda(raiz)

        return raiz


class InterfaceAVL:
    def __init__(self, window):
        self.window = window
        self.window.title("Visualizador de Árvore AVL Animado")
        self.window.geometry("900x650")

        self.avl = ArvoreAVL()
        self.raiz = None
        self.posicoes_atuais = {}  
        self.animando = False

        self.frame_controle = tk.Frame(self.window, bg="#f0f0f0", pady=10)
        self.frame_controle.pack(fill=tk.X)

        tk.Label(self.frame_controle, text="Valor:", font=("Arial", 11), bg="#f0f0f0").pack(side=tk.LEFT, padx=(15, 5))

        self.entry_valor = tk.Entry(self.frame_controle, font=("Arial", 11), width=8)
        self.entry_valor.pack(side=tk.LEFT, padx=5)
        self.entry_valor.bind("<Return>", lambda event: self.inserir_no())

        self.btn_inserir = tk.Button(self.frame_controle, text="Inserir", font=("Arial", 10, "bold"), bg="#4CAF50", fg="white", command=self.inserir_no)
        self.btn_inserir.pack(side=tk.LEFT, padx=5)

        self.btn_remover = tk.Button(self.frame_controle, text="Remover", font=("Arial", 10, "bold"), bg="#f44336", fg="white", command=self.remover_no)
        self.btn_remover.pack(side=tk.LEFT, padx=5)

        self.canvas = tk.Canvas(self.window, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def calcular_posicoes_alvo(self, no, x, y, desvio_x, dicionario_pos):
        if not no: return
        dicionario_pos[no.chave] = (x, y, self.avl.get_fator_balanceamento(no))
        if no.esquerda:
            self.calcular_posicoes_alvo(no.esquerda, x - desvio_x, y + 60, desvio_x / 2, dicionario_pos)
        if no.direita:
            self.calcular_posicoes_alvo(no.direita, x + desvio_x, y + 60, desvio_x / 2, dicionario_pos)

    def inserir_no(self):
        if self.animando: return
        val_str = self.entry_valor.get().strip()
        if not val_str.isdigit() and not (val_str.startswith('-') and val_str[1:].isdigit()): return

        # Zera a mensagem de rotação antes da operação
        self.avl.msg_rotacao = None  
        self.raiz = self.avl.inserir(self.raiz, int(val_str))
        self.entry_valor.delete(0, tk.END)
        self.preparar_animacao()

    def remover_no(self):
        if self.animando: return
        val_str = self.entry_valor.get().strip()
        if not val_str.isdigit() and not (val_str.startswith('-') and val_str[1:].isdigit()): return

        # Zera a mensagem de rotação antes da operação
        self.avl.msg_rotacao = None
        self.raiz = self.avl.remover(self.raiz, int(val_str))
        self.entry_valor.delete(0, tk.END)
        self.preparar_animacao()

    def preparar_animacao(self):
        largura = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 900
        posicoes_alvo = {}
        self.calcular_posicoes_alvo(self.raiz, largura / 2, 50, largura / 4, posicoes_alvo)

        self.animando = True
        self.btn_inserir.config(state=tk.DISABLED)
        self.btn_remover.config(state=tk.DISABLED)

        # Trata o primeiro nó inserido
        if not self.posicoes_atuais:
            self.posicoes_atuais = {k: (v[0], v[1]) for k, v in posicoes_alvo.items()}
            self.desenhar_estado(posicoes_alvo)
            self.finalizar_animacao(posicoes_alvo)
            return

        # Verifica se alguma rotação ocorreu
        rotacao_info = self.avl.msg_rotacao
        if rotacao_info and rotacao_info[1] in self.posicoes_atuais:
            texto_rotacao, chave_desbalanceada = rotacao_info
            x_desb, y_desb = self.posicoes_atuais[chave_desbalanceada]

            # Destaca o nó em vermelho e exibe o nome da rotação
            self.canvas.create_oval(x_desb - 25, y_desb - 25, x_desb + 25, y_desb + 25, outline="red", width=3, tags="destaque")
            self.canvas.create_text(x_desb, y_desb - 35, text=f"Desbalanceado!\n{texto_rotacao}", fill="red", font=("Arial", 11, "bold"), justify="center", tags="destaque")
            
            # Aguarda 2000 ms (2 segundos) antes de começar a mover os nós
            self.window.after(2000, lambda: self.iniciar_deslizamento(posicoes_alvo))
        else:
            # Sem rotação, anima direto
            self.iniciar_deslizamento(posicoes_alvo)

    def iniciar_deslizamento(self, posicoes_alvo):
        # Remove o texto de aviso se houver
        self.canvas.delete("destaque")

        # Configura a posição inicial de novos nós (para surgirem de cima)
        for chave, (x_alvo, y_alvo, _) in posicoes_alvo.items():
            if chave not in self.posicoes_atuais:
                self.posicoes_atuais[chave] = (x_alvo, y_alvo - 30)

        # Aumentamos os frames para 60 para deixar bem mais suave e lento
        self.animar_passo(0, 60, posicoes_alvo)

    def animar_passo(self, passo, total_passos, posicoes_alvo):
        t = (passo + 1) / total_passos

        posicoes_interpoladas = {}
        for chave, (x_alvo, y_alvo, fb) in posicoes_alvo.items():
            x_ini, y_ini = self.posicoes_atuais.get(chave, (x_alvo, y_alvo))
            x_atual = x_ini + (x_alvo - x_ini) * t
            y_atual = y_ini + (y_alvo - y_ini) * t
            posicoes_interpoladas[chave] = (x_atual, y_atual, fb)

        self.desenhar_estado(posicoes_interpoladas)

        if passo + 1 < total_passos:
            # Intervalo de 20ms por frame. Com 60 frames, a animação leva 1.2 segundos
            self.window.after(20, lambda: self.animar_passo(passo + 1, total_passos, posicoes_alvo))
        else:
            self.finalizar_animacao(posicoes_alvo)

    def finalizar_animacao(self, posicoes_alvo):
        self.posicoes_atuais = {k: (v[0], v[1]) for k, v in posicoes_alvo.items()}
        self.animando = False
        self.btn_inserir.config(state=tk.NORMAL)
        self.btn_remover.config(state=tk.NORMAL)

    def desenhar_estado(self, mapa_posicoes):
        self.canvas.delete("nos_e_linhas")
        if not self.raiz: return

        self._desenhar_linhas(self.raiz, mapa_posicoes)

        raio = 20
        for chave, (x, y, fb) in mapa_posicoes.items():
            # Define tags="nos_e_linhas" para podermos apagar facilmente no canvas
            self.canvas.create_oval(x - raio, y - raio, x + raio, y + raio, fill="#2196F3", outline="#0d47a1", width=2, tags="nos_e_linhas")
            self.canvas.create_text(x, y, text=str(chave), fill="white", font=("Arial", 10, "bold"), tags="nos_e_linhas")
            self.canvas.create_text(x, y - raio - 8, text=f"FB:{fb}", fill="#666666", font=("Arial", 8), tags="nos_e_linhas")

    def _desenhar_linhas(self, no, mapa_posicoes):
        if not no or no.chave not in mapa_posicoes: return

        x_pai, y_pai, _ = mapa_posicoes[no.chave]

        if no.esquerda and no.esquerda.chave in mapa_posicoes:
            x_filho, y_filho, _ = mapa_posicoes[no.esquerda.chave]
            self.canvas.create_line(x_pai, y_pai, x_filho, y_filho, fill="#555555", width=2, tags="nos_e_linhas")
            self._desenhar_linhas(no.esquerda, mapa_posicoes)

        if no.direita and no.direita.chave in mapa_posicoes:
            x_filho, y_filho, _ = mapa_posicoes[no.direita.chave]
            self.canvas.create_line(x_pai, y_pai, x_filho, y_filho, fill="#555555", width=2, tags="nos_e_linhas")
            self._desenhar_linhas(no.direita, mapa_posicoes)

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceAVL(root)
    root.mainloop()