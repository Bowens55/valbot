terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "3.111.0"
    }
  }
}

variable "client_secret" {
  description = "the client secret of the az app reg created. Pass this through when running a TF plan/apply."
  sensitive   = true
}

provider "azurerm" {
  features {}
  client_id       = "50f923a3-b9af-4720-8bb5-ba92f7545f78"
  client_secret   = var.client_secret
  tenant_id       = "e2eda608-1004-4441-a273-817d706fe28a"
  subscription_id = "a5fdb59b-0a87-4b2a-b6ab-0fba77e4b268"
}