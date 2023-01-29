import { has_customer_left_chat } from "./agent/chatbox";
import { get_cobrowsing_info, get_customer_request, get_voip_info } from "./agent/console";

const state = {
    speedMbps: 0,
    internet_iteration: 3,
};

////////////////////  Check if date is valid or not
function change_date_format_original(date)
{
    var dateParts = date.split("-");
    date = dateParts[2]+"-"+dateParts[1]+"-"+dateParts[0];  
    return date.trim();
}
function is_valid_date(date) {
    var date2 = change_date_format_original(date)
    date = new Date(date);
    date2 = new Date(date2);
    var check_date = date instanceof Date && !isNaN(date)
    var check_date2 =date2 instanceof Date && !isNaN(date2)
    return check_date || check_date2;
}

///////////////////////////////////////////////////
/////////////////////////////// Encryption And Decription //////////////////////////

function CustomEncrypt(msgString, key) {
    // msgString is expected to be Utf8 encoded
    var iv = CryptoJS.lib.WordArray.random(16);
    var encrypted = CryptoJS.AES.encrypt(msgString, CryptoJS.enc.Utf8.parse(key), {
        iv: iv,
    });
    var return_value = key;
    return_value += "." + encrypted.toString();
    return_value += "." + CryptoJS.enc.Base64.stringify(iv);
    return return_value;
}

function custom_encrypt(msgString, key) {
    // msgString is expected to be Utf8 encoded
    var iv = CryptoJS.lib.WordArray.random(16);
    var encrypted = CryptoJS.AES.encrypt(msgString, CryptoJS.enc.Utf8.parse(key), {
        iv: iv,
    });
    var return_value = key;
    return_value += "." + encrypted.toString();
    return_value += "." + CryptoJS.enc.Base64.stringify(iv);

    return return_value;
}

function encrypt_variable(data) {
    let utf_data = CryptoJS.enc.Utf8.parse(data);
    let encoded_data = utf_data;
    let random_key = generate_random_string(16);
    let encrypted_data = custom_encrypt(encoded_data, random_key);

    return encrypted_data;
}

export function generate_random_string(length) {
    var result = "";
    var characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    var charactersLength = characters.length;
    for (var i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}

function generateRandomString(length) {
    var result = "";
    var characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    var charactersLength = characters.length;
    for (var i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}

function EncryptVariable(data) {
    let utf_data = CryptoJS.enc.Utf8.parse(data);
    let encoded_data = utf_data;
    // encoded_data = CryptoJS.enc.Base64.stringify(utf_data);
    let random_key = generateRandomString(16);
    let encrypted_data = CustomEncrypt(encoded_data, random_key);

    return encrypted_data;
}

function custom_decrypt(msg_string) {
    var payload = msg_string.split(".");
    var key = payload[0];
    var decrypted_data = payload[1];
    var decrypted = CryptoJS.AES.decrypt(decrypted_data, CryptoJS.enc.Utf8.parse(key), {
        iv: CryptoJS.enc.Base64.parse(payload[2]),
    });
    return decrypted.toString(CryptoJS.enc.Utf8);
}

////////////////////////////////////////////////////////////////////////////////////

// Custom user session

/*
    get_delayed_date_object
    delay current date by delay_period
    var date_obj = new Date();                                      -> current date
    date_obj.setMinutes( date_obj.getMinutes() + delay_period );    -> delay by delay_period
*/

function get_delayed_date_object(delay_period) {
    var date_obj = new Date();
    date_obj.setMinutes(date_obj.getMinutes() + delay_period);
    return date_obj;
}

/*
    send_session_timeout_request
    is_online_from_this_time                -> delayed by 3 minuits date object
    user_last_activity_time_obj -> user's last activity time
    if(user_last_activity_time_obj > is_online_from_this_time) -> is user active  from last 3 minutes
*/

function set_cookie(cookiename, cookievalue, path = "") {
    if (path == "") {
        document.cookie = cookiename + "=" + cookievalue + ";samesite=strict";
    } else {
        document.cookie = cookiename + "=" + cookievalue + ";path=" + path + ";samesite=strict";
    }
}

function get_cookie(cookiename) {
    var cookie_name = cookiename + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var cookie_array = decodedCookie.split(";");
    for (var i = 0; i < cookie_array.length; i++) {
        var c = cookie_array[i];
        while (c.charAt(0) == " ") {
            c = c.substring(1);
        }
        if (c.indexOf(cookie_name) == 0) {
            return c.substring(cookie_name.length, c.length);
        }
    }
    return "";
}

function getCsrfToken() {
    var CSRF_TOKEN = $('input[name="csrfmiddlewaretoken"]').val();
    return CSRF_TOKEN;
}

function showToast(message, duration) {
    document.getElementById("toast_message").innerHTML = message;
    document.getElementsByClassName("toast-container")[0].style.display = "block";

    $(".toast").toast({
        delay: duration,
    });
    $(".toast").toast("show");

    setTimeout(function () {
        document.getElementsByClassName("toast-container")[0].style.display = "none";
    }, duration);
}

function validate_name(id) {
    var regex = /^[a-zA-Z ]{2,30}$/;
    var ctrl = document.getElementById(id);

    if (regex.test(ctrl.value)) {
        return true;
    } else {
        return false;
    }
}

function validate_phone_number(id) {
    var regex = /[6-9][0-9]{9}/;
    var ctrl = document.getElementById(id);
    if (regex.test(ctrl.value)) {
        return true;
    } else {
        return false;
    }
}

function validate_number_input(event) {
    let isnum = /^\d+$/.test(event.key);
    if (!isnum && event.keyCode != 8 && event.keyCode != 46 && event.keyCode != 37 && event.keyCode != 39) {
        event.preventDefault();
        return false;
    }

    return true;
}

function validate_number_input_value(value, event) {
    let isnum = /^\d+$/.test(value);
    if (!isnum) {
        event.preventDefault();
        return false;
    }

    return true;
}

function validate_email(id) {
    var regex = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
    var ctrl = document.getElementById(id);

    if (regex.test(ctrl.value)) {
        return true;
    } else {
        return false;
    }
}

function validate_username(id) {
    var regex = /^[a-zA-Z0-9]+$/;
    var ctrl = document.getElementById(id);

    if (regex.test(ctrl.value)) {
        return true;
    } else {
        return false;
    }
}

function validate_password(id) {
    var regex = /^\S*$/;
    var ctrl = document.getElementById(id);

    if (regex.test(ctrl.value)) {
        return true;
    } else {
        return false;
    }
}

function validate_keyword(id) {

    var regex = /^[a-zA-Z ]+$/;
    var ctrl = document.getElementById(id);

    if (regex.test(ctrl.value)) {
        return true;
    } else {
        return false;
    }
}

function validate_canned_response(id) {
    
    let response_data = document.getElementById(id);
    let text = String(response_data.value.trim());

    let disallowed_chars = window.DISALLOWED_CHARACTERS;
    let result = [];
    for (let i = 0; i < disallowed_chars.length; i++) {
        if (text.indexOf(disallowed_chars[i]) != -1){
            result.push(disallowed_chars[i]);
        }
            
    }
    if(result.length!=0){
       result.push(false);
    }
    else{
      result.push(true);
    }
    return result;
}

function validate_category_title(id) {
    var regex = /^[a-zA-Z ]+$/;
    var ctrl = document.getElementById(id);

    if (regex.test(ctrl.value)) {
        return true;
    } else {
        return false;
    }
}

function format_time(seconds) {
    let hours = parseInt(seconds / 3600);
    let minutes = parseInt((seconds % 3600) / 60);
    seconds = parseInt(seconds % 60);
    var formatted_time = "";
    if (hours > 0) {
        formatted_time += hours.toString() + " : ";
    }
    if (minutes > 0) {
        if (minutes >= 10) {
            formatted_time += minutes.toString() + " : ";
        } else {
            formatted_time += "0" + minutes.toString() + " : ";
        }
    } else {
        formatted_time += "00 : ";
    }
    if (seconds > 0) {
        if (seconds >= 10) {
            formatted_time += seconds.toString();
        } else {
            formatted_time += "0" + seconds.toString();
        }
    } else {
        formatted_time += "00";
    }
    return formatted_time;
}

function is_mobile() {
    return window.innerWidth < 769;
}

function stripHTML(str) {
    return str.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#039;');
}

function strip_unwanted_characters(html_string) {
    html_string = html_string.replace(/[&\/\\#,+()$~%.'":*?<>{}]/g, '')
    return html_string.replace(/[\\.\*\\\/\"\'<=\-\+,#!]/ig, '');
}

function remove_special_characters_from_str(text) {
    const regex = /:|;|'|"|=|-|\$|\*|%|!|`|~|&|\^|\(|\)|\[|\]|\{|\}|\[|\]|#|<|>|\/|\\/g;
    text = text.replace(regex, "");
    return text;
}

function stripHTMLtags(text) {
    text = String(text.trim());
    
    const regex = /(<([^>]+)>)/ig;
    return text.replace(regex, "");
}

function is_file_supported(name) {
    const allowed_file_extensions = [
        "png",
        "PNG",
        "JPG",
        "JPEG",
        "jpg",
        "jpeg",
        "bmp",
        "gif",
        "tiff",
        "exif",
        "jfif",
        "WEBM",
        "MPG",
        "MP2",
        "MPEG",
        "MPE",
        "MPV",
        "OGG",
        "MP4",
        "M4P",
        "M4V",
        "AVI",
        "WMV",
        "MOV",
        "QT",
        "FLV",
        "SWF",
        "AVCHD",
        "pdf",
        "docs",
        "docx",
        "doc",
        "PDF",
        "txt",
        "TXT",
    ];

    let ext = name.split(".");
    ext = ext[ext.length - 1];

    return (
        allowed_file_extensions.includes(ext) || allowed_file_extensions.includes(ext.toUpperCase())
    );
}

function check_file_size(size) {
    return size <= 5000000;
}

function check_malicious_file(name) {
    let ext = name.split(".");

    // let pattern = /[\\*\\\/\"\'<=\-\+,#!]/ig;

    return ext.length <= 2;
}

function get_file_name(value) {
    if (value.length > 15) {
        let file_ext = value.split(".").pop();
        value = value.slice(0, 10);
        return value + "..." + file_ext;
    } else {
        return value;
    }
}

function get_image_path_html(attached_file_src, img_file = "") {
    let html = "";

    if (img_file != "" && img_file != undefined) {
        html =
            '<img style="cursor:pointer;object-fit:fill;" src="' + img_file + '" onclick="preview_livechat_attachment_image(`'+attached_file_src+'`)">';
    } else {
        html =
            '<a href="' +
            attached_file_src +
            '" target="_blank"><img style="object-fit: none; margin-top: -8%; height: 148px;" src="/static/LiveChatApp/img/image-attachement.svg"></a>';
    }

    return html;
}

function get_video_path_html(attached_file_src) {
    var html =
        '<a href="' +
        attached_file_src +
        '" target="_blank"><video style="width: 100%;height:98%;border-radius: 1em; outline: none;" controls><source src="' +
        window.location.origin +
        attached_file_src +
        '" type="video/mp4"></video></a>';
    // var len = attached_file_src.split("/").length
    // var file_name = get_file_name(attached_file_src.split("/")[len - 1])
    // html += '<span style="color:black; margin: 5px;" class="modal-file">' + file_name + '</span>'
    return html;
}

function get_doc_path_html(attached_file_src) {
    var html =
        '<a href="' +
        attached_file_src +
        '" download><svg width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">\
                <path d="M13 0C20.15 0 26 5.85 26 13C26 20.15 20.15 26 13 26C5.85 26 0 20.15 0 13C0 5.85 5.85 0 13 0ZM7.8 19.5H18.2V16.9H7.8V19.5ZM18.2 10.4H14.95V5.2H11.05V10.4H7.8L13 15.6L18.2 10.4Z" fill="white"></path>\
                </svg></a>';
    var len = attached_file_src.split("/").length;
    // var file_name = get_file_name(attached_file_src.split("/")[len - 1])
    // html += '<span style="color:black; margin: 5px;" class="modal-file">' + file_name + '</span>'
    return html;
}
function get_unread_message_diffrentiator_html(count,session_id){
    let html = ""
    if(count == 1){
        html = "<div id='customer-unread-message-diffrentiator-"+session_id+"' class='livechat-customer-unread-message-diffrentiator-wrapper'> "+ count +" Unread Message </div>"
    }else{
         html = "<div id='customer-unread-message-diffrentiator-"+session_id+"' class='livechat-customer-unread-message-diffrentiator-wrapper'> "+ count +" Unread Messages </div>"
    }
    
    return html;
}
function get_new_chat_indicator_html(session_id){
    const html = '<div id="livechat-newchat-indigator-"'+ session_id +' class="livechat-newchat-indigator">\
                    <svg width="15" height="12" viewBox="0 0 15 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M12.75 0.75H1.75C0.986875 0.75 0.381875 1.36187 0.381875 2.125L0.375 10.375C0.375 11.1381 0.986875 11.75 1.75 11.75H12.75C13.5131 11.75 14.125 11.1381 14.125 10.375V2.125C14.125 1.36187 13.5131 0.75 12.75 0.75ZM4.84375 7.76937C4.84375 \
                        8.065 4.59625 8.3125 4.30063 8.3125C4.12875 8.3125 3.96375 8.23 3.86063 8.08563L2.26562 5.90625V7.88625C2.26562 8.12687 2.07313 8.3125 1.83938 8.3125C1.60563 8.3125 1.40625 8.12 1.40625 7.88625V4.73062C1.40625 4.435 1.65375 4.1875 1.94937 4.1875H1.98375C2.1625 4.1875 2.3275 4.27 2.43062 4.41437L3.98438 6.59375V4.61375C3.98438 4.38 4.17688 4.1875 4.4175 4.1875C4.65812 4.1875 4.84375 4.38 4.84375 4.61375V7.76937ZM8.28125 4.6275C8.28125 4.86813 8.08875 5.05375 7.855 5.05375H6.5625V5.82375H7.855C8.09562 5.82375 8.28125 6.01625 8.28125 6.25V6.25688C8.28125 6.4975 8.08875 6.68313 7.855 6.68313H6.5625V7.44625H7.855C8.09562 7.44625 8.28125 7.63875 8.28125 7.8725C8.28125 8.11312 8.08875 8.29875 7.855 8.29875H6.11563C5.7925 8.29875 5.53125 8.0375 5.53125 7.71438V4.75812C5.53125 4.44875 5.7925 4.1875 6.11563 4.1875H7.855C8.09562 4.1875 8.28125 4.38 8.28125 4.61375V4.6275ZM13.0938 7.625C13.0938 8.00313 12.7844 8.3125 12.4062 8.3125H9.65625C9.27812 8.3125 8.96875 8.00313 8.96875 7.625V4.61375C8.96875 4.38 9.16125 4.1875 9.395 4.1875C9.62875 4.1875 9.82125 4.38 9.82125 4.61375V7.28813H10.5981V5.29437C10.5981 5.05375 10.7906 4.86812 11.0244 4.86812C11.2581 4.86812 11.4506 5.06062 11.4506 5.29437V7.28125H12.2206V4.61375C12.2206 4.37312 12.4131 4.1875 12.6469 4.1875C12.8806 4.1875 13.0731 4.38 13.0731 4.61375V7.625H13.0938Z" fill="' + LIVECHAT_THEME_COLOR + '"/>\
                    </svg>\
                </div>'
    return html;
}

function get_guest_session_indicator_html(session_id){
    const html = '<div id="livechat-newagent-count-indigator-"'+ session_id +' class="livechat-newagent-count-indigator">\
                    <svg width="23" height="19" viewBox="0 0 23 19" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <rect width="23" height="19" rx="3" fill="#0254D7"></rect>\
                        <path d="M5.06348 9.50244V8.39795H7.58984V5.74463H8.75781V8.39795H11.2651V9.50244H8.75781V12.1685H7.58984V9.50244H5.06348ZM12.376 6.30322V5.22412C13.2096 5.22412 13.7957 5.12044 14.1343 4.91309C14.4771 4.70573 14.6484 4.36719 14.6484 3.89746H15.9497V13H14.5596V6.30322H12.376Z" fill="white"></path>\
                    </svg>\
                 </div>'
    return html;
}

export function get_user_group_member_count_html(id, count){
    const html = `<div id="livechat-user-group-count-indicator-${id}" class="livechat-user-group-member-count">
                    +${count}
                 </div>`
    return html;
}

export function get_voip_indicator_html(session_id) {
    let html = ``;

    const voip_customer_info = get_customer_request(session_id);
    const voip_info = get_voip_info();
    if (voip_customer_info && voip_customer_info.has_requested && !has_customer_left_chat(session_id)) {

        if (voip_info.session_id == session_id && voip_info.request_status == 'ongoing') {
            if(voip_info.voip_type == 'video_call'){
                html = `<div class="livechat-voip-call-indigator-div" id="voip_call_indicator-${session_id}">
                            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path fill-rule="evenodd" clip-rule="evenodd" d="M8 2.5C8 1.39543 7.10457 0.5 6 0.5H2C0.895431 0.5 0 1.39543 0 2.5V7.5C0 8.60457 0.895431 9.5 2 9.5H6C7.10457 9.5 8 8.60457 8 7.5V2.5Z" fill="#10B981"/>
                                <path fill-rule="evenodd" clip-rule="evenodd" d="M9 3.33817V6.66185L10.7344 8.30374C11.2125 8.75633 12 8.4174 12 7.75909V2.24093C12 1.58261 11.2125 1.2437 10.7344 1.69628L9 3.33817Z" fill="#10B981"/>
                            </svg>
                        </div>`
            } else {
                html = `<div class="livechat-voip-call-indigator-div" id="voip_call_indicator-${session_id}">
                            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path fill-rule="evenodd" clip-rule="evenodd" d="M8.64881 9.35429C11.6406 12.3453 12.3193 8.88504 14.2242 10.7886C16.0607 12.6246 17.1162 12.9924 14.7894 15.3185C14.498 15.5528 12.6462 18.3707 6.13845 11.8647C-0.370109 5.358 2.44619 3.50433 2.68048 3.21296C5.0129 0.880384 5.3744 1.94204 7.21087 3.778C9.11577 5.68237 5.65699 6.36331 8.64881 9.35429Z" fill="#10B981"></path>
                            </svg>
                        </div>`
            }
            
        } else {
            if(voip_info.voip_type == 'video_call'){
                html = `<div class="livechat-voip-call-indigator-div" id="voip_call_indicator-${session_id}">
                            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path fill-rule="evenodd" clip-rule="evenodd" d="M8 2.5C8 1.39543 7.10457 0.5 6 0.5H2C0.895431 0.5 0 1.39543 0 2.5V7.5C0 8.60457 0.895431 9.5 2 9.5H6C7.10457 9.5 8 8.60457 8 7.5V2.5Z" fill="#F59E0B"/>
                                <path fill-rule="evenodd" clip-rule="evenodd" d="M9 3.33817V6.66185L10.7344 8.30374C11.2125 8.75633 12 8.4174 12 7.75909V2.24093C12 1.58261 11.2125 1.2437 10.7344 1.69628L9 3.33817Z" fill="#F59E0B"/>
                            </svg>
                        </div>`
            } else {
                html = `<div class="livechat-voip-call-indigator-div" id="voip_call_indicator-${session_id}">
                            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path fill-rule="evenodd" clip-rule="evenodd" d="M8.64881 9.35429C11.6406 12.3453 12.3193 8.88504 14.2242 10.7886C16.0607 12.6246 17.1162 12.9924 14.7894 15.3185C14.498 15.5528 12.6462 18.3707 6.13845 11.8647C-0.370109 5.358 2.44619 3.50433 2.68048 3.21296C5.0129 0.880384 5.3744 1.94204 7.21087 3.778C9.11577 5.68237 5.65699 6.36331 8.64881 9.35429Z" fill="#F59E0B"></path>
                            </svg>
                        </div>`
            }
        }

    } else {
        if(voip_info.voip_type == 'video_call'){
            html = `<div class="livechat-voip-call-indigator-div" id="voip_call_indicator-${session_id}" style="display: none;">
                        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" clip-rule="evenodd" d="M8 2.5C8 1.39543 7.10457 0.5 6 0.5H2C0.895431 0.5 0 1.39543 0 2.5V7.5C0 8.60457 0.895431 9.5 2 9.5H6C7.10457 9.5 8 8.60457 8 7.5V2.5Z" fill="#10B981"/>
                            <path fill-rule="evenodd" clip-rule="evenodd" d="M9 3.33817V6.66185L10.7344 8.30374C11.2125 8.75633 12 8.4174 12 7.75909V2.24093C12 1.58261 11.2125 1.2437 10.7344 1.69628L9 3.33817Z" fill="#10B981"/>
                        </svg>
                    </div>`
        } else {
            html = `<div class="livechat-voip-call-indigator-div" id="voip_call_indicator-${session_id}" style="display: none;">
                        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" clip-rule="evenodd" d="M8.64881 9.35429C11.6406 12.3453 12.3193 8.88504 14.2242 10.7886C16.0607 12.6246 17.1162 12.9924 14.7894 15.3185C14.498 15.5528 12.6462 18.3707 6.13845 11.8647C-0.370109 5.358 2.44619 3.50433 2.68048 3.21296C5.0129 0.880384 5.3744 1.94204 7.21087 3.778C9.11577 5.68237 5.65699 6.36331 8.64881 9.35429Z" fill="#10B981"></path>
                        </svg>
                    </div>`
        }
        
    }

    return html;
}

export function get_cobrowsing_indicator_html (session_id) {
    const cobrowsing_info = get_cobrowsing_info();

    let html = ``;
    if (cobrowsing_info.session_id == session_id && cobrowsing_info.status == 'ongoing') {
        html = `<div class="livechat-voip-call-indigator-div" id="voip_call_indicator-${session_id}">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" clip-rule="evenodd" d="M0.5 3.16801C0.5 1.6946 1.6946 0.5 3.168 0.5H12.832C14.3054 0.5 15.5 1.6946 15.5 3.16801V12.832C15.5 14.3054 14.3054 15.5 12.832 15.5H3.168C1.6946 15.5 0.5 14.3054 0.5 12.832V3.16801ZM4.89532 9.89957H9.06216C10.0285 9.89957 10.8121 10.6832 10.8121 11.6496C10.8121 12.6161 10.0285 13.3996 9.06216 13.3996H4.89532C3.92894 13.3996 3.14534 12.6161 3.14534 11.6496C3.14534 10.6832 3.92894 9.89957 4.89532 9.89957ZM3.88053 8.35469C4.04389 8.4168 4.03872 8.64642 3.87275 8.70127L3.45157 8.84049L3.83838 9.23555C3.92201 9.32093 3.91958 9.45703 3.83302 9.53953C3.74639 9.62195 3.60845 9.6196 3.52481 9.53418L3.11223 9.1128L2.88218 9.46931C2.79363 9.6065 2.58139 9.57155 2.5429 9.41337L2.20555 8.02737C2.17043 7.88304 2.31397 7.75911 2.45447 7.81246L3.88053 8.35469ZM8.29522 4.49945H12.462C13.4284 4.49945 14.212 5.28305 14.212 6.24946C14.212 7.21603 13.4284 7.99943 12.462 7.99943H8.29522C7.32881 7.99943 6.5452 7.21603 6.5452 6.24946C6.5452 5.28305 7.32881 4.49945 8.29522 4.49945ZM7.28041 2.95457C7.44374 3.01666 7.43859 3.2463 7.27262 3.30115L6.85145 3.44036L7.23824 3.83543C7.32188 3.92081 7.31945 4.05691 7.23289 4.13941C7.14626 4.22182 7.0083 4.21947 6.92466 4.13405L6.51208 3.71268L6.28205 4.06919C6.19347 4.20638 5.98124 4.17143 5.94277 4.01324L5.60539 2.62723C5.57028 2.4829 5.71384 2.35897 5.85431 2.41234L7.28041 2.95457Z" fill="#10B981"/>
                    </svg>        
                </div>`
    } else {
        html = `<div class="livechat-voip-call-indigator-div" id="voip_call_indicator-${session_id}" style="display: none;">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" clip-rule="evenodd" d="M0.5 3.16801C0.5 1.6946 1.6946 0.5 3.168 0.5H12.832C14.3054 0.5 15.5 1.6946 15.5 3.16801V12.832C15.5 14.3054 14.3054 15.5 12.832 15.5H3.168C1.6946 15.5 0.5 14.3054 0.5 12.832V3.16801ZM4.89532 9.89957H9.06216C10.0285 9.89957 10.8121 10.6832 10.8121 11.6496C10.8121 12.6161 10.0285 13.3996 9.06216 13.3996H4.89532C3.92894 13.3996 3.14534 12.6161 3.14534 11.6496C3.14534 10.6832 3.92894 9.89957 4.89532 9.89957ZM3.88053 8.35469C4.04389 8.4168 4.03872 8.64642 3.87275 8.70127L3.45157 8.84049L3.83838 9.23555C3.92201 9.32093 3.91958 9.45703 3.83302 9.53953C3.74639 9.62195 3.60845 9.6196 3.52481 9.53418L3.11223 9.1128L2.88218 9.46931C2.79363 9.6065 2.58139 9.57155 2.5429 9.41337L2.20555 8.02737C2.17043 7.88304 2.31397 7.75911 2.45447 7.81246L3.88053 8.35469ZM8.29522 4.49945H12.462C13.4284 4.49945 14.212 5.28305 14.212 6.24946C14.212 7.21603 13.4284 7.99943 12.462 7.99943H8.29522C7.32881 7.99943 6.5452 7.21603 6.5452 6.24946C6.5452 5.28305 7.32881 4.49945 8.29522 4.49945ZM7.28041 2.95457C7.44374 3.01666 7.43859 3.2463 7.27262 3.30115L6.85145 3.44036L7.23824 3.83543C7.32188 3.92081 7.31945 4.05691 7.23289 4.13941C7.14626 4.22182 7.0083 4.21947 6.92466 4.13405L6.51208 3.71268L6.28205 4.06919C6.19347 4.20638 5.98124 4.17143 5.94277 4.01324L5.60539 2.62723C5.57028 2.4829 5.71384 2.35897 5.85431 2.41234L7.28041 2.95457Z" fill="#10B981"/>
                    </svg>        
                </div>`
    }

    return html;
}

function get_self_assign_indicator_html(session_id) {
    var html = `<div class="livechat-request-in-queue-chat-indigator-div-${session_id}" data-toggle="tooltip" data-placement="bottom" title="Self-Assigned Chat" data-original-title="Self-Assigned Chat">
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <g clip-path="url(#clip0_48:179)">
                        <g filter="url(#filter0_d_48:179)">
                        <path d="M5.50018 8.75013C5.50018 8.10566 5.68777 7.50501 6.01131 6.99978L2.12639 7.00009C1.50538 7.00009 1.00195 7.50352 1.00195 8.12453V8.58452C1.00195 8.87055 1.09116 9.14946 1.25714 9.38241C2.02822 10.4646 3.2897 11.0007 5.00018 11.0007C5.46584 11.0007 5.89829 10.9609 6.29606 10.8809C5.80029 10.3104 5.50018 9.5653 5.50018 8.75013Z" fill="#0F248C"/>
                        <path d="M7.50018 3.50244C7.50018 2.12173 6.38089 1.00244 5.00018 1.00244C3.61947 1.00244 2.50018 2.12173 2.50018 3.50244C2.50018 4.88315 3.61947 6.00244 5.00018 6.00244C6.38089 6.00244 7.50018 4.88315 7.50018 3.50244Z" fill="#0F248C"/>
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M11.5002 8.75012C11.5002 7.23134 10.269 6.00012 8.75018 6.00012C7.2314 6.00012 6.00018 7.23134 6.00018 8.75012C6.00018 10.2689 7.2314 11.5001 8.75018 11.5001C10.269 11.5001 11.5002 10.2689 11.5002 8.75012ZM8.70525 7.00414L8.75018 7.00011L8.79512 7.00414C8.89717 7.02266 8.97763 7.10313 8.99615 7.20518L9.00018 7.25011L8.99968 8.50012H10.2521L10.2971 8.50415C10.3991 8.52267 10.4796 8.60314 10.4981 8.70518L10.5021 8.75012L10.4981 8.79506C10.4796 8.89711 10.3991 8.97757 10.2971 8.99609L10.2521 9.00012H8.99968L9.00018 10.2501L8.99615 10.2951C8.97763 10.3971 8.89717 10.4776 8.79512 10.4961L8.75018 10.5001L8.70525 10.4961C8.6032 10.4776 8.52273 10.3971 8.50421 10.2951L8.50018 10.2501L8.49968 9.00012H7.25214L7.2072 8.99609C7.10515 8.97757 7.02469 8.89711 7.00617 8.79506L7.00214 8.75012L7.00617 8.70518C7.02469 8.60314 7.10515 8.52267 7.2072 8.50415L7.25214 8.50012H8.49968L8.50018 7.25011L8.50421 7.20518C8.52273 7.10313 8.6032 7.02266 8.70525 7.00414Z" fill="#0F248C"/>
                        </g>
                        <circle cx="8.5" cy="8.5" r="2.5" fill="#0F248C"/>
                        <path d="M8.74634 10.359C8.80653 10.4159 8.90147 10.4133 8.95839 10.3531C9.01532 10.2929 9.01267 10.198 8.95249 10.1411L7.90468 9.15004H10.4494C10.5323 9.15004 10.5994 9.08288 10.5994 9.00004C10.5994 8.9172 10.5323 8.85004 10.4494 8.85004H7.90422L8.95249 7.85859C9.01267 7.80166 9.01532 7.70672 8.95839 7.64654C8.90147 7.58635 8.80653 7.58371 8.74634 7.64063L7.4629 8.85452C7.42964 8.88598 7.40964 8.926 7.4029 8.96776C7.40062 8.97816 7.39941 8.98896 7.39941 9.00004C7.39941 9.01156 7.40071 9.02277 7.40317 9.03355C7.41017 9.07471 7.43008 9.11409 7.4629 9.14513L8.74634 10.359Z" fill="white"/>
                        </g>
                        <defs>
                        <filter id="filter0_d_48:179" x="-26.998" y="-25.9976" width="66.4982" height="66.4976" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
                        <feFlood flood-opacity="0" result="BackgroundImageFix"/>
                        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
                        <feOffset dy="1"/>
                        <feGaussianBlur stdDeviation="14"/>
                        <feComposite in2="hardAlpha" operator="out"/>
                        <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.15 0"/>
                        <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_48:179"/>
                        <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_48:179" result="shape"/>
                        </filter>
                        <clipPath id="clip0_48:179">
                        <rect width="12" height="12" fill="white"/>
                        </clipPath>
                        </defs>
                    </svg>
                </div>`;

    return html;
}

function is_image(attached_file_src) {
    let file_ext = attached_file_src.split(".");
    file_ext = attached_file_src.split(".")[file_ext.length - 1];
    file_ext = file_ext.toUpperCase();

    if (
        ["PNG", "JPG", "JPEG", "SVG", "BMP", "GIF", "TIFF", "EXIF", "JFIF", "JPE"].indexOf(file_ext) != -1
    ) {
        return true;
    }
    return false;
}

function is_video(attached_file_src) {
    let file_ext = attached_file_src.split(".");
    file_ext = attached_file_src.split(".")[file_ext.length - 1];
    file_ext = file_ext.toUpperCase();

    if (
        [
            "WEBM",
            "MPG",
            "MP2",
            "MPEG",
            "MPE",
            "MPV",
            "OGG",
            "MP4",
            "M4P",
            "M4V",
            "AVI",
            "WMV",
            "MOV",
            "QT",
            "FLV",
            "SWF",
            "AVCHD",
        ].indexOf(file_ext) != -1
    ) {
        return true;
    }
    return false;
}

function is_pdf(attached_file_src) {
    let file_ext = attached_file_src.split(".");
    file_ext = attached_file_src.split(".")[file_ext.length - 1];
    file_ext = file_ext.toUpperCase();

    if (["PDF"].indexOf(file_ext) != -1) {
        return true;
    }
    return false;
}

function is_docs(attached_file_src) {
    let file_ext = attached_file_src.split(".");
    file_ext = attached_file_src.split(".")[file_ext.length - 1];
    file_ext = file_ext.toUpperCase();

    if (["DOCS", "DOCX", "DOC"].indexOf(file_ext) != -1) {
        return true;
    }

    return false;
}
function is_txt(attached_file_src) {
    let file_ext = attached_file_src.split(".");
    file_ext = attached_file_src.split(".")[file_ext.length - 1];
    file_ext = file_ext.toUpperCase();

    if (["TXT"].indexOf(file_ext) != -1) {
        return true;
    }

    return false;
}

function is_excel(attached_file_src) {
    let file_ext = attached_file_src.split(".");
    file_ext = attached_file_src.split(".")[file_ext.length - 1];
    file_ext = file_ext.toUpperCase();

    if (["XLS", "XLSX"].indexOf(file_ext) != -1) {
        return true;
    }

    return false;
}

function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

function check_internet_speed() {
    var image_addr = window.location.origin + "/files/private/Pizigani_1367_Chart_1MB.jpg";
    var download_size = 1093957; //bytes

    var start_time = 0,
        end_time = 0;
    var download = new Image();
    download.onload = function () {
        end_time = new Date().getTime();
        if (end_time > start_time) {
            var duration = (end_time - start_time) / 1000;
            var bitsLoaded = download_size * 8;
            var speedBps = (bitsLoaded / duration).toFixed(2);
            var speedKbps = (speedBps / 1024).toFixed(2);
            state.speedMbps = (speedKbps / 1024).toFixed(2);
        }
    };

    start_time = new Date().getTime();
    var cache_buster = "?nnn=" + start_time;
    download.src = image_addr + cache_buster;
}

async function initiate_internet_speed_detection() {
    var total_value = 0;
    for (var i_index = 0; i_index < state.internet_iteration; i_index++) {
        check_internet_speed();
        await sleep(5000);
        total_value = parseInt(total_value) + parseInt(state.speedMbps);
        state.speedMbps = 0;
    }

    let avg_speedMbps = 0;

    if (state.internet_iteration > 0) {
        avg_speedMbps = (total_value / state.internet_iteration).toFixed(2);
    }

    // Adding this console for testing purpose
    console.log("Your average internet speed is " + avg_speedMbps + " Mbps.");
    if (avg_speedMbps < 3) {
        showToast(
            "Looks like your internet connection is weak. Some functionality of this application may not work properly.",
            20000
        );
    }
}

function initialize_page() {
    $("#accordionSidebar a").each(function (index, element) {
        if ($(this).attr("href") == window.location.pathname) {
            $(this).parent().addClass("active");
        }
    });

    if (is_mobile()) {
        try {
            if (window.location.pathname == "/livechat/agent-profile/") {
                var open_profile = localStorage.getItem("open_profile");
                if (open_profile == null || open_profile == "false") {
                    document.getElementById("live-chat-setting-menu").style.display = "block";
                    document.getElementById("live-chat-setting-menu").style.visibility = "visible";
                    document.getElementById("live-chat-setting-content-p").style.display = "none";
                } else {
                    document.getElementById("live-chat-setting-menu").style.display = "none";
                    document.getElementById("live-chat-setting-content-p").style.display = "block";
                    localStorage.setItem("open_profile", false);
                }
            } else {
                document.getElementById("live-chat-setting-menu").style.display = "none";

                try {
                    document.getElementById("live-chat-setting-content").style.display = "block";
                } catch (e) {}

                try {
                    document.getElementById("live-chat-setting-content-c").style.display = "block";
                } catch (e) {}

                try {
                    document.getElementById("live-chat-setting-content-cr").style.display = "block";
                } catch (e) {}

                try {
                    document.getElementById("live-chat-setting-content-gs").style.display = "block";
                } catch (e) {}
            }
        } catch (err) {}
    } else {
        try {
            document.getElementById("live-chat-setting-menu").style.display = "block";
            document.getElementById("live-chat-setting-menu").style.visibility = "visible";
        } catch (err) {}
    }

    var path = window.location.pathname;
    if (path == "/livechat/") {
        set_active("live-chat");
    } else if (path == "/livechat/get-archived-customer-chat/") {
        set_active("archived-customer-chat");
    } else if (path == "/livechat/chat-history/") {
        set_active("chat-history");
    } else if (path == "/livechat/voip-history/") {
        set_active("voip-history");
    } else if (path == "/livechat/vc-history/") {
        set_active("vc-history");
    } else if (path == "/livechat/cobrowsing-history/") {
        set_active("cobrowsing-history");
    } else if (path == "/livechat/manage-agents/") {
        set_active("manage-agents");
    } else if (path == "/livechat/requests-in-queue/") {
        set_active("live-chat-requests-in-queue");
    }  else if (path == "/livechat/followup-leads/") {
        set_active("followup-leads");
    } else if (path == "/livechat/agent-analytics/") {
        set_active("agent-analytics");
    } else if (
        path == "/livechat/analytics/" ||
        path == "/livechat/agent-performance-report/" ||
        path == "/livechat/daily-interaction-count/" ||
        path == "/livechat/hourly-interaction-count/" ||
        path == "/livechat/login-logout-report/" ||
        path == "/livechat/agent-not-ready-report/" ||
        path == "/livechat/missed-chats-report/"||
        path == "/livechat/offline-chats-report/"||
        path == "/livechat/abandoned-chats-report/"
    ) {
        set_active("livechat-reports");
    } else if (
        path == "/livechat/agent-profile/" ||
        path == "/livechat/calender/" ||
        path == "/livechat/canned-response/" ||
        path == "/livechat/agent-settings/"
    ) {
        set_active("settings");
    } else if (path == "/livechat/category/") {
        set_active("admin-settings", "category");
    } else if (path == "/livechat/canned-response/") {
        set_active("admin-settings", "canned");
    } else if (path == "/livechat/chat-escalation/" ||
        path == "/livechat/blacklisted-keyword/" ||
        path == "/livechat/reported-users/" ||
        path == "/livechat/blocked-users/")  
    {
        set_active("admin-settings", "chat-escalation");
    } else if (path == "/livechat/calender/") {
        set_active("admin-settings", "calender");
    } else if (path == "/livechat/manage-only-admin/") {
        set_active("manage-only-admin", "only_admin");
    } else if(path == "/livechat/internal-chat/"){
        set_active("internal-chat","Group Chat");
    } else if(path == "/livechat/email-settings/"){
        set_active("admin-settings","email-settings");
    }
    else {
        set_active("admin-settings", "general-settings");
    }
}

function set_active(id, sub_id) {
    let elem = document.getElementById(id);
    if (elem == null) {
        id = "admin-settings";
        elem = document.getElementById(id);
    }
    if (id == "live-chat") {
        elem.innerHTML =
            '<svg width="18" height="18" viewBox="0 0 18 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                      <path d="M5.60241 1.2C5.5181 1.20013 5.43489 1.22047 5.35895 1.25952C5.283 1.29857 5.21625 1.35533 5.16365 1.4256L1.7323 6H6.74994C6.89913 6 7.0422 6.06321 7.1477 6.17574C7.25319 6.28826 7.31245 6.44087 7.31245 6.6C7.31245 7.07739 7.49025 7.53523 7.80672 7.87279C8.1232 8.21036 8.55243 8.4 9 8.4C9.44757 8.4 9.8768 8.21036 10.1933 7.87279C10.5098 7.53523 10.6875 7.07739 10.6875 6.6C10.6875 6.44087 10.7468 6.28826 10.8523 6.17574C10.9578 6.06321 11.1009 6 11.2501 6H16.2677L12.8364 1.4256C12.7837 1.35533 12.717 1.29857 12.6411 1.25952C12.5651 1.22047 12.4819 1.20013 12.3976 1.2H5.60241ZM4.28612 0.6756C4.44406 0.465004 4.64435 0.294954 4.87218 0.178016C5.10001 0.0610776 5.34957 0.000240515 5.60241 0H12.3976C12.6504 0.000240515 12.9 0.0610776 13.1278 0.178016C13.3557 0.294954 13.5559 0.465004 13.7139 0.6756L17.8765 6.2256C17.9235 6.28813 17.9582 6.36005 17.9787 6.43713C17.9992 6.51421 18.005 6.59489 17.9957 6.6744L17.557 10.4232C17.506 10.8587 17.3076 11.2593 16.9991 11.5496C16.6906 11.84 16.2932 12.0002 15.8818 12H2.11819C1.70675 12.0002 1.30943 11.84 1.00094 11.5496C0.692445 11.2593 0.494035 10.8587 0.443017 10.4232L0.00425497 6.6744C-0.00496607 6.59489 0.000835349 6.51421 0.021317 6.43713C0.0417986 6.36005 0.0765456 6.28813 0.123508 6.2256L4.28612 0.6756Z" fill="' +
            LIVECHAT_THEME_COLOR +
            '"/>\
                                    </svg><span id="sidebarlink" style="color: ' +
            LIVECHAT_THEME_COLOR +
            '">Inbox</span>';
        document.getElementById("live-chat-page-name").innerHTML = "Inbox";
    } else if (id == "archived-customer-chat") {
        elem.innerHTML =
            '<svg width="18" height="16" viewBox="0 0 18 16" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                      <path d="M14.2234 16C15.7264 16 16.875 14.68 16.875 13.1429V4.57143H1.125V13.1429C1.125 14.68 2.27363 16 3.77663 16H14.2234ZM6.1875 6.85714H11.8125C11.9617 6.85714 12.1048 6.91735 12.2102 7.02451C12.3157 7.13167 12.375 7.27702 12.375 7.42857C12.375 7.58012 12.3157 7.72547 12.2102 7.83263C12.1048 7.9398 11.9617 8 11.8125 8H6.1875C6.03832 8 5.89524 7.9398 5.78975 7.83263C5.68426 7.72547 5.625 7.58012 5.625 7.42857C5.625 7.27702 5.68426 7.13167 5.78975 7.02451C5.89524 6.91735 6.03832 6.85714 6.1875 6.85714ZM0.9 0C0.661305 0 0.432387 0.0963262 0.263604 0.267788C0.0948212 0.43925 0 0.671802 0 0.914286L0 2.28571C0 2.5282 0.0948212 2.76075 0.263604 2.93221C0.432387 3.10367 0.661305 3.2 0.9 3.2H17.1C17.3387 3.2 17.5676 3.10367 17.7364 2.93221C17.9052 2.76075 18 2.5282 18 2.28571V0.914286C18 0.671802 17.9052 0.43925 17.7364 0.267788C17.5676 0.0963262 17.3387 0 17.1 0H0.9Z" fill="' +
            LIVECHAT_THEME_COLOR +
            '"/>\
                                    </svg><span id="sidebarlink" style="color: ' +
            LIVECHAT_THEME_COLOR +
            '">Archives</span>';
        document.getElementById("live-chat-page-name").innerHTML = "Archived Chats";
    } else if (id == "settings") {
        elem.innerHTML =
            '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                      <path d="M10.5806 1.18125C10.116 -0.39375 7.884 -0.39375 7.41937 1.18125L7.30687 1.56375C7.23745 1.79954 7.11613 2.01681 6.95182 2.19961C6.7875 2.38242 6.58434 2.52613 6.35726 2.6202C6.13017 2.71427 5.88491 2.75632 5.63945 2.74326C5.394 2.73021 5.15458 2.66238 4.93875 2.54475L4.59 2.3535C3.14663 1.56825 1.56825 3.14663 2.35462 4.58887L2.54475 4.93875C3.0465 5.86125 2.57063 7.00987 1.56375 7.30687L1.18125 7.41937C-0.39375 7.884 -0.39375 10.116 1.18125 10.5806L1.56375 10.6931C1.79954 10.7625 2.01681 10.8839 2.19961 11.0482C2.38242 11.2125 2.52613 11.4157 2.6202 11.6427C2.71427 11.8698 2.75632 12.1151 2.74326 12.3605C2.73021 12.606 2.66238 12.8454 2.54475 13.0612L2.3535 13.41C1.56825 14.8534 3.14663 16.4317 4.58887 15.6454L4.93875 15.4552C5.15458 15.3376 5.394 15.2698 5.63945 15.2567C5.88491 15.2437 6.13017 15.2857 6.35726 15.3798C6.58434 15.4739 6.7875 15.6176 6.95182 15.8004C7.11613 15.9832 7.23745 16.2005 7.30687 16.4362L7.41937 16.8188C7.884 18.3937 10.116 18.3937 10.5806 16.8188L10.6931 16.4362C10.7625 16.2005 10.8839 15.9832 11.0482 15.8004C11.2125 15.6176 11.4157 15.4739 11.6427 15.3798C11.8698 15.2857 12.1151 15.2437 12.3605 15.2567C12.606 15.2698 12.8454 15.3376 13.0612 15.4552L13.41 15.6465C14.8534 16.4317 16.4317 14.8534 15.6454 13.4111L15.4552 13.0612C15.3376 12.8454 15.2698 12.606 15.2567 12.3605C15.2437 12.1151 15.2857 11.8698 15.3798 11.6427C15.4739 11.4157 15.6176 11.2125 15.8004 11.0482C15.9832 10.8839 16.2005 10.7625 16.4362 10.6931L16.8188 10.5806C18.3937 10.116 18.3937 7.884 16.8188 7.41937L16.4362 7.30687C16.2005 7.23745 15.9832 7.11613 15.8004 6.95182C15.6176 6.7875 15.4739 6.58434 15.3798 6.35726C15.2857 6.13017 15.2437 5.88491 15.2567 5.63945C15.2698 5.394 15.3376 5.15458 15.4552 4.93875L15.6465 4.59C16.4317 3.14663 14.8534 1.56825 13.4111 2.35462L13.0612 2.54475C12.8454 2.66238 12.606 2.73021 12.3605 2.74326C12.1151 2.75632 11.8698 2.71427 11.6427 2.6202C11.4157 2.52613 11.2125 2.38242 11.0482 2.19961C10.8839 2.01681 10.7625 1.79954 10.6931 1.56375L10.5806 1.18125ZM9 12.2963C8.12578 12.2963 7.28737 11.949 6.6692 11.3308C6.05103 10.7126 5.70375 9.87422 5.70375 9C5.70375 8.12578 6.05103 7.28737 6.6692 6.6692C7.28737 6.05103 8.12578 5.70375 9 5.70375C9.87392 5.70375 10.712 6.05091 11.33 6.66887C11.948 7.28683 12.2951 8.12495 12.2951 8.99887C12.2951 9.8728 11.948 10.7109 11.33 11.3289C10.712 11.9468 9.87392 12.294 9 12.294V12.2963Z" fill="' +
            LIVECHAT_THEME_COLOR +
            '"/>\
                                    </svg><span id="sidebarlink" style="color: ' +
            LIVECHAT_THEME_COLOR +
            '">Settings</span>';

        if (!is_mobile()) {
            let path_name = window.location.pathname;
            path_name = path_name.split("/")[2];

            document.getElementById("settings-" + path_name).style.fill = LIVECHAT_THEME_COLOR;
            document.getElementById("settings-" + path_name + "-text").style.color =
                LIVECHAT_THEME_COLOR;
            document.getElementById("live-chat-page-name").innerHTML = "Settings";
        }
    } else if (id == "chat-history") {
        elem.innerHTML =
            '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                            <path d="M9.00026 3.38957e-06C10.8152 5.39339e-05 12.5877 0.548816 14.0851 1.57427C15.5826 2.59972 16.735 4.05395 17.3912 5.7461C18.0474 7.43824 18.1766 9.28924 17.762 11.0562C17.3473 12.8231 16.4082 14.4234 15.0678 15.647C13.7274 16.8706 12.0483 17.6604 10.251 17.9126C8.45374 18.1649 6.62216 17.8679 4.99668 17.0606C3.3712 16.2533 2.02777 14.9734 1.1427 13.3889C0.257642 11.8045 -0.127699 9.98941 0.0372572 8.182C0.0461214 8.08391 0.0742206 7.98851 0.11995 7.90128C0.16568 7.81404 0.228145 7.73666 0.303778 7.67356C0.379412 7.61047 0.466732 7.56289 0.560755 7.53353C0.654777 7.50418 0.75366 7.49364 0.851757 7.5025C0.949855 7.51137 1.04525 7.53947 1.13248 7.5852C1.21972 7.63093 1.2971 7.69339 1.3602 7.76902C1.42329 7.84466 1.47088 7.93198 1.50023 8.026C1.52958 8.12002 1.54012 8.21891 1.53126 8.317C1.42838 9.41277 1.56923 10.5177 1.94371 11.5526C2.31818 12.5876 2.91701 13.5268 3.69726 14.303C4.39232 15.0012 5.2188 15.5549 6.12899 15.932C7.03918 16.3091 8.01505 16.5021 9.00026 16.5C10.2787 16.4997 11.5359 16.1727 12.6524 15.5499C13.7689 14.9271 14.7077 14.0292 15.3796 12.9415C16.0514 11.8538 16.4341 10.6124 16.4913 9.33524C16.5484 8.05805 16.2781 6.78746 15.7061 5.64411C15.134 4.50077 14.2792 3.52264 13.2228 2.8026C12.1663 2.08257 10.9434 1.64454 9.67006 1.53011C8.39672 1.41568 7.11527 1.62864 5.9474 2.14878C4.77952 2.66893 3.764 3.47897 2.99726 4.502H5.75326C5.94328 4.50206 6.1262 4.57425 6.26505 4.70398C6.4039 4.8337 6.48833 5.0113 6.50128 5.20088C6.51424 5.39046 6.45474 5.5779 6.33482 5.7253C6.21491 5.87271 6.04351 5.9691 5.85526 5.995L5.75326 6.002H1.25026C1.06902 6.002 0.893915 5.93636 0.757327 5.81724C0.620738 5.69811 0.531906 5.53356 0.507257 5.354L0.500257 5.252V0.752003C0.500315 0.56198 0.572502 0.379063 0.70223 0.240212C0.831958 0.101361 1.00956 0.0169293 1.19914 0.00397735C1.38872 -0.00897464 1.57615 0.0505187 1.72356 0.170436C1.87096 0.290353 1.96736 0.461754 1.99326 0.650003L2.00026 0.752003L1.99926 3.343C2.84236 2.29817 3.90886 1.45554 5.12039 0.877032C6.33193 0.298522 7.65769 -0.00116263 9.00026 3.38957e-06ZM8.25026 4C8.43149 4.00001 8.6066 4.06565 8.74319 4.18477C8.87978 4.30389 8.96861 4.46845 8.99326 4.648L9.00026 4.75V9H11.2503C11.4403 9.00006 11.6232 9.07225 11.762 9.20198C11.9009 9.33171 11.9853 9.5093 11.9983 9.69888C12.0112 9.88847 11.9517 10.0759 11.8318 10.2233C11.7119 10.3707 11.5405 10.4671 11.3523 10.493L11.2503 10.5H8.25026C8.06902 10.5 7.89392 10.4344 7.75733 10.3152C7.62074 10.1961 7.53191 10.0316 7.50726 9.852L7.50026 9.75V4.75C7.50026 4.55109 7.57928 4.36033 7.71993 4.21967C7.86058 4.07902 8.05134 4 8.25026 4Z" fill="' +
            LIVECHAT_THEME_COLOR +
            '"></path>\
                                            </svg><span id="sidebarlink" style="color: ' +
            LIVECHAT_THEME_COLOR +
            '">Chat History</span>';

        document.getElementById("live-chat-page-name").innerHTML = "Chat History";
    } else if (id == "manage-agents") {
        elem.innerHTML =
            '<svg width="18" height="15" viewBox="0 0 18 15" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                            <path d="M7.875 14.125C7.875 14.125 6.75 14.125 6.75 13C6.75 11.875 7.875 8.5 12.375 8.5C16.875 8.5 18 11.875 18 13C18 14.125 16.875 14.125 16.875 14.125H7.875ZM12.375 7.375C13.2701 7.375 14.1286 7.01942 14.7615 6.38649C15.3944 5.75355 15.75 4.89511 15.75 4C15.75 3.10489 15.3944 2.24645 14.7615 1.61351C14.1286 0.980579 13.2701 0.625 12.375 0.625C11.4799 0.625 10.6214 0.980579 9.98851 1.61351C9.35558 2.24645 9 3.10489 9 4C9 4.89511 9.35558 5.75355 9.98851 6.38649C10.6214 7.01942 11.4799 7.375 12.375 7.375Z" fill="' +
            LIVECHAT_THEME_COLOR +
            '"></path>\
                                            <path fill-rule="evenodd" clip-rule="evenodd" d="M5.868 14.125C5.70122 13.7738 5.61805 13.3887 5.625 13C5.625 11.4756 6.39 9.90624 7.803 8.81499C7.09773 8.59768 6.36294 8.49141 5.625 8.49999C1.125 8.49999 0 11.875 0 13C0 14.125 1.125 14.125 1.125 14.125H5.868Z" fill="' +
            LIVECHAT_THEME_COLOR +
            '"></path>\
                                            <path d="M5.0625 7.375C5.80842 7.375 6.52379 7.07868 7.05124 6.55124C7.57868 6.02379 7.875 5.30842 7.875 4.5625C7.875 3.81658 7.57868 3.10121 7.05124 2.57376C6.52379 2.04632 5.80842 1.75 5.0625 1.75C4.31658 1.75 3.60121 2.04632 3.07376 2.57376C2.54632 3.10121 2.25 3.81658 2.25 4.5625C2.25 5.30842 2.54632 6.02379 3.07376 6.55124C3.60121 7.07868 4.31658 7.375 5.0625 7.375Z" fill="' +
            LIVECHAT_THEME_COLOR +
            '"></path>\
                                            </svg><span id="sidebarlink" style="color: ' +
            LIVECHAT_THEME_COLOR +
            '">Manage Users</span>';

        $(elem).parent().addClass("active");
        document.getElementById("live-chat-page-name").innerHTML = "Manage Users";
    } else if (id == "livechat-reports") {
        elem.innerHTML =
            '<svg width="14" height="18" viewBox="0 0 14 18" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                            <path d="M8.45463 0H2.5C1.90326 0 1.33097 0.237053 0.90901 0.65901C0.487053 1.08097 0.25 1.65326 0.25 2.25V15.75C0.25 16.3467 0.487053 16.919 0.90901 17.341C1.33097 17.7629 1.90326 18 2.5 18H11.5C12.0967 18 12.669 17.7629 13.091 17.341C13.5129 16.919 13.75 16.3467 13.75 15.75V5.29537C13.7499 4.99703 13.6314 4.71093 13.4204 4.5L9.25 0.329625C9.03907 0.118632 8.75297 6.37171e-05 8.45463 0V0ZM8.6875 3.9375V1.6875L12.0625 5.0625H9.8125C9.51413 5.0625 9.22798 4.94397 9.017 4.733C8.80603 4.52202 8.6875 4.23587 8.6875 3.9375ZM9.25 15.1875V8.4375C9.25 8.28832 9.30926 8.14524 9.41475 8.03975C9.52024 7.93426 9.66332 7.875 9.8125 7.875H10.9375C11.0867 7.875 11.2298 7.93426 11.3352 8.03975C11.4407 8.14524 11.5 8.28832 11.5 8.4375V15.1875C11.5 15.3367 11.4407 15.4798 11.3352 15.5852C11.2298 15.6907 11.0867 15.75 10.9375 15.75H9.8125C9.66332 15.75 9.52024 15.6907 9.41475 15.5852C9.30926 15.4798 9.25 15.3367 9.25 15.1875ZM6.4375 15.75C6.28832 15.75 6.14524 15.6907 6.03975 15.5852C5.93426 15.4798 5.875 15.3367 5.875 15.1875V10.6875C5.875 10.5383 5.93426 10.3952 6.03975 10.2898C6.14524 10.1843 6.28832 10.125 6.4375 10.125H7.5625C7.71168 10.125 7.85476 10.1843 7.96025 10.2898C8.06574 10.3952 8.125 10.5383 8.125 10.6875V15.1875C8.125 15.3367 8.06574 15.4798 7.96025 15.5852C7.85476 15.6907 7.71168 15.75 7.5625 15.75H6.4375ZM3.0625 15.75C2.91332 15.75 2.77024 15.6907 2.66475 15.5852C2.55926 15.4798 2.5 15.3367 2.5 15.1875V12.9375C2.5 12.7883 2.55926 12.6452 2.66475 12.5398C2.77024 12.4343 2.91332 12.375 3.0625 12.375H4.1875C4.33668 12.375 4.47976 12.4343 4.58525 12.5398C4.69074 12.6452 4.75 12.7883 4.75 12.9375V15.1875C4.75 15.3367 4.69074 15.4798 4.58525 15.5852C4.47976 15.6907 4.33668 15.75 4.1875 15.75H3.0625Z" fill="' +
            LIVECHAT_THEME_COLOR +
            '"></path>\
                                            </svg><span id="sidebarlink" style="color: ' +
            LIVECHAT_THEME_COLOR +
            '">Reports</span>';

        let path_name = window.location.pathname;
        path_name = path_name.split("/")[2];
        let elems = document.getElementsByClassName("reports-" + path_name);

        for (let i = 0; i < elems.length; ++i) {
            try {
                elems[i].style.fill = LIVECHAT_THEME_COLOR;
            } catch (err) {}

            try {
                elems[i].style.color = LIVECHAT_THEME_COLOR;
            } catch (err) {}
        }

        if (path_name == "login-logout-report") {
            document.getElementById("login-logout-report-stroke").style.stroke =
                LIVECHAT_THEME_COLOR;
            document.getElementById("login-logout-report-stroke").style.fill = "white";
        }
        document.getElementById("live-chat-page-name").innerHTML = "Reports";
    } else if (id == "admin-settings") {
        elem.innerHTML =
            '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                            <path d="M10.5806 1.18125C10.116 -0.39375 7.884 -0.39375 7.41937 1.18125L7.30687 1.56375C7.23745 1.79954 7.11613 2.01681 6.95182 2.19961C6.7875 2.38242 6.58434 2.52613 6.35726 2.6202C6.13017 2.71427 5.88491 2.75632 5.63945 2.74326C5.394 2.73021 5.15458 2.66238 4.93875 2.54475L4.59 2.3535C3.14663 1.56825 1.56825 3.14663 2.35462 4.58887L2.54475 4.93875C3.0465 5.86125 2.57063 7.00987 1.56375 7.30687L1.18125 7.41937C-0.39375 7.884 -0.39375 10.116 1.18125 10.5806L1.56375 10.6931C1.79954 10.7625 2.01681 10.8839 2.19961 11.0482C2.38242 11.2125 2.52613 11.4157 2.6202 11.6427C2.71427 11.8698 2.75632 12.1151 2.74326 12.3605C2.73021 12.606 2.66238 12.8454 2.54475 13.0612L2.3535 13.41C1.56825 14.8534 3.14663 16.4317 4.58887 15.6454L4.93875 15.4552C5.15458 15.3376 5.394 15.2698 5.63945 15.2567C5.88491 15.2437 6.13017 15.2857 6.35726 15.3798C6.58434 15.4739 6.7875 15.6176 6.95182 15.8004C7.11613 15.9832 7.23745 16.2005 7.30687 16.4362L7.41937 16.8188C7.884 18.3937 10.116 18.3937 10.5806 16.8188L10.6931 16.4362C10.7625 16.2005 10.8839 15.9832 11.0482 15.8004C11.2125 15.6176 11.4157 15.4739 11.6427 15.3798C11.8698 15.2857 12.1151 15.2437 12.3605 15.2567C12.606 15.2698 12.8454 15.3376 13.0612 15.4552L13.41 15.6465C14.8534 16.4317 16.4317 14.8534 15.6454 13.4111L15.4552 13.0612C15.3376 12.8454 15.2698 12.606 15.2567 12.3605C15.2437 12.1151 15.2857 11.8698 15.3798 11.6427C15.4739 11.4157 15.6176 11.2125 15.8004 11.0482C15.9832 10.8839 16.2005 10.7625 16.4362 10.6931L16.8188 10.5806C18.3937 10.116 18.3937 7.884 16.8188 7.41937L16.4362 7.30687C16.2005 7.23745 15.9832 7.11613 15.8004 6.95182C15.6176 6.7875 15.4739 6.58434 15.3798 6.35726C15.2857 6.13017 15.2437 5.88491 15.2567 5.63945C15.2698 5.394 15.3376 5.15458 15.4552 4.93875L15.6465 4.59C16.4317 3.14663 14.8534 1.56825 13.4111 2.35462L13.0612 2.54475C12.8454 2.66238 12.606 2.73021 12.3605 2.74326C12.1151 2.75632 11.8698 2.71427 11.6427 2.6202C11.4157 2.52613 11.2125 2.38242 11.0482 2.19961C10.8839 2.01681 10.7625 1.79954 10.6931 1.56375L10.5806 1.18125ZM9 12.2963C8.12578 12.2963 7.28737 11.949 6.6692 11.3308C6.05103 10.7126 5.70375 9.87422 5.70375 9C5.70375 8.12578 6.05103 7.28737 6.6692 6.6692C7.28737 6.05103 8.12578 5.70375 9 5.70375C9.87392 5.70375 10.712 6.05091 11.33 6.66887C11.948 7.28683 12.2951 8.12495 12.2951 8.99887C12.2951 9.8728 11.948 10.7109 11.33 11.3289C10.712 11.9468 9.87392 12.294 9 12.294V12.2963Z" fill="' +
            LIVECHAT_THEME_COLOR +
            '"></path>\
                                            </svg><span id="sidebarlink" style="color: ' +
            LIVECHAT_THEME_COLOR +
            '">Settings</span>';
        $(elem).parent().addClass("active");

        let path_name = window.location.pathname;
        path_name = path_name.split("/")[2];
        let elems = document.getElementsByClassName("settings-" + path_name);

        for (let i = 0; i < elems.length; ++i) {
            try {
                elems[i].style.fill = LIVECHAT_THEME_COLOR;
            } catch (err) {}

            try {
                elems[i].style.color = LIVECHAT_THEME_COLOR;
            } catch (err) {}
        }

        if (path_name == "category") {
            document.getElementById("category-settings").innerHTML =
                '<svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                                                        <mask id="path-1-inside-1" fill="white">\
                                                                        <path class="settings-category" d="M5.44444 0H0.777778C0.571498 0 0.373667 0.0819442 0.227806 0.227806C0.0819442 0.373667 0 0.571498 0 0.777778V5.44444C0 5.65072 0.0819442 5.84855 0.227806 5.99442C0.373667 6.14028 0.571498 6.22222 0.777778 6.22222H5.44444C5.65072 6.22222 5.84855 6.14028 5.99442 5.99442C6.14028 5.84855 6.22222 5.65072 6.22222 5.44444V0.777778C6.22222 0.571498 6.14028 0.373667 5.99442 0.227806C5.84855 0.0819442 5.65072 0 5.44444 0ZM4.66667 4.66667H1.55556V1.55556H4.66667V4.66667ZM13.2222 0H8.55556C8.34928 0 8.15145 0.0819442 8.00558 0.227806C7.85972 0.373667 7.77778 0.571498 7.77778 0.777778V5.44444C7.77778 5.65072 7.85972 5.84855 8.00558 5.99442C8.15145 6.14028 8.34928 6.22222 8.55556 6.22222H13.2222C13.4285 6.22222 13.6263 6.14028 13.7722 5.99442C13.9181 5.84855 14 5.65072 14 5.44444V0.777778C14 0.571498 13.9181 0.373667 13.7722 0.227806C13.6263 0.0819442 13.4285 0 13.2222 0ZM12.4444 4.66667H9.33333V1.55556H12.4444V4.66667ZM5.44444 7.77778H0.777778C0.571498 7.77778 0.373667 7.85972 0.227806 8.00558C0.0819442 8.15145 0 8.34928 0 8.55556V13.2222C0 13.4285 0.0819442 13.6263 0.227806 13.7722C0.373667 13.9181 0.571498 14 0.777778 14H5.44444C5.65072 14 5.84855 13.9181 5.99442 13.7722C6.14028 13.6263 6.22222 13.4285 6.22222 13.2222V8.55556C6.22222 8.34928 6.14028 8.15145 5.99442 8.00558C5.84855 7.85972 5.65072 7.77778 5.44444 7.77778ZM4.66667 12.4444H1.55556V9.33333H4.66667V12.4444ZM10.8889 7.77778C9.17311 7.77778 7.77778 9.17311 7.77778 10.8889C7.77778 12.6047 9.17311 14 10.8889 14C12.6047 14 14 12.6047 14 10.8889C14 9.17311 12.6047 7.77778 10.8889 7.77778ZM10.8889 12.4444C10.031 12.4444 9.33333 11.7468 9.33333 10.8889C9.33333 10.031 10.031 9.33333 10.8889 9.33333C11.7468 9.33333 12.4444 10.031 12.4444 10.8889C12.4444 11.7468 11.7468 12.4444 10.8889 12.4444Z"/>\
                                                                        </mask>\
                                                                        <path class="settings-category" id="livechat-category" d="M0.777778 0V-3V0ZM0 0.777778H-3H0ZM0 5.44444H-3H0ZM4.66667 4.66667V7.66667H7.66667V4.66667H4.66667ZM1.55556 4.66667H-1.44444V7.66667H1.55556V4.66667ZM1.55556 1.55556V-1.44444H-1.44444V1.55556H1.55556ZM4.66667 1.55556H7.66667V-1.44444H4.66667V1.55556ZM8.55556 0V-3V0ZM12.4444 4.66667V7.66667H15.4444V4.66667H12.4444ZM9.33333 4.66667H6.33333V7.66667H9.33333V4.66667ZM9.33333 1.55556V-1.44444H6.33333V1.55556H9.33333ZM12.4444 1.55556H15.4444V-1.44444H12.4444V1.55556ZM0 8.55556H-3H0ZM0 13.2222H-3H0ZM4.66667 12.4444V15.4444H7.66667V12.4444H4.66667ZM1.55556 12.4444H-1.44444V15.4444H1.55556V12.4444ZM1.55556 9.33333V6.33333H-1.44444V9.33333H1.55556ZM4.66667 9.33333H7.66667V6.33333H4.66667V9.33333ZM5.44444 -3H0.777778V3H5.44444V-3ZM0.777778 -3C-0.224151 -3 -1.18504 -2.60199 -1.89351 -1.89351L2.34913 2.34913C1.93238 2.76587 1.36715 3 0.777778 3V-3ZM-1.89351 -1.89351C-2.60199 -1.18504 -3 -0.224151 -3 0.777778H3C3 1.36715 2.76587 1.93238 2.34913 2.34913L-1.89351 -1.89351ZM-3 0.777778V5.44444H3V0.777778H-3ZM-3 5.44444C-3 6.44637 -2.60199 7.40727 -1.89351 8.11574L2.34913 3.8731C2.76587 4.28984 3 4.85507 3 5.44444H-3ZM-1.89351 8.11574C-1.18504 8.82421 -0.224153 9.22222 0.777778 9.22222V3.22222C1.36715 3.22222 1.93238 3.45635 2.34913 3.8731L-1.89351 8.11574ZM0.777778 9.22222H5.44444V3.22222H0.777778V9.22222ZM5.44444 9.22222C6.44638 9.22222 7.40727 8.82421 8.11574 8.11574L3.8731 3.8731C4.28984 3.45635 4.85507 3.22222 5.44444 3.22222V9.22222ZM8.11574 8.11574C8.82421 7.40727 9.22222 6.44638 9.22222 5.44444H3.22222C3.22222 4.85507 3.45635 4.28984 3.8731 3.8731L8.11574 8.11574ZM9.22222 5.44444V0.777778H3.22222V5.44444H9.22222ZM9.22222 0.777778C9.22222 -0.224153 8.82421 -1.18504 8.11574 -1.89351L3.8731 2.34913C3.45635 1.93238 3.22222 1.36715 3.22222 0.777778H9.22222ZM8.11574 -1.89351C7.40727 -2.60199 6.44637 -3 5.44444 -3V3C4.85507 3 4.28984 2.76587 3.8731 2.34913L8.11574 -1.89351ZM4.66667 1.66667H1.55556V7.66667H4.66667V1.66667ZM4.55556 4.66667V1.55556H-1.44444V4.66667H4.55556ZM1.55556 4.55556H4.66667V-1.44444H1.55556V4.55556ZM1.66667 1.55556V4.66667H7.66667V1.55556H1.66667ZM13.2222 -3H8.55556V3H13.2222V-3ZM8.55556 -3C7.55363 -3 6.59273 -2.60199 5.88426 -1.89351L10.1269 2.34913C9.71016 2.76587 9.14493 3 8.55556 3V-3ZM5.88426 -1.89351C5.17579 -1.18504 4.77778 -0.224153 4.77778 0.777778H10.7778C10.7778 1.36715 10.5437 1.93238 10.1269 2.34913L5.88426 -1.89351ZM4.77778 0.777778V5.44444H10.7778V0.777778H4.77778ZM4.77778 5.44444C4.77778 6.44638 5.17579 7.40727 5.88426 8.11574L10.1269 3.8731C10.5437 4.28984 10.7778 4.85507 10.7778 5.44444H4.77778ZM5.88426 8.11574C6.59273 8.82421 7.55362 9.22222 8.55556 9.22222V3.22222C9.14493 3.22222 9.71016 3.45635 10.1269 3.8731L5.88426 8.11574ZM8.55556 9.22222H13.2222V3.22222H8.55556V9.22222ZM13.2222 9.22222C14.2242 9.22222 15.185 8.82421 15.8935 8.11574L11.6509 3.8731C12.0676 3.45635 12.6329 3.22222 13.2222 3.22222V9.22222ZM15.8935 8.11574C16.602 7.40726 17 6.44637 17 5.44444H11C11 4.85508 11.2341 4.28985 11.6509 3.8731L15.8935 8.11574ZM17 5.44444V0.777778H11V5.44444H17ZM17 0.777778C17 -0.224145 16.602 -1.18504 15.8935 -1.89351L11.6509 2.34913C11.2341 1.93237 11 1.36714 11 0.777778H17ZM15.8935 -1.89351C15.185 -2.60199 14.2241 -3 13.2222 -3V3C12.6329 3 12.0676 2.76588 11.6509 2.34913L15.8935 -1.89351ZM12.4444 1.66667H9.33333V7.66667H12.4444V1.66667ZM12.3333 4.66667V1.55556H6.33333V4.66667H12.3333ZM9.33333 4.55556H12.4444V-1.44444H9.33333V4.55556ZM9.44444 1.55556V4.66667H15.4444V1.55556H9.44444ZM5.44444 4.77778H0.777778V10.7778H5.44444V4.77778ZM0.777778 4.77778C-0.224153 4.77778 -1.18504 5.17579 -1.89351 5.88426L2.34913 10.1269C1.93238 10.5437 1.36715 10.7778 0.777778 10.7778V4.77778ZM-1.89351 5.88426C-2.60199 6.59273 -3 7.55363 -3 8.55556H3C3 9.14493 2.76587 9.71016 2.34913 10.1269L-1.89351 5.88426ZM-3 8.55556V13.2222H3V8.55556H-3ZM-3 13.2222C-3 14.2241 -2.60199 15.185 -1.89351 15.8935L2.34913 11.6509C2.76588 12.0676 3 12.6329 3 13.2222H-3ZM-1.89351 15.8935C-1.18504 16.602 -0.224145 17 0.777778 17V11C1.36714 11 1.93237 11.2341 2.34913 11.6509L-1.89351 15.8935ZM0.777778 17H5.44444V11H0.777778V17ZM5.44444 17C6.44637 17 7.40726 16.602 8.11574 15.8935L3.8731 11.6509C4.28985 11.2341 4.85508 11 5.44444 11V17ZM8.11574 15.8935C8.82421 15.185 9.22222 14.2242 9.22222 13.2222H3.22222C3.22222 12.6329 3.45635 12.0676 3.8731 11.6509L8.11574 15.8935ZM9.22222 13.2222V8.55556H3.22222V13.2222H9.22222ZM9.22222 8.55556C9.22222 7.55362 8.82421 6.59273 8.11574 5.88426L3.8731 10.1269C3.45635 9.71016 3.22222 9.14493 3.22222 8.55556H9.22222ZM8.11574 5.88426C7.40727 5.17579 6.44638 4.77778 5.44444 4.77778V10.7778C4.85507 10.7778 4.28984 10.5437 3.8731 10.1269L8.11574 5.88426ZM4.66667 9.44444H1.55556V15.4444H4.66667V9.44444ZM4.55556 12.4444V9.33333H-1.44444V12.4444H4.55556ZM1.55556 12.3333H4.66667V6.33333H1.55556V12.3333ZM1.66667 9.33333V12.4444H7.66667V9.33333H1.66667ZM10.8889 4.77778C7.51626 4.77778 4.77778 7.51626 4.77778 10.8889H10.7778C10.7778 10.8699 10.7811 10.8584 10.785 10.8491C10.7898 10.8378 10.7982 10.8242 10.8112 10.8112C10.8242 10.7982 10.8378 10.7898 10.8491 10.785C10.8584 10.7811 10.8699 10.7778 10.8889 10.7778V4.77778ZM4.77778 10.8889C4.77778 14.2615 7.51626 17 10.8889 17V11C10.8699 11 10.8584 10.9967 10.8491 10.9928C10.8378 10.988 10.8242 10.9795 10.8112 10.9665C10.7982 10.9535 10.7898 10.94 10.785 10.9287C10.7811 10.9194 10.7778 10.9079 10.7778 10.8889H4.77778ZM10.8889 17C14.2615 17 17 14.2615 17 10.8889H11C11 10.9079 10.9967 10.9194 10.9928 10.9287C10.988 10.94 10.9795 10.9535 10.9665 10.9665C10.9535 10.9795 10.94 10.988 10.9287 10.9928C10.9194 10.9967 10.9079 11 10.8889 11V17ZM17 10.8889C17 7.51626 14.2615 4.77778 10.8889 4.77778V10.7778C10.9079 10.7778 10.9194 10.7811 10.9287 10.785C10.94 10.7898 10.9535 10.7982 10.9665 10.8112C10.9795 10.8242 10.988 10.8378 10.9928 10.8491C10.9967 10.8584 11 10.8699 11 10.8889H17ZM10.8889 9.44444C11.6879 9.44444 12.3333 10.0899 12.3333 10.8889H6.33333C6.33333 13.4036 8.37415 15.4444 10.8889 15.4444V9.44444ZM12.3333 10.8889C12.3333 11.6879 11.6879 12.3333 10.8889 12.3333V6.33333C8.37415 6.33333 6.33333 8.37415 6.33333 10.8889H12.3333ZM10.8889 12.3333C10.0899 12.3333 9.44444 11.6879 9.44444 10.8889H15.4444C15.4444 8.37415 13.4036 6.33333 10.8889 6.33333V12.3333ZM9.44444 10.8889C9.44444 10.0899 10.0899 9.44444 10.8889 9.44444V15.4444C13.4036 15.4444 15.4444 13.4036 15.4444 10.8889H9.44444Z" fill="' +
                LIVECHAT_THEME_COLOR +
                '" mask="url(#path-1-inside-1)"/>\
                                                                        </svg><span class="settings-category" id="livechat-category-text" style="color: ' +
                LIVECHAT_THEME_COLOR +
                '; padding-left: 9px;">Category</span>';
        }
        if(path_name == "email-settings") {
            document.getElementById("email-settings").innerHTML = 
                  '<svg width="16" height="12" viewBox="0 0 16 12" xmlns="http://www.w3.org/2000/svg">\
                      <path fill="' + LIVECHAT_THEME_COLOR + '" fill-rule="evenodd" clip-rule="evenodd" d="M14 0H2C1.175 0 0.5075 0.675 0.5075 1.5L0.5 10.5C0.5 11.325 1.175 12 2 12H14C14.825 12 15.5 11.325 15.5 10.5V1.5C15.5 0.675 14.825 0 14 0ZM14 9.75C14 10.1625 13.6625 10.5 13.25 10.5H2.75C2.3375 10.5 2 10.1625 2 9.75V3L7.205 6.255C7.6925 6.5625 8.3075 6.5625 8.795 6.255L14 3V9.75ZM2 1.5L8 5.25L14 1.5H2Z"/>\
                      </svg>\
                  <span class="email-settings" id="livechat-email-settings" style="color:' + LIVECHAT_THEME_COLOR + ' ">Email Settings</span>'
        }

        if(path_name == 'livechat-form-builder') {
            document.getElementById("live-chat-page-name").innerHTML = "Create Form";
        } else if (path_name == 'developer-settings') {
            document.getElementById("livechat-developer-settings").innerHTML = `
            <svg width="14" height="13" viewBox="0 0 14 13" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M11.0083 2.26201H13.5882C13.8157 2.26201 14 2.09074 14 1.87966C14 1.66859 13.8157 1.49731 13.5882 1.49731H11.0083C10.7808 1.49731 10.5965 1.66859 10.5965 1.87966C10.5965 2.09074 10.7808 2.26201 11.0083 2.26201Z" fill="${LIVECHAT_THEME_COLOR}" stroke="${LIVECHAT_THEME_COLOR}" stroke-width="0.2"/>
            <path d="M9.53385 3.63091C10.5739 3.63091 11.4199 2.84528 11.4199 1.87964C11.4199 0.913801 10.5739 0.128174 9.53385 0.128174C8.49384 0.128174 7.64778 0.913801 7.64778 1.87964C7.64778 2.84531 8.49384 3.63091 9.53385 3.63091ZM9.53385 0.892901C10.1198 0.892901 10.5964 1.33559 10.5964 1.87964C10.5964 2.42369 10.1198 2.86618 9.53385 2.86618C8.94794 2.86618 8.4713 2.42369 8.4713 1.87964C8.4713 1.33559 8.94794 0.892901 9.53385 0.892901Z" fill="${LIVECHAT_THEME_COLOR}" stroke="${LIVECHAT_THEME_COLOR}" stroke-width="0.2"/>
            <path d="M0.411822 2.26201H6.56602C6.79346 2.26201 6.97778 2.09074 6.97778 1.87966C6.97778 1.66859 6.79346 1.49731 6.56602 1.49731H0.411852C0.184414 1.49731 9.05991e-05 1.66859 9.05991e-05 1.87966C9.05991e-05 2.09074 0.184384 2.26201 0.411822 2.26201Z" fill="${LIVECHAT_THEME_COLOR}" stroke="${LIVECHAT_THEME_COLOR}" stroke-width="0.2"/>
            <path d="M4.00553 8.25132C5.04557 8.25132 5.8916 7.46569 5.8916 6.50005C5.8916 5.53441 5.04554 4.74878 4.00553 4.74878C2.96551 4.74878 2.11945 5.53441 2.11945 6.50005C2.11945 7.46569 2.96548 8.25132 4.00553 8.25132ZM4.00553 5.51351C4.59143 5.51351 5.06808 5.95599 5.06808 6.50005C5.06808 7.0441 4.59143 7.48659 4.00553 7.48659C3.41962 7.48659 2.94298 7.0441 2.94298 6.50005C2.94298 5.95599 3.41962 5.51351 4.00553 5.51351Z" fill="${LIVECHAT_THEME_COLOR}" stroke="${LIVECHAT_THEME_COLOR}" stroke-width="0.2"/>
            <path d="M6.97329 6.88238H13.5882C13.8157 6.88238 14 6.7111 14 6.50003C14 6.28895 13.8157 6.11768 13.5882 6.11768H6.97329C6.74585 6.11768 6.56153 6.28895 6.56153 6.50003C6.56153 6.7111 6.74585 6.88238 6.97329 6.88238Z" fill="${LIVECHAT_THEME_COLOR}" stroke="${LIVECHAT_THEME_COLOR}" stroke-width="0.2"/>
            <path d="M0.411791 6.88238H2.53111C2.75855 6.88238 2.94287 6.7111 2.94287 6.50003C2.94287 6.28895 2.75855 6.11768 2.53111 6.11768H0.411791C0.184352 6.11768 2.76566e-05 6.28895 2.76566e-05 6.50003C2.76566e-05 6.7111 0.184352 6.88238 0.411791 6.88238Z" fill="${LIVECHAT_THEME_COLOR}" stroke="${LIVECHAT_THEME_COLOR}" stroke-width="0.2"/>
            <path d="M9.99454 12.8716C11.0346 12.8716 11.8806 12.086 11.8806 11.1202C11.8806 10.1545 11.0346 9.3689 9.99454 9.3689C8.95453 9.3689 8.10847 10.1545 8.10847 11.1202C8.10847 12.086 8.95453 12.8716 9.99454 12.8716ZM9.99454 10.1336C10.5804 10.1336 11.0571 10.5761 11.0571 11.1202C11.0571 11.6642 10.5804 12.1069 9.99454 12.1069C9.40864 12.1069 8.93199 11.6642 8.93199 11.1202C8.93199 10.5761 9.40864 10.1336 9.99454 10.1336Z" fill="${LIVECHAT_THEME_COLOR}" stroke="${LIVECHAT_THEME_COLOR}" stroke-width="0.2"/>
            <path d="M0.411762 11.5027H7.02672C7.25415 11.5027 7.43848 11.3315 7.43848 11.1204C7.43848 10.9093 7.25415 10.738 7.02672 10.738H0.411762C0.184324 10.738 0 10.9093 0 11.1204C0 11.3315 0.184324 11.5027 0.411762 11.5027Z" fill="${LIVECHAT_THEME_COLOR}" stroke="${LIVECHAT_THEME_COLOR}" stroke-width="0.2"/>
            <path d="M11.4689 11.5025H13.5882C13.8157 11.5025 14 11.3312 14 11.1201C14 10.9091 13.8157 10.7378 13.5882 10.7378H11.4689C11.2415 10.7378 11.0572 10.9091 11.0572 11.1201C11.0572 11.3312 11.2415 11.5025 11.4689 11.5025Z" fill="${LIVECHAT_THEME_COLOR}" stroke="${LIVECHAT_THEME_COLOR}" stroke-width="0.2"/>
            </svg><span class="settings-developer-settings" style="color: ${LIVECHAT_THEME_COLOR}; padding-left: 9px;">Developer Settings</span>`

            document.getElementById("live-chat-page-name").innerHTML = "Developer Settings";
        } else if (path_name.includes('integrations')) {
            document.getElementById('livechat_integrations').innerHTML = `
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M6.99793 3H2.49941C2.22327 3 1.99941 3.22386 1.99941 3.5V7.66529" stroke="${LIVECHAT_THEME_COLOR}"></path>
                <path d="M1.99941 9.99792L3.73095 7.3737H0.26787L1.99941 9.99792Z" fill="${LIVECHAT_THEME_COLOR}"></path>
                <path d="M9 16.9979H13.4985C13.7747 16.9979 13.9985 16.7741 13.9985 16.4979V12.3326" stroke="${LIVECHAT_THEME_COLOR}"></path>
                <path d="M13.9985 10L12.267 12.6242H15.7301L13.9985 10Z" fill="${LIVECHAT_THEME_COLOR}"></path>
                <path fill-rule="evenodd" clip-rule="evenodd" d="M13.1382 1.43595C13.0611 1.14129 12.8301 0.905338 12.528 0.867129C12.3551 0.845263 12.1789 0.833995 12 0.833995C11.8211 0.833995 11.6449 0.845264 11.472 0.867132C11.1698 0.905344 10.9388 1.14129 10.8618 1.43595L10.7884 1.71654C10.6709 2.16557 10.2093 2.43212 9.76167 2.30931L9.48253 2.23272C9.1891 2.15221 8.8696 2.23403 8.68506 2.47596C8.47183 2.7555 8.29316 3.06281 8.15542 3.39152C8.03785 3.67208 8.12681 3.98965 8.3432 4.20345L8.55007 4.40787C8.88023 4.73409 8.88023 5.26719 8.55007 5.59342L8.34318 5.79784C8.1268 6.01165 8.03784 6.32921 8.1554 6.60977C8.29314 6.93847 8.47181 7.24578 8.68503 7.52532C8.86956 7.76725 9.18907 7.84908 9.4825 7.76857L9.76167 7.69197C10.2093 7.56916 10.6709 7.83571 10.7884 8.28475L10.8618 8.56538C10.9388 8.86004 11.1698 9.09598 11.472 9.13419C11.6449 9.15606 11.8211 9.16733 12 9.16733C12.1788 9.16733 12.3551 9.15606 12.528 9.1342C12.8301 9.09599 13.0611 8.86004 13.1382 8.56538L13.2116 8.28475C13.329 7.83571 13.7907 7.56916 14.2383 7.69197L14.5175 7.76857C14.8109 7.84909 15.1304 7.76726 15.315 7.52533C15.5282 7.24579 15.7069 6.93849 15.8446 6.60978C15.9622 6.32922 15.8732 6.01166 15.6568 5.79786L15.4499 5.59342C15.1198 5.26719 15.1198 4.73409 15.4499 4.40787L15.6568 4.20344C15.8732 3.98963 15.9621 3.67207 15.8446 3.3915C15.7068 3.0628 15.5282 2.75549 15.3149 2.47596C15.1304 2.23403 14.8109 2.1522 14.5175 2.23272L14.2383 2.30931C13.7907 2.43212 13.329 2.16557 13.2116 1.71654L13.1382 1.43595ZM13.4583 4.99998C13.4583 5.8054 12.8054 6.45831 12 6.45831C11.1946 6.45831 10.5417 5.8054 10.5417 4.99998C10.5417 4.19456 11.1946 3.54165 12 3.54165C12.8054 3.54165 13.4583 4.19456 13.4583 4.99998Z" fill="${LIVECHAT_THEME_COLOR}"></path>
                <path fill-rule="evenodd" clip-rule="evenodd" d="M6.1382 10.4359C6.06114 10.1413 5.83015 9.90534 5.52798 9.86713C5.35507 9.84526 5.17885 9.83399 5 9.83399C4.82114 9.83399 4.64491 9.84526 4.47199 9.86713C4.16983 9.90534 3.93884 10.1413 3.86177 10.4359L3.78839 10.7165C3.67095 11.1656 3.20927 11.4321 2.76167 11.3093L2.48253 11.2327C2.1891 11.1522 1.86959 11.234 1.68506 11.476C1.47183 11.7555 1.29316 12.0628 1.15542 12.3915C1.03785 12.6721 1.12681 12.9896 1.34319 13.2035L1.55007 13.4079C1.88023 13.7341 1.88023 14.2672 1.55007 14.5934L1.34318 14.7978C1.1268 15.0116 1.03784 15.3292 1.1554 15.6098C1.29314 15.9385 1.47181 16.2458 1.68503 16.5253C1.86956 16.7673 2.18907 16.8491 2.4825 16.7686L2.76167 16.692C3.20927 16.5692 3.67095 16.8357 3.78839 17.2847L3.86178 17.5654C3.93885 17.86 4.16984 18.096 4.472 18.1342C4.64492 18.1561 4.82115 18.1673 5 18.1673C5.17885 18.1673 5.35506 18.1561 5.52797 18.1342C5.83013 18.096 6.06113 17.86 6.13819 17.5654L6.21159 17.2847C6.32903 16.8357 6.79071 16.5692 7.23831 16.692L7.51749 16.7686C7.81093 16.8491 8.13043 16.7673 8.31497 16.5253C8.52819 16.2458 8.70685 15.9385 8.84459 15.6098C8.96216 15.3292 8.8732 15.0117 8.65681 14.7979L8.44991 14.5934C8.11975 14.2672 8.11975 13.7341 8.44991 13.4079L8.6568 13.2034C8.87318 12.9896 8.96214 12.6721 8.84458 12.3915C8.70683 12.0628 8.52816 11.7555 8.31494 11.476C8.1304 11.234 7.8109 11.1522 7.51747 11.2327L7.23831 11.3093C6.79071 11.4321 6.32903 11.1656 6.21159 10.7165L6.1382 10.4359ZM6.45833 14C6.45833 14.8054 5.80541 15.4583 5 15.4583C4.19458 15.4583 3.54167 14.8054 3.54167 14C3.54167 13.1946 4.19458 12.5416 5 12.5416C5.80541 12.5416 6.45833 13.1946 6.45833 14Z" fill="${LIVECHAT_THEME_COLOR}"></path>
            </svg>
			<span class="settings-integrations" style="color: ${LIVECHAT_THEME_COLOR};">Integrations</span>
            `
        } else if (path_name == 'chat-escalation' || path_name == 'blacklisted-keyword' || path_name == 'reported-users' || path_name == 'blocked-users') {
            document.getElementById('livechat-chat-escalation-response-div').innerHTML = `
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path class="settings-chat-escalation-keyword" id="livechat-chat-escalation-keyword-sidenav" d="M7 0C3.136 0 0 3.136 0 7C0 10.864 3.136 14 7 14C10.864 14 14 10.864 14 7C14 3.136 10.864 0 7 0ZM1.4 7C1.4 3.906 3.906 1.4 7 1.4C8.295 1.4 9.485 1.841 10.43 2.583L2.583 10.43C1.81424 9.45219 1.39747 8.24382 1.4 7ZM7 12.6C5.705 12.6 4.515 12.159 3.57 11.417L11.417 3.57C12.1858 4.54781 12.6025 5.75618 12.6 7C12.6 10.094 10.094 12.6 7 12.6Z" fill="${LIVECHAT_THEME_COLOR}"/>
                </svg>
                <span class="settings-chat-escalation-keyword" id="livechat-chat-escalation-keyword-sidenav-text" style="color: ${LIVECHAT_THEME_COLOR};">Chat Escalation Matrix</span>
            `
        } else if (path_name == 'system-settings' || path_name == 'interaction-settings') {
            document.getElementById("livechat-nav-general-settings-header").innerHTML = `
                        <h2 class="setting-page-nav-subheading-div">
                            <svg width="14" height="12" viewBox="0 0 14 12" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin: 4px 0px;">
                                <rect width="14" height="12" fill="#E5E5E5"></rect>
                                <g clip-path="url(#clip0)">
                                <rect width="1440" height="841" transform="translate(-90 -242)" fill="white"></rect>
                                <path d="M4.725 7.125C5.80034 7.125 6.70142 7.92437 6.93885 8.99875L13.475 9C13.7649 9 14 9.25184 14 9.5625C14 9.84727 13.8025 10.0826 13.5462 10.1199L13.475 10.125L6.93901 10.1255C6.70184 11.2003 5.80059 12 4.725 12C3.64941 12 2.74816 11.2003 2.51099 10.1255L0.525 10.125C0.23505 10.125 0 9.87316 0 9.5625C0 9.27773 0.197508 9.04238 0.453761 9.00514L0.525 9L2.51099 8.9995C2.74816 7.92474 3.64941 7.125 4.725 7.125ZM4.725 8.25C4.1901 8.25 3.73528 8.61732 3.56827 9.12937L3.55387 9.17637L3.52693 9.28752C3.50928 9.3762 3.5 9.46819 3.5 9.5625C3.5 9.67863 3.51408 9.79123 3.5405 9.89846L3.56836 9.9959L3.58635 10.0475C3.76638 10.5323 4.20834 10.875 4.725 10.875C5.25963 10.875 5.71427 10.508 5.88148 9.99639L5.90953 9.89836L5.89757 9.94356C5.93167 9.82296 5.95 9.69503 5.95 9.5625C5.95 9.48388 5.94355 9.40688 5.93118 9.33206L5.91016 9.22924L5.89616 9.17647L5.86338 9.07677C5.68316 8.59235 5.2414 8.25 4.725 8.25ZM9.275 0C10.3506 0 11.2518 0.799741 11.489 1.8745L13.475 1.875C13.7649 1.875 14 2.12684 14 2.4375C14 2.72227 13.8025 2.95762 13.5462 2.99487L13.475 3L11.489 3.0005C11.2518 4.07526 10.3506 4.875 9.275 4.875C8.19941 4.875 7.29816 4.07526 7.06099 3.0005L0.525 3C0.23505 3 0 2.74816 0 2.4375C0 2.15273 0.197508 1.91738 0.453761 1.88013L0.525 1.875L7.06115 1.87375C7.29858 0.799366 8.19966 0 9.275 0ZM9.275 1.125C8.7401 1.125 8.28528 1.49232 8.11827 2.00437L8.10387 2.05137L8.07693 2.16252C8.05928 2.2512 8.05 2.34319 8.05 2.4375C8.05 2.55363 8.06408 2.66623 8.0905 2.77346L8.11836 2.8709L8.13635 2.92248C8.31638 3.4073 8.75834 3.75 9.275 3.75C9.80963 3.75 10.2643 3.38304 10.4315 2.87139L10.4595 2.77336L10.4476 2.81856C10.4817 2.69796 10.5 2.57003 10.5 2.4375C10.5 2.35888 10.4935 2.28188 10.4812 2.20706L10.4602 2.10424L10.4462 2.05147L10.4134 1.95177C10.2332 1.46735 9.7914 1.125 9.275 1.125Z" fill="#4D4D4D"></path>
                                </g>
                                <defs>
                                <clipPath id="clip0">
                                <rect width="1440" height="841" fill="white" transform="translate(-90 -242)"></rect>
                                </clipPath>
                                </defs>
                            </svg>
                            <span style="margin-left: 4px; margin-top: -2px">General Settings</span>
                        </h2>`;
            document.getElementById("live-chat-page-name").innerHTML = "Settings";
        }
        else {
            document.getElementById("live-chat-page-name").innerHTML = "Settings";
        }
    } else if (id == "manage-only-admin") {
        elem.innerHTML =
            '<svg width="18" height="18" viewBox="0 0 18 21" fill="none" xmlns="http://www.w3.org/2000/svg">\
                            <path d="M11.9232 12.8502C11.7927 12.8078 10.9682 12.4381 11.4834 10.8799H11.476C12.8191 9.50383 13.8454 7.28948 13.8454 5.10941C13.8454 1.75728 11.6048 0 9.00082 0C6.39517 0 4.16691 1.75646 4.16691 5.10941C4.16691 7.29846 5.18751 9.52178 6.53874 10.8946C7.06545 12.2691 6.12361 12.7792 5.92671 12.8502C3.19964 13.8321 0 15.6204 0 17.3859V18.0478C0 20.4531 4.68788 21 9.02625 21C13.3712 21 18 20.4531 18 18.0478V17.3859C18 15.5674 14.7848 13.793 11.9232 12.8502ZM7.39772 19.9585C7.39772 17.878 8.72926 15.0695 8.72926 15.0695L7.80793 14.3504C7.80793 13.6632 9 12.9441 9 12.9441C9 12.9441 10.1888 13.6746 10.1888 14.3504L9.27074 15.0695C9.27074 15.0695 10.6023 17.8674 10.6023 19.9814C10.6023 20.3128 7.39772 20.236 7.39772 19.9585Z" fill="' +
            LIVECHAT_THEME_COLOR +
            '"></path>\
                        </svg><span id="sidebarlink" style="color: ' +
            LIVECHAT_THEME_COLOR +
            '">LiveChat Admin</span>';
        $(elem).parent().addClass("active");
        document.getElementById("live-chat-page-name").innerHTML = "LiveChat Admin";
    } else if (id == 'internal-chat') {
        elem.innerHTML = 
            `<svg width="22" height="22" viewBox="0 0 32 33" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9.94786 17.8901L5 21.8901V5.89014C5 5.62492 5.10536 5.37057 5.29289 5.18303C5.48043 4.99549 5.73478 4.89014 6 4.89014H22C22.2652 4.89014 22.5196 4.99549 22.7071 5.18303C22.8946 5.37057 23 5.62492 23 5.89014V16.8901C23 17.1554 22.8946 17.4097 22.7071 17.5972C22.5196 17.7848 22.2652 17.8901 22 17.8901H9.94786Z" stroke="${LIVECHAT_THEME_COLOR}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M11 17.8901V22.8901C11 23.1554 11.1054 23.4097 11.2929 23.5972C11.4804 23.7848 11.7348 23.8901 12 23.8901H24.0521L29 27.8901V11.8901C29 11.6249 28.8946 11.3706 28.7071 11.183C28.5196 10.9955 28.2652 10.8901 28 10.8901H23" stroke="${LIVECHAT_THEME_COLOR}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span style="padding-left: 9px; color: ${LIVECHAT_THEME_COLOR}" id="sidebarlink">Group Chat</span></a>`
    } else if (id == 'voip-history') {
        elem.innerHTML = 
            `<svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14.2788 11.3729C13.8165 10.9552 13.2196 10.7253 12.5979 10.7253C11.8911 10.7253 11.2134 11.0261 10.7387 11.5506L10.2655 12.0733C10.0824 12.276 9.9359 12.5026 9.8279 12.7496C7.9559 11.9594 6.41942 10.553 5.46542 8.75719C5.80832 8.61571 6.11684 8.39881 6.36812 8.12089L6.84044 7.59871C7.2899 7.10191 7.51868 6.46021 7.48502 5.79169C7.45172 5.12299 7.15994 4.50739 6.66314 4.05811L5.86556 3.33703C5.40404 2.91925 4.80716 2.68921 4.1849 2.68921C3.47732 2.68921 2.79944 2.98981 2.32514 3.51397L1.85282 4.03687C1.78748 4.10905 1.7252 4.18699 1.66706 4.26907C1.14254 4.73455 0.728 5.75569 0.97136 7.01371C2.01518 12.4486 6.59348 16.5893 12.1049 17.0834C12.2244 17.0944 12.3432 17.0998 12.4609 17.0998C13.0953 17.0998 13.6938 16.9434 14.1702 16.6502C14.4006 16.517 14.6064 16.351 14.7813 16.1573L15.2544 15.6344C16.181 14.6092 16.1013 13.0212 15.0765 12.0946L14.2788 11.3729ZM13.8289 16.0778C13.3779 16.3548 12.7862 16.4765 12.1648 16.4196C6.94772 15.952 2.61404 12.0325 1.6262 6.88789C1.4183 5.81329 1.80836 5.02543 2.12138 4.75795C2.13272 4.74823 2.14334 4.73797 2.15324 4.72681L2.17484 4.70269C2.18402 4.69243 2.19248 4.68163 2.2004 4.67047C2.2463 4.60423 2.2958 4.54177 2.34764 4.48435L2.81996 3.96145C3.16808 3.57679 3.6656 3.35611 4.18526 3.35611C4.64192 3.35611 5.07986 3.52495 5.41862 3.83167L6.21638 4.55275C6.58088 4.88251 6.79508 5.33431 6.81956 5.82499C6.84422 6.31585 6.67628 6.78691 6.34634 7.15159L5.87402 7.67377C5.64884 7.92289 5.36084\
                8.10541 5.04134 8.20135L4.89752 8.24473C4.80338 8.27299 4.7267 8.34157 4.68764 8.43175C4.64876 8.52193 4.65146 8.62489 4.69538 8.71273L4.76216 8.84665C5.81048 10.9516 7.59122 12.5858 9.7766 13.4485L9.9008 13.4973C9.98594 13.5308 10.0808 13.5277 10.1638 13.4892C10.2466 13.4505 10.3099 13.3796 10.3389 13.2928L10.381 13.167C10.4617 12.9271 10.5893 12.7093 10.7603 12.5201L11.2332 11.9975C11.5816 11.6125 12.079 11.3917 12.5981 11.3917C13.0544 11.3917 13.4925 11.5605 13.8318 11.8672L14.6294 12.5887C15.3814 13.2689 15.4399 14.4346 14.7599 15.1871L14.2867 15.71C14.1582 15.8528 14.0068 15.9748 13.8289 16.0778Z" fill="${LIVECHAT_THEME_COLOR}"/>\
                <path d="M9.28107 0.899902C8.87913 0.899902 8.55225 1.22696 8.55225 1.6289C8.55225 2.03048 8.87931 2.35736 9.28107 2.35736C12.7095 2.35736 15.4986 5.14664 15.4986 8.57492C15.4986 8.97668 15.8257 9.30356 16.2274 9.30356C16.6292 9.30356 16.9561 8.97668 16.9561 8.57492C16.9561 4.34294 13.513 0.899902 9.28107 0.899902ZM16.2274 8.85914C16.0707 8.85914 15.943 8.7317 15.943 8.5751C15.943 4.90166 12.9545 1.91294 9.28089 1.91294C9.12411 1.91294 8.99649 1.7855 8.99649 1.6289C8.99649 1.47194 9.12411 1.34432 9.28089 1.34432C13.2679 1.34432 16.5115 4.58792 16.5115 8.57492C16.5117 8.7317 16.3842 8.85914 16.2274 8.85914Z" fill="${LIVECHAT_THEME_COLOR}"/>\
                <path d="M13.0199 8.65651C13.0199 9.05845 13.3468 9.38533 13.7487 9.38533C14.1507 9.38533 14.4775 9.05827 14.4775 8.65651C14.4775 5.74645 12.1098 3.37891 9.19959 3.37891C8.79783 3.37891 8.47095 3.70579 8.47095 4.10737C8.47095 4.50931 8.79783 4.83619 9.19959 4.83619C11.3059 4.83619 13.0199 6.54997 13.0199 8.65651ZM9.19941 3.82351C11.8645 3.82351 14.0329 5.99161 14.0329 8.65669C14.0329 8.81347 13.9055 8.94109 13.7487 8.94109C13.5919 8.94109 13.4645 8.81347 13.4645 8.65669C13.4645 6.30499 11.5513 4.39177 9.19959 4.39177C9.04281 4.39177 8.91537 4.26433 8.91537 4.10755C8.91519 3.95077 9.04263 3.82351 9.19941 3.82351Z" fill="${LIVECHAT_THEME_COLOR}"/>\
            </svg>                        

            <span style="color: ${LIVECHAT_THEME_COLOR}" id="sidebarlink">Voice Call History</span>`
            $(elem).parent().addClass("active");
            document.getElementById("live-chat-page-name").innerHTML = "Voice Call History";
    } else if(id == 'live-chat-requests-in-queue') {
        elem.innerHTML =
            `<svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M10.7142 10.8927C11.661 10.8927 12.4285 11.6602 12.4285 12.607V13.1785C12.4285 15.4316 10.3033 17.7499 6.71419 17.7499C3.12501 17.7499 0.999817 15.4316 0.999817 13.1785V12.607C0.999817 11.6602 1.76733 10.8927 2.71414 10.8927H10.7142ZM10.7142 12.0356H2.71414C2.39854 12.0356 2.14271 12.2914 2.14271 12.607V13.1785C2.14271 14.8215 3.77947 16.6071 6.71419 16.6071C9.64885 16.6071 11.2857 14.8215 11.2857 13.1785V12.607C11.2857 12.2914 11.0298 12.0356 10.7142 12.0356ZM14.7143 8.60697C15.1877 8.60697 15.5714 8.99075 15.5714 9.46413C15.5714 9.9375 15.1877 10.3213 14.7143 10.3213C14.2408 10.3213 13.8571 9.9375 13.8571 9.46413C13.8571 8.99075 14.2408 8.60697 14.7143 8.60697ZM6.71419 3.46406C8.44992 3.46406 9.85708 4.87116 9.85708 6.60695C9.85708 8.34274 8.44992 9.74984 6.71419 9.74984C4.9784 9.74984 3.5713 8.34274 3.5713 6.60695C3.5713 4.87116 4.9784 3.46406 6.71419 3.46406ZM6.71419 4.60693C5.6096 4.60693 4.71417 5.50237 4.71417 6.60695C4.71417 7.71154 5.6096 8.60697 6.71419 8.60697C7.81877 8.60697 8.71421 7.71154 8.71421 6.60695C8.71421 5.50237 7.81877 4.60693 6.71419 4.60693ZM14.7143 1.74976C15.9766 1.74976 17 2.77314 17 4.0355C17 4.87042 16.758 5.33802 16.1383 5.9874L15.8365 6.29546C15.4051 6.74524 15.2857 6.98764 15.2857 7.46411C15.2857 7.77971 15.0298 8.03554 14.7143 8.03554C14.3987 8.03554 14.1428 7.77971 14.1428 7.46411C14.1428 6.62918 14.3848 6.16158 15.0045 5.5122L15.3063 5.20414C15.7377 4.75436 15.8571 4.51196 15.8571 4.0355C15.8571 3.40429 15.3454 2.89263 14.7143 2.89263C14.0831 2.89263 13.5714 3.40429 13.5714 4.0355C13.5714 4.3511 13.3155 4.60693 13 4.60693C12.6844 4.60693 12.4285 4.3511 12.4285 4.0355C12.4285 2.77314 13.4519 1.74976 14.7143 1.74976Z" fill="${LIVECHAT_THEME_COLOR}"/>
            </svg>
            <span style="color: ${LIVECHAT_THEME_COLOR} !important;" id="sidebarlink">Requests in Queue</span>`;
            $(elem).parent().addClass("active");
        document.getElementById("live-chat-page-name").innerHTML = "Requests in Queue";      
    } else if (id == 'vc-history') {
        elem.innerHTML = 
        `<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12.5 13.125C12.5 14.5057 11.3807 15.625 10 15.625H5C3.61929 15.625 2.5 14.5057 2.5 13.125V6.875C2.5 5.49429 3.61929 4.375 5 4.375H10C11.3807 4.375 12.5 5.49429 12.5 6.875V13.125Z" stroke="${LIVECHAT_THEME_COLOR}" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M13.75 12.0773V7.92269L15.918 5.87032C16.5156 5.30459 17.5 5.72825 17.5 6.55114V13.4488C17.5 14.2717 16.5156 14.6954 15.918 14.1297L13.75 12.0773Z" stroke="${LIVECHAT_THEME_COLOR}" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
                                

        <span style="color: ${LIVECHAT_THEME_COLOR}" id="sidebarlink">Video Call History</span>`
        $(elem).parent().addClass("active");
        document.getElementById("live-chat-page-name").innerHTML = "Video Call History";
    } else if (id == 'cobrowsing-history') {
        elem.innerHTML = 
            `<svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="18" height="18" rx="3" fill="${LIVECHAT_THEME_COLOR}"/>
            <path fill-rule="evenodd" clip-rule="evenodd" d="M1 3.84588C1 2.27424 2.27424 1 3.84587 1H14.1541C15.7258 1 17 2.27424 17 3.84588V14.1541C17 15.7258 15.7258 17 14.1541 17H3.84587C2.27424 17 1 15.7258 1 14.1541V3.84588ZM5.68835 11.0262H10.133C11.1638 11.0262 11.9996 11.8621 11.9996 12.8929C11.9996 13.9239 11.1638 14.7595 10.133 14.7595H5.68835C4.65754 14.7595 3.8217 13.9239 3.8217 12.8929C3.8217 11.8621 4.65754 11.0262 5.68835 11.0262ZM4.6059 9.37834C4.78015 9.44458 4.77463 9.68951 4.5976 9.74802L4.14835 9.89652L4.56093 10.3179C4.65015 10.409 4.64755 10.5542 4.55522 10.6422C4.46282 10.7301 4.31568 10.7276 4.22646 10.6365L3.78638 10.187L3.54099 10.5673C3.44653 10.7136 3.22015 10.6763 3.1791 10.5076L2.81925 9.02919C2.78179 8.87524 2.93491 8.74305 3.08477 8.79996L4.6059 9.37834ZM9.3149 5.26608H13.7595C14.7903 5.26608 15.6261 6.10192 15.6261 7.13276C15.6261 8.16376 14.7903 8.99939 13.7595 8.99939H9.3149C8.28407 8.99939 7.44822 8.16376 7.44822 7.13276C7.44822 6.10192 8.28407 5.26608 9.3149 5.26608ZM8.23243 3.61821C8.40666 3.68444 8.40117 3.92938 8.22413 3.98789L7.77488 4.13639L8.18746 4.55779C8.27667 4.64886 8.27408 4.79403 8.18175 4.88203C8.08934 4.96995 7.94218 4.96744 7.85297 4.87632L7.41289 4.42685L7.16752 4.80714C7.07304 4.95347 6.84666 4.91619 6.80562 4.74746L6.44575 3.26904C6.4083 3.1151 6.56143 2.9829 6.71127 3.03983L8.23243 3.61821Z" fill="white"/>
            </svg>
                            

            <span style="color: ${LIVECHAT_THEME_COLOR}" id="sidebarlink">Cobrowsing History</span>`
            $(elem).parent().addClass("active");
            document.getElementById("live-chat-page-name").innerHTML = "Cobrowsing History";
    } else if (id == 'followup-leads') {
        elem.innerHTML = 
        `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M15.9941 12.6877C15.4258 12.7865 14.9785 13.0324 14.5966 13.4562C14.2798 13.8079 14.0737 14.229 13.9743 14.7278C13.9279 14.9611 13.9278 15.4491 13.9743 15.6828C14.0889 16.2601 14.3414 16.7294 14.7427 17.1109L14.8531 17.2158L14.7815 17.2471C14.6067 17.3235 14.3177 17.4892 14.1275 17.6222C13.2062 18.2662 12.5858 19.2696 12.3863 20.4381C12.3388 20.7166 12.3145 21.5856 12.3506 21.7135C12.3786 21.8124 12.4508 21.9015 12.5472 21.9561L12.6247 22H16.3347H20.0447L20.1284 21.9503C20.1744 21.9229 20.2378 21.8617 20.2693 21.8143L20.3265 21.7281L20.3323 21.3069C20.3392 20.8076 20.3087 20.5025 20.2117 20.1004C19.9652 19.0796 19.356 18.1781 18.5231 17.6016C18.3631 17.4908 18.0315 17.3033 17.8973 17.2477L17.8162 17.2141L17.9293 17.1141C18.0435 17.013 18.2339 16.7824 18.3389 16.618C18.4887 16.3834 18.6319 16.0144 18.6964 15.6966C18.7432 15.4659 18.7421 14.9408 18.6943 14.7079C18.5881 14.1901 18.3805 13.787 18.0271 13.4127C17.6688 13.0332 17.289 12.816 16.7949 12.7082C16.5865 12.6626 16.196 12.6527 15.9941 12.6877ZM16.7761 13.5834C17.3118 13.7494 17.7226 14.1874 17.8789 14.759C17.9159 14.8944 17.9219 14.9605 17.921 15.2252C17.92 15.5083 17.9156 15.5475 17.8671 15.7027C17.7741 16.0005 17.6811 16.1655 17.4817 16.3865C17.2756 16.6148 17.016 16.7756 16.7198 16.8582C16.5079 16.9173 16.159 16.9175 15.9496 16.8586C15.3432 16.688 14.8869 16.1818 14.7652 15.5449C14.723 15.3236 14.736 14.9612 14.7939 14.7485C14.935 14.2294 15.3248 13.7902 15.8035 13.611C16.1008 13.4996 16.4719 13.4891 16.7761 13.5834ZM16.8969 17.8135C17.5841 17.937 18.2841 18.3534 18.7379 18.9087C19.225 19.5047 19.4814 20.1729 19.5367 20.9903L19.5031 20.6667H16.3333C13.7756 20.6667 13.1975 20.6865 13.1976 20.6667C13.1984 20.5468 13.168 20.6134 13.1976 20.4632C13.4583 19.1409 14.4362 18.1072 15.6884 17.8303C16.0714 17.7456 16.4865 17.7398 16.8969 17.8135Z" fill="${LIVECHAT_THEME_COLOR}"/>
            <path d="M5.66667 5.99999H3V21.3333H16.3333" stroke="${LIVECHAT_THEME_COLOR}" stroke-width="1.33333" stroke-linejoin="round"/>
            <path d="M13.6667 5.99999H16.3334V13.1611" stroke="${LIVECHAT_THEME_COLOR}" stroke-width="1.33333" stroke-linejoin="round"/>
            <path d="M7.66667 6L7 4.66666H11H12.3333L11.6667 6H7.66667Z" stroke="${LIVECHAT_THEME_COLOR}" stroke-width="1.33333" stroke-linejoin="round"/>
            <path d="M10.9999 3.33333C10.9999 4.06971 10.403 4.66667 9.66659 4.66667C8.93021 4.66667 8.33325 4.06971 8.33325 3.33333C8.33325 2.59695 8.93021 2 9.66659 2C10.403 2 10.9999 2.59695 10.9999 3.33333ZM9.04456 3.33333C9.04456 3.67687 9.32305 3.95535 9.66659 3.95535C10.0101 3.95535 10.2886 3.67687 10.2886 3.33333C10.2886 2.9898 10.0101 2.71131 9.66659 2.71131C9.32305 2.71131 9.04456 2.9898 9.04456 3.33333Z" fill="${LIVECHAT_THEME_COLOR}"/>
            <path d="M5.66675 10.6667L6.33341 11.3333L7.66675 9.99998" stroke="${LIVECHAT_THEME_COLOR}" stroke-width="0.666667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M9 10.6667H13.6667" stroke="${LIVECHAT_THEME_COLOR}" stroke-width="0.666667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M5.66675 13.3333L6.33341 14L7.66675 12.6667" stroke="${LIVECHAT_THEME_COLOR}" stroke-width="0.666667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M9 13.3333H13.6667" stroke="${LIVECHAT_THEME_COLOR}" stroke-width="0.666667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M5.66675 16L6.33341 16.6667L7.66675 15.3333" stroke="${LIVECHAT_THEME_COLOR}" stroke-width="0.666667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M9 16H11.6667" stroke="${LIVECHAT_THEME_COLOR}" stroke-width="0.666667" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
                                

        <span id="sidebarlink" style="color: ${LIVECHAT_THEME_COLOR};">Follow Up Leads</span>`
        $(elem).parent().addClass("active");
        document.getElementById("live-chat-page-name").innerHTML = "Follow Up Leads";
    } else if (id == 'agent-analytics') {
        elem.innerHTML = 
        `<svg width="15" height="20" viewBox="0 0 15 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9.5 1.5H3C2.2 1.5 1.66667 2.5 1.5 3V17C1.5 17.8 2.5 18.3333 3 18.5H12C13.2 18.5 13.8333 17.5 14 17V6L9.5 1.5Z" stroke="${LIVECHAT_THEME_COLOR}" stroke-width="1.5" stroke-linejoin="round"/>
            <path d="M9.5 4.5V2.5L10 2L11 3.1305L12.8094 5L13 6H11C9.8 6 9.5 5 9.5 4.5Z" fill="${LIVECHAT_THEME_COLOR}" stroke="${LIVECHAT_THEME_COLOR}"/>
            <rect x="10" y="9" width="2" height="8" rx="0.5" fill="${LIVECHAT_THEME_COLOR}"/>
            <rect x="7" y="11" width="2" height="6" rx="0.5" fill="${LIVECHAT_THEME_COLOR}"/>
            <rect x="4" y="13" width="2" height="4" rx="0.5" fill="${LIVECHAT_THEME_COLOR}"/>
        </svg>                        

        <span style="color: ${LIVECHAT_THEME_COLOR};" id="sidebarlink">Report</span></a>`
        $(elem).parent().addClass("active");  
    }
}

function get_url_vars() {
    let vars = {};
    let parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m, key, value) {
        vars[key] = value;
    });
    return vars;
}

function toggle_side_bar() {
    var onCollapse = document.getElementById("oncollapse");
    var withoutCollapse = document.getElementById("without-collapse");
    var min_screen = window.matchMedia("(min-width:1300px)");
    var max_screen = window.matchMedia("(max-width:1400px)");
    if (getComputedStyle(withoutCollapse).display === 'none') {
        onCollapse.style.display = "none";
        withoutCollapse.style.display = "block";
        $("[data-toggle='tooltip'][class='nav-link']").each(function(){
            $(this).hover(function(){
                $(this).tooltip('dispose');
            },function(){
                $(this).tooltip('dispose');
            });
        });
        try{
            if (min_screen.matches && max_screen.matches){
                document.getElementById("average_handle_time").style.paddingLeft = "30px";
                document.getElementById("average_handle_time").style.fontSize = "13px";
                document.getElementById("average_handle_time").style.paddingRight = "20px";
                document.getElementById("nps_avg").style.paddingLeft = "9px";
                document.getElementById("nps_avg").style.fontSize = "18px";
            }
            else{
                document.getElementById("average_handle_time").style.paddingLeft = "11px";
                document.getElementById("average_handle_time").style.fontSize = "15px";
            }
        }catch(err){
            console.log(err)
        }
    } else {
        onCollapse.style.display = "block";
        withoutCollapse.style.display = "none";
        $("[data-toggle='tooltip'][class='nav-link']").each(function(){
            $(this).hover(function(){
                $(this).tooltip('show');
            },function(){
                $(this).tooltip('dispose');
            });
            
        });
        try{
            if (min_screen.matches && max_screen.matches){
                document.getElementById("average_handle_time").style.paddingLeft = "11px";
                document.getElementById("average_handle_time").style.fontSize = "13px";
                document.getElementById("average_handle_time").style.paddingRight = "0px";
                document.getElementById("nps_avg").style.paddingLeft = "8px";
                document.getElementById("nps_avg").style.fontSize = "22px";
            }
            else{
                document.getElementById("average_handle_time").style.paddingLeft = "15px";
                document.getElementById("average_handle_time").style.fontSize = "16px";
            }
        }catch(err){
            console.log(err)
        }
    }
}

function get_params (json_string) {
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    return `json_string=${json_string}`;
}

function alphanumeric(inputtxt) {
    var letters = /^[0-9a-zA-Z &@';,.-:\n]+$/;
    if (inputtxt.match(letters)) {
        return true;
    } else {
        return false;
    }
}

function is_equal_json(obj1, obj2) {
    if(!obj1 || !obj2) return false;
    let keys1 = Object.keys(obj1);
    let keys2 = Object.keys(obj2);

    //return true when the two json has same length and all the properties has same value key by key
    return keys1.length === keys2.length && Object.keys(obj1).every(key=>obj1[key]==obj2[key]);
}

function strip_malicious_chars(text) {
    return text.replace(/[<*?>]/g, '');
}

export {
    change_date_format_original,
    is_valid_date,
    CustomEncrypt,
    custom_encrypt,
    custom_decrypt,
    encrypt_variable,
    EncryptVariable,
    get_delayed_date_object,
    set_cookie,
    get_cookie,
    getCsrfToken,
    showToast,
    validate_name,
    validate_phone_number,
    validate_email,
    validate_username,
    validate_password,
    validate_keyword,
    validate_canned_response,
    validate_category_title,
    format_time,
    is_mobile,
    stripHTML,
    is_file_supported,
    check_file_size,
    check_malicious_file,
    is_docs,
    is_video,
    is_txt,
    is_pdf,
    is_image,
    is_excel,
    get_image_path_html,
    get_video_path_html,
    get_doc_path_html,
    get_unread_message_diffrentiator_html,
    initiate_internet_speed_detection,
    initialize_page,
    get_url_vars,
    toggle_side_bar,
    get_params,
    get_new_chat_indicator_html,
    alphanumeric,
    strip_unwanted_characters,
    get_guest_session_indicator_html,
    get_self_assign_indicator_html,
    is_equal_json,
    validate_number_input,
    validate_number_input_value,
    remove_special_characters_from_str,
    stripHTMLtags,
    strip_malicious_chars,
};
