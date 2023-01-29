import json

from django.contrib.auth import logout
from django.contrib.sessions.models import Session
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import HttpResponseRedirect, redirect, render
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from AuditTrailApp.encrypt import CustomEncrypt
from AuditTrailApp.models import *
from AuditTrailApp.utils import *
from EasyChatApp.models import User, SecuredLogin, UserSession

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def unauthorisedPage(request):
    try:
        message = None

        return render(request, "AuditTrailApp/unauthorised.html", {
            "message": message
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("unauthorisedPage: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'AuditTrailApp'})

        return HttpResponse("Invalid Access")


def homePage(request):
    try:
        return redirect("/audit-trail/dashboard/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("homePage: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'AuditTrailApp'})
        return HttpResponseRedirect("/chat/login")


@authentication_classes([CsrfExemptSessionAuthentication, BasicAuthentication])
def logoutAPI(request):
    if request.user.is_authenticated:
        user_obj = User.objects.get(username=request.user.username)
        user_obj.is_online = False
        user_obj.save()
        try:
            secured_login_obj = SecuredLogin.objects.get(user=user_obj)
            secured_login_obj.failed_attempts = 0
            secured_login_obj.is_online = False
            secured_login_obj.save()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("logoutAPI: %s at %s", e, str(
                exc_tb.tb_lineno), extra={'AppName': 'AuditTrailApp'})

        logout_all(request.user.username, UserSession, Session)
        logout(request)

    return redirect("/chat/login/")


def dashboard(request):
    try:
        if not request.user.is_authenticated:
            return redirect("/chat/login")

        user_obj = User.objects.get(username=request.user.username)
        if check_is_allincall_user(user_obj) is False and user_obj.is_staff is False:
            return redirect("/audit-trail/unauthorised/")

        return render(request, "AuditTrailApp/dashboard.html", {
            'default_start_date': (datetime.today() - timedelta(days=7)).date(),
            'default_end_date': (datetime.today()).date(),
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("dashboard: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'AuditTrailApp'})
        return Response(status=401)


class GetAuditTrailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def apply_date_filters(self, data, audit_trail_objs):

        if 'filter_date_type' in data and data['filter_date_type'] != '':
            filter_date_type = data['filter_date_type']
        else:
            filter_date_type = 'all'

        if filter_date_type == '4':
            return audit_trail_objs

        end_date = datetime.now() - timedelta(days=1)
        start_date = datetime.now() - timedelta(days=7)

        if filter_date_type == '2':
            start_date = datetime.now() - timedelta(days=30)

        elif filter_date_type == '3':
            start_date = datetime.now() - timedelta(days=90)

        elif filter_date_type == '5':
            start_date = data['start_date']
            end_date = data['end_date']

            start_date = datetime.strptime(
                start_date, COMMON_DATE_FORMAT).date()

            end_date = datetime.strptime(
                end_date, COMMON_DATE_FORMAT).date()

        start_date = start_date.date()
        end_date = end_date.date()

        audit_trail_objs = audit_trail_objs.filter(
            datetime__date__gte=start_date, datetime__date__lte=end_date)

        return audit_trail_objs

    def apply_app_filter(self, data, audit_trail_objs):

        if 'selected_apps' in data:
            selected_apps = data['selected_apps']
            selected_apps = [app_name.upper() for app_name in selected_apps]
            audit_trail_objs = audit_trail_objs.filter(app_name__in=selected_apps)

        return audit_trail_objs

    def apply_pagination(self, target_objs, page_number, rows_per_pages):

        total_rows_per_pages = rows_per_pages
        target_objs_count = target_objs.count()

        paginator = Paginator(
            target_objs, total_rows_per_pages)

        try:
            target_objs = paginator.page(page_number)
        except PageNotAnInteger:
            target_objs = paginator.page(1)
        except EmptyPage:
            target_objs = paginator.page(paginator.num_pages)

        if page_number is not None:
            start_point = total_rows_per_pages * (int(page_number) - 1) + 1
            end_point = min(total_rows_per_pages *
                            int(page_number), target_objs_count)
            if start_point > end_point:
                start_point = max(end_point - target_objs_count + 1, 1)
        else:
            start_point = 1
            end_point = min(total_rows_per_pages, target_objs_count)

        start_point = min(start_point, end_point)

        pagination_range = target_objs.paginator.page_range

        has_next = target_objs.has_next()
        has_previous = target_objs.has_previous()
        next_page_number = -1
        previous_page_number = -1

        if has_next:
            next_page_number = target_objs.next_page_number()
        if has_previous:
            previous_page_number = target_objs.previous_page_number()

        pagination_metadata = {
            'total_count': target_objs_count,
            'start_point': start_point,
            'end_point': end_point,
            'page_range': [pagination_range.start, pagination_range.stop],
            'has_next': has_next,
            'has_previous': has_previous,
            'next_page_number': next_page_number,
            'previous_page_number': previous_page_number,
            'number': target_objs.number,
            'num_pages': target_objs.paginator.num_pages
        }

        return target_objs, pagination_metadata

    def parse_audit_trail_detail_list(self, audit_trail_objs):

        audit_trail_list = []
        for audit_trail_obj in audit_trail_objs:
            audit_trail_list.append(parse_audit_trail_details(audit_trail_obj))

        return audit_trail_list

    def post(self, request, *args, **kwargs):
        response = {'status': 500}
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            user_obj = User.objects.get(username=request.user.username)
            if check_is_allincall_user(user_obj) is False and user_obj.is_staff is False:
                return Response(status=401)
            page = data["page"]

            audit_trail_objs = CognoAIAuditTrail.objects.all()

            audit_trail_objs = self.apply_date_filters(data, audit_trail_objs)
            audit_trail_objs = self.apply_app_filter(data, audit_trail_objs)

            audit_trail_objs = audit_trail_objs.order_by('-datetime')

            audit_trail_objs, pagination_metadata = self.apply_pagination(audit_trail_objs, page, 20)

            audit_trail_list = self.parse_audit_trail_detail_list(audit_trail_objs)

            response["status"] = 200
            response["message"] = "success"
            response["audit_trail_list"] = audit_trail_list
            response["pagination_metadata"] = pagination_metadata
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAuditTrailAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'AuditTrailApp'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAuditTrail = GetAuditTrailAPI.as_view()


class ExportAuditTrailAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {"status": "500", "status_message": "Internal server Error"}
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            email_id = data["email_id"]
            request_date_type = data['request_date_type']

            user_obj = User.objects.get(username=request.user.username)
            if check_is_allincall_user(user_obj) is False and user_obj.is_staff is False:
                return Response(status=401)

            export_path = None

            if request_date_type == "1":
                # Last day data
                export_path = get_custom_audit_trail_dump(
                    get_requested_data_for_daily(), user_obj, CognoAIAuditTrail)

            elif request_date_type == "2":
                # Last 7 days data
                export_path = get_custom_audit_trail_dump(
                    get_requested_data_for_week(), user_obj, CognoAIAuditTrail)

            elif request_date_type == "3":
                # Last 30 days data
                export_path = get_custom_audit_trail_dump(
                    get_requested_data_for_month(), user_obj, CognoAIAuditTrail)

            elif request_date_type == "4":

                start_date = datetime.strptime(
                    data['start_date'], COMMON_DATE_FORMAT).date()
                end_date = datetime.strptime(
                    data["end_date"], COMMON_DATE_FORMAT).date()

                today_date = datetime.today().date()

                if (today_date - start_date).days > 30:
                    ExportRequest.objects.create(
                        export_type='AuditTrailExport', user=user_obj, start_date=start_date, end_date=end_date,
                        email_id=email_id)
                    response["status"] = 300
                    response["export_path"] = "None"
                    response["export_path_exist"] = False
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)
                else:
                    export_path = get_custom_audit_trail_dump(
                        get_requested_data_custom(start_date, end_date), user_obj, CognoAIAuditTrail)

            if export_path and os.path.exists(export_path):
                response["export_path_exist"] = True
                file_access_management_obj = FileAccessManagement.objects.create(
                    file_path="/" + export_path)
                response["export_path"] = 'audit-trail/download-file/' + \
                                          str(file_access_management_obj.key)
                response["status"] = 200

            response['status'] = 200
            response['message'] = 'success'
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ExportAuditTrailAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'AuditTrailApp'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportAuditTrail = ExportAuditTrailAPI.as_view()


def fileAccess(request, file_key):
    try:
        if request.user.is_authenticated:
            return file_download(file_key, FileAccessManagement)
        return HttpResponse(status=404)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error fileAccess %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'AuditTrailApp'})
    return HttpResponse(status=404)
