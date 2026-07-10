import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

# ----------------------------
# Carregar sites
# ----------------------------

with open("sites.txt", encoding="utf-8") as f:
    sites = [linha.strip() for linha in f if linha.strip()]

# ----------------------------
# Carregar palavras-chave
# ----------------------------

with open("keywords.txt", encoding="utf-8") as f:
    keywords = [k.strip().lower() for k in f if k.strip()]

relatorio = []

headers = {
    "User-Agent":"Mozilla/5.0"
}

print("Iniciando monitoramento...")

for site in sites:

    print(f"Lendo {site}")

    try:

        resposta = requests.get(site,headers=headers,timeout=30)

        soup = BeautifulSoup(resposta.text,"lxml")

        texto = soup.get_text(" ",strip=True)

        texto_lower = texto.lower()

        encontradas=[]

        for palavra in keywords:

            if palavra in texto_lower:

                encontradas.append(palavra)

        if encontradas:

            relatorio.append({

                "site":site,

                "palavras":", ".join(sorted(set(encontradas)))

            })

    except Exception as erro:

        relatorio.append({

            "site":site,

            "palavras":"ERRO: "+str(erro)

        })

# ----------------------------
# Salvar relatório
# ----------------------------

os.makedirs("relatorios",exist_ok=True)

arquivo=f"relatorios/relatorio_{datetime.now().strftime('%Y-%m-%d')}.md"

with open(arquivo,"w",encoding="utf-8") as f:

    f.write("# Relatório Diário\n\n")

    f.write(f"Data: {datetime.now()}\n\n")

    if len(relatorio)==0:

        f.write("Nenhuma ocorrência encontrada.")

    else:

        for item in relatorio:

            f.write(f"## {item['site']}\n")

            f.write(f"Palavras encontradas: {item['palavras']}\n\n")

print("Concluído.")
