"""Gera o relatório HTML a partir dos resultados experimentais.

O PDF formatado de entrega é mantido como artefato final e não é sobrescrito
por este gerador.
"""
import csv
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TESTS = ROOT / "testes"
RESULTS = TESTS / "resultados"
HTML_PATH = TESTS / "Relatorio_Experimentos.html"
TREES = ("AVL", "Rubro-Negra")
ORDERS = ("crescente", "aleatoria")
SIZES = (100, 1000, 10000)
PCTS = (10, 30, 50)


def read_csv(name):
    with (RESULTS / name).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def pt_number(value, decimals=3):
    number = float(value)
    if number.is_integer():
        return f"{int(number):,}".replace(",", ".")
    return f"{number:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def row_index(rows, keys):
    return {tuple(row[key] for key in keys): row for row in rows}


def get_row(index, n, order, tree, pct):
    return index[(str(n), order, tree, str(pct))]


def build_html(meta, valid, summary):
    index = row_index(summary, ("n", "ordem", "arvore", "percentual_remocao"))

    def table(headers, rows, compact=False):
        cls = ' class="compact"' if compact else ""
        th = "".join(f"<th>{html.escape(str(value))}</th>" for value in headers)
        body = "".join(
            "<tr>" + "".join(f"<td>{html.escape(str(value))}</td>" for value in row) + "</tr>"
            for row in rows
        )
        return f"<table{cls}><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>"

    insert_rows = []
    search_rows = []
    remove_rows = []
    for n in SIZES:
        for order in ORDERS:
            for tree in TREES:
                insertion = get_row(index, n, order, tree, 10)
                insert_rows.append((
                    order, pt_number(n), tree, pt_number(insertion["altura_antes"], 0),
                    pt_number(insertion["rotacoes_insercao"], 0),
                    "—" if tree == "AVL" else pt_number(insertion["recoloracoes_insercao"], 0),
                    pt_number(insertion["tempo_insercao_ms"]),
                ))
                search_rows.append((
                    order, pt_number(n), tree, pt_number(insertion["media_visitas_existentes"]),
                    pt_number(insertion["media_visitas_inexistentes"]),
                    pt_number(insertion["media_visitas_total"]),
                    pt_number(insertion["tempo_busca_total_ms"]),
                ))
                for pct in PCTS:
                    removal = get_row(index, n, order, tree, pct)
                    remove_rows.append((
                        order, pt_number(n), f"{pct}%", tree,
                        pt_number(removal["altura_antes"], 0),
                        pt_number(removal["altura_depois"], 0),
                        pt_number(removal["rotacoes_remocao"], 0),
                        "—" if tree == "AVL" else pt_number(removal["recoloracoes_remocao"], 0),
                        pt_number(removal["tempo_remocao_ms"]),
                    ))

    random_avl = get_row(index, 10000, "aleatoria", "AVL", 10)
    random_rb = get_row(index, 10000, "aleatoria", "Rubro-Negra", 10)
    random_avl50 = get_row(index, 10000, "aleatoria", "AVL", 50)
    random_rb50 = get_row(index, 10000, "aleatoria", "Rubro-Negra", 50)
    increasing_rb = get_row(index, 10000, "crescente", "Rubro-Negra", 10)

    synthesis = [
        ("Altura final após inserção", pt_number(random_avl["altura_antes"], 0), pt_number(random_rb["altura_antes"], 0)),
        ("Altura após remover 50%", pt_number(random_avl50["altura_depois"], 0), pt_number(random_rb50["altura_depois"], 0)),
        ("Rotações na inserção", pt_number(random_avl["rotacoes_insercao"], 0), pt_number(random_rb["rotacoes_insercao"], 0)),
        ("Rotações na remoção de 50%", pt_number(random_avl50["rotacoes_remocao"], 0), pt_number(random_rb50["rotacoes_remocao"], 0)),
        ("Recolorações na inserção", "—", pt_number(random_rb["recoloracoes_insercao"], 0)),
        ("Recolorações na remoção de 50%", "—", pt_number(random_rb50["recoloracoes_remocao"], 0)),
        ("Média de nós visitados", pt_number(random_avl["media_visitas_total"]), pt_number(random_rb["media_visitas_total"])),
        ("Tempo de inserção (ms)", pt_number(random_avl["tempo_insercao_ms"]), pt_number(random_rb["tempo_insercao_ms"])),
        ("Tempo de 20.000 buscas (ms)", pt_number(random_avl["tempo_busca_total_ms"]), pt_number(random_rb["tempo_busca_total_ms"])),
        ("Tempo de remoção de 5.000 (ms)", pt_number(random_avl50["tempo_remocao_ms"]), pt_number(random_rb50["tempo_remocao_ms"])),
    ]

    py_version = html.escape(meta["python"].split()[0])
    system = html.escape(meta["sistema"])
    processor = html.escape(meta["processador"] or "não identificado")
    commit = html.escape(meta.get("commit_execucao") or "não identificado")
    validation_status = html.escape(valid["status"])
    validation_count = pt_number(valid["operacoes_mistas_verificadas"], 0)
    css = """
    @page{size:A4;margin:15mm 16mm}*{box-sizing:border-box}body{margin:0;color:#203045;font:10px/1.42 Arial,sans-serif}
    .page{position:relative;min-height:267mm;page-break-after:always;padding-bottom:13mm}.page:last-child{page-break-after:auto}
    h1{font-size:28px;line-height:1.12;margin:16px 0 12px;color:#153c59}h2{font-size:19px;margin:8px 0 9px;color:#153c59}
    h3{font-size:12px;margin:11px 0 4px;color:#24628a}p{margin:5px 0}table{width:100%;border-collapse:collapse;margin:8px 0;font-size:9px}
    th{background:#183c56;color:white;text-align:left;padding:5px 4px}td{padding:3px 4px;border-bottom:1px solid #d9e1e9}
    tr:nth-child(even){background:#f1f5f8}.compact{font-size:8px}.compact td{padding:2px 3px}.compact th{padding:4px 3px}
    .eyebrow{font-size:9px;letter-spacing:1px;color:#52728c;text-transform:uppercase}.callout{border-left:4px solid #2b759e;background:#eff5f9;padding:9px 12px;margin:11px 0}
    .small{font-size:8px;color:#536779}.footer{position:absolute;bottom:0;width:100%;border-top:1px solid #d9e1e9;padding-top:4px;font-size:8px;color:#607589;display:flex;justify-content:space-between}
    li{margin:4px 0}code{font:9px Consolas,monospace;background:#eef2f6;padding:2px 4px}.badge{font-size:12px;font-weight:bold;color:#24628a}
    """
    sections = []
    def begin(title, page):
        sections.append(f'<section class="page"><div class="eyebrow">UFAM · Algoritmos e Estruturas de Dados II · Trabalho Prático I</div><h2>{title}</h2>')
    def end(page):
        sections.append(f'<div class="footer"><span>Sistema acadêmico | AVL × Rubro-Negra | 24/10/2026</span><span>{page} / 6</span></div></section>')

    sections.append('<section class="page"><div class="eyebrow">UFAM · Algoritmos e Estruturas de Dados II · Trabalho Prático I</div><h1>Árvores balanceadas<br>em um sistema acadêmico</h1><p class="badge">Relatório atualizado de experimentos e análise comparativa</p><p>Professor: Alternei Brito<br>Integrantes: Davi Vitor Santos Mota, Isabely Cristina Barbosa Beça, Thiago Silva dos Santos e Vicktor Eduardo Almeida Pinheiro</p><div class="callout"><strong>Objetivo.</strong> Comparar AVL e Rubro-Negra usando as mesmas chaves e sequências de operações, nos cenários de inserção crescente, inserção aleatória, busca e remoção.</div><h3>Protocolo experimental</h3><ul><li><strong>Tamanhos:</strong> 100, 1.000 e 10.000 matrículas distintas.</li><li><strong>Inserção:</strong> sequência crescente ou permutação aleatória; as duas árvores recebem a mesma ordem em cada cenário.</li><li><strong>Busca:</strong> n chaves existentes e n inexistentes, com consultas embaralhadas.</li><li><strong>Remoção:</strong> 10%, 30% e 50% de chaves existentes; cada percentual reconstrói a árvore completa.</li><li><strong>Repetições:</strong> cinco por cenário, alternando qual árvore executa primeiro; tabelas exibem medianas.</li><li><strong>Semente-base:</strong> 20261024; sementes concretas por operação e tamanho estão em <code>sequencias.json</code>.</li></ul><h3>Ambiente e definições</h3><p>CPython ' + py_version + ', ' + system + '. Processador: ' + processor + '. Medição por <code>perf_counter_ns</code>, em milissegundos.</p><p>Altura em número de nós: árvore vazia = 0; raiz isolada = 1. Cada rotação simples conta uma; rotação dupla conta duas. Recolorações contam mudanças efetivas em nós reais. Visitas contam nós reais e excluem NIL/None.</p><p>Commit HEAD registrado: <code>' + commit + '</code>. Hashes dos arquivos medidos e do módulo de execução estão nos metadados.</p><div class="footer"><span>Sistema acadêmico | AVL × Rubro-Negra | 24/10/2026</span><span>1 / 6</span></div></section>')

    begin("2. Inserção: experimentos A e B", 2)
    sections.append("<p>Altura, rotações, recolorações e mediana do tempo após inserir as n chaves.</p>")
    sections.append(table(("Ordem", "n", "Árvore", "Altura", "Rotações", "Recolorações", "Tempo (ms)"), insert_rows))
    sections.append(f'<h3>Interpretação</h3><p>Na ordem crescente, a AVL teve alturas 7, 10 e 14, contra 11, 17 e 24 na Rubro-Negra. Na ordem aleatória, as alturas empataram em 8, 12 e 16. A AVL realizou mais rotações de inserção em todos os seis cenários; a Rubro-Negra teve menor mediana de tempo de inserção nos seis.</p><p>Para 10.000 chaves, a Rubro-Negra registrou {pt_number(increasing_rb["recoloracoes_insercao"], 0)} recolorações na ordem crescente e {pt_number(random_rb["recoloracoes_insercao"], 0)} na aleatória. A quantidade alta de recolorações mostra que o rebalanceamento rubro-negro usa mudanças de cor junto às rotações.</p>')
    end(2)

    begin("3. Busca: experimento C", 3)
    sections.append("<p>Cada linha reúne n consultas existentes e n inexistentes. A média geral atribui peso igual aos dois grupos; o tempo é o total das 2n buscas.</p>")
    sections.append(table(("Ordem", "n", "Árvore", "Visitas exist.", "Visitas ausent.", "Média", "Tempo total (ms)"), search_rows))
    sections.append("<h3>Interpretação</h3><p>A AVL teve menor média de visitas e menor mediana de tempo de busca em todos os cenários. Com 10.000 chaves em ordem aleatória, as médias foram 13,078 visitas na AVL e 13,111 na Rubro-Negra. A diferença de visitas é pequena nesse caso, mas os tempos refletem também os custos específicos de cada implementação.</p><p>A contagem de visitas foi feita por um percurso instrumentado fora do cronômetro e conferida contra o resultado de <code>buscar</code>. O CSV detalhado contém cada consulta da primeira repetição.</p>")
    end(3)

    begin("4. Remoção: experimento D", 4)
    sections.append("<p>Cada percentual parte de uma árvore completa reconstruída. As remoções são chaves existentes; os subconjuntos de 10%, 30% e 50% são prefixos da mesma permutação.</p>")
    sections.append(table(("Ordem", "n", "Rem.", "Árvore", "Alt. antes", "Alt. depois", "Rot.", "Recol.", "Tempo (ms)"), remove_rows, True))
    sections.append("<p class=\"small\">Rot. = rotações durante a remoção; Recol. = recolorações durante a remoção. Tempos são medianas de cinco repetições. Recolorações AVL não se aplicam.</p>")
    sections.append(f'<h3>Interpretação</h3><p>Em 10.000 chaves aleatórias com remoção de 50%, a AVL fez {pt_number(random_avl50["rotacoes_remocao"], 0)} rotações e levou {pt_number(random_avl50["tempo_remocao_ms"])} ms; a Rubro-Negra fez {pt_number(random_rb50["rotacoes_remocao"], 0)} rotações, {pt_number(random_rb50["recoloracoes_remocao"], 0)} recolorações e levou {pt_number(random_rb50["tempo_remocao_ms"])} ms. A Rubro-Negra foi mais rápida em todos os cenários de remoção medidos, mesmo quando fez mais rotações.</p>')
    end(4)

    begin("5. Síntese das métricas obrigatórias", 5)
    sections.append("<p>Recorte representativo: 10.000 chaves, inserção aleatória, 20.000 buscas e remoção independente de 5.000 chaves.</p>")
    sections.append(table(("Métrica", "AVL", "Rubro-Negra"), synthesis))
    sections.append("<h3>Conclusões comparativas</h3><ul><li>A AVL foi mais baixa na inserção crescente e empatou em altura com a Rubro-Negra na aleatória.</li><li>A AVL fez mais rotações em todas as inserções; na remoção de 50%, a Rubro-Negra fez mais rotações nos seis cenários comparáveis.</li><li>A ordem crescente elevou a altura final da Rubro-Negra, enquanto a AVL manteve alturas menores. A ordem aleatória reduziu rotações de inserção e recolorações da Rubro-Negra.</li><li>Menor altura não garantiu menor tempo: a Rubro-Negra foi mais rápida em inserções e remoções; a AVL foi mais rápida nas buscas.</li><li>As diferenças mais nítidas apareceram na altura após inserção crescente e no tempo das operações de atualização para n = 10.000.</li></ul>")
    end(5)

    begin("6. Validade, limitações e reprodução", 6)
    sections.append(f'<p>Validação de regressão: <strong>{validation_status}</strong>, com {validation_count} operações mistas verificadas em dez sementes por árvore. As árvores também foram conferidas após cada construção e lote de remoção dos experimentos.</p>')
    sections.append(
        '''<h3>Limitações metodológicas</h3>
        <p>As cinco repetições medem variação temporal, não diversidade de sequências. Foi utilizado um computador, uma versão de Python e uma permutação aleatória por tamanho. Processos em segundo plano, cache e coleta de lixo podem afetar os tempos; não houve controle de afinidade ou frequência da CPU. Os resultados valem para estas implementações e cargas sintéticas, não para todas as cargas reais.</p>
        <p>Os tempos excluem criação dos alunos, geração de sequências, interface, validação, exportação e cálculo da altura. Para inserção e busca, os números se repetem nas três linhas de percentual de remoção no CSV; não são amostras independentes.</p>
        <h3>Arquivos e reprodução</h3>
        <p>Resultados brutos, resumo, buscas detalhadas, sequências, metadados e validação estão em <code>testes/resultados</code>. Execute os experimentos na raiz com <code>python -m src.services.experimentos --saida testes/resultados</code>. Para regenerar este relatório HTML, execute <code>python -m src.services.gerar_relatorio</code>. O PDF formatado de entrega não é sobrescrito por esse comando.</p>
        <p class="small">Enunciado: Trabalho Prático I — Árvores Balanceadas, UFAM. Código-base: TPI_Arvores_Balanceadas. O arquivo metadados.json registra commit, parâmetros, ambiente e hashes usados.</p>'''
    )
    end(6)
    document = '<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Experimentos AVL e Rubro-Negra</title><style>' + css + '</style><body>' + "".join(sections) + "</body></html>"
    HTML_PATH.write_text(document, encoding="utf-8")
    return document


def main():
    with (RESULTS / "metadados.json").open(encoding="utf-8") as stream:
        meta = json.load(stream)
    with (RESULTS / "validacao.json").open(encoding="utf-8") as stream:
        valid = json.load(stream)
    summary = read_csv("resumo.csv")
    build_html(meta, valid, summary)
    print(f"Relatório HTML atualizado: {HTML_PATH}")


if __name__ == "__main__":
    main()
