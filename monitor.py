import csv
import hashlib
import os
from datetime import datetime

def gerar_hash(texto):
    return hashlib.md5(
        texto.encode("utf-8")
    ).hexdigest()

def carregar_historico():

    vistos = set()

    if os.path.exists("historico.csv"):

        with open(
            "historico.csv",
            "r",
            encoding="utf-8"
        ) as arquivo:

            leitor = csv.DictReader(arquivo)

            for linha in leitor:
                vistos.add(linha["hash"])

    return vistos

def salvar_historico(titulo, url, fonte):

    identificador = gerar_hash(titulo + url)

    with open(
        "historico.csv",
        "a",
        newline="",
        encoding="utf-8"
    ) as arquivo:

        escritor = csv.writer(arquivo)

        escritor.writerow(
            [
                datetime.now().strftime("%Y-%m-%d"),
                titulo,
                url,
                fonte,
                identificador
            ]
        )

import requests
from bs4 import BeautifulSoup
from pathlib import Path

historico = carregar_historico()


# carregar sites
with open("sites.txt", encoding="utf-8") as f:
    sites = [s.strip() for s in f if s.strip()]

# carregar palavras-chave
with open("keywords.txt", encoding="utf-8") as f:
    keywords = [
        linha.strip().lower()
        for linha in f
        if linha.strip() and not linha.startswith("#")
    ]

resultado = []

for site in sites:

    try:

        resposta = requests.get(
            site,
            timeout=30,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        soup = BeautifulSoup(resposta.text, "lxml")
        print("Site analisado:", site)
        print("Links encontrados:", len(soup.find_all("a", href=True)))

        textos_encontrados = []

        for link in soup.find_all("a", href=True):

            titulo = link.get_text(
                " ",
                strip=True
            ).lower()

            if titulo:

    ignorar = [
        "home",
        "principal",
        "buscar",
        "assine",
        "cadastre-se",
        "entrar",
        "login",
        "ver mais",
        "leia mais",
        "clique aqui",
        "newsletter",
        "fale conosco",
        "quem somos",
        "termos de uso",
        "política de privacidade",
        "política de cookies",
        "dados abertos",
        "copyright"
    ]

    if len(titulo) < 10:
        continue

    if any(palavra in titulo for palavra in ignorar):
        continue

    print("TÍTULO:", titulo[:100])

    textos_encontrados.append(titulo)


        texto = " ".join(textos_encontrados)


        encontradas = []

        for palavra in keywords:

            if palavra in texto:
                encontradas.append(palavra)

        resultado.append({
            "site": site,
            "quantidade": len(encontradas),
            "palavras": sorted(set(encontradas))
        })

        if encontradas:

            salvar_historico(
                str(encontradas),
                site,
                "monitor"
            )

    except Exception as erro:

        resultado.append({
            "site": site,
            "erro": str(erro)
        })


# criar pasta de relatórios
Path("relatorios").mkdir(exist_ok=True)

arquivo = (
    f"relatorios/relatorio_"
    f"{datetime.now().strftime('%Y-%m-%d')}.md"
)

with open(arquivo, "w", encoding="utf-8") as f:

    f.write("# Relatório de Monitoramento\n\n")

    f.write(
        f"Gerado em: "
        f"{datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
    )

    for item in resultado:

        f.write(f"## {item['site']}\n")

        if "erro" in item:

            f.write(
                f"Erro: {item['erro']}\n\n"
            )

        else:

            f.write(
                f"Palavras encontradas: "
                f"{item['quantidade']}\n\n"
            )

            f.write(
                ", ".join(item["palavras"])
            )

            f.write("\n\n")


print("Relatório gerado com sucesso.")
