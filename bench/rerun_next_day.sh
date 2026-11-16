#!/usr/bin/env bash
# One-shot rerun of the whole benchmark on a different day, to measure day-to-day score drift.
# Scheduled by cron; removes its own cron line when done. Safe to run by hand: bash bench/rerun_next_day.sh
set -u
cd "$(dirname "$0")/.."
D=$(date -u +%Y%m%d); OUT=results/$D; mkdir -p "$OUT"; PY=.venv/bin/python
{
  echo "rerun started $(date -u +%FT%TZ)"
  $PY bench/run.py --out "$OUT/igc_corpus_raw.jsonl"
  sleep 20
  $PY bench/run.py --prefilter --out "$OUT/igc_corpus_prefilter.jsonl"
  sleep 20
  $PY bench/run.py --deepset --out "$OUT/igc_deepset_raw.jsonl"
  $PY bench/report.py "$OUT/igc_corpus_raw.jsonl" "$OUT/igc_deepset_raw.jsonl" > "$OUT/report.md"
  # day-over-day drift against the first run
  $PY - <<'PY'
import json, glob, os
first = "results/20261111"; now = sorted(glob.glob("results/2*"))[-1]
for name in ("igc_corpus_raw.jsonl", "igc_deepset_raw.jsonl"):
    a = {json.loads(l)["id"]: json.loads(l) for l in open(f"{first}/{name}")}; b = {json.loads(l)["id"]: json.loads(l) for l in open(f"{now}/{name}")}
    ids = [i for i in a if i in b and a[i]["ok"] and b[i]["ok"]]
    same = sum(a[i]["scores"] == b[i]["scores"] for i in ids); smax = sum(max(a[i]["scores"].values()) == max(b[i]["scores"].values()) for i in ids)
    print(f"{name}: {first} vs {now}: n={len(ids)} identical 3-category scores={same/len(ids)*100:.1f}% identical max={smax/len(ids)*100:.1f}%")
PY
  echo "rerun finished $(date -u +%FT%TZ)"
} >> "$OUT/rerun.log" 2>&1
crontab -l 2>/dev/null | grep -v 'rerun_next_day.sh' | crontab -
