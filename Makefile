# Python 3.10+ is required: boto3 for Python 3.9 stops at 1.42.x, which has no invoke_guardrail_checks.
PY      ?= .venv/bin/python
DATE    ?= $(shell date -u +%Y%m%d)
OUT     := results/$(DATE)
STACK   ?= guardrail-benchmark-iam
REGION  ?= us-east-1

venv:            ; python3.11 -m venv .venv && .venv/bin/pip install -q -r requirements.txt
corpus:          ; $(PY) bench/build_corpus.py
data:            ; $(PY) bench/fetch_deepset.py
bench:           ; mkdir -p $(OUT) && $(PY) bench/run.py --out $(OUT)/igc_corpus_raw.jsonl && $(PY) bench/run.py --prefilter --out $(OUT)/igc_corpus_prefilter.jsonl && $(PY) bench/run.py --deepset --out $(OUT)/igc_deepset_raw.jsonl
report:          ; $(PY) bench/report.py $(OUT)/igc_corpus_raw.jsonl $(OUT)/igc_corpus_prefilter.jsonl $(OUT)/igc_deepset_raw.jsonl
compare:         ; $(PY) bench/compare_apply_guardrail.py --out $(OUT)/ag_corpus.jsonl && $(PY) bench/compare_apply_guardrail.py --deepset --out $(OUT)/ag_deepset.jsonl
limits:          ; $(PY) bench/limits_probe.py $(OUT)/limits.json
deploy:          ; aws cloudformation deploy --region $(REGION) --stack-name $(STACK) --template-file infra/template.yaml --capabilities CAPABILITY_IAM --parameter-overrides TrustedPrincipalArn=$$(aws sts get-caller-identity --query Arn --output text)
verify:          ; $(PY) bench/verify_iam.py $$(aws cloudformation describe-stacks --region $(REGION) --stack-name $(STACK) --query "Stacks[0].Outputs[?OutputKey=='RoleArn'].OutputValue" --output text)
cleanup:         ; aws cloudformation delete-stack --region $(REGION) --stack-name $(STACK) && aws cloudformation wait stack-delete-complete --region $(REGION) --stack-name $(STACK)
.PHONY: venv corpus data bench report compare limits deploy verify cleanup
