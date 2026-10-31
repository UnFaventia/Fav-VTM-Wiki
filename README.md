# Fav-VTM-Wiki

The build recipe for Fav's wiki: <https://unfaventia.github.io/Fav-VTM-Wiki/>

The wiki has two sections, with a switch at the top of every page to flip between them (D35 in the hub's `DESIGN.md`):

- **VTM V5**: the private [VTM-V5](https://github.com/UnFaventia/VTM-V5) hub, at the site root.
- **Australia WoD**: the `australia/` folder of the private [WoD-Archive](https://github.com/UnFaventia/WoD-Archive), at `australia/` on the site.

This repo holds only the instructions for turning those two repos into a website, so no book text is ever stored here. The decision behind it is D32 in the hub's `DESIGN.md`.

## How it works

1. Something changes in VTM-V5, or in WoD-Archive's `australia/` folder, and that repo pings this one (or the nightly run fires, or you press **Run workflow** on the [Actions tab](https://github.com/UnFaventia/Fav-VTM-Wiki/actions/workflows/build.yml)). Each content repo sends its ping with its own `WIKI_TOKEN` secret; without one, it skips quietly and the nightly run catches up.
2. [`build.yml`](.github/workflows/build.yml) checks out VTM-V5 and WoD-Archive's `australia/` folder using the `WIKI_TOKEN` secret, plus a pinned copy of [Quartz](https://quartz.jzhao.xyz) (the program that builds the site).
3. [`scripts/patch_quartz.py`](scripts/patch_quartz.py) makes four small, exact edits to Quartz itself: search keeps to the section you're in, and opening a page no longer scrolls the switch off screen. If a Quartz upgrade changes the lines it edits, the build stops and says which patch to redo.
4. [`scripts/prepare.py`](scripts/prepare.py) turns both repos into wiki pages: each `README.md` becomes its folder's page, every page gets its title and an "At a glance" box built from its frontmatter, Fav's `[[sticky notes]]` show as notes rather than broken links, and links into anything the wiki leaves out (the machinery, the PDFs, the rest of WoD-Archive) go to GitHub instead.
5. Quartz builds the site, every page gets a "don't index me" tag, and the result goes straight to GitHub Pages.

The site is unlisted, not locked: search engines are told to stay out, but anyone with the link can read it.

### What the Australia section leaves out

`NOTES.md` (the build record, kept off by D35), `HANDOFF.md` and `SURVEY.md` (instructions and working notes for Claude sessions, like the hub's `CLAUDE.md`) and the extract build specs. The list is `sources()` in `prepare.py`.

## The look

Art deco × retro SchreckNet (Fav, 2026-10-31). The deco is the frame: brass on onyx (or ivory, in daylight mode), Limelight page titles with a sunburst fan under them, double rules, corner brackets. SchreckNet is the machine wired into it: dark screens with phosphor text for the switch, the search and code, in VT323. Body text is Literata, large, for long reading on a phone; headings and the sidebar are Jost.

**The switch.** A brass plate at the top of every page: a SchreckNet readout of where you are, and two lamps, red for VTM V5 and green for Australia WoD (green and gold, with the brass). The lit lamp is the section you're in.

- Tap the dark lamp to flip: it takes you back to the last page you read in that section (its homepage the first time).
- Tap the lit lamp to go to the current section's homepage.
- The sidebar shows only the current section ("The Hub" or "The Board"), the accent colour follows it, and search keeps to it. **Also search …** in the search box widens it to both; it stays on until you switch it off.

## What's here

| Path | What it is |
| --- | --- |
| `.github/workflows/build.yml` | The build and publish run |
| `scripts/prepare.py` | Repos → wiki pages converter |
| `scripts/patch_quartz.py` | The small edits to Quartz's own search and sidebar scripts |
| `quartz-overrides/` | Files copied over Quartz before the build: site config (title, colours, fonts), page layout, styling, the section switch (`quartz/components/SectionSwitch.tsx` and its script and styles), and the icon and link-preview image |
| `scripts/make_icons.py` | Draws the icon and the link-preview image (run once; the PNGs are committed) |

## Building it on your own machine

Clone Quartz at the version `build.yml` pins, then from this repo:

```sh
cp -r quartz-overrides/. ../quartz/
python3 scripts/patch_quartz.py ../quartz
python3 scripts/prepare.py ../VTM-V5 ../quartz/content --wod ../WoD-Archive
cd ../quartz && npx quartz build --serve
```

`patch_quartz.py` edits a fresh Quartz once; run it again on the same copy and it stops, because the lines it looks for have already changed.
