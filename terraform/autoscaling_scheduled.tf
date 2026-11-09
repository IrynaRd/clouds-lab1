resource "aws_appautoscaling_scheduled_action" "scale_day" {
  name               = "scale-day"
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  schedule           = "cron(0 5 * * ? *)"

  scalable_target_action {
    min_capacity = 2
    max_capacity = 3
  }
}

resource "aws_appautoscaling_scheduled_action" "scale_night" {
  name               = "scale-night"
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  schedule           = "cron(0 18 * * ? *)"

  scalable_target_action {
    min_capacity = 1
    max_capacity = 3
  }
}