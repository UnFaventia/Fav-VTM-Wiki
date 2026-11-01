import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"
import SectionSwitch from "./quartz/components/SectionSwitch"

// The sidebar shows one section at a time (D35). Quartz turns these two functions into
// text and runs them in the browser on every page change, so they can't use anything
// from this file: each works out the section from the page's slug on its own.
//  * filter: in VTM V5, hide the Australia WoD folder (and Quartz's tag pages);
//  * map: in Australia WoD, make the australia/ folder the top of the tree.
const explorerFilter = (node: any) => {
  if (node.slugSegment === "tags") return false
  const slug = document.body.dataset.slug || ""
  const wod = slug === "australia" || slug.startsWith("australia/")
  return wod || node.slug !== "australia/index"
}
const explorerMap = (node: any) => {
  if (node.slugSegment !== undefined) return
  const slug = document.body.dataset.slug || ""
  if (slug === "australia" || slug.startsWith("australia/")) {
    const board = node.children.find((c: any) => c.slug === "australia/index")
    if (board) node.children = board.children
  }
}

const explorer = Component.Explorer({
  title: "The Hub", // the switch's script renames it "The Board" in Australia WoD
  folderDefaultState: "collapsed",
  filterFn: explorerFilter,
  mapFn: explorerMap,
})

export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  header: [SectionSwitch()],
  afterBody: [],
  footer: Component.Footer({
    links: {
      "VTM-V5 on GitHub": "https://github.com/UnFaventia/VTM-V5",
      "WoD-Archive on GitHub": "https://github.com/UnFaventia/WoD-Archive",
      "Rebuild the wiki": "https://github.com/UnFaventia/Fav-VTM-Wiki/actions/workflows/build.yml",
    },
  }),
}

// No breadcrumbs on the two section homepages: there is nowhere above them to go.
const breadcrumbs = Component.ConditionalRender({
  component: Component.Breadcrumbs(),
  condition: (page) => page.fileData.slug !== "index" && page.fileData.slug !== "australia/index",
})

export const defaultContentPageLayout: PageLayout = {
  beforeBody: [breadcrumbs, Component.ArticleTitle()],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        { Component: Component.Search(), grow: true },
        { Component: Component.Darkmode() },
        { Component: Component.ReaderMode() },
      ],
    }),
    explorer,
  ],
  right: [
    Component.Graph(),
    Component.DesktopOnly(Component.TableOfContents()),
    Component.Backlinks(),
  ],
}

export const defaultListPageLayout: PageLayout = {
  beforeBody: [breadcrumbs, Component.ArticleTitle()],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        { Component: Component.Search(), grow: true },
        { Component: Component.Darkmode() },
      ],
    }),
    explorer,
  ],
  right: [],
}
