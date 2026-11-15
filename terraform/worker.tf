resource "aws_ecs_task_definition" "worker_task" {
  family                   = "worker-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_worker_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "worker-container"
      image     = "${aws_ecr_repository.api.repository_url}:latest"
      essential = true
      command   = ["python", "worker.py"]
      environment = [
        {
          name  = "DATABASE_URL"
          value = "mysql+pymysql://${var.db_user}:${var.db_password}@${aws_db_instance.api_imdb.endpoint}/${aws_db_instance.api_imdb.db_name}"
        },
        {
          name  = "SQS_QUEUE_URL"
          value = aws_sqs_queue.reviews_queue.url
        },
        {
          name  = "AWS_REGION"
          value = "eu-central-1"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/worker"
          "awslogs-region"        = "eu-central-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

# Worker Service
resource "aws_ecs_service" "worker_service" {
  name            = "worker-service"
  cluster         = aws_ecs_cluster.app_cluster.id
  task_definition = aws_ecs_task_definition.worker_task.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets          = [aws_subnet.private_a.id, aws_subnet.private_b.id]
    security_groups  = [aws_security_group.app_sg.id]
    assign_public_ip = false
  }

  lifecycle {
    ignore_changes = [
      desired_count
    ]
  }
}

resource "aws_cloudwatch_log_group" "worker_log_group" {
  name              = "/ecs/worker"
  retention_in_days = 7
}
