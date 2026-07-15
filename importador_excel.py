"""
=========================================================

IMPORTADOR_EXCEL.PY

Importa a base histórica de investimentos privados
(planilha 2021-2026) para o banco de dados do monitor.

Rodar uma vez sempre que a planilha for atualizada:
    python importador_excel.py

=========================================================
"""

import re
import pandas as pd

from banco import Banco


ARQUIVO_PLANILHA = "dados/Investimentos Privados em Contagem 2021-2026.xlsx"


# =====================================================
# LIMPEZA DE TEXTO
# =====================================================

def limpar_nome_empresa(nome):
    """
    Remove espaços extras, vírgulas soltas no início/fim
    e normaliza espaçamento interno, para evitar que a
    mesma empresa apareça duplicada no ranking
    (ex: "Komatsu " vs "Komatsu").
    """
    if not isinstance(nome, str):
        return ""

    nome = nome.strip()
    nome = nome.strip(",.;")
    nome = re.sub(r"\s+", " ", nome)  # colapsa espaços duplos
    return nome.strip()


def limpar_valor_investimento(valor):
    """
    Converte texto tipo "R$ 1.300.000.000" ou
    "R$ 45.000,50" para float.
    Retorna 0.0 se não conseguir interpretar.
    """
    if valor is None:
        return 0.0

    # Já é número (int/float/numpy)
    if isinstance(valor, (int, float)):
        return float(valor)

    texto = str(valor).strip()
    if not texto:
        return 0.0

    # Remove "R$", espaços e qualquer caractere que não seja
    # dígito, ponto ou vírgula
    texto = re.sub(r"[^\d.,]", "", texto)

    if not texto:
        return 0.0

    # Formato brasileiro: ponto = milhar, vírgula = decimal
    # Ex: "1.300.000.000" -> 1300000000
    # Ex: "45.000,50"     -> 45000.50
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    else:
        texto = texto.replace(".", "")

    try:
        return float(texto)
    except ValueError:
        return 0.0


def limpar_ano(ano):
    """Garante que o ano seja um inteiro válido."""
    try:
        return int(float(ano))
    except (ValueError, TypeError):
        return None


def limpar_fonte_url(fonte):
    """Normaliza a URL/fonte, removendo espaços extras."""
    if not isinstance(fonte, str):
        return ""
    return fonte.strip()


# =====================================================
# IMPORTAÇÃO
# =====================================================

def importar_planilha(arquivo=ARQUIVO_PLANILHA):
    """
    Lê a planilha histórica e adiciona cada linha como
    investimento no banco, marcando a origem como 'historico'.
    """

    print("=" * 60)
    print("IMPORTADOR DE PLANILHA HISTÓRICA")
    print("=" * 60)

    try:
        df = pd.read_excel(arquivo)
    except Exception as erro:
        print(f"❌ Erro ao abrir a planilha: {erro}")
        return

    # Remove espaços extras dos nomes das colunas
    # (a planilha tem colunas como "Ano " ou "Empresa " com espaço no final)
    df.columns = [str(c).strip() for c in df.columns]

    print(f"✓ Planilha carregada: {len(df)} registros encontrados")
    print(f"  Colunas: {list(df.columns)}\n")

    banco = Banco()

    importados = 0
    ignorados = 0
    atualizados = 0

    for idx, linha in df.iterrows():
        ano = limpar_ano(linha.get("Ano"))
        empresa = limpar_nome_empresa(linha.get("Empresa"))
        valor = limpar_valor_investimento(linha.get("Investimento"))
        fonte = limpar_fonte_url(linha.get("Fonte"))

        # Linha inválida: sem empresa ou sem ano, pula
        if not empresa or ano is None:
            print(f"⚠️  Linha {idx + 2} ignorada (empresa ou ano ausente)")
            ignorados += 1
            continue

        existente = banco.procurar_investimento(empresa, ano)

        if existente:
            # Já existe: atualiza dados caso a planilha tenha
            # sido corrigida/atualizada, mas preserva o id
            existente["valor"] = valor
            existente["fonte"] = fonte
            existente["url"] = fonte
            existente["origem"] = "historico"
            atualizados += 1
        else:
            novo = banco.adicionar_investimento(
                empresa=empresa,
                ano=ano,
                valor=valor,
                fonte=fonte,
                url=fonte,
            )
            novo["origem"] = "historico"
            importados += 1

        # Garante que a empresa também exista no cadastro
        # de empresas monitoradas
        banco.adicionar_empresa(empresa)

    banco.salvar()

    print(f"\n✓ Novos investimentos importados: {importados}")
    print(f"✓ Investimentos já existentes atualizados: {atualizados}")
    print(f"⚠️  Linhas ignoradas (dados incompletos): {ignorados}")
    print("\n" + "=" * 60)
    print("IMPORTAÇÃO CONCLUÍDA")
    print("=" * 60)


if __name__ == "__main__":
    importar_planilha()
