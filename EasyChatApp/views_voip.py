import sys
import logging
from LiveChatApp.models import LiveChatConfig, LiveChatVoIPData
from django.shortcuts import (render, HttpResponse,
                              HttpResponseRedirect)

logger = logging.getLogger(__name__)


def CustomerVoiceMeeting(request):  # noqa: N802
    try:
        meeting_id = request.GET['meeting_id']
        session_id = request.GET['session_id']

        meeting_obj = LiveChatVoIPData.objects.filter(meeting_id=meeting_id)

        if meeting_obj and not meeting_obj[0].is_completed:
            meeting_obj = meeting_obj.first()
            customer_obj = meeting_obj.customer
            bot_obj = customer_obj.bot

            config_obj = LiveChatConfig.objects.get(bot=bot_obj)
            meeting_domain = config_obj.meeting_domain

            if str(customer_obj.session_id) == session_id and not customer_obj.is_session_exp:
                display_name = customer_obj.username

                return render(request, 'EasyChatApp/voice_meeting.html', {
                    "meeting_id": meeting_id,
                    "session_id": session_id,
                    "display_name": display_name,
                    "meeting_domain": meeting_domain,
                })

        return render(request, "EasyChatApp/meeting_end.html", {})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("CustomerVoiceMeeting ! %s %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return render(request, 'EasyChatApp/error_500.html')


def CustomerVoIPMeetingEnded(request):
    try:
        return render(request, "EasyChatApp/meeting_end.html", {})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CustomerVoIPMeetingEnded %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return HttpResponse(status=401)
