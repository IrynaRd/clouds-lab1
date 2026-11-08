resource "aws_ecs_cluster" "app_cluster" {
  name = "app-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_task_definition" "app_task" {
  family                   = "app-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "api-container"
      image     = "${aws_ecr_repository.api.repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = 5000
          hostPort      = 5000
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "DATABASE_URL"
          value = "mysql+pymysql://${var.db_user}:${var.db_password}@${aws_db_instance.api_imdb.endpoint}/${aws_db_instance.api_imdb.db_name}"
        },
        {
          name  = "REDIS_URL"
          value = "redis://${aws_elasticache_cluster.redis_cluster.cache_nodes[0].address}:${aws_elasticache_cluster.redis_cluster.cache_nodes[0].port}/0"
        },
        {
          name  = "CACHE_ENABLED"
          value = "${var.cache_enabled}"
        },
        {
          name  = "CACHE_TTL"
          value = "${var.cache_ttl}"
        },
        {
          name  = "JWT_SECRET_KEY"
          value = "${var.jwt_secret_key}"
        },
        {
          name  = "APP_PASSWORD"
          value = "${var.app_password}"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/app"
          "awslogs-region"        = "eu-central-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

}

resource "aws_cloudwatch_log_group" "ecs_log_group" {
  name              = "/ecs/app"
  retention_in_days = 7
}

resource "aws_ecs_service" "app_service" {
  name            = "app-service"
  cluster         = aws_ecs_cluster.app_cluster.id
  task_definition = aws_ecs_task_definition.app_task.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets          = [aws_subnet.private_a.id, aws_subnet.private_b.id]
    security_groups  = [aws_security_group.app_sg.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app_tg.arn
    container_name   = "api-container"
    container_port   = 5000
  }

  lifecycle {
    ignore_changes = [
      task_definition,
      desired_count
    ]
  }
}


resource "aws_appautoscaling_target" "ecs_target" {
  min_capacity = 1
  max_capacity = 3

  resource_id = "service/${aws_ecs_cluster.app_cluster.name}/${aws_ecs_service.app_service.name}"

  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "ecs_cpu_policy" {
  name        = "ecs-cpu-autoscaling-policy"
  policy_type = "TargetTrackingScaling"

  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }

    target_value       = 60.0
    scale_out_cooldown = 60
    scale_in_cooldown  = 180
  }
}
