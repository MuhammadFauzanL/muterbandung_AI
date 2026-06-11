from __future__ import annotations

import html
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_MD = ROOT / "Dokumentasi_Sistem" / "MUTERBANDUNG_FILTER_PRIORITAS_2026-06-01.md"
OUTPUT_DOCX = ROOT / "Dokumentasi_Sistem" / "MUTERBANDUNG_FILTER_PRIORITAS_2026-06-01.docx"

PAGE_WIDTH_DXA = 12240
PAGE_HEIGHT_DXA = 15840
MARGIN_DXA = 1440
CONTENT_WIDTH_DXA = 9360
TABLE_INDENT_DXA = 120
TABLE_WIDTH_DXA = CONTENT_WIDTH_DXA - TABLE_INDENT_DXA


def esc(text: str) -> str:
    return html.escape(str(text), quote=False)


def strip_inline_markdown(text: str) -> str:
    text = text.strip()
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    return text


def run(text: str, *, bold: bool = False, italic: bool = False, color: str | None = None, font: str | None = None) -> str:
    props = []
    if bold:
        props.append("<w:b/>")
    if italic:
        props.append("<w:i/>")
    if color:
        props.append(f'<w:color w:val="{color}"/>')
    if font:
        props.append(f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}"/>')
    rpr = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
    preserve = ' xml:space="preserve"' if text.startswith(" ") or text.endswith(" ") else ""
    return f"<w:r>{rpr}<w:t{preserve}>{esc(text)}</w:t></w:r>"


def inline_runs(text: str) -> str:
    text = text.strip()
    pieces = []
    pos = 0
    for match in re.finditer(r"`([^`]+)`|\*\*([^*]+)\*\*", text):
        if match.start() > pos:
            pieces.append(run(text[pos : match.start()]))
        if match.group(1) is not None:
            pieces.append(run(match.group(1), font="Courier New", color="1F4D78"))
        else:
            pieces.append(run(match.group(2), bold=True))
        pos = match.end()
    if pos < len(text):
        pieces.append(run(text[pos:]))
    return "".join(pieces) or run("")


def paragraph(text: str = "", style: str = "BodyText", *, keep_next: bool = False, page_break_before: bool = False) -> str:
    extra = []
    if keep_next:
        extra.append("<w:keepNext/>")
    if page_break_before:
        extra.append("<w:pageBreakBefore/>")
    ppr_extra = "".join(extra)
    return f'<w:p><w:pPr><w:pStyle w:val="{style}"/>{ppr_extra}</w:pPr>{inline_runs(text)}</w:p>'


def bullet_paragraph(text: str) -> str:
    return (
        '<w:p><w:pPr><w:pStyle w:val="BodyText"/>'
        '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr></w:pPr>'
        f"{inline_runs(text)}</w:p>"
    )


def title_block() -> str:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return "".join(
        [
            paragraph("Muter Bandung - Prioritas Filter Website", "TitleText"),
            paragraph(
                "Decision guide untuk menyederhanakan filter user, menjaga fokus wisata, dan menempatkan hotel sebagai fitur pendukung itinerary.",
                "SubtitleText",
            ),
            paragraph(f"Sumber: {SOURCE_MD.name} | Dibuat: {generated}", "MetaText"),
            paragraph("", "BodyText"),
        ]
    )


def column_widths(column_count: int) -> list[int]:
    layouts = {
        2: [2600, TABLE_WIDTH_DXA - 2600],
        3: [2200, 2700, TABLE_WIDTH_DXA - 4900],
        4: [1150, 2300, 2900, TABLE_WIDTH_DXA - 6350],
        5: [1050, 1750, 2200, 2450, TABLE_WIDTH_DXA - 7450],
        6: [850, 1450, 1500, 2000, 2100, TABLE_WIDTH_DXA - 7900],
    }
    if column_count in layouts:
        return layouts[column_count]
    base = TABLE_WIDTH_DXA // column_count
    widths = [base] * column_count
    widths[-1] += TABLE_WIDTH_DXA - sum(widths)
    return widths


def cell(text: str, width: int, *, header: bool = False) -> str:
    fill = '<w:shd w:fill="E8EEF5"/>' if header else ""
    v_align = '<w:vAlign w:val="center"/>'
    margin = (
        "<w:tcMar>"
        '<w:top w:w="80" w:type="dxa"/>'
        '<w:left w:w="120" w:type="dxa"/>'
        '<w:bottom w:w="80" w:type="dxa"/>'
        '<w:right w:w="120" w:type="dxa"/>'
        "</w:tcMar>"
    )
    style = "TableHeader" if header else "TableText"
    text = strip_inline_markdown(text)
    return (
        "<w:tc>"
        f'<w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>{fill}{v_align}{margin}</w:tcPr>'
        f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr>{inline_runs(text)}</w:p>'
        "</w:tc>"
    )


def table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    col_count = max(len(row) for row in rows)
    widths = column_widths(col_count)
    grid = "".join(f'<w:gridCol w:w="{width}"/>' for width in widths)
    border = (
        "<w:tblBorders>"
        '<w:top w:val="single" w:sz="4" w:space="0" w:color="B8C4D4"/>'
        '<w:left w:val="single" w:sz="4" w:space="0" w:color="B8C4D4"/>'
        '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="B8C4D4"/>'
        '<w:right w:val="single" w:sz="4" w:space="0" w:color="B8C4D4"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="D7DEE8"/>'
        '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="D7DEE8"/>'
        "</w:tblBorders>"
    )
    tbl = [
        "<w:tbl>",
        "<w:tblPr>",
        '<w:tblStyle w:val="TableGrid"/>',
        f'<w:tblW w:w="{TABLE_WIDTH_DXA}" w:type="dxa"/>',
        f'<w:tblInd w:w="{TABLE_INDENT_DXA}" w:type="dxa"/>',
        '<w:tblLayout w:type="fixed"/>',
        border,
        "</w:tblPr>",
        f"<w:tblGrid>{grid}</w:tblGrid>",
    ]
    for row_index, row in enumerate(rows):
        normalized = row + [""] * (col_count - len(row))
        cant_split = "<w:cantSplit/>" if row_index == 0 else ""
        tbl.append(f"<w:tr><w:trPr>{cant_split}</w:trPr>")
        for idx, value in enumerate(normalized):
            tbl.append(cell(value, widths[idx], header=row_index == 0))
        tbl.append("</w:tr>")
    tbl.append("</w:tbl>")
    tbl.append(paragraph("", "BodyText"))
    return "".join(tbl)


def parse_markdown_tables(lines: list[str], start: int) -> tuple[list[list[str]], int]:
    rows = []
    idx = start
    while idx < len(lines) and lines[idx].strip().startswith("|"):
        raw = lines[idx].strip()
        parts = [part.strip() for part in raw.strip("|").split("|")]
        if not all(re.fullmatch(r":?-{3,}:?", part) for part in parts):
            rows.append(parts)
        idx += 1
    return rows, idx


def markdown_to_body(md: str) -> str:
    lines = md.splitlines()
    out = [title_block()]
    idx = 0
    skip_first_title = True
    while idx < len(lines):
        line = lines[idx].rstrip()
        stripped = line.strip()
        if not stripped:
            idx += 1
            continue

        if stripped.startswith("# "):
            if skip_first_title:
                skip_first_title = False
            else:
                out.append(paragraph(stripped[2:], "Heading1", keep_next=True))
            idx += 1
            continue

        if stripped.startswith("## "):
            out.append(paragraph(stripped[3:], "Heading1", keep_next=True))
            idx += 1
            continue

        if stripped.startswith("### "):
            out.append(paragraph(stripped[4:], "Heading2", keep_next=True))
            idx += 1
            continue

        if stripped.startswith("|"):
            rows, idx = parse_markdown_tables(lines, idx)
            out.append(table(rows))
            continue

        if stripped.startswith("- "):
            out.append(bullet_paragraph(stripped[2:]))
            idx += 1
            continue

        numbered = re.match(r"^\d+\.\s+(.*)", stripped)
        if numbered:
            out.append(bullet_paragraph(numbered.group(1)))
            idx += 1
            continue

        out.append(paragraph(stripped, "BodyText"))
        idx += 1
    return "".join(out)


def styles_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
    <w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/><w:color w:val="1F2937"/></w:rPr>
    <w:pPr><w:spacing w:after="120" w:line="300" w:lineRule="auto"/></w:pPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="TitleText">
    <w:name w:val="Title Text"/>
    <w:basedOn w:val="Normal"/><w:qFormat/>
    <w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:sz w:val="40"/><w:color w:val="0B2545"/></w:rPr>
    <w:pPr><w:spacing w:before="0" w:after="100" w:line="300" w:lineRule="auto"/></w:pPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="SubtitleText">
    <w:name w:val="Subtitle Text"/>
    <w:basedOn w:val="Normal"/><w:qFormat/>
    <w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="24"/><w:color w:val="4B5563"/></w:rPr>
    <w:pPr><w:spacing w:before="0" w:after="80" w:line="300" w:lineRule="auto"/></w:pPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="MetaText">
    <w:name w:val="Meta Text"/>
    <w:basedOn w:val="Normal"/>
    <w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="18"/><w:color w:val="6B7280"/></w:rPr>
    <w:pPr><w:spacing w:before="0" w:after="160" w:line="280" w:lineRule="auto"/></w:pPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="BodyText">
    <w:name w:val="Body Text"/>
    <w:basedOn w:val="Normal"/>
    <w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/><w:color w:val="1F2937"/></w:rPr>
    <w:pPr><w:spacing w:before="0" w:after="120" w:line="300" w:lineRule="auto"/></w:pPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="Heading 1"/>
    <w:basedOn w:val="Normal"/><w:qFormat/>
    <w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:sz w:val="32"/><w:color w:val="2E74B5"/></w:rPr>
    <w:pPr><w:spacing w:before="360" w:after="200" w:line="300" w:lineRule="auto"/></w:pPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="Heading 2"/>
    <w:basedOn w:val="Normal"/><w:qFormat/>
    <w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:sz w:val="26"/><w:color w:val="2E74B5"/></w:rPr>
    <w:pPr><w:spacing w:before="280" w:after="140" w:line="300" w:lineRule="auto"/></w:pPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="TableText">
    <w:name w:val="Table Text"/>
    <w:basedOn w:val="Normal"/>
    <w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="18"/><w:color w:val="1F2937"/></w:rPr>
    <w:pPr><w:spacing w:before="0" w:after="0" w:line="260" w:lineRule="auto"/></w:pPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="TableHeader">
    <w:name w:val="Table Header"/>
    <w:basedOn w:val="Normal"/>
    <w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:sz w:val="18"/><w:color w:val="0B2545"/></w:rPr>
    <w:pPr><w:spacing w:before="0" w:after="0" w:line="260" w:lineRule="auto"/></w:pPr>
  </w:style>
  <w:style w:type="table" w:styleId="TableGrid">
    <w:name w:val="Table Grid"/>
    <w:tblPr/>
  </w:style>
</w:styles>"""


def numbering_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:abstractNum w:abstractNumId="0">
    <w:multiLevelType w:val="hybridMultilevel"/>
    <w:lvl w:ilvl="0">
      <w:start w:val="1"/>
      <w:numFmt w:val="bullet"/>
      <w:lvlText w:val="•"/>
      <w:lvlJc w:val="left"/>
      <w:pPr><w:ind w:left="540" w:hanging="270"/></w:pPr>
      <w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/></w:rPr>
    </w:lvl>
  </w:abstractNum>
  <w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
</w:numbering>"""


def document_xml(body: str) -> str:
    sect = (
        "<w:sectPr>"
        f'<w:pgSz w:w="{PAGE_WIDTH_DXA}" w:h="{PAGE_HEIGHT_DXA}"/>'
        f'<w:pgMar w:top="{MARGIN_DXA}" w:right="{MARGIN_DXA}" w:bottom="{MARGIN_DXA}" w:left="{MARGIN_DXA}" w:header="709" w:footer="709" w:gutter="0"/>'
        "</w:sectPr>"
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<w:body>{body}{sect}</w:body></w:document>"
    )


def content_types_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
  <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""


def root_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""


def document_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
</Relationships>"""


def settings_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:zoom w:percent="100"/>
  <w:defaultTabStop w:val="720"/>
  <w:characterSpacingControl w:val="doNotCompress"/>
</w:settings>"""


def core_xml() -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Muter Bandung - Prioritas Filter Website</dc:title>
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>"""


def app_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Codex</Application>
</Properties>"""


def build_docx() -> None:
    md = SOURCE_MD.read_text(encoding="utf-8")
    body = markdown_to_body(md)
    OUTPUT_DOCX.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT_DOCX, "w", compression=zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", content_types_xml())
        docx.writestr("_rels/.rels", root_rels_xml())
        docx.writestr("word/document.xml", document_xml(body))
        docx.writestr("word/_rels/document.xml.rels", document_rels_xml())
        docx.writestr("word/styles.xml", styles_xml())
        docx.writestr("word/numbering.xml", numbering_xml())
        docx.writestr("word/settings.xml", settings_xml())
        docx.writestr("docProps/core.xml", core_xml())
        docx.writestr("docProps/app.xml", app_xml())
    print(OUTPUT_DOCX)


if __name__ == "__main__":
    build_docx()
