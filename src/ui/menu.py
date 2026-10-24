import tkinter as tk
import sys
from pathlib import Path

# Permite executar este arquivo diretamente ou como módulo a partir do projeto.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.trees.avl import ArvoreAVL
from src.trees.rubro_negra import ArvoreRubroNegra
from src.ui.avl_window import JanelaAVL
from src.ui.rubro_negra_window import JanelaRubroNegra
from src.ui.resultados_window import JanelaResultados

class MenuArvores:
    def __init__(self, janela: tk.Tk) -> None:
        self.janela = janela
        self.avl = ArvoreAVL()
        self.rubro_negra = ArvoreRubroNegra()
        
        self.janela.title("Sistema Acadêmico - Árvores Balanceadas")
        self.janela.geometry("460x330")
        self.janela.resizable(False, False)

        self.arvore_selecionada: str | None = None
        self.janela_avl: tk.Toplevel | None = None
        self.janela_rubro_negra: tk.Toplevel | None = None
        self.janela_resultados: tk.Toplevel | None = None

        quadro = tk.Frame(self.janela, padx=30, pady=25)
        quadro.pack(expand=True, fill=tk.BOTH)

        tk.Label(
            quadro,
            text="Árvores Balanceadas",
            font=("Arial", 18, "bold"),
        ).pack(pady=(0, 8))

        tk.Label(
            quadro,
            text="Selecione a estrutura que deseja utilizar:",
            font=("Arial", 11),
        ).pack(pady=(0, 18))

        botoes = tk.Frame(quadro)
        botoes.pack()

        self.botao_avl = tk.Button(
            botoes,
            text="Árvore AVL",
            width=16,
            font=("Arial", 11, "bold"),
            command=self.abrir_avl,
        )
        self.botao_avl.pack(side=tk.LEFT, padx=8)

        tk.Button(
            botoes,
            text="Árvore Rubro-Negra",
            width=19,
            font=("Arial", 11, "bold"),
            command=self.abrir_rubro_negra,
        ).pack(side=tk.LEFT, padx=8)

        self.botao_resultados = tk.Button(
            quadro,
            text="Resultados dos testes",
            width=31,
            font=("Arial", 11, "bold"),
            command=self.abrir_resultados,
        )
        self.botao_resultados.pack(pady=(16, 0))

        self.rotulo_selecao = tk.Label(
            quadro,
            text="Nenhuma árvore selecionada",
            font=("Arial", 10),
            fg="#555555",
        )
        self.rotulo_selecao.pack(pady=(20, 0))

    def selecionar_arvore(self, nome: str) -> None:
        self.arvore_selecionada = nome
        self.rotulo_selecao.config(text=f"Árvore selecionada: {nome}", fg="#1b5e20")

    def abrir_avl(self) -> None:
        self.selecionar_arvore("AVL")
        if self.janela_avl is not None and self.janela_avl.winfo_exists():
            self.janela_avl.lift()
            self.janela_avl.focus_force()
            return

        janela_avl = tk.Toplevel(self.janela)
        self.janela_avl = janela_avl
        JanelaAVL(janela_avl, self.avl)
        
    def abrir_rubro_negra(self) -> None:
        self.selecionar_arvore("Rubro-Negra")
        if self.janela_rubro_negra is not None and self.janela_rubro_negra.winfo_exists():
            self.janela_rubro_negra.lift()
            self.janela_rubro_negra.focus_force()
            return

        janela_rubro_negra = tk.Toplevel(self.janela)
        self.janela_rubro_negra = janela_rubro_negra
        JanelaRubroNegra(janela_rubro_negra, self.rubro_negra)

    def abrir_resultados(self) -> None:
        if self.janela_resultados is not None and self.janela_resultados.winfo_exists():
            self.janela_resultados.lift()
            self.janela_resultados.focus_force()
            return
        janela_resultados = tk.Toplevel(self.janela)
        self.janela_resultados = janela_resultados
        JanelaResultados(janela_resultados)


def main() -> None:
    janela = tk.Tk()
    MenuArvores(janela)
    janela.mainloop()


if __name__ == "__main__":
    main()
