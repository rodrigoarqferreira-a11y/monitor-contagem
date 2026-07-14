"""
====================================================

ANALISADOR.PY

Cérebro do sistema.

====================================================
"""

import re

from config import PALAVRAS_CHAVE
from utils import (
    normalizar,
    encontrar_empresas,
    encontrar_keywords,
    identificar_fase,
    identificar_status,
    estrelas,
    calcular_confianca,
    classificar_relevancia
)

# =====================================================
# FILTROS DE DESCARTE
# =====================================================

TERMOS_NEGATIVOS = [

    "processo seletivo",
    "pss",
    "concurso publico",
    "concurso público",
    "edital",
    "vacina",
    "campanha",
    "festival",
    "evento cultural",
    "esporte",
    "partida",
    "jogo",
    "saude",
    "saúde",
    "curso gratuito",
    "capacitação",
    "formacao tecnica",
    "formação técnica"

]


# =====================================================
# TERMOS QUE INDICAM INVESTIMENTO
# =====================================================

TERMOS_INVESTIMENTO = [

    "investimento",
    "investimentos",
    "nova unidade",
    "nova fabrica",
    "nova fábrica",
    "expansao",
    "expansão",
    "ampliacao",
    "ampliação",
    "planta industrial",
    "centro de distribuicao",
    "centro de distribuição",
    "galpao",
    "galpão",
    "implantacao",
    "implantação",
    "obra industrial"

]

# =====================================================
# É SOBRE CONTAGEM?
# =====================================================

def eh_contagem(noticia):

    texto = normalizar(

        noticia.titulo + " " + noticia.texto

    )

    termos = [

        "contagem",

        "municipio de contagem",

        "município de contagem",

        "prefeitura de contagem",

        "nova contagem"

    ]

    return any(

        termo in texto

        for termo in termos

    )


# =====================================================
# EXTRAIR EMPRESAS
# =====================================================

def analisar_empresas(noticia):

    texto = noticia.titulo + " " + noticia.texto

    noticia.empresas = encontrar_empresas(texto)


# =====================================================
# EXTRAIR VALORES
# =====================================================

def analisar_valores(noticia):

    texto = noticia.titulo + " " + noticia.texto

    padrao = r"R\$ ?[\d\.,]+ ?(?:milhões|milhao|milhão|bilhões|bilhao|bilhão|mil)?"

    noticia.valores = re.findall(

        padrao,

        texto,

        flags=re.IGNORECASE

    )


# =====================================================
# EXTRAIR EMPREGOS
# =====================================================

def analisar_empregos(noticia):

    texto = noticia.titulo + " " + noticia.texto

    padrao = r"\d+[\.]?\d*\s+(?:empregos|postos de trabalho|vagas)"

    noticia.empregos = re.findall(

        padrao,

        texto,

        flags=re.IGNORECASE

    )


# =====================================================
# IDENTIFICAR FASE
# =====================================================

def analisar_fase(noticia):

    texto = normalizar(

        noticia.titulo + " " + noticia.texto

    )

    fases = {

        "Negociação":[

            "protocolo",

            "assinatura"

        ],

        "Anunciado":[

            "anuncia",

            "anunciou",

            "investimento"

        ],

        "Licenciamento":[

            "copam",

            "licença",

            "licenciamento",

            "semad"

        ],

        "Construção":[

            "obra",

            "obras",

            "construção",

            "construcoes"

        ],

        "Contratação":[

            "contratação",

            "contratacao",

            "empregos",

            "vagas"

        ],

        "Operação":[

            "inauguração",

            "inauguracao",

            "operação",

            "operacao"

        ],

        "Expansão":[

            "expansão",

            "expansao",

            "ampliação",

            "ampliacao"

        ]

    }

    noticia.fase = "Não identificada"

    for fase, palavras in fases.items():

        for palavra in palavras:

            if palavra in texto:

                noticia.fase = fase

                return

# =====================================================
# CLASSIFICAR TIPO DA NOTICIA
# =====================================================

def classificar_tipo(noticia):

    texto = normalizar(
        noticia.titulo + " " + noticia.texto
    )


    # Notícias que não são investimento

    for termo in TERMOS_NEGATIVOS:

        if termo in texto:

            noticia.tipo = "Descartada"

            return


    tem_empresa = len(noticia.empresas) > 0

    tem_valor = len(noticia.valores) > 0

    tem_investimento = any(

        termo in texto

        for termo in TERMOS_INVESTIMENTO

    )


    if tem_empresa and (tem_valor or tem_investimento):

        noticia.tipo = "Investimento privado"

        return


    if tem_empresa and noticia.empregos:

        noticia.tipo = "Expansão empresarial"

        return


    noticia.tipo = "Não identificado"

# =====================================================
# CALCULAR PONTUAÇÃO
# =====================================================

def calcular_pontuacao(noticia):

    texto = normalizar(

        noticia.titulo + " " + noticia.texto

    )

    pontos = 0

    # -------------------------------------------------
    # CONTEXTO
    # -------------------------------------------------

    if eh_contagem(noticia):

        pontos += 20

    # -------------------------------------------------
    # EMPRESA
    # -------------------------------------------------

    if noticia.empresas:

        pontos += 30

    # -------------------------------------------------
    # VALORES
    # -------------------------------------------------

    if noticia.valores:

        pontos += 20

    # -------------------------------------------------
    # EMPREGOS
    # -------------------------------------------------

    if noticia.empregos:

        pontos += 15

    # -------------------------------------------------
    # PALAVRAS-CHAVE
    # -------------------------------------------------

    palavras = encontrar_keywords(texto)

    pontos += len(palavras) * 8

    # -------------------------------------------------
    # FASES IMPORTANTES
    # -------------------------------------------------

    if noticia.fase in (

        "Anunciado",

        "Expansão",

        "Construção",

        "Licenciamento",

        "Operação"

    ):

        pontos += 20

    # -------------------------------------------------
    # BÔNUS
    # -------------------------------------------------

    if noticia.empresas and noticia.valores:

        pontos += 20

    if noticia.empresas and noticia.empregos:

        pontos += 15

    if noticia.empresas and eh_contagem(noticia):

        pontos += 20

    # -------------------------------------------------
    # PENALIZAÇÕES
    # -------------------------------------------------

    texto_ruim = [

        "festival",

        "esporte",

        "vacinação",

        "vacinacao",

        "show",

        "teatro",

        "cultura",

        "hepatite",

        "educação",

        "educacao",

        "escola",

        "pss",

        "concurso",

        "processo seletivo",

        "ouvidoria"

    ]

    for palavra in texto_ruim:

        if palavra in texto:

            pontos -= 30

    # -------------------------------------------------
    # LIMITES
    # -------------------------------------------------

    if pontos < 0:

        pontos = 0

    noticia.pontuacao = pontos

    noticia.relevante = pontos >= 50


# =====================================================
# ANALISAR
# =====================================================

def analisar(noticia):

    texto = noticia.titulo + " " + noticia.texto

    # ---------------------------------------------
    # Empresas
    # ---------------------------------------------

    noticia.empresas = encontrar_empresas(texto)

    # ---------------------------------------------
    # Valores
    # ---------------------------------------------

    analisar_valores(noticia)

    # ---------------------------------------------
    # Empregos
    # ---------------------------------------------

    analisar_empregos(noticia)

    # ---------------------------------------------
    # Palavras-chave
    # ---------------------------------------------

    noticia.palavras = encontrar_keywords(texto)

    # ---------------------------------------------
    # Contexto Contagem
    # ---------------------------------------------

    contexto = eh_contagem(noticia)

    # ---------------------------------------------
    # Fase
    # ---------------------------------------------

    noticia.fase = identificar_fase(texto)

    # ---------------------------------------------
    # Status
    # ---------------------------------------------

    noticia.status = identificar_status(texto)

    # ---------------------------------------------
    # Tipo
    # ---------------------------------------------

    classificar_tipo(noticia)

    # ---------------------------------------------
    # Pontuação
    # ---------------------------------------------

    calcular_pontuacao(noticia)

    # ---------------------------------------------
    # Estrelas
    # ---------------------------------------------

    noticia.estrelas = estrelas(noticia.pontuacao)

    # ---------------------------------------------
    # Classificação
    # ---------------------------------------------

    noticia.classificacao = classificar_relevancia(
    noticia.pontuacao
    )

    # ---------------------------------------------
    # Confiança
    # ---------------------------------------------

    noticia.confianca = calcular_confianca(

        noticia.empresas,

        noticia.valores,

        noticia.empregos,

        contexto

    )

    return noticia

# =====================================================
# INTEGRAÇÃO COM O BANCO
# =====================================================

from banco import Banco


banco = Banco()


# =====================================================
# SALVAR NOTÍCIA
# =====================================================

def salvar_noticia(noticia):

    # Não salva notícias pouco relevantes
    if not noticia.relevante:
        return False

    # Salva a notícia
    banco.adicionar_noticia(noticia)

    # Se nenhuma empresa foi encontrada,
    # apenas registra a notícia.
    if len(noticia.empresas) == 0:

        banco.salvar()

        return True

    # Cria/atualiza empresas e investimentos

    ano = ""

    if noticia.data:

        ano = str(noticia.data)[:4]

    else:

        ano = "Desconhecido"

    for empresa in noticia.empresas:

        banco.adicionar_empresa(empresa)

        valor = ""

        if noticia.valores:

            valor = noticia.valores[0]

        empregos = ""

        if noticia.empregos:

            empregos = noticia.empregos[0]

        investimento = banco.adicionar_investimento(

            empresa=empresa,

            ano=ano,

            valor=valor,

            empregos=empregos

        )

        banco.adicionar_evento(

            investimento_id=investimento["id"],

            fase=noticia.fase,

            noticia=noticia

        )

    banco.salvar()

    return True


# =====================================================
# PROCESSAR
# =====================================================

def processar(noticia):

    noticia = analisar(noticia)

    salvar_noticia(noticia)

    return noticia


# =====================================================
# RESUMO
# =====================================================

def imprimir_resumo(noticia):

    print()

    print("=" * 70)

    print(noticia.titulo)

    print("=" * 70)

    print()

    print("Fonte:")

    print(noticia.fonte)

    print()

    print("Tipo:")

    print(noticia.tipo)

    print()

    print("Data:")

    print(noticia.data)

    print()

    print("Empresas:")

    if noticia.empresas:

        for empresa in noticia.empresas:

            print(" -", empresa)

    else:

        print(" Nenhuma")

    print()

    print("Valores:")

    if noticia.valores:

        for valor in noticia.valores:

            print(" -", valor)

    else:

        print(" Nenhum")

    print()

    print("Empregos:")

    if noticia.empregos:

        for emprego in noticia.empregos:

            print(" -", emprego)

    else:

        print(" Nenhum")

    print()

    print("Fase:")

    print(noticia.fase)

    print()

    print("Pontuação:")

    print(noticia.pontuacao)

    print()

    print("Relevante:")

    print("SIM" if noticia.relevante else "NÃO")

    print()

    print("=" * 70)
