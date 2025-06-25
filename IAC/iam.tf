data "aws_iam_user" "kubestronaut" {
  user_name = "Kubestronaut"
}

resource "aws_iam_policy" "eks_console_access" {
  name        = "EKSConsoleAccess"
  description = "Grants EKS GUI Console access to Kubestronaut"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "eks:AccessKubernetesApi",
          "eks:ListAccessEntries",
          "eks:DescribeAccessEntry",
          "eks:ListClusters",
          "eks:DescribeCluster",
          "eks:ListFargateProfiles",
          "eks:ListNodegroups",
          "eks:DescribeNodegroup",
          "eks:DescribeFargateProfile"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "kubestronaut_console_access" {
  user       = data.aws_iam_user.kubestronaut.user_name
  policy_arn = aws_iam_policy.eks_console_access.arn
}
