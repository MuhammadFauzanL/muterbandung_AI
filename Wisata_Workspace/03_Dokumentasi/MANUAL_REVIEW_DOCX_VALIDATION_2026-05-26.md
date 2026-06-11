# Manual Review DOCX Validation - 2026-05-26

Generated at: `2026-05-26T07:16:36.839495Z`
DOCX: `MANUAL_REVIEW_BATCH_1_TARGETED_DATA_COMPLETION_2026-05-25_FILLED_SAFE_REVIEW.docx`
Dataset: `Dataset\3_Curated\DATABASE_WISATA_LABELED_V2_REVIEWED.csv`
Plan queue: `Dataset\3_Curated\targeted_data_completion_top50.csv`

## Summary

- Records parsed: `20`
- Safe to apply automatically: `2`
- Blocked / needs review: `18`

## Per-Location Result

| Location | Decision | Safe | Issues | Safe Updates |
|---|---|---:|---|---|
| `LOC-155` Curug Panganten | unanswered | NO | active_status_decision_unclear_or_unanswered | - |
| `LOC-162` Rumah Putih Cukul | active | YES | missing_evidence_url_for_status_change, weekday_hours_present_without_source_url, weekend_hours_present_without_source_url | media_available=True, media_image_url=https://assets.pikiran-rakyat.com/crop/0x0:0x0/720x0/webp/photo/2024/06/14/2246854323.jpg, media_source=manual_review_docx, media_audit_status=accepted |
| `LOC-123` Museum Pendidikan Nasional UPI | active | NO | apply_decision_not_explicit_yes_or_boleh, missing_evidence_url_for_status_change | - |
| `LOC-158` Situ Ninah (Situ Datar) | active | YES | - | is_active_verified=True, review_status=reviewed |
| `LOC-228` Tanjung Duriat | remove_or_exclude_requested | NO | apply_decision_not_explicit_yes_or_boleh, facility_text_present_without_source_url, missing_evidence_url_for_status_change, remove_or_exclude_requested_requires_manual_confirmation_before_apply | - |
| `LOC-134` Bukit Bintang Bandung (Patahan Lembang) | active | NO | facility_text_present_without_source_url, missing_evidence_url_for_status_change, weekend_hours_present_without_source_url | - |
| `LOC-192` Curug Ngebul Gununghalu | unanswered | NO | active_status_decision_unclear_or_unanswered, apply_decision_not_explicit_yes_or_boleh, facility_text_present_without_source_url, weekday_hours_present_without_source_url, weekend_hours_present_without_source_url | - |
| `LOC-196` Curug Walanda Citatah | unanswered | NO | active_status_decision_unclear_or_unanswered, apply_decision_not_explicit_yes_or_boleh, facility_text_present_without_source_url, weekday_hours_present_without_source_url, weekend_hours_present_without_source_url | - |
| `LOC-226` Gunung Nini Pangalengan | active | NO | apply_decision_not_explicit_yes_or_boleh, facility_text_present_without_source_url, missing_evidence_url_for_status_change | - |
| `LOC-174` Lereng Anteng Panoramic Coffee | active | NO | apply_decision_not_explicit_yes_or_boleh, facility_text_present_without_source_url, missing_evidence_url_for_status_change | - |
| `LOC-220` Nimo Jungle Hot Spring | active | NO | apply_decision_not_explicit_yes_or_boleh, missing_evidence_url_for_status_change, weekday_hours_present_without_source_url, weekend_hours_present_without_source_url | - |
| `LOC-176` Padepokan Dayang Sumbi | unanswered | NO | active_status_decision_unclear_or_unanswered, apply_decision_not_explicit_yes_or_boleh | - |
| `LOC-133` Punclut Bandung (Puncak Ciumbuleuit) | unanswered | NO | active_status_decision_unclear_or_unanswered, apply_decision_not_explicit_yes_or_boleh | - |
| `LOC-195` Sungai Cikahuripan Green Canyon Saguling | unanswered | NO | active_status_decision_unclear_or_unanswered, apply_decision_not_explicit_yes_or_boleh | - |
| `LOC-213` Taman Cibeunying | unanswered | NO | active_status_decision_unclear_or_unanswered, apply_decision_not_explicit_yes_or_boleh | - |
| `LOC-023` Curug Malela | unanswered | NO | active_status_decision_unclear_or_unanswered, apply_decision_not_explicit_yes_or_boleh | - |
| `LOC-044` Jans Park (Jatinangor National Park) | unanswered | NO | active_status_decision_unclear_or_unanswered, apply_decision_not_explicit_yes_or_boleh | - |
| `LOC-138` Kebun Teh Sukawana | unanswered | NO | active_status_decision_unclear_or_unanswered, apply_decision_not_explicit_yes_or_boleh | - |
| `LOC-166` Muara Rahong Hills | unanswered | NO | active_status_decision_unclear_or_unanswered, apply_decision_not_explicit_yes_or_boleh | - |
| `LOC-069` Pemandian Cipanas Cileungsing | unanswered | NO | active_status_decision_unclear_or_unanswered, apply_decision_not_explicit_yes_or_boleh | - |

## Rule Notes

- Status changes require explicit decision plus evidence URL.
- `HAPUS` / out-of-scope requests are blocked for manual confirmation before dataset mutation.
- Hours/facility free text is not applied unless it has source URL and parseable structured value.
- Google cached thumbnail media URLs are blocked because they are unstable evidence.