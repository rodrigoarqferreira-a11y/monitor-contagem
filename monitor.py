"""
=====================================================

MONITOR DE INVESTIMENTOS PRIVADOS
CONTAGEM - MG

Arquivo principal do sistema.

=====================================================
"""

from crawler import executar
from analisador import processar
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

        print()
        print("Erro no monitor:")
        print(erro)
        return


    print()
    print(f"{len(noticias)} notícias encontradas.")
    print()


    relevantes = 0


    for noticia in noticias:

        noticia = processar(noticia)


        if noticia.relevante:

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

            print("Pontuação:", noticia.pontuacao)


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

    print("Monitoramento concluído.")



if __name__ == "__main__":

    main()
