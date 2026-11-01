terraform {
  required_providers {
    aiven = {
      source  = "aiven/aiven"
      version = "~> 4.0"
    }
    postgresql = {
      source  = "cyrilgdn/postgresql"
      version = "~> 1.25"
    }
  }
  backend "http" {}
}

provider "aiven" {
  api_token = var.aiven_api_token
}

resource "aiven_pg" "pg" {
  project      = var.aiven_project
  service_name = "equipe-${var.equipe}-pg"
  plan         = var.plan
  cloud_name   = var.cloud_name
}

resource "aiven_pg_database" "db" {
  project       = var.aiven_project
  service_name  = aiven_pg.pg.service_name
  database_name = var.database_name
}

resource "aiven_pg_user" "app" {
  project      = var.aiven_project
  service_name = aiven_pg.pg.service_name
  username     = var.db_user
}

provider "postgresql" {
  host      = aiven_pg.pg.service_host
  port      = aiven_pg.pg.service_port
  username  = aiven_pg.pg.service_username
  password  = aiven_pg.pg.service_password
  database  = aiven_pg_database.db.database_name
  sslmode   = "require"
  superuser = false
}

resource "postgresql_grant" "schema" {
  database    = aiven_pg_database.db.database_name
  role        = aiven_pg_user.app.username
  schema      = "public"
  object_type = "schema"
  privileges  = ["CREATE", "USAGE"]
}
