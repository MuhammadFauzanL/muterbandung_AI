# Targeted Verified Updates - 2026-05-25

Generated at: `2026-05-25T14:13:06.763671Z`
Backup: `Dataset\3_Curated\DATABASE_WISATA_LABELED_V2_REVIEWED.csv.bak_targeted_20260525_211306`

## Applied Updates

### LOC-016 - Chinatown Bandung

Reason: Multiple public sources mark Chinatown Bandung/Jalan Kelenteng closed or permanently closed; hide from active recommendations until a reliable reopening source is found.

Sources:
- https://www.exploresunda.com/jalan-Kelenteng-Bandung.html
- https://idetrips.com/chinatown-bandung-en/
- https://wanderlog.com/place/details/54367

Before:

```json
{
  "display_status": "active_candidate",
  "curation_action": "keep",
  "is_active_verified": "",
  "review_status": "auto_approved"
}
```

After:

```json
{
  "display_status": "temporarily_hidden",
  "curation_action": "hide_temporarily",
  "is_active_verified": "False",
  "review_status": "needs_review"
}
```

## Skipped Updates

No updates skipped.
