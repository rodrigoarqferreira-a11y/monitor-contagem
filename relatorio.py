"""
====================================================

RELATORIO.PY

Gerador de Relatórios de Investimentos Privados
Monitor de Contagem

====================================================
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

from banco import Banco


class GeradorRelatorio:
    """
    Gera relatórios completos sobre investimentos
    detectados pelo monitor.
    """

    def __init__(self, banco: Banco = None):
        """Inicializa com dados do banco."""
        self.banco = banco or Banco()
        self.data_geracao = datetime.now()
        self.pasta_relatorios = Path("relatorios")
        self.pasta_relatorios.mkdir(exist_ok=True)

    # =====================================================
    # NÚMEROS PRINCIPAIS
    # =====================================================

    def calcular_resumo_executivo(self):
        """Calcula os números principais do relatório."""

        noticias = self.banco.noticias
        investimentos = self.banco.investimentos
        empresas = self.banco.empresas

        # Contar investimentos relevantes (mencionam Contagem)
        investimentos_relevantes = [
            inv for inv in investimentos
            if "id" in inv  # Tem ID válido
        ]

        # Extrair valores
        valores = []
        for noticia in noticias:
            if noticia.get("relevante") and noticia.get("valores"):
                for valor_str in noticia.get("valores", []):
                    # Tenta extrair número
                    try:
                        valor_limpo = valor_str.replace("R$", "").replace(",", ".").strip()
                        valor_num = float(valor_limpo.split()[0])
                        valores.append(valor_num)
                    except:
                        pass

        # Extrair empregos
        empregos_total = 0
        for noticia in noticias:
            if noticia.get("relevante") and noticia.get("empregos"):
                for emp_str in noticia.get("empregos", []):
                    try:
                        emp_num = int("".join(filter(str.isdigit, emp_str.split()[0])))
                        empregos_total += emp_num
                    except:
                        pass

        # Confiança média
        confiancas = [
            n.get("confianca", 0)
            for n in noticias
            if n.get("relevante")
        ]
        confianca_media = int(statistics.mean(confiancas)) if confiancas else 0

        valor_total = sum(valores) if valores else 0

        return {
            "investimentos_detectados": len(investimentos_relevantes),
            "empresas_monitoradas": len(empresas),
            "novos_empregos": empregos_total,
            "valor_total": valor_total,
            "confianca_media": confianca_media,
            "noticias_relevantes": len([n for n in noticias if n.get("relevante")]),
            "periodo": self._obter_periodo_noticias()
        }

    # =====================================================
    # INVESTIMENTOS POR FASE
    # =====================================================

    def investimentos_por_fase(self):
        """Agrupa investimentos por fase."""

        noticias = self.banco.noticias
        fases = defaultdict(list)

        for noticia in noticias:
            if noticia.get("relevante"):
                fase = noticia.get("fase", "Não identificada")
                fases[fase].append(noticia)

        return dict(fases)

    # =====================================================
    # RANKING DE EMPRESAS
    # =====================================================

    def ranking_empresas(self, top_n=10):
        """Retorna top N empresas com mais investimentos."""

        noticias = self.banco.noticias
        empresas_contagem = Counter()
        empresas_valor = defaultdict(float)
        empresas_empregos = defaultdict(int)

        for noticia in noticias:
            if noticia.get("relevante") and noticia.get("mencionou_contagem"):
                for empresa in noticia.get("empresas", []):
                    empresas_contagem[empresa] += 1

                    # Valor
                    if noticia.get("valores"):
                        for valor_str in noticia.get("valores"):
                            try:
                                valor = float(
                                    valor_str.replace("R$", "").split()[0]
                                )
                                empresas_valor[empresa] += valor
                            except:
                                pass

                    # Empregos
                    if noticia.get("empregos"):
                        for emp_str in noticia.get("empregos"):
                            try:
                                emp = int("".join(filter(str.isdigit, emp_str.split()[0])))
                                empresas_empregos[empresa] += emp
                            except:
                                pass

        # Montar ranking
        ranking = []
        for empresa, count in empresas_contagem.most_common(top_n):
            ranking.append({
                "empresa": empresa,
                "investimentos": count,
                "valor_total": empresas_valor.get(empresa, 0),
                "empregos": empresas_empregos.get(empresa, 0)
            })

        return ranking

    # =====================================================
    # EVOLUÇÃO TEMPORAL
    # =====================================================

    def evolucao_mensal(self):
        """Calcula evolução de investimentos por mês."""

        noticias = self.banco.noticias
        evolucao = defaultdict(lambda: {
            "investimentos": 0,
            "empregos": 0,
            "valor": 0
        })

        for noticia in noticias:
            if noticia.get("relevante") and noticia.get("mencionou_contagem"):

                # Extrair mês
                data_str = noticia.get("data", "")
                if data_str:
                    try:
                        # Supõe formato YYYY-MM-DD ou DD/MM/YYYY
                        if "-" in data_str:
                            mes = data_str[:7]  # YYYY-MM
                        else:
                            mes = data_str[-4:]  # Último ano
                    except:
                        mes = "Desconhecido"
                else:
                    mes = "Desconhecido"

                evolucao[mes]["investimentos"] += 1

                # Empregos
                if noticia.get("empregos"):
                    for emp_str in noticia.get("empregos"):
                        try:
                            emp = int("".join(filter(str.isdigit, emp_str.split()[0])))
                            evolucao[mes]["empregos"] += emp
                        except:
                            pass

                # Valor
                if noticia.get("valores"):
                    for val_str in noticia.get("valores"):
                        try:
                            val = float(val_str.replace("R$", "").split()[0])
                            evolucao[mes]["valor"] += val
                        except:
                            pass

        return dict(sorted(evolucao.items()))

    # =====================================================
    # ANÁLISE POR FONTE
    # =====================================================

    def analise_por_fonte(self):
        """Agrupa dados por fonte de notícia."""

        noticias = self.banco.noticias
        por_fonte = defaultdict(lambda: {
            "total": 0,
            "relevantes": 0,
            "confianca_media": []
        })

        for noticia in noticias:
            fonte = noticia.get("fonte", "Desconhecida")

            por_fonte[fonte]["total"] += 1

            if noticia.get("relevante"):
                por_fonte[fonte]["relevantes"] += 1

            confianca = noticia.get("confianca", 0)
            if confianca > 0:
                por_fonte[fonte]["confianca_media"].append(confianca)

        # Calcular média de confiança
        resultado = {}
        for fonte, dados in por_fonte.items():
            confiancas = dados["confianca_media"]
            resultado[fonte] = {
                "total": dados["total"],
                "relevantes": dados["relevantes"],
                "taxa_precisao": round(
                    (dados["relevantes"] / dados["total"] * 100)
                    if dados["total"] > 0 else 0,
                    1
                ),
                "confianca_media": round(
                    statistics.mean(confiancas)
                    if confiancas else 0,
                    1
                )
            }

        return resultado

    # =====================================================
    # NOTÍCIAS "QUASE RELEVANTES"
    # =====================================================

    def noticias_quase_relevantes(self):
        """
        Notícias com boa pontuação mas descartadas por
        não mencionarem Contagem.
        """

        noticias = self.banco.noticias
        quase = []

        for noticia in noticias:
            pontuacao_ok = noticia.get("pontuacao", 0) >= 30
            sem_contagem = not noticia.get("mencionou_contagem", False)

            if pontuacao_ok and sem_contagem and not noticia.get("relevante"):
                quase.append({
                    "titulo": noticia.get("titulo", ""),
                    "empresas": noticia.get("empresas", []),
                    "pontuacao": noticia.get("pontuacao", 0),
                    "fase": noticia.get("fase", ""),
                    "fonte": noticia.get("fonte", ""),
                    "url": noticia.get("url", "")
                })

        return sorted(quase, key=lambda x: x["pontuacao"], reverse=True)

    # =====================================================
    # CONFIANÇA DOS DADOS
    # =====================================================

    def analise_confianca(self):
        """Analisa distribuição de confiança dos dados."""

        noticias = [
            n for n in self.banco.noticias
            if n.get("relevante")
        ]
        confiancas = [n.get("confianca", 0) for n in noticias]

        if not confiancas:
            return {
                "alta": 0,
                "media": 0,
                "baixa": 0,
                "media_geral": 0
            }

        alta = len([c for c in confiancas if c >= 80])
        media = len([c for c in confiancas if 50 <= c < 80])
        baixa = len([c for c in confiancas if c < 50])
        total = alta + media + baixa

        return {
            "alta": round((alta / total * 100) if total > 0 else 0, 1),
            "media": round((media / total * 100) if total > 0 else 0, 1),
            "baixa": round((baixa / total * 100) if total > 0 else 0, 1),
            "media_geral": round(statistics.mean(confiancas), 1) if confiancas else 0
        }

    # =====================================================
    # HELPER: PERÍODO DE NOTICIAS
    # =====================================================

    def _obter_periodo_noticias(self):
        """Obtém período das notícias."""

        noticias = self.banco.noticias
        if not noticias:
            return "Período desconhecido"

        datas = [
            n.get("data", "")
            for n in noticias
            if n.get("data")
        ]

        if datas:
            return f"{min(datas)} a {max(datas)}"
        return "Período desconhecido"

    # =====================================================
    # GERAR RELATÓRIO TEXTO
    # =====================================================

    def gerar_relatorio_texto(self):
        """Gera relatório em formato texto."""

        resumo = self.calcular_resumo_executivo()
        fases = self.investimentos_por_fase()
        ranking = self.ranking_empresas()
        evolucao = self.evolucao_mensal()
        fontes = self.analise_por_fonte()
        quase_relevantes = self.noticias_quase_relevantes()
        confianca = self.analise_confianca()

        # =====================================================
        # CAPA
        # =====================================================

        texto = []
        texto.append("=" * 70)
        texto.append("RELATÓRIO DE INVESTIMENTOS PRIVADOS")
        texto.append("MONITOR DE CONTAGEM - MG")
        texto.append("=" * 70)
        texto.append(f"\nData de Geração: {self.data_geracao.strftime('%d/%m/%Y %H:%M')}")
        texto.append(f"Período: {resumo['periodo']}\n")

        # =====================================================
        # SUMÁRIO EXECUTIVO
        # =====================================================

        texto.append("\n" + "=" * 70)
        texto.append("SUMÁRIO EXECUTIVO")
        texto.append("=" * 70)
        texto.append(f"\n┌─────────────────────────────────────────┐")
        texto.append(f"│ NÚMEROS PRINCIPAIS                      │")
        texto.append(f"├─────────────────────────────────────────┤")
        texto.append(f"│ Investimentos detectados..: {resumo['investimentos_detectados']:>10}  │")
        texto.append(f"│ Empresas monitoradas.....: {resumo['empresas_monitoradas']:>10}  │")
        texto.append(f"│ Novos empregos gerados..: {resumo['novos_empregos']:>10}  │")
        texto.append(f"│ Valor total anunciado...: R$ {resumo['valor_total']/1e9:>7.2f} bi │")
        texto.append(f"│ Notícias relevantes.....: {resumo['noticias_relevantes']:>10}  │")
        texto.append(f"│ Confiança média.........: {resumo['confianca_media']:>9}%  │")
        texto.append(f"└─────────────────────────────────────────┘")

        # =====================================================
        # INVESTIMENTOS POR FASE
        # =====================================================

        texto.append("\n" + "=" * 70)
        texto.append("INVESTIMENTOS POR FASE")
        texto.append("=" * 70)

        for fase, noticias_fase in sorted(fases.items()):
            barra = "█" * len(noticias_fase)
            texto.append(f"\n{fase:<20} {barra} ({len(noticias_fase)})")

        # =====================================================
        # RANKING DE EMPRESAS
        # =====================================================

        texto.append("\n" + "=" * 70)
        texto.append("TOP 10 EMPRESAS")
        texto.append("=" * 70)
        texto.append("\n{:<5} {:<30} {:<15} {:<15} {:<12} {:<15}".format(
            "Rank", "Empresa", "Investimentos", "Valor (R$ M)", "Empregos", "Confiança"
        ))
        texto.append("-" * 70)

        for idx, emp in enumerate(ranking, 1):
            valor_m = emp["valor_total"] / 1e6 if emp["valor_total"] > 0 else 0
            texto.append("{:<5} {:<30} {:<15} {:<15.1f} {:<12} {:<15}".format(
                str(idx),
                emp["empresa"][:28],
                str(emp["investimentos"]),
                valor_m,
                str(emp["empregos"]),
                "-"
            ))

        # =====================================================
        # EVOLUÇÃO MENSAL
        # =====================================================

        texto.append("\n" + "=" * 70)
        texto.append("EVOLUÇÃO TEMPORAL (ÚLTIMOS MESES)")
        texto.append("=" * 70)
        texto.append("\n{:<15} {:<20} {:<15} {:<15}".format(
            "Período", "Investimentos", "Empregos", "Valor (R$ M)"
        ))
        texto.append("-" * 70)

        for periodo, dados in evolucao.items():
            valor_m = dados["valor"] / 1e6 if dados["valor"] > 0 else 0
            texto.append("{:<15} {:<20} {:<15} {:<15.1f}".format(
                str(periodo),
                str(dados["investimentos"]),
                str(dados["empregos"]),
                valor_m
            ))

        # =====================================================
        # ANÁLISE POR FONTE
        # =====================================================

        texto.append("\n" + "=" * 70)
        texto.append("FONTES MONITORADAS")
        texto.append("=" * 70)
        texto.append("\n{:<25} {:<12} {:<15} {:<20} {:<15}".format(
            "Fonte", "Total", "Relevantes", "Taxa Precisão", "Confiança %"
        ))
        texto.append("-" * 70)

        total_geral = 0
        relevantes_geral = 0

        for fonte in sorted(fontes.keys()):
            dados = fontes[fonte]
            total_geral += dados["total"]
            relevantes_geral += dados["relevantes"]

            texto.append("{:<25} {:<12} {:<15} {:<19}% {:<14.1f}%".format(
                fonte[:23],
                str(dados["total"]),
                str(dados["relevantes"]),
                str(dados["taxa_precisao"]),
                dados["confianca_media"]
            ))

        texto.append("-" * 70)
        taxa_geral = round(
            (relevantes_geral / total_geral * 100) if total_geral > 0 else 0,
            1
        )
        texto.append("{:<25} {:<12} {:<15} {:<19}%".format(
            "TOTAL",
            str(total_geral),
            str(relevantes_geral),
            str(taxa_geral)
        ))

        # =====================================================
        # CONFIANÇA DOS DADOS
        # =====================================================

        texto.append("\n" + "=" * 70)
        texto.append("ANÁLISE DE CONFIANÇA")
        texto.append("=" * 70)
        texto.append(f"\nConfiança média geral: {confianca['media_geral']}%")
        texto.append(f"\nDistribuição:")
        texto.append(f"  Alta (80-100%)........: {confianca['alta']}%")
        texto.append(f"  Média (50-80%)........: {confianca['media']}%")
        texto.append(f"  Baixa (< 50%).........: {confianca['baixa']}%")

        # =====================================================
        # NOTÍCIAS "QUASE RELEVANTES"
        # =====================================================

        if quase_relevantes:
            texto.append("\n" + "=" * 70)
            texto.append("NOTÍCIAS 'QUASE RELEVANTES'")
            texto.append("=" * 70)
            texto.append("\nNotícias com boa pontuação mas fora de Contagem:")
            texto.append("(Potencial impacto regional)\n")

            for noticia in quase_relevantes[:5]:
                texto.append(f"\n• {noticia['titulo']}")
                if noticia['empresas']:
                    texto.append(f"  Empresa(s): {', '.join(noticia['empresas'])}")
                texto.append(f"  Pontuação: {noticia['pontuacao']}")
                texto.append(f"  Fase: {noticia['fase']}")
                texto.append(f"  URL: {noticia['url']}")

        # =====================================================
        # RODAPÉ
        # =====================================================

        texto.append("\n" + "=" * 70)
        texto.append("NOTAS FINAIS")
        texto.append("=" * 70)
        texto.append(f"\nData de geração: {self.data_geracao.strftime('%d/%m/%Y %H:%M')}")
        texto.append("Período de coleta: Últimos 30 dias")
        texto.append("\nCritérios de relevância:")
        texto.append("  ✓ Pontuação mínima: 30 pontos")
        texto.append("  ✓ Deve mencionar 'Contagem' explicitamente")
        texto.append("  ✓ Identificar ao menos uma empresa monitorada")

        return "\n".join(texto)

    # =====================================================
    # SALVAR RELATÓRIO
    # =====================================================

    def salvar_relatorio_texto(self):
        """Salva relatório em arquivo TXT."""

        relatorio = self.gerar_relatorio_texto()

        nome_arquivo = (
            self.pasta_relatorios /
            f"relatorio_{self.data_geracao.strftime('%Y%m%d_%H%M%S')}.txt"
        )

        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write(relatorio)

        return nome_arquivo

    def salvar_relatorio_json(self):
        """Salva dados do relatório em JSON."""

        dados = {
            "data_geracao": self.data_geracao.isoformat(),
            "resumo_executivo": self.calcular_resumo_executivo(),
            "investimentos_por_fase": self.investimentos_por_fase(),
            "ranking_empresas": self.ranking_empresas(),
            "evolucao_mensal": self.evolucao_mensal(),
            "analise_por_fonte": self.analise_por_fonte(),
            "noticias_quase_relevantes": self.noticias_quase_relevantes(),
            "analise_confianca": self.analise_confianca()
        }

        nome_arquivo = (
            self.pasta_relatorios /
            f"relatorio_{self.data_geracao.strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(nome_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

        return nome_arquivo

    # =====================================================
    # IMPRIMIR RELATÓRIO
    # =====================================================

    def imprimir_relatorio(self):
        """Imprime relatório no console."""
        print(self.gerar_relatorio_texto())


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("GERADOR DE RELATÓRIOS")
    print("=" * 70 + "\n")

    banco = Banco()

    gerador = GeradorRelatorio(banco)

    # Imprimir no console
    gerador.imprimir_relatorio()

    # Salvar arquivos
    print("\n" + "=" * 70)
    print("SALVANDO RELATÓRIOS...")
    print("=" * 70)

    txt_path = gerador.salvar_relatorio_texto()
    print(f"✓ Relatório TXT: {txt_path}")

    json_path = gerador.salvar_relatorio_json()
    print(f"✓ Relatório JSON: {json_path}")

    print("\n✓ Relatórios gerados com sucesso!")
