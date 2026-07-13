"""
=====================================================

INTEL.PY

Camada de inteligência do Monitor de Investimentos
Privados de Contagem.

Responsável por:

- Gerar resumo executivo
- Classificar relevância
- Identificar situação do investimento
- Gerar informações para relatórios

=====================================================
"""


from datetime import datetime

from config import (
    PONTUACAO_MINIMA
)

from utils import (
    estrelas,
    normalizar
)



# =====================================================
# CLASSIFICAR IMPORTÂNCIA
# =====================================================

def classificar_noticia(noticia):

    pontos = noticia.pontuacao


    if pontos >= 90:

        return "Muito relevante"


    if pontos >= 70:

        return "Relevante"


    if pontos >= 50:

        return "Monitorar"


    return "Baixa relevância"



# =====================================================
# CALCULAR CONFIANÇA
# =====================================================

def calcular_confianca(noticia):

    confianca = 0


    if noticia.empresas:

        confianca += 30


    if noticia.valores:

        confianca += 25


    if noticia.empregos:

        confianca += 15


    if noticia.url:

        confianca += 15


    if noticia.fonte:

        confianca += 15


    if confianca > 100:

        confianca = 100


    return confianca



# =====================================================
# IDENTIFICAR STATUS
# =====================================================

def identificar_status(noticia):

    texto = normalizar(

        noticia.titulo +
        " " +
        noticia.texto

    )


    if any(
        palavra in texto
        for palavra in [
            "inauguracao",
            "inauguração",
            "operacao",
            "operação"
        ]
    ):

        return "Em operação"



    if any(
        palavra in texto
        for palavra in [
            "obra",
            "construcao",
            "construção"
        ]
    ):

        return "Em construção"



    if any(
        palavra in texto
        for palavra in [
            "licenca",
            "licença",
            "licenciamento"
        ]
    ):

        return "Licenciamento"



    if any(
        palavra in texto
        for palavra in [
            "anuncia",
            "anunciou",
            "investimento"
        ]
    ):

        return "Anunciado"



    return "Não identificado"



# =====================================================
# GERAR RESUMO EXECUTIVO
# =====================================================

def gerar_resumo(noticia):


    empresas = ", ".join(
        noticia.empresas
    ) if noticia.empresas else "Empresa não identificada"



    valores = ", ".join(
        noticia.valores
    ) if noticia.valores else "Valor não informado"



    empregos = ", ".join(
        noticia.empregos
    ) if noticia.empregos else "Empregos não informados"



    resumo = f"""

Empresa:
{empresas}


Investimento:
{valores}


Empregos:
{empregos}


Fase:
{noticia.fase}


Status:
{noticia.status}


Fonte:
{noticia.fonte}


Data:
{noticia.data}


Link:
{noticia.url}

"""


    return resumo.strip()



# =====================================================
# PROCESSAMENTO INTELIGENTE
# =====================================================

def analisar_inteligencia(noticia):


    noticia.status = identificar_status(
        noticia
    )


    noticia.confianca = calcular_confianca(
        noticia
    )


    noticia.estrelas = estrelas(
        noticia.pontuacao
    )


    return {

        "classificacao":
            classificar_noticia(noticia),


        "confianca":
            noticia.confianca,


        "estrelas":
            noticia.estrelas,


        "status":
            noticia.status,


        "resumo":
            gerar_resumo(noticia)

    }



# =====================================================
# TESTE
# =====================================================

if __name__ == "__main__":


    print("=" * 60)

    print(
        "INTEL - Monitor de Investimentos"
    )

    print(
        datetime.now().strftime(
            "%d/%m/%Y %H:%M"
        )
    )

    print("=" * 60)
