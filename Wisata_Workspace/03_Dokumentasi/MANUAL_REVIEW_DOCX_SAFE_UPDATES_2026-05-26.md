# Manual Review DOCX Safe Updates - 2026-05-26

Generated at: `2026-05-26T07:17:58.925131Z`
Dataset: `Dataset\3_Curated\DATABASE_WISATA_LABELED_V2_REVIEWED.csv`
Validation source: `Dataset\3_Curated\manual_review_docx_validation_results.json`
Backup: `Dataset\3_Curated\DATABASE_WISATA_LABELED_V2_REVIEWED.csv.bak_manual_docx_20260526_141758`

## Applied

### LOC-162 - Rumah Putih Cukul

Decision: `active`
Issues not applied as data fields: `missing_evidence_url_for_status_change, weekday_hours_present_without_source_url, weekend_hours_present_without_source_url`

Sources:
- https://assets.pikiran-rakyat.com/crop/0x0:0x0/720x0/webp/photo/2024/06/14/2246854323.jpg

Updates:

```json
{
  "media_available": "True",
  "media_image_url": "https://assets.pikiran-rakyat.com/crop/0x0:0x0/720x0/webp/photo/2024/06/14/2246854323.jpg",
  "media_source": "manual_review_docx",
  "media_audit_status": "accepted"
}
```

Before:

```json
{
  "media_available": "False",
  "media_image_url": "",
  "media_source": "",
  "media_audit_status": "missing"
}
```

After:

```json
{
  "media_available": "True",
  "media_image_url": "https://assets.pikiran-rakyat.com/crop/0x0:0x0/720x0/webp/photo/2024/06/14/2246854323.jpg",
  "media_source": "manual_review_docx",
  "media_audit_status": "accepted"
}
```

### LOC-158 - Situ Ninah (Situ Datar)

Decision: `active`
Issues not applied as data fields: `-`

Sources:
- https://www.instagram.com/situdatarbuana/

Updates:

```json
{
  "is_active_verified": "True",
  "review_status": "reviewed"
}
```

Before:

```json
{
  "is_active_verified": "",
  "review_status": "auto_approved"
}
```

After:

```json
{
  "is_active_verified": "True",
  "review_status": "reviewed"
}
```

## Skipped

No updates skipped.

## Important Guardrail

Only fields marked safe by `validate_manual_review_docx.py` were applied. Ambiguous status, unstructured hours, facility text without source URL, and out-of-scope/remove requests remain blocked for manual confirmation.

Note cleanup backup: `Dataset\3_Curated\DATABASE_WISATA_LABELED_V2_REVIEWED.csv.bak_manual_docx_note_cleanup_20260526_142240`
