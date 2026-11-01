#!/usr/bin/env python3
"""Small, exact edits to Quartz's own files, applied after the overrides are copied in.

Usage: python3 scripts/patch_quartz.py <quartz checkout>

Overrides (quartz-overrides/) replace whole files; these patch a few lines instead, so the
rest of each file keeps up with whatever Quartz version build.yml pins. Every patch names
the exact text it expects and how often: if a Quartz upgrade changes that text, the build
stops here with a message saying which patch to redo, rather than quietly shipping a wiki
whose search ignores the section switch.
"""
import os
import sys

SEARCH = "quartz/components/scripts/search.inline.ts"
EXPLORER = "quartz/components/scripts/explorer.inline.ts"

PATCHES = [
    # The search keeps to the section you are in (the switch's "Also search…" chip widens
    # it). Ask flexsearch for plenty of matches, keep the in-section ones, show the top 8.
    (
        SEARCH,
        "limit: numSearchResults,",
        "limit: numSearchResults * 25,",
        2,
    ),
    (
        SEARCH,
        "searchResult.result = searchResult.result.slice(0, numSearchResults)",
        "searchResult.result = searchResult.result.slice(0, numSearchResults * 25)",
        1,
    ),
    (
        SEARCH,
        "const finalResults = [...allIds].map((id) => formatForDisplay(currentSearchTerm, id))",
        "const inScope = (window as any).favWikiInScope ?? (() => true)\n"
        "    const finalResults = [...allIds]\n"
        "      .filter((id) => inScope(idDataMap[id]))\n"
        "      .slice(0, numSearchResults)\n"
        "      .map((id) => formatForDisplay(currentSearchTerm, id))",
        1,
    ),
    # Opening a page scrolls the sidebar to it; Quartz's version scrolled the whole page
    # too, so the section switch at the top was off screen. Scroll only if it's hidden.
    (
        EXPLORER,
        'activeElement.scrollIntoView({ behavior: "smooth" })',
        'activeElement.scrollIntoView({ behavior: "smooth", block: "nearest" })',
        1,
    ),
]


def main(root):
    for rel, old, new, count in PATCHES:
        path = os.path.join(root, rel)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        found = text.count(old)
        if found != count:
            sys.exit(
                f"patch_quartz.py: expected {count} of this in {rel}, found {found}; "
                f"Quartz has changed, so redo this patch:\n  {old}"
            )
        with open(path, "w", encoding="utf-8") as f:
            f.write(text.replace(old, new))
    print(f"patch_quartz.py: {len(PATCHES)} patches applied")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
