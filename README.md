[![CodeQL](https://github.com/PhilipTodd/azure-distributed-systems-reference/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/PhilipTodd/azure-distributed-systems-reference/actions/workflows/codeql.yml)

<p align="center">
  <img src="docs/assets/images/distributed%20systems-social-media-Horizontal.png" alt="Azure Distributed Systems Reference" width="50%">
</p>

<h1 align="center">Azure Distributed Systems Reference</h1>
<p align="center"><strong>Architecture-led engineering for an Azure-native SaaS application.</strong></p>
<p align="center">
  <a href="https://distributed-systems.ausdatatech.com.au/">📖 Explore the documentation</a> ·
  <a href="https://ausdatatech.com.au/">🌐 Connect with Philip Todd</a> ·
  <a href="LICENSE">⚖️ MIT License</a>
</p>

## 🧭 The project

A practical reference for designing and building distributed systems on Microsoft Azure. **Parameter Pilot**, an AI-assisted aquarium management platform, provides the real-world context for exploring service boundaries, event-driven integration, security, and infrastructure as code.

**Current stage: architecture and design.** The repository contains requirements, architecture decisions, Structurizr models, a Jekyll documentation site, initial Azure Bicep infrastructure, and a static coming-soon page. Application services and their automated test suites are yet to be implemented.

## 🛠️ Technologies

| In the repository today | Purpose |
| --- | --- |
| Azure Bicep · Azure Static Web Apps | Initial infrastructure definitions |
| Structurizr DSL · C4 | Architecture as code |
| Jekyll · GitHub Pages · Markdown | Public engineering documentation |
| HTML · CSS | Static coming-soon page |
| GitHub Actions · CodeQL | Configured security analysis workflow |

**Selected application stack:** .NET 10 / ASP.NET Core, C# 14, Angular 22 / TypeScript, Entity Framework Core 10, and the Azure Cosmos DB .NET SDK. These are documented design choices; application projects and exact dependency versions are still pending. See the [technology baseline](docs/engineering/technology-baseline.md).

The badge above reports the **CodeQL workflow status on `main`**; it does not establish application build or test coverage.

## 📖 Explore the engineering

Visit the **[project documentation](https://distributed-systems.ausdatatech.com.au/)** for architecture, design decisions, requirements, and the development roadmap.

## 👋 Contact

Built by **Philip Todd**. Visit **[AusDataTech](https://ausdatatech.com.au/)** to learn more about my work and get in touch.

## ⚖️ License

[MIT License](LICENSE) · Copyright © 2026 Philip Todd.
