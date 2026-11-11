"""Same inputs through ApplyGuardrail (PROMPT_ATTACK filter) at several tiers/strengths.
Creates temporary guardrails (tagged purpose=igc-bench-temp) and ALWAYS deletes them in `finally`.
  python bench/compare_apply_guardrail.py --corpus corpus/corpus.jsonl --out results/DATE/ag_corpus.jsonl
"""
import argparse, json, pathlib, random, sys, time
from concurrent.futures import ThreadPoolExecutor

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from run import load  # noqa: E402

CONFIGS = [("classic_high", "CLASSIC", "HIGH"), ("standard_high", "STANDARD", "HIGH"), ("standard_medium", "STANDARD", "MEDIUM"), ("standard_low", "STANDARD", "LOW")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="corpus/corpus.jsonl"); ap.add_argument("--deepset", action="store_true")
    ap.add_argument("--out", required=True); ap.add_argument("--region", default="us-east-1"); ap.add_argument("--rate", type=float, default=10.0)
    a = ap.parse_args()
    rows = load(a)
    ctl = boto3.client("bedrock", region_name=a.region)
    rt = boto3.client("bedrock-runtime", region_name=a.region, config=Config(retries={"max_attempts": 1}, max_pool_connections=32))
    created = {}

    def apply(gid, text):
        for i in range(6):
            try:
                return rt.apply_guardrail(guardrailIdentifier=gid, guardrailVersion="DRAFT", source="INPUT", content=[{"text": {"text": text}}])["action"] == "GUARDRAIL_INTERVENED"
            except ClientError as e:
                if e.response["Error"]["Code"] != "ThrottlingException": return "ERR:" + e.response["Error"]["Code"]
                time.sleep(min(0.3 * 2 ** i, 4) * (0.5 + random.random()))
        return "ERR:Throttling"

    try:
        for name, tier, strength in CONFIGS:
            kw = dict(name=f"igc-bench-{name}", description="temporary benchmark guardrail", blockedInputMessaging="blocked", blockedOutputsMessaging="blocked",
                      tags=[{"key": "purpose", "value": "igc-bench-temp"}],
                      contentPolicyConfig={"filtersConfig": [{"type": "PROMPT_ATTACK", "inputStrength": strength, "outputStrength": "NONE", "inputAction": "BLOCK", "inputEnabled": True}],
                                           "tierConfig": {"tierName": tier}})
            if tier == "STANDARD": kw["crossRegionConfig"] = {"guardrailProfileIdentifier": "us.guardrail.v1:0"}
            gid = ctl.create_guardrail(**kw)["guardrailId"]; created[name] = gid
            for _ in range(40):
                if ctl.get_guardrail(guardrailIdentifier=gid, guardrailVersion="DRAFT")["status"] == "READY": break
                time.sleep(2)
        results = {n: [None] * len(rows) for n in created}
        for name, gid in created.items():
            t0 = time.perf_counter()
            with ThreadPoolExecutor(max_workers=8) as ex:
                futs = []
                for i, r in enumerate(rows):
                    wait = t0 + i / a.rate - time.perf_counter()
                    if wait > 0: time.sleep(wait)
                    futs.append(ex.submit(apply, gid, r["text"]))
                results[name] = [f.result() for f in futs]
            print(f"{name}: done, errors={sum(isinstance(x, str) for x in results[name])}")
        with open(a.out, "w", encoding="utf-8") as f:
            for i, r in enumerate(rows):
                f.write(json.dumps({"id": r["id"], "group": r["group"], "label": r["label"], **{n: results[n][i] for n in results}}) + "\n")
    finally:
        for name, gid in created.items():
            try: ctl.delete_guardrail(guardrailIdentifier=gid); print("deleted", name)
            except Exception as e: print("DELETE FAILED", name, gid, e)


if __name__ == "__main__":
    main()
