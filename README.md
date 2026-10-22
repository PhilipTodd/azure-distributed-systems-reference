# Azure Distributed Systems Reference

A production-grade reference implementation of a cloud-native, event-driven microservices architecture built on Microsoft Azure using .NET.

This project demonstrates how to design, build, secure, deploy, and operate distributed systems using modern DevSecOps practices and Azure-native services.

---

## 🎯 Purpose

This repository serves as:

- A senior-level Azure distributed systems reference
- A practical implementation of event-driven microservices
- A demonstration of modern DevSecOps and infrastructure-as-code practices
- A portfolio project showcasing hands-on cloud engineering capability

The goal is not to build a demo app, but to model how production systems should be structured and operated.

---





-----------------------------

# Parameter Pilot

**An Azure-native, AI-assisted aquarium management platform built using modern distributed systems architecture and agentic software engineering.**

Parameter Pilot is a cloud-based application designed to help aquarium owners record water parameters, monitor trends, manage maintenance activities, and receive AI-assisted recommendations based on their aquarium's history and configuration.

The project also serves as a practical reference implementation demonstrating how a modern SaaS application can be architected, developed, secured, deployed, and operated using Microsoft Azure, .NET, Angular, and AI-assisted development workflows.

> **Project status: Architecture & Design**
>
> Parameter Pilot is currently in the architecture and technical specification phase. The features and technologies described below represent the intended solution and may evolve as architectural decisions are reviewed and approved.

## Project Objectives

Parameter Pilot has two primary objectives.

### Product Objective

Build a useful aquarium management application that enables aquarium owners to make informed decisions about aquarium health and maintenance.

Planned capabilities include:

- **Aquarium Management:** Maintain aquarium profiles, equipment, livestock, and configuration.
- **Water Parameter Tracking:** Record and review measurements such as pH, ammonia, nitrite, nitrate, phosphate, alkalinity, calcium, and magnesium.
- **Trend Analysis:** Visualise historical measurements and identify changes over time.
- **Maintenance Management:** Record water changes, equipment maintenance, dosing, and other aquarium activities.
- **Activity Timeline:** Correlate parameter changes with maintenance events, equipment changes, and observations.
- **AI-Assisted Advice:** Generate contextual recommendations using aquarium history, configuration, and reference knowledge.
- **Dosing Calculators:** Calculate additive quantities using deterministic, testable formulas.
- **Photo Management:** Attach aquarium photographs to observations and maintenance records.
- **Subscription Management:** Provide free and premium functionality through a SaaS subscription model.

### Engineering Objective

Demonstrate the design and implementation of a production-oriented, distributed SaaS application using modern engineering practices.

The project will cover:

- Microservices and Clean Architecture
- Domain-driven design principles
- Event-driven and asynchronous messaging
- RESTful APIs and API management
- Authentication, authorisation, and tenant isolation
- Relational and NoSQL persistence
- Containerisation and serverless processing
- AI integration, retrieval-augmented generation (RAG), and vector search
- Infrastructure as Code
- Automated testing and CI/CD
- Security and DevSecOps
- Distributed tracing and observability
- Resilience, scalability, and operational readiness
- Agentic AI software development with human governance

The intention is to demonstrate not only the final application, but also the engineering decisions, processes, and controls used to deliver it.

## Architecture

Parameter Pilot is being designed as a distributed application hosted on Microsoft Azure.

The proposed architecture consists of three primary microservices, an Angular single-page application, an API gateway, and supporting Azure platform services.

### Microservices

| Service | Responsibility | Data Storage |
|---|---|---|
| Aquarium Service | Aquarium profiles, configuration, equipment, livestock, and parameter definitions | Azure SQL |
| Tracking Service | Parameter measurements, maintenance activities, observations, and historical trends | Azure Cosmos DB |
| Advisor Service | AI-assisted analysis and contextual maintenance recommendations | AI services and supporting data stores |

Each service follows Clean Architecture principles with separate API, Application, Domain, and Infrastructure layers.

### Technology Stack

| Category | Technology |
|---|---|
| Backend | .NET 10, C# 14, ASP.NET Core |
| Frontend | Angular, TypeScript |
| Architecture | Microservices, Clean Architecture, event-driven design |
| Relational Database | Azure SQL, Entity Framework Core |
| NoSQL Database | Azure Cosmos DB |
| API Gateway | Azure API Management |
| Messaging | Azure Service Bus |
| Serverless Processing | Azure Functions |
| File Storage | Azure Blob Storage |
| AI Platform | Microsoft Foundry |
| Knowledge Retrieval | Azure AI Search |
| Authentication | Microsoft Entra External ID |
| Secrets | Azure Key Vault |
| Configuration | Azure App Configuration |
| Container Registry | Azure Container Registry |
| Infrastructure as Code | Azure Bicep |
| Observability | OpenTelemetry, Application Insights, Log Analytics |
| CI/CD | GitHub Actions and/or Azure DevOps |
| Automated Testing | xUnit, FluentAssertions, Angular testing tools |
| Architecture Modelling | Structurizr DSL, C4 Model |

Technology choices will be confirmed through the architecture review and Architecture Decision Record (ADR) process.

### Architecture Diagrams

The architecture is maintained as code using Structurizr DSL and the C4 modelling approach.

The repository contains architecture definitions under:

`docs/architecture/structurizr/`

Planned and existing views include system context, containers, deployment topology, and dynamic interactions for parameter recording, trend analysis, maintenance advice, and photo uploads.

Architecture diagrams will evolve alongside the approved technical specifications.

## AI-Assisted Aquarium Advice

A key feature of Parameter Pilot is the planned AI Advisor.

Rather than providing generic aquarium advice, the Advisor will use contextual information such as aquarium type, volume, historical measurements, recent maintenance, dosing records, and relevant reference knowledge.

The proposed architecture combines:

1. Structured aquarium information retrieved from application services.
2. Historical parameter and maintenance data.
3. Curated aquarium knowledge retrieved using RAG.
4. An AI model hosted through Microsoft Foundry.

AI-generated recommendations will be distinguished from deterministic calculations and validated domain rules.

The system will incorporate appropriate safeguards, including grounded responses, evaluation, usage limits, and transparency about the limitations of AI-generated advice.

## Engineering Approach

Parameter Pilot follows a **design-first, agentic implementation methodology** intended to reflect engineering practices found in modern software development teams.

The approach separates architectural decision-making from implementation.

### Architecture and Technical Design

ChatGPT is used as an architecture and technical design partner to assist with:

- Product and functional requirements
- Non-functional requirements
- Domain modelling and service boundaries
- C4 architecture diagrams
- Architecture Decision Records
- API and event contracts
- Azure hosting and infrastructure design
- Security and identity architecture
- AI architecture
- CI/CD and observability design
- Engineering standards and agent governance

Design artefacts are reviewed and approved before implementation begins.

### Agentic Implementation

GitHub Copilot specialist agents are intended to implement approved technical specifications.

Agent responsibilities include backend development, frontend development, cloud infrastructure, AI integration, automated testing, security review, code review, and technical documentation.

Repository-wide agent instructions are defined in:

`AGENTS.md`

Specialist agent definitions are maintained in:

`.github/agents/`

Agents operate within defined engineering standards and implementation boundaries.

**AI agents do not have authority to independently change approved architectural decisions.**

Changes requiring architectural reconsideration must be escalated for human review.

### Human Governance

All significant implementation work follows a pull-request-based workflow.

```text
Product Requirements
        |
        v
Technical Specifications
        |
        v
Architecture Review & Approval
        |
        v
GitHub Issue
        |
        v
Specialist Copilot Agent
        |
        v
Implementation + Tests + Documentation
        |
        v
Pull Request
        |
        v
Automated Quality & Security Checks
        |
        v
Human Review & Approval
        |
        v
Merge into Main
```

Human review remains the final authority for approving changes to the application.

## Project Management

Parameter Pilot is managed using **GitHub Projects**, following an Agile, Kanban-based delivery approach.

The GitHub Project is publicly visible to provide transparency into the project's development lifecycle.

GitHub Issues are used to manage requirements, technical tasks, defects, architectural work, and improvements.

Work is prioritised and tracked through the project board, with implementation linked to relevant issues and pull requests.

**Project Board:** [Parameter Pilot — GitHub Projects](https://github.com/orgs/ausdatatech/projects) *(replace with the actual public project URL)*

### Traceability

A key engineering objective is to maintain traceability between requirements, architecture, implementation, and verification.

```text
Functional Requirement
        |
        v
Technical Specification
        |
        v
Architecture Decision / API Contract
        |
        v
GitHub Issue
        |
        v
Pull Request
        |
        v
Automated Tests
        |
        v
Human Approval
```

Significant changes should reference the relevant requirements, technical specifications, and ADRs.

This creates an auditable record of why a capability was developed, how it was designed, how it was implemented, and how it was verified.

## Development Standards

The project adopts the following engineering principles:

- **Architecture First:** Significant design decisions are documented before implementation.
- **Clean Architecture:** Business logic remains independent of infrastructure concerns.
- **Service Ownership:** Microservices own their respective business capabilities and data.
- **Contract-First Development:** APIs and integration events are defined through explicit contracts.
- **Automated Verification:** Code changes require appropriate automated tests and quality checks.
- **Security by Design:** Authentication, authorisation, secret management, and least-privilege access are fundamental requirements.
- **Infrastructure as Code:** Azure resources are provisioned and managed through version-controlled Bicep definitions.
- **Observability by Design:** Services expose appropriate logs, metrics, traces, and health information.
- **Human Accountability:** AI-generated changes remain subject to human review and approval.
- **Documentation as Code:** Requirements, architecture, technical specifications, and operational documentation are maintained alongside the source code.

## 📦 Repository Structure

The proposed repository organisation is:

```text
ParameterPilot/
├── .github/
│   ├── agents/                 # Specialist Copilot agents
│   ├── instructions/           # Path-specific development rules
│   └── workflows/              # CI/CD and security workflows
│
├── docs/
│   ├── requirements/           # Product and system requirements
│   ├── architecture/           # C4 diagrams and architecture decisions
│   ├── api/                    # OpenAPI specifications
│   ├── events/                 # Integration event contracts
│   ├── engineering/            # Engineering standards
│   └── operations/             # Deployment and operational procedures
│
├── src/
│   ├── services/
│   │   ├── Aquarium/
│   │   ├── Tracking/
│   │   └── Advisor/
│   ├── gateway/                # API Gateway / BFF
│   └── web/                    # Angular application
│
├── tests/                      # Automated tests
├── contracts/                  # Shared integration contracts
├── infra/                      # Azure Bicep infrastructure
├── scripts/                    # Development utilities
├── AGENTS.md                   # AI agent governance
├── README.md
└── SECURITY.md
```

The structure is subject to refinement as the Engineering & Architecture Pack is completed.

## Infrastructure and Deployment

The application is designed for Microsoft Azure, with infrastructure managed through Bicep.

The development environment will reuse appropriate resources from an existing Shared Development Platform where practical.

The hosting design includes an Azure Static Web App for the Angular frontend, containerised ASP.NET Core services, managed databases, asynchronous messaging, and centralised monitoring.

Infrastructure and application deployment will be automated through CI/CD pipelines, with appropriate validation and approval gates.

The project aims to minimise manual infrastructure changes and maintain consistency between deployed environments and version-controlled definitions.

## Development Roadmap

The high-level roadmap is:

| Phase | Focus |
|---|---|
| 1 | Product requirements and functional specifications |
| 2 | Architecture, technical design, and ADR approval |
| 3 | Engineering standards and agent governance |
| 4 | Core Aquarium and Tracking capabilities |
| 5 | Measurement history, maintenance tracking, and visualisation |
| 6 | Event-driven integration and background processing |
| 7 | AI Advisor and contextual recommendations |
| 8 | Identity, subscription management, and SaaS capabilities |
| 9 | Observability, security hardening, and operational readiness |
| 10 | Advanced AI capabilities and external integrations |

Detailed implementation tasks, priorities, and progress are maintained in the public GitHub Project.

## Documentation

Project documentation is maintained in Markdown alongside the source code.

The documentation is intended to provide an auditable record of the application's design and implementation, including requirements, architectural decisions, technical specifications, development standards, and operational procedures.

Where applicable, documentation is also published through the project's documentation website.

## Current Status

Parameter Pilot is under active design and development.

The current focus is establishing the Engineering & Architecture Pack, formalising requirements and technical specifications, and defining the governance model for AI-assisted implementation.

Existing work includes initial Structurizr architecture models, documentation structure, and Azure infrastructure definitions for the application website.

Implementation status and future milestones are tracked through GitHub Projects.

## Security

Security considerations are incorporated throughout the development lifecycle.

The project will use automated dependency and code scanning, secure identity practices, managed identities where supported, and appropriate secret-management controls.

Please refer to [SECURITY.md](SECURITY.md) for vulnerability reporting guidance.

## Licence

See [LICENSE](LICENSE) for the repository's licensing terms.

---

**Parameter Pilot** — A practical Azure SaaS application demonstrating architecture-led, AI-assisted software engineering.