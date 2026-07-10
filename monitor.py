import csv
import hashlib
import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from pathlib import Path

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

        texto = soup.get_text(" ", strip=True).lower()

        encontradas = []

        for palavra in keywords:

            if palavra in texto:
                encontradas.append(palavra)

        if encontradas:

            resultado.append({
                "site": site,
                "quantidade": len(encontradas),
                "palavras": sorted(set(encontradas))
            })

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
