import json
import os
import unittest
from unittest.mock import MagicMock, patch, mock_open

os.environ['BUCKET_NAME'] = 'bucket_name'

from src.processing.processing import (create_zip, download_from_s3,
                                       extract_frames, generate_url,
                                       lambda_handler, process_frames,
                                       send_email_error, send_email_sucesso, 
                                       upload_to_s3, normalize_body, 
                                       validate_request, create_response)

@patch('boto3.client')
class TestLambdaFunction(unittest.TestCase):

    def test_lambda_handler_exception(self, mock_boto_client):
        mock_boto_client.return_value = MagicMock()
        
        event = {
            'body': {
                "video_url": "video_teste.mp4",
                "user_name": "example",
                "email": "example@example.com",
                "frame_rate": 10
            }
        }
        context = {}
        response = lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 500)

    # def test_lambda_handler_missing_fields(self, mock_boto_client, mock_shortener):
    #     mock_boto_client.return_value = MagicMock()
    #     mock_shortener.return_value = MagicMock()
        
    #     event = {
    #         'body': {
    #             "video_url": "video_teste.mp4",
    #             "user_name": "example",
    #             "email": "example@example.com"
    #         }
    #     }
    #     context = {}
    #     response = lambda_handler(event, context)
    #     self.assertEqual(response['statusCode'], 400)

    # def test_normalize_body_string(self):
    #     event = {
    #         'body': '{"video_url": "video_teste.mp4", "user_name": "example", "email": "example@example.com", "frame_rate": 10}'
    #     }
    #     body = normalize_body(event)
    #     self.assertEqual(body['video_url'], "video_teste.mp4")

    # def test_normalize_body_dict(self):
    #     event = {
    #         'body': {
    #             "video_url": "video_teste.mp4",
    #             "user_name": "example",
    #             "email": "example@example.com",
    #             "frame_rate": 10
    #         }
    #     }
    #     body = normalize_body(event)
    #     self.assertEqual(body['video_url'], "video_teste.mp4")

    # def test_validate_request_success(self):
    #     body = {
    #         "video_url": "video_teste.mp4",
    #         "user_name": "example",
    #         "email": "example@example.com",
    #         "frame_rate": 10
    #     }
    #     validate_request(body)

    # def test_validate_request_missing_fields(self):
    #     body = {
    #         "video_url": "video_teste.mp4",
    #         "user_name": "example",
    #         "email": "example@example.com"
    #     }
    #     with self.assertRaises(ValueError):
    #         validate_request(body)

    # def test_create_response(self):
    #     response = create_response(200, message="Success", data={"key": "value"})
    #     self.assertEqual(response['statusCode'], 200)
    #     self.assertEqual(response['body']['message'], "Success")
    #     self.assertEqual(response['body']['key'], "value")

    # @patch('os.makedirs')
    # @patch('os.path.exists')
    # @patch('os.system')
    # def test_extract_frames(self, mock_system, mock_exists, mock_makedirs):
    #     mock_exists.return_value = False
    #     extract_frames("/tmp/video_teste.mp4", "/tmp/frames", 10)
    #     mock_makedirs.assert_called_once_with("/tmp/frames")
    #     mock_system.assert_called_once_with("/opt/bin/ffmpeg.exe -i /tmp/video_teste.mp4 -vf fps=1/10 /tmp/frames/frame_%04d.jpg")

    # @patch('zipfile.ZipFile')
    # @patch('os.walk')
    # def test_create_zip(self, mock_walk, mock_zipfile):
    #     mock_walk.return_value = [
    #         ('/tmp/frames', [], ['frame_0001.jpg', 'frame_0002.jpg'])
    #     ]
    #     create_zip("/tmp/frames", "/tmp/frames.zip")
    #     mock_zipfile.assert_called_once_with("/tmp/frames.zip", 'w')

    # @patch('boto3.client')
    # def test_download_from_s3(self, mock_boto_client):
    #     mock_s3 = MagicMock()
    #     mock_boto_client.return_value = mock_s3
    #     download_from_s3("bucket_name", "video_teste.mp4", "/tmp/video_teste.mp4")
    #     mock_s3.download_file.assert_called_once_with("bucket_name", "video_teste.mp4", "/tmp/video_teste.mp4")

    # @patch('boto3.client')
    # def test_upload_to_s3(self, mock_boto_client):
    #     mock_s3 = MagicMock()
    #     mock_boto_client.return_value = mock_s3
    #     upload_to_s3("bucket_name", "output_zip_key", "/tmp/frames.zip")
    #     mock_s3.upload_file.assert_called_once_with("/tmp/frames.zip", "bucket_name", "output_zip_key")

    # @patch('boto3.client')
    # def test_generate_url(self, mock_boto_client):
    #     mock_s3 = MagicMock()
    #     mock_boto_client.return_value = mock_s3
    #     mock_s3.generate_presigned_url.return_value = "http://example.com"
    #     url = generate_url("bucket_name", "video_teste.mp4")
    #     self.assertEqual(url, "http://example.com")

    # @patch('pyshorteners.Shortener')
    # def test_shorten_url(self, mock_shortener):
    #     mock_shortener.return_value.tinyurl.short.return_value = "http://tinyurl.com"
    #     short_url = shorten_url("http://example.com")
    #     self.assertEqual(short_url, "http://tinyurl.com")

    # def test_send_email_sucesso(self):
    #     response = send_email_sucesso("example@example.com", "http://example.com")
    #     self.assertEqual(response['statusCode'], 200)
    #     self.assertEqual(response['body']['email'], "example@example.com")
    #     self.assertEqual(response['body']['frame_url'], "http://example.com")

    # def test_send_email_error(self):
    #     response = send_email_error("example@example.com")
    #     self.assertEqual(response['statusCode'], 500)
    #     self.assertEqual(response['body']['email'], "example@example.com")

if __name__ == '__main__':
    unittest.main()