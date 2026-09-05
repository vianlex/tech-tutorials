<h1 align="center">
  <a href="https://docs.pgsty.com/">
    <img src="https://raw.githubusercontent.com/pgsty/docs/main/images/logo.svg" alt="Docs" width="420">
  </a>
</h1>

<p align="center">
  <strong>Open. Indexed. Navigable. Knowledge.</strong><br>
  A local-first Hugo theme for engineering documentation.
</p>

<p align="center">
  <a href="https://docs.pgsty.com/"><img alt="Website" src="https://img.shields.io/badge/website-docs.pgsty.com-17385c?style=flat-square"></a>
  <a href="https://github.com/pgsty/docs/releases/latest"><img alt="Release" src="https://img.shields.io/github/v/release/pgsty/docs?display_name=tag&amp;sort=semver&amp;style=flat-square"></a>
  <a href="https://github.com/pgsty/docs/actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/pgsty/docs/ci.yml?branch=main&amp;label=CI&amp;style=flat-square"></a>
  <a href="https://gohugo.io/"><img alt="Hugo Extended 0.160.1 or newer" src="https://img.shields.io/badge/Hugo_Extended-%E2%89%A50.160.1-ff4088?logo=hugo&amp;logoColor=white&amp;style=flat-square"></a>
  <a href="https://github.com/pgsty/docs/blob/main/LICENSE"><img alt="Apache 2.0" src="https://img.shields.io/github/license/pgsty/docs?label=license&amp;style=flat-square"></a>
</p>

<p align="center">
  <a href="https://docs.pgsty.com/docs/start/"><strong>Get started</strong></a> ·
  <a href="https://github.com/pgsty/docs-starter"><strong>Docs Starter</strong></a> ·
  <a href="https://docs.pgsty.com/docs/components/">Components</a> ·
  <a href="https://docs.pgsty.com/case/">Live cases</a> ·
  <a href="https://docs.pgsty.com/docs/design/">Design</a>
</p>

<a href="https://docs.pgsty.com/">
  <img src="https://raw.githubusercontent.com/pgsty/docs/main/images/screenshot.png" alt="Docs documentation landing page in dark mode">
</a>

Docs turns native Markdown into a complete knowledge-publishing site with one
Hugo Extended build. Its fonts, icons, search, diagrams, and feature runtimes
ship locally and load only where they are used. Consumer sites need no Node.js,
npm, PostCSS, bundler, or CDN.

The same content can serve people and tools: responsive HTML for readers,
print and RSS for publication, semantic Markdown for reuse, and optional
`llms.txt`, `llms-full.txt`, and `navigation.json` indexes for agents.

## Why Docs

- **One deterministic toolchain.** Resolve the Hugo Module once, then build and
  preview with one `hugo` binary.
- **Complete publishing surfaces.** Docs, Blog, Book, OpenAPI, releases,
  downloads, and data-driven landing pages share one navigation and visual
  system.
- **Native Markdown authoring.** Tables, fenced code, lists, and attributes
  become tabs, steps, cards, fields, galleries, diagrams, mathematics, charts,
  and API references without introducing MDX.
- **Local-first delivery.** Search, fonts, icons, syntax highlighting, and
  interactive runtimes are vendored; a normal build performs no remote asset
  fetch.
- **Multilingual by design.** Language-aware routing, translated-page peers,
  RTL support, alternate-site links, and localized search work across large
  documentation trees.
- **Progressive by default.** Server-rendered content remains useful without
  JavaScript; interaction, accessibility, responsive behavior, print, and
  machine-readable outputs are tested as separate contracts.

## Start a site

### Use Docs Starter

The recommended path is the public
[`pgsty/docs-starter`](https://github.com/pgsty/docs-starter) template. It is a
small production baseline with Docs, Blog, Book, English/Chinese/French
profiles, and GitHub Pages and Cloudflare Pages workflows—without this theme
repository's internal fixtures.

[**Use this template on GitHub**](https://github.com/new?template_name=docs-starter&template_owner=pgsty)
· [Live starter](https://pgsty.github.io/docs-starter/)
· [Setup guide](https://docs.pgsty.com/docs/start/)

The current starter expects Git, Go 1.27 or newer, and Hugo Extended 0.165.0
or newer; it does not require Node.js. To evaluate the neutral template locally:

```sh
git clone https://github.com/pgsty/docs-starter.git
cd docs-starter
hugo server
```

Open <http://localhost:1313/>. Replace the site identity, home-page data, and
sample content in that order; the starter already pins a tested Docs release
and includes a warning-strict production build.

### Add Docs to an existing Hugo site

Docs is a Hugo Module. A site that does not already use modules can initialize
one and resolve the latest release with:

```sh
hugo mod init github.com/example/docs
hugo mod get github.com/pgsty/docs@latest
```

Import the module in the site's root `hugo.yaml`:

```yaml
module:
  imports:
    - path: github.com/pgsty/docs

# Hugo does not merge a theme module's Goldmark settings into the site.
markup:
  goldmark:
    renderer:
      unsafe: true
    parser:
      wrapStandAloneImageWithinParagraph: false
      attribute:
        block: true
```

Those Goldmark settings enable Docs's native container shortcodes, block-image
attributes, steps, fields, captions, and numbered Book targets. Select the
HTML, RSS, Print, Markdown, LLMS, LLMSFULL, and NAVJSON outputs the site needs;
the [configuration reference](https://docs.pgsty.com/docs/customize/config/)
documents their defaults and scope.

For production, commit `go.mod` and `go.sum`, build with warnings promoted to
errors, and inspect representative routes:

```sh
hugo --cleanDestinationDir --gc --minify --environment production \
  --printPathWarnings --panicOnWarning
```

See [Get started](https://docs.pgsty.com/docs/start/) for repository structure,
language profiles, customization, and deployment. Existing Docsy sites should
also read the [upgrade and migration guide](https://docs.pgsty.com/docs/admin/upgrade/).

## What ships with the theme

| Area | Included capabilities |
| --- | --- |
| Reading shells | Docs, Blog, Book, Swagger/Redoc, releases, downloads, Print |
| Navigation | Sidebars, breadcrumbs, TOC rail, pager, version and language menus |
| Discovery | Local full-text search, command palette, taxonomies, backlinks |
| Authoring | Code, tabs, steps, cards, fields, images, galleries, callouts, includes |
| Technical content | Mermaid, PlantUML, Draw.io, Markmap, ECharts, KaTeX, Asciinema |
| Landing pages | 22 server-rendered sections with progressive enhancement |
| Outputs | HTML, RSS, Print, Markdown, LLMS, LLMSFULL, NAVJSON, Book manifest |
| Operations | SEO, analytics hooks, Giscus, feedback events, sharing, deployment-safe URLs |

Interactive features remain opt-in where they express site policy. The theme
provides the implementation; the consuming site decides which outputs,
analytics, comments, feedback, assistant links, and image behavior to enable.

## Live sites

Docs is exercised by fifteen real sites, from a two-page utility to large
documentation estates and multi-edition books. These are representative:

| Site | Shape | Case study |
| --- | --- | --- |
| [pigsty.io](https://pigsty.io/) / [pigsty.cc](https://pigsty.cc/) | Large English and Chinese documentation, blog, catalogue, and landing pages | [EN](https://docs.pgsty.com/case/pigsty-io/) · [ZH](https://docs.pgsty.com/case/pigsty-cc/) |
| [silo.pgsty.com](https://silo.pgsty.com/) | Large bilingual migration with manifest-generated navigation | [SILO](https://docs.pgsty.com/case/silo/) |
| [pgsty.com](https://pgsty.com/) | Compact bilingual corporate and landing-page site | [PGSTY](https://docs.pgsty.com/case/pgsty-com/) |
| [ddia.vonng.com](https://ddia.vonng.com/) | Multi-edition, multilingual Book with numbering and cross-references | [DDIA](https://docs.pgsty.com/case/ddia/) |
| [tpme.vonng.com](https://tpme.vonng.com/) | Focused bilingual Book publication | [TPME](https://docs.pgsty.com/case/tpme/) |
| [ext.pgsty.com](https://ext.pgsty.com/) | Data-driven PostgreSQL extension catalogue | [PGEXT](https://docs.pgsty.com/case/pgext-cloud/) |
| [exp.pgsty.com](https://exp.pgsty.com/) | Bilingual product docs with a structured metrics catalogue | [PG Exporter](https://docs.pgsty.com/case/pg-exporter/) |
| [caps.vonng.com](https://caps.vonng.com/) | Two-page bilingual project with an interactive configurator | [CapsLock](https://docs.pgsty.com/case/capslock/) |

[Browse all case studies](https://docs.pgsty.com/case/).

## Documentation

| Guide | Purpose |
| --- | --- |
| [Get started](https://docs.pgsty.com/docs/start/) | Install, understand the repository, and establish a working baseline |
| [Authoring](https://docs.pgsty.com/docs/write/) | Write Docs, Blog, Book, release, and OpenAPI content |
| [Components](https://docs.pgsty.com/docs/components/) | Source-first examples and parameter references |
| [Customization](https://docs.pgsty.com/docs/customize/) | Brand, navigation, layout, languages, search, outputs, and integrations |
| [Operations](https://docs.pgsty.com/docs/admin/) | Preview, deploy, upgrade, troubleshoot, analytics, and SEO |
| [Design](https://docs.pgsty.com/docs/design/) | Maintainer contracts, decisions, research, and active proposals |
| [Write Beautiful Docs](https://docs.pgsty.com/book/) | End-to-end tutorial in Docs's Book shell |

The public documentation and regression site lives in
[`pgsty/docs.pgsty.com`](https://github.com/pgsty/docs.pgsty.com). This theme
repository owns implementation, defaults, vendored assets, focused checkers,
and the narrow internal fixture under
[`tests/site/`](https://github.com/pgsty/docs/tree/main/tests/site/).

## Docs and Docsy

Docs began from Docsy's mature Hugo content model and remains Apache-2.0 with
explicit upstream attribution. It is now a separate theme rather than a Docsy
skin: Docs owns its Docs, Blog, Book, Swagger, and Landing shells; local search
and command palette; native-Markdown component model; responsive and
accessibility behavior; and reader, print, Markdown, and agent-facing outputs.

That difference is architectural as well as visual. Docs consumer sites do not
run Docsy's Node/PostCSS pipeline, and Docs changes navigation, configuration,
front matter, and extension contracts deliberately. Use the
[migration guide](https://docs.pgsty.com/docs/admin/upgrade/) instead of
assuming drop-in compatibility.

## Compatibility

| Dependency | Policy |
| --- | --- |
| Hugo | **Extended 0.160.1 or newer**; CI currently pins 0.165.0 |
| Go | 1.27 or newer for Hugo Module resolution; not needed when using an offline archive or submodule |
| Node.js | Not required to build or run an Docs site |
| Locales | Reviewed Docs interface text for English, Simplified Chinese, and Traditional Chinese; inherited Docsy locales retain English fallback for newer labels |

## Community and releases

[Releases](https://github.com/pgsty/docs/releases) ·
[Changelog](https://github.com/pgsty/docs/blob/main/CHANGELOG.md) ·
[Issues](https://github.com/pgsty/docs/issues) ·
[Discussions](https://github.com/pgsty/docs/discussions)

A local build, a committed change, a public tag, a consumer dependency update,
and a deployed site are separate release states. Pin a release tag for
production and verify the public routes after deployment.

## License

Docs is licensed under the
[Apache License 2.0](https://github.com/pgsty/docs/blob/main/LICENSE) and
derived from [Docsy](https://github.com/google/docsy). See
[NOTICE](https://github.com/pgsty/docs/blob/main/NOTICE) for upstream
attribution and
[VENDOR.json](https://github.com/pgsty/docs/blob/main/VENDOR.json) for bundled
third-party components.
