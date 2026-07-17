"""
=====================================================
MONITOR.PY
Monitor de Investimentos Privados — Contagem MG
=====================================================
"""

from crawler import executar
from analisador import processar
from intel import analisar_inteligencia
from relatorio import GeradorRelatorio
from banco import Banco
from datetime import datetime


def main():

    print()
    print("=" * 70)
    print("MONITOR DE INVESTIMENTOS PRIVADOS")
    print(f"Execução: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 70)

    # ── coleta ───────────────────────────────────────

    try:
        noticias = executar()
    except Exception as erro:
        import traceback
        traceback.print_exc()
        print("\nErro no crawler:", erro)
        return

    print(f"\n{len(noticias)} notícias encontradas.\n")

    # ── análise ──────────────────────────────────────

    relevantes    = 0
    quase_rel     = []

    for noticia in noticias:

        noticia = processar(noticia)

        if noticia.relevante:

            inteligencia = analisar_inteligencia(noticia)
            relevantes  += 1

            print("-" * 70)
            print(noticia.titulo)
            print()
            print("Empresa(s):")
            for emp in (noticia.empresas or ["Não identificada"]):
                print(" •", emp)
            print()
            print("Fase        :", noticia.fase)
            print("Status      :", inteligencia["status"])
            print("Classificação:", inteligencia["classificacao"])
            print("Confiança   :", inteligencia["confianca"], "%")
            print("Estrelas    :", inteligencia["estrelas"])
            print("Pontuação   :", noticia.pontuacao)
            if noticia.valores:
                print("Valor       :", ", ".join(noticia.valores))
            if noticia.empregos:
                print("Empregos    :", ", ".join(noticia.empregos))
            print("Fonte       :", noticia.fonte)
            print("URL         :", noticia.url)
            print("-" * 70)
            print()

        else:
            # guarda "quase relevantes" para o resumo
            if (getattr(noticia, "pontuacao", 0) >= 30
                    and not getattr(noticia, "mencionou_contagem", True)):
                quase_rel.append(noticia)

    # ── resumo no console ────────────────────────────

    print()
    print("=" * 70)
    print("RESUMO FINAL")
    print("=" * 70)
    print(f"Total de notícias........: {len(noticias)}")
    print(f"Notícias relevantes......: {relevantes}")
    print(f"Notícias descartadas.....: {len(noticias) - relevantes}")

    if quase_rel:
        print()
        print(f"Quase relevantes (boa pontuação, fora de Contagem): {len(quase_rel)}")
        for n in quase_rel:
            print(f"  • {n.titulo}")
            print(f"    Pontos: {n.pontuacao} | Fase: {n.fase} | URL: {n.url}")

    print()

    # ── gerar relatórios ─────────────────────────────
    # Lê o banco que acabou de ser atualizado pelo
    # processar() → analisador.py → salvar_noticia()
    # e gera todos os formatos (TXT, JSON, HTML, PDF).

    print("=" * 70)
    print("GERANDO RELATÓRIOS")
    print("=" * 70)

    try:
        banco   = Banco()
        gerador = GeradorRelatorio(banco)
        arquivos = gerador.gerar_todos()
        print(f"\n{len(arquivos)} arquivo(s) gerado(s) em /relatorios/")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nErro ao gerar relatórios: {e}")

    print()
    print("Monitoramento concluído.")


if __name__ == "__main__":
    main()
