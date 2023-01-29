from django.conf import settings
from django.utils import timezone

from DeveloperConsoleApp.models import *
from DeveloperConsoleApp.utils import get_developer_console_settings

import boto3
from botocore.exceptions import ClientError
from uuid import uuid4
import logging
import sys

logger = logging.getLogger(__name__)


def s3_bucket_upload_file_by_file_path(file_path, original_file_name):
    """Upload a file to an S3 bucket

    :param file_path: Path of the file to upload
    :param bucket: Bucket to upload to
    :return: CentralisedFileAccessManagement key if file was uploaded, else None
    """

    try:
        console_config_obj = get_developer_console_settings()
        aws_access_key_id = console_config_obj.aws_access_key_id
        aws_secret_access_key = console_config_obj.aws_secret_access_key
        aws_s3_bucket_name = console_config_obj.aws_s3_bucket_name

        # S3 object_name
        aws_s3_object_name = uuid4().hex

        # Upload the file
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key)

        s3_client.upload_file(
            file_path, aws_s3_bucket_name, aws_s3_object_name)

        file_access_management_obj = CentralisedFileAccessManagement.objects.create(
            file_path=file_path,
            original_file_name=original_file_name,
            aws_s3_object_name=aws_s3_object_name)

        return str(file_access_management_obj.key)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error s3_bucket_upload_file_by_file_path %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})

        return None


def s3_bucket_upload_file_by_content(content, original_file_name):
    """Upload a file to an S3 bucket

    :param file_path: Path of the file to upload
    :param bucket: Bucket to upload to
    :return: CentralisedFileAccessManagement key if file was uploaded, else None
    """

    try:
        console_config_obj = get_developer_console_settings()
        aws_access_key_id = console_config_obj.aws_access_key_id
        aws_secret_access_key = console_config_obj.aws_secret_access_key
        aws_s3_bucket_name = console_config_obj.aws_s3_bucket_name

        # S3 object_name
        aws_s3_object_name = uuid4().hex

        # Upload the file
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key)
            
        s3_client.upload_fileobj(
            content, aws_s3_bucket_name, aws_s3_object_name)
        
        file_access_management_obj = CentralisedFileAccessManagement.objects.create(
            original_file_name=original_file_name,
            aws_s3_object_name=aws_s3_object_name)

        return str(file_access_management_obj.key)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error s3_bucket_upload_file_by_content %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})

        return None


def s3_bucket_download_file(file_access_management_id, dest_file_path, extension):
    try:
        console_config_obj = get_developer_console_settings()
        aws_access_key_id = console_config_obj.aws_access_key_id
        aws_secret_access_key = console_config_obj.aws_secret_access_key
        aws_s3_bucket_name = console_config_obj.aws_s3_bucket_name

        file_access_management_obj = CentralisedFileAccessManagement.objects.get(
            key=file_access_management_id)
        aws_s3_object_name = file_access_management_obj.aws_s3_object_name

        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key)

        # file_path = file_access_management_obj.file_path

        s3_client.download_file(
            aws_s3_bucket_name, aws_s3_object_name, settings.SECURE_MEDIA_ROOT + dest_file_path + aws_s3_object_name + "." + extension)
        
        return settings.SECURE_MEDIA_ROOT + dest_file_path + aws_s3_object_name + "." + extension
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error s3_bucket_download_file %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})
