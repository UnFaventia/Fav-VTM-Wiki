# Fav-VTM-Wiki

The build recipe for Fav's VTM wiki: <https://unfaventia.github.io/Fav-VTM-Wiki/>

The content lives in the private [VTM-V5](https://github.com/UnFaventia/VTM-V5) hub. This repo holds only the instructions for turning it into a website, so no book text is ever stored here. The decision behind it is D32 in the hub's `DESIGN.md`.

## How it works

1. Something changes in VTM-V5 and it pings this repo (or the nightly run fires, or you press **Run workflow** on the [Actions tab](https://github.com/UnFaventia/Fav-VTM-Wiki/actions/workflows/build.yml)).
2. [`build.yml`](.github/workflows/build.yml) checks out VTM-V5 using the `WIKI_TOKEN` secret, plus a pinned copy of [Quartz](https://quartz.jzhao.xyz) (the program that builds the site).
3. [`scripts/prepare.py`](scripts/prepare.py) turns the hub into wiki pages: each `README.md` becomes its folder's page, every page gets its title and an "At a glance" box built from its frontmatter, and links into the machinery folders (`tools/`, `CLAUDE.md`) go to GitHub instead.
4. Quartz builds the site, every page gets a "don't index me" tag, and the result goes straight to GitHub Pages.

The site is unlisted, not locked: search engines are told to stay out, but anyone with the link can read it.

## What's here

| Path | What it is |
| --- | --- |
| `.github/workflows/build.yml` | The build and publish run |
| `scripts/prepare.py` | Hub → wiki page converter |
| `quartz-overrides/` | Files copied over Quartz before the build: site config (title, colours, fonts), page layout, extra styling, and the icon and link-preview image |
| `scripts/make_icons.py` | Draws the blood-drop icon and the link-preview image (run once; the PNGs are committed) |
