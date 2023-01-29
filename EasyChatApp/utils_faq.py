from datetime import datetime
from EasyChatApp.utils_validation import EasyChatInputValidation
from bs4 import BeautifulSoup
from xlwt import Workbook
import json
import re
import sys
import requests
import warnings
import logging
from EasyChatApp.utils_paraphrase import make_final_variations
from EasyChatApp.models import EventProgress
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from lxml.html.clean import clean_html
from DeveloperConsoleApp.utils import get_developer_console_settings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

logger = logging.getLogger(__name__)


"""
function: get_content
input params:
    url: url of website

return html content of that url
if advanced_faq_extraction is enabled, then selenium is used to get page html
"""


def get_content(url):
    try:
        console_config_obj = get_developer_console_settings()
        if console_config_obj.advanced_faq_extraction:
            try:
                options = webdriver.ChromeOptions()
                user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
                options.add_argument('user-agent={0}'.format(user_agent))
                options.add_experimental_option("prefs", {'profile.managed_default_content_settings.javascript': 1})
                options.add_argument('--headless')
                options.add_argument("--enable-javascript")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument('----no-sandbox')
                options.add_argument("--disable-dev-shm-usage")
                driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)

                driver.set_page_load_timeout(30)

                driver.get(url)
                # time.sleep(10) #If any website which renders data after page completes loading, uncomment this time.sleep
                content = driver.execute_script("return document.body.innerHTML")
                driver.quit()
                return content
            except TimeoutException:
                logger.error("Selenium execution took longer than time limit", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                driver.execute_script("window.stop();")
                driver.quit()
                return ""
        else:
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
            }
            resp = requests.get(url=url, headers=headers)
            content = resp.content
            return content
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_content! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return ""


def sentence_cleaner(raw_str):
    raw_str = " ".join(raw_str.split("\n"))
    raw_str = raw_str.strip()
    regex_cleaner = re.compile('^(:?Q?)(:?\.?)(:?\s?)\d+(:?\.?)')
    cleaned_raw_str = re.sub(regex_cleaner, '', raw_str)

    regex_cleaner = re.compile('^Q(:?\.?)(:?\:?) ')
    cleaned_raw_str = re.sub(regex_cleaner, '', cleaned_raw_str)

    regex_cleaner = re.compile('^A(:?\.?)(:?\:?) ')
    cleaned_raw_str = re.sub(regex_cleaner, '', cleaned_raw_str)

    validation_obj = EasyChatInputValidation()

    cleaned_raw_str = validation_obj.remo_html_from_string(cleaned_raw_str)
    cleaned_raw_str = " ".join(cleaned_raw_str.split('\n'))
    cleaned_raw_str = " ".join(cleaned_raw_str.split())
    cleaned_raw_str = cleaned_raw_str.replace("+ -", "")
    cleaned_raw_str = cleaned_raw_str.replace("- +", "")
    cleaned_raw_str = cleaned_raw_str.replace(")", "")
    cleaned_raw_str = cleaned_raw_str.replace("(", "")
    cleaned_raw_str = cleaned_raw_str.strip()
    return cleaned_raw_str


def answer_specific_cleaner(raw_str, validation_obj):
    raw_str = raw_str.strip()
    regex_cleaner = re.compile('^(:?Q?)(:?\.?)(:?\s?)\d+(:?\.?)')
    cleaned_raw_str = re.sub(regex_cleaner, '', raw_str)

    regex_cleaner = re.compile('^Q(:?\.?)(:?\:?) ')
    cleaned_raw_str = re.sub(regex_cleaner, '', cleaned_raw_str)

    regex_cleaner = re.compile('^A(:?\.?)(:?\:?) ')
    cleaned_raw_str = re.sub(regex_cleaner, '', cleaned_raw_str)

    # cleaned_raw_str=cleaned_raw_str.replace
    # regex_cleaner = re.compile('<ul.*?>')
    # cleaned_raw_str = re.sub(regex_cleaner, '###ul###', cleaned_raw_str)

    # cleaned_raw_str = cleaned_raw_str.replace('</ul>', '$$$ul$$$')

    regex_cleaner = re.compile('<li.*?>')
    cleaned_raw_str = re.sub(regex_cleaner, '###li###', cleaned_raw_str)

    cleaned_raw_str = cleaned_raw_str.replace('</li>', '$$$li$$$')
    regex_cleaner = re.compile('<table.*?>')
    cleaned_raw_str = re.sub(regex_cleaner, '###table###', cleaned_raw_str)

    cleaned_raw_str = cleaned_raw_str.replace('</table>', '$$$table$$$')
    regex_cleaner = re.compile('<th.*?>')
    cleaned_raw_str = re.sub(regex_cleaner, '###th###', cleaned_raw_str)

    cleaned_raw_str = cleaned_raw_str.replace('</th>', '$$$th$$$')
    regex_cleaner = re.compile('<td.*?>')
    cleaned_raw_str = re.sub(regex_cleaner, '###td###', cleaned_raw_str)

    cleaned_raw_str = cleaned_raw_str.replace('</td>', '$$$td$$$')
    regex_cleaner = re.compile('<tr.*?>')
    cleaned_raw_str = re.sub(regex_cleaner, '###tr###', cleaned_raw_str)

    cleaned_raw_str = cleaned_raw_str.replace('</tr>', '$$$tr$$$')
    regex_cleaner = re.compile('<a.*?>')
    cleaned_raw_str = re.sub(regex_cleaner, '###a###', cleaned_raw_str)

    cleaned_raw_str = cleaned_raw_str.replace('</a>', '$$$a$$$')
    regex_cleaner = re.compile('<p.*?>')
    cleaned_raw_str = re.sub(regex_cleaner, '###p###', cleaned_raw_str)

    cleaned_raw_str = cleaned_raw_str.replace('</p>', '$$$p$$$')
    regex_cleaner = re.compile('<div.*?>')
    cleaned_raw_str = re.sub(regex_cleaner, '###div###', cleaned_raw_str)

    cleaned_raw_str = cleaned_raw_str.replace('</div>', '$$$div$$$')
    
    cleaned_raw_str = validation_obj.remo_html_from_string(cleaned_raw_str)
    
    regex_cleaner = re.compile('<!--(.|\s|\n)*?-->')
    cleaned_raw_str = re.sub(regex_cleaner, '', cleaned_raw_str)

    # cleaned_raw_str = cleaned_raw_str.replace('###ul###', '<ul>')
    # cleaned_raw_str = cleaned_raw_str.replace('$$$ul$$$', '</ul>')
    last = len(cleaned_raw_str) - 1
    try:
        while cleaned_raw_str[last] != '$':
            cleaned_raw_str = cleaned_raw_str[0:last]
            last = last - 1
    except Exception:
        pass

    cleaned_raw_str = cleaned_raw_str.replace('###li###', '<br>• ')
    cleaned_raw_str = cleaned_raw_str.replace('$$$li$$$', '')
    cleaned_raw_str = strip_end(cleaned_raw_str, '<br>• ')
    cleaned_raw_str = cleaned_raw_str.replace('###table###', '<table>')
    cleaned_raw_str = cleaned_raw_str.replace('$$$table$$$', '</table>')
    cleaned_raw_str = cleaned_raw_str.replace('###th###', '<th>')
    cleaned_raw_str = cleaned_raw_str.replace('$$$th$$$', '</th>')
    cleaned_raw_str = cleaned_raw_str.replace('###td###', '<td>')
    cleaned_raw_str = cleaned_raw_str.replace('$$$td$$$', '</td>')
    cleaned_raw_str = cleaned_raw_str.replace('###tr###', '<tr>')
    cleaned_raw_str = cleaned_raw_str.replace('$$$tr$$$', '</tr>')
    cleaned_raw_str = cleaned_raw_str.replace('###a###', '<a>')
    cleaned_raw_str = cleaned_raw_str.replace('$$$a$$$', '</a>')
    cleaned_raw_str = cleaned_raw_str.replace('###p###', '<p>')
    cleaned_raw_str = cleaned_raw_str.replace('$$$p$$$', '</p>')
    cleaned_raw_str = cleaned_raw_str.replace('###div###', '<div>')
    cleaned_raw_str = cleaned_raw_str.replace('$$$div$$$', '</div>')

    if '?' in cleaned_raw_str:

        strng_arr = cleaned_raw_str.split('?')[0].split('.')
        cleaned_raw_str = '.'.join(strng_arr)

    cleaned_raw_str = cleaned_raw_str.replace("+-", "")
    cleaned_raw_str = cleaned_raw_str.replace("-+", "")
    return cleaned_raw_str


def strip_end(text, suffix):
    if not text.endswith(suffix):
        return text
    return text[:len(text) - len(suffix)]

"""
function: process_html
input params:
    content: html content

return content free of "a" tags
"""


def process_html(content):
    soup = BeautifulSoup(content)
    for a_tag in soup.findAll('a'):
        del a_tag['href']
        del a_tag['id']

    content = str(soup.html)
    return content


"""
function: get_q_score
input params:
    golden_tag: tag which to bec checked
    content:html content

return score depending on which tag contains more question
"""


def get_q_score(golden_tag, content):
    q_score = 0
    try:

        occurences = [m.start() for m in re.finditer(re.escape(golden_tag), str(content))]
        unique_q = {}
        q_repeat_reject = 5
        for iterator in range(len(occurences) - 1):
            temp_soup = BeautifulSoup(content[occurences[iterator]:occurences[iterator + 1]])
            if temp_soup is None or temp_soup.body is None:
                continue
            question = temp_soup.body.contents[0].text.strip()
            if question.strip() == "":
                continue
            answer = ""
            for body_content in temp_soup.body.contents[1:]:
                soup2 = BeautifulSoup(
                    str(body_content.encode('ascii', errors='ignore').decode("ascii")))
                answer += str(soup2.get_text().encode('ascii',
                                                      errors='ignore').decode("ascii")) + " "
            if question not in unique_q and ("?" in question or question.lower().startswith("i ")) and len(question.split()) > 2 and answer.strip() != "":
                q_score += 1
                unique_q[question] = 0
            if question not in unique_q:
                unique_q[question] = 0
            unique_q[question] += 1
            if unique_q[question] > q_repeat_reject:
                return 0
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_q_score! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return q_score


def remove_common_tags(tag_list):
    final_tag_list = []
    for tag in tag_list:
        include_in_list = True
        for tag1 in tag_list:
            if tag == tag1:
                continue
            if tag1.get_text() in tag.get_text():
                include_in_list = False
                break
        if include_in_list:
            final_tag_list.append(tag)
    return final_tag_list, len(final_tag_list)

"""
function: get_golden_tag
input params:
    content:html content

return golden tag which has maximum q_score
"""

"""
function: get_golden_tag
input params:
    content:html content
return golden tag which has maximum q_score
"""


def get_golden_tag_mode1(content):
    try:
        left_angular = content.split("<")
        golden_tag = ""
        max_score = 0
        tag_dict = {}
        for la in left_angular[1:]:
            right_angular = la.split(">")
            ra = right_angular[0]
            tag = "<" + ra + ">"
            if "/" not in tag and tag not in tag_dict:
                tag_dict[tag] = 1
                q_score = get_q_score(tag, content)
                if q_score > max_score:
                    max_score = q_score
                    golden_tag = tag

        logger.info("Golden TAG: %s", str(golden_tag), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return golden_tag
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_golden_tag_mode1 %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: get_golden_tag
input params:
    content:html content
    golden_tag: detected tag with maxm q_score
saves qustion answer pair excel from given html content
and returns list of qustions and corresponding answers
"""


def extract_questions_mode1(content, golden_tag):
    questions = []
    answers = []
    try:
        logger.info("inside extract_ques", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        occurences = [m.start() for m in re.finditer(re.escape(golden_tag), str(content))]
        logger.info("before for loop", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        
        validation_obj = EasyChatInputValidation()

        for iterator in range(len(occurences) - 1):
            temp_soup = BeautifulSoup(content[occurences[iterator]:occurences[iterator + 1]])
            if temp_soup is None or temp_soup.body is None:
                continue
            question = temp_soup.body.contents[0].text.strip()
            answer = ""
            for body_content in temp_soup.body.contents[1:]:
                soup2 = BeautifulSoup(
                    str(body_content.encode('ascii', errors='ignore').decode("ascii")))
                answer += str(soup2.encode('ascii',
                                           errors='ignore').decode("ascii")) + " "
            # question = " ".join(question.split())
            if (len(question.split(" ")) > 100 or "?" not in question) and not question.lower().startswith("i "):
                continue
            
            answer = answer_specific_cleaner(answer, validation_obj)
            if validation_obj.remo_html_from_string(answer).strip() == "":
                continue
            
            if len(answer.split(" ")) > 300:
                continue
            
            questions.append(sentence_cleaner(question))
            answers.append(answer)
        logger.info("before write_excel", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        write_excel(questions, answers)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error extract_questions_mode1 %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return questions, answers


def get_golden_tag_mode2(content):
    try:
        soup = BeautifulSoup(content, "html.parser")
        tag_list = list(set([str(tag.name) for tag in soup.find_all()]))
        if 'script' in tag_list:
            tag_list.remove('script')
        q_score_list = []
        for tag in tag_list:
            q_score = 0
            q_tag_list = []
            q_list = []
            for tag_type in soup.find_all(tag):
                if tag_type.get_text().count("?") > 0 and tag_type.get_text().count("?") < 3:
                    consider_tag = True
                    for tag_data in tag_type.find_all(recursive=False):
                        if tag_data.get_text().count("?") > 0 and tag_data.get_text().count("?") < 3:
                            consider_tag = False
                            break
                    if consider_tag and tag_type.get_text() not in q_list:
                        q_score += 1
                        q_tag_list.append(tag_type)
                        q_list.append(tag_type.get_text())
            if q_score > 0:
                q_score_list.append(
                    {'tag': tag, 'score': q_score, 'tag_list': q_tag_list})

        if len(q_score_list) > 1:
            for tag_list in q_score_list:
                tag_list['tag_list'], tag_list['score'] = remove_common_tags(tag_list[
                                                                             'tag_list'])
            q_score_list = sorted(
                q_score_list, key=lambda k: (-k['score']))[0]
        elif len(q_score_list) == 1:
            q_score_list = q_score_list[0]

        logger.info("Golden TAG Details", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return q_score_list
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_golden_tag_mode2 %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: get_golden_tag
input params:
    content:html content
    golden_tag: detected tag with maxm q_score

saves qustion answer pair excel from given html content
and returns list of qustions and corresponding answers
"""


def extract_questions_mode2(content, golden_tag_details):
    questions = []
    answers = []
    try:
        logger.info("inside extract_ques", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        if len(golden_tag_details):
            validation_obj = EasyChatInputValidation()
            tag_list = golden_tag_details['tag_list']
            for iterator in range(len(tag_list) - 1):
                curr_text = tag_list[iterator].get_text()
                question = curr_text.strip()
                question = sentence_cleaner(question)
                current_tag_occurence = str(content).index(
                    str(tag_list[iterator])) + len(str(tag_list[iterator]))
                next_tag_occurence = str(content).index(str(tag_list[iterator + 1]))
                # temp_soup = BeautifulSoup(
                #     content[current_tag_occurence:next_tag_occurence])
                answer = answer_specific_cleaner(
                    content[current_tag_occurence:next_tag_occurence], validation_obj)
                if validation_obj.remo_html_from_string(answer).strip() == "":
                    continue
                if len(question.split(" ")) > 100 or "?" not in question:
                    continue
                questions.append(question)
                answers.append(answer)
            question = tag_list[-1].get_text()
            if len(question.split(" ")) < 100 or "?" in question:
                questions.append(question)
                answers.append('')
        logger.info("before write_excel", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        write_excel(questions, answers)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error extract_questions_mode2 %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return questions, answers


"""
function: extract_faqs
input params:
    url_html:url/html from which FAQs to be extracted

returns json containing question answer pair
"""


def extract_faqs(url_html, user_obj, bot_obj, mode="both"):
    try:
        logger.info("URL_HTML: %s", str(url_html), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        content = ""
        event_obj = EventProgress.objects.create(
            user=user_obj,
            bot=bot_obj,
            event_type='faq_extraction',
        )
        if(len(url_html) > 500):
            content = url_html
        else:
            content = get_content(url_html)
        content = process_html(content)
        
        validation_obj = EasyChatInputValidation()

        if mode == "mode_1":
            golden_tag = get_golden_tag_mode1(content)
            questions, answers = extract_questions_mode1(content, golden_tag)
        elif mode == "mode_2":
            golden_tag_details = get_golden_tag_mode2(content)
            questions, answers = extract_questions_mode2(
                content, golden_tag_details)
        else:
            golden_tag1 = get_golden_tag_mode1(content)
            questions1, answers1 = extract_questions_mode1(
                content, golden_tag1)

            golden_tag_details2 = get_golden_tag_mode2(content)
            questions2, answers2 = extract_questions_mode2(
                content, golden_tag_details2)

            questions = questions2
            answers = answers2
            for iterator in range(len(questions1)):
                if questions1[iterator] not in questions:
                    questions.append(questions1[iterator])
                    answers.append(answers1[iterator])
                else:
                    if answers[questions.index(questions1[iterator])] == "":
                        answers[questions.index(questions1[iterator])] = answers1[iterator]
        json_resp_list = []
        for iterator in range(len(questions)):
            temp_dict = {}
            temp_question = questions[iterator].encode("ascii", errors="ignore")
            temp_question = temp_question.decode("ascii")

            temp_question = sentence_cleaner(temp_question)

            # if len(temp_question.split(" ")) > 100 or "?" not in temp_question:
            #     continue

            temp_answer = answers[iterator]

            if validation_obj.remo_html_from_string(temp_answer).strip() == "":
                continue

            temp_question = clean_html(temp_question)
            temp_answer = clean_html(temp_answer)
            temp_dict["question"] = temp_question
            temp_dict["answer"] = temp_answer
            json_resp_list.append(temp_dict)
    
        event_obj.event_info = json.dumps(json_resp_list)
        event_obj.is_completed = True
        event_obj.event_progress = 100
        event_obj.completed_datetime = datetime.now()
        event_obj.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error extract_faqs! %s %s",
                     str(exc), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: write_excel
input params:
    questions: list of questions
    answers: list answers corresponding to qustion list
saves excel containing qustion & answers pair 
"""


def write_excel(questions, answers):
    try:
        test_wb = Workbook()
        sheet1 = test_wb.add_sheet("Sheet1")
        sheet1.write(0, 0, "Question")
        sheet1.write(0, 1, "Variation")
        sheet1.write(0, 2, "Response")
        row = 1
        for iterator in range(len(questions)):
            sheet1.write(row, 0, questions[iterator])
            temp_str = "$$$".join(make_final_variations(questions[iterator]))
            sheet1.write(row, 1, temp_str)
            sheet1.write(row, 2, answers[iterator])
            row += 1

        filename = "files/FAQs.xls"
        test_wb.save(filename)
        return filename
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error write_excel %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
