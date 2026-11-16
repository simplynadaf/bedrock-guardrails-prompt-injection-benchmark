
### results/20261116/igc_corpus_raw.jsonl
rows=411 scored=411 errors_excluded=0  attacks=206 benign=205

| max-score threshold | detection | 95% CI | false positives | 95% CI |
|---|---|---|---|---|
| >= 0.2 | 197/206 = 95.6% | 91.9-97.7 | 28/205 = 13.7% | 9.6-19.0 |
| >= 0.4 | 196/206 = 95.1% | 91.3-97.3 | 24/205 = 11.7% | 8.0-16.8 |
| >= 0.6 | 195/206 = 94.7% | 90.7-97.0 | 22/205 = 10.7% | 7.2-15.7 |
| >= 0.8 | 169/206 = 82.0% | 76.2-86.7 | 11/205 = 5.4% | 3.0-9.4 |
| >= 1.0 | 136/206 = 66.0% | 59.3-72.1 | 9/205 = 4.4% | 2.3-8.1 |

| single category (>=0.6) | detection | false positives |
|---|---|---|
| max | 195/206 = 94.7% | 22/205 |
| JAILBREAK | 164/206 = 79.6% | 11/205 |
| PROMPT_INJECTION | 60/206 = 29.1% | 5/205 |
| PROMPT_LEAKAGE | 64/206 = 31.1% | 9/205 |

| group | n | share flagged >=0.2 | >=0.6 | >=0.8 | mean max |
|---|---|---|---|---|---|
| atk_direct | 24 | 100% | 100% | 100% | 0.99 |
| atk_hijack | 12 | 92% | 83% | 67% | 0.68 |
| atk_indirect_tool_output | 70 | 97% | 97% | 96% | 0.91 |
| atk_leak | 20 | 95% | 95% | 50% | 0.75 |
| atk_multilingual | 30 | 97% | 97% | 83% | 0.90 |
| atk_obfuscated | 20 | 85% | 85% | 85% | 0.84 |
| atk_persona | 15 | 100% | 100% | 100% | 0.99 |
| atk_soft | 15 | 93% | 87% | 20% | 0.60 |
| neg_discussion_quotes | 15 | 33% | 27% | 7% | 0.21 |
| neg_encoded_blob | 13 | 62% | 62% | 62% | 0.62 |
| neg_encoded_id | 17 | 0% | 0% | 0% | 0.00 |
| neg_imperative | 25 | 32% | 12% | 4% | 0.13 |
| neg_multilingual | 30 | 0% | 0% | 0% | 0.00 |
| neg_plain_chat | 40 | 0% | 0% | 0% | 0.00 |
| neg_security_talk | 25 | 4% | 4% | 4% | 0.03 |
| neg_tool_output | 40 | 15% | 15% | 0% | 0.09 |

score histogram attacks: {0.0: 9, 0.2: 1, 0.4: 1, 0.6: 26, 0.8: 33, 1.0: 136}
score histogram benign:  {0.0: 177, 0.2: 4, 0.4: 2, 0.6: 11, 0.8: 2, 1.0: 9}
latency p50=292ms p95=387ms; throttle retries=0; text units=421

### results/20261116/igc_deepset_raw.jsonl
rows=546 scored=546 errors_excluded=0  attacks=203 benign=343

| max-score threshold | detection | 95% CI | false positives | 95% CI |
|---|---|---|---|---|
| >= 0.2 | 107/203 = 52.7% | 45.9-59.5 | 0/343 = 0.0% | 0.0-1.1 |
| >= 0.4 | 106/203 = 52.2% | 45.4-59.0 | 0/343 = 0.0% | 0.0-1.1 |
| >= 0.6 | 91/203 = 44.8% | 38.1-51.7 | 0/343 = 0.0% | 0.0-1.1 |
| >= 0.8 | 58/203 = 28.6% | 22.8-35.1 | 0/343 = 0.0% | 0.0-1.1 |
| >= 1.0 | 25/203 = 12.3% | 8.5-17.5 | 0/343 = 0.0% | 0.0-1.1 |

| single category (>=0.6) | detection | false positives |
|---|---|---|
| max | 91/203 = 44.8% | 0/343 |
| JAILBREAK | 75/203 = 36.9% | 0/343 |
| PROMPT_INJECTION | 40/203 = 19.7% | 0/343 |
| PROMPT_LEAKAGE | 15/203 = 7.4% | 0/343 |

| group | n | share flagged >=0.2 | >=0.6 | >=0.8 | mean max |
|---|---|---|---|---|---|
| deepset_neg | 343 | 0% | 0% | 0% | 0.00 |
| deepset_pos | 203 | 53% | 45% | 29% | 0.38 |

score histogram attacks: {0.0: 96, 0.2: 1, 0.4: 15, 0.6: 33, 0.8: 33, 1.0: 25}
score histogram benign:  {0.0: 343, 0.2: 0, 0.4: 0, 0.6: 0, 0.8: 0, 1.0: 0}
latency p50=282ms p95=401ms; throttle retries=0; text units=553
