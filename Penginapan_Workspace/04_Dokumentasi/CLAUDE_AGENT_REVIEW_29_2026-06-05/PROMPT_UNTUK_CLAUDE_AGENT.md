# Prompt Untuk Claude Agent

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
