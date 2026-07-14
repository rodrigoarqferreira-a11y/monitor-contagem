"""
====================================================

ANALISADOR.PY

Cérebro do sistema.

====================================================
"""

import re

from config import PALAVRAS_CHAVE, PONTUACAO_MINIMA
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
# CLASSIFICAR TIPO
# =====================================================

def classificar_tipo(noticia):

    texto = normalizar(
        noticia.titulo + " " + noticia.texto
    )

    noticia.tipo = "Outro"

    noticia.motivos = []

    # ------------------------------------------
    # Investimento privado
    # ------------------------------------------

    if noticia.empresas:

        noticia.tipo = "Investimento Privado"
        noticia.motivos.append("Empresa identificada")

    if noticia.valores:

        noticia.motivos.append("Valor encontrado")

    if noticia.empregos:

        noticia.motivos.append("Empregos encontrados")

    # ------------------------------------------
    # Expansão
    # ------------------------------------------

    if noticia.fase == "Expansão":

        noticia.tipo = "Expansão"

        noticia.motivos.append("Fase expansão")

    # ------------------------------------------
    # Licenciamento
    # ------------------------------------------

    if noticia.fase == "Licenciamento":

        noticia.tipo = "Licenciamento"

        noticia.motivos.append("Licenciamento")

    # ------------------------------------------
    # Construção
    # ------------------------------------------

    if noticia.fase == "Construção":

        noticia.tipo = "Construção"

        noticia.motivos.append("Obra")

    # ------------------------------------------
    # Operação
    # ------------------------------------------

    if noticia.fase == "Operação":

        noticia.tipo = "Operação"

        noticia.motivos.append("Operação")

    # ------------------------------------------
    # Contratação isolada
    # ------------------------------------------

    if (
        noticia.fase == "Contratação"
        and
        not noticia.empresas
    ):

        noticia.tipo = "RH"

        noticia.motivos.append("Somente vagas")

    return noticia

# =====================================================
# CALCULAR PONTUAÇÃO
# =====================================================

def calcular_pontuacao(noticia):

    texto = normalizar(
        noticia.titulo + " " + noticia.texto
    )

    pontos = 0


    # -------------------------------------------------
    # ELEMENTOS
    # -------------------------------------------------

    tem_empresa = bool(noticia.empresas)

    tem_valor = bool(noticia.valores)

    tem_emprego = bool(noticia.empregos)

    tem_contagem = eh_contagem(noticia)


    # -------------------------------------------------
    # MUITO FORTE
    # -------------------------------------------------

    if tem_empresa and tem_contagem:
        pontos += 40


    if tem_empresa and tem_valor:
        pontos += 30


    if tem_empresa and tem_emprego:
        pontos += 20


    if tem_empresa and noticia.fase == "Expansão":
        pontos += 20


    if tem_empresa and noticia.fase == "Construção":
        pontos += 20


    if tem_empresa and noticia.fase == "Operação":
        pontos += 20


    if tem_empresa and noticia.fase == "Licenciamento":
        pontos += 20



    # -------------------------------------------------
    # PALAVRAS-CHAVE
    # Só contam se existir empresa
    # -------------------------------------------------

    palavras = encontrar_keywords(texto)

    if tem_empresa:

        pontos += len(palavras) * 5



    # -------------------------------------------------
    # FASE ANUNCIADO
    # -------------------------------------------------

    if tem_empresa and noticia.fase == "Anunciado":

        pontos += 20



    # -------------------------------------------------
    # CASOS FRACOS
    # -------------------------------------------------

    # Somente vagas

    if noticia.empregos and not tem_empresa:

        pontos += 20



    # Somente prefeitura

    if noticia.tipo == "Poder Público":

        pontos += 20



    # -------------------------------------------------
    # PENALIZAÇÕES
    # -------------------------------------------------

    texto_ruim = [

        "festival",
        "show",
        "teatro",
        "cultura",

        "vacinação",
        "vacinacao",
        "hospital",
        "saúde",
        "saude",

        "educação",
        "educacao",
        "escola"

    ]


    for palavra in texto_ruim:

        if palavra in texto:

            pontos -= 40



    # -------------------------------------------------
    # LIMITADORES
    # -------------------------------------------------

    if noticia.tipo == "RH":

        pontos = min(pontos, 30)


    if noticia.tipo == "Outro":

        pontos = min(pontos, 40)



    if pontos < 0:

        pontos = 0



    noticia.pontuacao = pontos

    return pontos


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
    # Relevância (define se será salva no banco)
    # ---------------------------------------------

    noticia.relevante = noticia.pontuacao >= PONTUACAO_MINIMA

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
