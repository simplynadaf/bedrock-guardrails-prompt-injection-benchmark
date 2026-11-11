"""Run a corpus through InvokeGuardrailChecks, paced, writing one JSON row per input.

  python bench/run.py --corpus corpus/corpus.jsonl --out results/DATE/igc_corpus_raw.jsonl
  python bench/run.py --deepset --out results/DATE/igc_deepset_raw.jsonl
  add --prefilter to strip base64/hex blobs first; --region to test other regions
"""
import argparse, json, pathlib, sys, time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import igc


def load(args):
    if args.deepset:
        import pyarrow.parquet as pq
        d = pq.read_table(pathlib.Path(__file__).resolve().parent.parent / "data" / "deepset.parquet").to_pydict()
        return [{"id": f"deepset-{i:04d}", "text": t, "label": y, "group": "deepset_pos" if y else "deepset_neg", "role": "user", "lang": "mixed"}
                for i, (t, y) in enumerate(zip(d["text"], d["label"]))]
    return [json.loads(l) for l in open(args.corpus, encoding="utf-8")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="corpus/corpus.jsonl"); ap.add_argument("--deepset", action="store_true")
    ap.add_argument("--out", required=True); ap.add_argument("--region", default="us-east-1")
    ap.add_argument("--rate", type=float, default=12.0, help="requests/second; documented quota is 1,500/min (25 rps)")
    ap.add_argument("--prefilter", action="store_true")
    a = ap.parse_args()
    rows = load(a); client = igc.make_client(a.region); pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)

    def one(r):
        text = igc.strip_blobs(r["text"]) if a.prefilter else r["text"]
        res = igc.check(client, text, role=r["role"])
        return {**{k: r[k] for k in ("id", "group", "label", "role", "lang")}, "chars": len(text), **res}

    t0 = time.perf_counter(); futs = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for i, r in enumerate(rows):
            wait = t0 + i / a.rate - time.perf_counter()
            if wait > 0: time.sleep(wait)
            futs.append(ex.submit(one, r))
        out = [f.result() for f in futs]
    with open(a.out, "w", encoding="utf-8") as f:
        for o in out: f.write(json.dumps(o, ensure_ascii=False) + "\n")
    errs = [o for o in out if not o["ok"]]
    print(f"{a.out}: {len(out)} rows in {time.perf_counter()-t0:.0f}s, errors={len(errs)}, "
          f"throttle_retries={sum(o['throttles'] for o in out)}, text_units={sum(o.get('units', 0) for o in out)}")


if __name__ == "__main__":
    main()
