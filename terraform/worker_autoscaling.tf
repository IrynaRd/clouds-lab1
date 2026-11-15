resource "aws_appautoscaling_target" "worker_target" {
  min_capacity = 1
  max_capacity = 3

  resource_id        = "service/${aws_ecs_cluster.app_cluster.name}/${aws_ecs_service.worker_service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_cloudwatch_metric_alarm" "worker_scale_out_alarm" {
  alarm_name          = "worker-queue-high"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 60
  statistic           = "Maximum"
  threshold           = 5
  alarm_description   = "Scale out workers when queue depth >= 5"

  dimensions = {
    QueueName = aws_sqs_queue.reviews_queue.name
  }

  alarm_actions = [aws_appautoscaling_policy.worker_scale_out.arn]
}

resource "aws_appautoscaling_policy" "worker_scale_out" {
  name               = "worker-scale-out"
  policy_type        = "StepScaling"
  resource_id        = aws_appautoscaling_target.worker_target.resource_id
  scalable_dimension = aws_appautoscaling_target.worker_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.worker_target.service_namespace

  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown                = 60
    metric_aggregation_type = "Maximum"

    step_adjustment {
      scaling_adjustment          = 1
      metric_interval_lower_bound = 0
      metric_interval_upper_bound = 50
    }

    step_adjustment {
      scaling_adjustment          = 2
      metric_interval_lower_bound = 50
    }
  }
}


resource "aws_cloudwatch_metric_alarm" "worker_scale_in_alarm" {
  alarm_name          = "worker-queue-empty"
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods  = 3
  datapoints_to_alarm = 3
  threshold           = 0
  alarm_description   = "Scale in workers when queue has no visible or in-flight messages"
  treat_missing_data  = "notBreaching"

  metric_query {
    id          = "visible"
    return_data = false

    metric {
      metric_name = "ApproximateNumberOfMessagesVisible"
      namespace   = "AWS/SQS"
      period      = 60
      stat        = "Maximum"

      dimensions = {
        QueueName = aws_sqs_queue.reviews_queue.name
      }
    }
  }

  metric_query {
    id          = "not_visible"
    return_data = false

    metric {
      metric_name = "ApproximateNumberOfMessagesNotVisible"
      namespace   = "AWS/SQS"
      period      = 60
      stat        = "Maximum"

      dimensions = {
        QueueName = aws_sqs_queue.reviews_queue.name
      }
    }
  }

  metric_query {
    id          = "backlog"
    expression  = "visible + not_visible"
    label       = "Total queue backlog"
    return_data = true
  }

  alarm_actions = [
    aws_appautoscaling_policy.worker_scale_in.arn
  ]
}

resource "aws_appautoscaling_policy" "worker_scale_in" {
  name               = "worker-scale-in"
  policy_type        = "StepScaling"
  resource_id        = aws_appautoscaling_target.worker_target.resource_id
  scalable_dimension = aws_appautoscaling_target.worker_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.worker_target.service_namespace

  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown                = 300
    metric_aggregation_type = "Maximum"

    step_adjustment {
      scaling_adjustment          = -1
      metric_interval_upper_bound = 0
    }
  }
}
