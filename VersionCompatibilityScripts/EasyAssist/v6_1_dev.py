from EasyAssistApp.models import *


def update_access_token_in_support_documents():
    for support_doc in SupportDocument.objects.all():
        access_token_obj = support_doc.agent.get_access_token_obj()
        try:
            file_access_management_obj = CobrowsingFileAccessManagement.objects.get(
                key=support_doc.file_access_management_key)
            file_access_management_obj.is_public = False
            file_access_management_obj.access_token = access_token_obj
            file_access_management_obj.save()
        except Exception as e:
            logger.error("Error in update_access_token_in_support_documents: %s", str(
                e), extra={'AppName': 'EasyAssist'})


def update_access_token_for_screenshots():

    cobrowse_ios = CobrowsingSessionMetaData.objects.all().values('cobrowse_io').distinct()
    for cobrowse_io in cobrowse_ios:
        try:
            cobrowse_io_obj = CobrowseIO.objects.get(
                session_id=cobrowse_io["cobrowse_io"])
            cobrowse_meta_objs = CobrowsingSessionMetaData.objects.filter(
                cobrowse_io=cobrowse_io_obj)
            access_token_obj = cobrowse_io_obj.agent.get_access_token_obj()

            for cobrowse_meta_obj in cobrowse_meta_objs:
                file_path = cobrowse_meta_obj.content
                file_name = file_path.split("/")[-1]
                file_access_management_objs = CobrowsingFileAccessManagement.objects.filter(
                    file_path="/" + file_path, original_file_name=file_name)

                for file_access_management_obj in file_access_management_objs:
                    file_access_management_obj.is_public = False
                    file_access_management_obj.access_token = access_token_obj
                    file_access_management_obj.save()
        except Exception as e:
            logger.error("Error in update_access_token_for_screenshots: %s", str(
                e), extra={'AppName': 'EasyAssist'})


def update_access_token_in_chat_attachments():
    attachments = CobrowseChatHistory.objects.filter(
        attachment__isnull=False)

    for attachment in attachments:
        try:
            access_token_obj = None
            access_token_obj = attachment.cobrowse_io.agent.get_access_token_obj()
            file_access_management_key = attachment.attachment.split('/')[-2]
            file_access_management_obj = CobrowsingFileAccessManagement.objects.get(
                key=file_access_management_key)
            file_access_management_obj.access_token = access_token_obj
            file_access_management_obj.save()
        except Exception as e:
            logger.error("Error in update_access_token_in_chat_attachments: %s", str(
                e), extra={'AppName': 'EasyAssist'})


def update_access_token_for_screen_recording():
    for access_token_obj in CobrowseAccessToken.objects.all():
        try:
            screen_recording_objs = CobrowseScreenRecordingAuditTrail.objects.filter(
                cobrowse_io__is_test=False, cobrowse_io__access_token=access_token_obj, recording_started__date__gte=access_token_obj.go_live_date)

            for screen_recording_obj in screen_recording_objs:
                file_access_management_key = screen_recording_obj.recorded_file
                file_access_management_obj = CobrowsingFileAccessManagement.objects.filter(
                    key=file_access_management_key).first()
                if file_access_management_obj:
                    file_access_management_obj.access_token = access_token_obj
                    file_access_management_obj.save()
        except Exception as e:
            logger.error("Error in update_access_token_for_screen_recording: %s", str(
                e), extra={'AppName': 'EasyAssist'})


def update_access_token_for_video_chat_attachments():
    for cobrowse_video_obj in CobrowseVideoConferencing.objects.all():
        try:
            video_audit_trails = CobrowseVideoAuditTrail.objects.filter(
                cobrowse_video=cobrowse_video_obj, message_history__isnull=False)
            access_token_obj = cobrowse_video_obj.agent.get_access_token_obj()

            for video_audit_trail in video_audit_trails:
                message_history = eval(video_audit_trail.message_history)
                for message in message_history:
                    packet = json.loads(message)
                    if 'download-file/' in packet['message']:
                        file_access_management_key = packet['message'].split(
                            'download-file/')[1].split('download')[0].strip()
                        file_access_management_obj = CobrowsingFileAccessManagement.objects.get(
                            key=file_access_management_key)
                        file_access_management_obj.access_token = access_token_obj
                        file_access_management_obj.save()
        except Exception as e:
            logger.error("Error in update_access_token_for_video_chat_attachments: %s", str(
                e), extra={'AppName': 'EasyAssist'})


def update_access_token_for_chrome_extension_files():
    for chrome_extension_obj in ChromeExtensionDetails.objects.all():
        try:
            file_access_management_key = chrome_extension_obj.extension_path.split(
                'download-file/')[1].strip()
            file_access_management_obj = CobrowsingFileAccessManagement.objects.get(
                key=file_access_management_key)
            file_access_management_obj.access_token = chrome_extension_obj.access_token
            file_access_management_obj.save()
        except Exception as e:
            logger.error("Error in update_access_token_for_chrome_extension_files: %s", str(
                e), extra={'AppName': 'EasyAssist'})


print("Running update_access_token_in_support_documents...\n")

update_access_token_in_support_documents()

print("Running update_access_token_for_screenshots...\n")

update_access_token_for_screenshots()

print("Running update_access_token_in_chat_attachments...\n")

update_access_token_in_chat_attachments()

print("Running update_access_token_for_screen_recording...\n")

update_access_token_for_screen_recording()

print("Running update_access_token_for_video_chat_attachments...\n")

update_access_token_for_video_chat_attachments()

print("Running update_access_token_for_chrome_extension_files...\n")

update_access_token_for_chrome_extension_files()
