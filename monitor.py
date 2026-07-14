"""
=====================================================

MONITOR DE INVESTIMENTOS PRIVADOS

CONTAGEM - MG

Arquivo principal do sistema.

=====================================================
"""

from crawler import executar
from analisador import processar
from intel import analisar_inteligencia
from datetime import datetime


def main():

    print()
    print("=" * 70)
    print("MONITOR DE INVESTIMENTOS PRIVADOS")
    print(
        f"Execução: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    )
    print("=" * 70)

    try:

        noticias = executar()

    except Exception as erro:

        import traceback
        traceback.print_exc()

        print()
        print("Erro no monitor:")
        print(erro)

        return

    print()
    print(f"{len(noticias)} notícias encontradas.")
    print()

    relevantes = 0

    # ---------------------------------------------
    # Lista de notícias "quase relevantes":
    # pontuação boa, mas descartadas só por não
    # mencionarem Contagem (ex: notícias sobre
    # Betim, BH, etc. que citam empresas monitoradas)
    # ---------------------------------------------

    quase_relevantes = []

    for noticia in noticias:

        noticia = processar(noticia)

        if noticia.relevante:

            inteligencia = analisar_inteligencia(noticia)

            relevantes += 1

            print("-" * 70)
            print(noticia.titulo)
            print()

            print("Empresa(s):")

            if noticia.empresas:

                for empresa in noticia.empresas:

                    print(" •", empresa)

            else:

                print(" • Não identificada")

            print()

            print("Fase:", noticia.fase)
            print("Status:", inteligencia["status"])

            print(
                "Classificação:",
                inteligencia["classificacao"]
            )

            print(
                "Confiança:",
                inteligencia["confianca"],
                "%"
            )

            print(
                "Estrelas:",
                inteligencia["estrelas"]
            )

            print(
                "Pontuação:",
                noticia.pontuacao
            )

            if noticia.valores:

                print(
                    "Valor:",
                    ", ".join(noticia.valores)
                )

            if noticia.empregos:

                print(
                    "Empregos:",
                    ", ".join(noticia.empregos)
                )

            print("Fonte:", noticia.fonte)
            print("URL:", noticia.url)
            print("-" * 70)
            print()

        else:

            # Notícia descartada. Verifica se seria
            # relevante apenas pela pontuação, mas
            # não mencionou Contagem — vale a pena
            # ficar de olho nessas, sem salvar no banco.

            pontuacao_ok = (
                noticia.pontuacao >= 30
            )

            sem_contagem = (
                not getattr(noticia, "mencionou_contagem", True)
            )

            if pontuacao_ok and sem_contagem:

                quase_relevantes.append(noticia)

    print()
    print("=" * 70)
    print("RESUMO FINAL")
    print("=" * 70)

    print(
        f"Total de notícias........: {len(noticias)}"
    )

    print(
        f"Notícias relevantes......: {relevantes}"
    )

    print(
        f"Notícias descartadas.....: {len(noticias)-relevantes}"
    )

    print()

    # ---------------------------------------------
    # Seção extra: quase relevantes
    # ---------------------------------------------

    if quase_relevantes:

        print("-" * 70)
        print(
            f"Descartadas por falta de menção a Contagem: "
            f"{len(quase_relevantes)}"
        )
        print(
            "(pontuação boa, mas fala de outra cidade "
            "ou não menciona Contagem)"
        )
        print("-" * 70)

        for noticia in quase_relevantes:

            print()
            print(" •", noticia.titulo)

            if noticia.empresas:

                print(
                    "   Empresa(s):",
                    ", ".join(noticia.empresas)
                )

            print("   Pontuação:", noticia.pontuacao)
            print("   Fase:", noticia.fase)
            print("   URL:", noticia.url)

        print()

    else:

        print(
            "Nenhuma notícia 'quase relevante' "
            "encontrada hoje."
        )
# DEPOIS — salva o banco e dispara o gerador de relatório:
    from banco import Banco
    from relatorio import GeradorRelatorio   # ajuste o nome da classe se diferente

    banco = Banco()
    # (opcional) salvar notícias novas no banco antes do relatório:
    for noticia in noticias:
        if noticia.relevante:
            banco.adicionar_noticia(noticia)
    banco.salvar()

    print()
    print("Gerando relatórios...")
    gerador = GeradorRelatorio(banco)
    gerador.gerar_todos()

    print()
    print("Monitoramento concluído.")

if __name__ == "__main__":
    main()
