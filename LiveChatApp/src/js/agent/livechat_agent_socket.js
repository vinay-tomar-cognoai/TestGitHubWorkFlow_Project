import {get_current_receiver_token, get_sender_websocket_token, get_is_group_chat, get_sender_username, append_last_message_time, go_to_one_on_one_chat, search_users, go_to_user_group, get_active_user_group, get_is_user_group, highlight_chat_based_chat_type, update_agent_last_seen, update_all_message_status, update_user_group_user_last_seen, update_user_group_user_last_seen_on_chat} from "../common/livechat_internal_chat_console";
import { get_total_group_list, get_active_group, update_group_chat_list } from "../admin/manage_group";
import {
    get_chat_data,
    mark_all_message_seen,
    update_customer_last_app_time,
    send_notification_for_new_message,
    append_system_text_response,
    append_response_server,
    return_time,
    get_file_to_agent_html_sent_customer,
    scroll_to_bottom,
    set_customer_left_chat,
    is_user_in_other_tab,
    update_unread_message_count,
    update_customer_last_ping,
    check_and_update_message_diffrentiator,
    save_system_message,
    update_message_history,
    remove_chat,
} from "./chatbox";

import {
    get_session_id,
    show_customer_typing_in_chat_icon,
    append_unread_msg_count_in_chat_icon,
    show_customer_status,
    append_message_in_chat_icon,
    is_notification_enabled,
    is_livechat_page,
    dispose_chat,
    reset_inactivity_timer,
    check_message_belongs_to_agent,
    get_theme_color,
    get_current_guest_sessions,
    set_current_guest_sessions,
    remove_guest_agent_from_pending_list,
    is_primary_agent,
    get_voip_info,
    get_agent_name,
    go_to_chat,
    set_cobrowsing_info,
    get_cobrowsing_info,
    set_cobrowse_session_id,
    append_message_in_chat_icon_new,
} from "./console";

import { save_message_to_local, update_customer_details_in_local } from './local_db'
import { cancel_meeting, connect_voip_call, handle_customer_voip_request, handle_meet_cancel_by_customer, handle_request_accepted_by_customer, handle_request_rejected_by_customer, remove_customer_request_on_end_chat, set_voip_status } from "./voip/voip";
import { handle_vc_request_accepted_by_customer, handle_vc_request_rejected_by_customer, handle_guest_agent_join_call_request } from "../../js/agent/vc/livechat_vc";
import { end_voip_calling } from "./voip/join_meeting_pip";

import { get_translated_text } from "./language_translation";
import { get_user_initial } from "../common/archive_customer";
import { custom_decrypt, getCsrfToken, get_params, get_user_group_member_count_html, is_mobile, encrypt_variable } from "../utils";
import { append_system_message, clear_session_end_timer, set_cobrowsing_status } from "./cobrowsing/manage_cobrowsing";
import { update_group_user_last_seen, update_group_user_last_seen_on_chat } from "../admin/group_chat_console";
import axios from "axios";
import { show_no_internet_notification } from "../common";

const state = {
    agent_socket: {
        socket: null,
        is_open: false,
        send_ping: null,
        token: "74a65650-2902-4d43-8eb4-d68fa8eeb4dd123",
    },
    channel: "",
    guest_agent_socket: {
        socket: null,
        is_open: false,
        send_ping: null,
        token: "",
        initial_msg: null,     
    },
    one_to_one_user_sessions: [],
    user_list: {},
    user_group_arr: [],
    user_group_map: {},
    all_user_groups: [],
};

function unset_every_one_to_one_chat() {

    for(var i = 0; i < state.one_to_one_user_sessions.length; i++) {

        var session_id = state.one_to_one_user_sessions[i]["websocket_token"];

        try {
            document
                .getElementById(session_id)
                .classList.remove("live-chat-active-customer-current");
        } catch (err) {}
    }
}

function set_one_to_one_user_list(user_list) {
    state.one_to_one_user_sessions = user_list;

    let html = '';
    state.one_to_one_user_sessions.forEach(user => {
        html += get_user_chat_icon_html(user, user.is_chat_started);
        state.user_list[user.websocket_token] = user;
    })

    if (html == '') {
        html += `
        <div class="groupchat-search-no-result-div" id="agent-search-no-result-div" style="display: block;">
            No user found
        </div> 
        `;
    } else {
        html += `
        <div class="groupchat-search-no-result-div" id="agent-search-no-result-div">
            No user found
        </div> 
        `;
    }

    $('#livechat_agent_contact_list').html(html);

    setTimeout(() => {
        add_chat_click_event(user_list);
    }, 300);
}

export function add_chat_click_event(user_list) {
    user_list.forEach(user => {
        const elem = document.getElementById(user.websocket_token);

        if (elem) {
            if (is_mobile()) {
                $(elem).unbind('touchend');
                $(elem).on("touchend", () => {
                    go_to_one_on_one_chat(user.websocket_token, user.username, user.full_name);
                });
            } else {
                $(elem).unbind('click');
                $(elem).on("click", () => {
                    go_to_one_on_one_chat(user.websocket_token, user.username, user.full_name);
                });
            }
        }
    })
}

export function get_user_chat_icon_html(user, is_chat_started) {
    let html = '';
    if (is_chat_started) {
        html += `
                <div class="live-chat-group-active-customer-item" id="${user.websocket_token}">
                    <div class="live-chat-active-group-details-wrapper">
                        <div class="live-chat-active-group-icon-div">
                            ${get_user_initial(user.full_name == '' ? user.username : user.full_name)}
                        </div>
                        <div class="live-chat-active-group-inside-details-wrapper">
                            <div class="live-chat-active-group-personname-date-wrapper">
                                <div class="live-chat-active-group-personname-text-div">
                                    <div class="live-chat-group-personname-div" id="username_${user.websocket_token}">${user.full_name == '' ? user.username : user.full_name}</div>
                                </div>
                                <div class="live-chat-active-group-date-time-div" id="livechat-last-message-time_${user.websocket_token}">${user.last_msg_time}</div>
                            </div>
                            <div class="live-chat-active-group-last-message-notif-wrapper">
                                <div class="live-chat-active-group-last-message-text-div" id="livechat-last-message-${user.websocket_token}">
                                    ${user.last_msg_text}
                                </div>
                                <div class="live-chat-active-group-message-notification-div" style="display: none;" id="livechat-unread-message-count-${user.websocket_token}"></div>
                                <div class="livechat-customer-typing-sidebar" id="customer-typing-${user.websocket_token}">Typing...</div>
                            </div>
                        </div>
                    </div>
                </div>
        `;
    }

    return html;
}

export function set_user_group_list(user_group_list) {
    let html = '';
    state.all_user_groups = user_group_list;
    const one_to_one_sessions = [], user_group_arr = [];
    user_group_list.forEach(user_group => {
        if (user_group.is_user_group) {
            html += get_user_group_chat_icon_html(user_group);
            state.user_group_map[user_group.id] = user_group;
            user_group_arr.push(user_group);
        } else {
            html += get_user_chat_icon_html(user_group, user_group.is_chat_started);
            state.user_list[user_group.websocket_token] = user_group;
            one_to_one_sessions.push(user_group);
        }
    })

    state.one_to_one_user_sessions = one_to_one_sessions;
    state.user_group_arr = user_group_arr;

    if (html == '') {
        html += `
        <div class="groupchat-search-no-result-div" id="agent-search-no-result-div" style="display: block;">
            No user found
        </div> 
        `;
    } else {
        html += `
        <div class="groupchat-search-no-result-div" id="agent-search-no-result-div">
            No user found
        </div> 
        `;
    }

    $('#livechat_agent_contact_list').html(html);

    setTimeout(() => {
        add_chat_click_event(state.one_to_one_user_sessions);

        const input_el = document.getElementById('livechat-groupchat-agent-search');

        if (input_el && input_el.value != '') search_users(input_el.value);

        add_user_group_click_event(state.user_group_arr);
    }, 300);
}

export function get_user_group_chat_icon_html(user_group) {
    let name = user_group.full_name;
    if (name == "") name = user_group.username;

    let html = '';
    html += `
            <div class="live-chat-group-active-customer-item" id="${user_group.id}">
                <div class="live-chat-active-group-details-wrapper">
                    <div class="live-chat-active-group-icon-div">
                        ${get_user_initial(user_group.full_name)}
                    </div>
                    <div class="live-chat-active-group-inside-details-wrapper">
                        <div class="live-chat-active-group-personname-date-wrapper">
                            <div class="live-chat-active-group-personname-text-div">
                                <div class="live-chat-group-personname-div" id="username_${user_group.id}"> ${user_group.full_name == '' ? user_group.username : user_group.full_name}</div>
                                <div id="livechat-user-group-count-indicator-${user_group.id}" class="livechat-user-group-member-count">
                                    ${get_user_group_member_count_html(user_group.id, user_group.members.length-1)}
                                </div>
                            </div>
                            <div class="live-chat-active-group-date-time-div" id="livechat-last-message-time_${user_group.id}">${user_group.last_message.time}</div>
                        </div>
                        <div class="live-chat-active-group-last-message-notif-wrapper">
                            <div class="live-chat-active-group-last-message-text-div" id="livechat-last-message-${user_group.id}">
                            ${user_group.last_message.text}
                            </div>
                            <div class="live-chat-active-group-message-notification-div" style="display: none;" id="livechat-unread-message-count-${user_group.id}"></div>
                            <div class="livechat-customer-typing-sidebar" id="customer-typing-${user_group.id}">Typing...</div>
                        </div>
                    </div>
                </div>
            </div>
        `;

    return html;
}


export function add_user_group_click_event(user_group_list) {
    user_group_list.forEach(user_group => {
        const elem = document.getElementById(user_group.id);

        if (elem) {
            if (is_mobile()) {
                $(elem).unbind('touchend');
                $(elem).on("touchend", () => {
                    go_to_user_group(user_group.id);
                });
            } else {
                $(elem).unbind('click');
                $(elem).on("click", () => {
                    go_to_user_group(user_group.id);
                });
            }
        }
    })
}


function check_and_update_notification(user_list, provided_group_list, user_group_list) {

    var positive_value = false;
    for(var i = 0; i < user_list.length; i++) {
        if (user_list[i].is_user_group) continue;

        let unread_message_count = localStorage.getItem(`unread_message_count-${user_list[i]["websocket_token"]}`);
        if(!unread_message_count) {

            unread_message_count = 0;
        }
        if(parseInt(unread_message_count)) {

            positive_value = true;
        }
        append_unread_msg_count_in_chat_icon(user_list[i]["websocket_token"], unread_message_count);
    }

    var group_list = provided_group_list;
    if(provided_group_list.length == 0) {

        group_list = get_total_group_list();
    }
    for(var i = 0; i < group_list.length; i++) {

        let unread_message_count = localStorage.getItem(`unread_message_count-${group_list[i]["id"]}`);
        if(!unread_message_count) {

            unread_message_count = 0;
        }
        if(parseInt(unread_message_count)) {

            positive_value = true;
        }
        append_unread_msg_count_in_chat_icon(group_list[i]["id"], unread_message_count);
    }

    for(var i = 0; i < user_group_list.length; i++) {
        if (!user_list[i].is_user_group) continue;

        let unread_message_count = localStorage.getItem(`unread_message_count-${user_group_list[i]["id"]}`);
        if(!unread_message_count) {

            unread_message_count = 0;
        }
        if(parseInt(unread_message_count)) {

            positive_value = true;
        }
        append_unread_msg_count_in_chat_icon(user_group_list[i]["id"], unread_message_count);
    }

    if(positive_value) {
        update_side_nav_group_chat_icon(1);
    } else {
        update_side_nav_group_chat_icon(0);
    }
}

function create_agent_socket() {

    const agent_socket = state.agent_socket;
    if (agent_socket.token == undefined || agent_socket.token == null) {
        return;
    }
    if (agent_socket.is_open == false) {
        agent_socket.socket = window.location.protocol == "http:" ? "ws://" : "wss://";
        agent_socket.socket += window.location.host + "/ws/" + agent_socket.token + "/agent/";
        agent_socket.socket = new WebSocket(agent_socket.socket);
        agent_socket.socket.onmessage = send_message_to_agent_socket;
        agent_socket.socket.onopen = function (e) {
            agent_socket.is_open = true;
            agent_socket.send_ping = setInterval(send_ping_to_agent_socket, 3000);
        };

        agent_socket.socket.onclose = function (e) {
            agent_socket.is_open = false;

            setTimeout(() => {
                create_agent_socket();
            }, 1000);
        };
    }

}

function update_agent_websocket_token(agent_websocket_token){
    return;
    if (agent_websocket_token) {

        state.agent_socket.token = agent_websocket_token;
        localStorage.setItem('agent_websocket_token', agent_websocket_token);
    } else {
        state.agent_socket.token = localStorage.getItem('agent_websocket_token')
    }
}

function check_message_belongs_current_account(websocket_token) {

    if(websocket_token == get_sender_websocket_token()) {

        return true;
    }
    var user_list = state.one_to_one_user_sessions
    for (var i = 0; i < user_list.length; i++) {

        if(user_list[i]["websocket_token"] == websocket_token) {

            return true;
        }
    }

    var group_list = get_total_group_list();
    for (var i = 0; i < group_list.length; i++) {

        if(group_list[i]["id"] == websocket_token) {
            const member = group_list[i].members.filter((value, index, arr) => {
                return value.name == get_sender_username();
            })

            if (member[0].is_removed || member[0].has_left) return false;
        
            return true;
        }
    }

    var user_group_list = get_user_group_list();
    if (user_group_list[websocket_token] != undefined) return true;

    return false;
}

function check_if_added_into_user_group (members, chat_belong_to) {
    if (chat_belong_to) {
        members.push(chat_belong_to);
    }

    return members.includes(get_sender_username());
}

async function send_message_to_agent_socket(e) {

    var data = JSON.parse(custom_decrypt(e.data));
    var message = JSON.parse(data["message"]);
    var sender = data["sender"];
    const session_id = get_session_id();
    const guest_session = localStorage.getItem(`guest_session-${message["session_id"]}`);
    const guest_session_status = localStorage.getItem(`guest_session_status-${message["session_id"]}`);
    
    if(sender == "Agent") {
        if(check_message_belongs_to_agent(message["session_id"])) {
            var is_guest_session = false;
            if(guest_session == "false" && message.is_guest_agent_message == "true")
                is_guest_session = true;
            if(session_id != message["session_id"]){
                const unread_message_count = update_unread_message_count(message["session_id"], false);
                if(message["path"] != ""){
                    let thumbnail_url = message["thumbnail"];

                    save_message_to_local({
                        attached_file_src: message["path"],
                        sender: "Agent",
                        sender_name: message["agent_name"],
                        session_id: message["session_id"],
                        file: thumbnail_url,
                        is_guest_agent_message: is_guest_session,
                        sender_username: message.sender_username,
                        message_id: message.message_id,
                        language: message.language,
                    });

                    if (is_livechat_page()) {
                        let html = get_file_to_agent_html_sent_customer(message["path"], message["agent_name"], thumbnail_url);
                       
                        check_and_update_message_diffrentiator(message["session_id"])
                        $(`#style-2_${message["session_id"]}`).append(html);
                        scroll_to_bottom();
                        append_unread_msg_count_in_chat_icon(message["session_id"], unread_message_count);
                        show_customer_status(unread_message_count, message["session_id"]);
                    }  
                }
                if (message["text_message"] != ""){

                    let text_message = message["text_message"];
                    if(localStorage.getItem(`is_translated-${message.session_id}`) == "true") {
                        text_message = await get_translated_text(message.message_id, text_message, message.session_id, message.sender_username);
                    }

                    save_message_to_local({
                        message: message["text_message"],
                        sender: "Agent",
                        sender_name: message["agent_name"],
                        session_id: message["session_id"],
                        is_guest_agent_message: is_guest_session,
                        sender_username: message.sender_username,
                        message_id: message.message_id,
                        language: message.language,
                    });

                    if (is_livechat_page()) {
                        append_response_server(text_message, message.session_id, message.agent_name, message.language);
                        append_unread_msg_count_in_chat_icon(message["session_id"], unread_message_count);
                        show_customer_status(unread_message_count, message["session_id"]);
                    }   
                }
            }
        }        
    }
    else if(sender == "System"){
        if(message["event_type"] == "GUEST_AGENT_JOIN_REQUEST") {
            if(!localStorage.getItem(`guest_agent_timer-${message["session_id"]}`)) {
                localStorage.setItem(`guest_agent_timer-${message["session_id"]}`, message["guest_agent_timer"]);
                var current_guest_sessions = get_current_guest_sessions();
                current_guest_sessions.push(message["session_id"]);
                set_current_guest_sessions(current_guest_sessions);
            }
        }
        if (!is_primary_agent(message.session_id) && message.event_type == 'CUSTOMER_DETAILS_UPDATED') {
            append_system_text_response(message.text_message, return_time(), message.session_id, message.message_id);
            save_message_to_local({
                message: message.text_message,
                sender: "System",
                sender_name: "system",
                session_id: message.session_id,
                message_id: message.message_id,
            })
            let msg = "Customer details updated";
            append_system_text_response(msg, return_time(), message.session_id, message.message_id);
            save_message_to_local({
                message: msg,
                sender: "System",
                sender_name: "system",
                session_id: message.session_id,
                message_id: message.message_id,
            })
            update_customer_details_in_local({
                name: message.updated_name,
                email: message.updated_email,
                phone: message.updated_phone,
                phone_country_code: message.phone_country_code,
                session_id: message.session_id,
            });
            remove_chat(message.session_id, false);
            go_to_chat(message.session_id, false);
        }

        if (!is_primary_agent(message.session_id) && message.event_type == 'GUEST_AGENT_VC_LINK') {
            handle_guest_agent_join_call_request(message.meeting_id, message.session_id, message.primary_agent_name);
        }
        
        if (is_primary_agent(message.session_id) && message.event_type == 'GUEST_AGENT_JOINED_VC') {
            const text = `${message.guest_agent_name} Joined the Video Call`
            let message_id = save_system_message(text, 'VIDEO_CALL', get_session_id());
            append_system_text_response(text, null, get_session_id(), message_id);
            save_message_to_local({
                message: text,
                sender: "System",
                sender_name: "system",
                session_id: get_session_id(),
                is_video_call_message: true,
                message_for: "primary_agent",
                message_id: message.message_id,
            })
        }

        if (is_primary_agent(message.session_id) && message.event_type == 'GUEST_AGENT_JOINED_CB') {
            const text = `${message.guest_agent_name} Joined the Cobrowsing Session`;
            append_system_message(text, message.session_id, "primary_agent");
        }

        if(check_message_belongs_to_agent(message["session_id"])) {
            if(session_id != message["session_id"]) {
                if(message["event_type"] == "GUEST_AGENT_JOINED" || message["event_type"] == "GUEST_AGENT_REJECT" || message["event_type"] == "GUEST_AGENT_EXIT" || message["event_type"] == "CUSTOMER_WARNING_MESSAGE" || message["event_type"] == "CUSTOMER_WARNING_MESSAGE_NOTIF" || message["event_type"] == "CUSTOMER_REPORT_MESSAGE" || message["event_type"] == "CUSTOMER_REPORT_MESSAGE_NOTIF"){

                    if(message["event_type"] == "GUEST_AGENT_JOINED" || message["event_type"] == "GUEST_AGENT_REJECT") {
                        remove_guest_agent_from_pending_list(message["agent_username"]);
                        localStorage.removeItem(`guest_agent_timer-${message["agent_username"]}-${message["session_id"]}`);
                    }

                    if(localStorage.getItem(`is_translated-${message.session_id}`) == "true") {
                        let text_message = await get_translated_text(message.message_id, text_message, message.session_id);
                    }

                    let is_customer_warning_message = false;
                    if(message["event_type"] == "CUSTOMER_WARNING_MESSAGE") {
                        is_customer_warning_message = message["is_customer_warning_message"];
                    }

                    let is_customer_report_message_notification = false;
                    if(message["event_type"] == "CUSTOMER_REPORT_MESSAGE_NOTIF") {
                        is_customer_report_message_notification = message["is_customer_report_message_notification"];
                    }  

                    const unread_message_count = update_unread_message_count(message["session_id"], false);
                    save_message_to_local({
                        message: message["text_message"],
                        sender: "System",
                        sender_name: "system",
                        session_id: message["session_id"],
                        language: message.language,
                        primary_agent_name: get_agent_name(),
                        message_id: message.message_id,
                        is_customer_warning_message: is_customer_warning_message,
                        is_customer_report_message_notification: is_customer_report_message_notification,
                    }); 

                    append_unread_msg_count_in_chat_icon(message["session_id"], unread_message_count);
                    show_customer_status(unread_message_count, message["session_id"]);  
                }
                else if(message["event_type"] == "GUEST_AGENT_JOIN_REQUEST"){
                    send_notification_for_new_message(message.text_message);
                }
            }
        }
    }
    else if (sender == "Supervisor") {
        if(check_message_belongs_to_agent(message["session_id"])) {
            if(session_id != message["session_id"]){
                if(message["path"] != "" || message["text_message"] != "") {
                    if(localStorage.getItem(`is_translated-${message.session_id}`) == "true") {
                        let text_message = await get_translated_text(message.message_id, message["text_message"], message.session_id, message.sender_username);
                    }
                }
                if(message["path"] != "") {
                    save_message_to_local({
                        message: message["text_message"],
                        sender: "Supervisor",
                        sender_name: message["sender_name"],
                        session_id: message["session_id"],
                        reply_message_id: message["reply_message_id"],
                        attached_file_src: message["path"],
                        file: message["thumbnail"],
                        sender_username: message["sender_username"],
                        message_id: message["message_id"],
                    });

                } else if (message["text_message"] != ""){
                    save_message_to_local({
                        message: message["text_message"],
                        sender: "Supervisor",
                        sender_name: message["sender_name"],
                        session_id: message["session_id"],
                        reply_message_id: message["reply_message_id"],
                        sender_username: message["sender_username"],
                        message_id: message["message_id"],
                    });

                }
            }   
        }
    }
    else if (sender == "Customer") {
        if (!check_message_belongs_to_agent(message.session_id)) return;
        
        if (is_message_seen_signal(message.event_type, message.session_id)) {
            return;
        }

        if (is_customer_typing_signal(message.event_type, session_id, message.session_id, message.bot_id)) {
            return;
        }

        if(is_customer_ping(message.event_type, session_id, message.session_id)) {
            return;
        }

        if (message.event_type == 'CUSTOMER_VOIP_REQUEST') {

            if (is_primary_agent(message.session_id)) {
                handle_customer_voip_request(message.session_id, message.sender_name);
                reset_inactivity_timer(message.session_id, message.bot_id, 'customer')
            }

            return;
        }

        if (message.event_type == 'CUSTOMER_VOIP_CONNECT') {
            if (is_primary_agent(message.session_id)) {
                connect_voip_call(message.sender_name);
            }

            return;
        }

        if (message.event_type == 'CANCEL_MEET') {
            if (is_primary_agent(message.session_id)) {
                handle_meet_cancel_by_customer(message.session_id);
            }

            return;
        }

        if (message.event_type == 'MEET_END') {
            if (is_primary_agent(message.session_id)) {
                end_voip_calling();
            }

            return;
        }

        if (message.event_type == 'SESSION_END_NOTIFICATION_RECEIVED') {
            if (is_primary_agent(message.session_id)) {
                clear_session_end_timer();
            }

            return;
        }

        if (is_notification_enabled() && (!is_livechat_page() || is_user_in_other_tab())) {
            send_notification_for_new_message(message.text_message);
        }
        
        const is_user_in_other_chat = session_id != message.session_id; 
        if (is_user_in_other_chat) {
            if (is_primary_agent(message.session_id)) {
                if (message.event_type == "REQUEST_REJECTED") {

                    handle_request_rejected_by_customer(true, message.sender_name);
                    return;
                } else if (message.event_type == "REQUEST_ACCEPTED") {
        
                    handle_request_accepted_by_customer(true, message.sender_name);
                    return;
                } else if (message.event_type == "VC_REQUEST_ACCEPTED") {

                    handle_vc_request_accepted_by_customer(true, message.sender_name);

                    var message = JSON.stringify({
                        message: JSON.stringify({
                            event_type: "GUEST_AGENT_VC_LINK",
                            session_id: message.session_id,
                            meeting_id: get_voip_info().meeting_id,
                        }),
                        sender: "System",
                    });
    
                    send_message_to_guest_agent_socket(message);
                    return;
                } else if (message.event_type == "VC_REQUEST_REJECTED") {

                    handle_vc_request_rejected_by_customer(true, message.sender_name);
                    return;
                }else if (message.event_type == "COBROWSING_REQUEST_ACCEPTED") {
                    const cobrowsing_info = get_cobrowsing_info();
                    set_cobrowsing_info({
                        meeting_id: cobrowsing_info.meeting_id,
                        session_id: cobrowsing_info.session_id,
                        status: 'accepted',
                    })
                    set_cobrowsing_status();
                    set_voip_status();
                    append_system_message('Cobrowsing Session Request Accepted', message.session_id, "primary_agent");
            
                } else if (message.event_type == "COBROWSING_REQUEST_REJECTED") {
                    const cobrowsing_info = get_cobrowsing_info();
                    set_cobrowsing_info({
                        meeting_id: cobrowsing_info.meeting_id,
                        session_id: cobrowsing_info.session_id,
                        status: 'rejected',
                    })
                    set_cobrowsing_status();
                    set_voip_status();
                    append_system_message('Cobrowsing Session Request Rejected', message.session_id, "primary_agent");
                    
                } else if (message.event_type == "COBROWSE_SESSION_ID") {
                    set_cobrowse_session_id(message.session_id)
                } else if(message.text_message == "The transcript will be sent over mail") {
                    if (is_livechat_page() && message.is_transcript_system_message) {
                        append_system_text_response(
                            text_message,
                            return_time(),
                            message.session_id,
                        );   
                    }
                    if(message.is_transcript_system_message) {
                    save_message_to_local({
                        message: message["text_message"],
                        sender: "System",
                        sender_name: "system",
                        session_id: message["session_id"],
                        message_id: message.message_id,
                    });
                    }
                    localStorage.setItem(`transcript_option-${message["session_id"]}`, false);
                    
                }
            }
    
            const unread_message_count = update_unread_message_count(message.session_id, false);

            if (is_livechat_page()) {
                append_unread_msg_count_in_chat_icon(message["session_id"], unread_message_count);
                show_customer_status(unread_message_count, message["session_id"]);

                let text_message = message["text_message"];
                if(localStorage.getItem(`is_translated-${message.session_id}`) == "true") {
                    text_message = await get_translated_text(message.message_id, text_message, message.session_id);
                }    

                let msg = {
                    text_message: text_message,
                    sender: "Customer",
                    is_attachment: "False",
                };
                if (message["path"] != "" && message["path"] != undefined) {
                    let attachment_name = message["path"].split("/");
                    msg.attachment_name = attachment_name[attachment_name.length - 1];
                    msg.is_attachment = "True";
                }
                append_message_in_chat_icon(message["session_id"], msg);
            }

            const is_ongoing_chat = localStorage.getItem(`ongoing_chat-${message["session_id"]}`);
            if (is_ongoing_chat == "true") {

                let text_message = message["text_message"];
                if(text_message != '') {
                    if(localStorage.getItem(`is_translated-${message.session_id}`) == "true") {
                        text_message = await get_translated_text(message.message_id, text_message, message.session_id);
                    }
                }

                if (message.text_message == "Customer left the chat") {
                    if (is_livechat_page()) {
                        append_system_text_response(
                            text_message,
                            return_time(),
                            message.session_id,
                        );
                        
                        set_customer_left_chat(message["session_id"], true);  
                        dispose_chat(message.session_id, message.bot_id, 'user_terminates_chat');
                        remove_customer_request_on_end_chat(message.session_id); 
                    }

                    localStorage.setItem(`customer_offline-${message["session_id"]}`, true);

                    save_message_to_local({
                        message: message["text_message"],
                        sender: "System",
                        sender_name: "system",
                        session_id: message["session_id"],
                        message_id: message.message_id,
                    });
                } else if(message.text_message == "Due to inactivity chat has ended") {
                    if (is_livechat_page()) {
                        append_system_text_response(
                            text_message,
                            return_time(),
                            message.session_id,
                        );
                        
                        set_customer_left_chat(message["session_id"], true);  
                        dispose_chat(message.session_id, message.bot_id, 'session_inactivity'); 
                    }

                    localStorage.setItem(`customer_offline-${message["session_id"]}`, true);

                    save_message_to_local({
                        message: message["text_message"],
                        sender: "System",
                        sender_name: "system",
                        session_id: message["session_id"],
                        message_id: message.message_id,
                    });
                }  else {
                    if (is_livechat_page()) {

                        if (message["text_message"] != "") {
                            append_response_server(text_message, message.session_id, message.message_id, message.language, message.sender_name);
                        } 
                        let path = message["path"];
                        if (path != "") {
                            let thumbnail_url = message["thumbnail_url"];
    
                            let html = get_file_to_agent_html_sent_customer(path, message["sender_name"], thumbnail_url);
                           
                            check_and_update_message_diffrentiator(message["session_id"])
                            $(`#style-2_${message["session_id"]}`).append(html);
                            scroll_to_bottom();
                        }
                    }

                    save_message_to_local({
                        attached_file_src: message["path"],
                        message: message["text_message"],
                        sender: "Customer",
                        sender_name: message["sender_name"],
                        session_id: message["session_id"],
                        file: message["thumbnail_url"],
                        message_id: message.message_id,
                        language: message.language,
                    });
                }
            } else {
                if (message.text_message == "Customer left the chat") {
                    if (is_livechat_page()) {
                        set_customer_left_chat(message.session_id, true);  
                        dispose_chat(message.session_id, message.bot_id, 'user_terminates_chat'); 
                        remove_customer_request_on_end_chat(message.session_id);
                    }
                    localStorage.setItem(`customer_offline-${message["session_id"]}`, true);
                } else if(message.text_message == "Due to inactivity chat has ended") {
                    if (is_livechat_page()) {
                        set_customer_left_chat(message["session_id"], true);  
                        dispose_chat(message.session_id, message.bot_id, 'session_inactivity'); 
                    }
                    localStorage.setItem(`customer_offline-${message["session_id"]}`, true);
                }
            }
        }
    } else if (sender == "OneToOneUser") {
        if ("event_type" in message && message.event_type == "LAST_SEEN") {
            update_agent_last_seen(message.sender_username, Date.parse(new Date()));
            update_all_message_status(message.sender_websocket_token, 1);
            update_group_user_last_seen(message.sender_username);
            update_user_group_user_last_seen(message.sender_username);
            return;
        }

        if(check_message_belongs_current_account(message["receiver_token"])) {
            if ("event_type" in message && message["event_type"] == "TYPING") {
                if (message.sender_username != get_sender_username() && get_current_receiver_token() != message["sender_websocket_token"]) {
                    show_customer_typing_in_chat_icon(message.sender_websocket_token);
                }
                return;
            }

            if ("event_type" in message && message.event_type == "LAST_SEEN_ON_CHAT") {

                if (get_sender_websocket_token() == message.receiver_token) {
                    update_all_message_status(message.sender_websocket_token, 2);
                } else if (message.is_group) {
                    update_group_user_last_seen_on_chat(message.sender_username, message.receiver_token);
                } else if (message.is_user_group) {
                    update_user_group_user_last_seen_on_chat(message.sender_username, message.receiver_token);
                }
                return;
            }
    
            let msg = {
                text_message: message["text_message"],
                sender: "Customer",
                is_attachment: "False",
            };
            let attachment_name = '';
            if (message["path"] != "" && message["path"] != undefined) {
                attachment_name = message["path"].split("/");
                attachment_name = attachment_name[attachment_name.length - 1];
                msg.attachment_name = attachment_name;
                msg.is_attachment = "True";
            }

            if(get_sender_websocket_token() == message.sender_websocket_token) {
                append_message_in_chat_icon(message.receiver_token, msg);
                append_last_message_time(message.receiver_token, return_time());
                return;
            } else {
                append_message_in_chat_icon(message["sender_websocket_token"], msg);
                append_last_message_time(message.receiver_token, return_time());
            }

            if(get_current_receiver_token() != message["sender_websocket_token"]) {

                state.global_notification_bool = false;
                update_user_chat_info(message.sender_websocket_token, message.text_message, attachment_name, return_time());
                search_users('');
                const unread_message_count = update_unread_message_count(message["sender_websocket_token"], true);
                append_unread_msg_count_in_chat_icon(message["sender_websocket_token"], unread_message_count);
                update_side_nav_group_chat_icon(1);
            }
        } else if ('added_members' in message && check_if_added_into_user_group(message.added_members, message.chat_belong_to)) {
            let receiver_token = get_current_receiver_token();
            if (message.chat_belong_to == get_sender_username() && !get_is_user_group() && !get_is_group_chat()) {
                if (receiver_token == message.sender_websocket_token) {
    
                    update_group_chat_list({
                        is_member_removed: false,
                        is_member_added: true,
                        user_group_id: message.receiver_token,
                    });        
                }
            } else {
                update_group_chat_list({
                    is_member_removed: false,
                    is_member_added: false,
                    user_group_id: null,
                });    
            }
        }
    } else if (sender == "GroupUser") {

        if(check_message_belongs_current_account(message["receiver_token"])){
            if ("event_type" in message && message["event_type"] == "TYPING") {
                if (message.sender_username != get_sender_username() && (get_active_group().id != message["receiver_token"]) || get_is_group_chat() == false) {
                    show_customer_typing_in_chat_icon(message.receiver_token, message.sender_name);
                }
                return;
            }

            if (message.sender_name.toLowerCase() == 'system' && (message.text_message.includes('changed the') || message.text_message.includes('removed'))) {
                message.text_message = message.text_message.replace(' ' + get_sender_username() + ' ', ' you ');
                
                if (message.sender_username == get_sender_username()) {
                    message.text_message = 'You ' + message.text_message;
                } else {
                    message.text_message = message.sender_username + ' ' + message.text_message;
                }
            }

            let msg = {
                text_message: message["text_message"],
                sender: message.sender_name,
                is_attachment: "False",
            };
            if (message["path"] != "" && message["path"] != undefined) {
                let attachment_name = message["path"].split("/");
                msg.attachment_name = attachment_name[attachment_name.length - 1];
                msg.is_attachment = "True";
            }

            append_message_in_chat_icon_new(message["sender_websocket_token"], msg, true);
            append_last_message_time(message.sender_websocket_token, return_time());

            if ('removed_user' in message || 'left_chat' in message) {
                const removed_member = message.removed_user;
                if (removed_member == get_sender_username()) {
                    update_group_chat_list({
                        is_member_removed: true,
                        is_member_added: false,
                        user_group_id: null,
                    });
                } else {
                    update_group_chat_list({
                        is_member_removed: false,
                        is_member_added: false,
                        user_group_id: null,
                    });
                }

                if (get_is_group_chat() && get_sender_username() != message.sender_username) {
                    const active_group = get_active_group();

                    if ('left_chat' in message && active_group.id == message.sender_websocket_token) {
                        append_system_text_response(message.text_message, return_time(), message.sender_websocket_token);
                    }
                }
            }

            if((get_active_group().id != message["receiver_token"]) || get_is_group_chat() == false) {

                state.global_notification_bool = false;
                const unread_message_count = update_unread_message_count(message["receiver_token"], true);
                append_unread_msg_count_in_chat_icon(message["receiver_token"], unread_message_count);
                update_side_nav_group_chat_icon(1);
            }
        } 
    } else if (sender == "UserGroup") {

        if(check_message_belongs_current_account(message["receiver_token"])) {
            if ("event_type" in message && message["event_type"] == "TYPING") {
                if (message.sender_username != get_sender_username() && (get_active_user_group().id != message["receiver_token"]) || get_is_user_group() == false) {
                    show_customer_typing_in_chat_icon(message.receiver_token, message.sender_name);
                }
                return;
            }

            let msg = {
                text_message: message["text_message"],
                sender: message.sender_name,
                is_attachment: "False",
            };
            if (message["path"] != "" && message["path"] != undefined) {
                let attachment_name = message["path"].split("/");
                msg.attachment_name = attachment_name[attachment_name.length - 1];
                msg.is_attachment = "True";
            }

            append_message_in_chat_icon(message.receiver_token, msg, true);
            append_last_message_time(message.receiver_token, return_time());

            if((get_active_user_group().id != message["receiver_token"]) || get_is_user_group() == false) {

                state.global_notification_bool = false;
                const unread_message_count = update_unread_message_count(message["receiver_token"], true);
                append_unread_msg_count_in_chat_icon(message["receiver_token"], unread_message_count);
                update_side_nav_group_chat_icon(1);
            }

            if ('added_members' in message && message.sender_username != get_sender_username()) {
                if (get_is_user_group() && get_active_user_group().id == message.receiver_token) {
                    update_group_chat_list({
                        is_member_removed: false,
                        is_member_added: true,
                        user_group_id: null,
                    });                    
                } else {
                    update_group_chat_list({
                        is_member_removed: false,
                        is_member_added: false,
                        user_group_id: null,
                    });
                }
            }

        } else if ('added_members' in message && check_if_added_into_user_group(message.added_members)) {
            update_group_chat_list({
                is_member_removed: false,
                is_member_added: false,
                user_group_id: null,
            });
        }
    } 
}

function send_ping_to_agent_socket() {

    const agent_socket = state.agent_socket;
    try{
        if (agent_socket.socket.readyState == 2 || agent_socket.socket.readyState == 3) {

            show_no_internet_notification();
        }
    }catch(err){
        console.log("Socket ready state not 2 or 3 because of " + err);
    }
    const chat_data = get_chat_data();
    if (agent_socket.is_open == true && agent_socket.socket != null) {
        var sentence = JSON.stringify({
            message: JSON.stringify({
                text_message: "",
                type: "text",
                channel: state.channel,
                path: "",
                bot_id: chat_data.bot_id,
            }),
            sender: "ping",
        });
        sentence = encrypt_variable(sentence);
        try{
            agent_socket.socket.send(sentence);
        }catch (err) {
            console.log("Error in sending data via socket");
        }

        if (agent_socket.socket.readyState == 2 || agent_socket.socket.readyState == 3) {

            show_no_internet_notification();
        }
    }
}

function send_notification_to_customer(sentence) {
    const agent_socket = state.agent_socket;
    if (agent_socket.is_open == true && agent_socket.socket != null) {
        sentence = encrypt_variable(sentence);
        agent_socket.socket.send(sentence);
    }
} 

function is_message_seen_signal (event_type, session_id) {
    if (event_type == "CUSTOMER_MESSAGE_SEEN") {
        if (is_livechat_page()) {
            mark_all_message_seen(session_id);
        }
        
        update_customer_last_app_time(session_id);
        
        return true;
    }

    return false;
}

function is_customer_typing_signal (event_type, session_id, message_session_id, bot_id) {
    if (event_type == "CUSTOMER_TYPING") {
        if (is_livechat_page() && session_id != message_session_id) {
            show_customer_typing_in_chat_icon(message_session_id);
            reset_inactivity_timer(session_id, bot_id, 'customer')
        }
        
        return true;
    }

    return false;
}

function is_customer_ping (event_type, session_id, message_session_id) {
    if (event_type == "CUSTOMER_STILL_THERE") {
        if (is_livechat_page() && session_id != message_session_id) {
            update_customer_last_ping(message_session_id);
        }
        
        return true;
    }

    return false;
}

function send_message_to_guest_agent_socket(sentence){
    if (state.agent_socket.is_open == true && state.agent_socket.socket != null) {
        sentence = encrypt_variable(sentence);
        state.agent_socket.socket.send(sentence);
    }
}

function append_unread_msg_count_in_neetoone_chat_icon(session_id, count) {
    const elem = document.getElementById(`livechat-unread-message-count-${session_id}`);
    try {
        if (count == 0) {
            elem.style.display = "none";
        } else {
            elem.innerHTML = count;
            elem.style.display = "flex";
        }
    } catch (err) {
        console.log(err);
    }
    
}


function set_zero_unread_message_count(session_id) {

    let unread_message_count = localStorage.getItem(`unread_message_count-${session_id}`);

    if(!unread_message_count) {
        unread_message_count = 0;
    }

    // if (unread_message_count) {
    //     let unread_threads = localStorage.getItem("unread_threads_internal_chat");
    //     unread_threads = parseInt(unread_threads) - 1;
    //     unread_threads = Math.max(unread_threads, 0);

    //     if(isNaN(unread_threads)) unread_threads = 0;
        
    //     localStorage.setItem("unread_threads_internal_chat", unread_threads);

    //     update_document_title(unread_threads);
    // }

    unread_message_count = 0
    localStorage.setItem(`unread_message_count-${session_id}`, unread_message_count);
    check_and_update_notification(state.one_to_one_user_sessions, [], []);
    return unread_message_count;
}

function update_side_nav_group_chat_icon(unread_message_count) {
    const theme_color = get_theme_color();

    if(unread_message_count) {

        if (window.location.href.includes('internal-chat')) {

            var html = `<svg width="22" height="22" viewBox="0 0 33 33" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M9.94786 18.8901L5 22.8901V6.89014C5 6.62492 5.10536 6.37057 5.29289 6.18303C5.48043 5.99549 5.73478 5.89014 6 5.89014H22C22.2652 5.89014 22.5196 5.99549 22.7071 6.18303C22.8946 6.37057 23 6.62492 23 6.89014V17.8901C23 18.1554 22.8946 18.4097 22.7071 18.5972C22.5196 18.7848 22.2652 18.8901 22 18.8901H9.94786Z" stroke="${theme_color.one}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M11 18.8901V23.8901C11 24.1554 11.1054 24.4097 11.2929 24.5972C11.4804 24.7848 11.7348 24.8901 12 24.8901H24.0521L29 28.8901V12.8901C29 12.6249 28.8946 12.3706 28.7071 12.183C28.5196 11.9955 28.2652 11.8901 28 11.8901H23" stroke="${theme_color.one}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <circle cx="29" cy="4.89001" r="4" fill="#E53E3E"/>
                        </svg>

                    <span style="padding-left: 9px; color: ${theme_color.one}" id="sidebarlink">Group Chat</span></a>`

            document.getElementById("internal-chat").innerHTML = html;
        } else {

            var html = `<svg width="22" height="22" viewBox="0 0 32 33" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M9.94786 18.8901L5 22.8901V6.89014C5 6.62492 5.10536 6.37057 5.29289 6.18303C5.48043 5.99549 5.73478 5.89014 6 5.89014H22C22.2652 5.89014 22.5196 5.99549 22.7071 6.18303C22.8946 6.37057 23 6.62492 23 6.89014V17.8901C23 18.1554 22.8946 18.4097 22.7071 18.5972C22.5196 18.7848 22.2652 18.8901 22 18.8901H9.94786Z" stroke="#4D4D4D" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M11 18.8901V23.8901C11 24.1554 11.1054 24.4097 11.2929 24.5972C11.4804 24.7848 11.7348 24.8901 12 24.8901H24.0521L29 28.8901V12.8901C29 12.6249 28.8946 12.3706 28.7071 12.183C28.5196 11.9955 28.2652 11.8901 28 11.8901H23" stroke="#4D4D4D" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <circle cx="29" cy="4.89001" r="4" fill="#E53E3E"/>
                        </svg>
                        <span style="padding-left: 9px; color: #858796;" id="sidebarlink">Group Chat</span></a>`

            document.getElementById("internal-chat").innerHTML = html;
        }
    } else {

        if (window.location.href.includes('internal-chat')) {

            var html = `<svg width="22" height="22" viewBox="0 0 32 33" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M8.94792 18.7786L4.00006 22.7786V6.77863C4.00006 6.51341 4.10542 6.25906 4.29295 6.07152C4.48049 5.88398 4.73484 5.77863 5.00006 5.77863H21.0001C21.2653 5.77863 21.5196 5.88398 21.7072 6.07152C21.8947 6.25906 22.0001 6.51341 22.0001 6.77863V17.7786C22.0001 18.0438 21.8947 18.2982 21.7072 18.4857C21.5196 18.6733 21.2653 18.7786 21.0001 18.7786H8.94792Z" stroke="${theme_color.one}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
                            <path d="M10.0001 18.7786V23.7786C10.0001 24.0438 10.1054 24.2982 10.293 24.4857C10.4805 24.6733 10.7348 24.7786 11.0001 24.7786H23.0522L28.0001 28.7786V12.7786C28.0001 12.5134 27.8947 12.2591 27.7072 12.0715C27.5196 11.884 27.2653 11.7786 27.0001 11.7786H22.0001" stroke="${theme_color.one}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
                        </svg>

                    <span style="padding-left: 9px; color: ${theme_color.one}" id="sidebarlink">Group Chat</span></a>`

            document.getElementById("internal-chat").innerHTML = html;
        } else {

            var html = `<svg width="22" height="22" viewBox="0 0 32 33" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M9.94786 17.8901L5 21.8901V5.89014C5 5.62492 5.10536 5.37057 5.29289 5.18303C5.48043 4.99549 5.73478 4.89014 6 4.89014H22C22.2652 4.89014 22.5196 4.99549 22.7071 5.18303C22.8946 5.37057 23 5.62492 23 5.89014V16.8901C23 17.1554 22.8946 17.4097 22.7071 17.5972C22.5196 17.7848 22.2652 17.8901 22 17.8901H9.94786Z" stroke="#4D4D4D" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M11 17.8901V22.8901C11 23.1554 11.1054 23.4097 11.2929 23.5972C11.4804 23.7848 11.7348 23.8901 12 23.8901H24.0521L29 27.8901V11.8901C29 11.6249 28.8946 11.3706 28.7071 11.183C28.5196 10.9955 28.2652 10.8901 28 10.8901H23" stroke="#4D4D4D" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>

                        <span style="padding-left: 9px; color: #858796;" id="sidebarlink">Group Chat</span></a>`

            document.getElementById("internal-chat").innerHTML = html;
        }
    }
}

export function update_user_chat_info(token, message, filename, message_time) {
    const user = state.user_list[token];

    user.last_msg_text = message;
    user.filename = filename;
    user.last_msg_time = message_time;
    user.is_chat_started = true;
}

export function set_is_chat_started(token) {
    return new Promise((res, rej) => {
        const user = state.user_list[token];

        if (user.is_chat_started) res();

        user.is_chat_started = true;

        const config = {
            headers: {
            'X-CSRFToken': getCsrfToken(),
            }
        }

        const json_string = JSON.stringify({
            is_user_group: false,
            username: user.username,
        });

        const params = get_params(json_string);

        axios
            .post('/livechat/set-chat-started/', params, config)
            .then (response => {
                response = custom_decrypt(response.data);
                response = JSON.parse(response);

                if (response.status == 200) {
                    console.log('success');
                    res();
                }
            })
    })
}

export function set_chat_started_in_user_group (group_id) {
    return new Promise((res, rej) => {

        const config = {
            headers: {
            'X-CSRFToken': getCsrfToken(),
            }
        }

        const json_string = JSON.stringify({
            is_user_group: true,
            user_group_id: group_id,
        });

        const params = get_params(json_string);

        axios
            .post('/livechat/set-chat-started/', params, config)
            .then (response => {
                response = custom_decrypt(response.data);
                response = JSON.parse(response);

                if (response.status == 200) {
                    console.log('success');
                    res();
                }
            })
    })   
}

export function get_user_list() {
    return state.user_list;
}

export function get_user_sessions() {
    return state.one_to_one_user_sessions;
}

export function get_user_group_list() {
    return state.user_group_map;
}

export function get_user_group_arr() {
    return state.user_group_arr;
}

export function get_all_user_groups() {
    return state.all_user_groups;
}

export { 
    create_agent_socket ,
    update_agent_websocket_token,
    send_notification_to_customer,
    send_message_to_guest_agent_socket,
    send_message_to_agent_socket,
    set_zero_unread_message_count,
    unset_every_one_to_one_chat,
    check_and_update_notification,
    set_one_to_one_user_list,
    // append_unread_msg_count_in_onetoone_chat_icon,
};
