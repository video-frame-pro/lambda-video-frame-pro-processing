######### PROVEDOR AWS #################################################
provider "aws" {
  region = var.aws_region
}

######### DADOS AWS ####################################################
# Obter informações sobre a conta AWS (ID da conta, ARN, etc.)
data "aws_caller_identity" "current" {}

######### REFERÊNCIA À LAYER ###########################################
data "aws_lambda_layer_version" "lib_layer" {
  layer_name = "${var.prefix_name}-${var.layer_name}"
}

######### FUNÇÃO LAMBDA ###############################################
# Função Lambda principal
resource "aws_lambda_function" "lambda_function" {
  function_name    = "${var.prefix_name}-${var.lambda_name}-lambda"
  handler          = var.lambda_handler
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_role.arn
  filename         = var.lambda_zip_path
  source_code_hash = filebase64sha256(var.lambda_zip_path)
  timeout       = 30  # Máximo permitido no Free Tier sem preocupações
  memory_size   = 256 # Ainda dentro do Free Tier

  # Adicionar a Layer na Lambda
  layers = [data.aws_lambda_layer_version.lib_layer.arn]

  # Variáveis de ambiente para a Lambda
  environment {
    variables = {
      BUCKET_NAME = var.bucket_name
    }
  }
}

######### GRUPO DE LOGS ###############################################
# Grupo de logs no CloudWatch para a Lambda
resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${var.prefix_name}-${var.lambda_name}-lambda"
  retention_in_days = var.log_retention_days
}

######### IAM: FUNÇÃO LAMBDA ##########################################
# Role IAM para a Lambda principal
resource "aws_iam_role" "lambda_role" {
  name = "${var.prefix_name}-${var.lambda_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# Política de permissões para a Lambda principal
resource "aws_iam_policy" "lambda_policy" {
  name = "${var.prefix_name}-${var.lambda_name}-policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        # Permissões para logs no CloudWatch
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
        Effect   = "Allow",
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/*"
      },
      {
        # Permissões de acesso ao S3
        Action   = ["s3:GetObject", "s3:PutObject"],
        Effect   = "Allow",
        Resource = "arn:aws:s3:::${var.bucket_name}/*"
      }
    ]
  })
}

# Anexar a política de permissões à role da Lambda
resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}