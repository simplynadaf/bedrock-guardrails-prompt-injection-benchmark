"""Assume the stack's role and prove the policy: one action allowed in one Region, everything else denied.
  python bench/verify_iam.py <role-arn>
"""
import sys, boto3
from botocore.exceptions import ClientError

creds = boto3.client("sts").assume_role(RoleArn=sys.argv[1], RoleSessionName="igc-verify")["Credentials"]
sess = lambda region: boto3.Session(aws_access_key_id=creds["AccessKeyId"], aws_secret_access_key=creds["SecretAccessKey"],
                                    aws_session_token=creds["SessionToken"], region_name=region)
CHK = {"promptAttack": {"categories": [{"category": "JAILBREAK"}]}}
MSG = [{"role": "user", "content": [{"text": "hello"}]}]


def attempt(label, fn, expect_ok):
    try:
        fn(); got = "allowed"
    except ClientError as e:
        got = e.response["Error"]["Code"]
    # deny checks are strict: only AccessDeniedException counts (a ValidationException would prove nothing)
    ok = got == "allowed" if expect_ok else got == "AccessDeniedException"
    print(f"{'PASS' if ok else 'FAIL'}  {label:55s} -> {got}")
    return ok


rt = lambda region: sess(region).client("bedrock-runtime")

# a REAL guardrail (created with the caller's own credentials) is needed: a made-up ID fails validation before authorization
admin = boto3.client("bedrock", region_name="us-east-1")
gid = admin.create_guardrail(name="igc-bench-verify-temp", blockedInputMessaging="blocked", blockedOutputsMessaging="blocked",
                             wordPolicyConfig={"wordsConfig": [{"text": "zzz-never-matches"}]},
                             tags=[{"key": "purpose", "value": "igc-bench-temp"}])["guardrailId"]
import time; time.sleep(5)
results = [
    attempt("InvokeGuardrailChecks in the allowed Region (us-east-1)", lambda: rt("us-east-1").invoke_guardrail_checks(messages=MSG, checks=CHK), True),
    attempt("InvokeGuardrailChecks in another Region (us-west-2)", lambda: rt("us-west-2").invoke_guardrail_checks(messages=MSG, checks=CHK), False),
    attempt("Converse (model invocation) is NOT granted", lambda: rt("us-east-1").converse(modelId="us.amazon.nova-micro-v1:0", messages=[{"role": "user", "content": [{"text": "hi"}]}], inferenceConfig={"maxTokens": 5}), False),
    attempt("ApplyGuardrail is NOT granted", lambda: rt("us-east-1").apply_guardrail(guardrailIdentifier=gid, guardrailVersion="DRAFT", source="INPUT", content=[{"text": {"text": "hi"}}]), False),
    attempt("ListGuardrails (control plane) is NOT granted", lambda: sess("us-east-1").client("bedrock").list_guardrails(), False),
]
admin.delete_guardrail(guardrailIdentifier=gid)
print("temporary guardrail deleted")
sys.exit(0 if all(results) else 1)
