resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "github_actions_role" {
  name = "github-actions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Principal= {
          Federated = aws_iam_openid_connect_provider.github_actions_oidc_provider.arn
        },
        Action= "sts:AssumeRoleWithWebIdentity",
        Condition= {
          StringEquals= {
            "token.actions.githubusercontent.com:aud"= "sts.amazonaws.com",
            "token.actions.githubusercontent.com:sub"= "repo:IrynaRd@181106680/clouds-lab1@1404682570:ref:refs/heads/main"
          }
        }
      }
    ]
  })
}

resource "aws_iam_policy" "github_ecr_policy" {
  name = "github-ecr-policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
        {
            Effect = "Allow",
            Action = [
                "ecr:CompleteLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:InitiateLayerUpload",
                "ecr:BatchCheckLayerAvailability",
                "ecr:PutImage",
                "ecr:BatchGetImage"
            ],
            Resource = aws_ecr_repository.api.arn
        },
        {
            Effect = "Allow",
            Action = "ecr:GetAuthorizationToken",
            Resource = "*"
        }
    ]

  })
}

resource "aws_iam_role_policy_attachment" "github_ecr_policy_attachment" {
  role       = aws_iam_role.github_actions_role.name
  policy_arn = aws_iam_policy.github_ecr_policy.arn
}

resource "aws_iam_policy" "github_ecs_policy" {
  name = "github-ecs-policy"
  policy = jsonencode({
    Version ="2012-10-17",
    Statement =[
      {
          Sid ="RegisterTaskDefinition",
          Effect ="Allow",
          Action =[
            "ecs:RegisterTaskDefinition"
         ],
          Resource ="*"
      },
      {
          Sid ="PassRolesInTaskDefinition",
          Effect ="Allow",
          Action =[
            "iam:PassRole"
         ],
          Resource =[
            aws_iam_role.ecs_task_execution_role.arn
         ]
      },
      {
          Sid ="DeployService",
          Effect ="Allow",
          Action =[
            "ecs:UpdateService",
            "ecs:DescribeServices"
         ],
          Resource =[
            aws_ecs_service.app_service.id
         ]
      }
   ]
  })
}

resource "aws_iam_role_policy_attachment" "github_ecs_policy_attachment" {
  role       = aws_iam_role.github_actions_role.name
  policy_arn = aws_iam_policy.github_ecs_policy.arn
}