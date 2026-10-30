#!/usr/bin/env python3
"""Validador editorial do livro PDF O Japonês por Trás das Palavras.

Somente conteúdo estático destinado à publicação em PDF. Não produz nem gerencia
áudio, interfaces, plataformas ou atividades interativas.
Requer Python 3.9+ e usa apenas a biblioteca padrão.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, re, sys, unicodedata
from pathlib import Path

SCHEMA = {
 "frases.csv": ["id_frase","capitulo","licao","forma_completa","forma_reduzida","reducao","registro","traducao_ptbr","explicacao_curta","versao_japones","versao_traducao","versao_explicacao","imp_japones","imp_traducao","imp_explicacao","situacao","observacoes"],
 "exercicios.csv": ["id_exercicio","capitulo","licao","degrau","tipo","enunciado","frases_usadas","secao_que_ensina","regra_comparacao","versao","imp_exercicio","situacao","observacoes"],
 "respostas.csv": ["id_resposta","id_exercicio","rotulo","texto","tipo","explicacao","versao","imp_resposta","situacao","observacoes"],
 "validacoes.csv": ["id_validacao","data","id_item","dimensao","imp_validada","status","revisor","revisor_identificacao","commit_revisado","apontamento","observacoes"],
}
PATTERNS = {
 "frase": re.compile(r"^J(\d{2})-\d{2,3}$"),
 "exercicio": re.compile(r"^X(\d{2})-[A-Za-z0-9]+$"),
 "resposta": re.compile(r"^(X\d{2}-[A-Za-z0-9]+)-[a-z0-9]+$"),
 "sha": re.compile(r"^[0-9a-f]{64}$"),
 "commit": re.compile(r"^[0-9a-f]{40}$"),
 "data": re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?(Z|[+-]\d{2}:\d{2})$"),
}
ENUMS = {
 "registro":{"FORMAL","NEUTRO_POLIDO","CASUAL","RUDE","REGIONAL"},
 "situacao":{"ATIVA","RETIRADA"},
 "degrau":{"RECONHECER","ESCREVER","ESCOLHER_TOM"},
 "tipo_exercicio":{"MULTIPLA_ESCOLHA","ESCRITA"},
 "comparacao":{"EXATA","IGNORA_PONTUACAO_FINAL","MANUAL"},
 "tipo_resposta":{"CORRETA","ACEITA","ERRADA"},
 "dimensao":{"LINGUISTICA","TRADUCAO","PEDAGOGICA","EDITORIAL"},
 "status":{"APROVADO","AJUSTAR","NAO_USAR","PENDENTE_DE_VALIDACAO"},
 "revisor":{"HUMANO_JAPONES","HUMANO_RESPONSAVEL","HUMANO_OUTRO","IA_CHATGPT","IA_CLAUDE"},
}
FINAL = {"LINGUISTICA":{"HUMANO_JAPONES"},"TRADUCAO":{"HUMANO_JAPONES"},
         "PEDAGOGICA":{"HUMANO_JAPONES","HUMANO_RESPONSAVEL"},
         "EDITORIAL":{"HUMANO_RESPONSAVEL"}}
FURIGANA = re.compile(r"\{([^{}|]+)\|([^{}|]+)\}")

def digest(name, *values):
    normalized = [unicodedata.normalize("NFC", str(v).replace("\r\n","\n").replace("\r","\n")).strip() for v in values]
    return hashlib.sha256("\x1f".join(["book-pdf-v1",name,*normalized]).encode("utf-8")).hexdigest()

def furigana_ok(value):
    return not any(c in FURIGANA.sub("", value) for c in "{}|")

def load(path, header, errors):
    if not path.exists():
        errors.append(f"ERRO ARQUIVO_AUSENTE: {path.name}"); return []
    raw=path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf") or b"\r" in raw:
        errors.append(f"ERRO CODIFICACAO_LINHA: {path.name} deve ser UTF-8 sem BOM e LF")
    try: text=raw.decode("utf-8")
    except UnicodeDecodeError:
        errors.append(f"ERRO UTF8: {path.name}"); return []
    rows=list(csv.reader(io.StringIO(text, newline="")))
    if not rows or rows[0] != header:
        errors.append(f"ERRO CABECALHO: {path.name}"); return []
    out=[]
    for n,row in enumerate(rows[1:],2):
        if not row or row==[""]: continue
        if len(row)!=len(header):
            errors.append(f"ERRO COLUNAS: {path.name}:{n}"); continue
        d=dict(zip(header,row)); d["_linha"]=n; out.append(d)
    return out

def run(data_dir):
    errors=[]; warnings=[]
    tables={name:load(data_dir/name,head,errors) for name,head in SCHEMA.items()}
    if errors: return errors,warnings
    phrases={}; exercises={}; answers={}
    def unique(rows,key,label):
        found={}
        for r in rows:
            v=r[key]
            if not v: errors.append(f"ERRO CAMPO_VAZIO: {label}:{r['_linha']} {key}")
            elif v in found: errors.append(f"ERRO ID_DUPLICADO: {label} {v}")
            found[v]=r
        return found
    phrases=unique(tables["frases.csv"],"id_frase","frases")
    exercises=unique(tables["exercicios.csv"],"id_exercicio","exercicios")
    answers=unique(tables["respostas.csv"],"id_resposta","respostas")
    for id_,r in phrases.items():
        m=PATTERNS["frase"].fullmatch(id_)
        if not m or int(m.group(1))!=int(r["capitulo"]): errors.append(f"ERRO ID_CAPITULO: {id_}")
        for field in ("forma_completa","traducao_ptbr","registro","situacao"):
            if not r[field]: errors.append(f"ERRO CAMPO_VAZIO: {id_}.{field}")
        if r["registro"] not in ENUMS["registro"]: errors.append(f"ERRO REGISTRO: {id_}")
        if r["situacao"] not in ENUMS["situacao"]: errors.append(f"ERRO SITUACAO: {id_}")
        for f in ("forma_completa","forma_reduzida"):
            if not furigana_ok(r[f]): errors.append(f"ERRO FURIGANA: {id_}.{f}")
        for f in ("imp_japones","imp_traducao","imp_explicacao"):
            if r[f] and not PATTERNS["sha"].fullmatch(r[f]): errors.append(f"ERRO IMPRESSAO: {id_}.{f}")
    by_ex={}
    for id_,r in exercises.items():
        m=PATTERNS["exercicio"].fullmatch(id_)
        if not m or int(m.group(1))!=int(r["capitulo"]): errors.append(f"ERRO ID_CAPITULO: {id_}")
        if r["degrau"] not in ENUMS["degrau"]: errors.append(f"ERRO DEGRAU: {id_}")
        if r["tipo"] not in ENUMS["tipo_exercicio"]: errors.append(f"ERRO TIPO_EXERCICIO: {id_}")
        if r["regra_comparacao"] not in ENUMS["comparacao"]: errors.append(f"ERRO COMPARACAO: {id_}")
        refs=[x for x in r["frases_usadas"].split("|") if x]
        if not refs: errors.append(f"ERRO SEM_FRASES: {id_}")
        for ref in refs:
            if ref not in phrases: errors.append(f"ERRO REFERENCIA_INEXISTENTE: {id_} -> {ref}")
            elif int(phrases[ref]["capitulo"])>int(r["capitulo"]): errors.append(f"ERRO CAPITULO_POSTERIOR: {id_} -> {ref}")
        by_ex[id_]=[]
    for id_,r in answers.items():
        m=PATTERNS["resposta"].fullmatch(id_)
        if not m or m.group(1)!=r["id_exercicio"]: errors.append(f"ERRO ID_RESPOSTA: {id_}")
        if r["id_exercicio"] not in exercises: errors.append(f"ERRO REFERENCIA_INEXISTENTE: {id_}")
        if r["tipo"] not in ENUMS["tipo_resposta"]: errors.append(f"ERRO TIPO_RESPOSTA: {id_}")
        if r["id_exercicio"] in by_ex and r["situacao"]=="ATIVA": by_ex[r["id_exercicio"]].append(r)
    for id_,r in exercises.items():
        if r["situacao"]=="ATIVA" and not any(a["tipo"]=="CORRETA" for a in by_ex[id_]):
            errors.append(f"ERRO SEM_RESPOSTA_CORRETA: {id_}")
    seen=set()
    for r in tables["validacoes.csv"]:
        if r["id_validacao"] in seen: errors.append(f"ERRO ID_VALIDACAO_DUPLICADO: {r['id_validacao']}")
        seen.add(r["id_validacao"])
        if r["dimensao"] not in ENUMS["dimensao"]: errors.append(f"ERRO DIMENSAO: {r['id_validacao']}")
        if r["status"] not in ENUMS["status"]: errors.append(f"ERRO STATUS: {r['id_validacao']}")
        if r["revisor"] not in ENUMS["revisor"]: errors.append(f"ERRO REVISOR: {r['id_validacao']}")
        if r["id_item"] not in phrases and r["id_item"] not in exercises and r["id_item"] not in answers:
            errors.append(f"ERRO ITEM_VALIDACAO_INEXISTENTE: {r['id_validacao']}")
        if r["revisor"].startswith("HUMANO_") and not r["revisor_identificacao"]:
            errors.append(f"ERRO REVISOR_SEM_IDENTIFICACAO: {r['id_validacao']}")
        if r["status"]=="APROVADO" and r["revisor"] not in FINAL.get(r["dimensao"],set()):
            warnings.append(f"AVISO APROVACAO_AUXILIAR: {r['id_validacao']}")
    return errors,warnings

def main():
    ap=argparse.ArgumentParser(description="Valida os dados editoriais do livro PDF.")
    ap.add_argument("--dados",default=str(Path(__file__).resolve().parents[1]/"01_dados"))
    args=ap.parse_args()
    try: errors,warnings=run(Path(args.dados))
    except OSError as e: print(f"ERRO: {e}"); return 3
    for x in errors+warnings: print(x)
    if not errors and not warnings: print("OK: estrutura editorial válida.")
    print(f"Resultado: {len(errors)} erro(s), {len(warnings)} aviso(s).")
    return 1 if errors else 0
if __name__=="__main__": sys.exit(main())
