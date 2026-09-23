# Documentation template

Jekyll documentation skeleton for three reference projects. Layout, colour, type, and navigation stay in this repository; each project site copies it and swaps `_config.yml` project settings, hero images, and short content.

Compatible with **local Jekyll** and **GitHub Pages** (no custom plugins).

## Run locally

Requires [Ruby](https://www.ruby-lang.org/) and [Bundler](https://bundler.io/).

```powershell
bundle install
bundle exec jekyll serve
```

Open [http://127.0.0.1:4000](http://127.0.0.1:4000).

If GitHub Pages will publish from a project site (`https://user.github.io/repo-name/`), set `baseurl: "/repo-name"` in `_config.yml` and serve with:

```powershell
bundle exec jekyll serve --baseurl "/repo-name"
```

## What to review first

1. Home - hero, pitch, Azure demo button, credentials, landscape/portrait image swap.
2. [Style guide](style-guide.md) - fonts, callouts, panels, tabs, buttons, tables, pipeline.
3. Inner pages - sidebar order matches the documentation contract (architecture through roadmap).

## Per-project fill-in

| Need | Where |
| --- | --- |
| Name, pitch, demo URL, credentials, GitHub links | `_config.yml` `project` |
| Hero images (1700 x 900 and 900 x 1700) | `assets/images/` + `project.images` |
| C4 diagrams from Structurizr | `assets/diagrams/` + `_data/c4.yml` |
| ADR log | `_data/adrs.yml` |
| Pipeline stages | `_data/pipeline.yml` |
| Azure inventory | `_data/azure-resources.yml` |
| Roadmap | `_data/roadmap.yml` |

Remove the Style guide nav entry in `_data/navigation.yml` when cloning for a real project.

## GitHub Pages

This site uses only GitHub Pages-safe plugins (`jekyll-seo-tag`, `jekyll-sitemap`) via the `github-pages` gem. Do not add custom Ruby plugins. Enable Pages from the repository root (or `/docs` if you later move the site there) using the GitHub Actions or "Deploy from a branch" Jekyll workflow.
