"""
=========================================================

BANCO.PY

Banco de dados em memória do
Monitor Inteligente de Investimentos

=========================================================
"""

import json
from pathlib import Path
from datetime import datetime

from modelos import Noticia


PASTA_DADOS = Path("dados")

PASTA_DADOS.mkdir(exist_ok=True)


ARQ_NOTICIAS = PASTA_DADOS / "noticias.json"

ARQ_EMPRESAS = PASTA_DADOS / "empresas.json"

ARQ_INVESTIMENTOS = PASTA_DADOS / "investimentos.json"

ARQ_EVENTOS = PASTA_DADOS / "eventos.json"


class Banco:


    def __init__(self):

        self.noticias = self.carregar(ARQ_NOTICIAS)

        self.empresas = self.carregar(ARQ_EMPRESAS)

        self.investimentos = self.carregar(ARQ_INVESTIMENTOS)

        self.eventos = self.carregar(ARQ_EVENTOS)



    # ====================================================

    # CARREGAR JSON

    # ====================================================

    def carregar(self, arquivo):

        if arquivo.exists():

            with open(

                arquivo,

                "r",

                encoding="utf-8"

            ) as f:

                return json.load(f)

        return []



    # ====================================================

    # SALVAR JSON

    # ====================================================

    def salvar(self):

        self._salvar(ARQ_NOTICIAS, self.noticias)

        self._salvar(ARQ_EMPRESAS, self.empresas)

        self._salvar(ARQ_INVESTIMENTOS, self.investimentos)

        self._salvar(ARQ_EVENTOS, self.eventos)



    def _salvar(self, arquivo, dados):

        with open(

            arquivo,

            "w",

            encoding="utf-8"

        ) as f:

            json.dump(

                dados,

                f,

                indent=4,

                ensure_ascii=False

            )



    # ====================================================

    # EMPRESA

    # ====================================================

    def obter_empresa(self, nome):

        for empresa in self.empresas:

            if empresa["nome"].lower() == nome.lower():

                return empresa

        return None



    def adicionar_empresa(self, nome):

        empresa = self.obter_empresa(nome)

        if empresa:

            empresa["ultima_atualizacao"] = datetime.now().strftime("%Y-%m-%d")

            return empresa

        nova = {

            "id": len(self.empresas)+1,

            "nome": nome,

            "primeira_aparicao": datetime.now().strftime("%Y-%m-%d"),

            "ultima_atualizacao": datetime.now().strftime("%Y-%m-%d"),

            "investimentos": []

        }

        self.empresas.append(nova)

        return nova



    # ====================================================

    # INVESTIMENTO

    # ====================================================

    def procurar_investimento(

        self,

        empresa,

        ano

    ):

        for inv in self.investimentos:

            if (

                inv["empresa"].lower()==empresa.lower()

                and

                inv["ano"]==ano

            ):

                return inv

        return None



    def adicionar_investimento(

    self,

    empresa,

    ano,

    valor="",

    empregos="",

    bairro="",

    fase="",

    fonte="",

    url=""

    ):

        existente=self.procurar_investimento(

            empresa,

            ano

        )

        if existente:

            return existente

        novo={

            "id":len(self.investimentos)+1,

            "empresa":empresa,

            "ano":ano,

            "valor":valor,

            "empregos":empregos,

            "bairro":bairro,

            "status":"Anunciado",

            "ultima_atualizacao":datetime.now().strftime("%Y-%m-%d"),

            "eventos":[],

            "fase": "Anunciado",

            "fonte": "",

            "url": ""

        }

        self.investimentos.append(novo)

        return novo



    # ====================================================

    # EVENTO

    # ====================================================

    def adicionar_evento(

        self,

        investimento_id,

        fase,

        noticia

    ):

        evento={

            "id":len(self.eventos)+1,

            "investimento":investimento_id,

            "fase":fase,

            "titulo":noticia.titulo,

            "fonte":noticia.fonte,

            "url":noticia.url,

            "data":noticia.data,

            "pontuacao":noticia.pontuacao

        }

        self.eventos.append(evento)



    # ====================================================

    # NOTICIA

    # ====================================================

    def noticia_existe(

        self,

        url

    ):

        for noticia in self.noticias:

            if noticia["url"]==url:

                return True

        return False



    def adicionar_noticia(

        self,

        noticia:Noticia

    ):

        if self.noticia_existe(noticia.url):

            return

        self.noticias.append(

            {

                "titulo":noticia.titulo,

                "texto":noticia.texto,

                "url":noticia.url,

                "fonte":noticia.fonte,

                "data":noticia.data,

                "empresas":noticia.empresas,

                "valores":noticia.valores,

                "empregos":noticia.empregos,

                "pontuacao":noticia.pontuacao,

                "relevante":noticia.relevante,

                "fase": noticia.fase,

                "status": noticia.status,

                "confianca": noticia.confianca

            }

        )



    # ====================================================

    # DASHBOARD

    # ====================================================

    def resumo(self):

        print()

        print("="*50)

        print("BANCO")

        print("="*50)

        print("Empresas.....:",len(self.empresas))

        print("Investimentos:",len(self.investimentos))

        print("Eventos......:",len(self.eventos))

        print("Noticias.....:",len(self.noticias))

        print("="*50)



if __name__=="__main__":

    banco=Banco()

    banco.resumo()
