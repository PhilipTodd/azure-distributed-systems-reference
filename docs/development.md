---
layout: page
title: Development
eyebrow: Source
description: Branching strategy, project management and the project folder structure.
permalink: /development/
---

## Live demo

<div class="btn-row">
  <a class="btn btn--primary" href="{{ site.project.demo.url }}" target="_blank" rel="noopener noreferrer">{{ site.project.demo.label }}</a>
</div>


{% if site.project.credentials.enabled %}
{% include credentials.html %}
{% endif %}


## Branching
This repository uses **trunk-based** development. `main` is the trunk and is always expected to be releasable.

Work lands through short-lived branches and pull requests into `main`. The CI pipeline runs on those pull requests and on every push to `main`. Infrastructure, application, and UI deploys are started separately when the dev environment needs a new drop. 



## Project management

This project is managed using an Agile project management approach. The chosen method is Kanban, tool is Github projects. 

<div class="btn-row">
  <a class="btn btn--ghost" href="{{ site.project.github.project }}" target="_blank" rel="noopener noreferrer">Github project</a>
</div>


## Project folder structure

The folder structure I have chosen mirrors other projects I have worked on in the past. I am attempting to organise different aspects of the project in a logical fashion while including all items to be shared and tracked in the git repository. A .gitignore file prevents artifacts from being tracked and uploaded into git.


```
ParameterPilot/
│
├── .github/                                  # GitHub configuration and AI-assisted delivery
│   ├── agents/                               # Specialist AI agent definitions
│   │   ├── architect.agent.md
│   │   ├── backend.agent.md
│   │   ├── frontend.agent.md
│   │   ├── infrastructure.agent.md
│   │   ├── testing.agent.md
│   │   ├── security.agent.md
│   │   └── documentation.agent.md
│   │
│   ├── workflows/
│   │   ├── security.yml                      # CodeQL/security scanning
│   │   └── docs.yml                          # Documentation site deployment
│   │
│   ├── CODEOWNERS
│   ├── dependabot.yml
│   └── pull_request_template.md
│
├── docs/                                     # Project documentation
│   ├── index.md
│   │
│   ├── architecture/
│   │   ├── overview.md
│   │   │
│   │   ├── decisions/                        # Architecture Decision Records
│   │   │   ├── 001-microservices.md
│   │   │   ├── 002-clean-architecture.md
│   │   │   ├── 003-data-ownership.md
│   │   │   └── 004-asynchronous-messaging.md
│   │   │
│   │   └── structurizr/                      # C4 architecture-as-code
│   │       ├── workspace.dsl
│   │       ├── model/
│   │       │   ├── people.dsl
│   │       │   ├── systems.dsl
│   │       │   ├── containers.dsl
│   │       │   └── components.dsl
│   │       └── views/
│   │           └── views.dsl
│   │
│   ├── requirements/
│   │   ├── functional-requirements.md
│   │   ├── non-functional-requirements.md
│   │   └── use-cases.md
│   │
│   ├── development/
│   │   ├── getting-started.md
│   │   ├── local-development.md
│   │   └── testing.md
│   │
│   └── operations/
│       ├── deployment.md
│       ├── observability.md
│       └── troubleshooting.md
│
├── src/                                      # Production application source
│   │
│   ├── services/                             # Independently deployable microservices
│   │   │
│   │   ├── Tracking/                         # Tracking Service boundary
│   │   │   │
│   │   │   ├── ParameterPilot.Tracking.Api/
│   │   │   │   ├── Controllers/
│   │   │   │   ├── Middleware/
│   │   │   │   ├── Program.cs
│   │   │   │   └── ParameterPilot.Tracking.Api.csproj
│   │   │   │
│   │   │   ├── ParameterPilot.Tracking.Application/
│   │   │   │   ├── Commands/
│   │   │   │   ├── Queries/
│   │   │   │   ├── Interfaces/
│   │   │   │   ├── Behaviours/
│   │   │   │   └── ParameterPilot.Tracking.Application.csproj
│   │   │   │
│   │   │   ├── ParameterPilot.Tracking.Domain/
│   │   │   │   ├── Entities/
│   │   │   │   ├── ValueObjects/
│   │   │   │   ├── Events/
│   │   │   │   ├── Exceptions/
│   │   │   │   └── ParameterPilot.Tracking.Domain.csproj
│   │   │   │
│   │   │   └── ParameterPilot.Tracking.Infrastructure/
│   │   │       ├── Persistence/
│   │   │       ├── Messaging/
│   │   │       ├── Repositories/
│   │   │       └── ParameterPilot.Tracking.Infrastructure.csproj
│   │   │
│   │   ├── Aquarium/                         # Aquarium Service boundary
│   │   │   │
│   │   │   ├── ParameterPilot.Aquarium.Api/
│   │   │   │   ├── Controllers/
│   │   │   │   ├── Middleware/
│   │   │   │   ├── Program.cs
│   │   │   │   └── ParameterPilot.Aquarium.Api.csproj
│   │   │   │
│   │   │   ├── ParameterPilot.Aquarium.Application/
│   │   │   │   ├── Commands/
│   │   │   │   ├── Queries/
│   │   │   │   ├── Interfaces/
│   │   │   │   ├── Behaviours/
│   │   │   │   └── ParameterPilot.Aquarium.Application.csproj
│   │   │   │
│   │   │   ├── ParameterPilot.Aquarium.Domain/
│   │   │   │   ├── Entities/
│   │   │   │   ├── ValueObjects/
│   │   │   │   ├── Events/
│   │   │   │   ├── Exceptions/
│   │   │   │   └── ParameterPilot.Aquarium.Domain.csproj
│   │   │   │
│   │   │   └── ParameterPilot.Aquarium.Infrastructure/
│   │   │       ├── Persistence/
│   │   │       ├── Messaging/
│   │   │       ├── Repositories/
│   │   │       └── ParameterPilot.Aquarium.Infrastructure.csproj
│   │   │
│   │   └── Advisor/                     # Advisor Service boundary
│   │       │
│   │       ├── ParameterPilot.Advisor.Api/
│   │       │   ├── Controllers/
│   │       │   ├── Middleware/
│   │       │   ├── Program.cs
│   │       │   └── ParameterPilot.Advisor.Api.csproj
│   │       │
│   │       ├── ParameterPilot.Advisor.Application/
│   │       │   ├── Commands/
│   │       │   ├── Queries/
│   │       │   ├── Interfaces/
│   │       │   ├── Behaviours/
│   │       │   └── ParameterPilot.Advisor.Application.csproj
│   │       │
│   │       ├── ParameterPilot.Advisor.Domain/
│   │       │   ├── Entities/
│   │       │   ├── ValueObjects/
│   │       │   ├── Events/
│   │       │   ├── Exceptions/
│   │       │   └── ParameterPilot.Advisor.Domain.csproj
│   │       │
│   │       └── ParameterPilot.Advisor.Infrastructure/
│   │           ├── Persistence/
│   │           ├── Messaging/
│   │           ├── Repositories/
│   │           └── ParameterPilot.Advisor.Infrastructure.csproj
│   │
│   ├── gateway/                              # External API boundary / BFF
│   │   └── ParameterPilot.Gateway/
│   │       ├── Configuration/
│   │       ├── Middleware/
│   │       ├── Program.cs
│   │       └── ParameterPilot.Gateway.csproj
│   │
│   └── web/                                  # Angular SPA
│       └── ParameterPilot.Web/
│           ├── src/
│           │   ├── app/
│           │   │   ├── core/
│           │   │   ├── features/
│           │   │   ├── shared/
│           │   │   └── app.routes.ts
│           │   ├── environments/
│           │   └── main.ts
│           ├── angular.json
│           └── package.json
│
├── tests/                                    # Automated test projects
│   │
│   ├── Tracking/
│   │   ├── ParameterPilot.Tracking.Domain.Tests/
│   │   ├── ParameterPilot.Tracking.Application.Tests/
│   │   ├── ParameterPilot.Tracking.Infrastructure.Tests/
│   │   └── ParameterPilot.Tracking.Api.Tests/
│   │
│   ├── Aquarium/
│   │   ├── ParameterPilot.Aquarium.Domain.Tests/
│   │   ├── ParameterPilot.Aquarium.Application.Tests/
│   │   ├── ParameterPilot.Aquarium.Infrastructure.Tests/
│   │   └── ParameterPilot.Aquarium.Api.Tests/
│   │
│   ├── Advisor/
│   │   ├── ParameterPilot.Advisor.Domain.Tests/
│   │   ├── ParameterPilot.Advisor.Application.Tests/
│   │   ├── ParameterPilot.Advisor.Infrastructure.Tests/
│   │   └── ParameterPilot.Advisor.Api.Tests/
│   │
│   ├── ParameterPilot.Architecture.Tests/    # Cross-solution architecture rules
│   └── ParameterPilot.EndToEnd.Tests/        # System-level integration/E2E tests
│
├── contracts/                                # Cross-service integration contracts
│   ├── events/
│   │   ├── ParameterRecorded.cs
│   │   ├── ParameterThresholdExceeded.cs
│   │   └── AdviceCompleted.cs
│   └── schemas/
│       └── ...
│
├── infra/                                    # Azure Infrastructure as Code
│   ├── main.bicep                            # Deployment orchestrator
│   │
│   ├── environments/
│   │   ├── dev.bicepparam
│   │   ├── test.bicepparam
│   │   └── prod.bicepparam
│   │
│   └── modules/
│       ├── appService.bicep
│       ├── applicationInsights.bicep
│       ├── cosmosDb.bicep
│       ├── keyVault.bicep
│       ├── logAnalytics.bicep
│       ├── serviceBus.bicep
│       ├── sql.bicep
│       └── storage.bicep
│
├── pipelines/                                # Azure DevOps pipelines
│   ├── templates/
│   │   ├── build-service.yml
│   │   ├── test-service.yml
│   │   ├── deploy-service.yml
│   │   ├── build-angular.yml
│   │   └── deploy-infrastructure.yml
│   │
│   ├── ci.yml
│   ├── deploy-infra.yml
│   ├── deploy-tracking.yml
│   ├── deploy-Aquarium.yml
│   ├── deploy-Advisor.yml
│   ├── deploy-gateway.yml
│   └── deploy-web.yml
│
├── scripts/
│   ├── setup-local.ps1
│   ├── build.ps1
│   └── seed-data.ps1
│
├── .editorconfig
├── .gitignore
├── AGENTS.md                                 # Repository-wide AI rules and boundaries
├── Directory.Build.props
├── Directory.Packages.props
├── ParameterPilot.slnx
├── README.md
├── SECURITY.md
└── LICENSE
```
