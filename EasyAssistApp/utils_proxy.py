import sys
import re
import logging
from django import forms
import threading
from EasyAssistApp.send_email import send_cobrowse_proxy_drop_link_over_email

from django.conf import settings
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def is_static_file_based_on_url(url):
    try:
        static_files_extension_list = [
            "js", "css", "jpg", "jpeg", "png", "gif", "ttf", "woff", "woff2", "map", "svg"]
        url_extension = url.split("?")[0].split(".")[-1]
        if url_extension.lower() in static_files_extension_list:
            return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            "In is_static_file_based_on_url: %s at %s",
            str(e),
            str(exc_tb.tb_lineno),
            extra={"AppName": "EasyAssist"},
        )
        pass
    return False


def get_origin_from_url(curr_url):
    try:
        curr_url = urlparse(curr_url)
        return curr_url.scheme + "://" + curr_url.netloc
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            "In get_origin_from_url: %s at %s",
            str(e),
            str(exc_tb.tb_lineno),
            extra={"AppName": "EasyAssist"},
        )
    return curr_url


def is_url_valid(url):
    try:
        regex = re.compile(
            r"^(?:http|ftp)s?://"  # http:// or https://
            # domain
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
            r"localhost|"  # localhost
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        if re.match(regex, url) is not None:
            return True
        else:
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            "In is_url_valid: %s at %s",
            str(e),
            str(exc_tb.tb_lineno),
            extra={"AppName": "EasyAssist"},
        )
        return False


"""
The below function is responsible to remove excess "/" from the sent url_path.
Example: 
Input - "///dev//dir///abc.js"
Output - "/dev/der/abc.js"
"""


def remove_excess_forward_slash(input_url):
    try:
        excess_forward_slash_regex = r"/+"
        cleaned_str = re.sub(excess_forward_slash_regex, "/", input_url)
        return cleaned_str
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            "In remove_excess_forward_slash: %s at %s",
            str(e),
            str(exc_tb.tb_lineno),
            extra={"AppName": "EasyAssist"},
        )
        return input_url


def get_absolute_link(active_url, url):
    try:
        if not len(url):
            logger.info("Proxy get_absolute_link url len in 0", extra={'AppName': 'EasyAssist'})
            return active_url + "/"

        # For image data
        if "data:" in url:
            logger.info("Proxy get_absolute_link data: case tiggered", extra={'AppName': 'EasyAssist'})
            return url.strip()

        """
        Preprocessing of the URL path received.
        The if condition handles the case when we have a URL like
        "//cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.3.0/css/datepicker.css"
        Here we do not want to remove the initial "//" as we need to handle the above in 
        Case 2 below.
        """
        if url[:2] != "//":
            url = remove_excess_forward_slash(url)
            logger.info("Proxy get_absolute_link after removing excess slash === " + url, extra={'AppName': 'EasyAssist'})
        
        # case 1
        # 01
        # link in form
        # site link =  https://www.esic.in/EmployeePortal/ABVKYEligibility.aspx
        # href="App_Themes/E_login/images/favicon.png"
        # should return https://www.esic.in/EmployeePortal/App_Themes/E_login/images/favicon.png
        # 02
        # link in form
        # site link = https://www.esic.in/ESICInsurance1/ESICInsurancePortal/PortalLogin.aspx
        # href="App_Themes/vendor/bootstrap/css/bootstrap.min.css"
        # should return  https://www.esic.in/ESICInsurance1/ESICInsurancePortal/App_Themes/vendor/bootstrap/css/bootstrap.min.css

        url_obj = urlparse(active_url)
        # urlparse("https://www.esic.in/EmployeePortal/ABVKYEligibility.aspx")
        # ParseResult(scheme='https', netloc='www.esic.in', path='/EmployeePortal/ABVKYEligibility.aspx', params='', query='', fragment='')

        if url[:4].lower() != "http" and (url[0].lower() not in ["/", ".", "//"]):
            new_url = f'{url_obj.scheme}://{url_obj.netloc}/{"/".join(url_obj.path.split("/")[:-1])}/'
            if new_url[-2:] == "//":
                new_url = new_url[:-1]
            logger.info("Proxy get_absolute_link case 1 triggered", extra={'AppName': 'EasyAssist'})
            return (new_url + url).strip()

        # case 2
        # 01
        # link in form
        # site link =  https://services.gst.gov.in/services/grievance
        # href="//static.gst.gov.in/uiassets/css/app1.1.css"
        # should return https://static.gst.gov.in/uiassets/css/app1.1.css

        if len(url) > 1 and url[:2] in "//":
            new_url = f"{url_obj.scheme}:"
            logger.info("Proxy get_absolute_link case 2 triggered", extra={'AppName': 'EasyAssist'})
            return (new_url + url).strip()

        # case 3
        # 01
        # link in form
        # site link =  https://unifiedportal-emp.epfindia.gov.in/epfo/
        # href="/epfo/styles/index-epfo-copper.css"
        # should return https://unifiedportal-emp.epfindia.gov.in/epfo/styles/index-epfo-copper.css
        # 02
        # site link =  https://assamegras.gov.in/challan/views/frmSignUp.php
        # base_url = 'href="../../Design/css/internalpagestyles.css"'
        # should return https://assamegras.gov.in/Design/css/internalpagestyles.css
        if url[0] in ["/", "."]:
            if url[0] == ".":
                url = url.replace("../../", "/")
                url = url.replace("././", "/")
                url = url.replace("../", "/")
                url = url.replace("./", "/")
            new_url = f"{url_obj.scheme}://{url_obj.netloc}"
            logger.info("Proxy get_absolute_link case 3 triggered", extra={'AppName': 'EasyAssist'})
            return (new_url + url).strip()

        """
        This handles the case where the incoming URL from the page-render URL is 
        a complete valid URL. In the below function we just remove the extra "/" 
        and then return the URL.

        This would mostly be the most frequently running condition.
        """
        # if is_url_valid(url):
        #     url_path_obj = urlparse(url)
        #     url_to_be_formatted = url
        #     if url_path_obj.scheme in url:
        #         url_to_be_formatted = url.replace(url_path_obj.scheme + "://", "")
        #     # logger.info("URL to be formatted = "+url_to_be_formatted, extra={'AppName': 'EasyAssist'})
        #     # TODO find a better way for replacements of multiple "/"
        #     url_to_be_formatted = url_to_be_formatted.replace("///", "/")
        #     url_to_be_formatted = url_to_be_formatted.replace("//", "/")
        #     url = url_path_obj.scheme + "://" + url_to_be_formatted
        #     return url.strip()

    except:
        pass
    logger.info("Proxy get_absolute_link no case triggered", extra={'AppName': 'EasyAssist'})
    return url.strip()


def process_request_content(content, content_type, proxy_key, current_page_url):
    try:
        base_url = f"{settings.EASYCHAT_HOST_URL}/easy-assist/cognoai-cobrowse/page-render/{proxy_key}/{current_page_url}/"
        try:
            content = content.decode('utf-8')
        except:
            return content

        if "text/html" in content_type:

            content = re.sub(r"(?:(href=['\"])(../..))", r"\1" + '', content)
            content = re.sub(r"(?:(src=['\"])(../..))", r"\1" + '', content)
            content = re.sub(r"(?:(content=['\"])(../..))", r"\1" + '', content)
            content = re.sub(r"(?:(action=['\"])(../..))", r"\1" + '', content)

            regex_href = r"(href=[\'\"])(http)?"
            content = re.sub(regex_href, r"\1" + base_url + r"\2", content)

            regex_href = r"(content=[\'\"])(http)"
            content = re.sub(regex_href, r"\1" + base_url + r"\2", content)

            regex_action = r"(action=[\'\"])(http)?"
            content = re.sub(regex_action, r"\1" + base_url + r"\2", content)

            regex_src = r"(src\s*=\s*[\'\"])([http])?"
            content = re.sub(regex_src, r"\1" + base_url + r"\2", content)

            if base_url + "data:" in content:
                content = content.replace(base_url + "data:", "data:")

            regex_srcset = r"(srcset=[\'\"])(http)?"
            content = re.sub(regex_srcset, r"\1" + base_url + r"\2", content)

            """
            This regex is responsible for removing the target="_blank" code 
            from the content so that opening of URLs in new tabs can be prevented.
            """
            regex_target = r"target=['\"]_blank['\"]"
            content = re.sub(regex_target, "", content)
            
            added_js = '<base href="' + base_url + '"/>'
            content = content.replace("</head>", added_js + "</head>", 1)

        if "css" in content_type:
            content = content.replace("url('/", "url('" + base_url)
            content = content.replace("url(/", "url(" + base_url)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            "In process_request_content: %s at %s",
            str(e),
            str(exc_tb.tb_lineno),
            extra={"AppName": "EasyAssist"},
        )
    finally:
        return content


def email_proxy_drop_link(client_page_link, active_agent, customer_email_id, generated_link):
    try:
        form_obj = forms.URLField()
        try:
            form_obj.clean(client_page_link)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error generate_proxy_drop_link %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return None

        if customer_email_id != "":
            agent_username = str(active_agent.user.username)
            thread = threading.Thread(target=send_cobrowse_proxy_drop_link_over_email, args=(
                customer_email_id, agent_username, generated_link), daemon=True)
            thread.start()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error generate_proxy_drop_link %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return None
