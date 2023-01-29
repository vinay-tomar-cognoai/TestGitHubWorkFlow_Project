import os
import sys
import json
import uuid
import random
import logging
from os import path
from zipfile import ZipFile
from os.path import basename
from itertools import groupby
from datetime import timezone, datetime, timedelta
import pytz

# Django REST framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, authentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from LiveChatApp.utils import *
from LiveChatApp.models import *
from EasyChatApp.models import Bot, Channel
from LiveChatApp.constants import *
from LiveChatApp.utils_analytics import *
from LiveChatApp.static_dummy_data import *
from LiveChatApp.utils_custom_encryption import *

from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect


User = get_user_model()

# Logger
logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def LiveChatAnalytics(request):
    try:
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            
            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)

            channel_obj_list = Channel.objects.all()
            bot_objs = user_obj.bots.all().filter(is_deleted=False)
            category_obj_list = user_obj.category.all().filter(
                bot__in=bot_objs, is_deleted=False)
            supervisors_list = user_obj.agents.filter(status="2", is_deleted=False)
            
            if user_obj.status != "3":
                user_obj_list = get_agents_under_this_user(user_obj)

                user_obj_list_without_admin = user_obj_list
                try:
                    user_obj_list_without_admin.remove(user_obj)
                except ValueError:
                    pass 
                
                total_entered_chat, total_closed_chat, denied_chats, chats_in_queue, abandon_chats, customer_declined_chats = get_chat_analytics(
                    user_obj_list, channel_obj_list, category_obj_list, Bot, LiveChatCustomer, LiveChatConfig)
                
                average_handle_time = get_livechat_avh(
                    user_obj_list, LiveChatCustomer)
                
                average_queue_time, avg_queue_time_percentage_change = get_livechat_avg_queue_time(
                    user_obj_list, channel_obj_list, category_obj_list, LiveChatCustomer)
                
                average_first_time_response_time = get_livechat_avg_first_time_response(
                    user_obj_list, channel_obj_list, category_obj_list, LiveChatCustomer)
                
                average_interactions = get_livechat_avg_interaction_per_chat(
                    user_obj_list, LiveChatCustomer, LiveChatMISDashboard)
                
                loggen_in_agents, ready_agents, not_ready_agents, stop_interaction_agents, current_capacity = get_agents_availibility_analytics(
                    user_obj_list_without_admin, LiveChatAdminConfig, LiveChatUser)
                
                nps_avg = get_nps_avg(user_obj_list, LiveChatCustomer)
                
                ongoing_chats = LiveChatCustomer.objects.filter(~Q(agent_id=None)).filter(
                    last_appearance_date__date=datetime.today().date(), is_session_exp=False, agent_id__in=user_obj_list).count()
                
                user_obj = LiveChatUser.objects.get(user=User.objects.get(
                    username=str(request.user.username)), is_deleted=False)
                
                disabled = False
                
                total_entered_chat_percent_change, total_closed_chat_percent_change, denied_chats_percent_change, abandon_chats_percent_change, customer_declined_chats_percent_change = 0, 0, 0, 0, 0
                
                avg_nps_percent_change, avg_handle_time_percent_change, inter_per_chat_percent_change = 0, 0, 0
                
                date_start = datetime.today().date()
                date_end = datetime.today().date()
                total_entered_chat_percent_change, total_closed_chat_percent_change, denied_chats_percent_change, abandon_chats_percent_change, customer_declined_chats_percent_change = get_chat_data_percentage_diff(total_entered_chat, total_closed_chat, denied_chats, abandon_chats, customer_declined_chats,
                                                                                                                                                                                                                       user_obj_list, Bot, LiveChatCustomer)
                avg_nps_percent_change, avg_handle_time_percent_change, inter_per_chat_percent_change = get_customer_report_percentage_change(
                    nps_avg, average_interactions, average_interactions, user_obj_list, LiveChatCustomer, LiveChatMISDashboard)
                
                voice_calls_initiated, voice_calls_percent_change = get_voice_calls_initiated(user_obj_list, LiveChatVoIPData)

                avg_call_duration, avg_call_duration_percent_change = get_average_call_duration(user_obj_list, LiveChatVoIPData)

                avg_video_call_duration, avg_video_call_duration_percent_change = get_average_video_call_duration(user_obj_list, LiveChatVoIPData)

                total_tickets_raised, tickets_raised_percent_change = get_total_tickets_raised(user_obj_list, LiveChatTicketAudit)

                avg_cobrowsing_duration, avg_cobrowsing_duration_percent_change = get_average_cobrowsing_duration(user_obj_list, LiveChatCobrowsingData)
                
                followup_leads = get_total_followup_leads(user_obj_list, LiveChatFollowupCustomer)

                customers_reported = get_customers_reported(user_obj_list, LiveChatReportedCustomer)

                total_customers_reported, customers_reported_percent_change = get_total_customers_reported(user_obj_list, LiveChatReportedCustomer)

                followup_leads_via_email, followup_leads_via_email_percent_change = get_followup_leads_via_email(user_obj_list, Channel, LiveChatFollowupCustomer) 

            else:
                return HttpResponse(ACCESS_DENIED) 

            if user_obj.static_analytics:
                STATIC_LIVECHAT_ANALYTICS_DUMMY_DATA[
                    "admin_config"] = admin_config
                STATIC_LIVECHAT_ANALYTICS_DUMMY_DATA["start_date"] = date_start
                STATIC_LIVECHAT_ANALYTICS_DUMMY_DATA["end_date"] = date_end
                STATIC_LIVECHAT_ANALYTICS_DUMMY_DATA["user_obj"] = user_obj
                STATIC_LIVECHAT_ANALYTICS_DUMMY_DATA["supervisors_list"] = supervisors_list
                return render(request, 'LiveChatApp/livechat_analytics.html', STATIC_LIVECHAT_ANALYTICS_DUMMY_DATA)
            return render(request, 'LiveChatApp/livechat_analytics.html', {
                "user_obj": user_obj,
                "total_entered_chat": total_entered_chat,
                "total_closed_chat": total_closed_chat,
                "denied_chats": denied_chats,
                "average_handle_time": average_handle_time,
                "loggen_in_agents": loggen_in_agents,
                "ready_agents": ready_agents,
                "not_ready_agents": not_ready_agents,
                "ongoing_chats": ongoing_chats,
                "stop_interaction_agents": stop_interaction_agents,
                "current_capacity": current_capacity,
                "chats_in_queue": chats_in_queue,
                "abandon_chats": abandon_chats,
                "nps_avg": nps_avg,
                "average_queue_time": average_queue_time,
                "average_interactions": average_interactions,
                "customer_declined_chats": customer_declined_chats,
                "admin_config": admin_config,
                "start_date": date_start,
                "end_date": date_end,
                "disabled": disabled,
                "avg_queue_time_percentage_change": avg_queue_time_percentage_change,
                "total_entered_chat_percent_change": total_entered_chat_percent_change,
                "total_closed_chat_percent_change": total_closed_chat_percent_change,
                "denied_chats_percent_change": denied_chats_percent_change,
                "abandon_chats_percent_change": abandon_chats_percent_change,
                "customer_declined_chats_percent_change": customer_declined_chats_percent_change,
                "avg_nps_percent_change": avg_nps_percent_change,
                "avg_handle_time_percent_change": avg_handle_time_percent_change,
                "inter_per_chat_percent_change": inter_per_chat_percent_change,
                "voice_calls_initiated": voice_calls_initiated,
                "voice_calls_percent_change": voice_calls_percent_change,
                "avg_call_duration": avg_call_duration,
                "avg_call_duration_percent_change": avg_call_duration_percent_change,
                "avg_video_call_duration": avg_video_call_duration,
                "avg_video_call_duration_percent_change": avg_video_call_duration_percent_change,
                "channel_obj_list": channel_obj_list,
                "total_tickets_raised": total_tickets_raised,
                "tickets_raised_percent_change": tickets_raised_percent_change,
                "category_obj_list": category_obj_list,
                "avg_cobrowsing_duration": avg_cobrowsing_duration,
                "avg_cobrowsing_duration_percent_change": avg_cobrowsing_duration_percent_change,
                "followup_leads": followup_leads,
                "customers_reported": customers_reported,
                "total_customers_reported": total_customers_reported,
                "customers_reported_percent_change": customers_reported_percent_change,
                "followup_leads_via_email": followup_leads_via_email,
                "followup_leads_via_email_percent_change": followup_leads_via_email_percent_change,
                "supervisors_list": supervisors_list,
                "average_first_time_response_time": average_first_time_response_time
            })
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("LiveChatAnalytics: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


def AgentAnalytics(request):
    try:
        if request.user.is_authenticated:

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            
            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)

            if not admin_config.is_agent_analytics_enabled:
                return HttpResponse(ACCESS_DENIED)
            
            if user_obj.status == "3":

                channel_obj_list = Channel.objects.all()
                user_obj_list = [user_obj]
                bot_obj = user_obj.bots.filter(is_deleted=False).first()
                livechat_config = LiveChatConfig.objects.filter(bot=bot_obj).first()
                
                total_closed_chats, total_closed_chats_percent_change = get_total_closed_chats(user_obj_list, LiveChatCustomer)
                
                average_interactions = get_livechat_avg_interaction_per_chat(
                    user_obj_list, LiveChatCustomer, LiveChatMISDashboard)

                average_handle_time = get_livechat_avh(
                    user_obj_list, LiveChatCustomer)
                
                nps_avg = get_nps_avg(user_obj_list, LiveChatCustomer)
                
                date_start = datetime.today().date()
                date_end = datetime.today().date()

                avg_nps_percent_change, avg_handle_time_percent_change, inter_per_chat_percent_change = get_customer_report_percentage_change(
                    nps_avg, average_handle_time, average_interactions, user_obj_list, LiveChatCustomer, LiveChatMISDashboard)

                avg_call_duration, avg_call_duration_percent_change = get_average_call_duration(user_obj_list, LiveChatVoIPData)

                avg_video_call_duration, avg_video_call_duration_percent_change = get_average_video_call_duration(user_obj_list, LiveChatVoIPData)

                total_tickets_raised, tickets_raised_percent_change = get_total_tickets_raised(user_obj_list, LiveChatTicketAudit)

                avg_cobrowsing_duration, avg_cobrowsing_duration_percent_change = get_average_cobrowsing_duration(user_obj_list, LiveChatCobrowsingData)
                
                followup_leads, followup_leads_percent_change = get_followup_leads(user_obj_list, LiveChatFollowupCustomer)

                disabled = False
                date_start = datetime.today().date()
                date_end = datetime.today().date()
            else:
                return HttpResponse(ACCESS_DENIED) 

            return render(request, 'LiveChatApp/livechat_agent_analytics.html', {
                "user_obj": user_obj,
                "admin_config": admin_config,
                "livechat_config": livechat_config,
                "channel_obj_list": channel_obj_list,
                "total_closed_chats": total_closed_chats,
                "total_closed_chats_percent_change": total_closed_chats_percent_change,
                "average_interactions": average_interactions,
                "average_handle_time": average_handle_time,
                "nps_avg": nps_avg,
                "inter_per_chat_percent_change": inter_per_chat_percent_change,
                "avg_handle_time_percent_change": avg_handle_time_percent_change,
                "avg_nps_percent_change": avg_nps_percent_change,
                "avg_call_duration": avg_call_duration,
                "avg_call_duration_percent_change": avg_call_duration_percent_change,
                "avg_video_call_duration": avg_video_call_duration,
                "avg_video_call_duration_percent_change": avg_video_call_duration_percent_change,
                "total_tickets_raised": total_tickets_raised,
                "tickets_raised_percent_change": tickets_raised_percent_change,
                "avg_cobrowsing_duration": avg_cobrowsing_duration,
                "avg_cobrowsing_duration_percent_change": avg_cobrowsing_duration_percent_change,
                "followup_leads": followup_leads,
                "followup_leads_percent_change": followup_leads_percent_change,
                "disabled": disabled,
                "start_date": date_start,
                "end_date": date_end,
            })
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("AgentAnalytics: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


def OfflineChatsReport(request):
    try:
        import datetime
        if request.user.is_authenticated:
            channel_obj_list = Channel.objects.all()
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)
            channel_name = request.GET.get('channel_name')
            if channel_name == 'None':
                channel_name = 'All'
            if user_obj.status != "3":
                category_list = user_obj.category.all()
                datetime_start = (datetime.datetime.today() -
                                  datetime.timedelta(7)).date()
                datetime_end = datetime.datetime.today().date()
                selected_category_pk = 0

                try:
                    channel_obj = Channel.objects.get(name=channel_name)
                except Exception:
                    channel_obj = None

                try:
                    start_date = request.GET.get('start_date')
                    end_date = request.GET.get('end_date')

                    if start_date and end_date:
                        datetime_start = datetime.datetime.strptime(start_date, DATE_YYYY_MM_DD).date()
                        datetime_end = datetime.datetime.strptime(end_date, DATE_YYYY_MM_DD).date()  # noqa: F841
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.warning("datetime_start and datetime_end is not in valid format %s at line no %s", str(
                        e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
                    selected_category_pk = 0

                if user_obj.static_analytics:
                    abandoned_chats = STATIC_LIVECHAT_ABANDONED_CHATS_REPORT_DATA
                else:
                    selected_category_pk = request.GET.get('selected_category_pk')

                    if not selected_category_pk or selected_category_pk == '0':
                        selected_category_pk = 0

                    if not selected_category_pk:
                        abandoned_chats = LiveChatCustomer.objects.filter(bot__in=user_obj.bots.all(
                        ), is_system_denied=True, request_raised_date__range=[datetime_start, datetime_end], category__in=category_list).order_by('-joined_date')
                    else:
                        category = LiveChatCategory.objects.get(
                            pk=int(selected_category_pk))
                        abandoned_chats = LiveChatCustomer.objects.filter(category=category, bot__in=user_obj.bots.all(
                        ), is_system_denied=True, request_raised_date__range=[datetime_start, datetime_end]).order_by('-joined_date')

                    if channel_name != None and channel_name != "All":
                        abandoned_chats = abandoned_chats.filter(
                            channel=channel_obj)

                page = request.GET.get('page')
                total_abandoned_chats, abandoned_chats, start_point, end_point = paginate(
                    abandoned_chats, ABANDONED_CHATS_COUNT, page)

                user_obj = LiveChatUser.objects.get(user=User.objects.get(
                    username=str(request.user.username)), is_deleted=False)
            else:
                return HttpResponse(ACCESS_DENIED)

            template_to_render = 'LiveChatApp/offline_chats_report.html'

            return render(request, template_to_render, {
                "user_obj": user_obj,
                "total_abandoned_chats": total_abandoned_chats,
                "abandoned_chats": abandoned_chats,
                "start_date": datetime_start,
                "end_date": datetime_end,
                "start_point": start_point,
                "end_point": end_point,
                "selected_category_pk": int(selected_category_pk),
                "category_list": category_list,
                "admin_config": admin_config,
                "channel_obj_list": channel_obj_list,
                "channel_name": channel_name,
                "is_report_generation_via_kafka_enabled": is_kafka_enabled(),
            })
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("OfflineChatsReport: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


def AbandonedChatsReport(request):
    try:
        import datetime
        if request.user.is_authenticated:
            channel_obj_list = Channel.objects.all()
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)
            channel_name = request.GET.get('channel_name')
            if channel_name == 'None':
                channel_name = 'All'
            if user_obj.status != "3":
                category_list = user_obj.category.all()
                datetime_start = (datetime.datetime.today() -
                                  datetime.timedelta(7)).date()
                datetime_end = datetime.datetime.today().date()
                selected_category_pk = 0

                try:
                    channel_obj = Channel.objects.get(name=channel_name)
                except Exception:
                    channel_obj = None

                try:
                    start_date = request.GET.get('start_date')
                    end_date = request.GET.get('end_date')

                    if start_date and end_date:
                        datetime_start = datetime.datetime.strptime(start_date, DATE_YYYY_MM_DD).date()
                        datetime_end = datetime.datetime.strptime(end_date, DATE_YYYY_MM_DD).date()  # noqa: F841
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.warning("datetime_start and datetime_end is not in valid format %s at line no %s", str(
                        e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
                    selected_category_pk = 0

                if user_obj.static_analytics:
                    customer_declined_chats = STATIC_LIVECHAT_TOTAL_DECLINED_CHATS_REPORT_DATA
                else:
                    selected_category_pk = request.GET.get('selected_category_pk')
                    if not selected_category_pk or selected_category_pk == '0':
                        selected_category_pk = 0

                    if not selected_category_pk:
                        customer_declined_chats = LiveChatCustomer.objects.filter(bot__in=user_obj.bots.all(
                        ), agent_id=None, abruptly_closed=True, request_raised_date__range=[datetime_start, datetime_end], category__in=category_list).order_by('-joined_date')
                    else:
                        category = LiveChatCategory.objects.get(
                            pk=int(selected_category_pk))
                        customer_declined_chats = LiveChatCustomer.objects.filter(category=category, bot__in=user_obj.bots.all(
                        ), agent_id=None, abruptly_closed=True, request_raised_date__range=[datetime_start, datetime_end]).order_by('-joined_date')

                    if channel_name != None and channel_name != "All":
                        customer_declined_chats = customer_declined_chats.filter(
                            channel=channel_obj)

                page = request.GET.get('page')
                total_customer_declined_chats, customer_declined_chats, start_point, end_point = paginate(
                    customer_declined_chats, TOTAL_CUSTOMER_DECLINED_CHATS_COUNT, page)

                user_obj = LiveChatUser.objects.get(user=User.objects.get(
                    username=str(request.user.username)), is_deleted=False)
            else:
                return HttpResponse(ACCESS_DENIED)

            template_to_render = 'LiveChatApp/abandoned_chats_report.html'

            return render(request, template_to_render, {
                "user_obj": user_obj,
                "total_customer_declined_chats": total_customer_declined_chats,
                "customer_declined_chats": customer_declined_chats,
                "start_date": datetime_start,
                "end_date": datetime_end,
                "start_point": start_point,
                "end_point": end_point,
                "selected_category_pk": int(selected_category_pk),
                "category_list": category_list,
                "admin_config": admin_config,
                "channel_obj_list": channel_obj_list,
                "channel_name": channel_name,
                "is_report_generation_via_kafka_enabled": is_kafka_enabled(),
            })
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("AbandonedChatsReport: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


def MissedChatsReport(request):
    try:
        import datetime
        if request.user.is_authenticated:
            channel_obj_list = Channel.objects.all()
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)
            channel_name = request.GET.get('channel_name')
            if channel_name == 'None':
                channel_name = 'All'
            if user_obj.status != "3":
                category_list = user_obj.category.all()
                datetime_start = (datetime.datetime.today() -
                                  datetime.timedelta(7)).date()
                datetime_end = datetime.datetime.today().date()
                selected_category_pk = 0

                try:
                    channel_obj = Channel.objects.get(name=channel_name)
                except Exception:
                    channel_obj = None

                try:
                    start_date = request.GET.get('start_date')
                    end_date = request.GET.get('end_date')

                    if start_date and end_date:
                        datetime_start = datetime.datetime.strptime(start_date, DATE_YYYY_MM_DD).date()
                        datetime_end = datetime.datetime.strptime(end_date, DATE_YYYY_MM_DD).date()  # noqa: F841
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.warning("datetime_start and datetime_end is not in valid format %s at line no %s", str(
                        e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
                    selected_category_pk = 0

                if user_obj.static_analytics:
                    offline_messages = STATIC_LIVECHAT_OFFLINE_MESSAGE_REPORT_DATA
                else:
                    selected_category_pk = request.GET.get('selected_category_pk')

                    if not selected_category_pk or selected_category_pk == '0':
                        selected_category_pk = 0

                    if not selected_category_pk:
                        offline_messages = LiveChatCustomer.objects.filter(bot__in=user_obj.bots.all(
                        ), is_denied=True, is_system_denied=False, request_raised_date__range=[datetime_start, datetime_end], category__in=category_list).order_by('-joined_date')
                    else:
                        category = LiveChatCategory.objects.get(
                            pk=int(selected_category_pk))
                        offline_messages = LiveChatCustomer.objects.filter(category=category, bot__in=user_obj.bots.all(
                        ), is_denied=True, is_system_denied=False, request_raised_date__range=[datetime_start, datetime_end]).order_by('-joined_date')

                    if channel_name != None and channel_name != "All":
                        offline_messages = offline_messages.filter(
                            channel=channel_obj)

                page = request.GET.get('page')
                total_offline_messages, offline_messages, start_point, end_point = paginate(
                    offline_messages, OFFLINE_MESSAGE_COUNT, page)

                user_obj = LiveChatUser.objects.get(user=User.objects.get(
                    username=str(request.user.username)), is_deleted=False)
            else:
                return HttpResponse(ACCESS_DENIED)

            template_to_render = 'LiveChatApp/missed_chats_report.html'
            if user_obj.static_analytics:
                template_to_render = STATIC_MISSED_CHATS_REPORT_PATH

            return render(request, template_to_render, {
                "user_obj": user_obj,
                "total_offline_messages": total_offline_messages,
                "offline_messages": offline_messages,
                "start_date": datetime_start,
                "end_date": datetime_end,
                "start_point": start_point,
                "end_point": end_point,
                "selected_category_pk": int(selected_category_pk),
                "category_list": category_list,
                "admin_config": admin_config,
                "channel_obj_list": channel_obj_list,
                "channel_name": channel_name,
                "is_report_generation_via_kafka_enabled": is_kafka_enabled(),
            })
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("MissedChatsReport: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


def LoginLogoutReport(request):
    try:
        import datetime
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)
            if user_obj.status != "3":
                datetime_start = (datetime.datetime.today() -
                                  datetime.timedelta(7)).date()
                datetime_end = datetime.datetime.today().date()

                try:
                    start_date = request.GET.get('start_date')
                    end_date = request.GET.get('end_date')

                    if start_date and end_date:
                        datetime_start = datetime.datetime.strptime(start_date, DATE_YYYY_MM_DD).date()
                        datetime_end = datetime.datetime.strptime(end_date, DATE_YYYY_MM_DD).date()  # noqa: F841
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.warning("datetime_start and datetime_end is not in valid format %s at line no %s", str(
                        e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

                agent_list = get_agents_under_this_user(user_obj)
                selected_supervisors = request.GET.get('selected_supervisors')
                supervisor_objs = []
                if selected_supervisors and user_obj.status == '1':
                    selected_supervisors = json.loads(selected_supervisors)
                    if len(selected_supervisors):
                        agent_list = get_agents_as_per_supervisors(selected_supervisors, agent_list, LiveChatUser)
                        supervisor_objs = LiveChatUser.objects.filter(pk__in=selected_supervisors)
                else:
                    selected_supervisors = [] 

                session_objects = LiveChatSessionManagement.objects.filter(user__in=agent_list, session_starts_at__date__range=[
                                                                           datetime_start, datetime_end]).order_by('-session_starts_at')
                    
                selected_agent_pk = request.GET.get('selected_agent_pk')

                if not selected_agent_pk or selected_agent_pk == '0' or selected_agent_pk == 'null':
                    selected_agent_pk = 0
                
                if selected_agent_pk:
                    user = LiveChatUser.objects.get(pk=int(selected_agent_pk))
                    session_objects = session_objects.filter(user=user)

                if user_obj.static_analytics:
                    session_objects = STATIC_LIVECHAT_LOGIN_LOGOUT_REPORT_DATA

                page = request.GET.get('page')
                total_session_objects, session_objects, start_point, end_point = paginate(
                    session_objects, SESSION_MANAGEMENT_ITEM_COUNT, page)

                user_obj = LiveChatUser.objects.get(user=User.objects.get(
                    username=str(request.user.username)), is_deleted=False)
                supervisors_list = user_obj.agents.filter(status="2", is_deleted=False)
                agent_list = get_agents_under_this_user(user_obj)
            else:
                return HttpResponse(ACCESS_DENIED)

            template_to_render = 'LiveChatApp/login_logout_report.html'
            if user_obj.static_analytics:
                template_to_render = 'LiveChatApp/static_login_logout_report.html'

            return render(request, template_to_render, {
                "user_obj": user_obj,
                "total_session_objects": total_session_objects,
                "session_objects": session_objects,
                "start_date": datetime_start,
                "end_date": datetime_end,
                "start_point": start_point,
                "end_point": end_point,
                "selected_agent_pk": int(selected_agent_pk),
                "agent_list": agent_list,
                "admin_config": admin_config,
                "supervisors_list": supervisors_list,
                "supervisor_objs": supervisor_objs,
                "selected_supervisors": json.dumps(selected_supervisors),
                "is_report_generation_via_kafka_enabled": is_kafka_enabled(),
            })
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("LoginLogoutReport: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


def DownloadChatTranscript(request):
    response = {}
    response["status_code"] = 500
    response["status_message"] = ""
    try:
        if request.user.is_authenticated and request.method == "GET":
            pk = request.GET["pk"]
            livechat_customer = LiveChatCustomer.objects.get(pk=pk)
            user_obj = LiveChatUser.objects.get(user=User.objects.get(
                username=str(request.user.username)), is_deleted=False)
            bot_obj = user_obj.bots.all()[0]
            config_obj = LiveChatConfig.objects.get(bot=bot_obj)
            filename, path_to_file = create_excel_of_chat(livechat_customer, config_obj.is_original_information_in_reports_enabled)
            if path_to_file != "":
                response = FileResponse(open(path_to_file, 'rb'))
                response['Content-Type'] = 'application/octet-stream'
                response['Content-Disposition'] = 'attachment;filename="' + \
                    filename + '"'
                response['Content-Length'] = os.path.getsize(path_to_file)
                return response
            else:
                HttpResponse(status=404)
        else:
            return HttpResponse(status=404)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[NLP]: Error DownloadChatTranscript %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return HttpResponse(status=500)


def AgentNotReadyReport(request):
    try:
        import datetime
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)
            if user_obj.status != "3":
                agent_list = get_agents_under_this_user(user_obj)
                datetime_start = (datetime.datetime.today() -
                                  datetime.timedelta(7)).date()
                datetime_end = datetime.datetime.today().date()

                try:
                    start_date = request.GET.get('start_date')
                    end_date = request.GET.get('end_date')

                    if start_date and end_date:
                        datetime_start = datetime.datetime.strptime(start_date, DATE_YYYY_MM_DD).date()
                        datetime_end = datetime.datetime.strptime(end_date, DATE_YYYY_MM_DD).date()  # noqa: F841
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.warning("datetime_start and datetime_end is not in valid format %s at line no %s", str(
                        e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

                selected_supervisors = request.GET.get('selected_supervisors')
                supervisor_objs = []
                if selected_supervisors and user_obj.status == '1':
                    selected_supervisors = json.loads(selected_supervisors)
                    if len(selected_supervisors):
                        agent_list = get_agents_as_per_supervisors(selected_supervisors, agent_list, LiveChatUser)
                        supervisor_objs = LiveChatUser.objects.filter(pk__in=selected_supervisors)
                else:
                    selected_supervisors = [] 

                not_ready_objects = LiveChatAgentNotReady.objects.filter(user__in=agent_list, not_ready_starts_at__date__range=[
                    datetime_start, datetime_end]).order_by('-not_ready_starts_at')
                
                selected_agent_pk = request.GET.get('selected_agent_pk')

                if not selected_agent_pk or selected_agent_pk == '0' or selected_agent_pk == 'null':
                    selected_agent_pk = 0

                if selected_agent_pk:
                    user = LiveChatUser.objects.get(pk=int(selected_agent_pk))
                    not_ready_objects = not_ready_objects.filter(user=user)

                if user_obj.static_analytics:
                    not_ready_objects = STATIC_LIVECHAT_AGENT_NOT_READY_REPORT_DATA

                page = request.GET.get('page')
                total_not_ready_objects, not_ready_objects, start_point, end_point = paginate(
                    not_ready_objects, AGENT_NOT_READY_REPORT_ITEM_COUNT, page)

                user_obj = LiveChatUser.objects.get(user=User.objects.get(
                    username=str(request.user.username)), is_deleted=False)
                supervisors_list = user_obj.agents.filter(status="2", is_deleted=False)
                agent_list = get_agents_under_this_user(user_obj)
            else:
                return HttpResponse(ACCESS_DENIED)

            template_to_render = 'LiveChatApp/livechat_agent_not_ready_report.html'
            if user_obj.static_analytics:
                template_to_render = 'LiveChatApp/static_livechat_agent_not_ready_report.html'

            return render(request, template_to_render, {
                "user_obj": user_obj,
                "total_not_ready_objects": total_not_ready_objects,
                "not_ready_objects": not_ready_objects,
                "start_date": datetime_start,
                "end_date": datetime_end,
                "start_point": start_point,
                "end_point": end_point,
                "selected_agent_pk": int(selected_agent_pk),
                "agent_list": agent_list,
                "admin_config": admin_config,
                "supervisors_list": supervisors_list,
                "supervisor_objs": supervisor_objs,
                "selected_supervisors": json.dumps(selected_supervisors),
                "is_report_generation_via_kafka_enabled": is_kafka_enabled(),
            })
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("AgentNotReadyReport: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


def AgentPerformanceReport(request):
    try:
        import datetime
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)
            if user_obj.status != "3":
                agent_list = get_agents_under_this_user(user_obj)
                datetime_start = (datetime.datetime.today() -
                                  datetime.timedelta(7)).date()
                datetime_end = datetime.datetime.today().date()

                try:
                    start_date = request.GET.get('start_date')
                    end_date = request.GET.get('end_date')
                    
                    if start_date and end_date:
                        datetime_start = datetime.datetime.strptime(start_date, DATE_YYYY_MM_DD).date()
                        datetime_end = datetime.datetime.strptime(end_date, DATE_YYYY_MM_DD).date()  # noqa: F841
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.warning("datetime_start and datetime_end is not in valid format %s at line no %s", str(
                        e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

                selected_supervisors = request.GET.get('selected_supervisors')
                supervisor_objs = []
                if selected_supervisors and user_obj.status == '1':
                    selected_supervisors = json.loads(selected_supervisors)
                    if len(selected_supervisors):
                        agent_list = get_agents_as_per_supervisors(selected_supervisors, agent_list, LiveChatUser)
                        supervisor_objs = LiveChatUser.objects.filter(pk__in=selected_supervisors)
                else:
                    selected_supervisors = [] 
                    
                selected_agent_pk = request.GET.get('selected_agent_pk')
                if not selected_agent_pk:
                    selected_agent_pk = []
                else:
                    selected_agent_pk = json.loads(selected_agent_pk)

                agent_objects = LiveChatSessionManagement.objects.filter(user__in=agent_list, session_starts_at__date__range=[
                    datetime_start, datetime_end]).order_by('-session_starts_at')
                
                selected_users = []
                if selected_agent_pk:
                    selected_users = LiveChatUser.objects.filter(pk__in=selected_agent_pk)
                    agent_objects = agent_objects.filter(user__in=selected_users)

                if user_obj.static_analytics:
                    agent_objects = STATIC_LIVECHAT_PERFORMANCE_REPORT_DATA

                page = request.GET.get('page')
                total_agent_objects, agent_objects, start_point, end_point = paginate(
                    agent_objects, AGENT_PERFORMANCE_REPORT_ITEM_COUNT, page)

                user_obj = LiveChatUser.objects.get(user=User.objects.get(
                    username=str(request.user.username)), is_deleted=False)
                supervisors_list = user_obj.agents.filter(status="2", is_deleted=False)
                agent_list = get_agents_under_this_user(user_obj)
            else:
                return HttpResponse(ACCESS_DENIED)

            template_to_render = 'LiveChatApp/livechat_agent_performance_report.html'
            if user_obj.static_analytics:
                template_to_render = 'LiveChatApp/static_performance_report.html'

            return render(request, template_to_render, {
                "user_obj": user_obj,
                "total_agent_objects": total_agent_objects,
                "agent_objects": agent_objects,
                "start_date": datetime_start,
                "end_date": datetime_end,
                "start_point": start_point,
                "end_point": end_point,
                "selected_agent_pk": json.dumps(selected_agent_pk),
                "agent_list": agent_list,
                "admin_config": admin_config,
                "selected_users": selected_users,
                "supervisors_list": supervisors_list,
                "supervisor_objs": supervisor_objs,
                "selected_supervisors": json.dumps(selected_supervisors),
                "is_report_generation_via_kafka_enabled": is_kafka_enabled(),
            })
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("AgentPerformanceReport: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


def HourlyInteractionCountPage(request):
    try:
        if request.user.is_authenticated:
            user_obj = get_livechat_user_obj_from_request(request, LiveChatUser, User)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)
            if user_obj.status != "3":
                bot_list = user_obj.bots.all()
                channel_list = Channel.objects.all()
                category_obj_list = user_obj.category.all().filter(bot__in=bot_list, is_deleted=False)
                datetime_start = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
                datetime_end = (datetime_start - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)

                range_start = (datetime_start - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
                interaction_objects = []
                if user_obj.static_analytics:
                    interaction_objects = STATIC_LIVECHAT_HOURLY_INTERACTION_REPORT_DATA
                
                user_obj = LiveChatUser.objects.get(user=User.objects.get(
                    username=str(request.user.username)), is_deleted=False)
            else:
                return HttpResponse(ACCESS_DENIED)

            template_to_render = 'LiveChatApp/livechat_hourly_interaction_report.html'
            if user_obj.static_analytics:
                template_to_render = 'LiveChatApp/static_livechat_hourly_interaction_report.html'

            return render(request, template_to_render, {
                "user_obj": user_obj,
                "interaction_objects": interaction_objects,
                "start_date": datetime_start,
                "end_date": datetime_end,
                "range_start": range_start,
                "range_end": datetime_start,
                "bot_list": bot_list,
                "admin_config": admin_config,
                "category_obj_list": category_obj_list,
                "channel_list": channel_list,
                "is_report_generation_via_kafka_enabled": is_kafka_enabled(),
            })
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("HourlyInteractionCount: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


class HourlyInteractionCountByDateAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)
            user_obj = get_livechat_user_obj_from_request(request, LiveChatUser, User)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)

            if user_obj.status != "3":
                if user_obj.static_analytics:
                    response = STATIC_LIVECHAT_HOURLY_INTERACTION_REPORT_DATA
                else:
                    agent_list = get_agents_under_this_user(user_obj)

                    channel_list = []
                    channels = requested_data['channel']
                    if channels:
                        if not isinstance(channels, list):
                            channels = channels.split(',')
                        channel_list = Channel.objects.filter(pk__in=channels)
                    else:
                        channel_list = Channel.objects.all()

                    category_list = []
                    categories = requested_data['category']
                    if categories:
                        if not isinstance(categories, list):
                            categories = categories.split(',')
                        category_list = LiveChatCategory.objects.filter(pk__in=categories)
                    else:
                        category_list = LiveChatCategory.objects.filter(is_deleted=False)

                    source_list = []
                    sources = requested_data['source']
                    if sources:
                        if not isinstance(sources, list):
                            source_list = sources.split(',')
                    else:
                        source_list = ['1', '2', '3']

                    selected_date = requested_data['selected_date']
                    date_format = "%Y-%m-%d"
                    datetime_start = datetime.strptime(selected_date, date_format).replace(hour=0, minute=0, second=0)
                    datetime_end = datetime_start.replace(hour=23, minute=59, second=59)

                    bot_list = user_obj.bots.all()

                    selected_bot_pk = requested_data['bot_pk']
                    if not selected_bot_pk or selected_bot_pk == '0':
                        selected_bot_pk = 0

                    if selected_bot_pk == 0:
                        query_bot_obj_list = bot_list
                    else:
                        query_bot_obj_list = [
                            Bot.objects.get(pk=int(selected_bot_pk))]

                    bot_names = ", ".join([bot_obj.name for bot_obj in query_bot_obj_list])

                    interaction_objects = []
                    interaction_object_list = LiveChatCustomer.objects.filter(agent_id__in=agent_list,
                                                                              bot__in=query_bot_obj_list,
                                                                              request_raised_date__range=[
                                                                                  datetime_start.date(), datetime_end.date()],
                                                                              channel__in=channel_list, category__in=category_list,
                                                                              source_of_incoming_request__in=source_list
                                                                              ).order_by('-joined_date')

                    current_datetime = datetime_start
                    current_datetime_end = datetime_end

                    tz = pytz.timezone(settings.TIME_ZONE)
                    current_datetime = current_datetime.astimezone(tz)
                    current_datetime_end = current_datetime_end.astimezone(tz)

                    start_time_obj = current_datetime.time().replace(hour=0, minute=0, second=0)
                    for itr in range(1, 25):
                        if itr != 24:
                            end_time_obj = current_datetime.time().replace(hour=itr, minute=0, second=0)
                        else:
                            end_time_obj = current_datetime.time().replace(hour=itr - 1, minute=59, second=59)
                        interaction_count = interaction_object_list.filter(request_raised_date=current_datetime.date(),
                                                                           joined_date__time__range=[
                                                                               start_time_obj, end_time_obj]
                                                                           ).count()
                        
                        interaction_objects.append({"date": current_datetime, "start_time": start_time_obj,
                                                        "end_time": end_time_obj, "bot_name": bot_names, "frequency": interaction_count})                            
                        
                        start_time_obj = current_datetime.time().replace(hour=itr % 24, minute=0, second=1)

                    interaction_objects = sorted(interaction_objects, key=lambda val: (val['start_time']))

                    interaction_count_table_data = []
                    for interaction_object in interaction_objects:
                        interaction_object_as_string = {
                            "date": interaction_object["date"].strftime("%d-%b-%Y"),
                            "start_time": interaction_object["start_time"].strftime("%I:%M %p"),
                            "end_time": interaction_object["end_time"].strftime("%I:%M %p"),
                            "bot_name": interaction_object["bot_name"],
                            "frequency": interaction_object["frequency"],
                        }
                        interaction_count_table_data.append(interaction_object_as_string)
                    response["peak_hours_daily_table_data"] = interaction_count_table_data
                            
                    interaction_count_daily_graph_label_data = []
                    interaction_count_daily_graph_count_data = [0]

                    for itr in range(0, 25):
                        label = f"{interaction_objects[0]['date'].strftime('%Y-%m-%d')} {str(itr).zfill(2)}:00"
                        value = 0
                        try:
                            if itr != 24:
                                value = interaction_objects[itr]['frequency']
                        except Exception:
                            value = 0

                        interaction_count_daily_graph_label_data.append(label)
                        interaction_count_daily_graph_count_data.append(value)

                    response["peak_hours_daily_graph_data"] = {
                        "interaction_count_daily_graph_label_data": interaction_count_daily_graph_label_data,
                        "interaction_count_daily_graph_count_data": interaction_count_daily_graph_count_data,
                        "selected_date": interaction_objects[0]["date"].strftime("%d-%m-%Y")
                    }

                response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("HourlyInteractionCountByDateAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


HourlyInteractionCountByDate = HourlyInteractionCountByDateAPI.as_view()


class HourlyInteractionCumulativeCountByDateRangeAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)
            user_obj = get_livechat_user_obj_from_request(request, LiveChatUser, User)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)

            if user_obj.status != "3":
                if user_obj.static_analytics:
                    response = STATIC_LIVECHAT_HOURLY_INTERACTION_REPORT_DATA
                else:
                    agent_list = get_agents_under_this_user(user_obj)

                    channel_list = []
                    channels = requested_data['channel']
                    if channels:
                        if not isinstance(channels, list):
                            channels = channels.split(',')
                        channel_list = Channel.objects.filter(pk__in=channels)
                    else:
                        channel_list = Channel.objects.all()

                    category_list = []
                    categories = requested_data['category']
                    if categories:
                        if not isinstance(categories, list):
                            categories = categories.split(',')
                        category_list = LiveChatCategory.objects.filter(pk__in=categories)
                    else:
                        category_list = LiveChatCategory.objects.filter(is_deleted=False)

                    source_list = []
                    sources = requested_data['source']
                    if sources:
                        if not isinstance(sources, list):
                            source_list = sources.split(',')
                    else:
                        source_list = ['1', '2', '3']

                    date_format = "%Y-%m-%d"
                    range_start_date = requested_data['range_start_date']
                    datetime_start = datetime.strptime(range_start_date, date_format).replace(hour=0, minute=0, second=0, microsecond=0)
                    range_end_date = requested_data['range_end_date']
                    datetime_end = datetime.strptime(range_end_date, date_format).replace(hour=23, minute=59, second=59)

                    no_of_days_in_range = (datetime_end + timedelta(seconds=2) - datetime_start).days

                    bot_list = user_obj.bots.all()
                    selected_bot_pk = requested_data['bot_pk']
                    if not selected_bot_pk or selected_bot_pk == '0':
                        selected_bot_pk = 0

                    if selected_bot_pk == 0:
                        query_bot_obj_list = bot_list
                    else:
                        query_bot_obj_list = [
                            Bot.objects.get(pk=int(selected_bot_pk))]
                    
                    interaction_objects = []

                    interaction_object_list = LiveChatCustomer.objects.filter(agent_id__in=agent_list,
                                                                              bot__in=query_bot_obj_list,
                                                                              request_raised_date__range=[
                                                                                  datetime_start.date(), datetime_end.date()],
                                                                              channel__in=channel_list, category__in=category_list,
                                                                              source_of_incoming_request__in=source_list).order_by('-joined_date'
                                                                                                                                   )

                    current_datetime = datetime_start
                    current_datetime_end = datetime_end
                    
                    tz = pytz.timezone(settings.TIME_ZONE)
                    current_datetime = current_datetime.astimezone(tz)
                    current_datetime_end = current_datetime_end.astimezone(tz)

                    first_iteration = True

                    while current_datetime <= current_datetime_end:
                        start_time_obj = current_datetime.time().replace(hour=0, minute=0, second=0)
                        for itr in range(1, 25):
                            if current_datetime.date() == datetime.now().date() and start_time_obj > datetime.now().time():
                                break
                            if itr != 24:
                                end_time_obj = current_datetime.time().replace(hour=itr, minute=0, second=0)
                            else:
                                end_time_obj = current_datetime.time().replace(hour=itr - 1, minute=59, second=59)
                            
                            interaction_count = interaction_object_list.filter(request_raised_date=current_datetime.date(
                            ), joined_date__time__range=[start_time_obj, end_time_obj]).count()

                            if first_iteration:
                                interaction_objects.append({
                                    "start_time": start_time_obj,
                                    "end_time": end_time_obj,
                                    "frequency": interaction_count,
                                })
                            else:    
                                interaction_objects[itr - 1]["frequency"] += interaction_count
                            
                            start_time_obj = current_datetime.time().replace(hour=itr % 24, minute=0, second=1)

                        current_datetime = current_datetime + timedelta(days=1)
                        first_iteration = False

                    interaction_objects = sorted(interaction_objects, key=lambda val: (val['frequency']), reverse=True)

                    interaction_count_cumulative_graph_label_data = []
                    interaction_count_cumulative_graph_count_data = []

                    for itr in range(0, 24):
                        label = f"{datetime_start.strftime('%Y-%m-%d')} {str(itr).zfill(2)}:00"

                        endtime = interaction_objects[itr]["end_time"].strftime("%H:%M")
                        y_axis = f"{datetime_start.strftime('%Y-%m-%d')} {endtime}"
                        x_axis = itr + 1
                        count = interaction_objects[itr]["frequency"]
                        average = interaction_objects[itr]['frequency'] / no_of_days_in_range
                        average = round(average, 1)

                        start_time = interaction_objects[itr]["start_time"].strftime("%I:%M %p")
                        end_time = interaction_objects[itr]["end_time"].strftime("%I:%M %p")

                        value = {
                            "x_axis": x_axis,
                            "y_axis": y_axis,
                            "average": average,
                            "count": count,
                            "start_time": start_time,
                            "end_time": end_time
                        }
                        interaction_count_cumulative_graph_label_data.append(label)
                        interaction_count_cumulative_graph_count_data.append(value)

                    response["peak_hours_cumulative_graph_data"] = {
                        "interaction_count_cumulative_graph_label_data": interaction_count_cumulative_graph_label_data,
                        "interaction_count_cumulative_graph_count_data": interaction_count_cumulative_graph_count_data,
                        "no_of_days_in_range": no_of_days_in_range
                    }

                response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("HourlyInteractionCountByDateAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)

HourlyInteractionCumulativeCountByDateRange = HourlyInteractionCumulativeCountByDateRangeAPI.as_view()


def DailyInteractionCount(request):
    try:
        import datetime
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)
            if user_obj.status != "3":
                agent_list = get_agents_under_this_user(user_obj)
                bot_list = user_obj.bots.all()
                datetime_start = (datetime.datetime.today() -
                                  datetime.timedelta(7)).date()
                datetime_end = datetime.datetime.today().date()
                selected_bot_pk = 0

                try:
                    start_date = request.GET.get('start_date')
                    end_date = request.GET.get('end_date')

                    if start_date and end_date:
                        datetime_start = datetime.datetime.strptime(start_date, DATE_YYYY_MM_DD).date()
                        datetime_end = datetime.datetime.strptime(end_date, DATE_YYYY_MM_DD).date()  # noqa: F841
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.warning("datetime_start and datetime_end is not in valid format %s at line no %s", str(
                        e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

                interaction_objects = []
                interaction_object_list = LiveChatCustomer.objects.filter(
                    agent_id__in=agent_list, request_raised_date__range=[datetime_start, datetime_end]).order_by('-joined_date')

                selected_bot_pk = request.GET.get('selected_bot_pk')
                if not selected_bot_pk:
                    selected_bot_pk = 0

                if not selected_bot_pk or selected_bot_pk == '0':
                    query_bot_obj_list = bot_list
                else:
                    query_bot_obj_list = [
                        Bot.objects.get(pk=int(selected_bot_pk))]

                for bot_obj in query_bot_obj_list:
                    interaction_list = list(interaction_object_list.filter(bot=bot_obj).values(
                        "joined_date").order_by("joined_date").annotate(frequency=Count("joined_date")))
                    for obj in interaction_list:
                        interaction_objects.append(
                            {"date": obj["joined_date"].date(), "bot_name": bot_obj.name, "frequency": obj["frequency"]})

                freq_array = [(key, len(list(group)))
                              for key, group in groupby(interaction_objects)]
                interaction_objects = []
                for freq_obj in freq_array:
                    freq_obj[0]["frequency"] = freq_obj[1]
                    interaction_objects.append(freq_obj[0])

                if user_obj.static_analytics:
                    interaction_objects = STATIC_LIVECHAT_DAILY_INTERACTION_REPORT_DATA

                interaction_objects = sorted(
                    interaction_objects, key=lambda val: val['date'])[::-1]

                page = request.GET.get('page')
                total_interaction_objects, interaction_objects, start_point, end_point = paginate(
                    interaction_objects, DAILY_INTERACTION_REPORT_ITEM_COUNT, page)

                user_obj = LiveChatUser.objects.get(user=User.objects.get(
                    username=str(request.user.username)), is_deleted=False)
            else:
                return HttpResponse(ACCESS_DENIED)

            template_to_render = 'LiveChatApp/livechat_daily_interaction_report.html'
            if user_obj.static_analytics:
                template_to_render = 'LiveChatApp/static_daily_interaction_report.html'

            return render(request, template_to_render, {
                "user_obj": user_obj,
                "total_interaction_objects": total_interaction_objects,
                "interaction_objects": interaction_objects,
                "start_date": datetime_start,
                "end_date": datetime_end,
                "start_point": start_point,
                "end_point": end_point,
                "bot_list": bot_list,
                "selected_bot_pk": int(selected_bot_pk),
                "admin_config": admin_config,
                "is_report_generation_via_kafka_enabled": is_kafka_enabled(),
            })
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("DailyInteractionCount: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


class ExportDataAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)
            username = request.user.username
            user_obj = LiveChatUser.objects.filter(user__username=username, is_deleted=False).first()
            if user_obj:
                user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
                username = user_obj.user.username
            export_path = None
            export_path_exist = None
            selected_report_type = requested_data["selected_report_type"]
            if user_obj.status != "3":
                
                if selected_report_type == "1":
                    
                    export_path, export_path_exist = get_chat_history_report(requested_data, user_obj, username, LiveChatCustomer, LiveChatSessionManagement, LiveChatAgentNotReady, LiveChatDataExportRequest, LiveChatFollowupCustomer)

                elif selected_report_type == "2":

                    export_path, export_path_exist = get_conversations_report(requested_data, user_obj, username, LiveChatCustomer, LiveChatMISDashboard, LiveChatFollowupCustomer)

            response["status"] = 200
            response["export_path"] = export_path
            response["export_path_exist"] = export_path_exist
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ExportDataAPI! %s %s", str(e), str(
                exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ExportData = ExportDataAPI.as_view()


class MissedChatsExportDataAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)
            
            user_obj = LiveChatUser.objects.filter(user=request.user, is_deleted=False).first()
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            export_path = None
            export_path_exist = None
            today = datetime.now()
            if user_obj.status != "3":
                if not os.path.exists(settings.MEDIA_ROOT + LIVECHAT_MISSED_CHATS_REPORT_PATH + str(user_obj.user.username)):
                    os.makedirs(settings.MEDIA_ROOT + LIVECHAT_MISSED_CHATS_REPORT_PATH + str(user_obj.user.username))

                if requested_data["selected_filter_value"] == "1":
                    try:
                        yesterday = today - timedelta(1)
                        zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_MISSED_CHATS_REPORT_PATH +
                                          str(user_obj.user.username) + "/MissedChatsReportLastOneDay.zip", "w")
                        file_path = LIVECHAT_MISSED_CHATS_REPORT_PATH + \
                            str(user_obj.user.username) + MISSED_CHATS_REPORT_PATH + \
                            str(yesterday.date()) + '.xls'
                        if path.exists(settings.MEDIA_ROOT + file_path):
                            zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        zip_obj.close()
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Livechat Missed Chats Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                            'AppName': 'LiveChat'})

                    export_path = FILES_MISSED_CHATS_REPORT + str(user_obj.user.username) + \
                        "/MissedChatsReportLastOneDay.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "2":
                    zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_MISSED_CHATS_REPORT_PATH +
                                      str(user_obj.user.username) + "/MissedChatsReportLastSevenDays.zip", 'w')
                    for index in range(1, 8):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_MISSED_CHATS_REPORT_PATH + \
                                str(user_obj.user.username) + MISSED_CHATS_REPORT_PATH + \
                                str(date.date()) + '.xls'
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Livechat Missed Chats Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

                    zip_obj.close()
                    export_path = FILES_MISSED_CHATS_REPORT + str(user_obj.user.username) + \
                        "/MissedChatsReportLastSevenDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "3":
                    zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_MISSED_CHATS_REPORT_PATH +
                                      str(user_obj.user.username) + "/MissedChatsReportLastThirtyDays.zip", 'w')
                    for index in range(1, 31):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_MISSED_CHATS_REPORT_PATH + \
                                str(user_obj.user.username) + MISSED_CHATS_REPORT_PATH + \
                                str(date.date()) + '.xls'
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Livechat Missed Chats Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})
    
                    zip_obj.close()
                    export_path = FILES_MISSED_CHATS_REPORT + str(user_obj.user.username) + \
                        "/MissedChatsReportLastThirtyDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "4":
                    
                    if is_kafka_enabled():
                        start_date = requested_data["startdate"]
                        end_date = requested_data["enddate"]

                        date_format = DATE_YYYY_MM_DD

                        start_date = datetime.strptime(start_date, date_format).date()
                        end_date = datetime.strptime(end_date, date_format).date()
                        if (end_date - start_date).days > DAYS_LIMIT_FOR_KAFKA:
                            create_export_request(user_obj, "6", requested_data, LiveChatDataExportRequest)
                            export_path = "request_saved_custom_range"
                        else:
                            export_zip_file_path = LIVECHAT_MISSED_CHATS_REPORT_PATH +\
                                str(user_obj.user.username) + "/MissedChatsReprtCustom.zip"
                            zip_obj = ZipFile(settings.MEDIA_ROOT + export_zip_file_path, 'w')

                            start_date_for_iteration = start_date
                            list_of_date = []
                            while start_date_for_iteration <= end_date:
                                try:
                                    file_path = LIVECHAT_MISSED_CHATS_REPORT_PATH + \
                                        str(user_obj.user.username) + MISSED_CHATS_REPORT_PATH + \
                                        str(start_date_for_iteration) + '.xls'
                                    if path.exists(settings.MEDIA_ROOT + file_path):
                                        zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                                    else:
                                        list_of_date.append(start_date_for_iteration)

                                except Exception as e:
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    logger.error("Livechat Missed Chats Datadump! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                        'AppName': 'LiveChat'})
                                start_date_for_iteration = start_date_for_iteration + timedelta(1)

                            export_zip_file_path = "files/" + export_zip_file_path
                            thread = threading.Thread(target=export_custom_missed_chat_history_report, args=(
                                user_obj, str(user_obj.user.username), list_of_date, requested_data, export_zip_file_path, LiveChatCustomer, zip_obj), daemon=True)
                            thread.start()
                            export_path = "request_saved"
                    else:
                        create_export_request(user_obj, "6", requested_data, LiveChatDataExportRequest)
                        export_path = "request_saved_custom_range"
                        
                elif requested_data["selected_filter_value"] == "5":
                    
                    if is_kafka_enabled():
                        try:
                            zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_MISSED_CHATS_REPORT_PATH +
                                                str(user_obj.user.username) + "/MissedChatsReportToday.zip", "w")
                            file_path = LIVECHAT_MISSED_CHATS_REPORT_PATH + \
                                str(user_obj.user.username) + MISSED_CHATS_REPORT_PATH + \
                                str(today.date()) + '.xls'
                            zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                            zip_obj.close()
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Livechat Offline Chats Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

                        export_path = FILES_MISSED_CHATS_REPORT + str(user_obj.user.username) + \
                            "/MissedChatsReportToday.zip"
                        export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                    else:
                        result = export_today_data(user_obj, "6", json.dumps(
                            requested_data), LiveChatCustomer, LiveChatSessionManagement, LiveChatAgentNotReady, LiveChatFollowupCustomer)
                        if result == True:
                            export_path = "request_saved_today"

            response["status"] = 200
            response["export_path"] = export_path
            response["export_path_exist"] = export_path_exist
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("MissedChatsExportDataAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


MissedChatsExportData = MissedChatsExportDataAPI.as_view()


class OfflineChatsExportDataAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)
            
            user_obj = LiveChatUser.objects.filter(user=request.user, is_deleted=False).first()
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)

            export_path = None
            export_path_exist = None
            today = datetime.now()
            if user_obj.status != "3":

                if not os.path.exists(settings.MEDIA_ROOT + LIVECHAT_OFFLINE_CHATS_REPORT + str(user_obj.user.username)):
                    os.makedirs(settings.MEDIA_ROOT + LIVECHAT_OFFLINE_CHATS_REPORT + str(user_obj.user.username))

                if requested_data["selected_filter_value"] == "1":
                    try:
                        yesterday = today - timedelta(1)
                        zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_OFFLINE_CHATS_REPORT +
                                          str(user_obj.user.username) + "/OfflineChatsReportLastOneDay.zip", "w")
                        file_path = LIVECHAT_OFFLINE_CHATS_REPORT + \
                            str(user_obj.user.username) + OFFLINE_CHATS_REPORT + \
                            str(yesterday.date()) + '.xls'
                        if path.exists(settings.MEDIA_ROOT + file_path):
                            zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        zip_obj.close()
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Livechat Offline Chats Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                            'AppName': 'LiveChat'})
            
                    export_path = "/files/livechat-offline-chats-report/" + \
                        str(user_obj.user.username) + "/OfflineChatsReportLastOneDay.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "2":
                    zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_OFFLINE_CHATS_REPORT +
                                      str(user_obj.user.username) + "/OfflineChatsReportLastSevenDays.zip", 'w')
                    for index in range(1, 8):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_OFFLINE_CHATS_REPORT + \
                                str(user_obj.user.username) + OFFLINE_CHATS_REPORT + \
                                str(date.date()) + '.xls'
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Livechat Offline Chats Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

                    zip_obj.close()
                    export_path = FILES_OFFLINE_CHATS_REPORT + \
                        str(user_obj.user.username) + "/OfflineChatsReportLastSevenDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "3":
                    zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_OFFLINE_CHATS_REPORT +
                                      str(user_obj.user.username) + "/OfflineChatsReportLastThirtyDays.zip", 'w')
                    for index in range(1, 31):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_OFFLINE_CHATS_REPORT + \
                                str(user_obj.user.username) + OFFLINE_CHATS_REPORT + \
                                str(date.date()) + '.xls'
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Livechat Offline Chats Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})
                            
                    zip_obj.close()
                    export_path = FILES_OFFLINE_CHATS_REPORT + \
                        str(user_obj.user.username) + "/OfflineChatsReportLastThirtyDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "4":

                    if is_kafka_enabled():
                        start_date = requested_data["startdate"]
                        end_date = requested_data["enddate"]

                        date_format = DATE_YYYY_MM_DD

                        start_date = datetime.strptime(start_date, date_format).date()
                        end_date = datetime.strptime(end_date, date_format).date()
                        
                        if (end_date - start_date).days > DAYS_LIMIT_FOR_KAFKA:
                            create_export_request(user_obj, "8", requested_data, LiveChatDataExportRequest)
                            export_path = "request_saved_custom_range"
                        else:
                            export_zip_file_path = LIVECHAT_OFFLINE_CHATS_REPORT +\
                                str(user_obj.user.username) + "/OfflineChatsReprtCustom.zip"
                            zip_obj = ZipFile(settings.MEDIA_ROOT + export_zip_file_path, 'w')

                            start_date_for_iteration = start_date
                            list_of_date = []
                            while start_date_for_iteration <= end_date:
                                try:
                                    file_path = LIVECHAT_OFFLINE_CHATS_REPORT + \
                                        str(user_obj.user.username) + OFFLINE_CHATS_REPORT + \
                                        str(start_date_for_iteration) + '.xls'
                                    if path.exists(settings.MEDIA_ROOT + file_path):
                                        zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                                    else:
                                        list_of_date.append(start_date_for_iteration)

                                except Exception as e:
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    logger.error("Livechat Offline Chats Datadump! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                        'AppName': 'LiveChat'})
                                start_date_for_iteration = start_date_for_iteration + timedelta(1)

                            export_zip_file_path = "files/" + export_zip_file_path
                            thread = threading.Thread(target=export_custom_offline_chat_history_report, args=(
                                user_obj, str(user_obj.user.username), list_of_date, requested_data, export_zip_file_path, LiveChatCustomer, zip_obj), daemon=True)
                            thread.start()
                            export_path = "request_saved"
                    else:
                        create_export_request(user_obj, "8", requested_data, LiveChatDataExportRequest)
                        export_path = "request_saved_custom_range"
                        
                elif requested_data["selected_filter_value"] == "5":
                    
                    if is_kafka_enabled():
                        try:
                            zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_OFFLINE_CHATS_REPORT +
                                                str(user_obj.user.username) + "/OfflineChatsReportToday.zip", "w")
                            file_path = LIVECHAT_OFFLINE_CHATS_REPORT + \
                                str(user_obj.user.username) + OFFLINE_CHATS_REPORT + \
                                str(today.date()) + '.xls'
                            zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                            zip_obj.close()
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Livechat Offline Chats Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

                        export_path = FILES_OFFLINE_CHATS_REPORT + \
                            str(user_obj.user.username) + \
                            "/OfflineChatsReportToday.zip"
                        export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                    else:
                        result = export_today_data(user_obj, "8", json.dumps(
                            requested_data), LiveChatCustomer, LiveChatSessionManagement, LiveChatAgentNotReady, LiveChatFollowupCustomer)
                        if result == True:
                            export_path = "request_saved_today"

            response["status"] = 200
            response["export_path"] = export_path
            response["export_path_exist"] = export_path_exist
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("OfflineChatsExportDataAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


OfflineChatsExportData = OfflineChatsExportDataAPI.as_view()


class AbandonedChatsExportDataAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)

            user_obj = LiveChatUser.objects.filter(user=request.user, is_deleted=False).first()
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            
            export_path = None
            export_path_exist = None
            today = datetime.now()
            if user_obj.status != "3":
                
                if not os.path.exists(settings.MEDIA_ROOT + LIVECHAT_ABANDONED_CHATS_REPORT_PATH + str(user_obj.user.username)):
                    os.makedirs(settings.MEDIA_ROOT + LIVECHAT_ABANDONED_CHATS_REPORT_PATH + str(user_obj.user.username))

                if requested_data["selected_filter_value"] == "1":
                    try:
                        yesterday = today - timedelta(1)
                        zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_ABANDONED_CHATS_REPORT_PATH +
                                          str(user_obj.user.username) + "/AbandonedChatsReportLastOneDay.zip", "w")
                        file_path = LIVECHAT_ABANDONED_CHATS_REPORT_PATH + \
                            str(user_obj.user.username) + ABANDONED_CHATS_REPORT_PATH + \
                            str(yesterday.date()) + '.xls'
                        if path.exists(settings.MEDIA_ROOT + file_path):
                            zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        zip_obj.close()
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Livechat Abandoned Chats Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                            'AppName': 'LiveChat'})
                    
                    export_path = FILES_ABANDONED_CHATS_REPORT_PATH + \
                        str(user_obj.user.username) + "/AbandonedChatsReportLastOneDay.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "2":
                    zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_ABANDONED_CHATS_REPORT_PATH +
                                      str(user_obj.user.username) + "/AbandonedChatsReportLastSevenDays.zip", 'w')
                    for index in range(1, 8):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_ABANDONED_CHATS_REPORT_PATH + \
                                str(user_obj.user.username) + ABANDONED_CHATS_REPORT_PATH + \
                                str(date.date()) + '.xls'
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Livechat Abandoned Chats Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

                    zip_obj.close()
                    export_path = FILES_ABANDONED_CHATS_REPORT_PATH + \
                        str(user_obj.user.username) + "/AbandonedChatsReportLastSevenDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "3":
                    zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_ABANDONED_CHATS_REPORT_PATH +
                                      str(user_obj.user.username) + "/AbandonedChatsReportLastThirtyDays.zip", 'w')
                    for index in range(1, 31):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_ABANDONED_CHATS_REPORT_PATH + \
                                str(user_obj.user.username) + ABANDONED_CHATS_REPORT_PATH + \
                                str(date.date()) + '.xls'
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Livechat Abandoned Chats Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})
    
                    zip_obj.close()
                    export_path = FILES_ABANDONED_CHATS_REPORT_PATH + \
                        str(user_obj.user.username) + "/AbandonedChatsReportLastThirtyDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "4":

                    if is_kafka_enabled():
                        start_date = requested_data["startdate"]
                        end_date = requested_data["enddate"]

                        date_format = DATE_YYYY_MM_DD

                        start_date = datetime.strptime(start_date, date_format).date()
                        end_date = datetime.strptime(end_date, date_format).date()
                        
                        if (end_date - start_date).days > DAYS_LIMIT_FOR_KAFKA:
                            create_export_request(user_obj, "9", requested_data, LiveChatDataExportRequest)
                            export_path = "request_saved_custom_range"
                        else:
                            export_zip_file_path = LIVECHAT_ABANDONED_CHATS_REPORT_PATH +\
                                str(user_obj.user.username) + "/AbanodonedChatsReportCustom.zip"
                            zip_obj = ZipFile(settings.MEDIA_ROOT + export_zip_file_path, 'w')

                            start_date_for_iteration = start_date
                            list_of_date = []
                            while start_date_for_iteration <= end_date:
                                try:
                                    file_path = LIVECHAT_ABANDONED_CHATS_REPORT_PATH + \
                                        str(user_obj.user.username) + ABANDONED_CHATS_REPORT_PATH + \
                                        str(start_date_for_iteration) + '.xls'
                                    if path.exists(settings.MEDIA_ROOT + file_path):
                                        zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                                    else:
                                        list_of_date.append(start_date_for_iteration)
                                        
                                except Exception as e:
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    logger.error("Livechat Abandoned Chats Datadump! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                        'AppName': 'LiveChat'})
                                start_date_for_iteration = start_date_for_iteration + timedelta(1)
                            
                            export_zip_file_path = "files/" + export_zip_file_path
                            thread = threading.Thread(target=export_custom_abandoned_chat_history_report, args=(
                                user_obj, str(user_obj.user.username), list_of_date, requested_data, export_zip_file_path, LiveChatCustomer, zip_obj), daemon=True)
                            thread.start()
                                
                            export_path = "request_saved"
                    else:
                        create_export_request(user_obj, "9", requested_data, LiveChatDataExportRequest)
                        export_path = "request_saved_custom_range"

                elif requested_data["selected_filter_value"] == "5":
                    
                    if is_kafka_enabled():
                        
                        try:
                            zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_ABANDONED_CHATS_REPORT_PATH +
                                                str(user_obj.user.username) + "/AbandonedChatsReportToday.zip", "w")
                            file_path = LIVECHAT_ABANDONED_CHATS_REPORT_PATH + \
                                str(user_obj.user.username) + ABANDONED_CHATS_REPORT_PATH + \
                                str(today.date()) + '.xls'
                            zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                            zip_obj.close()
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Livechat Abandoned Chats Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})
                        
                        export_path = FILES_ABANDONED_CHATS_REPORT_PATH + \
                            str(user_obj.user.username) + "/AbandonedChatsReportToday.zip"
                        export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                    else:
                        result = export_today_data(user_obj, "9", json.dumps(requested_data), LiveChatCustomer, LiveChatSessionManagement, LiveChatAgentNotReady, LiveChatFollowupCustomer)
                        if result == True:
                            export_path = "request_saved_today"
                        
            response["status"] = 200
            response["export_path"] = export_path
            response["export_path_exist"] = export_path_exist
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("AbandonedChatsExportDataAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


AbandonedChatsExportData = AbandonedChatsExportDataAPI.as_view()


class LoginLogoutReportExportDataAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)

            user_obj = LiveChatUser.objects.filter(user=request.user, is_deleted=False).first()
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            export_path = None
            export_path_exist = None
            today = datetime.now()
            if user_obj.status != "3":
                
                if not os.path.exists(settings.MEDIA_ROOT + LIVECHAT_LOGIN__LOGOUT_REPORT_PATH + str(user_obj.user.username)):
                    os.makedirs(settings.MEDIA_ROOT + LIVECHAT_LOGIN__LOGOUT_REPORT_PATH + str(user_obj.user.username))

                if requested_data["selected_filter_value"] == "1":
                    try:
                        yesterday = today - timedelta(1)
                        zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_LOGIN__LOGOUT_REPORT_PATH +
                                          str(user_obj.user.username) + "/LoginLogoutReportLastOneDay.zip", "w")
                        file_path = LIVECHAT_LOGIN__LOGOUT_REPORT_PATH + \
                            str(user_obj.user.username) + LOGIN_LOGOUT_REPORT_PATH + \
                            str(yesterday.date()) + '.xls'
                        if path.exists(settings.MEDIA_ROOT + file_path):
                            zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        zip_obj.close()
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Login Logout Interaction Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                            'AppName': 'LiveChat'})
                    
                    export_path = FILES_LOGIN_LOGOUT_REPORT_PATH + \
                        str(user_obj.user.username) + "/LoginLogoutReportLastOneDay.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "2":
                    zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_LOGIN__LOGOUT_REPORT_PATH +
                                      str(user_obj.user.username) + "/LoginLogoutReportLastSevenDays.zip", 'w')
                    for index in range(1, 8):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_LOGIN__LOGOUT_REPORT_PATH + \
                                str(user_obj.user.username) + LOGIN_LOGOUT_REPORT_PATH + \
                                str(date.date()) + '.xls'
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Login Logout Interaction Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

                    zip_obj.close()
                    export_path = FILES_LOGIN_LOGOUT_REPORT_PATH + \
                        str(user_obj.user.username) + "/LoginLogoutReportLastSevenDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "3":
                    # Zip file containing last 30 days
                    zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_LOGIN__LOGOUT_REPORT_PATH +
                                      str(user_obj.user.username) + "/LoginLogoutReportLastThirtyDays.zip", 'w')
                    for index in range(1, 31):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_LOGIN__LOGOUT_REPORT_PATH + \
                                str(user_obj.user.username) + LOGIN_LOGOUT_REPORT_PATH + \
                                str(date.date()) + '.xls'
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Login Logout Interaction Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

                    zip_obj.close()
                    export_path = FILES_LOGIN_LOGOUT_REPORT_PATH + \
                        str(user_obj.user.username) + "/LoginLogoutReportLastThirtyDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "4":
                    
                    if is_kafka_enabled():
                        start_date = requested_data["startdate"]
                        end_date = requested_data["enddate"]

                        date_format = DATE_YYYY_MM_DD

                        start_date = datetime.strptime(start_date, date_format).date()
                        end_date = datetime.strptime(end_date, date_format).date()
                        
                        if (end_date - start_date).days > DAYS_LIMIT_FOR_KAFKA:
                            create_export_request(user_obj, "5", requested_data, LiveChatDataExportRequest)
                            export_path = "request_saved_custom_range"
                        else:
                            export_zip_file_path = "files/" + LIVECHAT_LOGIN__LOGOUT_REPORT_PATH +\
                                str(user_obj.user.username) + "/LoginLogoutReportCustom.zip"
                            zip_obj = ZipFile(export_zip_file_path, 'w')

                            temp_date = start_date
                            list_of_date = []
                            while temp_date <= end_date:
                                try:
                                    file_path = LIVECHAT_LOGIN__LOGOUT_REPORT_PATH + \
                                        str(user_obj.user.username) + LOGIN_LOGOUT_REPORT_PATH + \
                                        str(temp_date) + '.xls'
                                    if path.exists(settings.MEDIA_ROOT + file_path):
                                        zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                                    else:
                                        list_of_date.append(temp_date)
                                        
                                except Exception as e:
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    logger.error("Login Logout Interaction Datadump! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                        'AppName': 'LiveChat'})
                                temp_date = temp_date + timedelta(1)
                            
                            thread = threading.Thread(target=export_custom_login_logout_report, args=(
                                user_obj, str(user_obj.user.username), list_of_date, requested_data, export_zip_file_path, LiveChatSessionManagement, zip_obj), daemon=True)
                            thread.start()
                                
                            export_path = "request_saved"
                    else:
                        create_export_request(user_obj, "5", requested_data, LiveChatDataExportRequest)
                        export_path = "request_saved_custom_range"
                        
                elif requested_data["selected_filter_value"] == "5":
                    
                    if is_kafka_enabled():
                        zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_LOGIN__LOGOUT_REPORT_PATH +
                                            str(user_obj.user.username) + "/LoginLogoutReportToday.zip", 'w')
                        try:
                            file_path = LIVECHAT_LOGIN__LOGOUT_REPORT_PATH + \
                                str(user_obj.user.username) + LOGIN_LOGOUT_REPORT_PATH + \
                                str(today.date()) + '.xls'
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Login Logout Interaction Datadump! %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

                        zip_obj.close()
                        export_path = FILES_LOGIN_LOGOUT_REPORT_PATH + \
                            str(user_obj.user.username) + "/LoginLogoutReportToday.zip"
                        # export_path_exist = path.exists(export_path[1:])
                        export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                    else:
                        result = export_today_data(user_obj, "5", json.dumps(
                            requested_data), LiveChatCustomer, LiveChatSessionManagement, LiveChatAgentNotReady, LiveChatFollowupCustomer)
                        if result == True:
                            export_path = "request_saved_today"
                    
            response["status"] = 200
            response["export_path"] = export_path
            response["export_path_exist"] = export_path_exist
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("LoginLogoutReportExportDataAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


LoginLogoutReportExportData = LoginLogoutReportExportDataAPI.as_view()


class AgentNotReadyReportExportDataAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)

            user_obj = LiveChatUser.objects.filter(user=request.user, is_deleted=False).first()
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            export_path = None
            export_path_exist = None
            today = datetime.now()
            if user_obj.status != "3":
                
                if not os.path.exists(settings.MEDIA_ROOT + LIVECHAT_AGENT_NOT_READY_REPORT_PATH + str(user_obj.user.username)):
                    os.makedirs(settings.MEDIA_ROOT + LIVECHAT_AGENT_NOT_READY_REPORT_PATH + str(user_obj.user.username))

                if requested_data["selected_filter_value"] == "1":
                    try:
                        yesterday = today - timedelta(1)
                        zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_AGENT_NOT_READY_REPORT_PATH +
                                          str(user_obj.user.username) + "/AgentNotReadyReportLastOneDay.zip", "w")
                        file_path = LIVECHAT_AGENT_NOT_READY_REPORT_PATH + \
                            str(user_obj.user.username) + AGENT_NOT_READY_REPORT_PATH + \
                            str(yesterday.date()) + '.xls'
                        if path.exists(settings.MEDIA_ROOT + file_path):
                            zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        zip_obj.close()
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Agent Not Ready Report Datadump Zip! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                     'AppName': 'LiveChat'})
                    export_path = FILES_AGENT_NOT_READY_REPORT_PATH + \
                        str(user_obj.user.username) + "/AgentNotReadyReportLastOneDay.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "2":
                    zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_AGENT_NOT_READY_REPORT_PATH +
                                      str(user_obj.user.username) + "/AgentNotReadyReportLastSevenDays.zip", 'w')
                    for index in range(1, 8):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_AGENT_NOT_READY_REPORT_PATH + \
                                str(user_obj.user.username) + AGENT_NOT_READY_REPORT_PATH + \
                                str(date.date()) + '.xls'
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Agent Not Ready Report Datadump Zip! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

                    zip_obj.close()

                    export_path = FILES_AGENT_NOT_READY_REPORT_PATH + \
                        str(user_obj.user.username) + "/AgentNotReadyReportLastSevenDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "3":
                    zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_AGENT_NOT_READY_REPORT_PATH +
                                      str(user_obj.user.username) + "/AgentNotReadyReportLastThirtyDays.zip", 'w')
                    for index in range(1, 31):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_AGENT_NOT_READY_REPORT_PATH + \
                                str(user_obj.user.username) + AGENT_NOT_READY_REPORT_PATH + \
                                str(date.date()) + '.xls'
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Agent Not Ready Report Datadump Zip! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

                    zip_obj.close()
                    export_path = FILES_AGENT_NOT_READY_REPORT_PATH + \
                        str(user_obj.user.username) + "/AgentNotReadyReportLastThirtyDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "4":
                    
                    if is_kafka_enabled():

                        start_date = requested_data["startdate"]
                        end_date = requested_data["enddate"]

                        date_format = DATE_YYYY_MM_DD

                        start_date = datetime.strptime(start_date, date_format).date()
                        end_date = datetime.strptime(end_date, date_format).date()
                        
                        if (end_date - start_date).days > DAYS_LIMIT_FOR_KAFKA:
                            create_export_request(user_obj, "0", requested_data, LiveChatDataExportRequest)
                            export_path = "request_saved_custom_range"
                        else:    
                        
                            export_zip_file_path = "files/" + LIVECHAT_AGENT_NOT_READY_REPORT_PATH +\
                                str(user_obj.user.username) + "/AgentNotReadyReportCustom.zip"
                            zip_obj = ZipFile(export_zip_file_path, 'w')
                            temp_date = start_date
                            list_of_date = []
                            while temp_date <= end_date:
                                try:
                                    file_path = LIVECHAT_AGENT_NOT_READY_REPORT_PATH + \
                                        str(user_obj.user.username) + AGENT_NOT_READY_REPORT_PATH + \
                                        str(temp_date) + '.xls'
                                    if path.exists(settings.MEDIA_ROOT + file_path):
                                        zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                                    else:
                                        list_of_date.append(temp_date)
                                        
                                except Exception as e:
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    logger.error("Agent Not Ready Report Datadump Zip! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                        'AppName': 'LiveChat'})
                                temp_date = temp_date + timedelta(1)
                            
                            thread = threading.Thread(target=export_custom_agent_not_ready_report, args=(
                                user_obj, str(user_obj.user.username), list_of_date, requested_data, export_zip_file_path, LiveChatAgentNotReady, zip_obj), daemon=True)
                            thread.start()
                                
                            export_path = "request_saved"
                    else:
                        create_export_request(user_obj, "0", requested_data, LiveChatDataExportRequest)
                        export_path = "request_saved_custom_range"

                elif requested_data["selected_filter_value"] == "5":
                    
                    if is_kafka_enabled():
                        zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_AGENT_NOT_READY_REPORT_PATH +
                                            str(user_obj.user.username) + "/AgentNotReadyReportToday.zip", 'w')
                        try:
                            file_path = LIVECHAT_AGENT_NOT_READY_REPORT_PATH + \
                                str(user_obj.user.username) + AGENT_NOT_READY_REPORT_PATH + \
                                str(today.date()) + '.xls'
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Agent Not Ready Report Datadump Zip! %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

                        zip_obj.close()
                        export_path = FILES_AGENT_NOT_READY_REPORT_PATH + \
                            str(user_obj.user.username) + "/AgentNotReadyReportToday.zip"
                        export_path_exist = path.exists(export_path[1:])
                    else:
                        result = export_today_data(user_obj, "0", json.dumps(
                            requested_data), LiveChatCustomer, LiveChatSessionManagement, LiveChatAgentNotReady, LiveChatFollowupCustomer)
                        if result == True:
                            export_path = "request_saved_today"

            response["status"] = 200
            response["export_path"] = export_path
            response["export_path_exist"] = export_path_exist
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("LoginLogoutReportExportDataAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


AgentNotReadyReportExportData = AgentNotReadyReportExportDataAPI.as_view()


class AgentPerformanceReportExportDataAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)

            user_obj = LiveChatUser.objects.filter(user=request.user, is_deleted=False).first()
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            export_path = None
            export_path_exist = None
            today = datetime.now()
            if user_obj.status != "3":

                if not os.path.exists(settings.MEDIA_ROOT + 'livechat-agent-performance-report/' + str(user_obj.user.username)):
                    os.makedirs(settings.MEDIA_ROOT + 'livechat-agent-performance-report/' + str(user_obj.user.username))

                if requested_data["selected_filter_value"] == "1":
                    # Zip file containing last x days
                    try:
                        yesterday = today - timedelta(1)
                        zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_AGENT_PERFORMANCE_REPORT_PATH +
                                          str(user_obj.user.username) + "/AgentPerformanceReportLastOneDay.zip", "w")
                        file_path = LIVECHAT_AGENT_PERFORMANCE_REPORT_PATH + \
                            str(user_obj.user.username) + AGENT_PERFORMANCE_REPORT + \
                            str(yesterday.date()) + '.xls'
                        if path.exists(settings.MEDIA_ROOT + file_path):
                            zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        zip_obj.close()
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Agent Performance Report Datadump Zip! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                     'AppName': 'LiveChat'})

                    export_path = FILES_AGENT_PERFORMANCE_REPORT + \
                        str(user_obj.user.username) + "/AgentPerformanceReportLastOneDay.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "2":
                    zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_AGENT_PERFORMANCE_REPORT_PATH +
                                      str(user_obj.user.username) + "/AgentPerformanceReportLastSevenDays.zip", 'w')
                    for index in range(1, 8):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_AGENT_PERFORMANCE_REPORT_PATH + \
                                str(user_obj.user.username) + AGENT_PERFORMANCE_REPORT + \
                                str(date.date()) + '.xls'
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Agent Performance Report Datadump Zip! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

                    zip_obj.close()
                    export_path = FILES_AGENT_PERFORMANCE_REPORT + \
                        str(user_obj.user.username) + "/AgentPerformanceReportLastSevenDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "3":
                    # Zip file containing last 30 days
                    zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_AGENT_PERFORMANCE_REPORT_PATH +
                                      str(user_obj.user.username) + "/AgentPerformanceReportLastThirtyDays.zip", 'w')
                    for index in range(1, 31):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_AGENT_PERFORMANCE_REPORT_PATH + \
                                str(user_obj.user.username) + AGENT_PERFORMANCE_REPORT + \
                                str(date.date()) + '.xls'
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Agent Performance Report Datadump Zip! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

                    zip_obj.close()
                    export_path = FILES_AGENT_PERFORMANCE_REPORT + \
                        str(user_obj.user.username) + "/AgentPerformanceReportLastThirtyDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "4":
                    
                    if is_kafka_enabled():

                        start_date = requested_data["startdate"]
                        end_date = requested_data["enddate"]

                        date_format = DATE_YYYY_MM_DD

                        start_date = datetime.strptime(start_date, date_format).date()
                        end_date = datetime.strptime(end_date, date_format).date()
                        
                        if (end_date - start_date).days > DAYS_LIMIT_FOR_KAFKA:
                            create_export_request(user_obj, "1", requested_data, LiveChatDataExportRequest)
                            export_path = "request_saved_custom_range"
                        else:    
                            export_zip_file_path = LIVECHAT_AGENT_PERFORMANCE_REPORT_PATH +\
                                str(user_obj.user.username) + "/AgentPerformanceReportCustom.zip"
                            zip_obj = ZipFile(settings.MEDIA_ROOT + export_zip_file_path, 'w')

                            start_date_for_iteration = start_date
                            list_of_date = []
                            while start_date_for_iteration <= end_date:
                                try:
                                    file_path = LIVECHAT_AGENT_PERFORMANCE_REPORT_PATH + \
                                        str(user_obj.user.username) + AGENT_PERFORMANCE_REPORT + \
                                        str(start_date_for_iteration) + '.xls'
                                    if path.exists(settings.MEDIA_ROOT + file_path):
                                        zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                                    else:
                                        list_of_date.append(start_date_for_iteration)

                                except Exception as e:
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    logger.error("AgentPerformanceReportExportDataAPI! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
                                start_date_for_iteration = start_date_for_iteration + timedelta(1)

                            thread = threading.Thread(target=export_custom_performance_report, args=(
                                user_obj, str(user_obj.user.username), list_of_date, requested_data, export_zip_file_path, LiveChatSessionManagement, zip_obj), daemon=True)
                            thread.start()
                            export_path = "request_saved"
                    else:
                        create_export_request(user_obj, "1", requested_data, LiveChatDataExportRequest)
                        export_path = "request_saved_custom_range"
                    
                elif requested_data["selected_filter_value"] == "5":
                    
                    if is_kafka_enabled():
                        zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_AGENT_PERFORMANCE_REPORT_PATH +
                                            str(user_obj.user.username) + "/AgentPerformanceReportToday.zip", 'w')
                        try:
                            file_path = LIVECHAT_AGENT_PERFORMANCE_REPORT_PATH + \
                                str(user_obj.user.username) + AGENT_PERFORMANCE_REPORT + \
                                str(today.date()) + '.xls'
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("AgentPerformanceReportExportDataAPI! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

                        zip_obj.close()
                        export_path = FILES_AGENT_PERFORMANCE_REPORT + \
                            str(user_obj.user.username) + "/AgentPerformanceReportToday.zip"
                        export_path_exist = path.exists(export_path[1:])
                    else:
                        result = export_today_data(user_obj, "1", json.dumps(
                            requested_data), LiveChatCustomer, LiveChatSessionManagement, LiveChatAgentNotReady, LiveChatFollowupCustomer)
                        if result == True:
                            export_path = "request_saved_today"

            response["status"] = 200
            response["export_path"] = export_path
            response["export_path_exist"] = export_path_exist
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("AgentPerformanceReportExportDataAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


AgentPerformanceReportExportData = AgentPerformanceReportExportDataAPI.as_view()


class HourlyInteractionCountExportDataAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)

            user_obj = LiveChatUser.objects.filter(user=request.user, is_deleted=False).first()
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            
            export_path = None
            export_path_exist = None
            today = datetime.now()
            if user_obj.status != "3":

                if not os.path.exists(settings.MEDIA_ROOT + LIVECHAT_HOURLY_INTERACTION_REPORT + str(user_obj.user.username)):
                    os.makedirs(settings.MEDIA_ROOT + LIVECHAT_HOURLY_INTERACTION_REPORT + str(user_obj.user.username))

                if requested_data["selected_filter_value"] == "1":
                    try:
                        yesterday = today - timedelta(1)
                        zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_HOURLY_INTERACTION_REPORT +
                                          str(user_obj.user.username) + "/HourlyInteractionReportLastOneDay.zip", "w")
                        file_path = LIVECHAT_HOURLY_INTERACTION_REPORT + \
                            str(user_obj.user.username) + HOURLY_INTERACTION_REPORT + \
                            str(yesterday.date()) + '.xls'
                        zip_obj.write(settings.MEDIA_ROOT +
                                      file_path, basename(file_path))
                        zip_obj.close()
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Hourly Interaction Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                            'AppName': 'LiveChat'})
                
                    export_path = FILES_HOURLY_INTERACTION_REPORT + \
                        str(user_obj.user.username) + "/HourlyInteractionReportLastOneDay.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))

                elif requested_data["selected_filter_value"] == "2":
                    zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_HOURLY_INTERACTION_REPORT +
                                      str(user_obj.user.username) + "/HourlyInteractionReportLastSevenDays.zip", 'w')
                    for index in range(1, 8):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_HOURLY_INTERACTION_REPORT + \
                                str(user_obj.user.username) + HOURLY_INTERACTION_REPORT + \
                                str(date.date()) + '.xls'
                            zip_obj.write(settings.MEDIA_ROOT +
                                          file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Hourly Interaction Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})
                
                    zip_obj.close()
                    export_path = FILES_HOURLY_INTERACTION_REPORT + \
                        str(user_obj.user.username) + "/HourlyInteractionReportLastSevenDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))

                elif requested_data["selected_filter_value"] == "3":
                    zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_HOURLY_INTERACTION_REPORT +
                                      str(user_obj.user.username) + "/HourlyInteractionReportLastThirtyDays.zip", 'w')
                    for index in range(1, 31):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_HOURLY_INTERACTION_REPORT + \
                                str(user_obj.user.username) + HOURLY_INTERACTION_REPORT + \
                                str(date.date()) + '.xls'
                            zip_obj.write(settings.MEDIA_ROOT +
                                          file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Hourly Interaction Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

                    zip_obj.close()
                    export_path = FILES_HOURLY_INTERACTION_REPORT + \
                        str(user_obj.user.username) + "/HourlyInteractionReportLastThirtyDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))

                elif requested_data["selected_filter_value"] == "4":
                    
                    if is_kafka_enabled():
                        
                        start_date = requested_data["startdate"]
                        end_date = requested_data["enddate"]

                        date_format = DATE_YYYY_MM_DD

                        start_date = datetime.strptime(start_date, date_format)
                        end_date = datetime.strptime(end_date, date_format)
                        
                        if (end_date - start_date).days > DAYS_LIMIT_FOR_KAFKA:
                            create_export_request(user_obj, "4", requested_data, LiveChatDataExportRequest)
                            export_path = "request_saved_custom_range"   
                        else:
                            export_zip_file_path = LIVECHAT_HOURLY_INTERACTION_REPORT +\
                                str(user_obj.user.username) + "/HourlyInteractionReportCustom.zip"
                            zip_obj = ZipFile(settings.MEDIA_ROOT + export_zip_file_path, 'w')

                            start_date_for_iteration = start_date
                            list_of_date = []
                            while start_date_for_iteration <= end_date:
                                try:
                                    file_path = LIVECHAT_HOURLY_INTERACTION_REPORT + \
                                        str(user_obj.user.username) + HOURLY_INTERACTION_REPORT + \
                                        str(start_date_for_iteration) + '.xls' 
                                    if path.exists(settings.MEDIA_ROOT + file_path):
                                        zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                                    else:
                                        list_of_date.append(start_date_for_iteration)

                                except Exception as e:
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    logger.error("Livechat Hourly Interactions Custom Report Datadump! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                        'AppName': 'LiveChat'})
                                start_date_for_iteration = start_date_for_iteration + timedelta(1)

                            export_zip_file_path = "files/" + export_zip_file_path
                            thread = threading.Thread(target=export_custom_hourly_interaction_report, args=(
                                user_obj, str(user_obj.user.username), list_of_date, requested_data, export_zip_file_path, LiveChatCustomer, zip_obj), daemon=True)
                            thread.start()
                            
                            export_path = "request_saved_custom"
                    else:
                        create_export_request(user_obj, "4", requested_data, LiveChatDataExportRequest)
                        export_path = "request_saved_custom_range"
                        
                elif requested_data["selected_filter_value"] == "5":
                    result = export_today_data(user_obj, "4", json.dumps(
                        requested_data), LiveChatCustomer, LiveChatSessionManagement, LiveChatAgentNotReady, LiveChatFollowupCustomer)
                    if result == True:
                        export_path = "request_saved_today"

            response["status"] = 200
            response["export_path"] = export_path
            response["export_path_exist"] = export_path_exist
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("HourlyInteractionCountExportDataAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


HourlyInteractionCountExportData = HourlyInteractionCountExportDataAPI.as_view()


class LiveChatAnalyticsExportDataAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)

            user_obj = LiveChatUser.objects.filter(user=request.user, is_deleted=False).first()
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            export_path = None
            export_path_exist = None
            today = datetime.now()
            if user_obj.status != "3":

                if not os.path.exists('secured_files/LiveChatApp/livechat-analytics-data/' + str(user_obj.user.username)):
                    os.makedirs('secured_files/LiveChatApp/livechat-analytics-data/' + str(user_obj.user.username))

                if requested_data["selected_filter_value"] == "1":
                    try:
                        yesterday = today - timedelta(1)
                        zip_obj = ZipFile(settings.SECURE_MEDIA_ROOT + 'LiveChatApp/' + LIVECHAT_ANALYTICS_DATA_PATH +
                                          str(user_obj.user.username) + "/AnalyticsLastOneDay.zip", "w")
                        file_path = LIVECHAT_ANALYTICS_DATA_PATH + \
                            str(user_obj.user.username) + ANALYTICS_PATH + \
                            str(yesterday.date()) + '.xls'
                        zip_obj.write(settings.MEDIA_ROOT +
                                      file_path, basename(file_path))
                        zip_obj.close()
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Agent Analytics Report Datadump Zip! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                            'AppName': 'LiveChat'})
                        
                    export_path = FILES_ANALYTICS_PATH + \
                        str(user_obj.user.username) + "/AnalyticsLastOneDay.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "2":
                    zip_obj = ZipFile(settings.SECURE_MEDIA_ROOT + 'LiveChatApp/' + LIVECHAT_ANALYTICS_DATA_PATH +
                                      str(user_obj.user.username) + "/AnalyticsLastSevenDays.zip", 'w')
                    for index in range(1, 8):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_ANALYTICS_DATA_PATH + \
                                str(user_obj.user.username) + ANALYTICS_PATH + \
                                str(date.date()) + '.xls'
                            zip_obj.write(settings.MEDIA_ROOT +
                                          file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Agent Analytics Report Datadump Zip! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})
                        
                    zip_obj.close()
                    export_path = FILES_ANALYTICS_PATH + \
                        str(user_obj.user.username) + "/AnalyticsLastSevenDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "3":
                    zip_obj = ZipFile(settings.SECURE_MEDIA_ROOT + 'LiveChatApp/' + LIVECHAT_ANALYTICS_DATA_PATH +
                                      str(user_obj.user.username) + "/AnalyticsLastThirtyDays.zip", 'w')
                    for index in range(1, 31):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_ANALYTICS_DATA_PATH + \
                                str(user_obj.user.username) + ANALYTICS_PATH + \
                                str(date.date()) + '.xls'
                            zip_obj.write(settings.MEDIA_ROOT +
                                          file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Agent Analytics Report Datadump Zip! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

                    zip_obj.close()
                    export_path = FILES_ANALYTICS_PATH + \
                        str(user_obj.user.username) + "/AnalyticsLastThirtyDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "4":
                    LiveChatDataExportRequest.objects.create(
                        user=user_obj, report_type="7", filter_param=json.dumps(requested_data))
                    export_path = "request_saved"

                if requested_data["selected_filter_value"] != "4":
                    file_access_management_obj = LiveChatFileAccessManagement.objects.create(
                        file_path=export_path, is_public=False)
                    file_access_management_obj.file_access_type = "personal_access"
                    file_access_management_obj.users.add(user_obj)
                    file_access_management_obj.save()

                    export_path = '/livechat/download-file/' + \
                        str(file_access_management_obj.key) + '/LiveChatAnalytics.zip'

            response["status"] = 200
            response["export_path"] = export_path
            response["export_path_exist"] = export_path_exist
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("AnalyticsExportDataAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


LiveChatAnalyticsExportData = LiveChatAnalyticsExportDataAPI.as_view()


class DailyInteractionCountExportDataAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)

            user_obj = LiveChatUser.objects.filter(user=request.user, is_deleted=False).first()
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            export_path = None
            export_path_exist = None
            today = datetime.now()
            if user_obj.status != "3":

                if not os.path.exists(settings.MEDIA_ROOT + LIVECHAT_DAILY_INTERACTION_REPORT_PATH + str(user_obj.user.username)):
                    os.makedirs(settings.MEDIA_ROOT + LIVECHAT_DAILY_INTERACTION_REPORT_PATH + str(user_obj.user.username))

                if requested_data["selected_filter_value"] == "1":
                    # Zip file containing last x days
                    try:
                        yesterday = today - timedelta(1)
                        zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_DAILY_INTERACTION_REPORT_PATH +
                                          str(user_obj.user.username) + "/DailyInteractionReportLastOneDay.zip", "w")
                        file_path = LIVECHAT_DAILY_INTERACTION_REPORT_PATH + \
                            str(user_obj.user.username) + DAILY_INTERACTION_REPORT_PATH + \
                            str(yesterday.date()) + '.xls'
                        zip_obj.write(settings.MEDIA_ROOT +
                                      file_path, basename(file_path))
                        zip_obj.close()
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Daily Interaction Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                            'AppName': 'LiveChat'})
                    
                    export_path = FILES_DAILY_INTERACTION_REPORT_PATH + \
                        str(user_obj.user.username) + "/DailyInteractionReportLastOneDay.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))

                elif requested_data["selected_filter_value"] == "2":
                    zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_DAILY_INTERACTION_REPORT_PATH +
                                      str(user_obj.user.username) + "/DailyInteractionReportLastSevenDays.zip", 'w')
                    for index in range(1, 8):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_DAILY_INTERACTION_REPORT_PATH + \
                                str(user_obj.user.username) + DAILY_INTERACTION_REPORT_PATH + \
                                str(date.date()) + '.xls'
                            zip_obj.write(settings.MEDIA_ROOT +
                                          file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Daily Interaction Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

                    zip_obj.close()
                    export_path = FILES_DAILY_INTERACTION_REPORT_PATH + \
                        str(user_obj.user.username) + "/DailyInteractionReportLastSevenDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))

                elif requested_data["selected_filter_value"] == "3":
                    zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_DAILY_INTERACTION_REPORT_PATH +
                                      str(user_obj.user.username) + "/DailyInteractionReportLastThirtyDays.zip", 'w')
                    for index in range(1, 31):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_DAILY_INTERACTION_REPORT_PATH + \
                                str(user_obj.user.username) + DAILY_INTERACTION_REPORT_PATH + \
                                str(date.date()) + '.xls'
                            zip_obj.write(settings.MEDIA_ROOT +
                                          file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Daily Interaction Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

                    zip_obj.close()
                    export_path = FILES_DAILY_INTERACTION_REPORT_PATH + \
                        str(user_obj.user.username) + "/DailyInteractionReportLastThirtyDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))

                elif requested_data["selected_filter_value"] == "4":
                    
                    if is_kafka_enabled():

                        start_date = requested_data["startdate"]
                        end_date = requested_data["enddate"]

                        date_format = DATE_YYYY_MM_DD

                        start_date = datetime.strptime(start_date, date_format).date()
                        end_date = datetime.strptime(end_date, date_format).date()
                        
                        if (end_date - start_date).days > DAYS_LIMIT_FOR_KAFKA:
                            create_export_request(user_obj, "3", requested_data, LiveChatDataExportRequest)
                            export_path = "request_saved_custom_range"
                            
                        else:
                            export_zip_file_path = LIVECHAT_DAILY_INTERACTION_REPORT_PATH +\
                                str(user_obj.user.username) + "/DailyInteractionReportCustom.zip"
                            zip_obj = ZipFile(settings.MEDIA_ROOT + export_zip_file_path, 'w')

                            start_date_for_iteration = start_date
                            list_of_date = []
                            while start_date_for_iteration <= end_date:
                                try:
                                    file_path = LIVECHAT_DAILY_INTERACTION_REPORT_PATH + \
                                        str(user_obj.user.username) + DAILY_INTERACTION_REPORT_PATH + \
                                        str(start_date_for_iteration) + '.xls'
                                    if path.exists(settings.MEDIA_ROOT + file_path):
                                        zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                                    else:
                                        list_of_date.append(start_date_for_iteration)

                                except Exception as e:
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    logger.error("Livechat Daily Interactions Custom Report Datadump! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                        'AppName': 'LiveChat'})
                                start_date_for_iteration = start_date_for_iteration + timedelta(1)

                            export_zip_file_path = "files/" + export_zip_file_path
                            thread = threading.Thread(target=export_custom_daily_interaction_report, args=(
                                user_obj, str(user_obj.user.username), list_of_date, requested_data, export_zip_file_path, LiveChatCustomer, zip_obj), daemon=True)
                            thread.start()
                            export_path = "request_saved_custom"
                    else:
                        create_export_request(user_obj, "3", requested_data, LiveChatDataExportRequest)
                        export_path = "request_saved_custom_range"
                    
                elif requested_data["selected_filter_value"] == "5":
                    result = export_today_data(user_obj, "3", json.dumps(
                        requested_data), LiveChatCustomer, LiveChatSessionManagement, LiveChatAgentNotReady, LiveChatFollowupCustomer)
                    if result == True:
                        export_path = "request_saved_today"

            response["status"] = 200
            response["export_path"] = export_path
            response["export_path_exist"] = export_path_exist
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DailyInteractionCountExportDataAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


DailyInteractionCountExportData = DailyInteractionCountExportDataAPI.as_view()


class LiveChatAnalyticsContinousAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)

            if user_obj.status != "3":
                if user_obj.static_analytics:
                    response = STATIC_LIVECHAT_CONTINUOUS_ANALYTICS_DUMMY_DATA
                else:
                    user_obj_list = get_agents_under_this_user(user_obj)
                    channel_name = requested_data['channel']
                    category_ids = requested_data['category']

                    if user_obj.status == '1' and 'supervisors_list' in requested_data:
                        supervisors_list = requested_data['supervisors_list']

                        if supervisors_list:
                            user_obj_list = get_agents_as_per_supervisors(supervisors_list, user_obj_list, LiveChatUser) 

                    if channel_name is None:
                        channel_name = 'All'
                    if category_ids is None or category_ids == '':
                        category_ids = 'All'
                        bot_objs = user_obj.bots.all().filter(is_deleted=False)
                        category_objs = user_obj.category.all().filter(
                            bot__in=bot_objs, is_deleted=False)
                    else:
                        category_ids = category_ids.split(',')
                        category_objs = get_analytics_category_objs(category_ids, LiveChatCategory)
                    channel_objs = get_analytics_channel_objs(channel_name, Channel)
                    category_wise_agent_list = []
                    for user in user_obj_list:
                        if user.status == "1":
                            continue
                        for category in user.category.all():
                            if category in category_objs:
                                category_wise_agent_list.append(user)
                                break
                    chats_in_queue = get_chats_in_queue(
                        user_obj_list, channel_objs, category_objs, Bot.objects.none(), LiveChatCustomer, LiveChatConfig)
                    average_handle_time = get_livechat_avh_filter(
                        user_obj_list, datetime.now().date(), datetime.now().date(), channel_objs, category_objs, LiveChatCustomer)
                    average_queue_time, avg_queue_time_percentage_change = get_livechat_avg_queue_time(
                        user_obj_list, channel_objs, category_objs, LiveChatCustomer)
                    average_first_time_response_time = get_livechat_avg_first_time_response(
                        user_obj_list, channel_objs, category_objs, LiveChatCustomer)
                    loggen_in_agents, ready_agents, not_ready_agents, stop_interaction_agents, current_capacity = get_agents_availibility_analytics(
                        category_wise_agent_list, LiveChatAdminConfig, LiveChatUser)
                    ongoing_chats = LiveChatCustomer.objects.filter(~Q(agent_id=None)).filter(
                        last_appearance_date__date=datetime.today().date(), is_session_exp=False, agent_id__in=user_obj_list, channel__in=channel_objs, category__in=category_objs).count()
                    followup_leads = LiveChatFollowupCustomer.objects.filter(
                        agent_id__in=user_obj_list, livechat_customer__channel__in=channel_objs, livechat_customer__category__in=category_objs).aggregate(Sum("followup_count"))
                    if not followup_leads['followup_count__sum']:
                        followup_leads['followup_count__sum'] = 0 

                    chat_termination_data = dict(LiveChatCustomer.objects.filter(
                        last_appearance_date__date=datetime.today().date(), is_session_exp=True, agent_id__in=user_obj_list, channel__in=channel_objs, 
                        category__in=category_objs).values_list('chat_ended_by').annotate(total=Count('chat_ended_by')).order_by('total'))
                    customers_reported = LiveChatReportedCustomer.objects.filter(
                        created_date__date=datetime.today().date(), livechat_customer__agent_id__in=user_obj_list, is_reported=True, is_completed=False,
                        livechat_customer__channel__in=channel_objs, livechat_customer__category__in=category_objs).count()
                    response = {
                        "average_handle_time": average_handle_time,
                        "loggen_in_agents": loggen_in_agents,
                        "ready_agents": ready_agents,
                        "not_ready_agents": not_ready_agents,
                        "ongoing_chats": ongoing_chats,
                        "stop_interaction_agents": stop_interaction_agents,
                        "current_capacity": current_capacity,
                        "chats_in_queue": chats_in_queue,
                        "average_queue_time": average_queue_time,
                        "avg_queue_time_percentage_change": avg_queue_time_percentage_change,
                        "followup_leads": followup_leads['followup_count__sum'],
                        "chat_termination_data": chat_termination_data,
                        "customers_reported": customers_reported,
                        "average_first_time_response_time": average_first_time_response_time,
                    }
                response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("LiveChatAnalyticsContinousAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


LiveChatAnalyticsContinous = LiveChatAnalyticsContinousAPI.as_view()


class GetLiveChatChatReportsAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            if user_obj.status != "3":

                if user_obj.static_analytics:
                    response = STATIC_LIVECHAT_CHAT_REPORTS_ANALYTICS_DATA
                else:
                    user_obj_list = get_agents_under_this_user(user_obj)
                    start_date = requested_data['start_date']
                    end_date = requested_data['end_date']
                    is_filter_applied = requested_data['is_filter_present']
                    channel_name = requested_data['channel']
                    category_ids = requested_data['category_pk_list']

                    if user_obj.status == '1' and 'supervisors_list' in requested_data:
                        supervisors_list = requested_data['supervisors_list']

                        if supervisors_list:
                            user_obj_list = get_agents_as_per_supervisors(supervisors_list, user_obj_list, LiveChatUser) 

                    channel_objs = get_analytics_channel_objs(channel_name, Channel)

                    category_objs = get_analytics_category_objs(category_ids, LiveChatCategory)

                    livechat_history_list, total_entered_chat, total_closed_chat, denied_chats, abandon_chats, customer_declined_chats = get_livechat_chat_report_history_list(
                        start_date, end_date, channel_objs, category_objs, user_obj_list, is_filter_applied, Bot, LiveChatConfig, LiveChatCustomer)
                    
                    voice_calls_initiated = get_voice_calls_initiated_filtered(user_obj_list, start_date, end_date, channel_objs, category_objs, LiveChatVoIPData)

                    avg_call_duration = get_average_call_duration_filtered(user_obj_list, start_date, end_date, channel_objs, category_objs, LiveChatVoIPData)

                    avg_video_call_duration = get_average_video_call_duration_filtered(user_obj_list, start_date, end_date, channel_objs, category_objs, LiveChatVoIPData)

                    total_tickets_raised = get_total_tickets_raised_filtered(user_obj_list, start_date, end_date, channel_objs, category_objs, LiveChatTicketAudit)

                    chat_termination_data = get_chat_termination_data_filtered(user_obj_list, start_date, end_date, channel_objs, category_objs, LiveChatCustomer, Channel)

                    source_of_incoming_request_data = get_source_of_incoming_request_data_filtered(user_obj_list, start_date, end_date, channel_objs, category_objs, LiveChatCustomer, Channel)

                    avg_cobrowsing_duration = get_average_cobrowsing_duration_filtered(user_obj_list, start_date, end_date, channel_objs, category_objs, LiveChatCobrowsingData)

                    total_customers_reported = get_total_customers_reported_filtered(user_obj_list, start_date, end_date, channel_objs, category_objs, LiveChatReportedCustomer)

                    followup_leads_via_email = get_followup_leads_via_email_filtered(user_obj_list, start_date, end_date, channel_objs, category_objs, Channel, LiveChatFollowupCustomer)

                    avg_first_time_response = get_livechat_avg_first_time_response(user_obj_list, channel_objs, category_objs, LiveChatCustomer, start_date, end_date, is_daily_data=False)

                    response['livechat_history_list'] = livechat_history_list
                    response['total_entered_chat'] = total_entered_chat
                    response['total_closed_chat'] = total_closed_chat
                    response['denied_chats'] = denied_chats
                    response['abandon_chats'] = abandon_chats
                    response['customer_declined_chats'] = customer_declined_chats
                    response['voice_calls_initiated'] = voice_calls_initiated
                    response['avg_call_duration'] = avg_call_duration
                    response['avg_video_call_duration'] = avg_video_call_duration
                    response['total_tickets_raised'] = total_tickets_raised
                    response['chat_termination_data'] = chat_termination_data
                    response['source_of_incoming_request_data'] = source_of_incoming_request_data
                    response['avg_cobrowsing_duration'] = avg_cobrowsing_duration
                    response['total_customers_reported'] = total_customers_reported
                    response['followup_leads_via_email'] = followup_leads_via_email
                    response['avg_first_time_response'] = avg_first_time_response

                response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetLiveChatChatReportsAnalyticsAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetLiveChatChatReportsAnalytics = GetLiveChatChatReportsAnalyticsAPI.as_view()


class GetAverageNPSAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            if user_obj.status != "3":

                if user_obj.static_analytics:
                    response = STATIC_LIVECHAT_AVG_NPS_ANALYTICS_DATA
                else:
                    user_obj_list = get_agents_under_this_user(user_obj)
                    start_date = requested_data['start_date']
                    end_date = requested_data['end_date']
                    is_filter_applied = requested_data['is_filter_present']
                    channel_name = requested_data['channel']
                    category_ids = requested_data['category_pk_list']

                    if user_obj.status == '1' and 'supervisors_list' in requested_data:
                        supervisors_list = requested_data['supervisors_list']

                        if supervisors_list:
                            user_obj_list = get_agents_as_per_supervisors(supervisors_list, user_obj_list, LiveChatUser) 

                    channel_objs = get_analytics_channel_objs(channel_name, Channel)
                    category_objs = get_analytics_category_objs(category_ids, LiveChatCategory)

                    livechat_avg_nps_list, avg_nps = get_avg_nps_list(
                        start_date, end_date, channel_objs, user_obj_list, is_filter_applied, category_objs, LiveChatCustomer)

                    response['livechat_avg_nps_list'] = livechat_avg_nps_list
                    response['avg_nps'] = avg_nps

                response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetLiveChatChatReportsAnalyticsAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetAverageNPSAnalytics = GetAverageNPSAnalyticsAPI.as_view()


class GetAverageHandleTimeAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            if user_obj.status != "3":
                if user_obj.static_analytics:
                    response = STATIC_LIVECHAT_AVG_HANDLE_TIME_DATA
                else:
                    user_obj_list = get_agents_under_this_user(user_obj)
                    start_date = requested_data['start_date']
                    end_date = requested_data['end_date']
                    is_filter_applied = requested_data['is_filter_present']
                    channel_name = requested_data['channel']
                    category_ids = requested_data['category_pk_list']

                    if user_obj.status == '1' and 'supervisors_list' in requested_data:
                        supervisors_list = requested_data['supervisors_list']

                        if supervisors_list:
                            user_obj_list = get_agents_as_per_supervisors(supervisors_list, user_obj_list, LiveChatUser) 

                    channel_objs = get_analytics_channel_objs(channel_name, Channel)
                    category_objs = get_analytics_category_objs(category_ids, LiveChatCategory)

                    livechat_avg_handle_time_list, avg_handle_time = get_livechat_avg_handle_time_list(
                        start_date, end_date, channel_objs, user_obj_list, is_filter_applied, category_objs, LiveChatCustomer)

                    response['livechat_avg_handle_time_list'] = livechat_avg_handle_time_list
                    response['avg_handle_time'] = avg_handle_time
                response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetLiveChatChatReportsAnalyticsAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetAverageHandleTimeAnalytics = GetAverageHandleTimeAnalyticsAPI.as_view()


class GetAverageQueueTimeAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            if user_obj.status != "3":
                if user_obj.static_analytics:
                    response = STATIC_LIVECHAT_AVG_QUEUE_TIME_DATA
                else:
                    user_obj_list = get_agents_under_this_user(user_obj)
                    start_date = requested_data['start_date']
                    end_date = requested_data['end_date']
                    is_filter_applied = requested_data['is_filter_present']
                    channel_name = requested_data['channel']
                    category_ids = requested_data['category_pk_list']

                    if user_obj.status == '1' and 'supervisors_list' in requested_data:
                        supervisors_list = requested_data['supervisors_list']

                        if supervisors_list:
                            user_obj_list = get_agents_as_per_supervisors(supervisors_list, user_obj_list, LiveChatUser) 

                    channel_objs = get_analytics_channel_objs(channel_name, Channel)
                    category_objs = get_analytics_category_objs(category_ids, LiveChatCategory)

                    livechat_avg_queue_time_list, average_queue_time_live = get_livechat_avg_queue_time_list(
                        start_date, end_date, channel_objs, user_obj_list, is_filter_applied, category_objs, LiveChatCustomer)

                    response['livechat_avg_queue_time_list'] = livechat_avg_queue_time_list
                    response['average_queue_time_live'] = average_queue_time_live
                response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetLiveChatChatReportsAnalyticsAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetAverageQueueTimeAnalytics = GetAverageQueueTimeAnalyticsAPI.as_view()


class GetInteractionsPerChatAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            if user_obj.status != "3":
                if user_obj.static_analytics:
                    response = STATIC_LIVECHAT_AVG_INTERACTION_DATA
                else:
                    user_obj_list = get_agents_under_this_user(user_obj)
                    start_date = requested_data['start_date']
                    end_date = requested_data['end_date']
                    is_filter_applied = requested_data['is_filter_present']
                    channel_name = requested_data['channel']
                    category_ids = requested_data['category_pk_list']

                    if user_obj.status == '1' and 'supervisors_list' in requested_data:
                        supervisors_list = requested_data['supervisors_list']

                        if supervisors_list:
                            user_obj_list = get_agents_as_per_supervisors(supervisors_list, user_obj_list, LiveChatUser) 

                    channel_objs = get_analytics_channel_objs(channel_name, Channel)
                    category_objs = get_analytics_category_objs(category_ids, LiveChatCategory)

                    livechat_interactions_per_chat_list, interactions_per_chat = get_livechat_avg_interaction_per_chat_list(
                        start_date, end_date, channel_objs, user_obj_list, is_filter_applied, category_objs, LiveChatCustomer, LiveChatMISDashboard)
                    response['livechat_interactions_per_chat_list'] = livechat_interactions_per_chat_list
                    response["interactions_per_chat"] = interactions_per_chat
                response['status'] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetLiveChatChatReportsAnalyticsAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetInteractionsPerChatAnalytics = GetInteractionsPerChatAnalyticsAPI.as_view()


class ExportVOIPDataAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)

            user_obj = LiveChatUser.objects.filter(user=request.user, is_deleted=False).first()
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            export_path = None
            export_path_exist = None
            today = datetime.now()
            if user_obj.status != "3":
                
                if not os.path.exists(settings.MEDIA_ROOT + 'livechat-voip-history/' + str(user_obj.user.username)):
                    os.makedirs(settings.MEDIA_ROOT + 'livechat-voip-history/' + str(user_obj.user.username))
                        
                if requested_data["selected_filter_value"] == "1":
                    try:
                        yesterday = today - timedelta(1)
                        zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_VOIP_HISTORY_PATH +
                                          str(user_obj.user.username) + "/VOIPHistoryLastOneDay.zip", "w")
                        file_path = LIVECHAT_VOIP_HISTORY_PATH + \
                            str(user_obj.user.username) + VOIP_HISTORY_PATH + \
                            str(yesterday.date()) + '.xls'
                        if path.exists(settings.MEDIA_ROOT + file_path):
                            zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        zip_obj.close()
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("VOIP History Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                            'AppName': 'LiveChat'})
                    
                    export_path = FILES_VOIP_HISTORY_PATH + \
                        str(user_obj.user.username) + "/VOIPHistoryLastOneDay.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "2":
                    zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_VOIP_HISTORY_PATH +
                                      str(user_obj.user.username) + "/VOIPHistoryLastSevenDays.zip", 'w')
                    for index in range(1, 8):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_VOIP_HISTORY_PATH + \
                                str(user_obj.user.username) + VOIP_HISTORY_PATH + \
                                str(date.date()) + '.xls'
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("VOIP History Datadump! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

                    zip_obj.close()
                    export_path = FILES_VOIP_HISTORY_PATH + \
                        str(user_obj.user.username) + "/VOIPHistoryLastSevenDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "3":
                    zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_VOIP_HISTORY_PATH +
                                      str(user_obj.user.username) + "/VOIPHistoryLastThirtyDays.zip", 'w')
                    for index in range(1, 31):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_VOIP_HISTORY_PATH + \
                                str(user_obj.user.username) + VOIP_HISTORY_PATH + \
                                str(date.date()) + '.xls'
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("VOIP History Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

                    zip_obj.close()
                    export_path = FILES_VOIP_HISTORY_PATH + \
                        str(user_obj.user.username) + "/VOIPHistoryLastThirtyDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "4":
                    
                    if is_kafka_enabled():

                        start_date = requested_data["startdate"]
                        end_date = requested_data["enddate"]

                        date_format = DATE_YYYY_MM_DD

                        start_date = datetime.strptime(start_date, date_format).date()
                        end_date = datetime.strptime(end_date, date_format).date()
                        
                        if (end_date - start_date).days > DAYS_LIMIT_FOR_KAFKA:
                            create_export_request(user_obj, "10", requested_data, LiveChatDataExportRequest)
                            export_path = "request_saved_custom_range"
                        else:
                            export_zip_file_path = LIVECHAT_VOIP_HISTORY_PATH +\
                                str(user_obj.user.username) + "/VOIPHistoryCustom.zip"
                            zip_obj = ZipFile(settings.MEDIA_ROOT + export_zip_file_path, 'w')
                            start_date_for_iteration = start_date
                            list_of_date = []
                            while start_date_for_iteration <= end_date:
                                try:
                                    file_path = LIVECHAT_VOIP_HISTORY_PATH + \
                                        str(user_obj.user.username) + VOIP_HISTORY_PATH + \
                                        str(start_date_for_iteration) + '.xls'
                                    if path.exists(settings.MEDIA_ROOT + file_path):
                                        zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                                    else:
                                        list_of_date.append(start_date_for_iteration)
                                        
                                except Exception as e:
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    logger.error("VOIP History Datadump! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                        'AppName': 'LiveChat'})
                                start_date_for_iteration = start_date_for_iteration + timedelta(1)
                            
                            export_zip_file_path = "files/" + export_zip_file_path
                            thread = threading.Thread(target=export_custom_voice_call_history_report, args=(
                                user_obj, str(user_obj.user.username), list_of_date, requested_data, export_zip_file_path, LiveChatVoIPData, zip_obj), daemon=True)
                            thread.start()
                                
                            export_path = "request_saved"
                    else:
                        create_export_request(user_obj, "10", requested_data, LiveChatDataExportRequest)
                        export_path = "request_saved_custom_range"

                elif requested_data["selected_filter_value"] == "5":
                    
                    if is_kafka_enabled():
                    
                        try:
                            zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_VOIP_HISTORY_PATH +
                                                str(user_obj.user.username) + "/VOIPHistoryToday.zip", "w")
                            file_path = LIVECHAT_VOIP_HISTORY_PATH + \
                                str(user_obj.user.username) + VOIP_HISTORY_PATH + \
                                str(today.date()) + '.xls'
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                            zip_obj.close()
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("VOIP History Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})
                        
                        export_path = FILES_VOIP_HISTORY_PATH + \
                            str(user_obj.user.username) + "/VOIPHistoryToday.zip"
                        export_path_exist = path.exists(export_path[1:])
                    else:
                        try:
                            thread = threading.Thread(target=export_today_voip_history_data, args=(user_obj, json.dumps(requested_data), LiveChatVoIPData), daemon=True)
                            thread.start()
                            export_path = "request_saved_today"
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("error in Todays data VOIP History Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})
                
            response["status"] = 200
            response["export_path"] = export_path
            response["export_path_exist"] = export_path_exist
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ExportVOIPDataAPI! %s %s", str(e), str(
                exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ExportVOIPData = ExportVOIPDataAPI.as_view()


class ExportVCDataAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)
            user_obj = LiveChatUser.objects.filter(user=request.user, is_deleted=False).first()
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            export_path = None
            export_path_exist = None
            today = datetime.now()
            if user_obj.status != "3":
                
                if not os.path.exists(settings.MEDIA_ROOT + LIVECHAT_VC_HISTORY_PATH + str(user_obj.user.username)):
                    os.makedirs(settings.MEDIA_ROOT + LIVECHAT_VC_HISTORY_PATH + str(user_obj.user.username))
                    
                if requested_data["selected_filter_value"] == "1":
                    try:
                        yesterday = today - timedelta(1)
                        zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_VC_HISTORY_PATH +
                                          str(user_obj.user.username) + "/VCHistoryLastOneDay.zip", "w")
                        file_path = LIVECHAT_VC_HISTORY_PATH + \
                            str(user_obj.user.username) + VC_HISTORY_PATH + \
                            str(yesterday.date()) + '.xls'
                        if path.exists(settings.MEDIA_ROOT + file_path):
                            zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        zip_obj.close()
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("VC History Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                            'AppName': 'LiveChat'})
                    
                    export_path = FILES_VC_HISTORY_PATH + \
                        str(user_obj.user.username) + "/VCHistoryLastOneDay.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "2":
                    zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_VC_HISTORY_PATH +
                                      str(user_obj.user.username) + "/VCHistoryLastSevenDays.zip", 'w')
                    for index in range(1, 8):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_VC_HISTORY_PATH + \
                                str(user_obj.user.username) + VC_HISTORY_PATH + \
                                str(date.date()) + '.xls'
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("VC History Datadump! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

                    zip_obj.close()
                    export_path = FILES_VC_HISTORY_PATH + \
                        str(user_obj.user.username) + "/VCHistoryLastSevenDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "3":
                    zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_VC_HISTORY_PATH +
                                      str(user_obj.user.username) + "/VCHistoryLastThirtyDays.zip", 'w')
                    for index in range(1, 31):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_VC_HISTORY_PATH + \
                                str(user_obj.user.username) + VC_HISTORY_PATH + \
                                str(date.date()) + '.xls'
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("VC History Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

                    zip_obj.close()
                    export_path = FILES_VC_HISTORY_PATH + \
                        str(user_obj.user.username) + "/VCHistoryLastThirtyDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "4":
                    
                    if is_kafka_enabled():

                        start_date = requested_data["startdate"]
                        end_date = requested_data["enddate"]

                        date_format = DATE_YYYY_MM_DD

                        start_date = datetime.strptime(start_date, date_format).date()
                        end_date = datetime.strptime(end_date, date_format).date()
                        
                        if (end_date - start_date).days > DAYS_LIMIT_FOR_KAFKA:
                            create_export_request(user_obj, "11", requested_data, LiveChatDataExportRequest)
                            export_path = "request_saved_custom_range"
                        else:
                            export_zip_file_path = LIVECHAT_VC_HISTORY_PATH +\
                                str(user_obj.user.username) + "/VCHistoryReportCustom.zip"
                            zip_obj = ZipFile(settings.MEDIA_ROOT + export_zip_file_path, 'w')                    

                            start_date_for_iteration = start_date
                            list_of_date = []
                            while start_date_for_iteration <= end_date:
                                try:
                                    file_path = LIVECHAT_VC_HISTORY_PATH + \
                                        str(user_obj.user.username) + VC_HISTORY_PATH + \
                                        str(start_date_for_iteration) + '.xls'
                                    if path.exists(settings.MEDIA_ROOT + file_path):
                                        zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                                    else:
                                        list_of_date.append(start_date_for_iteration)
                                        
                                except Exception as e:
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    logger.error("VC History Datadump! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                        'AppName': 'LiveChat'})
                                start_date_for_iteration = start_date_for_iteration + timedelta(1)
                            
                            export_zip_file_path = "files/" + export_zip_file_path
                            thread = threading.Thread(target=export_custom_video_call_history_report, args=(
                                user_obj, str(user_obj.user.username), list_of_date, requested_data, export_zip_file_path, LiveChatVoIPData, zip_obj), daemon=True)
                            thread.start()
                                
                            export_path = "request_saved"
                    else:
                        create_export_request(user_obj, "11", requested_data, LiveChatDataExportRequest)
                        export_path = "request_saved_custom_range"
                        
                elif requested_data["selected_filter_value"] == "5":
                    
                    if is_kafka_enabled():
                        try:
                            zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_VC_HISTORY_PATH +
                                                str(user_obj.user.username) + "/VCHistoryToday.zip", "w")
                            file_path = LIVECHAT_VC_HISTORY_PATH + \
                                str(user_obj.user.username) + VC_HISTORY_PATH + \
                                str(today.date()) + '.xls'
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                            zip_obj.close()
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("VC History Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})
                        
                        export_path = FILES_VC_HISTORY_PATH + \
                            str(user_obj.user.username) + "/VCHistoryToday.zip"
                        export_path_exist = path.exists(export_path[1:])
                    else:
                        try:
                            thread = threading.Thread(target=export_today_vc_history_data, args=(user_obj, json.dumps(requested_data), LiveChatVoIPData), daemon=True)
                            thread.start()
                            export_path = "request_saved_today"
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("error in Todays data VC History Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

            response["status"] = 200
            response["export_path"] = export_path
            response["export_path_exist"] = export_path_exist
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ExportVCDataAPI! %s %s", str(e), str(
                exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ExportVCData = ExportVCDataAPI.as_view()


class ExportCobrowsingDataAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)
            user_obj = LiveChatUser.objects.filter(user=request.user, is_deleted=False).first()
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            export_path = None
            export_path_exist = None
            today = datetime.now()
            if user_obj.status != "3":
                
                if not os.path.exists(settings.MEDIA_ROOT + LIVECHAT_COBROWSING_HISTORY_PATH + str(user_obj.user.username)):
                    os.makedirs(settings.MEDIA_ROOT + LIVECHAT_COBROWSING_HISTORY_PATH + str(user_obj.user.username))

                if requested_data["selected_filter_value"] == "1":
                    try:
                        yesterday = today - timedelta(1)
                        zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_COBROWSING_HISTORY_PATH +
                                          str(user_obj.user.username) + "/CobrowsingHistoryLastOneDay.zip", "w")
                        file_path = LIVECHAT_COBROWSING_HISTORY_PATH + \
                            str(user_obj.user.username) + COBROWSING_HISTORY_PATH + \
                            str(yesterday.date()) + '.xls'

                        if path.exists(settings.MEDIA_ROOT + file_path):
                            zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        zip_obj.close()
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("VOIP History Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                            'AppName': 'LiveChat'})
                    
                    export_path = FILES_COBROWSING_HISTORY_PATH + \
                        str(user_obj.user.username) + "/CobrowsingHistoryLastOneDay.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "2":
                    zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_COBROWSING_HISTORY_PATH +
                                      str(user_obj.user.username) + "/CobrowsingHistoryLastSevenDays.zip", 'w')
                    for index in range(1, 8):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_COBROWSING_HISTORY_PATH + \
                                str(user_obj.user.username) + COBROWSING_HISTORY_PATH + \
                                str(date.date()) + '.xls'
                            
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Cobrowsing History Datadump! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

                    zip_obj.close()
                    export_path = FILES_COBROWSING_HISTORY_PATH + \
                        str(user_obj.user.username) + "/CobrowsingHistoryLastSevenDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "3":
                    zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_COBROWSING_HISTORY_PATH +
                                      str(user_obj.user.username) + "/CobrowsingHistoryLastThirtyDays.zip", 'w')
                    for index in range(1, 31):
                        date = today - timedelta(index)
                        try:
                            file_path = LIVECHAT_COBROWSING_HISTORY_PATH + \
                                str(user_obj.user.username) + COBROWSING_HISTORY_PATH + \
                                str(date.date()) + '.xls'
                            
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Cobrowsing History Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

                    zip_obj.close()
                    export_path = FILES_COBROWSING_HISTORY_PATH + \
                        str(user_obj.user.username) + "/CobrowsingHistoryLastThirtyDays.zip"
                    # export_path_exist = path.exists(export_path[1:])
                    export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                elif requested_data["selected_filter_value"] == "4":
                    
                    if is_kafka_enabled():

                        start_date = requested_data["startdate"]
                        end_date = requested_data["enddate"]

                        date_format = DATE_YYYY_MM_DD

                        start_date = datetime.strptime(start_date, date_format).date()
                        end_date = datetime.strptime(end_date, date_format).date()
                        
                        if (end_date - start_date).days > DAYS_LIMIT_FOR_KAFKA:
                            create_export_request(user_obj, "12", requested_data, LiveChatDataExportRequest)
                            export_path = "request_saved_custom_range"
                        else:

                            export_zip_file_path = LIVECHAT_COBROWSING_HISTORY_PATH +\
                                str(user_obj.user.username) + "/CobrowsingHistoryCustom.zip"
                            zip_obj = ZipFile(settings.MEDIA_ROOT + export_zip_file_path, 'w')
                            
                            start_date_for_iteration = start_date
                            list_of_date = []
                            while start_date_for_iteration <= end_date:
                                try:
                                    file_path = LIVECHAT_COBROWSING_HISTORY_PATH + \
                                        str(user_obj.user.username) + COBROWSING_HISTORY_PATH + \
                                        str(start_date_for_iteration) + '.xls'
                                    if path.exists(settings.MEDIA_ROOT + file_path):
                                        zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                                    else:
                                        list_of_date.append(start_date_for_iteration)

                                except Exception as e:
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    logger.error("Cobrowsing History Datadump! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                        'AppName': 'LiveChat'})
                                start_date_for_iteration = start_date_for_iteration + timedelta(1)

                            export_zip_file_path = "files/" + export_zip_file_path
                            thread = threading.Thread(target=export_custom_cobrowsing_history_report, args=(
                                user_obj, str(user_obj.user.username), list_of_date, requested_data, export_zip_file_path, LiveChatCobrowsingData, zip_obj), daemon=True)
                            thread.start()
                            
                            export_path = "request_saved"
                    else:
                        create_export_request(user_obj, "12", requested_data, LiveChatDataExportRequest)
                        export_path = "request_saved_custom_range"
                    
                elif requested_data["selected_filter_value"] == "5":
                    
                    if is_kafka_enabled():
                        try:
                            zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_COBROWSING_HISTORY_PATH +
                                                str(user_obj.user.username) + "/CobrowsingHistoryToday.zip", "w")
                            file_path = LIVECHAT_COBROWSING_HISTORY_PATH + \
                                str(user_obj.user.username) + COBROWSING_HISTORY_PATH + \
                                str(today.date()) + '.xls'
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                            zip_obj.close()
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("error in Todays data Cobrowsing History Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

                        export_path = FILES_COBROWSING_HISTORY_PATH + \
                            str(user_obj.user.username) + "/CobrowsingHistoryToday.zip"
                        export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
                    else:
                        try:
                            thread = threading.Thread(target=export_today_cobrowsing_history_data, args=(user_obj, json.dumps(requested_data), LiveChatCobrowsingData), daemon=True)
                            thread.start()
                            export_path = "request_saved_today"
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("error in Todays data Cobrowsing History Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})

            response["status"] = 200
            response["export_path"] = export_path
            response["export_path_exist"] = export_path_exist
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ExportCobrowsingDataAPI! %s %s", str(e), str(
                exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ExportCobrowsingData = ExportCobrowsingDataAPI.as_view()


class GetCategoriesFromSupervisorsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            if user_obj.status == "1" and 'supervisors_list' in requested_data:

                supervisors_list = requested_data['supervisors_list']
                if supervisors_list:
                    if not isinstance(supervisors_list, list):
                        supervisors_list = supervisors_list.split(',')
                    user_obj_list = LiveChatUser.objects.filter(pk__in=supervisors_list)

                    bot_pks = user_obj_list.values_list('bots', flat=True).exclude(bots=None)
                    bot_objs = Bot.objects.filter(pk__in=bot_pks, is_deleted=False)

                    category_pks = user_obj_list.values_list('category', flat=True).exclude(category=None)
                    category_objs = LiveChatCategory.objects.filter(pk__in=category_pks, bot__in=bot_objs, is_deleted=False)

                else:
                    bot_objs = user_obj.bots.filter(is_deleted=False)
                    category_objs = user_obj.category.filter(
                        bot__in=bot_objs, is_deleted=False)

                category_data = []

                for category in category_objs:
                    category_data.append({
                        'pk': category.pk,
                        'name': category.get_category_name()
                    })

                response['status'] = 200
                response['category_data'] = category_data

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetCategoriesFromSupervisorsAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetCategoriesFromSupervisors = GetCategoriesFromSupervisorsAPI.as_view()


class GetAgentsFromSupervisorsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj_list = get_agents_under_this_user(user_obj)

            if user_obj.status == "1" and 'supervisors_list' in requested_data:

                supervisors_list = requested_data['supervisors_list']

                if supervisors_list:
                    user_obj_list = get_agents_as_per_supervisors(supervisors_list, user_obj_list, LiveChatUser)

                agents_data = []

                for agent in user_obj_list:
                    agents_data.append({
                        'pk': agent.pk,
                        'username': agent.user.username
                    })

                response['status'] = 200
                response['agents_data'] = agents_data

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetAgentsFromSupervisorsAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetAgentsFromSupervisors = GetAgentsFromSupervisorsAPI.as_view()


class GetSupervisorsFromCategoriesAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            category_objs = user_obj.category.filter(is_deleted=False)

            if user_obj.status == "1" and "category_list" in requested_data:

                category_list = requested_data['category_list']

                if category_list:
                    category_objs = LiveChatCategory.objects.filter(pk__in=category_list, is_deleted=False)
                else:
                    category_objs = user_obj.category.filter(is_deleted=False)

                supervisor_objs = LiveChatUser.objects.filter(category__in=category_objs, status='2').distinct() 

                supervisor_data = []

                supervisor_data.append({
                    'pk': user_obj.pk,
                    'username': user_obj.user.username
                })

                for supervisor in supervisor_objs:
                    supervisor_data.append({
                        'pk': supervisor.pk,
                        'username': supervisor.user.username
                    })

                response['status'] = 200
                response['supervisor_data'] = supervisor_data

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetSupervisorsFromCategoriesAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetSupervisorsFromCategories = GetSupervisorsFromCategoriesAPI.as_view()


class GetAgentAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)

            if user_obj.status == "3":

                user_obj_list = [user_obj]
                start_date = requested_data['start_date']
                end_date = requested_data['end_date']
                channel_name = requested_data['channel']

                date_format = DATE_YYYY_MM_DD
                start_date = datetime.strptime(
                    start_date, date_format).date()
                end_date = datetime.strptime(end_date, date_format).date()

                channel_objs = get_analytics_channel_objs(channel_name, Channel)
                category_objs = user_obj.category.filter(is_deleted=False)

                total_closed_chats = get_total_closed_chats_filtered(start_date, end_date, channel_objs, user_obj_list, LiveChatCustomer)

                avg_interactions = get_livechat_avg_interaction_per_chat_filter(
                    user_obj_list, start_date, end_date, channel_objs, category_objs, LiveChatCustomer, LiveChatMISDashboard)

                avg_handle_time = get_livechat_avh_filter(
                    user_obj_list, start_date, end_date, channel_objs, category_objs, LiveChatCustomer)

                avg_nps = get_nps_avg_filter(
                    user_obj_list, start_date, end_date, channel_objs, category_objs, LiveChatCustomer)

                followup_leads = get_followup_leads_filtered(start_date, end_date, channel_objs, user_obj_list, LiveChatFollowupCustomer)

                total_tickets_raised = get_total_tickets_raised_filtered(user_obj_list, start_date, end_date, channel_objs, category_objs, LiveChatTicketAudit)

                avg_call_duration = get_average_call_duration_filtered(user_obj_list, start_date, end_date, channel_objs, category_objs, LiveChatVoIPData)

                avg_video_call_duration = get_average_video_call_duration_filtered(user_obj_list, start_date, end_date, channel_objs, category_objs, LiveChatVoIPData)

                avg_cobrowsing_duration = get_average_cobrowsing_duration_filtered(user_obj_list, start_date, end_date, channel_objs, category_objs, LiveChatCobrowsingData)

                response['total_closed_chats'] = total_closed_chats
                response['avg_interactions'] = avg_interactions
                response['avg_handle_time'] = avg_handle_time
                response['avg_nps'] = avg_nps
                response['followup_leads'] = followup_leads
                response['total_tickets_raised'] = total_tickets_raised
                response['avg_call_duration'] = avg_call_duration
                response['avg_video_call_duration'] = avg_video_call_duration
                response['avg_cobrowsing_duration'] = avg_cobrowsing_duration

                response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetAgentAnalyticsAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetAgentAnalytics = GetAgentAnalyticsAPI.as_view()
