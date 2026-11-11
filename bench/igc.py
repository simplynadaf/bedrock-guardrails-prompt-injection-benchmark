"""Thin, honest client for Bedrock InvokeGuardrailChecks.

Design rules (learned the hard way, see README):
  * an API error is never a score: results are typed {ok: True|False}
  * throttling gets exponential backoff with jitter, and is counted
  * score = max over the three prompt-attack categories (never PROMPT_INJECTION alone)
  * optional pre-filter replaces long base64/hex blobs, which score JAILBREAK=1.0 whatever they contain
"""
import random, re, time
from dataclasses import dataclass

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

CATS = ["JAILBREAK", "PROMPT_INJECTION", "PROMPT_LEAKAGE"]
PROMPT_ATTACK = {"promptAttack": {"categories": [{"category": c} for c in CATS]}}
MAX_CHARS = 100_000          # observed hard limit per request (ValidationException above it)
BLOB_RE = re.compile(r"(?:[A-Za-z0-9+/=_-]{80,}|(?:[0-9a-fA-F]{2}){40,})")


def make_client(region="us-east-1"):
    return boto3.client("bedrock-runtime", region_name=region,
                        config=Config(retries={"max_attempts": 1}, read_timeout=60, max_pool_connections=64))


def strip_blobs(text):
    """Replace long base64/hex runs with a placeholder. Trade-off: encoded attacks are no longer seen."""
    return BLOB_RE.sub(lambda m: f"[blob:{len(m.group(0))} chars]", text)


def check(client, text, role="user", checks=PROMPT_ATTACK, tries=6):
    """One call with backoff. Returns a dict; never raises for service errors."""
    throttles = 0
    for i in range(tries):
        t0 = time.perf_counter()
        try:
            r = client.invoke_guardrail_checks(messages=[{"role": role, "content": [{"text": text}]}], checks=checks)
            out = {"ok": True, "ms": (time.perf_counter() - t0) * 1000, "throttles": throttles,
                   "units": sum(v["textUnits"] for v in r["usage"].values())}
            if "promptAttack" in r["results"]:
                out["scores"] = {x["category"]: x["severityScore"] for x in r["results"]["promptAttack"]["results"]}
            if "sensitiveInformation" in r["results"]:
                out["pii"] = r["results"]["sensitiveInformation"]["results"]
            return out
        except ClientError as e:
            code = e.response["Error"]["Code"]
            if code != "ThrottlingException":
                return {"ok": False, "error": code, "message": e.response["Error"]["Message"][:200], "throttles": throttles}
            throttles += 1
            time.sleep(min(0.3 * 2 ** i, 4) * (0.5 + random.random()))
    return {"ok": False, "error": "ThrottlingException", "message": "retries exhausted", "throttles": throttles}


def max_score(res):
    return max(res["scores"].values()) if res.get("ok") and "scores" in res else None


@dataclass
class Decision:
    action: str      # allow | block | error
    score: float | None
    detail: dict


def guard_step(client, text, role="assistant", block_at=0.6, prefilter=True):
    """Gate one step of an agent loop. Fail closed: errors return action='error', callers must not treat it as allow."""
    if len(text) > MAX_CHARS:
        return Decision("error", None, {"error": "too_long", "chars": len(text)})
    res = check(client, strip_blobs(text) if prefilter else text, role=role)
    if not res["ok"]:
        return Decision("error", None, res)
    s = max_score(res)
    return Decision("block" if s >= block_at else "allow", s, res)
