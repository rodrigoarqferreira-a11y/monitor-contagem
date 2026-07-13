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

        resposta.encoding = resposta.apparent_encoding

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

    if soup is None:
        return None

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


    try:

        for tag in soup.find_all(True):

            if not hasattr(tag, "get"):
                continue


            identificador = tag.get("id") or ""


            classes = tag.get("class") or []


            if isinstance(classes, list):

                classes = " ".join(classes)

            else:

                classes = str(classes)


            texto = (

                identificador +

                " " +

                classes

            ).lower()



            if any(
                palavra in texto
                for palavra in palavras
            ):

                tag.decompose()


    except Exception as erro:

        print("ERRO remover_blocos:")
        print(erro)


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

            "li",

            "blockquote",

            "figcaption"

        ]

    ):

        txt = p.get_text(

            " ",

            strip=True

        )

        if len(txt) > 15:

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

# =====================================================
# EXTRAIR IMAGEM PRINCIPAL
# =====================================================

def extrair_imagem(soup):

    if soup is None:
        return ""

    # Open Graph
    meta = soup.find("meta", property="og:image")

    if meta and meta.get("content"):
        return meta["content"]

    # Twitter
    meta = soup.find("meta", attrs={"name": "twitter:image"})

    if meta and meta.get("content"):
        return meta["content"]

    img = soup.find("img")

    if img and img.get("src"):
        return img["src"]

    return ""


# =====================================================
# EXTRAIR AUTOR
# =====================================================

def extrair_autor(soup):

    if soup is None:
        return ""

    meta = soup.find("meta", attrs={"name": "author"})

    if meta and meta.get("content"):
        return meta["content"]

    autor = soup.find(class_=lambda x: x and "author" in str(x).lower())

    if autor:
        return autor.get_text(" ", strip=True)

    return ""


# =====================================================
# IDENTIFICAR FONTE
# =====================================================

def identificar_fonte(url):

    url = url.lower()

    if "portal.contagem" in url:
        return "Portal Contagem"

    if "agenciaminas" in url:
        return "Agência Minas"

    if "investminas" in url:
        return "Invest Minas"

    if "fiemg" in url:
        return "FIEMG"

    if "diariodocomercio" in url:
        return "Diário do Comércio"

    if "otempo" in url:
        return "O Tempo"

    return "Desconhecido"


# =====================================================
# EXTRAIR NOTÍCIA COMPLETA
# =====================================================

def extrair_noticia(url):

    try:

        soup = baixar_html(url)

        if soup is None:
            return None

        print("OK baixar:", url)

        soup = limpar_html(soup)

        print("OK limpar")

        soup = remover_comentarios(soup)

        print("OK comentarios")

        soup = remover_blocos(soup)

        print("OK blocos")

        area = localizar_conteudo(soup)

        print("OK conteudo")


        noticia = Noticia()

        noticia.url = url

        noticia.fonte = identificar_fonte(url)

        noticia.titulo = extrair_titulo(soup)

        noticia.texto = extrair_texto(area)

        noticia.data = extrair_data(soup)

        noticia.autor = extrair_autor(soup)

        noticia.imagem = extrair_imagem(soup)

        noticia.resumo = noticia.texto[:600]

        print("OK noticia criada")

        return noticia


    except Exception as erro:

        print("ERRO INTERNO EXTRATOR:")
        print(url)
        print(erro)

        return None


# =====================================================
# TESTE
# =====================================================

if __name__ == "__main__":

    url = input("Cole uma URL de notícia:\n\n")

    noticia = extrair_noticia(url)

    if noticia is None:

        print("\nErro ao abrir a página.")

    else:

        print("\n==============================")

        print("FONTE")

        print(noticia.fonte)

        print("\n==============================")

        print("TÍTULO")

        print(noticia.titulo)

        print("\n==============================")

        print("DATA")

        print(noticia.data)

        print("\n==============================")

        print("AUTOR")

        print(noticia.autor)

        print("\n==============================")

        print("TEXTO")

        print(noticia.texto[:2000])

        print("\n==============================")

        print("IMAGEM")

        print(noticia.imagem)

        print("\n==============================")

