workspace "Azure Container Apps - 3 Microservices" "Reference architecture for local Docker + Azure Container Apps." {

  !identifiers hierarchical

  model {
    !include model/people.dsl
    !include model/systems.dsl
	!include model/deployment.azure.dsl
    !include model/relationships.dsl
  }

  views {
    !include views/views.dsl
    !include views/styles.dsl
  }
}
