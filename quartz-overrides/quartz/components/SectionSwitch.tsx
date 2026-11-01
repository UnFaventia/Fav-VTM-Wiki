// The switch between the wiki's two sections (D35): "VTM V5", the hub at the site root,
// and "Australia WoD", WoD-Archive's australia/ folder at australia/.
//
// Server-side it renders two links, so it works with scripts off. The script
// (scripts/sectionswitch.inline.ts) then makes it a switch: flipping returns you to the
// last page you read in the other section, and the sidebar, the search and the accent
// colour follow whichever section you are in.
import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { FullSlug, resolveRelative } from "../util/path"
import { classNames } from "../util/lang"
import style from "./styles/sectionswitch.scss"
// @ts-ignore
import script from "./scripts/sectionswitch.inline"

export const WOD_ROOT = "australia"

export function sectionOf(slug: string): "v5" | "wod" {
  return slug === WOD_ROOT || slug.startsWith(WOD_ROOT + "/") ? "wod" : "v5"
}

// Runs in <head> before the page paints, so the accent colour never flashes the wrong
// section. The pathname test is rough; the script corrects it from the page's slug.
const beforeDOMLoaded = `
document.documentElement.dataset.section =
  /\\/${WOD_ROOT}(\\/|$)/.test(window.location.pathname) ? "wod" : "v5"
`

export default (() => {
  const SectionSwitch: QuartzComponent = ({
    fileData,
    allFiles,
    displayClass,
  }: QuartzComponentProps) => {
    const slug = fileData.slug as FullSlug
    const here = sectionOf(slug)
    const pages = { v5: 0, wod: 0 }
    for (const f of allFiles) {
      if (f.slug && !f.slug.startsWith("tags/")) pages[sectionOf(f.slug)]++
    }
    // The 404 page has no files to count; it gets the modem's hang-up line instead.
    const lost = slug === "404"
    const node = lost ? "NO CARRIER" : here === "wod" ? "australia.wod" : "vtm.v5"
    return (
      <nav class={classNames(displayClass, "section-switch")} aria-label="Wiki section">
        <p class="switch-readout" aria-hidden="true">
          <span class="readout-host">schrecknet://</span>
          <span class="readout-node">{node}</span>
          {!lost && (
            <span class="readout-count">
              {" "}
              [{pages[here]} pages]
            </span>
          )}
        </p>
        <div class="switch-plate">
          <a
            class="switch-seg"
            data-section="v5"
            href={resolveRelative(slug, "index" as FullSlug)}
            aria-current={here === "v5" ? "true" : undefined}
          >
            <span class="switch-lamp" aria-hidden="true"></span>
            <span class="switch-label">VTM V5</span>
          </a>
          <a
            class="switch-seg"
            data-section="wod"
            href={resolveRelative(slug, `${WOD_ROOT}/index` as FullSlug)}
            aria-current={here === "wod" ? "true" : undefined}
          >
            <span class="switch-lamp" aria-hidden="true"></span>
            <span class="switch-label">Australia WoD</span>
          </a>
        </div>
      </nav>
    )
  }

  SectionSwitch.css = style
  SectionSwitch.beforeDOMLoaded = beforeDOMLoaded
  SectionSwitch.afterDOMLoaded = script
  return SectionSwitch
}) satisfies QuartzComponentConstructor
