NAME_PROCESSOR_VALIDATOR = """def f(x):
    import re
    json_response = {}
    json_response["status_code"]="308"
    json_response["status_message"]="User is talking about something else."
    json_response["child_choice"]=""
    json_response["data"]={}
    try:
        user_messages = str(x)
        strmsg = user_messages.strip()
        if re.match(r'^[a-zA-Z ]+$' , strmsg):
            if len(strmsg.split(" ")) >= 2:
                fname = strmsg.split(" ")[0]
                lname = strmsg.split(" ")[1]
            
                json_response["data"] = {
                "fname" : fname,
                "lname" : lname
                }
                json_response["status_code"]="200"
                json_response["status_message"]="SUCCESS"
            else:
                json_response["data"] = {
                    "fname" : strmsg,
                    "lname" : ""
                    }
                json_response["status_code"]="200"
                json_response["status_message"]="SUCCESS"    
        else:
            json_response["status_code"] = "206"
            json_response["status_message"] = "REDIRECT"
        
        return json_response
    except Exception:
        return json_response"""

MOBILE_NUMBER_VALIDATOR = """def f(x):
    json_response = {}
    json_response["status_code"]="308"
    json_response["status_message"]="User is talking about something else."
    json_response["child_choice"]=""
    json_response["data"]={}
    try:
        user_message = x.encode("ascii", errors="ignore").decode("ascii")
        user_message = user_message.lower().strip()

        b = ""
        for i in user_message:
            if i in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]:
                b += i
        mobile_number = b
        
        if len(str(mobile_number))==10:
            json_response["status_code"]="200"
            json_response["status_message"]="SUCCESS"
            json_response["child_choice"]=""
            json_response["data"]={
                "MobileNumber":mobile_number
            }
        return json_response
    except Exception:
        return json_response"""

EMAIL_VALIDATOR = """def f(x):
    import re
    json_response = {}
    json_response["status_code"]="500"
    json_response["status_message"]="Internal Server Error"
    json_response["child_choice"]=""
    json_response["data"]={}
    try:
#        user_message = str(x.encode("ascii", errors="ignore"))
        regex = '^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$'
#        json_response["abc"] = re.search(regex,str(x))
        if(re.search(regex,str(x).strip())):
            json_response["status_code"]="200"
            json_response["status_message"]="SUCCESS"
        else:
            json_response["status_code"]="206"
            json_response["status_message"]="REDIRECT"
        json_response["child_choice"]=""
        json_response["data"]={"EmailID":user_message}
        return json_response
    except Exception:
        return json_response
        
        
"""


FOUR_DIGIT_OTP_VALIDATOR = """def f(x):
    json_response = {}
    json_response["status_code"]="206"
    json_response["status_message"]="RE-Question"
    json_response["child_choice"]=""
    json_response["data"]={}
    try:
        user_message = x.encode("ascii", errors="ignore").decode("ascii")
        user_message = user_message.lower()

        if len(str(user_message).strip())==4:
            json_response["status_code"]="200"
            json_response["status_message"]="SUCCESS"
            json_response["child_choice"]=""
        return json_response
    except Exception:
        return json_response"""

SIX_DIGIT_OTP_VALIDATOR = """def f(x):
    json_response = {}
    json_response["status_code"]="206"
    json_response["status_message"]="RE-Question"
    json_response["child_choice"]=""
    json_response["data"]={}
    try:
        user_message = x.encode("ascii", errors="ignore").decode("ascii")
        user_message = user_message.lower()

        if len(str(user_message).strip())==6:
            json_response["status_code"]="200"
            json_response["status_message"]="SUCCESS"
            json_response["child_choice"]=""
        return json_response
    except Exception:
        return json_response"""


PAN_VALIDATOR = """def f(x):
    import re
    json_response = {}
    json_response["status_code"]="500"
    json_response["status_message"]="Internal Server Error"
    json_response["child_choice"]=""
    json_response["data"]={}
    try:
        user_message = x.encode("ascii", errors="ignore").decode("ascii")
        user_message = user_message.lower()
        
        if not bool(re.match("[a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z][0-9][0-9][0-9][0-9][a-zA-Z]$", user_message.strip())):
            json_response["status_code"]="206"
            json_response["status_message"]="REDIRECT"
        else:
            json_response["status_code"]="200"
            json_response["status_message"]="SUCCESS"
        json_response["child_choice"]=""
        # json_response["data"]={"EmailID":user_message}
        return json_response
    except Exception:
        return json_response"""

YES_NO_VALIDATOR = """def f(x):
    json_response = {}
    json_response["status_code"]="500"
    json_response["status_message"]="Internal Server Error"
    json_response["child_choice"]=""
    json_response["data"]={}
    try:
        user_message = x.encode("ascii", errors="ignore").decode("ascii")
        user_message = user_message.lower().strip()
        
        if str(user_message)=="yes":
            json_response["status_code"]="200"
            json_response["status_message"]="SUCCESS"
            json_response["child_choice"]="yes"
            json_response["data"]={
            }
        elif str(user_message)=="no":
            json_response["status_code"]="200"
            json_response["status_message"]="SUCCESS"
            json_response["child_choice"]="no"
            json_response["data"]={
            }
        else:
            json_response["status_code"]="206"
            json_response["status_message"]="SUCCESS"
            json_response["child_choice"]="no"
            json_response["data"]={}
        return json_response
    except Exception:
        return json_response"""

LOAD_AMOUNT_VALIDATOR = """def f(x):
    json_response = {}
    json_response["status_code"]="500"
    json_response["status_message"]="Internal Server Error"
    json_response["child_choice"]=""
    json_response["data"]={}
    try:
        user_message = x.encode("ascii", errors="ignore").decode("ascii")
        amount = user_message.strip().lower()

        try:
            float(amount)
        except Exception:
            json_response["status_code"]="308"
            json_response["status_message"]="User is talking about something else"
            json_response["child_choice"]=""
            json_response["data"]={}
            return json_response

        if float(amount)>=50000 and float(amount)<=649000:
            json_response["status_code"]="200"
            json_response["status_message"]="SUCCESS"
            json_response["child_choice"]="Next"
            json_response["data"]={
                "InstaLoanAmount":float(amount)
            }
        else:
            json_response["status_code"]="206"
            json_response["status_message"]="SUCCESS"
            json_response["child_choice"]="Next"
            json_response["data"]={}
        return json_response
    except Exception:
        return json_response"""


TENURE_VALIDATOR = """def f(x):
    json_response = {}
    json_response["status_code"]="500"
    json_response["status_message"]="Internal Server Error"
    json_response["child_choice"]=""
    json_response["data"]={}
    try:
        user_message = str(x.encode("ascii", errors="ignore").decode("ascii"))
        tenure = user_message.strip().lower()

        try:
            int(tenure)
        except Exception:
            json_response["status_code"]="308"
            json_response["status_message"]="User is talking about something else"
            json_response["child_choice"]=""
            json_response["data"]={}
            return json_response

        if int(tenure)>=12 and int(tenure)<=36:
            json_response["status_code"]="200"
            json_response["status_message"]="SUCCESS"
            json_response["child_choice"]="Next"
            json_response["data"]={
                "InstaLoanTenure":int(tenure)
            }
        else:
            json_response["status_code"]="206"
            json_response["status_message"]="SUCCESS"
            json_response["child_choice"]="Next"
            json_response["data"]={}
        return json_response
    except Exception:
        return json_response"""

DATE_VALIDATOR = """def f(x):
    json_response = {}
    json_response["status_code"]="308"
    json_response["status_message"]="User is talking about something else."
    json_response["child_choice"]=""
    json_response["data"]={}
    try:
        user_message = x.encode("ascii", errors="ignore").decode("ascii")
        user_message = user_message.lower()
        json_response["status_code"]="200"
        json_response["status_message"]="SUCCESS"
        json_response["child_choice"]=""
        json_response["data"]={
                "DOB":user_message
            }
        return json_response
    except Exception:
        return json_response"""

POLICY_NUMBER_VALIDATOR = """def f(x):
    json_response = {}
    json_response["status_code"]="308"
    json_response["status_message"]="User is talking about something else."
    json_response["child_choice"]=""
    json_response["data"]={}
    try:
        user_message = x.encode("ascii", errors="ignore").decode("ascii")
        user_message = user_message.lower()
        flag=0
        wl=""
        policy_number = user_message
        for word in user_message:
            if word in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]:
                wl += word
                print(wl)
        print(user_message.split())
        if "11" in user_message.split():
            if len(wl)==13:
                flag = 1
                policy_number = wl
        else:
            if len(wl)==11:
                flag = 1
                policy_number = wl
        
        print(flag)
        if flag==1:
            json_response["status_code"]="200"
            json_response["status_message"]="SUCCESS"
            json_response["child_choice"]=""
            json_response["data"]={
                "PolicyNumber":policy_number
            }
        elif "update" in user_message or "mobile" in user_message or "phone" in user_message:
            json_response["status_code"]="308"
            # json_response["status_message"]="Re-Question"
        else:
            json_response["status_code"]="206"
            json_response["status_message"]="Re-Question"
        return json_response
    except Exception:
        return json_response"""


IFSC_CODE_VALIDATOR = """
import re

def f(x):
    json_response = {}
    json_response["status_code"]="308"
    json_response["status_message"]="User is talking about something else."
    json_response["child_choice"]=""
    json_response["data"]={}
    try:
        user_message = x.encode("ascii", errors="ignore").decode("ascii")
        user_message = user_message.lower().strip()

        if not bool(re.match("[a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z][0][0-9][0-9][0-9][0-9][0-9][0-9]$", user_message)):
            json_response["status_code"]="206"
            json_response["status_message"]="REDIRECT"
        else:
            json_response["status_code"]="200"
            json_response["status_message"]="SUCCESS"

        json_response["child_choice"]=""
        return json_response
    except Exception as e:
        json_response["status_message"] = str(e)
        return json_response
"""


CREDIT_CARD_VALIDATOR = """def f(x):
    json_response = {}
    json_response["status_code"]="308"
    json_response["status_message"]="User is talking about something else."
    json_response["child_choice"]=""
    json_response["data"]={}
    try:
        def sum_digits(digit):
            if digit < 10:
                return digit
            else:
                sum = (digit % 10) + (digit // 10)
                return sum


        def validate(cc_num):
            cc_num = cc_num[::-1]
            cc_num = [int(x) for x in cc_num]
            doubled_second_digit_list = list()
            digits = list(enumerate(cc_num, start=1))
            for index, digit in digits:
                if index % 2 == 0:
                    doubled_second_digit_list.append(digit * 2)
                else:
                    doubled_second_digit_list.append(digit)

            doubled_second_digit_list = [sum_digits(x) for x in doubled_second_digit_list]
            sum_of_digits = sum(doubled_second_digit_list)
            return sum_of_digits % 10 == 0

        user_message = x.encode("ascii", errors="ignore").decode("ascii")
        user_message = user_message.strip()

        if validate(str(user_message)):
            json_response["status_code"]="200"
            json_response["status_message"]="SUCCESS"
            json_response["child_choice"]=""
            json_response["data"]={
                "CardNumber":user_message
            }
        return json_response
    except Exception:
        return json_response
"""


DEFAULT_POST_PROCESSOR_LIST = [{
    "name": "Name Validator",
    "processor": NAME_PROCESSOR_VALIDATOR,
    "processor_lang": "1"
}, {
    "name": "Mobile Number Validator",
    "processor": MOBILE_NUMBER_VALIDATOR,
    "processor_lang": "1"
}, {
    "name": "Email Validator",
    "processor": EMAIL_VALIDATOR,
    "processor_lang": "1"
}, {
    "name": "4 digit OTP Validator",
    "processor": FOUR_DIGIT_OTP_VALIDATOR,
    "processor_lang": "1"
}, {
    "name": "6 digit OTP Validator",
    "processor": SIX_DIGIT_OTP_VALIDATOR,
    "processor_lang": "1"
}, {
    "name": "PAN Validator",
    "processor": PAN_VALIDATOR,
    "processor_lang": "1"
}, {
    "name": "Yes No Validator",
    "processor": YES_NO_VALIDATOR,
    "processor_lang": "1"
}, {
    "name": "Loan Amount Validator",
    "processor": LOAD_AMOUNT_VALIDATOR,
    "processor_lang": "1"
}, {
    "name": "Tenure Validator",
    "processor": TENURE_VALIDATOR,
    "processor_lang": "1"
}, {
    "name": "Date Validator",
    "processor": DATE_VALIDATOR,
    "processor_lang": "1"
}, {
    "name": "Policy Number Validator",
    "processor": POLICY_NUMBER_VALIDATOR,
    "processor_lang": "1"
}, {
    "name": "IFSC Code Validator",
    "processor": IFSC_CODE_VALIDATOR,
    "processor_lang": "1"
}, {
    "name": "Credit Card Validator", 
    "processor": CREDIT_CARD_VALIDATOR, 
    "processor_lang": "1"
}]
