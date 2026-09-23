# Parameter Pilot - Structurizr Architecture

This directory contains the Structurizr DSL architecture model for the Parameter Pilot application.

The workspace loads the Microsoft Azure 2021 theme. Azure resource tags in `model/systems.dsl` and `model/deployment.azure.dsl` select its icons; `views/styles.dsl` styles the logical application elements. Structurizr Lite needs internet access to load the theme and icons.

## Run locally

From the repository root, run Structurizr Lite with the directory mounted:

```powershell
docker run -it --rm -p 8080:8080 -v "C:\Git\azure-distributed-systems-reference\docs\architecture\structurizr:/usr/local/structurizr" structurizr/lite
```

Then browse to:

```text
http://localhost:8080/
```

## Views

- System Context
- Container
- Record aquarium parameter
- View parameter trends
- Generate maintenance advice
- Upload aquarium photo
- Azure deployment

## Important DSL structure

External software systems such as Microsoft Entra External ID and Stripe are declared at the model/workspace scope, rather than inside the Parameter Pilot software-system declaration. This is required by the Structurizr DSL grammar.
