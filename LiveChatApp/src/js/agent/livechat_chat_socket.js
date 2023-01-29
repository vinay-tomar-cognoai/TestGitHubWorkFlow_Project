import {
    get_session_id,
    append_message_in_chat_icon,
    reset_inactivity_timer,
    dispose_chat,
    set_session_id,
    update_customer_list,
    go_to_chat,
    get_agent_username,
    remove_guest_agent_from_pending_list,
    get_unread_reply_message_count,
    set_unread_reply_message_count,
    get_unread_reply_message_ids,
    set_unread_reply_message_ids,
    is_primary_agent,
    get_voip_info,
    get_agent_name as get_primary_agent_name,
    set_cobrowsing_info,
    get_cobrowsing_info,
    set_cobrowse_session_id,
    remove_inactivity_timer,
    disable_input_fields_and_icons,
    show_custom_notification
} from "./console";

import {
    update_customer_last_ping,
    append_response_server,
    get_file_to_agent_html_sent_customer,
    scroll_to_bottom,
    mark_all_message_seen,
    update_customer_last_app_time,
    show_customer_typing_in_chat,
    append_system_text_response,
    customer_last_ping_greater_than_fifteen_sec,
    update_message_history,
    get_chat_data,
    return_time,
    set_customer_left_chat,
    check_and_update_message_diffrentiator,
    append_response_user,
    append_guest_agent_response,
    append_supervisor_message,
    append_supervisor_file,
    get_video_call_text_response,
    get_system_text_response_html,
    get_customer_warning_system_text_html,
    get_report_message_notif_html,
} from "./chatbox";

import { save_message_to_local } from "./local_db";

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
    update_message_history_realtime_view,
    append_message_history_realtime_chat_view,
    get_customer_name,
    get_agent_name,
    scroll_to_bottom_chat_view,
    get_active_url,
    set_customer_name,
} from "../admin/realtime_chat_view";

import {
    send_message_to_guest_agent_socket,
} from "./livechat_agent_socket"
import { handle_request_accepted_by_customer, handle_request_rejected_by_customer, remove_customer_request_on_end_chat, set_voip_status } from "./voip/voip";
import { handle_vc_request_accepted_by_customer, handle_vc_request_rejected_by_customer } from "./vc/livechat_vc";

import {
    get_reply_message_html,
} from "../admin/chat_history"

import {
    go_to_one_on_one_chat,
} from "../common/livechat_internal_chat_console";

import {
    custom_decrypt,
    EncryptVariable,
    encrypt_variable,
    is_mobile,
    getCsrfToken,
    showToast,
} from "../utils";

import {
    get_translated_text
} from "./language_translation";

import { set_cobrowsing_status, append_system_message as append_cobrowsing_system_message } from "./cobrowsing/manage_cobrowsing";

import { validate_customer_message, update_chat_escalation_status } from "../common/chat_escalation";

const state = {
    chat_socket: {
        socket: null,
        is_open: false,
        send_ping: null,
        websocket_timer: null,
        websocket_connection_check_timeout: null,
    },
    is_customer_there: null,
};

function create_websocket() {
    create_livechat_websocket();
    
    clearTimeout(state.chat_socket.websocket_connection_check_timeout);

    state.chat_socket.websocket_connection_check_timeout = setTimeout(() => {
        if(!state.chat_socket.is_open) {
            show_socket_connection_error();
        }
    }, 5000);

    state.chat_socket.websocket_timer = setInterval(function (e) {
        create_livechat_websocket();
    }, 1000);
}

function show_socket_connection_error() {
    show_custom_notification("Your chats might be loading slower than usual. We recommend that you reload the page, if the problem still persists.", 10000);
    disable_input_fields_and_icons(true, "Connection was not established, please reload the page");
}

function create_livechat_websocket() {
    const session_id = get_session_id();
    const chat_socket = state.chat_socket;
    if (chat_socket.is_open == false && chat_socket.socket == null) {
        chat_socket.socket = window.location.protocol == "http:" ? "ws://" : "wss://";
        chat_socket.socket += window.location.host + "/ws/" + session_id + "/agent/";
        chat_socket.socket = new WebSocket(chat_socket.socket);

        chat_socket.socket.onmessage = send_message_to_customer_socket;
        chat_socket.socket.onclose = close_livechat_socket;
        chat_socket.socket.onopen = open_livechat_socket;
        chat_socket.socket.onerror = check_and_close_weboscket;

        // clearInterval(chat_socket.websocket_timer);
    } else {
        clearInterval(chat_socket.websocket_timer);
    }
}

function send_message_to_customer_socket(e) {
    var data = JSON.parse(custom_decrypt(e.data));
    var message = JSON.parse(data["message"]);
    var sender = data["sender"];
    
    if (
        "event_type" in message &&
        message["event_type"] == "CUSTOMER_STILL_THERE" &&
        sender == "ping"
    ) {
        update_customer_last_ping();
    }

    const session_id = get_session_id();
    const chat_data = get_chat_data();
    const guest_session = localStorage.getItem(`guest_session-${session_id}`);

    let msg = {};
    msg.sender = "Customer";
    
    if (sender == "Customer") {

        handle_customer_message(message, chat_data, session_id, msg);
    } else if(sender == "Agent"){

        handle_agent_message(message, chat_data, session_id, msg, guest_session);
    } else if (sender == "System") {

        handle_system_message(message, chat_data, session_id, msg, guest_session);
    } else if (sender == "Supervisor") {

        handle_supervisor_message(message, session_id);

        check_and_display_supervisor_message_notification(message["reply_message_id"]);
    }
}

async function handle_customer_message(message, chat_data, session_id, msg) {
    
    if (message["text_message"] != "") {

        let text_message = message["text_message"];
        if(localStorage.getItem(`is_translated-${session_id}`) == "true") {
            text_message = await get_translated_text(message.message_id, text_message, session_id);
        }

        append_response_server(text_message, session_id, message["message_id"], message["language"]);

        save_message_to_local({
            message: message["text_message"],
            sender: "Customer",
            sender_name: chat_data.customer_name,
            session_id: session_id,
            message_id: message["message_id"],
            language: message.language,
        });

        msg.text_message = text_message;
        msg.is_attachment = "False";

        if(validate_customer_message(message["text_message"])) {
            update_chat_escalation_status(session_id);
        }
    }
    let path = message["path"];
    if (path != "") {
        let thumbnail_url = message["thumbnail_url"];

        let html = get_file_to_agent_html_sent_customer(
            path,
            chat_data.customer_name,
            thumbnail_url,
            false,
            message.message_id,
        );
        check_and_update_message_diffrentiator(session_id)
        $(`#style-2_${session_id}`).append(html);
        scroll_to_bottom();

        save_message_to_local({
            attached_file_src: path,
            sender: "Customer",
            sender_name: chat_data.customer_name,
            session_id: session_id,
            file: thumbnail_url,
            message_id: message.message_id,
            language: message.language,
        });

        let attachment_name = path.split("/");
        msg.attachment_name = attachment_name[attachment_name.length - 1];
        msg.is_attachment = "True";
    }

    reset_inactivity_timer(session_id, chat_data.bot_id, "customer");
    append_message_in_chat_icon(session_id, msg);
    check_for_message_seen_signal();
    mark_all_message_seen(session_id);
    update_customer_last_app_time(session_id);
    scroll_to_bottom();
    update_count();
}

async function handle_agent_message(message, chat_data, session_id, msg, guest_session) {

    if(get_agent_username() != message.sender_username) {

        var is_guest_session = false;
        if(guest_session == "false" && message.is_guest_agent_message == "true")
            is_guest_session = true;
        let path = message["path"];
        if (path != "") {

            let thumbnail_url = message["thumbnail"];

            let html = get_file_to_agent_html_sent_customer(
                path,
                message["agent_name"],
                thumbnail_url,
                true,
                message["message_id"]
            );
            check_and_update_message_diffrentiator(session_id);
            $(`#style-2_${session_id}`).append(html);
            scroll_to_bottom();

            save_message_to_local({
                attached_file_src: path,
                sender: "Agent",
                sender_name: message["agent_name"],
                session_id: session_id,
                file: thumbnail_url,
                message_id: message.message_id,
                is_guest_agent_message: is_guest_session,
                sender_username: message.sender_username,
                language: message.language,
            });

            let attachment_name = path.split("/");
            msg.attachment_name = attachment_name[attachment_name.length - 1];
            msg.is_attachment = "True";
        }
        if (message["text_message"] != "") {

            let text_message = message["text_message"];
            if(localStorage.getItem(`is_translated-${session_id}`) == "true") {
                text_message = await get_translated_text(message.message_id, text_message, session_id, message.sender_username);
            }

            append_guest_agent_response(text_message, session_id, message["agent_name"], message["language"], message["message_id"]);

            save_message_to_local({
                message: message["text_message"],
                sender: "Agent",
                sender_name: message["agent_name"],
                session_id: session_id,
                is_guest_agent_message: is_guest_session,
                sender_username: message.sender_username,
                message_id: message.message_id,
                language: message.language,
            });

            msg.text_message = text_message;
            msg.is_attachment = "False";
        }
        msg.is_guest_agent_message = true;
        reset_inactivity_timer(session_id, chat_data.bot_id, "agent");
        append_message_in_chat_icon(session_id, msg);
        scroll_to_bottom();
        update_count();
    }
}

async function handle_system_message(message, chat_data, session_id, msg, guest_session) {

    if (!('event_type' in message)) return;

    const event_type = message.event_type;

    if (event_type == "CUSTOMER_MESSAGE_SEEN") {

        update_count();
        mark_all_message_seen(session_id);
        update_customer_last_app_time(session_id);
    } else if (event_type == "CUSTOMER_TYPING") {

        show_customer_typing_in_chat();
        reset_inactivity_timer(session_id, chat_data.bot_id, "customer");
    } else if (event_type == "ENDBYUSER") {

        let text_message = message["text_message"];
        if(localStorage.getItem(`is_translated-${session_id}`) == "true") {
            text_message = await get_translated_text(message.message_id, text_message, session_id);
        }

        append_system_text_response(text_message, return_time(), session_id);

        let msg = {
            text_message: text_message,
            sender: "System",
            is_attachment: "False",
        };
        append_message_in_chat_icon(session_id, msg);

        set_customer_left_chat(session_id, true);
        remove_customer_request_on_end_chat(session_id);
        remove_inactivity_timer(session_id);
        localStorage.setItem(`customer_offline-${session_id}`, true);

        if (message.text_message == "Due to inactivity chat has ended") {
            dispose_chat(session_id, chat_data.bot_id, "session_inactivity");
        } else {
            dispose_chat(session_id, chat_data.bot_id, "user_terminates_chat");
        }

        save_message_to_local({
            message: message["text_message"],
            sender: "System",
            sender_name: "system",
            session_id: session_id,
            message_id: message.message_id,
        });

        try {
            document.getElementById("typing-text").innerHTML = "";
        } catch (err) {}
        clearInterval(state.is_customer_there);

        if(guest_session == "true"){
            update_customer_list();
            
            go_to_chat(get_session_id(), true);
        }

    } else if (event_type == "IS_CUSTOMER_TRANSCRIPT_REQUEST") {
        
        if (message["is_transcript_system_message"]) {
            let text_message = message["text_message"];
            if(localStorage.getItem(`is_translated-${session_id}`) == "true") {
                text_message = await get_translated_text(message.message_id, text_message, session_id);
            }

            append_system_text_response(text_message, return_time(), session_id);

            let msg = {
                text_message: text_message,
                sender: "System",
                is_attachment: "False",
            };
            save_message_to_local({
                message: message["text_message"],
                sender: "System",
                sender_name: "system",
                session_id: session_id,
                message_id: message.message_id,
            });
        
        }
        $("#transcript-button").addClass("disable-transcript-btn");
        localStorage.setItem(`transcript_option-${session_id}`, false);

    } else if (event_type == "GUEST_AGENT_JOINED"){

            let text_message = message["text_message"];
            if(localStorage.getItem(`is_translated-${session_id}`) == "true") {
                text_message = await get_translated_text(message.message_id, text_message, session_id);
            }

            remove_guest_agent_from_pending_list(message["agent_username"]);
            localStorage.removeItem(`guest_agent_timer-${message["agent_username"]}-${message["session_id"]}`);
            append_system_text_response(text_message, return_time(), session_id);
            save_message_to_local({
                message: message["text_message"],
                sender: "System",
                sender_name: "system",
                session_id: session_id,
                language: message.language,
                message_id: message.message_id,
            });

            if(message["agent_username"] != get_agent_username() && guest_session != "true") {
                document.getElementById("request-accepted-agent").innerHTML = "by " + message["agent_name"];

                $('#livechat-request-status-modal').modal('hide');
                $('#agent-request-accept-success-modal').modal('show');
                setTimeout(function() {
                    $('#agent-request-accept-success-modal').modal('hide')
                }, 5000);
            }
            document.getElementById("livechat-transfer-chat-btn").style.pointerEvents="none";
            document.getElementById("livechat-transfer-chat-btn").style.cursor="default";
            document.getElementById("livechat-transfer-chat-btn").style.opacity="0.3";
    } else if (event_type == "GUEST_AGENT_REJECT"){

            remove_guest_agent_from_pending_list(message["agent_username"]);
            localStorage.removeItem(`guest_agent_timer-${message["agent_username"]}-${message["session_id"]}`);
            document.getElementById("guest-agent-reject-message").innerHTML = message["agent_name"] + ' is not available currently. Please select a different agent';
            
            $('#livechat-request-status-modal').modal('hide');
            $('#agent-request-rejected-modal').modal('show');
            setTimeout(function() {
                $('#agent-request-rejected-modal').modal('hide')
            }, 5000);
            document.getElementById("livechat-add-agent-btn").style.pointerEvents="auto";
            document.getElementById("livechat-add-agent-btn").style.cursor="pointer";
            document.getElementById("livechat-add-agent-btn").style.opacity="1";
            document.getElementById("livechat-transfer-chat-btn").style.pointerEvents="auto";
            document.getElementById("livechat-transfer-chat-btn").style.cursor="pointer";
            document.getElementById("livechat-transfer-chat-btn").style.opacity="1";
    } else if (event_type == "GUEST_AGENT_EXIT"){

            let text_message = message["text_message"];
            if(localStorage.getItem(`is_translated-${session_id}`) == "true") {
                text_message = await get_translated_text(message.message_id, text_message, session_id);
            }

            append_system_text_response(text_message, return_time(), session_id);
            save_message_to_local({
                message: message["text_message"],
                sender: "System",
                sender_name: "system",
                session_id: session_id,
                language: message.language,
                message_id: message.message_id,
            });
            document.getElementById("livechat-add-agent-btn").style.pointerEvents="auto";
            document.getElementById("livechat-add-agent-btn").style.cursor="pointer";
            document.getElementById("livechat-add-agent-btn").style.opacity="1";
            document.getElementById("livechat-transfer-chat-btn").style.pointerEvents="auto";
            document.getElementById("livechat-transfer-chat-btn").style.cursor="pointer";
            document.getElementById("livechat-transfer-chat-btn").style.opacity="1";      
    } else if (event_type == "PRIMARY_AGENT_RESOLVED"){

        update_customer_list();

        go_to_chat(get_session_id(), true);
    } else if (event_type == "AGENT_TYPING" && (message.sender_username != get_agent_username())) {

        show_customer_typing_in_chat();

    } else if (event_type == "REQUEST_ACCEPTED" && is_primary_agent(session_id)) {

        handle_request_accepted_by_customer(true);
    } else if (event_type == "REQUEST_REJECTED" && is_primary_agent(session_id)) {

        handle_request_rejected_by_customer(true);
    } else if (event_type == "VC_REQUEST_ACCEPTED" && is_primary_agent(session_id)){
        handle_vc_request_accepted_by_customer(true);

        var message = JSON.stringify({
            message: JSON.stringify({
                event_type: "GUEST_AGENT_VC_LINK",
                session_id: get_session_id(),
                meeting_id: get_voip_info().meeting_id,
                primary_agent_name: get_primary_agent_name(),
            }),
            sender: "System",
        });

        send_message_to_guest_agent_socket(message);
    } else if (event_type == "VC_REQUEST_REJECTED" && is_primary_agent(session_id)){
        handle_vc_request_rejected_by_customer(true);
    } else if (event_type == "COBROWSING_REQUEST_ACCEPTED" && is_primary_agent(session_id)) {
        const cobrowsing_info = get_cobrowsing_info();
        set_cobrowsing_info({
            meeting_id: cobrowsing_info.meeting_id,
            session_id: cobrowsing_info.session_id,
            status: 'accepted',
        })
        set_cobrowsing_status();
        set_voip_status();
        append_cobrowsing_system_message('Cobrowsing Session Request Accepted', null, "primary_agent");

        if (is_mobile()) {
            $('#livechat_cobrowsing_request_accept_modal').modal('show');
        } else {
            $("#livechat_cobrowsing_request_accepted_modal").modal("show");
            
            setTimeout(() => {
                $("#livechat_cobrowsing_request_accepted_modal").modal("hide");
            }, 2000);
    
        }

    } else if (event_type == "COBROWSING_REQUEST_REJECTED" && is_primary_agent(session_id)) {
        const cobrowsing_info = get_cobrowsing_info();
        set_cobrowsing_info({
            meeting_id: cobrowsing_info.meeting_id,
            session_id: cobrowsing_info.session_id,
            status: 'rejected',
        })
        set_cobrowsing_status();
        set_voip_status();
        append_cobrowsing_system_message('Cobrowsing Session Request Rejected', null, "primary_agent");
        $('#livechat_voip_request_rejected_text').html(`${get_chat_data().customer_name} rejected the request for Cobrowsing.`)

        $('#livechat_voip_call_request_reject_modal').modal('show');
        
    } else if (event_type == "COBROWSE_SESSION_ID" && is_primary_agent(session_id)) {
        set_cobrowse_session_id(message.session_id)

    } else if (!is_primary_agent(session_id) && (event_type == "CUSTOMER_WARNING_MESSAGE" || event_type == "CUSTOMER_WARNING_MESSAGE_NOTIF" || event_type == "CUSTOMER_REPORT_MESSAGE" || event_type == "CUSTOMER_REPORT_MESSAGE_NOTIF")) {
        let text_message = message["text_message"];
        if(localStorage.getItem(`is_translated-${session_id}`) == "true") {
            text_message = await get_translated_text(message.message_id, text_message, session_id);
        }

        let is_customer_warning_message = false;
        let is_customer_report_message_notification = false;

        if(event_type == "CUSTOMER_WARNING_MESSAGE") {

            let html = get_customer_warning_system_text_html(text_message);
            $(`#style-2_${session_id}`).append(html);
            is_customer_warning_message = true;

        } else if (event_type == "CUSTOMER_REPORT_MESSAGE_NOTIF") {

            let html = get_report_message_notif_html(text_message);
            $(`#style-2_${session_id}`).append(html);
            is_customer_report_message_notification = true;

        } else if (event_type == "CUSTOMER_WARNING_MESSAGE_NOTIF" || event_type == "CUSTOMER_REPORT_MESSAGE") {

            append_system_text_response(text_message, return_time(), session_id);

        } 

        save_message_to_local({
            message: message["text_message"],
            sender: "System",
            sender_name: "system",
            session_id: session_id,
            language: message.language,
            message_id: message.message_id,
            is_customer_warning_message: is_customer_warning_message,
            is_customer_report_message_notification: is_customer_report_message_notification,
        });        
    }
}

async function handle_supervisor_message(message, session_id) {
        let path = message["path"];

        let text_message = message["text_message"];
        if(path != "" || message["text_message"] != "") {
            if(localStorage.getItem(`is_translated-${session_id}`) == "true") {
                text_message = await get_translated_text(message.message_id, text_message, session_id, message.sender_username);
            }
        }

        if (path != "") {

            append_supervisor_file(path, session_id, message["thumbnail"], text_message, message["reply_message_id"], message["sender_username"]);

            save_message_to_local({
                attached_file_src: path,
                sender: "Supervisor",
                sender_name: message["sender_name"],
                session_id: session_id,
                file: message["thumbnail"],
                message: message["text_message"],
                reply_message_id: message["reply_message_id"],
                sender_username: message["sender_username"],
                message_id: message["message_id"],
            });
        }
        else if (message["text_message"] != "") {

            append_supervisor_message(text_message, session_id, message["sender_name"], message["reply_message_id"], message["sender_username"], return_time());

            save_message_to_local({
                message: message["text_message"],
                sender: "Supervisor",
                sender_name: message["sender_name"],
                session_id: session_id,
                reply_message_id: message["reply_message_id"],
                sender_username: message["sender_username"],
                message_id: message["message_id"],
            });

        }
}

function close_livechat_socket(e) {
    state.chat_socket.is_open = false;
    state.chat_socket.socket = null;

    if (!e.wasClean) {
        console.log('close_livechat_socket: socket closed unexpectedly');
        console.log('creating websocket connection again');
        create_websocket();
    }
}

function open_livechat_socket(e) {
    disable_input_fields_and_icons(false, "Start with '/' to select a Canned Response");
    state.chat_socket.is_open = true;
    clearInterval(state.chat_socket.websocket_timer);
    state.chat_socket.send_ping = setInterval(send_ping_to_socket, 3000);
    state.is_customer_there = setInterval(customer_last_ping_greater_than_fifteen_sec, 6000);
    check_for_message_seen_signal();
    // update_message_history(false);
}

function close_chat_socket() {
    if (state.chat_socket.is_open == true && state.chat_socket.socket != null) {
        state.chat_socket.socket.close();
    }
}

function check_and_close_weboscket(e) {
    if (state.chat_socket.send_ping != null) {
        clearInterval(state.chat_socket.send_ping);
    }
    state.chat_socket.is_open = false;
    state.chat_socket.socket = null;
}

function send_ping_to_socket() {
    const chat_data = get_chat_data();
    if (state.chat_socket.is_open == true && state.chat_socket.socket != null) {
        var sentence = JSON.stringify({
            message: JSON.stringify({
                text_message: "",
                type: "text",
                channel: chat_data.channel,
                path: "",
                bot_id: chat_data.bot_id,
            }),
            sender: "ping",
        });
        sentence = encrypt_variable(sentence);
        try{
            state.chat_socket.socket.send(sentence);
        }catch(err){
            console.log("Unable to send ping into socket. May be socket is into closing state");
        }
    }
}

function send_message_to_socket(sentence) {
    if (state.chat_socket.is_open == true && state.chat_socket.socket != null) {
        sentence = encrypt_variable(sentence);
        state.chat_socket.socket.send(sentence);
    }
}

function check_for_message_seen_signal() {
    $(window).focus(function () {
        if (state.chat_socket.is_open == true && state.chat_socket.socket != null) {
            var sentence = JSON.stringify({
                message: JSON.stringify({
                    text_message: "",
                    type: "text",
                    channel: "Web",
                    path: "",
                    event_type: "AGENT_MESSAGE_SEEN",
                }),
                sender: "System",
            });
            sentence = encrypt_variable(sentence);
            state.chat_socket.socket.send(sentence);
        }
    });
}

function send_typing_message_to_customer() {
    if (state.chat_socket.is_open == true && state.chat_socket.socket != null) {
        var sentence = JSON.stringify({
            message: JSON.stringify({
                text_message: "",
                type: "text",
                channel: "Web",
                path: "",
                event_type: "AGENT_TYPING",
                sender_username: get_agent_username(),
            }),
            sender: "System",
        });
        sentence = encrypt_variable(sentence);
        state.chat_socket.socket.send(sentence);
    }
}

function update_count() {
    if (state.chat_socket.is_open == true && state.chat_socket.socket != null) {
        var sentence = JSON.stringify({
            message: JSON.stringify({
                text_message: "",
                type: "notification",
                channel: "Web",
                path: "",
                event_type: "DONT_SHOW_COUNT",
            }),
            sender: "agent",
        });
        sentence = encrypt_variable(sentence);
        state.chat_socket.socket.send(sentence);
    }
}
$(window).focus(function () {
    if (state.chat_socket.is_open == true && state.chat_socket.socket != null) {
        var sentence = JSON.stringify({
            message: JSON.stringify({
                text_message: "",
                type: "notification",
                channel: "Web",
                path: "",
                event_type: "DONT_SHOW_COUNT",
            }),
            sender: "agent",
        });
        sentence = encrypt_variable(sentence);
        state.chat_socket.socket.send(sentence);
    }
});

function clear_customer_there_interval() {
    clearInterval(state.is_customer_there);
}

function close_realtime_chat_socket() {
    if (state.chat_socket.is_open == true && state.chat_socket.socket != null) {
        state.chat_socket.socket.close();
    }    
}

function create_socket_ongoing_chat(session_id){

    const chat_socket = state.chat_socket;
    set_session_id(session_id);
    if (chat_socket.is_open == false && chat_socket.socket == null) {
        chat_socket.socket = window.location.protocol == "http:" ? "ws://" : "wss://";
        chat_socket.socket += window.location.host + "/ws/" + session_id + "/agent/";
        chat_socket.socket = new WebSocket(chat_socket.socket);

        chat_socket.socket.onmessage = send_message_realtime_chat_view;
        chat_socket.socket.onclose = close_livechat_socket;
        chat_socket.socket.onopen = open_livechat_socket_and_update_history;
        chat_socket.socket.onerror = check_and_close_weboscket;
    }
}

function send_message_realtime_chat_view(e){
    var data = JSON.parse(custom_decrypt(e.data));
    var message = JSON.parse(data["message"]);
    var sender = data["sender"];
    const session_id = get_session_id();
    const customer_name = get_customer_name();
    const agent_name = get_agent_name();
    const time = get_current_time();
    const active_url = get_active_url();
    if(sender == "Customer"){
        if (message["path"] != ""){
            append_file_to_agent(message["path"], message["text_message"], time, customer_name, sender, session_id, false, false, false, message["message_id"]);
        }
        else {
            const sender_initial = (customer_name).trim()[0].toUpperCase();
            append_customer_message(message["text_message"], customer_name, time, session_id, message["message_id"]);
        }
        mark_all_message_seen(session_id);
        scroll_to_bottom_chat_view();
    }
    else if(sender == "Agent" && message["is_guest_agent_message"] == "true"){
        if (message["path"] != ""){
            append_file_to_agent(message["path"], message["text_message"], time, message["agent_name"], sender, session_id, false, false, true, message["message_id"]);
        }
        if (message["text_message"] != ""){
            const sender_initial = (customer_name).trim()[0].toUpperCase();
            append_customer_message(message["text_message"], message["agent_name"], time, session_id, message["message_id"]);
        }
        mark_all_message_seen(session_id);
        scroll_to_bottom_chat_view();      
    }    
    else if(sender == "Agent"){
        if (message["path"] != ""){
            append_file_to_agent(message["path"], message["text_message"], time, message["agent_name"], sender, session_id, false, true, false, message["message_id"]);
        }
        else {
            const sender_initial = (message["agent_name"]).trim()[0].toUpperCase();
            append_agent_message(message["text_message"], sender_initial, time, session_id, false, true, message["message_id"]);
        }
        scroll_to_bottom_chat_view();
    }  
    else if(sender == "System"){
        if ("event_type" in message && (message["event_type"] == "CHAT_TRANSFERRED" || message["event_type"] == "ENDBYUSER") && "text_message" in message){
            append_system_message(active_url, message["text_message"], time, session_id);
            try{
            document.getElementById("chat-details-btn_"+session_id).click();
            }catch(err){} 
        }
        else if ("event_type" in message && message["event_type"] == "CUSTOMER_MESSAGE_SEEN") {
            mark_all_message_seen(session_id);
        }else if("text_message" in message && message["text_message"].includes("Customer details updated")){
            let html = `<div class="live-chat-customer-details-update-message-div">
                        ${message["text_message"]}
                    </div>`;
            document.getElementById("style-2-" + session_id).innerHTML += html;
        }else if("text_message" in message && message["text_message"].includes("Video Call")){
            let html = get_video_call_text_response(message["text_message"]);
            document.getElementById("style-2-" + session_id).innerHTML += html;
        }else if("text_message" in message && message["text_message"].includes("Voice Call")){
            let html = get_video_call_text_response(message["text_message"]);
            document.getElementById("style-2-" + session_id).innerHTML += html;
        }else if("text_message" in message && message["text_message"].includes("Customer Name: ")){
            set_customer_name(message.updated_name);
            let html = get_system_text_response_html(message["text_message"], return_time());
            document.getElementById("style-2-" + session_id).innerHTML += html;

        } else if("text_message" in message && message["event_type"] == "CUSTOMER_WARNING_MESSAGE") {

            let html = get_customer_warning_system_text_html(message["text_message"]);
            document.getElementById("style-2-" + session_id).innerHTML += html;

        } else if ("text_message" in message && message["event_type"] == "CUSTOMER_REPORT_MESSAGE_NOTIF") {

            let html = get_report_message_notif_html(message["text_message"]);
            document.getElementById("style-2-" + session_id).innerHTML += html;

        } else if ("text_message" in message && (message["event_type"] == "CUSTOMER_WARNING_MESSAGE_NOTIF" || message["event_type"] == "CUSTOMER_REPORT_MESSAGE")) {

            let html = get_system_text_response_html(message["text_message"], return_time());
            document.getElementById("style-2-" + session_id).innerHTML += html;
        }      

        scroll_to_bottom_chat_view();
    }
    else if (sender == "Supervisor") {
        let path = message["path"];
        if (path != "") {
            append_supervisor_file_realtime(path, session_id, message["thumbnail"], message["text_message"], message["reply_message_id"], time);
        }
        else if (message["text_message"] != "") {
            append_supervisor_message_realtime(message["text_message"], session_id, message["sender_name"], message["reply_message_id"], time);

        }
    }
}

function get_current_time() {
    var date = new Date();
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var ampm = hours >= 12 ? 'pm' : 'am';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    minutes = minutes < 10 ? '0' + minutes : minutes;
    var strTime = hours + ':' + minutes + ' ' + ampm;
    return strTime;
}

function open_livechat_socket_and_update_history(e) {
    state.chat_socket.is_open = true;
    state.chat_socket.send_ping = setInterval(send_ping_to_socket, 3000);
    state.is_customer_there = setInterval(customer_last_ping_greater_than_fifteen_sec, 6000);
    update_message_history_realtime_view();
}

function redirect_to_internal_chat(elem) {
    var sender_username = elem.getAttribute("sender");

    if(sender_username){
        var json_string = JSON.stringify({
            sender_username: sender_username, 
        }); 
        json_string = encrypt_variable(json_string);
        json_string = encodeURIComponent(json_string);

        var csrf_token = getCsrfToken();
        var xhttp = new XMLHttpRequest();
        var params = "json_string=" + json_string;
        xhttp.open("POST", "/livechat/check-reply-message-sender/", false);
        xhttp.setRequestHeader("X-CSRFToken", csrf_token);
        xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                let response = JSON.parse(this.responseText);
                response = custom_decrypt(response)
                response = JSON.parse(response);
                console.log(response);
                if (response.status_code == "200") {
                    if(response.redirect) {
                        window.location = "/livechat/internal-chat?webtoken="+response.supervisor_webtoken+"&username="+response.supervisor_username+"&name="+response.supervisor_name;
                    }
                }
            }
        };
        xhttp.send(params);
    } 
}

function check_and_display_supervisor_message_notification(message_id){
    var element = document.getElementById(message_id);
    if(!is_element_on_screen(element)) {
        var message_count = get_unread_reply_message_count();
        var message_ids = get_unread_reply_message_ids();

        message_ids.push(message_id);
        set_unread_reply_message_ids(message_ids);
        message_count += 1;
        set_unread_reply_message_count(message_count);

        document.getElementById("supervisor-comment-notif-"+get_session_id()).innerHTML = String(message_count) + " new comment from supervisor";
        $('#live-chat-new-message-reply-comment-notification-'+get_session_id()).css("display", "block");
    }
}

function is_element_on_screen(element)
{
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

function hide_message_reply_notification_function() {
    $('.live-chat-new-message-reply-comment-notification-div').css("display", "none");
    set_unread_reply_message_count(0);
    set_unread_reply_message_ids([]);
}

function go_to_specific_element() {
    
    var message_ids = get_unread_reply_message_ids();
    var myElement = document.getElementById(message_ids[message_ids.length-1]);
    var topPos = myElement.offsetTop;

    document.getElementById('style-2_'+get_session_id()).scrollTop = topPos;
    hide_message_reply_notification_function();
}

export {
    create_websocket,
    close_chat_socket,
    send_message_to_socket,
    clear_customer_there_interval,
    send_typing_message_to_customer,
    create_socket_ongoing_chat,
    redirect_to_internal_chat,
    hide_message_reply_notification_function,
    go_to_specific_element,
    close_realtime_chat_socket,
};
