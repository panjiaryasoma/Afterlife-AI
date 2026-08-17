# Frontend Comparison Protocol

## Purpose

Membandingkan presentation layer Afterlife AI secara fair antara:

- FastAPI + Jinja2 sebagai baseline Technical MVP RC
- Streamlit sebagai challenger presentation layer

Perbandingan hanya menilai karakteristik presentation layer dan integrasinya terhadap canonical Afterlife AI production pipeline.

Tidak ada perubahan domain logic, model, configuration, fixture, atau optimization behavior yang diperbolehkan hanya untuk menguntungkan salah satu frontend.

---

## Candidates

### Baseline

```yaml
frontend: FASTAPI_JINJA2
role: TECHNICAL_MVP_RC_BASELINE
status: BASELINE_UNTIL_DECISION
```

### Challenger

```yaml
frontend: STREAMLIT
role: CHALLENGER_PRESENTATION_LAYER
status: EVALUATE_AGAINST_BASELINE
```

---

## Fair Comparison Rules

Kedua frontend wajib:

1. Menggunakan fixture/input yang sama.
2. Menggunakan canonical production pipeline yang sama.
3. Menggunakan model artifact yang sama.
4. Menggunakan runtime configuration dan partner registry yang sama.
5. Tidak mengubah hard safety atau feasibility gates.
6. Tidak mengubah optimization behavior untuk menguntungkan salah satu frontend.
7. Menghasilkan canonical Rescue Decision Report yang konsisten untuk request context yang ekuivalen.
8. Mencatat perbedaan yang benar-benar berasal dari framework atau presentation layer.

---

## Fixed Comparison Run

```yaml
fixture: tests/fixtures/integration_001/RAW_INVENTORY_FIXTURE.xlsx
optimization_objective: MAXIMIZE_RECOVERY_VALUE
max_logistics_budget: 50000
minimum_expected_rescue_ratio: null
deadline_timezone: Asia/Jakarta
```

Request ID dan analysis timestamp boleh berbeda karena keduanya request-scoped metadata. Field domain/output lain yang ditentukan pipeline harus konsisten untuk input dan context ekuivalen.

---

## Dimensions

Setiap frontend dinilai pada skala 1-5.

- Development effort
- Demo clarity
- Operator usability
- UI flexibility
- Runtime stability
- Startup/setup complexity
- Docker/reproducibility
- Testability
- Maintenance burden
- Competition presentation quality

Untuk maintenance burden dan startup/setup complexity, skor lebih tinggi berarti burden/complexity lebih rendah.

### Score meaning

```text
5 = sangat kuat
4 = kuat
3 = memadai
2 = lemah
1 = sangat lemah
```

---

## Decision Rule

1. Canonical parity dan invariants adalah hard requirement.
2. Setelah hard requirements lolos, skor presentation-layer dibandingkan.
3. Jika skor total sangat dekat, competition presentation quality, demo clarity, dan operator usability menjadi tie-breaker.
4. Baseline tidak berubah sampai decision record eksplisit dibuat.
