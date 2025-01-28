import sys

sys.path.append('/opt/bin/')

import json
import logging
import os
import zipfile

import boto3
import pyshorteners
from botocore.exceptions import NoCredentialsError

s3_client = boto3.client('s3')
bucket_name = bucket_name = "${var.bucket_name}"

# Configuração do logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
    videoId = body_message['videoId']
    userName = body_message['userName']
    email = body_message['email']
    frameRate = body_message['frameRate']

    download_path_bucket = f"entrada/{videoId}"
    lambda_video_path = f"/tmp/{videoId}"
    output_folder = "/tmp/frames"
    zip_path = "/tmp/frames.zip"
    output_zip_key = f"saida/{userName}/{os.path.basename(zip_path)}"

    if frameRate > 0:
        download_from_s3(bucket_name, download_path_bucket, lambda_video_path)
        extract_frames(lambda_video_path, output_folder, frameRate)
        create_zip(output_folder, zip_path)
        upload_to_s3(bucket_name, output_zip_key, zip_path)

        long_url = generate_url(bucket_name, output_zip_key)
        url_download = shorten_url(long_url)

        logger.info(f"url_download: {url_download}")
        
        response = send_email_sucesso(email, url_download)

        return response
    else :
        return create_response(400, message="Invalid frame rate number, must be greater than 0")
    
def download_from_s3(bucket_name, videoId, download_path):
    try:
        s3_client.download_file(bucket_name, videoId, download_path)
        logger.info(f"Downloaded {videoId} from S3 bucket {bucket_name}")
    except NoCredentialsError:
        logger.info("Credentials not available")

def upload_to_s3(bucket_name, output_zip_key, file_path):
    try:
        s3_client.upload_file(file_path, bucket_name, output_zip_key)
        logger.info(f"Uploaded {file_path} to S3 bucket {bucket_name}")
    except NoCredentialsError:
        logger.info("Credentials not available")

def extract_frames(lambda_video_path, output_folder, frameRate):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    os.system(f"/opt/bin/ffmpeg.exe -i {lambda_video_path} -vf fps=1/{frameRate} {os.path.join(output_folder, 'frame_%04d.jpg')}")

def create_zip(output_folder, zip_path):
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(output_folder):
            for file in files:
                zipf.write(os.path.join(root, file), file)
    logger.info(f"Created zip file {zip_path}")

def generate_url(bucket_name, videoId):
    expiration=3600
    try:
        response = s3_client.generate_presigned_url('get_object',
            Params={'Bucket': bucket_name, 'Key': videoId},
            ExpiresIn=expiration)
    except NoCredentialsError:
        logger.info("Credentials not available")
        return None
    return response

def shorten_url(long_url):
    s = pyshorteners.Shortener()
    short_url = s.tinyurl.short(long_url)
    return short_url

def send_email_sucesso(email, url_download):
    message_body = { 
        "error": False, 
        "email": email,
        "processingLink": url_download
    }

    logger.info(f"Body: {message_body}")
    logger.info(f"Processing completed successfully!")

    return {
        'statusCode': 200,
        'body': message_body
    }

def send_email_error(email):
    message_body = {
        "error": True, 
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