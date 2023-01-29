import { custom_decrypt, getCsrfToken, get_params, is_mobile, showToast, stripHTML, stripHTMLtags, strip_unwanted_characters } from "../utils";
import { check_and_update_notification, send_message_to_guest_agent_socket, set_one_to_one_user_list, set_user_group_list } from "../agent/livechat_agent_socket";

import axios from "axios";
import { get_user_initial } from "../common/archive_customer";
import { get_character_limit } from "../common";
import { append_message_in_group_chat_icon, go_to_group, update_group_display_info } from "./group_chat_console";
import { append_message_in_one_one_chat_icon, append_message_in_user_group_chat_icon, append_message_in_user_group_icon, get_active_user_group, get_is_group_chat, get_sender_username, go_to_user_group, highlight_chat_based_chat_type, internal_chat_scroll_to_bottom, set_unread_message_count } from "../common/livechat_internal_chat_console";
import { append_system_text_response, get_system_text_response_html, return_time } from "../agent/chatbox";
import { send_message_to_internal_chat_socket, set_sender_websocket_token } from "../common/livechat_internal_chat_socket";
import { get_theme_color, highlight_chat } from "../agent/console";

const state = {
    new_group: {
        icon: null,
        base_64: null,
        member_count: 0,
    },
    total_group_list: [],
    group_list: {},
    cropper: null,
    default_icon: `<svg width="31" height="30" viewBox="0 0 31 30" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <g opacity="0.65">
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M10.1343 27.0426H20.6995C24.8325 27.0426 27.6082 24.1435 27.6082 19.8297V9.87406C27.6082 5.56025 24.8325 2.66116 20.7007 2.66116H10.1343C6.0025 2.66116 3.22681 5.56025 3.22681 9.87406V19.8297C3.22681 24.1435 6.0025 27.0426 10.1343 27.0426ZM11.1494 13.6328C9.46871 13.6328 8.1031 12.2653 8.1031 10.5851C8.1031 8.90491 9.46871 7.53744 11.1494 7.53744C12.8288 7.53744 14.1957 8.90491 14.1957 10.5851C14.1957 12.2653 12.8288 13.6328 11.1494 13.6328ZM24.9516 18.4286C25.3598 19.4753 25.1478 20.7333 24.7114 21.77C24.194 23.0029 23.2035 23.9364 21.9556 24.344C21.4015 24.5252 20.8205 24.6044 20.2406 24.6044H9.96662C8.94425 24.6044 8.03956 24.3591 7.29791 23.9024C6.8333 23.6156 6.75117 22.9538 7.09564 22.5248C7.6718 21.8077 8.2406 21.0881 8.8143 20.3622C9.90778 18.9733 10.6445 18.5707 11.4634 18.9242C11.7956 19.0702 12.1291 19.2891 12.4723 19.5206C13.3868 20.142 14.658 20.9963 16.3326 20.0691C17.4785 19.4273 18.1431 18.3264 18.7219 17.3677L18.7316 17.3516C18.7726 17.2844 18.8132 17.2171 18.8538 17.1501C19.0483 16.8282 19.2402 16.5107 19.4573 16.2181C19.7294 15.852 20.7383 14.7072 22.0451 15.5224C22.8775 16.0357 23.5774 16.7302 24.3264 17.4737C24.6121 17.758 24.8156 18.0813 24.9516 18.4286Z" fill="black"/>
                        </g>
                        </svg>
                    `,
    active_group: {
        id: null,
        name: null,
        desc: null,
        members: [],
        member_name: [],
        added_agents: [],
        remove_member: null,
        is_deleted: false,
        admin: null,
    },
    events: {
        group_edited: false,
        adding_member: false,
        removing_member: false,
        deleting_group: false,
    },
    all_agents: window.AGENTS,
    remove_member_display_text: '<p style="font-size: 13px">Remove {} from {}?</p>'
}

function create_chat_group (el) {
    let group_name = document.getElementById('livechat-new-group-name').value.trim();
    group_name = stripHTMLtags(group_name);
    
    if (group_name == '') {
        document.getElementById('create_group_error_text').innerHTML = 'Please enter group name.';
        document.getElementById('create_group_error_text').style.display = 'block'; 
        return;
    }

    let group_desc = document.getElementById('livechat-new-group-desc').value.trim();
    group_desc = stripHTMLtags(group_desc);
    
    if (group_desc == '') {
        document.getElementById('create_group_error_text').innerHTML = 'Please enter group description.';
        document.getElementById('create_group_error_text').style.display = 'block'; 
        return;
    }
    
    const group_member_elements = $('#select-group-member-dropdown').find("option:selected");;

    const group_members = []
    Array.from(group_member_elements).forEach((member) => {
        if (member.selected) group_members.push(member.value);
    })

    if (group_members.length == 0) {
        document.getElementById('create_group_error_text').innerHTML = 'Please select some group members.';
        document.getElementById('create_group_error_text').style.display = 'block'; 
        return;
    }

    document.getElementById('create_group_error_text').style.display = 'none';

    let json_string = {
        group_name: group_name,
        group_desc: group_desc,
        group_members: group_members,
    }

    if (state.new_group.icon) {
        json_string['filename'] = state.new_group.icon.name;
        json_string['base64_file'] = state.new_group.base_64;
    }

    json_string = JSON.stringify(json_string)
    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/create-chat-group/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);
            if (response.status == 200) {
                showToast('Group created successfully.', 2000);
                update_group_chat_list({
                    is_member_removed: false,
                    is_member_added: false,
                    user_group_id: null,
                });
                $('#livechat-create-new-group-chat-modal').modal('hide');
                reset_create_group_modal();
            } else {
                document.getElementById('create_group_error_text').innerHTML = response.message;
                document.getElementById('create_group_error_text').style.display = 'block';         
            }
        })
        .catch((err) => {
            console.log(err);
            console.log("Unable to create group. Please try again later.");
        });
}

function filterList(searchTerm, id) {
    searchTerm = searchTerm.toLowerCase();
    const optionsList = document.querySelectorAll(`#${id} .option`);
    let flag = 0;
    document.querySelector(`#${id} .no-elem`).style.display = "none";
    optionsList.forEach(option => {
        let label = option.firstElementChild.innerText.toLowerCase();
        if (label.indexOf(searchTerm) != -1) {
            flag = 1;
            option.parentElement.style.display = "block";
        } else {
            option.parentElement.style.display = "none";
        }
    })
    if (flag === 0)
        document.querySelector(`#${id} .no-elem`).style.display = "block";
}

function open_agent_dropdown_list() {
    const optionsContainer = document.querySelector("#members-box-options-container");
    const selected = document.querySelector("#add-member-dropdown-wrapper .selected");
    const searchBox = document.querySelector("#member-options-search-box input");
    const dropArrow = document.querySelector("#language-dropdown-arrow");
    
    optionsContainer.classList.toggle("active");
    const is_dropdown_open = optionsContainer.classList.contains("active");
    if (is_dropdown_open) {
        selected.innerHTML = "Add Members";
        selected.style.border = "none";
        dropArrow.style.transform = "translateY(-50%) rotate(180deg)";
        searchBox.focus();
        document.getElementById('livechat_added_members_list').style.display = 'none';
        document.getElementById('member-options-search-box').style.display = 'block';
    } else {
        dropArrow.style.transform = "translateY(-50%) rotate(0deg)";
        document.getElementById('livechat_added_members_list').style.display = 'block';
        document.getElementById('member-options-search-box').style.display = 'none';
    }
    searchBox.value = "";
    filterList("", "members-box-options-container");
}

function close_dropdown_list() {
    const optionsContainer = document.querySelector("#members-box-options-container");
    optionsContainer.classList.remove("active");

    const dropArrow = document.getElementById('language-dropdown-arrow');
    dropArrow.style.transform = "translateY(-50%) rotate(0deg)";
    document.getElementById('livechat_added_members_list').style.display = 'block';
    document.getElementById('member-options-search-box').style.display = 'none';
}

function select_member (el) {
    let id = el.id;
    
    if (el.selected) {

        if (state.new_group.member_count >= GROUP_SIZE_LIMIT) {

            showToast(`Exceeding group size limit of ${GROUP_SIZE_LIMIT} members.`, 2000);
            $('#select-group-member-dropdown').multiselect('deselect', el.value);
        } else {
            
            state.new_group.member_count += 1;

            const html = `<div class="livechat-admin-group-member-list-item" id="user_${id}">    
                            <div class="livechat-admin-group-member-list-name-area livechat-tentative-group-member">
                                ${id.split('-')[0]}
                            </div>
                            <div class="livechat-admin-group-member-list-delete-icon">
                                <svg id="remove-tentative-member-${id.split('-')[1]}" class="remove-tentative-member" width="22" height="22" viewBox="0 0 25 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M19.0885 5.70999C18.9017 5.52273 18.6481 5.4175 18.3835 5.4175C18.119 5.4175 17.8654 5.52273 17.6785 5.70999L12.7885 10.59L7.89854 5.69999C7.71171 5.51273 7.45806 5.4075 7.19354 5.4075C6.92903 5.4075 6.67538 5.51273 6.48854 5.69999C6.09854 6.08999 6.09854 6.71999 6.48854 7.10999L11.3785 12L6.48854 16.89C6.09854 17.28 6.09854 17.91 6.48854 18.3C6.87854 18.69 7.50854 18.69 7.89854 18.3L12.7885 13.41L17.6785 18.3C18.0685 18.69 18.6985 18.69 19.0885 18.3C19.4785 17.91 19.4785 17.28 19.0885 16.89L14.1985 12L19.0885 7.10999C19.4685 6.72999 19.4685 6.08999 19.0885 5.70999Z" fill="black" fill-opacity="0.54"/>
                                    </svg>
                            </div>
                        </div>`;

            if (!document.getElementById(`user_${id}`)) {
                $('#livechat_added_members_list').append(html);
            }
        }
    } else {
        if (document.getElementById(`user_${id}`)) {
            document.getElementById(`user_${id}`).remove();
            state.new_group.member_count -= 1;
        }
    }

    $(`#remove-tentative-member-${id.split('-')[1]}`).on('click', function(e) {
        state.new_group.member_count -= 1;
        remove_selected_member(e.target);
    })
}

function remove_selected_member (el) {
    if (el) {
        let id = el.parentElement.parentElement.id;

        if (!id) {
            id = el.parentElement.parentElement.parentElement.id;
            el.parentElement.parentElement.parentElement.remove();
        } else {
            el.parentElement.parentElement.remove();
        }
        
        id = id.split('_')[1];
        const option = document.getElementById(id);

        $('#select-group-member-dropdown').multiselect('deselect', option.value);
    }
}

function set_group_icon(el) {
    state.new_group.icon = el.files[0];

    const reader = new FileReader();

    reader.onload = event => {
        const data = event.target.result;

        state.new_group.base_64 = data.split(",")[1];

        const json_string = JSON.stringify({
            filename: state.new_group.icon.name,
            base64_file: state.new_group.base_64,
            filedata: data,
        })
        const params = get_params(json_string);

        let config = {
              headers: {
                'X-CSRFToken': getCsrfToken(),
              }
            }

        axios
            .post('/livechat/check-image-file/', params, config)
            .then(response => {
                response = custom_decrypt(response.data);
                response = JSON.parse(response)
                
                if (response.status == '200') {
                    let image_el = `<img id='new-group-icon' src=${response.data} style='width: inherit; height: inherit; border-radius: 50%;'/>`
                    document.getElementById('group_image_icon').innerHTML = image_el;
                    document.getElementById('create_group_error_text').style.display = 'none'; 
                } else {
                    document.getElementById('create_group_error_text').innerHTML = response.message;
                    document.getElementById('create_group_error_text').style.display = 'block'; 
                }
            })
    }

    reader.readAsDataURL(state.new_group.icon);
}

function update_group_chat_list ({is_member_removed, is_member_added, user_group_id}) {
    axios
        .post("/livechat/update-group-chat-list/")
        .then((response) => {
            if (response.status == 200) {
                response = custom_decrypt(response.data);
                response = JSON.parse(response);

                set_sender_websocket_token(response["sender_websocket_token"]);

                // User Group Update
                const input_el = document.getElementById('livechat-groupchat-agent-search');

                if (input_el && input_el.value == '') {
                    set_user_group_list(response.user_group_list)
                    append_message_in_user_group_icon(response.user_group_list);    
                }
                
                // Group update
                set_group_list(response.group_chat_list)
                set_unread_message_count(response.user_group_list, response.group_chat_list);
                check_and_update_notification(response.user_group_list, response.group_chat_list, response.user_group_list);
                append_message_in_group_chat_icon(response.group_chat_list);
                
                highlight_chat_based_chat_type();

                if (get_is_group_chat() && state.active_group.id) {
                    update_group_display_info(state.active_group.id);
                }
                if (get_is_group_chat() && is_member_removed) {
                    go_to_group(state.active_group.id);
                }
                if (is_member_added) {
                    if (user_group_id) {
                        go_to_user_group(user_group_id);
                    } else {
                        go_to_user_group(get_active_user_group().id);
                    }
                }
            } else {
                showToast(response.message, 2000);
            }
        })
        .catch((err) => {
            console.log(err);
            console.log("Unable to update group chat list. Please try again later.");
        });
}

function set_group_list(group_list) {

    state.total_group_list = group_list;
    let html = ""
    for(const group of group_list) {
        let group_icon = group.icon_path;

        html += `<div class="live-chat-group-active-customer-item livechat-active-group" id="${group.id}">
                    <div class="live-chat-group-active-groupname">${stripHTML(group.name)}</div>
                    <div class="live-chat-active-group-details-wrapper">
                        <div class="live-chat-active-group-icon-div">`;
        
        if (group_icon != '') {
            html += `<img src="/${group_icon}" />`;
        } else {
            // html += state.default_icon;
            html += `<div class="live-chat-client-image">${stripHTML(group.name[0].toUpperCase())}</div>`
        }

        html += `</div><div class="live-chat-active-group-inside-details-wrapper">
                    <div class="live-chat-active-group-personname-date-wrapper">
                        <div class="live-chat-active-group-personname-text-div">
                            <div class="live-chat-group-personname-div" id="livechat-message-sender-name-${group.id}">Timothy Gunther</div>
                        </div>
                        <div class="live-chat-active-group-date-time-div" id="livechat-last-message-time_${group.id}">${group.last_message.time}</div>
                    </div>
                    <div class="live-chat-active-group-last-message-notif-wrapper">
                        <div class="live-chat-active-group-last-message-text-div" id="livechat-last-message-${group.id}">
                            I’m looking to work with a designer that Individuals and interaction hello
                        </div>
                        <div class="live-chat-active-group-message-notification-div" style="display: none;" id="livechat-unread-message-count-${group.id}"></div>
                        <div class="livechat-customer-typing-sidebar" id="customer-typing-${group.id}">Typing...</div>
                    </div>
                </div>
            </div>
        </div>`

        state.group_list[group.id] = group;
    }

    if (html == '') {
        html += `<div class="groupchat-search-no-result-div" id="group-search-no-result-div" style="display: block;">
                    No group found
                </div>`

    } else {
        html += `<div class="groupchat-search-no-result-div" id="group-search-no-result-div">
                    No group found
                </div>`
    }

    $('#livechat_group_list').html(html);
    add_group_click_event();
}

function add_group_click_event() {
    const elems = document.getElementsByClassName("livechat-active-group");

    if (is_mobile()) {
        Array.from(elems).forEach((elem) => {
            $(elem).on("touchend", () => {
                go_to_group(elem.id);
            });
        });
    } else {
        Array.from(elems).forEach((elem) => {
            $(elem).on("click", () => {
                go_to_group(elem.id);
            });
        });
    }
}

function add_remove_member_from_group_events() {
    const elems = document.getElementsByClassName("livechat-customer-group-member-remove-button");

    if (is_mobile()) {
        Array.from(elems).forEach((elem) => {
            $(elem).on("touchend", () => {
                show_remove_member_confirmation_modal(elem.id);
            });
        });
    } else {
        Array.from(elems).forEach((elem) => {
            $(elem).on("click", () => {
                show_remove_member_confirmation_modal(elem.id);
            });
        });
    }
}

function enable_edit_group_description (el) {
    document.getElementById('livechat-group-details-description').disabled = false;
    document.getElementById('livechat-group-details-description').focus();

    el.style.display = 'none';
    document.getElementById('livechat_save_group_description').style.display = 'block';

    $("#livechat-group-details-description").css('border', `1px solid ${get_theme_color().three}`);
    $("#livechat-group-details-description").css("padding", "4px 8px");
}


function enable_edit_group_name (el) {
    document.getElementById('livechat-group-details-group-name').disabled = false;
    document.getElementById('livechat-group-details-group-name').focus();

    el.style.display = 'none';
    document.getElementById('livechat_save_group_name').style.display = 'block';
    document.getElementById('livechat-group-details-created-data').style.display = 'none';

    $("#livechat-group-details-group-name").css('border', `1px solid ${get_theme_color().three}`);
    $("#livechat-group-details-group-name").css("padding", "3px 2px");
}

export function enable_edit_group_details(event) {
    state.events.group_edited = true;
    $(event.target).addClass("livechat-customer-detail-edit-disabled-btn");
    $(".livechat-customer-personal-details-wrapper").addClass("livechat-customer-detail-edit-active");

    $(".livechat-customer-personal-details input").attr('readonly', false);
    $(".livechat-customer-personal-details textarea").attr('readonly', false);


    var value = $("#customer-name-input").val();
    $("#customer-name-input").focus().val('').val(value);
}

export function disable_edit_group_details() {
    state.events.group_edited = false;
    $("#livechat_customer_details_edit_btn").removeClass("livechat-customer-detail-edit-disabled-btn");
    $(".livechat-customer-personal-details-wrapper").removeClass("livechat-customer-detail-edit-active");

    $(".livechat-customer-personal-details input").attr('readonly', true);
    $(".livechat-customer-personal-details textarea").attr('readonly', true);

    const active_group = get_active_group();

    document.getElementById('livechat-group-details-group-name-edit').value = active_group.name;
    document.getElementById('livechat-group-details-description').value = active_group.desc;
}

function get_new_group_desc (el) {
    const desc_elem = document.getElementById('livechat-group-details-description');

    let new_group_desc = desc_elem.value.trim();
    new_group_desc = stripHTMLtags(new_group_desc);

    if (new_group_desc == '' || new_group_desc == state.active_group.desc) {
        return;
    }

    const char_limit = get_character_limit();
    if (new_group_desc.length > char_limit.large) {
        showToast(`Exceeding character limit of ${char_limit.large} characters in group description.`, 2000);
        return;
    }

    return new_group_desc;
}

function get_new_group_name () {
    const name_elem = document.getElementById('livechat-group-details-group-name-edit');

    let new_group_name = name_elem.value.trim();
    new_group_name = stripHTMLtags(new_group_name);

    if (new_group_name == '' || new_group_name == state.active_group.name) {
        return;
    }

    const char_limit = get_character_limit();
    if (new_group_name.length > char_limit.small) {
        showToast(`Exceeding character limit of ${char_limit.small} characters in group name.`, 2000);
        return;
    }

    return new_group_name;
}

export function update_group_details () {
    let json_string = {
        group_id: state.active_group.id,
    };
    let messages = [];

    const new_group_name = get_new_group_name();
    if (new_group_name) {
        json_string['name'] = new_group_name;
        messages.push('changed the group name');
    }

    const new_group_desc = get_new_group_desc();
    if (new_group_desc) {
        json_string['desc'] = new_group_desc;
        messages.push('changed the group description');
    }

    if (messages.length == 0) {
        disable_edit_group_details();
        return;
    }
    
    json_string = JSON.stringify(json_string);
    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/edit-group-details/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data)
            response = JSON.parse(response)
            if (response.status == 200) {
                
                messages.forEach(message => {
                    let temp_message = JSON.stringify({
                        text_message: message,
                        type: "text",
                        path: "",
                        thumbnail: "",
                        receiver_token: state.active_group.id,
                        receiver_username: "group",
                        sender_websocket_token: state.active_group.id,
                        sender_name: 'System',
                        sender_username: get_sender_username(),
                        is_group: true,
                    });
                
                    send_message_to_internal_chat_socket(temp_message, "System", true);    
                })

                let group_header = document.getElementById('livechat_group_name_header');
                if (new_group_name && group_header) {
                  group_header.innerHTML = stripHTML(new_group_name);
                }
                update_group_chat_list({
                    is_member_removed: false,
                    is_member_added: false,
                    user_group_id: null,
                });
            } else {
                showToast(response.message, 2000);
            }

            disable_edit_group_details();
        })
        .catch((err) => {
            console.log(err);
            console.log("Unable to update details. Please try again later.");
            disable_edit_group_details();
        });
}

function show_add_members_div (el) {
    state.all_agents = window.AGENTS;
    state.active_group.added_agents = [];
    state.events.adding_member = true;
    update_available_agents();
    $('#add_group_members').toggle();
    document.getElementById('livechat-group-tentative-added-members').style.display = 'none';
    document.getElementById('livechat-group-tentative-added-members').innerHTML = `<div class="livechat-customer-group-search-added-heading">Added</div>`;
    
    const elem = document.getElementById('group_members_search_div');
    elem.style.display = elem.style.display == 'flex' ? 'none' : 'flex';

    const add_member_btn = document.getElementById('add_new_members_btn');
    add_member_btn.style.display = add_member_btn.style.display == 'block' ? 'none' : 'block';

    const show_members_btn = document.getElementById('add_group_members_btn');
    show_members_btn.style.display = show_members_btn.style.display == 'block' ? 'none' : 'block';
}

function get_search_agents_html(agents) {
    const theme_color = get_theme_color();
    let html = ''
    for (const agent of agents) {
        if (!state.active_group.member_name.includes(agent) && !state.active_group.added_agents.includes(agent)) {
            html += `<div class="livechat-customer-group-member-items-div">
                        <div class="livechat-customer-group-member-icon-div">
                            ${get_user_initial(agent)}
                        </div>
                        <div class="livechat-customer-group-member-name-div">${agent}</div>
                        <button class="livechat-customer-group-search-added-btn" id="add_member-${agent}">
                            <svg width="38" height="38" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <rect width="44" height="44" rx="13" fill="${theme_color.one}"/>
                                <path d="M22 14C21.4477 14 21 14.4477 21 15V21H15C14.4477 21 14 21.4477 14 22C14 22.5523 14.4477 23 15 23H21V29C21 29.5523 21.4477 30 22 30C22.5523 30 23 29.5523 23 29V23H29C29.5523 23 30 22.5523 30 22C30 21.4477 29.5523 21 29 21H23V15C23 14.4477 22.5523 14 22 14Z" fill="white"/>
                            </svg>        
                        </button>
                    </div>`
        }
    }

    return html;
}

function update_available_agents(agents) {
    if (!agents) agents = [];

    const search_term = document.getElementById('search_available_agents').value.trim();

    if (search_term != '') {
        agents = search_available_agents(search_term);
    }

    const html = get_search_agents_html(agents);

    $('#all_agents_search_div').html(html);

    if (html == '') {
        $('.livechat-customer-group-search-result-list-div').hide();
    } else {
        $('.livechat-customer-group-search-result-list-div').show();
    }

    add_member_click_events();
}

function search_available_agents(searchTerm) {
    searchTerm = searchTerm.toLowerCase();
    const optionsList = document.querySelectorAll(".option");
    let flag = false;
    // document.querySelector(".no-elem").style.display = "none";
    const matching_agents = []

    if (!state.all_agents) state.all_agents = window.AGENTS;

    state.all_agents.forEach(agent_name => {
        if (agent_name.toLowerCase().indexOf(searchTerm.toLowerCase()) != -1) {
            flag = true;
            matching_agents.push(agent_name);
        }
    })

    // if (flag === 0)
    //     document.querySelector(".no-elem").style.display = "block";

    return matching_agents;
}

function add_member_click_events() {
    const elems = document.getElementsByClassName("livechat-customer-group-search-added-btn");

    if (is_mobile()) {
        Array.from(elems).forEach((elem) => {
            $(elem).on("touchend", () => {
                add_member_to_group(elem.id);
            });
        });
    } else {
        Array.from(elems).forEach((elem) => {
            $(elem).on("click", () => {
                add_member_to_group(elem.id);
            });
        });
    }   
}

function add_member_to_group (id) {
    const active_group = get_active_group();

    if ((active_group.member_name.length + active_group.added_agents.length) >= GROUP_SIZE_LIMIT) {
        showToast(`Exceeding group size limit of ${GROUP_SIZE_LIMIT} members.`, 2000);
        return;
    }

    const agent_name = id.split('-')[1];
    const theme_color = get_theme_color();

    document.getElementById('livechat-group-tentative-added-members').innerHTML += `<div class="livechat-customer-group-member-items-div">
                                                <div class="livechat-customer-group-member-icon-div">
                                                ${get_user_initial(agent_name)}
                                                </div>
                                                <div class="livechat-customer-group-member-name-div">${agent_name}</div>
                                                <button class="livechat-customer-group-search-added-success-btn livechat-remove-added-member-btn" id="tentative_user-${agent_name}">
                                                    <svg width="38" height="38" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
                                                        <path d="M30.25 16.7505L19.75 27.25L14.5 22.0005" stroke="${theme_color.one}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                                        <rect x="0.5" y="0.5" width="43" height="43" rx="12.5" stroke="black"/>
                                                        <rect x="0.5" y="0.5" width="43" height="43" rx="12.5" stroke="${theme_color.two}"/>
                                                    </svg>
                                                </button>
                                            </div>`
    
    document.getElementById('livechat-group-tentative-added-members').style.display = 'block';

    document.getElementById(id).parentElement.remove();
    state.active_group.added_agents.push(agent_name);
    update_available_agents();
    add_remove_member_click_event();
}

function add_remove_member_click_event() {
    const elems = document.getElementsByClassName("livechat-remove-added-member-btn");

    if (is_mobile()) {
        Array.from(elems).forEach((elem) => {
            $(elem).on("touchend", () => {
                remove_member_from_added_list(elem.id);
            });
        });
    } else {
        Array.from(elems).forEach((elem) => {
            $(elem).on("click", () => {
                remove_member_from_added_list(elem.id);
            });
        });
    }   
}

function remove_member_from_added_list (id) {
    const agent_name = id.split('-')[1];
    
    state.active_group.added_agents = state.active_group.added_agents.filter((value, index, arr) => {
        return value != agent_name;
    })

    document.getElementById(id).parentElement.remove();

    if (state.active_group.added_agents.length == 0) {
        $('#livechat-group-tentative-added-members').hide();
    }

    update_available_agents();
}

function update_group_members (el) {
    state.events.adding_member = false;
    if (state.active_group.added_agents.length == 0) {
        document.getElementById('add_group_members').style.display = 'none';
        document.getElementById('add_group_members_btn').style.display = 'block';
        document.getElementById('add_new_members_btn').style.display = 'none';
        document.getElementById('group_members_search_div').style.display = 'none';
        return;
    }

    const json_string = JSON.stringify({
        group_id: state.active_group.id,
        added_members: state.active_group.added_agents
    })

    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/edit-group-details/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data)
            response = JSON.parse(response)
            if (response.status == 200) {
                const message = `added ${state.active_group.added_agents[state.active_group.added_agents.length-1]} to the chat`;

                var temp_message = JSON.stringify({
                        text_message: message,
                        type: "text",
                        path: "",
                        thumbnail: "",
                        receiver_token: state.active_group.id,
                        receiver_username: "group",
                        sender_websocket_token: state.active_group.id,
                        sender_name: 'System',
                        sender_username: get_sender_username(),
                        added_members: state.active_group.added_agents,
                        is_group: true,
                    });
            
                send_message_to_internal_chat_socket(temp_message, "System", true);
            
                update_group_chat_list({
                    is_member_removed: false,
                    is_member_added: false,
                    user_group_id: null,
                });
            } else {
                showToast(response.message, 2000);
            }
        })
        .catch((err) => {
            console.log(err);
            console.log("Unable to update details. Please try again later.");
        });
}

function show_remove_member_confirmation_modal(id) {
    const member_name = id.split('-')[1];

    state.events.removing_member = true;
    state.active_group.remove_member = member_name;

    const value = [member_name, state.active_group.name];
    let itr = 0;

    let text = state.remove_member_display_text;
    text.match(/\{(.*?)\}/g).forEach(function(element) {
        text = text.replace(element, `<b>${value[itr]}</b>`);
        ++itr;
    })

    document.getElementById('remove_member_modal_display_text').innerHTML = text;
    
    $('#livechat-remove-group-member-modal').modal('show')
}

function remove_member_from_group(el) {
    const remove_member = state.active_group.remove_member;

    if (!remove_member) {
        return;
    }

    const json_string = JSON.stringify({
        group_id: state.active_group.id,
        remove_member: remove_member
    })

    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/edit-group-details/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data)
            response = JSON.parse(response)
            if (response.status == 200) {
                state.events.removing_member = false;
                const message = `removed ${remove_member} from the chat`;

                var temp_message = JSON.stringify({
                    text_message: message,
                    type: "text",
                    path: "",
                    thumbnail: "",
                    receiver_token: state.active_group.id,
                    receiver_username: "group",
                    sender_websocket_token: state.active_group.id,
                    sender_name: 'System',
                    sender_username: get_sender_username(),
                    removed_user: remove_member,
                    is_group: true,
                });
            
                send_message_to_internal_chat_socket(temp_message, "System", true);
            
                $('#livechat-remove-group-member-modal').modal('hide')
            } else {
                showToast(response.message, 2000);
            }
        })
        .catch((err) => {
            console.log("Unable to update details. Please try again later.");
        });
}

function delete_group() {
    const json_string = JSON.stringify({
        group_id: state.active_group.id,
        delete_group: true,
    })

    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/edit-group-details/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data)
            response = JSON.parse(response)
            if (response.status == 200) {
                var temp_message = JSON.stringify({
                        text_message: `group deleted`,
                        type: "text",
                        path: "",
                        thumbnail: "",
                        receiver_token: state.active_group.id,
                        receiver_username: "group",
                        sender_websocket_token: state.active_group.id,
                        sender_name: 'System',
                        sender_username: get_sender_username(),
                        deleted_group: true,
                        is_group: true,
                    });
            
                send_message_to_internal_chat_socket(temp_message, "System", true);

                const text_message = `This group is deleted`;

                const message = JSON.stringify({
                    message: JSON.stringify({
                        text_message: text_message,
                        type: "text",
                        path: "",
                        thumbnail: "",
                        receiver_token: state.active_group.id,
                        receiver_username: "group",
                        sender_websocket_token: state.active_group.id,
                        sender_name: 'System',
                        sender_username: get_sender_username(),
                        left_chat: true,
                        is_group: true,
                    }),
                    sender: "GroupUser",
                });
            
                send_message_to_guest_agent_socket(message);
            
                $('#livechat-delete-group-modal').modal('hide')
            } else {
                showToast(response.message, 2000);
            }
        })
        .catch((err) => {
            console.log("Unable to update details. Please try again later.");
        });
}

function remove_group() {
    const json_string = JSON.stringify({
        group_id: state.active_group.id,
        delete_group: true,
    })

    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/edit-group-details/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data)
            response = JSON.parse(response)
            if (response.status == 200) {
                $('#livechat-delete-group-modal').modal('hide');
                go_to_group(state.active_group.id, true);
                unset_active_group();
                update_group_chat_list({
                    is_member_removed: false,
                    is_member_added: false,
                    user_group_id: null,
                });
            } else {
                showToast(response.message, 2000);
            }
        })
        .catch((err) => {
            console.log(err);
            console.log("Unable to update details. Please try again later.");
        });
}

function disable_group_editing() {
    try {
        document.getElementById('remove_group_btn_2').style.display = 'block';
    } catch (err) {
        console.log(err);
    }
}

function enable_group_editing() {
    try {
        document.getElementById('remove_group_btn_2').style.display = 'none';
    } catch (err) {
        console.log(err);
    }
}

function unset_active_group () {
    state.active_group = {
        id: null,
        name: null,
        desc: null,
        members: [],
        member_name: [],
        added_agents: [],
        remove_member: null,
        is_deleted: false,
        admin: null,
    }
}

function reset_create_group_modal() {
    document.getElementById('livechat-new-group-name').value = '';
    document.getElementById('livechat-new-group-desc').value = '';

    $('#select-group-member-dropdown').multiselect('clearSelection');

    document.getElementById('livechat_added_members_list').innerHTML = '';
    document.getElementById('upload_group_image').value = '';
    document.getElementById('group_image_icon').innerHTML = state.default_icon;
    document.getElementById('create_group_error_text').style.display = 'none';         

    state.new_group.icon = null;
    state.new_group.base_64 = null;
    state.new_group.member_count = 0;
}

export function leave_group() {
    const json_string = JSON.stringify({})
    const params = get_params(json_string);

    let config = {
        headers: {
          'X-CSRFToken': getCsrfToken(),
        }
    }

    axios
        .post(`/livechat/leave-group/${get_active_group().id}`, params, config)
        .then((response) => {
            response = custom_decrypt(response.data)
            response = JSON.parse(response)
            if (response.status == 200) {
                const text_message = `${get_sender_username()} has left the chat`;

                const message = JSON.stringify({
                    message: JSON.stringify({
                        text_message: text_message,
                        type: "text",
                        path: "",
                        thumbnail: "",
                        receiver_token: state.active_group.id,
                        receiver_username: "group",
                        sender_websocket_token: state.active_group.id,
                        sender_name: 'System',
                        sender_username: get_sender_username(),
                        left_chat: true,
                        is_group: true,
                    }),
                    sender: "GroupUser",
                });
            
                send_message_to_guest_agent_socket(message);
            
                $('#livechat-leave-group-modal').modal('hide');
                go_to_group(state.active_group.id, true);
                unset_active_group();
                update_group_chat_list({
                    is_member_removed: false,
                    is_member_added: false,
                    user_group_id: null,
                });
            } else {
                showToast(response.message, 2000);
            }
        })
        .catch((err) => {
            console.log(err);
            console.log("Unable to update details. Please try again later.");
        });
}

export function cancel_remove_member_from_group() {
    state.events.removing_member = false;
}

function get_group_list() {
    return state.group_list;
}

function get_total_group_list() {
    return state.total_group_list;
}

function get_active_group() {
    return state.active_group;
}

function set_active_group(active_group) {
    state.active_group = active_group;
}

function set_all_agents(agents) {
    state.all_agents = agents;
}

function get_all_agents(agents) {
    return state.all_agents;
}

function get_default_icon() {
    return state.default_icon;
}

export function get_group_events() {
    return state.events;
}

export function set_is_adding_member(value) {
    state.events.adding_member = value;
}

export function reset_member_count() {
    state.new_group.member_count = 0;
}

export {
    create_chat_group,
    open_agent_dropdown_list,
    select_member,
    remove_selected_member,
    filterList,
    set_group_icon,
    update_group_chat_list,
    enable_edit_group_description,
    enable_edit_group_name,
    show_add_members_div,
    update_group_members,
    remove_member_from_group,
    add_remove_member_from_group_events,
    update_available_agents,
    get_group_list,
    get_active_group,
    set_active_group,
    delete_group,
    set_all_agents,
    get_all_agents,
    search_available_agents,
    disable_group_editing,
    enable_group_editing,
    remove_group,
    get_default_icon,
    get_total_group_list,
}