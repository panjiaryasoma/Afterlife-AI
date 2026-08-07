# Synthetic Generator Reuse Audit

**Status:** COMPLETE

## Purpose

Audit generator sintetis pre-production untuk menentukan bagian yang masih
layak dipertahankan dan bagian yang harus ditulis ulang sebelum digunakan
dalam production pipeline.

Generator lama diperlakukan sebagai reference material dan tidak disalin
secara wholesale ke production repository.

## Decision Labels

- `PROMOTE` ? konsep dapat dipertahankan dengan perubahan minimal.
- `ADAPT` ? konsep dipertahankan tetapi implementation harus disesuaikan.
- `REWRITE` ? responsibility tetap diperlukan tetapi implementation lama diganti.
- `REFERENCE_ONLY` ? hanya digunakan sebagai historical reference.

## Component Audit

| Component | Decision | Production decision |
|---|---|---|
| Grouped split by `scenario_group_id` | PROMOTE | Pertahankan grouped train/validation/test split |
| Primary seed `42` | PROMOTE | Gunakan sebagai primary reproducibility seed |
| Robustness seeds `42`, `137`, `2026` | PROMOTE | Pertahankan untuk robustness checks |
| Candidate/oracle artifact separation | PROMOTE | Oracle probability tidak masuk training feature table |
| Deterministic rerun verification | PROMOTE | Seed dan config sama harus menghasilkan output identik |
| Artifact SHA-256 hashing | PROMOTE | Pertahankan dalam dataset manifest |
| Split assignment artifact | PROMOTE | Simpan group assignment untuk setiap split |
| Dataset manifest | ADAPT | Gunakan schema dan artifact paths production |
| Structural dataset audit | ADAPT | Selaraskan dengan schema v2 |
| Leakage audit | ADAPT | Gunakan forbidden inputs dari schema v2 |
| Model feature allowlist | ADAPT | Schema v2 menjadi source of truth |
| Binary synthetic outcome mechanism | ADAPT | Probability recipe harus ditulis dan versioned ulang |
| Synthetic row contracts | REWRITE | Gunakan production contracts `afterlife_ai.*` |
| Sampling catalog | REWRITE | Turunkan dari active schema dan domain rules |
| Category-action compatibility | REWRITE | Jangan menduplikasi domain truth generator lama |
| Candidate generation | REWRITE | Ikuti semantics production planner |
| Cost and price sampling | REWRITE | Parameter baru harus eksplisit dan terdokumentasi |
| Demand and capacity sampling | REWRITE | Ikuti current feasibility semantics |
| Timing/window sampling | REWRITE | Ikuti safety dan commercial-window contracts |
| Latent outcome formula | REWRITE | Coefficient lama tidak diwariskan sebagai truth |
| Generator orchestration | REWRITE | Gunakan current production package structure |
| Old generated dataset | REFERENCE_ONLY | Bukan final training dataset |
| Old dataset metrics | REFERENCE_ONLY | Historical comparison saja |
| Old model artifacts | REFERENCE_ONLY | Tidak boleh menjadi selected production model |
| Old benchmark result | REFERENCE_ONLY | Benchmark baru wajib dijalankan |

## Schema Compatibility

Production model contract menggunakan:

```text
10 categorical features
20 numeric features
```

Schema v2 merupakan source of truth untuk model features.

Canonical fields:

```text
target:
simulated_rescue_outcome

latent generator field:
generator_success_probability

inference output:
estimated_rescue_success_score

grouping:
scenario_group_id
business_profile_id
```

Identifier, target, oracle probability, post-decision fields, optimizer output,
fixture score, dan expected-value fields yang bergantung pada model score tidak
boleh menjadi estimator input.

## Leakage Policy

Production generator harus memisahkan:

```text
candidate training table
??? model-eligible features
??? grouping metadata

oracle artifact
??? generator_success_probability
??? latent generator diagnostics
```

Grouping identifiers boleh digunakan untuk splitting tetapi tidak boleh masuk
estimator feature matrix.

## Reproducibility Policy

```yaml
primary_seed: 42

robustness_seeds:
  - 42
  - 137
  - 2026

split:
  train: 0.70
  validation: 0.15
  test: 0.15
  unit: scenario_group_id

requirements:
  random_row_split: forbidden
  group_leakage: 0
  same_seed_same_config_same_output: true
```

Test split hanya digunakan setelah generator configuration dibekukan.

## Final Reuse Decision

```yaml
promote:
  - grouped split
  - deterministic seeds
  - oracle separation
  - split assignment artifact
  - reproducibility verification
  - artifact hashing

adapt:
  - model feature allowlist
  - dataset manifest
  - dataset audit
  - leakage audit
  - binary outcome mechanism

rewrite:
  - production contracts
  - sampling catalog
  - candidate generation
  - numeric distributions
  - outcome probability recipe
  - generator orchestration

reference_only:
  - old generated datasets
  - old benchmark results
  - old trained model artifacts
```

## Conclusion

Generator pre-production menyediakan beberapa pola engineering yang layak
dipertahankan, terutama grouped splitting, reproducibility, oracle separation,
dan artifact auditing.

Implementation production tetap dibangun terhadap schema v2, active domain
rules, executable evaluation contracts, dan current production package
structure.

Tidak ada implementation atau trained artifact lama yang dianggap production
source of truth.
