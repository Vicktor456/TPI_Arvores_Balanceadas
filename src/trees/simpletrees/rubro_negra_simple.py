import tkinter as tk
from tkinter import messagebox

class NoRN:
    def __init__(self, chave):
        self.chave = chave
        self.pai = None
        self.esquerda = None
        self.direita = None
        self.cor = "VERMELHO"  # Novos nós sempre nascem vermelhos

class ArvoreRubroNegra:
    def __init__(self):
        # Em árvores RN, usamos um nó sentinela nulo (TNULL) sempre PRETO
        self.TNULL = NoRN(0)
        self.TNULL.cor = "PRETO"
        self.raiz = self.TNULL
        self.msg_acao = None  # Para exibir alertas na interface gráfica

    def rotacao_esquerda(self, x):
        y = x.direita
        x.direita = y.esquerda
        if y.esquerda != self.TNULL:
            y.esquerda.pai = x

        y.pai = x.pai
        if x.pai is None:
            self.raiz = y
        elif x == x.pai.esquerda:
            x.pai.esquerda = y
        else:
            x.pai.direita = y
        y.esquerda = x
        x.pai = y

    def rotacao_direita(self, x):
        y = x.esquerda
        x.esquerda = y.direita
        if y.direita != self.TNULL:
            y.direita.pai = x

        y.pai = x.pai
        if x.pai is None:
            self.raiz = y
        elif x == x.pai.direita:
            x.pai.direita = y
        else:
            x.pai.esquerda = y
        y.direita = x
        x.pai = y

    def arrumar_insercao(self, k):
        while k.pai and k.pai.cor == "VERMELHO":
            if k.pai == k.pai.pai.esquerda:
                tio = k.pai.pai.direita
                if tio.cor == "VERMELHO":
                    # CASO 1: Tio é vermelho -> Recoloração
                    if not self.msg_acao: self.msg_acao = ("Recoloração (Tio Vermelho)", k.pai.pai.chave)
                    tio.cor = "PRETO"
                    k.pai.cor = "PRETO"
                    k.pai.pai.cor = "VERMELHO"
                    k = k.pai.pai
                else:
                    if k == k.pai.direita:
                        # CASO 2: Tio preto, triângulo -> Rotação dupla (1ª parte)
                        if not self.msg_acao: self.msg_acao = ("Rotação à Esquerda", k.pai.chave)
                        k = k.pai
                        self.rotacao_esquerda(k)
                    # CASO 3: Tio preto, linha -> Rotação simples
                    if not self.msg_acao: self.msg_acao = ("Rotação à Direita", k.pai.pai.chave)
                    k.pai.cor = "PRETO"
                    k.pai.pai.cor = "VERMELHO"
                    self.rotacao_direita(k.pai.pai)
            else:
                tio = k.pai.pai.esquerda
                if tio.cor == "VERMELHO":
                    if not self.msg_acao: self.msg_acao = ("Recoloração (Tio Vermelho)", k.pai.pai.chave)
                    tio.cor = "PRETO"
                    k.pai.cor = "PRETO"
                    k.pai.pai.cor = "VERMELHO"
                    k = k.pai.pai
                else:
                    if k == k.pai.esquerda:
                        if not self.msg_acao: self.msg_acao = ("Rotação à Direita", k.pai.chave)
                        k = k.pai
                        self.rotacao_direita(k)
                    if not self.msg_acao: self.msg_acao = ("Rotação à Esquerda", k.pai.pai.chave)
                    k.pai.cor = "PRETO"
                    k.pai.pai.cor = "VERMELHO"
                    self.rotacao_esquerda(k.pai.pai)
            if k == self.raiz:
                break
        self.raiz.cor = "PRETO"

    def inserir(self, chave):
        no = NoRN(chave)
        no.pai = None
        no.esquerda = self.TNULL
        no.direita = self.TNULL

        y = None
        x = self.raiz

        # Busca local de inserção como numa BST normal
        while x != self.TNULL:
            y = x
            if no.chave < x.chave:
                x = x.esquerda
            elif no.chave > x.chave:
                x = x.direita
            else:
                return  # Ignora duplicatas

        no.pai = y
        if y is None:
            self.raiz = no
        elif no.chave < y.chave:
            y.esquerda = no
        else:
            y.direita = no

        if no.pai is None:
            no.cor = "PRETO"
            return
        if no.pai.pai is None:
            return

        # Conserta quebras de regra da árvore
        self.arrumar_insercao(no)


class InterfaceRN:
    def __init__(self, window):
        self.window = window
        self.window.title("Visualizador de Árvore Rubro-Negra")
        self.window.geometry("900x650")

        self.rn = ArvoreRubroNegra()
        self.posicoes_atuais = {}
        self.animando = False

        # Painel Superior
        self.frame_controle = tk.Frame(self.window, bg="#f0f0f0", pady=10)
        self.frame_controle.pack(fill=tk.X)

        tk.Label(self.frame_controle, text="Valor:", font=("Arial", 11), bg="#f0f0f0").pack(side=tk.LEFT, padx=(15, 5))

        self.entry_valor = tk.Entry(self.frame_controle, font=("Arial", 11), width=8)
        self.entry_valor.pack(side=tk.LEFT, padx=5)
        self.entry_valor.bind("<Return>", lambda event: self.inserir_no())

        self.btn_inserir = tk.Button(self.frame_controle, text="Inserir", font=("Arial", 10, "bold"), bg="#4CAF50", fg="white", command=self.inserir_no)
        self.btn_inserir.pack(side=tk.LEFT, padx=5)

        # Canvas
        self.canvas = tk.Canvas(self.window, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def calcular_posicoes_alvo(self, no, x, y, desvio_x, dicionario_pos):
        if no == self.rn.TNULL: 
            return
        # Salva também a cor atual do nó
        dicionario_pos[no.chave] = (x, y, no.cor)
        self.calcular_posicoes_alvo(no.esquerda, x - desvio_x, y + 60, desvio_x / 2, dicionario_pos)
        self.calcular_posicoes_alvo(no.direita, x + desvio_x, y + 60, desvio_x / 2, dicionario_pos)

    def inserir_no(self):
        if self.animando: return
        val_str = self.entry_valor.get().strip()
        if not val_str.isdigit() and not (val_str.startswith('-') and val_str[1:].isdigit()): return

        self.rn.msg_acao = None  
        self.rn.inserir(int(val_str))
        self.entry_valor.delete(0, tk.END)
        self.preparar_animacao()

    def preparar_animacao(self):
        largura = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 900
        posicoes_alvo = {}
        self.calcular_posicoes_alvo(self.rn.raiz, largura / 2, 50, largura / 4, posicoes_alvo)

        self.animando = True
        self.btn_inserir.config(state=tk.DISABLED)

        if not self.posicoes_atuais:
            self.posicoes_atuais = {k: (v[0], v[1]) for k, v in posicoes_alvo.items()}
            self.desenhar_estado(posicoes_alvo)
            self.finalizar_animacao(posicoes_alvo)
            return

        acao_info = self.rn.msg_acao
        # Se houve rotação ou recoloração, destaca antes de mover
        if acao_info and acao_info[1] in self.posicoes_atuais:
            texto_acao, chave_alvo = acao_info
            x_alvo, y_alvo = self.posicoes_atuais[chave_alvo]

            self.canvas.create_oval(x_alvo - 25, y_alvo - 25, x_alvo + 25, y_alvo + 25, outline="#ffeb3b", width=4, tags="destaque")
            self.canvas.create_text(x_alvo, y_alvo - 35, text=f"Violação!\n{texto_acao}", fill="#f57f17", font=("Arial", 11, "bold"), justify="center", tags="destaque")
            
            self.window.after(2000, lambda: self.iniciar_deslizamento(posicoes_alvo))
        else:
            self.iniciar_deslizamento(posicoes_alvo)

    def iniciar_deslizamento(self, posicoes_alvo):
        self.canvas.delete("destaque")

        for chave, (x_alvo, y_alvo, _) in posicoes_alvo.items():
            if chave not in self.posicoes_atuais:
                self.posicoes_atuais[chave] = (x_alvo, y_alvo - 30)

        self.animar_passo(0, 60, posicoes_alvo)

    def animar_passo(self, passo, total_passos, posicoes_alvo):
        t = (passo + 1) / total_passos
        posicoes_interpoladas = {}
        
        for chave, (x_alvo, y_alvo, cor) in posicoes_alvo.items():
            x_ini, y_ini = self.posicoes_atuais.get(chave, (x_alvo, y_alvo))
            x_atual = x_ini + (x_alvo - x_ini) * t
            y_atual = y_ini + (y_alvo - y_ini) * t
            posicoes_interpoladas[chave] = (x_atual, y_atual, cor)

        self.desenhar_estado(posicoes_interpoladas)

        if passo + 1 < total_passos:
            self.window.after(20, lambda: self.animar_passo(passo + 1, total_passos, posicoes_alvo))
        else:
            self.finalizar_animacao(posicoes_alvo)

    def finalizar_animacao(self, posicoes_alvo):
        self.posicoes_atuais = {k: (v[0], v[1]) for k, v in posicoes_alvo.items()}
        self.animando = False
        self.btn_inserir.config(state=tk.NORMAL)

    def desenhar_estado(self, mapa_posicoes):
        self.canvas.delete("nos_e_linhas")
        if self.rn.raiz == self.rn.TNULL: return

        self._desenhar_linhas(self.rn.raiz, mapa_posicoes)

        raio = 20
        for chave, (x, y, cor) in mapa_posicoes.items():
            # Define as cores do nó (Vermelho vs Preto)
            cor_fundo = "#d32f2f" if cor == "VERMELHO" else "#212121"
            cor_borda = "#b71c1c" if cor == "VERMELHO" else "#000000"

            self.canvas.create_oval(x - raio, y - raio, x + raio, y + raio, fill=cor_fundo, outline=cor_borda, width=2, tags="nos_e_linhas")
            self.canvas.create_text(x, y, text=str(chave), fill="white", font=("Arial", 10, "bold"), tags="nos_e_linhas")

    def _desenhar_linhas(self, no, mapa_posicoes):
        if no == self.rn.TNULL or no.chave not in mapa_posicoes: return

        x_pai, y_pai, _ = mapa_posicoes[no.chave]

        if no.esquerda != self.rn.TNULL and no.esquerda.chave in mapa_posicoes:
            x_filho, y_filho, _ = mapa_posicoes[no.esquerda.chave]
            self.canvas.create_line(x_pai, y_pai, x_filho, y_filho, fill="#555555", width=2, tags="nos_e_linhas")
            self._desenhar_linhas(no.esquerda, mapa_posicoes)

        if no.direita != self.rn.TNULL and no.direita.chave in mapa_posicoes:
            x_filho, y_filho, _ = mapa_posicoes[no.direita.chave]
            self.canvas.create_line(x_pai, y_pai, x_filho, y_filho, fill="#555555", width=2, tags="nos_e_linhas")
            self._desenhar_linhas(no.direita, mapa_posicoes)


if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceRN(root)
    root.mainloop()