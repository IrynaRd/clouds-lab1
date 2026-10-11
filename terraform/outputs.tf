output "app_url" {
  value = "http://${aws_lb.app_lb.dns_name}"
}

output "ecr_repository_url" {
  value = aws_ecr_repository.api.repository_url
}

output "database_endpoint" {
  value = aws_db_instance.api_imdb.address
}

output "ecs_service_name" {
  value = aws_ecs_service.app_service.name
}