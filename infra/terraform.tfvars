######### PREFIXO DO PROJETO ###########################################
prefix_name = "video-frame-pro" # Prefixo para nomear todos os recursos

######### AWS INFOS ####################################################
aws_region  = "us-east-1"              # Região AWS onde os recursos serão provisionados
bucket_name = "video-frame-pro-bucket" # Nome do bucket S3 para armazenar os vídeos

######### PROJECT INFOS ################################################
lambda_name     = "processing"                    # Nome da função Lambda principal
lambda_handler  = "processing.lambda_handler"     # Handler da função Lambda principal
lambda_zip_path = "../lambda/processing/send.zip" # Caminho para o ZIP da função Lambda
lambda_runtime  = "python3.12"                    # Runtime da função Lambda principal
lambda_timeout  = 900                             # Tempo limite de execução da função Lambda principal

######### LOGS CLOUD WATCH #############################################
log_retention_days = 7 # Dias para retenção dos logs no CloudWatch
