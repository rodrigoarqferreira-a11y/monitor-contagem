import pandas as pd

arquivo = "dados/Investimentos Privados em Contagem 2021-2026.xlsx"

try:
    df = pd.read_excel(arquivo)

    print("Planilha carregada com sucesso!")

    print(f"Total de registros: {len(df)}")

    print("\nColunas encontradas:")

    for coluna in df.columns:
        print("-", coluna)

except Exception as erro:
    print("Erro ao abrir a planilha:")
    print(erro)
