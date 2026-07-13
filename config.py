"""
config.py
----------------------------------------

Carrega todos os arquivos de configuração
utilizados pelo Monitor de Investimentos
Privados de Contagem.

Arquivos utilizados:

sites.txt
keywords.txt
contexto.txt
empresas.txt
descartaveis.txt

"""

from pathlib import Path

# ==========================================================
# PASTA RAIZ DO PROJETO
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def carregar_lista(nome_arquivo, minusculo=True):
    """
    Lê um arquivo .txt e retorna uma lista.

    Ignora:
        - linhas vazias
        - comentários iniciados por #

    """

    caminho = BASE_DIR / nome_arquivo

    if not caminho.exists():
        print(f"[AVISO] Arquivo não encontrado: {nome_arquivo}")
        return []

    resultado = []

    with open(caminho, "r", encoding="utf-8") as f:

        for linha in f:

            linha = linha.strip()

            if not linha:
                continue

            if linha.startswith("#"):
                continue

            if minusculo:
                linha = linha.lower()

            resultado.append(linha)

    return resultado


# ==========================================================
# SITES
# ==========================================================

SITES = carregar_lista("sites.txt", minusculo=False)


# ==========================================================
# PALAVRAS DE INTERESSE
# ==========================================================

PALAVRAS_CHAVE = carregar_lista("keywords.txt")

# ==========================================================
# CONTEXTO GEOGRÁFICO
# ==========================================================

CONTEXTO = carregar_lista("contexto.txt")


# ==========================================================
# PALAVRAS DESCARTADAS
# ==========================================================

DESCARTAVEIS = carregar_lista("descartaveis.txt")


# ==========================================================
# EMPRESAS MONITORADAS
# ==========================================================

EMPRESAS = carregar_lista("empresas.txt")


# ==========================================================
# CONFIGURAÇÕES GERAIS
# ==========================================================

USER_AGENT = (
    "Mozilla/5.0 "
    "(Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/138.0 Safari/537.36"
)

TIMEOUT = 30

MAX_LINKS_POR_SITE = 10

MINIMO_TITULO = 15

PONTOS_CONTEXTO = 20

PONTOS_KEYWORD = 10

PONTOS_EMPRESA = 25

PONTOS_VALOR = 20

PONTOS_EMPREGOS = 20

PONTOS_DECRETO = 10

PONTOS_EXPANSAO = 15

PONTUACAO_MINIMA = 30


# ==========================================================
# EXPRESSÕES IMPORTANTES
# ==========================================================

PALAVRAS_EXPANSAO = [

    "expansão",
    "expansao",
    "ampliação",
    "ampliacao",
    "nova unidade",
    "nova planta",
    "implantação",
    "implantacao",
    "inauguração",
    "inauguracao",

]

PALAVRAS_DECRETO = [

    "decreto",
    "lei",
    "projeto de lei",
    "licença",
    "licenca",
    "licenciamento",

]

PALAVRAS_EMPREGOS = [

    "empregos",
    "postos de trabalho",
    "vagas",
    "contratações",
    "contratacoes",
    "colaboradores",

]


# ==========================================================
# EXTENSÕES IGNORADAS
# ==========================================================

EXTENSOES_IGNORADAS = (

    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".zip",
    ".rar",
    ".mp4",
    ".avi",
    ".mp3",

)


# ==========================================================
# DEBUG
# ==========================================================

DEBUG = True


if __name__ == "__main__":

    print("=" * 60)

    print("CONFIGURAÇÃO CARREGADA")

    print("=" * 60)

    print(f"Sites...............: {len(SITES)}")
    print(f"Palavras-chave.....: {len(PALAVRAS_CHAVE)}")
    print(f"Contexto...........: {len(CONTEXTO)}")
    print(f"Empresas...........: {len(EMPRESAS)}")
    print(f"Descartáveis.......: {len(DESCARTAVEIS)}")

    print("=" * 60)

# ==========================================================
# FASES DOS INVESTIMENTOS
# ==========================================================

FASES = {

    "Negociação": [

        "protocolo",
        "assinatura"

    ],

    "Anunciado": [

        "anuncia",
        "anunciou",
        "investimento"

    ],

    "Licenciamento": [

        "copam",
        "licença",
        "licenca",
        "licenciamento",
        "semad"

    ],

    "Construção": [

        "obra",
        "obras",
        "construção",
        "construcao"

    ],

    "Contratação": [

        "empregos",
        "vagas",
        "contratação",
        "contratacao"

    ],

    "Operação": [

        "inauguração",
        "inauguracao",
        "operação",
        "operacao"

    ],

    "Expansão": [

        "expansão",
        "expansao",
        "ampliação",
        "ampliacao"

    ]

}
