import axios from "axios";

import {
    custom_decrypt,
    get_params,
    showToast,
    stripHTML,
    strip_unwanted_characters,
    EncryptVariable,
    encrypt_variable,
    getCsrfToken,
    is_mobile,
} from "../../utils";

import {
    get_theme_color,
} from "../../agent/console";

import {
    get_message_history,
    get_chat_html,
    append_supervisor_file_archive,
    append_supervisor_message_archive,
    add_chat_scroll_event,
} from "../../common/archive_customer";

const state = {
    page: 1,
    initial_refresh: true,
    refresh_interval: 0,
    checked_users: [],
    is_global_user_checkbox_enabled: false,
    unblock_btn_type: "global",
    current_selected_user: "",
    total_users: 0,
};

$(window).ready(function () {

    if (!window.location.pathname.includes('blocked-users')) {
        return;
    }

    state.refresh_interval = parseInt(REFRESH_INTERVAL);

    setInterval(() => {
        initialize_blocked_users_table(state.page);
    }, state.refresh_interval * 1000);

    state.initial_refresh = false;

    $("#chat-escalation-unblock-user-btn").on("click", function (e) {
        show_user_unblock_confirmation_modal(e.target);
    });

    $("#chat-escalation-unblock-btn").on("click", function (e) {
        chat_escalation_unblock_user();
    });

});

export async function initialize_blocked_users_table(page) {
    if (state.initial_refresh) {
        toggle_loader("show");
    }

    state.page = page;

    const response = await get_blocked_users(page); 
    toggle_loader("hide");
    state.total_users = response.blocked_users.length;

    if (response.blocked_users.length > 0) {
        const table_html = get_table_html(response);

        document.getElementById("livechat_blocked_users_no_data").style.display = "none";

        $("#livechat_blocked_users_table_div").html(table_html);
        $("#livechat_blocked_users_table_div").css("display", "block");

        initialize_datatable(response.start_point, response.total_users);
        apply_pagination(response.pagination_data);

        apply_event_listeners_on_users();

    } else {
        document.getElementById(
            "livechat_blocked_users_table_div"
        ).style.display = "none";
        document.getElementById("livechat_blocked_users_no_data").style.display =
            "block";
    }
    enable_disable_unblock_btn();
}

function toggle_loader(value) {
    value = value == "show" ? "block" : "none";

    document.getElementById("livechat_blocked_users_loader").style.display = value;
}

function get_blocked_users(page) {
    return new Promise((resolve, reject) => {
        let json_string = {
            page: page,
        };

        json_string = JSON.stringify(json_string);
        const params = get_params(json_string);

        let config = {
              headers: {
                'X-CSRFToken': getCsrfToken(),
              }
            }

        axios
            .post("/livechat/get-livechat-blocked-users/", params, config)
            .then((response) => {
                response = custom_decrypt(response.data);
                response = JSON.parse(response);
                
                resolve(response);
            })
            .catch((err) => {
                console.log(err);
            });  
    });

}

function get_table_html(response) {
    let table_html = `<table role="table" id="blocked-users-table" class="display">`;

    table_html += get_table_header();
    table_html += get_table_body(response.blocked_users);
    table_html += `</table>`;
    return table_html;
}

function get_table_header() {

    let user_checkbox_header = '<input type="checkbox" class="blacklisted-all-checkbox" id="blocked-user-checkbox-header">';
    if(state.is_global_user_checkbox_enabled) {
        user_checkbox_header = '<input type="checkbox" class="blacklisted-all-checkbox" id="blocked-user-checkbox-header" checked>';
    }

    return `
        <thead role="rowgroup">
            <tr role="row">
                <th role="columnheader">
                    <label class="cam custom-checkbox-input">
                        ${user_checkbox_header}
                        <span class="checkmark"></span>
                    </label>
                </th>
                <th role="columnheader">Name and Info </th>
                <th role="columnheader">Agent </th>
                <th role="columnheader">IP Address / User ID </th>
                <th role="columnheader">Source </th>    
                <th role="columnheader">Time left untill unblocked </th>
                <th role="columnheader">Chat History </th>
                <th role="columnheader">Action </th>

            </tr>
        </thead>`;
}

function get_table_body(blocked_users) {
    let body_html = ``;
    blocked_users.forEach((blocked_user) => {
        body_html += `<tr role="row">`;

        if(state.checked_users.includes(blocked_user.pk)) {
            body_html += get_col(`<label class="cam custom-checkbox-input"><input type="checkbox" class="blacklisted-report-checkbox blocked-user-checkbox" id="${blocked_user.pk}" checked><span class="checkmark"></span></label>`);
        } else {
            body_html += get_col(`<label class="cam custom-checkbox-input"><input type="checkbox" class="blacklisted-report-checkbox blocked-user-checkbox" id="${blocked_user.pk}"><span class="checkmark"></span></label>`);
        }
        body_html += get_col(` Name: ${blocked_user.username} <br> Mobile No. ${blocked_user.phone} <br> Email address: ${blocked_user.email}`);
        body_html += get_col(blocked_user.agent);
        if(blocked_user.channel == "Web") {
            body_html += get_col(blocked_user.ip_address); 
        } else {
            body_html += get_col(blocked_user.client_id);
        }
        body_html += get_col(blocked_user.channel);
        body_html += get_col(blocked_user.time_diff);
        body_html += get_col(`<button class="blacklist_chathistory_btn" id="blocked-user-transcript-btn_${blocked_user.pk}">Chat History</button>`);
        body_html += get_col(`<button class="livechat-blacklist-report-table-unblock-btn user-unblock-btn" id="user-unblock-btn_${blocked_user.pk}">Unblock</button>`);

        body_html += "</tr>";
    });

    return body_html;
}

function get_col(value) {
    return `
            <td role="cell">${value}</td>`;
}

function initialize_datatable(start_point, total_users) {
    $("#blocked-users-table").DataTable({
        language: {
            info: `Showing _START_ to _END_ entries out of ${total_users}`,
            infoEmpty: "No records available",
            infoFiltered: "(filtered from _MAX_ total records)",
        },
        bPaginate: false,
        ordering: false,
        infoCallback: function (settings, start, end, max, total, pre) {
            if (settings.oPreviousSearch["sSearch"] != "") {
                return pre;
            }
            end = start_point - 1 + end;
            start = start_point - 1 + start;
            return `Showing ${start} to ${end} entries out of ${total_users}`;
        },
    });

    const table = $("#blocked-users-table").DataTable();

    const value = document.getElementById("blacklisted-keyword-table-search").value;
    
    if (value != "") {
        table.search(value).draw();
    }

    $("#blacklisted-keyword-table-search").keyup(function () {
        let value = this.value;
        table.search(value).draw();
    });

}

function apply_pagination(pagination) {
    let html = `<div class="container-fluid">`;

    if (pagination.has_other_pages) {
        html += `<div class="pagination-div">
                    <ul class="pagination-content">`;

        for (let page = 1; page < pagination.page_range; ++page) {
            if (pagination.number == page) {
                if (page == 1) {
                    html += `<li class="active-page"><a data-page="${page}" class="blocked-users-pagination" style="color: #0254d7;" href="javascript:void(0)">${page}</a></li>`;
                } else if (pagination.num_pages == page) {
                    html += `<li class="active-page" style="border-radius: 0 6px 6px 0;"><a data-page="${page}" class="blocked-users-pagination" style="color: #0254d7;" href="javascript:void(0)">${page}</a></li>`;
                } else {
                    html += `<li class="active-page" style="border-radius: 0px;"><a data-page="${page}" class="blocked-users-pagination" style="color: #0254d7;" href="javascript:void(0)">${page}</a></li>`;
                }
            } else if (
                page > pagination.number - 5 &&
                page < pagination.number + 5
            ) {
                html += `<li><a class="blocked-users-pagination" href="javascript:void(0)" data-page="${page}">${page}</a></li>`;
            }
        }
    }

    $("#blocked-users-table_wrapper").append(html);

    add_pagination_events();
}

function add_pagination_events() {
    $(".blocked-users-pagination").on("click", (event) => {
        initialize_blocked_users_table(event.target.dataset.page);
    });
}

function apply_event_listeners_on_users() {

    $(".blacklist_chathistory_btn").on("click", function (e) {
        load_reported_user_transcripts(e.target);
    });

    $('.blocked-user-checkbox').on("click", function (e) {
        let checked_users = document.querySelectorAll('.blocked-user-checkbox:checked');

        if(checked_users.length) {
            $("#chat-escalation-unblock-user-btn").removeClass('disable-btn');
        } else {
            $("#chat-escalation-unblock-user-btn").addClass('disable-btn');
        }

        state.checked_users = [];
        for(let i = 0; i < checked_users.length; i++) {
            state.checked_users.push(checked_users[i].id);
        }

        if(checked_users.length == state.total_users) {
            $("#blocked-user-checkbox-header").prop('checked', true);
            state.is_global_user_checkbox_enabled = true;
        } else {
            $("#blocked-user-checkbox-header").prop('checked', false);
            state.is_global_user_checkbox_enabled = false;
        }

    });

    $("#blocked-user-checkbox-header").on("click", function (e) {

        if(e.target.checked) {

            $(".blocked-user-checkbox").prop('checked', true);
            let checked_users = document.querySelectorAll('.blocked-user-checkbox:checked');
            state.is_global_user_checkbox_enabled = true;

            state.checked_users = [];
            for(let i = 0; i < checked_users.length; i++) {
                state.checked_users.push(checked_users[i].id);
            }

        } else {
            $(".blocked-user-checkbox").prop('checked', false);
            state.is_global_user_checkbox_enabled = false;
            state.checked_users = [];
        }
        enable_disable_unblock_btn();

    });

    $(".user-unblock-btn").on("click", function (e) {
        show_user_unblock_confirmation_modal(e.target);
    });
}

function enable_disable_unblock_btn() {
    if(state.checked_users.length) {
        $("#chat-escalation-unblock-user-btn").removeClass('disable-btn');
    } else {
        $("#chat-escalation-unblock-user-btn").addClass('disable-btn');
    }
}

async function load_reported_user_transcripts(element) {

    let id = element.id.split("_")[1];
    document.getElementById("chat_history_download_btn").dataset.id = id;
    
    $("#chat-transcript-agent-modal").modal("show");

    const response = await get_message_history(id);
    var html = get_chat_html(response, id, true);

    $("#livechat-chat-messages").html('')
    $("#livechat-chat-messages").append(html);

    $('#style-2-'+ id).animate({ scrollTop: 9999999 }, 200);
    $("#livechat-modal-chats-customer-name-div").html(response["customer_name"])
    document.getElementById("chat_history_download_btn").style.opacity = "1"
    document.getElementById("chat_history_download_btn").style.pointerEvents = "auto"

    append_supervisor_messages(response);

    setTimeout(
        function(){ add_chat_scroll_event(
        response.client_id,
        id,
        response.joined_date,
        response.active_url
    ) }
     , 300)
}

function append_supervisor_messages(response) {

    for (var item = 0; item < response.message_history.length; item++) {
        let message = response.message_history[item];
        if (message.sender == "Supervisor") {
            if(message.attached_file_src != ''){
                append_supervisor_file_archive(message.attached_file_src, "", "", message.message, message.reply_message_id, message.time);
            } else if(message.message != '') {
                append_supervisor_message_archive(message.message, "", message.sender, message.reply_message_id, message.time);
            }

        }
    }
}

export function show_user_unblock_confirmation_modal(el) {
    if(el.id == "chat-escalation-unblock-user-btn") {
        state.unblock_btn_type = "global";
    } else {
        if(!el.id.split("_")[1]) return;
        state.unblock_btn_type = "local";
        state.current_selected_user = el.id.split("_")[1];
    }

    $("#livechat-user-unblock-modal").modal("show");
}

function chat_escalation_unblock_user() {

    if(!state.unblock_btn_type) return;

    let selected_users = [];

    if (state.unblock_btn_type == "global") {
        selected_users = state.checked_users;
    } else if (state.unblock_btn_type == "local") {
        selected_users = [state.current_selected_user];
    }

    if(selected_users.length == 0) return;

    let json_string = {
        selected_users: selected_users,
    };

    json_string = JSON.stringify(json_string);
    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/chat-escalation-mark-complete/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if(response.status == 200) {

                $("#livechat-user-unblock-modal").modal("hide");
                showToast("User/s has been successfully unblocked.", 2000);

                state.checked_users = [];
                state.is_global_user_checkbox_enabled = false;
                initialize_blocked_users_table(state.page);
            } else {
                $("#livechat-user-unblock-modal").modal("hide");
                showToast(response.message, 2000);
            }
        })        
        .catch((err) => {
            console.log(err);
        });
}