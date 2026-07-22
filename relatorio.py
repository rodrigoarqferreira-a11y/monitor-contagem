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

    def resumo_historico(self):
        h    = self._historico()
        tv   = sum(float(i.get("valor",0) or 0) for i in h)
        emp  = set(i.get("empresa","") for i in h if i.get("empresa"))
        anos = set(i.get("ano",0) for i in h if i.get("ano"))
        return {
            "total_investimentos": len(h),
            "total_valor":         tv,
            "empresas_unicas":     len(emp),
            "periodo":             f"{min(anos)} – {max(anos)}" if anos else "—",
        }

    def ranking_historico(self, top=15):
        h    = self._historico()
        cnt  = Counter(); vals = defaultdict(float)
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

    def gerar_relatorio_texto(self):
        r  = self.resumo_recente()
        rh = self.resumo_historico()
        rk = self.ranking_historico()
        pa = self.por_ano_historico()
        L  = ["="*70,"RELATÓRIO DE INVESTIMENTOS PRIVADOS — CONTAGEM MG",
              "SEDECON","="*70,
              f"Gerado em: {self.data_geracao.strftime('%d/%m/%Y %H:%M')}",
              "\n=== MONITORAMENTO RECENTE ===",
              f"  Notícias relevantes : {r['noticias_relevantes']}",
              f"  Novos empregos      : {r['novos_empregos']:,}",
              f"  Valor detectado     : R$ {r['valor_total']/1e6:.1f} M",
              f"  Confiança média     : {r['confianca_media']}%",
              "\n=== HISTÓRICO 2021-2026 ===",
              f"  Total investimentos : {rh['total_investimentos']}",
              f"  Valor total         : R$ {rh['total_valor']/1e9:.2f} bi",
              f"  Empresas únicas     : {rh['empresas_unicas']}",
              f"  Período             : {rh['periodo']}",
              "\n=== RANKING EMPRESAS ==="]
        for i,e in enumerate(rk,1):
            L.append(f"  {i:>2}. {e['empresa'][:35]:<36} R$ {e['valor_total']/1e6:>8.1f}M  ({e['investimentos']} inv.)")
        L.append("\n=== POR ANO ===")
        for a,d in pa.items():
            L.append(f"  {a}: {d['investimentos']} invest. — R$ {d['valor']/1e9:.2f} bi")
        return "\n".join(L)

    def gerar_graficos(self):
        if not HAS_MATPLOTLIB: return []
        arqs=[]; AZUL="#037482"; OURO="#D2DD68"; CIANO="#0EB9CD"; LARANJA="#FF7A01"

        def salvar(nome):
            p=self.pasta/nome
            plt.savefig(p,dpi=180,bbox_inches="tight")
            plt.close(); arqs.append(p); print(f"  ✓ {p}")

        try:
            rk=self.ranking_historico(10)
            pa=self.por_ano_historico()
            fs=self.fases_recentes()
            cf=self.confianca_recente()

            if rk:
                fig,ax=plt.subplots(figsize=(10,6))
                fig.patch.set_facecolor("#035863")
                ax.set_facecolor("#035863")
                nomes=[e["empresa"][:28] for e in rk]
                vals=[e["valor_total"]/1e6 for e in rk]
                bars=ax.barh(nomes,vals,color=CIANO,edgecolor="none")
                for b,v in zip(bars,vals):
                    ax.text(b.get_width()+2,b.get_y()+b.get_height()/2,
                            f"R$ {v:.0f}M",va="center",fontsize=8,color=OURO,fontweight="bold")
                ax.set_xlabel("R$ Milhões",color="white")
                ax.set_title("Top Empresas por Valor Investido",fontsize=12,
                             fontweight="bold",color=OURO,pad=14)
                ax.tick_params(colors="white")
                ax.spines[["top","right","left","bottom"]].set_visible(False)
                ax.xaxis.label.set_color("white")
                plt.tight_layout(); salvar("grafico_ranking.png")

            if pa:
                fig,ax=plt.subplots(figsize=(10,5))
                fig.patch.set_facecolor("#035863")
                ax.set_facecolor("#035863")
                anos=list(pa.keys()); vals=[pa[a]["valor"]/1e9 for a in anos]
                bars=ax.bar(anos,vals,color=CIANO,edgecolor="none",width=0.5)
                for b,v in zip(bars,vals):
                    ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.02,
                            f"R$ {v:.1f}bi",ha="center",fontsize=8,
                            fontweight="bold",color=OURO)
                ax.set_ylabel("R$ Bilhões",color="white")
                ax.set_title("Investimentos por Ano — Contagem MG",fontsize=12,
                             fontweight="bold",color=OURO,pad=14)
                ax.tick_params(colors="white")
                ax.spines[["top","right","left","bottom"]].set_visible(False)
                plt.tight_layout(); salvar("grafico_por_ano.png")

            if fs:
                fig,ax=plt.subplots(figsize=(9,4))
                fig.patch.set_facecolor("#035863")
                ax.set_facecolor("#035863")
                nomes=list(fs.keys()); vals=list(fs.values())
                bars=ax.barh(nomes,vals,color=LARANJA,edgecolor="none")
                for b,v in zip(bars,vals):
                    ax.text(b.get_width()+.05,b.get_y()+b.get_height()/2,
                            str(v),va="center",fontweight="bold",color=OURO)
                ax.set_xlabel("Notícias",color="white")
                ax.set_title("Notícias Recentes por Fase",fontsize=12,
                             fontweight="bold",color=OURO,pad=14)
                ax.tick_params(colors="white")
                ax.spines[["top","right","left","bottom"]].set_visible(False)
                plt.tight_layout(); salvar("grafico_fases.png")

            cv=[cf["alta"],cf["media"],cf["baixa"]]
            if any(v>0 for v in cv):
                fig,ax=plt.subplots(figsize=(6,6))
                fig.patch.set_facecolor("#035863")
                ax.set_facecolor("#035863")
                ax.pie(cv,
                       labels=[f"Alta\n{cf['alta']}%",f"Média\n{cf['media']}%",f"Baixa\n{cf['baixa']}%"],
                       colors=[CIANO,OURO,LARANJA],
                       startangle=90,wedgeprops={"edgecolor":"#035863","linewidth":3},
                       textprops={"color":"white","fontsize":10,"fontweight":"bold"})
                ax.set_title(f"Confiança dos Dados — Média {cf['mg']}%",
                             fontsize=12,fontweight="bold",color=OURO,pad=14)
                plt.tight_layout(); salvar("grafico_confianca.png")

        except Exception as e:
            print(f"  Erro gráficos: {e}")
        return arqs

    def gerar_html(self):
        r    = self.resumo_recente()
        rh   = self.resumo_historico()
        rk   = self.ranking_historico()
        pa   = self.por_ano_historico()
        fs   = self.fases_recentes()
        fn   = self.fontes_recentes()
        cf   = self.confianca_recente()
        qr   = self.quase_relevantes()
        nrs  = self._relevantes()
        alln = self._todas()
        hist = self.lista_historico()

        njs  = json.dumps(nrs,   ensure_ascii=False)
        ajs  = json.dumps(alln,  ensure_ascii=False)
        hjs  = json.dumps(hist,  ensure_ascii=False)
        rkjs = json.dumps(rk,    ensure_ascii=False)
        pajs = json.dumps(pa,    ensure_ascii=False)
        fsjs = json.dumps(fs,    ensure_ascii=False)
        qjs  = json.dumps(qr,    ensure_ascii=False)
        cfjs = json.dumps(cf,    ensure_ascii=False)

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

        vm  = r["valor_total"]/1e6
        vhb = rh["total_valor"]/1e9

        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Monitor de Investimentos — Contagem MG</title>
<script src="https://cdn.plot.ly/plotly-2.30.0.min.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{{
  --teal-dark:#035863;--teal:#037482;--teal-light:#0EB9CD;
  --lime:#D2DD68;--orange:#FF7A01;--white:#ffffff;
  --bg:#f0f4fa;--br:#ffffff;--bo:#dde3ec;--tx:#1f2937;--ci:#6b7280;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter','Segoe UI',sans-serif;background:var(--bg);color:var(--tx);font-size:14px}}

/* ── HEADER ── */
.hdr{{background:var(--teal);position:relative;overflow:hidden}}
.hdr-inner{{display:flex;align-items:stretch;min-height:120px}}
.hdr-logo{{background:var(--teal-dark);padding:20px 24px;display:flex;align-items:center;
            justify-content:center;min-width:150px;flex-shrink:0}}
.hdr-logo img{{max-height:72px;max-width:120px;object-fit:contain}}
.hdr-logo .logo-fb{{background:rgba(14,185,205,.15);border:1.5px solid rgba(14,185,205,.4);
  border-radius:8px;width:110px;height:68px;display:flex;align-items:center;justify-content:center;
  font-size:10px;color:var(--teal-light);text-align:center;font-weight:700;letter-spacing:.5px}}
.hdr-body{{flex:1;padding:22px 28px;display:flex;flex-direction:column;justify-content:center}}
.hdr-sup{{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:2px;
           color:var(--teal-light);margin-bottom:5px}}
.hdr-title{{font-size:20px;font-weight:800;color:var(--white);line-height:1.2;margin-bottom:5px}}
.hdr-sub{{font-size:11px;color:rgba(255,255,255,.6);font-weight:400}}
.hdr-right{{padding:20px 24px;display:flex;flex-direction:column;align-items:flex-end;
             justify-content:center;gap:8px;flex-shrink:0}}
.bdg-auto{{background:var(--lime);color:#1a3a00;font-size:9px;font-weight:800;
            padding:4px 12px;border-radius:20px;text-transform:uppercase;letter-spacing:1px}}
.hdr-date{{font-size:10px;color:rgba(255,255,255,.5);font-weight:500}}
.hdr-stripe{{height:3px;background:linear-gradient(90deg,var(--teal-dark) 0%,var(--teal-light) 40%,var(--lime) 72%,var(--orange) 100%)}}

/* ── MÉTRICAS ── */
.metrics{{display:grid;grid-template-columns:repeat(6,1fr);background:var(--teal-dark)}}
.mcard{{padding:14px 16px;text-align:center;border-right:1px solid rgba(14,185,205,.2);position:relative}}
.mcard:last-child{{border-right:none}}
.mcard::before{{content:"";position:absolute;top:0;left:0;right:0;height:2px;background:transparent}}
.mcard.ml::before{{background:var(--lime)}}.mcard.mc::before{{background:var(--teal-light)}}.mcard.mo::before{{background:var(--orange)}}
.mval{{font-size:22px;font-weight:800;color:var(--white);line-height:1;margin-bottom:3px}}
.mval.lime{{color:var(--lime)}}.mval.ciano{{color:var(--teal-light)}}.mval.oran{{color:var(--orange)}}
.mlbl{{font-size:8px;text-transform:uppercase;letter-spacing:.8px;color:rgba(255,255,255,.45);font-weight:600}}

/* ── ABAS ── */
.tabs-w{{background:#024f5a;border-bottom:2px solid var(--teal-dark)}}
.tabs{{display:flex;padding:0 24px;flex-wrap:wrap}}
.tab{{padding:11px 18px;font-size:11px;font-weight:600;color:rgba(255,255,255,.45);cursor:pointer;
       border-bottom:3px solid transparent;margin-bottom:-2px;transition:all .15s;white-space:nowrap;letter-spacing:.3px}}
.tab:hover{{color:rgba(255,255,255,.8)}}
.tab.on{{color:var(--lime);border-bottom-color:var(--lime)}}

/* ── PAINÉIS ── */
.pan{{display:none;padding:22px 28px}}.pan.on{{display:block}}
.sec{{margin-bottom:24px}}
.stit{{font-size:.88rem;font-weight:700;color:var(--teal);padding-bottom:8px;
        border-bottom:2px solid var(--lime);margin-bottom:14px}}
.g2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.g3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}}
.sbox{{background:var(--teal-dark);border-radius:10px;padding:18px;text-align:center}}
.sval{{font-size:1.8rem;font-weight:800;color:var(--lime);line-height:1}}
.slbl{{font-size:.65rem;color:rgba(255,255,255,.55);text-transform:uppercase;letter-spacing:.6px;margin-top:4px}}

/* ── FILTROS ── */
.flt{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px;align-items:center}}
.flt label{{font-size:.75rem;font-weight:600;color:var(--teal)}}
.flt select,.flt input{{padding:6px 10px;border:1.5px solid var(--teal-light);border-radius:6px;
  font-size:.8rem;background:var(--br);color:var(--tx);min-width:140px;outline:none}}
.flt select:focus,.flt input:focus{{border-color:var(--teal)}}
.btnx{{padding:6px 14px;background:var(--teal);color:var(--white);border:none;border-radius:6px;
        font-size:.78rem;font-weight:600;cursor:pointer;transition:background .15s}}
.btnx:hover{{background:var(--teal-dark)}}

/* ── TABELAS ── */
.twrap{{overflow-x:auto}}
table{{width:100%;border-collapse:collapse;font-size:.82rem}}
th{{background:var(--teal);color:var(--white);padding:9px 12px;text-align:left;
     font-size:.73rem;text-transform:uppercase;letter-spacing:.4px;white-space:nowrap}}
td{{padding:8px 12px;border-bottom:1px solid var(--bo);vertical-align:top}}
tr:hover td{{background:#e8f4f6}}
.tr-tot td{{background:#e0f0f2;font-weight:600;color:var(--teal-dark)}}

/* ── CARDS NOTÍCIA ── */
.nc{{background:var(--br);border:1px solid var(--bo);border-radius:8px;padding:13px;
      margin-bottom:9px;border-left:4px solid var(--teal)}}
.nc.q{{border-left-color:var(--orange)}}
.nt{{font-weight:700;font-size:.88rem;color:var(--teal-dark);margin-bottom:5px;line-height:1.4}}
.nm{{font-size:.72rem;color:var(--ci);display:flex;gap:8px;flex-wrap:wrap;margin-bottom:4px}}
.nu{{font-size:.72rem;color:var(--teal);text-decoration:none;word-break:break-all}}
.nu:hover{{text-decoration:underline;color:var(--teal-dark)}}
.bdg{{display:inline-block;padding:2px 7px;border-radius:11px;font-size:.66rem;font-weight:700;text-transform:uppercase}}
.bv{{background:#dcfce7;color:#15803d}}.bo2{{background:#fef9c3;color:#a16207}}
.bc{{background:#f1f5f9;color:#475569}}.ba{{background:#dbeafe;color:#1d4ed8}}
.bor{{background:#fff3e0;color:#e65100}}

/* ── GRÁFICOS ── */
.graf{{height:300px;background:var(--teal-dark);border-radius:8px;margin-bottom:14px}}
.vz{{text-align:center;padding:32px;color:var(--ci);font-style:italic}}

footer{{background:var(--teal-dark);color:rgba(255,255,255,.4);text-align:center;
         padding:14px;font-size:.72rem;margin-top:14px;border-top:3px solid var(--teal-light)}}
@media(max-width:768px){{
  .hdr-inner{{flex-wrap:wrap}}.hdr-logo{{min-width:100%;justify-content:flex-start}}
  .metrics{{grid-template-columns:repeat(3,1fr)}}.g2,.g3{{grid-template-columns:1fr}}
  .pan{{padding:16px}}.tabs{{overflow-x:auto}}
}}
</style>
</head>
<body>

<!-- HEADER -->
<div class="hdr">
  <div class="hdr-inner">
    <div class="hdr-logo">
      <img src="../dados/logo_sedecon_2.png" alt="SEDECON"
           onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">
      <div class="logo-fb" style="display:none">LOGO<br>SEDECON</div>
    </div>
    <div class="hdr-body">
    <div class="hdr-sup">Prefeitura de Contagem · MG</div>
      <div class="hdr-title">Monitor de Investimentos Privados</div>
      <div class="hdr-sub">SEDECON · Superintendência de Inovação e Informações Estratégicas</div>
    </div>
    <div class="hdr-right">
      <span class="bdg-auto">⚡ Automático</span>
      <span class="hdr-date">{self.data_geracao.strftime('%d/%m/%Y · %H:%M')}</span>
    </div>
  </div>
  <div class="hdr-stripe"></div>
</div>

<!-- MÉTRICAS -->
<div class="metrics">
  <div class="mcard ml">
    <div class="mval lime">{rh['total_investimentos']}</div>
    <div class="mlbl">Investimentos</div>
  </div>
  <div class="mcard ml">
    <div class="mval lime">{rh['empresas_unicas']}</div>
    <div class="mlbl">Empresas</div>
  </div>
  <div class="mcard mc">
    <div class="mval ciano">{r['novos_empregos']:,}</div>
    <div class="mlbl">Empregos gerados</div>
  </div>
  <div class="mcard mc">
    <div class="mval ciano">R$ {vhb:.1f}bi</div>
    <div class="mlbl">Valor total</div>
  </div>
  <div class="mcard mo">
    <div class="mval oran">{r['confianca_media']}%</div>
    <div class="mlbl">Confiança média</div>
  </div>
  <div class="mcard">
    <div class="mval">{r['noticias_relevantes']}</div>
    <div class="mlbl">Notícias relevantes</div>
  </div>
</div>

<!-- ABAS -->
<div class="tabs-w">
  <div class="tabs">
    <div class="tab on"  onclick="aba('recente',this)">🔔 Monitoramento Recente</div>
    <div class="tab"     onclick="aba('historico',this)">📋 Histórico 2021–2026</div>
    <div class="tab"     onclick="aba('graficos',this)">📈 Gráficos</div>
    <div class="tab"     onclick="aba('todas',this)">🗂 Todas as Notícias</div>
    <div class="tab"     onclick="aba('fontes',this)">📰 Fontes</div>
    <div class="tab"     onclick="aba('quase',this)">🔍 Quase Relevantes</div>
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
    <div class="sec"><div class="stit">✅ Confiança dos dados</div><div class="graf" id="g-cf"></div></div>
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
    <p style="color:var(--ci);font-size:.8rem;margin-bottom:14px">Pontuação ≥ 30, empresa identificada, sem menção explícita a Contagem. Possível impacto regional.</p>
    <div id="lst-quase"></div>
  </div>
</div>

<footer>Monitor de Investimentos Privados · SEDECON · Prefeitura de Contagem MG · {self.data_geracao.strftime('%d/%m/%Y %H:%M')} · Gerado automaticamente</footer>

<script>
const NR={njs};const ALL={ajs};const HIST={hjs};
const RK={rkjs};const PA={pajs};const FS={fsjs};
const QR={qjs};const CF={cfjs};
const TEAL='#037482',LIME='#D2DD68',CIANO='#0EB9CD',ORAN='#FF7A01',DARK='#035863';

let grafOk=false;
function aba(id,btn){{
  document.querySelectorAll('.pan').forEach(p=>p.classList.remove('on'));
  document.querySelectorAll('.tab').forEach(b=>b.classList.remove('on'));
  document.getElementById('p-'+id).classList.add('on');
  btn.classList.add('on');
  if(id==='graficos'&&!grafOk){{grafOk=true;renderGraf();}}
}}

function bdg(f){{
  const m={{'Anunciado':'ba','Construção':'bo2','Operação':'bv','Expansão':'bv',
             'Licenciamento':'bc','Contratação':'bc','Negociação':'bc','Em operação':'bv','Em construção':'bo2'}};
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
  const l=NR.filter(n=>(!e||(n.empresas||[]).join(' ').toLowerCase().includes(e))&&(!f|(n.fase||'').toLowerCase()===f)&&(!t|(n.titulo||'').toLowerCase().includes(t)));
  document.getElementById('lst-rec').innerHTML=l.length?l.map(n=>cardN(n,false)).join(''):'<div class="vz">Nenhuma notícia relevante encontrada.</div>';
}}
function limpRec(){{['r-emp','r-fas','r-txt'].forEach(id=>{{const el=document.getElementById(id);if(el)el.value=''}});renderRec();}}

function renderTodas(){{
  const e=document.getElementById('a-emp').value.toLowerCase();
  const f=document.getElementById('a-fas').value.toLowerCase();
  const r=document.getElementById('a-rel').value;
  const t=document.getElementById('a-txt').value.toLowerCase();
  const l=ALL.filter(n=>(!e||(n.empresas||[]).join(' ').toLowerCase().includes(e))&&(!f|(n.fase||'').toLowerCase()===f)&&(!r||(r==='s'?n.relevante:!n.relevante))&&(!t|(n.titulo||'').toLowerCase().includes(t)));
  document.getElementById('lst-todas').innerHTML=l.length?l.map(n=>cardN(n,false)).join(''):'<div class="vz">Nenhuma notícia com esses filtros.</div>';
}}
function limpTodas(){{['a-emp','a-fas','a-rel','a-txt'].forEach(id=>{{const el=document.getElementById(id);if(el)el.value=''}});renderTodas();}}

function renderRanking(){{
  const tb=document.getElementById('tb-rk');if(!tb)return;
  tb.innerHTML=RK.map((e,i)=>'<tr><td><b>'+(i+1)+'</b></td><td>'+e.empresa+'</td><td style="text-align:center">'+e.investimentos+'</td><td><b>R$ '+(e.valor_total/1e6).toFixed(1)+'M</b></td></tr>').join('')||'<tr><td colspan="4" class="vz">Sem dados.</td></tr>';
}}

function renderPorAno(){{
  const tb=document.getElementById('tb-ano');if(!tb)return;
  tb.innerHTML=Object.entries(PA).map(([a,d])=>'<tr><td><b>'+a+'</b></td><td style="text-align:center">'+d.investimentos+'</td><td><b>R$ '+(d.valor/1e9).toFixed(2)+'bi</b></td></tr>').join('')||'<tr><td colspan="3" class="vz">Sem dados.</td></tr>';
}}

function renderHist(){{
  const e=document.getElementById('h-emp').value.toLowerCase();
  const a=document.getElementById('h-ano').value;
  const t=document.getElementById('h-txt').value.toLowerCase();
  const l=HIST.filter(i=>(!e|(i.empresa||'').toLowerCase().includes(e))&&(!a|String(i.ano)===a)&&(!t|(i.empresa||'').toLowerCase().includes(t)||(i.descricao||'').toLowerCase().includes(t)));
  const tb=document.getElementById('tb-hist');if(!tb)return;
  tb.innerHTML=l.map(i=>'<tr><td>'+( i.ano||'—')+'</td><td><b>'+(i.empresa||'—')+'</b></td><td>'+(i.valor?('R$ '+(i.valor/1e6).toFixed(1)+'M'):'—')+'</td><td>'+(i.empregos||'—')+'</td><td>'+bdg(i.fase||i.status)+'</td><td><a class="nu" href="'+(i.url||'#')+'" target="_blank">'+(i.fonte||'—')+'</a></td></tr>').join('')||'<tr><td colspan="6" class="vz">Sem resultados.</td></tr>';
}}
function limpHist(){{['h-emp','h-ano','h-txt'].forEach(id=>{{const el=document.getElementById(id);if(el)el.value=''}});renderHist();}}

function renderQuase(){{
  document.getElementById('lst-quase').innerHTML=QR.length?QR.map(n=>cardN(n,true)).join(''):'<div class="vz">Nenhuma notícia quase relevante.</div>';
}}

function renderGraf(){{
  const cfg={{responsive:true,displayModeBar:false}};
  const base={{font:{{family:'Inter,Segoe UI,sans-serif',size:11,color:'#ffffff'}},
               paper_bgcolor:DARK,plot_bgcolor:DARK}};

  Plotly.newPlot('g-rk',[{{
    x:RK.map(e=>e.valor_total/1e6).reverse(),
    y:RK.map(e=>e.empresa).reverse(),
    type:'bar',orientation:'h',marker:{{color:CIANO}},
    text:RK.map(e=>'R$ '+(e.valor_total/1e6).toFixed(0)+'M').reverse(),
    textposition:'outside',textfont:{{color:LIME}}
  }}],{{...base,margin:{{l:170,r:80,t:30,b:40}},
       xaxis:{{title:'R$ Milhões',color:'white',gridcolor:'rgba(255,255,255,0.1)'}},
       yaxis:{{color:'white'}}}},cfg);

  const anos=Object.keys(PA),aV=anos.map(a=>PA[a].valor/1e9),aQ=anos.map(a=>PA[a].investimentos);
  Plotly.newPlot('g-ano',[
    {{x:anos,y:aV,type:'bar',name:'Valor (R$ bi)',marker:{{color:CIANO}},
      text:aV.map(v=>'R$ '+v.toFixed(1)+'bi'),textposition:'outside',
      textfont:{{color:LIME}},yaxis:'y'}},
    {{x:anos,y:aQ,type:'scatter',mode:'lines+markers',name:'Qtd.',
      line:{{color:LIME,width:2.5}},marker:{{size:7,color:LIME}},yaxis:'y2'}}
  ],{{...base,margin:{{l:50,r:50,t:30,b:40}},
     yaxis:{{title:'R$ Bilhões',color:'white',gridcolor:'rgba(255,255,255,0.1)'}},
     yaxis2:{{title:'Quantidade',overlaying:'y',side:'right',color:'white'}},
     legend:{{orientation:'h',y:-0.25,font:{{color:'white'}}}}}},cfg);

  const fN=Object.keys(FS),fV=Object.values(FS);
  if(fN.length){{
    Plotly.newPlot('g-fas',[{{x:fV,y:fN,type:'bar',orientation:'h',
      marker:{{color:ORAN}},text:fV,textposition:'outside',textfont:{{color:LIME}}
    }}],{{...base,margin:{{l:140,r:50,t:30,b:40}},
         xaxis:{{color:'white',gridcolor:'rgba(255,255,255,0.1)'}},yaxis:{{color:'white'}}}},cfg);
  }} else {{
    document.getElementById('g-fas').innerHTML='<div class="vz" style="color:rgba(255,255,255,0.4);padding-top:80px">Sem notícias relevantes recentes.</div>';
  }}

  const cv=[CF.alta,CF.media,CF.baixa];
  if(cv.some(v=>v>0)){{
    Plotly.newPlot('g-cf',[{{
      values:cv,
      labels:['Alta ≥80% ('+CF.alta+'%)','Média ('+CF.media+'%)','Baixa ('+CF.baixa+'%)'],
      type:'pie',hole:0.42,
      marker:{{colors:[CIANO,LIME,ORAN],line:{{color:DARK,width:3}}}},
      textinfo:'percent',textfont:{{color:'white',size:12}}
    }}],{{...base,margin:{{l:10,r:10,t:40,b:10}},
         title:{{text:'Média '+CF.mg+'%',font:{{color:LIME,size:13}}}},
         showlegend:true,legend:{{orientation:'h',y:-0.2,font:{{color:'white'}}}}}},cfg);
  }} else {{
    document.getElementById('g-cf').innerHTML='<div class="vz" style="color:rgba(255,255,255,0.4);padding-top:80px">Sem dados de confiança ainda.</div>';
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
            TEAL_=colors.HexColor("#037482"); LIME_=colors.HexColor("#D2DD68")
            DARK_=colors.HexColor("#035863"); CI_=colors.HexColor("#6b7280")
            CL_  =colors.HexColor("#e0f0f2")

            t_tit=ParagraphStyle("tt",parent=styles["Heading1"],fontSize=18,textColor=TEAL_,alignment=1,spaceAfter=4,fontName="Helvetica-Bold")
            t_sub=ParagraphStyle("ts",parent=styles["Normal"],fontSize=9,textColor=CI_,alignment=1,spaceAfter=2)
            t_sec=ParagraphStyle("tc",parent=styles["Heading2"],fontSize=11,textColor=TEAL_,spaceBefore=14,spaceAfter=8,fontName="Helvetica-Bold")
            t_bdy=ParagraphStyle("tb",parent=styles["Normal"],fontSize=8,textColor=colors.HexColor("#374151"),leading=13)

            def hr(): return HRFlowable(width="100%",thickness=2,color=LIME_,spaceAfter=8)
            def tbl(data,ws=None):
                t=Table(data,colWidths=ws,repeatRows=1)
                t.setStyle(TableStyle([
                    ("BACKGROUND",(0,0),(-1,0),TEAL_),("TEXTCOLOR",(0,0),(-1,0),colors.white),
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
                    Spacer(1,.4*cm),hr(),Paragraph("Sumário Executivo",t_sec)]
            story.append(tbl([["Indicador","Valor"],
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
            tg=rg=0; fn_rows=[["Fonte","Total","Relev.","Precisão","Confiança"]]
            for f in sorted(fn):
                d=fn[f]; tg+=d["total"]; rg+=d["relevantes"]
                fn_rows.append([f[:20],str(d["total"]),str(d["relevantes"]),f"{d['taxa']}%",f"{d['confianca']}%"])
            fn_rows.append(["TOTAL",str(tg),str(rg),f"{round(rg/tg*100 if tg else 0,1)}%","—"])
            story.append(tbl(fn_rows,ws=[5*cm,2*cm,2*cm,2.5*cm,4*cm]))

            story+=[hr(),Paragraph("Critérios de relevância",t_sec),
                    Paragraph("Pontuação mínima de 30 pontos · menção explícita a Contagem · empresa identificada na lista monitorada.",t_bdy)]
            doc.build(story); return nome
        except Exception as e:
            import traceback; traceback.print_exc(); print(f"  PDF erro: {e}"); return None

    def salvar_txt(self):
        p=self.pasta/f"relatorio_{self.data_geracao.strftime('%Y%m%d_%H%M%S')}.txt"
        p.write_text(self.gerar_relatorio_texto(),encoding="utf-8"); return p

    def salvar_json(self):
        dados={
            "data_geracao":      self.data_geracao.isoformat(),
            "resumo_recente":    self.resumo_recente(),
            "resumo_historico":  self.resumo_historico(),
            "ranking_historico": self.ranking_historico(),
            "por_ano_historico": self.por_ano_historico(),
            "fases_recentes":    self.fases_recentes(),
            "fontes_recentes":   self.fontes_recentes(),
            "quase_relevantes":  self.quase_relevantes(),
            "confianca_recente": self.confianca_recente(),
        }
        p=self.pasta/f"relatorio_{self.data_geracao.strftime('%Y%m%d_%H%M%S')}.json"
        p.write_text(json.dumps(dados,indent=4,ensure_ascii=False),encoding="utf-8"); return p

    def salvar_html(self):
        html=self.gerar_html()
        p=self.pasta/f"relatorio_{self.data_geracao.strftime('%Y%m%d_%H%M%S')}.html"
        p.write_text(html,encoding="utf-8"); return p

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
              

