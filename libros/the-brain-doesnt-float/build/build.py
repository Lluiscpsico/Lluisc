#!/usr/bin/env python3
"""Build KDP files for *The Brain Doesn't Float* from the master manuscript.

Outputs (in ../kdp):
  - interior PDF, 6 x 9 in, no bleed (paperback / hardcover interior)
  - EPUB (Kindle eBook)
  - DOCX, 6 x 9 in (editable copy)

Requires: pandoc, weasyprint, EB Garamond installed as a system font.
Usage: python3 build.py
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT / "manuscrito" / "the_brain_doesnt_float_EN.md"
OUT = ROOT / "kdp"
BASENAME = "the_brain_doesnt_float_KDP_6x9"

TITLE = "The Brain Doesn’t Float"
SUBTITLE = "Wisdom and Neuroscience on How to Return to the Body"
AUTHOR = "Lluís Carballo"
SERIES = "The Embodied Mind · The Seven Centers"
VOLUME = "Volume I"


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def titlecase(s):
    small = {"a", "an", "and", "the", "of", "to", "in", "on", "for", "from", "with"}
    words = s.lower().split()
    return " ".join(w if (i and w in small) else w[:1].upper() + w[1:] for i, w in enumerate(words))


def split_source(md):
    i = md.index("## PROLOGUE")
    front, body = md[:i], md[i:]
    copyright_block = front[front.index("©"):front.index("\n*To my patients")].strip()
    dedication = re.search(r"^\*(To my patients.*?)\*$", front, re.M).group(1)
    return copyright_block, dedication, body


def transform(body):
    """Turn the manuscript's heading conventions into pandoc markdown with classes."""
    lines = body.split("\n")
    out = []
    toc = []  # (level, id, label, title)
    open_unit = False
    i = 0

    def close_unit():
        nonlocal open_unit
        if open_unit:
            out.append("\n::::\n")
            open_unit = False

    def nextnonblank(j):
        while j < len(lines) and not lines[j].strip():
            j += 1
        return j

    while i < len(lines):
        ln = lines[i]
        m_part = re.match(r"^# (PART [IVX]+)$", ln)
        m_h2 = re.match(r"^## (.+)$", ln)
        if m_part:
            close_unit()
            j = nextnonblank(i + 1)
            title = titlecase(lines[j][2:].strip())
            pid = slug(m_part.group(1))
            label = m_part.group(1).title().replace("Part Iv", "Part IV").replace("Part Iii", "Part III").replace("Part Ii", "Part II")
            toc.append((0, pid, label, title))
            out.append(f':::: {{.partsec}}\n\n# {title} {{.part #{pid} data-num="{label}"}}\n')
            open_unit = True
            i = j + 1
            continue
        if m_h2:
            name = m_h2.group(1).strip()
            close_unit()
            j = nextnonblank(i + 1)
            has_sub = j < len(lines) and lines[j].startswith("### ")
            if name.startswith("CHAPTER"):
                num = name.title()
                cid = slug(name)
                title = lines[j][4:].strip()
                toc.append((1, cid, num.replace("Chapter ", ""), title))
                out.append(f':::: {{.chap}}\n\n# {title} {{.chapter #{cid} data-num="{num}"}}\n')
                i = j + 1
            elif name in ("PROLOGUE", "EPILOGUE", "LETTER FROM MARCOS") and has_sub:
                label = titlecase(name)
                cid = slug(name)
                title = lines[j][4:].strip()
                toc.append((1, cid, "", f"{label}. {title}"))
                out.append(f':::: {{.chap}}\n\n# {title} {{.chapter #{cid} data-num="{label}"}}\n')
                i = j + 1
            elif name == "CONTENTS":
                i += 1
                continue
            else:
                title = titlecase(name)
                cid = slug(name)
                toc.append((1, cid, "", title))
                out.append(f':::: {{.back .{cid}}}\n\n# {title} {{.backtitle #{cid}}}\n')
                i += 1
            open_unit = True
            # epigraph / key concepts right after the title
            k = nextnonblank(i)
            if k < len(lines) and re.match(r"^\*[^*].*\*$", lines[k].strip()):
                out.append(f"\n::: epigraph\n{lines[k].strip()}\n:::\n")
                i = k + 1
                k = nextnonblank(i)
            if k < len(lines) and lines[k].startswith("**Key concepts:**"):
                kc = lines[k].replace("**Key concepts:**", "").strip()
                out.append(f"\n::: keyconcepts\n**Key concepts**  {kc}\n:::\n")
                i = k + 1
            continue
        if ln.startswith("#### "):
            head = ln[5:].strip()
            j = i + 1
            block = []
            while j < len(lines) and not lines[j].startswith("#"):
                block.append(lines[j])
                j += 1
            while block and not block[-1].strip():
                block.pop()
            out.append(f"\n::: glance\n<p class=\"glance-head\">{head}</p>\n" + "\n".join(block) + "\n:::\n")
            i = j
            continue
        if ln.startswith("### "):
            out.append("## " + ln[4:].strip())
            i += 1
            continue
        s = ln.strip()
        if s in ("*Barcelona, 2026*", "*Marcos. Barcelona, 2026.*"):
            out.append(f"\n::: signoff\n{s}\n:::\n")
            i += 1
            continue
        if s.startswith("*This is the first volume of The Embodied Mind"):
            out.append(f"\n::: seriesnote\n{s}\n:::\n")
            i += 1
            continue
        out.append(ln)
        i += 1
    close_unit()
    return "\n".join(out), toc


def pandoc_html(md):
    r = subprocess.run(
        ["pandoc", "-f", "markdown+smart-implicit_figures", "-t", "html5", "--wrap=none"],
        input=md, capture_output=True, text=True, check=True,
    )
    return r.stdout


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def front_matter_html(copyright_block, dedication, toc):
    cp = "".join(f"<p>{esc(l)}</p>" for l in copyright_block.split("\n") if l.strip())
    items = []
    for level, cid, label, title in toc:
        if level == 0:
            items.append(f'<li class="toc-part"><a href="#{cid}"><span class="toc-label">{label}</span> {esc(title)}</a></li>')
        else:
            lab = f'<span class="toc-num">{label}</span>' if label else '<span class="toc-num"></span>'
            items.append(f'<li class="toc-ch">{lab}<a href="#{cid}">{esc(title)}</a></li>')
    return f"""
<section class="front halftitle"><p class="ht">{TITLE}</p></section>
<section class="front blank"></section>
<section class="front titlepage">
  <p class="tp-series">{SERIES} · {VOLUME}</p>
  <h1 class="tp-title">{TITLE}</h1>
  <p class="tp-sub">{SUBTITLE}</p>
  <p class="tp-author">{AUTHOR}</p>
</section>
<section class="front copyright">{cp}</section>
<section class="front dedication"><p>{esc(dedication)}</p></section>
<section class="front blank"></section>
<section class="front toc"><h2 class="toc-title">Contents</h2><ul>{''.join(items)}</ul></section>
"""


CSS = """
@page {
  size: 6in 9in;
  margin: 0.8in 0.65in 0.8in 0.65in;
}
@page :left  { margin-left: 0.65in; margin-right: 0.875in;
  @top-left { content: counter(page); font: 9.5pt 'EB Garamond'; vertical-align: bottom; padding-bottom: 6pt; }
  @top-center { content: "THE BRAIN DOESN’T FLOAT"; font: 8pt 'EB Garamond'; letter-spacing: 0.14em; vertical-align: bottom; padding-bottom: 7pt; }
}
@page :right { margin-left: 0.875in; margin-right: 0.65in;
  @top-right { content: counter(page); font: 9.5pt 'EB Garamond'; vertical-align: bottom; padding-bottom: 6pt; }
  @top-center { content: string(runhead, first-except); font: italic 9pt 'EB Garamond'; vertical-align: bottom; padding-bottom: 6pt; }
}
@page :blank { @top-left { content: none; } @top-right { content: none; } @top-center { content: none; } }
@page front { @top-left { content: none; } @top-right { content: none; } @top-center { content: none; } }
@page opener { @top-left { content: none; } @top-right { content: none; } @top-center { content: none; }
  @bottom-center { content: counter(page); font: 9.5pt 'EB Garamond'; } }

html { font-family: 'EB Garamond', serif; font-size: 11.2pt; line-height: 1.42; color: #000;
  font-variant-ligatures: common-ligatures; font-kerning: normal; }
body { margin: 0; }
p { margin: 0; text-align: justify; hyphens: auto; text-indent: 1.4em; orphans: 2; widows: 2; }
h1 + p, h2 + p, .epigraph + p, .keyconcepts + p, .glance + p, .signoff + p, ul + p, ol + p, blockquote + p { text-indent: 0; }
em { font-style: italic; }
strong { font-weight: 600; }

/* front matter */
.front { page: front; break-before: page; }
.halftitle .ht { text-align: center; text-indent: 0; margin-top: 2.2in; font-size: 17pt; letter-spacing: 0.12em; text-transform: uppercase; }
.titlepage { text-align: center; break-before: right; }
.titlepage p { text-align: center; text-indent: 0; }
.tp-series { margin-top: 0.4in; font-size: 9pt; letter-spacing: 0.16em; text-transform: uppercase; }
.tp-title { margin: 1.3in 0 0.2in; font-size: 30pt; font-weight: 500; line-height: 1.1; letter-spacing: 0.02em; }
.tp-sub { font-style: italic; font-size: 13pt; line-height: 1.3; margin: 0; hyphens: manual; }
.tp-author { margin-top: 2.1in; font-size: 13pt; letter-spacing: 0.18em; text-transform: uppercase; }
.copyright { break-before: left; display: flex; flex-direction: column; justify-content: flex-end; }
.copyright p { text-indent: 0; font-size: 8.6pt; line-height: 1.35; margin-bottom: 0.55em; text-align: left; hyphens: manual; }
.copyright p:first-child { margin-top: 3.3in; }
.dedication { break-before: right; }
.dedication p { hyphens: manual; margin: 2.3in 0.2in 0; text-align: center; text-indent: 0; font-style: italic; font-size: 12pt; line-height: 1.5; }
.toc { break-before: right; }
.toc-title { font-size: 16pt; font-weight: 500; text-align: center; letter-spacing: 0.14em; text-transform: uppercase; margin: 0.35in 0 0.3in; }
.toc ul { list-style: none; margin: 0; padding: 0; }
.toc li { font-size: 10.6pt; line-height: 1.3; margin: 0 0 0.32em; }
.toc li a { color: #000; text-decoration: none; }
.toc li a::after { content: leader('.') target-counter(attr(href), page); }
.toc-part { margin-top: 0.75em !important; font-variant: small-caps; letter-spacing: 0.05em; font-size: 11pt !important; }
.toc-part .toc-label { font-weight: 600; }
.toc-ch { display: flex; }
.toc-ch .toc-num { display: inline-block; width: 1.6em; flex: none; }
.toc-ch a { flex: 1; }

/* part pages */
.partsec { break-before: right; page: opener; }
h1.part { string-set: runhead content(text); text-align: center; font-size: 22pt; font-weight: 500; margin: 1.6in 0 0.25in; line-height: 1.15; }
h1.part::before { content: attr(data-num); display: block; font-size: 10.5pt; letter-spacing: 0.24em; text-transform: uppercase; margin-bottom: 0.5em; font-weight: 400; }
.partsec p { text-indent: 0; text-align: center; margin: 0 0.25in 0.7em; font-size: 10.6pt; hyphens: manual; }
.partsec h1 + p { font-style: italic; margin-bottom: 1.4em; font-size: 11.4pt; }

/* chapter openers */
.chap, .back { break-before: right; }
h1.chapter, h1.backtitle { page: opener; string-set: runhead content(text); font-weight: 500; line-height: 1.15; margin: 0.9in 0 0.28in; font-size: 20pt; text-align: left; hyphens: manual; }
h1.chapter::before { content: attr(data-num); display: block; font-size: 9.5pt; letter-spacing: 0.24em; text-transform: uppercase; margin-bottom: 0.65em; font-weight: 400; }
h1.chapter::after, h1.backtitle::after { content: ""; display: block; width: 0.9in; border-bottom: 0.6pt solid #000; margin-top: 0.3in; }
.epigraph p { font-style: italic; text-indent: 0; text-align: left; margin: 0 0 0.9em; font-size: 11pt; hyphens: manual; }
.epigraph em { font-style: italic; }
.keyconcepts p { text-indent: 0; text-align: left; font-size: 8.8pt; line-height: 1.35; letter-spacing: 0.02em; margin: 0 0 1.6em; hyphens: manual; }
.keyconcepts strong { font-variant: small-caps; letter-spacing: 0.08em; font-weight: 600; font-size: 9.6pt; }

h2 { font-size: 11.6pt; font-weight: 600; line-height: 1.25; margin: 1.35em 0 0.55em; text-align: left; break-after: avoid; hyphens: manual; }

ul, ol { margin: 0.5em 0 0.7em; padding-left: 1.3em; }
li { margin-bottom: 0.3em; text-align: justify; hyphens: auto; }
li p { text-indent: 0; }

.glance { margin: 1.6em 0 0.4em; padding: 0.7em 0 0.55em; border-top: 0.8pt solid #000; border-bottom: 0.8pt solid #000; break-inside: avoid; font-size: 10pt; line-height: 1.36; }
.glance p.glance-head { text-indent: 0; font-variant: small-caps; letter-spacing: 0.1em; font-weight: 600; font-size: 10.6pt; margin-bottom: 0.45em; text-align: left; }
.glance ul { margin: 0; padding-left: 1.1em; }
.glance li { margin-bottom: 0.28em; }

.signoff p { text-align: right; text-indent: 0; margin-top: 0.8em; font-style: italic; }
.seriesnote p { text-indent: 0; margin-top: 1.6em; font-style: italic; font-size: 10.4pt; border-top: 0.5pt solid #000; padding-top: 0.8em; }

/* back matter */
.back { font-size: 10.4pt; }
.back h1.backtitle { font-size: 18pt; }
.back .epigraph p { font-size: 10.6pt; }
.glossary ul, .recommended-reading ul { list-style: none; padding-left: 0; }
.glossary li, .recommended-reading li { padding-left: 1.2em; text-indent: -1.2em; margin-bottom: 0.55em; line-height: 1.36; }
.references p { text-indent: -1.6em; padding-left: 1.6em; margin-bottom: 0.45em; text-align: left; font-size: 9.6pt; line-height: 1.33; hyphens: manual; }
.references .epigraph p { text-indent: 0; padding-left: 0; font-size: 10.4pt; }
.back.about-the-author, .back.where-to-find-the-author { break-before: page; }
.about-the-author p, .where-to-find-the-author p { text-indent: 0; margin-bottom: 0.7em; }
"""


def build_pdf(body_html, front_html):
    from weasyprint import HTML

    html = f"""<!doctype html><html lang="en-US"><head><meta charset="utf-8">
<title>{TITLE}</title><meta name="author" content="{AUTHOR}"><style>{CSS}</style></head>
<body>{front_html}{body_html}</body></html>"""
    pdf = OUT / f"{BASENAME}_interior.pdf"
    HTML(string=html, base_url=str(OUT)).write_pdf(pdf)
    return pdf


EPUB_CSS = """
body { font-family: serif; line-height: 1.45; }
p { text-indent: 1.3em; margin: 0; text-align: justify; }
h1 + p, h2 + p, div + p, ul + p { text-indent: 0; }
h1 { margin: 2em 0 0.6em; line-height: 1.2; page-break-before: always; }
h1.part, h1.chapter { text-align: center; }
h2 { font-size: 1.1em; margin: 1.4em 0 0.5em; }
.epigraph p { font-style: italic; text-indent: 0; margin-bottom: 0.8em; }
.keyconcepts p { text-indent: 0; font-size: 0.85em; margin-bottom: 1.4em; }
.glance { border-top: 1px solid #444; border-bottom: 1px solid #444; padding: 0.6em 0; margin: 1.4em 0; font-size: 0.93em; }
.glance-head { font-weight: bold; text-indent: 0; font-variant: small-caps; }
.signoff p { text-align: right; font-style: italic; }
.references p { text-indent: -1.5em; padding-left: 1.5em; margin-bottom: 0.4em; text-align: left; }
"""


def build_epub(pmd):
    # Pandoc metadata + same structure; data-num labels become visible subtitles.
    md = re.sub(r'^# (.+?) \{\.(part|chapter) #(\S+) data-num="([^"]+)"\}',
                lambda m: f"# {m.group(4)}: {m.group(1)} {{.{m.group(2)} #{m.group(3)}}}" if m.group(2) == "part"
                else f"# {m.group(4)} — {m.group(1)} {{.{m.group(2)} #{m.group(3)}}}", pmd, flags=re.M)
    css = HERE / "epub.css"
    css.write_text(EPUB_CSS, encoding="utf-8")
    meta = HERE / "epub-meta.yaml"
    meta.write_text(f"""---
title:
  - type: main
    text: "{TITLE}"
  - type: subtitle
    text: "{SUBTITLE}"
creator:
  - role: author
    text: "{AUTHOR}"
belongs-to-collection: "{SERIES}"
group-position: 1
lang: en-US
rights: "© {AUTHOR}, 2026. All rights reserved."
---
""", encoding="utf-8")
    epub = OUT / f"{BASENAME.replace('_6x9', '')}_ebook.epub"
    src = HERE / "_epub.md"
    src.write_text(md, encoding="utf-8")
    subprocess.run(["pandoc", str(meta), str(src), "-f", "markdown+smart", "-o", str(epub), "--toc", "--toc-depth=1",
                    "--split-level=1", f"--css={css}", "--metadata", "toc-title=Contents"],
                   check=True)
    return epub


def build_docx(pmd, copyright_block, dedication):
    from docx import Document
    from docx.shared import Inches, Pt
    ref = HERE / "reference_6x9.docx"
    raw = subprocess.run(["pandoc", "--print-default-data-file", "reference.docx"],
                         capture_output=True, check=True).stdout
    ref.write_bytes(raw)
    d = Document(str(ref))
    for s in d.sections:
        s.page_width, s.page_height = Inches(6), Inches(9)
        s.left_margin = s.right_margin = Inches(0.75)
        s.top_margin = s.bottom_margin = Inches(0.8)
        s.gutter = Inches(0.15)
    st = d.styles
    for name in ("Normal", "Body Text", "First Paragraph"):
        if name in [x.name for x in st]:
            st[name].font.name = "EB Garamond"
            st[name].font.size = Pt(11)
    d.save(str(ref))
    md = re.sub(r'^# (.+?) \{\.(part|chapter) #(\S+) data-num="([^"]+)"\}',
                lambda m: f"# {m.group(4)}: {m.group(1)}" if m.group(2) == "part" else f"# {m.group(4)} — {m.group(1)}",
                pmd, flags=re.M)
    head = f"""---
title: "{TITLE}"
subtitle: "{SUBTITLE}"
author: "{AUTHOR}"
lang: en-US
---

{copyright_block}

*{dedication}*

"""
    docx = OUT / f"{BASENAME}.docx"
    subprocess.run(["pandoc", "-f", "markdown+smart", "-o", str(docx), f"--reference-doc={ref}", "--toc", "--toc-depth=1"],
                   input=head + md, text=True, check=True)
    return docx


def main():
    OUT.mkdir(exist_ok=True)
    md = SRC.read_text(encoding="utf-8")
    copyright_block, dedication, body = split_source(md)
    pmd, toc = transform(body)
    (HERE / "_structured.md").write_text(pmd, encoding="utf-8")
    body_html = pandoc_html(pmd)
    front = front_matter_html(copyright_block, dedication, toc)
    targets = sys.argv[1:] or ["pdf", "epub", "docx"]
    if "pdf" in targets:
        print("PDF:", build_pdf(body_html, front))
    if "epub" in targets:
        print("EPUB:", build_epub(pmd))
    if "docx" in targets:
        print("DOCX:", build_docx(pmd, copyright_block, dedication))


if __name__ == "__main__":
    main()
