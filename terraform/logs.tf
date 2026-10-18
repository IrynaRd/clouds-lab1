resource "aws_cloudwatch_dashboard" "app_dashboard" {
  dashboard_name = "app-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric", x = 0, y = 0, width = 12, height = 6
        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ClusterName", aws_ecs_cluster.app_cluster.name, "ServiceName", aws_ecs_service.app_service.name],
            ["AWS/ECS", "MemoryUtilization", "ClusterName", aws_ecs_cluster.app_cluster.name, "ServiceName", aws_ecs_service.app_service.name],

          ]
          period = 60
          stat   = "Average"
          region = "eu-central-1"
          title  = "CPU & Memory"
        }
      },
      {
        type = "metric", x = 12, y = 0, width = 12, height = 6
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
        type = "metric", x = 0, y = 6, width = 12, height = 6
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "HTTPCode_ELB_5XX_Count", "LoadBalancer", aws_lb.app_lb.arn_suffix],
            ["AWS/ApplicationELB", "HTTPCode_Target_5XX_Count", "LoadBalancer", aws_lb.app_lb.arn_suffix],
          ]
          period = 60
          view   = "bar"
          stat   = "Sum"
          region = "eu-central-1"
          title  = "5XX Errors"
        }
      },
      {
        type = "metric", x = 12, y = 6, width = 12, height = 6
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", aws_lb.app_lb.arn_suffix],
          ]
          period = 60
          stat   = "Average"
          region = "eu-central-1"
          title  = "Target Response Time"
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

resource "aws_cloudwatch_metric_alarm" "errors_5xx" {
  alarm_name                = "5XX-errors"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1
  metric_name               = "HTTPCode_Target_5XX_Count"
  namespace                 = "AWS/ApplicationELB"
  period                    = 60
  statistic                 = "Sum"
  threshold                 = 1
  alarm_description         = "Alert if the app returns 5XX error"
  insufficient_data_actions = []
  alarm_actions             = [aws_sns_topic.alerts.arn]
  dimensions = {
    LoadBalancer = aws_lb.app_lb.arn_suffix
  }
}
