import { QuartzConfig } from "./quartz/cfg"
import * as Plugin from "./quartz/plugins"

// Fav's VTM wiki. Built from the private VTM-V5 repo by .github/workflows/build.yml.
// The site is unlisted: no sitemap, no RSS, robots.txt says keep out, and every page
// carries a noindex tag (added after the build).
const config: QuartzConfig = {
  configuration: {
    pageTitle: "Fav's VTM Wiki",
    pageTitleSuffix: " · Fav's VTM Wiki",
    enableSPA: true,
    enablePopovers: true,
    analytics: null,
    locale: "en-GB",
    baseUrl: "unfaventia.github.io/Fav-VTM-Wiki",
    ignorePatterns: ["private", ".obsidian"],
    defaultDateType: "modified",
    theme: {
      fontOrigin: "googleFonts",
      cdnCaching: true,
      // Art deco × retro SchreckNet (Fav, 2026-10-31). Limelight is the deco marquee
      // (the wordmark here; page titles load it in custom.scss), Jost the period
      // geometric sans for headings and the sidebar, Literata the long-reading body, and
      // VT323 the terminal: the switch's readout, the search prompt and code.
      typography: {
        title: "Limelight",
        header: { name: "Jost", weights: [400, 500, 600] },
        body: "Literata",
        code: { name: "VT323", weights: [400] },
      },
      // The base is VTM V5's: blood-red phosphor on onyx and brass. custom.scss swaps
      // the accent to green for Australia WoD (green and gold).
      colors: {
        lightMode: {
          light: "#f2ede1",
          lightgray: "#d4c9b1",
          gray: "#665c4b",
          darkgray: "#1d1913",
          dark: "#0f0d0a",
          secondary: "#9e1b2c",
          tertiary: "#835f1c",
          highlight: "rgba(158, 27, 44, 0.07)",
          textHighlight: "#d2ac6255",
        },
        darkMode: {
          light: "#110f0c",
          lightgray: "#3b342a",
          gray: "#958a76",
          darkgray: "#ece3cf",
          dark: "#f6efdf",
          secondary: "#f2585c",
          tertiary: "#d2ac62",
          highlight: "rgba(242, 88, 92, 0.1)",
          textHighlight: "#d2ac6244",
        },
      },
    },
  },
  plugins: {
    transformers: [
      Plugin.FrontMatter(),
      Plugin.CreatedModifiedDate({ priority: ["frontmatter", "filesystem"] }),
      Plugin.SyntaxHighlighting({
        theme: { light: "github-light", dark: "github-dark" },
        keepBackground: false,
      }),
      Plugin.ObsidianFlavoredMarkdown({ enableInHtmlEmbed: false }),
      Plugin.GitHubFlavoredMarkdown(),
      Plugin.TableOfContents(),
      // The hub links files by relative path (../disciplines/...), so resolve them that way.
      Plugin.CrawlLinks({ markdownLinkResolution: "relative" }),
      Plugin.Description(),
    ],
    filters: [Plugin.RemoveDrafts()],
    emitters: [
      Plugin.AliasRedirects(),
      Plugin.ComponentResources(),
      Plugin.ContentPage(),
      Plugin.FolderPage(),
      Plugin.TagPage(),
      Plugin.ContentIndex({ enableSiteMap: false, enableRSS: false }),
      Plugin.Assets(),
      Plugin.Static(),
      Plugin.Favicon(),
      Plugin.NotFoundPage(),
    ],
  },
}

export default config
