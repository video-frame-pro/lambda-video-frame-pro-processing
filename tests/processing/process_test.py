import json
import os
import unittest
from unittest.mock import patch, MagicMock
import botocore.exceptions
import subprocess  # Corrigindo erro de importação!

# Definir variáveis de ambiente
os.environ["BUCKET_NAME"] = "test-bucket"

from src.processing.processing import (
    lambda_handler,
    process_video_frames,
    download_video_from_s3,
    upload_file_to_s3,
    extract_video_frames,
    create_zip_file,
    check_s3_file_exists,
    generate_presigned_s3_url,
    normalize_body,
    cleanup_temp_files,
    cleanup_temp_dirs, validate_request, TMP_DIR
)

class TestLambdaProcessing(unittest.TestCase):

    ## 🔹 TESTES PARA `normalize_body(event)`
    def test_normalize_body_dict(self):
        """ Testa se a função aceita um dicionário como corpo. """
        event = {"body": {"video_id": "123"}}
        body = normalize_body(event)
        self.assertEqual(body, {"video_id": "123"})

    def test_normalize_body_invalid(self):
        """ Testa erro ao passar um corpo inválido. """
        event = {"body": None}
        with self.assertRaises(ValueError):
            normalize_body(event)

    ## 🔹 TESTES PARA `check_s3_file_exists(s3_key)`
    @patch("src.processing.processing.s3_client.head_object")
    def test_check_s3_file_exists(self, mock_head):
        """ Testa se o arquivo existe no S3. """
        mock_head.return_value = True
        self.assertTrue(check_s3_file_exists("test/video.mp4"))

    @patch("src.processing.processing.s3_client.head_object")
    def test_check_s3_file_not_found(self, mock_head):
        """ Testa erro 404 (arquivo não encontrado no S3). """
        mock_head.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "404", "Message": "Not Found"}}, "HeadObject"
        )
        self.assertFalse(check_s3_file_exists("test/video.mp4"))

    @patch("src.processing.processing.s3_client.head_object")
    def test_check_s3_file_forbidden(self, mock_head):
        """ Testa erro 403 (acesso negado no S3). """
        mock_head.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "403", "Message": "Forbidden"}}, "HeadObject"
        )
        with self.assertRaises(ValueError):
            check_s3_file_exists("test/video.mp4")

    ## 🔹 TESTES PARA `download_video_from_s3(s3_key, local_path)`
    @patch("src.processing.processing.s3_client.download_file")
    def test_download_video_from_s3_success(self, mock_download):
        """ Testa o download do vídeo do S3. """
        download_video_from_s3("test/video.mp4", "/tmp/video.mp4")
        mock_download.assert_called_once()

    @patch("src.processing.processing.s3_client.download_file")
    def test_download_video_from_s3_error(self, mock_download):
        """ Testa erro ao baixar arquivo do S3. """
        mock_download.side_effect = Exception("Download Error")
        with self.assertRaises(ValueError):
            download_video_from_s3("test/video.mp4", "/tmp/video.mp4")

    ## 🔹 TESTES PARA `extract_video_frames(video_path, output_folder, frame_rate)`
    @patch("src.processing.processing.subprocess.run")
    def test_extract_video_frames_success(self, mock_subprocess):
        """ Testa a extração de frames do vídeo. """
        extract_video_frames("/tmp/video.mp4", "/tmp/frames", 10)
        mock_subprocess.assert_called_once()

    @patch("src.processing.processing.subprocess.run")
    def test_extract_video_frames_error(self, mock_subprocess):
        """ Testa erro ao extrair frames do vídeo. """
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "ffmpeg")
        with self.assertRaises(ValueError):
            extract_video_frames("/tmp/video.mp4", "/tmp/frames", 10)

    ## 🔹 TESTES PARA `upload_file_to_s3(s3_key, local_path)`
    @patch("src.processing.processing.s3_client.upload_file")
    def test_upload_file_to_s3_success(self, mock_upload):
        """ Testa o upload do arquivo para o S3. """
        upload_file_to_s3("test/output.zip", "/tmp/output.zip")
        mock_upload.assert_called_once()

    @patch("src.processing.processing.s3_client.upload_file")
    def test_upload_file_to_s3_error(self, mock_upload):
        """ Testa erro ao subir arquivo para o S3. """
        mock_upload.side_effect = Exception("Upload Error")
        with self.assertRaises(ValueError):
            upload_file_to_s3("test/output.zip", "/tmp/output.zip")

    ## 🔹 TESTES PARA `generate_presigned_s3_url(s3_key)`
    @patch("src.processing.processing.s3_client.generate_presigned_url", return_value="https://example.com/download.zip")
    def test_generate_presigned_s3_url_success(self, mock_generate_url):
        """ Testa a geração de URL pré-assinada do S3. """
        url = generate_presigned_s3_url("test/output.zip")
        self.assertEqual(url, "https://example.com/download.zip")
        mock_generate_url.assert_called_once()

    @patch("src.processing.processing.s3_client.generate_presigned_url")
    def test_generate_presigned_s3_url_error(self, mock_generate_url):
        """ Testa erro ao gerar URL pré-assinada. """
        mock_generate_url.side_effect = Exception("URL Error")
        with self.assertRaises(ValueError):
            generate_presigned_s3_url("test/output.zip")

    ## 🔹 TESTES PARA `process_video_frames(body)`
    def test_process_video_frames_invalid_frame_rate(self):
        """ Testa erro de frame_rate inválido. """
        body = {"video_id": "123", "user_name": "test_user", "email": "user@example.com", "frame_rate": 0}
        with self.assertRaises(ValueError):
            process_video_frames(body)

    def test_normalize_body_valid_dict(self):
        """Teste para corpo da requisição já em formato de dicionário."""
        event = {"body": {"video_id": "123"}}
        self.assertEqual(normalize_body(event), {"video_id": "123"})

    def test_normalize_body_valid_json_string(self):
        """Teste para corpo da requisição como string JSON válida."""
        event = {"body": json.dumps({"video_id": "123"})}
        self.assertEqual(normalize_body(event), {"video_id": "123"})

    def test_normalize_body_invalid_body(self):
        """Teste para erro ao tentar normalizar um corpo inválido."""
        event = {"body": 123}  # Corpo inválido (não é string nem dicionário)
        with self.assertRaises(ValueError) as context:
            normalize_body(event)
        self.assertIn("Request body is missing or invalid.", str(context.exception))


    def test_validate_request_missing_fields(self):
        """Teste para erro de campos obrigatórios ausentes."""
        body = {"frame_rate": 1, "video_id":  "123", "email": "email@gmail.com"}
        with self.assertRaises(ValueError) as context:
            validate_request(body)
        self.assertIn("Missing required fields: user_name", str(context.exception))


    ## 🔹 TESTES PARA `lambda_handler(event, context)`
    @patch("src.processing.processing.process_video_frames")
    def test_lambda_handler_success(self, mock_process):
        """ Testa execução bem-sucedida da Lambda. """
        mock_process.return_value = {"statusCode": 200}
        event = {"body": json.dumps({"video_id": "123", "user_name": "test_user", "video_url": "s3://test-bucket/video.mp4", "email": "user@example.com", "frame_rate": 10})}
        response = lambda_handler(event, {})
        self.assertEqual(response["statusCode"], 200)

    @patch("src.processing.processing.process_video_frames")
    def test_lambda_handler_error(self, mock_process):
        """ Testa erro inesperado na Lambda. """
        mock_process.side_effect = Exception("Unexpected Error")
        event = {"body": json.dumps({"video_id": "123", "user_name": "test_user", "video_url": "s3://test-bucket/video.mp4", "email": "user@example.com", "frame_rate": 10})}
        response = lambda_handler(event, {})
        self.assertEqual(response["statusCode"], 500)


    @patch("src.processing.processing.check_s3_file_exists", return_value=True)
    @patch("src.processing.processing.download_video_from_s3")
    @patch("src.processing.processing.extract_video_frames")
    @patch("src.processing.processing.create_zip_file")
    @patch("src.processing.processing.upload_file_to_s3")
    @patch("src.processing.processing.generate_presigned_s3_url", return_value="https://example.com/download.zip")
    @patch("src.processing.processing.cleanup_temp_files")
    @patch("src.processing.processing.cleanup_temp_dirs")
    def test_process_video_frames_success(
            self,
            mock_cleanup_dirs,
            mock_cleanup_files,
            mock_generate_url,
            mock_upload,
            mock_create_zip,
            mock_extract_frames,
            mock_download,
            mock_check_s3
    ):
        """ Testa o fluxo completo do processamento de vídeo com sucesso. """
        body = {
            "video_id": "123",
            "user_name": "test_user",
            "video_url": "s3://test-bucket/video.mp4",
            "email": "user@example.com",
            "frame_rate": 10
        }

        response = process_video_frames(body)

        expected_local_path = os.path.join(TMP_DIR, "123.mp4")
        expected_frames_path = os.path.join(TMP_DIR, "123_frames")
        expected_zip_path = os.path.join(TMP_DIR, "123-frames.zip")

        # Normalizar caminhos antes da verificação
        mock_check_s3.assert_called_once_with("videos/test_user/123/upload/123-source.mp4")
        mock_download.assert_called_once_with("videos/test_user/123/upload/123-source.mp4", expected_local_path)
        mock_extract_frames.assert_called_once_with(expected_local_path, expected_frames_path, 10)
        mock_create_zip.assert_called_once_with(expected_frames_path, expected_zip_path)
        mock_upload.assert_called_once_with("videos/test_user/123/processed/123-frames.zip", expected_zip_path)
        mock_generate_url.assert_called_once_with("videos/test_user/123/processed/123-frames.zip")

        self.assertEqual(response["statusCode"], 200)
        self.assertIn("frame_url", response["body"])
        self.assertEqual(response["body"]["frame_url"], "https://example.com/download.zip")

        # Verifica se os arquivos temporários foram removidos
        mock_cleanup_files.assert_called_once_with([expected_local_path, expected_zip_path])
        mock_cleanup_dirs.assert_called_once_with([expected_frames_path])


    @patch("src.processing.processing.check_s3_file_exists", return_value=False)
    def test_process_video_frames_s3_file_not_found(self, mock_check_s3):
        """ Testa erro quando o vídeo não existe no S3. """
        body = {
            "video_id": "123",
            "user_name": "test_user",
            "video_url": "s3://test-bucket/video.mp4",
            "email": "user@example.com",
            "frame_rate": 10
        }

        with self.assertRaises(ValueError) as context:
            process_video_frames(body)

        self.assertIn("Video file videos/test_user/123/upload/123-source.mp4 does not exist in S3.", str(context.exception))
        mock_check_s3.assert_called_once_with("videos/test_user/123/upload/123-source.mp4")
