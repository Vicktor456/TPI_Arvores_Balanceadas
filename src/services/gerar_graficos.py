"""Gera gráficos SVG dos resultados resumidos dos experimentos."""
import csv
import html
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SUMMARY_PATH = ROOT / "testes" / "resultados" / "resumo.csv"
OUTPUT_DIR = ROOT / "testes" / "graficos"
TREE_COLORS = {"AVL": "#24628a", "Rubro-Negra": "#bd594b"}
TREE_ORDER = ("AVL", "Rubro-Negra")
INPUT_ORDER = (("crescente", "Crescente"), ("aleatoria", "Aleatória"))
N = 10000


def format_number(value: float, decimals: int = 3) -> str:
    if value.is_integer():
        return f"{int(value):,}".replace(",", ".")
    return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def chart_svg(title: str, unit: str, rows: list[tuple[str, str, float]]) -> str:
    width = 760
    left = 220
    right = 112
    top = 66
    row_step = 48
    bottom = 48
    height = top + row_step * len(rows) + bottom
    plot_width = width - left - right
    max_value = max(value for _, _, value in rows) or 1
    axis_max = max_value * 1.12
    grid_steps = 4
    axis_decimals = 1 if unit.startswith("ms") or unit == "nós visitados" else 0

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">',
        f"<title>{html.escape(title)}</title>",
        f"<desc>Comparação AVL e Rubro-Negra para n igual a 10.000. Tempos são medianas em cinco repetições.</desc>",
        '<rect width="100%" height="100%" fill="#f7f9fb"/>',
        f'<text x="22" y="29" fill="#17324d" font-family="Arial, sans-serif" font-size="18" font-weight="700">{html.escape(title)}</text>',
        f'<text x="22" y="49" fill="#52687a" font-family="Arial, sans-serif" font-size="12">n = 10.000 · unidade: {html.escape(unit)}</text>',
    ]

    for tick in range(grid_steps + 1):
        value = axis_max * tick / grid_steps
        x = left + plot_width * tick / grid_steps
        parts.append(
            f'<line x1="{x:.1f}" y1="{top - 6}" x2="{x:.1f}" y2="{top + row_step * len(rows) - 9}" stroke="#d9e1e8" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{x:.1f}" y="{height - 18}" fill="#607589" font-family="Arial, sans-serif" font-size="11" text-anchor="middle">{format_number(value, axis_decimals)}</text>'
        )

    for i, (label, tree, value) in enumerate(rows):
        y = top + i * row_step
        bar_width = plot_width * value / axis_max
        parts.append(
            f'<text x="{left - 12}" y="{y + 17}" fill="#263c4d" font-family="Arial, sans-serif" font-size="12" text-anchor="end">{html.escape(label)}</text>'
        )
        parts.append(
            f'<rect x="{left}" y="{y}" width="{bar_width:.2f}" height="25" rx="3" fill="{TREE_COLORS[tree]}"/>'
        )
        parts.append(
            f'<text x="{left + bar_width + 7:.2f}" y="{y + 17}" fill="#263c4d" font-family="Arial, sans-serif" font-size="12" font-weight="600">{format_number(value)}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def load_summary() -> dict[tuple[str, str, str, str], dict[str, str]]:
    with SUMMARY_PATH.open(encoding="utf-8-sig", newline="") as stream:
        rows = csv.DictReader(stream)
        return {
            (row["n"], row["ordem"], row["arvore"], row["percentual_remocao"]): row
            for row in rows
        }


def build_rows(index, metric: str, removal_percent: int | None = None):
    rows = []
    for order, order_label in INPUT_ORDER:
        for tree in TREE_ORDER:
            percent = removal_percent or 10
            data = index[(str(N), order, tree, str(percent))]
            rows.append((f"{order_label} · {tree}", tree, float(data[metric])))
    return rows


def main() -> None:
    index = load_summary()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    charts = {
        "altura_antes.svg": ("Altura após inserção", "nós", build_rows(index, "altura_antes")),
        "rotacoes_insercao.svg": ("Rotações na inserção", "rotações", build_rows(index, "rotacoes_insercao")),
        "recoloracoes_insercao.svg": (
            "Recolorações na inserção — Rubro-Negra",
            "recolorações",
            [row for row in build_rows(index, "recoloracoes_insercao") if row[1] == "Rubro-Negra"],
        ),
        "media_visitas_busca.svg": ("Média de nós visitados por busca", "nós visitados", build_rows(index, "media_visitas_total")),
        "tempo_insercao_ms.svg": ("Tempo total de inserção", "ms · mediana", build_rows(index, "tempo_insercao_ms")),
        "tempo_busca_total_ms.svg": ("Tempo total das buscas", "ms · mediana de 20.000 buscas", build_rows(index, "tempo_busca_total_ms")),
        "rotacoes_remocao.svg": ("Rotações na remoção de 50%", "rotações", build_rows(index, "rotacoes_remocao", 50)),
        "recoloracoes_remocao.svg": (
            "Recolorações na remoção de 50% — Rubro-Negra",
            "recolorações",
            [row for row in build_rows(index, "recoloracoes_remocao", 50) if row[1] == "Rubro-Negra"],
        ),
        "tempo_remocao_ms.svg": ("Tempo para remover 50% dos alunos", "ms · mediana de 5.000 remoções", build_rows(index, "tempo_remocao_ms", 50)),
    }

    for filename, (title, unit, rows) in charts.items():
        (OUTPUT_DIR / filename).write_text(chart_svg(title, unit, rows), encoding="utf-8")

    print(f"{len(charts)} gráficos atualizados em {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
