#!/usr/bin/env python3
"""Turn a checkout of VTM-V5 into a Quartz content folder.

Usage: python3 scripts/prepare.py <vtm-v5 checkout> <quartz content dir>

What it does, file by file (the hub itself is never changed; this works on a copy):
  * copies every .md file, skipping the machinery folders (.git, .github, .claude,
    tools) and CLAUDE.md, which is instructions for Claude sessions, not reading;
  * renames each README.md to index.md, so a folder's README becomes that folder's
    page in the wiki, and rewrites links that point at README.md to match;
  * gives every page a title (its frontmatter `name`, else its first heading) and drops
    that first heading from the body, since Quartz prints the title itself;
  * adds an "At a glance" box under the title from the frontmatter: what the entry is,
    which books it comes from, and other names it goes by.
"""
import json
import os
import re
import shutil
import sys

import yaml

SKIP_DIRS = {".git", ".github", ".claude", "tools", "node_modules"}
SKIP_FILES = {"CLAUDE.md"}
README_LINK = re.compile(r"(\]\((?:[^)\s]*/)?)README\.md(#[^)\s]*)?\)")
H1 = re.compile(r"^#\s+(.+?)\s*#*\s*$")
MD_LINK = re.compile(r"\]\((?!https?:|mailto:|#)([^)\s]+)\)")
REPO_URL = "https://github.com/UnFaventia/VTM-V5"


def split_frontmatter(text):
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[4:end], text[end + 5:]
    return None, text


def source_label(src):
    if isinstance(src, dict):
        book = str(src.get("book") or "").strip()
        pages = str(src.get("pages") or "").strip()
        if pages:
            return f"{book}, p. {pages}" if "-" not in pages and "," not in pages else f"{book}, pp. {pages}"
        return book
    return str(src)


def glance_box(meta):
    lines = []
    what = meta.get("what")
    if what:
        lines.append(f"**What:** {what}")
    sources = [s for s in (source_label(s) for s in meta.get("sources") or []) if s]
    if sources:
        lines.append("**Sources:** " + "; ".join(sources))
    aka = meta.get("also_known_as") or []
    if aka:
        lines.append("**Also known as:** " + ", ".join(str(a) for a in aka))
    if not lines:
        return ""
    body = "\n>\n".join(f"> {l}" for l in lines)
    return f"> [!abstract] At a glance\n>\n{body}\n\n"


def link_out_machinery(body, rel_dir):
    """Links into folders the wiki leaves out (tools/, CLAUDE.md...) go to GitHub instead."""
    def fix(m):
        target = m.group(1)
        path, _, anchor = target.partition("#")
        resolved = os.path.normpath(os.path.join(rel_dir, path))
        top = resolved.split(os.sep)[0]
        if top in SKIP_DIRS or resolved in SKIP_FILES:
            kind = "tree" if path.endswith("/") or "." not in os.path.basename(resolved) else "blob"
            url = f"{REPO_URL}/{kind}/main/{resolved}" + (f"#{anchor}" if anchor else "")
            return f"]({url})"
        return m.group(0)
    return MD_LINK.sub(fix, body)


def convert(text, rel_dir="."):
    raw_meta, body = split_frontmatter(text)
    meta = {}
    if raw_meta is not None:
        try:
            meta = yaml.safe_load(raw_meta) or {}
        except yaml.YAMLError:
            meta = {}

    # Find the first heading; drop it if it opens the body.
    body_lines = body.split("\n")
    first_heading = None
    for i, line in enumerate(body_lines):
        if not line.strip():
            continue
        m = H1.match(line)
        if m:
            first_heading = m.group(1)
            del body_lines[i]
        break
    body = "\n".join(body_lines).lstrip("\n")

    title = meta.get("name") or first_heading
    body = README_LINK.sub(lambda m: f"{m.group(1)}index.md{m.group(2) or ''})", body)
    body = link_out_machinery(body, rel_dir)
    body = glance_box(meta) + body

    header = raw_meta if raw_meta is not None else ""
    if title and "title" not in meta:
        header = f"title: {json.dumps(str(title), ensure_ascii=False)}\n" + header
    if header.strip():
        return f"---\n{header.rstrip()}\n---\n\n{body}"
    return body


def main(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    count = 0
    for root, dirs, files in os.walk(src):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        rel = os.path.relpath(root, src)
        for name in sorted(files):
            if not name.endswith(".md") or (rel == "." and name in SKIP_FILES):
                continue
            out_name = "index.md" if name == "README.md" else name
            out_dir = os.path.normpath(os.path.join(dst, rel))
            os.makedirs(out_dir, exist_ok=True)
            with open(os.path.join(root, name), encoding="utf-8") as f:
                text = f.read()
            with open(os.path.join(out_dir, out_name), "w", encoding="utf-8") as f:
                f.write(convert(text, rel))
            count += 1
    print(f"prepare.py: {count} pages written to {dst}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
