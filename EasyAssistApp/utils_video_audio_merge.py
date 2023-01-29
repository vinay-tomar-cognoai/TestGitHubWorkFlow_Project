import sys
import ffmpeg
import logging
from django.conf import settings
import os
from EasyAssistApp.models import CobrowsingFileAccessManagement
from DeveloperConsoleApp.utils import *
from DeveloperConsoleApp.utils_aws_s3 import *

logger = logging.getLogger(__name__)


def audio_video_merger(video_path, audio_paths, delays, output_filename):
    logger.info("Inside merger...", extra={"AppName": "EasyAssist"})
    try:
        input_video = ffmpeg.input(video_path[1:])

        audio_files_list = [input_video.audio]
        merged_audio = input_video.audio

        video_stream = ffmpeg.probe(video_path[1:], select_streams='v')

        if len(video_stream["streams"]) == 0:
            for index in range(len(audio_paths)):
                added_audio = ffmpeg.input(
                    audio_paths[index][1:]).audio.filter('adelay', str(delays[index]))
                audio_files_list.append(added_audio)
                merged_audio = ffmpeg.filter([merged_audio, added_audio], 'amix')

            merged_file_path = "secured_files/EasyAssistApp/merged_files/"
            if not os.path.exists(merged_file_path):
                os.makedirs(merged_file_path)

            out, err = (
                ffmpeg
                .filter(audio_files_list, 'amix')
                .output(merged_file_path + output_filename)
                .run(overwrite_output=True)
            )
        else:
            for index in range(len(audio_paths)):
                added_audio = ffmpeg.input(
                    audio_paths[index][1:]).audio.filter('adelay', str(delays[index]))
                audio_files_list.append(added_audio)
                merged_audio = ffmpeg.filter([merged_audio, added_audio], 'amix')

            merged_file_path = "secured_files/EasyAssistApp/merged_files/"
            if not os.path.exists(merged_file_path):
                os.makedirs(merged_file_path)

            out, err = (
                ffmpeg
                .concat(input_video, merged_audio, v=1, a=1)
                .output(merged_file_path + output_filename)
                .run(overwrite_output=True)
            )
        logger.info("Merging done...", extra={"AppName": "EasyAssist"})
        
        if get_save_in_s3_bucket_status():
            s3_bucket_upload_file_by_file_path(merged_file_path + output_filename, output_filename)
            
        merged_file_path = "/" + merged_file_path + output_filename
        file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
            file_path=merged_file_path, is_public=False)

        src = str(file_access_management_obj.key)

        return src
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In audio_video_merger: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssist'})
        return "None"
