"""
==============================================================

MODELOS

Projeto:
Monitor Inteligente de Investimentos Privados de Contagem

==============================================================
"""

from dataclasses import dataclass, field
from typing import List


# ==========================================================
# NOTÍCIA
# ==========================================================

@dataclass
class Noticia:

    titulo: str = ""

    texto: str = ""

    resumo: str = ""

    url: str = ""

    fonte: str = ""

    data: str = ""

    autor: str = ""

    categoria: str = ""

    imagem: str = ""

    palavras: List[str] = field(default_factory=list)

    empresas: List[str] = field(default_factory=list)

    empregos: List[str] = field(default_factory=list)

    valores: List[str] = field(default_factory=list)

    bairros: List[str] = field(default_factory=list)

    pontuacao: int = 0

    estrelas: str = ""

    relevante: bool = False

    fase: str = ""

    status: str = ""

    confianca: int = 0


# ==========================================================
# INVESTIMENTO
# ==========================================================

@dataclass
class Investimento:

    id: int = 0

    empresa: str = ""

    tipo: str = ""

    segmento: str = ""

    valor: str = ""

    empregos: str = ""

    bairro: str = ""

    cidade: str = "Contagem"

    estado: str = "MG"

    data: str = ""

    fase: str = ""

    status: str = ""

    fonte: str = ""

    url: str = ""

    observacao: str = ""

    pontuacao: int = 0

    confianca: int = 0


# ==========================================================
# SITE
# ==========================================================

@dataclass
class Site:

    nome: str = ""

    url: str = ""

    dominio: str = ""

    wordpress: bool = False

    categoria: str = "Noticias"

    ativo: bool = True


# ==========================================================
# RESULTADO
# ==========================================================

@dataclass
class ResultadoCrawler:

    site: str

    links_lidos: int = 0

    noticias_lidas: int = 0

    noticias_relevantes: int = 0

    noticias_novas: int = 0

    erros: int = 0
