# PARHAF report set (French)

38 inbox messages of route `report_received`, built from PARHAF by `scripts/build_parhaf_set.py`
(seed 2026). Each message is a short, fixed French cover text plus the first report of one PARHAF
case, copied verbatim (none had to be shortened). No text in this folder was written or rewritten by a
language model. It complements the German GraSCCo set: French clinical text written by physicians, not
by a generator model.

## Source

- **Dataset:** PARHAF, HealthDataHub, train split (`data/train-00000-of-00001.parquet`, downloaded
  2026-10-13 from https://huggingface.co/datasets/HealthDataHub/PARHAF). 4,254 fictitious patient cases;
  according to the dataset card the reports were written by hand by resident physicians
  (paper arXiv:2603.20494). Names are fictitious. French health system, not Swiss.
- **Licence:** Licence Ouverte / Etalab 2.0 and CC BY 4.0, as shown on the dataset card. This folder
  follows CC BY 4.0: source named, licence linked, changes listed. The data licence of the rest of
  `data/` (CDLA-Permissive-2.0) does **not** apply to the PARHAF text in `messages.jsonl`.
- Report types picked (seeded, first report of a case only): 12 hospital stays (CRH), 10 consultations
  (CRC), 4 operation notes (CRO, fewer cases have one as first report), 6 pathology reports
  (ANAPATH), 6 emergency department reports (URGENCES).

## Changes and labels

1. Surrounding whitespace removed; nothing else changed in the report text.
2. A fictitious cover text, subject, sender (fictitious institutions, `.example` domains, `000` fax
   numbers) and received time were added by template.
3. Labels by fixed rule, not reviewed by a person: route `report_received`, deadline `today`,
   assignee doctor, no clinical flag. The rule is the same as for GraSCCo: a report goes to the doctor
   today anyway, so the safety net is not needed for it; a flag on a report is counted as a false alarm.

Each row stores the PARHAF case id, report type and the SHA-256 of the original report in `provenance`.
