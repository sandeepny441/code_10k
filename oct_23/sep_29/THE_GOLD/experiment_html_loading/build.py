#!/usr/bin/env python3
"""Bake content/*.md into content-bundle.js and report-standalone.html.

Local workflow: index.html + content-bundle.js (file:// OK after build).
Share: send only report-standalone.html — CONTENT_BUNDLE inlined, no siblings.
Scale: 10 chapters × 10 topics (100+) is fine; compact JSON embed stays
tens of KB to low hundreds KB for typical topic data.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
MANIFEST = CONTENT / "manifest.json"
BUNDLE = ROOT / "content-bundle.js"
INDEX = ROOT / "index.html"
STANDALONE = ROOT / "report-standalone.html"

BUNDLE_SCRIPT_TAG = '<script src="content-bundle.js"></script>'
JSON_SEP = (",", ":")  # compact embed for 100+ topics


def parse_front_matter(raw: str) -> tuple[dict[str, str], str]:
    text = raw.lstrip("\ufeff")
    fm: dict[str, str] = {}
    body = text
    m = re.match(r"^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$", text)
    if m:
        body = m.group(2)
        for line in m.group(1).splitlines():
            i = line.find(":")
            if i < 1:
                continue
            key = line[:i].strip()
            val = line[i + 1 :].strip()
            if (val.startswith('"') and val.endswith('"')) or (
                val.startswith("'") and val.endswith("'")
            ):
                val = val[1:-1]
            fm[key] = val
    return fm, body


def parse_markdown_topic(raw: str) -> dict[str, str]:
    fm, body = parse_front_matter(raw)
    bullets: list[str] = []
    for line in body.splitlines():
        bm = re.match(r"^\s*[-*+]\s+(.+)$", line)
        if bm:
            bullets.append(bm.group(1).strip())
    return {
        "chapter": fm.get("chapter", ""),
        "topic": fm.get("topic", ""),
        "question": fm.get("question") or fm.get("topic", ""),
        "chart_title": fm.get("chart_title") or fm.get("topic", ""),
        "unit": fm.get("unit", ""),
        "prefix": fm.get("prefix", ""),
        "suffix": fm.get("suffix", ""),
        "decimals": fm.get("decimals", ""),
        "data": fm.get("data", ""),
        "commentary": "\n".join(bullets),
    }


def discover_topic_files() -> tuple[str, list[Path]]:
    """Return (title, ordered list of .md paths). Prefer manifest.json."""
    if MANIFEST.is_file():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        title = manifest.get("title") or "GSE Loan Sales"
        paths: list[Path] = []
        for ch in manifest.get("chapters") or []:
            for topic in ch.get("topics") or []:
                rel = topic.get("file")
                if not rel:
                    continue
                paths.append(CONTENT / rel)
        return title, paths

    title = "GSE Loan Sales"
    paths = []
    for folder in sorted(CONTENT.iterdir()):
        if not folder.is_dir():
            continue
        name = folder.name
        if not re.match(r"^\d{2}-", name):
            continue
        for md in sorted(folder.glob("*.md")):
            paths.append(md)
    return title, paths


def ensure_index_loads_bundle() -> None:
    """Ensure index.html loads content-bundle.js before the main app script."""
    if not INDEX.is_file():
        return
    html = INDEX.read_text(encoding="utf-8")
    if "content-bundle.js" in html:
        return
    marker = "<script>\n/* ========================================================="
    if marker in html:
        html = html.replace(marker, BUNDLE_SCRIPT_TAG + "\n" + marker, 1)
    else:
        html = re.sub(
            r"(<script(?![^>]*\bsrc=)[^>]*>)",
            BUNDLE_SCRIPT_TAG + r"\n\1",
            html,
            count=1,
        )
    INDEX.write_text(html, encoding="utf-8")
    print(f"Updated {INDEX.name}: added {BUNDLE_SCRIPT_TAG}")


def write_bundle(title: str, rows: list[dict[str, str]]) -> None:
    payload = {"title": title, "rows": rows}
    js = "window.CONTENT_BUNDLE = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n"
    BUNDLE.write_text(js, encoding="utf-8")
    print(f"Wrote {BUNDLE.name} ({len(rows)} topic(s), title={title!r})")


def compact_bundle_js(title: str, rows: list[dict[str, str]]) -> str:
    payload = {"title": title, "rows": rows}
    return (
        "window.CONTENT_BUNDLE="
        + json.dumps(payload, ensure_ascii=False, separators=JSON_SEP)
        + ";"
    )


def rewrite_standalone_loader(html: str) -> str:
    """CONTENT_BUNDLE-only loader — no fetch, no content/, no localhost."""
    new_loader = """async function loadFromMarkdown() {
  const status = $("uploadStatus");
  try {
    if (window.CONTENT_BUNDLE && Array.isArray(window.CONTENT_BUNDLE.rows)) {
      applyBundle(window.CONTENT_BUNDLE);
      status.classList.remove("error");
      status.textContent = "Content loaded from inlined CONTENT_BUNDLE";
      return;
    }
    status.classList.add("error");
    status.textContent = "CONTENT_BUNDLE missing. Rebuild with python3 build.py.";
  } catch (err) {
    status.classList.add("error");
    status.textContent = "Load failed: " + (err && err.message ? err.message : err) + ". Rebuild with python3 build.py.";
    console.error(err);
  }
}"""
    pattern = re.compile(
        r"async function loadFromMarkdown\(\) \{[\s\S]*?\n\}\n\nloadFromMarkdown\(\);",
        re.M,
    )
    if not pattern.search(html):
        raise SystemExit("Could not rewrite loadFromMarkdown for standalone")
    return pattern.sub(new_loader + "\n\nloadFromMarkdown();", html, count=1)


def write_standalone(title: str, rows: list[dict[str, str]]) -> None:
    """Full index.html with CONTENT_BUNDLE inlined; no required sibling files."""
    if not INDEX.is_file():
        raise SystemExit(f"Missing template: {INDEX}")

    html = INDEX.read_text(encoding="utf-8")

    # Offline fonts: system-ui first; Inter Tight only if installed locally.
    html = re.sub(
        r'<link rel="preconnect" href="https://fonts\.googleapis\.com">\s*',
        "",
        html,
    )
    html = re.sub(
        r'<link rel="preconnect" href="https://fonts\.gstatic\.com"[^>]*>\s*',
        "",
        html,
    )
    html = re.sub(
        r'<link href="https://fonts\.googleapis\.com/css2\?[^"]*" rel="stylesheet">\s*',
        "",
        html,
    )
    html = html.replace(
        '--f: "Inter Tight", "Helvetica Neue", Helvetica, Arial, sans-serif;',
        '--f: system-ui, -apple-system, "Segoe UI", Roboto, "Inter Tight",'
        ' "Helvetica Neue", Helvetica, Arial, sans-serif;',
    )

    # Drop Excel / SheetJS CDN if present (no upload in standalone).
    html = re.sub(
        r'<script[^>]+src="https://cdn\.jsdelivr\.net/npm/xlsx[^"]*"[^>]*>\s*</script>\s*',
        "",
        html,
        flags=re.I,
    )
    html = re.sub(
        r'<script[^>]+src="https://unpkg\.com/xlsx[^"]*"[^>]*>\s*</script>\s*',
        "",
        html,
        flags=re.I,
    )

    inline = "<script>\n" + compact_bundle_js(title, rows) + "\n</script>"
    if BUNDLE_SCRIPT_TAG in html:
        html = html.replace(BUNDLE_SCRIPT_TAG, inline, 1)
    elif re.search(r'<script\s+src="content-bundle\.js"\s*>\s*</script>', html):
        html = re.sub(
            r'<script\s+src="content-bundle\.js"\s*>\s*</script>',
            inline,
            html,
            count=1,
        )
    else:
        marker = "<script>\n/* ========================================================="
        if marker in html:
            html = html.replace(marker, inline + "\n" + marker, 1)
        else:
            raise SystemExit("Could not locate insertion point for CONTENT_BUNDLE")

    html = rewrite_standalone_loader(html)

    html = html.replace(
        "Source: content/*.md baked into content-bundle.js (python3 build.py). "
        "Figures are illustrative sample data.",
        "Source: inlined CONTENT_BUNDLE from content/*.md "
        "(python3 build.py → report-standalone.html). "
        "Figures are illustrative sample data.",
    )
    html = html.replace(
        "Prefers window.CONTENT_BUNDLE (from content-bundle.js / build.py)\n"
        "   so file:// works without a server. Optional fetch fallback if\n"
        "   the bundle script is missing.",
        "Standalone: window.CONTENT_BUNDLE is inlined in this file.\n"
        "   No content/, content-bundle.js, or localhost required.",
    )
    html = html.replace(
        "Markdown experiment · rock bot",
        "Standalone · single-file share",
    )

    STANDALONE.write_text(html, encoding="utf-8")
    size = STANDALONE.stat().st_size
    print(f"Wrote {STANDALONE.name} ({len(rows)} topic(s), {size:,} bytes)")


def main() -> None:
    title, paths = discover_topic_files()
    rows: list[dict[str, str]] = []
    for path in paths:
        if not path.is_file():
            raise SystemExit(f"Missing topic file: {path}")
        rows.append(parse_markdown_topic(path.read_text(encoding="utf-8")))
    if not rows:
        raise SystemExit("No Markdown topics found under content/")
    write_bundle(title, rows)
    ensure_index_loads_bundle()
    write_standalone(title, rows)


if __name__ == "__main__":
    main()
