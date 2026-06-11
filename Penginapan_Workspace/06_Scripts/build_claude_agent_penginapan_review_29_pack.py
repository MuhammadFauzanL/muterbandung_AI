from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"
PACK_DIR = ROOT / "Penginapan_Workspace" / "04_Dokumentasi" / "CLAUDE_AGENT_REVIEW_29_2026-06-05"

CHILD_PARENT_INPUT = CURATED_DIR / "PENGINAPAN_NEEDS_REVIEW_20_CHILD_PARENT_CANDIDATE_2026-06-05.csv"
MANUAL_CHECK_INPUT = CURATED_DIR / "PENGINAPAN_NEEDS_REVIEW_9_MANUAL_CHECK_2026-06-05.csv"

COMBINED_OUTPUT = PACK_DIR / "PENGINAPAN_CLAUDE_REVIEW_29_PARENT_CHILD_DECISION_2026-06-05.csv"
CHILD_PARENT_COPY = PACK_DIR / "PENGINAPAN_REVIEW_20_ACCEPTED_BY_RULE_CANDIDATE_2026-06-05.csv"
MANUAL_CHECK_COPY = PACK_DIR / "PENGINAPAN_REVIEW_9_MANUAL_CHECK_2026-06-05.csv"
README_OUTPUT = PACK_DIR / "README_INSTRUKSI_CLAUDE_AGENT.md"
PROMPT_OUTPUT = PACK_DIR / "PROMPT_UNTUK_CLAUDE_AGENT.md"
SUMMARY_OUTPUT = PACK_DIR / "claude_agent_review_29_summary_2026-06-05.json"


KEEP_COLUMNS = [
    "review_target_id",
    "penginapan_id",
    "name",
    "property_type",
    "flag_group",
    "audit_recommendation",
    "parent_candidate_id",
    "parent_candidate_name",
    "parent_candidate_property_type",
    "parent_candidate_distance_km",
    "parent_candidate_name_ratio",
    "parent_candidate_token_score",
    "parent_candidate_score",
    "decision_group",
    "decision_status",
    "decision_reason",
    "google_maps_search_query",
    "google_maps_search_url",
    "manual_decision",
    "manual_note",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_review_file(path: Path, review_group: str) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df["review_group_for_claude"] = review_group
    df["claude_decision"] = ""
    df["claude_evidence_url"] = ""
    df["claude_reason"] = ""
    return df


def write_markdown_files(summary: dict) -> None:
    readme = f"""# Instruksi Claude Agent - Review 29 Parent/Child Penginapan

Folder ini berisi paket kecil untuk mengecek 29 data penginapan yang masih perlu keputusan parent/child.

## File Utama

| File | Isi |
|---|---|
| `PENGINAPAN_CLAUDE_REVIEW_29_PARENT_CHILD_DECISION_2026-06-05.csv` | Gabungan 29 data yang perlu dicek |
| `PENGINAPAN_REVIEW_20_ACCEPTED_BY_RULE_CANDIDATE_2026-06-05.csv` | 20 kandidat child-parent dari aturan sistem |
| `PENGINAPAN_REVIEW_9_MANUAL_CHECK_2026-06-05.csv` | 9 data yang perlu cek manual lebih hati-hati |
| `PROMPT_UNTUK_CLAUDE_AGENT.md` | Instruksi siap pakai untuk Claude |

## Tujuan

Tentukan apakah setiap `name` adalah child/detail dari `parent_candidate_name`, atau sebenarnya properti mandiri.

## Pilihan Keputusan

| Keputusan | Pakai Jika |
|---|---|
| `accept_as_child` | Nama adalah kamar/unit/detail dari parent kandidat |
| `accept_as_parent` | Nama adalah properti mandiri dan layak jadi target scraping |
| `hold_low_priority` | Masih ragu atau tidak penting untuk jalur utama |
| `needs_more_check` | Bukti belum cukup, perlu cek lanjutan |

## Cara Cek

1. Buka CSV gabungan 29 data.
2. Cek kolom `name`, `parent_candidate_name`, `parent_candidate_distance_km`, dan `parent_candidate_score`.
3. Search Google Maps/Web dengan nama child dan parent.
4. Catat keputusan di `claude_decision`.
5. Isi `claude_evidence_url` dengan URL bukti yang dipakai.
6. Isi `claude_reason` singkat, maksimal 1-2 kalimat.

## Ringkasan Data

| Kelompok | Jumlah |
|---|---:|
| 20 kandidat child-parent | {summary["child_parent_rows"]} |
| 9 manual check | {summary["manual_check_rows"]} |
| Total | {summary["combined_rows"]} |

## Catatan

Jangan menghapus data. Kalau tidak yakin, gunakan `hold_low_priority` atau `needs_more_check`.
"""

    prompt = """# Prompt Untuk Claude Agent

Saya sedang membersihkan dataset penginapan MuterBandung.ai.

Tolong review file:

`PENGINAPAN_CLAUDE_REVIEW_29_PARENT_CHILD_DECISION_2026-06-05.csv`

Tugas Anda:

1. Untuk setiap baris, tentukan apakah `name` adalah child/detail dari `parent_candidate_name`, atau properti mandiri.
2. Gunakan search Google Maps/Web jika perlu.
3. Jangan hanya memakai skor. Skor hanya petunjuk awal.
4. Isi keputusan dengan salah satu:
   - `accept_as_child`
   - `accept_as_parent`
   - `hold_low_priority`
   - `needs_more_check`
5. Berikan URL bukti jika tersedia.
6. Berikan alasan singkat, jangan panjang.

Aturan penting:

- Jika nama mengandung tipe kamar seperti `Deluxe Room`, `Standard Room`, `Double Room`, `Twin Room`, biasanya itu child.
- Jika nama mengandung villa/house, jangan langsung dianggap child. Cek apakah itu properti mandiri.
- Jika koordinat dekat tapi nama berbeda jauh, jangan otomatis digabung.
- Jika ragu, jangan paksa. Gunakan `hold_low_priority` atau `needs_more_check`.

Output yang saya butuhkan:

| review_target_id | name | parent_candidate_name | claude_decision | claude_evidence_url | claude_reason |
|---|---|---|---|---|---|
"""

    README_OUTPUT.write_text(readme, encoding="utf-8")
    PROMPT_OUTPUT.write_text(prompt, encoding="utf-8")


def main() -> None:
    PACK_DIR.mkdir(parents=True, exist_ok=True)

    child_parent = read_review_file(CHILD_PARENT_INPUT, "accepted_by_rule_candidate")
    manual_check = read_review_file(MANUAL_CHECK_INPUT, "manual_check")
    combined = pd.concat([child_parent, manual_check], ignore_index=True)

    columns = ["review_group_for_claude", *KEEP_COLUMNS, "claude_decision", "claude_evidence_url", "claude_reason"]
    columns = [column for column in columns if column in combined.columns]
    combined = combined[columns]

    combined.to_csv(COMBINED_OUTPUT, index=False)
    shutil.copy2(CHILD_PARENT_INPUT, CHILD_PARENT_COPY)
    shutil.copy2(MANUAL_CHECK_INPUT, MANUAL_CHECK_COPY)

    summary = {
        "generated_at": now_iso(),
        "pack_dir": str(PACK_DIR),
        "combined_rows": int(len(combined)),
        "child_parent_rows": int(len(child_parent)),
        "manual_check_rows": int(len(manual_check)),
        "outputs": {
            "combined": str(COMBINED_OUTPUT),
            "child_parent_copy": str(CHILD_PARENT_COPY),
            "manual_check_copy": str(MANUAL_CHECK_COPY),
            "readme": str(README_OUTPUT),
            "prompt": str(PROMPT_OUTPUT),
        },
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown_files(summary)

    print(f"pack_dir={PACK_DIR}")
    print(f"combined_rows={summary['combined_rows']}")
    print(f"child_parent_rows={summary['child_parent_rows']}")
    print(f"manual_check_rows={summary['manual_check_rows']}")
    print(f"combined_output={COMBINED_OUTPUT}")
    print(f"readme={README_OUTPUT}")
    print(f"prompt={PROMPT_OUTPUT}")


if __name__ == "__main__":
    main()
