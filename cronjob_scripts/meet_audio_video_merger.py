from django.conf import settings
from EasyAssistApp.utils_video_audio_merge import *
from EasyAssistApp.models import CobrowsingFileAccessManagement
from EasyAssistApp.models import CobrowseVideoAuditTrail
from DeveloperConsoleApp.utils import *
from DeveloperConsoleApp.utils_aws_s3 import *
import json
import sys
from datetime import datetime
import pytz

cobrowse_video_objs = CobrowseVideoAuditTrail.objects.filter(
    is_meeting_ended=True, is_merging_done=False).order_by('pk')

try:
    for cobrowse_video_obj in cobrowse_video_objs:
        if cobrowse_video_obj.meeting_recording == '' or cobrowse_video_obj.meeting_recording == 'None' or cobrowse_video_obj.meeting_recording == None:
            cobrowse_video_obj.is_merging_done = True
            cobrowse_video_obj.save()
            continue

        search_name = str(cobrowse_video_obj.cobrowse_video.meeting_id)
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
                s3_bucket_upload_file_by_file_path(file_path[1:], file_path)

            file_access_management_obj = CobrowsingFileAccessManagement.objects.filter(
                file_path=file_path, is_public=False)
            if not file_access_management_obj:
                file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                    file_path=file_path, is_public=False, access_token=cobrowse_video_obj.cobrowse_video.agent.get_access_token_obj())
            cobrowse_video_obj.merged_filepath = str(
                file_access_management_obj.key)
            cobrowse_video_obj.is_merging_done = True
            cobrowse_video_obj.save()
            continue

        audio_path = json.loads(
            cobrowse_video_obj.client_audio_recording)["items"]

        if audio_path == []:
            try:
                cobrowse_video_obj.merged_filepath = cobrowse_video_obj.meeting_recording
                cobrowse_video_obj.is_merging_done = True
                cobrowse_video_obj.save()

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print(str(exc_tb.tb_lineno))
                print(e)

            continue
        else:
            file_access_management_obj = CobrowsingFileAccessManagement.objects.get(
                key=cobrowse_video_obj.meeting_recording)
            video_file_path = file_access_management_obj.file_path
            
            audio_paths = []
            delays = []

            for item in audio_path:
                audio_file_path = item["path"]

                audio_time_stamp = item["time_stamp"]
                video_time_stamp = cobrowse_video_obj.agent_recording_start_time.astimezone(
                    pytz.timezone('Asia/Kolkata'))
                video_time_stamp = video_time_stamp.time()
                audio_time_stamp = datetime.strptime(
                    audio_time_stamp, '%H:%M:%S')

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

                audio_paths.append(audio_file_path)
                delays.append(time_diff)

            filepath = audio_video_merger(
                video_file_path, audio_paths, delays, "merged_" + video_file_path.split("/")[-1])

            if filepath != "None":
                cobrowse_video_obj.merged_filepath = filepath
                cobrowse_video_obj.is_merging_done = True
                cobrowse_video_obj.save()

except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print(str(exc_tb.tb_lineno))
    print(e)
