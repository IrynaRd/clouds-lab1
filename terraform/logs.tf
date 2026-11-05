resource "aws_cloudwatch_dashboard" "app_dashboard" {
  dashboard_name = "app-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric", x = 0, y = 0, width = 12, height = 6
        properties = {
          metrics = [
            ["ECS/ContainerInsights", "DesiredTaskCount", "ClusterName", aws_ecs_cluster.app_cluster.name, "ServiceName", aws_ecs_service.app_service.name],
            ["ECS/ContainerInsights", "RunningTaskCount", "ClusterName", aws_ecs_cluster.app_cluster.name, "ServiceName", aws_ecs_service.app_service.name],

          ]
          period = 60
          stat   = "Average"
          region = "eu-central-1"
          title  = "Desired & Running Task Count"
        }
      },
      {
        type = "metric", x = 12, y = 0, width = 12, height = 6
        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ClusterName", aws_ecs_cluster.app_cluster.name, "ServiceName", aws_ecs_service.app_service.name]
          ]
          period = 60
          stat   = "Average"
          region = "eu-central-1"
          title  = "CPU Utilization"
          yAxis = {
            left = {
              min = 0
              max = 100
            }
          }
        }
      },
      {
        type = "metric", x = 0, y = 6, width = 12, height = 6
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", aws_lb.app_lb.arn_suffix],
          ]
          period = 60
          stat   = "Sum"
          region = "eu-central-1"
          title  = "Request Count"
        }
      },
      {
        type = "metric", x = 0, y = 12, width = 12, height = 6
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "HTTPCode_Target_5XX_Count", "LoadBalancer", aws_lb.app_lb.arn_suffix],
          ]
          period = 60
          view   = "bar"
          stat   = "Sum"
          region = "eu-central-1"
          title  = "5XX Target Errors"
        }
      },
      {
        type = "metric", x = 12, y = 6, width = 12, height = 6
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", aws_lb.app_lb.arn_suffix, { stat = "p95" }],
          ]
          period = 60
          stat   = "Average"
          region = "eu-central-1"
          title  = "Target Response Time p95"
        }
      }
    ]
  })
}

resource "aws_sns_topic" "alerts" {
  name = "app-alerts"
}

resource "aws_sns_topic_subscription" "email_alert" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

resource "aws_cloudwatch_metric_alarm" "max_tasks" {
  alarm_name                = "max-tasks"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1
  datapoints_to_alarm       = 1
  metric_name               = "DesiredTaskCount"
  namespace                 = "ECS/ContainerInsights"
  period                    = 60
  statistic                 = "Maximum"
  threshold                 = aws_appautoscaling_target.ecs_target.max_capacity
  alarm_description         = "Alert if the tasks number reached maximum"
  insufficient_data_actions = []
  alarm_actions             = [aws_sns_topic.alerts.arn]
  ok_actions                = [aws_sns_topic.alerts.arn]
  dimensions = {
    ClusterName = aws_ecs_cluster.app_cluster.name
    ServiceName = aws_ecs_service.app_service.name
  }
}
