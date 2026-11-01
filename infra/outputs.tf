output "service_name" {
  value = aiven_pg.pg.service_name
}

output "db_password" {
  value     = aiven_pg_user.app.password
  sensitive = true
}

output "aiven_db_url" {
  value     = "postgresql://${aiven_pg_user.app.username}:${urlencode(aiven_pg_user.app.password)}@${aiven_pg.pg.service_host}:${aiven_pg.pg.service_port}/${aiven_pg_database.db.database_name}?sslmode=require"
  sensitive = true
}
