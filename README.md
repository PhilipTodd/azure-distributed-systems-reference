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



## 📦 Repository Structure

src/ → Microservices and shared building blocks

infra/ → Infrastructure-as-code and environment definitions

docs/ → Architecture documentation and C4 models

.github/ → CI/CD workflows



---
## Structurizr

Structurizr is a "diagrams-as-code" tool used by software developers and architects to visualize, document, and maintain software architecture. It is built specifically to implement the C4 model—a hierarchical mapping method that breaks down systems into Context, Containers, Components, and Code.

The files relevent for this project are in the following folder:

docs/architecture/structurizr

The following command can be run in Powershell to run Structurizr in a docker container displaying the reference project. Alter the path to suit your local environment:

  `docker run -it --rm -p 8080:8080 -v "C:\Git\azure-distributed-systems-reference\docs\architecture\structurizr:/usr/local/structurizr" structurizr/lite`


---

## 📄 License

MIT 
