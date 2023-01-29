from django.shortcuts import render, redirect

# from rest_framework import status

from django.core.paginator import EmptyPage, PageNotAnInteger

from CampaignApp.utils import *
from EasyChatApp.models import Bot

# Logger
import logging
logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


@login_required(login_url="/chat/login")
def WhatsappCampaignDetailsPage(request):
    try:
        if not request.user.is_authenticated:
            return redirect("/chat/login")

        bot_pk = request.GET['bot_pk']
        bot_obj = Bot.objects.filter(pk=int(bot_pk), is_deleted=False).first()
        if not bot_obj or request.user not in bot_obj.users.all():
            return redirect("/campaign/unauthorised/")

        status_list = [CAMPAIGN_COMPLETED, CAMPAIGN_FAILED,
                       CAMPAIGN_ONGOING, CAMPAIGN_PARTIALLY_COMPLETED, CAMPAIGN_PROCESSED, CAMPAIGN_DRAFT]

        campaign_id = request.GET['campaign_id']
        selected_campaign_obj = Campaign.objects.filter(
            bot=bot_obj, channel__value="whatsapp", status__in=status_list, pk=campaign_id, is_deleted=False).first()
        if not selected_campaign_obj:
            return render(request, 'CampaignApp/error_500.html')

        start_date = bot_obj.created_datetime.date()
        end_date = datetime.now().date()

        return render(request, "CampaignApp/whatsapp_campaign_details.html", {
            "selected_bot_obj": bot_obj,
            "selected_campaign_obj": selected_campaign_obj,
            "start_date": str(start_date),
            "end_date": str(end_date)
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error WhatsappCampaignDetailsPage %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return render(request, 'CampaignApp/error_500.html')


class GetWhatsappAudienceCampaignDetailsPageAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["message"] = "Internal Server Error"
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            bot_pk = data["bot_pk"]
            page = data["page"]
            total_rows_per_pages = int(data["number_of_records"])
            bot_obj = Bot.objects.filter(pk=bot_pk, is_deleted=False).first()
            user = request.user

            if bot_obj and user in bot_obj.users.all():
                audience_log_objs, return_data = get_whatsapp_audience_log_data(
                    data, bot_obj, False)

                unauthorised_campaign = return_data.get('unauthorised_campaign')
                if unauthorised_campaign:
                    response["status"] = "401"
                    response["message"] = "Unauthorised Campaign"
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)

                # date_range_list = return_data.get('date_range')
                if len(data['templates']) == 0:
                    response['selected_template_names'] = return_data.get(
                        'selected_template_names')

                selected_campaigns = return_data.get(
                    'selected_campaigns')
                if selected_campaigns:
                    response['selected_campaigns'] = selected_campaigns

                all_campaign_list = return_data.get('all_campaign_objs')
                if all_campaign_list:
                    response['all_campaign_list'] = all_campaign_list
                
                if not data.get('is_pagination'):
                    user_stats_list = get_whatsapp_users_stats(audience_log_objs)
                    response["user_stats_list"] = list(user_stats_list)

                quick_replies_obj = QuickReply.objects.filter(bot=bot_obj)

                audience_log_objs = audience_log_objs.order_by('-pk')

                paginator = Paginator(
                    audience_log_objs, total_rows_per_pages)
                try:
                    audience_log_objs = paginator.page(page)

                except PageNotAnInteger:
                    audience_log_objs = paginator.page(1)
                except EmptyPage:
                    audience_log_objs = paginator.page(paginator.num_pages)
                
                total_audience_log_objs = audience_log_objs.paginator.count
                
                if page != None:
                    start_point = total_rows_per_pages * (int(page) - 1) + 1
                    end_point = min(total_rows_per_pages *
                                    int(page), total_audience_log_objs)
                    if start_point > end_point:
                        start_point = max(
                            end_point - len(audience_log_objs) + 1, 1)
                else:
                    start_point = 1
                    end_point = min(total_rows_per_pages,
                                    total_audience_log_objs)

                start_point = min(start_point, end_point)

                pagination_range = audience_log_objs.paginator.page_range

                has_next = audience_log_objs.has_next()
                has_previous = audience_log_objs.has_previous()
                next_page_number = -1
                previous_page_number = -1
                template_objs = CampaignTemplate.objects.filter(
                    bot=bot_obj, is_deleted=False)
                if has_next:
                    next_page_number = audience_log_objs.next_page_number()
                if has_previous:
                    previous_page_number = audience_log_objs.previous_page_number()

                pagination_metadata = {
                    'total_count': total_audience_log_objs,
                    'start_point': start_point,
                    'end_point': end_point,
                    'page_range': [pagination_range.start, pagination_range.stop],
                    'has_next': has_next,
                    'has_previous': has_previous,
                    'next_page_number': next_page_number,
                    'previous_page_number': previous_page_number,
                    'number': audience_log_objs.number,
                    'num_pages': audience_log_objs.paginator.num_pages
                }

                whatsapp_campaign_data = []

                for audience_log_obj in audience_log_objs:
                    audience_data = get_whatsapp_audience_user_data(
                        audience_log_obj, quick_replies_obj)
                    if audience_data:
                        whatsapp_campaign_data.append(audience_data)

                response["status"] = "200"
                response["message"] = "Success"
                response["data"] = whatsapp_campaign_data
                response["quick_reply_data"] = list(
                    quick_replies_obj.values_list('name', flat=True))
                response["template_names"] = list(
                    template_objs.values_list('template_name', flat=True).distinct())
                response["pagination_metadata"] = pagination_metadata
                # response["date_range_list"] = date_range_list
            else:
                response["message"] = "You do not have access to this data"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetWhatsappAudienceCampaignDetailsPageAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetWhatsappAudienceCampaignDetailsPage = GetWhatsappAudienceCampaignDetailsPageAPI.as_view()


class SaveExportWhatsappCampaignHistoryRequestAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["message"] = "Internal Server Error"
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            bot_pk = data["bot_pk"]
            number_of_records = data.get('total_entry', 0)

            bot_obj = Bot.objects.filter(pk=bot_pk, is_deleted=False).first()
            user = request.user

            if bot_obj and user in bot_obj.users.all():
                if number_of_records == 0:
                    response["message"] = "No data available for the selected filter or campaign to export"
                elif number_of_records <= 5000:
                    audience_log_objs, _ = get_whatsapp_audience_log_data(
                        data, bot_obj, False)
                    file_path = get_whatsapp_audience_reports(
                        audience_log_objs, data)
                    file_path = 'files/' + file_path[0]
                    response["message"] = "Downloading the requested report"
                    response['file_path'] = file_path
                else:
                    CampaignHistoryExportRequest.objects.create(
                        user=user, request_data=json.dumps(data), is_whatsapp=True)
                    response["message"] = "You will receive the whatsapp filtered report on the given email ID within 24 hours."
                response["status"] = "200"
            else:
                response["message"] = "You do not have access to this data"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error in SaveExportWhatsappCampaignHistoryRequestAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveExportWhatsappCampaignHistoryRequest = SaveExportWhatsappCampaignHistoryRequestAPI.as_view()
