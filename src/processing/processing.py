import sys

sys.path.append('/opt/bin/')

import json
import logging
import os
import zipfile
import boto3
from botocore.exceptions import NoCredentialsError

# Configuração do logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Inicialização de clientes AWS
s3_client = boto3.client('s3')

# Variáveis de ambiente
BUCKET_NAME = os.environ["BUCKET_NAME"]

def create_response(status_code, message=None, data=None):
    """
    Gera uma resposta formatada.
    """
    response = {"statusCode": status_code, "body": {}}
    if message:
        response["body"]["message"] = message
    if data:
        response["body"].update(data)
    return response

def normalize_body(event):
    """
    Normaliza o corpo da requisição para garantir que seja um dicionário.
    """
    if isinstance(event.get("body"), str):
        return json.loads(event["body"])  # Desserializa string JSON para dicionário
    elif isinstance(event.get("body"), dict):
        return event["body"]  # Já está em formato de dicionário
    else:
        raise ValueError("Request body is missing or invalid.")

def validate_request(body):
    """
    Valida os campos obrigatórios na requisição.
    """
    required_fields = ["videoId", "userName", "email", "frameRate"]
    missing_fields = [field for field in required_fields if field not in body]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
def process_frames(body_message):
    video_id = body_message['videoId']
    user_name = body_message['userName']
    email = body_message['email']
    frame_rate = body_message['frameRate']

    download_path_bucket = f"videos/{user_name}/{video_id}/upload/{video_id}-source.mp4"
    lambda_video_path = f"/tmp/{video_id}"
    output_folder = "/tmp/frames"
    zip_path = "/tmp/frames.zip"
    output_zip_key = f"videos/{user_name}/{video_id}/processed/{os.path.basename(zip_path)}"

    if frame_rate > 0:
        download_from_s3(download_path_bucket, lambda_video_path)
        extract_frames(lambda_video_path, output_folder, frame_rate)
        create_zip(output_folder, zip_path)
        upload_to_s3(output_zip_key, zip_path)

        url = generate_url(output_zip_key)

        logger.info(f"url_download: {url}")
        
        response = send_email_sucesso(email, url)

        return response
    else :
        return create_response(400, message="Invalid frame rate number, must be greater than 0")
    
def download_from_s3(video_id, download_path):
    try:
        s3_client.download_file(BUCKET_NAME, video_id, download_path)
        logger.info(f"Downloaded {video_id} from S3 bucket {BUCKET_NAME}")
    except NoCredentialsError:
        logger.info("Credentials not available")

def upload_to_s3(output_zip_key, file_path):
    try:
        s3_client.upload_file(file_path, BUCKET_NAME, output_zip_key)
        logger.info(f"Uploaded {file_path} to S3 bucket {BUCKET_NAME}")
    except NoCredentialsError:
        logger.info("Credentials not available")

def extract_frames(lambda_video_path, output_folder, frame_rate):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    os.system(f"/opt/bin/ffmpeg.exe -i {lambda_video_path} -vf fps=1/{frame_rate} {os.path.join(output_folder, 'frame_%04d.jpg')}")

def create_zip(output_folder, zip_path):
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(output_folder):
            for file in files:
                zipf.write(os.path.join(root, file), file)
    logger.info(f"Created zip file {zip_path}")

def generate_url(video_id):
    expiration=3600
    try:
        response = s3_client.generate_presigned_url('get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': video_id},
            ExpiresIn=expiration)
    except NoCredentialsError:
        logger.info("Credentials not available")
        raise NoCredentialsError("Credentials not available")
    return response

def send_email_sucesso(email, url_download):
    logger.info(f"Body: {message_body}")
    logger.info(f"Processing completed successfully!")

    return {
        'statusCode': 200,
        'body': { 
            "email": email,
            "processingLink": url_download
        }
    }

def send_email_error(email):
    message_body = {
        "email": email,
    }

    logger.info(f"Body: {message_body}")

    return {
        'statusCode': 500,
        'body': message_body
    }


def lambda_handler(event, context):
    """
    Entrada principal da Lambda.
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        # Normalizar o corpo da requisição
        body = normalize_body(event)

        # Validar os campos obrigatórios no corpo da requisição
        validate_request(body)

        # Processar a geração dos frames
        response_data = process_frames(body)

        return create_response(200, data=response_data)

    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        return create_response(400, message=str(ve))

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return create_response(500, message="An unexpected error occurred. Please try again later.")