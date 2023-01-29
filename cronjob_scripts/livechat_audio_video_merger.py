from django.conf import settings
from LiveChatApp.utils_voip import audio_merger, audio_video_merger
from LiveChatApp.models import LiveChatFileAccessManagement, LiveChatVoIPData
from DeveloperConsoleApp.utils import *
from DeveloperConsoleApp.utils_aws_s3 import *
import json
import sys
import logging
from datetime import datetime
import pytz
import os

logger = logging.getLogger(__name__)


def cronjob():
    voip_objs = LiveChatVoIPData.objects.filter(
        is_completed=True, is_merging_done=False).order_by('pk')

    try:
        for voip_obj in voip_objs:
            if voip_obj.call_type == 'pip':
                voip_obj.is_merging_done = True
                voip_obj.save()

            search_name = str(voip_obj.meeting_id)
            file_name = ""
            folder_name = ""

            with os.scandir(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/cognovid/nfs_recordings/') as entries:
                for entry in entries:
                    try:
                        files_inside = os.listdir(entry)
                        folder_name = entry.name
                        for file_path_name in files_inside:
                            if search_name in file_path_name:
                                file_name = file_path_name
                                break
                        if file_name:
                            break
                    except Exception:
                        pass

            if file_name:
                file_path = '/secured_files/EasyAssistApp/cognovid/nfs_recordings/' + \
                    folder_name + "/" + file_name

                if get_save_in_s3_bucket_status():
                    s3_bucket_upload_file_by_file_path(file_path[1:], file_name)

                file_access_management_obj = LiveChatFileAccessManagement.objects.filter(
                    file_path=file_path, is_public=False)

                if not file_access_management_obj:
                    file_access_management_obj = LiveChatFileAccessManagement.objects.create(
                        file_path=file_path, is_public=False)

                voip_obj.merged_file_path = str(file_access_management_obj.key)
                voip_obj.is_merging_done = True
                voip_obj.save()
                continue
            
            try:
                audio_path = json.loads(
                    voip_obj.call_recording)["items"]
            except:
                continue

            if audio_path == []:
                try:
                    if voip_obj.call_type == 'video_call':
                        voip_obj.merged_file_path = voip_obj.video_recording
                    voip_obj.is_merging_done = True
                    voip_obj.save()

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    print(str(exc_tb.tb_lineno))
                    print(e)

                continue
            else:

                video_file_path = None
                if voip_obj.call_type == 'video_call':
                    file_access_management_obj = LiveChatFileAccessManagement.objects.filter(
                        key=voip_obj.video_recording)
                    
                    if file_access_management_obj:
                        video_file_path = file_access_management_obj.first().file_path
            
                audio_paths = []
                delays = []

                for item in audio_path:
                    audio_file_path = item["path"]

                    audio_time_stamp = item["time_stamp"]
                    audio_time_stamp = datetime.strptime(
                        audio_time_stamp, '%H:%M:%S')

                    audio_paths.append(audio_file_path)

                    if video_file_path:
                        video_time_stamp = voip_obj.agent_recording_start_time.astimezone(
                            pytz.timezone('Asia/Kolkata'))
                        video_time_stamp = video_time_stamp.time()

                        audio_total_second = (audio_time_stamp.hour * 60 * 60) + \
                            (audio_time_stamp.minute * 60) + audio_time_stamp.second
                        video_total_second = (video_time_stamp.hour * 60 * 60) + \
                            (video_time_stamp.minute * 60) + video_time_stamp.second
                        time_diff = abs(video_total_second - audio_total_second)

                        if int(time_diff) > 0:
                            temp_time_diff = int(time_diff)
                            if int(temp_time_diff) >= 0:
                                time_diff = int(temp_time_diff)

                        time_diff = time_diff * 1000

                        delays.append(time_diff)

                if video_file_path:
                    filepath = audio_video_merger(video_file_path, audio_paths, delays, "merged_" + str(voip_obj.meeting_id) + '.webm')
                else:
                    filepath = audio_merger(
                        audio_paths, "merged_" + str(voip_obj.meeting_id) + '.webm')

                if filepath != "None":
                    voip_obj.merged_file_path = filepath
                    voip_obj.is_merging_done = True
                    voip_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In livechat_audio_merger: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'LiveChat'})
