import { update_group_chat_list } from "../admin/manage_group";
import { append_system_text_response, return_time, show_customer_typing_in_chat, get_attachment_html } from "../agent/chatbox";
import { send_message_to_guest_agent_socket, update_user_chat_info } from "../agent/livechat_agent_socket"
import {
    append_internal_chat_response_server,
    append_internal_media_response_server,
    get_current_receiver_token,
    get_current_receiver_username,
    get_internal_chat_sender_name,
    get_sender_username,
    internal_chat_scroll_to_bottom,
    get_reply_response_user_html,
    get_is_group_chat,
    get_is_user_group,
} from "./livechat_internal_chat_console";
import { encrypt_variable, custom_decrypt } from "../utils";

const state = {
    chat_socket: {
        socket: null,
        is_open: false,
        send_ping: null,
        websocket_timer: null,
    },
    sender_websocket_token: window.SENDER_WEBSOCKET_TOKEN,
};

function set_sender_websocket_token(sender_websocket_token) {
    state.sender_websocket_token = sender_websocket_token;
}

function get_sender_websocket_token() {
    return state.sender_websocket_token;
}

function create_websocket(websocket_token, is_group) {
    create_one_to_one_chat_socket(websocket_token, is_group);
    state.chat_socket.websocket_timer = setInterval(function (e) {
        create_one_to_one_chat_socket(websocket_token, is_group);
    }, 1000);
}

function create_one_to_one_chat_socket(websocket_token, is_group) {
    const chat_socket = state.chat_socket;

    if (chat_socket.is_open == false && chat_socket.socket == null) {
        let web_socket_url;
        if (is_group) {
            web_socket_url = websocket_token;
        } else {
            const sender_websocket_token = get_sender_websocket_token();

            web_socket_url = [sender_websocket_token, websocket_token];
            web_socket_url.sort();
            web_socket_url = web_socket_url[0] + "-" + web_socket_url[1];
        }

        chat_socket.socket =
            window.location.protocol == "http:" ? "ws://" : "wss://";
        chat_socket.socket +=
            window.location.host + "/ws/" + web_socket_url + "/user/";
        chat_socket.socket = new WebSocket(chat_socket.socket);

        chat_socket.socket.onmessage = send_message_to_internal_chat_user;
        chat_socket.socket.onclose = close_internal_chat_socket;
        chat_socket.socket.onopen = open_livechat_socket;
        chat_socket.socket.onerror = check_and_close_internal_websocket;

        clearInterval(state.chat_socket.websocket_timer);

        console.log("Socket created succesfully");
    } else {
        clearInterval(state.chat_socket.websocket_timer);
    }
}

function send_message_to_internal_chat_user(e) {
    let data = JSON.parse(custom_decrypt(e.data));
    let message = JSON.parse(data["message"]);
    let sender = data["sender"];

    let sender_username = message["sender_username"];
    // message sent by himself
    if (sender != 'System' && sender_username == get_sender_username()) {
        return;
    }

    let receiver_token = message["receiver_token"];
    let text_message = message["text_message"];
    let sender_name = message["sender_name"];
    let sender_websocket_token = message["sender_websocket_token"];

    if (sender == "User") {
        if(message["is_replied_message"]) {
            var html = append_replied_message(message, "", "client");

            $(`#style-2_${sender_websocket_token}`).append(html);
        } else {
            let path = message["path"];
            if (path != "") {
                let thumbnail_url = message["thumbnail"];
                let html = append_internal_media_response_server(
                    path,
                    sender_name,
                    thumbnail_url,
                    message.text_message,
                );
                const session_id = receiver_token;

                $(`#style-2_${sender_websocket_token}`).append(html);
                internal_chat_scroll_to_bottom(sender_websocket_token);

            } else {
                if (message["text_message"] != "") {
                    append_internal_chat_response_server(
                        text_message,
                        sender_websocket_token,
                        sender_name
                    );
                }
            }

            if (message.receiver_username != 'group' && message.receiver_username != 'user_group') {
                update_user_chat_info(sender_websocket_token, text_message, path, return_time());
            }
        }
        internal_chat_scroll_to_bottom(sender_websocket_token);
    } else if (sender == 'System') {
        if ("event_type" in message && message["event_type"] == "TYPING") {
            if (sender_username != get_sender_username()) {
                if (message.is_group)
                    show_customer_typing_in_chat(message.sender_name);
                else
                    show_customer_typing_in_chat();
            }
            return;
        }

        if (message.text_message.includes('changed the') || message.text_message.includes('removed')) {
            message.text_message = message.text_message.replace(' ' + get_sender_username() + ' ', ' you ');
            
            if (message.sender_username == get_sender_username()) {
                message.text_message = 'You ' + message.text_message;
            } else {
                message.text_message = message.sender_username + ' ' + message.text_message;
            }
        }

        if ('added_members' in message) {
            const added_members = message.added_members;

            for (const member of added_members) {
                const msg = `added ${member} to the chat`;
                if (message.sender_username == get_sender_username()) {
                    msg = 'You ' + msg;
                } else {
                    msg = message.sender_username + ' ' + msg;
                }
                append_system_text_response(msg, return_time(), receiver_token);
            }

            update_group_chat_list({
                is_member_removed: false,
                is_member_added: false,
                user_group_id: null,
            });
        } else if ('removed_user' in message) {
            append_system_text_response(message.text_message, return_time(), receiver_token);

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
        } else if ('deleted_group' in message && message.deleted_group) {
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
            append_system_text_response(message.text_message, return_time(), receiver_token);
        }

        internal_chat_scroll_to_bottom(sender_websocket_token);
    }
}

function append_message_in_group_or_one2one_chat(session_id, message) {
    const elem = document.getElementById(`livechat-last-message-${session_id}`);
    try {
        elem.innerHTML = message;
        hide_customer_typing_in_chat_icon(session_id);
    } catch (err) {
        console.log(err);
    }
}

function send_message_to_internal_chat_socket(message, sender, is_it_group=false) {
    var final_packet = JSON.stringify({
                            message: message,
                            sender: sender
                        })
    const chat_socket = state.chat_socket;
    final_packet = encrypt_variable(final_packet);
    chat_socket.socket.send(final_packet);

    // Send message to global socket
    var message_for_agent = "";
    if(get_is_group_chat()) {

        message_for_agent = JSON.stringify({
            
            message: message,
            sender: "GroupUser",
        });
    } else if (get_is_user_group()) {
        message_for_agent = JSON.stringify({
            
            message: message,
            sender: "UserGroup",
        });
    } else {

        message_for_agent = JSON.stringify({
            
            message: message,
            sender: "OneToOneUser",
        });
    }
    send_message_to_guest_agent_socket(message_for_agent);
}

function open_livechat_socket(e) {
    state.chat_socket.is_open = true;
    state.chat_socket.send_ping = setInterval(send_ping_to_socket, 1000);
}

function close_chat_socket() {
    if (state.chat_socket.is_open == true && state.chat_socket.socket != null) {
        state.chat_socket.socket.close();
    }
}

function close_internal_chat_socket(e) {
    state.chat_socket.is_open = false;
    state.chat_socket.socket = null;
}

function check_and_close_internal_websocket(e) {
    state.chat_socket.is_open = false;
    state.chat_socket.socket = null;
}


function send_typing_message_to_customer(is_group) {
    if (state.chat_socket.is_open == true && state.chat_socket.socket != null) {
        const sentence = JSON.stringify({
                text_message: "",
                type: "text",
                channel: "Web",
                path: "",
                receiver_token: get_current_receiver_token(),
                receiver_username : get_current_receiver_username(),
                sender_websocket_token: get_sender_websocket_token(),
                sender_name: get_internal_chat_sender_name(),
                sender_username: get_sender_username(),
                event_type: "TYPING",
                is_group: is_group,
            });

        send_message_to_internal_chat_socket(sentence, 'System', is_group);
    }
}

function send_ping_to_socket() {
    if (state.chat_socket.is_open == true && state.chat_socket.socket != null) {
        var sentence = JSON.stringify({
            message: JSON.stringify({
                text_message: "",
                type: "text",
                path: "",
            }),
            sender: "ping",
        });
        sentence = encrypt_variable(sentence);
        state.chat_socket.socket.send(sentence);
    }
}

function append_replied_message(message, session_id, message_for, flag_not_seen=false) {
    var html;

    if(message.reply_file_path != "") {

        var reply_attachment_html = get_attachment_html(
            message.reply_file_path, 
            "", 
            message.reply_file_thumbnail,
            message.reply_message_text,
            message.time);

        if (message.path != "") {
            var attachment_html = get_attachment_html(
                message.path,
                "",
                message.thumbnail,
                message.text_message,
                message.time
                );

            html = get_reply_response_user_html(
                attachment_html,
                message.sender_name,
                flag_not_seen,
                "",
                message.time,
                reply_attachment_html,
                message.time,
                message_for,
                Date.parse(new Date()),
                true,
                true,
            );    

        } else if (message.text_message != "") {
            html = get_reply_response_user_html(
                message.text_message,
                message.sender_name,
                flag_not_seen,
                "",
                message.time,
                reply_attachment_html,
                message.time,
                message_for,
                Date.parse(new Date()),
                false,
                true
            );            
        }    

    } else if (message.reply_message_text != "") {
        if (message.path != "") {
            var attachment_html = get_attachment_html(
                message.path,
                "",
                message.thumbnail,
                message.text_message,
                message.time
                );

            html = get_reply_response_user_html(
                attachment_html,
                message.sender_name,
                flag_not_seen,
                "",
                message.time,
                message.reply_message_text,
                message.time,
                message_for,
                Date.parse(new Date()),
                true
            ); 

        } else if (message.text_message != "") {
            html = get_reply_response_user_html(
                message.text_message,
                message.sender_name,
                flag_not_seen,
                "",
                message.time,
                message.reply_message_text,
                message.time,
                message_for,
                Date.parse(new Date()),
            );            
        }
    }
    return html;
}

export {
    create_one_to_one_chat_socket,
    send_message_to_internal_chat_socket,
    get_sender_websocket_token,
    set_sender_websocket_token,
    check_and_close_internal_websocket,
    close_internal_chat_socket,
    create_websocket,
    close_chat_socket,
    send_typing_message_to_customer
};
