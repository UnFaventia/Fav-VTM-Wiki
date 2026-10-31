#!/usr/bin/env python3
"""Turn checkouts of VTM-V5 (and, optionally, WoD-Archive) into a Quartz content folder.

Usage: python3 scripts/prepare.py <vtm-v5 checkout> <quartz content dir> [--wod <wod-archive checkout>]

The wiki has two sections, and the header switch flips between them (D35):
  * **VTM V5**: the whole hub, at the site root;
  * **Australia WoD**: WoD-Archive's `australia/` folder, at `australia/` on the site,
    so a link written from either repo's root (`/australia/extracts/...`) lands in the
    same place on the site as in the repo.

What it does, file by file (the repos themselves are never changed; this works on copies):
  * copies every .md file it publishes, skipping each repo's machinery (see SOURCES);
  * renames each README.md to index.md, so a folder's README becomes that folder's
    page in the wiki, and rewrites links that point at README.md to match;
  * gives every page a title (its frontmatter `name`, else its first heading) and drops
    that first heading from the body, since Quartz prints the title itself;
  * adds an "At a glance" box under the title from the frontmatter: what the entry is,
    which books it comes from, and other names it goes by;
  * uses the entry's `what` as the page description (shown in search and link previews);
  * points links at anything the wiki leaves out (machinery, PDFs, the rest of
    WoD-Archive) at the file on GitHub instead;
  * shows Fav's `[[sticky notes]]` as notes, never as wiki links: `[[…]]` is her
    note syntax in both repos, and Quartz would otherwise read it as a link.
"""
import argparse
import json
import os
import re
import shutil

import yaml

README_LINK = re.compile(r"(\]\((?!https?:)(?:[^)\s]*/)?)README\.md(#[^)\s]*)?\)")
H1 = re.compile(r"^#\s+(.+?)\s*#*\s*$")
MD_LINK = re.compile(r"\]\((?!https?:|mailto:|#)([^)\s]+)\)")
FENCE = re.compile(r"^\s*(```|~~~)")
CODE_SPAN = re.compile(r"(`+)(.+?)\1")
STICKY = re.compile(r"\[\[(.+?)\]\]")


class Source:
    """One repo feeding the wiki: which part of it is published, and where."""

    def __init__(self, root, repo_url, subdir="", site_dir="", skip_dirs=(), skip_files=()):
        self.root = root
        self.repo_url = repo_url
        self.subdir = subdir          # the published part of the repo ("" = all of it)
        self.site_dir = site_dir      # where that part sits on the site ("" = root)
        self.skip_dirs = set(skip_dirs)    # folder names skipped wherever they appear
        self.skip_files = set(skip_files)  # repo-relative paths skipped

    def published(self, repo_path):
        """Is this repo-relative path on the site? (Folders and .md files only.)"""
        parts = [p for p in repo_path.split("/") if p not in ("", ".")]
        if self.subdir:
            if parts[: len(self.subdir.split("/"))] != self.subdir.split("/"):
                return False
        if any(p in self.skip_dirs for p in parts):
            return False
        if repo_path in self.skip_files:
            return False
        base = parts[-1] if parts else ""
        return "." not in base or base.endswith(".md")


def sources(hub_root, wod_root=None):
    found = [
        Source(
            hub_root,
            "https://github.com/UnFaventia/VTM-V5",
            skip_dirs={".git", ".github", ".claude", "tools", "node_modules"},
            # Instructions for Claude sessions, not reading.
            skip_files={"CLAUDE.md"},
        )
    ]
    if wod_root:
        found.append(
            Source(
                wod_root,
                "https://github.com/UnFaventia/WoD-Archive",
                subdir="australia",
                site_dir="australia",
                skip_dirs={".git", "specs"},
                skip_files={
                    # D35: NOTES.md stays off the site; it is the build record.
                    "australia/extracts/rage-across-australia/NOTES.md",
                    # Session instructions and a session's working survey, like the
                    # hub's CLAUDE.md: for Claude, not for reading.
                    "australia/extracts/rage-across-australia/HANDOFF.md",
                    "australia/extracts/rage-across-australia/SURVEY.md",
                },
            )
        )
    return found


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
    sources_ = [s for s in (source_label(s) for s in meta.get("sources") or []) if s]
    if sources_:
        lines.append("**Sources:** " + "; ".join(sources_))
    aka = meta.get("also_known_as") or []
    if aka:
        lines.append("**Also known as:** " + ", ".join(str(a) for a in aka))
    if not lines:
        return ""
    body = "\n>\n".join(f"> {l}" for l in lines)
    return f"> [!abstract] At a glance\n>\n{body}\n\n"


def link_out(body, rel_dir, source):
    """Links to anything the wiki leaves out go to the file on GitHub instead."""
    def fix(m):
        target = m.group(1)
        path, _, anchor = target.partition("#")
        if path.startswith("/"):
            resolved = os.path.normpath(path.lstrip("/"))
        else:
            resolved = os.path.normpath(os.path.join(rel_dir, path))
        resolved = resolved.replace(os.sep, "/")
        if resolved.startswith("..") or source.published(resolved):
            return m.group(0)
        kind = "tree" if path.endswith("/") or "." not in os.path.basename(resolved) else "blob"
        quoted = "/".join(seg.replace(" ", "%20") for seg in resolved.split("/"))
        url = f"{source.repo_url}/{kind}/main/{quoted}" + (f"#{anchor}" if anchor else "")
        return f"]({url})"
    return MD_LINK.sub(fix, body)


def sticky_notes(body):
    """[[…]] outside code becomes a visible note, so Quartz can't turn it into a link."""
    out, in_fence = [], False
    for line in body.split("\n"):
        if FENCE.match(line):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence or "[[" not in line:
            out.append(line)
            continue
        pieces, last = [], 0
        for m in CODE_SPAN.finditer(line):
            pieces.append(_sticky(line[last:m.start()]))
            pieces.append(m.group(0))
            last = m.end()
        pieces.append(_sticky(line[last:]))
        out.append("".join(pieces))
    return "\n".join(out)


def _sticky(text):
    # The first bracket sits in its own <span>, so no text run ever holds "[[" for
    # Quartz's wiki-link finder to match; the reader still sees [[…]] as written.
    return STICKY.sub(
        lambda m: f'<span class="sticky-note"><span>[</span>[{m.group(1)}]]</span>', text
    )


def convert(text, rel_dir=".", source=None):
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
    if source is not None:
        body = link_out(body, rel_dir, source)
    body = README_LINK.sub(lambda m: f"{m.group(1)}index.md{m.group(2) or ''})", body)
    body = sticky_notes(body)
    body = glance_box(meta) + body

    header = raw_meta if raw_meta is not None else ""
    if title and "title" not in meta:
        header = f"title: {json.dumps(str(title), ensure_ascii=False)}\n" + header
    # The page's search/link-preview description is its `what`, not the glance box text.
    if meta.get("what") and "description" not in meta:
        header = f"description: {json.dumps(str(meta['what']), ensure_ascii=False)}\n" + header
    if header.strip():
        return f"---\n{header.rstrip()}\n---\n\n{body}"
    return body


def write_source(source, dst):
    start = os.path.join(source.root, source.subdir) if source.subdir else source.root
    count = 0
    for root, dirs, files in os.walk(start):
        dirs[:] = sorted(d for d in dirs if d not in source.skip_dirs)
        repo_rel = os.path.relpath(root, source.root).replace(os.sep, "/")
        repo_rel = "" if repo_rel == "." else repo_rel
        site_rel = os.path.relpath(root, start).replace(os.sep, "/")
        site_rel = "" if site_rel == "." else site_rel
        out_dir = os.path.normpath(os.path.join(dst, source.site_dir, site_rel))
        for name in sorted(files):
            repo_path = f"{repo_rel}/{name}" if repo_rel else name
            if not name.endswith(".md") or not source.published(repo_path):
                continue
            out_name = "index.md" if name == "README.md" else name
            os.makedirs(out_dir, exist_ok=True)
            with open(os.path.join(root, name), encoding="utf-8") as f:
                text = f.read()
            with open(os.path.join(out_dir, out_name), "w", encoding="utf-8") as f:
                f.write(convert(text, repo_rel or ".", source))
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("hub", help="VTM-V5 checkout")
    parser.add_argument("dst", help="Quartz content folder (replaced)")
    parser.add_argument("--wod", help="WoD-Archive checkout (adds the Australia WoD section)")
    args = parser.parse_args()

    if os.path.exists(args.dst):
        shutil.rmtree(args.dst)
    if args.wod and os.path.exists(os.path.join(args.hub, "australia")):
        parser.error("VTM-V5 now has an australia/ folder, which would collide with the Australia WoD section")
    for source in sources(args.hub, args.wod):
        count = write_source(source, args.dst)
        print(f"prepare.py: {count} pages from {source.repo_url.rsplit('/', 1)[-1]} written to {os.path.join(args.dst, source.site_dir)}")


if __name__ == "__main__":
    main()
