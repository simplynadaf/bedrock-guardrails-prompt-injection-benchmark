"""Builds the README visuals (banner 1280x640, architecture, pipeline, threshold chart) from inline SVG/HTML.
Numbers in the chart come from results/20261111/igc_corpus_raw.jsonl (see README, 'What the data says')."""
from playwright.sync_api import sync_playwright
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "img"
C = dict(bg="#0c0a1f", panel="#14122b", panel2="#1b1838", line="#2b2850", text="#e8e6ff", muted="#9a97c8",
         mint="#7dffd9", cyan="#5fe0ff", indigo="#5b6df0", violet="#8a6bff", coral="#ff6a4d", amber="#ffb347")
FONT = "'Inter','Helvetica Neue','Segoe UI','DejaVu Sans',Arial,sans-serif"
MONO = "'JetBrains Mono','DejaVu Sans Mono',Menlo,monospace"

BASE_CSS = f"""
*{{box-sizing:border-box;margin:0}}
body{{background:{C['bg']};font-family:{FONT};color:{C['text']};
 background-image:radial-gradient(900px 520px at 85% 8%,rgba(255,106,77,.22),transparent 60%),
 radial-gradient(900px 600px at 6% 100%,rgba(138,107,255,.30),transparent 60%);}}
.grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:56px 56px;mask-image:radial-gradient(ellipse at 50% 55%,#000 30%,transparent 85%)}}
"""

# ---------------------------------------------------------------- banner (GitHub recommended 1280x640)
def banner():
    hs = [30, 86, 153, 220, 286, 352]
    cols = [("#3b3a63", "#26244a"), ("#4a52a8", "#2f3377"), ("#5b6df0", "#3b45b8"), ("#8a6bff", "#5a3fd6"), ("#ff9a62", "#f2603d"), ("#ffd27a", "#ff8a3d")]
    labs = ["0", "0.2", "0.4", "0.6", "0.8", "1.0"]
    bx = "".join(
        f'<div class="bar" style="height:{h}px;background:linear-gradient({a},{b});'
        f'{"box-shadow:0 0 50px rgba(255,150,80,.5),0 18px 40px rgba(0,0,0,.45);" if i>=4 else "box-shadow:0 18px 40px rgba(0,0,0,.45);"}">'
        f'<span>{lab}</span></div>' for i, (h, (a, b), lab) in enumerate(zip(hs, cols, labs)))
    return f"""<!doctype html><meta charset=utf-8><style>{BASE_CSS}
body{{width:1280px;height:640px;position:relative;overflow:hidden}}
.pill{{position:absolute;left:72px;top:58px;padding:9px 20px;border:1.5px solid {C['mint']};border-radius:999px;color:{C['mint']};font-size:19px;letter-spacing:.14em;font-weight:700;background:rgba(125,255,217,.08)}}
h1{{position:absolute;left:68px;top:108px;font-size:128px;line-height:1;font-weight:800;letter-spacing:-.03em;background:linear-gradient(90deg,{C['mint']},{C['cyan']} 55%,{C['violet']});-webkit-background-clip:text;color:transparent}}
.sub{{position:absolute;left:74px;top:272px;width:620px;font-size:35px;line-height:1.25;font-weight:600;color:{C['text']}}}
.sub b{{color:{C['amber']}}}
.chips{{position:absolute;left:74px;top:452px;display:flex;gap:14px}}
.chip{{padding:12px 18px;border-radius:14px;background:{C['panel2']};border:1px solid {C['line']};font-size:19px;color:{C['muted']}}}
.chip b{{color:{C['text']};font-size:28px;display:block}}
.bars{{position:absolute;left:770px;right:70px;bottom:78px;height:360px;display:flex;gap:24px;align-items:flex-end}}
.bar{{flex:1;border-radius:16px 16px 6px 6px;position:relative}}
.bar::after{{content:"";position:absolute;left:14%;right:14%;top:9px;height:7px;border-radius:4px;background:rgba(255,255,255,.35)}}
.bar span{{position:absolute;bottom:-38px;left:0;right:0;text-align:center;font-family:{MONO};font-size:19px;color:{C['muted']}}}
.gate{{position:absolute;left:730px;right:44px;bottom:{78+286}px;border-top:4px dashed {C['mint']};filter:drop-shadow(0 0 10px rgba(125,255,217,.9))}}
.node{{position:absolute;right:26px;bottom:{78+286-18}px;width:40px;height:40px;border-radius:50%;background:{C['mint']};box-shadow:0 0 0 9px rgba(125,255,217,.18),0 0 34px rgba(125,255,217,.9)}}
.node::after{{content:"";position:absolute;inset:12px;border-radius:50%;background:{C['bg']}}}
.lab{{position:absolute;left:742px;bottom:{78+286+14}px;font-family:{MONO};font-size:18px;color:{C['mint']}}}
</style><div class=grid></div>
<div class=pill>AMAZON BEDROCK GUARDRAILS</div>
<h1>igc-bench</h1>
<div class=sub>Measure <b>InvokeGuardrailChecks</b> before you let it guard an agent.</div>
<div class=chips>
 <div class=chip><b>957</b>inputs per run</div>
 <div class=chip><b>94.7%</b>detected at 0.6</div>
 <div class=chip><b>0.0</b>textbook attack</div>
</div>
<div class=gate></div><div class=lab>block tool output at 0.8</div><div class=node></div>
<div class=bars>{bx}</div>"""

# ---------------------------------------------------------------- svg helpers
def svg_open(w, h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FONT}">'
            f'<defs>'
            f'<marker id="a" markerWidth="12" markerHeight="12" refX="9" refY="6" orient="auto"><path d="M1,1 L10,6 L1,11 Z" fill="{C["muted"]}"/></marker>'
            f'<marker id="am" markerWidth="12" markerHeight="12" refX="9" refY="6" orient="auto"><path d="M1,1 L10,6 L1,11 Z" fill="{C["mint"]}"/></marker>'
            f'<marker id="ac" markerWidth="12" markerHeight="12" refX="9" refY="6" orient="auto"><path d="M1,1 L10,6 L1,11 Z" fill="{C["coral"]}"/></marker>'
            f'<marker id="aa" markerWidth="12" markerHeight="12" refX="9" refY="6" orient="auto"><path d="M1,1 L10,6 L1,11 Z" fill="{C["amber"]}"/></marker>'
            f'<filter id="glow"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
            f'</defs>')

def box(x, y, w, h, title, lines=(), stroke=None, fill=None, tcol=None, tsize=26, lsize=20, mono=False, r=18, glow=False):
    stroke = stroke or C["line"]; fill = fill or C["panel"]; tcol = tcol or C["text"]
    g = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"' + (' filter="url(#glow)"' if glow else '') + '/>'
    g += f'<text x="{x+24}" y="{y+42}" font-size="{tsize}" font-weight="700" fill="{tcol}">{title}</text>'
    for i, ln in enumerate(lines):
        fam = f' font-family="{MONO}"' if mono else ''
        g += f'<text x="{x+24}" y="{y+42+34+i*(lsize+10)}" font-size="{lsize}" fill="{C["muted"]}"{fam}>{ln}</text>'
    return g

def arrow(x1, y1, x2, y2, color="muted", dash=False, label=None, lx=None, ly=None):
    m = {"muted": "a", "mint": "am", "coral": "ac", "amber": "aa"}[color]
    col = C[color]
    d = ' stroke-dasharray="9 8"' if dash else ''
    g = f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{col}" stroke-width="3" fill="none" marker-end="url(#{m})"{d}/>'
    if label:
        g += f'<text x="{lx if lx is not None else (x1+x2)/2}" y="{ly if ly is not None else (y1+y2)/2-12}" font-size="19" fill="{col}" text-anchor="middle" font-family="{MONO}">{label}</text>'
    return g

def page(w, h, inner):
    return f"""<!doctype html><meta charset=utf-8><style>{BASE_CSS}body{{width:{w}px;height:{h}px;position:relative;overflow:hidden}}</style><div class=grid></div>{inner}"""

# ---------------------------------------------------------------- architecture
def architecture():
    W, H = 1680, 900
    s = svg_open(W, H)
    s += f'<text x="70" y="82" font-size="44" font-weight="800" fill="{C["text"]}">Where the gate sits in an agent loop</text>'
    s += f'<text x="70" y="122" font-size="23" fill="{C["muted"]}">Every tool result passes through guard_step() before the model sees it. Errors fail closed.</text>'
    # row 1
    s += box(70, 260, 270, 150, "Customer", ["asks a question"], stroke=C["indigo"])
    s += box(400, 260, 300, 150, "Agent", ["Converse + one tool", "temperature 0"], stroke=C["indigo"])
    s += box(760, 260, 270, 150, "Tool", ["search_docs", "returns a help page"], stroke=C["indigo"])
    s += arrow(340, 335, 398, 335); s += arrow(700, 335, 758, 335)
    # gate
    s += box(1130, 190, 480, 330, "guard_step()", [], stroke=C["mint"], fill="#10213a", tcol=C["mint"], glow=True)
    steps = ["1  strip long base64/hex blobs", "2  call InvokeGuardrailChecks", "3  score = max of 3 categories", "4  block at 0.8 (tool output)", "5  any error = fail closed"]
    for i, t in enumerate(steps):
        s += f'<text x="1156" y="{266+i*50}" font-size="23" fill="{C["text"]}" font-family="{MONO}">{t}</text>'
    s += arrow(1030, 335, 1128, 335, "mint"); s += f'<text x="1079" y="300" font-size="18" fill="{C["mint"]}" text-anchor="middle" font-family="{MONO}">page</text>'
    # bedrock
    s += box(1130, 40, 480, 100, "Amazon Bedrock", [], stroke=C["violet"], tsize=26)
    s += f'<text x="1154" y="116" font-size="20" fill="{C["muted"]}" font-family="{MONO}">InvokeGuardrailChecks, us-east-1</text>'
    s += arrow(1300, 140, 1300, 188, "mint"); s += f'<text x="1286" y="170" font-size="19" fill="{C["mint"]}" text-anchor="end" font-family="{MONO}">text in</text>'
    s += arrow(1440, 188, 1440, 140, "mint"); s += f'<text x="1456" y="170" font-size="19" fill="{C["mint"]}" text-anchor="start" font-family="{MONO}">scores out</text>'
    # outcomes
    s += box(1130, 620, 150, 150, "allow", [], stroke=C["cyan"], tcol=C["cyan"], tsize=28)
    s += f'<text x="1154" y="694" font-size="19" fill="{C["muted"]}">page goes</text><text x="1154" y="720" font-size="19" fill="{C["muted"]}">to the model</text>'
    s += box(1308, 620, 150, 150, "block", [], stroke=C["coral"], tcol=C["coral"], tsize=28)
    s += f'<text x="1332" y="694" font-size="19" fill="{C["muted"]}">model sees</text><text x="1332" y="720" font-size="19" fill="{C["muted"]}">"withheld"</text>'
    s += box(1486, 620, 150, 150, "error", [], stroke=C["amber"], tcol=C["amber"], tsize=28)
    s += f'<text x="1510" y="694" font-size="19" fill="{C["muted"]}">treated as</text><text x="1510" y="720" font-size="19" fill="{C["muted"]}">block, counted</text>'
    s += arrow(1205, 520, 1205, 618, "mint"); s += arrow(1383, 520, 1383, 618, "coral"); s += arrow(1561, 520, 1561, 618, "amber")
    # governance
    s += box(70, 560, 470, 210, "IAM role", ["one action: bedrock:InvokeGuardrailChecks", "pinned to one Region", "trust on one named principal", "proven by verify_iam.py"], stroke=C["violet"], lsize=19)
    s += box(580, 560, 470, 210, "CloudTrail data event", ["resource type AWS::Bedrock::Guardrail", "records checks, scores, text units", "does NOT record the prompt text", "log blocked text yourself if policy allows"], stroke=C["violet"], lsize=19)
    s += f'<text x="70" y="850" font-size="21" fill="{C["muted"]}">Two thresholds in this repo: 0.6 for user input, 0.8 for tool output. Reasoning and data in the README.</text>'
    s += '</svg>'
    return page(W, H, s)

# ---------------------------------------------------------------- pipeline
def pipeline():
    W, H = 1680, 700
    s = svg_open(W, H)
    s += f'<text x="70" y="82" font-size="44" font-weight="800" fill="{C["text"]}">How the benchmark runs</text>'
    s += f'<text x="70" y="122" font-size="23" fill="{C["muted"]}">Two input sets, one runner, five checks. Raw rows are kept, so every number is reproducible.</text>'
    s += box(70, 190, 420, 130, "corpus.jsonl", ["411 items: 206 attacks, 205 benign", "hard negatives on purpose"], stroke=C["indigo"], lsize=19)
    s += box(70, 350, 420, 130, "deepset/prompt-injections", ["546 rows: 203 attacks, 343 benign", "public, Apache-2.0"], stroke=C["indigo"], lsize=19)
    s += box(590, 255, 400, 170, "run.py", ["max of 3 categories", "jittered backoff on throttling", "errors are counted, never scored"], stroke=C["mint"], fill="#10213a", tcol=C["mint"], lsize=19, glow=True)
    s += arrow(490, 255, 588, 320); s += arrow(490, 415, 588, 360)
    s += box(1090, 170, 520, 80, "report.py", [], stroke=C["line"], tsize=24)
    s += f'<text x="1114" y="233" font-size="19" fill="{C["muted"]}">threshold tables, Wilson 95% intervals</text>'
    s += box(1090, 270, 520, 80, "compare_apply_guardrail.py", [], stroke=C["line"], tsize=24)
    s += f'<text x="1114" y="333" font-size="19" fill="{C["muted"]}">same inputs through ApplyGuardrail</text>'
    s += box(1090, 370, 520, 80, "agent_demo.py", [], stroke=C["line"], tsize=24)
    s += f'<text x="1114" y="433" font-size="19" fill="{C["muted"]}">poisoned help pages, two models</text>'
    s += box(1090, 470, 520, 80, "limits_probe.py", [], stroke=C["line"], tsize=24)
    s += f'<text x="1114" y="533" font-size="19" fill="{C["muted"]}">units, size, latency, throttling</text>'
    s += box(1090, 570, 520, 80, "verify_iam.py", [], stroke=C["violet"], tsize=24)
    s += f'<text x="1114" y="633" font-size="19" fill="{C["muted"]}">least-privilege role, proven action by action</text>'
    s += arrow(990, 330, 1088, 210, "mint"); s += arrow(990, 340, 1088, 310); s += arrow(990, 350, 1088, 410); s += arrow(990, 360, 1088, 510)
    s += f'<text x="590" y="480" font-size="21" fill="{C["muted"]}">output: results/YYYYMMDD/*.jsonl</text>'
    s += '</svg>'
    return page(W, H, s)

# ---------------------------------------------------------------- chart
def chart():
    W, H = 1680, 700
    s = svg_open(W, H)
    s += f'<text x="70" y="78" font-size="44" font-weight="800" fill="{C["text"]}">What the thresholds buy you</text>'
    s += f'<text x="70" y="116" font-size="23" fill="{C["muted"]}">Author corpus, 206 attacks and 205 benign items, 11 Nov 2026, us-east-1. Score = max of the three categories.</text>'
    def panel(x, w, title):
        return (f'<rect x="{x}" y="150" width="{w}" height="500" rx="20" fill="{C["panel"]}" stroke="{C["line"]}" stroke-width="2"/>'
                f'<text x="{x+26}" y="196" font-size="25" font-weight="700" fill="{C["text"]}">{title}</text>')
    # Panel A: detection vs FP across thresholds
    ax, aw = 70, 760
    s += panel(ax, aw, "Detection vs false positives")
    base, top = 590, 250; sc = (base-top)/100
    ths = ["0.2", "0.4", "0.6", "0.8", "1.0"]; det = [95.1, 95.1, 94.7, 81.6, 64.1]; fp = [15.1, 13.2, 12.2, 5.4, 4.4]
    for g in (0, 25, 50, 75, 100):
        y = base - g*sc; s += f'<line x1="{ax+70}" y1="{y}" x2="{ax+aw-30}" y2="{y}" stroke="{C["line"]}" stroke-width="1"/><text x="{ax+58}" y="{y+6}" font-size="17" fill="{C["muted"]}" text-anchor="end">{g}%</text>'
    for i, t in enumerate(ths):
        cx = ax + 120 + i*130
        hd, hf = det[i]*sc, fp[i]*sc
        hl = ' filter="url(#glow)"' if t in ("0.6", "0.8") else ''
        s += f'<rect x="{cx-44}" y="{base-hd}" width="40" height="{hd}" rx="6" fill="{C["mint"]}"{hl}/>'
        s += f'<rect x="{cx+4}" y="{base-hf}" width="40" height="{hf}" rx="6" fill="{C["coral"]}"{hl}/>'
        s += f'<text x="{cx-24}" y="{base-hd-10}" font-size="17" fill="{C["mint"]}" text-anchor="middle" font-family="{MONO}">{det[i]:.0f}</text>'
        s += f'<text x="{cx+24}" y="{base-hf-10}" font-size="17" fill="{C["coral"]}" text-anchor="middle" font-family="{MONO}">{fp[i]:.0f}</text>'
        s += f'<text x="{cx}" y="{base+34}" font-size="21" fill="{C["text"]}" text-anchor="middle" font-family="{MONO}">&gt;= {t}</text>'
    s += f'<rect x="{ax+90}" y="214" width="16" height="16" rx="4" fill="{C["mint"]}"/><text x="{ax+114}" y="228" font-size="19" fill="{C["muted"]}">attacks caught</text>'
    s += f'<rect x="{ax+280}" y="214" width="16" height="16" rx="4" fill="{C["coral"]}"/><text x="{ax+304}" y="228" font-size="19" fill="{C["muted"]}">benign items blocked</text>'
    # Panel B: single category vs max
    bx, bw = 860, 380
    s += panel(bx, bw, "Read all three categories")
    cats = [("max of 3", 94.7, C["mint"]), ("JAILBREAK", 79.1, C["violet"]), ("LEAKAGE", 31.1, C["indigo"]), ("INJECTION", 28.2, C["indigo"])]
    for i, (n, v, col) in enumerate(cats):
        y = 250 + i*88
        s += f'<text x="{bx+26}" y="{y+26}" font-size="20" fill="{C["text"]}" font-family="{MONO}">{n}</text>'
        s += f'<rect x="{bx+26}" y="{y+40}" width="{300}" height="20" rx="10" fill="{C["panel2"]}"/><rect x="{bx+26}" y="{y+40}" width="{3.0*v}" height="20" rx="10" fill="{col}"/>'
        s += f'<text x="{bx+bw-26}" y="{y+26}" font-size="22" font-weight="700" fill="{col}" text-anchor="end" font-family="{MONO}">{v}%</text>'
    s += f'<text x="{bx+26}" y="612" font-size="17" fill="{C["muted"]}">detection at &gt;= 0.6, single category</text>'
    # Panel C: tool output
    cx0, cw = 1270, 340
    s += panel(cx0, cw, "Tool output")
    s += f'<text x="{cx0+26}" y="240" font-size="19" fill="{C["muted"]}">harmless pages blocked</text>'
    s += f'<text x="{cx0+26}" y="312" font-size="64" font-weight="800" fill="{C["coral"]}" font-family="{MONO}">22%</text><text x="{cx0+190}" y="310" font-size="21" fill="{C["muted"]}">at 0.6</text>'
    s += f'<text x="{cx0+26}" y="392" font-size="64" font-weight="800" fill="{C["mint"]}" font-family="{MONO}">0%</text><text x="{cx0+190}" y="390" font-size="21" fill="{C["muted"]}">at 0.8</text>'
    s += f'<line x1="{cx0+26}" y1="430" x2="{cx0+cw-26}" y2="430" stroke="{C["line"]}"/>'
    s += f'<text x="{cx0+26}" y="470" font-size="19" fill="{C["muted"]}">attacks hidden in tool output</text>'
    s += f'<text x="{cx0+26}" y="535" font-size="44" font-weight="800" fill="{C["text"]}" font-family="{MONO}">97% <tspan fill="{C["muted"]}" font-size="26">to</tspan> 96%</text>'
    s += f'<text x="{cx0+26}" y="580" font-size="17" fill="{C["muted"]}">detected at 0.6 vs 0.8 (n=70)</text>'
    s += '</svg>'
    return page(W, H, s)

def main():
    jobs = [("banner", banner(), 1280, 640), ("architecture", architecture(), 1680, 900),
            ("pipeline", pipeline(), 1680, 700), ("threshold-chart", chart(), 1680, 700)]
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, html, w, h in jobs:
            pg = b.new_page(viewport={"width": w, "height": h})
            pg.set_content(html); pg.wait_for_timeout(300)
            pg.screenshot(path=str(OUT / f"{name}.png")); pg.close(); print("wrote", name)
        b.close()

if __name__ == "__main__":
    main()
