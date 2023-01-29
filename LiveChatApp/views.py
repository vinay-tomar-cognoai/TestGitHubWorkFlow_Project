import os
import sys
import json
import uuid
from django import conf
import xlrd
import pytz
import random
import logging
import mimetypes
import urllib.parse

# Django REST framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, authentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

# Django imports
from django.db.models import Q
from django.http import FileResponse
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse, HttpResponseRedirect

from EasyChat import settings
from EasyChatApp.utils import *
from LiveChatApp.utils import *
from LiveChatApp.utils_calendar import *
from LiveChatApp.models import *
from LiveChatApp.constants import *
from LiveChatApp.constants_processors import *
from EasyChatApp.static_dummy_data import *
from LiveChatApp.views_calender import *
from LiveChatApp.views_email_profile import *
from EasyChatApp.utils_google_buisness_messages import *
from EasyChatApp.utils_facebook import send_facebook_message, send_facebook_livechat_agent_response
from LiveChatApp.views_analytics import *
from LiveChatApp.views_internal_chat import *
from LiveChatApp.views_agent import *
from LiveChatApp.views_voip import *
from LiveChatApp.views_integrations import *
from LiveChatApp.views_translation import *
from LiveChatApp.views_ticket import *
from LiveChatApp.views_cobrowsing import *
from LiveChatApp.views_followup_leads import *
from LiveChatApp.views_chat_escalation import *
from LiveChatApp.views_email import *
from LiveChatApp.views_ameyo_fusion import *
from LiveChatApp.utils_custom_encryption import *
from LiveChatApp.utils_validation import LiveChatFileValidation
from LiveChatApp.utils_translation import get_translated_text
from LiveChatApp.utils_analytics import get_agents_availibility_analytics_filter
from LiveChatApp.utils_email import get_email_config_obj, check_if_email_chat_to_be_resolved
from EasyChatApp.models import SecuredLogin, UserSession, Profile, LiveChatBotChannelWebhook, Channel
from DeveloperConsoleApp.utils import get_developer_console_settings, get_developer_console_livechat_settings
from LiveChatApp.assign_task import assign_agent_via_scheduler
import datetime

User = get_user_model()
IST = pytz.timezone("Asia/Kolkata")

# Logger
logger = logging.getLogger(__name__)

ensure_element_tree(xlrd)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


def HomePage(request):
    from pytz import timezone
    ist = timezone('Asia/Kolkata')
    request.session["EASYCHAT_VERSION"] = settings.EASYCHAT_VERSION
    request.session[
        "EASYCHAT_DATE_OF_RELEASE"] = settings.EASYCHAT_DATE_OF_RELEASE
    try:
        if request.user.is_authenticated:
            user_obj = None
            try:
                user_obj = LiveChatUser.objects.get(user=User.objects.get(
                    username=str(request.user.username)), is_deleted=False)
                admin_obj = get_admin_from_active_agent(user_obj, LiveChatUser)

                is_video_meeting_enabled = LiveChatAdminConfig.objects.filter(
                    admin=admin_obj)[0].is_video_meeting_enabled
                request.session[
                    "is_video_meeting_enabled"] = is_video_meeting_enabled

                build_default_calendar(admin_obj, LiveChatCalender)

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("User Does Not Exist: %s at %s",
                             e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

            if user_obj == None:
                return HttpResponseRedirect(CHAT_LOGIN_PATH)

            # save_audit_trail_data("7", user_obj, LiveChatAuditTrail)

            is_user_agent = user_obj.status == "3"
            if not is_user_agent:
                check_and_add_admin_config(user_obj, LiveChatAdminConfig)
                return HttpResponseRedirect("/livechat/chat-history/")
            else:
                livechat_categories = LiveChatCategory.objects.all()
                admin_config = get_admin_config(
                    user_obj, LiveChatAdminConfig, LiveChatUser)

                livechat_session_obj = LiveChatSessionManagement.objects.filter(
                    user=user_obj, session_completed=False)[0]

                time_marked_stop_interaction = livechat_session_obj.time_marked_stop_interaction.astimezone(
                    ist)

                assigned_customer_count = LiveChatCustomer.objects.filter(
                    is_session_exp=False, agent_id=user_obj).count()

                canned_response_list = get_canned_response_for_current_agent(
                    user_obj, CannedResponse, LiveChatUser)
                canned_response = []
                for item in canned_response_list:
                    canned_response.append({
                        "key": item.keyword,
                        "value": item.response,
                        "status": item.status
                    })

                blacklisted_keyword = get_blacklisted_keyword_for_current_agent(
                    user_obj, LiveChatBlackListKeyword, LiveChatUser)
                blacklisted_keyword = list(
                    blacklisted_keyword.values_list('word', flat=True))

                customer_blacklisted_keyword = get_customer_blacklisted_keywords(
                    user_obj, LiveChatBlackListKeyword, LiveChatUser)
                customer_blacklisted_keyword = list(
                    customer_blacklisted_keyword.values_list('word', flat=True))
                customer_blacklisted_keyword = customer_blacklisted_keyword + DEFAULT_CUSTOMER_BLACKLISTED_KEYWORDS

                bot_obj = user_obj.bots.filter(is_deleted=False)[0]
                config_obj = LiveChatConfig.objects.get(bot=bot_obj)

                # get pending guest_agents
                livechat_customer_sessions = LiveChatCustomer.objects.filter(
                    guest_agents=user_obj, is_session_exp=False)
                current_guest_sessions = []
                for livechat_customer_session in livechat_customer_sessions:
                    session_status = json.loads(
                        livechat_customer_session.guest_session_status)
                    if session_status[user_obj.user.username] == "onhold":
                        current_guest_sessions.append(
                            str(livechat_customer_session.session_id))

                # voip info
                meeting_objs = LiveChatVoIPData.objects.filter(
                    agent=user_obj, is_completed=False, is_rejected=False).order_by('-pk')

                is_meeting_started = False
                is_meeting_end_required = False
                meeting_id = 'None'
                meeting_session_id = 'None'

                if meeting_objs:
                    meeting_obj = meeting_objs.first()

                    if not meeting_obj.customer.is_session_exp:
                        is_meeting_started = meeting_obj.is_started
                        is_meeting_end_required = (meeting_obj.call_type == 'pip') or (
                            meeting_obj.is_started == False)
                        meeting_id = str(meeting_obj.meeting_id)
                        meeting_session_id = str(
                            meeting_obj.customer.session_id)

                        if is_meeting_end_required:
                            meeting_obj.is_interrupted = True
                            meeting_obj.is_completed = True
                            meeting_obj.save()

                # check if bot selected language to be shown for virtual interpretation
                to_show_bot_lang = False
                if config_obj.is_virtual_interpretation_enabled:
                    eng_lang_obj = Language.objects.get(lang="en")
                    if user_obj.preferred_languages.count() == 1 and eng_lang_obj in user_obj.preferred_languages.all():
                        to_show_bot_lang = True

                # to show by default bot selected languages
                if not user_obj.preferred_languages.exists():
                    for language in bot_obj.languages_supported.all():
                        user_obj.preferred_languages.add(language)
                        user_obj.save()

                # Category list for form builder
                category_list = []
                category_objs = admin_config.admin.category.all().filter(
                    bot__pk=int(bot_obj.pk), is_public=True, is_deleted=False)
                for item in category_objs:
                    category_list.append(str(item.title))

                # cobrowsing info
                cobrowsing_info = get_cobrowsing_info_based_agent(user_obj, LiveChatCobrowsingData)
                cobrowsing_guest_info = get_cobrowsing_info_based_guest_agent(user_obj, LiveChatCobrowsingData, LiveChatCustomer)

                email_config_obj = get_email_config_obj(admin_config, LiveChatEmailConfig)

                livechat_channels_char_limit = {
                    "Facebook": LIVECHAT_FACEBOOK_CHAR_LIMIT,
                    "Instagram": LIVECHAT_INSTAGRAM_CHAR_LIMIT
                }

                return render(request, 'LiveChatApp/agent_console.html',
                              {
                                  "agent_websocket_token": get_agent_token(user_obj.user.username),
                                  "user_obj": user_obj, "assigned_customer_count": assigned_customer_count,
                                  "livechat_categories": livechat_categories,
                                  "is_video_meeting_enabled": is_video_meeting_enabled,
                                  "admin_config": admin_config,
                                  "time_marked_stop_interaction": time_marked_stop_interaction,
                                  "canned_response": canned_response,
                                  "blacklisted_keyword": blacklisted_keyword,
                                  "auto_chat_disposal_enabled": config_obj.auto_chat_disposal_enabled,
                                  "user_terminates_chat_enabled": config_obj.user_terminates_chat_enabled,
                                  "user_terminates_chat_dispose_time": config_obj.user_terminates_chat_dispose_time,
                                  "session_inactivity_enabled": config_obj.session_inactivity_enabled,
                                  "session_inactivity_chat_dispose_time": config_obj.session_inactivity_chat_dispose_time,
                                  "socket_access_token": config_obj.access_token,
                                  "guest_session_timer": config_obj.guest_agent_timer,
                                  "max_guest_agent": config_obj.max_guest_agent,
                                  "current_guest_sessions": current_guest_sessions,
                                  "config_obj": config_obj,
                                  "is_meeting_started": is_meeting_started,
                                  "is_meeting_end_required": is_meeting_end_required,
                                  "meeting_id": meeting_id,
                                  "meeting_session_id": meeting_session_id,
                                  "bot_id": bot_obj.pk,
                                  "to_show_bot_lang": to_show_bot_lang,
                                  "bot_obj": bot_obj,
                                  "meeting_domain": config_obj.meeting_domain,
                                  "category_list": category_list,
                                  "cobrowsing_info": cobrowsing_info,
                                  "cobrowsing_guest_info": cobrowsing_guest_info,
                                  "customer_blacklisted_keyword": customer_blacklisted_keyword,
                                  "email_config_obj": email_config_obj,
                                  "livechat_channels_char_limit": livechat_channels_char_limit,
                              })
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("HomePage: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


def AuditTrail(request):  # noqa: N802
    try:
        if request.user.is_authenticated:
            validation_obj = LiveChatInputValidation()

            channel_obj_list = Channel.objects.all()

            agent_username = request.GET.get('agent_username')
            agent_username = validation_obj.remo_html_from_string(
                agent_username)
            agent_username = validation_obj.remo_special_tag_from_string(
                agent_username)

            channel_name = request.GET.get('channel_name')
            if channel_name == 'None':
                channel_name = 'All'

            try:
                selected_category_pk = request.GET.get('selected_category_pk')
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("AuditTrail selected_category_pk not found! %s %s", str(e), str(
                    exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
                selected_category_pk = 0
            if selected_category_pk == None:
                selected_category_pk = 0

            if request.GET.get('start_date') and request.GET.get('end_date'):
                start_date = datetime.datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
                end_date = datetime.datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
            else:
                start_date = (datetime.datetime.today() - datetime.timedelta(7)).date()
                end_date = datetime.datetime.today().date()

            chat_status = request.GET.get('chat_status')

            user_obj = LiveChatUser.objects.get(user=User.objects.get(
                username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)

            if user_obj.status != "3":
                agent_obj_list = get_agents_under_this_user(user_obj)

                category_list = user_obj.category.all()
                agent_list = []
                for agent in agent_obj_list:
                    agent_list.append(agent.user.username)

                template_to_render = 'LiveChatApp/audit_trail.html'

                messages_list = []
                audit_obj_list = []
                if user_obj.static_analytics:
                    template_to_render = 'LiveChatApp/static_audit_trail.html'
                    audit_obj_list = STATIC_LIVECHAT_AGENT_MESSAGE_HISTORY
                    messages_list = STATIC_LIVECHAT_MESSAGES_LIST

                page = request.GET.get('page')
                total_audits, audit_obj_list, start_point, end_point = paginate(
                    audit_obj_list, AUDIT_TRAIL_ITEM_COUNT, page)

                admin_config = get_admin_config(
                    user_obj, LiveChatAdminConfig, LiveChatUser)

                return render(request, template_to_render, {
                    "audit_obj_list": audit_obj_list,
                    "total_audits": total_audits,
                    "user_obj": user_obj,
                    "agent_list": agent_list,
                    "agent_username": agent_username,
                    "DEFAULT_LIVECHAT_FILTER_START_DATETIME": start_date,
                    "DEFAULT_LIVECHAT_FILTER_END_DATETIME": end_date,
                    "start_date": start_date,
                    "end_date": end_date,
                    "conversation_report_custom_start_date": (datetime.datetime.today() - datetime.timedelta(30)).date(),
                    "chat_status": chat_status,
                    "start_point": start_point,
                    "end_point": end_point,
                    "admin_config": admin_config,
                    "messages_list": messages_list,
                    "channel_obj_list": channel_obj_list,
                    "channel_name": channel_name,
                    "category_list": category_list,
                    "selected_category_pk": int(selected_category_pk),
                    "is_report_generation_via_kafka_enabled": is_kafka_enabled(),
                })
            else: 
                return HttpResponse(ACCESS_DENIED) 
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("AuditTrail ! %s %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return render(request, 'LiveChatApp/error_500.html')


def VOIPHistory(request):  # noqa: N802
    try:
        if request.user.is_authenticated:
            validation_obj = LiveChatInputValidation()

            channel_obj_list = Channel.objects.all()

            agent_username = request.GET.get('agent_username')
            agent_username = validation_obj.remo_html_from_string(
                agent_username)
            agent_username = validation_obj.remo_special_tag_from_string(
                agent_username)

            user_obj = LiveChatUser.objects.get(user=User.objects.get(
                username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)

            agent_obj_list = get_agents_under_this_user(user_obj)

            category_list = user_obj.category.all()
            agent_list = []
            for agent in agent_obj_list:
                agent_list.append(agent.user.username)

            template_to_render = 'LiveChatApp/voip_history.html'

            messages_list = []
            voip_object_list = []
            if user_obj.static_analytics:
                template_to_render = 'LiveChatApp/static_audit_trail.html'
                voip_object_list = STATIC_LIVECHAT_AGENT_MESSAGE_HISTORY
                messages_list = STATIC_LIVECHAT_MESSAGES_LIST

            page = request.GET.get('page')
            total_audits, voip_object_list, start_point, end_point = paginate(
                voip_object_list, VOIP_HISTORY_ITEM_COUNT, page)

            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)

            user_obj = LiveChatUser.objects.get(user=User.objects.get(
                username=str(request.user.username)), is_deleted=False)

            return render(request, template_to_render, {
                "voip_object_list": voip_object_list,
                "total_audits": total_audits,
                "user_obj": user_obj,
                "agent_list": agent_list,
                "DEFAULT_LIVECHAT_FILTER_START_DATETIME": datetime.datetime.today().date(),
                "DEFAULT_LIVECHAT_FILTER_END_DATETIME": datetime.datetime.today().date(),
                "start_date": datetime.datetime.today().date(),
                "end_date": datetime.datetime.today().date(),
                "start_point": start_point,
                "end_point": end_point,
                "admin_config": admin_config,
                "messages_list": messages_list,
                "channel_obj_list": channel_obj_list,
                "category_list": category_list,
                "is_report_generation_via_kafka_enabled": is_kafka_enabled(),
            })
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("VOIPHistory ! %s %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return render(request, 'LiveChatApp/error_500.html')


def VCHistory(request):  # noqa: N802
    try:
        if request.user.is_authenticated:
            validation_obj = LiveChatInputValidation()

            channel_obj_list = Channel.objects.all()

            agent_username = request.GET.get('agent_username')
            agent_username = validation_obj.remo_html_from_string(
                agent_username)
            agent_username = validation_obj.remo_special_tag_from_string(
                agent_username)

            user_obj = LiveChatUser.objects.get(user=User.objects.get(
                username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)

            agent_obj_list = get_agents_under_this_user(user_obj)

            category_list = user_obj.category.all()
            agent_list = []
            for agent in agent_obj_list:
                agent_list.append(agent.user.username)

            template_to_render = 'LiveChatApp/vc_history.html'

            messages_list = []
            voip_object_list = []
            if user_obj.static_analytics:
                template_to_render = 'LiveChatApp/static_audit_trail.html'
                voip_object_list = STATIC_LIVECHAT_AGENT_MESSAGE_HISTORY
                messages_list = STATIC_LIVECHAT_MESSAGES_LIST

            page = request.GET.get('page')
            total_audits, voip_object_list, start_point, end_point = paginate(
                voip_object_list, VOIP_HISTORY_ITEM_COUNT, page)

            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)

            user_obj = LiveChatUser.objects.get(user=User.objects.get(
                username=str(request.user.username)), is_deleted=False)

            return render(request, template_to_render, {
                "voip_object_list": voip_object_list,
                "total_audits": total_audits,
                "user_obj": user_obj,
                "agent_list": agent_list,
                "DEFAULT_LIVECHAT_FILTER_START_DATETIME": datetime.datetime.today().date(),
                "DEFAULT_LIVECHAT_FILTER_END_DATETIME": datetime.datetime.today().date(),
                "start_date": datetime.datetime.today().date(),
                "end_date": datetime.datetime.today().date(),
                "start_point": start_point,
                "end_point": end_point,
                "admin_config": admin_config,
                "messages_list": messages_list,
                "channel_obj_list": channel_obj_list,
                "category_list": category_list,
                "is_report_generation_via_kafka_enabled": is_kafka_enabled(),
            })
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("VCHistory ! %s %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return render(request, 'LiveChatApp/error_500.html')


def ManageAgent(request):
    try:
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)

            if user_obj.status != "3":
                # fetching all agents under this user and its supervisors
                user_obj_list = fetch_all_agents_under_this_user(user_obj)
                supervisor_obj_list = user_obj_list.filter(status="2")

                status = request.GET["status"]
                user_type = request.GET["user_type"]

                supervisors_list = user_obj_list.filter(status='2')
                agents_list = user_obj_list.filter(status='3')

                if user_type == 'supervisors':
                    user_obj_list = supervisors_list
                else:
                    user_obj_list = agents_list

                total_agents = user_obj_list.count()

                logged_in_users_count, ready_users_count, not_ready_users_count = get_agents_availibility_analytics_filter(
                    user_obj_list)

                if status != 'total':
                    # this line fetches user objects pk for users who are logged in
                    user_ids = [
                        user.pk for user in user_obj_list if user.check_livechat_status()]
                    user_obj_list = user_obj_list.filter(pk__in=user_ids)

                    if(status == "ready"):
                        # users who are agent and online
                        user_obj_list = user_obj_list.filter(
                            status=3, is_online=True)

                    if(status == "not-ready"):
                        # users who are agent and offline
                        user_obj_list = user_obj_list.filter(
                            status=3, is_online=False)

                page = request.GET.get('page')
                total_user_objs, user_obj_list, start_point, end_point = paginate(
                    user_obj_list, AGENT_ITEM_COUNT, page)

                admin_config = get_admin_config(
                    user_obj, LiveChatAdminConfig, LiveChatUser)

                bot_objs = user_obj.bots.all().filter(is_deleted=False)
                livechat_categories = user_obj.category.all().filter(
                    bot__in=bot_objs, is_public=True, is_deleted=False)

                creation_allowed = check_if_user_creation_allowed(user_obj, LiveChatUser, LiveChatAdminConfig)

                return render(request, 'LiveChatApp/manage_agents.html', {
                    "user_obj_list": user_obj_list,
                    "user_obj": user_obj,
                    "livechat_categories": livechat_categories,
                    "start_point": start_point,
                    "end_point": end_point,
                    "total_user_objs": total_user_objs,
                    "bot_objs": bot_objs,
                    "supervisor_obj_list": supervisor_obj_list,
                    "logged_in_users": logged_in_users_count,
                    "not_ready_users": not_ready_users_count,
                    "ready_users": ready_users_count,
                    "admin_config": admin_config,
                    "status": status,
                    "total_agents": total_agents,
                    "user_type": user_type,
                    "supervisors_list": supervisors_list,
                    "agents_list": agents_list,
                    "creation_allowed": creation_allowed,
                    "max_limit_alert_for_user_creation": LIVECHAT_USER_CREATION_MAX_LIMIT_ALERT_TEXT
                })
            else:
                return HttpResponse(ACCESS_DENIED)    
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("HomePageAdminManageAgents: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


class ManageAgentsContinuousAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:

            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            user_type = data['user_type']

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)

            user_obj_list = fetch_all_agents_under_this_user(user_obj)

            if user_type == 'agents':
                user_obj_list = user_obj_list.filter(status='3')
            else:
                user_obj_list = user_obj_list.filter(status='2')

            total_agents = user_obj_list.count()

            logged_in_users_count, ready_users_count, not_ready_users_count = get_agents_availibility_analytics_filter(
                user_obj_list)

            users = list(user_obj_list.values(
                'pk', 'is_online', 'ongoing_chats'))

            response = {
                "users": users,
                "logged_in_users": logged_in_users_count,
                "not_ready_users": not_ready_users_count,
                "ready_users": ready_users_count,
                "total_agents": total_agents
            }
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ManageAgentsContinuous: %s at %s", e, str(
                exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ManageAgentsContinuous = ManageAgentsContinuousAPI.as_view()


def ManageOnlyAdmin(request):
    try:
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            if user_obj.status == "1" and not user_obj.is_livechat_only_admin:
                user_obj_list = user_obj.livechat_only_admin.filter(
                    is_deleted=False).order_by('-pk')

                page = request.GET.get('page')
                total_user_objs, user_obj_list, start_point, end_point = paginate(
                    user_obj_list, LIVECHAT_ONLY_ADMIN_ITEM_COUNT, page)

                bot_objs = user_obj.bots.all().filter(is_deleted=False)

                admin_config = get_admin_config(
                    user_obj, LiveChatAdminConfig, LiveChatUser)

                return render(request, 'LiveChatApp/manage_only_admin.html', {
                    "user_obj_list": user_obj_list,
                    "user_obj": user_obj,
                    "start_point": start_point,
                    "end_point": end_point,
                    "total_user_objs": total_user_objs,
                    "admin_config": admin_config,
                    "bot_objs": bot_objs
                })
            else:
                return HttpResponse(AUTHORIZATION_DENIED)
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ManageOnlyAdmin: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


def SystemSettings(request):
    try:
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            user_status = user_obj.status
            livechat_categories = LiveChatCategory.objects.all()
            meeting_host_url = user_obj.meeting_host_url
            bot_id = "-1"

            # user is admin
            if user_status == "1":
                if "bot_id" in request.GET:
                    bot_id = request.GET["bot_id"]
                    bot_obj = Bot.objects.get(pk=bot_id)
                else:
                    bot_obj = user_obj.bots.filter(is_deleted=False)[0]
                    bot_id = bot_obj.pk

                try:
                    livechat_config_obj = LiveChatConfig.objects.get(
                        bot=bot_obj)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Livechat config bot does not exists %s at %s", e, str(
                        exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
                    livechat_config_obj = LiveChatConfig.objects.create(
                        bot=bot_obj)

                try:
                    livechat_admin_config = LiveChatAdminConfig.objects.get(
                        admin=user_obj, livechat_config__in=[livechat_config_obj])
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("LivechatAdmin config bot does not exists %s at %s", e, str(
                        exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
                    livechat_admin_config = LiveChatAdminConfig.objects.get(
                        admin=user_obj)
                    livechat_admin_config.livechat_config.add(
                        livechat_config_obj)
                    livechat_admin_config.save()

                agent_unavialable_response = livechat_config_obj.agent_unavialable_response
                is_video_meeting_enabled = livechat_admin_config.is_video_meeting_enabled

                bot_obj_list = user_obj.bots.filter(is_deleted=False)
                request.session[
                    "is_video_meeting_enabled"] = is_video_meeting_enabled
                user_obj = LiveChatUser.objects.get(user=User.objects.get(
                    username=str(request.user.username)), is_deleted=False)

                livechat_developer_settings_obj = get_developer_console_livechat_settings()
                if livechat_developer_settings_obj:
                    livechat_masking_emails = json.loads(livechat_developer_settings_obj.livechat_masking_pii_data_otp_email)
                else:
                    livechat_masking_emails = settings.MASKING_PII_DATA_OTP_EMAIL

                livechat_masking_emails_str = ""
                for counter in range(0, len(livechat_masking_emails)):
                    livechat_masking_emails_str += livechat_masking_emails[counter]
                    if counter < len(livechat_masking_emails) - 2:
                        livechat_masking_emails_str += ", "
                    elif counter == len(livechat_masking_emails) - 2:
                        livechat_masking_emails_str += " and "

                developer_console_config = get_developer_console_settings()
                if developer_console_config and not developer_console_config.enable_footer_over_entire_console:
                    livechat_admin_config.show_version_footer = developer_console_config.enable_footer_over_entire_console
                    livechat_admin_config.save()

                email_config_id = ""
                email_config_obj = get_email_config_obj(livechat_admin_config, LiveChatEmailConfig)
                if email_config_obj.current_email_setup:
                    email_config_id = email_config_obj.current_email_setup.email

                return render(request, 'LiveChatApp/admin_system_settings.html', {
                    "admin_config": livechat_admin_config, 
                    "config_obj": livechat_config_obj, 
                    "user_obj": user_obj, 
                    "livechat_categories": livechat_categories, 
                    "meeting_url": meeting_host_url, 
                    "agent_unavialable_response": agent_unavialable_response, 
                    "is_video_meeting_enabled": is_video_meeting_enabled, 
                    "bot_id": int(bot_id), 
                    "bot_obj_list": bot_obj_list, 
                    "character_limit_large_text": LIVECHAT_CHARACTER_LIMIT_LARGE_TEXT,
                    "character_limit_medium_text": LIVECHAT_CHARACTER_LIMIT_MEDIUM_TEXT, 
                    "livechat_masking_emails_str": livechat_masking_emails_str,
                    "developer_console_config": developer_console_config,
                    "email_config_obj": email_config_obj,
                    "email_config_id": email_config_id})
            # user is supervisor
            elif user_status == "2":
                return HttpResponseRedirect("/livechat/canned-response/")
            else:
                return HttpResponse(AUTHORIZATION_DENIED)
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("SystemSettings: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


def InteractionSettings(request):
    try:
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            user_status = user_obj.status
            livechat_categories = LiveChatCategory.objects.all()
            meeting_host_url = user_obj.meeting_host_url
            bot_id = "-1"

            # user is admin
            if user_status == "1":
                if "bot_id" in request.GET:
                    bot_id = request.GET["bot_id"]
                    bot_obj = Bot.objects.get(pk=bot_id)
                else:
                    bot_obj = user_obj.bots.filter(is_deleted=False)[0]
                    bot_id = bot_obj.pk

                try:
                    livechat_config_obj = LiveChatConfig.objects.get(
                        bot=bot_obj)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Livechat config bot does not exists %s at %s", e, str(
                        exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
                    livechat_config_obj = LiveChatConfig.objects.create(
                        bot=bot_obj)

                try:
                    livechat_admin_config = LiveChatAdminConfig.objects.get(
                        admin=user_obj, livechat_config__in=[livechat_config_obj])
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("LivechatAdmin config bot does not exists %s at %s", e, str(
                        exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
                    livechat_admin_config = LiveChatAdminConfig.objects.get(
                        admin=user_obj)
                    livechat_admin_config.livechat_config.add(
                        livechat_config_obj)
                    livechat_admin_config.save()

                is_video_meeting_enabled = livechat_admin_config.is_video_meeting_enabled

                bot_obj_list = user_obj.bots.filter(is_deleted=False)
                request.session[
                    "is_video_meeting_enabled"] = is_video_meeting_enabled
                user_obj = LiveChatUser.objects.get(user=User.objects.get(
                    username=str(request.user.username)), is_deleted=False)

                return render(request, 'LiveChatApp/admin_interaction_settings.html', {
                    "admin_config": livechat_admin_config, 
                    "config_obj": livechat_config_obj, 
                    "user_obj": user_obj, 
                    "livechat_categories": livechat_categories, 
                    "meeting_url": meeting_host_url, 
                    "is_video_meeting_enabled": is_video_meeting_enabled, 
                    "bot_id": int(bot_id), 
                    "bot_obj_list": bot_obj_list, 
                    "character_limit_large_text": LIVECHAT_CHARACTER_LIMIT_LARGE_TEXT})
            # user is supervisor
            elif user_status == "2":
                return HttpResponseRedirect("/livechat/canned-response/")
            else:
                return HttpResponse(AUTHORIZATION_DENIED)
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("InteractionSettings: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


def GetCategoryList(request):
    try:
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)

            is_user_admin = user_obj.status == "1"
            if is_user_admin:
                bot_list = user_obj.bots.filter(is_deleted=False)
                livechat_categories = user_obj.category.filter(
                    bot__in=bot_list, is_deleted=False)
                total_livechat_categories = livechat_categories.count()

                page = request.GET.get('page')

                total_livechat_categories, livechat_categories, start_point, end_point = paginate(
                    livechat_categories, CATEGORY_ITEM_COUNT, page)

                admin_config = get_admin_config(
                    user_obj, LiveChatAdminConfig, LiveChatUser)
                user_obj = LiveChatUser.objects.get(user=User.objects.get(
                    username=str(request.user.username)), is_deleted=False)
                return render(request, 'LiveChatApp/livechat_category.html', {
                    "livechat_categories": livechat_categories,
                    "priority_list": get_priority_list(),
                    "user_obj": user_obj,
                    "start_point": start_point,
                    "end_point": end_point,
                    "total_livechat_categories": total_livechat_categories,
                    "bot_list": bot_list,
                    "admin_config": admin_config,
                    "character_limit_small_text": LIVECHAT_CHARACTER_LIMIT_SMALL_TEXT,
                })
            else:
                return HttpResponse(AUTHORIZATION_DENIED)
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("GetCategoryList: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


def BlackListKeyword(request):
    try:
        if request.user.is_authenticated:

            blacklist_for = "agent"

            if "blacklist_for" in request.GET:
                blacklist_for = request.GET["blacklist_for"]

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            if blacklist_for == "customer" and not user_obj.is_chat_escalation_enabled():
                return HttpResponse(AUTHORIZATION_DENIED)

            is_user_agent = user_obj.status == "3"
            if is_user_agent:
                HttpResponse(AUTHORIZATION_DENIED)

            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)

            if blacklist_for == "agent":

                if user_obj.status == "1":
                    blacklisted_keyword = LiveChatBlackListKeyword.objects.filter(
                        agent_id=user_obj, blacklist_keyword_for=blacklist_for)
                elif user_obj.status == "2":
                    blacklisted_keyword = LiveChatBlackListKeyword.objects.filter(agent_id=user_obj, blacklist_keyword_for=blacklist_for) | LiveChatBlackListKeyword.objects.filter(
                        agent_id=LiveChatUser.objects.filter(agents__user=user_obj.user)[0], blacklist_keyword_for=blacklist_for)

            elif blacklist_for == "customer":

                admin_obj = get_admin_from_active_agent(user_obj, LiveChatUser)
                blacklisted_keyword = LiveChatBlackListKeyword.objects.filter(agent_id=admin_obj, blacklist_keyword_for=blacklist_for) | LiveChatBlackListKeyword.objects.filter(
                    agent_id__in=admin_obj.agents.all(), blacklist_keyword_for=blacklist_for)               

            word_arr = blacklisted_keyword.values_list('word', flat=True)

            page = request.GET.get('page')
            total_blacklisted_keyword, blacklisted_keyword, start_point, end_point = paginate(
                blacklisted_keyword, BLACKLISTED_KEYWORD_COUNT, page)

            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)

            user_obj = LiveChatUser.objects.get(user=User.objects.get(
                username=str(request.user.username)), is_deleted=False)

            return render(request, 'LiveChatApp/blacklistedkeyword_admin.html', {
                "total_blacklisted_keyword": total_blacklisted_keyword, 
                "end_point": end_point, 
                "user_obj": user_obj, 
                "blacklisted_keyword": blacklisted_keyword, 
                "start_point": start_point, 
                "admin_config": admin_config, 
                "character_limit_small_text": LIVECHAT_CHARACTER_LIMIT_SMALL_TEXT,
                "blacklist_for": blacklist_for,
                "word_arr": list(word_arr),
            })
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("AgentSettings: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


def GetArchivedCustomerChat(request):
    try:
        if request.user.is_authenticated:
            # By default, chat history of last 7 days is loaded
            datetime_start = (datetime.datetime.today() -
                              datetime.timedelta(7)).date()
            datetime_end = datetime.datetime.today().date()

            try:
                start_date = request.GET.get('start_date')
                end_date = request.GET.get('end_date')

                if start_date and end_date:
                    datetime_start = datetime.datetime.strptime(start_date, DEFAULT_DATE_FORMAT).date()
                    datetime_end = datetime.datetime.strptime(end_date, DEFAULT_DATE_FORMAT).date()  # noqa: F841
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.warning("datetime_start and datetime_end is not in valid format %s at line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

            validation_obj = LiveChatInputValidation()

            chat_duration = request.GET.get('chat_duration')
            chat_duration = validation_obj.remo_html_from_string(chat_duration)

            if not chat_duration or chat_duration == 'None':
                chat_duration = 10000000

            user_obj = LiveChatUser.objects.get(user=User.objects.get(
                username=str(request.user.username)), is_deleted=False)

            livechat_followup_cust_objs = LiveChatFollowupCustomer.objects.filter(
                agent_id=user_obj, is_completed=True).values('livechat_customer')   
            customer_list = LiveChatCustomer.objects.filter(
                Q(agents_group__user=user_obj, is_session_exp=True) | Q(pk__in=livechat_followup_cust_objs))

            archive_cust_list = get_audit_objects([user_obj], None, datetime_start, datetime_end, customer_list, 'All', None, 0, None, None, livechat_followup_cust_objs)

            page = request.GET.get('page')
            total_archive, archive_cust_list_final, start_point, end_point = paginate(
                archive_cust_list, ARCHIVE_CUSTOMER_ITEM_COUNT, page)

            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)
            return render(request, 'LiveChatApp/archived_customer.html', {
                "archive_cust_list": archive_cust_list_final,
                "total_archive": total_archive,
                "user_obj": user_obj,
                "chat_duration": chat_duration,
                "start_date": datetime_start,
                "end_date": datetime_end,
                "DEFAULT_LIVECHAT_FILTER_START_DATETIME": datetime_start,
                "DEFAULT_LIVECHAT_FILTER_END_DATETIME": datetime_end,
                "chat_duration_list": get_chat_duration_list(),
                "start_point": start_point,
                "end_point": end_point,
                "admin_config": admin_config
            })
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("GetArchivedCustomerChat ! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return render(request, 'EasyTMSApp/error_500.html')


def CannedResponseURL(request):
    try:
        if request.user.is_authenticated:

            user_obj = None
            try:
                user_obj = LiveChatUser.objects.get(user=User.objects.get(
                    username=str(request.user.username)), is_deleted=False)
                user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("User Does Not Exist: %s at %s",
                             e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

                return HttpResponseRedirect(CHAT_LOGIN_PATH)

            canned_response_list = get_canned_response_for_current_agent(
                user_obj, CannedResponse, LiveChatUser)

            page = request.GET.get('page')
            total_canned_response, canned_response_list, start_point, end_point = paginate(
                canned_response_list, CANNED_RESPONSE_ITEM_COUNT, page)

            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)

            is_user_agent = user_obj.status == "3"

            context = {
                "admin_config": admin_config,
                "user_obj": user_obj,
                "canned_response_list": canned_response_list,
                "total_canned_response": total_canned_response,
                "start_point": start_point,
                "end_point": end_point,
                "character_limit_small_text": LIVECHAT_CHARACTER_LIMIT_SMALL_TEXT,
                "character_limit_large_text": LIVECHAT_CHARACTER_LIMIT_LARGE_TEXT,
                "disallowed_list_of_chars": list(admin_config.canned_response_config)
            }
            if is_user_agent:
                return render(request, 'LiveChatApp/agent_canned_response.html', context)
            else:
                return render(request, 'LiveChatApp/manager_canned_response.html', context)
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("AgentCannedResponse: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


class PreviousSessionMessagesAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["message_list"] = []
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:

            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)
            try:
                cust_obj_pk = data["cust_obj_pk"]
                client_id = data["client_id"]
                cust_obj_active_url = LiveChatCustomer.objects.get(
                    pk=cust_obj_pk).active_url
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("PreviousSessionMessages: %s at %s", e, str(
                    exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
                session_id = data["session_id"]
                client_id = LiveChatCustomer.objects.get(
                    session_id=session_id).client_id
                cust_obj_active_url = LiveChatCustomer.objects.get(
                    pk=session_id).active_url
                cust_obj_pk = session_id

            try:
                message_list, new_obj_pk = get_previous_session_messages(
                    cust_obj_pk, client_id, LiveChatMISDashboard, LiveChatCustomer)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("PreviousSessionMessages: %s at %s", e, str(
                    exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
                response["status_message"] = "No more data"
                response["status_code"] = "300"
                response["today_date"] = datetime.datetime.today().strftime(
                    DATE_DD_MMM_YYYY)
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if message_list == []:
                response["status_message"] = "No more data"
                response["status_code"] = "300"
                response["today_date"] = datetime.datetime.today().strftime(
                    DATE_DD_MMM_YYYY)
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            response["new_obj_pk"] = str(new_obj_pk)
            response["cust_obj_active_url"] = cust_obj_active_url
            response["today_date"] = datetime.datetime.today().strftime(
                DATE_DD_MMM_YYYY)
            response["joined_date"] = LiveChatCustomer.objects.get(
                pk=cust_obj_pk).joined_date.strftime(DATE_DD_MMM_YYYY)
            for message in message_list:
                message.message_time = message.message_time + \
                    timedelta(hours=5, minutes=30)
                response["updated_date"] = message.message_time.strftime(
                    DATE_DD_MMM_YYYY)
                response["message_list"].append({"sender": message.sender, "sender_name": message.sender_name,
                                                 "text_message": message.text_message, "attachment_file_name": message.attachment_file_name,
                                                 "attachment_file_path": message.attachment_file_path,
                                                 "preview_attachment_file_path": message.preview_attachment_file_path,
                                                 "message_time": message.message_time.strftime("%d-%b-%Y, %I:%M %p"), "thumbnail_file_path": message.thumbnail_file_path,
                                                 "is_guest_agent_message": message.is_guest_agent_message, "sender_username": message.sender_username,
                                                 "is_voice_call_message": message.is_voice_call_message,
                                                 "is_video_call_message": message.is_video_call_message,
                                                 "is_cobrowsing_message": message.is_cobrowsing_message,
                                                 "message_for": message.message_for,
                                                 "is_customer_warning_message": message.is_customer_warning_message,
                                                 "is_customer_report_message_notification": message.is_customer_report_message_notification,
                                                 })
            response["status_message"] = "SUCCESS"
            response["status_code"] = "200"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("PreviousSessionMessages: %s at %s", e, str(
                exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class CreateNewAgentAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)

            creation_allowed = check_if_user_creation_allowed(user_obj, LiveChatUser, LiveChatAdminConfig)

            is_user_agent = user_obj.status == "3"

            if not is_user_agent and creation_allowed:
                data = DecryptVariable(request.data["json_string"])
                data = json.loads(data)

                validation_obj = LiveChatInputValidation()

                name = data["name"]
                phone_number = data["phone_number"]
                email = data["email"]

                if not validation_obj.validate_name(name):
                    response["status_code"] = "400"
                    response["status_message"] = "Please enter a valid name"

                if not validation_obj.validate_phone_number(phone_number):
                    response["status_code"] = "400"
                    response["status_message"] = "Please enter a valid phone number."

                if not validation_obj.validate_email(email):
                    response["status_code"] = "400"
                    response["status_message"] = "Please enter a valid email."
                
                if response["status_code"] == "400":
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(
                        json.dumps(response))
                    return Response(data=response)

                split_name = name.split()
                first_name = split_name[0]
                if len(split_name) > 1:
                    last_name = split_name[-1]
                else:
                    last_name = ""

                username = email

                status = data["status"]
                status = validation_obj.remo_html_from_string(status)

                category_pk_list = data["category_pk_list"]
                bot_pk_list = data["bot_pk_list"]

                supervisor_pk = "-1"
                if "supervisor_pk" in data:
                    supervisor_pk = data["supervisor_pk"]

                max_customers_allowed = data["max_customers_allowed"]
                max_customers_allowed = validation_obj.remo_html_from_string(
                    max_customers_allowed)

                if int(max_customers_allowed) >= LIVECHAT_MAX_CUSTOMER_ALLOWED_FOR_AGENT or int(max_customers_allowed) <= 0:
                    response["status_message"] = "Max customer allowed should be between 1 to 100"
                    response["status_code"] = "301"
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                easychat_user_obj = None
                try:
                    is_easychat_user_obj_already_created = User.objects.filter(username__iexact=email)
                    password = generate_random_password()
                    if password and not is_easychat_user_obj_already_created:
                        easychat_user_obj = User.objects.create(
                            email=email, first_name=first_name, last_name=last_name, username=username, password=password, role="customer_care_agent", status="1")
                        send_password_mail(name, username, email, password)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("CreateNewAgent: %s at %s",
                                 e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

                is_created_user_admin = status == "1"
                if easychat_user_obj != None and not is_created_user_admin:
                    new_user_obj = LiveChatUser.objects.create(
                        user=easychat_user_obj, status=status, phone_number=phone_number, max_customers_allowed=max_customers_allowed)
                    for item in category_pk_list:
                        new_user_obj.category.add(
                            get_livechat_category_object(item, Bot.objects.get(pk=bot_pk_list[0]), LiveChatCategory))

                    for bot_pk in bot_pk_list:
                        new_user_obj.bots.add(Bot.objects.get(pk=bot_pk))

                    new_user_obj.save()
                    add_supervisor(new_user_obj, supervisor_pk,
                                   user_obj, LiveChatUser)
                    response["status_message"] = "SUCCESS"
                    response["status_code"] = "200"
                    description = "New User has been created with username" + \
                        " (" + username + " and id " + str(new_user_obj.pk) + ")"
                    add_audit_trail(
                        "LIVECHATAPP",
                        user_obj.user,
                        "Create-User",
                        description,
                        json.dumps(data),
                        request.META.get("PATH_INFO"),
                        request.META.get('HTTP_X_FORWARDED_FOR')
                    )
                else:
                    response["status_message"] = "SUCCESS"
                    response["status_code"] = "300"
            else:
                response["status_message"] = INVALID_OPERATION
                response["status_code"] = "500"
                if not creation_allowed:
                    response["status_message"] = "Your limit is max out for adding user to this account"
                    response["status_code"] = "403"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CreateNewAgent: %s at %s", e, str(
                exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class CreateAgentWithExcelAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        logger.info("Into CreateAgentWithExcelAPI..",
                    extra={'AppName': 'LiveChat'})
        response = {}
        response["status_code"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            duplicate_users = False
            user_obj = LiveChatUser.objects.get(user=User.objects.get(
                username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            data = request.data

            file_path = settings.MEDIA_ROOT + data['src']

            validation_obj = LiveChatInputValidation()

            wb = xlrd.open_workbook(file_path)
            sheet = wb.sheet_by_index(0)

            count = sheet.nrows - 1
            creation_allowed = check_if_user_creation_allowed(user_obj, LiveChatUser, LiveChatAdminConfig, count)
            
            livechat_admin_config_obj = get_admin_config(user_obj, LiveChatAdminConfig, LiveChatUser)
            max_users_allowed_to_be_created = livechat_admin_config_obj.max_users_allowed_to_be_created

            is_user_agent = user_obj.status == "3"
            
            if not is_user_agent and creation_allowed:
                for row in range(1, sheet.nrows):
                    try:

                        first_name = str(sheet.cell_value(row, 0)).strip()
                        last_name = str(sheet.cell_value(row, 1)).strip()
                        phone_number = str(
                            int(float(str(sheet.cell_value(row, 2)))))
                        email = str(sheet.cell_value(row, 3)).strip()
                        username = email
                        is_user_exists = False

                        try:
                            user = LiveChatUser.objects.get(user=User.objects.get(
                                username__iexact=username), is_deleted=False)
                            if user != None:
                                is_user_exists = True
                        except Exception:
                            is_user_exists = False

                        if is_user_exists:
                            duplicate_users = True
                            continue

                        password = ""
                        category_title = str(sheet.cell_value(
                            row, 7)).split(",")[0].strip()
                        if category_title == "":
                            category_title = "others"
                        try:
                            password = str(
                                int(float(str(sheet.cell_value(row, 4)))))
                        except Exception:
                            password = str(sheet.cell_value(row, 4))

                        if user_obj.status == "1":
                            supervisors = str(sheet.cell_value(row, 8)).strip()
                            if supervisors != None and supervisors != "":
                                supervisors = supervisors.split(',')
                            else:
                                supervisors = []

                        try:
                            max_customers_allowed = str(
                                int(float(str(sheet.cell_value(row, 9)))))
                        except Exception:
                            max_customers_allowed = "-1"

                        try:
                            if int(max_customers_allowed) < 1 or int(max_customers_allowed) >= LIVECHAT_MAX_CUSTOMER_ALLOWED_FOR_AGENT:
                                max_customers_allowed = "-1"
                        except Exception:
                            max_customers_allowed = "-1"

                        is_info_valid = True
                        if not validation_obj.validate_name(first_name):
                            response["status_message"] = "Enter valid first name!"
                            is_info_valid = False
                        elif not validation_obj.validate_name(last_name):
                            response["status_message"] = "Enter valid last name!"
                            is_info_valid = False
                        elif not validation_obj.validate_phone_number(phone_number):
                            response["status_message"] = "Enter valid phone number!"
                            is_info_valid = False
                        elif not validation_obj.validate_email(email):
                            response["status_message"] = "Enter valid email!"
                            is_info_valid = False
                        elif not validation_obj.validate_password(password):
                            response["status_message"] = "Enter valid password!"
                            is_info_valid = False

                        max_customers_allowed = int(max_customers_allowed)
                        if not is_info_valid:
                            response["status_code"] = 101
                            custom_encrypt_obj = CustomEncrypt()
                            response = custom_encrypt_obj.encrypt(
                                json.dumps(response))
                            return Response(data=response)

                    except Exception:
                        response["status_code"] = 101
                        response[
                            "status_message"] = FILE_UPLOAD_ERROR
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(json.dumps(response))
                        return Response(data=response)

                    # Checking if bot belongs to admin or not
                    bot_id = str(int(sheet.cell_value(row, 6)))
                    bot_obj = Bot.objects.get(pk=bot_id)
                    parent_user = get_admin_from_active_agent(
                        user_obj, LiveChatUser)

                    status = str(int(sheet.cell_value(row, 5)))
                    category_obj = LiveChatCategory.objects.filter(
                        title=category_title, bot=bot_obj, is_deleted=False)

                    is_status_valid = True
                    if status == "1":
                        response["status_message"] = "Not allowed to create an admin"
                        is_status_valid = False
                    elif user_obj.status == "2" and status == "2":
                        response[
                            "status_message"] = "Supervisor cannot create another supervisor"
                        is_status_valid = False
                    elif status != "2" and status != "3":
                        response[
                            "status_message"] = "Please enter correct status of user"
                        is_status_valid = False
                    elif bot_obj not in parent_user.bots.all():
                        response[
                            "status_message"] = "Bot id does not belong to Admin user."
                        is_status_valid = False

                    elif category_obj.count() > 0 and category_obj[0].is_public == False:
                        # checking wheter  category obj exists and category type is private
                        response[
                            "status_message"] = "Cannot create agent as category ( " + category_obj[0].title + " ) is a closing category."
                        is_status_valid = False

                    if not is_status_valid:
                        response["status_code"] = 101
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(json.dumps(response))
                        return Response(data=response)

                    try:
                        easychat_user_obj = User.objects.get(username=username)
                        easychat_user_obj.delete()
                    except Exception:
                        logger.info("Into CreateAgentWithExcelAPI: easychat_user not present.", extra={
                                    'AppName': 'LiveChat'})

                    easychat_user_obj = User.objects.create(
                        email=email, first_name=first_name, last_name=last_name, username=username, password=password, role="customer_care_agent", status="1")

                    try:
                        new_user_obj = LiveChatUser.objects.get(
                            user=easychat_user_obj)
                        new_user_obj.delete()
                    except Exception:
                        logger.info("Into CreateAgentWithExcelAPI: livechat_user not present.", extra={
                                    'AppName': 'LiveChat'})

                    if category_obj.count() > 0:
                        category_obj = category_obj[0]
                    else:
                        category_obj = LiveChatCategory.objects.create(
                            title=category_title, bot=bot_obj)
                        logger.info("Into CreateAgentWithExcelAPI: livechat_category not present.", extra={
                                    'AppName': 'LiveChat'})

                    new_user_obj = LiveChatUser.objects.create(
                        user=easychat_user_obj, status=status, phone_number=phone_number, max_customers_allowed=max_customers_allowed)
                    new_user_obj.category.add(category_obj)
                    new_user_obj.bots.add(bot_obj)
                    new_user_obj.save()

                    if user_obj.status == "1":
                        if supervisors != []:
                            if status == "3":
                                for supervisor in supervisors:
                                    supervisor = str(supervisor).strip()
                                    try:
                                        supervisor_easychat_obj = User.objects.filter(
                                            username=supervisor)[0]
                                        supervisor_obj = LiveChatUser.objects.filter(
                                            user=supervisor_easychat_obj)[0]

                                        is_supervisor_valid = True
                                        if supervisor_obj.status == "1":
                                            response["status_code"] = 101
                                            response[
                                                "status_message"] = "Cannot assign agent to admin"
                                            is_supervisor_valid = False
                                        elif supervisor_obj.status == "3":
                                            response[
                                                "status_message"] = "Cannot assign agent to agent"
                                            is_supervisor_valid = False

                                        if not is_supervisor_valid:
                                            response["status_code"] = 101
                                            custom_encrypt_obj = CustomEncrypt()
                                            response = custom_encrypt_obj.encrypt(
                                                json.dumps(response))
                                            return Response(data=response)

                                        supervisor_obj.agents.add(new_user_obj)
                                        supervisor_obj.category.add(category_obj)
                                        supervisor_obj.save()
                                    except Exception:
                                        response["status_code"] = 101
                                        response[
                                            "status_message"] = supervisor + " does not exist"
                                        custom_encrypt_obj = CustomEncrypt()
                                        response = custom_encrypt_obj.encrypt(
                                            json.dumps(response))
                                        return Response(data=response)

                            # Adding same category to Admin
                            user_obj.category.add(category_obj)
                            user_obj.save()
                        else:
                            user_obj.agents.add(new_user_obj)
                            user_obj.category.add(category_obj)
                            user_obj.save()
                    else:
                        # Adding same category to admin
                        parent_user.category.add(category_obj)
                        parent_user.save()

                        # Adding same category to Supevisor
                        user_obj.agents.add(new_user_obj)
                        user_obj.category.add(category_obj)
                        user_obj.save()

                if duplicate_users:
                    response["status_code"] = 300
                    response["status_message"] = "Success"
                else:
                    response["status_code"] = 200
                    response["status_message"] = "Success"
                    description = "New User(s) has been created for user with id" + \
                        " (" + str(new_user_obj.pk) + ")"
                    add_audit_trail(
                        "LIVECHATAPP",
                        user_obj.user,
                        "Create-User",
                        description,
                        json.dumps(data),
                        request.META.get("PATH_INFO"),
                        request.META.get('HTTP_X_FORWARDED_FOR')
                    )
            else:
                response["status_message"] = f"You cannot add more than a total of {max_users_allowed_to_be_created} user(s) to your account."
                response["status_code"] = "403"
                if is_user_agent:
                    response["status_message"] = INVALID_OPERATION
                    response["status_code"] = "500"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CreateAgentWithExcelAPI: %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


CreateAgentWithExcel = CreateAgentWithExcelAPI.as_view()


class DownloadAgentExcelTemplateAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            export_path = None
            export_path_exist = None
            if user_obj.status == "1":
                export_path = ("/files/templates/livechat-agent-create-excel-template" +
                               "/Template_createAgent.xlsx")
                # export_path_exist = path.exists(export_path[1:])
                export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
            elif user_obj.status == "2":
                export_path = ("/files/templates/livechat-agent-create-excel-template" +
                               "/Template_createAgent_bySupervisor.xlsx")
                # export_path_exist = path.exists(export_path[1:])
                export_path_exist = path.exists(str(settings.BASE_DIR + export_path))

            response["status"] = 200
            response["export_path"] = export_path
            response["export_path_exist"] = export_path_exist
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DownloadAgentExcelTemplateAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


DownloadAgentExcelTemplate = DownloadAgentExcelTemplateAPI.as_view()


class DeleteAgentAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            livechat_user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            livechat_user_obj = check_if_livechat_only_admin(livechat_user_obj, LiveChatUser)

            is_user_agent = livechat_user_obj.status == "3"
            if not is_user_agent:
                data = DecryptVariable(request.data["json_string"])
                data = json.loads(data)

                selected_users = data["selected_users"]
                user_objs = LiveChatUser.objects.filter(
                    pk__in=selected_users, is_deleted=False)

                for user_obj in user_objs:
                    if user_obj.status == '2':
                        agents = user_obj.agents.filter(is_deleted=False)
                        admin = get_admin_from_active_agent(user_obj, LiveChatUser)

                        for agent in agents:
                            user_obj.agents.remove(agent)
                            admin.agents.add(agent)
                        
                        admin.save()

                    user_obj.is_deleted = True
                    user_obj.save()

                    group_member_objs = LiveChatInternalChatGroupMembers.objects.filter(
                        user=user_obj)
                    for group_member_obj in group_member_objs:
                        group_obj = group_member_obj.group
                        group_obj.members.remove(group_member_obj)

                    user_group_objs = LiveChatInternalUserGroup.objects.filter(
                        members__in=[user_obj])
                    for user_group in user_group_objs:
                        user_group.members.remove(user_obj)

                response["status_code"] = "200"
                description = "User/s deleted with id/s" + \
                    " (" + str(selected_users) + ")"
                add_audit_trail(
                    "LIVECHATAPP",
                    livechat_user_obj.user,
                    "Delete-User",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )
            else:
                response["status_code"] = "500"
                response["status_message"] = INVALID_OPERATION

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DeleteAgentAPI: %s at %s", e, str(
                exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class ExportLiveChatUsersAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            livechat_user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            livechat_user_obj = check_if_livechat_only_admin(livechat_user_obj, LiveChatUser)

            is_user_agent = livechat_user_obj.status == "3"
            if not is_user_agent:
                data = DecryptVariable(request.data["json_string"])
                data = json.loads(data)

                users_list = data["users_list"]
                user_objs = LiveChatUser.objects.filter(
                    pk__in=users_list, is_deleted=False).select_related('user').order_by('status', '-pk')

                export_status, export_path = get_export_users_status(livechat_user_obj, user_objs, LiveChatUser, LiveChatFileAccessManagement)

                response["status_code"] = "200"
                response["status_message"] = "Success"
                response["export_path"] = export_path
                response["export_status"] = export_status

            else:
                response["status_code"] = "500"
                response["status_message"] = INVALID_OPERATION

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ExportLiveChatUsersAPI: %s at %s", e, str(
                exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class UpdateCustomerListAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            agent_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            if agent_obj.status == "1":
                response["status_code"] = "300"
                response["status_message"] = "SUCCESS"
                response["customer_list"] = []

                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            if 'assigned_customer_count' in data:
                assigned_customer_count = data["assigned_customer_count"]
            else:
                assigned_customer_count = 0
                
            response["assigned_customer_count"] = assigned_customer_count
            response["new_assigned_customer_count"] = 0
            response["customer_list"] = []

            admin_config = get_admin_config(agent_obj, LiveChatAdminConfig, LiveChatUser)

            customer_objs = LiveChatCustomer.objects.filter(
                Q(agent_id=agent_obj, is_session_exp=False) | Q(guest_agents=agent_obj, is_session_exp=False)).distinct().order_by('-last_appearance_date')

            unread_threads = customer_objs.filter(
                unread_message_count__gte=1).count()

            for customer_obj in customer_objs:
                livechat_config_obj = LiveChatConfig.objects.get(
                    bot=customer_obj.bot)

                guest_agents_list = customer_obj.guest_agents.all()
                guest_session_status_obj = json.loads(
                    customer_obj.guest_session_status)
                pending_guest_agents = []

                chat_escalation_status = "safe"
                if admin_config.is_chat_escalation_matrix_enabled:
                    chat_escalation_status = get_chat_escalation_status(customer_obj, LiveChatMISDashboard, LiveChatReportedCustomer)

                for guest_agent in guest_agents_list:
                    if(guest_session_status_obj[guest_agent.user.username] == "onhold"):
                        pending_guest_agents.append(guest_agent.user.username)

                to_show_language_translate_prompt = True
                if agent_obj.preferred_languages.count() == 1 and customer_obj.customer_language in agent_obj.preferred_languages.all():
                    to_show_language_translate_prompt = False

                customer_language = "en"
                customer_language_display = "English"

                if customer_obj.customer_language:
                    customer_language = customer_obj.customer_language.lang
                    customer_language_display = customer_obj.customer_language.name_in_english

                is_email_chat_to_be_resolved = check_if_email_chat_to_be_resolved(customer_obj, admin_config, LiveChatEmailConfig, LiveChatMISDashboard, LiveChatMISEmailData)

                if customer_obj.is_online:
                    if agent_obj in customer_obj.guest_agents.all():
                        guest_session_status = guest_session_status_obj[agent_obj.user.username]
                        response["customer_list"].append({"unread_message_count": customer_obj.unread_message_count, "session_id": str(customer_obj.session_id), "username": customer_obj.username, "agent_username": str(
                            request.user.username), "last_appearance_time": get_date(customer_obj.last_appearance_date), "sent_by": get_sender_name(customer_obj, LiveChatMISDashboard), "previous_message": get_one_previous_message(customer_obj, admin_config, LiveChatMISDashboard), "is_online": "online",
                            "bot_id": customer_obj.bot.pk, "chat_ended_by": customer_obj.chat_ended_by, "guest_session": "true", "guest_session_status": guest_session_status, "primary_agent_username": customer_obj.agent_id.user.username, "guest_agent_timer": livechat_config_obj.guest_agent_timer, "pending_guest_agents": pending_guest_agents, "is_self_assigned_chat": customer_obj.is_self_assigned_chat,
                            "is_external": customer_obj.is_external, "customer_language": customer_language, "customer_language_display": customer_language_display, "to_show_language_translate_prompt": to_show_language_translate_prompt, "chat_escalation_status": chat_escalation_status, "customer_channel": customer_obj.channel.name, "is_email_chat_to_be_resolved": is_email_chat_to_be_resolved})
                    else:
                        if customer_obj.guest_agents.exists():
                            guest_session_status = "accept"
                        else:
                            guest_session_status = "reject"
                        response["customer_list"].append({"unread_message_count": customer_obj.unread_message_count, "session_id": str(customer_obj.session_id), "username": customer_obj.username, "agent_username": str(
                            request.user.username), "last_appearance_time": get_date(customer_obj.last_appearance_date), "sent_by": get_sender_name(customer_obj, LiveChatMISDashboard), "previous_message": get_one_previous_message(customer_obj, admin_config, LiveChatMISDashboard), "is_online": "online",
                            "bot_id": customer_obj.bot.pk, "chat_ended_by": customer_obj.chat_ended_by, "guest_session": "false", "guest_session_status": guest_session_status, "primary_agent_username": customer_obj.agent_id.user.username, "guest_agent_timer": livechat_config_obj.guest_agent_timer, "pending_guest_agents": pending_guest_agents, "is_self_assigned_chat": customer_obj.is_self_assigned_chat,
                            "is_external": customer_obj.is_external, "customer_language": customer_language, "customer_language_display": customer_language_display, "to_show_language_translate_prompt": to_show_language_translate_prompt, "chat_escalation_status": chat_escalation_status, "customer_channel": customer_obj.channel.name, "is_email_chat_to_be_resolved": is_email_chat_to_be_resolved})
                else:
                    if agent_obj in customer_obj.guest_agents.all():
                        guest_session_status = guest_session_status_obj[agent_obj.user.username]
                        response["customer_list"].append({"unread_message_count": customer_obj.unread_message_count, "session_id": str(customer_obj.session_id), "username": customer_obj.username, "agent_username": str(
                            request.user.username), "last_appearance_time": get_date(customer_obj.last_appearance_date), "sent_by": get_sender_name(customer_obj, LiveChatMISDashboard), "previous_message": get_one_previous_message(customer_obj, admin_config, LiveChatMISDashboard), "is_online": "offline",
                            "bot_id": customer_obj.bot.pk, "chat_ended_by": customer_obj.chat_ended_by, "guest_session": "true", "guest_session_status": guest_session_status, "primary_agent_username": customer_obj.agent_id.user.username, "guest_agent_timer": livechat_config_obj.guest_agent_timer, "pending_guest_agents": pending_guest_agents, "is_self_assigned_chat": customer_obj.is_self_assigned_chat,
                            "is_external": customer_obj.is_external, "customer_language": customer_language, "customer_language_display": customer_language_display, "to_show_language_translate_prompt": to_show_language_translate_prompt, "chat_escalation_status": chat_escalation_status, "customer_channel": customer_obj.channel.name, "is_email_chat_to_be_resolved": is_email_chat_to_be_resolved})
                    else:
                        if customer_obj.guest_agents.exists():
                            guest_session_status = "accept"
                        else:
                            guest_session_status = "reject"
                        response["customer_list"].append({"unread_message_count": customer_obj.unread_message_count, "session_id": str(customer_obj.session_id), "username": customer_obj.username, "agent_username": str(
                            request.user.username), "last_appearance_time": get_date(customer_obj.last_appearance_date), "sent_by": get_sender_name(customer_obj, LiveChatMISDashboard), "previous_message": get_one_previous_message(customer_obj, admin_config, LiveChatMISDashboard), "is_online": "offline",
                            "bot_id": customer_obj.bot.pk, "chat_ended_by": customer_obj.chat_ended_by, "guest_session": "false", "guest_session_status": guest_session_status, "primary_agent_username": customer_obj.agent_id.user.username, "guest_agent_timer": livechat_config_obj.guest_agent_timer, "pending_guest_agents": pending_guest_agents, "is_self_assigned_chat": customer_obj.is_self_assigned_chat,
                            "is_external": customer_obj.is_external, "customer_language": customer_language, "customer_language_display": customer_language_display, "to_show_language_translate_prompt": to_show_language_translate_prompt, "chat_escalation_status": chat_escalation_status, "customer_channel": customer_obj.channel.name, "is_email_chat_to_be_resolved": is_email_chat_to_be_resolved})

            total_assigned_customer = customer_objs.count()
            if total_assigned_customer:
                response["new_assigned_customer_count"] = max(
                    0, total_assigned_customer - int(assigned_customer_count))
                response["assigned_customer_count"] = total_assigned_customer
                response["status_code"] = "200"
                response["status_message"] = "SUCCESS"
                response["unread_threads"] = unread_threads
                response['cobrowsing_guest_info'] = get_cobrowsing_info_based_guest_agent(agent_obj, LiveChatCobrowsingData, LiveChatCustomer)

            else:
                response["status_code"] = "300"
                response["status_message"] = "SUCCESS"
                response["assigned_customer_count"] = total_assigned_customer
                response["customer_list"] = []
                response['cobrowsing_guest_info'] = []
            
            livechat_session_obj = LiveChatSessionManagement.objects.filter(user=agent_obj, session_completed=False)
            if(livechat_session_obj.exists()):
                livechat_session_obj = livechat_session_obj[0]
                total_online_customer = customer_objs.filter(is_online=True).count()
                if total_online_customer > 0 and livechat_session_obj.is_idle:
                    livechat_session_obj.is_idle = False
                    time_diff = datetime.datetime.now(timezone.utc) - livechat_session_obj.last_idle_time
                    livechat_session_obj.idle_time += time_diff.seconds
                    livechat_session_obj.save()
                if total_online_customer == 0 and livechat_session_obj.is_idle == False and agent_obj.is_online:
                    livechat_session_obj.is_idle = True
                    livechat_session_obj.last_idle_time = datetime.datetime.now()
                    livechat_session_obj.save()
            
            response['cobrowsing_guest_info'] = get_cobrowsing_info_based_guest_agent(agent_obj, LiveChatCobrowsingData, LiveChatCustomer)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("UpdateCustomerListAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = e

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class CheckCustomersAreAssignedAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            agent_obj = LiveChatUser.objects.filter(user=request.user, is_deleted=False).first()

            is_customer_assigned = LiveChatCustomer.objects.filter(
                Q(agent_id=agent_obj, is_session_exp=False) | Q(guest_agents=agent_obj, is_session_exp=False)).filter(~Q(channel__name="Email")).distinct().exists()

            response["status_code"] = "200"
            response["status_message"] = "SUCCESS"
            response["is_customer_assigned"] = is_customer_assigned

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CheckCustomersAreAssignedAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


CheckCustomersAreAssigned = CheckCustomersAreAssignedAPI.as_view()


class MarkCustomerOfflineAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = request.data
            session_id = data["session_id"]
            customer_obj = LiveChatCustomer.objects.get(session_id=session_id)
            customer_obj.last_appearance_date = timezone.now()
            customer_obj.save()
            response["status_code"] = "200"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("MarkCustomerOfflineAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveSystemSettingsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = LiveChatInputValidation()

            auto_bot_response = validation_obj.remo_html_from_string(
                data["auto_bot_response"])
            agent_unavialable_response = validation_obj.remo_html_from_string(
                data["agent_unavialable_response"])
            queue_timer = data["queue_timer"]
            bot_pk = validation_obj.remo_html_from_string(
                data["select_bot_obj_pk"])
            show_version_footer = validation_obj.remo_html_from_string(
                data["show_version_footer"])
            theme_color = validation_obj.remo_html_from_string(
                data["theme_color"])
            masking_enabled = data["masking_enabled"]
            token = data["token"]
            auto_chat_disposal_enabled = data["auto_chat_disposal_enabled"]
            is_virtual_interpretation_enabled = data["is_virtual_interpretation_enabled"]
            user_terminates_chat_enabled = data["user_terminates_chat_enabled"]
            user_terminates_chat_dispose_time = data["user_terminates_chat_dispose_time"]
            session_inactivity_enabled = data["session_inactivity_enabled"]
            session_inactivity_chat_dispose_time = data["session_inactivity_chat_dispose_time"]
            is_supervisor_allowed_to_create_group = data["is_supervisor_allowed_to_create_group"]
            is_followup_lead_enabled = data["is_followup_lead_enabled"]
            followup_lead_sources = data["followup_lead_sources"]
            is_whatsapp_reinitiation_enabled = data["is_whatsapp_reinitiation_enabled"]
            whatsapp_reinitiating_text = data["whatsapp_reinitiating_text"]
            whatsapp_reinitiating_keyword = data["whatsapp_reinitiating_keyword"]

            whatsapp_reinitiating_text = validation_obj.remo_html_from_string(whatsapp_reinitiating_text)
            whatsapp_reinitiating_keyword = validation_obj.remo_html_from_string(whatsapp_reinitiating_keyword)

            if len(agent_unavialable_response) > LIVECHAT_CHARACTER_LIMIT_LARGE_TEXT:
                response["status_code"] = "400"
                response["status_message"] = "Agent not available bot response is too long."

            if len(agent_unavialable_response) == 0:
                response["status_code"] = "400"
                response["status_message"] = "Agent unavailable bot response cannot be empty."

            if not validation_obj.alphanumeric(agent_unavialable_response):
                response["status_code"] = "400"
                response["status_message"] = "Kindly enter alphanumeric text only in Agent not available bot response"

            if len(auto_bot_response) > LIVECHAT_CHARACTER_LIMIT_LARGE_TEXT:
                response["status_code"] = "400"
                response["status_message"] = "Non working hour bot response is too long."

            if not validation_obj.alphanumeric(auto_bot_response):
                response["status_code"] = "400"
                response["status_message"] = "Kindly enter alphanumeric text only in Non working hour bot response"

            if (auto_chat_disposal_enabled) and (not isinstance(user_terminates_chat_dispose_time, int) or not isinstance(session_inactivity_chat_dispose_time, int)):
                response["status_code"] = "400"
                response["status_message"] = 'Please enter integer value between 1 and 59 in "Time after which chat should dispose"'

            if not isinstance(queue_timer, int):
                response["status_code"] = "400"
                response["status_message"] = 'Please enter integer value in "Queue time"'
            
            if queue_timer > 600:
                response["status_code"] = "400"
                response["status_message"] = 'Queue Time must be less than or equal to 600'

            if is_followup_lead_enabled and len(followup_lead_sources) == 0:
                response["status_code"] = "400"
                response["status_message"] = 'Please select atleast one source of leads'

            if is_whatsapp_reinitiation_enabled and whatsapp_reinitiating_text.strip() == "":
                response["status_code"] = "400"
                response["status_message"] = "Reinitiating text to be sent on whatsapp cannot be empty."     

            if is_whatsapp_reinitiation_enabled and len(whatsapp_reinitiating_text) > LIVECHAT_CHARACTER_LIMIT_LARGE_TEXT:
                response["status_code"] = "400"
                response["status_message"] = "Reinitiating text to be sent on whatsapp is too long."     

            if is_whatsapp_reinitiation_enabled and whatsapp_reinitiating_keyword.strip() == "":
                response["status_code"] = "400"
                response["status_message"] = "Keywords to detect reinitiation cannot be empty."

            if is_whatsapp_reinitiation_enabled and len(whatsapp_reinitiating_keyword) > LIVECHAT_CHARACTER_LIMIT_MEDIUM_TEXT:
                response["status_code"] = "400"
                response["status_message"] = "Keywords to detect reinitiation is too long."

            if check_if_whatsapp_keyword_present_in_intent(bot_pk, is_whatsapp_reinitiation_enabled, whatsapp_reinitiating_keyword, Bot, Intent, LiveChatConfig): 
                response["status_code"] = "400"
                response["status_message"] = "Keywords/Phrase for detection is already used in an intent, please try another Keyword/Phrase."

            if response["status_code"] == "400":
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            livechat_config_obj = LiveChatConfig.objects.get(
                bot=Bot.objects.get(pk=bot_pk))
            user_status = user_obj.status
            if user_status == "1":
                try:
                    admin_config_obj = LiveChatAdminConfig.objects.get(
                        admin=user_obj, livechat_config__in=[livechat_config_obj])
                    admin_config_obj.livechat_theme_color = theme_color
                    admin_config_obj.show_version_footer = show_version_footer
                    admin_config_obj.is_supervisor_allowed_to_create_group = is_supervisor_allowed_to_create_group

                    livechat_config_obj.agent_unavialable_response = agent_unavialable_response
                    livechat_config_obj.auto_bot_response = auto_bot_response
                    livechat_config_obj.queue_timer = queue_timer

                    if masking_enabled:
                        livechat_config_obj.masking_enabled = masking_enabled
                    elif livechat_config_obj.masking_enabled:
                        data_toggle_obj = LiveChatPIIDataToggle.objects.get(
                            user=user_obj, bot=(Bot.objects.get(pk=int(bot_pk))))

                        if data_toggle_obj and not data_toggle_obj.is_expired:
                            generated_token = str(data_toggle_obj.token)
                            if token == generated_token:
                                livechat_config_obj.masking_enabled = masking_enabled
                                data_toggle_obj.is_expired = True
                                data_toggle_obj.save()
                            else:
                                logger.info("%s is trying to change the data masking toggle unethically", str(request.user.username), extra={
                                    'AppName': 'LiveChat'})
                        else:
                            logger.info("%s is trying to change the data masking toggle unethically", str(request.user.username), extra={
                                'AppName': 'LiveChat'})

                    livechat_config_obj.auto_chat_disposal_enabled = auto_chat_disposal_enabled

                    if auto_chat_disposal_enabled:
                        livechat_config_obj.user_terminates_chat_enabled = user_terminates_chat_enabled

                        if user_terminates_chat_enabled:
                            livechat_config_obj.user_terminates_chat_dispose_time = user_terminates_chat_dispose_time

                        livechat_config_obj.session_inactivity_enabled = session_inactivity_enabled

                        if session_inactivity_enabled:
                            livechat_config_obj.session_inactivity_chat_dispose_time = session_inactivity_chat_dispose_time

                    livechat_config_obj.is_followup_lead_enabled = is_followup_lead_enabled
                    livechat_config_obj.followup_lead_sources = json.dumps(followup_lead_sources)

                    livechat_config_obj.is_whatsapp_reinitiation_enabled = is_whatsapp_reinitiation_enabled
                    livechat_config_obj.whatsapp_reinitiating_text = whatsapp_reinitiating_text
                    previous_reinitiating_keyword = livechat_config_obj.whatsapp_reinitiating_keyword
                    livechat_config_obj.whatsapp_reinitiating_keyword = whatsapp_reinitiating_keyword
                    livechat_config_obj.is_virtual_interpretation_enabled = is_virtual_interpretation_enabled

                    if is_whatsapp_reinitiation_enabled:
                        store_keyword_for_livechat_intent(bot_pk, whatsapp_reinitiating_keyword, previous_reinitiating_keyword, Bot)

                    livechat_config_obj.save()
                    admin_config_obj.save()
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("SaveSystemSettingsAPI: %s at %s",
                                 e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
                    response["status_message"] = str(e)
                    response["status_code"] = "302"
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                response["status_code"] = "200"
                description = "Updated System settings for bot_id" + \
                    " (" + str(bot_pk) + ")"
                add_audit_trail(
                    "LIVECHATAPP",
                    user_obj.user,
                    "Update-Settings",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveSystemSettingsAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = e

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveInteractionSettingsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = LiveChatInputValidation()

            max_customer_count = data["max_customer_count"]
            category_enabled = validation_obj.remo_html_from_string(
                data["category_enabled"])
            bot_pk = validation_obj.remo_html_from_string(
                data["select_bot_obj_pk"])
            max_guest_agent = data["max_guest_agent"]
            guest_agent_timer = data["guest_agent_timer"]
            is_self_assign_chat_agent_enabled = data["is_self_assign_chat_agent_enabled"]
            is_agent_raise_ticket_functionality_enabled = data["is_agent_raise_ticket_functionality_enabled"]
            is_customer_details_editing_enabled = data["is_customer_details_editing_enabled"]
            is_cobrowsing_enabled = data["is_cobrowsing_enabled"]
            is_chat_escalation_matrix_enabled = data["is_chat_escalation_matrix_enabled"]
            is_transcript_enabled = data["is_transcript_enabled"]

            call_type = data['call_type']
            is_call_from_customer_end_enabled = data['is_call_from_customer_end_enabled']

            if not isinstance(max_customer_count, int):
                response["status_code"] = "400"
                response["status_message"] = 'Please enter integer value in "Maximum number of customers with whom an agent can chat at a time"'

            if max_customer_count > LIVECHAT_MAX_CUSTOMER_ALLOWED_FOR_AGENT or max_customer_count <= 0:
                response["status_code"] = "400"
                response["status_message"] = 'Please enter integer value between 1 and 100 in "Maximum number of customers with whom an agent can chat at a time"'

            if max_guest_agent != "1" and max_guest_agent != "2" and max_guest_agent != "3":
                response["status_code"] = "400"
                response["status_message"] = 'Maximum guest agents can be either 1, 2 or 3.'

            if not isinstance(guest_agent_timer, int):
                response["status_code"] = "400"
                response["status_message"] = 'Please enter integer value in "Pending time for accept/reject guest agent field"'

            if guest_agent_timer > 600:
                response["status_code"] = "400"
                response["status_message"] = '"Pending time for accept/reject guest agent field" must be less than or equal to 600'

            if response["status_code"] == "400":
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            livechat_config_obj = LiveChatConfig.objects.get(
                bot=Bot.objects.get(pk=bot_pk))
            user_status = user_obj.status
            if user_status == "1":
                try:
                    admin_config_obj = LiveChatAdminConfig.objects.get(
                        admin=user_obj, livechat_config__in=[livechat_config_obj])
                    admin_config_obj.is_self_assign_chat_agent_enabled = is_self_assign_chat_agent_enabled
                    admin_config_obj.is_chat_escalation_matrix_enabled = is_chat_escalation_matrix_enabled
                    livechat_config_obj.is_transcript_enabled = is_transcript_enabled
                    
                    livechat_config_obj.is_customer_details_editing_enabled = is_customer_details_editing_enabled

                    livechat_config_obj.max_customer_count = max_customer_count
                    livechat_config_obj.category_enabled = category_enabled
                    livechat_config_obj.max_guest_agent = max_guest_agent

                    if guest_agent_timer <= 15:
                        guest_agent_timer = 15
                    livechat_config_obj.guest_agent_timer = guest_agent_timer

                    livechat_config_obj.call_type = call_type

                    if call_type != 'none':
                        if call_type == 'video_call':
                            livechat_config_obj.is_livechat_vc_enabled = True
                            livechat_config_obj.is_voip_enabled = False
                        else:    
                            livechat_config_obj.is_voip_enabled = True
                            livechat_config_obj.is_livechat_vc_enabled = False

                        livechat_config_obj.is_call_from_customer_end_enabled = is_call_from_customer_end_enabled
                    else:
                        livechat_config_obj.is_voip_enabled = False
                        livechat_config_obj.is_livechat_vc_enabled = False

                    livechat_config_obj.is_agent_raise_ticket_functionality_enabled = is_agent_raise_ticket_functionality_enabled
                    livechat_config_obj.is_cobrowsing_enabled = is_cobrowsing_enabled

                    livechat_config_obj.save()
                    admin_config_obj.save()
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("SaveInteractionSettingsAPI: %s at %s",
                                 e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
                    response["status_message"] = str(e)
                    response["status_code"] = "302"
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                response["status_code"] = "200"
                description = "Updated Interaction settings for bot_id" + \
                    " (" + str(bot_pk) + ")"
                add_audit_trail(
                    "LIVECHATAPP",
                    user_obj.user,
                    "Update-Settings",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveInteractionSettingsAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = e

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class CreateNewCannedResponseAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            user_obj = LiveChatUser.objects.get(user=User.objects.get(
                username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = LiveChatInputValidation()

            title = data["title"]
            keyword = data["keyword"]
            canned_response = data["response"]
            status = data["status"]

            admin = get_admin_from_active_agent(user_obj, LiveChatUser)
            config = LiveChatAdminConfig.objects.get(admin=admin)
            character_set = set(canned_response).intersection(
                config.canned_response_config)
            if len(character_set) > 0:
                characters = " ".join(character_set)
                response["status_code"] = "302"
                response["status_message"] = characters + \
                    NOT_ALLOWED_IN_CANNED_RESPONSE
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            title = validation_obj.remo_html_from_string(title)
            keyword = validation_obj.remo_html_from_string(keyword)
            canned_response = validation_obj.remo_html_from_string(
                canned_response)
            status = validation_obj.remo_html_from_string(status)
            title = validation_obj.remo_special_tag_from_string(title)
            keyword = validation_obj.remo_special_tag_from_string(keyword)
            canned_response = validation_obj.remo_special_tag_from_string(
                canned_response)

            if len(keyword.strip()) > LIVECHAT_CHARACTER_LIMIT_SMALL_TEXT:
                response["status_code"] = "400"
                response["status_message"] = EXCEEDING_CHARACTER_LIMIT + \
                    str(LIVECHAT_CHARACTER_LIMIT_SMALL_TEXT) + \
                    CHARACTERS_IN_KEYWORD

            if len(keyword.strip()) == 0:
                response["status_code"] = "400"
                response["status_message"] = KEYWORD_CANNOT_BE_EMPTY

            if len(canned_response.strip()) > LIVECHAT_CHARACTER_LIMIT_LARGE_TEXT:
                response["status_code"] = "400"
                response["status_message"] = EXCEEDING_CHARACTER_LIMIT + \
                    str(LIVECHAT_CHARACTER_LIMIT_LARGE_TEXT) + \
                    CHARACTERS_IN_CANNED_RESPONSE

            if len(canned_response.strip()) == 0:
                response["status_code"] = "400"
                response["status_message"] = CANNED_RESPONSE_CANNOT_BE_EMPTY

            if response["status_code"] == "400":
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            canned_response_list = get_canned_response_for_current_agent(
                user_obj, CannedResponse, LiveChatUser)
            if canned_response_list.filter(keyword=keyword.strip()).count():
                response["status_code"] = "300"
                response["status_message"] = "DUPLICATE"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            # splitting canned response and creating all_blacklisted_keywords lst
            # checking if intersection is present
            blacklisted_keyword = get_blacklisted_keyword_for_current_agent(
                user_obj, LiveChatBlackListKeyword, LiveChatUser)

            for item in blacklisted_keyword:
                if item.word.lower() in canned_response.lower().strip():
                    response["status_code"] = "301"
                    response[
                        "status_message"] = "CANNED RESPONSE CONTAINS BLACKLISTED WORD"
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

            CannedResponse.objects.create(status=status, agent_id=user_obj, title=title,
                                          keyword=keyword, response=canned_response, is_deleted=False)
            response["status_code"] = "200"
            response["status_message"] = "SUCCESS"
            description = "Added Canned response for id" + \
                " (" + str(user_obj.pk) + ")"
            add_audit_trail(
                "LIVECHATAPP",
                user_obj.user,
                "Add-Canned-response",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CreateNewCannedResponseAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = e

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class CreateCannedResponseWithExcelAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        logger.info("Into CreateAgentWithExcelAPI..",
                    extra={'AppName': 'LiveChat'})
        response = {}
        response["status_code"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            user_obj = LiveChatUser.objects.get(user=User.objects.get(
                username=str(request.user.username)), is_deleted=False)
            data = request.data

            validation_obj = LiveChatInputValidation()

            file_path = settings.MEDIA_ROOT + data['src']

            wb = xlrd.open_workbook(file_path)
            sheet = wb.sheet_by_index(0)
            character_set = set()

            admin = get_admin_from_active_agent(user_obj, LiveChatUser)
            config = LiveChatAdminConfig.objects.get(admin=admin)

            for row in range(1, sheet.nrows):
                canned_response = str(sheet.cell_value(row, 1)).strip()
                character_set.update(set(canned_response).intersection(
                    config.canned_response_config))

            if len(character_set) > 0:
                characters = " ".join(character_set)
                response["status_code"] = "302"
                response["status_message"] = characters + \
                    NOT_ALLOWED_IN_CANNED_RESPONSE
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            is_duplicate_count = 0
            for row in range(1, sheet.nrows):
                is_duplicate = False
                try:
                    title = "None"
                    keyword = str(sheet.cell_value(row, 0)).strip()
                    canned_response = str(sheet.cell_value(row, 1)).strip()
                    status = str(data['canned-status'])

                    keyword = validation_obj.remo_html_from_string(keyword)
                    canned_response = validation_obj.remo_html_from_string(
                        canned_response)
                    status = validation_obj.remo_html_from_string(status)

                    keyword = validation_obj.remo_special_tag_from_string(
                        keyword)
                    keyword = keyword.strip()
                    canned_response = validation_obj.remo_special_tag_from_string(
                        canned_response)
                    canned_response = canned_response.strip()

                    if len(keyword) > LIVECHAT_CHARACTER_LIMIT_SMALL_TEXT:
                        response["status_code"] = "400"
                        response["status_message"] = EXCEEDING_CHARACTER_LIMIT + \
                            str(LIVECHAT_CHARACTER_LIMIT_SMALL_TEXT) + \
                            CHARACTERS_IN_KEYWORD

                    if len(keyword) == 0:
                        response["status_code"] = "400"
                        response["status_message"] = KEYWORD_CANNOT_BE_EMPTY

                    if len(canned_response) > LIVECHAT_CHARACTER_LIMIT_LARGE_TEXT:
                        response["status_code"] = "400"
                        response["status_message"] = EXCEEDING_CHARACTER_LIMIT + \
                            str(LIVECHAT_CHARACTER_LIMIT_LARGE_TEXT) + \
                            CHARACTERS_IN_CANNED_RESPONSE

                    if len(canned_response) == 0:
                        response["status_code"] = "400"
                        response["status_message"] = CANNED_RESPONSE_CANNOT_BE_EMPTY

                    if not validation_obj.validate_keyword(keyword):
                        response["status_code"] = "400"
                        response["status_message"] = "Please enter a valid keyword"

                    if not validation_obj.validate_canned_response(canned_response):
                        response["status_code"] = "400"
                        response["status_message"] = "Please enter a valid canned response."

                    if response["status_code"] == "400":
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)

                    canned_response_list = get_canned_response_for_current_agent(
                        user_obj, CannedResponse, LiveChatUser)
                    if canned_response_list.filter(keyword=keyword.strip()).count():
                        is_duplicate = True
                        is_duplicate_count += 1

                    # splitting canned response and creating all_blacklisted_keywords lst
                    # checking if intersection is present
                    blacklisted_keyword = get_blacklisted_keyword_for_current_agent(
                        user_obj, LiveChatBlackListKeyword, LiveChatUser)

                    for item in blacklisted_keyword:
                        if item.word.lower() in canned_response.lower().strip():
                            response["status_code"] = "301"
                            response[
                                "status_message"] = "CANNED RESPONSE CONTAINS BLACKLISTED WORD"
                            custom_encrypt_obj = CustomEncrypt()
                            response = custom_encrypt_obj.encrypt(
                                json.dumps(response))
                            return Response(data=response)
                    if is_duplicate == False:
                        if is_duplicate_count == 0 and len(character_set) == 0:
                            CannedResponse.objects.create(status=status, agent_id=user_obj, title=title,
                                                          keyword=keyword, response=canned_response, is_deleted=False)
                            response["status_code"] = "200"
                            response["status_message"] = "SUCCESS"

                        if is_duplicate_count > 0 and len(character_set) == 0:
                            CannedResponse.objects.create(status=status, agent_id=user_obj, title=title,
                                                          keyword=keyword, response=canned_response, is_deleted=False)
                            response["status_code"] = "201"
                            response["status_message"] = "SUCCESS"

                        description = "Added Canned response with excel for id" + \
                            " (" + str(user_obj.pk) + ")"
                        add_audit_trail(
                            "LIVECHATAPP",
                            user_obj.user,
                            "Add-Canned-response",
                            description,
                            json.dumps(data),
                            request.META.get("PATH_INFO"),
                            request.META.get('HTTP_X_FORWARDED_FOR')
                        )

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("CreateCannedResponseWithExcelAPI: %s at %s",
                                 e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
                    response["status_message"] = e
            if is_duplicate_count == sheet.nrows - 1:
                response["status_code"] = "300"
                response["status_message"] = "DUPLICATE"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CreateCannedResponseWithExcelAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = e

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


CreateCannedResponseWithExcel = CreateCannedResponseWithExcelAPI.as_view()


class GetCannedResponseAPI(APIView):

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            user_obj = LiveChatUser.objects.get(user=User.objects.get(
                username=str(request.user.username)), is_deleted=False)
            canned_response_list = get_canned_response_for_current_agent(
                user_obj, CannedResponse, LiveChatUser)
            response["canned_response"] = []
            for item in canned_response_list:
                response["canned_response"].append({
                    "key": item.keyword,
                    "value": item.response,
                    "status": item.status
                })
            response["status_code"] = "200"
            response["status_message"] = "SUCCESS"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetCannedResponseAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = e

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class EditCannedResponseAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = "Canned response can't be created, due to some internal error!"
        try:
            user_obj = LiveChatUser.objects.get(user=User.objects.get(
                username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = LiveChatInputValidation()

            title = data["title"]
            keyword = data["keyword"]
            canned_response = data["response"]
            status = data["status"]
            canned_response_pk = data["canned_response_pk"]
            admin = get_admin_from_active_agent(user_obj, LiveChatUser)
            config = LiveChatAdminConfig.objects.get(admin=admin)
            character_set = set(canned_response).intersection(
                config.canned_response_config)
            if len(character_set) > 0:
                characters = " ".join(character_set)
                response["status_code"] = "302"
                response["status_message"] = characters + \
                    NOT_ALLOWED_IN_CANNED_RESPONSE
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            title = validation_obj.remo_html_from_string(title)
            keyword = validation_obj.remo_html_from_string(keyword)
            canned_response = validation_obj.remo_html_from_string(
                canned_response)
            status = validation_obj.remo_html_from_string(status)
            canned_response_pk = validation_obj.remo_html_from_string(
                str(canned_response_pk))

            title = validation_obj.remo_special_tag_from_string(title)
            keyword = validation_obj.remo_special_tag_from_string(keyword)
            canned_response = validation_obj.remo_special_tag_from_string(
                canned_response)

            if len(keyword.strip()) > LIVECHAT_CHARACTER_LIMIT_SMALL_TEXT:
                response["status_code"] = "400"
                response["status_message"] = EXCEEDING_CHARACTER_LIMIT + \
                    str(LIVECHAT_CHARACTER_LIMIT_SMALL_TEXT) + \
                    CHARACTERS_IN_KEYWORD

            if len(keyword.strip()) == 0:
                response["status_code"] = "400"
                response["status_message"] = KEYWORD_CANNOT_BE_EMPTY

            if len(canned_response.strip()) > LIVECHAT_CHARACTER_LIMIT_LARGE_TEXT:
                response["status_code"] = "400"
                response["status_message"] = EXCEEDING_CHARACTER_LIMIT + \
                    str(LIVECHAT_CHARACTER_LIMIT_LARGE_TEXT) + \
                    CHARACTERS_IN_CANNED_RESPONSE

            if len(canned_response.strip()) == 0:
                response["status_code"] = "400"
                response["status_message"] = CANNED_RESPONSE_CANNOT_BE_EMPTY

            if response["status_code"] == "400":
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            canned_response_obj = CannedResponse.objects.get(
                pk=int(canned_response_pk))
            if canned_response_obj.keyword != keyword:
                canned_response_list = get_canned_response_for_current_agent(
                    user_obj, CannedResponse, LiveChatUser)
                if canned_response_list.filter(keyword=keyword):
                    response["status_code"] = "300"
                    response["status_message"] = "DUPLICATE"
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

            # splitting canned response and creating all_blacklisted_keywords lst
            # checking if intersection is present
            blacklisted_keyword = get_blacklisted_keyword_for_current_agent(
                user_obj, LiveChatBlackListKeyword, LiveChatUser)

            for item in blacklisted_keyword:
                if item.word.lower() in canned_response.lower():
                    response["status_code"] = "301"
                    response[
                        "status_message"] = "CANNED RESPONSE CONTAINS BLACKLISTED WORD"
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)
            canned_response_obj.title = title
            canned_response_obj.keyword = keyword
            canned_response_obj.response = canned_response
            canned_response_obj.status = status
            canned_response_obj.save()
            response["status_code"] = "200"
            response["status_message"] = "SUCCESS"
            description = "Updated Canned response for id" + \
                " (" + str(user_obj.pk) + ")"
            add_audit_trail(
                "LIVECHATAPP",
                user_obj.user,
                "Update-Canned-response",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EditCannedResponseAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = e

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class DeleteCannedResponseAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            canned_response_pk_list = data["canned_response_pk_list"]

            for canned_response in canned_response_pk_list:
                canned_response_obj = CannedResponse.objects.get(
                    pk=int(canned_response))
                canned_response_obj.is_deleted = True
                canned_response_obj.save()
            response["status_code"] = "200"
            response["status_message"] = "SUCCESS"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DeleteCannedResponseAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = e

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveLiveChatFeedbackAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = LiveChatInputValidation()

            session_id = data["session_id"]

            rate_value = data["rate_value"]
            bot_id = data["bot_id"]
            nps_text_feedback = data["nps_text_feedback"]

            session_id = validation_obj.remo_html_from_string(session_id)
            rate_value = validation_obj.remo_html_from_string(str(rate_value))
            bot_id = validation_obj.remo_html_from_string(bot_id)
            nps_text_feedback = validation_obj.remo_html_from_string(nps_text_feedback)
            nps_text_feedback = validation_obj.remo_unwanted_characters(nps_text_feedback)

            if int(rate_value) < -1 or int(rate_value) > 10:
                response["status_code"] = "400"
                response["status_message"] = "Invalid rating"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            
            customer_obj = LiveChatCustomer.objects.get(session_id=session_id)
            customer_obj.rate_value = rate_value
            customer_obj.nps_feedback_date = timezone.now()
            customer_obj.nps_text_feedback = nps_text_feedback
            customer_obj.save()
            response["status_code"] = "200"
            send_event_for_nps(customer_obj, LiveChatUser, LiveChatAdminConfig, LiveChatConfig, Bot)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveLiveChatFeedbackAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = e

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)

###################  Update Last Seen    #################################


class UpdateLastSeenAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        try:
            user_obj = None
            response["status_set_by_admin_supervisor"] = None
            try:
                easychat_user_obj = User.objects.filter(username=str(request.user.username))

                if easychat_user_obj:
                    user_obj = LiveChatUser.objects.get(
                        user=easychat_user_obj.first(), is_deleted=False)

                    time_zone = pytz.timezone(settings.TIME_ZONE)
                    user_obj.last_updated_time = datetime.datetime.now().astimezone(time_zone)

                    user_obj.save(update_fields=['last_updated_time'])

                    if user_obj.current_status == "9" or user_obj.current_status == "10":
                        response["status_set"] = "Offline"
                    if user_obj.current_status == "6":
                        response["status_set"] = "Online"
                    
                    response['status_changed_by_admin_supervisor'] = user_obj.status_changed_by_admin_supervisor
                
                # checking if livechat agent is a cobrowse agent and marking him/her active
                active_agent = get_active_agent_obj(request, CobrowseAgent)
                if active_agent:
                    active_agent.is_active = True
                    active_agent.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("UpdateLastSeenAPI: %s at %s",
                             e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

            response["status"] = 200
            response["message"] = "SUCCESS"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[ENGINE] %s at %s", str(e), str(
                exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status"] = 500
            response["message"] = "Could not update last seen"

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class CreateNewCategoryAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = "Category can't be created, due to some internal error!"
        try:
            livechat_user = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            livechat_user = check_if_livechat_only_admin(
                livechat_user, LiveChatUser)
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = LiveChatInputValidation()

            title = data["title"]
            title = title.strip()
            priority = data["priority"]
            bot_id = data["bot_id"]
            is_public = data["is_public"]
            bot_obj = Bot.objects.get(pk=bot_id)
            category_objs = LiveChatCategory.objects.filter(bot=bot_obj)

            title = validation_obj.remo_html_from_string(title)
            priority = validation_obj.remo_html_from_string(priority)
            title = validation_obj.remo_special_tag_from_string(title)

            if len(title) > LIVECHAT_CHARACTER_LIMIT_SMALL_TEXT:
                response["status_code"] = "400"
                response["status_message"] = EXCEEDING_CHARACTER_LIMIT + \
                    str(LIVECHAT_CHARACTER_LIMIT_SMALL_TEXT) + \
                    " characters in category title"

            if len(title) == 0:
                response["status_code"] = "400"
                response["status_message"] = "Category title cannot be empty"

            if response["status_code"] == "400":
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            response["status_message"] = "SUCCESS"

            for item in category_objs:
                if item.title.lower().strip() == str(title).lower().strip():
                    if item.is_deleted == True:
                        response["status_code"] = "200"
                        item.priority = priority
                        item.is_public = is_public
                        item.is_deleted = False
                        item.save()
                        livechat_user.category.add(item)
                        livechat_user.save()
                        break
                    else:
                        response["status_code"] = "300"

            if response["status_code"] == "500" and livechat_user.status == "1":

                response["status_code"] = "200"
                livechat_category = LiveChatCategory.objects.create(
                    title=title, priority=priority, bot=bot_obj, is_public=is_public)
                livechat_user.category.add(livechat_category)
                livechat_user.save()

            description = "Add Category for bot id" + \
                " (" + str(bot_id) + ")"
            add_audit_trail(
                "LIVECHATAPP",
                livechat_user.user,
                "Add-Category",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside CreateNewCategoryAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_code"] = "500"
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


CreateNewCategory = CreateNewCategoryAPI.as_view()


class EditLiveChatCategoryAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            livechat_user = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = LiveChatInputValidation()

            title = data["title"]
            priority = data["priority"]
            category_pk = data["category_pk"]
            bot_pk = data["bot_id"]
            is_public = data["is_public"]

            title = validation_obj.remo_html_from_string(title)
            priority = validation_obj.remo_html_from_string(priority)
            category_pk = validation_obj.remo_html_from_string(
                str(category_pk))
            title = validation_obj.remo_special_tag_from_string(title)

            if len(title.strip()) > LIVECHAT_CHARACTER_LIMIT_SMALL_TEXT:
                response["status_code"] = "400"
                response["status_message"] = EXCEEDING_CHARACTER_LIMIT + \
                    str(LIVECHAT_CHARACTER_LIMIT_SMALL_TEXT) + \
                    " characters in category title"

            if len(title.strip()) == 0:
                response["status_code"] = "400"
                response["status_message"] = "Category title cannot be empty"

            if response["status_code"] == "400":
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            category_objs = LiveChatCategory.objects.filter(
                bot=Bot.objects.get(pk=int(bot_pk)), is_deleted=False)

            response["status_message"] = "SUCCESS"

            for item in category_objs:
                if item.title.lower().strip() == str(title).lower().strip() and str(item.pk) != str(category_pk):
                    response["status_code"] = "300"

            if response["status_code"] == "500" and livechat_user.status == "1":
                response["status_code"] = "200"
                category_obj = LiveChatCategory.objects.get(
                    pk=int(category_pk))
                category_obj.title = title
                category_obj.priority = priority
                category_obj.bot = Bot.objects.get(pk=bot_pk)
                category_obj.is_public = is_public
                category_obj.save()

            description = "Update Category for bot id" + \
                " (" + str(bot_pk) + " and category_pk " + str(category_pk) + ")"
            add_audit_trail(
                "LIVECHATAPP",
                livechat_user.user,
                "Update-Category",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside EditLiveChatCategoryAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_code"] = "500"
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


EditLiveChatCategory = EditLiveChatCategoryAPI.as_view()


class DeleteLiveChatCategoryAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            livechat_user = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            livechat_user = check_if_livechat_only_admin(
                livechat_user, LiveChatUser)
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            category_pk_list = data["category_pk_list"]

            if livechat_user.status == "1" or livechat_user.is_allow_toggle:
                for item in category_pk_list:
                    category_obj = LiveChatCategory.objects.get(pk=int(item))
                    category_obj.is_deleted = True
                    category_obj.save()

                response["status_message"] = "SUCCESS"
                response["status_code"] = "200"
                description = "Deleted Category(ies) with id(s)" + \
                    " (" + str(category_pk_list) + ")"
                add_audit_trail(
                    "LIVECHATAPP",
                    livechat_user.user,
                    "Delete-Category",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )
            else:
                response["status_code"] = "300"
                response["status_message"] = "Unautherised access"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside DeleteLiveChatCategoryAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_code"] = "500"
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


DeleteLiveChatCategory = DeleteLiveChatCategoryAPI.as_view()


class GetLiveChatCategoryListAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        response["category_list"] = []
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            bot_id = data["bot_id"]
            selected_language = "en"
            if "selected_language" in data:
                selected_language = data["selected_language"]

            config_obj = LiveChatConfig.objects.filter(
                bot=Bot.objects.get(pk=bot_id))
            livechat_admin = LiveChatAdminConfig.objects.filter(
                livechat_config__in=config_obj)[0].admin

            category_list = []
            category_objs = livechat_admin.category.all().filter(
                bot__pk=int(bot_id), is_public=True, is_deleted=False)
            for item in category_objs:
                title = get_translated_text(str(item.title), selected_language, LiveChatTranslationCache)
                category_list.append(
                    {"pk": str(item.pk), "title": title})
            response["status_message"] = "SUCCESS"
            response["status_code"] = "200"
            response["category_list"] = category_list
            if not config_obj[0].category_enabled:
                response["status_code"] = "300"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside GetLiveChatCategoryListAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_code"] = "500"
            response["status_message"] = str(e)
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetLiveChatCategoryList = GetLiveChatCategoryListAPI.as_view()


class SwitchAgentManagerAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["message"] = INTERNAL_SERVER_ERROR
        try:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            if not user_obj.is_allow_toggle:
                response["status_code"] = "300"
                response["message"] = "Unauthorised access"
            else:
                data = urllib.parse.unquote(request.data['json_string'])
                data = DecryptVariable(data)
                data = json.loads(data)

                status = data["status"]
                if status:
                    user_obj.status = "3"
                    response["message"] = "Successfully switched to Agent mode!"
                else:
                    response["message"] = "Successfully switched to Manager mode!"
                    user_obj.status = "1"

                user_obj.save()

                response["status_code"] = "200"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside SwitchAgentManagerAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_code"] = "500"
            response["status_message"] = str(e)
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SwitchAgentManager = SwitchAgentManagerAPI.as_view()


class GetBotUnderUserAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            selected_pk = data["selected_pk"]
            user_obj = LiveChatUser.objects.get(
                pk=int(selected_pk), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            bot_objs = user_obj.bots.all().filter(is_deleted=False)
            response["bot_objs"] = []

            for bot in bot_objs:
                response["bot_objs"].append(
                    {"bot_pk": bot.pk, "bot_name": bot.name})

            response["status_code"] = "200"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside GetBotUnderUser %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_code"] = "500"
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetBotUnderUser = GetBotUnderUserAPI.as_view()


class AddBlacklistedKeywordAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Keyword can't be added, due to some internal error."
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = LiveChatInputValidation()

            user_obj = LiveChatUser.objects.filter(~Q(status="3")).get(
                user=User.objects.get(username=str(request.user.username)))
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            added_words = data["added_words"]
            blacklist_for = data["blacklist_for"]

            if len(added_words) == 0:
                response["status"] = "400"
                response["message"] = KEYWORD_CANNOT_BE_EMPTY
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            all_words_added = True
            for word in added_words:
                word = validation_obj.remo_html_from_string(word)
                word = validation_obj.remo_special_tag_from_string(word)

                if len(word.strip()) > LIVECHAT_CHARACTER_LIMIT_SMALL_TEXT:
                    all_words_added = False
                    continue

                if len(word.strip()) == 0:
                    all_words_added = False
                    continue

                if is_blacklist_keyword_present(word, user_obj, blacklist_for, LiveChatBlackListKeyword, LiveChatUser):
                    all_words_added = False 
                else:
                    LiveChatBlackListKeyword.objects.create(
                        word=word.lower(), agent_id=user_obj, blacklist_keyword_for=blacklist_for)
                    response["status"] = "200"
                    description = "Added Blacklisted word for id" + \
                        " (" + str(user_obj.pk) + ")"
                    add_audit_trail(
                        "LIVECHATAPP",
                        user_obj.user,
                        "Add-Blacklistedkeyword",
                        description,
                        json.dumps(data),
                        request.META.get("PATH_INFO"),
                        request.META.get('HTTP_X_FORWARDED_FOR')
                    )

            response['status'] = 200
            response['message'] = 'success'
            response['all_words_added'] = all_words_added
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside AddBlacklistedKeywordAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_code"] = "500"
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


AddBlacklistedKeyword = AddBlacklistedKeywordAPI.as_view()


class EditBlacklistedKeywordAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["message"] = "Keyword can't be added, due to some internal error."
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            user_obj = LiveChatUser.objects.filter(~Q(status="3")).get(
                user=User.objects.get(username=str(request.user.username)))
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            word = data["word"]
            pk = data["pk"]
            blacklist_for = data["blacklist_for"]

            if len(word.strip()) > LIVECHAT_CHARACTER_LIMIT_SMALL_TEXT:
                response["status_code"] = "400"
                response["message"] = EXCEEDING_CHARACTER_LIMIT + \
                    str(LIVECHAT_CHARACTER_LIMIT_SMALL_TEXT) + " characters"

            if len(word.strip()) == 0:
                response["status_code"] = "400"
                response["message"] = KEYWORD_CANNOT_BE_EMPTY

            if response["status_code"] == "400":
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if is_blacklist_keyword_present(word, user_obj, blacklist_for, LiveChatBlackListKeyword, LiveChatUser):
                response["status_code"] = "300"
            else:
                keyword_obj = LiveChatBlackListKeyword.objects.get(
                    pk=int(pk), blacklist_keyword_for=blacklist_for)
                keyword_obj.word = word.lower()
                keyword_obj.save()
                response["status_code"] = "200"
                description = "Updated Blacklisted word for id" + \
                    " (" + str(pk) + ")"
                add_audit_trail(
                    "LIVECHATAPP",
                    user_obj.user,
                    "Update-Blacklistedkeyword",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside EditBlacklistedKeywordAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_code"] = "500"
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


EditBlacklistedKeyword = EditBlacklistedKeywordAPI.as_view()


class DeleteBlackListedKeywordAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            user_obj = LiveChatUser.objects.filter(~Q(status="3")).get(
                user=User.objects.get(username=str(request.user.username)))
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            blacklisted_keyword_pk_list = data["blacklisted_keyword_pk_list"]

            for pk in blacklisted_keyword_pk_list:
                keyword_obj = LiveChatBlackListKeyword.objects.get(pk=int(pk))
                if ((keyword_obj.agent_id.pk == user_obj.pk) or (keyword_obj.blacklist_keyword_for == "customer" and (keyword_obj.agent_id == get_admin_from_active_agent(user_obj, LiveChatUser) or keyword_obj.agent_id in user_obj.agents.all()))):
                    keyword_obj.delete()

            response["status_code"] = "200"
            description = "Delete Blacklisted word(s) with id list" + \
                " (" + str(blacklisted_keyword_pk_list) + ")"
            add_audit_trail(
                "LIVECHATAPP",
                user_obj.user,
                "Delete-Blacklistedkeyword",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside DeleteBlackListedKeywordAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_code"] = "500"
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


DeleteBlackListedKeyword = DeleteBlackListedKeywordAPI.as_view()


class SwitchAgentStatusAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            status = data["status"]
            selected_status = data["selected_status"]
            pk = data["pk"]
            request_user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            request_user_obj = check_if_livechat_only_admin(
                request_user_obj, LiveChatUser)
            user_obj = LiveChatUser.objects.get(pk=int(pk), is_deleted=False)
            if "status_changed_by_admin_supervisor" in data and request_user_obj.status != "3" and (user_obj in get_agents_under_this_user(request_user_obj)):
                if (is_agent_live(user_obj) == False):
                    response["message"] = "Seems like the agent has logged out"
                    response["status_code"] = "300"
                    user_obj.is_online = False
                    user_obj.save()
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))

                    return Response(data=response)
                if (user_obj.is_online == False and (user_obj.current_status != "9" and user_obj.current_status != "10")):
                    response["message"] = "Seems like the agent is offline"
                    response["status_code"] = "300"
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                user_obj.status_changed_by_admin_supervisor = True if data[
                    "status_changed_by_admin_supervisor"] == "1" else False

            elif request_user_obj != user_obj:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            if status:
                if user_obj.is_online == False:
                    save_session_details(
                        user_obj, "6", LiveChatSessionManagement, LiveChatAgentNotReady, LiveChatUser, LiveChatAdminConfig, LiveChatConfig, Bot)
                    user_obj.current_status = "6"
                    user_obj.is_online = True
                    user_obj.save()
                    save_audit_trail_data("6", user_obj, LiveChatAuditTrail)
                    response[
                        "message"] = "Successfully switched to online(Working) mode."
                else:
                    response["message"] = "User is already online."
            else:
                if user_obj.is_online == True:
                    save_session_details(
                        user_obj, selected_status, LiveChatSessionManagement, LiveChatAgentNotReady, LiveChatUser, LiveChatAdminConfig, LiveChatConfig, Bot)
                    user_obj.is_online = False
                    user_obj.current_status = selected_status
                    user_obj.save()
                    save_audit_trail_data(
                        selected_status, user_obj, LiveChatAuditTrail)
                    response["message"] = "Successfully switched to offline(" + user_obj.get_current_status(
                    ) + ") mode."
                elif user_obj.current_status == "0":
                    save_session_details(
                        user_obj, selected_status, LiveChatSessionManagement, LiveChatAgentNotReady, LiveChatUser, LiveChatAdminConfig, LiveChatConfig, Bot)
                    user_obj.is_online = False
                    user_obj.current_status = selected_status
                    user_obj.save()
                    save_audit_trail_data(
                        selected_status, user_obj, LiveChatAuditTrail)
                    response["message"] = "Offline reason succesfully changed"
                else:
                    response["message"] = "User is already offline"
            response["status_code"] = "200"
            response["status_message"] = "SUCCESS"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SwitchAgentStatusAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SwitchAgentStatus = SwitchAgentStatusAPI.as_view()


UpdateLastSeen = UpdateLastSeenAPI.as_view()
UpdateCustomerList = UpdateCustomerListAPI.as_view()
CreateNewAgent = CreateNewAgentAPI.as_view()
PreviousSessionMessages = PreviousSessionMessagesAPI.as_view()
DeleteAgent = DeleteAgentAPI.as_view()
MarkCustomerOffline = MarkCustomerOfflineAPI.as_view()
SaveSystemSettings = SaveSystemSettingsAPI.as_view()
SaveInteractionSettings = SaveInteractionSettingsAPI.as_view()
CreateNewCannedResponse = CreateNewCannedResponseAPI.as_view()
GetCannedResponse = GetCannedResponseAPI.as_view()
EditCannedResponse = EditCannedResponseAPI.as_view()
DeleteCannedResponse = DeleteCannedResponseAPI.as_view()
SaveLiveChatFeedback = SaveLiveChatFeedbackAPI.as_view()
ExportLiveChatUsers = ExportLiveChatUsersAPI.as_view()


class EditAgentInfoAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            if user_obj.status != "3":
                data = DecryptVariable(request.data["json_string"])
                data = json.loads(data)

                validation_obj = LiveChatInputValidation()

                current_pk = data["current_pk"]
                name = data["name"]
                phone_number = data["phone_number"]
                category_pk_list = data["category_pk_list"]
                max_customers_allowed = data["max_customers_allowed"]
                supervisor_pk = data['supervisor_pk']

                if int(max_customers_allowed) >= LIVECHAT_MAX_CUSTOMER_ALLOWED_FOR_AGENT and int(max_customers_allowed) <= 0:
                    response["status_message"] = "Max customer allowed should be between 1 to 100"
                    response["status_code"] = "301"
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                split_name = name.split()
                first_name = split_name[0]
                if len(split_name) > 1:
                    last_name = split_name[-1]
                else:
                    last_name = ""

                first_name = validation_obj.remo_html_from_string(first_name)
                last_name = validation_obj.remo_html_from_string(last_name)
                phone_number = validation_obj.remo_html_from_string(
                    phone_number)

                first_name = validation_obj.remo_special_tag_from_string(
                    first_name)
                last_name = validation_obj.remo_special_tag_from_string(
                    last_name)

                easychat_user_obj = None
                try:
                    easychat_user_obj = LiveChatUser.objects.get(
                        pk=int(current_pk)).user
                    easychat_user_obj.first_name = first_name
                    easychat_user_obj.last_name = last_name
                    easychat_user_obj.save()
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("EditAgentInfoAPI: %s at %s",
                                 e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
                    easychat_user_obj = None

                if easychat_user_obj != None:
                    new_user_obj = LiveChatUser.objects.get(pk=int(current_pk))
                    new_user_obj.phone_number = phone_number
                    new_user_obj.max_customers_allowed = max_customers_allowed
                    new_user_obj.category.clear()
                    for item in category_pk_list:
                        new_user_obj.category.add(
                            get_livechat_category_object(item, new_user_obj.bots.all()[0], LiveChatCategory))

                    if new_user_obj.status == '3' and supervisor_pk != -1:
                        supervisor_obj = LiveChatUser.objects.filter(pk=supervisor_pk).first()

                        if supervisor_obj and not supervisor_obj.agents.filter(user=easychat_user_obj):
                            if new_user_obj.is_online or is_agent_live(new_user_obj):
                                response["status_code"] = 400
                                response["status_message"] = "Cannot change supervisor while agent is active"
                                custom_encrypt_obj = CustomEncrypt()
                                response = custom_encrypt_obj.encrypt(json.dumps(response))
                                return Response(data=response)
                            
                            prev_supervisor = LiveChatUser.objects.filter(agents__in=[new_user_obj]).first()
                            prev_supervisor.agents.remove(new_user_obj)
                            prev_supervisor.save()

                            supervisor_obj.agents.add(new_user_obj)
                            remove_agent_from_prev_groups(user_obj, new_user_obj, supervisor_obj, LiveChatInternalChatGroup, LiveChatInternalChatGroupMembers, LiveChatInternalMessageInfo, LiveChatInternalMISDashboard)

                    new_user_obj.save()
                    response["status_message"] = "SUCCESS"
                    response["status_code"] = "200"
                    description = "Update User Info with id" + \
                        " (" + str(current_pk) + ")"
                    add_audit_trail(
                        "LIVECHATAPP",
                        easychat_user_obj,
                        "Update-User",
                        description,
                        json.dumps(data),
                        request.META.get("PATH_INFO"),
                        request.META.get('HTTP_X_FORWARDED_FOR')
                    )
                else:
                    response["status_message"] = "SUCCESS"
                    response["status_code"] = "300"
            else:
                response["status_message"] = INVALID_OPERATION
                response["status_code"] = "500"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EditAgentInfoAPI: %s at %s", e, str(
                exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


EditAgentInfo = EditAgentInfoAPI.as_view()


def FileAccess(request, file_key, file_name):
    try:
        username = request.user.username

        livechat_user_obj = LiveChatUser.objects.filter(user__username=request.user.username, is_deleted=False).first()
        if livechat_user_obj:
            livechat_user_obj = check_if_livechat_only_admin(livechat_user_obj, LiveChatUser)
            username = livechat_user_obj.user.username

        file_access_management_obj = LiveChatFileAccessManagement.objects.get(
            key=file_key)
        if request.user.is_authenticated:
            return file_download(file_key, username, LiveChatUser, LiveChatFileAccessManagement)
        elif file_access_management_obj.is_public_to_all_user:
            return file_download(file_key, username, LiveChatUser, LiveChatFileAccessManagement)
        elif is_valid_livechat_file_access_request(file_access_management_obj):
            return file_download(file_key, username, LiveChatUser, LiveChatFileAccessManagement)
        elif file_access_management_obj.is_mailer_report:
            return HttpResponse('This link has been expired')

        else:
            if "source" in request.GET:
                return file_download(file_key, username, LiveChatUser, LiveChatFileAccessManagement)
            if "livechat_session_id" in request.GET:
                session_id = request.GET["livechat_session_id"]
                livechat_cust_obj = LiveChatCustomer.objects.get(
                    session_id=session_id)
                if livechat_cust_obj.is_session_exp == True:
                    return HttpResponse(status=404)
                else:
                    return file_download(file_key, username, LiveChatUser, LiveChatFileAccessManagement)
            return HttpResponse(status=404)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error FileAccess %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponse(status=404)


def LiveChatLogoutPage(request):  # noqa: N802
    if request.user.is_authenticated:

        user = User.objects.get(username=request.user.username)
        user.is_online = False
        user.save()
        secured_login = SecuredLogin.objects.get(user=user)
        secured_login.failed_attempts = 0
        secured_login.save()

        audit_trail_data = json.dumps({
            "user_id": user.pk
        })
        try:
            livechat_user = LiveChatUser.objects.get(user=user)
            sessions_obj = LiveChatSessionManagement.objects.filter(
                user=livechat_user, session_completed=False)[0]
            if sessions_obj.user.is_online:
                diff = timezone.now(timezone.utc) - \
                    sessions_obj.session_ends_at
                sessions_obj.online_time += diff.seconds
                sessions_obj.session_ends_at = timezone.now()
                sessions_obj.session_completed = True
                sessions_obj.is_idle = False
                time_diff = datetime.now(timezone.utc) - sessions_obj.last_idle_time
                sessions_obj.idle_time += time_diff.seconds
                sessions_obj.save()
            else:
                diff = timezone.now(
                    timezone.utc) - sessions_obj.session_ends_at
                sessions_obj.offline_time += diff.seconds
                sessions_obj.session_ends_at = timezone.now()
                sessions_obj.session_completed = True
                if sessions_obj.agent_not_ready.all().count():
                    agent_not_ready_obj = sessions_obj.agent_not_ready.all().order_by(
                        '-not_ready_starts_at')[0]
                    agent_not_ready_obj.not_ready_ends_at = timezone.now()
                    agent_not_ready_obj.save()
                sessions_obj.save()

            livechat_user.is_online = False
            livechat_user.is_session_exp = True
            livechat_user.resolved_chats = 0
            livechat_cust_objs = LiveChatCustomer.objects.filter(
                agent_id=livechat_user, is_session_exp=False)
            for livechat_cust_obj in livechat_cust_objs:
                diff = timezone.now() - livechat_cust_obj.joined_date
                livechat_cust_obj.is_session_exp = True
                livechat_cust_obj.abruptly_closed = True
                livechat_cust_obj.chat_duration = diff.seconds
                livechat_cust_obj.last_appearance_date = timezone.now()
                livechat_cust_obj.chat_ended_by = "System"
                livechat_cust_obj.save()
            livechat_user.save()
            save_audit_trail_data("8", livechat_user, LiveChatAuditTrail)
        except Exception:
            pass

        save_audit_trail(user, USER_LOGGED_OUT, audit_trail_data)

        user_session_obj = UserSession.objects.filter(
            user__username=request.user.username)
        logout(request)
        description = "Logout from the system"
        add_audit_trail(
            "LIVECHATAPP",
            user,
            "Logout",
            description,
            json.dumps({}),
            request.META.get("PATH_INFO"),
        )

        if user_session_obj:
            delete_user_session(user_session_obj[0])

    return HttpResponseRedirect("/livechat/login")


###########################   LiveChat only admin ########################


class CreateNewLiveChatOnlyAdminAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            if user_obj.status == "1" and not user_obj.is_livechat_only_admin:
                data = DecryptVariable(request.data["json_string"])
                data = json.loads(data)

                validation_obj = LiveChatInputValidation()

                name = data["name"]
                phone_number = data["phone_number"]
                email = data["email"]

                split_name = name.split()
                first_name = split_name[0]
                if len(split_name) > 1:
                    last_name = split_name[-1]
                else:
                    last_name = ""

                first_name = validation_obj.remo_html_from_string(first_name)
                last_name = validation_obj.remo_html_from_string(last_name)
                phone_number = validation_obj.remo_html_from_string(
                    phone_number)
                email = validation_obj.remo_html_from_string(email)
                username = email

                first_name = validation_obj.remo_special_tag_from_string(
                    first_name)
                last_name = validation_obj.remo_special_tag_from_string(
                    last_name)

                easychat_user_obj = None
                try:
                    password = generate_random_password()
                    if password:
                        easychat_user_obj = User.objects.create(
                            email=email, first_name=first_name, last_name=last_name, username=username, password=password, role="bot_builder", status="1")
                        send_password_mail(name, username, email, password)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("CreateNewLiveChatOnlyAdmin: %s at %s",
                                 e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

                if easychat_user_obj != None:
                    new_user_obj = LiveChatUser.objects.create(
                        user=easychat_user_obj, status="1", phone_number=phone_number, is_livechat_only_admin=True)
                    new_user_obj.bots.set(user_obj.bots.all())
                    new_user_obj.category.set(user_obj.category.all())
                    new_user_obj.save()
                    user_obj.livechat_only_admin.add(new_user_obj)
                    user_obj.save()
                    response["status_message"] = "SUCCESS"
                    response["status_code"] = "200"
                else:
                    response["status_message"] = "SUCCESS"
                    response["status_code"] = "300"
            else:
                response["status_message"] = INVALID_OPERATION
                response["status_code"] = "500"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CreateNewLiveChatOnlyAdmin: %s at %s", e, str(
                exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


CreateNewLiveChatOnlyAdmin = CreateNewLiveChatOnlyAdminAPI.as_view()


class CreateLiveChatOnlyAdminWithExcelAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        logger.info("Into CreateLiveChatOnlyAdminWithExcelAPI..",
                    extra={'AppName': 'LiveChat'})
        response = {}
        response["status_code"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            user_obj = LiveChatUser.objects.get(user=User.objects.get(
                username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            data = request.data
            uploaded_file = data['livechat_only_admin_file']
            path = default_storage.save(
                uploaded_file.name, ContentFile(uploaded_file.read()))
            file_path = settings.MEDIA_ROOT + path

            ext = str(uploaded_file.name).split(".")[-1]
            if ext not in ["xls", "xlsx"]:
                response["status_code"] = 101
                response[
                    "status_message"] = FILE_UPLOAD_ERROR
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            validation_obj = LiveChatInputValidation()

            wb = xlrd.open_workbook(file_path)
            sheet = wb.sheet_by_index(0)
            for row in range(1, sheet.nrows):
                try:
                    first_name = str(sheet.cell_value(row, 0)).strip()
                    last_name = str(sheet.cell_value(row, 1)).strip()
                    phone_number = str(
                        int(float(str(sheet.cell_value(row, 2)))))
                    email = str(sheet.cell_value(row, 3))
                    password = ""
                    try:
                        password = str(
                            int(float(str(sheet.cell_value(row, 4)))))
                    except Exception:
                        password = str(sheet.cell_value(row, 4))

                    is_info_valid = True
                    if not validation_obj.validate_name(first_name):
                        response["status_message"] = "Enter valid first name!"
                        is_info_valid = False
                    elif not validation_obj.validate_phone_number(phone_number):
                        response["status_message"] = "Enter valid phone number!"
                        is_info_valid = False
                    elif not validation_obj.validate_email(email):
                        response["status_message"] = "Enter valid email!"
                        is_info_valid = False
                    elif not validation_obj.validate_password(password):
                        response["status_message"] = "Enter valid password!"
                        is_info_valid = False

                    if not is_info_valid:
                        response["status_code"] = 101
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)

                except Exception:
                    response["status_code"] = 101
                    response[
                        "status_message"] = FILE_UPLOAD_ERROR
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                try:
                    easychat_user_obj = User.objects.get(username=email)
                    easychat_user_obj.delete()
                except Exception:
                    logger.info("Into CreateLiveChatOnlyAdminWithExcelAPI: easychat_user not present.", extra={
                                'AppName': 'LiveChat'})

                easychat_user_obj = User.objects.create(
                    email=email, first_name=first_name, last_name=last_name, username=email, password=password, role="customer_care_agent", status="1")

                try:
                    new_user_obj = LiveChatUser.objects.get(
                        user=easychat_user_obj)
                    new_user_obj.delete()
                except Exception:
                    logger.info("Into CreateLiveChatOnlyAdminWithExcelAPI: livechat_user not present.", extra={
                                'AppName': 'LiveChat'})

                new_user_obj = LiveChatUser.objects.create(
                    user=easychat_user_obj, status="1", phone_number=phone_number, is_livechat_only_admin=True)
                new_user_obj.save()
                user_obj.livechat_only_admin.add(new_user_obj)
                user_obj.save()

            response["status_code"] = 200
            response["status_message"] = "Success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CreateLiveChatOnlyAdminWithExcelAPI: %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = e

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


CreateLiveChatOnlyAdminWithExcel = CreateLiveChatOnlyAdminWithExcelAPI.as_view()


class DownloadLiveChatOnlyAdminExcelTemplateAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            export_path = None
            export_path_exist = None
            if user_obj.status == "1" and not user_obj.is_livechat_only_admin:
                export_path = "/files/templates/livechat-only-admin-excel-template" + \
                    "/Template_createLiveChatOnlyAdmin.xlsx"
                # export_path_exist = path.exists(export_path[1:])
                export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                response["status"] = 200
            response["export_path"] = export_path
            response["export_path_exist"] = export_path_exist
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DownloadLiveChatOnlyAdminExcelTemplateAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


DownloadLiveChatOnlyAdminExcelTemplate = DownloadLiveChatOnlyAdminExcelTemplateAPI.as_view()


class DeleteLiveChatOnlyAdminAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            if user_obj.status == "1" and not user_obj.is_livechat_only_admin:
                data = DecryptVariable(request.data["json_string"])
                data = json.loads(data)

                validation_obj = LiveChatInputValidation()

                current_livechat_only_admin_pk = data[
                    "current_livechat_only_admin_pk"]
                current_livechat_only_admin_pk = validation_obj.remo_html_from_string(
                    current_livechat_only_admin_pk)

                livechat_only_admin = LiveChatUser.objects.get(
                    pk=int(current_livechat_only_admin_pk), is_deleted=False)
                if livechat_only_admin in user_obj.livechat_only_admin.all():
                    livechat_only_admin.is_deleted = True
                    livechat_only_admin.save()
                    response["status_code"] = "200"
                else:
                    response["status_code"] = "300"
                    response[
                        "status_message"] = "This user does not belong to current admin."
            else:
                response["status_code"] = "500"
                response["status_message"] = INVALID_OPERATION

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DeleteLiveChatOnlyAdminAPI: %s at %s", e, str(
                exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


DeleteLiveChatOnlyAdmin = DeleteLiveChatOnlyAdminAPI.as_view()


class EditLiveChatOnlyAdminInfoAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            if user_obj.status == "1" and not user_obj.is_livechat_only_admin:
                data = DecryptVariable(request.data["json_string"])
                data = json.loads(data)

                validation_obj = LiveChatInputValidation()

                name = data["name"]
                phone_number = data["phone_number"]
                email = data["email"]
                username = email
                current_livechat_only_admin_pk = data[
                    "current_livechat_only_admin_pk"]

                split_name = name.split()
                first_name = split_name[0]
                if len(split_name) > 1:
                    last_name = split_name[-1]
                else:
                    last_name = ""

                first_name = validation_obj.remo_html_from_string(first_name)
                last_name = validation_obj.remo_html_from_string(last_name)
                phone_number = validation_obj.remo_html_from_string(
                    phone_number)
                username = validation_obj.remo_html_from_string(username)
                email = validation_obj.remo_html_from_string(email)

                first_name = validation_obj.remo_special_tag_from_string(
                    first_name)
                last_name = validation_obj.remo_special_tag_from_string(
                    last_name)

                easychat_user_obj = None
                try:
                    easychat_user_obj = LiveChatUser.objects.get(
                        pk=int(current_livechat_only_admin_pk)).user
                    easychat_user_obj.first_name = first_name
                    easychat_user_obj.last_name = last_name
                    easychat_user_obj.email = email
                    easychat_user_obj.username = username
                    easychat_user_obj.save()
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("EditLiveChatOnlyAdminInfoAPI: %s at %s",
                                 e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
                    easychat_user_obj = None

                if easychat_user_obj != None:
                    new_user_obj = LiveChatUser.objects.get(
                        pk=int(current_livechat_only_admin_pk))
                    new_user_obj.phone_number = phone_number
                    new_user_obj.save()
                    response["status_message"] = "SUCCESS"
                    response["status_code"] = "200"
                else:
                    response["status_message"] = "SUCCESS"
                    response["status_code"] = "300"
            else:
                response["status_message"] = INVALID_OPERATION
                response["status_code"] = "500"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EditLiveChatOnlyAdminInfoAPI: %s at %s", e, str(
                exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


EditLiveChatOnlyAdminInfo = EditLiveChatOnlyAdminInfoAPI.as_view()


def DeveloperSettings(request):
    try:
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            bot_obj_list = user_obj.bots.filter(is_deleted=False)
            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)
            if user_obj.status == "1":
                if 'bot_pk' in request.GET:
                    bot_pk = request.GET["bot_pk"]
                    bot_pk = int(bot_pk)
                else:
                    bot_pk = -1

                if 'id' in request.GET:
                    type_of_editor = request.GET["id"]
                else:
                    type_of_editor = -1

                ticket_raise_functionality = {}
                for bot_obj in bot_obj_list:
                    try:
                        livechat_config = LiveChatConfig.objects.get(bot=bot_obj)
                    except Exception:
                        livechat_config = LiveChatConfig.objects.create(bot=bot_obj)
                        pass
                    ticket_raise_functionality[bot_obj.pk] = str(livechat_config.is_agent_raise_ticket_functionality_enabled)

                return render(request, 'LiveChatApp/developer_settings.html', {'user_obj': user_obj, 'admin_config': admin_config, 'bot_obj_list': bot_obj_list, 'bot_pk': bot_pk, 'type_of_editor': type_of_editor, "ticket_raise_functionality": ticket_raise_functionality})
            else:
                return HttpResponse(AUTHORIZATION_DENIED)
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("DeveloperSettings: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


def DeveloperEditor(request):
    try:
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)
            bot_pk = request.GET["bot_pk"]
            type_of_processor = request.GET["editor_id"]

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            processor_obj = LiveChatProcessors.objects.filter(bot=bot_obj)

            if not processor_obj:
                processor_obj = LiveChatProcessors.objects.create(bot=bot_obj)
            else:
                processor_obj = processor_obj.first()

            if type_of_processor == "1":

                if not processor_obj.show_customer_details_processor:
                    processor_obj.show_customer_details_processor = LiveChatDeveloperProcessor.objects.create(
                        function=LIVECHAT_PROCESSOR_EXAMPLE)
                    processor_obj.save()

                code = processor_obj.show_customer_details_processor.function
                name = processor_obj.show_customer_details_processor.name
            elif type_of_processor == "2":

                if not processor_obj.end_chat_processor:
                    processor_obj.end_chat_processor = LiveChatDeveloperProcessor.objects.create(
                        function=LIVECHAT_PROCESSOR_EXAMPLE_END_CHAT)
                    processor_obj.save()

                code = processor_obj.end_chat_processor.function
                name = processor_obj.end_chat_processor.name
            elif type_of_processor == '3':

                if not processor_obj.assign_agent_processor:
                    processor_obj.assign_agent_processor = LiveChatDeveloperProcessor.objects.create(
                        function=LIVECHAT_PROCESSOR_EXAMPLE_ASSIGN_AGENT)
                    processor_obj.save()

                code = processor_obj.assign_agent_processor.function
                name = processor_obj.assign_agent_processor.name
            elif type_of_processor == '9':

                if not processor_obj.raise_ticket_processor:
                    processor_obj.raise_ticket_processor = LiveChatDeveloperProcessor.objects.create(
                        function=LIVECHAT_PROCESSOR_EXAMPLE_RAISE_TICKET)
                    processor_obj.save()

                code = processor_obj.raise_ticket_processor.function
                name = processor_obj.raise_ticket_processor.name
            elif type_of_processor == '10':

                if not processor_obj.search_ticket_processor:
                    processor_obj.search_ticket_processor = LiveChatDeveloperProcessor.objects.create(
                        function=LIVECHAT_PROCESSOR_EXAMPLE_SEARCH_TICKET)
                    processor_obj.save()

                code = processor_obj.search_ticket_processor.function
                name = processor_obj.search_ticket_processor.name
            elif type_of_processor == '11':

                if not processor_obj.get_previous_tickets_processor:
                    processor_obj.get_previous_tickets_processor = LiveChatDeveloperProcessor.objects.create(
                        function=LIVECHAT_PROCESSOR_EXAMPLE_PREVIOUS_TICKETS)
                    processor_obj.save()

                code = processor_obj.get_previous_tickets_processor.function
                name = processor_obj.get_previous_tickets_processor.name
            else:

                if not processor_obj.push_api:
                    processor_obj.push_api = LiveChatDeveloperProcessor.objects.create(
                        function=LIVECHAT_PROCESSOR_EXAMPLE_PUSH_API)
                    processor_obj.save()

                code = processor_obj.push_api.function
                name = processor_obj.push_api.name

            config_obj = LiveChatConfig.objects.get(
                bot=Bot.objects.get(pk=int(bot_pk)))
            system_commands = config_obj.system_commands

            if user_obj.status == "1":
                return render(request, 'LiveChatApp/editor_settings.html', {'user_obj': user_obj, 'admin_config': admin_config, 'code': code, 'name': name, 'bot_pk': bot_pk, 'type_of_processor': type_of_processor, 'system_commands': system_commands})
            else:
                return HttpResponse(AUTHORIZATION_DENIED)
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("DeveloperEditor: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


class SaveLiveChatProcessorContentAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = 500
        response["message"] = INTERNAL_SERVER_ERROR
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            code = data["code"]
            bot_pk = data["bot_pk"]
            name = data["name"]
            type_of_processor = data["type_of_processor"]

            if check_for_system_commands(code, bot_pk, LiveChatConfig, Bot):
                response['status_code'] = 400
                response['message'] = "Code contains system commands. Please remove them and then save."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(
                    json.dumps(response))
                return Response(data=response)

            processor_obj = LiveChatProcessors.objects.get(
                bot=Bot.objects.get(pk=int(bot_pk)))

            if type_of_processor == "1":

                show_customer_details_processor = processor_obj.show_customer_details_processor
                show_customer_details_processor.function = code
                show_customer_details_processor.name = name
                show_customer_details_processor.save()
                processor_obj.save()
            elif type_of_processor == "2":

                end_chat_processor = processor_obj.end_chat_processor
                end_chat_processor.function = code
                end_chat_processor.name = name
                end_chat_processor.save()
                processor_obj.save()
            elif type_of_processor == '3':

                assign_agent_processor = processor_obj.assign_agent_processor
                assign_agent_processor.function = code
                assign_agent_processor.name = name
                assign_agent_processor.save()
                processor_obj.save()
            elif type_of_processor == '9':

                raise_ticket_processor = processor_obj.raise_ticket_processor
                raise_ticket_processor.function = code
                raise_ticket_processor.name = name
                raise_ticket_processor.save()
                processor_obj.save()
            elif type_of_processor == '10':

                search_ticket_processor = processor_obj.search_ticket_processor
                search_ticket_processor.function = code
                search_ticket_processor.name = name
                search_ticket_processor.save()
                processor_obj.save()
            elif type_of_processor == '11':

                get_previous_tickets_processor = processor_obj.get_previous_tickets_processor
                get_previous_tickets_processor.function = code
                get_previous_tickets_processor.name = name
                get_previous_tickets_processor.save()
                processor_obj.save()
            else:

                push_api = processor_obj.push_api
                push_api.function = code
                push_api.name = name
                push_api.save()
                processor_obj.save()

            response["status_code"] = 200
            response["message"] = "SUCCESS"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveLiveChatProcessorContent: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveLiveChatProcessorContent = SaveLiveChatProcessorContentAPI.as_view()


class LiveChatProcessorRunAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = INTERNAL_SERVER_ERROR
        response["elapsed_time"] = "0.0000"
        try:
            import urllib.parse
            import time
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            code = data["code"]
            bot_pk = data["bot_pk"]
            parameter = data["parameter"]

            start_time = time.time()

            if check_for_system_commands(code, bot_pk, LiveChatConfig, Bot):
                response['status'] = 400
                response['message'] = "Code contains system commands. Please remove them and try again."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(
                    json.dumps(response))
                return Response(data=response)

            processor_check_dictionary = {'open': open_file}

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            try:
                user = Profile.objects.filter(
                    user_id=parameter, bot=bot_obj)[0]
            except Exception:
                try:
                    livechat_cust_obj = LiveChatCustomer.objects.filter(client_id=parameter)[
                        0]
                    user = Profile.objects.filter(
                        user_id=livechat_cust_obj.easychat_user_id, bot=bot_obj)[0]
                except Exception:
                    response['status'] = 400
                    response['message'] = "Customer with given client id or easychat user id does not exist."
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(
                        json.dumps(response))
                    return Response(data=response)

            processed_code = replace_data_values(user, code, '', '', '')

            exec(str(processed_code), processor_check_dictionary)

            json_data = processor_check_dictionary['f'](parameter)

            response["status"] = 200

            end_time = time.time()

            elapsed_time = end_time - start_time

            response["elapsed_time"] = str(elapsed_time)

            response["message"] = json.dumps(json_data)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EasyChatProcessorRunAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            response["message"] = str(e)
            response["status"] = 300
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


LiveChatProcessorRun = LiveChatProcessorRunAPI.as_view()


class DataMaskToggleAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            bot_id = data["bot_id"]

            bot_obj = Bot.objects.get(pk=int(bot_id))
            user = request.user

            livechat_user = LiveChatUser.objects.get(
                user=user, is_deleted=False)
            livechat_user = check_if_livechat_only_admin(
                livechat_user, LiveChatUser)

            if livechat_user.status != "1":
                response["status_message"] = "User is not an admin."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            try:
                data_toggle_obj = LiveChatPIIDataToggle.objects.get(
                    user=livechat_user, bot=bot_obj)
                data_toggle_obj.token = uuid.uuid4()
            except Exception:
                logger.info("Creating new data toggle object: %s: %s", extra={
                            'AppName': 'LiveChat', 'user_id': str(request.user.username)})
                data_toggle_obj = LiveChatPIIDataToggle.objects.create(
                    user=livechat_user, bot=bot_obj)

            otp = random.randrange(10**5, 10**6)

            data_toggle_obj.otp = otp
            data_toggle_obj.is_expired = False
            data_toggle_obj.save()

            livechat_config_obj = get_developer_console_livechat_settings()
            if livechat_config_obj:
                email_ids = json.loads(livechat_config_obj.livechat_masking_pii_data_otp_email)
            else:
                email_ids = settings.MASKING_PII_DATA_OTP_EMAIL
            send_otp_mail(email_ids, otp, user.username, bot_obj)

            response["status_code"] = "200"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DataMaskToggleAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = e

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


DataMaskToggle = DataMaskToggleAPI.as_view()


class CheckDataToggleOtpAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            bot_id = data["bot_id"]
            entered_otp = data["entered_otp"]

            user = request.user
            livechat_user = LiveChatUser.objects.get(
                user=user, is_deleted=False)
            livechat_user = check_if_livechat_only_admin(
                livechat_user, LiveChatUser)

            data_toggle_obj = LiveChatPIIDataToggle.objects.get(
                user=livechat_user, bot=(Bot.objects.get(pk=int(bot_id))))
            sent_otp = data_toggle_obj.otp

            if not data_toggle_obj.is_expired and entered_otp == sent_otp:
                response["message"] = "Matched"
                response["token"] = str(data_toggle_obj.token)
            else:
                response["message"] = "Not Matched"

            response["status_code"] = "200"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CheckDataToggleOtpAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = e

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


CheckDataToggleOtp = CheckDataToggleOtpAPI.as_view()


class LiveChatUploadExcelAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data["Request"]
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = LiveChatInputValidation()

            uploaded_file = data[0]

            file_name = uploaded_file["filename"]
            file_name = validation_obj.remo_html_from_string(file_name)

            base64_content = uploaded_file["base64_file"]

            if file_name.find("<") != -1 or file_name.find(">") != -1 or file_name.find("=") != -1:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            file_validation_obj = LiveChatFileValidation()

            if file_validation_obj.check_malicious_file(file_name):
                response["status"] = 300
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            file_extension = file_name.split(".")[-1]
            file_extension = file_extension.lower()

            allowed_files_list = ["xls", "xlsx", "xlsm", "xlt", "xltm", "xlb"]
            if file_extension in allowed_files_list:

                if file_validation_obj.check_malicious_file_from_content(base64_content, allowed_files_list):
                    response["status"] = 300
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                file_name = str(uuid.uuid4()) + '.' + file_extension
                file_path = settings.MEDIA_ROOT + file_name
                fh = open(file_path, "wb")
                fh.write(base64.b64decode(base64_content))
                fh.close()

                response["src"] = file_name
                response["status"] = 200
            else:
                response["status"] = 300
                logger.info("File format is not supported", extra={'AppName': 'LiveChat', 'user_id': str(
                    request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error LiveChatUploadExcelAPI : %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


LiveChatUploadExcel = LiveChatUploadExcelAPI.as_view()


def FormBuilderPage(request):
    try:
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)
            bot_pk = request.GET["bot_pk"]

            if user_obj.status == "1":

                bot_obj = Bot.objects.get(pk=int(bot_pk))
                form_obj = LiveChatDisposeChatForm.objects.filter(bot=bot_obj)

                if not form_obj:
                    form_obj = LiveChatDisposeChatForm.objects.create(
                        bot=bot_obj, form=json.dumps({}))
                else:
                    form_obj = form_obj[0]

                is_form_enabled = form_obj.is_form_enabled
                form = form_obj.form

                return render(request, 'LiveChatApp/form_builder.html', {'user_obj': user_obj, 'admin_config': admin_config, 'bot_pk': bot_pk, 'is_form_enabled': is_form_enabled, 'form': form, 'bot_obj': bot_obj})
            else:
                return HttpResponse(AUTHORIZATION_DENIED)
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("FormBuilderPage: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


class SaveDisposeChatFormAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            bot_id = data["bot_pk"]
            is_form_enabled = data['is_form_enabled']
            form = data['form']

            bot_obj = Bot.objects.get(pk=int(bot_id))
            form_obj = LiveChatDisposeChatForm.objects.get(bot=bot_obj)

            form_obj.is_form_enabled = is_form_enabled

            if is_form_enabled:
                form_obj.form = json.dumps(form)

            form_obj.edited_datetime = timezone.now()
            form_obj.save()

            response["status"] = "200"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveDisposeChatFormAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = e

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveDisposeChatForm = SaveDisposeChatFormAPI.as_view()


class GetDisposeChatFormDataAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = LiveChatInputValidation()

            id = data["id"]

            form_filled = []
            if validation_obj.is_valid_uuid(id):
                customer_obj = LiveChatCustomer.objects.filter(session_id=id)
                if customer_obj:
                    if (isinstance(customer_obj[0].form_filled, list)):
                        form_filled = customer_obj[0].form_filled
                    else:
                        form_filled = json.loads(customer_obj[0].form_filled)
            else:
                logger.error("GetDisposeChatFormDataAPI invalid uuid: %s",
                             str(id), extra={'AppName': 'LiveChat'})

            response['form_filled'] = form_filled
            response["status"] = "200"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetDisposeChatFormDataAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = e

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetDisposeChatFormData = GetDisposeChatFormDataAPI.as_view()


class GetLiveChatHistoryAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get_data(self, key):
        try:
            if key in self.data:
                return self.data[key]
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetLiveChatHistoryAPI get_data: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 'None'

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            import math
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            self.data = data

            user_obj = LiveChatUser.objects.get(user=User.objects.get(
                username=str(request.user.username)), is_deleted=False)
            
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)

            agent_usernames = self.get_data('agent_username')
            if agent_usernames == 'None' or (isinstance(agent_usernames, list) and not agent_usernames):
                query_user_obj = get_agents_under_this_user(user_obj)
            else:
                query_user_obj = LiveChatUser.objects.filter(user__username__in=agent_usernames)

            archive_customer = self.get_data('archive_customer')
            if archive_customer == 'None':
                archive_customer = 'false'

            current_history_id = self.get_data('current_history_id')
            channel_name = self.get_data('channel_name')
            if channel_name == 'None':
                channel_name = 'All'

            selected_category_pk = self.get_data('selected_category_pk')

            if selected_category_pk == 'None':
                selected_category_pk = 0

            try:
                channel_obj = Channel.objects.get(name=channel_name)
            except Exception:
                channel_obj = None

            chat_termination = self.get_data('chat_termination')
            if chat_termination == 'None':
                chat_termination = 'All'

            # By default, chat history of last 7 days is loaded
            datetime_start = (datetime.datetime.today() -
                              datetime.timedelta(7)).date()
            datetime_end = datetime.datetime.today().date()
            try:
                start_date = self.get_data('start_date')
                end_date = self.get_data('end_date')

                if start_date != 'None':
                    datetime_start = datetime.datetime.strptime(
                        start_date.strip(), DEFAULT_DATE_FORMAT).date()
                
                if end_date != 'None':
                    datetime_end = datetime.datetime.strptime(end_date.strip(), DEFAULT_DATE_FORMAT).date()  # noqa: F841
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.warning("datetime_start and datetime_end is not in valid format %s at line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

            chat_status = self.get_data('chat_status')
            if archive_customer == "false":
                user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)

                agent_obj_list = get_agents_under_this_user(user_obj)

                livechat_followup_cust_objs = LiveChatFollowupCustomer.objects.filter(
                    agent_id__in=agent_obj_list, is_completed=True).values('livechat_customer')
                livechat_cust_objs = LiveChatCustomer.objects.filter(
                    Q(agent_id__in=agent_obj_list) | Q(pk__in=livechat_followup_cust_objs))
                
                category_obj = None
                try:
                    if selected_category_pk and selected_category_pk != '0':
                        category_obj = user_obj.category.get(
                            pk=int(selected_category_pk))
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("AuditTrail ! %s %s", str(e), str(
                        exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
                    category_obj = None
            else:

                livechat_followup_cust_objs = LiveChatFollowupCustomer.objects.filter(
                    agent_id=user_obj, is_completed=True).values('livechat_customer')               
                livechat_cust_objs = LiveChatCustomer.objects.filter(
                    Q(agents_group__user=user_obj, is_session_exp=True) | Q(pk__in=livechat_followup_cust_objs))
                query_user_obj = [user_obj]
                chat_status = None
                channel_name = 'All'
                channel_obj = None
                selected_category_pk = 0
                category_obj = None
                chat_termination = None

            audit_obj_list = get_audit_objects(
                query_user_obj, chat_status, datetime_start, datetime_end, livechat_cust_objs, channel_name, channel_obj, selected_category_pk, category_obj, chat_termination, livechat_followup_cust_objs)

            page = self.get_data('page')

            total_audits, audit_obj_list_final, start_point, end_point = paginate(
                audit_obj_list, AUDIT_TRAIL_ITEM_COUNT, page)

            response['audit_obj_list'] = parse_audit_object_list(
                audit_obj_list_final)
            response['pagination_data'] = get_audit_trail_pagination_data(
                audit_obj_list_final)
            response['total_audits'] = total_audits
            response['start_point'] = start_point
            response['end_point'] = end_point

            total_pages = math.ceil(total_audits / AUDIT_TRAIL_ITEM_COUNT)

            trailing_list = get_trailing_list(
                current_history_id, audit_obj_list, AUDIT_TRAIL_ITEM_COUNT, audit_obj_list_final, page, total_pages)

            response["trailing_list"] = trailing_list
            trailing_list = []
            for list_obj in response["trailing_list"]:
                trailing_list.append(str(list_obj.session_id))
            response["trailing_list"] = trailing_list
            response["status"] = 200
            response["status_message"] = "Success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetLiveChatHistoryAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = e

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetLiveChatHistory = GetLiveChatHistoryAPI.as_view()


class GetLiveChatMessageHistoryAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            session_id = data["session_id"]

            validation_obj = LiveChatInputValidation()

            livechat_cust_obj = LiveChatCustomer.objects.filter(
                session_id=session_id)

            if livechat_cust_obj:
                livechat_cust_obj = livechat_cust_obj[0]

                sender_username = validation_obj.remo_html_from_string(
                    request.user.username).strip()
                receiver_username = livechat_cust_obj.get_agent_username()

                # Loading messages of follow up leads if not loaded previously
                if livechat_cust_obj.followup_assignment:
                    livechat_followup_cust_obj = LiveChatFollowupCustomer.objects.get(livechat_customer=livechat_cust_obj)
                    update_followup_lead_message_history(livechat_cust_obj, livechat_followup_cust_obj, LiveChatMISDashboard, MISDashboard)

                response["message_history"] = get_message_history(
                    livechat_cust_obj, False, LiveChatMISDashboard, LiveChatTranslationCache)
                response["customer_name"] = livechat_cust_obj.username
                response['is_session_exp'] = livechat_cust_obj.is_session_exp
                response['active_url'] = livechat_cust_obj.active_url
                response['client_id'] = livechat_cust_obj.client_id
                response['joined_date'] = livechat_cust_obj.joined_date.strftime(
                    DATE_DD_MMM_YYYY)
                response["status"] = 200
                response["message"] = "success"
                response["sender_username"] = sender_username
                response["receiver_username"] = receiver_username
                response["sender_websocket_token"] = get_agent_token_based_on_username(
                    sender_username)
                response["receiver_websocket_token"] = get_agent_token_based_on_username(
                    receiver_username)
            else:
                response['message'] = 'Invalid Session ID'
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetLiveChatMessageHistoryAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = "error"

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetLiveChatMessageHistory = GetLiveChatMessageHistoryAPI.as_view()


class GetLiveChatCallHistoryAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get_data(self, key):
        try:
            if key in self.data:
                return self.data[key]
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetLiveChatVOIPHistoryAPI get_data: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 'None'

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            self.data = data

            validation_obj = LiveChatInputValidation()

            agent_username = self.get_data('agent_username')
            agent_username = validation_obj.remo_html_from_string(
                agent_username)
            agent_username = validation_obj.remo_special_tag_from_string(
                agent_username)

            try:
                query_user_obj = LiveChatUser.objects.get(
                    user=User.objects.get(username=str(agent_username)))
            except Exception:
                query_user_obj = None

            # By default, voip history of last 1 days is loaded
            datetime_start = (datetime.datetime.today()).date()
            datetime_end = (datetime.datetime.today() +
                            datetime.timedelta(1)).date()
            # datetime end is not inclusive so adding 1 day
            try:
                start_date = self.get_data('start_date')
                end_date = self.get_data('end_date')
                datetime_start = datetime.datetime.strptime(
                    start_date.strip(), DEFAULT_DATE_FORMAT).date()
                datetime_end = (datetime.datetime.strptime(
                    end_date.strip(), DEFAULT_DATE_FORMAT) + datetime.timedelta(1)).date()  # noqa: F841
                # datetime end is not inclusive in range so adding 1 day
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.warning("datetime_start and datetime_end is not in valid format %s at line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

            call_type = self.get_data('call_type')

            user_obj = LiveChatUser.objects.get(user=User.objects.get(
                username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)

            agent_obj_list = get_agents_under_this_user(user_obj)

            voip_object_list = get_call_data_history_objects(
                agent_username, query_user_obj, datetime_end, datetime_start, agent_obj_list, call_type, LiveChatVoIPData)

            page = self.get_data('page')

            total_audits, voip_object_list, start_point, end_point = paginate(
                voip_object_list, VOIP_HISTORY_ITEM_COUNT, page)

            response['voip_object_list'] = parse_voip_history_object_list(
                voip_object_list, LiveChatFileAccessManagement)

            response['pagination_data'] = get_audit_trail_pagination_data(
                voip_object_list)
            response['total_audits'] = total_audits
            response['start_point'] = start_point
            response['end_point'] = end_point

            response["status"] = 200
            response["status_message"] = "Success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetLiveChatCallHistoryAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = e

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetLiveChatCallHistory = GetLiveChatCallHistoryAPI.as_view()


def WhatsAppWebhookConsole(request):
    try:
        if request.user.is_authenticated:
            bot_pk = request.GET["bot_pk"]

            user = User.objects.get(username=str(request.user.username))
            user_obj = LiveChatUser.objects.get(
                user=user, is_deleted=False)
            bot_obj_list = user_obj.bots.filter(is_deleted=False)
            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)

            if user_obj.status == "1":
                bot_obj = Bot.objects.get(pk=bot_pk)
                livechat_webhook_obj = LiveChatBotChannelWebhook.objects.filter(
                    bot=bot_obj).first()

                selected_whatsapp_service_provider = None
                is_any_other_user_active = False
                code = ""

                if livechat_webhook_obj:
                    code = livechat_webhook_obj.function
                    selected_whatsapp_service_provider = livechat_webhook_obj.whatsapp_service_provider

                    time_diff = datetime.datetime.now(
                        datetime.timezone.utc) - livechat_webhook_obj.last_updated_timestamp
                    if (time_diff.days == 0 and time_diff.seconds <= 60):
                        if user not in livechat_webhook_obj.users_active.all():
                            is_any_other_user_active = True
                    else:
                        livechat_webhook_obj.users_active.clear()
                        livechat_webhook_obj.users_active.add(user)
                        livechat_webhook_obj.last_updated_datetime = datetime.datetime.now()
                        livechat_webhook_obj.save()

                config_obj = LiveChatConfig.objects.get(bot=bot_obj)
                system_commands = config_obj.system_commands

                whatsapp_service_providers = LiveChatWhatsAppServiceProvider.objects.all().order_by("pk")

                return render(request, 'LiveChatApp/whatsapp_webhook_console.html', {
                    'user_obj': user_obj,
                    'admin_config': admin_config,
                    'bot_obj_list': bot_obj_list,
                    'bot_obj': bot_obj,
                    "system_commands": system_commands,
                    "selected_whatsapp_service_provider": selected_whatsapp_service_provider,
                    "code": code,
                    "is_any_other_user_active": is_any_other_user_active,
                    "whatsapp_service_providers": whatsapp_service_providers
                })
            else:
                return HttpResponse(AUTHORIZATION_DENIED)
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("WhatsAppWebhookConsole: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})


class GetLiveChatWebhookDefaultCodeAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            wsp_code = data["wsp_code"]
            wsp_code = validation_obj.remo_html_from_string(wsp_code)

            wsp_obj = LiveChatWhatsAppServiceProvider.objects.filter(
                name=wsp_code).first()

            if wsp_obj:
                sample_file_path = wsp_obj.default_code_file_path
                if sample_file_path != None and sample_file_path != "":
                    file_obj = open(sample_file_path, "r")
                    response["default_code"] = file_obj.read()
                    response["status"] = 200
                    response["message"] = "Success"
                else:
                    response["message"] = "Cannot find default code for {} WhatsApp BSP.".format(
                        wsp_obj.get_name_display())
                response["wsp_name"] = wsp_obj.get_name_display()
            else:
                response["message"] = "WhatsApp BSP does not exists."
                response["wsp_name"] = ""

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetLiveChatWebhookDefaultCodeAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetLiveChatWebhookDefaultCode = GetLiveChatWebhookDefaultCodeAPI.as_view()


class SaveLiveChatWebhookContentAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            code = data["code"]
            bot_id = data["bot_id"]
            wsp_code = data["wsp_code"]
            wsp_obj = LiveChatWhatsAppServiceProvider.objects.get(
                name=wsp_code)
            user = User.objects.get(username=request.user.username)

            bot_obj = Bot.objects.filter(pk=int(bot_id)).first()
            if bot_obj:
                whatsapp_webhook_obj = LiveChatBotChannelWebhook.objects.filter(
                    bot=bot_obj).first()
                if whatsapp_webhook_obj:
                    whatsapp_webhook_obj.function = code
                    whatsapp_webhook_obj.bot = bot_obj
                    whatsapp_webhook_obj.whatsapp_service_provider = wsp_obj
                    whatsapp_webhook_obj.last_updated_timestamp = datetime.datetime.now()
                    whatsapp_webhook_obj.users_active.add(user)
                    whatsapp_webhook_obj.save()
                else:
                    channel_obj = Channel.objects.get(name="WhatsApp")
                    whatsapp_webhook_obj = LiveChatBotChannelWebhook.objects.create(
                        bot=bot_obj, function=code, whatsapp_service_provider=wsp_obj, channel=channel_obj)
                    whatsapp_webhook_obj.users_active.add(user)
                    whatsapp_webhook_obj.save()

                response["status"] = 200
                response["message"] = "SUCCESS"
            else:
                response["status"] = 305
                response["message"] = "Bot not found."
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveWhatsAppWebhookContentAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveLiveChatWebhookContent = SaveLiveChatWebhookContentAPI.as_view()


def APIDocsPage(request):
    try:
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)
            bot_pk = request.GET["bot_pk"]

            if user_obj.status == "1":
                return render(request, 'LiveChatApp/api_docs.html', {'user_obj': user_obj, 'admin_config': admin_config, 'bot_pk': bot_pk})
            else:
                return HttpResponse(AUTHORIZATION_DENIED)
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("APIDocsPage: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


def DownloadLiveChatDocuments(request, document_type):
    try:
        if request.user.is_authenticated:

            username = request.user.username

            original_file_name = LIVECHAT_DOCUMENTS[document_type]["original_file_name"]
            display_file_name = LIVECHAT_DOCUMENTS[document_type]["display_file_name"]

            path_to_file = f'secured_files/LiveChatApp/livechat-documents/{username}/{original_file_name}'

            if not path.exists(path_to_file):
                generate_livechat_api_document(username)

            if path.exists(path_to_file):
                with open(path_to_file, 'rb') as fh:
                    response = HttpResponse(
                        fh.read(), status=200, content_type="docs")
                    response['Content-Disposition'] = 'attachment; filename="%s"' % smart_str(
                        str(display_file_name))
                    return response
            else:
                return HttpResponse(status=404)
        else:
            return HttpResponse(status=404)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error DownloadLiveChatDocuments %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponse(status=404)


class GetLiveChatSupervisorCategoryAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            user_pk = data['user_pk']
            agent_pk = data['agent_pk']

            user_obj = LiveChatUser.objects.filter(pk=user_pk).first()
            agent_obj = LiveChatUser.objects.filter(pk=agent_pk).first()
            
            if user_obj:
                category_objs = user_obj.category.filter(bot__in=agent_obj.bots.all(), is_deleted=False)
                
                category_list = []
                for category in category_objs:
                    category_list.append({
                        'pk': category.pk,
                        'title': category.title,
                    })

                response['category_list'] = category_list
                response["status"] = 200
                response["message"] = 'success'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetLiveChatSupervisorCategoryAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetLiveChatSupervisorCategory = GetLiveChatSupervisorCategoryAPI.as_view()


class CreateBlacklistedKeywordWithExcelAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        logger.info("Into CreateAgentWithExcelAPI..",
                    extra={'AppName': 'LiveChat'})
        response = {}
        response["status_code"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            user_obj = LiveChatUser.objects.get(user=User.objects.get(
                username=str(request.user.username)), is_deleted=False)
            
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)

            data = request.data

            validation_obj = LiveChatInputValidation()

            file_path = settings.MEDIA_ROOT + data['src']
            blacklist_for = data['blacklist_for']

            wb = xlrd.open_workbook(file_path)
            sheet = wb.sheet_by_index(0)

            if sheet.nrows <= 1:
                response['status'] = 400
                response['message'] = 'File is empty'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            all_words_created = True
            for row in range(1, sheet.nrows):
                try:
                    keyword = str(sheet.cell_value(row, 0)).strip()
                    keyword = validation_obj.remo_html_from_string(keyword)
                    keyword = validation_obj.remo_special_tag_from_string(keyword)

                    if len(keyword) > LIVECHAT_CHARACTER_LIMIT_SMALL_TEXT:
                        all_words_created = False
                        continue

                    if len(keyword) == 0:
                        all_words_created = False
                        continue

                    if not validation_obj.validate_keyword(keyword):
                        all_words_created = False
                        continue

                    if is_blacklist_keyword_present(keyword, user_obj, blacklist_for, LiveChatBlackListKeyword, LiveChatUser):
                        all_words_created = False 
                    else:
                        LiveChatBlackListKeyword.objects.create(
                            word=keyword.lower(), agent_id=user_obj, blacklist_keyword_for=blacklist_for)
                        response["status"] = "200"
                        description = "Added Blacklisted word for id" + \
                            " (" + str(user_obj.pk) + ")"
                        add_audit_trail(
                            "LIVECHATAPP",
                            user_obj.user,
                            "Add-Blacklistedkeyword",
                            description,
                            json.dumps(data),
                            request.META.get("PATH_INFO"),
                            request.META.get('HTTP_X_FORWARDED_FOR')
                        )

                except Exception as e:
                    all_words_created = False
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("CreateBlacklistedKeywordWithExcelAPI: %s at %s",
                                 e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
                    response["status_message"] = e

            response['status'] = 200
            response['message'] = 'success'
            response['all_words_created'] = all_words_created
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CreateBlacklistedKeywordWithExcelAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = e

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


CreateBlacklistedKeywordWithExcel = CreateBlacklistedKeywordWithExcelAPI.as_view()


class LiveChatTranscriptAPI(APIView):
    
    def post(self, request, *args, **kwargs):
        logger.info("Into LiveChatTranscriptAPI..",
                    extra={'AppName': 'LiveChat'})
        response = {}
        response["status_code"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            is_agent_request = data["is_agent_request"]
            session_id = data['session_id']
            is_feedback_transcript_request = data['is_feedback_transcript_request']
            
            if is_agent_request:
                if not request.user.is_authenticated:
                    response['status'] = 403
                    response['status_message'] = 'User is not authenticated'
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)
 
            customer_obj = LiveChatCustomer.objects.filter(session_id=session_id).first()
            
            if not customer_obj:
                response["status_code"] = "500"
                response["status_message"] = "This customer livechat session id does not exist."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            
            message_objs = LiveChatMISDashboard.objects.filter(livechat_customer=customer_obj).order_by('message_time')
            
            if is_agent_request:
                username = request.user.username
            else:
                username = customer_obj.agent_id.get_agent_name()
            
            if customer_obj.transcript_email:
                email_id = customer_obj.transcript_email
            else:
                email_id = customer_obj.email
                
            if not customer_obj.is_transcript_sent and (is_feedback_transcript_request or customer_obj.is_transcript_request_enabled):
                thread = threading.Thread(target=export_chat_transcript, args=(
                    username, email_id, customer_obj, message_objs, LiveChatTranslationCache, LiveChatFileAccessManagement), daemon=True)
                thread.start()
                customer_obj.is_transcript_sent = True    
                customer_obj.save(update_fields=['is_transcript_sent'])
            
            response['status'] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("LiveChatTranscriptAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)

LiveChatTranscript = LiveChatTranscriptAPI.as_view() 


class GetLiveChatSpecialCharacterToggleAPI(APIView):
    
    def post(self, request, *args, **kwargs):
        logger.info("Into GetLiveChatSpecialCharacterToggleAPI..",
                    extra={'AppName': 'LiveChat'})
        response = {}
        response["status_code"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            validation_obj = LiveChatInputValidation()

            session_id = validation_obj.remo_html_from_string(data["session_id"])
            customer_obj = LiveChatCustomer.objects.filter(session_id=session_id).first()
            agent_obj = customer_obj.agent_id

            admin_config = get_admin_config(
                agent_obj, LiveChatAdminConfig, LiveChatUser)

            response['is_special_character_allowed_in_file_name'] = admin_config.is_special_character_allowed_in_file_name
            response['is_special_character_allowed_in_chat'] = admin_config.is_special_character_allowed_in_chat
            response['status'] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetLiveChatSpecialCharacterToggleAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)

GetLiveChatSpecialCharacterToggle = GetLiveChatSpecialCharacterToggleAPI.as_view() 


class EnableLiveChatTranscriptAPI(APIView):
    
    def post(self, request, *args, **kwargs):
        logger.info("Into CheckLiveChatTranscriptAPI..",
                    extra={'AppName': 'LiveChat'})
        response = {}
        response["status_code"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            is_agent_request = data["is_agent_request"]
            session_id = data['session_id']
            
            if is_agent_request:
                if not request.user.is_authenticated:
                    response['status'] = 403
                    response['status_message'] = 'User is not authenticated'
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)
                
            customer_obj = LiveChatCustomer.objects.filter(session_id=session_id).first()
            
            if not customer_obj:
                response["status_code"] = "500"
                response["status_message"] = "This customer livechat session id does not exist."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            
            if "email_id" in data:
                email_id = data['email_id']
            else:
                email_id = customer_obj.email
                
            customer_obj.is_transcript_request_enabled = True
            customer_obj.transcript_email = email_id
            customer_obj.save(update_fields=["is_transcript_request_enabled", "transcript_email"])
            
            response['status'] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CheckLiveChatTranscriptAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)

EnableLiveChatTranscript = EnableLiveChatTranscriptAPI.as_view() 
