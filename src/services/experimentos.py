"""Experimentos reproduzíveis sobre as classes originais da equipe (stdlib).

Execute na raiz do projeto:
    python -m src.services.experimentos --saida resultados
"""
import argparse
import csv
import hashlib
import json
import platform
import random
import shutil
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from src.models.aluno import Aluno
from src.trees.avl import ArvoreAVL
from src.trees.rubro_negra import ArvoreRubroNegra

COMMIT = "2f5e17cabd2398f2347b061d1f33d101665c5c78"
CLASSES = {"AVL": ArvoreAVL, "Rubro-Negra": ArvoreRubroNegra}
def aluno(k):
    return Aluno(k, f"Aluno {k}", "Engenharia de Software", 1)
def validar(t):
    return t.validar_avl() if isinstance(t, ArvoreAVL) else t.validar_rubro_negra()
def conferir(t, esperado):
    exigir(validar(t), "Propriedades da árvore inválidas")
    exigir(
        [a.matricula for a in t.em_ordem()] == sorted(esperado),
        "Conteúdo em ordem divergente do conjunto de referência",
    )
    exigir(
        t.obter_quantidade_nos() == len(esperado),
        "Quantidade de nós divergente do conjunto de referência",
    )
    return True


def exigir(condicao, mensagem):
    """Mantém as verificações ativas mesmo quando Python é executado com -O."""
    if not condicao:
        raise RuntimeError(mensagem)


def validar_parametros(repeticoes, semente, tamanhos):
    if isinstance(repeticoes, bool) or not isinstance(repeticoes, int) or repeticoes < 1:
        raise ValueError("repeticoes deve ser um inteiro maior ou igual a 1")
    if isinstance(semente, bool) or not isinstance(semente, int):
        raise ValueError("semente deve ser um inteiro")
    if not tamanhos:
        raise ValueError("informe ao menos um tamanho de experimento")
    if any(isinstance(n, bool) or not isinstance(n, int) or n < 1 for n in tamanhos):
        raise ValueError("cada tamanho deve ser um inteiro maior ou igual a 1")
    if len(set(tamanhos)) != len(tamanhos):
        raise ValueError("os tamanhos de experimento devem ser distintos")


def buscar_e_contar_visitas(t, chave):
    """Replica as comparações de buscar e conta apenas nós reais visitados.

    A contagem é executada fora do intervalo cronometrado. O resultado é
    comparado ao método buscar da árvore para detectar divergências.
    """
    no, nil, total = t.raiz, getattr(t, "NIL", None), 0
    while no is not nil:
        total += 1
        if chave == no.aluno.matricula:
            encontrado = no.aluno
            break
        if chave < no.aluno.matricula:
            no = no.esquerda
        else:
            no = no.direita
    else:
        encontrado = None

    exigir(
        encontrado is t.buscar(chave),
        f"Busca instrumentada divergiu de buscar({chave})",
    )
    return encontrado, total


def obter_commit_execucao(raiz_projeto):
    """Obtém o HEAD usando Git quando disponível, com leitura direta como fallback."""
    executavel_git = shutil.which("git")
    if executavel_git:
        resultado = subprocess.run(
            [executavel_git, "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=raiz_projeto,
            check=False,
        )
        if resultado.returncode == 0:
            return resultado.stdout.strip()

    caminho_git = raiz_projeto / ".git"
    if caminho_git.is_file():
        conteudo = caminho_git.read_text(encoding="utf-8").strip()
        if conteudo.startswith("gitdir:"):
            caminho_git = (raiz_projeto / conteudo.partition(":")[2].strip()).resolve()
    if not caminho_git.is_dir():
        return None

    head = (caminho_git / "HEAD").read_text(encoding="utf-8").strip()
    if not head.startswith("ref:"):
        return head or None
    referencia = head.partition(":")[2].strip()
    caminho_ref = caminho_git / referencia
    if caminho_ref.is_file():
        return caminho_ref.read_text(encoding="utf-8").strip() or None

    packed_refs = caminho_git / "packed-refs"
    if packed_refs.is_file():
        for linha in packed_refs.read_text(encoding="utf-8").splitlines():
            campos = linha.split()
            if len(campos) == 2 and campos[1] == referencia:
                return campos[0]
    return None
def csv_salvar(path, linhas):
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=list(linhas[0]))
        w.writeheader();w.writerows(linhas)
def teste_regressao():
    checks=0
    for nome, cls in CLASSES.items():
        for seed in range(10):
            rng=random.Random(seed); t=cls(); esperado=set()
            for _ in range(1000):
                k=rng.randint(1,200); op=rng.randrange(3)
                if op==0:
                    exigir(t.inserir(aluno(k)) == (k not in esperado), "Resultado incorreto ao inserir")
                    esperado.add(k)
                elif op==1:
                    exigir(t.remover(k) == (k in esperado), "Resultado incorreto ao remover")
                    esperado.discard(k)
                else:
                    found=t.buscar(k)
                    exigir((found is not None)==(k in esperado), "Resultado incorreto ao buscar")
                    if found:
                        exigir(found.matricula==k, "Busca retornou matrícula incorreta")
                conferir(t,esperado)
                menor=t.obter_menor()
                maior=t.obter_maior()
                exigir((menor.matricula if menor else None)==(min(esperado) if esperado else None), "Mínimo incorreto")
                exigir((maior.matricula if maior else None)==(max(esperado) if esperado else None), "Máximo incorreto")
                exigir(sorted(a.matricula for a in t.pre_ordem()) == sorted(esperado), "Pré-ordem contém chaves incorretas")
                exigir(sorted(a.matricula for a in t.pos_ordem()) == sorted(esperado), "Pós-ordem contém chaves incorretas")
                checks+=1
            for k in sorted(esperado):
                exigir(t.remover(k), "Falha ao esvaziar a árvore de referência")
            conferir(t,set())
        t=cls()
        for k in [40,20,60,10,30,50,70]:t.inserir(aluno(k))
        exigir([a.matricula for a in t.pre_ordem()]==[40,20,10,30,60,50,70], "Pré-ordem de referência incorreta")
        exigir([a.matricula for a in t.pos_ordem()]==[10,30,20,50,70,60,40], "Pós-ordem de referência incorreta")
    for seq in ([30,20,10],[10,20,30],[30,10,20],[10,30,20]):
        t=ArvoreAVL()
        for k in seq:t.inserir(aluno(k))
        exigir(t.raiz.aluno.matricula==20 and validar(t), "Caso de rotação AVL inválido")
        exigir(t.rotacoes==(1 if seq in ([30,20,10],[10,20,30]) else 2), "Contagem de rotações AVL incorreta")
    return {"status":"APROVADO", "operacoes_mistas_verificadas":checks,
            "sementes":list(range(10)), "observacao":"Inclui duplicadas, ausentes, minimo/maximo, caminhamentos, esvaziamento e quatro casos AVL."}
def executar(saida="resultados", repeticoes=5, semente=20261024, tamanhos=(100,1000,10000)):
    tamanhos=tuple(tamanhos)
    validar_parametros(repeticoes, semente, tamanhos)
    out=Path(saida);out.mkdir(parents=True,exist_ok=True)
    testes=teste_regressao()
    (out/"validacao.json").write_text(json.dumps(testes,indent=2),encoding="utf-8")
    print("Regressao aprovada:",testes["operacoes_mistas_verificadas"],flush=True)
    brutos=[];buscas=[];manifest={}
    # Aquecimento fora da medicao.
    for cls in CLASSES.values():
        t=cls()
        for k in range(1,201):t.inserir(aluno(k))
        for k in range(1,201):t.buscar(k)
        for k in range(1,201):t.remover(k)
    for n in tamanhos:
        base=list(range(2,2*n+1,2))  # impares intercalados sao ausentes
        hit=base.copy();random.Random(semente+n+1).shuffle(hit)
        miss=list(range(1,2*n,2));random.Random(semente+n+2).shuffle(miss)
        removal=base.copy();random.Random(semente+n+3).shuffle(removal)
        sementes={
            "insercao_aleatoria":semente+n,
            "busca_existente":semente+n+1,
            "busca_inexistente":semente+n+2,
            "remocao":semente+n+3,
        }
        for ordem in ("crescente","aleatoria"):
            keys=base.copy()
            if ordem=="aleatoria":random.Random(sementes["insercao_aleatoria"]).shuffle(keys)
            manifest[f"{n}_{ordem}"]={"insercao":keys,"buscas_existentes":hit,
                "buscas_inexistentes":miss,"ordem_remocao":removal,
                "sementes":{
                    "insercao":sementes["insercao_aleatoria"] if ordem=="aleatoria" else None,
                    "busca_existente":sementes["busca_existente"],
                    "busca_inexistente":sementes["busca_inexistente"],
                    "remocao":sementes["remocao"],
                }}
            records=[aluno(k) for k in keys]
            for rep in range(1,repeticoes+1):
                nomes=list(CLASSES)
                if rep%2==0:nomes.reverse()
                for nome in nomes:
                    cls=CLASSES[nome];t=cls()
                    start=time.perf_counter_ns()
                    for a in records:t.inserir(a)
                    insert_ms=(time.perf_counter_ns()-start)/1e6
                    conferir(t,set(base))
                    h=t.obter_altura();ri=t.rotacoes;ci=getattr(t,"recoloracoes",0)
                    tempos={};medias={}
                    for tipo,queries in (("existente",hit),("inexistente",miss)):
                        start=time.perf_counter_ns()
                        for k in queries:t.buscar(k)
                        tempos[tipo]=(time.perf_counter_ns()-start)/1e6
                        instrumentadas=[buscar_e_contar_visitas(t,k) for k in queries]
                        counts=[quantidade for _,quantidade in instrumentadas]
                        medias[tipo]=statistics.mean(counts)
                        for k,(encontrado,_) in zip(queries,instrumentadas):
                            exigir(
                                (encontrado is not None)==(tipo=="existente"),
                                f"Consulta classificada incorretamente: {k}",
                            )
                        if rep==1:
                            buscas.extend({"n":n,"ordem":ordem,"arvore":nome,"tipo":tipo,
                                           "matricula":k,"nos_visitados":v} for k,v in zip(queries,counts))
                    # Cada percentual parte de uma arvore nova e completa.
                    for pct in (10,30,50):
                        d=cls()
                        for a in records:d.inserir(a)
                        r0=d.rotacoes;c0=getattr(d,"recoloracoes",0)
                        subset=removal[:n*pct//100]
                        start=time.perf_counter_ns()
                        for k in subset:d.remover(k)
                        remove_ms=(time.perf_counter_ns()-start)/1e6
                        validacao=conferir(d,set(base)-set(subset))
                        brutos.append(dict(n=n,ordem=ordem,repeticao=rep,arvore=nome,
                            percentual_remocao=pct,altura_antes=h,altura_depois=d.obter_altura(),
                            rotacoes_insercao=ri,rotacoes_remocao=d.rotacoes-r0,
                            recoloracoes_insercao=ci,recoloracoes_remocao=getattr(d,"recoloracoes",0)-c0,
                            media_visitas_existentes=medias["existente"],media_visitas_inexistentes=medias["inexistente"],
                            media_visitas_total=(medias["existente"]+medias["inexistente"])/2,
                            tempo_insercao_ms=insert_ms,tempo_busca_existente_ms=tempos["existente"],
                            tempo_busca_inexistente_ms=tempos["inexistente"],
                            tempo_busca_total_ms=sum(tempos.values()),tempo_remocao_ms=remove_ms,
                            quantidade_final=d.obter_quantidade_nos(),validacao=validacao))
            print("Concluido:",n,ordem,flush=True)
    csv_salvar(out/"resultados_brutos.csv",brutos)
    csv_salvar(out/"buscas_detalhadas.csv",buscas)
    (out/"sequencias.json").write_text(json.dumps(manifest,separators=(",",":")),encoding="utf-8")
    resumo=[]
    keys=("n","ordem","arvore","percentual_remocao")
    for group in dict.fromkeys(tuple(r[k] for k in keys) for r in brutos):
        rs=[r for r in brutos if tuple(r[k] for k in keys)==group]
        row=dict(zip(keys,group))
        for k in brutos[0]:
            if k in keys or k in ("repeticao","validacao"):continue
            vals=[r[k] for r in rs]
            row[k]=statistics.median(vals)
            if k.startswith("tempo"):
                row[k.replace("_ms","_min_ms")]=min(vals)
                row[k.replace("_ms","_max_ms")]=max(vals)
            else:
                exigir(
                    len(set(vals))==1,
                    f"Métrica não temporal variou entre repetições: {k}",
                )
        resumo.append(row)
    csv_salvar(out/"resumo.csv",resumo)
    root=Path(__file__).resolve().parents[1]
    hashes={str(p.relative_to(root)).replace("\\","/"):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [root/"trees/avl.py",root/"trees/rubro_negra.py",root/"models/aluno.py"]}
    commit_execucao=obter_commit_execucao(Path(__file__).resolve().parents[2])
    meta={"data_utc":datetime.now(timezone.utc).isoformat(),"python":sys.version,
        "sistema":platform.platform(),"processador":platform.processor(),"commit_base":COMMIT,
        "commit_execucao":commit_execucao,
        "arquivo_experimento_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "comando_argv":[sys.executable,"-m","src.services.experimentos",*sys.argv[1:]],
        "parametros_efetivos":{"saida":str(out.resolve()),"repeticoes":repeticoes,
            "semente_base":semente,"tamanhos":list(tamanhos),"percentuais_remocao":[10,30,50]},
        "semente_base":semente,"sementes_por_n":{"insercao":"base+n","busca_existente":"base+n+1",
        "busca_inexistente":"base+n+2","remocao":"base+n+3"},"repeticoes":repeticoes,
        "tamanhos":tamanhos,"hashes_sha256":hashes,"cronometro":"perf_counter_ns",
        "nota":"As colunas de insercao/busca repetem-se nas tres linhas de percentuais; nao somar essas copias.",
        "contagem_visitas":"percurso instrumentado fora do cronometro; resultado conferido com buscar; conta nos reais e exclui NIL/None",
        "remocao":"somente chaves existentes; cada percentual usa uma arvore reconstruida antes da medicao",
        "altura":"numero de nos no maior caminho: vazia=0, raiz=1",
        "recoloracao":"mudanca efetiva de cor de no real; inclui tornar a raiz preta e transferencia de cor na remocao",
        "rotacao":"cada rotacao simples conta 1; dupla conta 2"}
    (out/"metadados.json").write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding="utf-8")
    return resumo
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--saida",default="resultados");p.add_argument("--repeticoes",type=int,default=5)
    p.add_argument("--semente",type=int,default=20261024)
    args=p.parse_args()
    try:
        validar_parametros(args.repeticoes,args.semente,(100,1000,10000))
    except ValueError as erro:
        p.error(str(erro))
    executar(args.saida,args.repeticoes,args.semente)
if __name__=="__main__":main()
