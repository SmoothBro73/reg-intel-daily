"""Render a Reg Intel Daily edition (Markdown) as a whitepaper-style PDF.

Usage: python3 make_pdf.py EDITION.md OUTPUT.pdf
Needs: pip install markdown playwright (Chromium must be available to Playwright).
Expects the edition layout: a header block (Edition date / Coverage window / Top line),
sections "## 1. Key Developments" ... "## 5. Sources", then "# Podcast / Radio Script",
"## Show Notes" and "# Archive Entry".
"""
import re, sys, html, markdown
from playwright.sync_api import sync_playwright

NAVY, GOLD, INK, MUTED = "#0b2545", "#b8922a", "#1d1d1f", "#5b6370"


def field(text, label):
    m = re.search(r"\*\*" + re.escape(label) + r":\*\*\s*(.+)", text)
    return m.group(1).strip() if m else ""


def md(text):
    text = re.sub(r"([^\n])\n(- |\d+\. )", r"\1\n\n\2", text)  # lists need a blank line before them
    h = markdown.markdown(text, extensions=["extra", "sane_lists"])
    return re.sub(r'(?<!href=")(https?://[^\s<)]+)', r'<a href="\1">\1</a>', h)


def build_html(src):
    src = src.replace("\r\n", "\n")
    head, _, rest = src.partition("## 1. Key Developments")
    briefing, _, after = ("## 1. Key Developments" + rest).partition("# Podcast / Radio Script")
    script, _, after2 = after.partition("## Show Notes")
    notes, _, archive = after2.partition("# Archive Entry")
    strip = lambda s: re.sub(r"\n-{3,}\s*$", "", re.sub(r"^\s*-{3,}\s*\n", "", s.strip())).strip()
    edition, window, topline = field(head, "Edition date"), field(head, "Coverage window"), field(head, "Top line")
    # split briefing into numbered sections
    parts = re.split(r"^## (\d+\. .+)$", briefing, flags=re.M)
    sections = ""
    for i in range(1, len(parts), 2):
        title, body = parts[i].strip(), strip(parts[i + 1].replace("---", ""))
        cls = "sources" if "Sources" in title else ""
        sections += f'<section class="{cls}"><h2>{html.escape(title)}</h2>{md(body)}</section>'
    script_body = strip(re.sub(r"^\*\(Target[^\n]*\)\*\s*", "", script.strip()))
    css = f"""
    * {{ box-sizing: border-box; }}
    body {{ font-family: 'Caladea', 'DejaVu Serif', serif; color: {INK}; font-size: 10.6pt; line-height: 1.5; margin: 0; }}
    h1, h2, h3, .label, .kicker {{ font-family: 'Carlito', 'DejaVu Sans', sans-serif; }}
    a {{ color: {NAVY}; text-decoration: none; word-break: break-all; }}
    .cover {{ height: 10.99in; width: 8.5in; position: relative; page-break-after: always; background: #fff; }}
    .cover .band {{ background: {NAVY}; color: #fff; height: 5.6in; padding: 1.1in 0.95in 0 0.95in; position: relative; }}
    .cover .band:after {{ content: ""; position: absolute; left: 0.95in; bottom: 0.55in; width: 1.4in; height: 5px; background: {GOLD}; }}
    .kicker {{ letter-spacing: 0.22em; text-transform: uppercase; font-size: 10pt; color: #c9d6e3; }}
    .cover h1 {{ font-size: 46pt; line-height: 1.05; margin: 0.35in 0 0.18in; font-weight: 700; }}
    .cover .sub {{ font-size: 15pt; color: #dfe7ef; font-family: 'Caladea', serif; font-style: italic; }}
    .cover .meta {{ padding: 0.55in 0.95in 0; }}
    .cover .meta table {{ border-collapse: collapse; font-size: 10.5pt; }}
    .cover .meta td {{ padding: 4px 18px 4px 0; vertical-align: top; }}
    .label {{ color: {MUTED}; text-transform: uppercase; letter-spacing: 0.12em; font-size: 8.5pt; white-space: nowrap; }}
    .exec {{ margin: 0.4in 0.95in 0; border-left: 4px solid {GOLD}; background: #f6f3ea; padding: 16px 20px; }}
    .exec .label {{ display: block; margin-bottom: 6px; color: {NAVY}; }}
    .exec p {{ margin: 0; font-size: 12pt; line-height: 1.45; }}
    .cover .foot {{ position: absolute; bottom: 0.6in; left: 0.95in; right: 0.95in; font-size: 8.5pt; color: {MUTED};
                   border-top: 1px solid #d9dde3; padding-top: 8px; font-family: 'Carlito', sans-serif; }}
    h2 {{ color: {NAVY}; font-size: 17pt; margin: 0 0 10px; padding-bottom: 6px; border-bottom: 2px solid {GOLD}; }}
    section {{ margin-bottom: 22px; }}
    h3 {{ color: {NAVY}; font-size: 12.5pt; margin: 18px 0 2px; page-break-after: avoid; }}
    h3 + p em {{ color: {MUTED}; font-size: 9.6pt; }}
    p {{ margin: 0 0 8px; text-align: justify; hyphens: auto; }}
    ul, ol {{ margin: 0 0 10px; padding-left: 20px; }} li {{ margin-bottom: 4px; }} li p {{ margin: 0; }}
    strong {{ color: #0f1a2b; }}
    section.sources {{ font-size: 9pt; line-height: 1.4; }} section.sources p {{ text-align: left; }}
    .appendix {{ page-break-before: always; }}
    .appendix h2 .tag {{ color: {GOLD}; font-size: 10pt; letter-spacing: 0.15em; display: block; margin-bottom: 2px; }}
    .script p {{ text-align: left; }}
    .small {{ font-size: 9.4pt; }}
    """
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>
    <!--COVER--><div class="cover">
      <div class="band"><div class="kicker">Regulatory Intelligence Briefing</div>
        <h1>Reg Intel Daily</h1><div class="sub">Financial regulatory developments that matter to RBC</div></div>
      <div class="meta"><table>
        <tr><td class="label">Edition</td><td>{html.escape(edition)}</td></tr>
        <tr><td class="label">Coverage</td><td>{html.escape(window)}</td></tr></table></div>
      <div class="exec"><span class="label">Top line</span><p>{html.escape(topline)}</p></div>
      <div class="foot">Prepared from public sources. Confirmed requirements are distinguished from analysis of potential RBC impacts; analysis is labeled as such. Not legal advice.</div>
    </div><!--/COVER-->
    {sections}
    <section class="appendix script"><h2><span class="tag">APPENDIX A</span>Podcast Script</h2>{md(script_body)}</section>
    <section class="appendix small"><h2><span class="tag">APPENDIX B</span>Show Notes</h2>{md(strip(notes))}</section>
    <section class="appendix small"><h2><span class="tag">APPENDIX C</span>Archive Entry</h2>{md(strip(archive))}</section>
    </body></html>""", edition


def main(src_path, out_path):
    doc, edition = build_html(open(src_path, encoding="utf-8").read())
    header = (f'<div style="width:100%;font-family:Carlito,sans-serif;font-size:7.5pt;color:{MUTED};padding:0 0.85in;'
              f'display:flex;justify-content:space-between"><span style="color:{NAVY};font-weight:bold;letter-spacing:.12em">'
              f'REG INTEL DAILY</span><span>{html.escape(edition)}</span></div>')
    footer = (f'<div style="width:100%;font-family:Carlito,sans-serif;font-size:7.5pt;color:{MUTED};padding:0 0.85in;'
              'display:flex;justify-content:space-between"><span>For internal reference. Prepared from public sources.</span>'
              '<span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>')
    pre, _, tail = doc.partition("<!--COVER-->")
    cover, _, post = tail.partition("<!--/COVER-->")
    cover_doc, body_doc = pre + cover + "</body></html>", pre + post
    from pypdf import PdfReader, PdfWriter
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.set_content(cover_doc, wait_until="load")
        pg.pdf(path=out_path + ".cover", format="Letter", print_background=True,
               margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}, page_ranges="1")
        pg.set_content(body_doc, wait_until="load")
        pg.pdf(path=out_path + ".body", format="Letter", print_background=True, display_header_footer=True,
               header_template=header, footer_template=footer,
               margin={"top": "0.9in", "bottom": "0.9in", "left": "0.85in", "right": "0.85in"})
        b.close()
    w = PdfWriter()
    for part in (out_path + ".cover", out_path + ".body"):
        for page in PdfReader(part).pages:
            w.add_page(page)
    w.add_metadata({"/Title": f"Reg Intel Daily — {edition}", "/Author": "Reg Intel Daily"})
    with open(out_path, "wb") as f:
        w.write(f)
    import os
    os.remove(out_path + ".cover"); os.remove(out_path + ".body")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
