"""
=========================================================
BANCO.PY
Monitor Inteligente de Investimentos — Contagem MG
=========================================================
"""

import json
from pathlib import Path
from datetime import datetime
from modelos import Noticia

PASTA_DADOS    = Path("dados")
PASTA_DADOS.mkdir(exist_ok=True)

ARQ_NOTICIAS     = PASTA_DADOS / "noticias.json"
ARQ_EMPRESAS     = PASTA_DADOS / "empresas.json"
ARQ_INVESTIMENTOS= PASTA_DADOS / "investimentos.json"
ARQ_EVENTOS      = PASTA_DADOS / "eventos.json"


class Banco:

    def __init__(self):
        self.noticias      = self.carregar(ARQ_NOTICIAS)
        self.empresas      = self.carregar(ARQ_EMPRESAS)
        self.investimentos = self.carregar(ARQ_INVESTIMENTOS)
        self.eventos       = self.carregar(ARQ_EVENTOS)

    # ── carregar ─────────────────────────────────────

    def carregar(self, arquivo):
        if arquivo.exists():
            with open(arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    # ── salvar ───────────────────────────────────────

    def salvar(self):
        self._salvar(ARQ_NOTICIAS,      self.noticias)
        self._salvar(ARQ_EMPRESAS,      self.empresas)
        self._salvar(ARQ_INVESTIMENTOS, self.investimentos)
        self._salvar(ARQ_EVENTOS,       self.eventos)

    def _salvar(self, arquivo, dados):
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

    # ── empresa ──────────────────────────────────────

    def obter_empresa(self, nome):
        for e in self.empresas:
            if e["nome"].lower() == nome.lower():
                return e
        return None

    def adicionar_empresa(self, nome):
        empresa = self.obter_empresa(nome)
        if empresa:
            empresa["ultima_atualizacao"] = datetime.now().strftime("%Y-%m-%d")
            return empresa
        nova = {
            "id": len(self.empresas) + 1,
            "nome": nome,
            "primeira_aparicao":  datetime.now().strftime("%Y-%m-%d"),
            "ultima_atualizacao": datetime.now().strftime("%Y-%m-%d"),
            "investimentos": []
        }
        self.empresas.append(nova)
        return nova

    # ── investimento ─────────────────────────────────

    def procurar_investimento(self, empresa, ano):
        for inv in self.investimentos:
            if inv["empresa"].lower() == empresa.lower() and inv["ano"] == ano:
                return inv
        return None

    def adicionar_investimento(self, empresa, ano, valor="",
                               empregos="", bairro="", fase="",
                               fonte="", url=""):
        existente = self.procurar_investimento(empresa, ano)
        if existente:
            return existente
        novo = {
            "id":               len(self.investimentos) + 1,
            "empresa":          empresa,
            "ano":              ano,
            "valor":            valor,
            "empregos":         empregos,
            "bairro":           bairro,
            "status":           "Anunciado",
            "ultima_atualizacao": datetime.now().strftime("%Y-%m-%d"),
            "eventos":          [],
            "fase":             fase or "Anunciado",
            "fonte":            fonte,
            "url":              url,
        }
        self.investimentos.append(novo)
        return novo

    # ── evento ───────────────────────────────────────

    def adicionar_evento(self, investimento_id, fase, noticia):
        evento = {
            "id":          len(self.eventos) + 1,
            "investimento": investimento_id,
            "fase":        fase,
            "titulo":      noticia.titulo,
            "fonte":       noticia.fonte,
            "url":         noticia.url,
            "data":        noticia.data,
            "pontuacao":   noticia.pontuacao,
        }
        self.eventos.append(evento)

    # ── notícia ──────────────────────────────────────

    def noticia_existe(self, url):
        return any(n["url"] == url for n in self.noticias)

    def adicionar_noticia(self, noticia: Noticia):
        if self.noticia_existe(noticia.url):
            return
        self.noticias.append({
            "titulo":             noticia.titulo,
            "texto":              noticia.texto,
            "url":                noticia.url,
            "fonte":              noticia.fonte,
            "data":               noticia.data,
            "empresas":           noticia.empresas,
            "valores":            noticia.valores,
            "empregos":           noticia.empregos,
            "pontuacao":          noticia.pontuacao,
            "relevante":          noticia.relevante,
            # ← campo que faltava: necessário para
            #   o relatório filtrar "quase relevantes"
            "mencionou_contagem": getattr(noticia, "mencionou_contagem", False),
            "fase":               noticia.fase,
            "status":             noticia.status,
            "confianca":          noticia.confianca,
        })

    # ── resumo ───────────────────────────────────────

    def resumo(self):
        print()
        print("=" * 50)
        print("BANCO DE DADOS")
        print("=" * 50)
        print("Empresas.....:", len(self.empresas))
        print("Investimentos:", len(self.investimentos))
        print("Eventos......:", len(self.eventos))
        print("Notícias.....:", len(self.noticias))
        print("=" * 50)


if __name__ == "__main__":
    Banco().resumo()
