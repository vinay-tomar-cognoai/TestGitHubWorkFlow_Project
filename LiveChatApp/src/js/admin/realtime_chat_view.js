import {
    EncryptVariable,
    custom_decrypt,
    encrypt_variable,
    getCsrfToken,
} from "../utils";

import {
    append_file_to_agent,
    get_user_initial,
    get_masked_message,
    append_customer_message,
    append_agent_message,
    append_system_message,
    append_supervisor_message_realtime,
    append_supervisor_file_realtime,
} from "../common/archive_customer";

import {
    get_session_id,
    showToast,
} from "../agent/console";

import {
    get_reply_message_html,
    get_actual_message_details,
    reset_file_upload_modal_chathistory,
} from "./chat_history";

import { 
    get_system_text_response_html, 
    get_video_call_text_response, 
    get_customer_warning_system_text_html,
     get_report_message_notif_html 
 } from "../agent/chatbox";

const state = {
    customer_name: null,
    agent_name: null,
    active_url: null
}

function update_message_history_realtime_view(){
    const session_id = get_session_id();
    var json_string = JSON.stringify({
        session_id: session_id,
        refresh_customer_details: false
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);
    document.getElementById("chat_loader-"+session_id).style.display = "flex";

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/update-message-history/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                    let message_history = response.message_history;
                    let cust_last_updated_time = response.cust_last_updated_time;
                    set_customer_name(response.name);
                    set_agent_name(response.assigned_agent);
                    set_active_url(response.active_url);
                    append_message_history_realtime_chat_view(message_history, cust_last_updated_time);
            }
            document.getElementById("chat_loader-"+session_id).style.display = "none";
        }
    };
    xhttp.send(params);
}

function append_message_history_realtime_chat_view(message_history, cust_last_updated_time){
    const session_id = get_session_id();
    const active_url = get_active_url();
    var html =  `<input type="hidden"  value = "${session_id}"/>
                <input type="hidden"  value = "0"/>`
    $(`#style-2-${session_id}`).html(html);
    for (var item = 0; item < message_history.length; item++) {
        let message = message_history[item];
        let sender_initial = (message.sender_name).trim()[0].toUpperCase();
        if (message.sender == "Customer" || (message.sender == "Agent" && message.is_guest_agent_message) ) {
            if (message.attached_file_src != "") {
                append_file_to_agent(
                    message.attached_file_src,
                    message.message,
                    message.time,
                    message.sender_name,
                    message.sender,
                    session_id,
                    false,
                    false,
                    true,
                    message.message_id
                );
            }
            if (message.message != "") {
                append_customer_message(
                    message.message,
                    message.sender_name,
                    message.time,
                    session_id,
                    message.message_id
                );
            }
        } 
        else if (message.sender == "Agent") {
            if (message.is_video_call_message) continue;
            let customer_last_appear_time = get_formatted_time(cust_last_updated_time);
            let message_time = get_formatted_time((message.time).split(" ")[0]);
            var flag_not_seen = true;
            if (customer_last_appear_time < message_time) {
                flag_not_seen = false;
            }
            if (message.attached_file_src != "") {
                append_file_to_agent(
                    message.attached_file_src,
                    message.message,
                    message.time,
                    message.sender_name,
                    message.sender,
                    session_id,
                    flag_not_seen,
                    true,
                    false,
                    message.message_id
                );
            } else {

                append_agent_message(
                    message.message,
                    sender_initial,
                    message.time,
                    session_id,
                    flag_not_seen,
                    true, 
                    message.message_id
                );
            }
        }
        else if (message.sender == "Bot") {
            append_agent_message(
                    message.message,
                    sender_initial,
                    message.time,
                    session_id,
                    false,
                    false,
                    message.message_id
            );
        } else if (message.sender == "System") {
            if(message.is_file_not_support_message) {
                continue;
            }
            if (message.is_video_call_message || message.is_cobrowsing_message || message.is_voice_call_message) {
                if (message.message_for == 'primary_agent') {
                    html = get_video_call_text_response(message.message);
                }
            } else if(message.message.includes("Customer details updated") || message.message.includes("Reinitiating Request Sent")){
                html = `<div class="live-chat-customer-details-update-message-div">
                            ${message.message}
                        </div>`;
            } else if(message.is_customer_report_message_notification) {
                html = get_report_message_notif_html(message.message);
            } else if(!message.is_customer_warning_message){
                html = get_system_text_response_html(
                    message.message,
                    message.time
                );
            }
            document.getElementById("style-2-" + session_id).innerHTML += html;
            html = ''
        }
    }

    //Appending supervisor/admin's reply messages
    for (var item = 0; item < message_history.length; item++) {
        let message = message_history[item];
        if (message.sender == "Supervisor") {
            if(message.attached_file_src != ''){
                append_supervisor_file_realtime(message.attached_file_src, session_id, message.file, message.message,  message.reply_message_id, message.time);
            } else if(message.message != '') {
                append_supervisor_message_realtime(message.message, session_id, message.sender_name, message.reply_message_id, message.time);
            }

        }
    }

    scroll_to_bottom_chat_view();
}

function get_formatted_time(time_string){
    var format_time = new Date();
    var hh_mm = time_string.split(':');
    format_time.setHours(parseInt(hh_mm[0]), parseInt(hh_mm[1]), 0)
    return format_time;
}

function get_customer_name() {
    return state.customer_name;
}

function set_customer_name(customer_name) {
    state.customer_name = customer_name;
}

function get_agent_name() {
    return state.agent_name;
}

function set_agent_name(agent_name) {
    state.agent_name = agent_name;
}

function get_active_url() {
    return state.active_url;
}

function set_active_url(active_url) {
    state.active_url = active_url;
}

function scroll_to_bottom_chat_view() {
    const session_id = get_session_id();
    var objDiv = document.getElementById(`style-2-${session_id}`);
    objDiv.scrollTop = objDiv.scrollHeight;
}

function reply_on_message_function(elem) {

    try{
        var message_bubble_container = elem.parentNode.parentNode;
        var reply_message_id = elem.parentNode.parentNode.parentNode.id;

        var query_elem = document.getElementById("admin-query");
        var reply_value = get_actual_message_details(reply_message_id);
        var actual_message = "";

        if(reply_value[3] != "") {
            document.getElementById("reply-message-value").innerHTML = reply_value[3].trim();
            actual_message = reply_value[3].trim();
        }
        else {
            document.getElementById("reply-message-value").innerHTML = reply_value[0].trim();
            actual_message = reply_value[0].trim();
        }
        $('.live-chat-admin-chat-history-modal-text-box-wrapper').css("display", "block");
        query_elem.setAttribute("reply_message", reply_message_id);
        query_elem.setAttribute("actual_message", actual_message);

        $("#chathistory-query-file").val("");
        $("#chathistory-query-file").css("height", "80px");
        reset_file_upload_modal_chathistory();

    } catch (err) {
        console.log(err);
        showToast("Cannot reply to this message!", 2000);
    }
    livechat_resize_chat_window();
}

function cancel_reply_on_message_function() {
    $('.live-chat-admin-chat-history-modal-text-box-wrapper').css("display", "none");
    document.getElementById("admin-query").value = "";
    livechat_resize_chat_window();

}

function livechat_resize_chat_window() {
    document.getElementById('live-chat-area-admin-section').style.height = (document.getElementById("livechat-history-message-box-container-div").clientHeight - document.getElementById("live-chat-admin-chat-history-modal-reply-text-box").clientHeight).toString() + "px ";
}

export {
    update_message_history_realtime_view,
    append_message_history_realtime_chat_view,
    get_customer_name,
    get_agent_name,
    scroll_to_bottom_chat_view,
    get_active_url,
    reply_on_message_function,
    cancel_reply_on_message_function,
    set_customer_name,
};