"""
====================================================

EXTRATOR HTML

Responsável por:

• Baixar páginas
• Extrair título
• Extrair texto
• Extrair data
• Limpar HTML

====================================================
"""

import requests

from bs4 import BeautifulSoup

from bs4.element import Comment

from datetime import datetime

from modelos import Noticia

from config import USER_AGENT, TIMEOUT


# =====================================================
# BAIXAR HTML
# =====================================================

def baixar_html(url):

    try:

        resposta = requests.get(

            url,

            headers={

                "User-Agent": USER_AGENT

            },

            timeout=TIMEOUT

        )

        resposta.raise_for_status()

        return BeautifulSoup(

            resposta.text,

            "lxml"

        )

    except Exception as erro:

        print(f"Erro ao abrir {url}")

        print(erro)

        return None


# =====================================================
# REMOVER TAGS INÚTEIS
# =====================================================

def limpar_html(soup):

    if soup is None:

        return None

    remover = [

        "script",

        "style",

        "noscript",

        "iframe",

        "svg",

        "footer",

        "header",

        "nav",

        "form",

        "aside"

    ]

    for tag in remover:

        for item in soup.find_all(tag):

            item.decompose()

    return soup


# =====================================================
# REMOVER COMENTÁRIOS HTML
# =====================================================

def remover_comentarios(soup):

    comentarios = soup.find_all(

        string=lambda texto:

        isinstance(texto, Comment)

    )

    for comentario in comentarios:

        comentario.extract()

    return soup


# =====================================================
# REMOVER DIVS COMUNS
# =====================================================

def remover_blocos(soup):

    palavras = [

        "menu",

        "sidebar",

        "newsletter",

        "banner",

        "cookie",

        "social",

        "compartilhe",

        "coment",

        "rodape",

        "footer",

        "relacionad",

        "publicidade",

        "ads"

    ]

    for tag in soup.find_all(True):

        texto = " ".join(

            [

                tag.get("id",""),

                " ".join(tag.get("class",[]))

            ]

        ).lower()

        if any(

            palavra in texto

            for palavra in palavras

        ):

            tag.decompose()

    return soup


# =====================================================
# LOCALIZAR ÁREA PRINCIPAL
# =====================================================

def localizar_conteudo(soup):

    candidatos = [

        "article",

        "main",

        ".entry-content",

        ".post-content",

        ".content",

        ".conteudo",

        ".article-content",

        ".news-content",

        ".single-content"

    ]

    for seletor in candidatos:

        try:

            if seletor.startswith("."):

                area = soup.select_one(seletor)

            else:

                area = soup.find(seletor)

            if area:

                return area

        except:

            pass

    return soup.body


# =====================================================
# EXTRAIR TEXTO
# =====================================================

def extrair_texto(area):

    if area is None:

        return ""

    textos = []

    for p in area.find_all(

        [

            "p",

            "h1",

            "h2",

            "h3",

            "li"

        ]

    ):

        txt = p.get_text(

            " ",

            strip=True

        )

        if len(txt) > 20:

            textos.append(txt)

    return "\n\n".join(textos)


# =====================================================
# EXTRAIR TÍTULO
# =====================================================

def extrair_titulo(soup):

    if soup.find("h1"):

        return soup.find("h1").get_text(

            strip=True

        )

    if soup.title:

        return soup.title.get_text(

            strip=True

        )

    return ""


# =====================================================
# EXTRAIR DATA
# =====================================================

def extrair_data(soup):

    time = soup.find("time")

    if time:

        if time.get("datetime"):

            return time["datetime"]

        return time.get_text(

            strip=True

        )

    return datetime.now().strftime("%Y-%m-%d")
