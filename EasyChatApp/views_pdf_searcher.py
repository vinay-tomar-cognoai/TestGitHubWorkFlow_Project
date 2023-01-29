from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication  # noqa F401
from django.contrib.sessions.models import Session

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.utils.encoding import smart_str
# from django.utils.safestring import mark_safe

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponse, \
    HttpResponseRedirect
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.clickjacking import xframe_options_exempt
from django.http import HttpResponseNotFound

from EasyChatApp.models import Bot, User
from EasySearchApp.models import *
from EasyChatApp.constants import *
from EasySearchApp.constants import PDF_SEARCH_ACTIVE_STATUS, PDF_SEARCH_INACTIVE_STATUS, \
    PDF_SEARCH_INDEXING_STATUS, PDF_SEARCH_NOT_INDEXED_STATUS

from EasyChatApp.utils import *
from EasyChatApp.utils_faq import *
from EasyChatApp.utils_parse_pdf_search import *
from EasyChatApp.utils_validation import EasyChatInputValidation, EasyChatFileValidation
from EasyChatApp.utils_pdf_search import *
from EasyChatApp.utils_custom_encryption import *
# from EasyChatApp.utils_custom_encryption import generate_random_key


from django.core.files.storage import FileSystemStorage
from EasyChat.settings import BASE_DIR, EASYCHAT_HOST_URL
from dateutil import tz
from datetime import datetime, date, timedelta

import json
import xlrd
import logging
import uuid
import threading
import re
import sys
import time
import mimetypes
import random
import hashlib
import pytz

logger = logging.getLogger(__name__)


def PDFSearcher(request):
    try:
        if not request.user.is_authenticated:
            return HttpResponse(status=404)

        bot_pk = request.GET['bot_pk']

        if not check_access_for_user(request.user, bot_pk, "PDF Searcher"):
            return HttpResponseNotFound("You do not have access to this page")

        username = request.user.username
        user_obj = User.objects.get(username=str(username))

        bot_obj = Bot.objects.get(pk=int(bot_pk), users__in=[
            user_obj], is_uat=True, is_deleted=False)

        if bot_obj.is_pdf_search_allowed == False:
            return HttpResponse(status=404)

        is_indexing_in_progress = easysearch_check_indexing_in_progress(bot_obj, PDFSearchIndexStat)
        is_indexing_required = easysearch_check_indexing_required(bot_obj, PDFSearchIndexStat)

        return render(request, 'EasyChatApp/platform/pdf_searcher.html', {
            "bot_obj": bot_obj,
            "selected_bot_obj": bot_obj,
            "selected_language": "en",
            'default_start_date': (datetime.today() - timedelta(days=7)).date(),
            'default_end_date': (datetime.today()).date(),
            "is_indexing_in_progress": is_indexing_in_progress,
            "is_indexing_required": is_indexing_required,
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error PDFSearcher %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return HttpResponse(status=404)


def EasySearchPDFRedirect(request, pdf_search_key, page_number):
    try:
        pdf_search_obj = EasyPDFSearcher.objects.get(key=pdf_search_key)

        pdf_search_analytics_obj = EasyPDFSearcherAnalytics.objects.filter(
            pdf_searcher=pdf_search_obj).first()
        if pdf_search_analytics_obj is None:
            pdf_search_analytics_obj = EasyPDFSearcherAnalytics.objects.create(
                pdf_searcher=pdf_search_obj)

        pdf_search_analytics_obj.click_count += 1
        pdf_search_analytics_obj.save()

        show_pdf_url = "/chat/pdf/show/" + \
            pdf_search_key + "/" + str(page_number)
        return HttpResponseRedirect(show_pdf_url)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error EasySearchPDFRender %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return HttpResponse(status=404)


def EasySearchPDFRender(request, pdf_search_key, page_number):
    try:
        pdf_search_obj = EasyPDFSearcher.objects.filter(
            key=pdf_search_key).first()

        file_name = pdf_search_obj.name
        file_path = pdf_search_obj.file_path
        pdf_source_url = settings.EASYCHAT_HOST_URL + \
            file_path + "#page=" + str(page_number)

        return render(request, 'EasyChatApp/platform/pdf_render.html', {
            "pdf_source_url": pdf_source_url,
            "title": file_name,
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error EasySearchPDFRender %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return HttpResponse(status=404)


"""

GetActivePDFAPI() : return all active PDF objs

"""


class GetActivePDFAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            page = data["page"]
            bot_pk = data["bot_pk"]
            bot_obj = Bot.objects.get(pk=int(bot_pk))

            pdf_objs = EasyPDFSearcher.objects.filter(
                bot_obj=bot_obj, is_deleted=False)

            if 'selected_date_filter' in data and data['selected_date_filter'] != '':
                selected_date_filter = data['selected_date_filter']
            else:
                selected_date_filter = 'all'

            if selected_date_filter == 'all':
                default_start_date = datetime.now() - timedelta(days=7)
                default_end_date = datetime.now()
                pdf_objs = pdf_objs.filter(
                    created_datetime__date__gte=default_start_date, created_datetime__date__lte=default_end_date)
            else:
                if selected_date_filter != '5':
                    if selected_date_filter == '1':
                        start_date = datetime.now() - timedelta(days=7)
                        end_date = datetime.now()

                    elif selected_date_filter == '2':
                        start_date = datetime.now() - timedelta(days=30)
                        end_date = datetime.now()

                    elif selected_date_filter == '3':
                        start_date = datetime.now() - timedelta(days=90)
                        end_date = datetime.now()

                    elif selected_date_filter == '4':
                        date_format = "%Y-%m-%d"
                        start_date = data['start_date']
                        end_date = data['end_date']

                        start_date = datetime.strptime(
                            start_date, date_format).date()

                        end_date = datetime.strptime(
                            end_date, date_format).date()

                    pdf_objs = pdf_objs.filter(
                        created_datetime__date__gte=start_date, created_datetime__date__lte=end_date)

            if 'pdf_search_status' in data and len(data['pdf_search_status']) > 0:
                status = data['pdf_search_status']
                pdf_objs = pdf_objs.filter(status__in=status)

            pdf_objs = pdf_objs.order_by('-created_datetime')

            total_rows_per_pages = 20
            total_pdf_objs = pdf_objs.count()

            paginator = Paginator(
                pdf_objs, total_rows_per_pages)

            try:
                pdf_objs = paginator.page(page)
            except PageNotAnInteger:
                pdf_objs = paginator.page(1)
            except EmptyPage:
                pdf_objs = paginator.page(paginator.num_pages)

            if page != None:
                start_point = total_rows_per_pages * (int(page) - 1) + 1
                end_point = min(total_rows_per_pages *
                                int(page), total_pdf_objs)
                if start_point > end_point:
                    start_point = max(end_point - len(pdf_objs) + 1, 1)
            else:
                start_point = 1
                end_point = min(total_rows_per_pages, total_pdf_objs)

            start_point = min(start_point, end_point)

            pagination_range = pdf_objs.paginator.page_range

            has_next = pdf_objs.has_next()
            has_previous = pdf_objs.has_previous()
            next_page_number = -1
            previous_page_number = -1

            if has_next:
                next_page_number = pdf_objs.next_page_number()
            if has_previous:
                previous_page_number = pdf_objs.previous_page_number()

            pagination_metadata = {
                'total_count': total_pdf_objs,
                'start_point': start_point,
                'end_point': end_point,
                'page_range': [pagination_range.start, pagination_range.stop],
                'has_next': has_next,
                'has_previous': has_previous,
                'next_page_number': next_page_number,
                'previous_page_number': previous_page_number,
                'number': pdf_objs.number,
                'num_pages': pdf_objs.paginator.num_pages
            }

            active_pdfs = []
            for pdf_obj in pdf_objs:
                active_pdfs.append(parse_pdf_details(
                    pdf_obj, EasyPDFSearcherAnalytics))

            is_indexing_in_progress = easysearch_check_indexing_in_progress(bot_obj, PDFSearchIndexStat)
            is_indexing_required = easysearch_check_indexing_required(bot_obj, PDFSearchIndexStat)

            response["status"] = 200
            response["message"] = "success"
            response["active_pdfs"] = active_pdfs
            response["pagination_metadata"] = pagination_metadata
            response["is_indexing_in_progress"] = is_indexing_in_progress
            response["is_indexing_required"] = is_indexing_required
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetActivepdfsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetActivePDF = GetActivePDFAPI.as_view()


class UploadPDFAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            file_validation_obj = EasyChatFileValidation()
            validation_obj = EasyChatInputValidation()

            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            pdfname = data["name"]
            filename = data["file_name"]
            bot_pk = data["bot_pk"]
            important_pages = data["important_pages"]
            skipped_pages = data["skipped_pages"]

            pdfname = validation_obj.remo_html_from_string(pdfname)
            pdfname = validation_obj.remo_special_tag_from_string(pdfname)
            filename = validation_obj.remo_html_from_string(filename)
            filename = validation_obj.remo_special_tag_from_string(filename)
            filename = get_dot_replaced_file_name(filename)

            if not check_access_for_user(request.user, bot_pk, "PDF Searcher"):
                return HttpResponseNotFound("You do not have access to this request")

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            base64_data = validation_obj.remo_html_from_string(
                data["base64_file"])

            filename = generate_random_key(
                10) + "_" + filename.replace(" ", "")

            # file_path = 'secured_files/EasyChatApp/PDFSearch/' + filename
            file_path = "files/PDFSearch/" + filename

            file_extention = file_path.split(".")[-1]
            file_extention = file_extention.lower()

            allowed_files_list = ['pdf']
            if file_extention in allowed_files_list:
                media_type = "file"
            else:
                media_type = None

            is_file_malicious = file_validation_obj.check_malicious_file_from_filename(
                filename, allowed_files_list)
            is_file_malicious |= file_validation_obj.check_malicious_file_from_content(
                base64_data, allowed_files_list)

            if media_type == None or is_file_malicious:
                response["status"] = 300
            else:
                fh = open(file_path, "wb")
                fh.write(base64.b64decode(base64_data))
                fh.close()

                file_path = "/" + file_path
                # file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
                #     file_path=file_path, is_public=False, is_customer_attachment=False)

                filtered_pdf_object_by_name = EasyPDFSearcher.objects.filter(
                    name=pdfname, bot_obj=bot_obj, is_deleted=False)

                if len(filtered_pdf_object_by_name) > 0:
                    response["status"] = 400
                    response["message"] = "PDF with the provided name already exists."

                else:
                    EasyPDFSearcher.objects.create(
                        name=pdfname,
                        file_path=file_path,
                        important_pages=important_pages,
                        skipped_pages=skipped_pages,
                        status=PDF_SEARCH_NOT_INDEXED_STATUS,
                        bot_obj=bot_obj
                    )

                    easysearch_set_indexing_required(True, bot_obj, PDFSearchIndexStat)

                    response["status"] = 200
                    response["message"] = "success"
                    response["file_path"] = file_path
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UploadPDFAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UploadPDF = UploadPDFAPI.as_view()


class DeletePDFAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            bot_pk = data["bot_pk"]
            pdf_key = data["pdf_key"]
            bot_obj = Bot.objects.get(pk=int(bot_pk))

            pdf_search_obj = EasyPDFSearcher.objects.get(
                key=pdf_key, bot_obj=bot_obj, is_deleted=False)
            pdf_search_obj.is_deleted = True
            pdf_search_obj.deleted_datetime = timezone.now()
            pdf_search_obj.save()

            easysearch_set_indexing_required(True, bot_obj, PDFSearchIndexStat)

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeletePDFAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeletePDF = DeletePDFAPI.as_view()


class UpdatePDFAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            file_validation_obj = EasyChatFileValidation()
            validation_obj = EasyChatInputValidation()

            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            pdfname = data["name"]
            pdf_key = data["pdf_key"]
            bot_pk = data["bot_pk"]
            important_pages = data["important_pages"]
            skipped_pages = data["skipped_pages"]
            status = data["status"]

            is_file_attached = data["is_file_attached"]
            filename = None
            base64_data = None
            if is_file_attached:
                filename = data["file_name"]
                filename = validation_obj.remo_html_from_string(filename)
                filename = validation_obj.remo_special_tag_from_string(filename)
                filename = get_dot_replaced_file_name(filename)

                base64_data = validation_obj.remo_html_from_string(
                    data["base64_file"])

            status = validation_obj.remo_html_from_string(status)
            pdfname = validation_obj.remo_html_from_string(pdfname)
            pdfname = validation_obj.remo_special_tag_from_string(pdfname)

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            is_all_check_valid = True

            file_path = None
            if is_file_attached:
                filename = generate_random_key(
                    10) + "_" + filename.replace(" ", "")

                # file_path = 'secured_files/EasyChatApp/PDFSearch/' + filename
                file_path = 'files/PDFSearch/' + filename
                file_extention = file_path.split(".")[-1]
                file_extention = file_extention.lower()

                allowed_files_list = ['pdf']
                if file_extention in allowed_files_list:
                    media_type = "file"
                else:
                    media_type = None

                is_file_malicious = file_validation_obj.check_malicious_file_from_filename(
                    filename, allowed_files_list)
                is_file_malicious |= file_validation_obj.check_malicious_file_from_content(
                    base64_data, allowed_files_list)

                if media_type == None or is_file_malicious:
                    response["status"] = 300
                    is_all_check_valid = False
                else:
                    fh = open(file_path, "wb")
                    fh.write(base64.b64decode(base64_data))
                    fh.close()

                    file_path = "/" + file_path

                    old_pdf_object = EasyPDFSearcher.objects.get(key=pdf_key)
                    old_pdf_name = old_pdf_object.name

                    filtered_pdf_object_by_name = EasyPDFSearcher.objects.filter(
                        name=pdfname, bot_obj=bot_obj, is_deleted=False)

                    if len(filtered_pdf_object_by_name) > 0 and pdfname != old_pdf_name:
                        response["status"] = 400
                        response["message"] = "PDF with the provided name already exists."
                        is_all_check_valid = False

            if is_all_check_valid:
                pdf_search_obj = EasyPDFSearcher.objects.get(
                    key=pdf_key, bot_obj=bot_obj)

                is_indexing_required = False

                if pdf_search_obj.important_pages != important_pages:
                    is_indexing_required = True
                elif pdf_search_obj.skipped_pages != skipped_pages:
                    is_indexing_required = True
                elif pdf_search_obj.name != pdfname:
                    is_indexing_required = True
                elif is_file_attached:
                    is_indexing_required = True

                pdf_search_obj.name = pdfname
                pdf_search_obj.important_pages = important_pages
                pdf_search_obj.skipped_pages = skipped_pages
                pdf_search_obj.status = status

                if is_file_attached and file_path:
                    pdf_search_obj.file_path = file_path

                pdf_search_obj.save()

                response["status"] = 200
                response["message"] = "success"
                response["file_path"] = file_path
                response["is_indexing_required"] = is_indexing_required

                if is_indexing_required:
                    easysearch_set_indexing_required(True, bot_obj, PDFSearchIndexStat)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdatePDFAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UpdatePDF = UpdatePDFAPI.as_view()


"""

ExportPDFSearchReportAPI() : Export pdf search report API

"""


class ExportPDFSearchReportAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["message"] = "Internal server Error"
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            bot_id = data["bot_id"]
            email_id = data["email_id"]

            bot_obj = Bot.objects.get(pk=int(bot_id))

            if bot_obj.created_by != request.user:
                response[
                    'message'] = 'You are not authorised to perform this request.'
            else:
                export_request = PDFSearchExportRequest.objects.create(
                    email_id=email_id,
                    user=request.user,
                    bot=bot_obj)

                request_date_type = data['request_date_type']

                if request_date_type == '1':
                    start_date = datetime.today() - timedelta(days=7)
                    end_date = datetime.today()
                elif request_date_type == '2':
                    start_date = datetime.today() - timedelta(days=30)
                    end_date = datetime.today()
                elif request_date_type == '3':
                    start_date = datetime.today() - timedelta(days=90)
                    end_date = datetime.today()
                else:
                    date_format = "%d-%m-%Y"
                    start_date = data['start_date']
                    end_date = data['end_date']

                    start_date = datetime.strptime(
                        start_date, date_format).date()

                    end_date = datetime.strptime(
                        end_date, date_format).date()

                export_request.start_date = start_date
                export_request.end_date = end_date
                export_request.save()

                response['status'] = 200
                response['message'] = 'success'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ExportPDFSearchReportAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportPDFSearchReport = ExportPDFSearchReportAPI.as_view()


class StartIndexingAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            bot_pk = data["bot_pk"]
            bot_obj = Bot.objects.get(pk=int(bot_pk))

            is_elasticsearch_server_active = easysearch_check_server_active()
            is_indexing_process_running = easysearch_check_indexing_in_progress(bot_obj, PDFSearchIndexStat)
            is_indexing_required = easysearch_check_indexing_required(bot_obj, PDFSearchIndexStat)

            if is_elasticsearch_server_active == False:
                response["status"] = 300

            elif is_indexing_process_running:
                response["status"] = 301

            elif is_indexing_required == False:
                response["status"] = 302

            else:
                thread = threading.Thread(target=easysearch_start_indexing, args=(
                    bot_obj, EasyPDFSearcher, PDFSearchIndexStat), daemon=True)
                thread.start()

                response["status"] = 200
                response["message"] = "success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error StartIndexingAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


StartIndexing = StartIndexingAPI.as_view()
