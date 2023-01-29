var EASYCHAT_IMG_PATH = "/static/EasyAssistApp/img/";
var EASYCHAT_INPUT_QUERY_DEFAULT_PLACEHOLDER = "Type your message and hit enter";
var CLEAR_API_URL = "/chat/clear-user-data/";
var EASYCHAT_FEEDBACK_SAVE_URL = "/chat/save-easychat-feedback-msg/";
var GET_LIVECHAT_CATEGORY = "/livechat/get-livechat-category/"
var EASYCHAT_QUERY_URL = "/chat/query/";
var RESPONSE_SENTENCE_SEPARATOR = "$$$";
var is_doubletick = false;
var suggestion_list = [];
var code_list = [];
var custom_quote_list_flag = "";
var bot_id = null;
var bot_name = null;
var user_id = "";
var session_id = "";
var window_location = "";
var easychat_card_counter = 0;
var captcha_id = "";
var is_map_js_loaded = false;
var is_captcha = null;
var is_flow_ended = true;
var hide_mic = false;
var is_custom_complete = false;
var message = null;
var voices = null;
var final_transcript = '';
var recognizing = false;
var ignore_onend;
var recognition = null;
var marker = null;
var is_livechat = false;
var form_assist_enabled = false;
var GallaryslideIndex, gallery_slides, gallery_dots;
var attached_file_src = "None";
var attachment_file_name = "None";
var attachment_file_global = undefined;
var uploaded_attached_files = [];
var do_not_disturb = "";
var MAX_TEXT_RESPONSE_LENGTH = 200;
var embed_cookies = ""
var embed_meta_data = ""
var is_cobrowsing_chat = false;
var agent_name = null;
var livechat_typing_loader_show_interval = null;

var file_type_ext = {
    "image(ex. .jpeg, .png)": ".jpeg, .png, .gif",
    "word processor(i.e. .doc,.pdf)": ".doc, .odt, .pdf, .rtf, .tex, .txt, .wks, .wkp",
    "compressed file(ex. .zip)": ".zip, .rar, .rpm, .z, .tar.gz, .pkg",
}

if (typeof String.prototype.trim !== 'function') {
    String.prototype.trim = function() {
        return this.replace(/^\s+|\s+$/g, '');
    }
}

// Create Element.remove() function if not exist
if (!('remove' in Element.prototype)) {
    Element.prototype.remove = function() {
        if (this.parentNode) {
            this.parentNode.removeChild(this);
        }
    };
}

/////////////////////////////// Encryption And Decription //////////////////////////

// function easyassist_custom_encrypt(msgString, key) {
//     // msgString is expected to be Utf8 encoded
//     var iv = CryptoJS.lib.WordArray.random(16);
//     var encrypted = CryptoJS.AES.encrypt(msgString, CryptoJS.enc.Utf8.parse(key), {
//         iv: iv
//     });
//     var return_value = key;
//     return_value += "." + encrypted.toString();
//     return_value += "." + CryptoJS.enc.Base64.stringify(iv);
//     return return_value;
// }

function generate_random_string(length) {
    var result = '';
    var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for(let i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}


function encrypt_variable(data) {

    var utf_data = CryptoJS.enc.Utf8.parse(data);
    var encoded_data = utf_data;
    var random_key = generate_random_string(16);
    var encrypted_data = easyassist_custom_encrypt(encoded_data, random_key);

    return encrypted_data;
}


// function easyassist_custom_decrypt(msg_string) {

//     var payload = msg_string.split(".");
//     var key = payload[0];
//     var decrypted_data = payload[1];
//     var decrypted = CryptoJS.AES.decrypt(decrypted_data, CryptoJS.enc.Utf8.parse(key), {
//         iv: CryptoJS.enc.Base64.parse(payload[2])
//     });
//     return decrypted.toString(CryptoJS.enc.Utf8);
// }

////////////////////////////////////////////////////////////////////////////////////


function show_scroll_image() {
    var scrollHeight = document.getElementById("easychat-chat-container").scrollHeight;
    var scrollTop = document.getElementById("easychat-chat-container").scrollTop;
    var clientHeight = document.getElementById("easychat-chat-container").clientHeight;

    if (scrollHeight - (scrollTop + clientHeight) > 100) {
        document.getElementById("img-scroll-to-bottom").style.display = "block";
    } else {
        document.getElementById("img-scroll-to-bottom").style.display = "none";
    }
}

function get_url_vars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m, key, value) {
        vars[key] = value;
    });
    return vars;
}

function set_cookie(cookiename, cookievalue) {
    var domain = window.location.hostname.substring(window.location.host.indexOf(".") + 1);

    if(window.location.hostname.split(".").length==2){
        domain = window.location.hostname;
    }

    document.cookie = cookiename + "=" + cookievalue + ";domain=" + domain;
}

function get_csrf_token() {
    var CSRF_TOKEN = $('input[name="csrfmiddlewaretoken"]').val();
    return CSRF_TOKEN;
}


function get_cookie(cookiename) {
    var cookie_name = cookiename + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var cookie_array = decodedCookie.split(';');
    for(let i = 0; i < cookie_array.length; i++) {
        var c = cookie_array[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(cookie_name) == 0) {
            return c.substring(cookie_name.length, c.length);
        }
    }
    return "";
}

// send_form_assist_recommendation() if "do not distrub" is true
function send_form_assist_recommendation(bot_id, bot_name, form_assist_id) {
    append_bot_text_response("It looks like you are stuck here. Do you need any assistance");
    var recommendations_list = ["Need Form Assistance", "Chat with the Bot"]
    append_bot_recommendation(recommendations_list)
}

//show_form_assist_result()
function show_form_assist_result() {
    var url_parameters = get_url_vars();
    bot_id = url_parameters["id"];
    bot_name = url_parameters["name"];
    var form_assist_id = url_parameters["form_assist_id"];
    session_id = get_cookie("easychat_session_id");
    set_cookie("isFeedbackDone", "0")
    // window_location = window.top.location.href;
    window_location = url_parameters["easychat_window_location"]
    if (window_location == undefined) {
        window_location = 'localhost'
    }
    default_bot_color(bot_id);
    setTimeout(function(e) {
        if (form_assist_id != null && form_assist_id != undefined && form_assist_id != "") {
            form_assist_enabled = true;
            form_assist_id = decodeURI(form_assist_id);
            send_message_to_server(form_assist_id, user_id, bot_id, bot_name, "None");
            scroll_to_bottom();
        } else {
            append_welcome_message(bot_id, bot_name);
            get_suggestion_list(bot_id, bot_name);
        }
    }, 1000);
}

// function start_chatbot(){
window.onload = function(e) {
    document.getElementsByClassName("easyassist-chat-loader")[0].remove();
    // changeMiddleContainer();
    document.getElementById("easychat-navbar-wrapper").style.backgroundColor = BOT_THEME_COLOR;
    document.getElementById("user_input").style.borderColor = BOT_THEME_COLOR;
    document.getElementById("model-feedback-header").style.color = BOT_THEME_COLOR;
    document.getElementById("img-scroll-to-bottom").style.color = BOT_THEME_COLOR;
    document.getElementById("easyassist-chat-box-body").style.display = "flex";
    if (agent_to_customer_cobrowsing == "True") {
        append_system_text_response("Hi, to start a conversation with our Customer Service Agent, simply send a message through this chat window");                
    }else{
        append_system_text_response("Hi, now assist your customer with our real time live chat facility. Simply send a message through this chat window to start a conversation with the customer.");        
    }
}

function close_feedback_modal() {
    document.getElementById("feedback_modal").style.display = "none";
}

function restart_chatbot(el) {
    if(livechat_queue_timer){
        clearInterval(livechat_queue_timer);
    }
    remove_queue_timer();
    el.style.color = BOT_THEME_COLOR;
    // clear_userData();
    var myNode = document.querySelectorAll("#easychat-chat-container div");
    for (let i = 0; i < myNode.length; i++) {
        myNode[i].remove();
    }
    url_parameters = get_url_vars();
    bot_id = url_parameters["id"];
    bot_name = url_parameters["name"];
    session_id = get_cookie("easychat_session_id");
    // window_location = window.location.href;
    window_location = url_parameters["easychat_window_location"]
    if (window_location == undefined) {
        window_location = 'localhost'
    }
    append_welcome_message(bot_id, bot_name);
    get_suggestion_list(bot_id, bot_name);
    setTimeout(function() {
        el.style.color = "#808080";
    }, 1000);
}

function minimize_chatbot() {
    close_chatbot();
    parent.postMessage('minimize-chatbot', '*');
}

function close_chatbot(is_nps_required) {
    try {
        modal_create_issue.style.display = "none";
        modal_check_ticket_status.style.display = "none";
        modal_check_meeting_status.style.display = "none";
        modal_schedule_meeting.style.display = "none";
    } catch (err) {
        console.log(err)
    }
    try {
        document.getElementById("modal-send-attachement-modal").style.display = "none";
    } catch(err) {
        console.log(err);
    }

    cancel_text_to_speech();
    // console.log(is_nps_required)
    if (is_nps_required == "True" && user_id != "" && get_cookie("isFeedbackDone") == "0") {
        document.getElementById("feedback_modal").style.display = "block";
        if (detectIEEdge()) {
            document.getElementById("easychat-rating-circular-bar__xyzw").style.display = "none";
        } else {
            document.getElementById("rating-bar-container__XqPZ").style.display = "none";
        }
    } else {
        // clear_userData();
        parent.postMessage('close-bot', '*');
    }
}


// ##############   FeedBack #######################


function change_content(el) {
    let contentvalue = parseInt(el.getAttribute("value"))
    if (contentvalue <= 2)
        document.getElementById("easychat-rating-circular-bar-content-img").setAttribute("src", EASYCHAT_IMG_PATH + "Very_Sad_Face_Emoji_Icon_ios10_large.webp")
    else if (contentvalue > 2 && contentvalue <= 5)
        document.getElementById("easychat-rating-circular-bar-content-img").setAttribute("src", EASYCHAT_IMG_PATH + "face-with-one-eyebrow-raised_1f928.png")
    else if (contentvalue > 5 && contentvalue <= 8) {
        document.getElementById("easychat-rating-circular-bar-content-img").setAttribute("src", EASYCHAT_IMG_PATH + "no_reaction.png")
    } else if (contentvalue >= 9) {
        document.getElementById("easychat-rating-circular-bar-content-img").setAttribute("src", EASYCHAT_IMG_PATH + "Smiling_Face_Emoji_large.webp")
    }

}

var contentvalue = 0;

function feedback_modal(el) {
    var temp_value = document.getElementsByClassName("circle-value")
    document.getElementById("easychat-exit-app-feedback").style.display = "none";
    for(let i = 0; i < temp_value.length; i++) {
        temp_value[i].style.strokeWidth = "1.5em"
    }
    el.style.strokeWidth = "2em"
    contentvalue = parseInt(el.getAttribute("value"))
    if (contentvalue < 10) {
        document.getElementById("value-0" + el.getAttribute("value")).style.strokeWidth = "2em"
    } else {
        document.getElementById("value-" + el.getAttribute("value")).style.strokeWidth = "2em"
    }
    document.getElementById("chatbot_feedback_comment_box").style.display = "block";
}

function no_feedback_given(e) {
    document.getElementById("feedback_modal").style.display = "none";
    // clear_userData();
    parent.postMessage('close-bot', '*');
}

function submit_feedback() {
    text_value = document.getElementById("chatbot-comment-box").value;
    text_value = stripHTML(text_value);
    text_value = remove_special_characters_from_str(text_value);
    document.getElementById("feedback_modal").style.display = "none";
    save_feedback(contentvalue, text_value)
}

function save_feedback(contentvalue, text_value) {
    var json_string = JSON.stringify({
        session_id: session_id,
        user_id: user_id,
        bot_id: bot_id,
        rating: contentvalue,
        comments: text_value
    });
    set_cookie("isFeedbackDone", "1")
    close_chatbot()
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
    xhttp.open("POST", "/chat/save-feedback/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log("Feedback saved!!!");
        }
    }
    xhttp.send(params);
}

// ######################################################

function disable_user_input() {
    document.getElementById("user_input").disabled = true;
}

function enable_user_input() {
    document.getElementById("user_input").disabled = false;
}

function focus_user_input() {
    var field = document.getElementById("user_input");
    field.focus();
}

function blur_user_input() {
    document.getElementById("user_input").blur();
}

function hide_mic_icon() {
    document.getElementById("easychat-mic-div").style.display = "none";
    document.getElementById("mic-span").style.marginRight = "";
}

function show_mic() {

    document.getElementById("easychat-mic-div").style.display = "inline-block";
}

function activate_mic() {

    document.getElementById("easychat-mic-div").style.opacity = "0.5";
    document.getElementById("user_input").placeholder = "Speak now";
    document.getElementById("easychat-query-submit-div").style.display = "none";
    if(document.getElementById("easychat-upload-doc-div")) {
        document.getElementById("easychat-upload-doc-div").style.display = "none";
    }
    document.getElementById("easychat-mic-disable").style.display = "flex";
    disable_user_input();
    if (recognition != null) {
        recognition.start();
    } else {
        hide_mic_icon();
    }
}

function deactivate_mic() {

    document.getElementById("easychat-mic-div").style.opacity = "1";
    document.getElementById("mic-span").style.marginRight = "";
    if(initialize_canned_response == "True"){
        document.getElementById("user_input").placeholder = "Type ‘/’ to add a canned response";
    } else {
        document.getElementById("user_input").placeholder = EASYCHAT_INPUT_QUERY_DEFAULT_PLACEHOLDER;
    }
    document.getElementById("easychat-query-submit-div").style.display = "";
    if(document.getElementById("easychat-upload-doc-div")) {
        document.getElementById("easychat-upload-doc-div").style.display = "";
    }
    document.getElementById("easychat-mic-disable").style.display = "none";
    enable_user_input();
    if (recognition != null) {
        recognition.abort();
        recognition.continuous = false;
        recognition = null;
    } else {
        hide_mic_icon();
    }
}

function activate_query_submit_button() {
    document.getElementById("img-submit-query").disabled = false;
}

function deactivate_query_submit_button() {
    document.getElementById("img-submit-query").disabled = true;
}

function scroll_to_bottom() {
    setTimeout(function(e){
        var objDiv = document.getElementById("easychat-chat-container");
        objDiv.scrollTop = objDiv.scrollHeight;
    }, 500);
}

function scroll_to_bottom_instant() {
    var objDiv = document.getElementById("easychat-chat-container");
    objDiv.scrollTop = objDiv.scrollHeight;
}

function return_time() {
    var d = new Date();
    var hours = d.getHours().toString();
    var minutes = d.getMinutes().toString();
    var flagg = "AM";
    if (parseInt(hours) > 12) {
        hours = hours - 12;
        flagg = "PM";
    }
    if (hours.length == 1) {
        hours = "0" + hours;
    }
    if (minutes.length == 1) {
        minutes = "0" + minutes;
    }

    var time = hours + ":" + minutes + " " + flagg;
    return time;
}

function viewMore(element) {
    element.parentNode.previousElementSibling.children[0].classList.add("easychat-expand-text");
    element.setAttribute("onclick", "showLess(this)")
    element.innerHTML = 'Show Less<i class="fa fa-chevron-up" style="color:' + BOT_THEME_COLOR + ';margin-left:5px"></i></div>'
}

function showLess(element) {
    element.parentNode.previousElementSibling.children[0].classList.remove("easychat-expand-text");
    element.setAttribute("onclick", "viewMore(this)")
    element.innerHTML = 'View More<i class="fa fa-chevron-down" style="color:' + BOT_THEME_COLOR + ';margin-left:5px"></i></div>'
}

function append_bot_text_response(text_response, name=null, time=null, agent_profile_pic_source) {
    let html;
    if(time == null)
        time = return_time()
    if(name == null)
        name = "bot"

        let msg_sender_icon = "";
        let profile = "";
    
        if (window.DISPLAY_AGENT_PROFILE == "True" && agent_profile_pic_source != "" && agent_profile_pic_source != undefined) {
            let src = "/"  + agent_profile_pic_source;
            profile = '<img src = "' + src + '"/>';
        }
    
        if (agent_to_customer_cobrowsing == "True") {
            if (profile != "") {
                msg_sender_icon = profile;
            } else {
                msg_sender_icon = ['<svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">',
                    '<path d="M20 6.99892C20.5304 6.99892 21.0391 7.20964 21.4142 7.58471C21.7893 7.95978 22 8.46849 22 8.99892V12.9989C22 13.5294 21.7893 14.0381 21.4142 14.4131C21.0391 14.7882 20.5304 14.9989 20 14.9989H18.938C18.6942 16.9322 17.7533 18.7101 16.2917 19.9989C14.8302 21.2877 12.9486 21.9989 11 21.9989V19.9989C12.5913 19.9989 14.1174 19.3668 15.2426 18.2416C16.3679 17.1163 17 15.5902 17 13.9989V7.99892C17 6.40762 16.3679 4.8815 15.2426 3.75628C14.1174 2.63106 12.5913 1.99892 11 1.99892C9.4087 1.99892 7.88258 2.63106 6.75736 3.75628C5.63214 4.8815 5 6.40762 5 7.99892V14.9989H2C1.46957 14.9989 0.960859 14.7882 0.585786 14.4131C0.210714 14.0381 0 13.5294 0 12.9989V8.99892C0 8.46849 0.210714 7.95978 0.585786 7.58471C0.960859 7.20964 1.46957 6.99892 2 6.99892H3.062C3.30603 5.06582 4.24708 3.2882 5.70857 1.9996C7.17007 0.711003 9.05155 0 11 0C12.9484 0 14.8299 0.711003 16.2914 1.9996C17.7529 3.2882 18.694 5.06582 18.938 6.99892H20ZM6.76 14.7839L7.82 13.0879C8.77308 13.685 9.87537 14.0007 11 13.9989C12.1246 14.0007 13.2269 13.685 14.18 13.0879L15.24 14.7839C13.9693 15.5801 12.4995 16.0012 11 15.9989C9.50046 16.0012 8.03074 15.5801 6.76 14.7839Z" fill="white"/>',
                    '</svg>',
                ].join('');
            }
        } else {
            if (profile != "") {
                msg_sender_icon = profile;
            } else {
                msg_sender_icon = [
                    '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">',
                    '<path d="M4.5 4.26316C4.5 6.61358 6.519 8.52632 9 8.52632C11.481 8.52632 13.5 6.61358 13.5 4.26316C13.5 1.91274 11.481 0 9 0C6.519 0 4.5 1.91274 4.5 4.26316ZM17 18H18V17.0526C18 13.3967 14.859 10.4211 11 10.4211H7C3.14 10.4211 0 13.3967 0 17.0526V18H17Z" fill="white"></path>',
                    '</svg>',
                ].join('');
            }
        }
    
        if (agent_to_customer_cobrowsing == "True") {
            html = ['<div class="easychat-bot-message-div">',
                '<div style="display: flex; flex-direction: row;">',
                '<div class="easychat-bot-msg-sender-profile" style="background-color: ' + BOT_THEME_COLOR + '">',
                msg_sender_icon,
                '</div>',
                '<div class="easychat-bot-message" style="color: ' + BOT_MESSAGE_COLOR + ';">',
                '<div class="easychat-bot-message-name" style="color: ' + BOT_THEME_COLOR + '">' + name + '</div>',
                '<div class="easychat-bot-message-line">',
                '<div class="easychat-show-less-text">' + text_response + '</div>',
                '</div>',
                '<div class=view_more_wrapper style="margin-right:5px;display:none ">',
                '<div style="margin-right: 12px !important;padding-bottom: 7px;float:right;cursor: pointer;" onclick="viewMore(this)">',
                'View More<i class="fa fa-chevron-down" style="color:' + BOT_THEME_COLOR + ';margin-left:5px"></i>',
                '</div>',
                '</div>',
                '</div>',
                '</div>',
                '<span class="message-time-bot">' + time + '</span>',
                '</div>',
            ].join(' ');
        } else {
            html = ['<div class="easychat-bot-message-div">',
                '<div style="display: flex; flex-direction: row;">',
                '<div class="easychat-bot-msg-sender-profile" style="background-color: ' + BOT_THEME_COLOR + '">',
                msg_sender_icon,
                '</div>',
                '<div class="easychat-bot-message" style="color: ' + BOT_MESSAGE_COLOR + ';">',
                '<div class="easychat-bot-message-name" style="color: ' + BOT_THEME_COLOR + '">' + name + '</div>',
                '<div class="easychat-bot-message-line">',
                '<div class="easychat-show-less-text">' + text_response + '</div>',
                '</div>',
                '<div class=view_more_wrapper style="margin-right:5px;display:none ">',
                '<div style="margin-right: 12px !important;padding-bottom: 7px;float:right;cursor: pointer;" onclick="viewMore(this)">',
                'View More<i class="fa fa-chevron-down" style="color:' + BOT_THEME_COLOR + ';margin-left:5px"></i>',
                '</div>',
                '</div>',
                '</div>',
                '</div>',
                '<span class="message-time-bot">' + time + '</span>',
                '</div>',
            ].join(' ');
        }

    document.getElementById("easychat-chat-container").innerHTML += html;

    setTimeout(function(e) {
        reset_size_of_text_field();
    }, 200);
}

function reset_size_of_text_field() {
    let viewmore_height = document.getElementsByClassName('easychat-show-less-text')[document.getElementsByClassName('easychat-show-less-text').length - 1].scrollHeight;
    if (viewmore_height > 300) {
        document.getElementsByClassName('view_more_wrapper')[document.getElementsByClassName('view_more_wrapper').length - 1].style.display = 'block';
    }
}

function reset_size_of_text_field_all(){
    var elements = document.getElementsByClassName('easychat-show-less-text');
    for(let index=0 ; index<elements.length ; index++){
        let viewmore_height = elements[index].scrollHeight
        if(viewmore_height>300){
            document.getElementsByClassName('view_more_wrapper')[index].style.display='block';
        }
    }
}

function append_system_text_response(text_response) {

    var time = return_time();
    var html = '<div class="easychat-system-message-div" ><div class="easychat-system-message easychat-system-message-line" style="color:' + BOT_MESSAGE_COLOR + '" >' + text_response
    document.getElementById("easychat-chat-container").innerHTML += html
}

// ******************* File attachment Livechat ***************************

function append_file_to_customer(url, message) {

    if (message != "") {
        if (is_image(url) || is_video(url)) {

            document.getElementById("easychat-chat-container").innerHTML += '<div style="width:98%;display:inline-block;"><div class="easychat-livechat-customer-attachment">' + get_file_path_html(url) + '<div class="easychat-livechat-message">' + message + '</div></div></div>'
        } else {

            document.getElementById("easychat-chat-container").innerHTML += '<div style="margin:5px 0px 5px 0px;width:98%;display:inline-block;"><div class="easychat-livechat-user-doc-attachment"><div class="easychat-livechat-doc-attachment-content">' + get_doc_path_html(url) + '</div><div class="easychat-livechat-message">' + message + '</div></div></div>'
        }
    } else {

        if (is_image(url) || is_video(url)) {

            document.getElementById("easychat-chat-container").innerHTML += '<div style="width:98%;display:inline-block;"><div class="easychat-livechat-customer-attachment">' + get_file_path_html(url) + '</div></div>'
        } else {

            document.getElementById("easychat-chat-container").innerHTML += '<div style="margin:5px 0px 5px 0px;width:98%;display:inline-block;"><div class="easychat-livechat-user-doc-attachment"><div class="easychat-livechat-doc-attachment-content">' + get_doc_path_html(url) + '</div></div></div>'
        }
    }
    setTimeout(function() {
        scroll_to_bottom();
    }, 1000);
}

function get_file_path_html(attached_file_src) {
    var html = '';
    if (is_image(attached_file_src)) {
        html = '<a href="' + attached_file_src + '" download><img src="' + window.location.origin + attached_file_src + '" style="height: 100%;width: 100%;border-radius: 1em;object-fit: cover;"></a>';
    } else {
        html = '<a href="' + attached_file_src + '" download><video style="width: 100%;height:100%;border-radius: 1em;" class="easychat-livechat-attached-video" controls><source src="' + window.location.origin + attached_file_src + '" type="video/mp4"></video></a>';
    }
    return html;
}

function get_doc_path_html(url) {

    var html = '<a href="' + url + '" download><img src="/static/LiveChatApp/img/documents2.png" style="height: 100%;width: 100%;border-radius: 1em;object-fit: contain;"></a>';
    return html
}

function is_image(attached_file_src) {

    let file_ext = attached_file_src.split(".")
    file_ext = attached_file_src.split(".")[file_ext.length - 1]

    if (["png", "jpg", "jpeg", "svg", "bmp", "gif", "tiff", "exif", "jfif"].indexOf(file_ext) != -1) {
        return true;
    }

    return false;
}

function is_video(attached_file_src) {

    file_ext = attached_file_src.split(".")
    file_ext = attached_file_src.split(".")[file_ext.length - 1]
    file_ext = file_ext.toUpperCase()
    if (["WEBM", "MPG", "MP2", "MPEG", "MPE", "MPV", "OGG", "MP4", "M4P", "M4V", "AVI", "WMV", "MOV", "QT", "FLV", "SWF", "AVCHD"].indexOf(file_ext) != -1) {

        return true;
    }

    return false;
}
// ************************************************************************

var urlRegex =/(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
function show_hyperlink_inside_text(text) {
        return text.replace(urlRegex, function(url) {
            return '<a href="' + url +'" target="_blank">' + url + '</a>';
        });
}

function send_user_input(user_input) {

    user_input = stripHTML(user_input);
    if(check_text_link(user_input)) {
        user_input = easyassist_linkify(user_input);
    } else {
        user_input = remove_special_characters_from_str(user_input);
    }

    if(!user_input || user_input.trim() == "") {
        return;
    }

    var time = return_time();

    if (agent_to_customer_cobrowsing == "True") {
        document.getElementById("easychat-chat-container").innerHTML += [
            '<div class="easychat-user-message-div">',
                '<div class="easychat-user-message" style="background-color:' + BOT_THEME_COLOR + ';color: ' + USER_MESSAGE_COLOR + '">',
                    '<div class="easychat-user-message-line">',
                        user_input,
                    '</div>',
                '</div>',
                '<span class="message-time-user">' + time + '</span>',
            '</div>',
        ].join('');
    } else {
        document.getElementById("easychat-chat-container").innerHTML += [
            '<div class="easychat-user-message-div">',
                '<div class="easychat-user-message" style="background-color:' + BOT_THEME_COLOR + ';color: ' + USER_MESSAGE_COLOR + '">',
                    '<div class="easychat-user-message-line">',
                        user_input,
                    '</div>',
                '</div>',
                '<span class="message-time-user">' + time + '</span>',
            '</div>'
        ].join('');
    }

    scroll_to_bottom();

    is_doubletick = true;

    parent.postMessage({
        event_id: 'cobrowsing-agent-chat-message',
        data: {
            message: user_input,
            attachment: attached_file_src,
            attachment_file_name: attachment_file_name,
            time: time
        }
    }, "*");
    attached_file_src = "None";
    attachment_file_name = "None";

    deactivate_query_submit_button()
}

function append_captcha(url) {
    let captcha_element = document.getElementById("recaptcha-div");
    if (captcha_element != null || captcha_element != undefined) {
        captcha_element.remove();
    }
    let captcha_html = '<div class="easychat-captcha-div" id="recaptcha-div" align="center">\
        <img src="/' + url + '" id="img-captcha">\
        </div>';
    document.getElementById("easychat-chat-container").innerHTML += captcha_html;
    scroll_to_bottom();
    scroll_to_bottom();
}


function create_captcha() {
    var xhttp = new XMLHttpRequest();
    var params = '';
    xhttp.open("POST", "/chat/get_captcha/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            if (response["status"] == 200) {
                captcha_id = response["random"];
                append_captcha(response["url"]);
                scroll_to_bottom();
            }
        }
    }
    xhttp.send(params);
}

function get_quotes_suggestions(query_code) {
    if (custom_quote_list_flag != query_code) {
        var json_string = JSON.stringify({
            query_code: query_code
        });
        // json_string = encrypt_variable(json_string);
        // json_string = encodeURIComponent(json_string);

        var xhttp = new XMLHttpRequest();
        // var params = 'json_string='+json_string
        var params = 'query_code=' + query_code
        xhttp.open("POST", "/chat/get-quote-codes/", true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                if (response["status"] == 200) {
                    code_list = response["code_list"];
                    custom_quote_list_flag = query_code
                    //custom_autocomplete(document.getElementById("user_input"), code_list)
                }
            }
        }
        xhttp.send(params);
    }
}

function verify_captcha(user_input) {
    var xhttp = new XMLHttpRequest();
    var params = 'random=' + captcha_id;
    xhttp.open("POST", "/chat/get_captcha_value/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            if (response["status"] == 200) {
                // console.log(String(user_input), String(response['value']));
                if (String(user_input) == String(response['value'])) {
                    is_captcha = null;
                    send_message_to_server("correct", user_id, bot_id, bot_name, "None")
                } else {
                    create_captcha();
                    scroll_to_bottom();
                }
            }
        }
    }
    xhttp.send(params);
}

function append_recaptcha() {
    create_captcha();
}

function handle_input_type(modes, modes_param) {
    var input_maxlength = "5000000";
    var is_numeric = '';
    if ('is_numeric_input' in modes) {

        is_numeric = modes['is_numeric_input'];
    }

    if ('input_maxlength' in modes_param) {
        input_maxlength = modes_param['input_maxlength'];
    }

    if (is_numeric == "true") {
        document.getElementById("user_input").type = "number";
        hide_mic = true;
    } else {
        document.getElementById("user_input").type = "text";
    }

    document.getElementById("user_input").maxlength = input_maxlength;
}


function append_google_map_location() {
    let map_element = document.getElementById("google-map");
    if (map_element != null || map_element != undefined) {
        map_element.remove();
    }

    let location_html = '<div class="easychat-gmap-wrapper" id="google-map">\
        <div id="map" class="easychat-gmap-div"></div>\
    </div>';
    document.getElementById("easychat-chat-container").innerHTML += location_html;

    var script = document.createElement("script");
    script.src = "https://maps.googleapis.com/maps/api/js?key=AIzaSyBAHTtk1lkVvIl1X_i7_1aIK9RCrhqGEpQ&libraries=places&callback=initMap";
    document.getElementById("google-map").appendChild(script);
    is_map_js_loaded = true;
}


function get_message_list(message, separator) {
    var message_list = message.split(separator);
    return message_list;
}


var speech_synthesis_utterance_instance = null;
var speech_synthesis_instance = window.speechSynthesis;
var voices = null;

function cancel_text_to_speech() {
    if (speech_synthesis_instance != null) {
        speech_synthesis_instance.cancel();
    }
}

function text_to_speech(message_to_be_spoken) {
    cancel_text_to_speech();
    message_to_be_spoken = message_to_be_spoken.replace(/<[^>]*>?/gm, '');
    speech_synthesis_utterance_instance = new SpeechSynthesisUtterance(message_to_be_spoken);
    speech_synthesis_utterance_instance.lang = "en-US";
    speech_synthesis_utterance_instance.rate = 0.95;
    speech_synthesis_utterance_instance.pitch = 1;
    speech_synthesis_utterance_instance.volume = 1;
    voices = speech_synthesis_instance.getVoices();
    speech_synthesis_instance.speak(speech_synthesis_utterance_instance);
}

function detectmob() {
    if (window.outerWidth < 450) {
        blur_user_input();
    } else {
        enable_user_input();
        focus_user_input();
    }
}

function append_bot_response(response) {
    hide_mic = false;
    var server_reply = response.response.text_response.text;
    var speech_response = response.response.speech_response.text;
    var is_text_to_speech_required = response.response.is_text_to_speech_required;
    disable_user_input();

    if (is_text_to_speech_required == true && speech_response != "") {
        text_to_speech(speech_response);
    }

    if (is_doubletick) {
        var easychat_doubletick_list = document.getElementsByClassName("doubletick_easychat");
        easychat_doubletick_list[easychat_doubletick_list.length - 1].src = EASYCHAT_IMG_PATH + 'doubletick_blue.svg';
    }

    var recommendations = response.response.recommendations;
    var choices = response.response.choices;
    var cards = response.response.cards;
    var videos = response.response.videos;
    var images = response.response.images;
    var tables = response.response.tables;

    var easy_search_results = response.response.easy_search_results;

    is_flow_ended = response.response.is_flow_ended;


    if (is_flow_ended) {
        autocomplete(document.getElementById("user_input"), suggestion_list, []);
    }

    var modes = response.response.text_response.modes;
    var modes_param = response.response.text_response.modes_param;

    if ("is_livechat" in modes && modes["is_livechat"] == "true") {
        if (window.hasOwnProperty("WebSocket") == false) {
            return;
        }
    }

    if ("enable_screenshare" in modes && modes["enable_screenshare"] == "true") {
        show_connect_with_agent_modal();
        return;
    }

    let is_quote_response = false;
    if ("is_quote_response" in modes && modes["is_quote_response"] == "true") {
        is_quote_response = true
    }

    let is_tms_intent = false
    if (("raise_service_request" in modes && modes["raise_service_request"] == "true") || ("schedule_meeting" in modes && modes["schedule_meeting"] == "true") || ("check_meeting_status" in modes && modes["check_meeting_status"] == "true") || ("check_ticket_status" in modes && modes["check_ticket_status"] == "true")) {
        is_tms_intent = true
    }

    if (is_tms_intent == false) {
        message_list = get_message_list(server_reply, RESPONSE_SENTENCE_SEPARATOR);
        for(let i = 0; i < message_list.length; i++) {
            append_bot_text_response(message_list[i]);
        }
    }

    if ("auto_trigger_last_intent" in modes && modes["auto_trigger_last_intent"] == "true") {
        if (last_identified_intent != null && last_identified_intent != "None") {
            send_message_to_server(last_identified_intent, user_id, bot_id, bot_name, "None");
            return;
        }
    }

    if ("form_assist_disable" in modes && modes["form_assist_disable"] == "true") {
        parent.postMessage('disable-form-assist', '*');
        return;
    }

    if ("check_ticket_status" in modes && modes["check_ticket_status"] == "true") {
        modal_check_ticket_status.style.display = "block";
        disable_user_input();
        return;
    }

    if ("check_meeting_status" in modes && modes["check_meeting_status"] == "true") {
        modal_check_meeting_status.style.display = "block";
        disable_user_input();
        return;
    }

    if ("raise_service_request" in modes && modes["raise_service_request"] == "true") {
        modal_create_issue.style.display = "block";
        disable_user_input();
        return;
    }

    if (response.is_attachment_required == true) {
        var choosen_file_type = response.choosen_file_type;
        choosen_file_type = choosen_file_type.replace(/"/g, '');
        let choosen_file_ext = file_type_ext[choosen_file_type];
        append_attachment(choosen_file_ext, is_flow_ended);
    }

    if ("raise_service_request" in modes && modes["raise_service_request"] == "true") {
        modal_create_issue.style.display = "block";
        disable_user_input();
        return;
    }

    if ("schedule_meeting" in modes && modes["schedule_meeting"] == "true") {
        modal_schedule_meeting.style.display = "block";
        disable_user_input();
        return;
    }

    if ("is_livechat" in modes && modes["is_livechat"] == "true") {
        if (window.hasOwnProperty("WebSocket") == true) {
            append_livechat_response();
        }
        return;
    }

    if ("is_typable" in modes) {
        if (modes["is_typable"] == "true") {
            enable_user_input();
            focus_user_input();
            handle_input_type(modes, modes_param);
            //focus_user_input();
        } else {
            disable_user_input();
        }
    }

    if (cards.length > 0) {
        append_bot_slider_cards(cards);
    }

    if (easy_search_results != null && easy_search_results != undefined && easy_search_results.length > 0) {

        append_bot_slider_cards(easy_search_results);
    }

    if ("is_recaptcha" in modes && modes["is_recaptcha"] == "true") {
        append_recaptcha();
        is_captcha = true;
        hide_mic = true;
        handle_input_type(modes, modes_param);
    }

    if ("is_location_required" in modes && modes["is_location_required"] == "true") {
        append_google_map_location();
    }

    is_custom_complete = false
    if ("is_custom_complete" in modes && modes["is_custom_complete"] == "true") {
        start_custom_complete();
        is_custom_complete = true
    }

    if ("is_datepicker" in modes && modes["is_datepicker_required"] == "true") {
        // DatePicker input format [{"placeholder":"From Date"}, {"placeholder":"To Date"}]
        append_datepicker(modes_param["datepicker_list"]);
    }

    if ("is_range_slider" in modes && modes["is_range_slider"] == "true") {
        // Input Range Slider list format [{"placeholder":"Loan Amount", "min":50000, "max":640000}]
        append_bot_range_slider(modes_param["range_slider_list"]);
    }

    if (tables != undefined && tables != null && tables.length > 0) {
        append_bot_tables(tables);
    }

    if (images.length > 0) {
        append_bot_slider_images(images);
    }

    if (videos.length > 0) {
        append_bot_slider_videos(videos);
    }

    if (choices.length > 0) {
        append_bot_choices(choices);
    }

    if (recommendations.length > 0) {
        append_bot_recommendation(recommendations);
    }

    if ("is_feedback_required" in response["response"]) {
        var is_feedback_required = response["response"]["is_feedback_required"]
        if (is_feedback_required) {
            var feedback_id = response["response"]["feedback_id"]
            append_feedback_btns(feedback_id)
        }
    }

    scroll_to_bottom();
    deactivate_mic();
    deactivate_query_submit_button();

    if (recognition != null) {
        if (hide_mic == true) {
            hide_mic_icon();
        } else {
            show_mic();
        }
    } else {
        hide_mic_icon();
    }

    setTimeout(function(e) {
        scroll_to_bottom();
    }, 500);
}

function start_custom_complete() {
    custom_autocomplete(document.getElementById("user_input"), [])
    
}

function append_bot_slider_videos(video_url_list) {
    if (video_url_list.length > 0) {
        let slider_main_container = document.getElementById("easychat-slideshow-container-main-div");
        if (slider_main_container != undefined && slider_main_container != null) {
            slider_main_container.remove();
        }

        let video_html = '<div class="easychat-slider-wrapper">\
        <div style="color:' + BOT_THEME_COLOR + '; width: 80%;margin: auto;"><div class="slideshow-container"  value=1 >';
        let total_video = video_url_list.length;

        for(let i = 0; i < video_url_list.length; i++) {
            let current_video_no = i + 1;
            if (i == 0) {
                video_html += '<div class="mySlides fade" >'
                if (video_url_list[i].indexOf("embed") != -1) {
                    video_html += '<div class="video-container">\
                      <iframe class="easychat-video-iframe" src="' + video_url_list[i] + '" frameborder="1" allowfullscreen></iframe>\
                    </div>';
                } else {
                    video_html += '<video width="325" height="200" style="border-radius: 1em;" controls>\
                      <source src="' + video_url_list[i] + '" type="video/mp4">\
                    </video>';
                }
            } else {
                video_html += '<div class="mySlides fade" style="display: none;">'
                if (video_url_list[i].indexOf("embed") != -1) {
                    video_html += '<div class="video-container">\
                      <iframe class="easychat-video-iframe" src="' + video_url_list[i] + '" frameborder="1" allowfullscreen></iframe>\
                    </div>';
                } else {
                    video_html += '<video width="325" height="200" style="border-radius: 1em;" controls>\
                      <source src="' + video_url_list[i] + '" type="video/mp4">\
                    </video>';
                }
            }
            if (video_url_list.length != 1) {
                video_html += '<div class="pageno-co">' + current_video_no + ' / ' + total_video + '</div></div>';
            } else {
                video_html += '</div>'
            }

        }
        if (video_url_list.length != 1) {
            video_html += '<a class="prev-image-video" onclick="plusImageSlides(-1,this)">&#10094;</a>\
            <a class="next-image-video" onclick="plusImageSlides(1,this)">&#10095;</a>\
            </div><script>showSlides(1,this);</script><br><div style="text-align:center"></div>';
        }
        video_html += '</div></div>';

        document.getElementById("easychat-chat-container").innerHTML += video_html;


    }
}

function append_bot_slider_images(image_url_list) {

    slider_main_container = document.getElementById("easychat-slideshow-container-main-div");
    if (slider_main_container != undefined && slider_main_container != null) {
        slider_main_container.remove();
    }

    let image_slidershow_html = '<div class="easychat-slider-wrapper">\
    <div style="color:' + BOT_THEME_COLOR + '; width: 80%;margin: auto;"><div class="slideshow-container"  value=1 >';
    let total_images = image_url_list.length;

    for(let i = 0; i < image_url_list.length; i++) {
        let current_image_no = i + 1;
        if (i == 0) {
            image_slidershow_html += '<div class="mySlides fade" >'
        } else {
            image_slidershow_html += '<div class="mySlides fade" style="display: none;">'
        }
        if (image_url_list.length != 1) {
            image_slidershow_html += '<div class="pageno-co">' + current_image_no + ' / ' + total_images + '</div>\
            <img src="' + image_url_list[i] + '" class="easychat-image-el">\
          </div>';
        } else {
            image_slidershow_html += '<img src="' + image_url_list[i] + '" class="easychat-image-el" ></div>';
        }
    }
    if (image_url_list.length != 1) {
        image_slidershow_html += '<a class="prev-image-video" onclick="plusImageSlides(-1,this)">&#10094;</a>\
        <a class="next-image-video" onclick="plusImageSlides(1,this)">&#10095;</a>\
        </div><script>showSlides(1,this);</script><br><div style="text-align:center"></div>';
    }
    image_slidershow_html += '</div></div>';


    document.getElementById("easychat-chat-container").innerHTML += image_slidershow_html;

}

function append_bot_slider_cards(cards) {
    var cards_html = '<div class="easychat-card-slider-wrapper"><div>'
    if (cards[0]["content"] == "" && cards[0]["img_url"] == "") {
        for(let i = 0; i < cards.length; i++) {
            cards_html += '<a href="' + cards[i]["link"] + '" target="_blank" style="color:black;"><div class="easychat-card">\
                <div class="container" onmouseover="custom_button_change_card(this)" onmouseout="custom_button_change_normal_card(this)">\
                    <b>' + cards[i]["title"] + '</b>\
                </div>\
                </div></a>';
        }
    } else if (cards[0]["img_url"] == "") {
        cards_html = '<div style="color:' + BOT_THEME_COLOR + ';" class="easychat-slides-wrapper"><div class="slideshow-container"  value=1 >';
        total_images = cards.length;

        for(let i = 0; i < cards.length; i++) {
            current_image_no = i + 1;
            if (i == 0) {
                cards_html += '<div onclick="'
                cards_html += "window.open('" + cards[i]["link"] + "');"
                cards_html += '"  class="mySlides fade easychat-slider-card" >'
            } else {
                cards_html += '<div onclick="'
                cards_html += "window.open('" + cards[i]["link"] + "');"
                cards_html += '"  class="mySlides fade easychat-slider-card" style="display: none;">'
            }
            if (cards.length != 1) {
                cards_html += '<div class="pageno-co">' + current_image_no + ' / ' + total_images + '</div>'
                if (cards[i]["title"].length > 25) {
                    var cards_title = cards[i]["title"].slice(0, 25) + " ..."
                    cards_html += '<h5>' + cards_title + '</h5>'
                } else {
                    cards_html += '<h5>' + cards[i]["title"] + '</h5>'
                }
                if (cards[i]["content"].length > 300) {
                    cards_html += '<p>' + (cards[i]["content"].slice(0, 300) + " ... ") + '</p></div>'
                } else {
                    cards_html += '<p>' + cards[i]["content"] + '</p></div>'
                }


            } else {
                cards_html += '<h5>' + cards[i]["title"] + '</h5><p>' + cards[i]["content"] + '</p></div>';
            }
        }
        if (cards.length != 1) {
            cards_html += '<a class="prev-image-video" onclick="plusImageSlides(-1,this)">&#10094;</a>\
                <a class="next-image-video" onclick="plusImageSlides(1,this)">&#10095;</a>\
                </div><script>showSlides(1,this);</script><br><div style="text-align:center"></div>';
        }
        cards_html += '</div>';
    } else {
        cards_html = '<div style="color:' + BOT_THEME_COLOR + ';" class="easychat-slides-wrapper" ><div class="slideshow-container"  value=1 >';
        total_images = cards.length;

        for(let i = 0; i < cards.length; i++) {
            current_image_no = i + 1;
            if (i == 0) {
                cards_html += '<div onclick="'
                cards_html += "window.open('" + cards[i]["link"] + "');"
                cards_html += '"  class="mySlides fade easychat-slider-card" >'
            } else {
                cards_html += '<div onclick="'
                cards_html += "window.open('" + cards[i]["link"] + "');"
                cards_html += '"  class="mySlides fade easychat-slider-card" style="display: none;">'
            }
            if (cards.length != 1) {
                cards_html += '<div class="pageno-co">' + current_image_no + ' / ' + total_images + '</div>'
                cards_html += '<img src="' + cards[i]["img_url"] + '">'
                if (cards[i]["title"].length > 25) {
                    let cards_title = cards[i]["title"].slice(0, 25) + " ..."
                    cards_html += '<h5>' + cards_title + '</h5>'
                } else {
                    cards_html += '<h5>' + cards[i]["title"] + '</h5>'
                }
                if (cards[i]["content"].length > 300) {
                    cards_html += '<p>' + (cards[i]["content"].slice(0, 300) + " ... ") + '</p></div>'
                } else {
                    cards_html += '<p>' + cards[i]["content"] + '</p></div>'
                }
            } else {
                cards_html += '<img src="' + cards[i]["img_url"] + '">'
                cards_html += '<h5>' + cards[i]["title"] + '</h5><p>' + cards[i]["content"] + '</p></div>';
            }
        }
        if (cards.length != 1) {
            cards_html += '<a class="prev-image-video" onclick="plusImageSlides(-1,this)">&#10094;</a>\
            <a class="next-image-video" onclick="plusImageSlides(1,this)">&#10095;</a>\
            </div><script>showSlides(1,this);</script><br><div style="text-align:center"></div>';
        }
        cards_html += '</div>';

    }
    cards_html += '</div></div>'
    document.getElementById("easychat-chat-container").innerHTML += cards_html;
}

function append_attachment(choosen_file_type, is_flow_ended) {
    var html =
        '<div class="easychat-dragdropContainer__XPS">\
        <span class="easychat-dragdropMsg__XPS" style="color:' + BOT_THEME_COLOR + '">Drag your (' + choosen_file_type + ') files here<br>Or Click in this area.</span>\
        <div class="easychat-dragdrop__XPS" style="border: 4px dashed ' + BOT_THEME_COLOR + '"><input onchange="change_span_name_to_file_name(this)" id="easychat-uploadfile__XPS" type="file" accept="' + choosen_file_type + '"></div>\
        <div class="easychat-dragdropafterSelect__XPS">\
            <span id="easychat-dragdropAlertMsg__XPS">Error Message</span>\
            <button onclick="upload_attachment_to_server(this,' + is_flow_ended + ')" id="easychat-dragdropUploadBTN__XPS" style="background-color:' + BOT_THEME_COLOR + '">Upload</button>\
            <div style="width:100%;float:left;display:none;" id="easychat-dragdropbottyping-loader"><img src="' + EASYCHAT_IMG_PATH + 'preloader.svg" style="height:3em;"></div>\
        </div></div>';
    document.getElementById("easychat-chat-container").innerHTML += html;
}

function change_span_name_to_file_name(el) {
    if (el.files[0] != undefined || el.files[0] != null) {
        var file_ext = el.files[0].name.split(".");
        file_ext = el.files[0].name.split(".")[file_ext.length - 1];
        if (document.getElementById("easychat-uploadfile__XPS").getAttribute("accept").toString().indexOf(file_ext.toLowerCase()) !== -1) {
            if (el.files[0].size <= 5 * 1024 * 1024) {
                document.getElementsByClassName("easychat-dragdropafterSelect__XPS")[0].style.backgroundColor = "white"
                document.getElementById("easychat-dragdropAlertMsg__XPS").style.fontSize = "unset"
                document.getElementsByClassName("easychat-dragdropafterSelect__XPS")[0].style.padding = "1em"
                document.getElementsByClassName("easychat-dragdropafterSelect__XPS")[0].style.boxShadow = "1px 1px 6px rgba(0, 0, 0, 0.2)"
                document.getElementsByClassName("easychat-dragdropafterSelect__XPS")[0].style.borderRadius = "1em"
                document.getElementById("easychat-dragdropAlertMsg__XPS").style.display = "inline-block"
                document.getElementById("easychat-dragdropAlertMsg__XPS").style.color = "black"
                let file_name = el.files[0].name.split(".")
                let file_length = file_name.length
                file_ext = parseInt(parseInt(file_length) - 1)
                // console.log(file_ext)
                if (el.files[0].name.length >= 15) {
                    var file_name_mod = file_name[0].slice(0, 15) + "... ." + file_name[file_name.length - 1]
                } else {
                    var file_name_mod = el.files[0].name
                }
                document.getElementById("easychat-dragdropAlertMsg__XPS").innerHTML = file_name_mod + ' <span onclick="remove_file_from_attachment()" class="easychat-dragdropAlertMsgClose__XPS" style="color: ' + BOT_THEME_COLOR + ';">x</span>'
                document.getElementById("easychat-dragdropUploadBTN__XPS").style.display = "inline-block"
                document.getElementsByClassName("easychat-dragdropMsg__XPS")[0].style.display = "none"
                document.getElementsByClassName("easychat-dragdrop__XPS")[0].style.display = "none"
            } else {
                document.getElementById("easychat-dragdropAlertMsg__XPS").style.display = "inline-block"
                document.getElementById("easychat-dragdropAlertMsg__XPS").style.fontSize = "unset"
                document.getElementById("easychat-dragdropAlertMsg__XPS").style.color = "red"
                document.getElementById("easychat-dragdropAlertMsg__XPS").textContent = "Please Select file < 5MB*"
            }
        } else {
            document.getElementById("easychat-dragdropAlertMsg__XPS").style.display = "inline-block"
            document.getElementById("easychat-dragdropAlertMsg__XPS").style.fontSize = "unset"
            document.getElementById("easychat-dragdropAlertMsg__XPS").style.color = "red"
            document.getElementById("easychat-dragdropAlertMsg__XPS").textContent = "Please Select Correct File Type*"
        }
    } else {
        document.getElementById("easychat-dragdropAlertMsg__XPS").style.display = "inline-block"
        document.getElementById("easychat-dragdropAlertMsg__XPS").style.fontSize = "unset"
        document.getElementById("easychat-dragdropAlertMsg__XPS").style.color = "red"
        document.getElementById("easychat-dragdropAlertMsg__XPS").textContent = "No File Selected*"
        document.getElementById("easychat-dragdropUploadBTN__XPS").style.display = "none"
    }
}

function upload_attachment_to_server(el, is_flow_ended) {
    var formData = new FormData();
    var upload_attachment_data = document.querySelector('#easychat-uploadfile__XPS').files[0]
    formData.append("upload_attachment", upload_attachment_data);
    document.getElementById("easychat-dragdropbottyping-loader").style.display = "inline-block"
    var xhttp = new XMLHttpRequest();
    var params = formData;
    xhttp.open("POST", "/chat/upload-attachment/", true);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            if (response.status == 200) {
                attached_file_src = response.src;
                var file_name = document.getElementById("easychat-dragdropAlertMsg__XPS").childNodes[0].textContent
                setTimeout(function() {
                    document.getElementById("easychat-dragdropbottyping-loader").style.display = "none"
                    document.getElementsByClassName("easychat-dragdropContainer__XPS")[0].remove()
                    append_bot_text_response(file_name + " has been successfully uploaded.")
                    if (!is_flow_ended) {
                        send_message_to_server("attachment", user_id, bot_id, bot_name, "");
                    }
                }, 1000);
            } else {
                document.getElementById("easychat-dragdropUploadBTN__XPS").style.display = "none"
                setTimeout(function() {
                    document.getElementById("easychat-dragdropbottyping-loader").style.display = "none"
                    document.getElementById("easychat-dragdropAlertMsg__XPS").style.color = "red"
                    document.getElementById("easychat-dragdropAlertMsg__XPS").innerHTML = "Unable to Upload"
                    setTimeout(function() {
                        remove_file_from_attachment();
                    }, 1000);
                }, 1000);
            }
        }
    }
    xhttp.send(params);
}

function remove_file_from_attachment() {
    document.getElementById("easychat-dragdropAlertMsg__XPS").innerHTML = ""
    document.getElementById("easychat-uploadfile__XPS").value = ""
    document.getElementById("easychat-dragdropUploadBTN__XPS").style.display = "none"
    document.getElementById("easychat-dragdropAlertMsg__XPS").style.display = "none"
    document.getElementsByClassName("easychat-dragdropMsg__XPS")[0].style.display = "block"
    document.getElementsByClassName("easychat-dragdrop__XPS")[0].style.display = "block"
    document.getElementsByClassName("easychat-dragdropafterSelect__XPS")[0].style.backgroundColor = "unset"
    document.getElementsByClassName("easychat-dragdropafterSelect__XPS")[0].style.padding = "0"
    document.getElementsByClassName("easychat-dragdropafterSelect__XPS")[0].style.boxShadow = "unset"
    document.getElementsByClassName("easychat-dragdropafterSelect__XPS")[0].style.borderRadius = "unset"
}


function append_bot_recommendation(recommendations_list) {
    var recommendations_html = '<div class="easychat-recommendation-wrapper" align="left">';
    for(let i = 0; i < recommendations_list.length; i++) {
        recommendations_html += "<div class=\"easychat-recommendation\" onmouseover='custom_button_change(this)' onmouseout='custom_button_change_normal(this)' style=\"border: 0.05em solid " + BOT_THEME_COLOR + ";color: " + BOT_THEME_COLOR + "\" onclick=\"send_selected_recommendation(this)\">" + recommendations_list[i] + "</div>";
    }
    recommendations_html += "</div>";
    document.getElementById("easychat-chat-container").innerHTML += recommendations_html;
}

function append_bot_choices(choices_list) {
    var choices_html = '<div class="easychat-choices-wrapper">';
    for(let i = 0; i < choices_list.length; i++) {
        var display = choices_list[i]["display"];
        var value = choices_list[i]["value"];
        choices_html += '<button class="easychat-choices" onmouseover="custom_button_change(this)" onmouseout="custom_button_change_normal(this)" style=\"border: 0.05em solid ' + BOT_THEME_COLOR + ';color: ' + BOT_THEME_COLOR + '\" value="' + value + '" onclick="send_selected_choice(this)">' + display + '</button>';
    }
    choices_html += "</div>";
    document.getElementById("easychat-chat-container").innerHTML += choices_html;
}

function append_feedback_btns(feedback_id) {
    var choices_html = '<div class="easychat-choices-wrapper">\
        <button class="easychat-choices" onmouseover="custom_button_change(this)" onmouseout="custom_button_change_normal(this)" style=\"border: 0.05em solid ' + BOT_THEME_COLOR + ';color: ' + BOT_THEME_COLOR + '\" onclick="easychat_send_feedback_msg(this,' + feedback_id + ',1,\'\')"><img src="/static/EasyChatApp/img/thumbs-up-filled.png" style="height:2em;"></button>\
        <button class="easychat-choices" onmouseover="custom_button_change(this)" onmouseout="custom_button_change_normal(this)" style=\"border: 0.05em solid ' + BOT_THEME_COLOR + ';color: ' + BOT_THEME_COLOR + '\" onclick="easychat_send_feedback_msg(this,' + feedback_id + ',-1,\'\')"><img src="/static/EasyChatApp/img/thumbs-down-filled.png" style="height:2em;"></button>\
    </div>';
    document.getElementById("easychat-chat-container").innerHTML += choices_html;
}

function easychat_send_feedback_msg(element, feedback_id, feedback_type, feedback_cmt) {

    var elements = document.getElementsByClassName("easychat-intent-feedback-wrapper");
    for(let i = 0; i < elements.length; i++) {
        elements[i].parentNode.removeChild(elements[i]);
    }

    for(let i = 0; i < element.parentElement.children.length; i++) {
        element.parentElement.children[i].style.backgroundColor = "white";
        element.parentElement.children[i].style.color = BOT_THEME_COLOR;
        element.parentElement.children[i].style.borderColor = BOT_THEME_COLOR;
        element.parentElement.children[i].removeAttribute("easychat-feedback-selected");
    }

    element.style.backgroundColor = BOT_THEME_COLOR;
    element.style.color = "white";
    element.style.borderColor = BOT_THEME_COLOR;
    element.setAttribute("easychat-feedback-selected", "true");

    for(let i = 0; i < element.parentElement.children.length; i++) {
        //if(element.parentElement.children[i].hasAttribute("onclick")){element.parentElement.children[i].removeAttribute("onclick")}
        //if(element.parentElement.children[i].hasAttribute("onmouseout")){element.parentElement.children[i].removeAttribute("onmouseout")}
        //if(element.parentElement.children[i].hasAttribute("onmouseover")){element.parentElement.children[i].removeAttribute("onmouseover")}
    }

    easychat_send_feedback_message_to_server(feedback_id, feedback_type, feedback_cmt);

    var html = '<div class="easychat-intent-feedback-wrapper">\
                    <div class="easychat-intent-feedback-cmt-wrapper" style="width: 75%;">\
                    <p style="margin: 0;margin-bottom: 0.5em;">\
                    Please provide your feedback:\
                    </p>\
                    <p style="margin: 0;margin-bottom: 0.5em; color:red; display:none" id="feedback-empty-warning"> \
                    Feedback can not be empty \
                    </p>\
                    <div class="feedback_cmt" contenteditable="true" style="padding: 0.5em;border: solid 1px;width: 95%;border-radius: 0.5em;">\
                    <div><br></div></div>\
                    <button onclick="easychat_submit_feedback_message_to_server(' + feedback_id + ',' + feedback_type + ')" style="margin-top: 5px;float: right;">\
                    Submit\
                    </button>\
                </div>\
                </div>'
    document.getElementById("easychat-chat-container").innerHTML += html;
    scroll_to_bottom()
}

function easychat_submit_feedback_message_to_server(feedback_id, feedback_type) {

    var feedback_cmt = document.getElementsByClassName("feedback_cmt")[[document.getElementsByClassName("feedback_cmt").length - 1]].innerText
    feedback_cmt = feedback_cmt.trim();
    if(feedback_cmt.length==0){
        $("#feedback-empty-warning").css("display","block");
        return;
    }else{
        $("#feedback-empty-warning").css("display","none");
    }
    var elmnt = document.getElementsByClassName("easychat-intent-feedback-wrapper")[
        document.getElementsByClassName("easychat-intent-feedback-wrapper").length - 1]
    elmnt.setAttribute("feedback_submitted", "true");
    elmnt.innerHTML = '\
    <div class="easychat-intent-feedback-cmt-wrapper" style="width: 75%;">\
                    <p style="margin: 0;margin-bottom: 0.5em;">\
                    Thank you for your feedback\
                    </p>\
            </div>'
    scroll_to_bottom()
    easychat_send_feedback_message_to_server(feedback_id, feedback_type, feedback_cmt);
}

function easychat_send_feedback_message_to_server(feedback_id, feedback_type, feedback_cmt) {
    var json_string = JSON.stringify({
        feedback_id: feedback_id,
        feedback_type: feedback_type,
        feedback_cmt: feedback_cmt
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
    xhttp.open("POST", EASYCHAT_FEEDBACK_SAVE_URL, true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
        }
    }
    xhttp.send(params);
}

function append_bot_tables(table_list) {
    var tables_html = '<!--<style>table {border-left: 0;border-spacing: 0px;box-shadow: 1px 1px 6px rgba(0, 0, 0, 0.2);background-color: white;}th,td {    padding: 5px 4px 6px 4px; text-align: left; vertical-align: top;}tr {display: table-row;    vertical-align: inherit;    border-color: inherit;}td {    border-top: 1px solid #000;word-break: break-all;    min-width: 65px;}th {    text-align: center;background-color: #9D1D27;    color: white;}</style>--><div style="margin-top:0.3em;width:100%;display:inline-block;border-radius:10px;overflow:hidden"><table class="easychat-bot-table"><tbody>';
    for(let row_index = 0; row_index < table_list.length; row_index++) {
        tables_html += "<tr>";
        if (row_index == 0) {
            for(let col_index = 0; col_index < table_list[row_index].length; col_index++) {
                tables_html += "<th>" + table_list[row_index][col_index] + "</th>";
            }
        } else {
            for(let col_index = 0; col_index < table_list[row_index].length; col_index++) {
                tables_html += "<td>" + table_list[row_index][col_index] + "</td>";
            }
        }
        tables_html += "</tr>";
    }
    tables_html += '</tbody></table></div>';
    document.getElementById("easychat-chat-container").innerHTML += tables_html;
}

function append_datepicker(datepicker_list) {

    if (datepicker_list.length > 0) {
        let datepicker_container = document.getElementById("easychat-datepicker-container");
        if (datepicker_container != undefined && datepicker_container != null) {
            datepicker_container.remove();
        }

        var datepicker_html = '<div class="easychat-datepicker-container"  align="center" id="easychat-datepicker-container">';
        for(let i = 0; i < datepicker_list.length; i++) {
            datepicker_html += '<div style="width:100%"><br>\
            ' + datepicker_list[i]["placeholder"] + ' <input type="date" name="datepicker" class="easychat-datepicker" id="easychat-datepicker-' + i + '" onchange="append_selected_date_into_user_query(this)" placeholder="' + datepicker_list[i]["placeholder"] + '">\
            </div>';
        }
        datepicker_html += "</div>";

        document.getElementById("easychat-chat-container").innerHTML += datepicker_html;
    }
}

function append_selected_date_into_user_query(element) {
    let easychat_datepicker_list = document.getElementsByClassName("easychat-datepicker");
    var user_input = "";
    for(let i = 0; i < easychat_datepicker_list.length; i++) {
        user_input += easychat_datepicker_list[i].placeholder + ": " + easychat_datepicker_list[i].value;
        if (i != easychat_datepicker_list.length - 1) {
            user_input += ", ";
        }
    }
    document.getElementById("user_input").value = user_input;
}

function append_bot_range_slider(range_slider_list) {
    if (range_slider_list.length > 0) {
        let easychat_range_slider_container = document.getElementById("easychat-range-slider-container");
        if (easychat_range_slider_container != undefined && easychat_range_slider_container != null) {
            easychat_range_slider_container.remove();
        }

        var range_slider_html = '<div class="easychat-range-slider-container" id="easychat-range-slider-container">';
        for(let i = 0; i < range_slider_list.length; i++) {
            let range_slider = range_slider_list[i];
            range_slider_html += '<div style="width:100%;display:inline-block;">\
              <p>Min: ' + range_slider["min"] + ', Max: ' + range_slider["max"] + '</p>\
              <p>' + range_slider["placeholder"] + ': <span id="easychat-range-slider-value-' + i + '"></span></p>\
              <input type="range" min="' + range_slider["min"] + '" max="' + range_slider["max"] + '" value="' + range_slider["max"] + '" class="easychat-range-slider" id="easychat-range-slider-' + i + '" onchange="append_selected_value_into_user_query(this)" placeholder="' + range_slider["placeholder"] + '">\
            </div>';
        }
        range_slider_html += '</div>';
        document.getElementById("easychat-chat-container").innerHTML += range_slider_html;
        for(let i = 0; i < range_slider_list.length; i++) {
            document.getElementById("easychat-range-slider-" + i).onchange();
        }
    }
}

function append_selected_value_into_user_query(element) {
    let range_count = element.id.split("-")[3];
    document.getElementById("easychat-range-slider-value-" + range_count).innerHTML = element.value;
    var user_input = "";
    let easychat_range_slider_list = document.getElementsByClassName("easychat-range-slider");
    for(let i = 0; i < easychat_range_slider_list.length; i++) {
        let range_slider_element = easychat_range_slider_list[i];
        user_input += range_slider_element.placeholder + ": " + range_slider_element.value;
        if (i != easychat_range_slider_list.length - 1) {
            user_input += ", ";
        }
    }
    document.getElementById("user_input").value = user_input;
}

function show_bot_typing_loader(name=""){
    if(name){
        name = name.charAt(0).toUpperCase() + name.slice(1)
    }
    // document.getElementById("easychat-chat-container").innerHTML += '<div style="width:100%;float:left;display:inline-block;" id="div-bottyping-loader"><img src="'+EASYCHAT_IMG_PATH+'preloader.svg" style="height:3em;"></div>';

    if(name){
        document.getElementById("easychat-chat-container").innerHTML += '<div class="typing-indicator" id="div-bottyping-loader">\
                                                                            '+
                                                                             name + " is"
                                                                            +'\
                                                                            Typing\
                                                                            <span></span>\
                                                                            <span></span><span></span>\
                                                                        </div>'
    }else{
        document.getElementById("easychat-chat-container").innerHTML += '<div class="typing-indicator" id="div-bottyping-loader">\
                                                                            Typing\
                                                                            <span></span>\
                                                                            <span></span><span></span>\
                                                                        </div>'
    }
}

function show_start_bot_loader() {
    document.getElementById("easychat-chat-container").innerHTML += '<div style="width:100%;float:left;padding-left:28%;padding-top:46%" id="div-bot-start-loader"><img src="' + EASYCHAT_IMG_PATH + 'preloader.svg" style="height:12em;"></div>';
}

function hide_start_bot_loader() {
    document.getElementById("div-bot-start-loader").remove();
}

function hide_bot_typing_loader() {
    var eles = document.querySelectorAll("[id=div-bottyping-loader]");

    for(let index=0 ; index < eles.length ; index++){
        eles[index].remove();
    }
    last_typing_name = null;
}

function send_message_to_server(message, userid, bot_id, bot_name, channel_params) {
    message = stripHTML(message);
    message = remove_special_characters_from_str(message);

    if (is_livechat == true) {
        save_customer_chat(message, userid, "customer");
        var sentence = JSON.stringify({
            'message': message,
            'sender': 'user',
            'file_type': 'message'
        });
        chat_socket1.send(sentence);
        return;
    }

    if (is_cobrowsing_chat == true) {
        parent.postMessage({
            event_id: 'cobrowsing-client-chat-message',
            data: {
                message: message
            }
        }, "*");
        return;
    }

    var element = document.getElementsByClassName("easychat-dragdropContainer__XPS")[0]
    if (element != null && element != undefined) {
        element.remove()
    }

    document.getElementById("easychat-chat-container").click();
    show_bot_typing_loader();
    disable_user_input();

    let data = {
        "session_id": session_id,
        "window_location": decodeURIComponent(window_location),
        "is_form_assist": form_assist_enabled,
        "attached_file_src": attached_file_src
    }
    if (embed_cookies != "") {
        let embed_cookies_decrypted = easyassist_custom_decrypt(embed_cookies)
        embed_cookies_decrypted = JSON.parse(embed_cookies_decrypted)
        data = Object.assign({}, data, embed_cookies_decrypted);
    }
    if (embed_meta_data != "") {
        let embed_meta_data_decrypted = easyassist_custom_decrypt(embed_meta_data)
        embed_meta_data_decrypted = JSON.parse(embed_meta_data_decrypted)
        data = Object.assign({}, data, embed_meta_data_decrypted);
    }

    channel_params = JSON.stringify(data);

    var json_string = JSON.stringify({
        message: message,
        user_id: userid,
        channel: "Web",
        channel_params: channel_params,
        bot_id: bot_id,
        bot_name: bot_name,
        bot_display_name: bot_name
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
    xhttp.open("POST", EASYCHAT_QUERY_URL, true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response)
            response = JSON.parse(response);
            user_id = response.user_id;
            attached_file_src = null;
            hide_bot_typing_loader();
            if (form_assist_enabled) {
                response["response"]["recommendations"].push(["Do not disturb"]);
                do_not_disturb = "true";
            }
            append_bot_response(response);
            enable_user_input();
            detectmob();
            form_assist_enabled = false;
        }
    }
    xhttp.send(params);
}

function getPrevSessionHistory(prev_session_id) {
    var xhttp = new XMLHttpRequest();
    var params = "prev_session_id=" + prev_session_id;
    xhttp.open("POST", "/chat/get-prev-session-history/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            for (i = response["prev_msg_histry"].length - 1; i >= 0; i--) {
                var time = return_time();
                document.getElementById("easychat-chat-container").innerHTML += '<div class="easychat-user-message-div"><div class="easychat-user-message" style="background-color:' + BOT_THEME_COLOR + ';color: ' + USER_MESSAGE_COLOR + '"><div class="easychat-user-message-line">'+ response["prev_msg_histry"][i]["user_msg"] + '</div></div><span class="message-time-user">' + time + '<img class="doubletick_easychat" src="' + EASYCHAT_IMG_PATH + 'doubletick_blue.svg" style="height:1.5em;></span></div>'
                //appendResponseUser(response["prev_msg_histry"][i]["user_msg"])
                message_list = get_message_list(response["prev_msg_histry"][i]["bot_response"], RESPONSE_SENTENCE_SEPARATOR);
                for(let j = 0; j < message_list.length; j++) {
                    append_bot_text_response(message_list[j]);
                }
                scroll_to_bottom();
            }
        }
    }
    xhttp.send(params);
}

function default_bot_color(bot_id) {
    var json_string = JSON.stringify({
        bot_id: bot_id,
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/chat/get-bot-message-image/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onload = function() {
        if (this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response)
            response = JSON.parse(response);
            BOT_THEME_COLOR = "#" + response.bot_theme_color
            document.getElementById("easychat-navbar-wrapper").style.backgroundColor = BOT_THEME_COLOR;
            document.getElementById("user_input").style.borderColor = BOT_THEME_COLOR;
            document.getElementById("model-feedback-header").style.color = BOT_THEME_COLOR;
            document.getElementById("img-scroll-to-bottom").style.color = BOT_THEME_COLOR;
        }

    }
    xhttp.send(params);
}

function custom_button_change(x) {
    x.style.backgroundColor = BOT_THEME_COLOR;
    x.style.color = "white";
    x.style.borderWidth = "0.05em";
    x.style.borderColor = BOT_THEME_COLOR
    x.style.borderStyle = "solid";
}

function custom_button_change_normal(x) {
    if (x.getAttribute("easychat-feedback-selected") == "true") {
        return;
    }
    x.style.backgroundColor = "#f6f6f6";
    x.style.color = BOT_THEME_COLOR;
}

function custom_button_change_card(x) {
    x.style.backgroundColor = BOT_THEME_COLOR;
    x.style.color = "white";
    x.style.borderRadius = "1em";
}


function custom_button_change_normal_card(x) {
    x.style.backgroundColor = "white";
    x.style.color = "black";
    x.style.borderRadius = "1em";
}

function append_welcome_message(bot_id, bot_name) {
    show_start_bot_loader();
    var json_string = JSON.stringify({
        bot_id: bot_id,
        bot_name: bot_name,
        user_id: user_id,
        session_id: session_id,
        channel_name: "Web"
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
    xhttp.open("POST", "/chat/get-channel-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onload = function() {
        if (this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response)
            response = JSON.parse(response);
            let welcome_message = response.welcome_message;
            let recommendations = response.initial_messages["items"];
            let carousel_img_url_list = response.carousel_img_url_list["items"];
            let redirect_url_list = response.redirect_url_list["items"];
            let welcome_msg_images = response.initial_messages["images"];

            let welcome_msg_videos = response.initial_messages["videos"];
            let is_text_to_speech_required = response.is_text_to_speech_required
            let bot_start_conversation_intent = response.bot_start_conversation_intent
            let poweredby_required = response.is_powered_by_required;

            if (poweredby_required === true) {
                document.getElementById("easychat-powered-by-div").style.display = "block";
            }

            document.getElementById("user_input").disabled = true;
            document.getElementById("user_input").disabled = false;
            detectmob();

            if (carousel_img_url_list.length) {
                add_banner(carousel_img_url_list, redirect_url_list)
            }
            if (carousel_img_url_list.length) {
                init_gallery()
            }

            let prev_session_id = get_cookie("easychat_prev_session_id");
            if (is_text_to_speech_required) {
                text_to_speech(welcome_message);
            }

            append_bot_text_response(welcome_message);
            hide_start_bot_loader();

            if (welcome_msg_videos != null && welcome_msg_videos != undefined && welcome_msg_videos.length > 0) {
                append_bot_slider_videos(welcome_msg_videos);
            }

            if (welcome_msg_images != null && welcome_msg_images != undefined && welcome_msg_images.length > 0) {
                append_bot_slider_images(welcome_msg_images);
            }

            append_bot_recommendation(recommendations);

            if (prev_session_id != "") {
                getPrevSessionHistory(prev_session_id);
                session_id = prev_session_id;
                set_cookie("easychat_prev_session_id", "");
                prev_session_id = get_cookie("easychat_prev_session_id");
            }

            if (bot_start_conversation_intent != null && bot_start_conversation_intent != undefined) {
                send_message_to_server(bot_start_conversation_intent, user_id, bot_id, bot_name, "None");
            }
        }
    }
    xhttp.send(params);
}

function send_message() {
    var user_input = document.getElementById("user_input").value.trim();
    // Remove equal sign
    // user_input = user_input.replace(/=/gm, '')
    // Remove html tags from message
    user_input = user_input.replace(/<[^>]*>?/gm, '');

    document.getElementById("user_input").value = '';

    if (user_input.length == 0) {
        return;
    }

    send_user_input(user_input);
}

document.onkeyup = function(e) {
    e = e || window.event;

    var input_element = document.getElementById("user_input");
    var user_query = input_element.value.trim();
    if (user_query != "") {
        activate_query_submit_button();
    } else {
        deactivate_query_submit_button();
    }

    let maxlength = input_element.maxlength;
    if (input_element.value.length > maxlength) {
        let restricted_value = input_element.value.substr(0, maxlength);
        input_element.value = restricted_value;
    }

    if (e.keyCode == 13) {
        send_message();
    }
}

function confirm_do_not_disturb() {
    append_bot_text_response("Are you sure, you want to enable 'Do not disturb'? By clicking 'Yes', form assistant will be disabled.");
    var choices_html = '<div class="easychat-choices-wrapper">';
    choices_html += '<button class="easychat-choices" onmouseover="custom_button_change(this)" onmouseout="custom_button_change_normal(this)" style=\"border: 0.05em solid ' + BOT_THEME_COLOR + ';color: ' + BOT_THEME_COLOR + '\" value="Yes" onclick="disable_form_assist(this)">Yes</button>';
    choices_html += '<button class="easychat-choices" onmouseover="custom_button_change(this)" onmouseout="custom_button_change_normal(this)" style=\"border: 0.05em solid ' + BOT_THEME_COLOR + ';color: ' + BOT_THEME_COLOR + '\" value="No" onclick="nothing_form_assist(this)">No</button>';
    choices_html += "</div>";
    document.getElementById("easychat-chat-container").innerHTML += choices_html;
}

function disable_form_assist(element) {
    parent.postMessage('disable-form-assist', '*');
}

function nothing_form_assist(element) {
    append_bot_text_response("Great, How may I help you?");
}

function send_selected_recommendation(element) {
    var user_input = element.innerHTML;

    if (do_not_disturb == "true") {
        if (user_input == "Do not disturb") {
            // show_form_assist_result();
            // do_not_disturb = "false"
            // form_assist_enabled = true
            // document.getElementsByClassName("easychat-recommendation")[0].style.pointerEvents = "none"
            // document.getElementsByClassName("easychat-recommendation")[1].style.pointerEvents = "none"
            // parent.postMessage('enable-form-assist','*');
            confirm_do_not_disturb();
        } else {
            // do_not_disturb = "true"
            // form_assist_enabled = false
            // document.getElementsByClassName("easychat-recommendation")[0].style.pointerEvents = "none"
            // document.getElementsByClassName("easychat-recommendation")[1].style.pointerEvents = "none"
            // append_welcome_message(bot_id, bot_name);
            // get_suggestion_list(bot_id, bot_name);
        }
        do_not_disturb = "false";
    } else {
        // var user_input = element.innerHTML;
        send_user_input(user_input);
        element.remove();
    }
}

function send_selected_choice(element) {
    var user_input = element.value;
    for(let i = 0; i < element.parentElement.children.length; i++) {
        if (element.parentElement.children[i].hasAttribute("onclick")) {
            element.parentElement.children[i].removeAttribute("onclick")
        }
        if (element.parentElement.children[i].hasAttribute("onmouseout")) {
            element.parentElement.children[i].removeAttribute("onmouseout")
        }
        if (element.parentElement.children[i].hasAttribute("onmouseover")) {
            element.parentElement.children[i].removeAttribute("onmouseover")
        }
    }
    send_user_input(user_input);
}

if (!('webkitSpeechRecognition' in window)) {
    document.getElementById("easychat-mic-div").remove();
    document.getElementById("easychat-mic-disable").style.display = "none";
}

function check_mic_access() {

    document.getElementById("mic-span").style.marginRight = "9px";

    var SpeechRecognition = SpeechRecognition || webkitSpeechRecognition
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;

    recognition.onstart = function() {
        recognizing = true;
    };

    recognition.onerror = function(event) {
        if (event.error == 'no-speech') {
            ignore_onend = true;
        }
        if (event.error == 'audio-capture') {
            ignore_onend = true;
        }
        if (event.error == 'not-allowed') {
            ignore_onend = true;
            recognition = null;
            deactivate_mic();
            alert("You will not be able to use voicebot feature as you haven't allowed microphone access.");
        }
    };

    recognition.onend = function() {
        recognizing = false;
        if (ignore_onend) {
            document.getElementById("mic-span").style.marginRight = "";
            return;
        }
        if (!final_transcript) {
            document.getElementById("mic-span").style.marginRight = "";
            return;
        }
    };

    recognition.onresult = function(event) {
        document.getElementById('user_input').value = event.results[0][0].transcript;
        if(document.getElementById('user_input').value.trim() != "") {
            activate_query_submit_button();
        }
        if (event.results[0].isFinal) {
            recognition.abort();
            recognition.continuous = false;
            deactivate_mic();
        }
    };

    if (recognition != null) {
        activate_mic();
    } else {
        mic_access = false;
        hide_mic_icon();
    }
}

function initMap() {
    var current_latitude = "";
    var current_longitude = "";

    if (("geolocation" in navigator)) {
        navigator.geolocation.getCurrentPosition(
            function success(position) {
                current_latitude = position.coords.latitude
                current_longitude = position.coords.longitude

                var map = new google.maps.Map(document.getElementById('map'), {
                    center: {
                        lat: current_latitude,
                        lng: current_longitude
                    },
                    zoom: 15
                });

                var request = {
                    placeId: 'ChIJN1t_tDeuEmsRUsoyG83frY4',
                    fields: ['name', 'formatted_address', 'place_id', 'geometry']
                };

                var infowindow = new google.maps.InfoWindow();
                var service = new google.maps.places.PlacesService(map);

                service.getDetails(request, function(place, status) {
                    if (status === google.maps.places.PlacesServiceStatus.OK) {
                        marker = new google.maps.Marker({
                            map: map,
                            position: place.geometry.location
                        });

                        marker.setPosition(map.getCenter())

                        var centerControlDiv = document.createElement("div");
                        var centerControl = new CenterControl(centerControlDiv, map);
                        centerControlDiv.index = 1;
                        map.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(centerControlDiv);
                    }
                });

                function CenterControl(controlDiv, map) {
                    var controlUI = document.createElement("div");
                    controlUI.style.backgroundColor = "#fff";
                    controlUI.style.border = "2px solid #fff";
                    controlUI.style.borderRadius = "3px";
                    controlUI.style.boxShadow = "0 2px 6px rgba(0,0,0,.3)";
                    controlUI.style.cursor = "pointer";
                    controlUI.style.marginBottom = "22px";
                    controlUI.style.textAlign = "center";
                    controlUI.title = "Click to Submit the location";
                    controlDiv.appendChild(controlUI);
                    // Set CSS for the control interior.\
                    var controlText = document.createElement("div");
                    controlText.style.color = "rgb(25,25,25)";
                    controlText.style.fontFamily = "Roboto,Arial,sans-serif";
                    controlText.style.fontSize = "16px";
                    controlText.style.lineHeight = "38px";
                    controlText.style.paddingLeft = "5px";
                    controlText.style.paddingRight = "5px";
                    controlText.innerHTML = "Click here to submit your location";
                    controlUI.appendChild(controlText);
                    // Setup the click event listeners: simply set the map to Chicago.\
                    controlUI.addEventListener("click", function() {
                        var lat = marker.getPosition().lat();
                        var lng = marker.getPosition().lng();
                        let user_input = lat + "__" + lng;
                        send_message_to_server(user_input, user_id, bot_id, bot_name, "None");
                        scroll_to_bottom();
                    });
                }
            },
            function error(error_message) {
                // for when getting location results in an error
                console.error('An error has occured while retrieving' +
                    'location before', error_message)
                document.getElementById("google-map").remove();
                append_bot_text_response("Unable to fetch your location details.");
                send_message_to_server("Share Pincode", user_id, bot_id, bot_name, "None");
            });
    } else {
        document.getElementById("google-map").remove();
        append_bot_text_response("Unable to fetch your location details.");
        send_message_to_server("Share Pincode", user_id, bot_id, bot_name, "None");
    }
}

function autocomplete(inp, arr, word_mapper_list) {
    /*the autocomplete function takes two arguments,
    the text field element and an array of possible autocompleted values:*/
    var currentFocus;
    /*execute a function when someone writes in the text field:*/
    inp.addEventListener("input", function(e) {
        var a, b, i, val = this.value;
        /*close any already open lists of autocompleted values*/
        closeAllLists();
        if (!val) {
            return false;
        }
        currentFocus = -1;
        /*create a DIV element that will contain the items (values):*/
        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");
        /*append the DIV element as a child of the autocomplete container:*/
        this.parentNode.appendChild(a);
        /*for each item in the array...*/

        for(let word_index = 0; word_index < word_mapper_list.length; word_index++) {
            for(let s_index = 0; s_index < word_mapper_list[word_index]["similar_words"].length; s_index++) {
                if (word_mapper_list[word_index]["similar_words"][s_index].toLowerCase() == val.toLowerCase()) {
                    //similar_word_list.push(word_mapper_list[word_index]["keyword"].toLowerCase());
                    val = word_mapper_list[word_index]["keyword"].toLowerCase();
                }
            }
        }

        var count = 0;
        //console.log(arr)
        let arr_value_list = []
        for (i = 0; i < arr.length; i++) {
            if (is_flow_ended && count < 5 && is_livechat == false && is_cobrowsing_chat == false) {
                //console.log(arr[i])
                /*check if the item starts with the same letters as the text field value:*/
                if (arr[i]["key"].toUpperCase().indexOf(val.toUpperCase()) != -1 && arr_value_list.indexOf(arr[i]["value"]) < 0) {
                    /*create a DIV element for each matching element:*/
                    b = document.createElement("DIV");
                    arr_value_list.push(arr[i]["value"]);
                    /*make the matching letters bold:*/
                    b.innerHTML = "" + arr[i]["value"].substr(0, val.length) + "";
                    b.innerHTML += arr[i]["value"].substr(val.length);
                    /*insert a input field that will hold the current array item's value:*/
                    b.innerHTML += "<input type='hidden' value='" + arr[i]["value"] + "'>";
                    /*execute a function when someone clicks on the item value (DIV element):*/
                    b.addEventListener("click", function(e) {
                        /*insert the value for the autocomplete text field:*/
                        inp.value = this.getElementsByTagName("input")[0].value;
                        /*close the list of autocompleted values,
                        (or any other open lists of autocompleted values:*/
                        closeAllLists();
                        send_user_input(inp.value);
                        inp.value = "";
                    });
                    a.appendChild(b);
                    count += 1;
                }
            }
        }
    });
    /*execute a function presses a key on the keyboard:*/
    inp.addEventListener("keydown", function(e) {
        var x = document.getElementById(this.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        if (e.keyCode == 40) {
            /*If the arrow DOWN key is pressed,
            increase the currentFocus variable:*/
            currentFocus++;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode == 38) { //up
            /*If the arrow UP key is pressed,
            decrease the currentFocus variable:*/
            currentFocus--;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode == 13) {
            /*If the ENTER key is pressed, prevent the form from being submitted,*/
            e.preventDefault();
            if (currentFocus > -1) {
                /*and simulate a click on the "active" item:*/
                if (x) x[currentFocus].click();
            }
        }
    });

    function addActive(x) {
        /*a function to classify an item as "active":*/
        if (!x) return false;
        /*start by removing the "active" class on all items:*/
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        /*add class "autocomplete-active":*/
        x[currentFocus].classList.add("autocomplete-active");
    }

    function removeActive(x) {
        /*a function to remove the "active" class from all autocomplete items:*/
        for(let i = 0; i < x.length; i++) {
            x[i].classList.remove("autocomplete-active");
        }
    }

    function closeAllLists(elmnt) {
        /*close all autocomplete lists in the document,
        except the one passed as an argument:*/
        var x = document.getElementsByClassName("autocomplete-items");
        for(let i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != inp) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }
    /*execute a function when someone clicks in the document:*/
    document.addEventListener("click", function(e) {
        closeAllLists(e.target);
    });
}

function custom_autocomplete(inp, arr) {
    /*the autocomplete function takes two arguments,
    the text field element and an array of possible autocompleted values:*/
    var currentFocus;
    /*execute a function when someone writes in the text field:*/
    inp.addEventListener("input", function(e) {
        var a, b, i, val = this.value;
        /*close any already open lists of autocompleted values*/
        closeAllLists();
        if (!val) {
            return false;
        }
        if (val.length == 2 && is_custom_complete) {
            get_quotes_suggestions(val)
        }
        currentFocus = -1;

        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");
        /*append the DIV element as a child of the autocomplete container:*/
        this.parentNode.appendChild(a);
        /*for each item in the array...*/
        var count = 0;

        //console.log(arr)
        arr_value_list = []
        arr = code_list
        for (i = 0; i < arr.length; i++) {
            if (is_custom_complete && count < 5 && is_livechat == false && is_cobrowsing_chat == false) {
                //console.log(arr[i])
                /*check if the item starts with the same letters as the text field value:*/
                if (arr[i]["key"].toUpperCase().indexOf(val.toUpperCase()) != -1 && arr_value_list.indexOf(arr[i]["value"]) < 0) {
                    /*create a DIV element for each matching element:*/
                    b = document.createElement("DIV");
                    arr_value_list.push(arr[i]["value"]);
                    /*make the matching letters bold:*/
                    b.innerHTML = "" + arr[i]["value"].substr(0, val.length) + "";
                    b.innerHTML += arr[i]["value"].substr(val.length);
                    /*insert a input field that will hold the current array item's value:*/
                    b.innerHTML += "<input type='hidden' value='" + arr[i]["value"] + "'>";
                    /*execute a function when someone clicks on the item value (DIV element):*/
                    b.addEventListener("click", function(e) {
                        /*insert the value for the autocomplete text field:*/
                        inp.value = this.getElementsByTagName("input")[0].value;
                        /*close the list of autocompleted values,
                        (or any other open lists of autocompleted values:*/
                        closeAllLists();
                        send_user_input(inp.value);
                        inp.value = "";
                    });
                    a.appendChild(b);
                    count += 1;
                }
            }
        }
    });
    /*execute a function presses a key on the keyboard:*/
    inp.addEventListener("keydown", function(e) {
        var x = document.getElementById(this.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        if (e.keyCode == 40) {
            /*If the arrow DOWN key is pressed,
            increase the currentFocus variable:*/
            currentFocus++;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode == 38) { //up
            /*If the arrow UP key is pressed,
            decrease the currentFocus variable:*/
            currentFocus--;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode == 13) {
            /*If the ENTER key is pressed, prevent the form from being submitted,*/
            e.preventDefault();
            if (currentFocus > -1) {
                /*and simulate a click on the "active" item:*/
                if (x) x[currentFocus].click();
            }
        }
    });

    function addActive(x) {
        /*a function to classify an item as "active":*/
        if (!x) return false;
        /*start by removing the "active" class on all items:*/
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        /*add class "autocomplete-active":*/
        x[currentFocus].classList.add("autocomplete-active");
    }

    function removeActive(x) {
        /*a function to remove the "active" class from all autocomplete items:*/
        for(let i = 0; i < x.length; i++) {
            x[i].classList.remove("autocomplete-active");
        }
    }

    function closeAllLists(elmnt) {
        /*close all autocomplete lists in the document,
        except the one passed as an argument:*/
        var x = document.getElementsByClassName("autocomplete-items");
        for(let i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != inp) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }
    /*execute a function when someone clicks in the document:*/
    document.addEventListener("click", function(e) {
        closeAllLists(e.target);
    });
}

function get_suggestion_list(bot_id, bot_name) {
    var json_string = JSON.stringify({
        bot_id: bot_id,
        bot_name: bot_name,
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
    xhttp.open("POST", "/chat/get-data/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                suggestion_list = response["sentence_list"];
                let word_mapper_list = response["word_mapper_list"];
                autocomplete(document.getElementById("user_input"), response["sentence_list"], word_mapper_list);
            } else {
                autocomplete(document.getElementById("user_input"), [], []);
            }
        }
    }
    xhttp.send(params);
}

function resize_chabot_window() {
    document.getElementById('easychat-chat-container').style.height = (document.documentElement.clientHeight - (document.getElementById("easychat-navbar").clientHeight + document.getElementById("easychat-footer").clientHeight) - 30).toString() + "px";
}

window.onresize = function() {
    scroll_to_bottom();
    // changeMiddleContainer();
}

function plusImageSlides(n, el) {
    let slideIndex = parseInt(el.parentElement.getAttribute("value"))
    slideIndex += n
    el.parentElement.setAttribute("value", slideIndex.toString())
    showSlides(slideIndex, el.parentElement);
}

function showSlides(n, el) {
    var i;
    slideIndex = parseInt(el.getAttribute("value"))
    var c = el.children
    var slides = []
    for(let i = 0; i < c.length; i++) {
        if (c[i].className == "mySlides fade easychat-slider-card") {
            slides.push(c[i])
        } else if (c[i].className == "mySlides fade") {
            slides.push(c[i])
        }
    }
    //var slides = document.getElementsByClassName("mySlides");
    if (n > slides.length) {
        el.setAttribute("value", "1")
    }
    if (n < 1) {
        el.setAttribute("value", (slides.length).toString())
    }
    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    slideIndex = parseInt(el.getAttribute("value"))
    slides[slideIndex - 1].style.display = "block";
}

function add_banner(carousel_img_url_list, redirect_url_list) {

    let html = '<div class="galleryContainer"><div class="slideShowContainer">';
    html += '<div onclick="move_gallary_slides(-1)" class="nextPrevBtn leftArrow"><span class="arrow arrowLeft"></span></div>';

    if (carousel_img_url_list.length > 1) {
        html += '<div onclick="move_gallary_slides(1)" class="nextPrevBtn rightArrow"><span class="arrow arrowRight"></span></div>';
    }

    for(let i = 0; i < carousel_img_url_list.length; i++) {

        var redirect_url = redirect_url_list[i];
        if (redirect_url == "") {
            redirect_url = "javascript:void(0)"
        }

        html += '<div style="cursor: pointer;" class="GallarySlidesimageHolder">';
        html += '<img vlink="' + redirect_url + '" onclick="open_link_banner(this)" src="' + carousel_img_url_list[i] + '"></div>'
    }

    html += "</div>";

    if (carousel_img_url_list.length > 1) {
        html += '<div id="GallarydotsContainer"></div>';
    }

    html += '</div>';

    document.getElementById("easychat-chat-container").innerHTML += html;
}

function open_link_banner(el) {
    var url = el.getAttribute("vlink")
    var pattern = /^((http|https|ftp):\/\/)/;
    if (!pattern.test(url)) {
        url = "http://" + url;
    }
    window.open(url);
}

//function open_link_banner(el){window.open(el.getAttribute("vlink"));}

function remove_banner() {
    var elements = document.getElementsByClassName("galleryContainer");
    if (elements) {
        while (elements.length > 0) {
            elements[0].parentNode.removeChild(elements[0]);
        }

    }
}

function remove_feedback_div() {
    var elements = document.getElementsByClassName("easychat-intent-feedback-wrapper");
    for(let i = 0; i < elements.length; i++) {
        if (elements[i].getAttribute("feedback_submitted") != "true") {
            elements[i].parentNode.removeChild(elements[i]);
        }
    }
}

function init_gallery() {

    GallaryslideIndex = 0;
    gallery_slides = document.getElementsByClassName("GallarySlidesimageHolder");
    gallery_slides[GallaryslideIndex].style.opacity = 1;
    for (i = 0; i < gallery_slides.length; i++) {
        gallery_slides[i].style.display = "none";
    }
    gallery_slides[GallaryslideIndex].style.display = "block";

    //disable nextPrevBtn if slide count is one
    if (gallery_slides.length < 2) {
        var nextPrevBtns = document.querySelector(".leftArrow,.rightArrow");
        if (nextPrevBtns != undefined && nextPrevBtns != null) {
            nextPrevBtns.style.display = "none";
            for (i = 0; i < nextPrevBtns.length; i++) {
                nextPrevBtns[i].style.display = "none";
            }
        }
    }

    //add gallery_dots
    gallery_dots = [];
    try {
        var dotsContainer = document.getElementById("GallarydotsContainer"),
            i;
        for (i = 0; i < gallery_slides.length; i++) {
            var dot = document.createElement("span");
            dot.classList.add("gallary_dots");
            dotsContainer.append(dot);
            dot.setAttribute("onclick", "move_slide(" + i + ")");
            gallery_dots.push(dot);
        }
        gallery_dots[GallaryslideIndex].classList.add("active");
    } catch (e) {}
}

function move_gallary_slides(n) {
    move_slide(GallaryslideIndex + n);
}

function move_slide(n) {
    var i;
    var current, next;
    var move_slideAnimClass = {
        forCurrent: "",
        forNext: ""
    };

    var slideTextAnimClass;
    for (i = 0; i < gallery_slides.length; i++) {
        gallery_slides[i].style.display = "none";
    }
    if (n > GallaryslideIndex) {
        if (n >= gallery_slides.length) {
            n = 0;
        }
        move_slideAnimClass.forCurrent = "moveLeftCurrentSlide";
        move_slideAnimClass.forNext = "moveLeftNextSlide";
        slideTextAnimClass = "slideTextFromTop";
    } else if (n < GallaryslideIndex) {
        if (n < 0) {
            n = gallery_slides.length - 1;
        }
        move_slideAnimClass.forCurrent = "moveRightCurrentSlide";
        move_slideAnimClass.forNext = "moveRightPrevSlide";
        slideTextAnimClass = "slideTextFromBottom";
    }

    gallery_slides[n].style.display = "block";

    if (n != GallaryslideIndex) {
        next = gallery_slides[n];
        current = gallery_slides[GallaryslideIndex];
        for (i = 0; i < gallery_slides.length; i++) {
            gallery_slides[i].className = "GallarySlidesimageHolder";
            gallery_slides[i].style.opacity = 0;
            gallery_dots[i].className = gallery_dots[i].className.replace(/\bactive\b/g, "");
            document.getElementsByClassName("gallary_dots")[i].className = document.getElementsByClassName("gallary_dots")[i].className.replace(/\bactive\b/g, "");
        }
        current.classList.add(move_slideAnimClass.forCurrent);
        next.classList.add(move_slideAnimClass.forNext);
        gallery_dots[n].className = "gallary_dots active"
        document.getElementsByClassName("gallary_dots")[n].className = "gallary_dots active"
        GallaryslideIndex = n;
    }

}

// function get_url_vars() {
//     var vars = {};
//     var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m, key, value) {
//         vars[key] = value;
//     });
//     return vars;
// }

function create_issue(element) {
    name = document.getElementById("new-issue-name").value;
    document.getElementById("create-issue-error-message").innerHTML = "";

    if (name == "") {
        //showToast("Please enter your name.");
        document.getElementById("create-issue-error-message").innerHTML = "Please enter your name.";
        return;
    }

    if (!/^[a-zA-Z ]*$/.test(name)) {
        // showToast("Please enter a valid name.");
        document.getElementById("create-issue-error-message").innerHTML = "Please enter a valid name.";
        return;
    }

    let phone_no = document.getElementById("new-issue-phone").value;
    if (phone_no == "" || phone_no.length != 10) {
        // showToast("Please enter your 10 digits mobile number.");
        document.getElementById("create-issue-error-message").innerHTML = "Please enter your 10 digits mobile number";
        return;
    }

    if (phone_no.length != 10 || !/^\d{10}$/.test(phone_no)) {
        // showToast("Please enter a valid phone no.");
        document.getElementById("create-issue-error-message").innerHTML = "Please enter a valid phone no.";
        return;
    }

    let issue = document.getElementById("new-issue-issue").value;
    if (issue == "") {
        // showToast("Please describe your issue.");
        document.getElementById("create-issue-error-message").innerHTML = "Please describe your issue.";
        return;
    }

    let priority = document.getElementById("ticket-priority").value;
    if (priority == "") {
        // showToast("Please select the priority.");
        document.getElementById("create-issue-error-message").innerHTML = "Please select the priority.";
        return;
    }

    let category = document.getElementById("ticket-category").value;
    if (category == "") {
        // showToast("Please select the category.");
        document.getElementById("create-issue-error-message").innerHTML = "Please select the category.";
        return;
    }

    // bot_id = getUrlVars()["id"]

    let json_string = JSON.stringify({
        name: name,
        phone_no: phone_no,
        email: "",
        issue: issue,
        priority: priority,
        category: category,
        // bot_id:"bot_id"
    });
    json_string = encrypt_variable(json_string);

    var CSRF_TOKEN = get_csrf_token();
    $.ajax({
        url: '/tms/create-issue/',
        type: 'POST',
        headers: {
            'X-CSRFToken': CSRF_TOKEN
        },
        data: {
            data: json_string
        },
        success: function(response) {
            response = easyassist_custom_decrypt(response["response"])
            response = JSON.parse(response);
            if (response["status_code"] == 200 && response["ticket_id"] != "") {

                modal_create_issue.style.display = "none";
                // appendResponseServer("Thank you for submitting your issue. Our agent will contact you soon.",false, "", "", "");
                // message = "Thank you for submitting your issue. Our agent will contact you soon.";
                message = "Thank you for reporting your issue. Your Ticket ID is " + response["ticket_id"] + ". Kindly save it for further reference. Our customer service agent will contact you shortly."
                append_bot_text_response(message);
            } else if (response["status_code"] == 305 && response["ticket_id"] != "") {

                modal_create_issue.style.display = "none";
                message = "Your issue has been registred. Your Ticket ID is " + response["ticket_id"] + " Today our office is closed. We will proceed with your issue as soon as possible."
                append_bot_text_response(message);
            } else {

                console.log("Please report this. ", response["status_message"]);
            }

            scroll_to_bottom();
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        }
    });
}

function schedule_meeting(element) {
    document.getElementById("schedule-error-message").innerHTML = "";
    name = document.getElementById("new-meeting-name").value;

    if (name == "") {
        // showToast("Please enter your name.");
        document.getElementById("schedule-error-message").innerHTML = "Please enter your name";
        return;
    }
    if (!/^[a-zA-Z ]*$/.test(name)) {
        // showToast("Please enter a valid name.");
        document.getElementById("schedule-error-message").innerHTML = "Please enter a valid name";
        return;
    }

    phone_no = document.getElementById("new-meeting-phone").value;
    if (phone_no == "" || phone_no.length != 10) {
        // showToast("Please enter your 10 digits mobile number.");
        document.getElementById("schedule-error-message").innerHTML = "Please enter 10 digits mobile number";
        return;
    }

    if (phone_no.length != 10 || !/^\d{10}$/.test(phone_no)) {
        // showToast("Please enter a valid phone no.");
        document.getElementById("schedule-error-message").innerHTML = "Please enter a valid phone no.";
        return;
    }

    // meet_agent_date_time = document.getElementById("new-meeting-date-time").value;
    // if(meet_agent_date_time == ""){
    //   document.getElementById("schedule-error-message").innerHTML="Please enter date and time.";
    //   // showToast("Please enter date and time.");
    //   return;
    // }

    // meet_year = meet_agent_date_time.split("T")[0].split("-")[0]
    // meet_month = meet_agent_date_time.split("T")[0].split("-")[1]
    // meet_date = meet_agent_date_time.split("T")[0].split("-")[2]

    // if(meet_year < new Date().getFullYear())
    // {
    //   document.getElementById("schedule-error-message").innerHTML="Please enter valid year.";
    //   // showToast("Please enter valid year.");
    //   return;
    // }
    // else if(meet_year == new Date().getFullYear() && meet_month < new Date().getMonth())
    // {
    //   document.getElementById("schedule-error-message").innerHTML="Please enter valid month.";
    //   //showToast("Please enter valid month.");
    //   return;
    // }
    // else if(meet_year == new Date().getFullYear() && meet_date < new Date().getDate())
    // {
    //   document.getElementById("schedule-error-message").innerHTML="Please enter valid date.";
    //   //showToast("Please enter valid date.");
    //   return;
    // }
    // if(meet_year == new Date().getFullYear() && meet_date == new Date().getDate())
    // {
    //     meet_hour = meet_agent_date_time.split("T")[1].split(":")[0]
    //     meet_minute = meet_agent_date_time.split("T")[1].split(":")[1]
    //     meet_hour = parseInt(meet_hour)
    //     meet_minute = parseInt(meet_minute)
    //     current_hour = new Date().getHours().toString()
    //     current_min = new Date().getMinutes().toString()
    //     if(meet_hour < current_hour){
    //         document.getElementById("schedule-error-message").innerHTML="Please enter valid time.";
    //         //showToast("Please enter valid date.");
    //         return;
    //     }
    //     else if(meet_hour == current_hour && meet_minute < current_min){
    //         document.getElementById("schedule-error-message").innerHTML="Please enter valid time.";
    //         //showToast("Please enter valid date.");
    //         return;
    //     }

    // }

    //Meeting Date

    let meet_date = document.getElementById("new-meeting-date").value;
    if (meet_date == "") {
        // showToast("Please enter meeting date.")
        document.getElementById("schedule-error-message").innerHTML = "Please enter date.";
        return;
    }

    let meet_date_year = meet_date.split("-")[0]
    let meet_date_month = meet_date.split("-")[1]
    let meet_date_date = meet_date.split("-")[2]

    if (meet_date_year < new Date().getFullYear()) {
        // console.log("Year problem.")
        // showToast("Please enter a valid year.")
        document.getElementById("schedule-error-message").innerHTML = "Please enter a valid year.";
        return;
    } else if (meet_date_year == new Date().getFullYear() && meet_date_month < (new Date().getMonth() + 1)) {
        // console.log("Month problem.")
        // showToast("Please enter a valid month.")
        document.getElementById("schedule-error-message").innerHTML = "Please enter a valid year.";
        return;
    } else if (meet_date_year == new Date().getFullYear() && meet_date_month == (new Date().getMonth() + 1) && meet_date_date < new Date().getDate()) {
        // console.log("Date Problem.")
        // showToast("Please enter a valid date.")
        document.getElementById("schedule-error-message").innerHTML = "Please enter a valid year.";
        return;
    }

    // Meeting Time
    let meet_time = document.getElementById("new-meeting-time").value;
    if (meet_time == "") {
        // showToast("Please enter meeting time.")
        document.getElementById("schedule-error-message").innerHTML = "Please enter meeting time.";
        return;
    }
    if (meet_date_year == new Date().getFullYear() && meet_date_month == (new Date().getMonth() + 1) && meet_date_date == new Date().getDate()) {
        let meet_time_hour = meet_time.split(":")[0]
        meet_time_hour = parseInt(meet_time_hour)

        let meet_time_minute = meet_time.split(":")[1]
        meet_time_minute = parseInt(meet_time_minute)

        let current_hour = new Date().getHours()
        let current_minute = new Date().getMinutes()
        if (meet_time_hour < current_hour) {
            // showToast("Please enter valid time.")
            document.getElementById("schedule-error-message").innerHTML = "Please enter valid time.";
            return;
        } else if (meet_time_hour == current_hour && meet_time_minute < current_minute) {
            // showToast("Please enter valid time.");
            document.getElementById("schedule-error-message").innerHTML = "Please enter valid time.";
            return;
        }
    }

    let meet_agent_date_time = meet_date + "T" + meet_time

    let user_pincode = document.getElementById("new-meeting-pincode").value;

    issue = document.getElementById("new-meeting-issue").value;
    if (issue == "") {
        //showToast("Please describe your issue.");
        document.getElementById("schedule-error-message").innerHTML = "Please describe your issue";
        return;
    }

    json_string = JSON.stringify({
        name: name,
        phone_no: phone_no,
        email: "",
        issue: issue,
        meet_agent_date_time: meet_agent_date_time,
        user_pincode: user_pincode
    });
    json_string = encrypt_variable(json_string);

    var CSRF_TOKEN = get_csrf_token();
    $.ajax({
        url: '/tms/schedule-meeting/',
        type: 'POST',
        headers: {
            'X-CSRFToken': CSRF_TOKEN
        },
        data: {
            data: json_string
        },
        success: function(response) {
            response = easyassist_custom_decrypt(response["response"])
            response = JSON.parse(response);
            if (response["status_code"] == 200 && response["meeting_id"] != "") {
                modal_schedule_meeting.style.display = "none";
                // appendResponseServer("Thank you for scheduling the meeting. Our agent will contact you soon.",false, "", "", "");
                message = "Thank you for scheduling the meeting. Your Meeting ID is " + response["meeting_id"] + " .Kindly save it for further reference. Our customer service agent will contact you shortly."
                // message = "Thank you for scheduling the meeting. Our agent will contact you soon.";
                append_bot_text_response(message);
            } else {
                // showToast("Unable to schedule meeting due to some internal server error. Kindly report the same", 2000);
                console.log("Please report this. ", response["status_message"]);
            }

            scroll_to_bottom();
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        }
    });
}

function check_ticket_status(element) {
    document.getElementById("ticket-status-error-message").innerHTML = "";
    let ticket_id = document.getElementById("check-ticket-id").value;
    if (ticket_id == "") {
        // showToast("Please enter your ticket id.");
        document.getElementById("ticket-status-error-message").innerHTML = "Please enter your ticket id.";
        return;
    }
    json_string = JSON.stringify({
        ticket_id: ticket_id,
    });
    json_string = encrypt_variable(json_string);

    var CSRF_TOKEN = get_csrf_token();
    $.ajax({
        url: '/tms/check-ticket-status/',
        type: 'POST',
        headers: {
            'X-CSRFToken': CSRF_TOKEN
        },
        data: {
            data: json_string
        },
        success: function(response) {
            response = easyassist_custom_decrypt(response["response"])
            response = JSON.parse(response);
            if (response["status_code"] == 200 && response["ticket_exist"] == true) {
                // $('#modal-check-ticket-status').modal('close');
                modal_check_ticket_status.style.display = "none";
                message = response["ticket_status_message_response"]
                append_bot_text_response(message);
            } else if (response["ticket_exist"] == false) {
                // $('#modal-check-ticket-status').modal('close');
                modal_check_ticket_status.style.display = "none";
                message = "Sorry, no such ticket found. Please check your Ticket ID and try again."
                append_bot_text_response(message);
            } else {
                showToast("Unable to get your ticket due to some internal server error. Kindly report the same", 2000);
                console.log("Please report this. ", response["status_message"]);
            }
            scroll_to_bottom();
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        }
    });
}

function check_meeting_status(element) {
    document.getElementById("meeting-status-error-message").innerHTML = "";
    let meeting_id = document.getElementById("check-meeting-id").value;
    if (meeting_id == "") {
        // showToast("Please enter your meeting id.");
        document.getElementById("meeting-status-error-message").innerHTML = "Please enter your meeting id.";
        return;
    }
    json_string = JSON.stringify({
        meeting_id: meeting_id,
    });
    json_string = encrypt_variable(json_string);

    var CSRF_TOKEN = get_csrf_token();
    $.ajax({
        url: '/tms/check-meeting-status/',
        type: 'POST',
        headers: {
            'X-CSRFToken': CSRF_TOKEN
        },
        data: {
            data: json_string
        },
        success: function(response) {
            response = easyassist_custom_decrypt(response["response"])
            response = JSON.parse(response);
            if (response["status_code"] == 200 && response["meeting_exist"] == true) {
                // $('#modal-check-meeting-status').modal('close');
                modal_check_meeting_status.style.display = "none";
                message = response["meeting_status_message_response"]
                append_bot_text_response(message);
            } else if (response["meeting_exist"] == false) {
                // $('#modal-check-meeting-status').modal('close');
                modal_check_meeting_status.style.display = "none";
                message = "Sorry, no such meeting found. Please check your Meeting ID and try again."
                append_bot_text_response(message);
            } else {
                showToast("Unable to submit your issue due to some internal server error. Kindly report the same", 2000);
                console.log("Please report this. ", response["status_message"]);
            }
            scroll_to_bottom();
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        }
    });
}

$(document).ready(function() {
    $(':input').on('focus', function() {
        $(this).attr('autocomplete', 'off');
    });

    if(initialize_canned_response == "True"){
        initialize_livechat_canned_response();
    }
    
});

//////////////////////////////////////////////////////////////// LiveChat

var liveChatSocket = null;
var agent_assigned = false;
var need_to_add_wel_msg = true;
var chat_socket1 = null;
var check_agent_assign_timer = null;
var customer_info_needed = true;
var email = "not_available";
var phone = "not_available";
var username = "not_available";
var send_ping_to_socket_holder = null;
var livechat_category = "-1";

function append_livechat_response() {

    if (customer_info_needed) {
        disable_user_input();
        append_info_form();
        customer_info_needed = false;
        setTimeout(function() {
            disable_user_input();
        }, 1000);
    } else {
        create_socket1(user_id)
    }
}

function create_customer(bot_id, session_id, user_id, email, phone, username, livechat_category) {

    var json_string = JSON.stringify({
        bot_id: bot_id,
        session_id: session_id,
        user_id: user_id,
        username: username,
        phone: phone,
        email: email,
        livechat_category: livechat_category,
    });
    json_string = encrypt_variable(json_string);

    var CSRF = $('input[name="csrfmiddlewaretoken"]').val();
    $.ajax({
        url: '/livechat/create-customer/',
        type: 'POST',
        headers: {
            'X-CSRFToken': CSRF
        },
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = easyassist_custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status_code"] == 200) {

                check_agent_assign_timer = setInterval(assign_agent, 5000);
            } else {
                M.toast({
                    "html": "Unable to delete due to some internal server error. Kindly report the same"
                }, 2000);
                console.log("Please report this. ", response["status_message"]);
            }
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        }
    });

    //check_agent_assign_timer = setInterval(assign_agent, 5000);
}


function assign_agent() {
    var json_string = JSON.stringify({
        user_id: user_id,
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string;
    xhttp.open("POST", '/livechat/assign-agent/', true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            // console.log("Agent Assigned!!!");
            agent_assigned = true;
            // console.log(typeof(this.response))
            response = this.response
            response = JSON.parse(response)
            response = easyassist_custom_decrypt(response)
            response = JSON.parse(response);
            let assigned_agent = response["assigned_agent"]
            if (assigned_agent == "None") {
                agent_assigned = false;
                need_to_add_wel_msg = true;
            } else if (assigned_agent == "not_available") {

                let message = "Our agent is unable to connect you.<br>Please wait, we are connecting you to other agent."
                append_system_text_response(message);
                need_to_add_wel_msg = true;
                scroll_to_bottom();
            } else if (assigned_agent == "session_end") {
                is_livechat = false;
                chat_socket1.close();
                clearInterval(check_agent_assign_timer);
                need_to_add_wel_msg = true;
                scroll_to_bottom();
            } else if (assigned_agent == "no_cutomer_online") {
                chat_socket1.close()
            } else {
                if (need_to_add_wel_msg) {
                    let message = "<b>" + assigned_agent + "</b> has joined the chat. Please ask your queries now.<br>"
                    append_system_text_response(message);
                    message = assigned_agent + " has joined the chat. Please ask your queries now."
                    save_customer_chat(message, user_id, "system")
                    need_to_add_wel_msg = false;
                    scroll_to_bottom();
                }
            }
        }
    }
    xhttp.send(params);
}

function send_ping_to_socket() {
    var sentence = JSON.stringify({
        'message': "eyJhbGciOiJkeySUzI1NiJ9.eyJqdGkiOiIyMzE3",
        'sender': 'system1',
        'file_type': ''
    });
    chat_socket1.send(sentence);
}

function create_socket1(user_id) {

    is_livechat = true;
    if (window.location.protocol == "http:") {
        chat_socket1 = new WebSocket(
            'ws://' + window.location.host +
            '/ws/' + user_id + '/customer/');
    } else {

        chat_socket1 = new WebSocket(
            'wss://' + window.location.host +
            '/ws/' + user_id + '/customer/');
    }

    chat_socket1.onmessage = function(e) {
        var data = JSON.parse(e.data);
        // console.log(data)
        let message = data['message'];
        var sender = data['sender'];
        var file_type = data['file_type'];
        if (sender == "agent" && message == "eyJhbGciOiJSUzI1NiJ9.eyJqdGkiOiIyMzE3") {

            append_feedback_form();
            scroll_to_bottom();
        } else if (sender == "agent") {
            if (file_type == 'file') {
                let file_path = message.split("$*$*$*")[0]
                message = message.split("$*$*$*")[1]
                append_file_to_customer(file_path, message);
                scroll_to_bottom();
            } else {
                append_bot_text_response(message);
                scroll_to_bottom();
            }
        } else if (sender == "system") {

            append_system_text_response(message);
        }
    }

    chat_socket1.onclose = function(e) {
        console.log('Chat socket closed unexpectedly');
        if (is_livechat == true) {
            append_system_text_response("All our chat representatives are busy attending to customers, please try again later.");
            append_bot_text_response("Hi, I am your personal virtual assistant. How may I assist you further?");
            scroll_to_bottom();
        }
        is_livechat = false;
        clearInterval(send_ping_to_socket_holder);
        clearInterval(check_agent_assign_timer);
        need_to_add_wel_msg = true;
    };

    chat_socket1.onopen = function(e) {
        console.log("Connection established.")
        is_livechat = true;
        create_customer(bot_id, session_id, user_id, email, phone, username, livechat_category)
        send_ping_to_socket_holder = setInterval(send_ping_to_socket, 1000);
    }
    scroll_to_bottom();
}

function append_feedback_form() {

    append_system_text_response("Agent has left the session. LiveChat session ended.");
    disable_user_input()

    user_input = "It was great helping you. Your feedback help us to improvise our service quality.\nPlease rate your agent.";
    var time = return_time();
    var html = '<div class="rating-bar-container__wrapper" style="width: 92%;margin: auto;margin-top: 1em;">\
                <div id="rating-bar-container__XqPZ" class="rating-bar-container" zQPK="false" onmouseout="change_color_ratingz_bar_all(this)">\
                <button id="rating-bar-button__01" onmouseover="change_color_ratingv_bar(this)" onmouseout="change_color_ratingz_bar(this)" onclick="set_value_to_some(this)" value="1">1</button><button id="rating-bar-button__02" onclick="set_value_to_some(this)" onmouseover="change_color_ratingv_bar(this)" onmouseout="change_color_ratingz_bar(this)" value="2">2</button><button id="rating-bar-button__03" onmouseover="change_color_ratingv_bar(this)" onclick="set_value_to_some(this)" onmouseout="change_color_ratingz_bar(this)" value="3">3</button><button id="rating-bar-button__04" onclick="set_value_to_some(this)" onmouseover="change_color_ratingv_bar(this)" onmouseout="change_color_ratingz_bar(this)" value="4">4</button><button id="rating-bar-button__05" onmouseover="change_color_ratingv_bar(this)" onclick="set_value_to_some(this)" onmouseout="change_color_ratingz_bar(this)" value="5">5</button><button id="rating-bar-button__06" onclick="set_value_to_some(this)" onmouseover="change_color_ratingv_bar(this)" onmouseout="change_color_ratingz_bar(this)" value="6">6</button><button id="rating-bar-button__07" onmouseover="change_color_ratingv_bar(this)" onclick="set_value_to_some(this)" onmouseout="change_color_ratingz_bar(this)" value="7">7</button><button id="rating-bar-button__08" onclick="set_value_to_some(this)" onmouseover="change_color_ratingv_bar(this)" onmouseout="change_color_ratingz_bar(this)" value="8">8</button><button id="rating-bar-button__09" onmouseover="change_color_ratingv_bar(this)" onclick="set_value_to_some(this)" onmouseout="change_color_ratingz_bar(this)" value="9">9</button><button id="rating-bar-button__10" onclick="set_value_to_some(this)" onmouseover="change_color_ratingv_bar(this)" onmouseout="change_color_ratingz_bar(this)" value="10">10</button>\
                </div><br><div style="width:30%;margin:auto;"><span id="rating-bar-container-timer__XqPZ"></span></div></div>';
    document.getElementById("easychat-chat-container").innerHTML += '<div id="livechat_feedback" style="display:inline-block;"><div style="box-shadow: 1px 1px 6px rgba(0, 0, 0, 0.2);color: black;width: 80%;margin: auto;margin-top: 1.5em;border-radius: 1em;padding: 1em;background-color:white;">' + user_input + html + '</div></div>';
    scroll_to_bottom();
    feedback_timer_fun();
    // document.getElementById("easychat-chat-container").innerHTML += html;

}

function feedback_timer_fun() {
    var timer_value = 60
    let ratingTimer = setInterval(function() {
        if (timer_value < 10) {
            document.getElementById("rating-bar-container-timer__XqPZ").textContent = "00:0" + timer_value;
        } else {
            document.getElementById("rating-bar-container-timer__XqPZ").textContent = "00:" + timer_value;
        }
        if (timer_value <= 10) {
            // document.getElementById("rating-bar-container-timer__XqPZ").style.border = "solid red";
            document.getElementById("rating-bar-container-timer__XqPZ").style.color = "red";
        }
        if (timer_value > 10 && timer_value <= 30) {
            // document.getElementById("rating-bar-container-timer__XqPZ").style.border = "solid orange";
            document.getElementById("rating-bar-container-timer__XqPZ").style.color = "orange";
        }
        if (timer_value > 30) {
            // document.getElementById("rating-bar-container-timer__XqPZ").style.border = "solid green";
            document.getElementById("rating-bar-container-timer__XqPZ").style.color = "green";
        }
        timer_value = timer_value - 1;
        if (timer_value == -1) {
            document.getElementById("livechat_feedback").remove()
            append_bot_text_response("Hi, I am your personal virtual assistant. How may I assist you further?");
            clearInterval(ratingTimer);
            scroll_to_bottom();
            enable_user_input();
        }
    }, 1000);

}

function set_value_to_some(el) {
    el.parentElement.setAttribute("zQPK", "true")
    var rate_value = el.getAttribute("value")
    clearInterval(ratingTimer);
    save_livechat_feedback(rate_value, user_id);
    // el.parentElement.parentElement.remove()
    document.getElementById("livechat_feedback").remove()
    append_bot_text_response("Thank you for connecting us. Hoping to help you in future.");
    append_bot_text_response("Hi, I am your personal virtual assistant. How may I assist you further?");
    scroll_to_bottom();
    enable_user_input()
}

function change_color_ratingz_bar_all(el) {
    let current_hover_value = parseInt(el.childElementCount);
    if (el.getAttribute("zQPK") == "false") {
        for(let i = 0; i <= current_hover_value; i++) {
            if (el.children[i] != undefined) {
                el.children[i].style.color = "black"
                el.children[i].style.backgroundColor = "white"
            }
        }
    }
}

function change_color_ratingz_bar(el) {
    current_hover_value = parseInt(el.getAttribute("value"));
    for(let i = current_hover_value; i <= current_hover_value; i++) {
        if (el.parentElement.children[i] != undefined) {
            el.parentElement.children[i].style.color = "black"
            el.parentElement.children[i].style.backgroundColor = "white"
        }
    }
}

function change_color_ratingv_bar(el) {
    current_hover_value = parseInt(el.getAttribute("value"));
    for(let i = 0; i < current_hover_value; i++) {
        if (current_hover_value <= 6) {
            el.parentElement.children[i].style.color = "white"
            el.parentElement.children[i].style.backgroundColor = "red"
        }
        if (6 < current_hover_value && current_hover_value <= 8) {
            el.parentElement.children[i].style.color = "white"
            el.parentElement.children[i].style.backgroundColor = "orange"
        }
        if (8 < current_hover_value) {
            el.parentElement.children[i].style.color = "white"
            el.parentElement.children[i].style.backgroundColor = "green"
        }
    }
    for(let j = current_hover_value; j <= el.parentElement.childElementCount; j++) {
        if (el.parentElement.children[j] != undefined) {
            el.parentElement.children[j].style.color = "black"
            el.parentElement.children[j].style.backgroundColor = "white"
        }
    }
}


function save_livechat_feedback(rate_value, user_id) {

    var json_string = JSON.stringify({
        user_id: user_id,
        rate_value: rate_value
    });

    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
    xhttp.open("POST", '/livechat/save-livechat-feedback/', true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log("Rating updated successfully!!!")
        }
    }
    xhttp.send(params);
}


function save_customer_chat(sentence, user_id, sender) {

    var json_string = JSON.stringify({
        message: sentence,
        user_id: user_id,
        sender: sender,
        attached_file_src: ""
    });
    json_string = encrypt_variable(json_string);

    var CSRF = $('input[name="csrfmiddlewaretoken"]').val();
    $.ajax({
        url: '/livechat/save-customer-chat/',
        type: "POST",
        headers: {
            'X-CSRFToken': CSRF
        },
        async: false,
        data: {
            json_string: json_string
        },
        success: function(response) {

            response = easyassist_custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {} else {
                console.log("chat send by agent saved");
            }
        }
    });
}

// var mark_offline_var = false;
window.onbeforeunload = function(e) {
    cancel_text_to_speech()
    // clear_userData()
    if (chat_socket1 != null) {
        chat_socket1.close();
    }
}


document.addEventListener("visibilitychange", function() {
    if (document.hidden) {
        cancel_text_to_speech();
    }
}, false);


///////////////////////////////      LiveChat Customer Info     ////////////////////////////

function append_info_form(assigned_agent) {
    var html = '<div id="customer_info_form_modal" class="easychat-modal livechat-agent-modal">\
      <div class="easychat-modal-content livechat-agent-modal-content" style="margin: 17% auto;height:67%;">\
        <span class="easychat-close" onclick="close_customer_info_form_modal()">&times;</span>\
            <div id="customer_info_form_div">\
                <span>Please fill in the following details</span><br>\
                <div>\
                    <p>Name<sup style="color:red;">*</sup></p>\
                    <input id="easychat-customer-name" placeholder="Your Name" style="width:70%;">\
                </div>\
                <div>\
                    <p>Email ID<sup style="color:red;">*</sup></p>\
                    <input id="easychat-customer-email" placeholder="Email" style="width:70%;">\
                </div>\
                <div>\
                    <p>Phone Number<sup style="color:red;">*</sup></p>\
                    <input id="easychat-customer-phone" placeholder="Phone Number" style="width:70%;">\
                </div>\
                <div id="livechat-agent-category-div">\
                </div>\
                <div style="position: absolute; bottom: 7em; right: 4em;">\
                    <input class="livechat-modal-submit-btn" onclick="submit_customer_info()" type="submit">\
                </div>\
                <div id = "easychat_customer_info_form_error" style="display:none;">\
                    <p id = "easychat_customer_info_form_error_ptag" style="color:red;"></p>\
                </div>\
            </div>\
            <div id="cutomer_info_form_termination">\
                <p>To connect our LiveChat agent, you have to fill the previous form.</p><br>\
                <input class="livechat-modal-continue-btn" onclick="submit_continue()" type="submit" value="<< Continue">\
                <input class="livechat-modal-cancel-btn" onclick="submit_go_back()" type="submit" value="Go Back >>">\
            </div>\
      </div>\
    </div>';
    document.getElementById("easychat-chat-container").innerHTML += html;
    append_livechat_category()
    document.getElementById("customer_info_form_modal").style.display = "block";
    disable_user_input();
}

function append_livechat_category() {

    var xhttp = new XMLHttpRequest();
    var params = 'json_string=""';
    xhttp.open("POST", GET_LIVECHAT_CATEGORY, true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {

        if (this.readyState == 4 && this.status == 200) {

            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status_code"] == "200") {
                let category_list = response["category_list"]

                var value = "-1";

                var html = "<p>Category<sup style=\"color:red;\">*</sup></p>\
                                <div class=\"input-field col s12\" style=\"display: block;\">\
                                    <select id=\"livechat-agent-category\" style=\"width:25em;height:3em;\">\
                                        <option value=\"" + value + "\" selected>Choose a category</option>"
                for(let i = 0; i < category_list.length; i++) {

                    html += "<option value=\"" + category_list[i]["pk"] + "\">" + category_list[i]["title"] + "</option>"
                }
                html += "</select>\
                    </div>"
                document.getElementById("livechat-agent-category-div").innerHTML = html;
            }
        }
    }
    xhttp.send(params);

}

function validate_name(id) {

    var regex = /^[a-zA-Z ]{2,30}$/;
    var ctrl = document.getElementById(id);

    if (ctrl.value != "" && regex.test(ctrl.value)) {
        return true;
    } else {
        return false;
    }
}

function validate_phone_number(id) {

    var regex = /[7-9][0-9]{9}/;
    var ctrl = document.getElementById(id);
    console.log(ctrl.value);
    if (ctrl.value != "" && regex.test(ctrl.value) && ctrl.value.length == 10) {
        return true;
    } else {
        return false;
    }
}

function validate_email(id) {

    var regex = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
    var ctrl = document.getElementById(id);

    if (ctrl.value != "" && regex.test(ctrl.value)) {
        return true;
    } else {
        return false;
    }
}

function submit_customer_info() {

    document.getElementById("easychat_customer_info_form_error").style.display = "none";
    if (validate_name("easychat-customer-name") == false) {
        document.getElementById("easychat-customer-name").setAttribute("placeholder", "Please enter a valid name.");
        document.getElementById("easychat_customer_info_form_error").style.display = "block";
        document.getElementById("easychat_customer_info_form_error_ptag").innerHTML = "Please enter a valid name."
        return;
    }
    if (validate_email("easychat-customer-email") == false) {

        document.getElementById("easychat-customer-email").setAttribute("placeholder", "Please enter a valid email.");
        document.getElementById("easychat_customer_info_form_error").style.display = "block";
        document.getElementById("easychat_customer_info_form_error_ptag").innerHTML = "Please enter a valid email."
        return;
    }
    if (validate_phone_number("easychat-customer-phone") == false) {

        document.getElementById("easychat-customer-phone").setAttribute("placeholder", "Please enter a valid phone number.");
        document.getElementById("easychat_customer_info_form_error").style.display = "block";
        document.getElementById("easychat_customer_info_form_error_ptag").innerHTML = "Please enter a valid phone number."
        return;
    }
    email = document.getElementById("easychat-customer-email").value;
    phone = document.getElementById("easychat-customer-phone").value;
    username = document.getElementById("easychat-customer-name").value;
    var element = document.getElementById("livechat-agent-category");
    if (element != undefined && element != null) {
        livechat_category = element.value;
    } else {
        livechat_category = "-1";
    }
    document.getElementById("customer_info_form_modal").remove();
    create_socket1(user_id);
    enable_user_input();

    parent.postMessage({
        event_id: 'create-cobrowsing-lead',
        data: {
            username: username,
            email: email,
            phone: phone
        }
    }, "*");
}

function close_customer_info_form_modal() {

    document.getElementById("customer_info_form_div").style.display = "none";
    document.getElementById("cutomer_info_form_termination").style.display = "block";
    enable_user_input()
}

function submit_continue() {

    document.getElementById("customer_info_form_div").style.display = "block";
    document.getElementById("cutomer_info_form_termination").style.display = "none";
    enable_user_input()
}

function submit_go_back() {

    document.getElementById("customer_info_form_modal").remove();
    customer_info_needed = true
    append_bot_text_response("Hi, I am your personal virtual assistant. How may I assist you further?");
    is_livechat = false
    enable_user_input()
}

function clear_userData() {
    var json_string = JSON.stringify({
        user_id: user_id,
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);
    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string;
    xhttp.open("POST", CLEAR_API_URL, true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
        }
    }
    xhttp.send(params);
    if (chat_socket1 != null) {
        chat_socket1.close();
    }
    if (check_agent_assign_timer != null) {

        clearInterval(check_agent_assign_timer);
    }
}


// ############## NPS  FeedBack js  START #######################
var contentvalue = 10;

function ChangeContent(el) {
    let contentvalue = parseInt(el.getAttribute("value"))
    if (contentvalue <= 2)
        document.getElementById("easychat-rating-circular-bar-content-img").setAttribute("src", "/static/EasyChatApp/img/Very_Sad_Face_Emoji_Icon_ios10_large.png")
    else if (contentvalue > 2 && contentvalue <= 5)
        document.getElementById("easychat-rating-circular-bar-content-img").setAttribute("src", "/static/EasyChatApp/img/face-with-one-eyebrow-raised_1f928.png")
    else if (contentvalue > 5 && contentvalue <= 8) {
        document.getElementById("easychat-rating-circular-bar-content-img").setAttribute("src", "/static/EasyChatApp/img/316a64a45f9c0f6652daf822876dbfe4.png")
    } else if (contentvalue >= 9) {
        document.getElementById("easychat-rating-circular-bar-content-img").setAttribute("src", "/static/EasyChatApp/img/Smiling_Face_Emoji_large.png")
    }
}

function FeedbackModal(el) {
    var temp_value = document.getElementsByClassName("circle-value")
    document.getElementById("easychat-exit-app-feedback").style.display = "none";
    for(let i = 0; i < temp_value.length; i++) {
        temp_value[i].style.strokeWidth = "1.5em"
    }
    el.style.strokeWidth = "2em"
    contentvalue = parseInt(el.getAttribute("value"))
    if (contentvalue < 10) {
        document.getElementById("value-0" + el.getAttribute("value")).style.strokeWidth = "2em"
    } else {
        document.getElementById("value-" + el.getAttribute("value")).style.strokeWidth = "2em"
    }
    document.getElementById("chatbot_feedback_comment_box").style.display = "block";
}

function NoFeedbackGiven() {
    document.getElementById("feedback_modal").style.display = "none";
    save_feedback(contentvalue);
    setCookie("isFeedbackDone", "1")
}

function SubmitFeedback() {
    text_value = document.getElementById("chatbot-comment-box").value;
    document.getElementById("feedback_modal").style.display = "none";
    setCookie("isFeedbackDone", "1")
    save_feedback(contentvalue, text_value)
}
var text_value = '';

function save_feedback(contentvalue, text_value) {
    var json_string = JSON.stringify({
        session_id: session_id,
        user_id: user_id,
        bot_id: bot_id,
        rating: contentvalue,
        comments: text_value
    });

    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);
    var params = 'json_string=' + json_string;
    set_cookie("isFeedbackDone", "1")
    close_chatbot();
    //json_string = EncryptVariable(json_string);
    //json_string = encodeURIComponent(json_string);
    var xhttp = new XMLHttpRequest();
    //var params = 'json_string='+json_string
    xhttp.open("POST", "/chat/save-feedback/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            //console.log("Feedback saved!!!");
        }
    }
    xhttp.send(params);
}

function setValuetoSome(el) {
    el.parentElement.setAttribute("zQPK", "true")
    document.getElementById("easychat-exit-app-feedback").style.display = "none";
    document.getElementById("chatbot_feedback_comment_box").style.display = "block";
}

function changeColorRatingzBarAll(el) {
    current_hover_value = parseInt(el.childElementCount);
    if (el.getAttribute("zQPK") == "false") {
        for(let i = 0; i <= current_hover_value; i++) {
            if (el.children[i] != undefined) {
                el.children[i].style.color = "black"
                el.children[i].style.backgroundColor = "white"
            }
        }
    }
}

function changeColorRatingzBar(el) {
    current_hover_value = parseInt(el.getAttribute("value"));
    for(let i = current_hover_value; i <= current_hover_value; i++) {
        if (el.parentElement.children[i] != undefined) {
            el.parentElement.children[i].style.color = "black"
            el.parentElement.children[i].style.backgroundColor = "white"
        }
    }
}

function changeColorRatingvBar(el) {
    current_hover_value = parseInt(el.getAttribute("value"));
    for(let i = 0; i < current_hover_value; i++) {
        if (current_hover_value <= 6) {
            el.parentElement.children[i].style.color = "white"
            el.parentElement.children[i].style.backgroundColor = "red"
        }
        if (6 < current_hover_value && current_hover_value <= 8) {
            el.parentElement.children[i].style.color = "white"
            el.parentElement.children[i].style.backgroundColor = "orange"
        }
        if (8 < current_hover_value) {
            el.parentElement.children[i].style.color = "white"
            el.parentElement.children[i].style.backgroundColor = "green"
        }
    }
    for(let j = current_hover_value; j <= el.parentElement.childElementCount; j++) {
        if (el.parentElement.children[j] != undefined) {
            el.parentElement.children[j].style.color = "black"
            el.parentElement.children[j].style.backgroundColor = "white"
        }
    }
}

function detectIEEdge() {
    var ua = window.navigator.userAgent;
    var msie = ua.indexOf('MSIE ');
    if (msie > 0) {
        // IE 10 or older => return version number
        return true;
    }
    var trident = ua.indexOf('Trident/');
    if (trident > 0) {
        // IE 11 => return version number
        rv = ua.indexOf('rv:');
        return true;
    }
    var edge = ua.indexOf('Edge/');
    if (edge > 0) {
        // Edge => return version number
        return false;
    }
    // other browser
    return false;
}

// ############## NPS  FeedBack js  END #######################
// ############## Height Adjustment #################

// function changeMiddleContainer() {
//     document.getElementById("easychat-chat-container").style.height = String(window.innerHeight - (document.getElementById("easychat-navbar").offsetHeight + document.getElementById("easychat-footer").offsetHeight)) + "px";
// }

// ############## Cobrowsing Integration Start ####################

function screenshare_with_agent(element) {
    element.innerHTML = "Connecting...";
    document.getElementById("connect-agent-status-error-message").innerHTML = "";
    var full_name = document.getElementById("connect-agent-name").value;
    var mobile_number = document.getElementById("connect-agent-phone").value;
    var regName = /^[a-zA-Z]+ [a-zA-Z]+$/;
    var regMob = /^[6-9]{1}[0-9]{9}$/;

    if (!regName.test(full_name)) {
        document.getElementById("connect-agent-status-error-message").innerHTML = "Please enter full name";
        return;
    }

    if (!regMob.test(mobile_number)) {
        document.getElementById("connect-agent-status-error-message").innerHTML = "Please enter valid 10-digit mobile number";
        return;
    }

    parent.postMessage({
        event_id: 'connect-with-agent',
        data: {
            "full_name": full_name,
            "mobile_number": mobile_number
        }
    }, "*");

    document.getElementById("modal-connect-with-agent").style.display = "none";
}

// function append_connect_with_agent(){
//     var recommendations_html = '<div class="easychat-recommendation-wrapper" align="left">';
//     if(window.EASYCHAT_EASYASSIST_ENABLED=="True"){
//      recommendations_html+= "<div class=\"easychat-recommendation\" onmouseover='custom_button_change(this)' onmouseout='custom_button_change_normal(this)' style=\"border: 0.05em solid "+BOT_THEME_COLOR+";color: "+BOT_THEME_COLOR+"\" onclick=\"show_connect_with_agent_modal(this)\">Connect with expert</div>";
//     }else if(window.EASYCHAT_LIVECHAT_ENABLED=="True"){
//      recommendations_html+= "<div class=\"easychat-recommendation\" onmouseover='custom_button_change(this)' onmouseout='custom_button_change_normal(this)' style=\"border: 0.05em solid "+BOT_THEME_COLOR+";color: "+BOT_THEME_COLOR+"\" onclick=\"append_livechat_response(this)\">Chat with expert</div>";
//     }
//     recommendations_html+="</div>";
//     document.getElementById("easychat-chat-container").innerHTML += recommendations_html;
// }

// ############## Cobrowsing Integration End ########################


window.addEventListener('message', handle_parent_message, false);

var last_typing_name = null;

function handle_parent_message(event) {
    data = JSON.parse(event.data);

    if(data.id == "livechat-typing"){

      if(last_typing_name != data.name){
        hide_bot_typing_loader();
        show_bot_typing_loader(data.name);
      }

      last_typing_name = data.name;
      scroll_to_bottom_instant();
      if(livechat_typing_loader_show_interval != null){
        clearTimeout(livechat_typing_loader_show_interval)
      }
      livechat_typing_loader_show_interval = setTimeout(function(e) {
        hide_bot_typing_loader();
      }, 2000);
      return;
    }

    if(data.id == "agent_name")
    {
      session_id = data.session_id;
      agent_name = data.name;
      // agent_connect_message = data.agent_connect_message;
      // if(agent_connect_message != null && agent_connect_message != undefined && agent_connect_message.length > 0)
      //   send_user_input(agent_connect_message);
      return ;
    }
    if("focus_textbox" in data){
        setTimeout(function(){
            reset_size_of_text_field_all();
        },900);
        return;
    }
    var time = null;
    if("time" in data) {
        time = data.time;
    } else {
        time = return_time();
    }

    if(data.attachment == "None") data.attachment = null;
    if("sender" in data && "name" in data && data.sender != "client"){
        data.name = "Agent: " + data.name;
    }

    if("show_client_message" in data) {
        hide_bot_typing_loader();
        if(data.chat_type == "chat_bubble"){
            append_system_text_response(data.message);
        } else {
            if(data.attachment != null) {
                var attachment_message = data.message;
                if(data.message != null && data.message.trim() != "") {
                    attachment_message = data.message.trim();
                } else {
                    attachment_message = "";
                }
                append_attachment_and_message_in_chat(attachment_message, data.attachment, data.attachment_file_name, time, "client", data.name, data.agent_profile_pic_source);
            } else  {
                if(data.message != null && data.message.trim() != "") {
                    append_bot_text_response(data.message, data.name, time, data.agent_profile_pic_source);
                }
            }
        }
    } else if("show_agent_message" in data) {
        hide_bot_typing_loader();
        if(data.chat_type == "chat_bubble"){
            append_system_text_response(data.message);
        } else {
            if(data.attachment != null) {
                var attachment_message = data.message;
                if(data.message != null && data.message.trim() != "") {
                    attachment_message = data.message.trim();
                } else {
                    attachment_message = "";
                }
                append_attachment_and_message_in_chat(attachment_message, data.attachment, data.attachment_file_name, time, "agent", data.name, data.agent_profile_pic_source);
            } else {
                if(data.message != null && data.message.trim() != "") {
                    document.getElementById("easychat-chat-container").innerHTML += '<div class="easychat-user-message-div"><div class="easychat-user-message" style="background-color:' + BOT_THEME_COLOR + ';color: ' + USER_MESSAGE_COLOR + '"><div class="easychat-user-message-line">'+ data.message + '</div></div><span class="message-time-user">' + time + '</span></div>';
                }
            }
        }
    } else if("show_other_agent_message" in data) {
        hide_bot_typing_loader();
        if(data.chat_type == "chat_bubble"){
            append_system_text_response(data.message);
        } else {
            if(data.attachment != null) {
                var attachment_message = data.message;
                if(data.message != null && data.message.trim() != "") {
                    attachment_message = data.message.trim();
                } else {
                    attachment_message = "";
                }
                append_attachment_and_message_in_chat(attachment_message, data.attachment, data.attachment_file_name, time, "invited_agent", data.name, data.agent_profile_pic_source);
            } else {
                if (data.message != null && data.message.trim() != "") {
                    if (window.DISPLAY_AGENT_PROFILE == "True" && data.agent_profile_pic_source != "" && data.agent_profile_pic_source != undefined) {
                        let src = "/"  + data.agent_profile_pic_source;
                        var insider = '<div class="easychat-bot-msg-sender-profile">\
                                            <img src = "'+ src + '"/>\
                                        </div>';
                    } else {
                        var insider = '<div class="easychat-bot-msg-sender-profile" style="background-color: ' + BOT_THEME_COLOR + '">\
                                        <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                            <path d="M20 6.99892C20.5304 6.99892 21.0391 7.20964 21.4142 7.58471C21.7893 7.95978 22 8.46849 22 8.99892V12.9989C22 13.5294 21.7893 14.0381 21.4142 14.4131C21.0391 14.7882 20.5304 14.9989 20 14.9989H18.938C18.6942 16.9322 17.7533 18.7101 16.2917 19.9989C14.8302 21.2877 12.9486 21.9989 11 21.9989V19.9989C12.5913 19.9989 14.1174 19.3668 15.2426 18.2416C16.3679 17.1163 17 15.5902 17 13.9989V7.99892C17 6.40762 16.3679 4.8815 15.2426 3.75628C14.1174 2.63106 12.5913 1.99892 11 1.99892C9.4087 1.99892 7.88258 2.63106 6.75736 3.75628C5.63214 4.8815 5 6.40762 5 7.99892V14.9989H2C1.46957 14.9989 0.960859 14.7882 0.585786 14.4131C0.210714 14.0381 0 13.5294 0 12.9989V8.99892C0 8.46849 0.210714 7.95978 0.585786 7.58471C0.960859 7.20964 1.46957 6.99892 2 6.99892H3.062C3.30603 5.06582 4.24708 3.2882 5.70857 1.9996C7.17007 0.711003 9.05155 0 11 0C12.9484 0 14.8299 0.711003 16.2914 1.9996C17.7529 3.2882 18.694 5.06582 18.938 6.99892H20ZM6.76 14.7839L7.82 13.0879C8.77308 13.685 9.87537 14.0007 11 13.9989C12.1246 14.0007 13.2269 13.685 14.18 13.0879L15.24 14.7839C13.9693 15.5801 12.4995 16.0012 11 15.9989C9.50046 16.0012 8.03074 15.5801 6.76 14.7839Z" fill="white"/>\
                                        </svg>\
                                    </div>';
                    }
                
                    var html = ['<div class="easychat-bot-message-div">',
                                    '<div style="display: flex; flex-direction: row;">',
                                        insider,
                                        '<div class="easychat-bot-message" style="color: ' + BOT_MESSAGE_COLOR + ';">',
                                            '<div class="easychat-bot-message-name" style="color: ' + BOT_THEME_COLOR + '">' + data.name + '</div>',
                                            '<div class="easychat-bot-message-line">',
                                                '<div class="easychat-show-less-text">' + data.message + '</div>',
                                            '</div>',
                                            '<div class=view_more_wrapper style="margin-right:5px;display:none ">',
                                                '<div style="margin-right: 12px !important;padding-bottom: 7px;float:right;cursor: pointer;" onclick="viewMore(this)">',
                                                   ' View More<i class="fa fa-chevron-down" style="color:' + BOT_THEME_COLOR + ';margin-left:5px"></i>',
                                                '</div>',
                                            '</div>',
                                        '</div>',
                                    '</div>',
                                    '<span class="message-time-bot">' + time + '</span>',
                                '</div>'].join(' ');
                    document.getElementById("easychat-chat-container").innerHTML += html;
                }
            }
        }
    }
    scroll_to_bottom_instant();
    is_cobrowsing_chat = true;
}

function open_file_explorer(element) {
    $("#file-attachment").click();
}

function hide_file_name_modal_container() {
    document.getElementById("easyassist-upload-file-name-container").innerHTML = "";
}

function stop_file_upload_progress_bar() {
    var progress_divs = document.getElementsByClassName("progress");
    for(let idx = 0; idx < progress_divs.length; idx ++) {
        progress_divs[idx].children[0].classList.add("determinate");
        progress_divs[idx].children[0].classList.remove("indeterminate");
    }
}

function show_no_file_selected_message() {
    var html = [
    '<div class="modal-upload-file">',
        '<div class="file-icon pd-mg">',
            '<svg width="24" height="32" viewBox="0 0 24 32" fill="none" xmlns="http://www.w3.org/2000/svg">',
                '<path fill-rule="evenodd" clip-rule="evenodd" d="M14 0V8.50667C14 9.33333 14.6667 10 15.4933 10H24V30.5067C24 31.3333 23.3333 32 22.5067 32H1.49333C0.666665 32 0 31.3333 0 30.5067V1.49333C0 0.666667 0.666665 0 1.49333 0H14ZM17.4404 0.426667L23.5471 6.56C23.8404 6.85333 24.0004 7.22667 24.0004 7.62667V8H16.0004V0H16.3737C16.7737 0 17.147 0.16 17.4404 0.426667Z" fill="#ef827f"/>',
                '<defs>',
                    '<linearGradient id="paint0_linear" x1="2.39111" y1="3" x2="23.3908" y2="32.0002" gradientUnits="userSpaceOnUse">',
                        '<stop stop-color="#E08F8D"/>',
                        '<stop offset="1" stop-color="#FE736F"/>',
                    '</linearGradient>',
                '</defs>',
            '</svg>',
        '</div>',
        '<div class=" file-name-container">',
            '<div class="file-name-div">',
                'No file Choosen',
            '</div>',
        '</div>',
    '</div>',
    ].join('');
    document.getElementById("easyassist-upload-file-name-container").innerHTML = html;
    document.getElementById("send-document-error").innerHTML = "";
}

function remove_selected_file(element, file_id) {
    element.parentElement.remove();

    var updated_attached_files = [];
    for(let idx = 0; idx < uploaded_attached_files.length; idx ++) {
        if(uploaded_attached_files[idx].file_id != file_id) {
            updated_attached_files.push(uploaded_attached_files[idx]);
        }
    }

    uploaded_attached_files = updated_attached_files;

    var updated_attachment_file_global = [];
    for(let idx = 0; idx < attachment_file_global.length; idx ++) {
        if(attachment_file_global[idx].file_id != file_id) {
            updated_attachment_file_global.push(attachment_file_global[idx]);
        }
    }
    attachment_file_global = updated_attachment_file_global;

    if(attachment_file_global.length == 0) {
        updated_attached_files = [];
        document.getElementById("file-attachment").value = "";
        document.getElementById("send-document-error").innerHTML = "";
        document.getElementById("send-document-button").style.display = "none";
    }
}

function add_file_name_progress_div(file, file_id) {
    var html = [
    '<div class="modal-upload-file">',
        '<div class="file-icon pd-mg">',
            '<svg width="24" height="32" viewBox="0 0 24 32" fill="none" xmlns="http://www.w3.org/2000/svg">',
                '<path fill-rule="evenodd" clip-rule="evenodd" d="M14 0V8.50667C14 9.33333 14.6667 10 15.4933 10H24V30.5067C24 31.3333 23.3333 32 22.5067 32H1.49333C0.666665 32 0 31.3333 0 30.5067V1.49333C0 0.666667 0.666665 0 1.49333 0H14ZM17.4404 0.426667L23.5471 6.56C23.8404 6.85333 24.0004 7.22667 24.0004 7.62667V8H16.0004V0H16.3737C16.7737 0 17.147 0.16 17.4404 0.426667Z" fill="#ef827f"/>',
                '<defs>',
                    '<linearGradient id="paint0_linear" x1="2.39111" y1="3" x2="23.3908" y2="32.0002" gradientUnits="userSpaceOnUse">',
                        '<stop stop-color="#E08F8D"/>',
                        '<stop offset="1" stop-color="#FE736F"/>',
                    '</linearGradient>',
                '</defs>',
            '</svg>',
        '</div>',
        '<div class=" file-name-container">',
            '<div class="file-name-div">',
                file.name,
            '</div>',
            '<div class="progress">',
                '<div class="indeterminate">',
                '</div>',
            '</div>',
        '</div>',
        '<div class="download-icon" style="padding-right: 10px;cursor: pointer; display: none;" onclick="remove_selected_file(this, \'' + file_id + '\')">',
            '<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">',
                '<rect width="28" height="28" rx="14" fill="#F0F1F5"/>',
                '<rect width="28" height="28" rx="14" fill="#F0F1F5"/>',
                '<path d="M15.8891 13.9806L20.1845 9.72491C20.4232 9.48628 20.4232 9.04878 20.1845 8.81014L19.1902 7.81582C18.9516 7.57719 18.5141 7.57719 18.2754 7.81582L14.0198 12.1113L9.7243 7.81582C9.48566 7.57719 9.04816 7.57719 8.80953 7.81582L7.81521 8.81014C7.57657 9.04878 7.57657 9.48628 7.81521 9.72491L12.1107 13.9806L7.81521 18.276C7.57657 18.5147 7.57657 18.9522 7.81521 19.1908L8.80953 20.1851C9.04816 20.4238 9.48566 20.4238 9.7243 20.1851L14.0198 15.8897L18.2754 20.1851C18.5141 20.4238 18.9516 20.4238 19.1902 20.1851L20.1845 19.1908C20.4232 18.9522 20.4232 18.5147 20.1845 18.276L15.8891 13.9806Z" fill="#757575"/>',
            '</svg>',
        '</div>',
    '</div>',
    ].join('');
    document.getElementById("easyassist-upload-file-name-container").innerHTML += html;
}

function get_file_reader_promise(file, file_id) {
    var reader = new FileReader();
    return new Promise((resolve, reject) => {
        reader.onerror = function(error) {
            reader.abort();
            reject(null);
            console.log('Error: ', error);
        };

        reader.onload = function() {
            var data = {
                "data": reader.result,
                "file_id": file_id,
                "file_name": file.name,
            }
            resolve(data);
        };

        reader.readAsDataURL(file);
    });
}

function getBase64() {
    hide_file_name_modal_container();

    var error_element = document.getElementById("send-document-error");
    var file_promises = [];
    for(let idx = 0; idx < attachment_file_global.length; idx ++) {
        var file_id = "file_" + idx;
        add_file_name_progress_div(attachment_file_global[idx], file_id);
        file_promises.push(get_file_reader_promise(attachment_file_global[idx], file_id));
    }

    Promise.all(file_promises).then(function(result) {
        var support_files = [];
        var updated_attached_files = [];
        for(let idx = 0; idx < result.length; idx ++) {
            try {
                var base64_str = result[idx]["data"].split(",")[1];
                support_files.push({
                    "filename": result[idx]["file_name"],
                    "base64_file": base64_str,
                    "file_id": result[idx]["file_id"]
                });

                updated_attached_files.push({
                    "file_id": result[idx]["file_id"],
                });
            } catch(err) {}
        }

        attachment_file_global = updated_attached_files;
        $('.modal-upload-file .download-icon').show();

        json_string = JSON.stringify({
            "session_id" : session_id,
            "files": support_files,
            "base64_file": base64_str
        });

        encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/save-multiple-document/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrf_token());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if(response["status"]==200){
                    uploaded_attached_files = response["uploaded_files"];

                    if(response["file_upload_fail"].length) {
                        var file_upload_fail = response["file_upload_fail"];
                        var error_html = "Not able to upload these files. Please try again. <br />";
                        for(let idx = 0; idx < file_upload_fail.length; idx ++) {
                            error_html += file_upload_fail[idx] + "<br />";
                        }
                        error_element.innerHTML = error_html;
                        error_element.style.color = "red";
                    }

                    if(uploaded_attached_files.length && attachment_file_global.length) {
                        error_element.innerHTML = "Uploaded";
                        error_element.style.color = "green";
                        document.getElementById("send-document-button").style.display = "inline-block";
                    } else {
                        document.getElementById("send-document-button").style.display = "none";
                    }
                } else if(response["status"] == 302) {
                    uploaded_attached_files = [];
                    error_element.innerHTML = "This file format is not allowed";
                    error_element.style.color = "red";
                    document.getElementById("send-document-button").style.display = "none";
                } else if(response["status"] == 301) {
                    uploaded_attached_files = [];
                    error_element.innerHTML = "Please do not use .(dot) except for extension";
                    error_element.style.color = "red";
                    document.getElementById("send-document-button").style.display = "none";
                } else {
                    uploaded_attached_files = [];
                    error_element.innerHTML = "Unable to upload the document";
                    error_element.style.color = "red";
                    document.getElementById("send-document-button").style.display = "none";
                }
                stop_file_upload_progress_bar();
            }
        }
        xhttp.send(params);
    });
}

function check_file_selection(element) {
    var files = element.files;
    var error_element = document.getElementById("send-document-error");

    if(files.length == 0) {
        if(attachment_file_global == undefined){
            show_no_file_selected_message();
            error_element.innerHTML = "";
            document.getElementById("send-document-button").style.display = "none";
            return;
        }
    } else if(files.length > 5) {
        error_element.innerHTML = "Maximum 5 files can be uploaded at a time.";
        error_element.style.color = "red";
        document.getElementById("send-document-button").style.display = "none";
        return;
    }

    error_element.innerHTML = "Validating file...";
    error_element.style.color = "green";

    var all_files_valid = true;
    var files_validation_error = "";
    var uploaded_files_list = [];

    for(let idx = 0; idx < files.length; idx ++) {
        var file = files[idx];
        if(file.size/1000000 > 5){
            all_files_valid = false;
            files_validation_error = "file_size";
        } else if (check_file_extension(file.name) == false) {
            all_files_valid = false;
            files_validation_error = "file_extension";
        } else if(check_malicious_file_chatbot(file.name)) {
            all_files_valid = false;
            files_validation_error = "malicious_file";
        } else if(check_file_name(file.name)) {
            all_files_valid = false;
            files_validation_error = "file_name";
        } else {
            uploaded_files_list.push(file);
        }
    }

    if(all_files_valid) {
        attachment_file_global = uploaded_files_list;
        element.value = "";
        getBase64();
    } else {
        if(files_validation_error == "file_size") {
            error_element.innerHTML = "File size is greater than 5 MB";
        } else if(files_validation_error == "malicious_file") {
            error_element.innerHTML = "Please do not use .(dot) except for extension";
        } else if(files_validation_error == "file_name") {
            error_element.innerHTML = "Please don't use special characters other than hyphen(-) and underscore(_) in the file name";
        } else {
            error_element.innerHTML = 'Invalid file type, only "png", "jpg", "jpeg", "pdf", "doc", "docx" are allowed';
        }
        error_element.style.color = "red";
        error_element.style.display = "";
        document.getElementById("send-document-button").style.display = "none";
        return;
    }
}

function append_agent_attachment_and_message_in_chat(attachement_message, file_src, file_name, time) {
    var extension = file_name.split(".")[1];
    var html = "";
    var attachment_message_html = "";
    var file_name_in_url = file_name.replace(/([\""|\''])/g, '\\$1');

    if(check_image_file_chatbot(extension)) {
        html = [
            '<div class="easychat-user-message-div">',
                '<div class="live-chat-agent-message-bubble-image-attachment" style="border-radius: 16px 16px 0px 16px;">',
                    '<div class="slideshow-container" value="1">',
                        '<div class="mySlides livechat-slider-card">',
                            '<img src="' + file_src + '?session_id=' + session_id + '">',
                            '<div style="text-align: left; position: relative;">',
                                '<h5 style="overflow-wrap: break-word; ">' + file_name + '</h5>',
                                '<a href="' + file_src + '?session_id=' + session_id + '" style="position: absolute; top: 6px; right: 8px; cursor: pointer;" target="_blank">',
                                    '<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                        '<path d="M11.875 11.25H3.125C2.77982 11.25 2.5 11.5298 2.5 11.875C2.5 12.2202 2.77982 12.5 3.125 12.5H11.875C12.2202 12.5 12.5 12.2202 12.5 11.875C12.5 11.5298 12.2202 11.25 11.875 11.25Z" fill="#757575">','</path>',
                                        '<path d="M2.5 10.625V11.875C2.5 12.2202 2.77982 12.5 3.125 12.5C3.47018 12.5 3.75 12.2202 3.75 11.875V10.625C3.75 10.2798 3.47018 10 3.125 10C2.77982 10 2.5 10.2798 2.5 10.625Z" fill="#757575">','</path>',
                                        '<path d="M11.25 10.625V11.875C11.25 12.2202 11.5298 12.5 11.875 12.5C12.2202 12.5 12.5 12.2202 12.5 11.875V10.625C12.5 10.2798 12.2202 10 11.875 10C11.5298 10 11.25 10.2798 11.25 10.625Z" fill="#757575">','</path>',
                                        '<path d="M7.50003 9.375C7.37046 9.37599 7.24378 9.33667 7.13753 9.2625L4.63753 7.5C4.50279 7.40442 4.41137 7.25937 4.38326 7.09658C4.35515 6.93379 4.39264 6.76649 4.48753 6.63125C4.5349 6.56366 4.59518 6.50611 4.66491 6.46194C4.73463 6.41777 4.81242 6.38785 4.89377 6.37391C4.97512 6.35996 5.05843 6.36227 5.13889 6.38069C5.21934 6.39911 5.29535 6.43329 5.36253 6.48125L7.50003 7.975L9.62503 6.375C9.75764 6.27555 9.92432 6.23284 10.0884 6.25628C10.2525 6.27973 10.4006 6.36739 10.5 6.5C10.5995 6.63261 10.6422 6.7993 10.6187 6.96339C10.5953 7.12749 10.5076 7.27555 10.375 7.375L7.87503 9.25C7.76685 9.33114 7.63526 9.375 7.50003 9.375Z" fill="#757575">','</path>',
                                        '<path d="M7.5 8.125C7.33424 8.125 7.17527 8.05915 7.05806 7.94194C6.94085 7.82473 6.875 7.66576 6.875 7.5V2.5C6.875 2.33424 6.94085 2.17527 7.05806 2.05806C7.17527 1.94085 7.33424 1.875 7.5 1.875C7.66576 1.875 7.82473 1.94085 7.94194 2.05806C8.05915 2.17527 8.125 2.33424 8.125 2.5V7.5C8.125 7.66576 8.05915 7.82473 7.94194 7.94194C7.82473 8.05915 7.66576 8.125 7.5 8.125Z" fill="#757575">','</path>',
                                    '</svg>',
                                '</a>',
                                '<p style="overflow-wrap: break-word;">' + attachement_message + '</p>',
                            '</div>',
                        '</div>',
                    '</div>',
                '</div>',
                '<span class="message-time-user">' + time + '</span>',
            '</div>',
        ].join('');
    } else {
        var document_file_svg = "";
        if(extension == "pdf") {
            document_file_svg = `
            <svg width="24" height="24" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M7.3567 0H18.9983L26.3249 7.30121V25.9001C26.3249 27.6016 24.9407 28.985 23.241 28.985H7.35665C5.65592 28.985 4.27171 27.6016 4.27171 25.9001V24.5176H3.97034C3.28392 24.5176 2.72729 23.9615 2.72729 23.2747V15.7357C2.72729 15.0487 3.28392 14.4925 3.97034 14.4925H4.27171V3.08493C4.27171 1.38517 5.65592 0 7.3567 0ZM7.3567 27.0957H23.241C23.8995 27.0957 24.4349 26.5595 24.4349 25.9L24.3903 8.04961L20.4307 8.06099C19.2494 8.06099 18.2914 7.10216 18.2914 5.92158V1.87969L7.3567 1.89112C6.69812 1.89112 6.16187 2.42737 6.16187 3.08493V14.4925H20.9695C21.6559 14.4925 22.2126 15.0487 22.2126 15.7357V23.2747C22.2126 23.9615 21.6558 24.5176 20.9695 24.5176H6.16187V25.9001C6.16187 26.5595 6.69812 27.0957 7.3567 27.0957ZM5.55078 16.8984V22.5H6.81641V20.6602H7.71875C8.07552 20.6602 8.40234 20.5807 8.69922 20.4219C8.99609 20.2604 9.23177 20.0352 9.40625 19.7461C9.58333 19.457 9.67188 19.1328 9.67188 18.7734C9.67188 18.224 9.48568 17.7747 9.11328 17.4258C8.74349 17.0742 8.27865 16.8984 7.71875 16.8984H5.55078ZM7.59375 19.5898H6.81641V17.9805H7.59375C7.82552 17.9805 8.01432 18.0534 8.16016 18.1992C8.30859 18.3424 8.38281 18.5339 8.38281 18.7734C8.38281 19.0156 8.30859 19.2122 8.16016 19.3633C8.01172 19.5143 7.82292 19.5898 7.59375 19.5898ZM10.4336 16.8984V22.5H12.4258C13.319 22.5 14.0221 22.2474 14.5352 21.7422C15.0508 21.2344 15.3086 20.5456 15.3086 19.6758C15.3086 19.2695 15.2422 18.8958 15.1094 18.5547C14.9766 18.2109 14.7878 17.918 14.543 17.6758C14.2982 17.431 13.9935 17.2409 13.6289 17.1055C13.2669 16.9674 12.8659 16.8984 12.4258 16.8984H10.4336ZM12.3711 21.4023H11.6992V17.9961H12.3711C12.5846 17.9961 12.7852 18.0286 12.9727 18.0938C13.1602 18.1562 13.3307 18.2526 13.4844 18.3828C13.6406 18.5104 13.763 18.6849 13.8516 18.9062C13.9427 19.1276 13.9883 19.3841 13.9883 19.6758C13.9883 19.9232 13.9583 20.1458 13.8984 20.3438C13.8385 20.5417 13.7578 20.7057 13.6562 20.8359C13.5547 20.9661 13.4336 21.0742 13.293 21.1602C13.1523 21.2461 13.0052 21.3086 12.8516 21.3477C12.7005 21.3841 12.5404 21.4023 12.3711 21.4023ZM16.168 16.8984V22.5H17.4336V20.3477H19.4883V19.2695H17.4336V17.9805H19.7148V16.8984H16.168Z" fill="#D32F2F"/>
            </svg>`
        } else {
            document_file_svg = [
                '<svg width="24" height="24" viewBox="0 0 18 22" fill="none" xmlns="http://www.w3.org/2000/svg">',
                    '<path d="M11.9321 0H3.3949C2.14766 0 1.13257 1.01579 1.13257 2.26228V10.6278H0.91157C0.408194 10.6278 0 11.0357 0 11.5395V17.0681C0 17.5718 0.408194 17.9796 0.91157 17.9796H1.13257V18.9934C1.13257 20.2412 2.14766 21.2557 3.39486 21.2557H15.0434C16.2898 21.2557 17.3049 20.2412 17.3049 18.9934V5.35422L11.9321 0ZM1.5081 12.2989C1.82671 12.2482 2.24178 12.2196 2.67996 12.2196C3.40808 12.2196 3.88025 12.3503 4.25022 12.6289C4.64836 12.9249 4.89846 13.3974 4.89846 14.0742C4.89846 14.8078 4.6313 15.3144 4.26133 15.6271C3.85763 15.9626 3.24311 16.1217 2.49237 16.1217C2.04287 16.1217 1.72426 16.0933 1.50814 16.0648V12.2989H1.5081ZM15.0434 19.8702H3.3949C2.91194 19.8702 2.51869 19.477 2.51869 18.9934V17.9796H13.3776C13.8809 17.9796 14.2892 17.5718 14.2892 17.0681V11.5395C14.2892 11.0357 13.881 10.6278 13.3776 10.6278H2.51869V2.26228C2.51869 1.78007 2.91194 1.38682 3.3949 1.38682L11.4137 1.37844V4.34249C11.4137 5.20825 12.1162 5.91139 12.9825 5.91139L15.8862 5.90305L15.9189 18.9933C15.9189 19.477 15.5263 19.8702 15.0434 19.8702ZM5.29308 14.1936C5.29308 13.0444 6.02685 12.1856 7.15902 12.1856C8.33674 12.1856 8.97943 13.0673 8.97943 14.1255C8.97943 15.3824 8.21723 16.1446 7.09647 16.1446C5.95878 16.1446 5.29308 15.2859 5.29308 14.1936ZM11.5131 15.4221C11.7747 15.4221 12.0647 15.3651 12.2356 15.2969L12.3663 15.9737C12.2072 16.0537 11.8486 16.1391 11.3824 16.1391C10.0567 16.1391 9.37409 15.3144 9.37409 14.2222C9.37409 12.9138 10.3072 12.1856 11.4675 12.1856C11.9171 12.1856 12.2582 12.2766 12.4118 12.3559L12.2356 13.0444C12.0591 12.97 11.8145 12.902 11.5075 12.902C10.8189 12.902 10.2843 13.3175 10.2843 14.1707C10.2843 14.9385 10.7394 15.4221 11.5131 15.4221Z" fill="#0254D7"/>',
                    '<path d="M3.97708 14.1026C3.98264 13.3057 3.51612 12.8854 2.77088 12.8854C2.57734 12.8854 2.45227 12.902 2.3783 12.9194V15.4276C2.45227 15.4451 2.57183 15.4451 2.67989 15.4451C3.46502 15.4506 3.97708 15.0184 3.97708 14.1026Z" fill="#0254D7"/>',
                    '<path d="M8.0637 14.1534C8.0637 13.4655 7.73367 12.8735 7.13644 12.8735C6.5504 12.8735 6.20886 13.4314 6.20886 14.1763C6.20886 14.9274 6.56182 15.4561 7.14204 15.4561C7.72812 15.4561 8.0637 14.8988 8.0637 14.1534Z" fill="#0254D7"/>',
                '</svg>',
            ].join('');
        }
        if(attachement_message) {
            attachment_message_html = '<div class="upload-file-text-area" style="margin-bottom:10px">' + attachement_message + '</div>';
        }
        html = `
                <div class="easychat-user-message-div">
                    <div class="message-outer-container">
                        <div class="message-inner-container">
                            <div class="pdf-container">
                                <div class="pdf-description">
                                    <div class="pdf-logo">
                                    ${document_file_svg}                   
                                    </div>
                                    <div class="pdf-name" style="margin-left: 11px;">
                                        <p class="document-name-p-tag">${file_name}</p>
                                    </div>
                                </div>
                                <div class="pdf-download-logo tooltip" style="cursor: pointer;">
                                <a href="${file_src}?session_id=${session_id}" style="cursor: pointer;" target="_blank">
                                        <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path fill-rule="evenodd" clip-rule="evenodd" d="M9.65213 4.08279C9.65213 3.34671 10.2549 2.75 10.9985 2.75C11.7421 2.75 12.3448 3.34671 12.3448 4.08279V10.3144C12.3448 10.4093 12.4226 10.4862 12.5184 10.4862H14.3647C14.6285 10.4863 14.8679 10.6388 14.9773 10.8764C15.0867 11.114 15.0459 11.393 14.873 11.5901L11.5068 15.4228C11.379 15.5687 11.1935 15.6525 10.9985 15.6525C10.8035 15.6525 10.618 15.5687 10.4902 15.4228L7.12398 11.5901C6.95103 11.393 6.91026 11.114 7.01965 10.8764C7.12905 10.6388 7.36848 10.4863 7.63225 10.4862H9.47854C9.57441 10.4862 9.65213 10.4093 9.65213 10.3144V4.08279ZM17.5634 15.2255C17.5634 14.7654 17.9402 14.3924 18.405 14.3924C18.6288 14.3915 18.8438 14.4789 19.0023 14.6352C19.1609 14.7915 19.25 15.004 19.25 15.2255V16.5006C19.25 18.019 18.0065 19.25 16.4726 19.25H5.524C3.99142 19.2481 2.75004 18.0177 2.75004 16.5006V15.2255C2.75004 14.7654 3.12682 14.3924 3.5916 14.3924C4.05638 14.3924 4.43316 14.7654 4.43316 15.2255V16.5006C4.43393 17.0965 4.92197 17.5793 5.524 17.5797H16.4726C17.0746 17.5793 17.5627 17.0965 17.5634 16.5006V15.2255Z" fill="${BOT_THEME_COLOR}"/>
                                        </svg>
                                
                                        </a>        
                                        <span class="download-tooltip">Download</span>            
                                </div>
                            </div>
                            ${attachment_message_html}
                `
        if(extension == "pdf") {
            
            if(window.enable_preview_functionality == "True") {
                html += `<button onclick="open_pdf('${file_name_in_url}','${file_src}','${session_id}')" class="coview-btn" id="coview" style="background: ${BOT_THEME_COLOR};">Preview</button>`
            }
            html += `</div>
                    </div>
                <span class="message-time-user">${time}</span>
            </div>`      
        }else{
            html += `</div>
                </div>
                <span class="message-time-user">${time}</span>
            </div>`
        }
    }

    document.getElementById("easychat-chat-container").innerHTML += html;

    scroll_to_bottom();
}

function append_client_attachment_and_message_in_chat(attachement_message, file_src, file_name, time, name, agent_profile_pic_source) { 
    var extension = file_name.split(".")[1];
    var html = "";
    var attachment_message_html = "";
    var file_name_in_url = file_name.replace(/([\""|\''])/g, '\\$1');

    let profile = "";
    let msg_sender_icon = "";
    if (window.DISPLAY_AGENT_PROFILE == "True" && agent_profile_pic_source != undefined && agent_profile_pic_source != "") {
        let src = "/" + agent_profile_pic_source;
        profile = '<img src = "' + src + '"/>';
    }

    if (agent_to_customer_cobrowsing == "True") {
        if (profile != "") {
            msg_sender_icon = profile;
            try {
                document.querySelector(".easychat-bot-msg-sender-profile").style.backgroundColor = "none";
            }
            catch(err) {
                console.log(err)
            }
        } else {
            msg_sender_icon = ['<svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">',
                '<path d="M20 6.99892C20.5304 6.99892 21.0391 7.20964 21.4142 7.58471C21.7893 7.95978 22 8.46849 22 8.99892V12.9989C22 13.5294 21.7893 14.0381 21.4142 14.4131C21.0391 14.7882 20.5304 14.9989 20 14.9989H18.938C18.6942 16.9322 17.7533 18.7101 16.2917 19.9989C14.8302 21.2877 12.9486 21.9989 11 21.9989V19.9989C12.5913 19.9989 14.1174 19.3668 15.2426 18.2416C16.3679 17.1163 17 15.5902 17 13.9989V7.99892C17 6.40762 16.3679 4.8815 15.2426 3.75628C14.1174 2.63106 12.5913 1.99892 11 1.99892C9.4087 1.99892 7.88258 2.63106 6.75736 3.75628C5.63214 4.8815 5 6.40762 5 7.99892V14.9989H2C1.46957 14.9989 0.960859 14.7882 0.585786 14.4131C0.210714 14.0381 0 13.5294 0 12.9989V8.99892C0 8.46849 0.210714 7.95978 0.585786 7.58471C0.960859 7.20964 1.46957 6.99892 2 6.99892H3.062C3.30603 5.06582 4.24708 3.2882 5.70857 1.9996C7.17007 0.711003 9.05155 0 11 0C12.9484 0 14.8299 0.711003 16.2914 1.9996C17.7529 3.2882 18.694 5.06582 18.938 6.99892H20ZM6.76 14.7839L7.82 13.0879C8.77308 13.685 9.87537 14.0007 11 13.9989C12.1246 14.0007 13.2269 13.685 14.18 13.0879L15.24 14.7839C13.9693 15.5801 12.4995 16.0012 11 15.9989C9.50046 16.0012 8.03074 15.5801 6.76 14.7839Z" fill="white"/>',
                '</svg>',
            ].join('');
        }
    } else {
        if (profile != "") {
            msg_sender_icon = profile;
            try {
                document.querySelector(".easychat-bot-msg-sender-profile").style.backgroundColor = "none";
            }
            catch(err) {
                console.log(err)
            }
        } else {
            msg_sender_icon = [
                '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">',
                '<path d="M4.5 4.26316C4.5 6.61358 6.519 8.52632 9 8.52632C11.481 8.52632 13.5 6.61358 13.5 4.26316C13.5 1.91274 11.481 0 9 0C6.519 0 4.5 1.91274 4.5 4.26316ZM17 18H18V17.0526C18 13.3967 14.859 10.4211 11 10.4211H7C3.14 10.4211 0 13.3967 0 17.0526V18H17Z" fill="white"></path>',
                '</svg>',
            ].join('');
        }
    }

    if (check_image_file_chatbot(extension)) {
        html = [
            '<div class="easychat-bot-message-div">',
                '<div style="display: flex; flex-direction: row;">',
                    '<div class="easychat-bot-msg-sender-profile" style="background-color: ' + BOT_THEME_COLOR + '">',
                      msg_sender_icon,
                   '</div>',
                    '<div class="live-chat-agent-message-bubble-image-attachment" style="border-radius: 16px 16px 16px 0px;">',
                        '<div class="easychat-bot-message-name" style="color: ' + BOT_THEME_COLOR + ';text-align: left;">' + name + '</div>',
                        '<div class="slideshow-container" value="1" style="padding-top: 0.5em;">',
                            '<div class="mySlides livechat-slider-card">',
                                '<img src="' + file_src + '?session_id=' + session_id + '" style="border-radius: 0px;">',
                                '<div style="text-align: left; position: relative;">',
                                    '<h5 style="overflow-wrap: break-word; ">' + file_name + '</h5>',
                                    '<a href="' + file_src + '?session_id=' + session_id + '" style="position: absolute; top: 6px; right: 8px; cursor: pointer;" target="_blank">',
                                        '<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                            '<path d="M11.875 11.25H3.125C2.77982 11.25 2.5 11.5298 2.5 11.875C2.5 12.2202 2.77982 12.5 3.125 12.5H11.875C12.2202 12.5 12.5 12.2202 12.5 11.875C12.5 11.5298 12.2202 11.25 11.875 11.25Z" fill="#757575">','</path>',
                                            '<path d="M2.5 10.625V11.875C2.5 12.2202 2.77982 12.5 3.125 12.5C3.47018 12.5 3.75 12.2202 3.75 11.875V10.625C3.75 10.2798 3.47018 10 3.125 10C2.77982 10 2.5 10.2798 2.5 10.625Z" fill="#757575">','</path>',
                                            '<path d="M11.25 10.625V11.875C11.25 12.2202 11.5298 12.5 11.875 12.5C12.2202 12.5 12.5 12.2202 12.5 11.875V10.625C12.5 10.2798 12.2202 10 11.875 10C11.5298 10 11.25 10.2798 11.25 10.625Z" fill="#757575">','</path>',
                                            '<path d="M7.50003 9.375C7.37046 9.37599 7.24378 9.33667 7.13753 9.2625L4.63753 7.5C4.50279 7.40442 4.41137 7.25937 4.38326 7.09658C4.35515 6.93379 4.39264 6.76649 4.48753 6.63125C4.5349 6.56366 4.59518 6.50611 4.66491 6.46194C4.73463 6.41777 4.81242 6.38785 4.89377 6.37391C4.97512 6.35996 5.05843 6.36227 5.13889 6.38069C5.21934 6.39911 5.29535 6.43329 5.36253 6.48125L7.50003 7.975L9.62503 6.375C9.75764 6.27555 9.92432 6.23284 10.0884 6.25628C10.2525 6.27973 10.4006 6.36739 10.5 6.5C10.5995 6.63261 10.6422 6.7993 10.6187 6.96339C10.5953 7.12749 10.5076 7.27555 10.375 7.375L7.87503 9.25C7.76685 9.33114 7.63526 9.375 7.50003 9.375Z" fill="#757575">','</path>',
                                            '<path d="M7.5 8.125C7.33424 8.125 7.17527 8.05915 7.05806 7.94194C6.94085 7.82473 6.875 7.66576 6.875 7.5V2.5C6.875 2.33424 6.94085 2.17527 7.05806 2.05806C7.17527 1.94085 7.33424 1.875 7.5 1.875C7.66576 1.875 7.82473 1.94085 7.94194 2.05806C8.05915 2.17527 8.125 2.33424 8.125 2.5V7.5C8.125 7.66576 8.05915 7.82473 7.94194 7.94194C7.82473 8.05915 7.66576 8.125 7.5 8.125Z" fill="#757575">','</path>',
                                        '</svg>',
                                    '</a>',
                                    '<p style="overflow-wrap: break-word;">' + attachement_message + '</p>',
                                '</div>',
                            '</div>',
                        '</div>',
                    '</div>',
                '</div>',
                '<span class="message-time-bot">' + time + '</span>',
            '</div>',
        ].join('');
    } else {
        var document_file_svg = "";
        if(extension == "pdf") {
            document_file_svg = `
            <svg width="24" height="24" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M7.3567 0H18.9983L26.3249 7.30121V25.9001C26.3249 27.6016 24.9407 28.985 23.241 28.985H7.35665C5.65592 28.985 4.27171 27.6016 4.27171 25.9001V24.5176H3.97034C3.28392 24.5176 2.72729 23.9615 2.72729 23.2747V15.7357C2.72729 15.0487 3.28392 14.4925 3.97034 14.4925H4.27171V3.08493C4.27171 1.38517 5.65592 0 7.3567 0ZM7.3567 27.0957H23.241C23.8995 27.0957 24.4349 26.5595 24.4349 25.9L24.3903 8.04961L20.4307 8.06099C19.2494 8.06099 18.2914 7.10216 18.2914 5.92158V1.87969L7.3567 1.89112C6.69812 1.89112 6.16187 2.42737 6.16187 3.08493V14.4925H20.9695C21.6559 14.4925 22.2126 15.0487 22.2126 15.7357V23.2747C22.2126 23.9615 21.6558 24.5176 20.9695 24.5176H6.16187V25.9001C6.16187 26.5595 6.69812 27.0957 7.3567 27.0957ZM5.55078 16.8984V22.5H6.81641V20.6602H7.71875C8.07552 20.6602 8.40234 20.5807 8.69922 20.4219C8.99609 20.2604 9.23177 20.0352 9.40625 19.7461C9.58333 19.457 9.67188 19.1328 9.67188 18.7734C9.67188 18.224 9.48568 17.7747 9.11328 17.4258C8.74349 17.0742 8.27865 16.8984 7.71875 16.8984H5.55078ZM7.59375 19.5898H6.81641V17.9805H7.59375C7.82552 17.9805 8.01432 18.0534 8.16016 18.1992C8.30859 18.3424 8.38281 18.5339 8.38281 18.7734C8.38281 19.0156 8.30859 19.2122 8.16016 19.3633C8.01172 19.5143 7.82292 19.5898 7.59375 19.5898ZM10.4336 16.8984V22.5H12.4258C13.319 22.5 14.0221 22.2474 14.5352 21.7422C15.0508 21.2344 15.3086 20.5456 15.3086 19.6758C15.3086 19.2695 15.2422 18.8958 15.1094 18.5547C14.9766 18.2109 14.7878 17.918 14.543 17.6758C14.2982 17.431 13.9935 17.2409 13.6289 17.1055C13.2669 16.9674 12.8659 16.8984 12.4258 16.8984H10.4336ZM12.3711 21.4023H11.6992V17.9961H12.3711C12.5846 17.9961 12.7852 18.0286 12.9727 18.0938C13.1602 18.1562 13.3307 18.2526 13.4844 18.3828C13.6406 18.5104 13.763 18.6849 13.8516 18.9062C13.9427 19.1276 13.9883 19.3841 13.9883 19.6758C13.9883 19.9232 13.9583 20.1458 13.8984 20.3438C13.8385 20.5417 13.7578 20.7057 13.6562 20.8359C13.5547 20.9661 13.4336 21.0742 13.293 21.1602C13.1523 21.2461 13.0052 21.3086 12.8516 21.3477C12.7005 21.3841 12.5404 21.4023 12.3711 21.4023ZM16.168 16.8984V22.5H17.4336V20.3477H19.4883V19.2695H17.4336V17.9805H19.7148V16.8984H16.168Z" fill="#D32F2F"/>
            </svg>`
        } else {
            document_file_svg = [
                '<svg width="24" height="24" viewBox="0 0 18 22" fill="none" xmlns="http://www.w3.org/2000/svg">',
                    '<path d="M11.9321 0H3.3949C2.14766 0 1.13257 1.01579 1.13257 2.26228V10.6278H0.91157C0.408194 10.6278 0 11.0357 0 11.5395V17.0681C0 17.5718 0.408194 17.9796 0.91157 17.9796H1.13257V18.9934C1.13257 20.2412 2.14766 21.2557 3.39486 21.2557H15.0434C16.2898 21.2557 17.3049 20.2412 17.3049 18.9934V5.35422L11.9321 0ZM1.5081 12.2989C1.82671 12.2482 2.24178 12.2196 2.67996 12.2196C3.40808 12.2196 3.88025 12.3503 4.25022 12.6289C4.64836 12.9249 4.89846 13.3974 4.89846 14.0742C4.89846 14.8078 4.6313 15.3144 4.26133 15.6271C3.85763 15.9626 3.24311 16.1217 2.49237 16.1217C2.04287 16.1217 1.72426 16.0933 1.50814 16.0648V12.2989H1.5081ZM15.0434 19.8702H3.3949C2.91194 19.8702 2.51869 19.477 2.51869 18.9934V17.9796H13.3776C13.8809 17.9796 14.2892 17.5718 14.2892 17.0681V11.5395C14.2892 11.0357 13.881 10.6278 13.3776 10.6278H2.51869V2.26228C2.51869 1.78007 2.91194 1.38682 3.3949 1.38682L11.4137 1.37844V4.34249C11.4137 5.20825 12.1162 5.91139 12.9825 5.91139L15.8862 5.90305L15.9189 18.9933C15.9189 19.477 15.5263 19.8702 15.0434 19.8702ZM5.29308 14.1936C5.29308 13.0444 6.02685 12.1856 7.15902 12.1856C8.33674 12.1856 8.97943 13.0673 8.97943 14.1255C8.97943 15.3824 8.21723 16.1446 7.09647 16.1446C5.95878 16.1446 5.29308 15.2859 5.29308 14.1936ZM11.5131 15.4221C11.7747 15.4221 12.0647 15.3651 12.2356 15.2969L12.3663 15.9737C12.2072 16.0537 11.8486 16.1391 11.3824 16.1391C10.0567 16.1391 9.37409 15.3144 9.37409 14.2222C9.37409 12.9138 10.3072 12.1856 11.4675 12.1856C11.9171 12.1856 12.2582 12.2766 12.4118 12.3559L12.2356 13.0444C12.0591 12.97 11.8145 12.902 11.5075 12.902C10.8189 12.902 10.2843 13.3175 10.2843 14.1707C10.2843 14.9385 10.7394 15.4221 11.5131 15.4221Z" fill="#0254D7"/>',
                    '<path d="M3.97708 14.1026C3.98264 13.3057 3.51612 12.8854 2.77088 12.8854C2.57734 12.8854 2.45227 12.902 2.3783 12.9194V15.4276C2.45227 15.4451 2.57183 15.4451 2.67989 15.4451C3.46502 15.4506 3.97708 15.0184 3.97708 14.1026Z" fill="#0254D7"/>',
                    '<path d="M8.0637 14.1534C8.0637 13.4655 7.73367 12.8735 7.13644 12.8735C6.5504 12.8735 6.20886 13.4314 6.20886 14.1763C6.20886 14.9274 6.56182 15.4561 7.14204 15.4561C7.72812 15.4561 8.0637 14.8988 8.0637 14.1534Z" fill="#0254D7"/>',
                '</svg>',
            ].join('');
        }
        if(attachement_message) {
            attachment_message_html = '<div class="upload-file-text-area" style="margin-bottom:10px">' + attachement_message + '</div>';
        }
        html = `
            <div class="easychat-bot-message-div">
            <div style="display: flex; flex-direction: row;">
                <div class="easychat-bot-msg-sender-profile" style="background-color: ${BOT_THEME_COLOR}"> 
                    ${msg_sender_icon}
                </div>
            <div class="message-outer-container">
                    <div class="message-inner-container">
                    <div class="easychat-agent-message-name" style="color: ${BOT_THEME_COLOR};text-align: left;"> ${name} </div>
                    <div class="pdf-container">
                        <div class="pdf-description">
                            <div class="pdf-logo">
                            ${document_file_svg}                   
                            </div>
                            <div class="pdf-name" style="margin-left: 11px;">
                                <p class="document-name-p-tag">${file_name}</p>
                            </div>
                    </div>
                    <div class="pdf-download-logo tooltip" style="cursor: pointer;">
                        <a href="${file_src}?session_id=${session_id}" style="cursor: pointer;" target="_blank">
                        <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path fill-rule="evenodd" clip-rule="evenodd" d="M9.65213 4.08279C9.65213 3.34671 10.2549 2.75 10.9985 2.75C11.7421 2.75 12.3448 3.34671 12.3448 4.08279V10.3144C12.3448 10.4093 12.4226 10.4862 12.5184 10.4862H14.3647C14.6285 10.4863 14.8679 10.6388 14.9773 10.8764C15.0867 11.114 15.0459 11.393 14.873 11.5901L11.5068 15.4228C11.379 15.5687 11.1935 15.6525 10.9985 15.6525C10.8035 15.6525 10.618 15.5687 10.4902 15.4228L7.12398 11.5901C6.95103 11.393 6.91026 11.114 7.01965 10.8764C7.12905 10.6388 7.36848 10.4863 7.63225 10.4862H9.47854C9.57441 10.4862 9.65213 10.4093 9.65213 10.3144V4.08279ZM17.5634 15.2255C17.5634 14.7654 17.9402 14.3924 18.405 14.3924C18.6288 14.3915 18.8438 14.4789 19.0023 14.6352C19.1609 14.7915 19.25 15.004 19.25 15.2255V16.5006C19.25 18.019 18.0065 19.25 16.4726 19.25H5.524C3.99142 19.2481 2.75004 18.0177 2.75004 16.5006V15.2255C2.75004 14.7654 3.12682 14.3924 3.5916 14.3924C4.05638 14.3924 4.43316 14.7654 4.43316 15.2255V16.5006C4.43393 17.0965 4.92197 17.5793 5.524 17.5797H16.4726C17.0746 17.5793 17.5627 17.0965 17.5634 16.5006V15.2255Z" fill="${BOT_THEME_COLOR}"/>
                                        </svg>
                            </a>        
                            <span class="download-tooltip">Download</span>            
                    </div>
                </div>
                ${attachment_message_html}
                    `
        if(extension == "pdf") {
            
            if(window.enable_preview_functionality == "True") {
                html += `<button onclick="open_pdf('${file_name_in_url}','${file_src}','${session_id}')" class="coview-btn" id="coview" style="background: ${BOT_THEME_COLOR};">Preview</button>`
            }
            html += `</div>
                    </div>
                </div>
                <span class="message-time-bot">${time}</span>
            </div>` 
        }else{
            html += `</div>
                </div>
                </div>
                <span class="message-time-bot">${time}</span>
            </div>`
        }
    }

    document.getElementById("easychat-chat-container").innerHTML += html;

    scroll_to_bottom();
}

function append_invited_agent_attachment_and_message_in_chat(attachement_message, file_src, file_name, time, name, agent_profile_pic_source) {
    var extension = file_name.split(".")[1];
    var attachment_message_html = "";
    var html = "";
    var file_name_in_url = file_name.replace(/([\""|\''])/g, '\\$1');

    let profile = "";
    let msg_sender_icon = "";
    if (window.DISPLAY_AGENT_PROFILE == "True" && agent_profile_pic_source != "" && agent_profile_pic_source != undefined) {
        let src = "/" + agent_profile_pic_source;
        profile = '<img src = "' + src + '"/>';
    }

    if (agent_to_customer_cobrowsing == "True") {
        if (profile != "") {
            msg_sender_icon = profile;
            try {
                document.querySelector(".easychat-bot-msg-sender-profile").style.backgroundColor = "none";
            }
            catch(err) {
                console.log(err)
            }
        } else {
            msg_sender_icon = ['<svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">',
                '<path d="M20 6.99892C20.5304 6.99892 21.0391 7.20964 21.4142 7.58471C21.7893 7.95978 22 8.46849 22 8.99892V12.9989C22 13.5294 21.7893 14.0381 21.4142 14.4131C21.0391 14.7882 20.5304 14.9989 20 14.9989H18.938C18.6942 16.9322 17.7533 18.7101 16.2917 19.9989C14.8302 21.2877 12.9486 21.9989 11 21.9989V19.9989C12.5913 19.9989 14.1174 19.3668 15.2426 18.2416C16.3679 17.1163 17 15.5902 17 13.9989V7.99892C17 6.40762 16.3679 4.8815 15.2426 3.75628C14.1174 2.63106 12.5913 1.99892 11 1.99892C9.4087 1.99892 7.88258 2.63106 6.75736 3.75628C5.63214 4.8815 5 6.40762 5 7.99892V14.9989H2C1.46957 14.9989 0.960859 14.7882 0.585786 14.4131C0.210714 14.0381 0 13.5294 0 12.9989V8.99892C0 8.46849 0.210714 7.95978 0.585786 7.58471C0.960859 7.20964 1.46957 6.99892 2 6.99892H3.062C3.30603 5.06582 4.24708 3.2882 5.70857 1.9996C7.17007 0.711003 9.05155 0 11 0C12.9484 0 14.8299 0.711003 16.2914 1.9996C17.7529 3.2882 18.694 5.06582 18.938 6.99892H20ZM6.76 14.7839L7.82 13.0879C8.77308 13.685 9.87537 14.0007 11 13.9989C12.1246 14.0007 13.2269 13.685 14.18 13.0879L15.24 14.7839C13.9693 15.5801 12.4995 16.0012 11 15.9989C9.50046 16.0012 8.03074 15.5801 6.76 14.7839Z" fill="white"/>',
                '</svg>',
            ].join('');
        }
    } else {
        if (profile != "") {
            msg_sender_icon = profile;
            try {
                document.querySelector(".easychat-bot-msg-sender-profile").style.backgroundColor = "none";
            }
            catch(err) {
                console.log(err)
            }
        } else {
            msg_sender_icon = ['<svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">',
            '<path d="M20 6.99892C20.5304 6.99892 21.0391 7.20964 21.4142 7.58471C21.7893 7.95978 22 8.46849 22 8.99892V12.9989C22 13.5294 21.7893 14.0381 21.4142 14.4131C21.0391 14.7882 20.5304 14.9989 20 14.9989H18.938C18.6942 16.9322 17.7533 18.7101 16.2917 19.9989C14.8302 21.2877 12.9486 21.9989 11 21.9989V19.9989C12.5913 19.9989 14.1174 19.3668 15.2426 18.2416C16.3679 17.1163 17 15.5902 17 13.9989V7.99892C17 6.40762 16.3679 4.8815 15.2426 3.75628C14.1174 2.63106 12.5913 1.99892 11 1.99892C9.4087 1.99892 7.88258 2.63106 6.75736 3.75628C5.63214 4.8815 5 6.40762 5 7.99892V14.9989H2C1.46957 14.9989 0.960859 14.7882 0.585786 14.4131C0.210714 14.0381 0 13.5294 0 12.9989V8.99892C0 8.46849 0.210714 7.95978 0.585786 7.58471C0.960859 7.20964 1.46957 6.99892 2 6.99892H3.062C3.30603 5.06582 4.24708 3.2882 5.70857 1.9996C7.17007 0.711003 9.05155 0 11 0C12.9484 0 14.8299 0.711003 16.2914 1.9996C17.7529 3.2882 18.694 5.06582 18.938 6.99892H20ZM6.76 14.7839L7.82 13.0879C8.77308 13.685 9.87537 14.0007 11 13.9989C12.1246 14.0007 13.2269 13.685 14.18 13.0879L15.24 14.7839C13.9693 15.5801 12.4995 16.0012 11 15.9989C9.50046 16.0012 8.03074 15.5801 6.76 14.7839Z" fill="white"/>',
            '</svg>',
        ].join('');
        }
    }


    if (check_image_file_chatbot(extension)) {
        html = [
            '<div class="easychat-bot-message-div">',
                '<div style="display: flex; flex-direction: row;">',
                    '<div class="easychat-bot-msg-sender-profile" style="background-color: ' + BOT_THEME_COLOR + '">',
                    msg_sender_icon,
                    '</div>',
                    '<div class="live-chat-agent-message-bubble-image-attachment" style="border-radius: 16px 16px 16px 0px;">',
                        '<div class="easychat-bot-message-name" style="color: ' + BOT_THEME_COLOR + ';text-align: left;">' + name + '</div>',
                        '<div class="slideshow-container" value="1" style="padding-top: 0.5em;">',
                            '<div class="mySlides livechat-slider-card">',
                                '<img src="' + file_src + '?session_id=' + session_id + '" style="border-radius: 0px;">',
                                '<div style="text-align: left; position: relative;">',
                                    '<h5 style="overflow-wrap: break-word; ">' + file_name + '</h5>',
                                    '<a href="' + file_src + '?session_id=' + session_id + '" style="position: absolute; top: 6px; right: 8px; cursor: pointer;" target="_blank">',
                                        '<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                            '<path d="M11.875 11.25H3.125C2.77982 11.25 2.5 11.5298 2.5 11.875C2.5 12.2202 2.77982 12.5 3.125 12.5H11.875C12.2202 12.5 12.5 12.2202 12.5 11.875C12.5 11.5298 12.2202 11.25 11.875 11.25Z" fill="#757575">','</path>',
                                            '<path d="M2.5 10.625V11.875C2.5 12.2202 2.77982 12.5 3.125 12.5C3.47018 12.5 3.75 12.2202 3.75 11.875V10.625C3.75 10.2798 3.47018 10 3.125 10C2.77982 10 2.5 10.2798 2.5 10.625Z" fill="#757575">','</path>',
                                            '<path d="M11.25 10.625V11.875C11.25 12.2202 11.5298 12.5 11.875 12.5C12.2202 12.5 12.5 12.2202 12.5 11.875V10.625C12.5 10.2798 12.2202 10 11.875 10C11.5298 10 11.25 10.2798 11.25 10.625Z" fill="#757575">','</path>',
                                            '<path d="M7.50003 9.375C7.37046 9.37599 7.24378 9.33667 7.13753 9.2625L4.63753 7.5C4.50279 7.40442 4.41137 7.25937 4.38326 7.09658C4.35515 6.93379 4.39264 6.76649 4.48753 6.63125C4.5349 6.56366 4.59518 6.50611 4.66491 6.46194C4.73463 6.41777 4.81242 6.38785 4.89377 6.37391C4.97512 6.35996 5.05843 6.36227 5.13889 6.38069C5.21934 6.39911 5.29535 6.43329 5.36253 6.48125L7.50003 7.975L9.62503 6.375C9.75764 6.27555 9.92432 6.23284 10.0884 6.25628C10.2525 6.27973 10.4006 6.36739 10.5 6.5C10.5995 6.63261 10.6422 6.7993 10.6187 6.96339C10.5953 7.12749 10.5076 7.27555 10.375 7.375L7.87503 9.25C7.76685 9.33114 7.63526 9.375 7.50003 9.375Z" fill="#757575">','</path>',
                                            '<path d="M7.5 8.125C7.33424 8.125 7.17527 8.05915 7.05806 7.94194C6.94085 7.82473 6.875 7.66576 6.875 7.5V2.5C6.875 2.33424 6.94085 2.17527 7.05806 2.05806C7.17527 1.94085 7.33424 1.875 7.5 1.875C7.66576 1.875 7.82473 1.94085 7.94194 2.05806C8.05915 2.17527 8.125 2.33424 8.125 2.5V7.5C8.125 7.66576 8.05915 7.82473 7.94194 7.94194C7.82473 8.05915 7.66576 8.125 7.5 8.125Z" fill="#757575">','</path>',
                                        '</svg>',
                                    '</a>',
                                    '<p style="overflow-wrap: break-word;">' + attachement_message + '</p>',
                                '</div>',
                            '</div>',
                        '</div>',
                    '</div>',
                '</div>',
                '<span class="message-time-bot">' + time + '</span>',
            '</div>',
        ].join('');
    } else {
        var document_file_svg = "";
        if(extension == "pdf") {
            document_file_svg = 
                `<svg width="24" height="24" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" clip-rule="evenodd" d="M7.3567 0H18.9983L26.3249 7.30121V25.9001C26.3249 27.6016 24.9407 28.985 23.241 28.985H7.35665C5.65592 28.985 4.27171 27.6016 4.27171 25.9001V24.5176H3.97034C3.28392 24.5176 2.72729 23.9615 2.72729 23.2747V15.7357C2.72729 15.0487 3.28392 14.4925 3.97034 14.4925H4.27171V3.08493C4.27171 1.38517 5.65592 0 7.3567 0ZM7.3567 27.0957H23.241C23.8995 27.0957 24.4349 26.5595 24.4349 25.9L24.3903 8.04961L20.4307 8.06099C19.2494 8.06099 18.2914 7.10216 18.2914 5.92158V1.87969L7.3567 1.89112C6.69812 1.89112 6.16187 2.42737 6.16187 3.08493V14.4925H20.9695C21.6559 14.4925 22.2126 15.0487 22.2126 15.7357V23.2747C22.2126 23.9615 21.6558 24.5176 20.9695 24.5176H6.16187V25.9001C6.16187 26.5595 6.69812 27.0957 7.3567 27.0957ZM5.55078 16.8984V22.5H6.81641V20.6602H7.71875C8.07552 20.6602 8.40234 20.5807 8.69922 20.4219C8.99609 20.2604 9.23177 20.0352 9.40625 19.7461C9.58333 19.457 9.67188 19.1328 9.67188 18.7734C9.67188 18.224 9.48568 17.7747 9.11328 17.4258C8.74349 17.0742 8.27865 16.8984 7.71875 16.8984H5.55078ZM7.59375 19.5898H6.81641V17.9805H7.59375C7.82552 17.9805 8.01432 18.0534 8.16016 18.1992C8.30859 18.3424 8.38281 18.5339 8.38281 18.7734C8.38281 19.0156 8.30859 19.2122 8.16016 19.3633C8.01172 19.5143 7.82292 19.5898 7.59375 19.5898ZM10.4336 16.8984V22.5H12.4258C13.319 22.5 14.0221 22.2474 14.5352 21.7422C15.0508 21.2344 15.3086 20.5456 15.3086 19.6758C15.3086 19.2695 15.2422 18.8958 15.1094 18.5547C14.9766 18.2109 14.7878 17.918 14.543 17.6758C14.2982 17.431 13.9935 17.2409 13.6289 17.1055C13.2669 16.9674 12.8659 16.8984 12.4258 16.8984H10.4336ZM12.3711 21.4023H11.6992V17.9961H12.3711C12.5846 17.9961 12.7852 18.0286 12.9727 18.0938C13.1602 18.1562 13.3307 18.2526 13.4844 18.3828C13.6406 18.5104 13.763 18.6849 13.8516 18.9062C13.9427 19.1276 13.9883 19.3841 13.9883 19.6758C13.9883 19.9232 13.9583 20.1458 13.8984 20.3438C13.8385 20.5417 13.7578 20.7057 13.6562 20.8359C13.5547 20.9661 13.4336 21.0742 13.293 21.1602C13.1523 21.2461 13.0052 21.3086 12.8516 21.3477C12.7005 21.3841 12.5404 21.4023 12.3711 21.4023ZM16.168 16.8984V22.5H17.4336V20.3477H19.4883V19.2695H17.4336V17.9805H19.7148V16.8984H16.168Z" fill="#D32F2F"/>
                </svg>`
        } else {
            document_file_svg = [
                '<svg width="24" height="24" viewBox="0 0 18 22" fill="none" xmlns="http://www.w3.org/2000/svg">',
                    '<path d="M11.9321 0H3.3949C2.14766 0 1.13257 1.01579 1.13257 2.26228V10.6278H0.91157C0.408194 10.6278 0 11.0357 0 11.5395V17.0681C0 17.5718 0.408194 17.9796 0.91157 17.9796H1.13257V18.9934C1.13257 20.2412 2.14766 21.2557 3.39486 21.2557H15.0434C16.2898 21.2557 17.3049 20.2412 17.3049 18.9934V5.35422L11.9321 0ZM1.5081 12.2989C1.82671 12.2482 2.24178 12.2196 2.67996 12.2196C3.40808 12.2196 3.88025 12.3503 4.25022 12.6289C4.64836 12.9249 4.89846 13.3974 4.89846 14.0742C4.89846 14.8078 4.6313 15.3144 4.26133 15.6271C3.85763 15.9626 3.24311 16.1217 2.49237 16.1217C2.04287 16.1217 1.72426 16.0933 1.50814 16.0648V12.2989H1.5081ZM15.0434 19.8702H3.3949C2.91194 19.8702 2.51869 19.477 2.51869 18.9934V17.9796H13.3776C13.8809 17.9796 14.2892 17.5718 14.2892 17.0681V11.5395C14.2892 11.0357 13.881 10.6278 13.3776 10.6278H2.51869V2.26228C2.51869 1.78007 2.91194 1.38682 3.3949 1.38682L11.4137 1.37844V4.34249C11.4137 5.20825 12.1162 5.91139 12.9825 5.91139L15.8862 5.90305L15.9189 18.9933C15.9189 19.477 15.5263 19.8702 15.0434 19.8702ZM5.29308 14.1936C5.29308 13.0444 6.02685 12.1856 7.15902 12.1856C8.33674 12.1856 8.97943 13.0673 8.97943 14.1255C8.97943 15.3824 8.21723 16.1446 7.09647 16.1446C5.95878 16.1446 5.29308 15.2859 5.29308 14.1936ZM11.5131 15.4221C11.7747 15.4221 12.0647 15.3651 12.2356 15.2969L12.3663 15.9737C12.2072 16.0537 11.8486 16.1391 11.3824 16.1391C10.0567 16.1391 9.37409 15.3144 9.37409 14.2222C9.37409 12.9138 10.3072 12.1856 11.4675 12.1856C11.9171 12.1856 12.2582 12.2766 12.4118 12.3559L12.2356 13.0444C12.0591 12.97 11.8145 12.902 11.5075 12.902C10.8189 12.902 10.2843 13.3175 10.2843 14.1707C10.2843 14.9385 10.7394 15.4221 11.5131 15.4221Z" fill="#0254D7"/>',
                    '<path d="M3.97708 14.1026C3.98264 13.3057 3.51612 12.8854 2.77088 12.8854C2.57734 12.8854 2.45227 12.902 2.3783 12.9194V15.4276C2.45227 15.4451 2.57183 15.4451 2.67989 15.4451C3.46502 15.4506 3.97708 15.0184 3.97708 14.1026Z" fill="#0254D7"/>',
                    '<path d="M8.0637 14.1534C8.0637 13.4655 7.73367 12.8735 7.13644 12.8735C6.5504 12.8735 6.20886 13.4314 6.20886 14.1763C6.20886 14.9274 6.56182 15.4561 7.14204 15.4561C7.72812 15.4561 8.0637 14.8988 8.0637 14.1534Z" fill="#0254D7"/>',
                '</svg>',
            ].join('');
        }
        if(attachement_message) {
            attachment_message_html = '<div class="upload-file-text-area" style="margin-bottom:10px">' + attachement_message + '</div>';
        }
        html = `
                <div class="easychat-bot-message-div">
                <div style="display: flex; flex-direction: row;">
                    <div class="easychat-bot-msg-sender-profile" style="background-color: ${BOT_THEME_COLOR}"> 
                        ${msg_sender_icon}
                    </div>
                <div class="message-outer-container">
                <div class="message-inner-container">
                    <div class="easychat-agent-message-name" style="color: ${BOT_THEME_COLOR};text-align: left;"> ${name} </div>
                    <div class="pdf-container">
                        <div class="pdf-description">
                            <div class="pdf-logo">
                            ${document_file_svg}                   
                            </div>
                            <div class="pdf-name" style="margin-left: 11px;">
                                <p class="document-name-p-tag">${file_name}</p>
                            </div>
                        </div>
                        <div class="pdf-download-logo tooltip" style="cursor: pointer;">
                            <a href="${file_src}?session_id=${session_id}" style="cursor: pointer;" target="_blank">
                            <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path fill-rule="evenodd" clip-rule="evenodd" d="M9.65213 4.08279C9.65213 3.34671 10.2549 2.75 10.9985 2.75C11.7421 2.75 12.3448 3.34671 12.3448 4.08279V10.3144C12.3448 10.4093 12.4226 10.4862 12.5184 10.4862H14.3647C14.6285 10.4863 14.8679 10.6388 14.9773 10.8764C15.0867 11.114 15.0459 11.393 14.873 11.5901L11.5068 15.4228C11.379 15.5687 11.1935 15.6525 10.9985 15.6525C10.8035 15.6525 10.618 15.5687 10.4902 15.4228L7.12398 11.5901C6.95103 11.393 6.91026 11.114 7.01965 10.8764C7.12905 10.6388 7.36848 10.4863 7.63225 10.4862H9.47854C9.57441 10.4862 9.65213 10.4093 9.65213 10.3144V4.08279ZM17.5634 15.2255C17.5634 14.7654 17.9402 14.3924 18.405 14.3924C18.6288 14.3915 18.8438 14.4789 19.0023 14.6352C19.1609 14.7915 19.25 15.004 19.25 15.2255V16.5006C19.25 18.019 18.0065 19.25 16.4726 19.25H5.524C3.99142 19.2481 2.75004 18.0177 2.75004 16.5006V15.2255C2.75004 14.7654 3.12682 14.3924 3.5916 14.3924C4.05638 14.3924 4.43316 14.7654 4.43316 15.2255V16.5006C4.43393 17.0965 4.92197 17.5793 5.524 17.5797H16.4726C17.0746 17.5793 17.5627 17.0965 17.5634 16.5006V15.2255Z" fill="${BOT_THEME_COLOR}"/>
                                        </svg>
                                </a>        
                                <span class="download-tooltip">Download</span>            
                        </div>
                    </div>
                    ${attachment_message_html}
                `
            if(extension == "pdf") {
                if(window.enable_preview_functionality == "True") {
                    html += `<button onclick="open_pdf('${file_name_in_url}','${file_src}','${session_id}')" class="coview-btn" id="coview" style="background: ${BOT_THEME_COLOR};">Preview</button>`
                }
                html += `</div>
                        </div>
                    </div>
                    <span class="message-time-bot">${time}</span>
                </div>
                `
            }else{
                html += `</div>
                    </div>
                    </div>
                    <span class="message-time-bot">${time}</span>
                </div>`
            }
    }

    document.getElementById("easychat-chat-container").innerHTML += html;

    scroll_to_bottom();
}

function append_attachment_and_message_in_chat(attachement_message, file_src, file_name, time, sender, name, agent_profile_pic_source) {
    if(sender == "client") {
        append_client_attachment_and_message_in_chat(attachement_message, file_src, file_name, time, name, agent_profile_pic_source)
    } else if(sender == "invited_agent") {
        append_invited_agent_attachment_and_message_in_chat(attachement_message, file_src, file_name, time, name, agent_profile_pic_source)
    } else {
        append_agent_attachment_and_message_in_chat(attachement_message, file_src, file_name, time);
    }
}

function append_attachment_send_message(element){

    let attachment_message = document.getElementById("attachment-message").value;
    if(check_text_link(attachment_message) == false) {
        attachment_message = stripHTML(attachment_message)
        attachment_message = remove_special_characters_from_str(attachment_message)
    } else {
        attachment_message = easyassist_linkify(perform_url_encoding(attachment_message));
    }
    attachment_message = attachment_message.trim();
    var time = return_time();

    for(let idx = 0; idx < uploaded_attached_files.length; idx ++) {
        attached_file_src = uploaded_attached_files[idx]["file_path"];
        attachment_file_name = uploaded_attached_files[idx]["file_name"];
        append_attachment_and_message_in_chat(attachment_message, attached_file_src, attachment_file_name, time, "agent", "agent");
        parent.postMessage({
            event_id: 'cobrowsing-agent-chat-message',
            data: {
                message: attachment_message,
                attachment: attached_file_src,
                attachment_file_name: attachment_file_name,
                time: time
            }
        }, "*");
    }

    document.getElementById("modal-send-attachement-modal").style.display = "none";
    attachment_file_name = "None";
    attached_file_src = "None";
    uploaded_attached_files = [];
}

document.getElementById("span-easychat-send-attachment-close").onclick = function(e){
    document.getElementById("modal-send-attachement-modal").style.display = "none";
    attachment_file_name= "None";
}


function easyassist_typing_indication_send(){
    parent.postMessage({
        event_id: 'livechat-typing',
        data: {}
    }, "*");
}

document.getElementById("user_input").addEventListener("keydown", easyassist_typing_indication_send)

function open_pdf(file_name,file_src,session_id){
    parent.postMessage({
        event_id: 'open_pdf_render_modal',
        file_name: file_name,
        file_src: file_src,
        session_id: session_id
    }, "*");
}

function update_agent_used_canned_response(keyword) {
    let json_string = JSON.stringify({
        "keyword": remove_special_characters_from_str(stripHTML(keyword))
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/update-agent-used-canned-response/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response);
            response = JSON.parse(response);
            if(response["status_code"] != 200){
              console.log("error");
            }
        }
    }
    xhttp.send(params);
}

function initialize_livechat_canned_response() {
    let user_input = document.getElementById('user_input');
    
    const canned_response_list = CANNED_RESPONSE;
    let dom_body = document.querySelectorAll.bind(document);
    
    function auto_complete() {
        let canned_response_scroll_list = [];
        let current_focus = -1;
        let div_element;
      
        div_element = document.createElement("DIV");
        div_element.setAttribute("id", "user-input-autocomplete-list");
        div_element.setAttribute("class", "canned-response-list-div canned-response-tab hide");
        user_input.parentNode.appendChild(div_element);
        
        for (let i = 0; i < canned_response_list.length; i++) {
          let keyword = "/" + canned_response_list[i]["keyword"];
          let response = canned_response_list[i]["response"];
          let pk_id = canned_response_list[i]['pk'];
  
          let li_element = document.createElement('li');
          li_element.setAttribute('id', 'canned-keyword-' + pk_id)
          li_element.setAttribute('class', 'canned-list-item')
          
          if(agent_to_customer_cobrowsing == "True"){
            li_element.setAttribute('onclick', `update_agent_used_canned_response_reverse('${keyword}')`)
          } else {
            li_element.setAttribute('onclick', `update_agent_used_canned_response('${keyword}')`)
          }
          
          let keyword_div = document.createElement('div');
          keyword_div.setAttribute('class', 'keyword-div');
          keyword_div.innerHTML = keyword;
          li_element.appendChild(keyword_div);
          
          let response_div = document.createElement('div');
          response_div.setAttribute('class', 'response-div');
          response_div.innerHTML = response;
          li_element.appendChild(response_div);
          
          li_element.innerHTML += `<input type="hidden" id="canned-keyword" focus_id=${i} pk_id=${pk_id}>`;
          li_element.getElementsByTagName("input")[0].value = keyword.toLowerCase();
          
          li_element.innerHTML += '<input type="hidden" id="canned-list-response">';
          li_element.getElementsByTagName("input")[1].value = response;
          
          div_element.appendChild(li_element);
          li_element.addEventListener("click", function(e) {
            user_input.value = this.getElementsByTagName("input")[1].value;
            close_response_div();
          });

          canned_response_scroll_list.push(i);
  
        }
  
        function remove_active(x) {
          for (let i = 0; i < x.length; i++) {
            x[i].classList.remove("active");
          }
        }
  
        function add_active(current_div) {
            if (!current_div) 
                return false;
            remove_active(current_div);
            if (current_focus > canned_response_scroll_list.length - 1) 
                current_focus = 0;
            if (current_focus < 0) 
                current_focus = canned_response_scroll_list.length - 1;
            current_div[canned_response_scroll_list[current_focus]].classList.add("active");
        }
  
        user_input.addEventListener("input", function(e) {
            let current_div = document.getElementById('user-input-autocomplete-list');
            canned_response_scroll_list = []
            current_focus = -1;
            let value = this.value.toLowerCase();
            if(value && value[0] == '/'){
              current_div.classList.remove("hide");
            
            let inital_canned_list = document.querySelectorAll(".searched");
  
            for(let i = 0; i < inital_canned_list.length; i++) {
              inital_canned_list[i].classList.add("hide");
              inital_canned_list[i].classList.remove("searched");
            }
  
            let matched_keyword_list = dom_body(`input#canned-keyword[value^="${value}"]`)
            
            if(!matched_keyword_list.length){
                document.getElementById("no-data-div").classList.remove("hide");
            } else {
            
                for(let i = 0 ; i < matched_keyword_list.length; i++){
                    let pk_id = matched_keyword_list[i].getAttribute("pk_id");
                    let element = document.getElementById("canned-keyword-" + pk_id)
                    element.classList.remove("hide");
                    element.classList.add("searched");
                    canned_response_scroll_list.push(matched_keyword_list[i].getAttribute("focus_id"))
              }
            }
          } else {
            close_response_div();
            if(current_div) 
                remove_active(current_div.getElementsByClassName("canned-list-item"))
          }
  
        });
  
        function close_response_div(){
          let list_continer = document.getElementById('user-input-autocomplete-list');
          if(!list_continer.classList.contains('hide')){
            list_continer.classList.add("hide");
          }
  
          let no_data_div = document.getElementById("no-data-div");
          if(!no_data_div.classList.contains("hide")) {
            no_data_div.classList.add("hide");
          }
        }
  
        document.addEventListener("click", function (e) {
          close_response_div();
        });
  
        user_input.addEventListener("keydown", function (e) {
          let current_div = document.getElementById(
            'user-input-autocomplete-list'
          );
        
          if (current_div)
            current_div = current_div.getElementsByClassName("canned-list-item");
            if (e.keyCode == 40) {
                current_focus++;
            if (current_focus > canned_response_scroll_list.length - 1) {
                current_focus = 0;
            }
            current_div[canned_response_scroll_list[current_focus]].scrollIntoView({
                behaviour: "smooth",
                block: "nearest",
            });
            add_active(current_div);
          } else if (e.keyCode == 38) {
            current_focus--;
            if (current_focus < 0) {
              current_focus = canned_response_scroll_list.length - 1;
            }
            current_div[canned_response_scroll_list[current_focus]].scrollIntoView({
              behaviour: "smooth",
              block: "nearest",
            });
            add_active(current_div);
          } else if (e.keyCode == 13) {
            e.preventDefault();
            if (current_focus > -1) {
                user_input.value = "";
                setTimeout(function(){
                    if (current_div) {
                        current_div[canned_response_scroll_list[current_focus]].click();
                        remove_active(current_div);
                    }
                    current_focus = -1;
                }, 500)
            }
        }
        });
    }
    auto_complete();
}

function update_agent_used_canned_response_reverse(keyword) {
    let url_parameters = new URLSearchParams(window.location.search);
    let agent_code = url_parameters.get("agent_code")
    let json_string = JSON.stringify({
        "agent_code": stripHTML(agent_code),
        "keyword": remove_special_characters_from_str(stripHTML(keyword))
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/reverse/update-agent-used-canned-response/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response);
            response = JSON.parse(response);
            if(response["status_code"] != 200){
              console.log("error");
            }
        }
    }
    xhttp.send(params);
}