import {
    send_message_to_internal_chat_socket,
    get_sender_websocket_token,
    create_websocket,
    close_chat_socket,
    send_typing_message_to_customer,
} from "./livechat_internal_chat_socket";

import { add_chat_click_event, add_user_group_click_event, get_all_user_groups, get_user_chat_icon_html, get_user_group_arr, get_user_group_chat_icon_html, get_user_group_list, get_user_list, get_user_sessions, send_message_to_guest_agent_socket, set_chat_started_in_user_group, set_is_chat_started, set_one_to_one_user_list, set_user_group_list, set_zero_unread_message_count, update_user_chat_info } from "../agent/livechat_agent_socket";

import { get_user_initial } from "./archive_customer";

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
    get_image_path_html,
    get_video_path_html,
    get_doc_path_html,
    EncryptVariable,
    get_unread_message_diffrentiator_html,
    get_params,
    get_user_group_member_count_html,
} from "../utils";
import {
    return_time,
    livechat_linkify,
    get_system_text_response_html,
    get_attachment_html,
} from "../agent/chatbox";
import { auto_resize, append_file_to_modal, is_url } from "../agent/chatbox_input";

import {
    get_theme_color,
    showToast,
    append_message_in_chat_icon,
    get_icons,
    highlight_chat,
    append_unread_msg_count_in_chat_icon,
    set_theme_color,
    getCsrfToken,
    append_message_in_chat_icon_new,
} from "../agent/console";

import {
    get_min_last_seen,
    get_min_last_seen_on_chat,
    hide_group_header,
    mark_group_messages_as_delivered,
    mark_group_messages_as_read,
    send_media_message_to_group,
    send_message_to_group,
    update_internal_chat_group_history,
} from "../admin/group_chat_console";

import { filterList, get_active_group, set_all_agents, update_group_chat_list } from "../admin/manage_group";

import axios from "axios";

const state = {
    sender_username: "",
    current_receiver_name: "",
    current_receiver_token: null,
    current_receiver_username: "",
    previous_chat_console_id: null,
    mic: {
        instance: null,
        recognizing: false,
        prev_text: "",
        start: new Date().getTime(),
        end: new Date().getTime(),
        ignore_onend: false,
    },
    is_mobile: is_mobile(),
    attachment: {
        data: "",
        form_data: "",
        file_src: "",
        file_name: "",
    },
    chat_history: {},
    is_group_chat: false,
    is_user_group: false,
    chat_load: {
        index: 0,
        is_completed: true,
        limit: 50
    },
    check_list: [],
    active_user_group: {
        id: null,
        name: null,
        members: [],
        members_username: [],
        added_agents: [],
    },
    new_user_group: {
        member_count: 0,
    },
    tick: {
        single: `<svg style="margin:-5px -2px 0px 5px;" width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M13.4996 4.50032L6.49963 11.5L2.99963 8.00032" stroke="#CBCACA" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"></path>
                </svg>`,
        
        double: `<svg style="margin:-5px 5px 0px 5px;" width="14" height="10" viewBox="0 0 14 10" fill="none" xmlns="http://www.w3.org/2000/svg">\
                    <path d="M3.45714 6.51434L1.07304 4.18025C0.827565 3.93994 0.429579 3.93994 0.184102 4.18025C-0.0613675 4.42056 -0.0613675 4.81022 0.184102 5.05053L3.01268 7.81976C3.25815 8.06007 3.65614 8.06007 3.90161 7.81976L10.8159 1.05053C11.0614 0.810204 11.0614 0.420567 10.8159 0.18024C10.5704 -0.0600801 10.1724 -0.0600801 9.92697 0.18024L3.45714 6.51434Z" fill="#4d4d4d"/>\
                    <path d="M5.6412 8.51434L5.07684 7.99999C4.83137 7.75969 4.42956 8.27404 4.18409 8.51434C3.93862 8.75465 3.93864 8.62614 4.18411 8.86645L5.19673 9.81976C5.44221 10.0601 5.8402 10.0601 6.08567 9.81976L13 3.05053C13.2454 2.8102 13.2454 2.42057 13 2.18024C12.7545 1.93992 12.3565 1.93992 12.111 2.18024L5.6412 8.51434Z" fill="#4d4d4d"/>\
                </svg>`,
        
        blue: `<svg style="margin:-5px 5px 0px 5px;" width="14" height="10" viewBox="0 0 14 10" fill="none" xmlns="http://www.w3.org/2000/svg">\
                <path d="M3.45714 6.51434L1.07304 4.18025C0.827565 3.93994 0.429579 3.93994 0.184102 4.18025C-0.0613675 4.42056 -0.0613675 4.81022 0.184102 5.05053L3.01268 7.81976C3.25815 8.06007 3.65614 8.06007 3.90161 7.81976L10.8159 1.05053C11.0614 0.810204 11.0614 0.420567 10.8159 0.18024C10.5704 -0.0600801 10.1724 -0.0600801 9.92697 0.18024L3.45714 6.51434Z" fill="#0254D7"/>\
                <path d="M5.6412 8.51434L5.07684 7.99999C4.83137 7.75969 4.42956 8.27404 4.18409 8.51434C3.93862 8.75465 3.93864 8.62614 4.18411 8.86645L5.19673 9.81976C5.44221 10.0601 5.8402 10.0601 6.08567 9.81976L13 3.05053C13.2454 2.8102 13.2454 2.42057 13 2.18024C12.7545 1.93992 12.3565 1.93992 12.111 2.18024L5.6412 8.51434Z" fill="#0254D7"/>\
                </svg>`
    },
    is_sent: 0,
    is_delivered: 1,
    is_read: 2,
    agent_last_seen: {},
    last_seen_on_chat: {
        groups: {},
        user_groups: {},
        single_chats: {},
    },
    date_set: null,
};

$(function () {
    $("#query").keyup(function (e) {
        e = e || window.event;

        const input_element = document.getElementById("query");
        const user_query = input_element.value.trim();
        const theme_color = get_theme_color();

        if (user_query != "") {
            document.getElementById("fill-submit-btn").style.fill =
                theme_color.one;
            send_typing_message_to_customer(state.is_group_chat);
        } else {
            document.getElementById("fill-submit-btn").style.fill =
                theme_color.two;
        }
    });
    // Used when agent is redirected to internal chat after clicking replied message
    if(String(window.location.href).includes('internal-chat')) {

        if (String(window.location.href).includes('webtoken')) {
            var url= document.location.href;
            var url_params = (url.split("?")[1]).split("&");
            var websocket_token = url_params[0].split("=")[1]
            var username = url_params[1].split("=")[1]
            var name = url_params[2].split("=")[1]
            setTimeout(() => {
                go_to_one_on_one_chat(websocket_token, username, name);
                window.history.pushState({}, "", url.split("?")[0]);    
            }, 300);
        }

        setInterval(() => {
            send_agent_last_seen_time();

            if (window.isActive) {
                update_last_seen_on_chat();
                send_last_seen_on_chats_to_server();
                send_last_seen_on_chat_signal();
            }
        }, 2000);
    }

    window.isActive = true;
    $(window).focus(function() { this.isActive = true; });
    $(window).blur(function() { this.isActive = false; });
});

function initialize_internal_console() {
    state.sender_username = window.SENDER_USERNAME;
    set_all_agents(window.AGENTS);
    set_theme_color(window.LIVECHAT_THEME_COLOR, window.LIVECHAT_THEME_COLOR_LIGHT, window.LIVECHAT_THEME_COLOR_LIGHT_ONE);
}

function hide_previous_chat() {
    $("div[id^=style-2]").hide();
}

function get_internal_chat_sender_name() {
    return window.SENDER_NAME;
}
function set_current_receiver_details(websocket_token, username, name) {
    state.current_receiver_token = websocket_token;
    state.current_receiver_username = username;
    state.current_receiver_name = name;
}

function reload_user_details_click_events() {
    const elems = document.getElementsByClassName("reload-user-details");

    if (is_mobile()) {
        Array.from(elems).forEach((elem) => {
            $(elem).on("touchend", () => {
                fetch_and_add_active_user_details(elem.id);
            });
        });
    } else {
        Array.from(elems).forEach((elem) => {
            $(elem).on("click", () => {
                fetch_and_add_active_user_details(elem.id);
            });
        });
    }   
}

function show_loading_text() {

    var failed_div_list = document.getElementsByClassName("livechat-detail-loading-failed-div");
    if(failed_div_list.length) {

        var failed_div = failed_div_list[0];
        failed_div.innerHTML = "Loading..."
    }
}
function prepare_front_end_user_details(response, username) {

    let html = "";
    if (response.status == "200") {
        let { name, email, phone, user_status, last_seen_time, last_seen_date } = response;

        name = name == "" ? 'Not Available' : name;
        email = email == "" ? '-' : email;
        phone = phone == "" || phone == 'None' ? '-' : phone;

        const theme_color = get_theme_color();

        html = `                       
                <div class="live-chat-customer-details-todo" style="background-color: #fff;">
                    <div class="livechat-details-card-div">
                        <div class="live-chat-customer-name">
                            <div class="livechat-info-heading-div">
                                ${user_status}
                            </div>
                            <div style="display: flex; align-items: center;">
                                <div class="live-chat-mobile-display back-arrow">
                                    <img src="/static/LiveChatApp/img/mobile-back.svg" alt="Back arrow" id="live-chat-customer-details-closer" onclick="close_customer_details()">
                                </div>
                                <div style="display: flex; align-items: center;">
                                    <div class="live-chat-client-image"> ${get_user_initial(name)} </div>
                                    <div class="livechat-customer-name-text-div">
                                        <p class="live-chat-customer-name-text">${name}</p>
                                        <h6 id="livechat-group-details-last-seen-data">Last seen ${last_seen_date}, ${last_seen_time}</h6>
                                    </div>
                                </div>
                            </div>
                            <button class="customer-details-refresh-button reload-user-details" id="${username}" style="pointer-events: auto;">
                                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M14.7015 5.29286C13.3432 3.93453 11.4182 3.15119 9.30154 3.36786C6.2432 3.67619 3.72654 6.15953 3.38487 9.21786C2.92654 13.2595 6.05154 16.6679 9.9932 16.6679C12.6515 16.6679 14.9349 15.1095 16.0015 12.8679C16.2682 12.3095 15.8682 11.6679 15.2515 11.6679C14.9432 11.6679 14.6515 11.8345 14.5182 12.1095C13.5765 14.1345 11.3182 15.4179 8.85154 14.8679C7.00154 14.4595 5.50987 12.9512 5.1182 11.1012C4.4182 7.86786 6.87654 5.00119 9.9932 5.00119C11.3765 5.00119 12.6099 5.57619 13.5099 6.48453L12.2515 7.74286C11.7265 8.26786 12.0932 9.16786 12.8349 9.16786H15.8265C16.2849 9.16786 16.6599 8.79286 16.6599 8.33453V5.34286C16.6599 4.60119 15.7599 4.22619 15.2349 4.75119L14.7015 5.29286Z" fill="#717171"></path>
                                </svg>
                            </button>
                        </div>
                        <div class="livechat-customer-personal-details-wrapper">
                            <div class="livechat-customer-personal-details">
                                <div class="livechat-customer-detail-items-wrapper">
                                    <div class="livechat-customer-detail-icon-wrapper">
                                        <div class="livechat-customer-detail-icon-div">
                                            <svg width="20" height="20" fill="${theme_color.one}" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                                <circle cx="10" cy="10" r="10" fill="#F8F8F8"/>
                                                <path fill-rule="evenodd" clip-rule="evenodd" d="M9.6 5C8.60588 5 7.8 5.80589 7.8 6.8C7.8 7.79411 8.60588 8.6 9.6 8.6C10.5941 8.6 11.4 7.79411 11.4 6.8C11.4 5.80589 10.5941 5 9.6 5ZM8.7 6.8C8.7 6.30294 9.10294 5.9 9.6 5.9C10.0971 5.9 10.5 6.30294 10.5 6.8C10.5 7.29705 10.0971 7.7 9.6 7.7C9.10294 7.7 8.7 7.29705 8.7 6.8Z" />
                                                <path fill-rule="evenodd" clip-rule="evenodd" d="M11.85 9.49999L7.34998 9.49999C6.60441 9.49999 6 10.1044 6 10.85C6 11.8545 6.41307 12.6592 7.09093 13.2033C7.75807 13.7388 8.65223 14 9.59999 14C10.5478 14 11.4419 13.7388 12.1091 13.2033C12.7869 12.6592 13.2 11.8545 13.2 10.85C13.2 10.1044 12.5956 9.49999 11.85 9.49999ZM7.34998 10.4L11.85 10.4C12.0985 10.4 12.3 10.6015 12.3 10.85C12.3 11.5852 12.0079 12.1304 11.5457 12.5014C11.0728 12.881 10.3919 13.1 9.59999 13.1C8.80807 13.1 8.12722 12.881 7.65429 12.5014C7.19208 12.1304 6.9 11.5852 6.9 10.85C6.9 10.6015 7.10148 10.4 7.34998 10.4Z" />
                                            </svg>
                                        </div>
                                    </div>
                                    <input type="text" id="customer-name-input" class="live-chat-content" value="${name}" readonly/>
                                </div>
                                <div class="livechat-customer-detail-items-wrapper">
                                    <div class="livechat-customer-detail-icon-wrapper">
                                        <div class="livechat-customer-detail-icon-div">
                                            <svg width="20" height="20" fill="${theme_color.one}" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                                <circle cx="10" cy="10" r="10" fill="#F8F8F8"/>
                                                <path d="M12.8553 6C13.6587 6 14.31 6.65129 14.31 7.45469V12.1097C14.31 12.9131 13.6587 13.5644 12.8553 13.5644H6.45469C5.65129 13.5644 5 12.9131 5 12.1097V7.45469C5 6.65129 5.65129 6 6.45469 6H12.8553ZM13.7281 8.30481L9.80251 10.6148C9.72664 10.6595 9.63557 10.6669 9.55463 10.6371L9.50749 10.6148L5.58188 8.30597V12.1097C5.58188 12.5917 5.97265 12.9825 6.45469 12.9825H12.8553C13.3374 12.9825 13.7281 12.5917 13.7281 12.1097V8.30481ZM12.8553 6.58187H6.45469C5.97265 6.58187 5.58188 6.97265 5.58188 7.45469V7.63041L9.655 10.0265L13.7281 7.62983V7.45469C13.7281 6.97265 13.3374 6.58187 12.8553 6.58187Z"/>
                                            </svg>
                                        </div>
                                    </div>
                                    <input type="email" class="live-chat-content" value="${email}" readonly />
                                </div>
                                <div class="livechat-customer-detail-items-wrapper">
                                    <div class="livechat-customer-detail-icon-wrapper">
                                        <div class="livechat-customer-detail-icon-div">
                                            <svg width="20" height="20" fill="${theme_color.one}" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                                <circle cx="10" cy="10" r="10" fill="#F8F8F8"/>
                                                <path d="M8.64427 6.42965L8.32176 6.52686C7.73517 6.70367 7.30435 7.2046 7.21729 7.81104C7.08365 8.74196 7.38255 9.83008 8.10276 11.0775C8.82144 12.3223 9.6125 13.1245 10.4833 13.4754C11.0547 13.7056 11.7078 13.5816 12.155 13.1581L12.3992 12.9268C12.7266 12.6167 12.7741 12.1123 12.5102 11.7467L11.8998 10.9006C11.7307 10.6663 11.4313 10.5656 11.155 10.6501L10.2322 10.9322L10.2084 10.9369C10.1066 10.9517 9.87203 10.7317 9.57947 10.2249C9.2734 9.69481 9.20997 9.38484 9.29447 9.30493L9.76398 8.86711C10.1159 8.53899 10.2198 8.02327 10.0225 7.58445L9.72488 6.92233C9.53953 6.51002 9.07709 6.29918 8.64427 6.42965ZM9.31445 7.10684L9.6121 7.76896C9.73038 8.03206 9.66805 8.34127 9.45708 8.538L8.98642 8.9769C8.68533 9.26163 8.78506 9.74897 9.18976 10.4499C9.57055 11.1095 9.91795 11.4354 10.2912 11.3789L10.3472 11.3669L11.2866 11.0804C11.3787 11.0522 11.4785 11.0858 11.5348 11.1639L12.1453 12.01C12.2772 12.1928 12.2535 12.445 12.0898 12.6L11.8456 12.8313C11.5261 13.1339 11.0596 13.2224 10.6515 13.058C9.8874 12.7501 9.16524 12.0178 8.49247 10.8525C7.81832 9.68485 7.54549 8.69164 7.66272 7.87498C7.72491 7.44181 8.03264 7.08401 8.45163 6.95771L8.77414 6.8605C8.99055 6.79527 9.22177 6.90069 9.31445 7.10684Z" />
                                            </svg>
                                        </div>
                                    </div>
                                    <input type="tel" class="live-chat-content" value="${phone}" readonly/>
                                </div>
                            </div>
                        </div>
                    </div>
                    <br>
                    <br>
                </div>`

    } else {
        html = `<div class="livechat-detail-loading-failed-div">
                    <img src="/static/LiveChatApp/img/loading_error.svg" width="200px" height="150px">
                    <p>
                        Unable to load user details
                        <a href="javascript:void(0)" class="reload-user-details" id="${username}">
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M14.7015 5.29286C13.3432 3.93453 11.4182 3.15119 9.30154 3.36786C6.2432 3.67619 3.72654 6.15953 3.38487 9.21786C2.92654 13.2595 6.05154 16.6679 9.9932 16.6679C12.6515 16.6679 14.9349 15.1095 16.0015 12.8679C16.2682 12.3095 15.8682 11.6679 15.2515 11.6679C14.9432 11.6679 14.6515 11.8345 14.5182 12.1095C13.5765 14.1345 11.3182 15.4179 8.85154 14.8679C7.00154 14.4595 5.50987 12.9512 5.1182 11.1012C4.4182 7.86786 6.87654 5.00119 9.9932 5.00119C11.3765 5.00119 12.6099 5.57619 13.5099 6.48453L12.2515 7.74286C11.7265 8.26786 12.0932 9.16786 12.8349 9.16786H15.8265C16.2849 9.16786 16.6599 8.79286 16.6599 8.33453V5.34286C16.6599 4.60119 15.7599 4.22619 15.2349 4.75119L14.7015 5.29286Z" fill="#717171"></path>
                            </svg>
                        </a>
                    </p>
                </div>`
    }

    document.getElementById("live-chat-group-details-sidebar").innerHTML = html;
    document.getElementById("live-chat-group-details-sidebar").style.display =
        "flex";
}

function fetch_and_add_active_user_details(username) {

    show_loading_text();
    var json_string = JSON.stringify({
        username: username,
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/get-livechat-user-details/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            prepare_front_end_user_details(response, username);
            reload_user_details_click_events();
        }
    };
    xhttp.send(params);
}

async function go_to_one_on_one_chat(websocket_token, username, name) {
    set_is_group_chat(false);
    set_is_user_group(false);

    state.chat_load.is_completed = false;
    state.chat_load.index = 0;
    const previous_chat_console_id = state.current_receiver_token;
    state.previous_chat_console_id = previous_chat_console_id;

    close_chat_socket();
    highlight_chat(previous_chat_console_id, websocket_token);
    hide_previous_chat();
    set_current_receiver_details(websocket_token, username, name);
    show_internal_chat_console(websocket_token);
    hide_group_header();

    const user_list = get_user_list();
    show_user_name_on_header(user_list[websocket_token]);

    fetch_and_add_active_user_details(username);

    reset_date_set();
    update_internal_chat_message_history();
    create_websocket(websocket_token);
    update_members_list();

    update_last_seen_on_chat();

    document.getElementById('groupchat-user-search-global').value = '';
    const search_el = document.getElementById('livechat-groupchat-agent-search');

    if (search_el.value != '') {
        search_el.value = '';
        await set_is_chat_started(websocket_token);
        update_group_chat_list({is_member_added: false, is_member_removed: false, user_group_id: null});
        $('#livechat_agent_search_bar_toggle').trigger('click');    
    }

    $('#livechat_add_members_btn').show();
}

function show_user_name_on_header(user) {
    const name_elem = document.getElementById('livechat_group_name_header');

    if(name_elem) {
        name_elem.innerHTML = user.full_name == '' ? stripHTML(user.username) : stripHTML(user.full_name);
        name_elem.style.display = 'block';
    }
}

function show_user_name_on_header_user_group(name, total_members, id) {
    const name_elem = document.getElementById('livechat_group_name_header');

    if(name_elem) {
        name_elem.innerHTML = stripHTML(name);
        name_elem.style.display = 'flex';
        name_elem.style.gap = '0.5em';
    }

    if (total_members != undefined) {
        name_elem.innerHTML += `<div class="livechat-user-group-member-count">
                                    ${get_user_group_member_count_html(id, total_members-1)}
                                </div>`
    } 
}

export async function go_to_user_group(id) {
    set_is_group_chat(false);
    set_is_user_group(true);

    const prev_active_group = state.active_user_group;

    const previous_chat_console_id = prev_active_group.id;
    state.previous_chat_console_id = previous_chat_console_id;

    close_chat_socket();
    highlight_chat(previous_chat_console_id, id);
    hide_previous_chat();
    set_current_receiver_details(id, "user_group");
    update_user_group_display_info(id);

    show_internal_chat_console(id);
    hide_group_header();

    $('#livechat_add_members_btn').show();

    set_chat_load({
        index: 0,
        is_completed: false,
        limit: get_chat_load().limit,
    });

    show_user_name_on_header_user_group(state.active_user_group.name, state.active_user_group.members.length, state.active_user_group.id);

    reset_date_set();
    update_internal_user_group_history(id);
    update_members_list();
    create_websocket(id, true);

    document.getElementById('groupchat-user-search-global').value = '';
    const search_el = document.getElementById('livechat-groupchat-agent-search');

    if (search_el.value != '') {
        search_el.value = '';
        await set_chat_started_in_user_group(id);
        update_group_chat_list({is_member_added: false, is_member_removed: false, user_group_id: null});
        $('#livechat_agent_search_bar_toggle').trigger('click');    
    }
}

function update_internal_user_group_history(id, is_more_chat_loaded) {
    const chat_div = document.getElementById(`style-2_${id}`);
    const scroll_pos = chat_div.scrollHeight - chat_div.scrollTop;
    const chat_load = get_chat_load();

    const json_string = JSON.stringify({
        group_id: id,
        chat_index: chat_load.index,
    });

    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/get-user-group-chat-history/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if (response.status == 200) {
                const loader_div = document.getElementById(`more-chat-loader_${id}`);
                if (loader_div) {
                    loader_div.remove();
                }
                
                const last_seen_time = response.last_seen_time;
                const last_seen_on_chat = response.last_seen_on_chat;
                append_internal_message_history(response.message_history, last_seen_time, last_seen_on_chat, is_more_chat_loaded);

                if (is_more_chat_loaded) {
                    chat_div.scrollTop = chat_div.scrollHeight - scroll_pos;
                }
                set_chat_load({
                    index: chat_load.index + chat_load.limit,
                    is_completed: response.all_chat_loaded,
                    limit: chat_load.limit,
                });

            } else {
                showToast(response.message, 2000);
            }
        })
        .catch((err) => {
            console.log(err);
            console.log("Unable to create group. Please try again later.");
        });
}

function update_user_group_display_info(id) {
    const group_list = get_user_group_list();
    const group_detail = group_list[id];

    update_active_user_group(id, group_detail);

    document.getElementById("live-chat-group-details-sidebar").innerHTML = get_user_group_details_html();

    const html = get_user_group_members_display_html(group_detail.members);

    $("#livechat-group-members-list").html(html);

    $(".livechat-customer-group-active-member-count-div").html(
        `${group_detail.members.length} Members`
    );

    document.getElementById("live-chat-no-chat-opened").style.display = "none";
    document.getElementById("live-chat-group-details-sidebar").style.display =
        "flex";
}

function get_user_group_details_html () {
    const theme_color = get_theme_color();

    let temp_html = `
                <div class="live-chat-customer-details-todo" style="background-color: #fff;">`;

    temp_html += `
                <div class="live-chat-customer-full-details">`;
    
    temp_html += '<div style="display: flex; flex-flow: column; padding: 12px 20px 4px 12px;">'
    
    temp_html += `
                        <p style="color: #000; font-size: 12px; font-weight: 500; margin-bottom: 10px;">Members</p>
                        <div class="livechat-customer-group-active-member-count-div" style="font-size: 12px; color: #7B7A7B;">1 Members</div>
                    </div>
                </div>
                <div class="livechat-customer-group-member-items-list-area" id="livechat-group-members-list">
                </div>`

    temp_html += `</div></div>`;
            
    return temp_html;
}

function get_user_group_members_display_html(members) {
    let html = ``;
    for (const member of members) {
        html += `                    
                <div class="livechat-customer-group-member-items-div">
                    <div class="livechat-customer-group-member-icon-div">
                        ${get_user_initial(member.name)}
                    </div>
                    <div>
                        <div class="livechat-customer-group-member-name-div livechat-customer-group-member-name-with-profile" style="width: 100%;">${member.name}</div>
                    `;
        
        if (member.is_supervisor) {
            html += `
                            <div class="livechat-customer-group-supervisor-identity-div">
                                Supervisor
                            </div>
                        </div>
                    </div>
            `
        } else if (member.is_admin) {
            html += `
                            <div class="livechat-customer-group-supervisor-identity-div">
                                Admin
                            </div>
                        </div>
                    </div>
            `
        } else {
            html += `</div>`
        }

        html += `</div>`
    }

    return html;
}

function update_active_user_group(id, details) {
    state.active_user_group.id = id;
    state.active_user_group.name = details.full_name;
    state.active_user_group.members = details.members;
    state.active_user_group.members_username = []

    details.members.forEach(member => {
        state.active_user_group.members_username.push(member.name);
    })
}

export function get_active_user_group() {
    return state.active_user_group;
}

function get_current_receiver_username() {
    return state.current_receiver_username.trim();
}

function get_current_receiver_name() {
    if (state.current_receiver_name.trim() == "") {
        return get_current_receiver_username();
    }
    return state.current_receiver_name.trim();
}

function get_current_receiver_token() {
    return state.current_receiver_token;
}

function send_internal_message_to_user() {
    const receiver_username = get_current_receiver_username();
    if (receiver_username == "") {
        console.log("Something went wrong try again later");
        return;
    }

    const theme_color = get_theme_color();
    document.getElementById("fill-submit-btn").style.fill = theme_color.two;

    let sentence = process_sentence($("#query").val());

    if (sentence.trim() == '') return;
    
    append_response_internal_chat_user(sentence, window.SENDER_NAME, false);
    document.getElementById("query").value = "";

    var json_string = JSON.stringify({
        message: sentence,
        sender: "user",
        attached_file_src: "",
        thumbnail_url: "",
        receiver_username: receiver_username,
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/save-internal-chat/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            console.log("chat send by agent saved");
        }
    };
    xhttp.send(params);

    const receiver_websocket_token = get_current_receiver_token();
    const sender_websocket_token = get_sender_websocket_token();

    let text_message = sentence;
    var message_packet = JSON.stringify({
        text_message: text_message,
        type: "text",
        path: "",
        thumbnail: "",
        receiver_token: receiver_websocket_token,
        receiver_username: receiver_username,
        sender_websocket_token: sender_websocket_token,
        sender_name: get_internal_chat_sender_name(),
        sender_username: state.sender_username,
        is_group: false,
    });

    send_message_to_internal_chat_socket(message_packet, "User", false);

    update_user_chat_info(receiver_websocket_token, text_message, "", return_time());
}

export function send_message_to_user_group() {
    const theme_color = get_theme_color();
    document.getElementById("fill-submit-btn").style.fill = theme_color.two;

    var sentence = process_sentence($("#query").val());

    if (sentence.trim() == "") return;

    append_response_internal_chat_user(sentence, window.SENDER_NAME, false);
    const active_group = state.active_user_group;
    const group_id = active_group.id;

    var json_string = JSON.stringify({
        message: sentence,
        sender: "user",
        attached_file_src: "",
        thumbnail_url: "",
        receiver_username: "user_group",
        group_id: group_id,
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/save-internal-chat/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            console.log("chat send by agent saved");
        }
    };
    xhttp.send(params);

    document.getElementById("query").value = "";

    var temp_message = JSON.stringify({
        text_message: sentence,
        type: "text",
        path: "",
        thumbnail: "",
        receiver_token: group_id,
        receiver_username: "user_group",
        sender_websocket_token: group_id,
        sender_name: get_internal_chat_sender_name(),
        sender_username: get_sender_username(),
        is_group: true,
    });

    send_message_to_internal_chat_socket(temp_message, "User", true);
}

export function process_sentence(sentence) {
    if (is_url(sentence)) return sentence;

    sentence = $($.parseHTML(sentence)).text();
    sentence = sentence.replace(/\*/g, "");
    sentence = stripHTML(sentence);
    sentence = strip_unwanted_characters(sentence);

    return sentence;
}

function append_response_internal_chat_user(
    sentence,
    sender_username,
    flag_not_seen,
    time = return_time()
) {
    sentence = stripHTML(sentence);
    sentence = livechat_linkify(sentence);
    sentence = sentence.trim();

    const rec_websocket_token = state.current_receiver_token;

    let blue_ticks = state.tick.single;
    let custom_class = 'single_tick';
    if (flag_not_seen == state.is_delivered) {
        blue_ticks = state.tick.double;
        custom_class = 'double_tick';
    } else if (flag_not_seen == state.is_read) {
        blue_ticks = state.tick.blue;
        custom_class = 'blue_tick';
    }

    let html = '';
    if (!state.date_set.has('Today')) {
        state.date_set.add('Today');
        html += get_chat_date_html('Today');
    }

    html +=
        `<div class="live-chat-agent-message-wrapper">
            <div class="live-chat-agent-image">
                ${get_user_initial(sender_username)}
            </div>
            <div class="live-chat-agent-message-bubble">
                ${sentence}
            </div>
            <div class="live-chat-agent-message-time">
                ${time}
                <div data-time="${Date.parse(new Date())}" class="blue_tick-${rec_websocket_token} ${custom_class}">${blue_ticks}</div>
            </div>
        </div>`

    $(`#style-2_${rec_websocket_token}`).append(html);
    localStorage.setItem(`user_input-${rec_websocket_token}`, "");
    internal_chat_scroll_to_bottom(rec_websocket_token);
}

function show_internal_chat_console(websocket_token) {
    let session_id = websocket_token;

    try {
        document.getElementById("livechat-group-console-menu").style.display =
            "none";
    } catch (err) {}

    if ($("#live-chat-indicator-" + session_id).length)
        $("#live-chat-indicator-" + session_id).css("display", "flex");

    const chat_div = document.getElementById(`style-2_${session_id}`);
    // scrollendHandler()
    document.getElementById("live-chat-no-chat-opened").style.display = "none";
    document.getElementById("livechat-main-console").style.display = "block";

    if (chat_div == undefined || chat_div == null) {
        const parent_chat_div =
            document.getElementsByClassName("live-chat-area")[0];
        const html = `<div class="live-chat-message-wrapper" id="style-2_${session_id}" ></div><input id="hidden_current_session_id_${session_id}" type="hidden"  value = "${session_id}"><input id="top_reached_${session_id}" type="hidden"  value = "0">`;

        $(parent_chat_div).prepend(html);

        $(`#style-2_${session_id}`).on('scroll', (e) => {
            load_more_chat(session_id, state.is_group_chat);
        })
    } else {
        chat_div.style.display = "block";
    }

    const user_input = localStorage.getItem(
        `user_input-${session_id}`
    );
    
    const theme_color = get_theme_color();
    if (user_input && user_input != "") {
        document.getElementById("query").value = user_input;
        document.getElementById("fill-submit-btn").style.fill = theme_color.one;    
    } else {
        document.getElementById("query").value = "";
        document.getElementById("fill-submit-btn").style.fill = theme_color.two;    
    }

    document.getElementById("query").oninput = () => {
        localStorage.setItem(
            `user_input-${session_id}`,
            document.getElementById("query").value
        );
    };

    document.getElementById("livechat_input_box").style.display = "flex";
    document.getElementById("livechat_cant_send_message_div").style.display =
        "none";

    auto_resize();
}

function append_internal_chat_response_server(
    sentence,
    token_id,
    sender_name,
    time = return_time()
) {
    let session_id = token_id;
    sentence = livechat_linkify(sentence);
    sentence = sentence.replace("<p>", "");
    sentence = sentence.replace("</p>", "");
    sentence = sentence.replace("<strong>", "<b>");
    sentence = sentence.replace("</strong>", "</b>");
    sentence = sentence.replace("<em>", "<i>");
    sentence = sentence.replace("</em>", "</i>");
    sentence = sentence.replace("background-color:#ffffff; color:#000000", "");
    sentence = sentence.replace("background-color:#ffffff;", "");

    let html = '';
    if (!state.date_set.has('Today')) {
        state.date_set.add('Today');
        html += get_chat_date_html('Today');
    }

    html += `<div class="live-chat-client-message-wrapper">
            <div class="live-chat-client-image"> 
                ${get_user_initial(sender_name)}
            </div>
            <div class="group-chat-element live-chat-client-name-with-message">${sender_name}</div>
            <div class="live-chat-client-message-bubble">\
                ${sentence}
            </div>
            <div class="live-chat-client-message-time">
                ${time}
            </div>
        </div>`;

    $(`#style-2_${session_id}`).append(html);
    internal_chat_scroll_to_bottom(session_id);
}

// ////////////////////////////////////////////////////////////  attachment start ///////////////////////////////////
function reset_file_upload_modal() {
    document
        .getElementById("send_internal_chat_attachment")
        .classList.add("disabled");
    document.getElementById(
        "send_internal_chat_attachment"
    ).style.pointerEvents = "none";
    document.getElementById("live_chat_file_wrapper").innerHTML = "";
    state.attachment.file_src = "";
    document.getElementById('query-file').value = '';
}
function internal_chat_scroll_to_bottom(id) {
    if (!id) {
        id = get_current_receiver_token();
    }

    const elem = document.getElementById(`style-2_${id}`);
    if (elem) {
        $(elem).scrollTop($(elem)[0].scrollHeight);
    }
}

function upload_internal_file_attachment(e) {
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

    document
        .getElementById("file-upload-cancel-btn")
        .addEventListener("click", function () {
            reset_file_upload_modal();
        });

    document
        .getElementById("send_internal_chat_attachment")
        .classList.remove("disabled");
    document.getElementById(
        "send_internal_chat_attachment"
    ).style.pointerEvents = "auto";
    document.querySelector("#easychat-livechat-file-attchment-input").value =
        "";
}

$(document).on("click", "#send_internal_chat_attachment", function () {
    $("#livechat-file-upload-modal").modal("toggle");

    var upload_attachment_data = state.attachment.data;

    var reader = new FileReader();
    reader.readAsDataURL(upload_attachment_data);
    reader.onload = function () {
        var base64_str = reader.result.split(",")[1];

        var uploaded_file = [];
        uploaded_file.push({
            filename: upload_attachment_data.name,
            base64_file: base64_str,
        });
        var json_string = JSON.stringify(uploaded_file);
        json_string = encrypt_variable(json_string);
        state.attachment.form_data.append("uploaded_file", json_string);
        upload_internal_chat_file_attachment_to_server();
    };

    reader.onerror = function (error) {
        console.log("Error: ", error);
    };
});

function upload_internal_chat_file_attachment_to_server() {

    let chat_type = "";
    let group_id = "";
    let user_group_id = "";
    let receiver_username = "";

    if (state.is_group_chat) {
        chat_type = "group_chat";
        group_id = get_active_group().id;
    } else if (state.is_user_group) {
        chat_type = "user_group_chat";
        user_group_id = get_active_user_group().id;
    } else {
        chat_type = "user_chat";
        receiver_username = get_current_receiver_username();
    }

    state.attachment.form_data.append("chat_type", chat_type);
    state.attachment.form_data.append("group_id", group_id);
    state.attachment.form_data.append("user_group_id", user_group_id);
    state.attachment.form_data.append("receiver_username", receiver_username);

    const params = state.attachment.form_data;

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/livechat/upload-internal-chat-attachment/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response.status == 200) {
                append_temp_file_to_internal_chat(
                    state.attachment.data.name,
                    window.SENDER_NAME
                );
                state.attachment.file_src = response.src;
                state.attachment.file_name = response.name;

                if (is_image(state.attachment.file_src)) {
                    const reader = new FileReader();
                    reader.addEventListener(
                        "load",
                        function () {
                            state.attachment.form_data = "";
                            state.attachment.data = "";
                            send_media_message_handler(
                                state.attachment.file_src,
                                response.thumbnail_url,
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
                    send_media_message_handler(
                        state.attachment.file_src,
                        response.thumbnail_url
                    );
                }
            }
            if (response.status == 500) {
                if (response.status_message == "Malicious File") {
                    showToast("Invalid File Format!", 3000);
                } else if (
                    response.status_message == "File Size Bigger Than Expected"
                ) {
                    showToast(
                        "Please Enter a file of size less than 5MB!",
                        3000
                    );
                }
            }
        }
    };
    xhttp.send(params);
}

function send_media_message_handler(
    attached_file_src,
    thumbnail_url,
    img_file = ""
) {
    if (state.is_group_chat) {
        send_media_message_to_group(attached_file_src, thumbnail_url, img_file);
    } else if (state.is_user_group) {
        send_media_message_to_user_group(attached_file_src, thumbnail_url, img_file);
    } 
    else {
        send_message_to_internal_chat_user_with_file(
            attached_file_src,
            thumbnail_url,
            img_file
        );
    }
    reset_file_upload_modal();
    auto_resize();
}

function send_message_to_internal_chat_user_with_file(
    attached_file_src,
    thumbnail_url,
    img_file = ""
) {
    if (true || $("#query-file").val().length < 3000) {
        var sentence = $("#query-file").val();
        sentence = $($.parseHTML(sentence)).text().trim();

        $("#query-file").val("");

        sentence = stripHTML(sentence);
        sentence = strip_unwanted_characters(sentence);
        var receiver_username = get_current_receiver_username();
        if (receiver_username == "") {
            console.log(
                "Something went wrong try again later rec username",
                receiver_username
            );
            return;
        }

        var json_string = JSON.stringify({
            message: sentence,
            sender: "user",
            attached_file_src: attached_file_src,
            thumbnail_url: thumbnail_url,
            receiver_username: receiver_username,
        });
        json_string = encrypt_variable(json_string);
        json_string = encodeURIComponent(json_string);

        var csrf_token = getCsrfToken();
        var xhttp = new XMLHttpRequest();
        var params = "json_string=" + json_string;
        xhttp.open("POST", "/livechat/save-internal-chat/", true);
        xhttp.setRequestHeader("X-CSRFToken", csrf_token);
        xhttp.setRequestHeader(
            "Content-Type",
            "application/x-www-form-urlencoded"
        );
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                console.log("chat send by agent saved");
            }
        };
        xhttp.send(params);

        const chat_console_id = get_current_receiver_token();
        let html = append_internal_chat_file_to_agent(
            attached_file_src,
            sentence,
            false,
            img_file,
            window.SENDER_NAME,
            chat_console_id
        );
        const elem = document.getElementsByClassName("live-chat-temp-file")[0];
        elem.classList.remove("live-chat-temp-file");
        elem.innerHTML = html;

        const receiver_websocket_token = get_current_receiver_token();
        const sender_websocket_token = get_sender_websocket_token();
        let text_message = sentence;
        var message = JSON.stringify({
            text_message: text_message,
            type: "file",
            path: attached_file_src,
            thumbnail: thumbnail_url,
            receiver_token: receiver_websocket_token,
            receiver_username: receiver_username,
            sender_websocket_token: sender_websocket_token,
            sender_name: get_internal_chat_sender_name(),
        });

        send_message_to_internal_chat_socket(message, "User", false);
        internal_chat_scroll_to_bottom(chat_console_id);

        let file_name = attached_file_src.split('/');
        file_name = file_name[file_name.length - 1];
        update_user_chat_info(receiver_websocket_token, text_message, file_name, return_time());

        //   will have to do save msg to local index db
    }
}

function send_media_message_to_user_group(
    attached_file_src,
    thumbnail_url,
    img_file = ""
) {
    if (true || $("#query-file").val().length < 3000) {
        var sentence = $("#query-file").val();
        sentence = $($.parseHTML(sentence)).text().trim();

        $("#query-file").val("");

        sentence = stripHTML(sentence);
        sentence = strip_unwanted_characters(sentence);

        const active_group = state.active_user_group;
        const chat_console_id = active_group.id;

        var json_string = JSON.stringify({
            message: sentence,
            sender: "user",
            attached_file_src: attached_file_src,
            thumbnail_url: thumbnail_url,
            receiver_username: "user_group",
            group_id: active_group.id,
        });
        json_string = encrypt_variable(json_string);
        json_string = encodeURIComponent(json_string);

        var csrf_token = getCsrfToken();
        var xhttp = new XMLHttpRequest();
        var params = "json_string=" + json_string;
        xhttp.open("POST", "/livechat/save-internal-chat/", true);
        xhttp.setRequestHeader("X-CSRFToken", csrf_token);
        xhttp.setRequestHeader(
            "Content-Type",
            "application/x-www-form-urlencoded"
        );
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                console.log("chat send by agent saved");
            }
        };
        xhttp.send(params);

        let html = append_internal_chat_file_to_agent(
            attached_file_src,
            sentence,
            false,
            img_file,
            window.SENDER_NAME,
            chat_console_id
        );
        const elem = document.getElementsByClassName("live-chat-temp-file")[0];
        elem.classList.remove("live-chat-temp-file");
        elem.innerHTML = html;

        let text_message = sentence;
        var temp_message = JSON.stringify({
            text_message: text_message,
            type: "file",
            path: attached_file_src,
            thumbnail: thumbnail_url,
            receiver_token: chat_console_id,
            receiver_username: "user_group",
            sender_websocket_token: chat_console_id,
            sender_name: get_internal_chat_sender_name(),
            sender_username: get_sender_username(),
        });
        send_message_to_internal_chat_socket(temp_message, "User", true);

        // let msg = {
        //     sender: "Agent",
        //     text_message: sentence,
        //     is_attachment: "True",
        // };
        // let attachment_name = attached_file_src.split("/");
        // msg.attachment_name = attachment_name[attachment_name.length - 1];
        // // append_message_in_chat_icon(session_id, msg);
        internal_chat_scroll_to_bottom(chat_console_id);

        //   will have to do save msg to local index db
    }
}

function append_internal_chat_file_to_agent(
    attached_file_src,
    message,
    flag_not_seen,
    img_file,
    sender_name,
    chat_console_id,
    time = return_time()
) {
    const session_id = chat_console_id;
    var len = attached_file_src.split("/").length;
    
    let blue_ticks = state.tick.single;
    let custom_class = 'single_tick';
    if (flag_not_seen == state.is_delivered) {
        blue_ticks = state.tick.double;
        custom_class = 'double_tick';
    } else if (flag_not_seen == state.is_read) {
        blue_ticks = state.tick.blue;
        custom_class = 'blue_tick';
    }

    message = livechat_linkify(message);

    let html = "";
    const icons = get_icons();
    if (is_pdf(attached_file_src)) {
        html = `<div class="live-chat-agent-image">${get_user_initial(
            sender_name
        )}</div>
                    <div class="live-chat-agent-message-bubble file-attachement-download">
                        <div style="width: 50px;  display: inline-block;">
                        ${icons.pdf}
                        </div>
                        <div class="file-attachment-path"><span id="custom-text-attach">${
                            attached_file_src.split("/")[len - 1]
                        }</span><br>
                        <a href="${attached_file_src}" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>
                        <div style="width: 30px;cursor: pointer;  display: inline-block; float: right; margin-top: 12px;">
                        ${get_doc_path_html(attached_file_src)}
                        </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area">${message}</div>`;
        }

        html += `</div><div class="live-chat-agent-message-time">
                    ${time}
                    <div data-time="${Date.parse(new Date())}" class="blue_tick-${session_id} ${custom_class}">${blue_ticks}</div>
                </div>`;
    } else if (is_txt(attached_file_src)) {
        html = `<div class="live-chat-agent-image">${get_user_initial(
            sender_name
        )}</div>
        <div class="live-chat-agent-message-bubble file-attachement-download">
            <div style="width: 50px;  display: inline-block;">
            ${icons.txt}
            </div>
            <div class="file-attachment-path"><span id="custom-text-attach">${
                attached_file_src.split("/")[len - 1]
            }</span><br>
            <a href="${attached_file_src}" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>
            <div style="width: 30px;cursor: pointer;  display: inline-block; float: right; margin-top: 12px;">
            ${get_doc_path_html(attached_file_src)}
            </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area">${message}</div>`;
        }

        html += `</div><div class="live-chat-agent-message-time">
                ${time}
                <div data-time="${Date.parse(new Date())}" class="blue_tick-${session_id} ${custom_class}">${blue_ticks}</div>
            </div>`;
    } else if (is_docs(attached_file_src)) {
        html = `<div class="live-chat-agent-image">${get_user_initial(
            sender_name
        )}</div>
        <div class="live-chat-agent-message-bubble file-attachement-download">
            <div style="width: 50px;  display: inline-block;">
            ${icons.doc}
            </div>
            <div class="file-attachment-path"><span id="custom-text-attach">${
                attached_file_src.split("/")[len - 1]
            }</span><br>
            <a href="${attached_file_src}" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>
            <div style="width: 30px;cursor: pointer;  display: inline-block; float: right; margin-top: 12px;">
            ${get_doc_path_html(attached_file_src)}
            </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area">${message}</div>`;
        }

        html += `</div><div class="live-chat-agent-message-time">
                ${time}
                <div data-time="${Date.parse(new Date())}" class="blue_tick-${session_id} ${custom_class}">${blue_ticks}</div>
            </div>`;
    } else if (is_excel(attached_file_src)) {
        html = `<div class="live-chat-agent-image">${get_user_initial(
            sender_name
        )}</div>
        <div class="live-chat-agent-message-bubble file-attachement-download">
            <div style="width: 50px;  display: inline-block;">
            ${icons.excel}
            </div>
            <div class="file-attachment-path"><span id="custom-text-attach">${
                attached_file_src.split("/")[len - 1]
            }</span><br>
            <a href="${attached_file_src}" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>
            <div style="width: 30px;cursor: pointer;  display: inline-block; float: right; margin-top: 12px;">
            ${get_doc_path_html(attached_file_src)}
            </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area">${message}</div>`;
        }

        html += `</div><div class="live-chat-agent-message-time">
                ${time}
                <div data-time="${Date.parse(new Date())}" class="blue_tick-${session_id} ${custom_class}">${blue_ticks}</div>
            </div>`;
    } else if (is_image(attached_file_src)) {
        html = `<div class="live-chat-agent-image">${get_user_initial(
            sender_name
        )}</div>
                        <div class="live-chat-agent-message-bubble-image-attachment">
                            <div class="slideshow-container" value="1">
                                <div class="mySlides livechat-slider-card">
                                    ${get_image_path_html(
                                        attached_file_src,
                                        img_file
                                    )}
                                    <div style="text-align: left;">
                                        <h5 style="overflow-wrap: break-word; ">${
                                            attached_file_src.split("/")[
                                                len - 1
                                            ]
                                        }</h5>
                                        <a href="${attached_file_src}" target="_blank"><span style="position: absolute; top: 8.5rem; right: 8px;"><svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M11.875 11.25H3.125C2.77982 11.25 2.5 11.5298 2.5 11.875C2.5 12.2202 2.77982 12.5 3.125 12.5H11.875C12.2202 12.5 12.5 12.2202 12.5 11.875C12.5 11.5298 12.2202 11.25 11.875 11.25Z" fill="#757575"/>
                                        <path d="M2.5 10.625V11.875C2.5 12.2202 2.77982 12.5 3.125 12.5C3.47018 12.5 3.75 12.2202 3.75 11.875V10.625C3.75 10.2798 3.47018 10 3.125 10C2.77982 10 2.5 10.2798 2.5 10.625Z" fill="#757575"/>
                                        <path d="M11.25 10.625V11.875C11.25 12.2202 11.5298 12.5 11.875 12.5C12.2202 12.5 12.5 12.2202 12.5 11.875V10.625C12.5 10.2798 12.2202 10 11.875 10C11.5298 10 11.25 10.2798 11.25 10.625Z" fill="#757575"/>
                                        <path d="M7.50003 9.375C7.37046 9.37599 7.24378 9.33667 7.13753 9.2625L4.63753 7.5C4.50279 7.40442 4.41137 7.25937 4.38326 7.09658C4.35515 6.93379 4.39264 6.76649 4.48753 6.63125C4.5349 6.56366 4.59518 6.50611 4.66491 6.46194C4.73463 6.41777 4.81242 6.38785 4.89377 6.37391C4.97512 6.35996 5.05843 6.36227 5.13889 6.38069C5.21934 6.39911 5.29535 6.43329 5.36253 6.48125L7.50003 7.975L9.62503 6.375C9.75764 6.27555 9.92432 6.23284 10.0884 6.25628C10.2525 6.27973 10.4006 6.36739 10.5 6.5C10.5995 6.63261 10.6422 6.7993 10.6187 6.96339C10.5953 7.12749 10.5076 7.27555 10.375 7.375L7.87503 9.25C7.76685 9.33114 7.63526 9.375 7.50003 9.375Z" fill="#757575"/>
                                        <path d="M7.5 8.125C7.33424 8.125 7.17527 8.05915 7.05806 7.94194C6.94085 7.82473 6.875 7.66576 6.875 7.5V2.5C6.875 2.33424 6.94085 2.17527 7.05806 2.05806C7.17527 1.94085 7.33424 1.875 7.5 1.875C7.66576 1.875 7.82473 1.94085 7.94194 2.05806C8.05915 2.17527 8.125 2.33424 8.125 2.5V7.5C8.125 7.66576 8.05915 7.82473 7.94194 7.94194C7.82473 8.05915 7.66576 8.125 7.5 8.125Z" fill="#757575"/>
                                        </svg>
                                        </span></a>`;

        if (message != "") {
            html += `<p style="overflow-wrap: break-word;">${message}</p>`;
        }

        html += `</div>
                    </div>
                </div>
                
                </div>
                <div class="live-chat-agent-message-time">
                ${time}
                <div data-time="${Date.parse(new Date())}" class="blue_tick-${session_id} ${custom_class}">${blue_ticks}</div>
                </div>`;
    } else if (is_video(attached_file_src)) {
        html = `<div class="live-chat-agent-image">${get_user_initial(
            sender_name
        )}</div>
                        <div class="live-chat-agent-message-bubble-image-attachment">
                            <div class="slideshow-container" value="1">
                                <div class="mySlides livechat-slider-card">
                                    ${get_video_path_html(attached_file_src)}
                                    <div style="text-align: left;">
                                        <h5 style="overflow-wrap: break-word; ">${
                                            attached_file_src.split("/")[
                                                len - 1
                                            ]
                                        }</h5>`;

        if (message != "") {
            html += `<p style="overflow-wrap: break-word;">${message}</p>`;
        }

        html += `</div>
                    </div>
                </div>
                
                </div>
                <div class="live-chat-agent-message-time">
                ${time}
                <div data-time="${Date.parse(new Date())}" class="blue_tick-${session_id} ${custom_class}">${blue_ticks}</div>
                </div>`;
    }

    return html;
}
function append_temp_file_to_internal_chat(name, sender_name) {
    const chat_console_id = get_current_receiver_token();
    let message = $("#query-file").val();
    message = stripHTML(message);
    message = strip_unwanted_characters(message);
    const session_id = chat_console_id;
    let html = "";
    if (!state.date_set.has('Today')) {
        state.date_set.add('Today');
        html += get_chat_date_html('Today');
    }

    const icons = get_icons();
    if (is_pdf(name)) {
        html += `<div class="live-chat-agent-message-wrapper live-chat-temp-file">
        <div class="live-chat-agent-image">${get_user_initial(
            sender_name
        )}</div>
        <div class="live-chat-agent-message-bubble file-attachement-download">
            <div style="width: 50px;  display: inline-block;">
            ${icons.pdf}
            </div>
            <div class="file-attachment-path"><span id="custom-text-attach">${name}</span><br>
            </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area">${message}</div>`;
        }

        html += `</div><div class="live-chat-agent-message-time">
                    sending...
                </div></div>`;
    } else if (is_txt(name)) {
        html += `<div class="live-chat-agent-message-wrapper live-chat-temp-file">
        <div class="live-chat-agent-image">${get_user_initial(
            sender_name
        )}</div>
        <div class="live-chat-agent-message-bubble file-attachement-download">
            <div style="width: 50px;  display: inline-block;">
            ${icons.txt}
            </div>
            <div class="file-attachment-path"><span id="custom-text-attach">${name}</span><br>
            </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area">${message}</div>`;
        }

        html += `</div><div class="live-chat-agent-message-time">
                    sending...
                </div></div>`;
    } else if (is_docs(name)) {
        html += `<div class="live-chat-agent-message-wrapper live-chat-temp-file">
        <div class="live-chat-agent-image">${get_user_initial(
            sender_name
        )}</div>
        <div class="live-chat-agent-message-bubble file-attachement-download">
            <div style="width: 50px;  display: inline-block;">
            ${icons.doc}
            </div>
            <div class="file-attachment-path"><span id="custom-text-attach">${name}</span><br>
            </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area">${message}</div>`;
        }

        html += `</div><div class="live-chat-agent-message-time">
                    sending...
                </div></div>`;
    } else if (is_excel(name)) {
        html += `<div class="live-chat-agent-message-wrapper live-chat-temp-file">
        <div class="live-chat-agent-image">${get_user_initial(
            sender_name
        )}</div>
        <div class="live-chat-agent-message-bubble file-attachement-download">
            <div style="width: 50px;  display: inline-block;">
            ${icons.excel}
            </div>
            <div class="file-attachment-path"><span id="custom-text-attach">${name}</span><br>
            </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area">${message}</div>`;
        }

        html += `</div><div class="live-chat-agent-message-time">
                    sending...
                </div></div>`;
    } else if (is_image(name)) {
        html += `<div class="live-chat-agent-message-wrapper live-chat-temp-file">
                    <div class="live-chat-agent-image">${get_user_initial(
                        sender_name
                    )}</div>
                        <div class="live-chat-agent-message-bubble-image-attachment">
                            <div class="slideshow-container" value="1">
                                <div class="mySlides livechat-slider-card">
                                    ${get_image_path_html(name)}
                                    <div style="text-align: left;">
                                        <h5 style="overflow-wrap: break-word; ">${name}</h5>`;

        if (message != "") {
            html += `<p style="overflow-wrap: break-word;">${message}</p>`;
        }

        html += `</div>
                    </div>
                </div>
                
                </div>
                <div class="live-chat-agent-message-time">
                sending...
                </div></div>`;
    } else if (is_video(name)) {
        html += `<div class="live-chat-agent-message-wrapper live-chat-temp-file">
                    <div class="live-chat-agent-image">${get_user_initial(
                        sender_name
                    )}</div>
                        <div class="live-chat-agent-message-bubble-image-attachment">
                            <div class="slideshow-container" value="1">
                                <div class="mySlides livechat-slider-card">
                                    ${get_video_path_html(name)}
                                    <div style="text-align: left;">
                                        <h5 style="overflow-wrap: break-word; ">${name}</h5>`;

        if (message != "") {
            html += `<p style="overflow-wrap: break-word;">${message}</p>`;
        }

        html += `</div>
                    </div>
                </div>
                
                </div>
                <div class="live-chat-agent-message-time">
                sending...
                </div></div>`;
    }

    $(`#style-2_${session_id}`).append(html);
    // remove_message_diffrentiator(session_id);
    internal_chat_scroll_to_bottom(session_id);
}

// /////////////////////////////////////////////////////////////////////// attachment end ////////////////////////////////////////////////////

function update_internal_chat_message_history(is_more_chat_loaded) {
    const chat_div = document.getElementById(`style-2_${get_current_receiver_token()}`);
    const scroll_pos = chat_div.scrollHeight - chat_div.scrollTop;

    const json_string = JSON.stringify({
        receiver_username: get_current_receiver_username(),
        chat_index: state.chat_load.index,
    });

    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post('/livechat/update-internal-chat-history/', params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);
            
            if (response.status == 200) {
                let message_history = response.message_history;
                const last_seen_time = response.last_seen_time;
                const last_seen_on_chat = response.last_seen_on_chat;

                state.chat_history[get_current_receiver_token()] = message_history;

                const loader_div = document.getElementById(`more-chat-loader_${get_current_receiver_token()}`);
                if (loader_div) {
                    loader_div.remove();
                }

                append_internal_message_history(message_history, last_seen_time, last_seen_on_chat, is_more_chat_loaded);

                if (is_more_chat_loaded) {
                    chat_div.scrollTop = chat_div.scrollHeight - scroll_pos;
                }

                state.chat_load.index = state.chat_load.index + state.chat_load.limit;
                state.chat_load.is_completed = response.all_chat_loaded;
            } else {
                append_error_loading_customer_details_html();
            }
        })
        .catch((err) => {
            console.log(err);
            console.log("Unable to load customer details. Please try again later.");
        });
}

function append_error_loading_customer_details_html() {
    let html = `<div class="live-chat-customer-details-todo">`;

    html += `<div class="live-chat-customer-name">
                <div class="live-chat-mobile-display back-arrow">
                    <img src="/static/LiveChatApp/img/mobile-back.svg" alt="Back arrow" id="live-chat-customer-details-closer" onclick="close_customer_details()">
                </div>`;

    html += `<div class="live-chat-client-image"> </div>
            <p> </p>
            <button class="customer-details-refresh-button" id="refresh_customer_details_btn">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M14.7015 5.29286C13.3432 3.93453 11.4182 3.15119 9.30154 3.36786C6.2432 3.67619 3.72654 6.15953 3.38487 9.21786C2.92654 13.2595 6.05154 16.6679 9.9932 16.6679C12.6515 16.6679 14.9349 15.1095 16.0015 12.8679C16.2682 12.3095 15.8682 11.6679 15.2515 11.6679C14.9432 11.6679 14.6515 11.8345 14.5182 12.1095C13.5765 14.1345 11.3182 15.4179 8.85154 14.8679C7.00154 14.4595 5.50987 12.9512 5.1182 11.1012C4.4182 7.86786 6.87654 5.00119 9.9932 5.00119C11.3765 5.00119 12.6099 5.57619 13.5099 6.48453L12.2515 7.74286C11.7265 8.26786 12.0932 9.16786 12.8349 9.16786H15.8265C16.2849 9.16786 16.6599 8.79286 16.6599 8.33453V5.34286C16.6599 4.60119 15.7599 4.22619 15.2349 4.75119L14.7015 5.29286Z" fill="#717171"/>
                </svg>
            </button>
        </div><br><div id="livechat-customer-all-details"><p>Failed to load customer details.</p></div>`;

    document.getElementById(
        "live-chat-customer-details-sidebar"
    ).innerHTML = html;
}

function append_internal_message_history(message_history, last_seen_time, last_seen_on_chat, is_more_chat_loaded) {
    const session_id = get_current_receiver_token();
    let unread_message_count = localStorage.getItem(`unread_message_count-${session_id}`);
    set_zero_unread_message_count(session_id);
    append_unread_msg_count_in_chat_icon(session_id, 0)
    var unread_html = get_unread_message_diffrentiator_html(unread_message_count, session_id);
    let old_message_count = message_history.length - unread_message_count;

    let html = ``;
    for (var item = message_history.length-1; item >= 0; item--) {
        old_message_count--;
        if(old_message_count == -1) html += unread_html;

        let message = message_history[item];

        const message_date = get_message_date(parseInt(message.time_in_minisec));

        if (!state.date_set.has(message_date)) {
            state.date_set.add(message_date);

            html += get_chat_date_html(message_date);
        }

        if (message.sender == "CurrentUser") {
            let flag_not_seen = state.is_sent;

            if (last_seen_time >= message.time_in_minisec) {
                flag_not_seen = state.is_delivered;
            }

            if (last_seen_on_chat >= message.time_in_minisec) {
                flag_not_seen = state.is_read;
            }

            if(message.is_replied_message) {

                html += append_replied_message(message, session_id, "agent", flag_not_seen);
            } else {
                if (message.attached_file_src != "") {
                    html += get_file_to_agent_html(
                        message.attached_file_src,
                        message.message,
                        message.sender_name,
                        flag_not_seen,
                        message.file,
                        session_id,
                        "",
                        message.time,
                        message.time_in_minisec
                    );
                } else {
                    html += get_response_user_html(
                        message.message,
                        message.sender_name,
                        flag_not_seen,
                        session_id,
                        message.time,
                        message.time_in_minisec,
                    );
                }
            }
        } else if (message.sender == "ReceiverUser") {
            if(message.is_replied_message) {

                html += append_replied_message(message, session_id, "client");
            } else {

                if (message.attached_file_src != "") {
                    html += get_file_to_agent_html_sent_customer(
                        message.attached_file_src,
                        message.message,
                        message.sender_name,
                        message.file,
                        message.time
                    );
                } else if (message.message != "") {
                    html += get_response_server_html(
                        message.message,
                        message.sender_name,
                        message.time
                    );
                }
            }
        } else if (message.sender.toLowerCase() == "system") {
            if (
                message.message.includes("changed the") ||
                message.message.includes("removed") ||
                message.message.includes("added")
            ) {
                message.message = message.message.replace(
                    " " + state.sender_username + " ",
                    " you "
                );
                if (message.sender_username == state.sender_username) {
                    message.message = "You " + message.message;
                } else {
                    message.message =
                        message.sender_username + " " + message.message;
                }
            } else if (message.message.includes("has left the chat")) {
                if (message.sender_username == state.sender_username) {
                    message.message = "You have left the chat";
                }
            }
            html += get_system_text_response_html(
                message.message,
                message.time
            );
            if (
                message.message.includes("Customer left the chat") ||
                message.message.includes("Due to inactivity chat has ended")
            ) {
                if (state.customer_left_chat[session_id] == undefined) {
                    state.customer_left_chat[session_id] = true;
                }
            }
        }
    }

    if(is_more_chat_loaded) {
        $(`#style-2_${session_id}`).prepend(html);
    } else {
        $(`#style-2_${session_id}`).html("");
        $(`#style-2_${session_id}`).append(html);
        internal_chat_scroll_to_bottom(session_id);
    }
}

function get_file_to_agent_html_sent_customer(
    attached_file_src,
    text_message,
    sender_name,
    thumbnail_url,
    time = return_time()
) {
    let html = "";
    var len = attached_file_src.split("/").length;
    if (is_pdf(attached_file_src)) {
        html =
            '<div class="live-chat-client-message-wrapper">\
                        <div class="live-chat-client-image">' +
            get_user_initial(sender_name) +
            '</div>\
            <div class="group-chat-element live-chat-client-name-with-message">' +
            sender_name +
            '</div>\
                        <div class="live-chat-client-message-bubble file-attachement-download">\
                        <div style="    width: 50px; height: 45px; display: inline-block;"><svg width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">\
                            <path d="M31.6312 2.71948L38.934 10.332V39.2805H11.6537V39.375H39.0272V10.4278L31.6312 2.71948Z" fill="#909090"></path>\
                            <path d="M31.5406 2.625H11.5604V39.2805H38.9339V10.3333L31.5393 2.625" fill="#F4F4F4"></path>\
                            <path d="M11.3596 4.59375H2.97272V13.5542H29.354V4.59375H11.3596Z" fill="#7A7B7C"></path>\
                            <path d="M29.4943 13.4019H3.14328V4.43494H29.4943V13.4019Z" fill="#DD2025"></path>\
                            <path d="M11.8808 5.95087H10.1653V12.2509H11.5146V10.1259L11.8125 10.143C12.102 10.138 12.3888 10.0862 12.6617 9.98943C12.901 9.90713 13.1211 9.77721 13.3088 9.60749C13.4997 9.44582 13.6503 9.24177 13.7485 9.01162C13.8801 8.62902 13.9271 8.22241 13.8863 7.81987C13.8781 7.53231 13.8277 7.24752 13.7367 6.97462C13.6538 6.77762 13.5308 6.60003 13.3756 6.45315C13.2204 6.30627 13.0362 6.19332 12.835 6.12149C12.6609 6.05849 12.4811 6.01277 12.2982 5.98499C12.1596 5.96361 12.0197 5.95221 11.8795 5.95087H11.8808ZM11.6314 8.96174H11.5146V7.01924H11.7679C11.8797 7.01118 11.9919 7.02834 12.0962 7.06946C12.2004 7.11058 12.2941 7.17461 12.3703 7.2568C12.5283 7.46814 12.6126 7.72537 12.6105 7.98918C12.6105 8.31205 12.6105 8.60474 12.3192 8.8108C12.1092 8.92626 11.8703 8.97824 11.6314 8.96043" fill="#464648"></path>\
                            <path d="M16.4495 5.93381C16.3038 5.93381 16.162 5.94431 16.0623 5.94825L15.7499 5.95612H14.7262V12.2561H15.931C16.3915 12.2687 16.8499 12.1907 17.2803 12.0264C17.6267 11.889 17.9334 11.6676 18.1728 11.382C18.4056 11.0938 18.5727 10.7583 18.6624 10.3989C18.7655 9.99189 18.8158 9.57326 18.812 9.15337C18.8374 8.65745 18.7991 8.16032 18.6978 7.67419C18.6017 7.31635 18.4217 6.98656 18.1728 6.71212C17.9775 6.49052 17.7384 6.31177 17.4706 6.18712C17.2406 6.0807 16.9987 6.00227 16.75 5.9535C16.6512 5.93716 16.551 5.9297 16.4508 5.93119L16.4495 5.93381ZM16.2119 11.0985H16.0807V7.077H16.0977C16.3683 7.04587 16.6421 7.09469 16.8852 7.21744C17.0633 7.35961 17.2084 7.53874 17.3105 7.74244C17.4207 7.95681 17.4842 8.1921 17.4969 8.43281C17.5087 8.72156 17.4969 8.95781 17.4969 9.15337C17.5022 9.37865 17.4877 9.60395 17.4535 9.82669C17.4131 10.0554 17.3383 10.2766 17.2317 10.4829C17.1111 10.6748 16.9481 10.8364 16.7553 10.9554C16.5934 11.0602 16.4016 11.109 16.2093 11.0946" fill="#464648"></path>\
                            <path d="M22.8769 5.95612H19.6875V12.2561H21.0367V9.75712H22.743V8.58637H21.0367V7.12687H22.8742V5.95612" fill="#464648"></path>\
                            <path d="M28.5875 26.5847C28.5875 26.5847 32.7717 25.8261 32.7717 27.2554C32.7717 28.6847 30.1795 28.1033 28.5875 26.5847ZM25.4939 26.6936C24.8291 26.8405 24.1812 27.0556 23.5606 27.3355L24.0856 26.1542C24.6106 24.9729 25.1553 23.3625 25.1553 23.3625C25.7817 24.4169 26.5106 25.4069 27.3314 26.3183C26.7124 26.4106 26.099 26.5367 25.4939 26.6963V26.6936ZM23.8375 18.1624C23.8375 16.9168 24.2405 16.5769 24.5541 16.5769C24.8678 16.5769 25.2209 16.7278 25.2327 17.8093C25.1305 18.8968 24.9028 19.9688 24.5541 21.004C24.0766 20.1349 23.8294 19.158 23.8362 18.1663L23.8375 18.1624ZM17.7357 31.9646C16.4521 31.1968 20.4277 28.833 21.1482 28.7569C21.1443 28.7582 19.0797 32.7679 17.7357 31.9646ZM33.9936 27.4247C33.9805 27.2935 33.8624 25.8405 31.2768 25.9022C30.199 25.8848 29.1218 25.9608 28.0572 26.1293C27.0259 25.0903 26.1378 23.9184 25.4165 22.6446C25.8709 21.3313 26.146 19.9627 26.2342 18.5758C26.1961 17.0008 25.8194 16.0978 24.6119 16.111C23.4044 16.1241 23.2285 17.1806 23.3873 18.753C23.5429 19.8096 23.8363 20.8413 24.2601 21.8216C24.2601 21.8216 23.7023 23.5581 22.9647 25.2853C22.2271 27.0126 21.7231 27.9182 21.7231 27.9182C20.4404 28.3358 19.2329 28.9561 18.1465 29.7557C17.065 30.7624 16.6253 31.5354 17.195 32.3085C17.6858 32.9753 19.4039 33.1262 20.9395 31.1141C21.7555 30.0749 22.5009 28.9822 23.1708 27.8434C23.1708 27.8434 25.5123 27.2016 26.2407 27.0257C26.9691 26.8498 27.8498 26.7107 27.8498 26.7107C27.8498 26.7107 29.9879 28.8619 32.0498 28.7858C34.1118 28.7096 34.012 27.5533 33.9989 27.4273" fill="#DD2025"></path>\
                            <path d="M31.4397 2.72607V10.4344H38.833L31.4397 2.72607Z" fill="#909090"></path>\
                            <path d="M31.5408 2.625V10.3333H38.9341L31.5408 2.625Z" fill="#F4F4F4"></path>\
                            <path d="M11.7797 5.84982H10.0642V12.1498H11.4187V10.0262L11.718 10.0433C12.0075 10.0383 12.2943 9.98642 12.5672 9.8897C12.8064 9.80737 13.0265 9.67745 13.2142 9.50776C13.4038 9.34565 13.553 9.14164 13.65 8.91189C13.7816 8.52929 13.8286 8.12268 13.7878 7.72014C13.7796 7.43258 13.7292 7.14778 13.6382 6.87489C13.5553 6.67789 13.4324 6.5003 13.2771 6.35342C13.1219 6.20654 12.9378 6.09359 12.7365 6.02176C12.5617 5.95815 12.381 5.91198 12.1971 5.88395C12.0585 5.86257 11.9186 5.85116 11.7784 5.84982H11.7797ZM11.5303 8.8607H11.4135V6.9182H11.6681C11.7799 6.91014 11.8921 6.9273 11.9964 6.96842C12.1006 7.00954 12.1943 7.07356 12.2706 7.15576C12.4285 7.36709 12.5128 7.62433 12.5107 7.88814C12.5107 8.21101 12.5107 8.5037 12.2194 8.70976C12.0095 8.82521 11.7705 8.8772 11.5316 8.85939" fill="white"></path>\
                            <path d="M16.3486 5.83277C16.203 5.83277 16.0612 5.84327 15.9615 5.8472L15.653 5.85508H14.6293V12.1551H15.8341C16.2946 12.1677 16.7531 12.0897 17.1834 11.9254C17.5298 11.788 17.8365 11.5665 18.0759 11.281C18.3087 10.9928 18.4758 10.6573 18.5655 10.2979C18.6686 9.89085 18.7189 9.47222 18.7151 9.05233C18.7405 8.55641 18.7022 8.05928 18.6009 7.57314C18.5048 7.21531 18.3248 6.88551 18.0759 6.61108C17.8806 6.38948 17.6415 6.21073 17.3737 6.08608C17.1437 5.97966 16.9018 5.90122 16.6531 5.85245C16.5543 5.83612 16.4541 5.82865 16.3539 5.83014L16.3486 5.83277ZM16.115 10.9975H15.9838V6.97595H16.0008C16.2714 6.94482 16.5452 6.99364 16.7883 7.11639C16.9664 7.25857 17.1115 7.43769 17.2136 7.64139C17.3238 7.85577 17.3873 8.09106 17.4 8.33177C17.4118 8.62052 17.4 8.85677 17.4 9.05233C17.4053 9.2776 17.3908 9.50291 17.3566 9.72564C17.3162 9.95432 17.2414 10.1756 17.1348 10.3819C17.0142 10.5737 16.8512 10.7354 16.6584 10.8544C16.4965 10.9591 16.3047 11.008 16.1124 10.9935" fill="white"></path>\
                            <path d="M22.7758 5.85507H19.5864V12.1551H20.9356V9.65607H22.6419V8.48532H20.9356V7.02582H22.7731V5.85507" fill="white"></path>\
                            </svg></div>\
                            <div style="width: 120px; height: 50px; display: inline-block;"><span id="custom-text-attach">' +
            attached_file_src.split("/")[len - 1] +
            '</span><br>\
            <a href="' + attached_file_src + '" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>\
                            <div style="width: 30px;cursor: pointer; height: 35px; display: inline-block;">\
                            ' +
            get_doc_path_html(attached_file_src) +
            '\
                            </div>\
                            <div class="upload-file-text-area" style="color: white;">' +
            text_message +
            '</div>\
                        </div>\
                        <div class="live-chat-client-message-time">\
                            ' +
            time +
            "\
                        </div>\
                    </div>";
    } else if (is_txt(attached_file_src)) {
        html =
            '<div class="live-chat-agent-message-wrapper">\
                            <div class="live-chat-agent-image">' +
            get_user_initial(sender_name) +
            '</div>\
            <div class="group-chat-element live-chat-client-name-with-message">' +
            sender_name +
            '</div>\
                            <div class="live-chat-agent-message-bubble file-attachement-download">\
                            <div style="    width: 50px; height: 45px; display: inline-block;"><svg width="32" height="42" viewBox="0 0 32 42" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M9.1875 18.375C8.8394 18.375 8.50556 18.5133 8.25942 18.7594C8.01328 19.0056 7.875 19.3394 7.875 19.6875C7.875 20.0356 8.01328 20.3694 8.25942 20.6156C8.50556 20.8617 8.8394 21 9.1875 21H22.3125C22.6606 21 22.9944 20.8617 23.2406 20.6156C23.4867 20.3694 23.625 20.0356 23.625 19.6875C23.625 19.3394 23.4867 19.0056 23.2406 18.7594C22.9944 18.5133 22.6606 18.375 22.3125 18.375H9.1875ZM7.875 24.9375C7.875 24.5894 8.01328 24.2556 8.25942 24.0094C8.50556 23.7633 8.8394 23.625 9.1875 23.625H22.3125C22.6606 23.625 22.9944 23.7633 23.2406 24.0094C23.4867 24.2556 23.625 24.5894 23.625 24.9375C23.625 25.2856 23.4867 25.6194 23.2406 25.8656C22.9944 26.1117 22.6606 26.25 22.3125 26.25H9.1875C8.8394 26.25 8.50556 26.1117 8.25942 25.8656C8.01328 25.6194 7.875 25.2856 7.875 24.9375ZM7.875 30.1875C7.875 29.8394 8.01328 29.5056 8.25942 29.2594C8.50556 29.0133 8.8394 28.875 9.1875 28.875H14.4375C14.7856 28.875 15.1194 29.0133 15.3656 29.2594C15.6117 29.5056 15.75 29.8394 15.75 30.1875C15.75 30.5356 15.6117 30.8694 15.3656 31.1156C15.1194 31.3617 14.7856 31.5 14.4375 31.5H9.1875C8.8394 31.5 8.50556 31.3617 8.25942 31.1156C8.01328 30.8694 7.875 30.5356 7.875 30.1875Z" fill="black"/>\
                                <path d="M19.6875 0H5.25C3.85761 0 2.52226 0.553124 1.53769 1.53769C0.553123 2.52226 0 3.85761 0 5.25V36.75C0 38.1424 0.553123 39.4777 1.53769 40.4623C2.52226 41.4469 3.85761 42 5.25 42H26.25C27.6424 42 28.9777 41.4469 29.9623 40.4623C30.9469 39.4777 31.5 38.1424 31.5 36.75V11.8125L19.6875 0ZM19.6875 2.625V7.875C19.6875 8.91929 20.1023 9.92081 20.8408 10.6592C21.5792 11.3977 22.5807 11.8125 23.625 11.8125H28.875V36.75C28.875 37.4462 28.5984 38.1139 28.1062 38.6062C27.6139 39.0984 26.9462 39.375 26.25 39.375H5.25C4.55381 39.375 3.88613 39.0984 3.39384 38.6062C2.90156 38.1139 2.625 37.4462 2.625 36.75V5.25C2.625 4.55381 2.90156 3.88613 3.39384 3.39384C3.88613 2.90156 4.55381 2.625 5.25 2.625H19.6875Z" fill="black"/>\
                                </svg></div>\
                                <div style="width: 120px; height: 50px; display: inline-block;"><span id="custom-text-attach">' +
            attached_file_src.split("/")[len - 1] +
            '</span><br>\
            <a href="' + attached_file_src + '" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>\
                                <div style="width: 30px;cursor: pointer; height: 35px; display: inline-block;">\
                                ' +
            get_doc_path_html(attached_file_src) +
            '\
                                </div>\
                            <div class="upload-file-text-area" style="color: white;">' +
            text_message +
            '</div>\
                            </div>\
                            <div class="live-chat-agent-message-time">\
                                ' +
            time +
            "\
                                " +
            blue_ticks +
            "\
                            </div>\
                        </div>";
    } else if (is_docs(attached_file_src)) {
        html =
            '<div class="live-chat-client-message-wrapper">\
                        <div class="live-chat-client-image">' +
            get_user_initial(sender_name) +
            '</div>\
            <div class="group-chat-element live-chat-client-name-with-message">' +
            sender_name +
            '</div>\
                        <div class="live-chat-client-message-bubble file-attachement-download">\
                        <div style="    width: 50px; height: 45px; display: inline-block;">\
                        <svg width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">\
                            <path d="M37.8079 3.9375H12.7378C12.5324 3.93733 12.3289 3.97763 12.139 4.05609C11.9491 4.13455 11.7766 4.24965 11.6312 4.39481C11.4858 4.53996 11.3704 4.71233 11.2916 4.90208C11.2128 5.09183 11.1722 5.29524 11.172 5.50069V12.4688L25.7001 16.7344L39.375 12.4688V5.50069C39.3748 5.29513 39.3341 5.09161 39.2553 4.90178C39.1764 4.71194 39.0609 4.53951 38.9154 4.39434C38.7698 4.24917 38.5971 4.1341 38.4071 4.05571C38.2171 3.97733 38.0134 3.93716 37.8079 3.9375Z" fill="#41A5EE"/>\
                            <path d="M39.375 12.4688H11.172V21L25.7001 23.5594L39.375 21V12.4688Z" fill="#2B7CD3"/>\
                            <path d="M11.172 21V29.5312L24.8456 31.2375L39.375 29.5312V21H11.172Z" fill="#185ABD"/>\
                            <path d="M12.7378 38.0625H37.8066C38.0122 38.063 38.216 38.023 38.4062 37.9447C38.5964 37.8664 38.7692 37.7513 38.9149 37.6061C39.0606 37.4609 39.1762 37.2884 39.2552 37.0985C39.3341 36.9086 39.3748 36.705 39.375 36.4993V29.5312H11.172V36.4993C11.1722 36.7048 11.2128 36.9082 11.2916 37.0979C11.3704 37.2877 11.4858 37.46 11.6312 37.6052C11.7766 37.7504 11.9491 37.8654 12.139 37.9439C12.3289 38.0224 12.5324 38.0627 12.7378 38.0625Z" fill="#103F91"/>\
                            <path opacity="0.1" d="M21.5696 10.7625H11.172V32.0906H21.5696C21.9839 32.0886 22.3808 31.9234 22.6741 31.6308C22.9674 31.3382 23.1336 30.9418 23.1368 30.5275V12.3257C23.1336 11.9114 22.9674 11.515 22.6741 11.2224C22.3808 10.9298 21.9839 10.7646 21.5696 10.7625Z" fill="black"/>\
                            <path opacity="0.2" d="M20.7152 11.6156H11.172V32.9438H20.7152C21.1295 32.9417 21.5263 32.7765 21.8196 32.4839C22.113 32.1913 22.2792 31.7949 22.2823 31.3806V13.1788C22.2792 12.7645 22.113 12.3681 21.8196 12.0755C21.5263 11.7829 21.1295 11.6177 20.7152 11.6156Z" fill="black"/>\
                            <path opacity="0.2" d="M20.7152 11.6156H11.172V31.2375H20.7152C21.1295 31.2354 21.5263 31.0702 21.8196 30.7776C22.113 30.485 22.2792 30.0886 22.2823 29.6743V13.1788C22.2792 12.7645 22.113 12.3681 21.8196 12.0755C21.5263 11.7829 21.1295 11.6177 20.7152 11.6156Z" fill="black"/>\
                            <path opacity="0.2" d="M19.8607 11.6156H11.172V31.2375H19.8607C20.2751 31.2354 20.6719 31.0702 20.9652 30.7776C21.2585 30.485 21.4248 30.0886 21.4279 29.6743V13.1788C21.4248 12.7645 21.2585 12.3681 20.9652 12.0755C20.6719 11.7829 20.2751 11.6177 19.8607 11.6156Z" fill="black"/>\
                            <path d="M4.19212 11.6156H19.8608C20.2758 11.6153 20.674 11.7797 20.9679 12.0729C21.2617 12.366 21.4272 12.7638 21.4279 13.1788V28.8212C21.4272 29.2362 21.2617 29.634 20.9679 29.9272C20.674 30.2203 20.2758 30.3847 19.8608 30.3844H4.19212C3.98656 30.3847 3.78295 30.3446 3.59291 30.2662C3.40288 30.1878 3.23016 30.0727 3.08462 29.9275C2.93909 29.7824 2.82358 29.6099 2.74472 29.4201C2.66585 29.2303 2.62517 29.0268 2.625 28.8212V13.1788C2.62517 12.9733 2.66585 12.7697 2.74472 12.5799C2.82358 12.3901 2.93909 12.2176 3.08462 12.0725C3.23016 11.9273 3.40288 11.8122 3.59291 11.7338C3.78295 11.6555 3.98656 11.6153 4.19212 11.6156Z" fill="url(#paint0_linear)"/>\
                            <path d="M9.05627 23.6093C9.08645 23.8508 9.10745 24.0608 9.11664 24.2406H9.15339C9.16651 24.0699 9.19539 23.8639 9.2387 23.6237C9.28201 23.3835 9.32008 23.1801 9.35551 23.0134L11.0027 15.9167H13.1342L14.8405 22.9071C14.9398 23.3395 15.0109 23.7779 15.0531 24.2196H15.082C15.1133 23.7896 15.1725 23.3622 15.2591 22.9399L16.6228 15.9075H18.5614L16.1674 26.0768H13.9007L12.2771 19.3489C12.2299 19.1546 12.1765 18.9018 12.117 18.5903C12.0575 18.2788 12.0208 18.0513 12.0068 17.9078H11.9792C11.9608 18.0731 11.9241 18.3186 11.869 18.6441C11.8138 18.9709 11.7705 19.2111 11.7377 19.3686L10.2113 26.0807H7.90652L5.49939 15.9167H7.46814L8.95258 23.0278C8.99688 23.2198 9.03149 23.4138 9.05627 23.6093Z" fill="white"/>\
                            <defs>\
                            <linearGradient id="paint0_linear" x1="5.89837" y1="10.3871" x2="18.1545" y2="31.6129" gradientUnits="userSpaceOnUse">\
                            <stop stop-color="#2368C4"/>\
                            <stop offset="0.5" stop-color="#1A5DBE"/>\
                            <stop offset="1" stop-color="#1146AC"/>\
                            </linearGradient>\
                            </defs>\
                        </svg>\
                            </div>\
                            <div style="width: 120px; height: 50px; display: inline-block;"><span id="custom-text-attach">' +
            attached_file_src.split("/")[len - 1] +
            '</span><br>\
            <a href="' + attached_file_src + '" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>\
                        <div style="width: 30px;cursor: pointer; height: 35px; display: inline-block;">\
                        ' +
            get_doc_path_html(attached_file_src) +
            '\
                        </div><div class="upload-file-text-area" style="color: white;">' +
            text_message +
            '</div></div>\
                        <div class="live-chat-client-message-time">\
                            ' +
            time +
            "\
                        </div>\
                    </div>";
    } else if (is_image(attached_file_src)) {
        html =
            '<div class="live-chat-client-message-wrapper">\
                    <div class="live-chat-client-image">' +
            get_user_initial(sender_name) +
            '</div>\
            <div class="group-chat-element live-chat-client-name-with-message">' +
            sender_name +
            '</div>\
                    <div class="live-chat-client-message-bubble-image-attachment" style="height: unset;">\
                        ' +
            get_image_path_html(attached_file_src, thumbnail_url) +
            '\
                        <div class="file-attach-name-area" style="text-align: left; margin-top: 0px; position: relative;">\
                            <h5 id="custom-text-attach-img" style="padding-left: 0px;">' +
            attached_file_src.split("/")[len - 1] +
            '</h5>\
            <p style="overflow-wrap: break-word;">' +
            text_message +
            '</p>\
                            <a href="' +
            attached_file_src +
            '" target="_blank"><span style="position: absolute; top: 0.6rem; right: 8px;"><svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M11.875 11.25H3.125C2.77982 11.25 2.5 11.5298 2.5 11.875C2.5 12.2202 2.77982 12.5 3.125 12.5H11.875C12.2202 12.5 12.5 12.2202 12.5 11.875C12.5 11.5298 12.2202 11.25 11.875 11.25Z" fill="#757575"/>\
                                <path d="M2.5 10.625V11.875C2.5 12.2202 2.77982 12.5 3.125 12.5C3.47018 12.5 3.75 12.2202 3.75 11.875V10.625C3.75 10.2798 3.47018 10 3.125 10C2.77982 10 2.5 10.2798 2.5 10.625Z" fill="#757575"/>\
                                <path d="M11.25 10.625V11.875C11.25 12.2202 11.5298 12.5 11.875 12.5C12.2202 12.5 12.5 12.2202 12.5 11.875V10.625C12.5 10.2798 12.2202 10 11.875 10C11.5298 10 11.25 10.2798 11.25 10.625Z" fill="#757575"/>\
                                <path d="M7.50003 9.375C7.37046 9.37599 7.24378 9.33667 7.13753 9.2625L4.63753 7.5C4.50279 7.40442 4.41137 7.25937 4.38326 7.09658C4.35515 6.93379 4.39264 6.76649 4.48753 6.63125C4.5349 6.56366 4.59518 6.50611 4.66491 6.46194C4.73463 6.41777 4.81242 6.38785 4.89377 6.37391C4.97512 6.35996 5.05843 6.36227 5.13889 6.38069C5.21934 6.39911 5.29535 6.43329 5.36253 6.48125L7.50003 7.975L9.62503 6.375C9.75764 6.27555 9.92432 6.23284 10.0884 6.25628C10.2525 6.27973 10.4006 6.36739 10.5 6.5C10.5995 6.63261 10.6422 6.7993 10.6187 6.96339C10.5953 7.12749 10.5076 7.27555 10.375 7.375L7.87503 9.25C7.76685 9.33114 7.63526 9.375 7.50003 9.375Z" fill="#757575"/>\
                                <path d="M7.5 8.125C7.33424 8.125 7.17527 8.05915 7.05806 7.94194C6.94085 7.82473 6.875 7.66576 6.875 7.5V2.5C6.875 2.33424 6.94085 2.17527 7.05806 2.05806C7.17527 1.94085 7.33424 1.875 7.5 1.875C7.66576 1.875 7.82473 1.94085 7.94194 2.05806C8.05915 2.17527 8.125 2.33424 8.125 2.5V7.5C8.125 7.66576 8.05915 7.82473 7.94194 7.94194C7.82473 8.05915 7.66576 8.125 7.5 8.125Z" fill="#757575"/>\
                                </svg>\
                                </span></a>\
                        </div></div>\
                        <div class="live-chat-client-message-time">\
                            ' +
            time +
            "\
                            </div>\
                    </div>";
    }

    return html;
}

function get_response_server_html(sentence, sender_name, time = return_time()) {
    sentence = livechat_linkify(sentence);

    sentence = sentence.replace("<p>", "");
    sentence = sentence.replace("</p>", "");
    sentence = sentence.replace("<strong>", "<b>");
    sentence = sentence.replace("</strong>", "</b>");
    sentence = sentence.replace("<em>", "<i>");
    sentence = sentence.replace("</em>", "</i>");
    sentence = sentence.replace("background-color:#ffffff; color:#000000", "");
    sentence = sentence.replace("background-color:#ffffff;", "");

    var html = `<div class="live-chat-client-message-wrapper">
            <div class="live-chat-client-image">
                ${get_user_initial(sender_name)}
            </div>
            <div class="group-chat-element live-chat-client-name-with-message">${sender_name}</div>
            <div class="live-chat-client-message-bubble">
                ${sentence}
            </div>
            <div class="live-chat-client-message-time">
                ${time}
            </div>
        </div>`;

    return html;
}

function get_sender_username() {
    return state.sender_username;
}

function get_is_group_chat() {
    return state.is_group_chat;
}

function set_is_group_chat(value) {
    state.is_group_chat = value;
}

export function set_is_user_group(value) {
    state.is_user_group = value;
}

export function get_is_user_group() {
    return state.is_user_group;
}

function send_message_handler() {
    if (state.is_group_chat) {
        send_message_to_group();
    } else if (state.is_user_group) {
        send_message_to_user_group();
    } else {
        send_internal_message_to_user();
    }
    auto_resize();
}

function append_internal_media_response_server(
    attached_file_src,
    sender_name,
    thumbnail_url,
    text_message,
    time = return_time()
) {
    let html = "";
    var len = attached_file_src.split("/").length;

    if (!state.date_set.has('Today')) {
        state.date_set.add('Today');
        html += get_chat_date_html('Today');
    }

    if (is_pdf(attached_file_src)) {
        html +=
            '<div class="live-chat-client-message-wrapper">\
                        <div class="live-chat-client-image">' +
            get_user_initial(sender_name) +
            '</div>\
            <div class="group-chat-element live-chat-client-name-with-message">' +
            sender_name +
            '</div>\
                        <div class="live-chat-client-message-bubble file-attachement-download">\
                        <div style="    width: 50px; height: 45px; display: inline-block;"><svg width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">\
                            <path d="M31.6312 2.71948L38.934 10.332V39.2805H11.6537V39.375H39.0272V10.4278L31.6312 2.71948Z" fill="#909090"></path>\
                            <path d="M31.5406 2.625H11.5604V39.2805H38.9339V10.3333L31.5393 2.625" fill="#F4F4F4"></path>\
                            <path d="M11.3596 4.59375H2.97272V13.5542H29.354V4.59375H11.3596Z" fill="#7A7B7C"></path>\
                            <path d="M29.4943 13.4019H3.14328V4.43494H29.4943V13.4019Z" fill="#DD2025"></path>\
                            <path d="M11.8808 5.95087H10.1653V12.2509H11.5146V10.1259L11.8125 10.143C12.102 10.138 12.3888 10.0862 12.6617 9.98943C12.901 9.90713 13.1211 9.77721 13.3088 9.60749C13.4997 9.44582 13.6503 9.24177 13.7485 9.01162C13.8801 8.62902 13.9271 8.22241 13.8863 7.81987C13.8781 7.53231 13.8277 7.24752 13.7367 6.97462C13.6538 6.77762 13.5308 6.60003 13.3756 6.45315C13.2204 6.30627 13.0362 6.19332 12.835 6.12149C12.6609 6.05849 12.4811 6.01277 12.2982 5.98499C12.1596 5.96361 12.0197 5.95221 11.8795 5.95087H11.8808ZM11.6314 8.96174H11.5146V7.01924H11.7679C11.8797 7.01118 11.9919 7.02834 12.0962 7.06946C12.2004 7.11058 12.2941 7.17461 12.3703 7.2568C12.5283 7.46814 12.6126 7.72537 12.6105 7.98918C12.6105 8.31205 12.6105 8.60474 12.3192 8.8108C12.1092 8.92626 11.8703 8.97824 11.6314 8.96043" fill="#464648"></path>\
                            <path d="M16.4495 5.93381C16.3038 5.93381 16.162 5.94431 16.0623 5.94825L15.7499 5.95612H14.7262V12.2561H15.931C16.3915 12.2687 16.8499 12.1907 17.2803 12.0264C17.6267 11.889 17.9334 11.6676 18.1728 11.382C18.4056 11.0938 18.5727 10.7583 18.6624 10.3989C18.7655 9.99189 18.8158 9.57326 18.812 9.15337C18.8374 8.65745 18.7991 8.16032 18.6978 7.67419C18.6017 7.31635 18.4217 6.98656 18.1728 6.71212C17.9775 6.49052 17.7384 6.31177 17.4706 6.18712C17.2406 6.0807 16.9987 6.00227 16.75 5.9535C16.6512 5.93716 16.551 5.9297 16.4508 5.93119L16.4495 5.93381ZM16.2119 11.0985H16.0807V7.077H16.0977C16.3683 7.04587 16.6421 7.09469 16.8852 7.21744C17.0633 7.35961 17.2084 7.53874 17.3105 7.74244C17.4207 7.95681 17.4842 8.1921 17.4969 8.43281C17.5087 8.72156 17.4969 8.95781 17.4969 9.15337C17.5022 9.37865 17.4877 9.60395 17.4535 9.82669C17.4131 10.0554 17.3383 10.2766 17.2317 10.4829C17.1111 10.6748 16.9481 10.8364 16.7553 10.9554C16.5934 11.0602 16.4016 11.109 16.2093 11.0946" fill="#464648"></path>\
                            <path d="M22.8769 5.95612H19.6875V12.2561H21.0367V9.75712H22.743V8.58637H21.0367V7.12687H22.8742V5.95612" fill="#464648"></path>\
                            <path d="M28.5875 26.5847C28.5875 26.5847 32.7717 25.8261 32.7717 27.2554C32.7717 28.6847 30.1795 28.1033 28.5875 26.5847ZM25.4939 26.6936C24.8291 26.8405 24.1812 27.0556 23.5606 27.3355L24.0856 26.1542C24.6106 24.9729 25.1553 23.3625 25.1553 23.3625C25.7817 24.4169 26.5106 25.4069 27.3314 26.3183C26.7124 26.4106 26.099 26.5367 25.4939 26.6963V26.6936ZM23.8375 18.1624C23.8375 16.9168 24.2405 16.5769 24.5541 16.5769C24.8678 16.5769 25.2209 16.7278 25.2327 17.8093C25.1305 18.8968 24.9028 19.9688 24.5541 21.004C24.0766 20.1349 23.8294 19.158 23.8362 18.1663L23.8375 18.1624ZM17.7357 31.9646C16.4521 31.1968 20.4277 28.833 21.1482 28.7569C21.1443 28.7582 19.0797 32.7679 17.7357 31.9646ZM33.9936 27.4247C33.9805 27.2935 33.8624 25.8405 31.2768 25.9022C30.199 25.8848 29.1218 25.9608 28.0572 26.1293C27.0259 25.0903 26.1378 23.9184 25.4165 22.6446C25.8709 21.3313 26.146 19.9627 26.2342 18.5758C26.1961 17.0008 25.8194 16.0978 24.6119 16.111C23.4044 16.1241 23.2285 17.1806 23.3873 18.753C23.5429 19.8096 23.8363 20.8413 24.2601 21.8216C24.2601 21.8216 23.7023 23.5581 22.9647 25.2853C22.2271 27.0126 21.7231 27.9182 21.7231 27.9182C20.4404 28.3358 19.2329 28.9561 18.1465 29.7557C17.065 30.7624 16.6253 31.5354 17.195 32.3085C17.6858 32.9753 19.4039 33.1262 20.9395 31.1141C21.7555 30.0749 22.5009 28.9822 23.1708 27.8434C23.1708 27.8434 25.5123 27.2016 26.2407 27.0257C26.9691 26.8498 27.8498 26.7107 27.8498 26.7107C27.8498 26.7107 29.9879 28.8619 32.0498 28.7858C34.1118 28.7096 34.012 27.5533 33.9989 27.4273" fill="#DD2025"></path>\
                            <path d="M31.4397 2.72607V10.4344H38.833L31.4397 2.72607Z" fill="#909090"></path>\
                            <path d="M31.5408 2.625V10.3333H38.9341L31.5408 2.625Z" fill="#F4F4F4"></path>\
                            <path d="M11.7797 5.84982H10.0642V12.1498H11.4187V10.0262L11.718 10.0433C12.0075 10.0383 12.2943 9.98642 12.5672 9.8897C12.8064 9.80737 13.0265 9.67745 13.2142 9.50776C13.4038 9.34565 13.553 9.14164 13.65 8.91189C13.7816 8.52929 13.8286 8.12268 13.7878 7.72014C13.7796 7.43258 13.7292 7.14778 13.6382 6.87489C13.5553 6.67789 13.4324 6.5003 13.2771 6.35342C13.1219 6.20654 12.9378 6.09359 12.7365 6.02176C12.5617 5.95815 12.381 5.91198 12.1971 5.88395C12.0585 5.86257 11.9186 5.85116 11.7784 5.84982H11.7797ZM11.5303 8.8607H11.4135V6.9182H11.6681C11.7799 6.91014 11.8921 6.9273 11.9964 6.96842C12.1006 7.00954 12.1943 7.07356 12.2706 7.15576C12.4285 7.36709 12.5128 7.62433 12.5107 7.88814C12.5107 8.21101 12.5107 8.5037 12.2194 8.70976C12.0095 8.82521 11.7705 8.8772 11.5316 8.85939" fill="white"></path>\
                            <path d="M16.3486 5.83277C16.203 5.83277 16.0612 5.84327 15.9615 5.8472L15.653 5.85508H14.6293V12.1551H15.8341C16.2946 12.1677 16.7531 12.0897 17.1834 11.9254C17.5298 11.788 17.8365 11.5665 18.0759 11.281C18.3087 10.9928 18.4758 10.6573 18.5655 10.2979C18.6686 9.89085 18.7189 9.47222 18.7151 9.05233C18.7405 8.55641 18.7022 8.05928 18.6009 7.57314C18.5048 7.21531 18.3248 6.88551 18.0759 6.61108C17.8806 6.38948 17.6415 6.21073 17.3737 6.08608C17.1437 5.97966 16.9018 5.90122 16.6531 5.85245C16.5543 5.83612 16.4541 5.82865 16.3539 5.83014L16.3486 5.83277ZM16.115 10.9975H15.9838V6.97595H16.0008C16.2714 6.94482 16.5452 6.99364 16.7883 7.11639C16.9664 7.25857 17.1115 7.43769 17.2136 7.64139C17.3238 7.85577 17.3873 8.09106 17.4 8.33177C17.4118 8.62052 17.4 8.85677 17.4 9.05233C17.4053 9.2776 17.3908 9.50291 17.3566 9.72564C17.3162 9.95432 17.2414 10.1756 17.1348 10.3819C17.0142 10.5737 16.8512 10.7354 16.6584 10.8544C16.4965 10.9591 16.3047 11.008 16.1124 10.9935" fill="white"></path>\
                            <path d="M22.7758 5.85507H19.5864V12.1551H20.9356V9.65607H22.6419V8.48532H20.9356V7.02582H22.7731V5.85507" fill="white"></path>\
                            </svg></div>\
                            <div style="width: 120px; height: 50px; display: inline-block;"><span id="custom-text-attach">' +
            attached_file_src.split("/")[len - 1] +
            '</span><br>\
            <a href="' + attached_file_src + '" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>\
                            <div style="width: 30px;cursor: pointer; height: 35px; display: inline-block;">\
                            ' +
            get_doc_path_html(attached_file_src) +
            '\
                            </div>\
                            <div class="upload-file-text-area" style="color: white;">' +
            text_message +
            '</div>\
                        </div>\
                        <div class="live-chat-client-message-time">\
                            ' +
            time +
            "\
                        </div>\
                    </div>";
    } else if (is_txt(attached_file_src)) {
        html +=
            '<div class="live-chat-agent-message-wrapper">\
                            <div class="live-chat-agent-image">' +
            get_user_initial(sender_name) +
            '</div>\
            <div class="group-chat-element live-chat-client-name-with-message">' +
            sender_name +
            '</div>\
                            <div class="live-chat-agent-message-bubble file-attachement-download">\
                            <div style="    width: 50px; height: 45px; display: inline-block;"><svg width="32" height="42" viewBox="0 0 32 42" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M9.1875 18.375C8.8394 18.375 8.50556 18.5133 8.25942 18.7594C8.01328 19.0056 7.875 19.3394 7.875 19.6875C7.875 20.0356 8.01328 20.3694 8.25942 20.6156C8.50556 20.8617 8.8394 21 9.1875 21H22.3125C22.6606 21 22.9944 20.8617 23.2406 20.6156C23.4867 20.3694 23.625 20.0356 23.625 19.6875C23.625 19.3394 23.4867 19.0056 23.2406 18.7594C22.9944 18.5133 22.6606 18.375 22.3125 18.375H9.1875ZM7.875 24.9375C7.875 24.5894 8.01328 24.2556 8.25942 24.0094C8.50556 23.7633 8.8394 23.625 9.1875 23.625H22.3125C22.6606 23.625 22.9944 23.7633 23.2406 24.0094C23.4867 24.2556 23.625 24.5894 23.625 24.9375C23.625 25.2856 23.4867 25.6194 23.2406 25.8656C22.9944 26.1117 22.6606 26.25 22.3125 26.25H9.1875C8.8394 26.25 8.50556 26.1117 8.25942 25.8656C8.01328 25.6194 7.875 25.2856 7.875 24.9375ZM7.875 30.1875C7.875 29.8394 8.01328 29.5056 8.25942 29.2594C8.50556 29.0133 8.8394 28.875 9.1875 28.875H14.4375C14.7856 28.875 15.1194 29.0133 15.3656 29.2594C15.6117 29.5056 15.75 29.8394 15.75 30.1875C15.75 30.5356 15.6117 30.8694 15.3656 31.1156C15.1194 31.3617 14.7856 31.5 14.4375 31.5H9.1875C8.8394 31.5 8.50556 31.3617 8.25942 31.1156C8.01328 30.8694 7.875 30.5356 7.875 30.1875Z" fill="black"/>\
                                <path d="M19.6875 0H5.25C3.85761 0 2.52226 0.553124 1.53769 1.53769C0.553123 2.52226 0 3.85761 0 5.25V36.75C0 38.1424 0.553123 39.4777 1.53769 40.4623C2.52226 41.4469 3.85761 42 5.25 42H26.25C27.6424 42 28.9777 41.4469 29.9623 40.4623C30.9469 39.4777 31.5 38.1424 31.5 36.75V11.8125L19.6875 0ZM19.6875 2.625V7.875C19.6875 8.91929 20.1023 9.92081 20.8408 10.6592C21.5792 11.3977 22.5807 11.8125 23.625 11.8125H28.875V36.75C28.875 37.4462 28.5984 38.1139 28.1062 38.6062C27.6139 39.0984 26.9462 39.375 26.25 39.375H5.25C4.55381 39.375 3.88613 39.0984 3.39384 38.6062C2.90156 38.1139 2.625 37.4462 2.625 36.75V5.25C2.625 4.55381 2.90156 3.88613 3.39384 3.39384C3.88613 2.90156 4.55381 2.625 5.25 2.625H19.6875Z" fill="black"/>\
                                </svg></div>\
                                <div style="width: 120px; height: 50px; display: inline-block;"><span id="custom-text-attach">' +
            attached_file_src.split("/")[len - 1] +
            '</span><br>\
            <a href="' + attached_file_src + '" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>\
                                <div style="width: 30px;cursor: pointer; height: 35px; display: inline-block;">\
                                ' +
            get_doc_path_html(attached_file_src) +
            '\
                                </div>\
                                <div class="upload-file-text-area" style="color: white;">' +
            text_message +
            '</div>\
                            </div>\
                            <div class="live-chat-agent-message-time">\
                                ' +
            time +
            "\
                                " +
            blue_ticks +
            "\
                            </div>\
                        </div>";
    } else if (is_docs(attached_file_src)) {
        html +=
            '<div class="live-chat-client-message-wrapper">\
                        <div class="live-chat-client-image">' +
            get_user_initial(sender_name) +
            '</div>\
            <div class="group-chat-element live-chat-client-name-with-message">' +
            sender_name +
            '</div>\
                        <div class="live-chat-client-message-bubble file-attachement-download">\
                        <div style="    width: 50px; height: 45px; display: inline-block;">\
                        <svg width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">\
                            <path d="M37.8079 3.9375H12.7378C12.5324 3.93733 12.3289 3.97763 12.139 4.05609C11.9491 4.13455 11.7766 4.24965 11.6312 4.39481C11.4858 4.53996 11.3704 4.71233 11.2916 4.90208C11.2128 5.09183 11.1722 5.29524 11.172 5.50069V12.4688L25.7001 16.7344L39.375 12.4688V5.50069C39.3748 5.29513 39.3341 5.09161 39.2553 4.90178C39.1764 4.71194 39.0609 4.53951 38.9154 4.39434C38.7698 4.24917 38.5971 4.1341 38.4071 4.05571C38.2171 3.97733 38.0134 3.93716 37.8079 3.9375Z" fill="#41A5EE"/>\
                            <path d="M39.375 12.4688H11.172V21L25.7001 23.5594L39.375 21V12.4688Z" fill="#2B7CD3"/>\
                            <path d="M11.172 21V29.5312L24.8456 31.2375L39.375 29.5312V21H11.172Z" fill="#185ABD"/>\
                            <path d="M12.7378 38.0625H37.8066C38.0122 38.063 38.216 38.023 38.4062 37.9447C38.5964 37.8664 38.7692 37.7513 38.9149 37.6061C39.0606 37.4609 39.1762 37.2884 39.2552 37.0985C39.3341 36.9086 39.3748 36.705 39.375 36.4993V29.5312H11.172V36.4993C11.1722 36.7048 11.2128 36.9082 11.2916 37.0979C11.3704 37.2877 11.4858 37.46 11.6312 37.6052C11.7766 37.7504 11.9491 37.8654 12.139 37.9439C12.3289 38.0224 12.5324 38.0627 12.7378 38.0625Z" fill="#103F91"/>\
                            <path opacity="0.1" d="M21.5696 10.7625H11.172V32.0906H21.5696C21.9839 32.0886 22.3808 31.9234 22.6741 31.6308C22.9674 31.3382 23.1336 30.9418 23.1368 30.5275V12.3257C23.1336 11.9114 22.9674 11.515 22.6741 11.2224C22.3808 10.9298 21.9839 10.7646 21.5696 10.7625Z" fill="black"/>\
                            <path opacity="0.2" d="M20.7152 11.6156H11.172V32.9438H20.7152C21.1295 32.9417 21.5263 32.7765 21.8196 32.4839C22.113 32.1913 22.2792 31.7949 22.2823 31.3806V13.1788C22.2792 12.7645 22.113 12.3681 21.8196 12.0755C21.5263 11.7829 21.1295 11.6177 20.7152 11.6156Z" fill="black"/>\
                            <path opacity="0.2" d="M20.7152 11.6156H11.172V31.2375H20.7152C21.1295 31.2354 21.5263 31.0702 21.8196 30.7776C22.113 30.485 22.2792 30.0886 22.2823 29.6743V13.1788C22.2792 12.7645 22.113 12.3681 21.8196 12.0755C21.5263 11.7829 21.1295 11.6177 20.7152 11.6156Z" fill="black"/>\
                            <path opacity="0.2" d="M19.8607 11.6156H11.172V31.2375H19.8607C20.2751 31.2354 20.6719 31.0702 20.9652 30.7776C21.2585 30.485 21.4248 30.0886 21.4279 29.6743V13.1788C21.4248 12.7645 21.2585 12.3681 20.9652 12.0755C20.6719 11.7829 20.2751 11.6177 19.8607 11.6156Z" fill="black"/>\
                            <path d="M4.19212 11.6156H19.8608C20.2758 11.6153 20.674 11.7797 20.9679 12.0729C21.2617 12.366 21.4272 12.7638 21.4279 13.1788V28.8212C21.4272 29.2362 21.2617 29.634 20.9679 29.9272C20.674 30.2203 20.2758 30.3847 19.8608 30.3844H4.19212C3.98656 30.3847 3.78295 30.3446 3.59291 30.2662C3.40288 30.1878 3.23016 30.0727 3.08462 29.9275C2.93909 29.7824 2.82358 29.6099 2.74472 29.4201C2.66585 29.2303 2.62517 29.0268 2.625 28.8212V13.1788C2.62517 12.9733 2.66585 12.7697 2.74472 12.5799C2.82358 12.3901 2.93909 12.2176 3.08462 12.0725C3.23016 11.9273 3.40288 11.8122 3.59291 11.7338C3.78295 11.6555 3.98656 11.6153 4.19212 11.6156Z" fill="url(#paint0_linear)"/>\
                            <path d="M9.05627 23.6093C9.08645 23.8508 9.10745 24.0608 9.11664 24.2406H9.15339C9.16651 24.0699 9.19539 23.8639 9.2387 23.6237C9.28201 23.3835 9.32008 23.1801 9.35551 23.0134L11.0027 15.9167H13.1342L14.8405 22.9071C14.9398 23.3395 15.0109 23.7779 15.0531 24.2196H15.082C15.1133 23.7896 15.1725 23.3622 15.2591 22.9399L16.6228 15.9075H18.5614L16.1674 26.0768H13.9007L12.2771 19.3489C12.2299 19.1546 12.1765 18.9018 12.117 18.5903C12.0575 18.2788 12.0208 18.0513 12.0068 17.9078H11.9792C11.9608 18.0731 11.9241 18.3186 11.869 18.6441C11.8138 18.9709 11.7705 19.2111 11.7377 19.3686L10.2113 26.0807H7.90652L5.49939 15.9167H7.46814L8.95258 23.0278C8.99688 23.2198 9.03149 23.4138 9.05627 23.6093Z" fill="white"/>\
                            <defs>\
                            <linearGradient id="paint0_linear" x1="5.89837" y1="10.3871" x2="18.1545" y2="31.6129" gradientUnits="userSpaceOnUse">\
                            <stop stop-color="#2368C4"/>\
                            <stop offset="0.5" stop-color="#1A5DBE"/>\
                            <stop offset="1" stop-color="#1146AC"/>\
                            </linearGradient>\
                            </defs>\
                        </svg>\
                            </div>\
                            <div style="width: 120px; height: 50px; display: inline-block;"><span id="custom-text-attach">' +
            attached_file_src.split("/")[len - 1] +
            '</span><br>\
            <a href="' + attached_file_src + '" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>\
                        <div style="width: 30px;cursor: pointer; height: 35px; display: inline-block;">\
                        ' +
            get_doc_path_html(attached_file_src) +
            '\
                        </div><div class="upload-file-text-area" style="color: white;">' +
            text_message +
            '</div></div>\
                        <div class="live-chat-client-message-time">\
                            ' +
            time +
            "\
                        </div>\
                    </div>";
    } else if (is_image(attached_file_src)) {
        html +=
            '<div class="live-chat-client-message-wrapper">\
                    <div class="live-chat-client-image">' +
            get_user_initial(sender_name) +
            '</div>\
            <div class="group-chat-element live-chat-client-name-with-message">' +
            sender_name +
            '</div>\
                    <div class="live-chat-client-message-bubble-image-attachment" style="height: unset;">\
                        ' +
            get_image_path_html(attached_file_src, thumbnail_url) +
            '\
                        <div class="file-attach-name-area" style="text-align: left; position: relative; margin-top: 0px;">\
                            <h5 id="custom-text-attach-img" style="padding-left: 0px;">' +
            attached_file_src.split("/")[len - 1] +
            '</h5>\
            <p style="overflow-wrap: break-word;">' +
            text_message +
            '</p>\
                            <a href="' +
            attached_file_src +
            '" target="_blank"><span style="position: absolute; top: 0.6rem; right: 8px;"><svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M11.875 11.25H3.125C2.77982 11.25 2.5 11.5298 2.5 11.875C2.5 12.2202 2.77982 12.5 3.125 12.5H11.875C12.2202 12.5 12.5 12.2202 12.5 11.875C12.5 11.5298 12.2202 11.25 11.875 11.25Z" fill="#757575"/>\
                                <path d="M2.5 10.625V11.875C2.5 12.2202 2.77982 12.5 3.125 12.5C3.47018 12.5 3.75 12.2202 3.75 11.875V10.625C3.75 10.2798 3.47018 10 3.125 10C2.77982 10 2.5 10.2798 2.5 10.625Z" fill="#757575"/>\
                                <path d="M11.25 10.625V11.875C11.25 12.2202 11.5298 12.5 11.875 12.5C12.2202 12.5 12.5 12.2202 12.5 11.875V10.625C12.5 10.2798 12.2202 10 11.875 10C11.5298 10 11.25 10.2798 11.25 10.625Z" fill="#757575"/>\
                                <path d="M7.50003 9.375C7.37046 9.37599 7.24378 9.33667 7.13753 9.2625L4.63753 7.5C4.50279 7.40442 4.41137 7.25937 4.38326 7.09658C4.35515 6.93379 4.39264 6.76649 4.48753 6.63125C4.5349 6.56366 4.59518 6.50611 4.66491 6.46194C4.73463 6.41777 4.81242 6.38785 4.89377 6.37391C4.97512 6.35996 5.05843 6.36227 5.13889 6.38069C5.21934 6.39911 5.29535 6.43329 5.36253 6.48125L7.50003 7.975L9.62503 6.375C9.75764 6.27555 9.92432 6.23284 10.0884 6.25628C10.2525 6.27973 10.4006 6.36739 10.5 6.5C10.5995 6.63261 10.6422 6.7993 10.6187 6.96339C10.5953 7.12749 10.5076 7.27555 10.375 7.375L7.87503 9.25C7.76685 9.33114 7.63526 9.375 7.50003 9.375Z" fill="#757575"/>\
                                <path d="M7.5 8.125C7.33424 8.125 7.17527 8.05915 7.05806 7.94194C6.94085 7.82473 6.875 7.66576 6.875 7.5V2.5C6.875 2.33424 6.94085 2.17527 7.05806 2.05806C7.17527 1.94085 7.33424 1.875 7.5 1.875C7.66576 1.875 7.82473 1.94085 7.94194 2.05806C8.05915 2.17527 8.125 2.33424 8.125 2.5V7.5C8.125 7.66576 8.05915 7.82473 7.94194 7.94194C7.82473 8.05915 7.66576 8.125 7.5 8.125Z" fill="#757575"/>\
                                </svg>\
                                </span></a>\
                        </div></div>\
                        <div class="live-chat-client-message-time">\
                            ' +
            time +
            "\
                            </div>\
                    </div>";
    }

    return html;
}

function get_reply_response_user_html(
    message,
    sender_name,
    flag_not_seen,
    session_id,
    time,
    reply_message_text,
    reply_message_time,
    message_for,
    message_time,
    is_attachment=false,
    is_reply_attachment=false,
) {

    if(!is_reply_attachment) {
        reply_message_text = stripHTML(reply_message_text);
        reply_message_text = livechat_linkify(reply_message_text);
        reply_message_text = reply_message_text.trim();
    }
    
    let blue_ticks = state.tick.single;
    let custom_class = 'single_tick';
    if (flag_not_seen == state.is_delivered) {
        blue_ticks = state.tick.double;
        custom_class = 'double_tick';
    } else if (flag_not_seen == state.is_read) {
        blue_ticks = state.tick.blue;
        custom_class = 'blue_tick';
    }

    var client_name_html = "";
    if(message_for == "client") {
        client_name_html = '<div class="group-chat-element live-chat-client-name-with-message">'+sender_name+'</div>';
        blue_ticks = '';
    }
    var message_bubble_container_start = '<div class="live-chat-'+ message_for +'-message-bubble">';
    var message_bubble_container_end = '</div>';
    if(is_attachment) {
        message_bubble_container_start = '';
        message_bubble_container_end = '';
    }

    var html =  `'<div class="live-chat-${message_for}-message-wrapper live-chat-agent-message-reply-comment-wrapper">
                    <div class="live-chat-${message_for}-image">${get_user_initial(sender_name)}</div>
                        ${client_name_html}
                    <div class="live-chat-${message_for}-message-bubble-reply-wrapper">
                        ${message_bubble_container_start}
                        ${message}
                        ${message_bubble_container_end}
                        <div class="live-chat-${message_for}-message-reply-text-container">
                            <div class="live-chat-${message_for}-message-reply-text-hover-text-div">
                                *This message is only visible to Agents, Supervisors & Admin*
                            </div>
                            <div class="live-chat-${message_for}-message-reply-text-bubble">
                                ${reply_message_text}
                            </div>
                            <div class="live-chat-${message_for}-message-reply-time-div">
                                ${reply_message_time}
                            </div>
                        </div>
                    </div>
                    <div class="live-chat-${message_for}-message-time">
                    ${time}
                    <div data-time="${message_time}" class="blue_tick-${session_id} ${custom_class}">${blue_ticks}</div>
                </div>
                </div>`;

    return html;
}

function append_replied_message(message, session_id, message_for, flag_not_seen) {
    var html;

    if(message.reply_attached_file_src != "") {

        var reply_attachment_html = get_attachment_html(
            message.reply_attached_file_src, 
            session_id, 
            message.reply_thumbnail_file_src,
            message.reply_message_text,
            message.reply_message_time);

        if (message.attached_file_src != "") {
            var attachment_html = get_attachment_html(
                message.attached_file_src,
                session_id,
                message.file,
                message.message,
                message.time
                );

            html = get_reply_response_user_html(
                attachment_html,
                message.sender_name,
                flag_not_seen,
                session_id,
                message.time,
                reply_attachment_html,
                message.reply_message_time,
                message_for,
                message.time_in_minisec,
                true,
                true
            );    

        } else if (message.message != "") {
            html = get_reply_response_user_html(
                message.message,
                message.sender_name,
                flag_not_seen,
                session_id,
                message.time,
                reply_attachment_html,
                message.reply_message_time,
                message_for,
                message.time_in_minisec,
                false,
                true
            );            
        }    

    } else if (message.reply_message_text != "") {
        if (message.attached_file_src != "") {
            var attachment_html = get_attachment_html(
                message.attached_file_src,
                session_id,
                message.file,
                message.message,
                message.time
                );

            html = get_reply_response_user_html(
                attachment_html,
                message.sender_name,
                flag_not_seen,
                session_id,
                message.time,
                message.reply_message_text,
                message.reply_message_time,
                message_for,
                message.time_in_minisec,
                true
            ); 

        } else if (message.message != "") {
            html = get_reply_response_user_html(
                message.message,
                message.sender_name,
                flag_not_seen,
                session_id,
                message.time,
                message.reply_message_text,
                message.reply_message_time,
                message_for,
                message.time_in_minisec,
            );            
        }
    }
    return html;
}

function append_message_in_one_one_chat_icon(agent) {
    let msg = {
        text_message: agent.last_msg_text,
        sender: agent.sender,
        is_attachment: "False",
    };

    if (agent.filename != "") {
        msg.attachment_name = agent.filename;
        msg.is_attachment = "True";
    }

    append_message_in_chat_icon(agent.websocket_token, msg);
}

export function append_message_in_user_group_chat_icon(user_group) {
    let msg = {
        text_message: user_group.last_message.text,
        sender: user_group.last_message.sender,
        is_attachment: "False",
    };

    if (user_group.last_message.filename != "") {
        msg.attachment_name = user_group.last_message.filename;
        msg.is_attachment = "True";
    }

    append_message_in_chat_icon_new(user_group.id, msg);
}

export function append_message_in_user_group_icon(user_group_list) {
    user_group_list.forEach(user_group => {
        if (user_group.is_user_group) {
            append_message_in_user_group_chat_icon(user_group);
        } else {
            append_message_in_one_one_chat_icon(user_group);
        }
    })
}

function resize_internal_chat_window() {
    let session_id = get_current_receiver_token();

    var parent_elem_height = document.getElementById(
        "livechat-main-console"
    ).clientHeight;
    var input_elem_height = document.getElementsByClassName(
        "live-chat-text-box-wrapper"
    )[0].clientHeight;
    var target_elem = document.getElementById(`style-2_${session_id}`);

    let footer_height = 0;
    if (SHOW_VERSION_FOOTER == "True") {
        footer_height = 28;
    }
    try {
        if (state.is_mobile) {
            target_elem.style.height =
                window.innerHeight -
                (input_elem_height + 52 + 20 + footer_height + 70 + 41) +
                "px";
        } else {
            target_elem.style.height =
                parent_elem_height -
                (input_elem_height + 20 + 20 + footer_height + 21) +
                "px";
        }
    } catch (err) {
        console.log(err);
    }
    if (!state.is_mobile) {
        internal_chat_scroll_to_bottom();
    }
}

function load_more_chat(id, is_group) {
    const chat_div = document.getElementById(`style-2_${id}`);

    if (chat_div.scrollTop == 0 && !state.chat_load.is_completed) {
        const loader_div = document.getElementById(`more-chat-loader_${id}`);

        if (!loader_div) {
            const html = `<div class="spinner" id="more-chat-loader_${id}" style="display: flex;">\
                            <div class="bounce1"></div>\
                            <div class="bounce2"></div>\
                            <div class="bounce3"></div>\
                        </div>`
            
            $(`#style-2_${id}`).prepend(html);

            setTimeout(() => {
                if (is_group) update_internal_chat_group_history(get_current_receiver_token(), true);
                else if (state.is_user_group) update_internal_user_group_history(get_current_receiver_token(), true); 
                else update_internal_chat_message_history(true); 
            }, 1000)
        }
    } 
}

export function search_users(input) {
    input = input.trim().toLowerCase();

    const user_list = get_user_list();

    if (input == '') {
        set_user_group_list(get_all_user_groups());
        append_message_in_user_group_icon(get_user_sessions());
        append_message_in_user_group_icon(get_user_group_arr());
        highlight_chat_based_chat_type();
        return;
    }

    const matching_users = perform_search(user_list, input);
    const user_group_list = get_user_group_list();
    const matching_user_groups = perform_search(user_group_list, input);

    if (matching_users.length == 0 && matching_user_groups.length == 0) {
        document.getElementById('agent-search-no-result-div').style.display = "block";
    } else {
        document.getElementById('agent-search-no-result-div').style.display = "none";
    }

    matching_users.forEach(user => {
        const elem = document.getElementById(user.websocket_token);

        if (!elem) {
            const html = get_user_chat_icon_html(user, true);

            $('#livechat_agent_contact_list').append(html);
        }
    })

    matching_user_groups.forEach(group => {
        const elem = document.getElementById(group.id);

        if (!elem) {
            const html = get_user_group_chat_icon_html(group);

            $('#livechat_agent_contact_list').prepend(html);
        }
    })

    setTimeout(() => {
        highlight_chat_based_chat_type();
        add_chat_click_event(matching_users);
        add_user_group_click_event(matching_user_groups);
    }, 300);

    append_message_in_user_group_icon(get_user_sessions());
}

export function highlight_chat_based_chat_type () {
    if (state.is_group_chat) {
        const active_group = get_active_group();
        highlight_chat(null, active_group.id);
    } else if (state.is_user_group) {
        highlight_chat(null, state.active_user_group.id);
    } else {
        highlight_chat(null, state.current_receiver_token);
    }
}

function perform_search(map, input) {
    const matching_users = []
    for (const token in map) {
        let text_to_match = map[token].full_name;
        if (text_to_match == "") text_to_match = map[token].username;

        if (text_to_match.toLowerCase().indexOf(input) != -1) {

            matching_users.push(map[token]);
        } else {
            const elem = document.getElementById(token);

            if (elem) {
                elem.remove();
            } 
        }
    }

    return matching_users;
}

export function toggle_add_member_dropdown() {
    const optionsContainer = document.querySelector("#user-box-options-container");
    const selected = document.querySelector("#add-user-dropdown-wrapper .selected");
    const searchBox = document.querySelector("#user-options-search-box input");
    const dropArrow = document.querySelector("#user-dropdown-arrow");
    const search_div = document.getElementById('user-options-search-box');
    
    $(search_div).toggle();
    optionsContainer.classList.toggle("active");
    const is_dropdown_open = optionsContainer.classList.contains("active");
    if (is_dropdown_open) {
        selected.innerHTML = "Add Members";
        selected.style.border = "none";
        dropArrow.style.transform = "translateY(-50%) rotate(180deg)";
        searchBox.focus();
        document.getElementById('livechat_added_members_list').style.display = 'none';
        document.getElementById('user-options-search-box').style.display = 'block';
    } else {
        dropArrow.style.transform = "translateY(-50%) rotate(0deg)";
        document.getElementById('livechat_added_members_list').style.display = 'block';
        document.getElementById('user-options-search-box').style.display = 'none';
    }
    searchBox.value = "";

    filterList("", "user-box-options-container");
}

export function update_members_list() {
    const container = document.getElementById('user-box-options-container');

    if (container.classList.contains("active")) {
        toggle_add_member_dropdown();
    }

    const is_user_group = get_is_user_group();
    let html = ``;
    if (!is_user_group) {

        const token = get_current_receiver_token();
        const user_list = get_user_list();
        
        for (const key in user_list) {
            if (key != token) {
                const user = user_list[key];

                html += `
                        <label for="agent-${user.username}-1" style="margin: 0px; display: block;">
                            <div class="option member-option" id="add-user-${user.username}">
                                <p>${user.username}</p>
                                <input type="checkbox" style="width: 10% !important;height: 0.8rem !important " class="item-checkbox member-checkbox user-group-member-checkbox" value="${user.username}" id="agent-${user.username}-1" name="${user.username}">
                                <span class="checkmark"></span>
                            </div>
                        </label>
                        `;
            }
        }
    } else {

        const user_list = get_user_list();
        for (const key in user_list) {
            if (!state.active_user_group.members_username.includes(user_list[key].username)) {
                const user = user_list[key];

                html += `
                        <label for="agent-${user.username}-1" style="margin: 0px; display: block;">
                            <div class="option member-option" id="add-user-${user.username}">
                                <p>${user.username}</p>
                                <input type="checkbox" style="width: 10% !important;height: 0.8rem !important " class="item-checkbox member-checkbox user-group-member-checkbox" value="${user.username}" id="agent-${user.username}-1" name="${user.username}">
                                <span class="checkmark"></span>
                            </div>
                        </label>
                        `;
            }
        }

    }

    html += `<div class='no-elem'>No such member found</div>`
    container.innerHTML = html;

    setTimeout(()=> {
        state.new_user_group.member_count = 0;
        $('.user-group-member-checkbox').on('change', (e) => {
            check_user_group_size(is_user_group, e);
        })
    }, 300);
}

function check_user_group_size(is_user_group, event) {
    if (event.target.checked) {
        state.new_user_group.member_count += 1;
    } else {
        state.new_user_group.member_count -= 1;
    }

    if (is_user_group) {
        
        const total_members_count = state.active_user_group.members_username.length + state.new_user_group.member_count;
        if (total_members_count > GROUP_SIZE_LIMIT) {
            showToast(`Exceeding group size limit of ${GROUP_SIZE_LIMIT} members.`, 2000);
            event.target.checked = false;
        }
    } else {
        const total_members_count = state.new_user_group.member_count + 2;
        if (total_members_count > GROUP_SIZE_LIMIT) {
            showToast(`Exceeding group size limit of ${GROUP_SIZE_LIMIT} members.`, 2000);
            event.target.checked = false;
        }
    }
}

export function add_user_to_user_group() {
    const selected_users = get_selected_users();

    if (selected_users.length == 0) {
        showToast('No user selected', 2000);
        return;
    }

    let json_string, chat_belong_to = "";
    if (state.is_user_group) {
        json_string = JSON.stringify({
            is_user_group: true,
            selected_users: selected_users,
            group_id: state.active_user_group.id,
        })
    } else {
        const token = get_current_receiver_token();
        const user_list = get_user_list();  
        chat_belong_to = user_list[token].username;

        json_string = JSON.stringify({
            is_user_group: false,
            selected_users: selected_users,
            chat_belong_to: chat_belong_to,
        })
    }  

    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post('/livechat/add-user-to-user-group/', params, config)
        .then (response => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);
            
            if (response.status == 200) {
                showToast('Users added successfully.', 2000);
                $('#livechat-group-add-member-chat-modal').modal('hide');

                state.active_user_group.id = response.group_id;
                const message = `added ${selected_users[selected_users.length-1]} to the chat`;

                var temp_message = JSON.stringify({
                        text_message: message,
                        type: "text",
                        path: "",
                        thumbnail: "",
                        receiver_token: state.active_user_group.id,
                        receiver_username: "user_group",
                        sender_websocket_token: get_sender_websocket_token(),
                        sender_name: 'System',
                        sender_username: get_sender_username(),
                        added_members: selected_users,
                        chat_belong_to: chat_belong_to,
                        is_group: true,
                    });
            
                send_message_to_internal_chat_socket(temp_message, "System", true);

                update_group_chat_list({
                    is_member_removed: false,
                    is_member_added: true,
                    user_group_id: null,
                })
            } else {
                showToast(response.message, 2000);
            }
        })
}

function get_response_user_html(
    sentence,
    sender_name,
    flag_not_seen,
    session_id,
    time = return_time(),
    message_time,
    message_id = "",
) {
    sentence = sentence.replace(new RegExp("\r?\n", "g"), "<br/>");
    sentence = livechat_linkify(sentence);

    let blue_ticks = state.tick.single;
    let custom_class = 'single_tick';
    if (flag_not_seen == state.is_delivered) {
        blue_ticks = state.tick.double;
        custom_class = 'double_tick';
    } else if (flag_not_seen == state.is_read) {
        blue_ticks = state.tick.blue;
        custom_class = 'blue_tick';
    }

    const html =
        `<div class="live-chat-agent-message-wrapper" id=${message_id}>
            <div class="live-chat-agent-image">
                ${get_user_initial(sender_name)}
            </div>
            <div class="live-chat-agent-message-bubble">
                ${sentence}
            </div>
            <div class="livechat-agent-message-translate-wrapper"><div class="live-chat-agent-message-time">
                ${time}
                <div data-time="${message_time}" class="blue_tick-${session_id} ${custom_class}">${blue_ticks}</div>
            </div></div></div>`;

    return html;
}

function get_file_to_agent_html(
    attached_file_src,
    message,
    sender_name,
    flag_not_seen,
    img_file,
    session_id,
    message_id="",
    time = return_time(),
    message_time
) {
    var len = attached_file_src.split("/").length;
    
    let blue_ticks = state.tick.single;
    let custom_class = 'single_tick';
    if (flag_not_seen == state.is_delivered) {
        blue_ticks = state.tick.double;
        custom_class = 'double_tick';
    } else if (flag_not_seen == state.is_read) {
        blue_ticks = state.tick.blue;
        custom_class = 'blue_tick';
    }

    message = livechat_linkify(message);

    const icons = get_icons();
    let html = "";
    if (is_pdf(attached_file_src)) {
        html = `<div class="live-chat-agent-message-wrapper" id=${message_id}><div class="live-chat-agent-image">${get_user_initial(sender_name)}</div>
        <div class="live-chat-agent-message-bubble file-attachement-download live-chat-attachment-div">
            <div style="width: 50px;  display: inline-block;">
            ${icons.pdf}
            </div>
            <div class="file-attachment-path"><span id="custom-text-attach">${
                attached_file_src.split("/")[len - 1]
            }</span><br>
            <a href="${attached_file_src}" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>
            <div style="width: 30px;cursor: pointer;  display: inline-block; float: right; margin-top: 12px;">
            ${get_doc_path_html(attached_file_src)}
            </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area live-chat-attachment-text">${message}</div>`;
        }

        html += `</div><div class="livechat-agent-message-translate-wrapper"><div class="live-chat-agent-message-time">
                ${time}
                <div data-time="${message_time}" class="blue_tick-${session_id} ${custom_class}">${blue_ticks}</div>
            </div></div></div>`;
    } else if (is_txt(attached_file_src)) {
        html = `<div class="live-chat-agent-message-wrapper" id=${message_id}><div class="live-chat-agent-image">${get_user_initial(sender_name)}</div>
        <div class="live-chat-agent-message-bubble file-attachement-download live-chat-attachment-div">
            <div style="width: 50px;  display: inline-block;">
            ${icons.txt}
            </div>
            <div class="file-attachment-path"><span id="custom-text-attach">${
                attached_file_src.split("/")[len - 1]
            }</span><br>
            <a href="${attached_file_src}" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>
            <div style="width: 30px;cursor: pointer;  display: inline-block; float: right; margin-top: 12px;">
            ${get_doc_path_html(attached_file_src)}
            </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area live-chat-attachment-text">${message}</div>`;
        }

        html += `</div><div class="livechat-agent-message-translate-wrapper"><div class="live-chat-agent-message-time">
                ${time}
                <div data-time="${message_time}" class="blue_tick-${session_id} ${custom_class}">${blue_ticks}</div>
            </div></div></div>`;
    } else if (is_docs(attached_file_src)) {
        html = `<div class="live-chat-agent-message-wrapper" id=${message_id}><div class="live-chat-agent-image">${get_user_initial(sender_name)}</div>
        <div class="live-chat-agent-message-bubble file-attachement-download live-chat-attachment-div">
            <div style="width: 50px;  display: inline-block;">
            ${icons.doc}
            </div>
            <div class="file-attachment-path"><span id="custom-text-attach">${
                attached_file_src.split("/")[len - 1]
            }</span><br>
            <a href="${attached_file_src}" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>
            <div style="width: 30px;cursor: pointer;  display: inline-block; float: right; margin-top: 12px;">
            ${get_doc_path_html(attached_file_src)}
            </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area live-chat-attachment-text">${message}</div>`;
        }

        html += `</div><div class="livechat-agent-message-translate-wrapper"><div class="live-chat-agent-message-time">
                ${time}
                <div data-time="${message_time}" class="blue_tick-${session_id} ${custom_class}">${blue_ticks}</div>
                </div></div></div>`;    
    } else if (is_excel(attached_file_src)) {
        html = `<div class="live-chat-agent-message-wrapper" id=${message_id}><div class="live-chat-agent-image">${get_user_initial(sender_name)}</div>
        <div class="live-chat-agent-message-bubble file-attachement-download live-chat-attachment-div">
            <div style="width: 50px;  display: inline-block;">
            ${icons.excel}
            </div>
            <div class="file-attachment-path"><span id="custom-text-attach">${
                attached_file_src.split("/")[len - 1]
            }</span><br>
            <a href="${attached_file_src}" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>
            <div style="width: 30px;cursor: pointer;  display: inline-block; float: right; margin-top: 12px;">
            ${get_doc_path_html(attached_file_src)}
            </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area live-chat-attachment-text">${message}</div>`;
        }

        html += `</div><div class="livechat-agent-message-translate-wrapper"><div class="live-chat-agent-message-time">
                ${time}
                <div data-time="${message_time}" class="blue_tick-${session_id} ${custom_class}">${blue_ticks}</div>
            </div></div></div>`;
    } else if (is_image(attached_file_src)) {
        html = `<div class="live-chat-agent-message-wrapper" id=${message_id}>
                        <div class="live-chat-agent-image">${get_user_initial(sender_name)}</div>
                        <div class="live-chat-agent-message-bubble-image-attachment live-chat-attachment-div">
                            <div class="slideshow-container" value="1">
                                <div class="mySlides livechat-slider-card">
                                    ${get_image_path_html(
                                        attached_file_src,
                                        img_file
                                    )}
                                    <div style="text-align: left;">
                                        <h5 style="overflow-wrap: break-word; ">${
                                            attached_file_src.split("/")[
                                                len - 1
                                            ]
                                        }</h5>
                                        <a href="${attached_file_src}" target="_blank"><span style="position: absolute; top: 8.5rem; right: 8px;"><svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M11.875 11.25H3.125C2.77982 11.25 2.5 11.5298 2.5 11.875C2.5 12.2202 2.77982 12.5 3.125 12.5H11.875C12.2202 12.5 12.5 12.2202 12.5 11.875C12.5 11.5298 12.2202 11.25 11.875 11.25Z" fill="#757575"/>
                                        <path d="M2.5 10.625V11.875C2.5 12.2202 2.77982 12.5 3.125 12.5C3.47018 12.5 3.75 12.2202 3.75 11.875V10.625C3.75 10.2798 3.47018 10 3.125 10C2.77982 10 2.5 10.2798 2.5 10.625Z" fill="#757575"/>
                                        <path d="M11.25 10.625V11.875C11.25 12.2202 11.5298 12.5 11.875 12.5C12.2202 12.5 12.5 12.2202 12.5 11.875V10.625C12.5 10.2798 12.2202 10 11.875 10C11.5298 10 11.25 10.2798 11.25 10.625Z" fill="#757575"/>
                                        <path d="M7.50003 9.375C7.37046 9.37599 7.24378 9.33667 7.13753 9.2625L4.63753 7.5C4.50279 7.40442 4.41137 7.25937 4.38326 7.09658C4.35515 6.93379 4.39264 6.76649 4.48753 6.63125C4.5349 6.56366 4.59518 6.50611 4.66491 6.46194C4.73463 6.41777 4.81242 6.38785 4.89377 6.37391C4.97512 6.35996 5.05843 6.36227 5.13889 6.38069C5.21934 6.39911 5.29535 6.43329 5.36253 6.48125L7.50003 7.975L9.62503 6.375C9.75764 6.27555 9.92432 6.23284 10.0884 6.25628C10.2525 6.27973 10.4006 6.36739 10.5 6.5C10.5995 6.63261 10.6422 6.7993 10.6187 6.96339C10.5953 7.12749 10.5076 7.27555 10.375 7.375L7.87503 9.25C7.76685 9.33114 7.63526 9.375 7.50003 9.375Z" fill="#757575"/>
                                        <path d="M7.5 8.125C7.33424 8.125 7.17527 8.05915 7.05806 7.94194C6.94085 7.82473 6.875 7.66576 6.875 7.5V2.5C6.875 2.33424 6.94085 2.17527 7.05806 2.05806C7.17527 1.94085 7.33424 1.875 7.5 1.875C7.66576 1.875 7.82473 1.94085 7.94194 2.05806C8.05915 2.17527 8.125 2.33424 8.125 2.5V7.5C8.125 7.66576 8.05915 7.82473 7.94194 7.94194C7.82473 8.05915 7.66576 8.125 7.5 8.125Z" fill="#757575"/>
                                        </svg>
                                        </span></a>`;

        if (message != "") {
            html += `<p style="overflow-wrap: break-word;" class="live-chat-attachment-text" >${message}</p>`;
        }

        html += `</div>
                    </div>
                </div>
                
                </div>
                <div class="livechat-agent-message-translate-wrapper"><div class="live-chat-agent-message-time">
                ${time}
                <div data-time="${message_time}" class="blue_tick-${session_id} ${custom_class}">${blue_ticks}</div>
                </div></div>
                </div>`;
    } else if (is_video(attached_file_src)) {
        html = `<div class="live-chat-agent-message-wrapper" id=${message_id}>
                        <div class="live-chat-agent-image">${get_user_initial(sender_name)}</div>
                        <div class="live-chat-agent-message-bubble-image-attachment live-chat-attachment-div">
                            <div class="slideshow-container" value="1">
                                <div class="mySlides livechat-slider-card">
                                    ${get_video_path_html(
                                        attached_file_src,
                                        img_file
                                    )}
                                    <div style="text-align: left;">
                                        <h5 style="overflow-wrap: break-word; ">${
                                            attached_file_src.split("/")[
                                                len - 1
                                            ]
                                        }</h5>`;

        if (message != "") {
            html += `<p style="overflow-wrap: break-word;" class="live-chat-attachment-text">${message}</p>`;
        }

        html += `</div>
                    </div>
                </div>
                
                </div>
                <div class="livechat-agent-message-translate-wrapper"><div class="live-chat-agent-message-time">
                ${time}
                <div data-time="${message_time}" class="blue_tick-${session_id} ${custom_class}">${blue_ticks}</div>
                </div></div>
                </div>`;
    }

    return html;
}

function get_selected_users() {
    const options = document.querySelectorAll('#user-box-options-container .option input')

    const selected_users = [];
    options.forEach(option => {
        if (option.checked) selected_users.push(option.name)
    })

    return selected_users;
}


export function toggle_agent_search_bar() {
    $('#livechat-groupchat-agent-searchbar').toggle();
}

function append_last_message_time(id, date) {
    const elem = document.getElementById(`livechat-last-message-time_${id}`);

    if (elem) {
        elem.innerHTML = date;
    }
}

export function send_agent_last_seen_time () {
    const receiver_websocket_token = get_current_receiver_token();
    const sender_websocket_token = get_sender_websocket_token();

    var message = JSON.stringify({
        message: JSON.stringify({
            event_type: "LAST_SEEN",
            receiver_token: receiver_websocket_token,
            sender_websocket_token: sender_websocket_token,
            sender_name: get_internal_chat_sender_name(),
            sender_username: state.sender_username,
        }),
        sender: "OneToOneUser",
    });

    send_message_to_guest_agent_socket(message);
}

export function send_last_seen_on_chat_signal () {
    const receiver_websocket_token = get_current_receiver_token();
    const sender_websocket_token = get_sender_websocket_token();

    var message = JSON.stringify({
        message: JSON.stringify({
            event_type: "LAST_SEEN_ON_CHAT",
            receiver_token: receiver_websocket_token,
            sender_websocket_token: sender_websocket_token,
            sender_name: get_internal_chat_sender_name(),
            sender_username: state.sender_username,
            is_group: get_is_group_chat(),
            is_user_group: get_is_user_group(),
        }),
        sender: "OneToOneUser",
    });

    send_message_to_guest_agent_socket(message);
}

export function update_all_message_status (session_id, status) {
    if (status == state.is_delivered) {
        $(`.blue_tick-${session_id}.single_tick`).html(state.tick.double);
        $(`.blue_tick-${session_id}.single_tick`).addClass('double_tick');
        $(`.blue_tick-${session_id}.single_tick`).removeClass('single_tick');
    } else if (status == state.is_read) {
        $(`.blue_tick-${session_id}.single_tick`).html(state.tick.blue);
        $(`.blue_tick-${session_id}.single_tick`).addClass('blue_tick');
        $(`.blue_tick-${session_id}.single_tick`).removeClass('single_tick');

        $(`.blue_tick-${session_id}.double_tick`).html(state.tick.blue);
        $(`.blue_tick-${session_id}.double_tick`).addClass('blue_tick');
        $(`.blue_tick-${session_id}.double_tick`).removeClass('double_tick');
    }
}

export function update_last_seen_on_chat () {

    if (state.is_group_chat) {
        const active_group = get_active_group();
        state.last_seen_on_chat.groups[active_group.id] = Date.parse(new Date());
    } else if (state.is_user_group) {
        const active_group = get_active_user_group();
        state.last_seen_on_chat.user_groups[active_group.id] = Date.parse(new Date());
    } else {
        const receiver_token = get_current_receiver_username();

        if (receiver_token) {
            state.last_seen_on_chat.single_chats[receiver_token] = Date.parse(new Date());
        }
    }
}

export function send_last_seen_on_chats_to_server () {
    let json_string = {};

    let single_chats = state.last_seen_on_chat.single_chats;
    if (Object.keys(single_chats).length != 0) {
        json_string.single_chats = single_chats;
    }

    let user_groups = state.last_seen_on_chat.user_groups;
    if (Object.keys(user_groups).length != 0) {
        json_string.user_groups = user_groups;
    }

    let groups = state.last_seen_on_chat.groups;
    if (Object.keys(groups).length != 0) {
        json_string.groups = groups;
    }

    if (Object.keys(json_string).length == 0) return;

    json_string = JSON.stringify(json_string);
    const params = get_params(json_string);

    let config = {
        headers: {
          'X-CSRFToken': getCsrfToken(),
        }
    }

    axios
        .post("/livechat/update-last-seen-on-chats/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            console.log(response);
        })
        .catch((err) => {
            console.log(err);
            console.log("Unable to update last seen on chat. Please try again later.");
        });
}

export function update_user_group_user_last_seen (username) {
    if (get_is_user_group()) {
        const active_group = get_active_user_group();
        let member = active_group.members.filter((value, index, arr) => {
            return value.name == username;
        });

        if (member && member.length > 0) {
            member = member[0];
            member.last_seen_time = Date.parse(new Date());

            const min_last_seen = get_min_last_seen(active_group.members);

            mark_group_messages_as_delivered(active_group.id, min_last_seen);
        }
    }
}

export function update_user_group_user_last_seen_on_chat (username, group_id) {
        const group_list = get_user_group_list();
        const group = group_list[group_id];

        let member = group.members.filter((value, index, arr) => {
            return value.name == username;
        });

        if (member && member.length > 0) {
            member = member[0];
            member.last_seen_on_chat = Date.parse(new Date());

            const min_last_seen = get_min_last_seen_on_chat(group.members);

            mark_group_messages_as_read(group.id, min_last_seen);
        }
}

export function set_unread_message_count(user_group_list, group_list) {


    user_group_list.forEach(user_group => {
        if (user_group.is_user_group) {
            localStorage.setItem(`unread_message_count-${user_group.id}`, user_group.unread_message_count);
        } else {
            localStorage.setItem(`unread_message_count-${user_group.websocket_token}`, user_group.unread_message_count);
        }
    })

    group_list.forEach(group => {
        localStorage.setItem(`unread_message_count-${group.id}`, group.unread_message_count);
    })
}

function get_message_date(time_in_millisec) {
    let message_date = new Date(time_in_millisec);
    message_date = message_date.toLocaleDateString();

    let curr_date = new Date();
    curr_date = curr_date.toLocaleDateString();

    let yes_date = get_yesterday_date();
    yes_date = yes_date.toLocaleDateString();

    return message_date == curr_date ? 'Today' : message_date == yes_date ? 'Yesterday' : message_date;
}

function get_yesterday_date() {
    return new Date(new Date().getTime() - 24*60*60*1000);
}

function get_chat_date_html (message_date) {
    return `<div class="livechat-group-today-unread-load-message-indicator-wrapper">
                <div class="livechat-group-today-unread-load-message-line-div"></div>
                <div class="livechat-group-today-unread-load-message-text-div">
                    <div class="group-today-unread-load-message-text">
                        ${message_date}
                    </div>
                </div>
            </div>`;
}

function get_chat_load() {
    return state.chat_load;
}

function set_chat_load(chat_load) {
    state.chat_load = chat_load;
}

export function update_agent_last_seen(token, last_seen_time) {
    state.agent_last_seen[token] = last_seen_time;
}

export function get_message_status() {
    return {
        is_delivered: state.is_delivered,
        is_read: state.is_read,
        is_sent: state.is_sent,
    }
}

export function get_tick() {
    return state.tick;
}

export function reset_date_set() {
    state.date_set = new Set();
}

export {
    go_to_one_on_one_chat,
    send_internal_message_to_user,
    append_internal_chat_response_server,
    get_current_receiver_username,
    upload_internal_file_attachment,
    internal_chat_scroll_to_bottom,
    get_sender_websocket_token,
    get_current_receiver_token,
    hide_previous_chat,
    show_internal_chat_console,
    set_current_receiver_details,
    initialize_internal_console,
    get_sender_username,
    get_is_group_chat,
    set_is_group_chat,
    send_message_handler,
    append_response_internal_chat_user,
    get_internal_chat_sender_name,
    append_internal_media_response_server,
    append_internal_chat_file_to_agent,
    append_internal_message_history,
    append_message_in_one_one_chat_icon,
    resize_internal_chat_window,
    get_chat_load,
    set_chat_load,
    append_last_message_time,
    reset_file_upload_modal,
    get_reply_response_user_html
};
