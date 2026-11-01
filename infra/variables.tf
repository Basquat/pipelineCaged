variable "aiven_api_token" {
  type      = string
  sensitive = true
}

variable "aiven_project" {
  type = string
}

variable "equipe" {
  type = string
}

variable "plan" {
  type    = string
  default = "free-1-1gb"
}

variable "cloud_name" {
  type    = string
  default = null
}

variable "database_name" {
  type    = string
  default = "caged"
}

variable "db_user" {
  type    = string
  default = "app"
}
