workspace "Parameter Pilot" "Cloud-native aquarium parameter tracking and AI-assisted maintenance advice." {

  !identifiers hierarchical

  model {
    !include model/people.dsl
    !include model/systems.dsl
    !include model/relationships.dsl
    !include model/deployment.azure.dsl
  }

  views {
    theme https://static.structurizr.com/themes/microsoft-azure-2021.01.26/theme.json
    !include views/views.dsl
    !include views/styles.dsl
  }
}
