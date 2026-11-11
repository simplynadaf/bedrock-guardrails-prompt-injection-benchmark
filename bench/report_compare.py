"""Side-by-side: ApplyGuardrail configs vs InvokeGuardrailChecks thresholds on the same inputs.
  python bench/report_compare.py results/DATE/igc_X.jsonl results/DATE/ag_X.jsonl
"""
import json, sys
from report import wilson, family

igc = {json.loads(l)["id"]: json.loads(l) for l in open(sys.argv[1], encoding="utf-8")}
ag = [json.loads(l) for l in open(sys.argv[2], encoding="utf-8")]
cfgs = [k for k in ag[0] if k not in ("id", "group", "label")]
rows = [r for r in ag if igc[r["id"]]["ok"] and not any(isinstance(r[c], str) for c in cfgs)]
pos = [r for r in rows if r["label"] == 1]; neg = [r for r in rows if r["label"] == 0]
print(f"compared rows={len(rows)} (attacks={len(pos)}, benign={len(neg)}); excluded for errors={len(ag)-len(rows)}")
print("\n| detector | detection | 95% CI | false positives | 95% CI |\n|---|---|---|---|---|")
def line(name, pf):
    k = sum(pf(r) for r in pos); f = sum(pf(r) for r in neg); lo, hi = wilson(k, len(pos)); flo, fhi = wilson(f, len(neg))
    print(f"| {name} | {k}/{len(pos)} = {k/len(pos)*100:.1f}% | {lo:.1f}-{hi:.1f} | {f}/{len(neg)} = {f/len(neg)*100:.1f}% | {flo:.1f}-{fhi:.1f} |")
for c in cfgs: line("ApplyGuardrail " + c, lambda r, c=c: bool(r[c]))
for t in [0.2, 0.6, 0.8, 1.0]: line(f"InvokeGuardrailChecks max>={t}", lambda r, t=t: max(igc[r["id"]]["scores"].values()) >= t)
print("\nper group: share flagged by ApplyGuardrail standard_high vs IGC>=0.6")
groups = sorted({family(r["group"]) for r in rows})
print("| group | n | AG standard_high | IGC >=0.6 | AG classic_high |\n|---|---|---|---|---|")
for g in groups:
    rs = [r for r in rows if family(r["group"]) == g]; n = len(rs)
    print(f"| {g} | {n} | {sum(bool(r['standard_high']) for r in rs)/n*100:.0f}% | {sum(max(igc[r['id']]['scores'].values())>=0.6 for r in rs)/n*100:.0f}% | {sum(bool(r['classic_high']) for r in rs)/n*100:.0f}% |")
