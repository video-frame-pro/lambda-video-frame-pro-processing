import json
import unittest
from unittest.mock import MagicMock, patch

from src.processing.processing import (create_zip, download_from_s3,
                                       extract_frames, generate_url,
                                       lambda_handler, process_frames,
                                       send_email_error, send_email_sucesso, 
                                       shorten_url, upload_to_s3)


# @patch('boto3.client')
# @patch('pyshorteners.Shortener')
# class TestLambdaFunction(unittest.TestCase):

#     @patch('src.processing.processing.process_message')
#     def test_lambda_handler_success(self, mock_process_message, mock_boto_client, mock_shortener):
#         mock_process_message.return_value = {'statusCode': 200}
#         mock_boto_client.return_value = MagicMock()
#         mock_shortener.return_value = MagicMock()
        
#         event = {
#             'Records': [{
#                 'body': json.dumps({
#                     "videoId": "video_teste.mp4",
#                     "userName": "example",
#                     "email": "example@example.com",
#                     "frameRate": 10
#                 }),
#                 'receiptHandle': 'mock_receipt_handle'
#             }]
#         }
#         context = {}
#         lambda_handler(event, context)

#     @patch('src.processing.processing.process_message')
#     @patch('src.processing.processing.send_email_error')
#     def test_lambda_handler_error(self, send_email_error, mock_process_message, mock_boto_client, mock_shortener):
#         mock_process_message.return_value = {'statusCode': 500}
#         mock_boto_client.return_value = MagicMock()
#         mock_shortener.return_value = MagicMock()
        
#         event = {
#             'Records': [{
#                 'body': {
#                     "videoId": "video_teste.mp4",
#                     "userName": "example",
#                     "email": "example@example.com",
#                     "frameRate": 10
#                 },
#                 'receiptHandle': 'mock_receipt_handle'
#             }]
#         }
#         context = {}
#         lambda_handler(event, context)

if __name__ == '__main__':
    unittest.main()