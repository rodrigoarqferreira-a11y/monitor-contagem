"""
===================================================

RELATORIO.PY

Gerador de Relatórios de Investimentos Privados
Monitor de Contagem

Formatos suportados:
- TXT (texto puro)
- JSON (dados indonos)
- PDF (documento formatado)
- HTML (painel web)
- Gráficos (PNG/SVG)

===================================================
"""

importar json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
estatísticas de importação
from io import BytesIO

do banco import Banco

# =====================================================
# IMPORTAÇÕES CONDICIONAIS
# =====================================================

tentar:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Tabela, Estilo de Tabela, Parágrafo, Espaçador,
        PageBreak, Imagem como RLImage
    )
    HAS_REPORTLAB = Verdadeiro
exceto ImportError:
    HAS_REPORTLAB = Falso

tentar:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg') # Interface gráfica de usuário do backend semântico
    HAS_MATPLOTLIB = Verdadeiro
exceto ImportError:
    HAS_MATPLOTLIB = Falso

tentar:
    import plotly.graph_objects as go
    import plotly.express as px
    HAS_PLOTLY = Verdadeiro
exceto ImportError:
    HAS_PLOTLY = Falso


classe GeradorRelatório:
    """
    Gera relatórios completos sobre investimentos
    detectado pelo monitor.
    """

    def __init__(self, banco: Banco = None):
        """Inicializa com dados do banco."""
        self.banco = banco ou Banco()
        self.data_geracao = datetime.now()
        self.pasta_relatorios = Caminho("relatorios")
        self.pasta_relatorios.mkdir(exist_ok=True)

    # =====================================================
    # NÚMEROS PRINCIPAIS
    # =====================================================

    def calcular_resumo_executivo(self):
        """Calcula os números principais do relatório."""

        notícias = self.banco.noticias
        investimentos = self.banco.investimentos
        empresas = self.banco.empresas

        # Contar investimentos relevantes (mencionar Contagem)
        _relevantes = [
            inv para inv em y
            se "id" em inv # ID do Tem
        ]

        # Valores Extrair
        valores = []
        para noticia em noticias:
            if noticia.get("relevante") e noticia.get("valores"):
                para valor_str em noticia.get("valores", []):
                    # Tenta extrair número
                    tentar:
                        valor_limpo = valor_str.replace("R$", "").replace(",", ".").strip()
                        valor_num = float(valor_limpo.split()[0])
                        valores.append(valor_num)
                    exceto:
                        passar

        # Extrairra
        total_sem ...
        para noticia em noticias:
            if noticia.get("relevante") e noticia.get("empregos"):
                para emp_str em noticia.get("empregos", []):
                    tentar:
                        emp_num = int("".join(filter(str.isdigit, emp_str.split()[0])))
                        total_de_sinal += número_de_funcionários
                    exceto:
                        passar

        # Confiança média
        confiancas = [
            n.get("confianca", 0)
            para n em notícias
            se n.get("relevante")
        ]
        confianca_media = int(statistics.mean(confiancas)) if confiancas else 0

        valor_total = soma(valores) if valores else 0

        retornar {
            "investimentos_detectados": len(investimentos_relevantes),
            "empresas_monitoradas": len(empresas),
            "novos_empregos": empregos_total,
            "valor_total": valor_total,
            "confianca_media": confianca_media,
            "noticias_relevantes": len([n for n in noticias if n.get("relevante")]),
            "período": self._obter_periodo_noticias()
        }

    # =====================================================
    # INVESTIMENTOS POR FASE
    # =====================================================

    def investimentos_por_fase(self):
        """Agrupa investimentos por fase."""

        notícias = self.banco.noticias
        símbolo = defaultdict(lista)

        para noticia em noticias:
            se noticia.get("relevante"):
                fase = noticia.get("fase", "Não identificado")
                g[fase].append(noticia)

        retornar dict(fases)

    # =====================================================
    # RANKING DE EMPRESAS
    # =====================================================

    def ranking_empresas(self, top_n=10):
        """Retorna top N empresas com mais investimentos."""

        notícias = self.banco.noticias
        empresas_contagem = Contador()
        empresas_valor = defaultdict(float)
        empresas_empregos = defaultdict(int)

        para noticia em noticias:
            if noticia.get("relevante") e noticia.get("mencionou_contagem"):
                para empresa em noticia.get("empresas", []):
                    empresas_contagem[empresa] += 1

                    # Valor
                    se noticia.get("valores"):
                        para valor_str em noticia.get("valores"):
                            tentar:
                                valor = float(
                                    valor_str.replace("R$", "").split()[0]
                                )
                                empresas_valor[empresa] += valor
                            exceto:
                                passar

                    # Empregos
                    se noticia.get("empregos"):
                        para emp_str em noticia.get("empregos"):
                            tentar:
                                emp = int("".join(filter(str.isdigit, emp_str.split()[0])))
                                empresas_empregos[empresa] += emp
                            exceto:
                                passar

        # Ranking Montar
        classificação = []
        para empresa, conte em empresas_contagem.most_common(top_n):
            ranking.append({
                "empresa": empresa,
                "investimentos": contagem,
                "valor_total": empresas_valor.get(empresa, 0),
                "empregos": empresas_empregos.get(empresa, 0)
            })

        classificação de retorno

    # =====================================================
    # EVOLUÇÃO TEMPORAL
    # =====================================================

    def evolução_mensal(self):
        """Cálculo da evolução dos investimentos por mês."""

        notícias = self.banco.noticias
        evolução = defaultdict(lambda: {
            "investimentos": 0,
            "empregos": 0,
            "valor": 0
        })

        para noticia em noticias:
            if noticia.get("relevante") e noticia.get("mencionou_contagem"):

                # Extrair mês
                data_str = noticia.get("dados", "")
                se data_str:
                    tentar:
                        # Suponha o formato AAAA-MM-DD ou DD/MM/AAAA
                        se "-" em data_str:
                            mes = data_str[:7] # AAAA-MM
                        outro:
                            mes = data_str[-4:] # Último ano
                    exceto:
                        mes = "Desconhecido"
                outro:
                    mes = "Desconhecido"

                evolução[mes]["investimentos"] += 1

                # Empregos
                se noticia.get("empregos"):
                    para emp_str em noticia.get("empregos"):
                        tentar:
                            emp = int("".join(filter(str.isdigit, emp_str.split()[0])))
                            evolucao[mes]["empregos"] += emp
                        exceto:
                            passar

                # Valor
                se noticia.get("valores"):
                    para val_str em noticia.get("valores"):
                        tentar:
                            val = float(val_str.replace("R$", "").split()[0])
                            evolucao[mes]["valor"] += val
                        exceto:
                            passar

        retornar dict(sorted(evolucao.items()))

    # =====================================================
    # ANÁLISE POR FONTE
    # =====================================================

    def analise_por_fonte(self):
        """Agrupa dados por fonte de notícias."""

        notícias = self.banco.noticias
        por_fonte = defaultdict(lambda: {
            "total": 0,
            "relevantes": 0,
            "confianca_media": []
        })

        para noticia em noticias:
            fonte = noticia.get("fonte", "Desconhecida")

            por_fonte[fonte]["total"] += 1

            se noticia.get("relevante"):
                por_fonte[fonte]["relevantes"] += 1

            confiança = noticia.get("confianca", 0)
            se confianca > 0:
                por_fonte[fonte]["confianca_media"].append(confianca)

        # Calcular média de confiança
        resultado = {}
        para fonte, dados em por_fonte.items():
            confiancas = dados["confianca_media"]
            resultado[fonte] = {
                "total": dados["total"],
                "relevantes": dados["relevantes"],
                "taxa_precisao": arredondar(
                    (dados["relevantes"] / dados["total"] * 100)
                    se dados["total"] > 0 senão 0,
                    1
                ),
                "confianca_media": redondo(
                    estatísticas.média(confianças)
                    se confiancas senão 0,
                    1
                )
            }

        retornar resultado

    # =====================================================
    # NOTÍCIAS "QUASE RELEVANTES"
    # =====================================================

    def noticias_quase_relevantes(self):
        """
        Notícias com boa avaliação mas descartadas por
        não mencionem Contagem.
        """

        notícias = self.banco.noticias
        cotas = []

        para noticia em noticias:
            pontuacao_ok = noticia.get("pontuação", 0) >= 30
            sem_contagem = not noticia.get("mencionou_contagem", False)

            se pontuacao_ok e sem_contagem e não noticia.get("relevante"):
                quase.append({
                    "titulo": noticia.get("titulo", ""),
                    "empresas": noticia.get("empresas", []),
                    "pontuação": noticia.get("pontuação", 0),
                    "fase": noticia.get("fase", ""),
                    "fonte": noticia.get("fonte", ""),
                    "url": noticia.get("url", "")
                })

        return ordenado(quase, key=lambda x: x["pontuacao"], reverso=True)

    # =====================================================
    # CONFIANÇA DOS DADOS
    # =====================================================

    def analise_confianca(self):
        """Análise da distribuição de confiança dos dados."""

        notícias = [
            n por n em self.banco.noticias
            se n.get("relevante")
        ]
        confiancas = [n.get("confianca", 0) for n em notícias]

        se não confiancas:
            retornar {
                "alta": 0,
                "mídia": 0,
                "baixa": 0,
                "media_geral": 0
            }

        alta = len([c for c em confiáveis ​​if c >= 80])
        media = len([c para c em confiancas se 50 <= c < 80])
        baixa = len([c for c em confiáveis ​​if c < 50])
        total = alta + média +

        retornar {
            "alta": arredondar((alta / total * 100) se total > 0 senão 0, 1),
            "mídia": arredondar((mídia / total * 100) se total > 0 senão 0, 1),
            "baixa": round((baixa / total * 100) if total > 0 else 0, 1),
            "media_geral": round(statistics.mean(confiancas), 1) if confiancas else 0
        }

    # =====================================================
    # DADOS HISTÓRICOS (para a aba Histórico)
    # =====================================================

    def dados_historico_completo(self):
        """
        Monta uma estrutura completa de dados históricos,
        pronto para ser embutido como JSON no HTML e
        manipulado em JavaScript pelos filtros.
        """

        investimentos = self.banco.investimentos

        registros = []
        for inv em:
            registros.append({
                "empresa": inv.get("empresa", ""),
                "ano": inv.get("ano"),
                "valor": inv.get("valor", 0),
                "fonte": inv.get("fonte", ""),
                "url": inv.get("url", ""),
                "fase": inv.get("fase", "Anunciado"),
                "origem": inv.get("origem", "monitoramento"),
            })

        registros de devolução

    def resumo_historico_por_ano(self):
        """
        Totais agregados por ano: total investido,
        número de investimentos, número de empresas únicas.
        """

        investimentos = self.banco.investimentos
        por_ano = {}

        for inv em:
            ano = inv.get("ano")
            se ano for None:
                continuar

            se ano não estiver em por_ano:
                por_ano[ano] = {
                    "ano": ano,
                    "total_investido": 0,
                    "num_investimentos": 0,
                    "empresas": conjunto(),
                }

            por_ano[ano]["total_investido"] += inv.get("valor", 0)
            por_ano[ano]["num_investimentos"] += 1
            por_ano[ano]["empresas"].add(inv.get("empresas", ""))

        resultado = []
        para ano em sorted(por_ano.keys()):
            dados = por_ano[ano]
            resultado.append({
                "ano": dados["ano"],
                "total_investido": dados["total_investido"],
                "num_investimentos": dados["num_investimentos"],
                "num_empresas": len(dados["empresas"]),
            })

        retornar resultado

    def ranking_empresas_historico(self, ano=Nenhum):
        """
        Ranking de empresas por valor total investido,
        somando todos os anos (base histórica).
        Se 'ano' for informado, filtre apenas aquele ano.
        """

        investimentos = self.banco.investimentos
        valores_por_empresa = {}

        for inv em:
            Se ano não for None e inv.get("ano") != ano:
                continuar

            empresa = inv.get("empresa", "")
            se não for empresa:
                continuar

            se empresa não estiver em valores_por_empresa:
                valores_por_empresa[empresa] = {
                    "empresa": empresa,
                    "valor_total": 0,
                    "num_investimentos": 0,
                }

            valores_por_empresa[empresa]["valor_total"] += inv.get("valor", 0)
            valores_por_empresa[empresa]["num_investimentos"] += 1

        classificação = ordenado(
            valores_por_empresa.valores(),
            chave=lambda x: x["valor_total"],
            reverso=Verdadeiro
        )

        classificação de retorno

    def totais_gerais_historico(self):
        """Números consolidados de toda a base histórica."""

        investimentos = self.banco.investimentos

        se não for:
            retornar {
                "total_investido": 0,
                "num_investimentos": 0,
                "num_empresas": 0,
                "ano_min": Nenhum,
                "ano_max": Nenhum,
            }

        empresas = set(inv.get("empresa", "") para inv em investimentos)
        anos = [inv.get("ano") for inv in investimentos if inv.get("ano") is not None]

        retornar {
            "total_investido": sum(inv.get("valor", 0) para inv em investimentos),
            "num_investimentos": len(investimentos),
            "num_empresas": len(empresas),
            "ano_min": min(anos) if anos else Nenhum,
            "ano_max": max(anos) if anos else Nenhum,
        }

    # =====================================================
    # AJUDANTE: PERÍODO DE NOTÍCIAS
    # =====================================================

    def _obter_periodo_noticias(self):
        """Obtém período das notícias."""

        notícias = self.banco.noticias
        se não houver notícias:
            retornar "Período desconhecido"

        dados = [
            n.get("dados", "")
            para n em notícias
            se n.get("dados")
        ]

        se houver dados:
            retornar f"{min(dados)} a {max(dados)}"
        retornar "Período desconhecido"

    # =====================================================
    # GERAR RELATÓRIO TEXTO
    # =====================================================

    def gerar_relatorio_texto(self):
        """Gera relatório em formato texto."""

        resumo = self.calcular_resumo_executivo()
        fases = self.investimentos_por_fase()
        ranking = self.ranking_empresas()
        evolução = self.evolucao_mensal()
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
        texto.append(f"\nDados de Geração: {self.data_geracao.strftime('%d/%m/%Y %H:%M')}")
        texto.append(f"Período: {resumo['período']}\n")

        # =====================================================
        # SUMÁRIO EXECUTIVO
        # =====================================================

        texto.append("\n" + "=" * 70)
        texto.append("SUMÁRIO EXECUTIVO")
        texto.append("=" * 70)
        texto.append(f"\n┌──────────────────────────────────────────┐")
        texto.append(f"│ NÚMEROS PRINCIPAIS │")
        texto.append(f"├───────────────────────────────────────────┤")
        texto.append(f"│ Investimentos detectados..: {resumo['investimentos_detectados']:>10} │")
        texto.append(f"│ Empresas monitoradas.....: {resumo['empresas_monitoradas']:>10} │")
        texto.append(f"│ Novos empregos gerados..: {resumo['novos_empregos']:>10} │")
        texto.append(f"│ Valor total anunciado...: R$ {resumo['valor_total']/1e9:>7.2f} bi │")
        texto.append(f"│ Notícias relevantes.....: {resumo['noticias_relevantes']:>10} │")
        texto.append(f"│ Confiança média.........: {resumo['confianca_media']:>9}% │")
        texto.append(f"└───────────────────────────────────────────┘")

        # =====================================================
        # INVESTIMENTOS POR FASE
        # =====================================================

        texto.append("\n" + "=" * 70)
        texto.append("INVESTIMENTOS POR FASE")
        texto.append("=" * 70)

        para fase, noticias_fase em sorted(fases.items()):
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

        para idx, emp em enumerate(ranking, 1):
            valor_m = emp["valor_total"] / 1e6 se emp["valor_total"] > 0 senão 0
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

        para período, dados em evolucao.items():
            valor_m = dados["valor"] / 1e6 if dados["valor"] > 0 else 0
            texto.append("{:<15} {:<20} {:<15} {:<15.1f}".format(
                str(período),
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

        para fonte em sorted(fontes.keys()):
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
        taxa_geral = arredondar(
            (relevantes_geral / total_geral * 100) se total_geral > 0 senão 0,
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
        texto.append(f" Alta (80-100%)........: {confianca['alta']}%")
        texto.append(f" Média (50-80%)........: {confianca['media']}%")
        texto.append(f" Baixa (< 50%).........: {confianca['baixa']}%")

        # =====================================================
        # NOTÍCIAS "QUASE RELEVANTES"
        # =====================================================

        se as questões forem relevantes:
            texto.append("\n" + "=" * 70)
            texto.append("NOTÍCIAS 'QUASE RELEVANTES'")
            texto.append("=" * 70)
            texto.append("\nNotícias com boa pontuação mas fora de Contagem:")
            texto.append("(Potencial impacto regional)\n")

            para noticia em quase_relevantes[:5]:
                texto.append(f"\n• {noticia['titulo']}")
                se noticia['empresas']:
                    texto.append(f" Empresa(s): {', '.join(noticia['empresas'])}")
                texto.append(f" Pontuação: {noticia['pontuacao']}")
                texto.append(f" Fase: {noticia['fase']}")
                texto.append(f" URL: {noticia['url']}")

        # =====================================================
        # RODAPÉ
        # =====================================================

        texto.append("\n" + "=" * 70)
        texto.append("NOTAS FINAIS")
        texto.append("=" * 70)
        texto.append(f"\nDados de geração: {self.data_geracao.strftime('%d/%m/%Y %H:%M')}")
        texto.append("Período de coleta: Últimos 30 dias")
        texto.append("\nCritérios de relevância:")
        texto.append(" ✓ Pontuação mínima: 30 pontos")
        texto.append(" ✓ Deve mencionar 'Contagem' explicitamente")
        texto.append(" ✓ identificar ao menos uma empresa monitorada")

        retornar "\n".join(texto)

    # =====================================================
    # GERAR GRÁFICOS
    # =====================================================

    def gerar_gráficos(self):
        """Gera gráficos em matplotlib e plotly."""

        se não HAS_MATPLOTLIB e não HAS_PLOTLY:
            print("⚠️ Matplotlib ou Plotly não instalado. Pulando gráficos.")
            retornar []

        arquivos_gerados = []

        tentar:
            fases = self.investimentos_por_fase()
            ranking = self.ranking_empresas(10)
            evolução = self.evolucao_mensal()
            confianca = self.analise_confianca()

            # =====================================================
            # GRÁFICO 1: INVESTIMENTOS POR FASE
            # =====================================================

            se HAS_MATPLOTLIB:
                fig, ax = plt.subplots(figsize=(12, 6))

                fases_nomes = lista(fases.chaves())
                fases_contagem = [len(fases[f]) para f in fases_nomes]

                cores_fase = plt.cm.Set3(range(len(fases_nomes)))
                ax.barh(fases_nomes, fases_contagem, color=colors_fase)
                ax.set_xlabel("Número de Investimentos", fontsize=12)
                ax.set_title("Investimentos por Fase", fontsize=14, fontweight='bold')
                ax.grid(axis='x', alpha=0.3)

                para i, v em enumerar(fases_contagem):
                    ax.text(v + 0.1, i, str(v), va='center', fontweight='bold')

                plt.tight_layout()
                arquivo = self.pasta_relatorios / "grafico_fases.png"
                plt.savefig(arquivo, dpi=300, bbox_inches='apertado')
                plt.close()
                arquivos_gerados.append(arquivo)
                print(f"✓ Gráfico: {arquivo}")

            # =====================================================
            # GRÁFICO 2: TOP 10 EMPRESAS
            # =====================================================

            se HAS_MATPLOTLIB:
                fig, ax = plt.subplots(figsize=(12, 8))

                empresas_nomes = [e["empresa"] para e no ranking]
                empresas_count = [e["investimentos"] para e no ranking]

                cores_emp = plt.cm.viridis(range(len(empresas_nomes)))
                ax.barh(empresas_nomes, empresas_count, color=colors_emp)
                ax.set_xlabel("Número de Investimentos", fontsize=12)
                ax.set_title("Top 10 Empresas com Mais Investimentos", fontsize=14, fontweight='bold')
                ax.grid(axis='x', alpha=0.3)

                para i, v em enumerate(empresas_count):
                    ax.text(v + 0.1, i, str(v), va='center', fontweight='bold')

                plt.tight_layout()
                arquivo = self.pasta_relatorios / "grafico_empresas.png"
                plt.savefig(arquivo, dpi=300, bbox_inches='apertado')
                plt.close()
                arquivos_gerados.append(arquivo)
                print(f"✓ Gráfico: {arquivo}")

            # =====================================================
            #GRÁFICO 3: EVOLUÇÃO TEMPORAL
            # =====================================================

            se HAS_MATPLOTLIB:
                fig, ax = plt.subplots(figsize=(14, 6))

                períodos = lista(evolucao.keys())
                investimentos = [evolucao[p]["investimentos"] for p in periodos]

                ax.plot(periodos, investimentos, marker='o', linewidth=2, markersize=8, color='#2E86AB')
                ax.fill_between(range(len(periodos)), investimentos, alpha=0.3, color='#2E86AB')
                ax.set_xlabel("Período", fontsize=12)
                ax.set_ylabel("Número de Investimentos", fontsize=12)
                ax.set_title("Evolução de Investimentos ao Longo do Tempo", fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3)
                plt.xticks(rotação=45, ha='direita')

                plt.tight_layout()
                arquivo = self.pasta_relatorios / "grafico_evolucao.png"
                plt.savefig(arquivo, dpi=300, bbox_inches='apertado')
                plt.close()
                arquivos_gerados.append(arquivo)
                print(f"✓ Gráfico: {arquivo}")

            # =====================================================
            # GRÁFICO 4: CONFIANÇA (TABELA DE TORTA)
            # =====================================================

            se HAS_MATPLOTLIB:
                fig, ax = plt.subplots(figsize=(10, 8))

                = [confianca['alta'], confianca['media'], confianca['baixa']]

                se sum(tamanhos) == 0:
                    ax.text(
                        0.5, 0.5, "Sem dados ainda",
                        ha='centro', va='centro',
                        tamanho da fonte=14, cor='cinza',
                        transformar=ax.transAxes
                    )
                    ax.axis('off')
                outro:
                    rotulos = [
                        f"Alta (80-100%)\n{confianca['alta']}%",
                        f"Mídia (50-80%)\n{confianca['media']}%",
                        f"Baixa (<50%)\n{confianca['baixa']}%"
                    ]
                    cores = ['#90EE90', '#FFD700', '#FF6B6B']

                    cunhas, textos, autotextos = ax.pie(
                        tamanhos,
                        rótulos=rotulos,
                        cores=núcleos,
                        autopct='',
                        ângulo inicial=90,
                        textprops={'fontsize': 11, 'fontweight': 'bold'}
                    )

                ax.set_title(f"Distribuição de Confiança\nMédia Geral: {confianca['media_geral']}%",
                           tamanho da fonte=14, peso da fonte='negrito')

                plt.tight_layout()
                arquivo = self.pasta_relatorios / "grafico_confianca.png"
                plt.savefig(arquivo, dpi=300, bbox_inches='apertado')
                plt.close()
                arquivos_gerados.append(arquivo)
                print(f"✓ Gráfico: {arquivo}")

        exceto Exception como e:
            print(f"❌ Erro ao gerar gráficos: {e}")

        retornar arquivos_gerados

    # =====================================================
    # GERAR HTML
    # =====================================================

    def gerar_html(self):
        """Gera painel interativo em HTML."""

        resumo = self.calcular_resumo_executivo()
        fases = self.investimentos_por_fase()
        ranking = self.ranking_empresas()
        evolução = self.evolucao_mensal()
        fontes = self.analise_por_fonte()
        confianca = self.analise_confianca()

        # Dados históricos (aba Histórico)
        dados_histórico = self.dados_histórico_completo()
        resumo_ano = self.resumo_histórico_por_ano()
        totais_histórico = self.totais_gerais_histórico()

        # Dados para gráficos
        fases_rótulos = lista(fases.chaves())
        fases_dados = [len(fases[f]) para f em fases_rótulos]

        empresas_labels = [e["empresa"] para e no ranking]
        empresas_data = [e["investimentos"] para e no ranking]

        períodos = lista(evolucao.keys())
        investimentos_data = [evolucao[p]["investimentos"] for p in periodos]

        ano_min = totais_historico['ano_min'] se totais_historico['ano_min'] não for Nenhum outro "-"
        ano_max = totais_historico['ano_max'] se totais_historico['ano_max'] não for Nenhum outro "-"

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
            margem: 0;
            preenchimento: 0;
            box-sized: caixa com borda;
        }}

        @import url('https://fonts.googleapis.com/css2?family=Fira+Sans:wght@400;600;700&display=swap');

        corpo {{
            família de fontes: 'Fira Sans', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            fundo: #e8eef0;
            altura mínima: 100vh;
            preenchimento: 20px;
        }}

        .container {{
            largura máxima: 1400px;
            margem: 0 auto;
            fundo: branco;
            raio da borda: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: oculto;
        }}

        .header {{
            fundo: #037482;
            cor: branca;
            preenchimento: 30px 40px;
            alinhamento de texto: esquerda;
            Exibir: flexível;
            alinhamento-itens: centro;
            espaçamento: 25px;
        }}

        .header img {{
            altura: 60px;
            fundo: branco;
            preenchimento: 8px 14px;
            raio da borda: 6px;
        }}

        .header .header-text h1 {{
            tamanho da fonte: 1,8em;
            margem-inferior: 4px;
        }}

        .header .header-text p {{
            tamanho da fonte: 1em;
            opacidade: 0,9;
        }}

        .header .selo-trabalho {{
            margem-esquerda: automática;
            fundo: #FF7A01;
            preenchimento: 6px 16px;
            raio da borda: 20px;
            tamanho da fonte: 0,85em;
            peso da fonte: 600;
            espaço em branco: nowrap;
        }}

        .header h1 {{
            tamanho da fonte: 2,5em;
            margem-inferior: 10px;
        }}

        .header p {{
            tamanho da fonte: 1,1em;
            opacidade: 0,9;
        }}

        .contente {{
            preenchimento: 40px;
        }}

        .summary-card {{
            fundo: branco;
            cor: #333;
            preenchimento: 25px;
            raio da borda: 10px;
            borda superior: 4px sólida #037482;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            alinhamento do texto: centralizado;
        }}

        .summary-card h3 {{
            cor: #037482;
        }}

        .summary-card .value {{
            Cor: #FF7A01;
        }}

        .seção {{
            margem-inferior: 40px;
        }}

        .seção h2 {{
            cor: #667eea;
            margem-inferior: 20px;
            preenchimento-inferior: 10px;
            borda inferior: 3px sólida #667eea;
        }}

        .chart-container {{
            fundo: #f8f9fa;
            raio da borda: 10px;
            preenchimento: 20px;
            margem-inferior: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}

        mesa {{
            largura: 100%;
            colapso de fronteira: colapso;
            margem superior: 20px;
        }}

        tabela th {{
            fundo: #667eea;
            cor: branca;
            preenchimento: 15px;
            alinhamento de texto: esquerda;
            peso da fonte: 600;
        }}

        tabela td {{
            preenchimento: 12px 15px;
            borda inferior: 1px sólida #e0e0e0;
        }}

        tabela tr:hover {{
            fundo: #f5f5f5;
        }}

        tabela tr:nth-child(par) {{
            fundo: #f9f9f9;
        }}

        .footer {{
            fundo: #f8f9fa;
            preenchimento: 20px;
            alinhamento do texto: centralizado;
            cor: #666;
            borda superior: 1px sólida #e0e0e0;
        }}

        /* ===== ABAS ===== */
        .tabs {{
            Exibir: flexível;
            espaçamento: 10px;
            borda inferior: 3px sólida #e0e0e0;
            margem-inferior: 30px;
        }}

        .tab-button {{
            preenchimento: 14px 28px;
            Contexto: nenhum;
            fronteira: nenhuma;
            tamanho da fonte: 1em;
            peso da fonte: 600;
            cor: #888;
            cursor: ponteiro;
            borda inferior: 3px sólida transparente;
            margem-inferior: -3px;
            transição: todos os 0,2s;
        }}

        .tab-button:hover {{
            cor: #037482;
        }}
        .tab-button.active {{
            cor: #037482;
            cor-da-borda-inferior: #FF7A01;
        }}
        .tab-content {{
            exibir: nenhum;
        }}
        .tab-content.active {{
            exibir: bloco;
        }}

        /* ===== FILTROS ===== */
        .filtros {{
            Exibir: flexível;
            espaçamento: 15px;
            flex-wrap: envolver;
            fundo: #f8f9fa;
            preenchimento: 20px;
            raio da borda: 10px;
            margem-inferior: 25px;
            alinhamento-itens: flex-end;
        }}

        .filtro-grupo {{
            Exibir: flexível;
            flex-direction: coluna;
            espaçamento: 6px;
        }}

        .filtro-grupo rótulo {{
            tamanho da fonte: 0,85em;
            peso da fonte: 600;
            cor: #555;
        }}

        .filtro-grupo selecionar {{
            preenchimento: 10px 15px;
            borda: 2px sólida #e0e0e0;
            raio da borda: 8px;
            tamanho da fonte: 0,95em;
            largura mínima: 180px;
            fundo: branco;
            cursor: ponteiro;
        }}

        .filtro-grupo select:focus {{
            Esboço: nenhum;
            cor da borda: #667eea;
        }}

        .btn-limpar-filtros {{
            preenchimento: 10px 20px;
            fundo: #e0e0e0;
            fronteira: nenhuma;
            raio da borda: 8px;
            peso da fonte: 600;
            cursor: ponteiro;
            cor: #555;
            transição: fundo 0,2s;
        }}

        .btn-limpar-filtros:hover {{
            fundo: #d0d0d0;
        }}

        /* ===== CARTÕES HISTÓRICO ===== */
        .hist-summary {{
            Exibir: grade;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            espaço: 20px;
            margem-inferior: 30px;
        }}

        .hist-card {{
            fundo: branco;
            borda: 2px sólida #f0f0f0;
            raio da borda: 10px;
            preenchimento: 20px;
            alinhamento do texto: centralizado;
        }}

        .hist-card h4 {{
            tamanho da fonte: 0,85em;
            cor: #888;
            text-transform: maiúsculas;
            margem-inferior: 8px;
        }}

        .hist-card .valor {{
            tamanho da fonte: 1,8em;
            peso da fonte: negrito;
            cor: #667eea;
        }}

        /* ===== TABELA HISTÓRICA ===== */
        .tabela-scroll {{
            altura máxima: 500px;
            overflow-y: automático;
            raio da borda: 10px;
            borda: 1px sólida #e0e0e0;
        }}

        .tabela-scroll tabela {{
            margem superior: 0;
        }}

        .tabela-scroll cabeçalho th {{
            posição: pegajosa;
            topo: 0;
            Índice z: 1;
        }}

        .link-fonte {{
            cor: #667eea;
            decoração de texto: nenhuma;
            tamanho da fonte: 0,85em;
        }}

        .link-fonte:hover {{
            decoração de texto: sublinhado;
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                tamanho da fonte: 1,8em;
            }}

            .resumo {{
                grid-template-columns: 1fr;
            }}

            .contente {{
                preenchimento: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Monitor de Investimentos Privados</h1>
            <p>Contagem-MG | Relatório gerado em {self.data_geracao.strftime('%d/%m/%Y %H:%M')}</p>
        </div>

        <div class="content">

            <!-- SISTEMA DE ABAS -->
            <div class="tabs">
                <button class="tab-button active" onclick="mostrarAba('recente')">🔴 Monitoramento recente</button>
                <button class="tab-button" onclick="mostrarAba('historico')">📊 Histórico {ano_min}-{ano_max}</button>
                <button class="tab-button" onclick="mostrarAba('analise')">🔍 Análise</button>
            </div>

            <!-- ABA: MONITORAMENTO RECENTE -->
            <div id="aba-recente" class="tab-content active">

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
                    <h3>Notícias Relevantes</h3>
                    <div class="value">{resumo['noticias_relevantes']}</div>
                </div>
            </div>

            </div>
            <!-- FIM ABA: MONITORAMENTO RECENTE -->

            <!-- ABA: ANÁLISE -->
            <div id="aba-analise" class="tab-content">

            <!-- INVESTIMENTOS POR FASE -->
            <div class="section">
                <h2>📈 Investimentos por Fase</h2>
                <div class="chart-container" id="chart-fases"></div>
                <script>
                    var data_fases = [{{
                        x: {dados_fases},
                        y: {rótulos_fases},
                        tipo: 'barra',
                        orientação: 'h',
                        marcador: {{cor: '#667eea'}}
                    }}];
                    var layout_fases = {{
                        título: 'Distribuição por Fase do Investimento',
                        xaxis: {{título: 'Quantidade'}},
                        margem: {{l: 150}}
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
                        tipo: 'barra',
                        orientação: 'h',
                        marcador: {{cor: '#764ba2'}}
                    }}];
                    var layout_empresas = {{
                        título: 'Empresas com Mais Investimentos',
                        xaxis: {{título: 'Quantidade'}},
                        margem: {{l: 200}}
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
                        x: {períodos},
                        y: {investimentos_data},
                        tipo: 'disperso',
                        modo: 'linhas+marcadores',
                        linha: {{cor: '#667eea', largura: 3}},
                        marcador: {{tamanho: 8}}
                    }}];
                    var layout_evolucao = {{
                        título: 'Evolução de Investimentos',
                        eixo x: {{título: 'Período'}},
                        eixo y: {{título: 'Quantidade'}},
                        modo de pairar: 'mais próximo'
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
                            <th>Taxa de Preence</th>
                            <th>Confiança Média</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        para fonte em sorted(fontes.keys()):
            dados = fontes[fonte]
            html += f"""
                        <tr>
                            <td>{fonte>
                            <td>{dados['total']}td>
                            <td>{dados['relevantes']}</td>
                            <td>{dados['taxa_precisao']}%</td>
                            <td>{dados['confianca_media']}%</td>
                        </tr>
            """

        html += f"""
                    </tbody>
                </table>
            </div>

            <!-- CONFIANÇA -->
            <div class="section">
                <h2>✅ Análise de Confiança</h2>
                <div class="chart-container" id="chart-confianca"></div>
                <script>
                    var data_confianca = [{{
                        valores: [{confianca['alta']}, {confianca['media']}, {confianca['baixa']}],
                        rótulos: ['Alta (80-100%)', 'Média (50-80%)', 'Baixa (<50%)'],
                        tipo: 'torta',
                        marcador: {{cores: ['#90EE90', '#FFD700', '#FF6B6B']}}
                    }}];
                    var layout_confianca = {{
                        título: 'Distribuição de Confiança dos Dados'
                    }};
                    Plotly.newPlot('chart-confianca', data_confianca, layout_confianca, {{responsivo: verdadeiro}});
                </script>
            </div>

            </div>
            <!-- FIM ABA: ANÁLISE -->

            <!-- ABA: HISTÓRICO -->
            <div id="aba-historico" class="tab-content">

                <div class="hist-summary">
                    <div class="hist-card">
                        <h4>Total Investido</h4>
                        <div class="valor" id="hist-total-investido">R$ {totais_historico['total_investido']/1e9:.2f}B</div>
                    </div>
                    <div class="hist-card">
                        <h4>Investimentos</h4>
                        <div class="valor" id="hist-num-investimentos">{totais_historico['num_investimentos']}</div>
                    </div>
                    <div class="hist-card">
                        <h4>Empresas Únicas</h4>
                        <div class="valor" id="hist-num-empresas">{totais_historico['num_empresas']}</div>
                    </div>
                    <div class="hist-card">
                        <h4>Período</h4>
                        <div class="valor" style="font-size: 1.3em;">{ano_min} – {ano_max}</div>
                    </div>
                </div>

                <div class="filtros">
                    <div class="filtro-grupo">
                        <label for="filtro-ano">Ano</label>
                        <select id="filtro-ano" onchange="aplicarFiltros()">
                            <option value="">Todos os anos</option>
                        </select>
                    </div>
                    <div class="filtro-grupo">
                        <label for="filtro-empresa">Empresa</label>
                        <select id="filtro-empresa" onchange="aplicarFiltros()">
                            <option value="">Todas as empresas</option>
                        </select>
                    </div>
                    <div class="filtro-grupo">
                        <label for="filtro-fase">Fase</label>
                        <select id="filtro-fase" onchange="aplicarFiltros()">
                            <option value="">Todas as<option>
                        </select>
                    </div>
                    <button class="btn-limpar-filtros" onclick="limparFiltros()">Filtros Limpar</button>
                </div>

                <div class="section">
                    <h2 id="hist-titulo-grafico">📈 Evolução do Investimento por Ano</h2>
                    <div class="chart-container" id="chart-historico"></div>
                </div>

                <div class="section">
                    <h2>🏆 Ranking de Empresas</h2>
                    <div class="tabela-scroll">
                        <table id="tabela-ranking-historico">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Empresa</th>
                                    <th>Valor Total</th>
                                    <th>Investimentos</th>
                                </tr>
                            </thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>

                <div class="section">
                    <h2>📋 Lista de Investimentos</h2>
                    <div class="tabela-scroll">
                        <table id="tabela-lista-historico">
                            <thead>
                                <tr>
                                    <th>Ano</th>
                                    <th>Empresa</th>
                                    <th>Valor</th>
                                    <th>Fase</th>
                                    <th>Fonte</th>
                                </tr>
                            </thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>

            </div>
            <!-- FIM ABA: HISTÓRICO -->

        </div>

        <div class="footer">
            <p>Relatório gerado pelo Monitor de Investimentos Privados de Contagem</p>
            <p>Período: {resumo['periodo']}</p>
        </div>
    </div>

    <script>
        // ===== DADOS DO HISTÓRICO (embutidos pelo Python) =====
        var dadosHistórico = {json.dumps(dados_historico, garanta_ascii=False)};
        var resumoAno = {json.dumps(resumo_ano, garanta_ascii=False)};

        // ===== SISTEMA DE ABAS =====
        função mostrarAba(nome) {{
            document.querySelectorAll('.tab-content').forEach(function(el) {{
                el.classList.remove('active');
            }});
            document.querySelectorAll('.tab-button').forEach(function(el) {{
                el.classList.remove('active');
            }});

            document.getElementById('aba-' + nome).classList.add('active');
            evento.target.classList.add('ativo');

            se (nome === 'histórico') {{
                renderizarHistorico();
            }}
        }}

        // ===== FILTROS POPULARES (uma vez, ao carregar) =====
        função popularFiltros() {{
            var anos = [...new Set(dadosHistorico.map(d => d.ano))].sort();
            var empresas = [...new Set(dadosHistorico.map(d => d.empresa))].sort();
            var fases = [...new Set(dadosHistorico.map(d => d.fase))].sort();

            var selAno = document.getElementById('filtro-ano');
            anos.forEach(function(ano) {{
                var opt = document.createElement('option');
                opt.value = ano;
                opt.textContent = ano;
                selAno.appendChild(opt);
            }});

            var selEmpresa = document.getElementById('filtro-empresa');
            empresas.forEach(function(emp) {{
                var opt = document.createElement('option');
                opt.value = emp;
                opt.textContent = emp;
                selEmpresa.appendChild(opt);
            }});

            var selFase = document.getElementById('filtro-fase');
            g.forEach(function(fase) {{
                var opt = document.createElement('option');
                opt.value = fase;
                opt.textContent = fase;
                selFase.appendChild(opt);
            }});
        }}

        função limparFiltros() {{
            document.getElementById('filtro-ano').value = '';
            document.getElementById('filtro-empresa').value = '';
            document.getElementById('filtro-fase').value = '';
            aplicarFiltros();
        }}

        função formatarMoeda(valor) {{
            se (valor >= 1e9) retorne 'R$ ' + (valor/1e9).toFixed(2) + 'B';
            se (valor >= 1e6) retorne 'R$ ' + (valor/1e6).toFixed(1) + 'M';
            retornar 'R$ ' + valor.toLocaleString('pt-BR');
        }}

        // ===== FILTRAR E RENDERIZAR TUDO =====
        função aplicarFiltros() {{
            var anoFiltro = document.getElementById('filtro-ano').value;
            var empresaFiltro = document.getElementById('filtro-empresa').value;
            var faseFiltro = document.getElementById('filtro-fase').value;

            var dadosFiltrados = dadosHistórico.filter(function(d) {{
                se (anoFiltro && String(d.ano) !== anoFiltro) retorne falso;
                if (empresaFiltro && d.empresa !== empresaFiltro) retorna falso;
                se (faseFiltro && d.fase !== faseFiltro) retorne falso;
                retornar verdadeiro;
            }});

            // Cartões de resumo
            var totalInvestido = dadosFiltrados.reduce((s, d) => s + d.valor, 0);
            var numInvestimentos = dadosFiltrados.length;
            var numEmpresas = new Set(dadosFiltrados.map(d => d.empresa)).size;

            document.getElementById('hist-total-investido').textContent = formatarMoeda(totalInvestido);
            document.getElementById('hist-num-investimentos').textContent = numInvestimentos;
            document.getElementById('hist-num-empresas').textContent = numEmpresas;

            // Gráfico: se ano específico selecionado -> barras por empresa
            // se não -> linha do tempo por ano
            se (anoFiltro) {{
                renderizarGraficoBarrasEmpresa(dadosFiltrados, anoFiltro);
            }} outro {{
                renderizarGráficoLinhaDoTempo();
            }}

            // Classificação
            renderizarRanking(dadosFiltrados);

            // Lista
            renderizarLista(dadosFiltrados);
        }}

        função renderizarGraficoLinhaDoTempo() {{
            document.getElementById('hist-titulo-grafico').textContent = '📈 Evolução do Investimento por Ano';

            var anos = resumoAno.map(d => d.ano);
            var valores = resumoAno.map(d => d.total_investido);

            var data = [{{
                x: anos,
                y: valores,
                tipo: 'disperso',
                modo: 'linhas+marcadores',
                linha: {{cor: '#667eea', largura: 3}},
                marcador: {{tamanho: 10}},
                preencher: 'zeroy',
                cor de preenchimento: 'rgba(102, 126, 234, 0.15)'
            }}];

            var layout = {{
                eixo x: {{título: 'Ano', dtick: 1}},
                yaxis: {{title: 'Total Investido (R$)'}},
                modo de pairar: 'mais próximo'
            }};

            Plotly.newPlot('chart-historico', data, layout, {{responsive: true}});
        }}

        function renderizarGraficoBarrasEmpresa(dadosFiltrados, ano) {{
            document.getElementById('hist-titulo-grafico').textContent = '🏢 Investimentos por Empresa em ' + ano;

            var ordenado = [...dadosFiltrados].sort((a, b) => b.valor - a.valor);

            var data = [{{
                x: ordenado.map(d => d.valor),
                y: ordenado.map(d => d.empresa),
                tipo: 'barra',
                orientação: 'h',
                marcador: {{cor: '#764ba2'}}
            }}];

            var layout = {{
                xaxis: {{title: 'Valor Investido (R$)'}},
                margem: {{l: 220}},
                altura: Math.max(400, ordenado.length * 30)
            }};

            Plotly.newPlot('chart-historico', data, layout, {{responsive: true}});
        }}

        função renderizarRanking(dadosFiltrados) {{
            var porEmpresa = {{}};
            dadosFiltrados.forEach(function(d) {{
                if (!porEmpresa[d.empresa]) {{
                    porEmpresa[d.empresa] = {{valor: 0, contagem: 0}};
                }}
                porEmpresa[d.empresa].valor += d.valor;
                porEmpresa[d.empresa].count += 1;
            }});

            var ranking = Object.keys(porEmpresa).map(function(emp) {{
                return {{empresa: emp, valor: porEmpresa[emp].valor, contagem: porEmpresa[emp].count}};
            }}).sort((a, b) => b.valor - a.valor);

            var tbody = document.querySelector('#tabela-ranking-historico tbody');
            tbody.innerHTML = '';

            ranking.forEach(function(item, idx) {{
                var tr = document.createElement('tr');
                tr.innerHTML = '<td>' + (idx + 1) + '</td>' +
                    '<td>' + item.empresa + '</td>' +
                    '<td>' + formatarMoeda(item.valor) + '</td>' +
                    '<td>' + item.count + '</td>';
                tbody.appendChild(tr);
            }});
        }}

        função renderizarLista(dadosFiltrados) {{
            var ordenado = [...dadosFiltrados].sort((a, b) => b.ano - a.ano || b.valor - a.valor);

            var tbody = document.querySelector('#tabela-lista-historico tbody');
            tbody.innerHTML = '';

            ordenado.forEach(function(d) {{
                var tr = document.createElement('tr');
                var linkFonte = d.url ? '<a class="link-fonte" href="' + d.url + '" target="_blank">Ver fonte ↗</a>' : '-';
                tr.innerHTML = '<td>' + d.ano + '</td>' +
                    '<td>' + d.empresa + '</td>' +
                    '<td>' + formatarMoeda(d.valor) + '</td>' +
                    '<td>' + d.fase + '</td>' +
                    '<td>' + linkFonte + '</td>';
                tbody.appendChild(tr);
            }});
        }}

        função renderizarHistorico() {{
            if (document.getElementById('filtro-ano').options.length <= 1) {{
                filtrosPopular();
            }}
            aplicarFiltros();
        }}
    </script>
</body>
</html>
        """

        retornar html

    # =====================================================
    # GERAR PDF
    # =====================================================

    def gerar_pdf(self):
        """Gerar relatório em PDF usando ReportLab."""

        se não HAS_REPORTLAB:
            print("⚠️ ReportLab não instalado. Pulando PDF.")
            retornar Nenhum

        tentar:
            resumo = self.calcular_resumo_executivo()
            ranking = self.ranking_empresas()
            fases = self.investimentos_por_fase()
            fontes = self.analise_por_fonte()

            nome_arquivo = (
                self.pasta_relatórios /
                f"relatorio_{self.data_geracao.strftime('%Y%m%d_%H%M%S')}.pdf"
            )

            doc = SimpleDocTemplate(
                str(nome_arquivo),
                tamanho_da_página=carta,
                margemDireita = 0,75 polegadas
                margemEsquerda = 0,75 polegadas
                margemSuperior=0,75 polegadas
                margemInferior=0,75*polegadas,
            )

            história = []
            estilos = obterFolhaDeEstiloDeAmostra()

            # Título
            estilo_do_título = Estilo_do_parágrafo(
                'Título personalizado',
                pai=estilos['Cabeçalho1'],
                tamanho da fonte=24,
                textColor=colors.HexColor('#667eea'),
                espaçoApós=10,
                alinhamento=1
            )
            story.append(Paragraph("Monitor de Investimentos Privados", title_style))
            story.append(Paragraph("Contagem - MG", styles['Normal']))
            história.append(Spacer(1, 0.3*polegada))

            # Dados
            história.append(Parágrafo(
                f"Dados de Geração: {self.data_geracao.strftime('%d/%m/%Y %H:%M')}",
                estilos['Normal']
            ))
            história.append(Spacer(1, 0.2*polegada))

            # Resumo
            story.append(Parágrafo("SUMÁRIO EXECUTIVO", estilos['Título2']))

            resumo_dados = [
                ["Investimentos detectados", str(resumo['investimentos_detectados'])],
                ["Empresas monitoradas", str(resumo['empresas_monitoradas'])],
                ["Novos empregos", f"{resumo['novos_empregos']:,}"],
                ["Valor total", f"R$ {resumo['valor_total']/1e9:.2f}B"],
                ["Confiança média", f"{resumo['confianca_media']}%"],
                ["Notícias relevantes", str(resumo['noticias_relevantes'])],
            ]

            resumo_tabela = Tabela(resumo_dados)
            resumo_table.setStyle(TableStyle([
                ('FUNDO', (0, 0), (-1, -1), cores.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), cores.preto),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('TAMANHO DA FONTE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, cores.cinza),
            ]))

            história.append(tabela_resumo)
            história.append(Spacer(1, 0.3*polegada))

            # 10 Melhores Empresas
            story.append(Paragraph("TOP 10 EMPRESAS", styles['Heading2']))

            ranking_data = [["Classificação", "Empresa", "Investimentos", "Valor (R$M)", "Empregos"]]
            para idx, emp em enumerate(ranking, 1):
                valor_m = emp["valor_total"] / 1e6 se emp["valor_total"] > 0 senão 0
                ranking_dados.append([
                    str(idx),
                    emp["empresa"][:25],
                    str(emp["investimentos"]),
                    f"{valor_m:.1f}",
                    str(emp["empregos"])
                ])

            tabela_de_classificação = Tabela(dados_de_classificação)

            estilos_ranking = [
                ('FUNDO', (0, 0), (-1, 0), cores.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), cores.fumaçabranca),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('TAMANHO DA FONTE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, cores.cinza),
            ]

            # Manual de striping Zebra (ROWBACKGROUNDS não existe no ReportLab)
            para i em range(1, len(ranking_data)):
                cor = cores.branco se i % 2 == 1 senão cores.HexColor('#f9f9f9')
                estilos_ranking.append(('BACKGROUND', (0, i), (-1, i), cor))

            ranking_table.setStyle(TableStyle(estilos_ranking))

            história.append(tabela_de_classificação)
            história.append(Spacer(1, 0.4*polegada))

            # =====================================================
            # RANKING HISTÓRICO (2021-2026)
            # =====================================================

            totais_hist = self.totais_gerais_historico()
            ranking_hist = self.ranking_empresas_historico()[:10]

            se ranking_hist:
                ano_min = totais_hist['ano_min']
                ano_max = totais_hist['ano_max']

                história.append(Parágrafo(
                    f"TOP 10 EMPRESAS — HISTÓRICO {ano_min}-{ano_max}",
                    estilos['Título2']
                ))
                história.append(Parágrafo(
                    f"Total investido no período: R$ {totais_hist['total_investido']/1e9:.2f}B "
                    f"em {totais_hist['num_investimentos']} investimentos",
                    estilos['Normal']
                ))
                história.append(Spacer(1, 0.15*polegada))

                ranking_hist_data = [["Classificação", "Empresa", "Valor Total (R$M)", "Investimentos"]]
                para idx, emp em enumerate(ranking_hist, 1):
                    valor_m = emp["valor_total"] / 1e6 se emp["valor_total"] > 0 senão 0
                    ranking_hist_data.append([
                        str(idx),
                        emp["empresa"][:35],
                        f"{valor_m:,.1f}",
                        str(emp["num_investimentos"])
                    ])

                tabela_hist_de_classificação = Tabela(dados_hist_de_classificação)

                estilos_hist = [
                    ('FUNDO', (0, 0), (-1, 0), cores.HexColor('#764ba2')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), cores.fumaçabranca),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('TAMANHO DA FONTE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, cores.cinza),
                ]

                para i em range(1, len(ranking_hist_data)):
                    cor = cores.branco se i % 2 == 1 senão cores.HexColor('#f5f0fa')
                    estilos_hist.append(('BACKGROUND', (0, i), (-1, i), cor))

                ranking_hist_table.setStyle(TableStyle(estilos_hist))

                história.append(tabela_hist_de_classificação)

            # Construir PDF
            doc.build(história)
            retornar nome_arquivo

        exceto Exception como e:
            print(f"❌ Erro ao gerar PDF: {e}")
            retornar Nenhum

    # =====================================================
    # SALVAR RELATÓRIO
    # =====================================================

    def salvar_relatorio_texto(self):
        """Salva relatório em arquivo TXT."""

        relatorio = self.gerar_relatorio_texto()

        nome_arquivo = (
            self.pasta_relatórios /
            f"relatorio_{self.data_geracao.strftime('%Y%m%d_%H%M%S')}.txt"
        )

        com open(nome_arquivo, "w", encoding="utf-8") as f:
            f.escrever(relatório)

        retornar nome_arquivo

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
            self.pasta_relatórios /
            f"relatorio_{self.data_geracao.strftime('%Y%m%d_%H%M%S')}.json"
        )

        com open(nome_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, recuo=4, garantir_ascii=Falso)

        retornar nome_arquivo

    def salvar_relatorio_html(self):
        """Salva relatório em HTML."""

        html = self.gerar_html()

        nome_arquivo = (
            self.pasta_relatórios /
            f"relatorio_{self.data_geracao.strftime('%Y%m%d_%H%M%S')}.html"
        )

        com open(nome_arquivo, "w", encoding="utf-8") as f:
            f.escrever(html)

        # Salva também uma cópia fixa, sempre com o mesmo nome,
        # para manter uma URL estável no GitHub Pages
        caminho_fixo = self.pasta_relatorios / "ultimo_relatorio.html"
        com open(caminho_fixo, "w", encoding="utf-8") como f:
            f.escrever(html)

        retornar nome_arquivo

    # =====================================================
    # IMPRIMIR RELATÓRIO
    # =====================================================

    def imprimir_relatório(self):
        """Imprime relatório no console."""
        imprimir(self.gerar_relatorio_texto())

    # =====================================================
    # GERAR TODOS OS RELATÓRIOS
    # =====================================================

    def gerar_todos(self):
        """Gera todos os formatos de relatório."""

        print("\n" + "=" * 70)
        imprimir("GERANDO RELATÓRIOS")
        print("=" * 70 + "\n")

        arquivos = []

        # TXT
        tentar:
            txt_path = self.salvar_relatorio_texto()
            print(f"✓ Relatório TXT: {txt_path}")
            arquivos.append(txt_path)
        exceto Exception como e:
            print(f"❌ Erro ao gerar TXT: {e}")

        # JSON
        tentar:
            json_path=self.salvar_relatorio_json()
            print(f"✓ Relatório JSON: {json_path}")
            arquivos.append(caminho_json)
        exceto Exception como e:
            print(f"❌ Erro ao gerar JSON: {e}")

        # HTML
        tentar:
            html_path = self.salvar_relatorio_html()
            print(f"✓ Painel HTML: {html_path}")
            arquivos.append(html_path)
        exceto Exception como e:
            print(f"❌ Erro ao gerar HTML: {e}")

        # PDF
        tentar:
            pdf_path = self.gerar_pdf()
            se pdf_path:
                print(f"✓ Relatório PDF: {pdf_path}")
                arquivos.append(caminho_pdf)
        exceto Exception como e:
            print(f"❌ Erro ao gerar PDF: {e}")

        # GRÁFICOS
        tentar:
            gráficos = self.gerar_graficos()
            para gráfico em gráficos:
                arquivos.append(gráfico)
        exceto Exception como e:
            print(f"❌ Erro ao gerar gráficos: {e}")

        print("\n" + "=" * 70)
        print(f"✓ {len(arquivos)} arquivo(s) gerado(s) com sucesso!")
        print("=" * 70 + "\n")

        devolver arquivos


# =====================================================
# PRINCIPAL
# =====================================================

se __name__ == "__main__":

    banco = Banco()
    gerador = GeradorRelatório(banco)

    # Gerar todos os se
    gerador.gerar_todos()

    # Exibir relatório no console
    print("\n" + "=" * 70)
    print("PRÉVIA DO RELATÓRIO TEXTO")
    print("=" * 70 + "\n")
    gerador.imprimir_relatório()
