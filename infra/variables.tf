######### PREFIXO DO PROJETO ###########################################
variable "prefix_name" {
  description = "Prefixo para nomear todos os recursos do projeto"
}

######### AWS INFOS ####################################################
variable "aws_region" {
  description = "Região AWS onde os recursos serão provisionados"
}
######### PROJECT INFOS ################################################
variable "lambda_name" {
  description = "Nome da função Lambda principal"
}

variable "lambda_handler" {
  description = "Handler da função Lambda principal"
}

variable "lambda_zip_path" {
  description = "Caminho para o pacote ZIP contendo o código da função Lambda"
}

variable "lambda_runtime" {
  description = "Runtime da função Lambda principal"
}

variable "lambda_timeout" {
  description = "Tempo limite de execução da função Lambda principal"
}

######### LOGS CLOUD WATCH #############################################
variable "log_retention_days" {
  description = "Número de dias para retenção dos logs no CloudWatch"
}

######### S3 BUCKET INFOS ###############################################
variable "bucket_name" {
  description = "Nome do bucket S3 para armazenar os vídeos"
}