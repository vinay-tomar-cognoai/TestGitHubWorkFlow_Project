import axios from "axios";

import {
    get_theme_color,
    highlight_chat,
    append_unread_msg_count_in_chat_icon,
    append_message_in_chat_icon,
    append_message_in_chat_icon_new,
} from "../agent/console";
import {
    unset_every_one_to_one_chat,
    set_zero_unread_message_count,
} from "../agent/livechat_agent_socket";

import {
    close_chat_socket,
    create_websocket,
    send_message_to_internal_chat_socket,
} from "../common/livechat_internal_chat_socket";

import { get_user_initial } from "../common/archive_customer";

import {
    append_internal_chat_file_to_agent,
    append_internal_message_history,
    append_response_internal_chat_user,
    get_chat_load,
    get_current_receiver_token,
    get_internal_chat_sender_name,
    get_is_group_chat,
    get_message_status,
    get_sender_username,
    get_tick,
    hide_previous_chat,
    internal_chat_scroll_to_bottom,
    process_sentence,
    reset_date_set,
    set_chat_load,
    set_current_receiver_details,
    set_is_all_chat_loaded,
    set_is_group_chat,
    set_is_user_group,
    show_internal_chat_console,
} from "../common/livechat_internal_chat_console";

import {
    add_remove_member_from_group_events,
    disable_edit_group_details,
    disable_group_editing,
    enable_edit_group_description,
    enable_edit_group_details,
    enable_edit_group_name,
    enable_group_editing,
    get_active_group,
    get_all_agents,
    get_group_list,
    search_available_agents,
    set_active_group,
    set_is_adding_member,
    show_add_members_div,
    update_available_agents,
    update_group_details,
    update_group_members,
} from "./manage_group";
import {
    custom_decrypt,
    encrypt_variable,
    get_params,
    showToast,
    stripHTML,
    strip_unwanted_characters,
    getCsrfToken,
} from "../utils";
import { get_character_limit } from "../common";

const state = {
    previous_chat_console_id: null,
};

function go_to_group(id, is_removed = false) {
    if (is_removed) {
        hide_group_console();
        remove_group_chat(id);
        hide_group_header();
        return;
    }

    set_is_group_chat(true);
    set_is_user_group(false);
    set_is_adding_member(false);
    const prev_active_group = get_active_group();

    const previous_chat_console_id = prev_active_group.id;
    state.previous_chat_console_id = previous_chat_console_id;

    close_chat_socket();
    highlight_chat(previous_chat_console_id, id);
    hide_previous_chat();
    set_current_receiver_details(id, "group");
    update_group_display_info(id);

    const active_group = get_active_group();
    const member = active_group.members.filter((value, index, arr) => {
        return value.name == get_sender_username();
    });

    show_internal_chat_console(id);
    document.getElementById('groupchat-user-search-global').value = '';

    show_group_header(active_group, member[0]);

    // if (active_group.admin == member[0].name) {
    //     document.getElementById("livechat-group-console-menu").style.display = "block";
    // }

    $('#livechat_add_members_btn').hide();

    set_chat_load({
        index: 0,
        is_completed: false,
        limit: get_chat_load().limit,
    });

    reset_date_set();
    update_internal_chat_group_history(id);

    if (active_group.is_deleted || member[0].has_left || member[0].is_removed) {
        disable_group_editing();
        document.getElementById("livechat_input_box").style.display = "none";
        document.getElementById(
            "livechat_cant_send_message_div"
        ).style.display = "flex";
    } else {
        document.getElementById("livechat_input_box").style.display = "flex";
        document.getElementById(
            "livechat_cant_send_message_div"
        ).style.display = "none";
        enable_group_editing();
        create_websocket(id, true);
    }
}

export function show_group_header(active_group, member) {
    const name_elem = document.getElementById('livechat_group_name_header');

    if(name_elem) {
        name_elem.innerHTML = stripHTML(active_group.name);
        name_elem.style.display = 'block';
    }

    const is_admin = active_group.admin == member.name;

    if ( !is_admin && !member.has_left && !active_group.is_deleted && !member.is_removed) {
        document.getElementById('livechat_group_leave_button').style.display = 'block';
        document.getElementById('livechat_group_delete_button').style.display = 'none';
    } else {
        document.getElementById('livechat_group_delete_button').style.display = 'block';
        document.getElementById('livechat_group_leave_button').style.display = 'none';
    }
}

export function hide_group_header() {
    document.getElementById('livechat_group_name_header').style.display = 'none';
    document.getElementById('livechat_group_leave_button').style.display = 'none';
    document.getElementById('livechat_group_delete_button').style.display = 'none';
}

function update_internal_chat_group_history(id, is_more_chat_loaded) {
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
        .post("/livechat/get-group-chat-history/", params, config)
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

function get_default_html_code_for_group_details(active_group, member) {
    const theme_color = get_theme_color();

    let temp_html = `
                <div class="live-chat-customer-details-todo" style="background-color: #fff;">
                    <div class="livechat-details-card-div">
                        <div class="live-chat-customer-name">
                            <div class="livechat-info-heading-div">
                                Group
                            </div>
            
                            <div style="display: flex; align-items: center;">
                                <div class="live-chat-mobile-display back-arrow">
                                    <img src="/static/LiveChatApp/img/mobile-back.svg" alt="Back arrow" id="live-chat-customer-details-closer" onclick="close_customer_details()">
                                </div>
                                <div style="display: flex; align-items: center;">
                                <div id="livechat-group-details-icon" style="width: 34px; height: 34px; border-radius: 50%; background: #C4C4C4; display: flex; align-items: center; justify-content: center; cursor: pointer;"> G </div>
                                <p class="live-chat-customer-name-text" id="livechat-group-details-group-name"> Group Name </p>
                            </div>
                        </div>`;
    
    if (active_group.admin == member.name || member.is_supervisor || member.is_admin) {
        if (active_group.is_deleted || member.has_left || member.is_removed) {
            temp_html += `
                        <button class="customer-details-refresh-button" id="refresh_group_details_btn" style="pointer-events: auto;">
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M14.7015 5.29286C13.3432 3.93453 11.4182 3.15119 9.30154 3.36786C6.2432 3.67619 3.72654 6.15953 3.38487 9.21786C2.92654 13.2595 6.05154 16.6679 9.9932 16.6679C12.6515 16.6679 14.9349 15.1095 16.0015 12.8679C16.2682 12.3095 15.8682 11.6679 15.2515 11.6679C14.9432 11.6679 14.6515 11.8345 14.5182 12.1095C13.5765 14.1345 11.3182 15.4179 8.85154 14.8679C7.00154 14.4595 5.50987 12.9512 5.1182 11.1012C4.4182 7.86786 6.87654 5.00119 9.9932 5.00119C11.3765 5.00119 12.6099 5.57619 13.5099 6.48453L12.2515 7.74286C11.7265 8.26786 12.0932 9.16786 12.8349 9.16786H15.8265C16.2849 9.16786 16.6599 8.79286 16.6599 8.33453V5.34286C16.6599 4.60119 15.7599 4.22619 15.2349 4.75119L14.7015 5.29286Z" fill="#717171"></path>
                            </svg>
                        </button>
                        <button id="livechat_customer_details_edit_btn" class="livechat-customer-detail-edit-disabled-btn">
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="${theme_color.one}" xmlns="http://www.w3.org/2000/svg">
                                <path d="M12.2417 6.58543L6.2702 12.5584C5.9498 12.8788 5.54835 13.1061 5.10877 13.216L2.81777 13.7887C2.45158 13.8803 2.11988 13.5486 2.21143 13.1824L2.78418 10.8914C2.89407 10.4518 3.12137 10.0504 3.44177 9.72996L9.41331 3.75701L12.2417 6.58543ZM13.6567 2.3435C14.4377 3.12455 14.4377 4.39088 13.6567 5.17193L12.9488 5.87833L10.1204 3.0499L10.8282 2.3435C11.6093 1.56245 12.8756 1.56245 13.6567 2.3435Z"></path>
                            </svg>
                        </button>      
                        `;
        } else {
            temp_html += `
                    <button class="customer-details-refresh-button" id="refresh_group_details_btn" style="pointer-events: auto;">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M14.7015 5.29286C13.3432 3.93453 11.4182 3.15119 9.30154 3.36786C6.2432 3.67619 3.72654 6.15953 3.38487 9.21786C2.92654 13.2595 6.05154 16.6679 9.9932 16.6679C12.6515 16.6679 14.9349 15.1095 16.0015 12.8679C16.2682 12.3095 15.8682 11.6679 15.2515 11.6679C14.9432 11.6679 14.6515 11.8345 14.5182 12.1095C13.5765 14.1345 11.3182 15.4179 8.85154 14.8679C7.00154 14.4595 5.50987 12.9512 5.1182 11.1012C4.4182 7.86786 6.87654 5.00119 9.9932 5.00119C11.3765 5.00119 12.6099 5.57619 13.5099 6.48453L12.2515 7.74286C11.7265 8.26786 12.0932 9.16786 12.8349 9.16786H15.8265C16.2849 9.16786 16.6599 8.79286 16.6599 8.33453V5.34286C16.6599 4.60119 15.7599 4.22619 15.2349 4.75119L14.7015 5.29286Z" fill="#717171"></path>
                        </svg>
                    </button>
                    <button id="livechat_customer_details_edit_btn" class="">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="${theme_color.one}" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12.2417 6.58543L6.2702 12.5584C5.9498 12.8788 5.54835 13.1061 5.10877 13.216L2.81777 13.7887C2.45158 13.8803 2.11988 13.5486 2.21143 13.1824L2.78418 10.8914C2.89407 10.4518 3.12137 10.0504 3.44177 9.72996L9.41331 3.75701L12.2417 6.58543ZM13.6567 2.3435C14.4377 3.12455 14.4377 4.39088 13.6567 5.17193L12.9488 5.87833L10.1204 3.0499L10.8282 2.3435C11.6093 1.56245 12.8756 1.56245 13.6567 2.3435Z"></path>
                        </svg>
                    </button>      
                    `;
        }
    }

    temp_html += `
                    </div>
                    <div class="livechat-customer-personal-details-wrapper">
                        <div class="livechat-customer-personal-details">
                            <div class="livechat-group-details-edit-div">
                                Edit Group Details
                            </div>
                            <div class="livechat-customer-detail-items-wrapper" style="flex-direction: row !important; align-items: center;">
                                <div class="livechat-customer-detail-icon-wrapper">
                                    <div class="livechat-customer-detail-icon-div">
                                        <svg fill="${theme_color.one}" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <circle cx="10" cy="10" r="10" fill="#F8F8F8"/>
                                            <path fill-rule="evenodd" clip-rule="evenodd" d="M13.4695 5.01915C13.3446 5.04403 13.2004 5.10504 13.0867 5.18098C13.0278 5.22036 12.1312 6.10311 11.055 7.18122C9.2509 8.98869 9.12755 9.11655 9.10853 9.19888C9.09737 9.24723 9.05058 9.60839 9.00458 10.0015L8.92093 10.7162L8.97599 10.8287C9.03735 10.9541 9.15071 11.0426 9.2768 11.0635C9.3176 11.0702 9.66129 11.0378 10.0739 10.9883C10.6399 10.9203 10.8159 10.8926 10.8747 10.8621C10.9196 10.8388 11.7318 10.0392 12.8851 8.88288C14.6699 7.09348 14.8249 6.93288 14.8815 6.81482C15.0478 6.46744 15.0392 6.11798 14.855 5.7449C14.7828 5.59854 14.7337 5.53093 14.6056 5.40141C14.474 5.26835 14.4136 5.22413 14.2605 5.14857C13.9908 5.0155 13.7145 4.97028 13.4695 5.01915ZM13.8659 5.88104C14.0493 5.96988 14.1617 6.13884 14.1624 6.3271L14.1629 6.43412L12.3318 8.26603L10.5007 10.098L10.171 10.1374C9.98966 10.159 9.83765 10.1731 9.8332 10.1687C9.82876 10.1642 9.84333 10.0123 9.8656 9.83113L9.9061 9.50165L11.678 7.72707C12.6526 6.75104 13.4843 5.927 13.5262 5.89585C13.6211 5.82528 13.74 5.8201 13.8659 5.88104ZM5.97946 6.27958C5.52246 6.37843 5.12835 6.77628 5.0322 7.23582C4.98927 7.44107 4.98927 13.8085 5.0322 14.0138C5.10657 14.3692 5.36195 14.6987 5.68775 14.8595C5.98891 15.0082 5.77278 14.9995 9.15891 14.9999C12.5203 15.0002 12.3526 15.0064 12.6297 14.8729C12.9454 14.7207 13.1894 14.4272 13.2961 14.0711C13.328 13.9647 13.3314 13.8175 13.3375 12.2783C13.3451 10.3735 13.3511 10.4572 13.1981 10.3162C13.0477 10.1776 12.8659 10.1626 12.6898 10.2742C12.622 10.3172 12.5861 10.3586 12.5508 10.4345L12.5031 10.5369L12.5025 12.1874C12.5019 13.7415 12.4998 13.8425 12.4663 13.9163C12.4219 14.0141 12.3113 14.1128 12.215 14.1407C12.1629 14.1558 11.259 14.1603 9.12224 14.1563L6.10307 14.1505L6.02661 14.0971C5.98456 14.0677 5.92819 14.0113 5.90134 13.9716L5.85251 13.8994L5.84745 10.6443L5.84241 7.38909L5.88802 7.3027C5.91311 7.25517 5.97106 7.18991 6.0168 7.15768L6.09998 7.09908L8.009 7.08932L9.918 7.07955L10.0141 7.02085C10.2111 6.90055 10.2759 6.63254 10.1529 6.44666C10.1239 6.40281 10.0635 6.34269 10.0187 6.31306L9.93731 6.25916L8.02185 6.25565C6.43966 6.25274 6.08432 6.2569 5.97946 6.27958Z" />
                                        </svg>
                                    </div>
                                </div>
                                <div class="live-chat-content" id="livechat-group-details-created-data">12-Dec-2021</div>
                            </div>
                            <div class="livechat-customer-detail-items-wrapper">
                                <div class="livechat-customer-detail-icon-wrapper">
                                    <div class="livechat-customer-detail-icon-div">
                                        <svg fill="${theme_color.one}" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <circle cx="10" cy="10" r="10" fill="#F8F8F8"/>
                                            <path fill-rule="evenodd" clip-rule="evenodd" d="M10 5C8.89543 5 8 5.89543 8 7C8 8.10457 8.89543 9 10 9C11.1046 9 12 8.10457 12 7C12 5.89543 11.1046 5 10 5ZM9 7C9 6.44772 9.44772 6 10 6C10.5523 6 11 6.44772 11 7C11 7.55228 10.5523 8 10 8C9.44772 8 9 7.55228 9 7Z" />
                                            <path fill-rule="evenodd" clip-rule="evenodd" d="M12.5 10L7.49998 10C6.67156 10 6 10.6716 6 11.5C6 12.6161 6.45897 13.5103 7.21215 14.1148C7.95342 14.7098 8.94692 15 10 15C11.0531 15 12.0466 14.7098 12.7879 14.1148C13.541 13.5103 14 12.6161 14 11.5C14 10.6716 13.3284 10 12.5 10ZM7.49998 11L12.5 11C12.7761 11 13 11.2239 13 11.5C13 12.3169 12.6755 12.9227 12.1619 13.3349C11.6364 13.7567 10.8799 14 10 14C9.12008 14 8.36358 13.7567 7.8381 13.3349C7.32453 12.9227 7 12.3169 7 11.5C7 11.2239 7.22387 11 7.49998 11Z" />
                                        </svg>
                                    </div>
                                    <div class="livechat-customer-detail-label" style="display: none;">Group Name</div>
                                </div>
                                <input type="text" class="live-chat-content" id="livechat-group-details-group-name-edit" value="MNP" readonly />
                            </div>
                            <div class="livechat-customer-detail-items-wrapper" style="align-items: baseline;">
                                <div class="livechat-customer-detail-icon-wrapper">
                                    <div class="livechat-customer-detail-icon-div">
                                        <svg fill="${theme_color.one}" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <circle cx="10" cy="10" r="10" fill="#F8F8F8"/>
                                            <path fill-rule="evenodd" clip-rule="evenodd" d="M5.2452 5.05485C5.188 5.08503 5.10941 5.15475 5.07059 5.20982L5 5.30991V10.0039V14.6979L5.05882 14.7847C5.09118 14.8325 5.15911 14.9004 5.20976 14.9357L5.30186 15H10H14.6981L14.7902 14.9357C14.8409 14.9004 14.9088 14.8325 14.9412 14.7847L15 14.6979V10.0058V5.3136L14.9357 5.22161C14.9003 5.17102 14.8323 5.10317 14.7845 5.07086L14.6976 5.0121L10.0234 5.00606L5.34922 5L5.2452 5.05485ZM14.0181 6.49854L14.0245 6.99793H10.0005H5.97647V6.50834C5.97647 6.23904 5.98355 6.01164 5.99224 6.003C6.00089 5.99435 7.80882 5.98993 10.0099 5.9932L14.0118 5.99914L14.0181 6.49854ZM14.0177 11.0107L14.0118 14.013H10H5.98824L5.98226 11.0107L5.97628 8.00847H10H14.0237L14.0177 11.0107ZM7.28235 9.55152C6.89609 9.75454 6.89228 10.2578 7.27553 10.4547C7.35993 10.4981 7.45054 10.4995 9.99318 10.4991C12.5032 10.4986 12.6278 10.4965 12.7176 10.455C13.1038 10.2765 13.1077 9.75429 12.7245 9.55737C12.64 9.51401 12.5497 9.51256 9.99506 9.51347C7.63459 9.51432 7.34541 9.51836 7.28235 9.55152ZM7.32179 11.5369C7.20795 11.5696 7.04393 11.7433 7.0108 11.8662C6.9504 12.0902 7.04572 12.3285 7.24181 12.4436L7.35294 12.5089H8.74118H10.1294L10.2343 12.4501C10.3919 12.3618 10.478 12.2242 10.4896 12.0423C10.5003 11.8752 10.4553 11.7582 10.3375 11.6465C10.1908 11.5075 10.2196 11.5099 8.74781 11.5122C7.96621 11.5134 7.36715 11.5238 7.32179 11.5369Z" />
                                        </svg>
                                    </div>
                                    <div class="livechat-customer-detail-label" style="display: none;">Description </div>
                                </div>
                                <textarea class="live-chat-details-admin-description-text live-chat-content" readonly id="livechat-group-details-description" maxlength="500">Descrdfzzsdfgxfgzdfgfdffxfxdff                    </textarea>
                            </div>
                        </div>
                        <div class="customer-detail-cancel-save-btns" style="display: none;">
                            <button class="customer-detail-cancel-btn" id="livechat_customer_details_cancel_edit_btn">Cancel</button>
                            <button class="customer-detail-save-btn" id="livechat_customer_details_save_btn" style="background-color: ${theme_color.one};">Save</button>
                        </div>
                    </div>
                </div><div class="live-chat-customer-full-details">`;
    
    if (active_group.admin == member.name || member.is_supervisor || member.is_admin) {
        temp_html += `
        <div style="display: flex; flex-flow: column; padding: 12px 20px 4px 12px;">
            <div class="livechat-customer-group-add-member-div livechat-group-chats-header">
                <p style="color: #000; font-size: 14px;">Members</p>
                <div class="livechat-group-chats-header-search">
                    <div class="search-container" id="group_members_search_div" style="display: none;">
                        <button type="submit">
                            <!-- <img src="./img/Vector-search.svg"> -->
                            <svg width="13" height="13" viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <rect width="13" height="13" fill="#E5E5E5"></rect>
                                <g clip-path="url(#clip0)">
                                <rect width="1440" height="660" transform="translate(-1209 -141)" fill="white"></rect>
                                <rect x="-962" y="-85" width="1193" height="604" fill="#FAFAFA"></rect>
                                <rect x="-952" y="-74" width="1174" height="114" fill="white"></rect>
                                <g filter="url(#filter0_d)">
                                <rect x="-14" y="-10" width="219" height="33" rx="5" fill="white"></rect>
                                </g>
                                <path d="M5.55942 11.1182C6.79289 11.118 7.99083 10.7051 8.96247 9.94526L12.0174 13L13 12.0174L9.9451 8.96269C10.7054 7.991 11.1185 6.79285 11.1188 5.55912C11.1188 2.49396 8.62474 0 5.55942 0C2.49409 0 0 2.49396 0 5.55912C0 8.62428 2.49409 11.1182 5.55942 11.1182ZM5.55942 1.38978C7.85893 1.38978 9.72898 3.25973 9.72898 5.55912C9.72898 7.85851 7.85893 9.72846 5.55942 9.72846C3.2599 9.72846 1.38985 7.85851 1.38985 5.55912C1.38985 3.25973 3.2599 1.38978 5.55942 1.38978Z" fill="#757575"></path>
                                </g>
                                <defs>
                                <filter id="filter0_d" x="-22" y="-18" width="235" height="49" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
                                <feFlood flood-opacity="0" result="BackgroundImageFix"></feFlood>
                                <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"></feColorMatrix>
                                <feOffset></feOffset>
                                <feGaussianBlur stdDeviation="4"></feGaussianBlur>
                                <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.08 0"></feColorMatrix>
                                <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow"></feBlend>
                                <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow" result="shape"></feBlend>
                                </filter>
                                <clipPath id="clip0">
                                <rect width="1440" height="660" fill="white" transform="translate(-1209 -141)"></rect>
                                </clipPath>
                                </defs>
                            </svg>
                                
                        </button>
                        <input type="text" id="search_available_agents" placeholder="Search" name="search" autocomplete="off">
                        <!-- <input type="text" placeholder="Search" name="search" autocomplete="off"> -->
                    </div>
                </div>`;
        
        if (active_group.is_deleted || member.has_left || member.is_removed) {
            temp_html += `
                        <button class="customer-details-admin-add-member-button customer-details-admin-add-member-button-disabled" style="display: block;">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <rect width="24" height="24" fill="#FAFAFA"></rect>
                                <path d="M17.9999 13H12.9999V18C12.9999 18.55 12.5499 19 11.9999 19C11.4499 19 10.9999 18.55 10.9999 18V13H5.99994C5.44994 13 4.99994 12.55 4.99994 12C4.99994 11.45 5.44994 11 5.99994 11H10.9999V6C10.9999 5.45 11.4499 5 11.9999 5C12.5499 5 12.9999 5.45 12.9999 6V11H17.9999C18.5499 11 18.9999 11.45 18.9999 12C18.9999 12.55 18.5499 13 17.9999 13Z" fill="black"></path>
                            </svg>
                        </button>
                        `
        } else {
            temp_html += `
                        <button class="customer-details-admin-add-member-button" id="add_group_members_btn" style="display: block;">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <rect width="24" height="24" fill="#FAFAFA"></rect>
                                <path d="M17.9999 13H12.9999V18C12.9999 18.55 12.5499 19 11.9999 19C11.4499 19 10.9999 18.55 10.9999 18V13H5.99994C5.44994 13 4.99994 12.55 4.99994 12C4.99994 11.45 5.44994 11 5.99994 11H10.9999V6C10.9999 5.45 11.4499 5 11.9999 5C12.5499 5 12.9999 5.45 12.9999 6V11H17.9999C18.5499 11 18.9999 11.45 18.9999 12C18.9999 12.55 18.5499 13 17.9999 13Z" fill="black"></path>
                            </svg>
                        </button>
                        `
        }

        temp_html += `
                <button class="customer-details-admin-add-member-button" id="add_new_members_btn" style="display: none;">
                    <svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"
                        viewBox="0 0 80.588 61.158" style="enable-background:new 0 0 80.588 61.158;" xml:space="preserve" width="16" height="16">
                    <path style="fill:#231F20;" d="M29.658,61.157c-1.238,0-2.427-0.491-3.305-1.369L1.37,34.808c-1.826-1.825-1.826-4.785,0-6.611
                        c1.825-1.826,4.786-1.827,6.611,0l21.485,21.481L72.426,1.561c1.719-1.924,4.674-2.094,6.601-0.374
                        c1.926,1.72,2.094,4.675,0.374,6.601L33.145,59.595c-0.856,0.959-2.07,1.523-3.355,1.56C29.746,61.156,29.702,61.157,29.658,61.157z
                        "/>
                    </svg>
                </button>
            </div>
            <div class="livechat-customer-group-member-list-area">
            <div id="add_group_members" style="display: none;">

                <div class="livechat-customer-group-search-result-list-div" style="display: none;">
                    <div class="livechat-customer-group-search-result-list-wrapper" id="all_agents_search_div">
                    </div>
                </div>
                <div class="livechat-customer-group-search-added-result-div" id="livechat-group-tentative-added-members" style="display: none;">
                    <div class="livechat-customer-group-search-added-heading">Added</div>
                </div>
            </div>
        </div>`;
    } else {
        temp_html += '<div style="display: flex; flex-flow: column; padding: 12px 20px 4px 12px;">'
    }
    
    temp_html += `
                        <div class="livechat-customer-group-active-member-count-div">1 Members</div>
                    </div>
                </div>
                <div class="livechat-customer-group-member-items-list-area" id="livechat-group-members-list">
                </div>`

    if (active_group.admin == member.name) {
        temp_html += `<div style="display: flex; align-items: center; justify-content: center; padding-bottom: 40px;">
                        <button class="btn btn-danger" id="remove_group_btn_2" style="display: none;" data-toggle="modal" data-target="#livechat-remove-group-modal">Remove Group</button>
                        </div>`;
    }

    temp_html += `</div></div>`;
            
    return temp_html;
}
function update_group_display_info(id) {
    const group_list = get_group_list();
    const group_detail = group_list[id];

    update_active_group(id, group_detail);

    const active_group = get_active_group();
    const member = active_group.members.filter((value, index, arr) => {
        return value.name == get_sender_username();
    });

    document.getElementById("live-chat-group-details-sidebar").innerHTML =
        get_default_html_code_for_group_details(active_group, member[0]);

    document.getElementById("livechat-group-details-group-name").innerHTML =
    stripHTML(group_detail.name);
    
    document.getElementById("livechat-group-details-group-name-edit").value =
        group_detail.name;
    
    document.getElementById("livechat-group-details-description").value =
        group_detail.desc;
    
    document.getElementById(
        "livechat-group-details-created-data"
    ).innerHTML = `Created ${group_detail.created_date}`;
    
    if (group_detail.icon_path) {

        document.getElementById(
            "livechat-group-details-icon"
        ).innerHTML = `<img src="/${group_detail.icon_path}" onclick="preview_livechat_attachment_image('${window.location.origin}/${group_detail.icon_path}')" style="width: inherit; height: inherit; border-radius: 50%; cursor: pointer;" />`;
    } else {

        document.getElementById(
            "livechat-group-details-icon"
        ).innerHTML = `<div class="live-chat-client-image">${group_detail.name[0].toUpperCase()}</div>`;
    }

    try {
        document.getElementById("add_group_members").style.display = "none";

        document.getElementById("livechat_save_group_name").style.display =
            "none";
        document.getElementById("livechat_edit_group_name").style.display =
            "block";
        document.getElementById(
            "livechat_save_group_description"
        ).style.display = "none";
        document.getElementById(
            "livechat_edit_group_description"
        ).style.display = "block";
        document.getElementById("add_group_members_btn").style.display =
            "block";
        document.getElementById("search_available_agents").value = "";
    } catch (err) {}

    const group_owner = group_detail.members.filter((value, index, arr) => {
        return value.name == group_detail.admin;
    });

    const html = get_members_display_html(
        group_detail.members,
        group_owner[0],
    );

    $("#livechat-group-members-list").html(html);

    $("#search_available_agents").on("keyup", (e) => {
        update_available_agents();
    });

    add_group_sidebar_click_events();
    add_remove_member_from_group_events();

    $(".livechat-customer-group-active-member-count-div").html(
        `${active_group.member_name.length} Members`
    );

    document.getElementById("live-chat-no-chat-opened").style.display = "none";
    document.getElementById("live-chat-group-details-sidebar").style.display =
        "flex";
}

function add_group_sidebar_click_events() {
    $("#add_group_members_btn").on("click", function (e) {
        show_add_members_div(e.target);
    });

    $("#add_new_members_btn").on("click", function (e) {
        update_group_members(e.target);
    });

    $("#livechat_customer_details_edit_btn").on ('click', e => {
        enable_edit_group_details(e);
    });

    $("#livechat_customer_details_cancel_edit_btn").on ('click', e => {
        disable_edit_group_details(e);
    });

    $("#livechat_customer_details_save_btn").on ('click', e => {
        update_group_details();
    });

    $('#refresh_group_details_btn').on('click', () => {
        update_group_display_info(get_active_group().id);
    })
}

function update_active_group(id, group_detail) {
    const active_group = {};
    active_group.id = id;
    active_group.name = group_detail.name;
    active_group.desc = group_detail.desc;
    active_group.members = group_detail.members;
    active_group.added_agents = [];
    active_group.member_name = [];
    active_group.removed_member = null;
    active_group.member_name = [];
    active_group.is_deleted = group_detail.is_deleted;
    active_group.admin = group_detail.admin;
    for (const member of group_detail.members) {
        if (!member.is_removed && !member.has_left) active_group.member_name.push(member.name);
    }

    set_active_group(active_group);
    unset_every_one_to_one_chat();
}

function get_members_display_html(members, admin) {
    let html = "";

    html += `                    
            <div class="livechat-customer-group-member-items-div">
                <div class="livechat-customer-group-member-icon-div">
                    ${get_user_initial(admin.name)}
                </div>
                <div style="width: 100%";>
                    <div class="livechat-customer-group-member-name-div livechat-customer-group-member-name-with-profile" style="width: 100%";>${admin.name}</div>
                    <div class="livechat-customer-group-supervisor-identity-div">
                        ${admin.is_supervisor ? 'Supervisor': 'Admin'}
                    </div>
                </div>
            </div>
                `;

    let curr_member = members.filter((value, index, arr) => {
        return value.name == get_sender_username();
    });
    curr_member = curr_member[0];
    const all_agents = get_all_agents();
    const active_group = get_active_group();

    for (const member of members) {
        if (member.is_removed || admin.name == member.name || member.has_left) continue;

        if ((curr_member.is_supervisor || curr_member.is_admin) &&
                curr_member.name != member.name &&
                all_agents.includes(member.name) && !member.is_admin &&
                (!member.is_supervisor || curr_member.is_admin || curr_member == admin)) {

            html += `<div class="livechat-customer-group-member-items-div">
            <div class="livechat-customer-group-member-icon-div">
                ${get_user_initial(member.name)}
            </div>
            <div style="width: 51%;">
            <div class="livechat-customer-group-member-name-div livechat-group-member" style="width: 100%;">${
                member.name
            }</div>`;

            if (member.is_supervisor) {
                html += `
                    <div class="livechat-customer-group-supervisor-identity-div">
                            Supervisor
                        </div>
                    </div>
                `
            } else if (member.is_admin) {
                html += `
                    <div class="livechat-customer-group-supervisor-identity-div">
                            Admin
                        </div>
                    </div>
                `
            } else {
                html += `</div>`
            }

            if (active_group.is_deleted || curr_member.is_removed || curr_member.has_left) {
                html += `<button class="livechat-customer-group-member-remove-button removed-group" id="remove_member-${member.name}">
                            Remove
                        </button>`;
            } else {
                html += `<button class="livechat-customer-group-member-remove-button" id="remove_member-${member.name}">
                            Remove
                        </button>`;
            }
    
        } else {
            html += `<div class="livechat-customer-group-member-items-div">
            <div class="livechat-customer-group-member-icon-div">
                ${get_user_initial(member.name)}
            </div>
            <div style="width: 100%;">
            <div class="livechat-customer-group-member-name-div livechat-group-member" style="width: 100%;">${
                member.name
            }</div>`;

            if (member.is_supervisor) {
                html += `
                    <div class="livechat-customer-group-supervisor-identity-div">
                            Supervisor
                        </div>
                    </div>
                `
            } else if (member.is_admin) {
                html += `
                    <div class="livechat-customer-group-supervisor-identity-div">
                            Admin
                        </div>
                    </div>
                `
            } else {
                html += `</div>`
            }

        }

        html += `</div>`;
    }

    return html;
}

function send_message_to_group() {
    const theme_color = get_theme_color();
    document.getElementById("fill-submit-btn").style.fill = theme_color.two;

    var sentence = process_sentence($("#query").val());

    if (sentence.trim() == "") return;

    append_response_internal_chat_user(sentence, window.SENDER_NAME, false);
    const active_group = get_active_group();
    const group_id = active_group.id;

    var json_string = JSON.stringify({
        message: sentence,
        sender: "user",
        attached_file_src: "",
        thumbnail_url: "",
        receiver_username: "group",
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
        receiver_username: "group",
        sender_websocket_token: group_id,
        sender_name: get_internal_chat_sender_name(),
        sender_username: get_sender_username(),
        is_group: true,
    });

    send_message_to_internal_chat_socket(temp_message, "User", true);
}

function send_media_message_to_group(
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

        const active_group = get_active_group();
        const chat_console_id = active_group.id;

        var json_string = JSON.stringify({
            message: sentence,
            sender: "user",
            attached_file_src: attached_file_src,
            thumbnail_url: thumbnail_url,
            receiver_username: "group",
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
            receiver_username: "group",
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

function hide_group_console() {
    document.getElementById("live-chat-group-details-sidebar").style.display =
        "none";
    document.getElementById("livechat-main-console").style.display = "none";
    document.getElementById("live-chat-no-chat-opened").style.display = "block";
}

function remove_group_chat(id) {
    const chat_div = document.getElementById(`style-2_${id}`);

    if (chat_div) {
        chat_div.remove();
    }
}

function append_message_in_group_chat_icon(group_list) {
    for (const group of group_list) {
        if (
            group.last_message.sender.toLowerCase() == "system" &&
            (group.last_message.text.includes("changed the") ||
                group.last_message.text.includes("removed"))
        ) {
            group.last_message.text = group.last_message.text.replace(
                " " + get_sender_username() + " ",
                " you "
            );

            if (group.last_message.sender_username == get_sender_username()) {
                group.last_message.text = "you " + group.last_message.text;
            } else {
                group.last_message.text =
                    group.last_message.sender_username +
                    " " +
                    group.last_message.text;
            }
        }

        let msg = {
            text_message: group.last_message.text,
            sender: group.last_message.sender,
            is_attachment: "False",
        };

        if (group.last_message.filename != "") {
            msg.attachment_name = group.last_message.filename;
            msg.is_attachment = "True";
        }

        append_message_in_chat_icon_new(group.id, msg, true);
    }
}

export function update_group_user_last_seen (username) {
    if (get_is_group_chat()) {
        const active_group = get_active_group();
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

export function get_min_last_seen(members) {
    let min_last_seen = -1;

    members.forEach(member => {
        if (member.name != get_sender_username() && !member.is_removed && !member.has_left) {

            if (min_last_seen == -1) {
                min_last_seen = member.last_seen_time;
            } else {
                min_last_seen = Math.min(min_last_seen, member.last_seen_time);
            }
        }
    })

    return min_last_seen;
}

export function update_group_user_last_seen_on_chat (username, group_id) {
        const group_list = get_group_list();
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

export function get_min_last_seen_on_chat(members) {
    let min_last_seen = -1;

    members.forEach(member => {
        if (member.name != get_sender_username() && !member.is_removed && !member.has_left) {

            if (min_last_seen == -1) {
                min_last_seen = member.last_seen_on_chat;
            } else {
                min_last_seen = Math.min(min_last_seen, member.last_seen_on_chat);
            }
        }
    })

    return min_last_seen;
}

export function mark_group_messages_as_delivered(id, last_seen_time) {
    let all_ticks = document.querySelectorAll(`.blue_tick-${id}.single_tick`);

    all_ticks.forEach(tick => {
        if (tick.dataset.time <= last_seen_time) {
            tick.innerHTML = get_tick().double;
            $(tick).removeClass('single_tick');
            $(tick).addClass('double_tick');
        }
    })
}

export function mark_group_messages_as_read(id, last_seen_time) {
    let all_ticks = document.querySelectorAll(`.blue_tick-${id}.single_tick, .blue_tick-${id}.double_tick`);

    all_ticks.forEach(tick => {
        if (tick.dataset.time <= last_seen_time) {
            tick.innerHTML = get_tick().blue;
            $(tick).removeClass('single_tick');
            $(tick).removeClass('double_tick');

            $(tick).addClass('blue_tick');
        }
    })
}

export {
    go_to_group,
    send_message_to_group,
    update_group_display_info,
    send_media_message_to_group,
    hide_group_console,
    remove_group_chat,
    append_message_in_group_chat_icon,
    update_internal_chat_group_history,
};
