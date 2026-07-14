"""
utils.py
------------------------------------------------------------

Funções auxiliares utilizadas em todo o projeto.

Autor: Projeto Monitor Contagem

"""

import hashlib
import re
import unicodedata
from urllib.parse import urljoin, urlparse

from config import (
    EMPRESAS,
    EXTENSOES_IGNORADAS,
    CONTEXTO,
    PALAVRAS_CHAVE,
    FASES
)

# ==========================================================
# TEXTO
# ==========================================================

def remover_acentos(texto: str) -> str:
    if not texto:
        return ""

    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def limpar_texto(texto: str) -> str:

    if texto is None:
        return ""

    texto = texto.replace("\n", " ")
    texto = texto.replace("\r", " ")
    texto = texto.replace("\t", " ")

    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def normalizar(texto: str) -> str:

    texto = limpar_texto(texto)

    texto = remover_acentos(texto)

    return texto.lower()


# ==========================================================
# HASH
# ==========================================================

def gerar_hash(texto: str) -> str:

    return hashlib.md5(
        texto.encode("utf-8")
    ).hexdigest()


# ==========================================================
# URL
# ==========================================================

def url_absoluta(site, link):

    if not link:
        return None

    link = link.strip()

    if link.startswith("javascript:"):
        return None

    if link.startswith("#"):
        return None

    return urljoin(site, link)


def url_valida(url):

    if not url:
        return False

    try:

        resultado = urlparse(url)

        if resultado.scheme not in ("http", "https"):
            return False

        caminho = resultado.path.lower()

        for ext in EXTENSOES_IGNORADAS:

            if caminho.endswith(ext):
                return False

        return True

    except:

        return False


# ==========================================================
# EMPRESAS
# ==========================================================

def encontrar_empresas(texto):

    texto_normalizado = normalizar(texto)

    encontradas = []

    for linha in EMPRESAS:

        nomes = [
            n.strip()
            for n in linha.split("|")
            if n.strip()
        ]

        nome_oficial = nomes[0]

        for nome in nomes:

            nome_normalizado = normalizar(nome)

            # transforma em busca por palavra inteira
            padrao = r"\b" + re.escape(nome_normalizado) + r"\b"

            if re.search(
                padrao,
                texto_normalizado
            ):

                encontradas.append(nome_oficial)

                break


    return sorted(set(encontradas))


# ==========================================================
# VALORES
# ==========================================================

def extrair_valores(texto):

    texto = limpar_texto(texto)

    padrao = re.compile(

        r"""
        (R\$|US\$|€)?
        \s*
        (\d+(?:[\.,]\d+)?)
        \s*
        (mil|milhão|milhoes|milhões|bilhão|bilhoes|bilhões)?
        """,

        re.IGNORECASE | re.VERBOSE

    )

    valores = []

    for moeda, numero, unidade in padrao.findall(texto):

        numero = numero.strip()

        moeda = moeda.strip()

        unidade = unidade.strip()

        if len(numero) == 0:
            continue

        valores.append(

            f"{moeda} {numero} {unidade}".strip()

        )

    return valores


# ==========================================================
# EMPREGOS
# ==========================================================

def extrair_empregos(texto):

    texto = limpar_texto(texto)

    padrao = re.compile(

        r"""
        (\d[\d\.]*)

        \s*

        (

        empregos|

        vagas|

        colaboradores|

        funcionários|

        funcionarios|

        postos\ de\ trabalho

        )

        """,

        re.IGNORECASE | re.VERBOSE

    )

    encontrados = []

    for numero, tipo in padrao.findall(texto):

        encontrados.append(

            f"{numero} {tipo}"

        )

    return encontrados


# ==========================================================
# CONTAGEM
# ==========================================================

def possui_contagem(texto, contexto):

    texto = normalizar(texto)

    for palavra in contexto:

        if normalizar(palavra) in texto:

            return True

    return False


# ==========================================================
# KEYWORDS
# ==========================================================

def encontrar_keywords(texto, PALAVRAS_CHAVE):

    texto = normalizar(texto)

    resultado = []

    for palavra in keywords:

        if normalizar(palavra) in texto:

            resultado.append(palavra)

    return sorted(set(resultado))


# ==========================================================
# PONTUAÇÃO
# ==========================================================

def calcular_pontuacao(

    possui_contexto,

    quantidade_keywords,

    quantidade_empresas,

    quantidade_valores,

    quantidade_empregos

):

    pontos = 0

    if possui_contexto:

        pontos += 20

    pontos += quantidade_keywords * 10

    pontos += min(quantidade_empresas,3) * 5

    pontos += quantidade_valores * 15

    pontos += quantidade_empregos * 15

    return pontos


# ==========================================================
# ESTRELAS
# ==========================================================

def estrelas(pontos):

    if pontos >= 90:
        return "★★★★★"

    if pontos >= 70:
        return "★★★★☆"

    if pontos >= 50:
        return "★★★☆☆"

    if pontos >= 30:
        return "★★☆☆☆"

    return "★☆☆☆☆"

# ==========================================================
# PALAVRAS-CHAVE ENCONTRADAS
# ==========================================================

def encontrar_keywords(texto):

    texto = normalizar(texto)

    encontradas = []

    for palavra in PALAVRAS_CHAVE:

        if normalizar(palavra) in texto:

            encontradas.append(palavra)

    return sorted(set(encontradas))

# ==========================================================
# IDENTIFICAR FASE
# ==========================================================

def identificar_fase(texto):

    texto = normalizar(texto)

    for fase, palavras in FASES.items():

        for palavra in palavras:

            if normalizar(palavra) in texto:

                return fase

    return "Não identificada"


# ==========================================================
# IDENTIFICAR STATUS
# ==========================================================

def identificar_status(texto):

    texto = normalizar(texto)

    regras = {

        "Em operação": [

            "opera",
            "operação",
            "operacao",
            "funcionando",
            "inaugurada",
            "inaugurado"

        ],

        "Em construção": [

            "obra",
            "obras",
            "construção",
            "construcao"

        ],

        "Anunciado": [

            "anunciou",
            "anuncia",
            "investimento"

        ]

    }

    for status, palavras in regras.items():

        for palavra in palavras:

            if normalizar(palavra) in texto:

                return status

    return "Não identificado"

# ==========================================================
# CLASSIFICAÇÃO
# ==========================================================

def classificar_relevancia(pontos):

    if pontos >= 80:

        return "Muito relevante"

    if pontos >= 60:

        return "Relevante"

    if pontos >= 40:

        return "Monitorar"

    return "Baixa relevância"

# ==========================================================
# CONFIANÇA
# ==========================================================

def calcular_confianca(

    empresas,

    valores,

    empregos,

    contexto

):

    confianca = 40

    if contexto:

        confianca += 20

    if empresas:

        confianca += 20

    if valores:

        confianca += 10

    if empregos:

        confianca += 10

    return min(confianca, 100)


# ==========================================================
# DEBUG
# ==========================================================

if __name__ == "__main__":

    texto = """

    Mercado Livre anuncia investimento
    de R$ 400 milhões em Contagem,
    criando 850 empregos.

    """

    print()

    print("EMPRESAS")

    print(encontrar_empresas(texto))

    print()

    print("VALORES")

    print(extrair_valores(texto))

    print()

    print("EMPREGOS")

    print(extrair_empregos(texto))

    print()

    print("KEYWORDS")

    from config import PALAVRAS_CHAVE

    print(encontrar_keywords(texto, PALAVRAS_CHAVE))

    print()

    print("CONTAGEM")

    from config import CONTEXTO

    print(possui_contagem(texto, CONTEXTO))

    print()

    pontos = calcular_pontuacao(

        True,

        5,

        1,

        1,

        1

    )

    print("PONTOS")

    print(pontos)

    print(estrelas(pontos))
