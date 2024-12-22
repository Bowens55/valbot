resource "azurerm_resource_group" "rg" {
  name     = local.prefix
  location = var.location
}