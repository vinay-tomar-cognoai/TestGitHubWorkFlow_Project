import axios from "axios";

import { 
    get_character_limit,
} from '../common'

import {
    custom_decrypt,
    EncryptVariable,
    getCsrfToken,
    showToast,
    validate_name,
    validate_phone_number,
    validate_email,
    is_valid_date,
    alphanumeric,
    encrypt_variable,
    get_params,
} from "../utils";

import { 
    get_session_id,
    get_chat_escalation_status,
    set_chat_escalation_status,
    check_chat_escalation_status,
    is_primary_agent, 
    remove_inactivity_timer
} from "../agent/console";

import {
    save_system_message,
    append_system_text_response,
    get_chat_data,
    return_time,
    get_customer_warning_system_text_html,
    get_customer_blacklisted_keywords,
    get_report_message_notif_html,
    set_customer_left_chat,
    has_customer_left_chat,
} from "../agent/chatbox";

import {
    send_message_to_socket,
} from "../agent/livechat_chat_socket";

import {
    send_message_to_guest_agent_socket,
    send_notification_to_customer,
} from "../agent/livechat_agent_socket";

import {
    get_translated_text,
} from "../agent/language_translation";

import {
    save_message_to_local,
} from "../agent/local_db";

import {
    set_voip_status,
} from "../agent/voip/voip";

import {
    force_end_cobrowsing,
    is_cobrowsing_ongoing,
    set_cobrowsing_status,
} from "../agent/cobrowsing/manage_cobrowsing";

import { end_voip_calling } from "../agent/voip/join_meeting_pip";

$(window).ready(function () {

    if (!window.location.pathname.includes('chat-escalation')) {
        return;
    }

    $("#chat-escalation-save-btn").on("click", function (e) {
        save_chat_escalation_data();
    });

    $("#blacklist-keyword-view-btn").on("click", function (e) {
        window.location.href = "/livechat/blacklisted-keyword?blacklist_for=agent"; 
    });

    $("#is-chat-escalation-matrix-enabled").on('change', function(e) {
        if(e.target.checked) {
            document.getElementById("chat-escalation-details-container").style.display = "block";
        } else {
            document.getElementById("chat-escalation-details-container").style.display = "none";
        }
    })

    $("#blacklist_reported_user_view_btn").on("click", function (e) {
        window.location.href = "/livechat/reported-users/"; 
    });

    $("#blacklist_blocked_user_view_btn").on("click", function (e) {
        window.location.href = "/livechat/blocked-users/"; 
    });

});

function save_chat_escalation_data() {

	let is_chat_escalation_matrix_enabled = document.getElementById("is-chat-escalation-matrix-enabled").checked;
	let is_agent_allowed_to_force_report = document.getElementById("is-agent-allowed-to-force-report").checked;
	let warning_text_for_customer = document.getElementById("warning-text-for-customer").value.trim();
	let end_chat_text_for_reported_customer = document.getElementById("end-chat-text-for-reported-customer").value.trim();

	const char_limit = get_character_limit();

    if(warning_text_for_customer == "") {
        showToast("Warning Text For The Customer cannot be empty.", 2000);
        return;
    }

    if(warning_text_for_customer.length > char_limit.large) {
        showToast("Warning Text For The Customer is too long.", 2000)
        return;
    }

    if (!alphanumeric(warning_text_for_customer)) {
        showToast("Kindly enter alphanumeric text only in Warning Text For The Customer", 2000);
        return;
    }

    if(end_chat_text_for_reported_customer == "") {
        showToast("End Chat Text For The Customer cannot be empty.", 2000);
        return;
    }

    if(end_chat_text_for_reported_customer.length > char_limit.large) {
        showToast("End Chat Text For The Customer is too long.", 2000)
        return;
    }

    if (!alphanumeric(end_chat_text_for_reported_customer)) {
        showToast("Kindly enter alphanumeric text only in End Chat Text For The Customer", 2000);
        return;
    }

    let json_string = {
    	is_chat_escalation_matrix_enabled: is_chat_escalation_matrix_enabled,
    	is_agent_allowed_to_force_report: is_agent_allowed_to_force_report,
    	warning_text_for_customer: warning_text_for_customer, 
    	end_chat_text_for_reported_customer: end_chat_text_for_reported_customer,
    };

    json_string = JSON.stringify(json_string);
    const params = get_params(json_string);
    let config = {
        headers: {
          'X-CSRFToken': getCsrfToken(),
        }
      }
    axios
        .post("/livechat/save-chat-escalation-data/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);
            
            if (response.status == 200) {
                showToast("Changes Saved successfully!", 3000);
                setTimeout(()=>{location.reload();}, 2000);
            } else {
                showToast(response.message, 3000);
            }
        })       
        .catch((err) => {
            console.log(err);
        });

}

export function chat_escalation_warn_user() {
    let session_id = get_session_id();

    if (has_customer_left_chat(session_id)) {
        showToast("Customer has left the chat. Cannot warn now.", 2000);
        return;
    }

    let json_string = {
        session_id: session_id,
    };

    json_string = JSON.stringify(json_string);
    const params = get_params(json_string);
    let config = {
        headers: {
          'X-CSRFToken': getCsrfToken(),
        }
      }
    axios
        .post("/livechat/chat-escalation-warn-user/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);
            
            if (response.status == 200) {

                hide_chat_escalation_notification();
                $("#report-user-btn").removeClass('disable-report-user-btn');

                let chat_escalation_status = get_chat_escalation_status();
                chat_escalation_status[session_id] = "warned";
                set_chat_escalation_status(chat_escalation_status);

                handle_chat_escalation_system_messages(response["warning_message"], response["message_to_customer"], "CUSTOMER_WARNING_MESSAGE", session_id);

                handle_chat_escalation_system_messages("Warning Text Sent to the User", "Warning Text Sent to the User", "CUSTOMER_WARNING_MESSAGE_NOTIF", session_id);

            } else {
                showToast(response.message, 3000);
            }
        })       
        .catch((err) => {
            console.log(err);
        });

}

export function chat_escalation_report_user() {
    // End Ongoing PIP Voice Call if any
    end_voip_calling();

    let session_id = get_session_id();

    if (has_customer_left_chat(session_id)) {
        $("#livechat-blacklist-report-modal").modal('hide');
        showToast("Customer has left the chat. Cannot report now.", 2000);
        return;
    }

    let json_string = {
        session_id: session_id,
    };

    json_string = JSON.stringify(json_string);
    const params = get_params(json_string);
    let config = {
        headers: {
          'X-CSRFToken': getCsrfToken(),
        }
      }

    axios
        .post("/livechat/chat-escalation-report-user/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);
            
            if (response.status == 200) {

                $("#livechat-blacklist-report-modal").modal('hide');
                hide_chat_escalation_notification();
                $("#report-user-btn").addClass('disable-report-user-btn');

                let chat_escalation_status = get_chat_escalation_status();
                chat_escalation_status[session_id] = "reported";
                set_chat_escalation_status(chat_escalation_status);

                if (is_cobrowsing_ongoing()) {
                    force_end_cobrowsing(false);
                }

                handle_chat_escalation_system_messages("Chat has been Reported", "Chat has been Reported", "CUSTOMER_REPORT_MESSAGE_NOTIF", session_id);

                handle_chat_escalation_system_messages(response["report_message"], response["message_to_customer"], "CUSTOMER_REPORT_MESSAGE", session_id);
                remove_inactivity_timer(session_id);

            } else {
                $("#livechat-blacklist-report-modal").modal('hide');
                showToast(response.message, 3000);
            }
        })       
        .catch((err) => {
            console.log(err);
        });    
}

async function handle_chat_escalation_system_messages(text_message, text_message_customer, event_type, session_id) {

    if(event_type == "CUSTOMER_REPORT_MESSAGE" && ["web", "android"].includes(get_chat_data().channel.toLowerCase())) {
        let sender = "chat_escalation_report";
        let sentence = JSON.stringify({
            message: JSON.stringify({
                text_message: text_message_customer,
                type: "text",
                channel: "",
                path: "",
                bot_id: get_chat_data().bot_id,
                session_id: session_id,
                text_agent_message: text_message,
            }),
            sender: sender,
        });

        send_notification_to_customer(sentence);
        return;
    }

    let message_id = save_system_message(text_message, event_type, session_id);

    let translated_text = text_message;
    if(localStorage.getItem(`is_translated-${session_id}`) == "true") {
        translated_text = await get_translated_text(message.message_id, text_message, session_id);
    }

    let is_customer_warning_message = false;
    let is_customer_report_message_notification = false;

    if(event_type == "CUSTOMER_WARNING_MESSAGE") {

        is_customer_warning_message = true;

    } else if (event_type == "CUSTOMER_REPORT_MESSAGE_NOTIF") {

        let html = get_report_message_notif_html(translated_text);
        $(`#style-2_${session_id}`).append(html);
        is_customer_report_message_notification = true;
        set_customer_left_chat(session_id, true);
        set_voip_status();
        set_cobrowsing_status();

    } else if (event_type == "CUSTOMER_WARNING_MESSAGE_NOTIF" || event_type == "CUSTOMER_REPORT_MESSAGE") {

        append_system_text_response(translated_text, return_time(), session_id);

    }

    let message = JSON.stringify({
        message: JSON.stringify({
            text_message: text_message,
            text_message_customer: text_message_customer,
            type: "text",
            channel: get_chat_data().channel,
            path: "",
            event_type: event_type,
            session_id: session_id,
            message_id: message_id,
            is_customer_warning_message: is_customer_warning_message,
            is_customer_report_message_notification: is_customer_report_message_notification,
        }),
        sender: "System",
    });

    send_message_to_socket(message);
    send_message_to_guest_agent_socket(message);

    save_message_to_local({
        message: text_message,
        sender: "System",
        sender_name: "system",
        session_id: session_id,
        message_id: message_id,
        is_customer_warning_message: is_customer_warning_message,
        is_customer_report_message_notification: is_customer_report_message_notification,
    })
}

export function hide_chat_escalation_notification() {
    $("#report-warn-user-div").css("display", "none");
    $("#warn-user-toast").css("display", "none");
    $("#report-user-toast").css("display", "none");
}

function find_common_words(list_1, list_2)
{
    list_1 = list_1.map(word => word.toLowerCase());  
    list_2 = list_2.map(word => word.toLowerCase());

    let words_set = new Set(list_2);
    return list_1.filter(word => words_set.has(word));
}

export function validate_customer_message(sentence) {
    
    let session_id = get_session_id();

    if(!window.IS_CHAT_ESCALATION_ENABLED || !is_primary_agent(session_id)) return false;

    let blacklisted_keywords = get_customer_blacklisted_keywords();
    let  sentence_list = sentence.trim().split(/\s+/);

    let common_words = find_common_words(blacklisted_keywords, sentence_list);

    return (common_words.length);
}

export function update_chat_escalation_status(session_id) {

    let chat_escalation_status_data = get_chat_escalation_status();

    if(chat_escalation_status_data[session_id]) {
        let chat_escalation_status = chat_escalation_status_data[session_id];

        if(chat_escalation_status == "safe") {
            chat_escalation_status = "to_be_warned";
        } else if(chat_escalation_status == "warned") {
            chat_escalation_status = "to_be_reported";
        }

        chat_escalation_status_data[session_id] = chat_escalation_status;

        set_chat_escalation_status(chat_escalation_status_data);

        check_chat_escalation_status();
    }
}

export function chat_escalation_ignore_notification(notification_type) {
    let session_id = get_session_id();

    let json_string = {
        session_id: session_id,
        notification_type: notification_type,
    };

    json_string = JSON.stringify(json_string);
    const params = get_params(json_string);
    let config = {
        headers: {
          'X-CSRFToken': getCsrfToken(),
        }
    }
    axios
        .post("/livechat/chat-escalation-ignore-notification/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);
            
            if (response.status == 200) {

                hide_chat_escalation_notification();
                let chat_escalation_status = get_chat_escalation_status();
                chat_escalation_status[session_id] = response["chat_escalation_status"];
                set_chat_escalation_status(chat_escalation_status);
                check_chat_escalation_status();

            } else {
                hide_chat_escalation_notification();
                showToast(response.message, 3000);
            }
        })       
        .catch((err) => {
            console.log(err);
        });    
}

