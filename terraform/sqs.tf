resource "aws_sqs_queue" "reviews_queue" {
  name                       = "reviews-queue"
  visibility_timeout_seconds = 30
  message_retention_seconds  = 86400
  receive_wait_time_seconds  = 20

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.reviews_dlq.arn
    maxReceiveCount     = 5
  })
}

resource "aws_sqs_queue" "reviews_dlq" {
  name                      = "reviews-dlq"
  message_retention_seconds = 172800
}