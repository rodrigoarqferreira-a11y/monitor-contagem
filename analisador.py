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
    encontrar_empresas
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

    pontos = 0

    if eh_contagem(noticia):
        pontos += 30

    pontos += len(noticia.empresas) * 20

    pontos += len(noticia.valores) * 15

    pontos += len(noticia.empregos) * 10

    texto = normalizar(

        noticia.titulo + " " + noticia.texto

    )

    for palavra in PALAVRAS_CHAVE:

        if normalizar(palavra) in texto:
            pontos += 2

    noticia.pontuacao = pontos

    noticia.relevante = (
    pontos >= 40
    and
    (
        len(noticia.valores) > 0
        or
        len(noticia.empregos) > 0
        or
        noticia.fase in [
            "Anunciado",
            "Construção",
            "Operação",
            "Expansão"
        ]
    )
)


# =====================================================
# ANALISAR
# =====================================================

def analisar(noticia):

    analisar_empresas(noticia)

    analisar_valores(noticia)

    analisar_empregos(noticia)

    analisar_fase(noticia)

    classificar_tipo(noticia)

    calcular_pontuacao(noticia)

    classificar_tipo(noticia)

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
