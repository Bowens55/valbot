variable "location" {
  default     = "West US 2"
  description = "location of the resources in Azure."
  validation {
    condition     = contains(["West US 2", "West US"], var.location)
    error_message = "Azure region/location must be West US 2 or West US."
  }
}

variable "env" {
  default = "prd"
}

variable "discord_token" {
  description = "discord token set as an env var on the container app."
}

variable "guild_id" {
  description = "guild ID set as env var."
}

variable "channel_id" {
  description = "channel ID set as env var."
}

variable "docker_secret" {
  description = "docker secret used to pull image."
}

variable "image_tag" {
  description = "image tag to use for vlrbot docker image. Dev=latest."
  default     = "latest"
}

locals {
  location_str = substr(var.location, 0, 3)
  prefix       = lower("${var.env}-valobot-${local.location_str}")
}