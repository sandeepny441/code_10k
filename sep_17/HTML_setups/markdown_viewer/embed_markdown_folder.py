#!/usr/bin/env python3
"""Pack a Markdown folder into markdown_folder_viewer.html.

Browsers block sibling-file access when you double-click an HTML page, so
notes are packed into the file itself. If you move the HTML next to a new
notes folder, run this script again — or serve the folder and the viewer
will pick up Markdown sitting beside it.

Usage:
  python3 embed_markdown_folder.py
  python3 embed_markdown_folder.py path/to/notes markdown_folder_viewer.html
  python3 embed_markdown_folder.py --serve
  python3 embed_markdown_folder.py --clear
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import sys
from pathlib import Path

START = "<!-- EMBEDDED_FOLDER_START -->"
END = "<!-- EMBEDDED_FOLDER_END -->"
SKIP_NAMES = {".ds_store", "manifest.json", "thumbs.db"}
SKIP_DIRS = {".git", ".obsidian", "node_modules", "__pycache__"}
PREFERRED_LIBRARIES = ("md_uploaded", "markdown", "notes", "md")
IMAGE_EXT = {".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp"}
MD_EXT = {".md"}


def has_markdown(folder: Path) -> bool:
    for path in folder.rglob("*.md"):
        if any(part.startswith(".") or part in SKIP_DIRS for part in path.relative_to(folder).parts):
            continue
        return True
    return False


def find_library(html_dir: Path) -> Path:
    for name in PREFERRED_LIBRARIES:
        candidate = html_dir / name
        if candidate.is_dir() and has_markdown(candidate):
            return candidate

    children = [
        path
        for path in sorted(html_dir.iterdir())
        if path.is_dir() and not path.name.startswith(".") and path.name not in SKIP_DIRS
    ]
    with_md = [path for path in children if has_markdown(path)]
    wrappers = [
        path
        for path in with_md
        if any(child.is_dir() and has_markdown(child) for child in path.iterdir())
    ]
    if len(wrappers) == 1:
        return wrappers[0]
    if wrappers:
        return wrappers[0]
    if with_md:
        return html_dir
    raise SystemExit(f"No Markdown folder found next to {html_dir}")


def collect_files(folder: Path) -> list[dict]:
    entries: list[dict] = []
    for path in sorted(folder.rglob("*")):
        if not path.is_file():
            continue
        relative_parts = path.relative_to(folder).parts
        if any(part.startswith(".") or part in SKIP_DIRS for part in relative_parts):
            continue
        if path.name.lower() in SKIP_NAMES:
            continue
        suffix = path.suffix.lower()
        rel = path.relative_to(folder).as_posix()
        if suffix in MD_EXT:
            entries.append({"path": rel, "text": path.read_text(encoding="utf-8")})
        elif suffix in IMAGE_EXT:
            mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            if suffix == ".svg":
                mime = "image/svg+xml"
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            entries.append({"path": rel, "dataUrl": f"data:{mime};base64,{encoded}"})
    if not any("text" in entry for entry in entries):
        raise SystemExit(f"No Markdown files found in {folder}")
    return entries


def payload_json(root: str, files: list[dict]) -> str:
    raw = json.dumps({"root": root, "files": files}, ensure_ascii=False, indent=2)
    return raw.replace("<", "\\u003c")


def wrap_payload(raw: str) -> str:
    return (
        f"{START}\n"
        '    <script type="application/json" id="embeddedFolder">\n'
        f"{raw}\n"
        "    </script>\n"
        f"    {END}"
    )


def replace_embed(html: str, block: str) -> str:
    start = html.find(START)
    end = html.find(END)
    if start == -1 or end == -1 or end < start:
        raise SystemExit("Could not find EMBEDDED_FOLDER markers in the HTML file.")
    end += len(END)
    return html[:start] + block + html[end:]


def write_manifest(folder: Path, html_dir: Path, files: list[dict]) -> None:
    library = "" if folder.resolve() == html_dir.resolve() else folder.name
    manifest = {
        "root": folder.name,
        "library": library,
        "files": [entry["path"] for entry in files],
    }
    text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    (html_dir / "manifest.json").write_text(text, encoding="utf-8")
    if library:
        (folder / "manifest.json").write_text(text, encoding="utf-8")


def serve(html_path: Path, port: int) -> None:
    import http.server
    import os
    import socketserver
    import webbrowser

    directory = html_path.parent.resolve()
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
        url = f"http://127.0.0.1:{port}/{html_path.name}"
        print(f"Serving {directory}")
        print(f"Open {url}")
        print("The viewer will load whatever Markdown folder sits next to the HTML.")
        print("Press Ctrl+C to stop.")
        webbrowser.open(url)
        httpd.serve_forever()


def main() -> int:
    parser = argparse.ArgumentParser(description="Embed a Markdown folder into the viewer HTML.")
    parser.add_argument("folder", nargs="?", help="Folder of .md files and images. Default: auto-detect next to the HTML.")
    parser.add_argument("html", nargs="?", default="markdown_folder_viewer.html", help="Viewer HTML to update")
    parser.add_argument("--clear", action="store_true", help="Remove the embedded folder")
    parser.add_argument("--serve", action="store_true", help="Open the viewer over a local server so it can pick up a sibling Markdown folder")
    parser.add_argument("--port", type=int, default=8765, help="Port for --serve")
    args = parser.parse_args()

    folder_arg = args.folder
    html_path = Path(args.html)
    if folder_arg and folder_arg.lower().endswith((".html", ".htm")) and not Path(folder_arg).is_dir():
        html_path = Path(folder_arg)
        folder_arg = None
    if not html_path.is_file():
        raise SystemExit(f"HTML file not found: {html_path}")

    if args.clear:
        files: list[dict] = []
        root = ""
        folder = None
    else:
        folder = Path(folder_arg) if folder_arg else find_library(html_path.parent)
        if not folder.is_dir():
            raise SystemExit(f"Folder not found: {folder}")
        files = collect_files(folder)
        root = folder.name

    html = html_path.read_text(encoding="utf-8")
    html_path.write_text(replace_embed(html, wrap_payload(payload_json(root, files))), encoding="utf-8")

    if args.clear:
        print(f"Cleared embedded folder from {html_path}")
    else:
        write_manifest(folder, html_path.parent, files)
        md_count = sum(1 for entry in files if "text" in entry)
        image_count = len(files) - md_count
        print(f"Embedded {md_count} Markdown file(s) and {image_count} image(s) from {folder} into {html_path}")
        print("Double-click the HTML to view the packed notes.")
        print("Or run with --serve after moving the HTML next to a new Markdown folder.")

    if args.serve:
        serve(html_path, args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
