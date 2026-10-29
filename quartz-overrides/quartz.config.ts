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
      typography: {
        header: "Cinzel",
        body: "Source Sans Pro",
        code: "IBM Plex Mono",
      },
      colors: {
        lightMode: {
          light: "#faf7f5",
          lightgray: "#e6dfdc",
          gray: "#b0a4a2",
          darkgray: "#3f3838",
          dark: "#231d1d",
          secondary: "#8b1e2d",
          tertiary: "#b4656f",
          highlight: "rgba(139, 30, 45, 0.08)",
          textHighlight: "#f5d0d688",
        },
        darkMode: {
          light: "#141113",
          lightgray: "#36292d",
          gray: "#6e5f63",
          darkgray: "#ddd3d4",
          dark: "#f2eaea",
          secondary: "#e0566a",
          tertiary: "#c9a24a",
          highlight: "rgba(224, 86, 106, 0.12)",
          textHighlight: "#8b1e2d88",
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
