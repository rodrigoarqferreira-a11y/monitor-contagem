"""
====================================================
RELATORIO.PY
Monitor de Investimentos Privados — SEDECON
Prefeitura de Contagem MG
====================================================
"""

import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from banco import Banco

# ─────────────────────────────────────────────────
# DEPENDÊNCIAS OPCIONAIS
# ─────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────
# GERADOR PRINCIPAL
# ─────────────────────────────────────────────────

class GeradorRelatorio:

    def __init__(self, banco: Banco = None):
        self.banco        = banco or Banco()
        self.data_geracao = datetime.now()
        self.pasta        = Path("relatorios")
        self.pasta.mkdir(exist_ok=True)

    # ── helpers ──────────────────────────────────

    def _relevantes(self):
        return [n for n in self.banco.noticias if n.get("relevante")]

    def _periodo(self):
        datas = [n.get("data","") for n in self.banco.noticias if n.get("data")]
        return f"{min(datas)} a {max(datas)}" if datas else "—"

    def _num_valor(self, s):
        try:
            return float(s.replace("R$","").replace(".","").replace(",",".").strip().split()[0])
        except:
            return 0.0

    def _num_emprego(self, s):
        try:
            return int("".join(c for c in s.split()[0] if c.isdigit()))
        except:
            return 0

    # ── análises ─────────────────────────────────

    def calcular_resumo_executivo(self):
        ns = self._relevantes()
        valores   = [self._num_valor(v)   for n in ns for v in n.get("valores",[])]
        empregos  = sum(self._num_emprego(e) for n in ns for e in n.get("empregos",[]))
        confs     = [n.get("confianca",0) for n in ns if n.get("confianca",0)>0]
        return {
            "investimentos_detectados": len(self.banco.investimentos),
            "empresas_monitoradas":     len(self.banco.empresas),
            "novos_empregos":           empregos,
            "valor_total":              sum(valores),
            "confianca_media":          int(statistics.mean(confs)) if confs else 0,
            "noticias_relevantes":      len(ns),
            "periodo":                  self._periodo(),
        }

    def investimentos_por_fase(self):
        d = defaultdict(list)
        for n in self._relevantes():
            d[n.get("fase","Não identificada")].append(n)
        return dict(d)

    def ranking_empresas(self, top=10):
        cnt = Counter(); vals = defaultdict(float); emps = defaultdict(int)
        for n in self._relevantes():
            for e in n.get("empresas",[]):
                cnt[e] += 1
                for v in n.get("valores",[]): vals[e] += self._num_valor(v)
                for em in n.get("empregos",[]): emps[e] += self._num_emprego(em)
        return [{"empresa":e,"investimentos":c,"valor_total":vals[e],"empregos":emps[e]}
                for e,c in cnt.most_common(top)]

    def evolucao_mensal(self):
        d = defaultdict(lambda:{"investimentos":0,"empregos":0,"valor":0})
        for n in self._relevantes():
            dt = n.get("data","")
            mes = dt[:7] if dt and "-" in dt else (dt[-4:] if dt else "?")
            d[mes]["investimentos"] += 1
            for em in n.get("empregos",[]): d[mes]["empregos"] += self._num_emprego(em)
            for v  in n.get("valores", []): d[mes]["valor"]    += self._num_valor(v)
        return dict(sorted(d.items()))

    def analise_por_fonte(self):
        d = defaultdict(lambda:{"total":0,"relevantes":0,"confs":[]})
        for n in self.banco.noticias:
            f = n.get("fonte","Desconhecida")
            d[f]["total"] += 1
            if n.get("relevante"): d[f]["relevantes"] += 1
            c = n.get("confianca",0)
            if c > 0: d[f]["confs"].append(c)
        return {
            f: {
                "total":        v["total"],
                "relevantes":   v["relevantes"],
                "taxa_precisao": round(v["relevantes"]/v["total"]*100 if v["total"] else 0, 1),
                "confianca_media": round(statistics.mean(v["confs"]) if v["confs"] else 0, 1),
            } for f, v in d.items()
        }

    def noticias_quase_relevantes(self):
        quase = [
            {"titulo": n.get("titulo",""), "empresas": n.get("empresas",[]),
             "pontuacao": n.get("pontuacao",0), "fase": n.get("fase",""),
             "fonte": n.get("fonte",""), "url": n.get("url","")}
            for n in self.banco.noticias
            if n.get("pontuacao",0) >= 30
            and not n.get("mencionou_contagem", False)
            and not n.get("relevante")
        ]
        return sorted(quase, key=lambda x: x["pontuacao"], reverse=True)

    def analise_confianca(self):
        cs = [n.get("confianca",0) for n in self._relevantes()]
        if not cs: return {"alta":0,"media":0,"baixa":0,"media_geral":0}
        t = len(cs)
        return {
            "alta":        round(len([c for c in cs if c>=80])/t*100,1),
            "media":       round(len([c for c in cs if 50<=c<80])/t*100,1),
            "baixa":       round(len([c for c in cs if c<50])/t*100,1),
            "media_geral": round(statistics.mean(cs),1),
        }

    # ── texto ────────────────────────────────────

    def gerar_relatorio_texto(self):
        r  = self.calcular_resumo_executivo()
        fs = self.investimentos_por_fase()
        rk = self.ranking_empresas()
        ev = self.evolucao_mensal()
        fn = self.analise_por_fonte()
        cf = self.analise_confianca()
        qr = self.noticias_quase_relevantes()

        L = []
        def h(t): L.extend(["\n"+"="*70, t, "="*70])

        L += ["="*70,"RELATÓRIO DE INVESTIMENTOS PRIVADOS — CONTAGEM MG",
              "SEDECON · Secretaria de Desenvolvimento Econômico","="*70,
              f"Gerado em : {self.data_geracao.strftime('%d/%m/%Y %H:%M')}",
              f"Período   : {r['periodo']}"]

        h("SUMÁRIO EXECUTIVO")
        L += [f"  Investimentos detectados : {r['investimentos_detectados']}",
              f"  Empresas monitoradas     : {r['empresas_monitoradas']}",
              f"  Novos empregos           : {r['novos_empregos']:,}",
              f"  Valor total anunciado    : R$ {r['valor_total']/1e6:.1f} milhões",
              f"  Notícias relevantes      : {r['noticias_relevantes']}",
              f"  Confiança média          : {r['confianca_media']}%"]

        h("INVESTIMENTOS POR FASE")
        for fase, ns in sorted(fs.items()):
            L.append(f"  {fase:<22} {'█'*len(ns)} ({len(ns)})")

        h("TOP 10 EMPRESAS")
        L.append(f"  {'#':<4}{'Empresa':<28}{'Invest.':<10}{'Valor R$M':<12}{'Empregos'}")
        L.append("  "+"-"*60)
        for i,e in enumerate(rk,1):
            L.append(f"  {i:<4}{e['empresa'][:26]:<28}{e['investimentos']:<10}{e['valor_total']/1e6:<12.1f}{e['empregos']}")

        h("EVOLUÇÃO MENSAL")
        for p,d in ev.items():
            L.append(f"  {p:<12}{d['investimentos']:<10}{d['empregos']:<10}{d['valor']/1e6:.1f}M")

        h("ANÁLISE DE CONFIANÇA")
        L += [f"  Média geral : {cf['media_geral']}%",
              f"  Alta (≥80%) : {cf['alta']}%",
              f"  Média 50–80%: {cf['media']}%",
              f"  Baixa (<50%): {cf['baixa']}%"]

        if qr:
            h("QUASE RELEVANTES")
            for n in qr[:5]:
                L += [f"  • {n['titulo']}",
                      f"    Empresa(s): {', '.join(n['empresas']) or '—'} | Pontos: {n['pontuacao']}",
                      f"    URL: {n['url']}"]

        return "\n".join(L)

    # ── gráficos ─────────────────────────────────

    def gerar_graficos(self):
        if not HAS_MATPLOTLIB:
            print("⚠  Matplotlib não instalado.")
            return []

        arqs = []
        fs = self.investimentos_por_fase()
        rk = self.ranking_empresas(10)
        ev = self.evolucao_mensal()
        cf = self.analise_confianca()
        AZUL = "#1a3a5c"; OURO = "#e8a020"

        def salvar(nome):
            p = self.pasta / nome
            plt.savefig(p, dpi=200, bbox_inches="tight")
            plt.close(); arqs.append(p); print(f"  ✓ {p}")

        try:
            # Fases (horizontal)
            if fs:
                fig, ax = plt.subplots(figsize=(10,5))
                nomes = list(fs.keys()); vals = [len(fs[f]) for f in nomes]
                bars = ax.barh(nomes, vals, color=AZUL)
                for b,v in zip(bars,vals):
                    ax.text(b.get_width()+.05, b.get_y()+b.get_height()/2,
                            str(v), va="center", fontweight="bold", color=AZUL)
                ax.set_xlabel("Quantidade"); ax.spines[["top","right"]].set_visible(False)
                ax.set_title("Investimentos por Fase", fontsize=13, fontweight="bold", color=AZUL)
                plt.tight_layout(); salvar("grafico_fases.png")

            # Empresas (horizontal)
            if rk:
                fig, ax = plt.subplots(figsize=(10,6))
                nomes = [e["empresa"] for e in rk]; vals = [e["investimentos"] for e in rk]
                bars = ax.barh(nomes, vals, color=OURO)
                for b,v in zip(bars,vals):
                    ax.text(b.get_width()+.05, b.get_y()+b.get_height()/2,
                            str(v), va="center", fontweight="bold", color="#333")
                ax.set_xlabel("Investimentos"); ax.spines[["top","right"]].set_visible(False)
                ax.set_title("Top Empresas", fontsize=13, fontweight="bold", color=AZUL)
                plt.tight_layout(); salvar("grafico_empresas.png")

            # Evolução (linha)
            if ev:
                fig, ax = plt.subplots(figsize=(12,5))
                ps = list(ev.keys()); ivs = [ev[p]["investimentos"] for p in ps]
                ax.plot(ps, ivs, marker="o", linewidth=2.5, color=AZUL,
                        markersize=7, markerfacecolor=OURO)
                ax.fill_between(ps, ivs, alpha=.12, color=AZUL)
                ax.set_ylabel("Investimentos"); ax.spines[["top","right"]].set_visible(False)
                ax.set_title("Evolução Mensal", fontsize=13, fontweight="bold", color=AZUL)
                plt.xticks(rotation=40, ha="right"); plt.tight_layout()
                salvar("grafico_evolucao.png")

            # Confiança (pizza)
            vals_cf = [cf["alta"], cf["media"], cf["baixa"]]
            if any(v > 0 for v in vals_cf):
                fig, ax = plt.subplots(figsize=(7,7))
                labels = [f"Alta ≥80%\n{cf['alta']}%",
                          f"Média 50–80%\n{cf['media']}%",
                          f"Baixa <50%\n{cf['baixa']}%"]
                ax.pie(vals_cf, labels=labels,
                       colors=["#2ecc71", OURO, "#e74c3c"],
                       startangle=90,
                       wedgeprops={"edgecolor":"white","linewidth":2})
                ax.set_title(f"Confiança dos Dados\nMédia: {cf['media_geral']}%",
                             fontsize=13, fontweight="bold", color=AZUL)
                plt.tight_layout(); salvar("grafico_confianca.png")

        except Exception as e:
            print(f"  ❌ Erro gráficos: {e}")

        return arqs

    # ── HTML ─────────────────────────────────────

    def gerar_html(self):
        r   = self.calcular_resumo_executivo()
        fs  = self.investimentos_por_fase()
        rk  = self.ranking_empresas()
        ev  = self.evolucao_mensal()
        fn  = self.analise_por_fonte()
        cf  = self.analise_confianca()
        qr  = self.noticias_quase_relevantes()
        nrs = self._relevantes()
        all_n = list(self.banco.noticias)

        # serializar para JS
        njs = json.dumps(nrs,    ensure_ascii=False)
        ajs = json.dumps(all_n,  ensure_ascii=False)
        fjs = json.dumps({k:len(v) for k,v in fs.items()}, ensure_ascii=False)
        ejs = json.dumps(rk,     ensure_ascii=False)
        vjs = json.dumps(ev,     ensure_ascii=False)
        qjs = json.dumps(qr,     ensure_ascii=False)

        # fontes HTML
        f_rows = ""
        tg=rg=0
        for f in sorted(fn):
            d=fn[f]; tg+=d["total"]; rg+=d["relevantes"]
            f_rows += (f'<tr><td>{f}</td><td>{d["total"]}</td>'
                       f'<td>{d["relevantes"]}</td><td>{d["taxa_precisao"]}%</td>'
                       f'<td>{d["confianca_media"]}%</td></tr>')
        taxa = round(rg/tg*100 if tg else 0,1)
        f_rows += (f'<tr class="tr-total"><td><b>TOTAL</b></td><td><b>{tg}</b></td>'
                   f'<td><b>{rg}</b></td><td><b>{taxa}%</b></td><td>—</td></tr>')

        vm = r["valor_total"]/1e6

        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Monitor de Investimentos — Contagem MG</title>
<script src="https://cdn.plot.ly/plotly-2.30.0.min.js"></script>
<style>
:root{{
  --azul:#1a3a5c;--ouro:#e8a020;--bg:#f0f4fa;--branco:#fff;
  --cinza:#6b7280;--borda:#dde3ec;--verde:#16a34a;--text:#1f2937;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);font-size:15px}}

/* HEADER */
.hdr{
    background:var(--azul);
    color:#fff;
    padding:28px 36px;
    display:flex;
    justify-content:space-between;
    align-items:center;
    flex-wrap:wrap;
}

.hdr-centro{
    flex:1;
}

.titulo-linha{
    display:flex;
    align-items:center;
    justify-content:center;
    gap:20px;
}

.logo-sedecon{
    height:90px;
    width:auto;
}

.hdr h1{
    font-size:2.4rem;
    font-weight:800;
    text-align:center;
    letter-spacing:1px;
    margin-bottom:6px;
}

.hdr p{
    text-align:center;
    font-size:.9rem;
    opacity:.9;
}

.subtitulo{
    margin-top:4px;
    font-size:.85rem;
    opacity:.85;
    font-weight:500;
}

/* CARDS */
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
        gap:14px;padding:24px 36px 0}}
.card{{background:var(--branco);border:1px solid var(--borda);border-radius:10px;
       padding:18px;text-align:center;position:relative;overflow:hidden}}
.card::before{{content:"";position:absolute;top:0;left:0;right:0;height:4px;background:var(--azul)}}
.card.ouro::before{{background:var(--ouro)}}
.card.verde::before{{background:var(--verde)}}
.card-val{{font-size:1.9rem;font-weight:800;color:var(--azul);line-height:1;margin-bottom:5px}}
.card-lbl{{font-size:.68rem;text-transform:uppercase;letter-spacing:.6px;color:var(--cinza);font-weight:600}}

/* ABAS */
.tabs-wrap{{padding:24px 36px 0}}
.tabs{{display:flex;gap:3px;border-bottom:2px solid var(--borda)}}
.tab{{padding:9px 20px;border:1px solid transparent;border-bottom:none;border-radius:7px 7px 0 0;
      background:none;font-size:.88rem;font-weight:600;color:var(--cinza);cursor:pointer;
      position:relative;bottom:-2px;transition:all .15s}}
.tab:hover{{background:var(--bg);color:var(--azul)}}
.tab.on{{background:var(--branco);color:var(--azul);border-color:var(--borda);border-bottom-color:var(--branco)}}

/* PAINÉIS */
.painel{{
    display:none;
    padding:24px 36px;
}}

.painel.on{{
    display:block;
}}

/* SEÇÃO */
.sec{{margin-bottom:28px}}
.sec-title{{font-size:.95rem;font-weight:700;color:var(--azul);padding-bottom:8px;
            border-bottom:2px solid var(--ouro);margin-bottom:14px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}

/* FILTROS */
.filtros{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px;align-items:center}}
.filtros label{{font-size:.8rem;font-weight:600;color:var(--cinza)}}
.filtros select,.filtros input{{padding:6px 11px;border:1px solid var(--borda);border-radius:6px;
  font-size:.83rem;background:var(--branco);color:var(--text);min-width:150px}}
.btn-x{{padding:6px 13px;background:var(--azul);color:#fff;border:none;border-radius:6px;
         font-size:.8rem;font-weight:600;cursor:pointer;transition:opacity .15s}}
.btn-x:hover{{opacity:.85}}

/* TABELA */
.tbl-wrap{{overflow-x:auto}}
table{{width:100%;border-collapse:collapse;font-size:.86rem}}
th{{background:var(--azul);color:#fff;padding:10px 13px;text-align:left;font-size:.78rem;
    text-transform:uppercase;letter-spacing:.4px;white-space:nowrap}}
td{{padding:9px 13px;border-bottom:1px solid var(--borda);vertical-align:top}}
tr:hover td{{background:#eef2fa}}
.tr-total td{{background:var(--bg);font-weight:600}}

/* CARD NOTICIA */
.ncard{{background:var(--branco);border:1px solid var(--borda);border-radius:8px;
        padding:14px;margin-bottom:10px;border-left:4px solid var(--azul)}}
.ncard.quase{{border-left-color:var(--ouro)}}
.ncard-title{{font-weight:700;font-size:.93rem;color:var(--azul);margin-bottom:5px;line-height:1.4}}
.ncard-meta{{font-size:.76rem;color:var(--cinza);display:flex;gap:10px;flex-wrap:wrap;margin-bottom:5px}}
.ncard-url{{font-size:.76rem;color:var(--azul);text-decoration:none;word-break:break-all}}
.ncard-url:hover{{text-decoration:underline}}

/* BADGE */
.bdg{{display:inline-block;padding:2px 7px;border-radius:11px;font-size:.7rem;font-weight:700;text-transform:uppercase}}
.bdg-v{{background:#dcfce7;color:#15803d}}.bdg-o{{background:#fef9c3;color:#a16207}}
.bdg-c{{background:#f1f5f9;color:#475569}}.bdg-a{{background:#dbeafe;color:#1d4ed8}}

/* GRÁFICO */
.graf{{height:300px;background:var(--branco);border:1px solid var(--borda);border-radius:8px;margin-bottom:16px}}

/* VAZIO */
.vazio{{text-align:center;padding:36px;color:var(--cinza);font-style:italic}}

footer{{background:var(--azul);color:rgba(255,255,255,.55);text-align:center;
        padding:16px;font-size:.76rem;margin-top:16px}}

@media(max-width:768px){{
  .hdr,.cards,.tabs-wrap,.aba{{padding-left:14px;padding-right:14px}}
  .grid2{{grid-template-columns:1fr}}
}}
</style>
</head>
<body>

<div class="hdr">
  <div>
    <h1>📊 Monitor de Investimentos Privados</h1>
    <p>SEDECON · Prefeitura de Contagem MG &nbsp;|&nbsp; {self.data_geracao.strftime('%d/%m/%Y %H:%M')}</p>
  </div>
  <div class="badge-periodo">Período: {r['periodo']}</div>
</div>

<div class="cards">
  <div class="card"><div class="card-val">{r['investimentos_detectados']}</div><div class="card-lbl">Investimentos</div></div>
  <div class="card"><div class="card-val">{r['empresas_monitoradas']}</div><div class="card-lbl">Empresas</div></div>
  <div class="card ouro"><div class="card-val">{r['novos_empregos']:,}</div><div class="card-lbl">Empregos gerados</div></div>
  <div class="card ouro"><div class="card-val">R$ {vm:.0f}M</div><div class="card-lbl">Valor total</div></div>
  <div class="card verde"><div class="card-val">{r['confianca_media']}%</div><div class="card-lbl">Confiança média</div></div>
  <div class="card"><div class="card-val">{r['noticias_relevantes']}</div><div class="card-lbl">Notícias relevantes</div></div>
</div>

<div class="tabs-wrap">
 <div class="hdr">

  <div class="hdr-centro">

      <div class="titulo-linha">

          <img src="dados/logo secretaria sedecon.png" class="logo-sedecon">

          <div>
              <h1>MONITOR DE INVESTIMENTOS PRIVADOS</h1>

              <p>
                  SEDECON · Prefeitura de Contagem MG |
                  {self.data_geracao.strftime('%d/%m/%Y %H:%M')}
              </p>

              <p class="subtitulo">
                  Superintendência de Inovação e Informações Estratégicas
              </p>
          </div>

      </div>

  </div>

  <div class="badge-periodo">
      Período: {r['periodo']}
  </div>

</div>

<!-- ABA RESUMO -->
<div id="resumo" class="painel on">

    <div class="sec">

        <div class="sec-title">
            Sumário Executivo
        </div>

        <table>

            <tr>
                <th>Indicador</th>
                <th>Valor</th>
            </tr>

            <tr>
                <td>Investimentos detectados</td>
                <td>{r["investimentos_detectados"]}</td>
            </tr>

            <tr>
                <td>Empresas monitoradas</td>
                <td>{r["empresas_monitoradas"]}</td>
            </tr>

            <tr>
                <td>Empregos gerados</td>
                <td>{r["novos_empregos"]}</td>
            </tr>

            <tr>
                <td>Valor anunciado</td>
                <td>R$ {vm:.1f} milhões</td>
            </tr>

            <tr>
                <td>Confiança média</td>
                <td>{r["confianca_media"]}%</td>
            </tr>

        </table>

        </div>

    <div class="sec">

        <div class="sec-title">
            Ranking das Empresas
        </div>

        <div class="tbl-wrap">

            <table>

                <thead>

                    <tr>

                        <th>#</th>
                        <th>Empresa</th>
                        <th>Investimentos</th>
                        <th>Valor</th>
                        <th>Empregos</th>

                    </tr>

                </thead>

                <tbody id="tb-rk">

                </tbody>

            </table>
        </div>
</div>


    <!-- =============================== -->
    <!-- GRÁFICOS -->
    <!-- =============================== -->

    <div class="sec">

        <div class="sec-title">

            Panorama Geral

        </div>

        <div class="grid2">

            <div id="g-fases" class="graf"></div>

            <div id="g-emp" class="graf"></div>

        </div>

    </div>

    <!-- =============================== -->
    <!-- EVOLUÇÃO -->
    <!-- =============================== -->

    <div class="sec">

        <div class="sec-title">

            Evolução dos Investimentos

        </div>

        <div id="g-evol" class="graf"></div>

    </div>

    <!-- =============================== -->
    <!-- RANKING -->
    <!-- =============================== -->

    <div class="sec">

        <div class="sec-title">

            Ranking das Empresas

        </div>

        <div class="tbl-wrap">

            <table>

                <thead>

                    <tr>

                        <th>#</th>

                        <th>Empresa</th>

                        <th>Investimentos</th>

                        <th>Valor</th>

                        <th>Empregos</th>

                    </tr>

                </thead>

                <tbody id="tb-rk">

                </tbody>

            </table>

        </div>

    </div>

    <!-- =============================== -->
    <!-- QUASE RELEVANTES -->
    <!-- =============================== -->

    <div class="sec">

        <div class="sec-title">

            Notícias Quase Relevantes

        </div>

        <div id="lista-quase">

        </div>

    </div>

</div>

<!-- ABA HISTORICO -->
<div id="historico" class="painel">
    <h2>Histórico de Investimentos</h2>

    <p>
        Em breve serão exibidos os gráficos e ranking de empresas.
    </p>
</div>

<!-- ABA NOTÍCIAS -->
<div id="noticias" class="painel">
    <h2>Notícias Monitoradas</h2>

      <div class="sec">
          <div class="sec-title">Desempenho por fonte</div>

          <div class="tbl-wrap">
              <table>
                  <thead>
                      <tr>
                          <th>Fonte</th>
                          <th>Total</th>
                          <th>Relevantes</th>
                          <th>Precisão</th>
                          <th>Confiança</th>
                      </tr>
                  </thead>

                  <tbody>
                      {f_rows}
                  </tbody>

              </table>
          </div>

      </div>

  </div>

</div>

<footer>Monitor de Investimentos Privados · SEDECON · Prefeitura de Contagem MG · {self.data_geracao.strftime('%d/%m/%Y %H:%M')}</footer>

<script>
// ── dados ──────────────────────────────────────────────────
const NOTICIAS = {njs};
const TODAS    = {ajs};
const FASES_D  = {fjs};
const EMPS_D   = {ejs};
const EVOL_D   = {vjs};
const QUASE_D  = {qjs};
const CONF_D   = {{alta:{cf['alta']},media:{cf['media']},baixa:{cf['baixa']},mg:{cf['media_geral']}}};
const AZUL='#1a3a5c', OURO='#e8a020', VERDE='#16a34a';

// ── abas ───────────────────────────────────────────────────
function aba(id, btn){{

    document.querySelectorAll(".painel")
        .forEach(p => p.classList.remove("on"));

    document.querySelectorAll(".tab")
        .forEach(t => t.classList.remove("on"));

    document.getElementById(id)
        .classList.add("on");

    btn.classList.add("on");

    if(id==="resumo"){{

        renderGraf();

        renderRanking();

    }}

}}

// ── badge fase ─────────────────────────────────────────────
function bdgFase(f){{
  const m={{'Anunciado':'bdg-a','Construção':'bdg-o','Operação':'bdg-v','Expansão':'bdg-v'}};
  return `<span class="bdg ${{m[f]||'bdg-c'}}">${{f||'—'}}</span>`;
}}

// ── card notícia ───────────────────────────────────────────
function cardN(n, extra){{
  const emps=(n.empresas||[]).join(', ')||'—';
  const vals=(n.valores ||[]).join(', ')||'—';
  const empr=(n.empregos||[]).join(', ')||'—';
  return `<div class="ncard${{extra?' quase':''}}">
    <div class="ncard-title">${{n.titulo||'—'}}</div>
    <div class="ncard-meta">
      <span>📍 ${{n.fonte||'—'}}</span><span>📅 ${{n.data||'—'}}</span>
      <span>🎯 ${{n.pontuacao||0}} pts</span>${{bdgFase(n.fase)}}
      ${{n.relevante?'<span class="bdg bdg-v">✓ Relevante</span>':''}}
    </div>
    <div class="ncard-meta">🏢 ${{emps}} &nbsp;|&nbsp; 💰 ${{vals}} &nbsp;|&nbsp; 👥 ${{empr}}</div>
    <a class="ncard-url" href="${{n.url}}" target="_blank">${{n.url}}</a>
  </div>`;
}}

// ── popular selects ────────────────────────────────────────
function popSelect(selId, arr){{
  const s=document.getElementById(selId);
  [...new Set(arr)].sort().forEach(v=>s.add(new Option(v,v)));
}}
function limpar(...ids){{
  ids.forEach(id=>{{const el=document.getElementById(id); if(el)el.value=''}});
  renderRecentes(); renderHist();
}}

// ── RECENTES ───────────────────────────────────────────────
function renderRecentes(){{
  const e=document.getElementById('r-emp').value.toLowerCase();
  const f=document.getElementById('r-fase').value.toLowerCase();
  const t=document.getElementById('r-txt').value.toLowerCase();
  const lista=NOTICIAS.filter(n=>
    (!e||(n.empresas||[]).join(' ').toLowerCase().includes(e))&&
    (!f|(n.fase||'').toLowerCase()===f)&&
    (!t|(n.titulo||'').toLowerCase().includes(t))
  );
  document.getElementById('lista-recentes').innerHTML=
    lista.length ? lista.map(n=>cardN(n,false)).join('') : '<div class="vazio">Nenhuma notícia com esses filtros.</div>';
}}

// ── HISTÓRICO ──────────────────────────────────────────────
function renderHist(){{
  const e=document.getElementById('h-emp').value.toLowerCase();
  const f=document.getElementById('h-fase').value.toLowerCase();
  const r=document.getElementById('h-rel').value;
  const t=document.getElementById('h-txt').value.toLowerCase();
  const lista=TODAS.filter(n=>
    (!e||(n.empresas||[]).join(' ').toLowerCase().includes(e))&&
    (!f|(n.fase||'').toLowerCase()===f)&&
    (!r||(r==='s'?n.relevante:!n.relevante))&&
    (!t|(n.titulo||'').toLowerCase().includes(t))
  );
  document.getElementById('lista-hist').innerHTML=
    lista.length ? lista.map(n=>cardN(n,false)).join('') : '<div class="vazio">Nenhuma notícia com esses filtros.</div>';
}}

// ── QUASE ──────────────────────────────────────────────────
function renderQuase(){{
  document.getElementById('lista-quase').innerHTML=
    QUASE_D.length ? QUASE_D.map(n=>cardN(n,true)).join('') : '<div class="vazio">Nenhuma notícia quase relevante.</div>';
}}

// ── RANKING tabela ─────────────────────────────────────────
function renderRanking(){{
  document.getElementById('tb-rk').innerHTML=
    EMPS_D.map((e,i)=>`<tr>
      <td><b>${{i+1}}</b></td><td>${{e.empresa}}</td><td>${{e.investimentos}}</td>
      <td>R$ ${{(e.valor_total/1e6).toFixed(1)}}M</td><td>${{e.empregos}}</td>
    </tr>`).join('') || '<tr><td colspan="5" class="vazio">Sem dados.</td></tr>';
}}

// ── GRÁFICOS Plotly ────────────────────────────────────────
function renderGraf(){{
  const cfg={{responsive:true,displayModeBar:false}};
  const base={{font:{{family:'Segoe UI,system-ui',size:12}},
               paper_bgcolor:'#fff',plot_bgcolor:'#fff'}};

  // Fases — horizontal
  Plotly.newPlot('g-fases',[{{
    x:Object.values(FASES_D), y:Object.keys(FASES_D),
    type:'bar', orientation:'h',
    marker:{{color:AZUL}},
    text:Object.values(FASES_D), textposition:'outside'
  }}],{{...base,title:'Por Fase',margin:{{l:140,r:30,t:40,b:40}},
       xaxis:{{title:'Quantidade'}}}},cfg);

  // Empresas — horizontal
  Plotly.newPlot('g-emp',[{{
    x:EMPS_D.map(e=>e.investimentos), y:EMPS_D.map(e=>e.empresa),
    type:'bar', orientation:'h',
    marker:{{color:OURO}},
    text:EMPS_D.map(e=>e.investimentos), textposition:'outside'
  }}],{{...base,title:'Top Empresas',margin:{{l:160,r:30,t:40,b:40}},
       xaxis:{{title:'Investimentos'}}}},cfg);

  // Evolução — linha
  const ps=Object.keys(EVOL_D), ivs=ps.map(p=>EVOL_D[p].investimentos);
  Plotly.newPlot('g-evol',[{{
    x:ps, y:ivs, type:'scatter', mode:'lines+markers',
    line:{{color:AZUL,width:2.5}},
    marker:{{size:8,color:OURO}},
    fill:'tozeroy', fillcolor:'rgba(26,58,92,0.08)'
  }}],{{...base,title:'Evolução Mensal',margin:{{l:60,r:20,t:40,b:60}},
       xaxis:{{tickangle:-40}},yaxis:{{title:'Investimentos'}}}},cfg);

  // Confiança — pizza
  const cv=[CONF_D.alta,CONF_D.media,CONF_D.baixa];
  if(cv.some(v=>v>0)){{
    Plotly.newPlot('g-conf',[{{
      values:cv,
      labels:[`Alta ≥80% (${{CONF_D.alta}}%)`,`Média (${{CONF_D.media}}%)`,`Baixa (${{CONF_D.baixa}}%)`],
      type:'pie', hole:0.4,
      marker:{{colors:[VERDE,OURO,'#dc2626'],line:{{color:'white',width:2}}}},
      textinfo:'percent'
    }}],{{...base,title:`Confiança — Média ${{CONF_D.mg}}%`,
         margin:{{l:20,r:20,t:50,b:20}},
         showlegend:true,legend:{{orientation:'h',y:-0.15}}}},cfg);
  }} else {{
    document.getElementById('g-conf').innerHTML='<div class="vazio" style="padding-top:80px">Sem dados ainda.</div>';
  }}
}}

// ── init ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded',()=>{{

    popSelect('r-emp', NOTICIAS.flatMap(n=>n.empresas||[]));
    popSelect('r-fase', NOTICIAS.map(n=>n.fase).filter(Boolean));

    popSelect('h-emp', TODAS.flatMap(n=>n.empresas||[]));
    popSelect('h-fase', TODAS.map(n=>n.fase).filter(Boolean));

    renderRanking();

    renderGraf();

}});

</script>
</body>
</html>"""

    # ── PDF ──────────────────────────────────────

    def gerar_pdf(self):
        if not HAS_REPORTLAB:
            print("⚠  ReportLab não instalado."); return None
        try:
            r  = self.calcular_resumo_executivo()
            rk = self.ranking_empresas()
            fs = self.investimentos_por_fase()
            fn = self.analise_por_fonte()
            cf = self.analise_confianca()
            qr = self.noticias_quase_relevantes()

            nome = self.pasta / f"relatorio_{self.data_geracao.strftime('%Y%m%d_%H%M%S')}.pdf"
            doc  = SimpleDocTemplate(str(nome), pagesize=A4,
                                     rightMargin=2*cm, leftMargin=2*cm,
                                     topMargin=2*cm,  bottomMargin=2*cm)

            styles = getSampleStyleSheet()
            AZUL_  = colors.HexColor("#1a3a5c")
            OURO_  = colors.HexColor("#e8a020")
            CLARO_ = colors.HexColor("#f4f7fb")
            CINZA_ = colors.HexColor("#6b7280")

            t_tit = ParagraphStyle("tt", parent=styles["Heading1"],
                fontSize=20, textColor=AZUL_, alignment=1, spaceAfter=4, fontName="Helvetica-Bold")
            t_sub = ParagraphStyle("ts", parent=styles["Normal"],
                fontSize=10, textColor=CINZA_, alignment=1, spaceAfter=2)
            t_sec = ParagraphStyle("tc", parent=styles["Heading2"],
                fontSize=12, textColor=AZUL_, spaceBefore=16, spaceAfter=8, fontName="Helvetica-Bold")
            t_bdy = ParagraphStyle("tb", parent=styles["Normal"],
                fontSize=9, textColor=colors.HexColor("#374151"), leading=14)

            def hr(): return HRFlowable(width="100%", thickness=1.5, color=OURO_, spaceAfter=10)

            def tbl(data, ws=None):
                t = Table(data, colWidths=ws, repeatRows=1)
                t.setStyle(TableStyle([
                    ("BACKGROUND",  (0,0),(-1,0),  AZUL_),
                    ("TEXTCOLOR",   (0,0),(-1,0),  colors.white),
                    ("FONTNAME",    (0,0),(-1,0),  "Helvetica-Bold"),
                    ("FONTSIZE",    (0,0),(-1,-1), 8),
                    ("ALIGN",       (0,0),(-1,-1), "LEFT"),
                    ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
                    ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, CLARO_]),
                    ("GRID",        (0,0),(-1,-1), 0.4, colors.HexColor("#dde3ec")),
                    ("TOPPADDING",  (0,0),(-1,-1), 6),
                    ("BOTTOMPADDING",(0,0),(-1,-1),6),
                    ("LEFTPADDING", (0,0),(-1,-1), 8),
                    ("RIGHTPADDING",(0,0),(-1,-1), 8),
                ]))
                return t

            story = []
            story += [Spacer(1,1.5*cm),
                      Paragraph("Monitor de Investimentos Privados", t_tit),
                      Paragraph("SEDECON · Prefeitura de Contagem · MG", t_sub),
                      Paragraph(f"Gerado em {self.data_geracao.strftime('%d/%m/%Y %H:%M')} · Período: {r['periodo']}", t_sub),
                      Spacer(1,.5*cm), hr(),
                      Paragraph("Sumário Executivo", t_sec)]

            story.append(tbl([
                ["Indicador","Valor"],
                ["Investimentos detectados",  str(r["investimentos_detectados"])],
                ["Empresas monitoradas",      str(r["empresas_monitoradas"])],
                ["Novos empregos",            f"{r['novos_empregos']:,}"],
                ["Valor total anunciado",     f"R$ {r['valor_total']/1e6:.1f} milhões"],
                ["Notícias relevantes",       str(r["noticias_relevantes"])],
                ["Confiança média",           f"{r['confianca_media']}%"],
            ], ws=[11*cm,5*cm]))

            story += [Spacer(1,.4*cm), Paragraph("Fases", t_sec)]
            fase_rows = [["Fase","Qtd."]]
            for f,ns in sorted(fs.items()): fase_rows.append([f, str(len(ns))])
            story.append(tbl(fase_rows, ws=[11*cm,5*cm]) if len(fase_rows)>1
                         else Paragraph("Sem dados.", t_bdy))

            story += [Spacer(1,.4*cm), Paragraph("Top Empresas", t_sec)]
            rk_rows = [["#","Empresa","Invest.","R$ M","Empregos"]]
            for i,e in enumerate(rk,1):
                rk_rows.append([str(i), e["empresa"][:28],
                                 str(e["investimentos"]),
                                 f"{e['valor_total']/1e6:.1f}",
                                 str(e["empregos"])])
            story.append(tbl(rk_rows, ws=[1*cm,7.5*cm,2*cm,2.5*cm,2.5*cm]) if len(rk_rows)>1
                         else Paragraph("Sem empresas.", t_bdy))

            story += [Spacer(1,.4*cm), Paragraph("Fontes", t_sec)]
            tg=rg=0
            fn_rows=[["Fonte","Total","Relev.","Precisão","Confiança"]]
            for f in sorted(fn):
                d=fn[f]; tg+=d["total"]; rg+=d["relevantes"]
                fn_rows.append([f[:22], str(d["total"]), str(d["relevantes"]),
                                 f"{d['taxa_precisao']}%", f"{d['confianca_media']}%"])
            taxa=round(rg/tg*100 if tg else 0,1)
            fn_rows.append(["TOTAL",str(tg),str(rg),f"{taxa}%","—"])
            story.append(tbl(fn_rows, ws=[5.5*cm,2*cm,2*cm,2.5*cm,3.5*cm]))

            story += [Spacer(1,.4*cm), Paragraph("Confiança", t_sec)]
            story.append(tbl([
                ["Nível","Percentual"],
                ["Alta (≥ 80%)",   f"{cf['alta']}%"],
                ["Média (50–80%)", f"{cf['media']}%"],
                ["Baixa (< 50%)",  f"{cf['baixa']}%"],
                ["Média geral",    f"{cf['media_geral']}%"],
            ], ws=[11*cm,5*cm]))

            if qr:
                story += [PageBreak(), Paragraph("Quase Relevantes", t_sec),
                          Paragraph("Pontuação ≥ 30 mas sem menção explícita a Contagem.", t_bdy),
                          Spacer(1,.3*cm)]
                for n in qr[:8]:
                    story += [Paragraph(f"<b>• {n['titulo']}</b>", t_bdy),
                              Paragraph(f"&nbsp;&nbsp;Empresa(s): {', '.join(n['empresas']) or '—'} | Fase: {n['fase']} | Pontos: {n['pontuacao']}", t_bdy),
                              Paragraph(f"&nbsp;&nbsp;URL: {n['url']}", t_bdy),
                              Spacer(1,.15*cm)]

            story += [hr(), Paragraph("Critérios de relevância", t_sec),
                      Paragraph("Pontuação mínima de 30 pontos · menção explícita a Contagem · empresa identificada na lista monitorada.", t_bdy)]

            doc.build(story)
            return nome
        except Exception as e:
            import traceback; traceback.print_exc()
            print(f"  ❌ PDF: {e}"); return None

    # ── salvar ───────────────────────────────────

    def salvar_txt(self):
        p = self.pasta / f"relatorio_{self.data_geracao.strftime('%Y%m%d_%H%M%S')}.txt"
        p.write_text(self.gerar_relatorio_texto(), encoding="utf-8"); return p

    def salvar_json(self):
        dados = {
            "data_geracao":      self.data_geracao.isoformat(),
            "resumo_executivo":  self.calcular_resumo_executivo(),
            "investimentos_por_fase": {k:len(v) for k,v in self.investimentos_por_fase().items()},
            "ranking_empresas":  self.ranking_empresas(),
            "evolucao_mensal":   self.evolucao_mensal(),
            "analise_por_fonte": self.analise_por_fonte(),
            "quase_relevantes":  self.noticias_quase_relevantes(),
            "analise_confianca": self.analise_confianca(),
        }
        p = self.pasta / f"relatorio_{self.data_geracao.strftime('%Y%m%d_%H%M%S')}.json"
        p.write_text(json.dumps(dados, indent=4, ensure_ascii=False), encoding="utf-8"); return p

    def salvar_html(self):
        p = self.pasta / f"relatorio_{self.data_geracao.strftime('%Y%m%d_%H%M%S')}.html"
        p.write_text(self.gerar_html(), encoding="utf-8"); return p

    # ── gerar tudo ───────────────────────────────

    def gerar_todos(self):
        print("\n"+"="*60+"\n  GERANDO RELATÓRIOS\n"+"="*60)
        gerados = []
        for nome, fn in [("TXT",self.salvar_txt),("JSON",self.salvar_json),
                         ("HTML",self.salvar_html),("PDF",self.gerar_pdf)]:
            try:
                p = fn()
                if p: print(f"  ✓ {nome}: {p}"); gerados.append(p)
            except Exception as e:
                print(f"  ❌ {nome}: {e}")
        try:
            gerados += self.gerar_graficos()
        except Exception as e:
            print(f"  ❌ Gráficos: {e}")
        print("="*60+f"\n  {len(gerados)} arquivo(s) gerado(s).\n"+"="*60+"\n")
        return gerados

    def imprimir_relatorio(self):
        print(self.gerar_relatorio_texto())


# ─────────────────────────────────────────────────
if __name__ == "__main__":
    GeradorRelatorio().gerar_todos()
