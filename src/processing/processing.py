import boto3
import json
import logging
import os
import zipfile
import shutil
import subprocess

# Inicialização de clientes AWS
s3_client = boto3.client('s3')

# Variáveis
BUCKET_NAME = os.environ["BUCKET_NAME"]
MAX_ZIP_SIZE_MB = 100  # Limite máximo de tamanho do ZIP
TMP_DIR = "/tmp"

# Configuração do logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_response(status_code, message=None, data=None):
    """
    Gera uma resposta formatada.
    """
    logger.info(f"[create_response] status_code={status_code}, message={message}, data={data}")
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
    required_fields = ["video_id", "user_name", "video_url", "email", "frame_rate"]
    missing_fields = [field for field in required_fields if field not in body]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

def check_s3_file_exists(s3_key):
    """
    Verifica se o arquivo existe no S3 antes de tentar o download.
    """
    logger.info(f"[check_s3_file_exists] Checking if {s3_key} exists in S3.")
    try:
        s3_client.head_object(Bucket=BUCKET_NAME, Key=s3_key)
        return True
    except s3_client.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            logger.error(f"[check_s3_file_exists] File {s3_key} does not exist.")
            return False
        else:
            logger.error(f"[check_s3_file_exists] Error checking file existence: {str(e)}")
            raise ValueError("Error checking file existence in S3.")

def download_video_from_s3(s3_key, local_path):
    """
    Faz o download de um arquivo do S3.
    """
    logger.info(f"[download_video_from_s3] Downloading {s3_key} to {local_path}.")
    try:
        s3_client.download_file(BUCKET_NAME, s3_key, local_path)
        logger.info(f"[download_video_from_s3] Download completed: {local_path}")
    except Exception as e:
        logger.error(f"[download_video_from_s3] Error downloading {s3_key}: {str(e)}")
        raise ValueError(f"Failed to download {s3_key} from S3.")

def extract_video_frames(video_path, output_folder, frame_rate):
    """
    Extrai frames de um vídeo com base no frame rate fornecido.
    """
    logger.info(f"[extract_video_frames] Extracting frames from {video_path} to {output_folder}.")
    os.makedirs(output_folder, exist_ok=True)

    command = [
        "/opt/bin/ffmpeg",
        "-i", video_path,
        "-vf", f"fps=1/{frame_rate}",
        os.path.join(output_folder, "frame_%04d.jpg")
    ]

    try:
        subprocess.run(command, check=True)
        logger.info("[extract_video_frames] Frame extraction completed.")
    except subprocess.CalledProcessError as e:
        logger.error(f"[extract_video_frames] Error extracting frames: {str(e)}")
        raise ValueError("Error extracting frames from video.")

def create_zip_file(source_folder, zip_path):
    """
    Cria um arquivo ZIP a partir de um diretório de origem.
    """
    logger.info(f"[create_zip_file] Creating ZIP at {zip_path}.")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_folder):
            for file in files:
                zipf.write(os.path.join(root, file), file)
    logger.info("[create_zip_file] ZIP created successfully.")

def upload_file_to_s3(s3_key, local_path):
    """
    Faz o upload de um arquivo para o S3.
    """
    logger.info(f"[upload_file_to_s3] Uploading {local_path} to {s3_key}.")
    try:
        s3_client.upload_file(local_path, BUCKET_NAME, s3_key)
        logger.info(f"[upload_file_to_s3] Upload completed: {s3_key}")
    except Exception as e:
        logger.error(f"[upload_file_to_s3] Error uploading {local_path}: {str(e)}")
        raise ValueError(f"Failed to upload {local_path} to S3.")

def generate_presigned_s3_url(s3_key, expiration=3600):
    """
    Gera uma URL pré-assinada para download do arquivo S3.
    """
    logger.info(f"[generate_presigned_s3_url] Generating URL for {s3_key}.")
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=expiration
        )
        logger.info(f"[generate_presigned_s3_url] URL generated: {url}")
        return url
    except Exception as e:
        logger.error(f"[generate_presigned_s3_url] Failed to generate presigned URL: {str(e)}")
        raise ValueError("Failed to generate presigned URL.")

def cleanup_temp_files(file_paths):
    """
    Remove arquivos temporários.
    """
    for file_path in file_paths:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"[cleanup_temp_files] File removed: {file_path}")
            except Exception as e:
                logger.error(f"[cleanup_temp_files] Error removing file {file_path}: {str(e)}")

def cleanup_temp_dirs(dir_paths):
    """
    Remove diretórios temporários.
    """
    for dir_path in dir_paths:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                logger.info(f"[cleanup_temp_dirs] Directory removed: {dir_path}")
            except Exception as e:
                logger.error(f"[cleanup_temp_dirs] Error removing directory {dir_path}: {str(e)}")

def process_video_frames(body):
    """
    Orquestra o processamento de frames do vídeo e gera um arquivo ZIP contendo os frames extraídos.
    """
    logger.info(f"[process_video_frames] Starting processing with body: {body}")

    user_name = body["user_name"]
    email = body["email"]
    video_id = body["video_id"]
    frame_rate = body["frame_rate"]

    if not isinstance(frame_rate, int) or frame_rate <= 0:
        logger.error("[process_video_frames] Invalid frame rate number.")
        raise ValueError("Invalid frame rate number, must be an integer greater than 0")

    video_s3_key = f"videos/{user_name}/{video_id}/upload/{video_id}-source.mp4"
    local_video_path = os.path.join(TMP_DIR, f"{video_id}.mp4")
    frames_output_folder = os.path.join(TMP_DIR, f"{video_id}_frames")
    zip_path = os.path.join(TMP_DIR, f"{video_id}-frames.zip")
    output_zip_key = f"videos/{user_name}/{video_id}/processed/{os.path.basename(zip_path)}"

    try:
        if not check_s3_file_exists(video_s3_key):
            raise ValueError(f"Video file {video_s3_key} does not exist in S3.")

        download_video_from_s3(video_s3_key, local_video_path)
        extract_video_frames(local_video_path, frames_output_folder, frame_rate)
        create_zip_file(frames_output_folder, zip_path)
        upload_file_to_s3(output_zip_key, zip_path)

        return create_response(200, data={"email": email, "frame_url": generate_presigned_s3_url(output_zip_key)})

    finally:
        cleanup_temp_files([local_video_path, zip_path])
        cleanup_temp_dirs([frames_output_folder])

def lambda_handler(event, context):
    """
    Entrada principal da Lambda.
    """
    logger.info(f"[lambda_handler] Event received: {json.dumps(event)}")
    try:
        body = normalize_body(event)
        validate_request(body)
        return process_video_frames(body)
    except ValueError as ve:
        logger.error(f"[lambda_handler] Validation error: {ve}")
        return create_response(400, message=str(ve))
    except Exception as e:
        logger.error(f"[lambda_handler] Unexpected error: {e}")
        return create_response(500, message="An unexpected error occurred. Please try again later.")
