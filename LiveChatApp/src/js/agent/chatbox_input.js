import { send_message_to_socket, send_typing_message_to_customer } from "./livechat_chat_socket";
import {
    is_mobile,
    encrypt_variable,
    custom_decrypt,
    is_file_supported,
    check_file_size,
    check_malicious_file,
    is_docs,
    is_image,
    is_pdf,
    is_txt,
    is_video,
    is_excel,
    stripHTML,
    strip_unwanted_characters,
    EncryptVariable,
    getCsrfToken,
    remove_special_characters_from_str,
    stripHTMLtags,
    strip_malicious_chars,
} from "../utils";

import {
    resize_chat_window,
    has_customer_left_chat,
    append_response_user,
    get_chat_data,
    scroll_to_bottom,
    append_temp_file_to_agent,
    send_message_to_user_with_file,
    get_blacklisted_keywords,
    send_mail_to_customer,
    is_special_character_allowed_in_file_name,
    is_special_character_allowed_in_chat,
    get_livechat_channels_char_limit
} from "./chatbox";

import {
    get_session_id,
    get_theme_color,
    showToast,
    append_message_in_chat_icon,
    get_agent_name,
    get_icons,
    reset_inactivity_timer,
    remove_message_diffrentiator,
    get_agent_username,
    get_current_customer_tab,
    check_is_email_session,
} from "./console";
import { save_message_to_local } from "./local_db";

import {
    send_message_to_guest_agent_socket,
} from "./livechat_agent_socket"
import { resize_internal_chat_window } from "../common/livechat_internal_chat_console";

const state = {
    mic: {
        instance: null,
        recognizing: false,
        prev_text: "",
        start: new Date().getTime(),
        end: new Date().getTime(),
        ignore_onend: false,
    },
    attachment: {
        data: "",
        form_data: "",
        file_src: '',
        file_name: '',
        channel_file_url: '',
    },
};


$(function(){ // this will be called when the DOM is ready
$("#query").keyup(function (e) {
    e = e || window.event;

    var input_element = document.getElementById("query");
    var user_query = input_element.value.trim();
    const theme_color = get_theme_color();
    if (user_query != "") {
        document.getElementById("fill-submit-btn").style.fill = theme_color.one;
        send_typing_message_to_customer();
    } else {
        document.getElementById("fill-submit-btn").style.fill = theme_color.two;
    }
});

$("#query-mobile").keyup(function (e) {
    e = e || window.event;

    var input_element = document.getElementById("query-mobile");
    var user_query = input_element.value.trim();
    const theme_color = get_theme_color();
    if (user_query != "") {
        document.getElementById("fill-submit-btn").style.fill = theme_color.one;
        send_typing_message_to_customer();
    } else {
        document.getElementById("fill-submit-btn").style.fill = theme_color.two;
    }
});
});

function check_if_sentence_valid(sentence, channel) {
    const livechat_channels_char_limit = get_livechat_channels_char_limit();

    let char_limit = 3000;
    if (channel == 'Facebook') {
        char_limit = livechat_channels_char_limit.Facebook;
    } else if (channel == 'Instagram') {
        char_limit = livechat_channels_char_limit.Instagram;
    }

    return (sentence.length && sentence.length < char_limit);
}

function send_message_to_user() {
    const session_id = get_session_id();
    const chat_data = get_chat_data();
    const guest_session = localStorage.getItem(`guest_session-${session_id}`);
    const guest_session_status = localStorage.getItem(`guest_session_status-${session_id}`);
    var is_guest_session = false;
    var message_id = "";
    var translated_text = "";
    if(guest_session == "true")
        is_guest_session = true;
    
    if (has_customer_left_chat(session_id) && !check_is_email_session(session_id)) {
        showToast("Customer has left the chat. Cannot send message now.", 2000);
        return;
    }
    reset_inactivity_timer(session_id, chat_data.bot_id, 'agent');

    var sentence = "";

    var condition = false;
    let chat_text_id = (is_mobile()) ? "#query-mobile" : "#query";

    sentence = $(chat_text_id).val();
    sentence = strip_malicious_chars(sentence)
    if (!is_url(sentence)) {
        // sentence = stripHTMLtags(sentence);
        if (!is_special_character_allowed_in_chat()) {
            sentence = remove_special_characters_from_str(sentence);
        }
    }
    sentence = sentence.trim()
    condition = check_if_sentence_valid(sentence, chat_data.channel);

    if (sentence.length == 0) {
        $(chat_text_id).val("");
        return;
    }
    if (validate_agent_input(sentence)) {
        return;
    }
    $(chat_text_id).val("");
    auto_resize();
    

    if (condition) {
       
        const theme_color = get_theme_color();
        document.getElementById("fill-submit-btn").style.fill = theme_color.two;

        let msg = {
            sender: "Agent",
            text_message: sentence,
            is_attachment: "False",
            is_guest_agent_message: is_guest_session,
        };
        const session_id = get_session_id();
        append_message_in_chat_icon(session_id, msg);

        document.getElementById("query").value = "";
        localStorage.setItem(`user_input-${session_id}`, "");

        let agent_preferred_language = "en";
        let customer_language = localStorage.getItem(`customer_language-${session_id}`);
        
        if(localStorage.getItem(`agent_language-${session_id}`)) {
            agent_preferred_language = localStorage.getItem(`agent_language-${session_id}`);
        }
        
        let to_translate_message = false;
        if(agent_preferred_language != customer_language) {
            to_translate_message = true;
        }

        var json_string = JSON.stringify({
            message: sentence,
            sender: "Agent",
            attached_file_src: "",
            thumbnail_url: "",
            session_id: session_id,
            is_guest_agent_message: is_guest_session,
            sender_name: get_agent_name(),
            sender_username: get_agent_username(),
            to_translate_message: to_translate_message,
        });
        json_string = encrypt_variable(json_string);
        json_string = encodeURIComponent(json_string);

        let save_data_url = "/livechat/save-agent-chat/";
        if(check_is_email_session(session_id)) {
            save_data_url = "/livechat/save-agent-email-chat/";
        } 

        var csrf_token = getCsrfToken();
        var xhttp = new XMLHttpRequest();
        var params = "json_string=" + json_string;
        xhttp.open("POST", save_data_url, false);
        xhttp.setRequestHeader("X-CSRFToken", csrf_token); 
        xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xhttp.onreadystatechange = function () {
                if (this.readyState == 4 && this.status == 200) {
                let response = JSON.parse(this.responseText);
                response = custom_decrypt(response);
                response = JSON.parse(response);
                if (response["status_code"] == "200") {
                    console.log("chat send by agent saved");
                    message_id = response["message_id"];
                    translated_text = response["translated_text"];
                }
            }
        };
        xhttp.send(params);

        if(check_is_email_session(session_id)) {
            send_mail_to_customer(session_id, message_id, "");
        }

        if(!agent_preferred_language)
            agent_preferred_language = "en";

        append_response_user(sentence, false, message_id, agent_preferred_language);

        save_message_to_local({
            message: sentence,
            sender: "Agent",
            sender_name: get_agent_name(),
            session_id: session_id,
            is_guest_agent_message: is_guest_session,
            sender_username: get_agent_username(),
            message_id: message_id,
            language: agent_preferred_language,
        });

        let chat_data = get_chat_data();
        var text_message = sentence;
        var is_guest_agent_message = "false";
        if(guest_session == "true" && guest_session_status == "accept")
            is_guest_agent_message = "true";
        var sentence = JSON.stringify({
            message: JSON.stringify({
                text_message: sentence,
                type: "text",
                channel: chat_data.channel,
                path: "",
                bot_id: chat_data.bot_id,
                is_guest_agent_message: is_guest_agent_message,
                agent_name: get_agent_name(),
                session_id: session_id,
                sender_username: get_agent_username(),
                message_id: message_id,
                language: agent_preferred_language,
                translated_text: translated_text,
            }),
            sender: "Agent",
        });

        send_message_to_socket(sentence);

        send_message_to_guest_agent_socket(sentence);

        scroll_to_bottom();
    } else {
        if (chat_data.channel == 'Facebook' || chat_data.channel == 'Instagram') {
            showToast("You have exceeded the character limit for this channel.", 3000);
        }
        else {
            showToast("Seems like we have exceeded the maximum permissible character limit.", 3000);
        }
    }
    remove_message_diffrentiator(session_id);
}

function validate_agent_input(sentence) {
    let warning_message = "";
    let blacklisted_keywords = get_blacklisted_keywords();
    for (var i = 0; i < blacklisted_keywords.length; i++) {
        if (sentence.toLowerCase().includes(blacklisted_keywords[i].toLowerCase())) {
            warning_message += "<b>" + blacklisted_keywords[i] + "</b>, ";
            continue;
        }
    }
    if (warning_message != "") {
        let html =
            "<p>This message could not be sent because it contains blacklisted keyword(s) " +
            warning_message.slice(0, -2) +
            ". Please remove these keywords to send the message.</p>";
        showToast(html, 5000);
        return true;
    }
    return false;
}

function append_file_to_modal(name) {
    let file_svg = "";
    const icons = get_icons();
    if (is_pdf(name)) file_svg = icons.pdf;
    else if (is_docs(name)) file_svg = icons.doc;
    else if (is_excel(name)) file_svg = icons.excel;
    else if (is_txt(name)) file_svg = icons.txt;
    else if (is_image(name)) file_svg = icons.image;
    else if (is_video(name)) file_svg = icons.video;

    const html = `<div class="live-chat-file-bubble file-attachement-modal">
                    <div style="width: 50px; height: 45px; display: inline-flex;">
                        ${file_svg}                
                    </div>                    
                    <div style="width: 85%; height: 50px; display: inline-block;">
                        <span id="custom-text-file-name">
                            ${name}
                        </span>
                        <div style="position: absolute; right: 3.5em; top: 7.5em; cursor: pointer;" id="file-upload-cancel-btn"> ${icons.cross} </div>
                        <br>                        
                        <div id="file-upload-progress-bar"></div>
                    </div>               
                </div>`;

    $("#live_chat_file_wrapper").html(html);

    const theme_color = get_theme_color();
    // document.getElementById("livechat_cross_btn").style.fill = theme_color.one;
}

function reset_file_upload_modal(is_msg_reset_reqd) {
    document.getElementById("send_attachment").classList.add("disabled");
    document.getElementById("send_attachment").style.pointerEvents = "none";
    document.getElementById("live_chat_file_wrapper").innerHTML = "";

    if (is_msg_reset_reqd) {
        document.getElementById('query-file').value = '';
    }
    state.attachment.file_src = "";
}

function upload_file_attachment(e) {
    state.attachment.form_data = new FormData();
    state.attachment.data = document.querySelector(
        "#easychat-livechat-file-attchment-input"
    ).files[0];

    if (
        !is_file_supported(state.attachment.data.name) ||
        !check_malicious_file(state.attachment.data.name)
    ) {
        showToast("Invalid File Format!", 3000);
        document.querySelector("#easychat-livechat-file-attchment-input").value = "";
        return;
    }

    if (!check_file_size(state.attachment.data.size)) {
        showToast("Please Enter a file of size less than 5MB!", 3000);
        document.querySelector("#easychat-livechat-file-attchment-input").value = "";
        return;
    }

    append_file_to_modal(state.attachment.data.name);

    $("#file-upload-progress-bar").progressbar({
        max: 100,
        value: 100,
    });

    document.getElementById("file-upload-cancel-btn").addEventListener("click", function () {
        reset_file_upload_modal(true);
    });

    document.getElementById("send_attachment").classList.remove("disabled");
    document.getElementById("send_attachment").style.pointerEvents = "auto";
    document.querySelector("#easychat-livechat-file-attchment-input").value = "";
}

$(document).on("click", "#send_attachment", function(){
    var sentence = $("#query-file").val();

    if(validate_agent_input(sentence)){
        return;
    }
    
    if (sentence.length >= 3000) {
        showToast("Seems like we have exceeded the maximum permissible character limit.", 3000);
        return;
    }
    
    reset_file_upload_modal(false);
    $("#livechat-file-upload-modal").modal("toggle");

    var upload_attachment_data = state.attachment.data;
    let attachment_name = upload_attachment_data.name;
    attachment_name = attachment_name.replace(/ /g, "");

    const special_char_regex = /[-'/`~!#*$@%+=,^&(){}[\]|;:<>"?\\]/g;
    if (is_special_character_allowed_in_file_name()) {
        attachment_name = attachment_name.replace(special_char_regex, '_');
    } else if (special_char_regex.test(attachment_name)) {
        showToast(`<p> File not supported due to presence of special characters in the name </p>`, 3000);
        $("#query-file").val("");
        return;
    }

    var reader = new FileReader();
    reader.readAsDataURL(upload_attachment_data);
    reader.onload = function() {

        var base64_str = reader.result.split(",")[1];

        var uploaded_file = [];
        uploaded_file.push({
            "filename": attachment_name,
            "base64_file": base64_str,
            "session_id": get_session_id(),
        });
        var json_string = JSON.stringify(uploaded_file)
        json_string = encrypt_variable(json_string)
        state.attachment.form_data.append("uploaded_file", json_string);
        upload_file_attachment_to_server();
    };

    reader.onerror = function(error) {
        console.log('Error: ', error);
    };

});

function upload_file_attachment_to_server() {
    const params = state.attachment.form_data;

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/livechat/upload-attachment/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response.status == 200) {
                append_temp_file_to_agent(state.attachment.data.name);
                state.attachment.file_src = response.src;
                state.attachment.file_name = response.name;

                try {
                    state.attachment.channel_file_url = response.channel_file_url;
                } catch (err) {
                    state.attachment.channel_file_url = "";
                }

                if (is_image(state.attachment.file_src)) {
                    const reader = new FileReader();
                    reader.addEventListener(
                        "load",
                        function () {
                            state.attachment.form_data = "";
                            state.attachment.data = "";
                            send_message_to_user_with_file(
                                state.attachment.file_src,
                                response.thumbnail_url,
                                state.attachment.channel_file_url,
                                reader.result
                            );
                        },
                        false
                    );

                    if (state.attachment.data) {
                        reader.readAsDataURL(state.attachment.data);
                    }
                } else {
                    state.attachment.form_data = "";
                    state.attachment.data = "";
                    send_message_to_user_with_file(state.attachment.file_src, response.thumbnail_url, state.attachment.channel_file_url);
                }
            } else if(response.status == 300){
                showToast("<p> File not supported due to presence of special characters in the name </p>", 3000);
            }
            if (response.status == 500) {
                if (response.status_message == "Malicious File") {
                    showToast("Invalid File Format!", 3000);
                } else if (response.status_message == "File Size Bigger Than Expected") {
                    showToast("Please Enter a file of size less than 5MB!", 3000);
                }
            }
        }
    };
    xhttp.send(params);
}

function auto_resize() {
    let el;
    if (is_mobile()) {
        el = document.getElementById("query-mobile");
    } else {
        el = document.getElementById("query");
    }

    el.style.boxSizing = el.style.mozBoxSizing = "border-box";
    el.style.overflowY = "hidden";

    el.addEventListener("input", function () {
        adjustHeight(el);
    });

    window.addEventListener("resize", function () {
        adjustHeight(el);
    });

    adjustHeight(el);
}

function adjustHeight(el) {
    reset_input_size();
    var minHeight = el.scrollHeight;
    var outerHeight = parseInt(window.getComputedStyle(el).height, 10);
    var diff = outerHeight - el.clientHeight;

    if (el.value == "") {
        el.style.height = el.style.minHeight;
        el.parentElement.parentElement.style.height =
            el.parentElement.parentElement.style.minHeight;
    } else {
        if (el.scrollHeight < 104) {
            el.style.height = 0;
            el.style.height = Math.max(minHeight, el.scrollHeight + diff) + "px";
            el.parentElement.parentElement.style.height =
                Math.max(minHeight, el.scrollHeight + diff) + 19 + "px";
            el.style.overflowY = "hidden";
        } else {
            el.style.height = "90px";
            el.parentElement.parentElement.style.height = "109px";
            el.style.overflowY = "auto";
        }
    }

    if (window.location.href.includes('internal-chat')) {
        resize_internal_chat_window();
    } else {
        resize_chat_window();
    }
}

function reset_input_size() {
    let el;
    if (is_mobile()) {
        el = document.getElementById("query-mobile");
    } else {
        el = document.getElementById("query");
    }

    el.style.height = "0";
    el.parentElement.parentElement.style.height = "0";
}

function append_livechat_file_upload_modal(is_internal_chat="false") {
if(is_internal_chat != "true"){
    const session_id = get_session_id();
    const chat_data = get_chat_data();
    reset_inactivity_timer(session_id, chat_data.bot_id, 'agent');
    if (has_customer_left_chat(session_id) && !check_is_email_session(session_id)) {
        showToast("Customer has left the chat. Cannot send message now.", 2000);
        return;
    }
}
    $("#livechat-file-upload-modal").modal("show");
}

/* Mic Functionality Starts */

function add_mic_functionality() {
    let SpeechRecognition = SpeechRecognition || webkitSpeechRecognition;
    const mic = state.mic;
    mic.instance = new SpeechRecognition();
    mic.instance.continuous = false;
    mic.instance.interimResults = true;

    mic.instance.onstart = function () {
        mic.recognizing = true;
    };

    mic.instance.onerror = function (event) {
        if (event.error == "no-speech") {
            state.mic.ignore_onend = true;
        }
        if (event.error == "audio-capture") {
            state.mic.ignore_onend = true;
        }
        if (event.error == "not-allowed") {
            state.mic.ignore_onend = true;
            mic.instance = null;
            deactivate_mic();
            alert(
                "You will not be able to use voicebot feature as you haven't allowed microphone access."
            );
        }
    };

    mic.instance.onend = function () {
        if (is_mobile()) {
            if (state.mic.prev_text == document.getElementById("query-mobile").value) {
                state.mic.end = new Date().getTime();
            }
            if (state.mic.prev_text != document.getElementById("query-mobile").value) {
                state.mic.end = new Date().getTime();
                state.mic.start = new Date().getTime();
                state.mic.prev_text = document.getElementById("query-mobile").value;
            }
        } else {
            if (state.mic.prev_text == document.getElementById("query").value) {
                state.mic.end = new Date().getTime();
            }
            if (state.mic.prev_text != document.getElementById("query").value) {
                state.mic.end = new Date().getTime();
                state.mic.start = new Date().getTime();
                state.mic.prev_text = document.getElementById("query").value;
            }
        }
        if (state.mic.end - state.mic.start >= 5000) {
            state.mic.recognizing = false;
            state.mic.instance.continuous = false;
            state.mic.instance.abort();
        }

        if (!state.mic.recognizing) {
            if (mic.instance) mic.instance.abort();

            document.getElementById("btn-mic-up").style.fill = "#2F405B";
            document.getElementById("btn-mic-down").style.fill = "#2F405B";
        } else {
            mic.instance.start();
        }
    };

    mic.instance.onresult = function (event) {
        var text = event.results[0][0].transcript;

        if (is_mobile()) {
            if (event.results[0].isFinal) {
                text = " " + text;
                document.getElementById("query-mobile").value += text;
                state.mic.ignore_onend = true;
                state.mic.recognizing = false;
                state.mic.continuous = false;
                state.mic.instance.abort();
            }
        } else {
            if (event.results[0].isFinal) {
                text = " " + text;
                document.getElementById("query").value += text;
                state.mic.ignore_onend = true;
                state.mic.recognizing = false;
                state.mic.continuous = false;
                state.mic.instance.abort();
            }
        }
    };
}

function activate_mic() {
    const session_id = get_session_id();
    const chat_data = get_chat_data();
    reset_inactivity_timer(session_id, chat_data.bot_id, 'agent');
    if (has_customer_left_chat(session_id)) {
        showToast("Customer has left the chat. Cannot send message now.", 2000);
        return;
    }
    const mic = state.mic;
    if (mic.recognizing) {
        mic.recognizing = false;
        mic.instance.continuous = false;
        mic.instance.abort();
        document.getElementById("btn-mic-up").style.fill = "#2F405B";
        document.getElementById("btn-mic-down").style.fill = "#2F405B";
    } else if (mic.instance != null) {
        const theme_color = get_theme_color();
        document.getElementById("btn-mic-up").style.fill = theme_color.one;
        document.getElementById("btn-mic-down").style.fill = theme_color.one;
        state.mic.start = new Date().getTime();
        state.mic.end = new Date().getTime();
        mic.instance.start();
    } else {
        alert(
            "You will not be able to use voicebot feature as you haven't allowed microphone access."
        );
        deactivate_mic();
    }
}

function deactivate_mic () {
    const mic = state.mic;

    if (mic.recognizing) {
        mic.recognizing = false;
        mic.instance.continuous = false;
        mic.instance.abort();
    }
    if (mic.instance) {
        mic.recognizing = false;
        mic.instance.continuous = false;
        mic.instance.abort();
    }

    document.getElementById("btn-mic-up").style.fill = "#2F405B";
    document.getElementById("btn-mic-down").style.fill = "#2F405B";
}

function is_url(sentence) {
    if (new RegExp("([a-zA-Z0-9]+://)?([a-zA-Z0-9_]+:[a-zA-Z0-9_]+@)?([a-zA-Z0-9.-]+\\.[A-Za-z]{2,4})(:[0-9]+)?(/.*)?").test(sentence)) {
        return true;
    }
    return false;
}  

/* Mic Functionality Ends */

export {
    send_message_to_user,
    add_mic_functionality,
    auto_resize,
    append_livechat_file_upload_modal,
    upload_file_attachment,
    activate_mic,
    reset_file_upload_modal,
    append_file_to_modal,
    is_url,
    check_if_sentence_valid
};
