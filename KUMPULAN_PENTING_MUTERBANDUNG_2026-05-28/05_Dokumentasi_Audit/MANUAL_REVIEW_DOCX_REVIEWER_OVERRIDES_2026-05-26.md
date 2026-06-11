# Manual Review DOCX Reviewer Overrides - 2026-05-26

Generated at: `2026-05-26T07:37:39.654191Z`
Dataset: `Dataset\3_Curated\DATABASE_WISATA_LABELED_V2_REVIEWED.csv`
Backup: `Dataset\3_Curated\DATABASE_WISATA_LABELED_V2_REVIEWED.csv.bak_manual_docx_override_20260526_143739`

## Applied Overrides

### LOC-123 - Museum Pendidikan Nasional UPI

Reason: Reviewer states the destination is still active and provided a weekly hours table in the DOCX.

Sources / basis:
- manual_reviewer_docx_2026-05-26

Updates:

```json
{
  "is_active_verified": "True",
  "review_status": "reviewed",
  "jam_buka_weekday": "08:00",
  "jam_tutup_weekday": "15:00",
  "jam_buka_weekend": "Tutup",
  "jam_tutup_weekend": "Tutup"
}
```

Before:

```json
{
  "curation_note": "",
  "is_active_verified": "",
  "jam_buka_weekday": "08:00",
  "jam_buka_weekend": "",
  "jam_tutup_weekday": "15:00",
  "jam_tutup_weekend": "",
  "qa_flag_reason": "",
  "review_status": "auto_approved"
}
```

After:

```json
{
  "curation_note": "Manual reviewer override 2026-05-26: active; weekday hours summarized as 08:00-15:00. DOCX table notes Mon-Thu 08:00-11:30, 13:00-15:00; Fri 08:00-11:00, 13:00-15:30; Sat-Sun closed. Sources: manual_reviewer_docx_2026-05-26",
  "is_active_verified": "True",
  "jam_buka_weekday": "08:00",
  "jam_buka_weekend": "Tutup",
  "jam_tutup_weekday": "15:00",
  "jam_tutup_weekend": "Tutup",
  "qa_flag_reason": "manual_docx_override:active_status:opening_hours",
  "review_status": "reviewed"
}
```

### LOC-155 - Curug Panganten

Reason: Reviewer allowed applying the source that says the place opens tomorrow 07:00-16:00, plus location-specific Travelspromo media/facility text.

Sources / basis:
- https://id.trip.com/travel-guide/attraction/cisarua/curug-panganten-cimahi-137230763/
- https://travelspromo.com/htm-wisata/curug-panganten-bandung-barat/

Updates:

```json
{
  "is_active_verified": "True",
  "review_status": "reviewed",
  "jam_buka_weekday": "07:00",
  "jam_tutup_weekday": "16:00",
  "jam_buka_weekend": "07:00",
  "jam_tutup_weekend": "16:00",
  "parking_verified": "True",
  "media_available": "True",
  "media_image_url": "https://travelspromo.com/wp-content/uploads/2021/09/Air-terjun-yang-diselimuti-mitos-dan-misteri-Asrie-Kuswara-1536x1152.jpg",
  "media_source": "manual_review_docx",
  "media_audit_status": "accepted"
}
```

Before:

```json
{
  "curation_note": "",
  "is_active_verified": "",
  "jam_buka_weekday": "07:00",
  "jam_buka_weekend": "07:00",
  "jam_tutup_weekday": "17:00",
  "jam_tutup_weekend": "17:00",
  "media_audit_status": "missing",
  "media_available": "False",
  "media_image_url": "",
  "media_source": "",
  "parking_verified": "False",
  "qa_flag_reason": "",
  "review_status": "auto_approved"
}
```

After:

```json
{
  "curation_note": "Manual reviewer override 2026-05-26: active/opening hours 07:00-16:00 from Trip.com field; Travelspromo text notes area parkir, gazebo, and warung, but no toilet/mushola/ruang ganti. Sources: https://id.trip.com/travel-guide/attraction/cisarua/curug-panganten-cimahi-137230763/; https://travelspromo.com/htm-wisata/curug-panganten-bandung-barat/",
  "is_active_verified": "True",
  "jam_buka_weekday": "07:00",
  "jam_buka_weekend": "07:00",
  "jam_tutup_weekday": "16:00",
  "jam_tutup_weekend": "16:00",
  "media_audit_status": "accepted",
  "media_available": "True",
  "media_image_url": "https://travelspromo.com/wp-content/uploads/2021/09/Air-terjun-yang-diselimuti-mitos-dan-misteri-Asrie-Kuswara-1536x1152.jpg",
  "media_source": "manual_review_docx",
  "parking_verified": "True",
  "qa_flag_reason": "manual_docx_override:active_status:opening_hours:parking:media",
  "review_status": "reviewed"
}
```

### LOC-158 - Situ Ninah (Situ Datar)

Reason: Reviewer provided Instagram source with explicit weekday/weekend hours and facility text.

Sources / basis:
- https://www.instagram.com/situdatarbuana/

Updates:

```json
{
  "jam_buka_weekday": "09:00",
  "jam_tutup_weekday": "16:00",
  "jam_buka_weekend": "09:00",
  "jam_tutup_weekend": "17:00",
  "parking_verified": "True",
  "toilet_verified": "True",
  "mushola_verified": "True"
}
```

Before:

```json
{
  "curation_note": "Manual DOCX safe update 2026-05-26: applied is_active_verified, review_status. Decision=active. Sources: https://www.instagram.com/situdatarbuana/",
  "jam_buka_weekday": "00:00",
  "jam_buka_weekend": "00:00",
  "jam_tutup_weekday": "23:59",
  "jam_tutup_weekend": "23:59",
  "mushola_verified": "False",
  "parking_verified": "False",
  "qa_flag_reason": "Malam label removed: not night_verified | manual_docx_safe_update:active_status",
  "toilet_verified": "False"
}
```

After:

```json
{
  "curation_note": "Manual DOCX safe update 2026-05-26: applied is_active_verified, review_status. Decision=active. Sources: https://www.instagram.com/situdatarbuana/ | Manual reviewer override 2026-05-26: tourism hours weekday 09:00-16:00 and weekend 09:00-17:00; camping appears 24h/reservation-only, so open_24h_verified is not set. Facility text mentions parking, toilet, and musola. Sources: https://www.instagram.com/situdatarbuana/",
  "jam_buka_weekday": "09:00",
  "jam_buka_weekend": "09:00",
  "jam_tutup_weekday": "16:00",
  "jam_tutup_weekend": "17:00",
  "mushola_verified": "True",
  "parking_verified": "True",
  "qa_flag_reason": "Malam label removed: not night_verified | manual_docx_safe_update:active_status | manual_docx_override:opening_hours:facility",
  "toilet_verified": "True"
}
```

### LOC-162 - Rumah Putih Cukul

Reason: Reviewer explicitly confirms Google Maps still shows active and recent reviews.

Sources / basis:
- manual_reviewer_google_maps_observation_2026-05-26

Updates:

```json
{
  "is_active_verified": "True",
  "review_status": "reviewed",
  "jam_buka_weekday": "08:00",
  "jam_tutup_weekday": "18:00",
  "jam_buka_weekend": "08:00",
  "jam_tutup_weekend": "18:00"
}
```

Before:

```json
{
  "curation_note": "Manual DOCX safe update 2026-05-26: applied media_audit_status, media_available, media_image_url, media_source. Decision=active. Sources: https://assets.pikiran-rakyat.com/crop/0x0:0x0/720x0/webp/photo/2024/06/14/2246854323.jpg",
  "is_active_verified": "",
  "jam_buka_weekday": "08:00",
  "jam_buka_weekend": "08:00",
  "jam_tutup_weekday": "18:00",
  "jam_tutup_weekend": "18:00",
  "qa_flag_reason": "manual_docx_safe_update:media",
  "review_status": "auto_approved"
}
```

After:

```json
{
  "curation_note": "Manual DOCX safe update 2026-05-26: applied media_audit_status, media_available, media_image_url, media_source. Decision=active. Sources: https://assets.pikiran-rakyat.com/crop/0x0:0x0/720x0/webp/photo/2024/06/14/2246854323.jpg | Manual reviewer override 2026-05-26: reviewer observed Google Maps active status and recent reviews. DOCX text states operating hours 08:00-18:00 daily. Sources: manual_reviewer_google_maps_observation_2026-05-26",
  "is_active_verified": "True",
  "jam_buka_weekday": "08:00",
  "jam_buka_weekend": "08:00",
  "jam_tutup_weekday": "18:00",
  "jam_tutup_weekend": "18:00",
  "qa_flag_reason": "manual_docx_safe_update:media | manual_docx_override:active_status:opening_hours",
  "review_status": "reviewed"
}
```

### LOC-134 - Bukit Bintang Bandung (Patahan Lembang)

Reason: Reviewer notes active status and Google Maps name Puncak Bintang; hours and facility text are clear enough for core fields.

Sources / basis:
- manual_reviewer_google_maps_observation_2026-05-26

Updates:

```json
{
  "is_active_verified": "True",
  "review_status": "reviewed",
  "jam_buka_weekday": "06:00",
  "jam_tutup_weekday": "17:00",
  "jam_buka_weekend": "06:00",
  "jam_tutup_weekend": "17:00",
  "parking_verified": "True",
  "toilet_verified": "True",
  "mushola_verified": "True"
}
```

Before:

```json
{
  "curation_note": "",
  "is_active_verified": "",
  "jam_buka_weekday": "00:00",
  "jam_buka_weekend": "00:00",
  "jam_tutup_weekday": "23:59",
  "jam_tutup_weekend": "23:59",
  "mushola_verified": "False",
  "parking_verified": "False",
  "qa_flag_reason": "",
  "review_status": "auto_approved",
  "toilet_verified": "False"
}
```

After:

```json
{
  "curation_note": "Manual reviewer override 2026-05-26: active; Google Maps name observed as Puncak Bintang. Do not rename primary location_name yet; retain alias in curation_note. Facility text mentions parkir, toilet, and mushola. Sources: manual_reviewer_google_maps_observation_2026-05-26",
  "is_active_verified": "True",
  "jam_buka_weekday": "06:00",
  "jam_buka_weekend": "06:00",
  "jam_tutup_weekday": "17:00",
  "jam_tutup_weekend": "17:00",
  "mushola_verified": "True",
  "parking_verified": "True",
  "qa_flag_reason": "manual_docx_override:active_status:opening_hours:facility:alias",
  "review_status": "reviewed",
  "toilet_verified": "True"
}
```

### LOC-174 - Lereng Anteng Panoramic Coffee

Reason: Reviewer-provided text confirms active cafe context; existing hours already match the extracted weekday/weekend pattern.

Sources / basis:
- manual_reviewer_docx_2026-05-26

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
  "curation_note": "",
  "is_active_verified": "",
  "qa_flag_reason": "",
  "review_status": "auto_approved"
}
```

After:

```json
{
  "curation_note": "Manual reviewer override 2026-05-26: active cafe context confirmed in DOCX. Existing hours retained: weekday 08:00-22:00, weekend 08:00-23:00. Sources: manual_reviewer_docx_2026-05-26",
  "is_active_verified": "True",
  "qa_flag_reason": "manual_docx_override:active_status",
  "review_status": "reviewed"
}
```

### LOC-220 - Nimo Jungle Hot Spring

Reason: Reviewer-provided ticket/hour text indicates active ticketing and a repeated 08:00-20:00 daily schedule.

Sources / basis:
- https://nagantour.com/nimo-jungle-hot-spring/
- manual_reviewer_docx_2026-05-26

Updates:

```json
{
  "is_active_verified": "True",
  "review_status": "reviewed",
  "jam_buka_weekday": "08:00",
  "jam_tutup_weekday": "20:00",
  "jam_buka_weekend": "08:00",
  "jam_tutup_weekend": "20:00"
}
```

Before:

```json
{
  "curation_note": "",
  "is_active_verified": "",
  "jam_buka_weekday": "09:00",
  "jam_buka_weekend": "08:00",
  "jam_tutup_weekday": "17:00",
  "jam_tutup_weekend": "23:00",
  "qa_flag_reason": "Malam label removed: not night_verified",
  "review_status": "auto_approved"
}
```

After:

```json
{
  "curation_note": "Manual reviewer override 2026-05-26: active ticketing context and hours normalized to 08:00-20:00 daily from DOCX text. Sources: https://nagantour.com/nimo-jungle-hot-spring/; manual_reviewer_docx_2026-05-26",
  "is_active_verified": "True",
  "jam_buka_weekday": "08:00",
  "jam_buka_weekend": "08:00",
  "jam_tutup_weekday": "20:00",
  "jam_tutup_weekend": "20:00",
  "qa_flag_reason": "Malam label removed: not night_verified | manual_docx_override:active_status:opening_hours",
  "review_status": "reviewed"
}
```

### LOC-228 - Tanjung Duriat

Reason: Reviewer explicitly requests removal because it is in Jatigede and outside Bandung Raya scope.

Sources / basis:
- manual_reviewer_scope_decision_2026-05-26

Updates:

```json
{
  "display_status": "exclude_scope",
  "curation_action": "remove",
  "is_active_verified": "False",
  "review_status": "reviewed"
}
```

Before:

```json
{
  "curation_action": "keep",
  "curation_note": "",
  "display_status": "active_candidate",
  "is_active_verified": "",
  "qa_flag_reason": "",
  "review_status": "auto_approved"
}
```

After:

```json
{
  "curation_action": "remove",
  "curation_note": "Manual reviewer override 2026-05-26: removed from active recommendation scope because located in Jatigede, outside Bandung Raya. Sources: manual_reviewer_scope_decision_2026-05-26",
  "display_status": "exclude_scope",
  "is_active_verified": "False",
  "qa_flag_reason": "manual_docx_override:exclude_scope",
  "review_status": "reviewed"
}
```

## Skipped

No overrides skipped.

## Guardrail

These are explicit reviewer overrides requested after the first strict validation pass. They are marked in `curation_note` and `qa_flag_reason` so future audits can distinguish reviewer-observed facts from URL-verified facts.