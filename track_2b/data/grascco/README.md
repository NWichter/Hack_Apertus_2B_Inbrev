# GraSCCo report set

40 inbox messages of route `report_received`, built from GraSCCo by
`scripts/build_grascco_set.py`. Each message is a short, fixed cover text plus one GraSCCo letter,
copied verbatim (five letters shortened, see below). No text in this folder was written or
rewritten by a language model.

## Source

- **Dataset:** GraSCCo - Graz Synthetic Clinical text Corpus, version 1.1, 63 German clinical
  letters ("formulated as letters from the hospital to the patient's GP after in-patient or
  out-patient care"). All names and dates in it are fictional; the dataset card says there is no
  relation to existing patients, clinicians or institutions, and that medical plausibility must
  not be assumed.
- **Creator:** Stefan Schulz, Medical University of Graz.
- **Record:** https://zenodo.org/records/18874981, DOI
  [10.5281/zenodo.18874981](https://doi.org/10.5281/zenodo.18874981) (all versions:
  10.5281/zenodo.6539130). Downloaded 2026-10-04; every file is checked against the MD5 checksum
  of the record, and each row stores the MD5 of its source file.
- **Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0,
  https://creativecommons.org/licenses/by/4.0/), as given in the licence field of the Zenodo
  record (v1.1 and v1). The record description additionally states a CC0 public-domain
  dedication. This folder follows the stricter of the two, CC BY 4.0: it names the source, links
  the licence and lists the changes below. The data licence of the rest of `data/`
  (CDLA-Permissive-2.0) does **not** apply to the GraSCCo text in `messages.jsonl`.

### Citation

> Modersohn L, Schulz S, Lohr C, Hahn U. GRASCCO - The First Publicly Shareable,
> Multiply-Alienated German Clinical Text Corpus. Studies in Health Technology and Informatics
> (GMDS 2022), 2022. doi:10.3233/SHTI220805
>
> Schulz S. GraSCCo (version 1.1). Zenodo, 2026. doi:10.5281/zenodo.18874981

## Changes to the original texts

1. Byte-order mark and leading/trailing whitespace removed.
2. Five letters longer than 6,000 characters were cut at the last paragraph, line or sentence
   break before character 6,000 (`Theodor.txt`, `Colon_Fake_J.txt`, `Albers.txt`,
   `Obradovic.txt`, `Fleischmann.txt`). No marker is inserted in the text; `provenance.truncated`,
   `original_chars` and `kept_chars` record the cut.
3. Each letter is preceded by a fixed cover text (templates `W1-hin`, `W2-hin`, `W3-fax`,
   `W4-email`, `W5-email`) that names a fictitious sending institution and the report type.
4. Subject (templates `S1` to `S4`), sender (fictitious `*.example` domain or fax line in the
   `000` block), channel and `received_at` were added by the script.

Nothing inside the GraSCCo text was changed: names, dates, drug names and clinic names are as in
the original. No AHV number was added.

## Selection

From the 63 letters, the script removes (in file-name order):

- letters shorter than 400 characters (none);
- letters with an e-mail address or URL (`Weil.txt`), or a phone number in Swiss format outside
  the `000` block (`Colon_Fake_H.txt`, `Xavier.txt`), because they could reach a real person;
- near-duplicates (5-character shingles, Jaccard ≥ 0.5; the later file is removed):
  `Queisser.txt`, `Schnitzler.txt`, `Tupolev_2.txt`, `Weber.txt`.

It then samples 40 of the remaining 56 with `random.Random(2026)`. Channel cycles
`hin_mail`, `fax`, `email`; institution, subject template and `received_at` (a workday in
October 2026, 07:00 to 17:59) come from `random.Random(2027)`. The output is byte-identical on
every run.

| Report type (`fields.report_type`) | Rule (first match) | n |
| --- | --- | --- |
| `Bildgebungsbefund` | radiology header in the first 400 characters | 1 |
| `Austrittsbericht` | in-patient stay mentioned (stationär, Station, Aufenthalt, Entlassung, …) | 29 |
| `Facharztbericht` | out-patient clinic or follow-up in the first 400 characters | 8 |
| `Befundbericht` | anything else | 2 |

Channels: 14 `hin_mail`, 13 `fax`, 13 `email`. Body length: mean 3,652 characters (median 3,215,
range 1,328 to 6,137), of which the GraSCCo part is on average 3,509 characters.

## Labels

Every row has the same label: route `report_received`, deadline `today`, `deadline_date` null,
assignee `doctor`, `abstain` false, `safety_flag` false, `patient` empty, `fields.report_type`
and `fields.sender_institution` from the templates. Evidence quotes are verbatim: the subject
for `route`, the report type and the institution name from the subject or cover text.

Why `safety_flag` is false: administratively, an incoming hospital or specialist report is a
report for the doctor, and the taxonomy already gives every report deadline `today`, so the
doctor sees it the same day. A system that sets the safety flag on these messages is therefore
counted as a **false alarm** on this set. This is debatable: the letters describe diagnoses,
symptoms and sometimes acute events (falls, sepsis, metastases), and a stricter reading of the
safety rule ("may contain symptoms that a clinician has to read") would flag many of them.
Report the safety-flag rate on this set separately and do not merge it into a single false-alarm
number without saying so.

Labels come from a fixed rule, not from reading each letter; no person has reviewed them.

## Validation

```
python scripts/build_grascco_set.py            # also writes data/external/grascco/grid.jsonl
python scripts/validate.py --grid data/external/grascco/grid.jsonl \
    --report data/external/grascco/validation-report.md data/grascco/messages.jsonl
```

Result: 40 rows, 36 errors, 19 warnings. All 36 errors are the check "German text contains ß":
GraSCCo is written in German and Austrian spelling, and Swiss German does not use "ß". The text
is kept verbatim on purpose, so this check does not fit this set. Warnings: 15 drug brand or company names
inside the GraSCCo text (e.g. Pantozol, Novalgin) and 4 shared cover sentences (same template,
institution and report type). There are no schema, evidence, deadline, e-mail, phone or
duplicate errors.

## Limitations

- **Not Swiss.** The letters come from German and Austrian settings (ß, Austrian and German
  addresses, "Entlassungsbrief" instead of "Austrittsbericht"); the cover texts are Swiss. The
  institution in the cover text differs from the clinic in the letterhead.
- **One route only.** The set measures recall and field extraction for `report_received` and the
  false-alarm rate of the safety flag; it says nothing about the other routes.
- **Long, clinical texts.** Bodies are several times longer than the other test messages and
  full of diagnoses; this tests whether a model keeps routing administratively instead of
  reacting to clinical content.
- **Rule-based report type.** `report_type` is a keyword rule on the original text; some letters
  could fit more than one type.
- **No examination date, no patient fields.** They are left empty instead of being extracted
  automatically.
- **Medical content not plausible by design** (see the dataset card); never use it for anything
  clinical.
