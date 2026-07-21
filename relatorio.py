"""
====================================================
RELATORIO.PY — Monitor de Investimentos Privados
SEDECON · Prefeitura de Contagem MG
====================================================
"""

import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from banco import Banco

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        HRFlowable, PageBreak, Paragraph,
        SimpleDocTemplate, Spacer, Table, TableStyle,
    )
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

try:
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.use("Agg")
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class GeradorRelatorio:

    def __init__(self, banco: Banco = None):
        self.banco        = banco or Banco()
        self.data_geracao = datetime.now()
        self.pasta        = Path("relatorios")
        self.pasta.mkdir(exist_ok=True)

    def _relevantes(self):
        return [n for n in self.banco.noticias if n.get("relevante")]

    def _todas(self):
        return list(self.banco.noticias)

    def _historico(self):
        return [i for i in self.banco.investimentos if i.get("origem") == "historico"]

    def _periodo(self):
        datas = [n.get("data","") for n in self.banco.noticias if n.get("data")]
        return f"{min(datas)} a {max(datas)}" if datas else "—"

    def _vnum(self, v):
        if isinstance(v, (int, float)): return float(v)
        try:
            return float(str(v).replace("R$","").replace(".","").replace(",",".").strip().split()[0])
        except: return 0.0

    def _enum(self, s):
        try: return int("".join(c for c in str(s).split()[0] if c.isdigit()))
        except: return 0

    # ── ANÁLISES RECENTES ─────────────────────────────

    def resumo_recente(self):
        ns   = self._relevantes()
        vals = [self._vnum(v) for n in ns for v in n.get("valores",[])]
        emps = sum(self._enum(e) for n in ns for e in n.get("empregos",[]))
        cfs  = [n.get("confianca",0) for n in ns if n.get("confianca",0)>0]
        return {
            "noticias_relevantes": len(ns),
            "novos_empregos":      emps,
            "valor_total":         sum(vals),
            "confianca_media":     int(statistics.mean(cfs)) if cfs else 0,
            "periodo":             self._periodo(),
        }

    def fases_recentes(self):
        d = defaultdict(int)
        for n in self._relevantes():
            d[n.get("fase","Não identificada")] += 1
        return dict(d)

    def fontes_recentes(self):
        d = defaultdict(lambda:{"total":0,"relevantes":0,"cfs":[]})
        for n in self.banco.noticias:
            f = n.get("fonte","Desconhecida")
            d[f]["total"] += 1
            if n.get("relevante"): d[f]["relevantes"] += 1
            c = n.get("confianca",0)
            if c>0: d[f]["cfs"].append(c)
        return {
            f: {
                "total":      v["total"],
                "relevantes": v["relevantes"],
                "taxa":       round(v["relevantes"]/v["total"]*100 if v["total"] else 0,1),
                "confianca":  round(statistics.mean(v["cfs"]) if v["cfs"] else 0,1),
            } for f,v in d.items()
        }

    def quase_relevantes(self):
        return sorted([
            {"titulo":n.get("titulo",""), "empresas":n.get("empresas",[]),
             "pontuacao":n.get("pontuacao",0), "fase":n.get("fase",""),
             "fonte":n.get("fonte",""), "url":n.get("url","")}
            for n in self.banco.noticias
            if n.get("pontuacao",0)>=30
            and not n.get("mencionou_contagem",False)
            and not n.get("relevante")
        ], key=lambda x: x["pontuacao"], reverse=True)

    def confianca_recente(self):
        cs = [n.get("confianca",0) for n in self._relevantes()]
        if not cs: return {"alta":0,"media":0,"baixa":0,"mg":0}
        t = len(cs)
        return {
            "alta":  round(len([c for c in cs if c>=80])/t*100,1),
            "media": round(len([c for c in cs if 50<=c<80])/t*100,1),
            "baixa": round(len([c for c in cs if c<50])/t*100,1),
            "mg":    round(statistics.mean(cs),1),
        }

    # ── ANÁLISES HISTÓRICO ────────────────────────────

    def resumo_historico(self):
        h   = self._historico()
        tv  = sum(float(i.get("valor",0) or 0) for i in h)
        emp = set(i.get("empresa","") for i in h if i.get("empresa"))
        anos= set(i.get("ano",0) for i in h if i.get("ano"))
        return {
            "total_investimentos": len(h),
            "total_valor":         tv,
            "empresas_unicas":     len(emp),
            "periodo":             f"{min(anos)} – {max(anos)}" if anos else "—",
        }

    def ranking_historico(self, top=15):
        h   = self._historico()
        cnt = Counter(); vals = defaultdict(float)
        for i in h:
            e = i.get("empresa","")
            if not e: continue
            cnt[e] += 1
            vals[e] += float(i.get("valor",0) or 0)
        return [
            {"empresa":e,"investimentos":c,"valor_total":vals[e]}
            for e,c in cnt.most_common(top)
        ]

    def por_ano_historico(self):
        h = self._historico()
        d = defaultdict(lambda:{"investimentos":0,"valor":0})
        for i in h:
            a = str(i.get("ano","?"))
            d[a]["investimentos"] += 1
            d[a]["valor"] += float(i.get("valor",0) or 0)
        return dict(sorted(d.items()))

    def lista_historico(self):
        return sorted(
            self._historico(),
            key=lambda x: (x.get("ano",0), -(float(x.get("valor",0) or 0)))
        )

    # ── TEXTO ─────────────────────────────────────────

    def gerar_relatorio_texto(self):
        r  = self.resumo_recente()
        rh = self.resumo_historico()
        rk = self.ranking_historico()
        pa = self.por_ano_historico()
        L  = ["="*70,"RELATÓRIO DE INVESTIMENTOS PRIVADOS — CONTAGEM MG",
              "SEDECON","="*70,
              f"Gerado em: {self.data_geracao.strftime('%d/%m/%Y %H:%M')}",
              f"\n=== MONITORAMENTO RECENTE ===",
              f"  Notícias relevantes : {r['noticias_relevantes']}",
              f"  Novos empregos      : {r['novos_empregos']:,}",
              f"  Valor detectado     : R$ {r['valor_total']/1e6:.1f} M",
              f"  Confiança média     : {r['confianca_media']}%",
              f"\n=== HISTÓRICO 2021-2026 ===",
              f"  Total investimentos : {rh['total_investimentos']}",
              f"  Valor total         : R$ {rh['total_valor']/1e9:.2f} bi",
              f"  Empresas únicas     : {rh['empresas_unicas']}",
              f"  Período             : {rh['periodo']}",
              f"\n=== RANKING EMPRESAS ==="]
        for i,e in enumerate(rk,1):
            L.append(f"  {i:>2}. {e['empresa'][:35]:<36} R$ {e['valor_total']/1e6:>8.1f}M  ({e['investimentos']} inv.)")
        L.append(f"\n=== POR ANO ===")
        for a,d in pa.items():
            L.append(f"  {a}: {d['investimentos']} invest. — R$ {d['valor']/1e9:.2f} bi")
        return "\n".join(L)

    # ── GRÁFICOS ──────────────────────────────────────

    def gerar_graficos(self):
        if not HAS_MATPLOTLIB: return []
        arqs=[]; AZUL="#1a3a5c"; OURO="#e8a020"

        def salvar(nome):
            p=self.pasta/nome
            plt.savefig(p,dpi=180,bbox_inches="tight")
            plt.close(); arqs.append(p); print(f"  ✓ {p}")

        try:
            rk = self.ranking_historico(10)
            pa = self.por_ano_historico()
            fs = self.fases_recentes()
            cf = self.confianca_recente()

            if rk:
                fig,ax=plt.subplots(figsize=(10,6))
                nomes=[e["empresa"][:28] for e in rk]
                vals=[e["valor_total"]/1e6 for e in rk]
                bars=ax.barh(nomes,vals,color=AZUL)
                for b,v in zip(bars,vals):
                    ax.text(b.get_width()+2,b.get_y()+b.get_height()/2,
                            f"R$ {v:.0f}M",va="center",fontsize=8,color=AZUL)
                ax.set_xlabel("R$ Milhões")
                ax.set_title("Top Empresas por Valor Investido",fontsize=12,fontweight="bold",color=AZUL)
                ax.spines[["top","right"]].set_visible(False)
                plt.tight_layout(); salvar("grafico_ranking.png")

            if pa:
                fig,ax=plt.subplots(figsize=(10,5))
                anos=list(pa.keys()); vals=[pa[a]["valor"]/1e9 for a in anos]
                bars=ax.bar(anos,vals,color=OURO,edgecolor="white",linewidth=1.5)
                for b,v in zip(bars,vals):
                    ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.02,
                            f"R$ {v:.1f}bi",ha="center",fontsize=8,fontweight="bold",color=AZUL)
                ax.set_ylabel("R$ Bilhões")
                ax.set_title("Investimentos por Ano",fontsize=12,fontweight="bold",color=AZUL)
                ax.spines[["top","right"]].set_visible(False)
                plt.tight_layout(); salvar("grafico_por_ano.png")

            if fs:
                fig,ax=plt.subplots(figsize=(9,4))
                nomes=list(fs.keys()); vals=list(fs.values())
                bars=ax.barh(nomes,vals,color=AZUL)
                for b,v in zip(bars,vals):
                    ax.text(b.get_width()+.05,b.get_y()+b.get_height()/2,
                            str(v),va="center",fontweight="bold",color=AZUL)
                ax.set_xlabel("Notícias")
                ax.set_title("Notícias Recentes por Fase",fontsize=12,fontweight="bold",color=AZUL)
                ax.spines[["top","right"]].set_visible(False)
                plt.tight_layout(); salvar("grafico_fases.png")

            cv=[cf["alta"],cf["media"],cf["baixa"]]
            if any(v>0 for v in cv):
                fig,ax=plt.subplots(figsize=(6,6))
                ax.pie(cv,
                       labels=[f"Alta\n{cf['alta']}%",f"Média\n{cf['media']}%",f"Baixa\n{cf['baixa']}%"],
                       colors=["#2ecc71",OURO,"#e74c3c"],
                       startangle=90,wedgeprops={"edgecolor":"white","linewidth":2})
                ax.set_title(f"Confiança dos Dados — Média {cf['mg']}%",
                             fontsize=12,fontweight="bold",color=AZUL)
                plt.tight_layout(); salvar("grafico_confianca.png")

        except Exception as e:
            print(f"  Erro gráficos: {e}")
        return arqs


    # ── HTML ──────────────────────────────────────────

    def gerar_html(self):
        r   = self.resumo_recente()
        rh  = self.resumo_historico()
        rk  = self.ranking_historico()
        pa  = self.por_ano_historico()
        fs  = self.fases_recentes()
        fn  = self.fontes_recentes()
        cf  = self.confianca_recente()
        qr  = self.quase_relevantes()
        nrs = self._relevantes()
        all_n = self._todas()
        hist  = self.lista_historico()

        njs  = json.dumps(nrs,    ensure_ascii=False)
        ajs  = json.dumps(all_n,  ensure_ascii=False)
        hjs  = json.dumps(hist,   ensure_ascii=False)
        rkjs = json.dumps(rk,     ensure_ascii=False)
        pajs = json.dumps(pa,     ensure_ascii=False)
        fsjs = json.dumps(fs,     ensure_ascii=False)
        qjs  = json.dumps(qr,     ensure_ascii=False)
        cfjs = json.dumps(cf,     ensure_ascii=False)

        f_rows=""
        tg=rg=0
        for f in sorted(fn):
            d=fn[f]; tg+=d["total"]; rg+=d["relevantes"]
            f_rows+=(f'<tr><td>{f}</td><td>{d["total"]}</td>'
                     f'<td>{d["relevantes"]}</td><td>{d["taxa"]}%</td>'
                     f'<td>{d["confianca"]}%</td></tr>')
        taxa=round(rg/tg*100 if tg else 0,1)
        f_rows+=(f'<tr class="tr-tot"><td><b>TOTAL</b></td><td><b>{tg}</b></td>'
                 f'<td><b>{rg}</b></td><td><b>{taxa}%</b></td><td>—</td></tr>')

        vm = r["valor_total"]/1e6
        vhb= rh["total_valor"]/1e9

        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Monitor de Investimentos — Contagem MG</title>
<script src="https://cdn.plot.ly/plotly-2.30.0.min.js"></script>
<style>
:root{{--az:#1a3a5c;--ou:#e8a020;--bg:#f0f4fa;--br:#fff;--ci:#6b7280;--bo:#dde3ec;--vd:#16a34a;--tx:#1f2937}}
*{{box-sizing:border-box;margin:0;padding:0}}
  body {{
    font-family: 'Inter', 'Segoe UI', sans-serif;
    background: #f0f4fa;
  }}
  /* HEADER PRINCIPAL */
  .hdr {{
    background: #037482;
    padding: 0;
    position: relative;
    overflow: hidden;
  }}

  .hdr-inner {{
    display: flex;
    align-items: stretch;
    min-height: 130px;
  }}
  /* Faixa lateral esquerda com cor mais escura */
  .hdr-logo-col {{
    background: #035863;
    padding: 34px 38px;
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 300px;
    flex-shrink: 0;
  }}
  .hdr-logo-col img {{
    max-width: 110px;
    max-height: 70px;
    width: auto;
    height: auto;
    display: block;
}}

   .logo-placeholder {{
    background: rgba(14, 185, 205, 0.15);
    border: 2px solid rgba(14, 185, 205, 0.4);
    border-radius: 20px;
    width: 110px;
    height: 70px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    color: #0EB9CD;
    text-align: center;
    font-weight: 600;
    letter-spacing: 0.5px;
  }}

    /* Conteúdo central */
  .hdr-content {{
    flex: 1;
    padding: 24px 32px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }}

    .hdr-supertitle {{
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #0EB9CD;
    margin-bottom: 6px;
  }}

  .hdr-title {{
    font-size: 22px;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.2;
    margin-bottom: 6px;
  }}

  .hdr-subtitle {{
    font-size: 12px;
    color: rgba(255,255,255,0.65);
    font-weight: 400;
  }}

  /* Linha decorativa accent */
  .hdr-accent-line {{
    height: 3px;
    background: linear-gradient(90deg, #035863 0%, #0EB9CD 40%, #D2DD68 75%, #FF7A01 100%);
  }}

   /* CARDS DE MÉTRICAS */
  .cards {{
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 0;
    background: #035863;
  }}

  .metric-card {{
    padding: 16px 20px;
    text-align: center;
    border-right: 1px solid rgba(14, 185, 205, 0.2);
    position: relative;
  }}

  .metric-card:last-child {{ border-right: none; }}

  .metric-card::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: transparent;
  }}

  .metric-card.destaque::before {{ background: #D2DD68; }}
  .metric-card.alerta::before   {{ background: #FF7A01; }}
  .metric-card.info::before     {{ background: #0EB9CD; }}

  .metric-val {{
    font-size: 24px;
    font-weight: 800;
    color: #ffffff;
    line-height: 1;
    margin-bottom: 4px;
  }}

  .metric-val.ouro  {{ color: #D2DD68; }}
  .metric-val.ciano {{ color: #0EB9CD; }}
  .metric-val.laranja {{ color: #FF7A01; }}

  .metric-lbl {{
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: rgba(255,255,255,0.5);
    font-weight: 600;
  }}

    /* ABAS */
  .tabs-wrap {{
    background: #024f5a;
    padding: 0 0 0 0;
    border-bottom: 2px solid #035863;
  }}

  .tabs {{
    display: flex;
    padding: 0 24px;
  }}

  .tab {{
    padding: 12px 20px;
    font-size: 12px;
    font-weight: 600;
    color: rgba(255,255,255,0.5);
    cursor: pointer;
    border-bottom: 3px solid transparent;
    margin-bottom: -2px;
    transition: all 0.15s;
    white-space: nowrap;
    letter-spacing: 0.3px;
  }}

  .tab:hover {{ color: rgba(255,255,255,0.8); }}

  .tab.on {{
    color: #D2DD68;
    border-bottom-color: #D2DD68;
  }}
footer{{background:var(--az);color:rgba(255,255,255,.5);text-align:center;padding:14px;font-size:.74rem;margin-top:14px}}
@media(max-width:768px){{.hdr,.cards,.tabs-wrap,.pan{padding-left:14px;padding-right:14px}}.g2,.g3{{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="hdr">
  <div class="hdr-inner">
    <div class="hdr-logo-col">
      <div class="logo-placeholder">LOGO<br>SEDECON</div>
    </div>
    <div class="hdr-content">
      <div class="hdr-supertitle">Prefeitura de Contagem · MG</div>
      <div class="hdr-title">Monitor de Investimentos Privados</div>
      <div class="hdr-subtitle">SEDECON · Superintendência de Inovação e Informações Estratégicas</div>
    </div>
  </div>
  <div class="hdr-accent-line"></div>
</div> 

<div class="cards">

    <div class="metric-card">
        <div class="metric-val">{r['investimentos_detectados']}</div>
        <div class="metric-lbl">Investimentos</div>
    </div>

    <div class="metric-card">
        <div class="metric-val">{r['empresas_monitoradas']}</div>
        <div class="metric-lbl">Empresas</div>
    </div>

    <div class="metric-card destaque">
        <div class="metric-val ouro">{r['novos_empregos']:,}</div>
        <div class="metric-lbl">Empregos gerados</div>
    </div>

    <div class="metric-card destaque">
        <div class="metric-val ouro">R$ {vm:.0f}M</div>
        <div class="metric-lbl">Valor total</div>
    </div>

    <div class="metric-card info">
        <div class="metric-val ciano">{r['confianca_media']}%</div>
        <div class="metric-lbl">Confiança média</div>
    </div>

    <div class="metric-card alerta">
        <div class="metric-val laranja">{r['noticias_relevantes']}</div>
        <div class="metric-lbl">Notícias relevantes</div>
    </div>

</div>

<div class="tabs-wrap">
  <div class="tabs">
    <button class="tab on"  onclick="aba('recente',this)">🔔 Monitoramento Recente</button>
    <button class="tab"     onclick="aba('historico',this)">📋 Histórico 2021–2026</button>
    <button class="tab"     onclick="aba('graficos',this)">📈 Gráficos</button>
    <button class="tab"     onclick="aba('todas',this)">🗂 Todas as Notícias</button>
    <button class="tab"     onclick="aba('fontes',this)">📰 Fontes</button>
    <button class="tab"     onclick="aba('quase',this)">🔍 Quase Relevantes</button>
  </div>
</div>

<!-- RECENTE -->
<div id="p-recente" class="pan on">
  <div class="g3" style="margin-bottom:20px">
    <div class="sbox"><div class="sval">{r['noticias_relevantes']}</div><div class="slbl">Notícias relevantes</div></div>
    <div class="sbox"><div class="sval">{r['novos_empregos']:,}</div><div class="slbl">Empregos detectados</div></div>
    <div class="sbox"><div class="sval">R$ {vm:.0f}M</div><div class="slbl">Valor monitorado</div></div>
  </div>
  <div class="flt">
    <label>Empresa</label><select id="r-emp" onchange="renderRec()"><option value="">Todas</option></select>
    <label>Fase</label><select id="r-fas" onchange="renderRec()"><option value="">Todas</option></select>
    <label>Buscar</label><input id="r-txt" placeholder="Palavra no título..." oninput="renderRec()">
    <button class="btnx" onclick="limpRec()">✕ Limpar</button>
  </div>
  <div id="lst-rec"></div>
</div>

<!-- HISTÓRICO -->
<div id="p-historico" class="pan">
  <div class="g3" style="margin-bottom:20px">
    <div class="sbox"><div class="sval">{rh['total_investimentos']}</div><div class="slbl">Investimentos registrados</div></div>
    <div class="sbox"><div class="sval">R$ {vhb:.1f}bi</div><div class="slbl">Valor total 2021–2026</div></div>
    <div class="sbox"><div class="sval">{rh['empresas_unicas']}</div><div class="slbl">Empresas únicas</div></div>
  </div>
  <div class="g2">
    <div class="sec">
      <div class="stit">🏆 Ranking por valor investido</div>
      <div class="twrap"><table>
        <thead><tr><th>#</th><th>Empresa</th><th>Invest.</th><th>Valor total</th></tr></thead>
        <tbody id="tb-rk"></tbody>
      </table></div>
    </div>
    <div class="sec">
      <div class="stit">📅 Por ano</div>
      <div class="twrap"><table>
        <thead><tr><th>Ano</th><th>Qtd.</th><th>Valor total</th></tr></thead>
        <tbody id="tb-ano"></tbody>
      </table></div>
    </div>
  </div>
  <div class="sec">
    <div class="stit">📄 Lista completa de investimentos</div>
    <div class="flt">
      <label>Empresa</label><select id="h-emp" onchange="renderHist()"><option value="">Todas</option></select>
      <label>Ano</label><select id="h-ano" onchange="renderHist()"><option value="">Todos</option></select>
      <label>Buscar</label><input id="h-txt" placeholder="Empresa ou descrição..." oninput="renderHist()">
      <button class="btnx" onclick="limpHist()">✕ Limpar</button>
    </div>
    <div class="twrap"><table>
      <thead><tr><th>Ano</th><th>Empresa</th><th>Valor</th><th>Empregos</th><th>Fase</th><th>Fonte</th></tr></thead>
      <tbody id="tb-hist"></tbody>
    </table></div>
  </div>
</div>

<!-- GRÁFICOS -->
<div id="p-graficos" class="pan">
  <div class="g2">
    <div class="sec"><div class="stit">🏆 Top empresas por valor (histórico)</div><div class="graf" id="g-rk"></div></div>
    <div class="sec"><div class="stit">📅 Investimentos por ano</div><div class="graf" id="g-ano"></div></div>
  </div>
  <div class="g2">
    <div class="sec"><div class="stit">🔔 Notícias recentes por fase</div><div class="graf" id="g-fas"></div></div>
    <div class="sec"><div class="stit">✅ Confiança dos dados recentes</div><div class="graf" id="g-cf"></div></div>
  </div>
</div>

<!-- TODAS -->
<div id="p-todas" class="pan">
  <div class="flt">
    <label>Empresa</label><select id="a-emp" onchange="renderTodas()"><option value="">Todas</option></select>
    <label>Fase</label><select id="a-fas" onchange="renderTodas()"><option value="">Todas</option></select>
    <label>Relevância</label>
    <select id="a-rel" onchange="renderTodas()">
      <option value="">Todas</option><option value="s">Relevantes</option><option value="n">Descartadas</option>
    </select>
    <label>Buscar</label><input id="a-txt" placeholder="Palavra no título..." oninput="renderTodas()">
    <button class="btnx" onclick="limpTodas()">✕ Limpar</button>
  </div>
  <div id="lst-todas"></div>
</div>

<!-- FONTES -->
<div id="p-fontes" class="pan">
  <div class="sec">
    <div class="stit">📰 Desempenho por fonte</div>
    <div class="twrap"><table>
      <thead><tr><th>Fonte</th><th>Total</th><th>Relevantes</th><th>Precisão</th><th>Confiança</th></tr></thead>
      <tbody>{f_rows}</tbody>
    </table></div>
  </div>
</div>

<!-- QUASE -->
<div id="p-quase" class="pan">
  <div class="sec">
    <div class="stit">🔍 Boa pontuação, mas fora de Contagem</div>
    <p style="color:var(--ci);font-size:.82rem;margin-bottom:14px">Pontuação ≥ 30, empresa monitorada identificada, mas sem menção explícita a Contagem.</p>
    <div id="lst-quase"></div>
  </div>
</div>

<footer>Monitor de Investimentos Privados · SEDECON · Prefeitura de Contagem MG · {self.data_geracao.strftime('%d/%m/%Y %H:%M')}</footer>

<script>
const NR={njs};
const ALL={ajs};
const HIST={hjs};
const RK={rkjs};
const PA={pajs};
const FS={fsjs};
const QR={qjs};
const CF={cfjs};
const AZUL='#1a3a5c',OURO='#e8a020',VERDE='#16a34a';

let grafOk=false;
function aba(id,btn){{
  document.querySelectorAll('.pan').forEach(p=>p.classList.remove('on'));
  document.querySelectorAll('.tab').forEach(b=>b.classList.remove('on'));
  document.getElementById('p-'+id).classList.add('on');
  btn.classList.add('on');
  if(id==='graficos'&&!grafOk){{grafOk=true;renderGraf();}}
}}

function bdg(f){{
  const m={{'Anunciado':'ba','Construção':'bo2','Operação':'bv','Expansão':'bv','Licenciamento':'bc','Contratação':'bc','Negociação':'bc'}};
  return '<span class="bdg '+(m[f]||'bc')+'">'+(f||'—')+'</span>';
}}

function cardN(n,extra){{
  const e=(n.empresas||[]).join(', ')||'—';
  const v=(n.valores||[]).join(', ')||'—';
  const em=(n.empregos||[]).join(', ')||'—';
  return '<div class="nc'+(extra?' q':'')+'"><div class="nt">'+(n.titulo||'—')+'</div>'
    +'<div class="nm"><span>📍 '+(n.fonte||'—')+'</span><span>📅 '+(n.data||'—')+'</span>'
    +'<span>🎯 '+(n.pontuacao||0)+' pts</span>'+bdg(n.fase)
    +(n.relevante?'<span class="bdg bv">✓ Relevante</span>':'')+'</div>'
    +'<div class="nm">🏢 '+e+' | 💰 '+v+' | 👥 '+em+'</div>'
    +'<a class="nu" href="'+(n.url||'#')+'" target="_blank">'+(n.url||'')+'</a></div>';
}}

function popSel(id,arr){{
  const s=document.getElementById(id);if(!s)return;
  [...new Set(arr.filter(Boolean))].sort().forEach(v=>s.add(new Option(v,v)));
}}

function renderRec(){{
  const e=document.getElementById('r-emp').value.toLowerCase();
  const f=document.getElementById('r-fas').value.toLowerCase();
  const t=document.getElementById('r-txt').value.toLowerCase();
  const lista=NR.filter(n=>
    (!e||(n.empresas||[]).join(' ').toLowerCase().includes(e))&&
    (!f|(n.fase||'').toLowerCase()===f)&&
    (!t|(n.titulo||'').toLowerCase().includes(t))
  );
  document.getElementById('lst-rec').innerHTML=
    lista.length?lista.map(n=>cardN(n,false)).join(''):'<div class="vz">Nenhuma notícia relevante encontrada.</div>';
}}
function limpRec(){{['r-emp','r-fas','r-txt'].forEach(id=>{{const el=document.getElementById(id);if(el)el.value=''}});renderRec();}}

function renderTodas(){{
  const e=document.getElementById('a-emp').value.toLowerCase();
  const f=document.getElementById('a-fas').value.toLowerCase();
  const r=document.getElementById('a-rel').value;
  const t=document.getElementById('a-txt').value.toLowerCase();
  const lista=ALL.filter(n=>
    (!e||(n.empresas||[]).join(' ').toLowerCase().includes(e))&&
    (!f|(n.fase||'').toLowerCase()===f)&&
    (!r||(r==='s'?n.relevante:!n.relevante))&&
    (!t|(n.titulo||'').toLowerCase().includes(t))
  );
  document.getElementById('lst-todas').innerHTML=
    lista.length?lista.map(n=>cardN(n,false)).join(''):'<div class="vz">Nenhuma notícia com esses filtros.</div>';
}}
function limpTodas(){{['a-emp','a-fas','a-rel','a-txt'].forEach(id=>{{const el=document.getElementById(id);if(el)el.value=''}});renderTodas();}}

function renderRanking(){{
  const tb=document.getElementById('tb-rk');if(!tb)return;
  tb.innerHTML=RK.map((e,i)=>'<tr><td><b>'+(i+1)+'</b></td><td>'+e.empresa+'</td><td style="text-align:center">'+e.investimentos+'</td><td>R$ '+(e.valor_total/1e6).toFixed(1)+'M</td></tr>').join('')||'<tr><td colspan="4" class="vz">Sem dados.</td></tr>';
}}

function renderPorAno(){{
  const tb=document.getElementById('tb-ano');if(!tb)return;
  tb.innerHTML=Object.entries(PA).map(([a,d])=>'<tr><td><b>'+a+'</b></td><td style="text-align:center">'+d.investimentos+'</td><td>R$ '+(d.valor/1e9).toFixed(2)+'bi</td></tr>').join('')||'<tr><td colspan="3" class="vz">Sem dados.</td></tr>';
}}

function renderHist(){{
  const e=document.getElementById('h-emp').value.toLowerCase();
  const a=document.getElementById('h-ano').value;
  const t=document.getElementById('h-txt').value.toLowerCase();
  const lista=HIST.filter(i=>
    (!e|(i.empresa||'').toLowerCase().includes(e))&&
    (!a|String(i.ano)===a)&&
    (!t|(i.empresa||'').toLowerCase().includes(t)||(i.descricao||'').toLowerCase().includes(t))
  );
  const tb=document.getElementById('tb-hist');if(!tb)return;
  tb.innerHTML=lista.map(i=>'<tr><td>'+( i.ano||'—')+'</td><td><b>'+(i.empresa||'—')+'</b></td><td>'+(i.valor?('R$ '+(i.valor/1e6).toFixed(1)+'M'):'—')+'</td><td>'+(i.empregos||'—')+'</td><td>'+bdg(i.fase||i.status)+'</td><td><a class="nu" href="'+(i.url||'#')+'" target="_blank">'+(i.fonte||'—')+'</a></td></tr>').join('')||'<tr><td colspan="6" class="vz">Sem resultados.</td></tr>';
}}
function limpHist(){{['h-emp','h-ano','h-txt'].forEach(id=>{{const el=document.getElementById(id);if(el)el.value=''}});renderHist();}}

function renderQuase(){{
  document.getElementById('lst-quase').innerHTML=
    QR.length?QR.map(n=>cardN(n,true)).join(''):'<div class="vz">Nenhuma notícia quase relevante.</div>';
}}

function renderGraf(){{
  const cfg={{responsive:true,displayModeBar:false}};
  const base={{font:{{family:'Segoe UI,system-ui',size:11}},paper_bgcolor:'#fff',plot_bgcolor:'#fff'}};

  Plotly.newPlot('g-rk',[{{
    x:RK.map(e=>e.valor_total/1e6).reverse(),y:RK.map(e=>e.empresa).reverse(),
    type:'bar',orientation:'h',marker:{{color:AZUL}},
    text:RK.map(e=>'R$ '+(e.valor_total/1e6).toFixed(0)+'M').reverse(),textposition:'outside'
  }}],{{...base,title:'Top Empresas por Valor (R$ M)',margin:{{l:180,r:70,t:40,b:40}},xaxis:{{title:'R$ Milhões'}}}},cfg);

  const anos=Object.keys(PA),aV=anos.map(a=>PA[a].valor/1e9),aQ=anos.map(a=>PA[a].investimentos);
  Plotly.newPlot('g-ano',[
    {{x:anos,y:aV,type:'bar',name:'Valor (R$ bi)',marker:{{color:OURO}},text:aV.map(v=>'R$ '+v.toFixed(1)+'bi'),textposition:'outside',yaxis:'y'}},
    {{x:anos,y:aQ,type:'scatter',mode:'lines+markers',name:'Qtd.',line:{{color:AZUL,width:2}},marker:{{size:7,color:AZUL}},yaxis:'y2'}}
  ],{{...base,title:'Investimentos por Ano',margin:{{l:60,r:60,t:40,b:40}},
     yaxis:{{title:'R$ Bilhões'}},yaxis2:{{title:'Quantidade',overlaying:'y',side:'right'}},
     legend:{{orientation:'h',y:-0.2}}}},cfg);

  const fN=Object.keys(FS),fV=Object.values(FS);
  if(fN.length){{
    Plotly.newPlot('g-fas',[{{x:fV,y:fN,type:'bar',orientation:'h',marker:{{color:AZUL}},text:fV,textposition:'outside'}}],
      {{...base,title:'Notícias por Fase',margin:{{l:140,r:40,t:40,b:40}}}},cfg);
  }} else {{
    document.getElementById('g-fas').innerHTML='<div class="vz" style="padding-top:80px">Sem notícias relevantes recentes.</div>';
  }}

  const cv=[CF.alta,CF.media,CF.baixa];
  if(cv.some(v=>v>0)){{
    Plotly.newPlot('g-cf',[{{
      values:cv,labels:['Alta ≥80% ('+CF.alta+'%)','Média ('+CF.media+'%)','Baixa ('+CF.baixa+'%)'],
      type:'pie',hole:0.4,
      marker:{{colors:[VERDE,OURO,'#dc2626'],line:{{color:'white',width:2}}}},textinfo:'percent'
    }}],{{...base,title:'Confiança — Média '+CF.mg+'%',margin:{{l:10,r:10,t:50,b:10}},
         showlegend:true,legend:{{orientation:'h',y:-0.2}}}},cfg);
  }} else {{
    document.getElementById('g-cf').innerHTML='<div class="vz" style="padding-top:80px">Sem dados de confiança.</div>';
  }}
}}

document.addEventListener('DOMContentLoaded',()=>{{
  popSel('r-emp',NR.flatMap(n=>n.empresas||[]));
  popSel('r-fas',NR.map(n=>n.fase).filter(Boolean));
  popSel('a-emp',ALL.flatMap(n=>n.empresas||[]));
  popSel('a-fas',ALL.map(n=>n.fase).filter(Boolean));
  popSel('h-emp',HIST.map(i=>i.empresa).filter(Boolean));
  popSel('h-ano',HIST.map(i=>String(i.ano)).filter(Boolean));
  renderRec();renderTodas();renderRanking();renderPorAno();renderHist();renderQuase();
}});
</script>
</body>
</html>"""

    # ── PDF ───────────────────────────────────────────

    def gerar_pdf(self):
        if not HAS_REPORTLAB:
            print("  PDF: ReportLab não instalado."); return None
        try:
            r  = self.resumo_recente()
            rh = self.resumo_historico()
            rk = self.ranking_historico()
            fn = self.fontes_recentes()
            cf = self.confianca_recente()
            pa = self.por_ano_historico()

            nome = self.pasta/f"relatorio_{self.data_geracao.strftime('%Y%m%d_%H%M%S')}.pdf"
            doc  = SimpleDocTemplate(str(nome),pagesize=A4,
                                     rightMargin=2*cm,leftMargin=2*cm,
                                     topMargin=2*cm,bottomMargin=2*cm)

            styles=getSampleStyleSheet()
            AZ_=colors.HexColor("#1a3a5c"); OU_=colors.HexColor("#e8a020")
            CL_=colors.HexColor("#f4f7fb"); CI_=colors.HexColor("#6b7280")

            t_tit=ParagraphStyle("tt",parent=styles["Heading1"],fontSize=18,textColor=AZ_,alignment=1,spaceAfter=4,fontName="Helvetica-Bold")
            t_sub=ParagraphStyle("ts",parent=styles["Normal"],fontSize=9,textColor=CI_,alignment=1,spaceAfter=2)
            t_sec=ParagraphStyle("tc",parent=styles["Heading2"],fontSize=11,textColor=AZ_,spaceBefore=14,spaceAfter=8,fontName="Helvetica-Bold")
            t_bdy=ParagraphStyle("tb",parent=styles["Normal"],fontSize=8,textColor=colors.HexColor("#374151"),leading=13)

            def hr(): return HRFlowable(width="100%",thickness=1.5,color=OU_,spaceAfter=8)

            def tbl(data,ws=None):
                t=Table(data,colWidths=ws,repeatRows=1)
                t.setStyle(TableStyle([
                    ("BACKGROUND",(0,0),(-1,0),AZ_),("TEXTCOLOR",(0,0),(-1,0),colors.white),
                    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8),
                    ("ALIGN",(0,0),(-1,-1),"LEFT"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                    ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,CL_]),
                    ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#dde3ec")),
                    ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
                    ("LEFTPADDING",(0,0),(-1,-1),7),("RIGHTPADDING",(0,0),(-1,-1),7),
                ]))
                return t

            story=[]
            story+=[Spacer(1,1*cm),
                    Paragraph("Monitor de Investimentos Privados",t_tit),
                    Paragraph("SEDECON · Prefeitura de Contagem MG",t_sub),
                    Paragraph(f"Gerado em {self.data_geracao.strftime('%d/%m/%Y %H:%M')}",t_sub),
                    Spacer(1,.4*cm),hr(),
                    Paragraph("Sumário Executivo",t_sec)]

            story.append(tbl([
                ["Indicador","Valor"],
                ["Notícias relevantes (recente)", str(r["noticias_relevantes"])],
                ["Empregos detectados",           f"{r['novos_empregos']:,}"],
                ["Valor monitorado",              f"R$ {r['valor_total']/1e6:.1f} M"],
                ["Confiança média",               f"{r['confianca_media']}%"],
                ["Investimentos histórico",        str(rh["total_investimentos"])],
                ["Valor total histórico",          f"R$ {rh['total_valor']/1e9:.2f} bi"],
                ["Empresas únicas",                str(rh["empresas_unicas"])],
                ["Período histórico",              rh["periodo"]],
            ],ws=[11*cm,5*cm]))

            story+=[Spacer(1,.4*cm),Paragraph("Ranking de Empresas — Histórico",t_sec)]
            rk_rows=[["#","Empresa","Invest.","Valor R$M"]]
            for i,e in enumerate(rk,1):
                rk_rows.append([str(i),e["empresa"][:30],str(e["investimentos"]),f"{e['valor_total']/1e6:.1f}"])
            story.append(tbl(rk_rows,ws=[1*cm,9*cm,2.5*cm,3*cm]) if len(rk_rows)>1 else Paragraph("Sem dados.",t_bdy))

            story+=[Spacer(1,.4*cm),Paragraph("Investimentos por Ano",t_sec)]
            pa_rows=[["Ano","Qtd.","Valor total"]]
            for a,d in pa.items():
                pa_rows.append([a,str(d["investimentos"]),f"R$ {d['valor']/1e9:.2f} bi"])
            story.append(tbl(pa_rows,ws=[3*cm,4*cm,8.5*cm]) if len(pa_rows)>1 else Paragraph("Sem dados.",t_bdy))

            story+=[Spacer(1,.4*cm),Paragraph("Fontes",t_sec)]
            tg=rg=0
            fn_rows=[["Fonte","Total","Relev.","Precisão","Confiança"]]
            for f in sorted(fn):
                d=fn[f]; tg+=d["total"]; rg+=d["relevantes"]
                fn_rows.append([f[:20],str(d["total"]),str(d["relevantes"]),f"{d['taxa']}%",f"{d['confianca']}%"])
            fn_rows.append(["TOTAL",str(tg),str(rg),f"{round(rg/tg*100 if tg else 0,1)}%","—"])
            story.append(tbl(fn_rows,ws=[5*cm,2*cm,2*cm,2.5*cm,4*cm]))

            story+=[Spacer(1,.4*cm),Paragraph("Confiança dos Dados",t_sec)]
            story.append(tbl([
                ["Nível","Percentual"],
                ["Alta (≥ 80%)",   f"{cf['alta']}%"],
                ["Média (50–80%)", f"{cf['media']}%"],
                ["Baixa (< 50%)",  f"{cf['baixa']}%"],
                ["Média geral",    f"{cf['mg']}%"],
            ],ws=[11*cm,5*cm]))

            story+=[hr(),Paragraph("Critérios de relevância",t_sec),
                    Paragraph("Pontuação mínima de 30 pontos · menção explícita a Contagem · empresa identificada na lista monitorada.",t_bdy)]

            doc.build(story)
            return nome
        except Exception as e:
            import traceback; traceback.print_exc()
            print(f"  PDF erro: {e}"); return None

    # ── SALVAR ────────────────────────────────────────

    def salvar_txt(self):
        p=self.pasta/f"relatorio_{self.data_geracao.strftime('%Y%m%d_%H%M%S')}.txt"
        p.write_text(self.gerar_relatorio_texto(),encoding="utf-8"); return p

    def salvar_json(self):
        dados={
            "data_geracao":       self.data_geracao.isoformat(),
            "resumo_recente":     self.resumo_recente(),
            "resumo_historico":   self.resumo_historico(),
            "ranking_historico":  self.ranking_historico(),
            "por_ano_historico":  self.por_ano_historico(),
            "fases_recentes":     self.fases_recentes(),
            "fontes_recentes":    self.fontes_recentes(),
            "quase_relevantes":   self.quase_relevantes(),
            "confianca_recente":  self.confianca_recente(),
        }
        p=self.pasta/f"relatorio_{self.data_geracao.strftime('%Y%m%d_%H%M%S')}.json"
        p.write_text(json.dumps(dados,indent=4,ensure_ascii=False),encoding="utf-8"); return p

    def salvar_html(self):
        p=self.pasta/f"relatorio_{self.data_geracao.strftime('%Y%m%d_%H%M%S')}.html"
        p.write_text(self.gerar_html(),encoding="utf-8"); return p

    # ── GERAR TODOS ───────────────────────────────────

    def gerar_todos(self):
        print("\n"+"="*60+"\n  GERANDO RELATÓRIOS\n"+"="*60)
        gerados=[]
        for nome,fn in [("TXT",self.salvar_txt),("JSON",self.salvar_json),
                        ("HTML",self.salvar_html),("PDF",self.gerar_pdf)]:
            try:
                p=fn()
                if p: print(f"  ✓ {nome}: {p}"); gerados.append(p)
            except Exception as e: print(f"  ✗ {nome}: {e}")
        try: gerados+=self.gerar_graficos()
        except Exception as e: print(f"  ✗ Gráficos: {e}")
        print("="*60+f"\n  {len(gerados)} arquivo(s) gerado(s).\n"+"="*60+"\n")
        return gerados

    def imprimir_relatorio(self):
        print(self.gerar_relatorio_texto())


if __name__ == "__main__":
    GeradorRelatorio().gerar_todos()


 
