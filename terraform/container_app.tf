resource "azurerm_log_analytics_workspace" "law" {
  name                = "${local.prefix}-law"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_container_app_environment" "appenv" {
  name                       = "${local.prefix}-appenv"
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
  depends_on                 = [azurerm_log_analytics_workspace.law]
}

resource "azurerm_container_app" "valobot" {
  name                         = local.prefix
  container_app_environment_id = azurerm_container_app_environment.appenv.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"
  template {
    max_replicas = 1
    min_replicas = 1
    container {
      name   = "vlrbot"
      image  = "bowens55/vlrbot:${var.image_tag}"
      cpu    = 0.25
      memory = "0.5Gi"
      env {
        name  = "DISCORD_TOKEN"
        value = var.discord_token
      }
      env {
        name  = "API_BASE_URL"
        value = "https://${azurerm_container_app.valobotapi.latest_revision_fqdn}"
      }
      env {
        name  = "GUILD_ID"
        value = var.guild_id
      }
      env {
        name  = "CHANNEL_ID"
        value = var.channel_id
      }
    }
  }
  registry {
    server               = "docker.io"
    username             = "bowens55"
    password_secret_name = "dockerio-bowens55"
  }
  secret {
    name  = "dockerio-bowens55"
    value = var.docker_secret
  }
  identity {
    type = "SystemAssigned"
  }
  depends_on = [azurerm_container_app.valobotapi, azurerm_container_app_environment.appenv]
  lifecycle {
    ignore_changes = [template[0].container[0].image]
  }
}

resource "azurerm_container_app" "valobotapi" {
  name                         = "${local.prefix}-api"
  container_app_environment_id = azurerm_container_app_environment.appenv.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"
  template {
    max_replicas = 1
    min_replicas = 1
    container {
      name   = "vlrbotapi"
      image  = "ghcr.io/axsddlr/vlrggapi:latest"
      cpu    = 0.5
      memory = "1Gi"
    }
  }
  ingress {
    external_enabled = true
    target_port      = 3001
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }
  depends_on = [azurerm_container_app_environment.appenv]
}
