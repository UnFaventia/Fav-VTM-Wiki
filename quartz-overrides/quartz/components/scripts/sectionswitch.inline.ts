// The section switch's behaviour (see SectionSwitch.tsx). Runs on every page change.
const WOD_ROOT = "australia"
const LAST = (section: string) => `fav-wiki-last-${section}`
const SEARCH_BOTH = "fav-wiki-search-both"

type Section = "v5" | "wod"
const NAMES: Record<Section, string> = { v5: "VTM V5", wod: "Australia WoD" }
const EXPLORER_TITLES: Record<Section, string> = { v5: "The Hub", wod: "The Board" }

function sectionOf(slug: string): Section {
  return slug === WOD_ROOT || slug.startsWith(WOD_ROOT + "/") ? "wod" : "v5"
}

function currentSection(): Section {
  return (document.documentElement.dataset.section as Section) || "v5"
}

function store(key: string, value: string | null) {
  try {
    if (value === null) localStorage.removeItem(key)
    else localStorage.setItem(key, value)
  } catch {
    // private browsing: the switch still works, it just won't remember
  }
}

function read(key: string): string | null {
  try {
    return localStorage.getItem(key)
  } catch {
    return null
  }
}

// The search (patched by scripts/patch_quartz.py) asks this which results to keep.
;(window as any).favWikiInScope = (slug: string) =>
  read(SEARCH_BOTH) === "1" || sectionOf(slug) === currentSection()

function setupScopeChip(section: Section) {
  const other: Section = section === "wod" ? "v5" : "wod"
  for (const space of document.querySelectorAll(".search .search-space")) {
    const bar = space.querySelector(".search-bar") as HTMLInputElement | null
    if (!bar) continue
    let chip = space.querySelector(".search-scope") as HTMLButtonElement | null
    if (!chip) {
      chip = document.createElement("button")
      chip.type = "button"
      chip.className = "search-scope"
      bar.insertAdjacentElement("afterend", chip)
    }
    const both = read(SEARCH_BOTH) === "1"
    chip.setAttribute("aria-pressed", both ? "true" : "false")
    chip.textContent = `Also search ${NAMES[other]}`
    bar.placeholder = both ? "Search both sections" : `Search ${NAMES[section]}`
    const toggle = () => {
      const on = read(SEARCH_BOTH) !== "1"
      store(SEARCH_BOTH, on ? "1" : null)
      chip!.setAttribute("aria-pressed", on ? "true" : "false")
      bar.placeholder = on ? "Search both sections" : `Search ${NAMES[section]}`
      bar.dispatchEvent(new Event("input"))
      bar.focus()
    }
    chip.addEventListener("click", toggle)
    window.addCleanup(() => chip!.removeEventListener("click", toggle))
  }
}

let lastSection: Section | null = null

document.addEventListener("nav", (e: CustomEventMap["nav"]) => {
  const section = sectionOf(e.detail.url)
  document.documentElement.dataset.section = section

  // The screen re-lights when you change section (and only then).
  if (lastSection !== null && lastSection !== section) {
    for (const screen of document.querySelectorAll(".section-switch .switch-readout")) {
      screen.classList.add("relit")
      screen.addEventListener("animationend", () => screen.classList.remove("relit"), {
        once: true,
      })
    }
  }
  lastSection = section

  // Remember where we are, so flipping back lands here instead of on the homepage.
  store(LAST(section), window.location.pathname + window.location.hash)
  const other: Section = section === "wod" ? "v5" : "wod"
  const saved = read(LAST(other))
  for (const link of document.querySelectorAll(`.section-switch a[data-section="${other}"]`)) {
    if (saved) link.setAttribute("href", saved)
  }

  for (const title of document.querySelectorAll(".explorer .title-button h2")) {
    title.textContent = EXPLORER_TITLES[section]
  }

  setupScopeChip(section)
})
