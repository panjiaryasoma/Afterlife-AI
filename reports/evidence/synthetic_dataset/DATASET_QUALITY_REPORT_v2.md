# Synthetic Dataset Quality Report

**Status:** PASS

## Claim Boundary

Quality checks validate internal synthetic consistency only. They do not validate real-world rescue probabilities.

## Dataset Structure

- Candidate rows: 12020
- Oracle rows: 12020
- Scenario groups: 2400
- Missing cells: 0
- Duplicate rows: 0
- Duplicate candidate IDs: 0
- Candidate/oracle aligned: True

## Class Distribution

- Positive rows: 9635
- Negative rows: 2385
- Positive rate: 0.801581
- Minority rate: 0.198419

## Label Generation

- Oracle probability min: 0.258361
- Oracle probability max: 0.952370
- Oracle probability mean: 0.806126
- Observed positive rate: 0.801581
- Overall calibration gap: 0.004545

## Group Distribution

- Group count: 2400
- Min candidates/group: 2
- Max candidates/group: 8
- Mean candidates/group: 5.008333

## Errors

- None

## Warnings

- class minority berada di bawah 20%; interpretasikan ranking dan calibration dengan hati-hati
