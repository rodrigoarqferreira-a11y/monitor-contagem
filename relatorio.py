"""
====================================================

RELATORIO.PY

Gerador de Relatórios de Investimentos Privados
Monitor de Contagem

Formatos suportados:
- TXT (texto puro)
- JSON (dados estruturados)
- PDF (documento formatado)
- HTML (painel web)
- Gráficos (PNG/SVG)

====================================================
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
from io import BytesIO

from banco import Banco

# =====================================================
# IMPORTAÇÕES CONDICIONAIS
# =====================================================

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
        PageBreak, Image as RLImage
    )
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Backend sem GUI
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False


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
    # DADOS HISTÓRICOS (para a aba Histórico)
    # =====================================================

    def dados_historico_completo(self):
        """
        Monta a estrutura completa de dados históricos,
        pronta para ser embutida como JSON no HTML e
        manipulada em JavaScript pelos filtros.
        """

        investimentos = self.banco.investimentos

        registros = []
        for inv in investimentos:
            registros.append({
                "empresa": inv.get("empresa", ""),
                "ano": inv.get("ano"),
                "valor": inv.get("valor", 0),
                "fonte": inv.get("fonte", ""),
                "url": inv.get("url", ""),
                "fase": inv.get("fase", "Anunciado"),
                "origem": inv.get("origem", "monitoramento"),
            })

        return registros

    def resumo_historico_por_ano(self):
        """
        Totais agregados por ano: total investido,
        número de investimentos, número de empresas únicas.
        """

        investimentos = self.banco.investimentos
        por_ano = {}

        for inv in investimentos:
            ano = inv.get("ano")
            if ano is None:
                continue

            if ano not in por_ano:
                por_ano[ano] = {
                    "ano": ano,
                    "total_investido": 0,
                    "num_investimentos": 0,
                    "empresas": set(),
                }

            por_ano[ano]["total_investido"] += inv.get("valor", 0)
            por_ano[ano]["num_investimentos"] += 1
            por_ano[ano]["empresas"].add(inv.get("empresa", ""))

        resultado = []
        for ano in sorted(por_ano.keys()):
            dados = por_ano[ano]
            resultado.append({
                "ano": dados["ano"],
                "total_investido": dados["total_investido"],
                "num_investimentos": dados["num_investimentos"],
                "num_empresas": len(dados["empresas"]),
            })

        return resultado

    def ranking_empresas_historico(self, ano=None):
        """
        Ranking de empresas por valor total investido,
        somando todos os anos (base histórica).
        Se 'ano' for informado, filtra apenas aquele ano.
        """

        investimentos = self.banco.investimentos
        valores_por_empresa = {}

        for inv in investimentos:
            if ano is not None and inv.get("ano") != ano:
                continue

            empresa = inv.get("empresa", "")
            if not empresa:
                continue

            if empresa not in valores_por_empresa:
                valores_por_empresa[empresa] = {
                    "empresa": empresa,
                    "valor_total": 0,
                    "num_investimentos": 0,
                }

            valores_por_empresa[empresa]["valor_total"] += inv.get("valor", 0)
            valores_por_empresa[empresa]["num_investimentos"] += 1

        ranking = sorted(
            valores_por_empresa.values(),
            key=lambda x: x["valor_total"],
            reverse=True
        )

        return ranking

    def totais_gerais_historico(self):
        """Números consolidados de toda a base histórica."""

        investimentos = self.banco.investimentos

        if not investimentos:
            return {
                "total_investido": 0,
                "num_investimentos": 0,
                "num_empresas": 0,
                "ano_min": None,
                "ano_max": None,
            }

        empresas = set(inv.get("empresa", "") for inv in investimentos)
        anos = [inv.get("ano") for inv in investimentos if inv.get("ano") is not None]

        return {
            "total_investido": sum(inv.get("valor", 0) for inv in investimentos),
            "num_investimentos": len(investimentos),
            "num_empresas": len(empresas),
            "ano_min": min(anos) if anos else None,
            "ano_max": max(anos) if anos else None,
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
    # GERAR GRÁFICOS
    # =====================================================

    def gerar_graficos(self):
        """Gera gráficos em matplotlib e plotly."""

        if not HAS_MATPLOTLIB and not HAS_PLOTLY:
            print("⚠️  Matplotlib ou Plotly não instalados. Pulando gráficos.")
            return []

        arquivos_gerados = []

        try:
            fases = self.investimentos_por_fase()
            ranking = self.ranking_empresas(10)
            evolucao = self.evolucao_mensal()
            confianca = self.analise_confianca()

            # =====================================================
            # GRÁFICO 1: INVESTIMENTOS POR FASE
            # =====================================================

            if HAS_MATPLOTLIB:
                fig, ax = plt.subplots(figsize=(12, 6))

                fases_nomes = list(fases.keys())
                fases_contagem = [len(fases[f]) for f in fases_nomes]

                colors_fase = plt.cm.Set3(range(len(fases_nomes)))
                ax.barh(fases_nomes, fases_contagem, color=colors_fase)
                ax.set_xlabel("Número de Investimentos", fontsize=12)
                ax.set_title("Investimentos por Fase", fontsize=14, fontweight='bold')
                ax.grid(axis='x', alpha=0.3)

                for i, v in enumerate(fases_contagem):
                    ax.text(v + 0.1, i, str(v), va='center', fontweight='bold')

                plt.tight_layout()
                arquivo = self.pasta_relatorios / "grafico_fases.png"
                plt.savefig(arquivo, dpi=300, bbox_inches='tight')
                plt.close()
                arquivos_gerados.append(arquivo)
                print(f"✓ Gráfico: {arquivo}")

            # =====================================================
            # GRÁFICO 2: TOP 10 EMPRESAS
            # =====================================================

            if HAS_MATPLOTLIB:
                fig, ax = plt.subplots(figsize=(12, 8))

                empresas_nomes = [e["empresa"] for e in ranking]
                empresas_count = [e["investimentos"] for e in ranking]

                colors_emp = plt.cm.viridis(range(len(empresas_nomes)))
                ax.barh(empresas_nomes, empresas_count, color=colors_emp)
                ax.set_xlabel("Número de Investimentos", fontsize=12)
                ax.set_title("Top 10 Empresas com Mais Investimentos", fontsize=14, fontweight='bold')
                ax.grid(axis='x', alpha=0.3)

                for i, v in enumerate(empresas_count):
                    ax.text(v + 0.1, i, str(v), va='center', fontweight='bold')

                plt.tight_layout()
                arquivo = self.pasta_relatorios / "grafico_empresas.png"
                plt.savefig(arquivo, dpi=300, bbox_inches='tight')
                plt.close()
                arquivos_gerados.append(arquivo)
                print(f"✓ Gráfico: {arquivo}")

            # =====================================================
            # GRÁFICO 3: EVOLUÇÃO TEMPORAL
            # =====================================================

            if HAS_MATPLOTLIB:
                fig, ax = plt.subplots(figsize=(14, 6))

                periodos = list(evolucao.keys())
                investimentos = [evolucao[p]["investimentos"] for p in periodos]

                ax.plot(periodos, investimentos, marker='o', linewidth=2, markersize=8, color='#2E86AB')
                ax.fill_between(range(len(periodos)), investimentos, alpha=0.3, color='#2E86AB')
                ax.set_xlabel("Período", fontsize=12)
                ax.set_ylabel("Número de Investimentos", fontsize=12)
                ax.set_title("Evolução de Investimentos ao Longo do Tempo", fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3)
                plt.xticks(rotation=45, ha='right')

                plt.tight_layout()
                arquivo = self.pasta_relatorios / "grafico_evolucao.png"
                plt.savefig(arquivo, dpi=300, bbox_inches='tight')
                plt.close()
                arquivos_gerados.append(arquivo)
                print(f"✓ Gráfico: {arquivo}")

            # =====================================================
            # GRÁFICO 4: CONFIANÇA (PIE CHART)
            # =====================================================

            if HAS_MATPLOTLIB:
                fig, ax = plt.subplots(figsize=(10, 8))

                tamanhos = [confianca['alta'], confianca['media'], confianca['baixa']]

                if sum(tamanhos) == 0:
                    ax.text(
                        0.5, 0.5, "Sem dados ainda",
                        ha='center', va='center',
                        fontsize=14, color='gray',
                        transform=ax.transAxes
                    )
                    ax.axis('off')
                else:
                    rotulos = [
                         f"Alta (80-100%)\n{confianca['alta']}%",
                         f"Média (50-80%)\n{confianca['media']}%",
                         f"Baixa (<50%)\n{confianca['baixa']}%"
                    ]
                    cores = ['#90EE90', '#FFD700', '#FF6B6B']

                    wedges, texts, autotexts = ax.pie(
                         tamanhos,
                         labels=rotulos,
                         colors=cores,
                         autopct='',
                         startangle=90,
                         textprops={'fontsize': 11, 'fontweight': 'bold'}
                    )

                ax.set_title(f"Distribuição de Confiança\nMédia Geral: {confianca['media_geral']}%",
                           fontsize=14, fontweight='bold')

                plt.tight_layout()
                arquivo = self.pasta_relatorios / "grafico_confianca.png"
                plt.savefig(arquivo, dpi=300, bbox_inches='tight')
                plt.close()
                arquivos_gerados.append(arquivo)
                print(f"✓ Gráfico: {arquivo}")

        except Exception as e:
            print(f"❌ Erro ao gerar gráficos: {e}")

        return arquivos_gerados

    # =====================================================
    # GERAR HTML
    # =====================================================

    def gerar_html(self):
        """Gera painel interativo em HTML."""

        resumo = self.calcular_resumo_executivo()
        fases = self.investimentos_por_fase()
        ranking = self.ranking_empresas()
        evolucao = self.evolucao_mensal()
        fontes = self.analise_por_fonte()
        confianca = self.analise_confianca()

        # Dados para gráficos
        fases_labels = list(fases.keys())
        fases_data = [len(fases[f]) for f in fases_labels]

        empresas_labels = [e["empresa"] for e in ranking]
        empresas_data = [e["investimentos"] for e in ranking]

        periodos = list(evolucao.keys())
        investimentos_data = [evolucao[p]["investimentos"] for p in periodos]

        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Investimentos - Contagem</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .content {{
            padding: 40px;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
        }}

        .summary-card h3 {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}

        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
        }}

        .section {{
            margin-bottom: 40px;
        }}

        .section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}

        .chart-container {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        table th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}

        table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }}

        table tr:hover {{
            background: #f5f5f5;
        }}

        table tr:nth-child(even) {{
            background: #f9f9f9;
        }}

        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e0e0e0;
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}

            .summary {{
                grid-template-columns: 1fr;
            }}

            .content {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Monitor de Investimentos Privados</h1>
            <p>Contagem - MG | Relatório gerado em {self.data_geracao.strftime('%d/%m/%Y %H:%M')}</p>
        </div>

        <div class="content">
            <!-- SUMÁRIO EXECUTIVO -->
            <div class="summary">
                <div class="summary-card">
                    <h3>Investimentos Detectados</h3>
                    <div class="value">{resumo['investimentos_detectados']}</div>
                </div>
                <div class="summary-card">
                    <h3>Empresas Monitoradas</h3>
                    <div class="value">{resumo['empresas_monitoradas']}</div>
                </div>
                <div class="summary-card">
                    <h3>Novos Empregos</h3>
                    <div class="value">{resumo['novos_empregos']:,}</div>
                </div>
                <div class="summary-card">
                    <h3>Valor Total</h3>
                    <div class="value">R$ {resumo['valor_total']/1e9:.2f}B</div>
                </div>
                <div class="summary-card">
                    <h3>Confiança Média</h3>
                    <div class="value">{resumo['confianca_media']}%</div>
                </div>
                <div class="summary-card">
                    <h3>Notícias Relevantes</h3>
                    <div class="value">{resumo['noticias_relevantes']}</div>
                </div>
            </div>

            <!-- INVESTIMENTOS POR FASE -->
            <div class="section">
                <h2>📈 Investimentos por Fase</h2>
                <div class="chart-container" id="chart-fases"></div>
                <script>
                    var data_fases = [{{
                        x: {fases_data},
                        y: {fases_labels},
                        type: 'bar',
                        orientation: 'h',
                        marker: {{color: '#667eea'}}
                    }}];
                    var layout_fases = {{
                        title: 'Distribuição por Fase do Investimento',
                        xaxis: {{title: 'Quantidade'}},
                        margin: {{l: 150}}
                    }};
                    Plotly.newPlot('chart-fases', data_fases, layout_fases, {{responsive: true}});
                </script>
            </div>

            <!-- TOP 10 EMPRESAS -->
            <div class="section">
                <h2>🏢 Top 10 Empresas</h2>
                <div class="chart-container" id="chart-empresas"></div>
                <script>
                    var data_empresas = [{{
                        x: {empresas_data},
                        y: {empresas_labels},
                        type: 'bar',
                        orientation: 'h',
                        marker: {{color: '#764ba2'}}
                    }}];
                    var layout_empresas = {{
                        title: 'Empresas com Mais Investimentos',
                        xaxis: {{title: 'Quantidade'}},
                        margin: {{l: 200}}
                    }};
                    Plotly.newPlot('chart-empresas', data_empresas, layout_empresas, {{responsive: true}});
                </script>
            </div>

            <!-- EVOLUÇÃO TEMPORAL -->
            <div class="section">
                <h2>📅 Evolução Temporal</h2>
                <div class="chart-container" id="chart-evolucao"></div>
                <script>
                    var data_evolucao = [{{
                        x: {periodos},
                        y: {investimentos_data},
                        type: 'scatter',
                        mode: 'lines+markers',
                        line: {{color: '#667eea', width: 3}},
                        marker: {{size: 8}}
                    }}];
                    var layout_evolucao = {{
                        title: 'Evolução de Investimentos',
                        xaxis: {{title: 'Período'}},
                        yaxis: {{title: 'Quantidade'}},
                        hovermode: 'closest'
                    }};
                    Plotly.newPlot('chart-evolucao', data_evolucao, layout_evolucao, {{responsive: true}});
                </script>
            </div>

            <!-- ANÁLISE POR FONTE -->
            <div class="section">
                <h2>📰 Fontes Monitoradas</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Fonte</th>
                            <th>Total</th>
                            <th>Relevantes</th>
                            <th>Taxa de Precisão</th>
                            <th>Confiança Média</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        for fonte in sorted(fontes.keys()):
            dados = fontes[fonte]
            html += f"""
                        <tr>
                            <td>{fonte}</td>
                            <td>{dados['total']}</td>
                            <td>{dados['relevantes']}</td>
                            <td>{dados['taxa_precisao']}%</td>
                            <td>{dados['confianca_media']}%</td>
                        </tr>
            """

        html += """
                    </tbody>
                </table>
            </div>

            <!-- CONFIANÇA -->
            <div class="section">
            <!-- CONFIANÇA -->
            <div class="section">
                <h2>✅ Análise de Confiança</h2>
                <div class="chart-container" id="chart-confianca"></div>
                <script>
                    var data_confianca = [{{
                        values: [{confianca['alta']}, {confianca['media']}, {confianca['baixa']}],
                        labels: ['Alta (80-100%)', 'Média (50-80%)', 'Baixa (<50%)'],
                        type: 'pie',
                        marker: {{colors: ['#90EE90', '#FFD700', '#FF6B6B']}}
                    }}];
                    var layout_confianca = {{
                        title: 'Distribuição de Confiança dos Dados'
                    }};
                    Plotly.newPlot('chart-confianca', data_confianca, layout_confianca, {{responsive: true}});
                </script>
            </div>
        </div>

        <div class="footer">
            <p>Relatório gerado pelo Monitor de Investimentos Privados de Contagem</p>
            <p>Período: {resumo['periodo']}</p>
        </div>
    </div>
</body>
</html>
        """

        return html

    # =====================================================
    # GERAR PDF
    # =====================================================

    def gerar_pdf(self):
        """Gera relatório em PDF usando ReportLab."""

        if not HAS_REPORTLAB:
            print("⚠️  ReportLab não instalado. Pulando PDF.")
            return None

        try:
            resumo = self.calcular_resumo_executivo()
            ranking = self.ranking_empresas()
            fases = self.investimentos_por_fase()
            fontes = self.analise_por_fonte()

            nome_arquivo = (
                self.pasta_relatorios /
                f"relatorio_{self.data_geracao.strftime('%Y%m%d_%H%M%S')}.pdf"
            )

            doc = SimpleDocTemplate(
                str(nome_arquivo),
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch,
            )

            story = []
            styles = getSampleStyleSheet()

            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#667eea'),
                spaceAfter=10,
                alignment=1
            )
            story.append(Paragraph("Monitor de Investimentos Privados", title_style))
            story.append(Paragraph("Contagem - MG", styles['Normal']))
            story.append(Spacer(1, 0.3*inch))

            # Data
            story.append(Paragraph(
                f"Data de Geração: {self.data_geracao.strftime('%d/%m/%Y %H:%M')}",
                styles['Normal']
            ))
            story.append(Spacer(1, 0.2*inch))

            # Resumo
            story.append(Paragraph("SUMÁRIO EXECUTIVO", styles['Heading2']))

            resumo_data = [
                ["Investimentos detectados", str(resumo['investimentos_detectados'])],
                ["Empresas monitoradas", str(resumo['empresas_monitoradas'])],
                ["Novos empregos", f"{resumo['novos_empregos']:,}"],
                ["Valor total", f"R$ {resumo['valor_total']/1e9:.2f}B"],
                ["Confiança média", f"{resumo['confianca_media']}%"],
                ["Notícias relevantes", str(resumo['noticias_relevantes'])],
            ]

            resumo_table = Table(resumo_data)
            resumo_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))

            story.append(resumo_table)
            story.append(Spacer(1, 0.3*inch))

            # Top 10 Empresas
            story.append(Paragraph("TOP 10 EMPRESAS", styles['Heading2']))

            ranking_data = [["Rank", "Empresa", "Investimentos", "Valor (R$M)", "Empregos"]]
            for idx, emp in enumerate(ranking, 1):
                valor_m = emp["valor_total"] / 1e6 if emp["valor_total"] > 0 else 0
                ranking_data.append([
                    str(idx),
                    emp["empresa"][:25],
                    str(emp["investimentos"]),
                    f"{valor_m:.1f}",
                    str(emp["empregos"])
                ])

            ranking_table = Table(ranking_data)
            estilos_ranking = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]

            # Zebra striping manual (substitui o ROWBACKGROUNDS inválido)
            for i in range(1, len(ranking_data)):
                cor = colors.white if i % 2 == 1 else colors.HexColor('#f9f9f9')
                estilos_ranking.append(('BACKGROUND', (0, i), (-1, i), cor))

            ranking_table.setStyle(TableStyle(estilos_ranking))

            story.append(ranking_table)

            # Construir PDF
            doc.build(story)
            return nome_arquivo

        except Exception as e:
            print(f"❌ Erro ao gerar PDF: {e}")
            return None

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

    def salvar_relatorio_html(self):
        """Salva relatório em HTML."""

        html = self.gerar_html()

        nome_arquivo = (
            self.pasta_relatorios /
            f"relatorio_{self.data_geracao.strftime('%Y%m%d_%H%M%S')}.html"
        )

        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write(html)

        # Salva também uma cópia fixa, sempre com o mesmo nome,
        # para manter uma URL estável no GitHub Pages
        caminho_fixo = self.pasta_relatorios / "ultimo_relatorio.html"
        with open(caminho_fixo, "w", encoding="utf-8") as f:
            f.write(html)

        return nome_arquivo

    # =====================================================
    # IMPRIMIR RELATÓRIO
    # =====================================================

    def imprimir_relatorio(self):
        """Imprime relatório no console."""
        print(self.gerar_relatorio_texto())

    # =====================================================
    # GERAR TODOS OS RELATÓRIOS
    # =====================================================

    def gerar_todos(self):
        """Gera todos os formatos de relatório."""

        print("\n" + "=" * 70)
        print("GERANDO RELATÓRIOS")
        print("=" * 70 + "\n")

        arquivos = []

        # TXT
        try:
            txt_path = self.salvar_relatorio_texto()
            print(f"✓ Relatório TXT: {txt_path}")
            arquivos.append(txt_path)
        except Exception as e:
            print(f"❌ Erro ao gerar TXT: {e}")

        # JSON
        try:
            json_path = self.salvar_relatorio_json()
            print(f"✓ Relatório JSON: {json_path}")
            arquivos.append(json_path)
        except Exception as e:
            print(f"❌ Erro ao gerar JSON: {e}")

        # HTML
        try:
            html_path = self.salvar_relatorio_html()
            print(f"✓ Painel HTML: {html_path}")
            arquivos.append(html_path)
        except Exception as e:
            print(f"❌ Erro ao gerar HTML: {e}")

        # PDF
        try:
            pdf_path = self.gerar_pdf()
            if pdf_path:
                print(f"✓ Relatório PDF: {pdf_path}")
                arquivos.append(pdf_path)
        except Exception as e:
            print(f"❌ Erro ao gerar PDF: {e}")

        # GRÁFICOS
        try:
            graficos = self.gerar_graficos()
            for grafico in graficos:
                arquivos.append(grafico)
        except Exception as e:
            print(f"❌ Erro ao gerar gráficos: {e}")

        print("\n" + "=" * 70)
        print(f"✓ {len(arquivos)} arquivo(s) gerado(s) com sucesso!")
        print("=" * 70 + "\n")

        return arquivos


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    banco = Banco()
    gerador = GeradorRelatorio(banco)

    # Gerar todos os formatos
    gerador.gerar_todos()

    # Exibir relatório no console
    print("\n" + "=" * 70)
    print("PRÉVIA DO RELATÓRIO TEXTO")
    print("=" * 70 + "\n")
    gerador.imprimir_relatorio()
