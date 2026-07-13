"""
====================================================

CRAWLER

Responsável por:

• Ler os sites
• Encontrar notícias
• Abrir cada notícia
• Devolver objetos Noticia

====================================================
"""

from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup

from config import (
    SITES,
    USER_AGENT,
    TIMEOUT,
    MAX_LINKS_POR_SITE
)

from utils import (
    url_valida
)

from extrator_html import (
    extrair_noticia
)


# =====================================================
# BAIXAR PÁGINA
# =====================================================

def baixar(site):

    try:

        r = requests.get(

            site,

            headers={

                "User-Agent": USER_AGENT

            },

            timeout=TIMEOUT

        )

        r.raise_for_status()

        return BeautifulSoup(

            r.text,

            "lxml"

        )

    except Exception as erro:

        print(f"Erro em {site}")

        print(erro)

        return None


# =====================================================
# IDENTIFICAR LINK DE NOTÍCIA
# =====================================================

def parece_noticia(url):

    url = url.lower()

    palavras = [

        "/noticia",

        "/noticias",

        "/news",

        "/article",

        "/202",

        "/20"

    ]

    return any(

        palavra in url

        for palavra in palavras

    )


# =====================================================
# COLETAR LINKS
# =====================================================

def coletar_links(site):

    soup = baixar(site)

    if soup is None:

        return []

    links = set()

    for a in soup.find_all("a", href=True):

        href = a["href"]

        href = urljoin(site, href)

        if not url_valida(href):

            continue

        if not parece_noticia(href):

            continue

        links.add(href)

    return sorted(links)[:MAX_LINKS_POR_SITE]


# =====================================================
# EXECUTAR CRAWLER
# =====================================================

def executar():

    noticias = []

    for site in SITES:

        print()

        print("=" * 60)

        print(site)

        print("=" * 60)

        links = coletar_links(site)

        print(f"{len(links)} links encontrados")

        for i, link in enumerate(links, start=1):

            print(f"[{i}/{len(links)}]")

            try:

                noticia = extrair_noticia(link)

            except Exception as erro:

                print()
                print("Erro ao extrair notícia:")
                print(link)
                print(erro)
                print()

                continue


            if noticia is None:
                continue


            if len(noticia.texto) < 200:
                continue


            noticias.append(noticia)

    return noticias


# =====================================================
# TESTE
# =====================================================

if __name__ == "__main__":

    noticias = executar()

    print()

    print("=" * 60)

    print(f"TOTAL DE NOTÍCIAS: {len(noticias)}")

    print("=" * 60)

    for noticia in noticias[:10]:

        print()

        print(noticia.fonte)

        print(noticia.titulo)

        print(noticia.url)

        print("-" * 60)
