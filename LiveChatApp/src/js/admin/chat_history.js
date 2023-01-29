import axios from "axios";

import {
    append_file_to_agent_attach,
    get_system_text_response_html,
    get_video_call_text_response,
    on_chat_history_div_scroll,
    prepend_agent_message,
    prepend_customer_message,
    return_time,
    get_customer_warning_system_text_html,
    get_report_message_notif_html, 
} from "../agent/chatbox";

import { is_url } from "../agent/chatbox_input";

import { create_socket_ongoing_chat, close_realtime_chat_socket } from "../agent/livechat_chat_socket";

import { 
    show_tagging_details,
    append_supervisor_message_realtime,
    append_supervisor_file_realtime,
 } from "../common/archive_customer";

import {
    change_date_format_original,
    custom_decrypt,
    get_params,
    is_valid_date,
    showToast,
    stripHTML,
    strip_unwanted_characters,
    EncryptVariable,
    encrypt_variable,
    is_file_supported,
    check_file_size,
    check_malicious_file,
    is_docs,
    is_image,
    is_pdf,
    is_txt,
    is_video,
    is_excel,
    getCsrfToken,
    stripHTMLtags,
    remove_special_characters_from_str,
} from "../utils";

import {
    send_message_to_socket,
} from "../agent/livechat_chat_socket";

import {
    send_message_to_guest_agent_socket,
} from "../agent/livechat_agent_socket";

import { auto_resize, append_file_to_modal } from "../agent/chatbox_input";

import {
    send_message_to_internal_chat_socket,
    create_websocket,
    close_chat_socket,
    create_one_to_one_chat_socket,
    close_internal_chat_socket,
} from "../common/livechat_internal_chat_socket";

import {
    cancel_reply_on_message_function
} from "./realtime_chat_view";

import { get_theme_color } from "../agent/console";

const state = {
    filter: {
        is_applied: false,
        agent_username: null,
        chat_status: null,
        channel_name: null,
        selected_category_pk: null,
        chat_termination: null,
        start_date: null,
        end_date: null,
    },
    page: 1,
    refresh_interval: 0,
    supervisor_name: window.SUPERVISOR_NAME,
    attachment: {
        data: "",
        form_data: "",
        file_src: '',
        file_name: '',
        channel_file_url: '',
    },
    session_id: '',
    receiver_username: '',
    sender_username: '',
    receiver_websocket_token: '',
    sender_websocket_token: '',
    mic: {
        instance: null,
        recognizing: false,
        prev_text: "",
        start: new Date().getTime(),
        end: new Date().getTime(),
        ignore_onend: false,
    },
    trailing_list: [],
    current_history_id: '',
};

$(window).ready(function () {
    if (!window.location.pathname.includes('chat-history')) {
        return;
    }

    state.refresh_interval = parseInt(REFRESH_INTERVAL);

    setInterval(() => {
        initialize_chat_history_table(state.page, true);
    }, state.refresh_interval * 1000);

    $("#apply_audit_trail_filter_btn").on("click", function (e) {
        apply_audit_trail_filter();
    });

    $("#refresh_chat_history_btn").on("click", () => {
        initialize_chat_history_table(state.page);
    });

    $("#reset_audit_trail_filter").on("click", () => {
        reset_audit_trail_filter();
    });

    initilialize_multiselect_filter_options();

});

function initilialize_multiselect_filter_options() {

    $("#select-agent-username").multiselect({
        nonSelectedText: 'Select agent',
        enableFiltering: true,
        includeSelectAllOption: true,
        enableCaseInsensitiveFiltering: true
    });

    $(".livechat-multiselect-dropdown.livechat-multiselect-filter-dropdown .multiselect-container>li>a>label").addClass("custom-checkbox-input");
    $(".livechat-multiselect-dropdown.livechat-multiselect-filter-dropdown .multiselect-container>li").find(".custom-checkbox-input").append("<span class='checkmark'></span>");
}

export async function initialize_chat_history_table(
    page,
    auto_refresh = false
) {
    if (!auto_refresh) {
        toggle_loader("show");
        $("#livechat_audit_trail_no_data").css("display", "none");
        $("#livechat_audit_trail_table_div").css("display", "none");
    }

    state.page = page;

    const response = await get_chat_history(page);
    
    toggle_loader("hide");

    if (response.total_audits > 0) {
        const table_html = get_table_html(response);

        document.getElementById("livechat_audit_trail_no_data").style.display =
            "none";

        $("#livechat_audit_trail_table_div").html(table_html);
        $("#livechat_audit_trail_table_div").css("display", "block");

        initialize_datatable(response.start_point, response.total_audits);
        apply_pagination(response.pagination_data);

        add_taggings_events();

        $('.live-chat-history-prev-btn').unbind('click').click(function () {});
        $('.live-chat-history-next-btn').unbind('click').click(function () {});
        // $(document).unbind('keydown')

        add_chat_history_events();
        add_nps_events();

        update_chat_history_modal(response.audit_obj_list);
    } else {
        document.getElementById(
            "livechat_audit_trail_table_div"
        ).style.display = "none";
        document.getElementById("livechat_audit_trail_no_data").style.display =
            "block";
    }
}

function toggle_loader(value) {
    value = value == "show" ? "block" : "none";

    document.getElementById("livechat_audit_trail_loader").style.display =
        value;
}

export function get_chat_history(page) {
    return new Promise((resolve, reject) => {
        let json_string = {
            page: page,
            current_history_id: state.current_history_id,
            archive_customer: "false",
            start_date: URL_FILTER_START_DATE,
            end_date: URL_FILTER_END_DATE,
        };

        if (state.filter.is_applied) {
            const filter = state.filter;

            json_string = {
                ...json_string,
                agent_username: filter.agent_username,
                channel_name: filter.channel_name,
                chat_status: filter.chat_status,
                selected_category_pk: filter.selected_category_pk,
                chat_termination: filter.chat_termination,
                start_date: filter.start_date,
                end_date: filter.end_date,
            };
        }

        json_string = JSON.stringify(json_string);
        const params = get_params(json_string);

        let config = {
              headers: {
                'X-CSRFToken': getCsrfToken(),
              }
            }

        axios
            .post("/livechat/get-livechat-history/", params, config)
            .then((response) => {
                response = custom_decrypt(response.data);
                response = JSON.parse(response);

                resolve(response);
            });
    });
}

function get_table_html(response) {
    let table_html = `<table role="table" id="audit-trail-table" class="display">`;
    state.trailing_list = response.trailing_list
    table_html += get_table_header();
    table_html += get_table_body(response.audit_obj_list);
    table_html += `</table>`;
    return table_html;
}

function get_table_header() {
    return `
            <thead role="rowgroup">
                <tr role="row">
                    <th role="columnheader">Customer Name</th>
                    <th role="columnheader">Agent Username</th>
                    <th role="columnheader">Channel</th>
                    <th role="columnheader">Source</th>
                    <th role="columnheader">Chat Category</th>
                    <th role="columnheader">NPS</th>
                    <th role="columnheader">Taggings</th>
                    <th role="columnheader">Start Date-Time</th>
                    <th role="columnheader">End Date-Time</th>
                    <th role="columnheader">Duration</th>
                    <th role="columnheader">Wait Time</th>
                    <th role="columnheader">First Time Response</th>
                    <th role="columnheader">Chat Termination</th>
                    <th role="columnheader"> </th>
                </tr>
            </thead>`;
}

function get_table_body(audit_list) {
    let body_html = ``;
    audit_list.forEach((audit) => {
        body_html += `<tr role="row">`;

        body_html += get_col(audit.username);
        body_html += get_col(audit.agent_username);
        if(!audit.is_followup_lead) {
            body_html += get_col(audit.channel);
        } else {
            body_html += get_col(audit.channel + '/' + audit.previous_channel + ' (Follow Up)');
        }

        if(audit.source) {
            body_html += get_col(audit.source);
        } else {
            body_html += get_col("Others");
        }
        
        body_html += get_col(audit.closing_category);

        if (audit.rate_value == "-1") {
            body_html += get_col(
                `<button class="livechat-nps-details" style="visibility: unset !important; cursor: default;">  NA </button>`
            );
        } else {
            body_html += get_col(
                `<button id="nps-details-btn_${audit.pk}" data-value="${audit.rate_value}" data-text="${audit.rate_text}" class="livechat-nps-details livechat-nps-details-btn" style="visibility: unset !important;">${audit.rate_value}</button>`
            );
        }

        if (audit.form_filled == "[]") {
            body_html += get_col(
                `<button class="livechat-nps-details" style="opacity: 0.5; visibility: unset !important; cursor: default;">  View </button>`
            );
        } else {
            body_html += get_col(
                `<button data-id="${audit.pk}" class="livechat-nps-details audit_trail_taggings_btn" style="visibility: unset !important;">View</button>`
            );
        }

        body_html += get_col(audit.joined_date);
        if (audit.is_session_exp) {
            body_html += get_col(audit.last_appearance_date);
        } else {
            body_html += get_col("-");
        }
        body_html += get_col(audit.chat_duration);
        body_html += get_col(audit.wait_time);
        body_html += get_col(audit.first_time_response);
        body_html += get_col(audit.chat_ended_by);

        if (audit.is_session_exp) {
            body_html += get_col(
                `<button class="chat_history_btn" id="chat-details-btn_${audit.pk}">Chat History</button>`
            );
        } else {
            body_html +=
                get_col(`<button class="livechat-ongoing-chat-notif" style="color: #38B224 !important; border: none !important;">
                            <svg width="11" height="11" viewBox="0 0 11 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <circle cx="5.5" cy="5.5" r="5.5" fill="#38B224"/>
                            </svg>
                            Ongoing chat
                        </button>
                        <button class="realtime-chat-btn chat_history_btn" id="chat-details-btn_${audit.pk}" 
                             style="background-color: #38b224 !important; border: none !important;color: #FFFFFF !important;">View live chat</button>`);
        }

        body_html += "</tr>";
    });

    return body_html;
}

function get_col(value) {
    return `
            <td role="cell">${value}</td>`;
}

function add_taggings_events() {
    $(".audit_trail_taggings_btn").on("click", (event) => {
        show_tagging_details(event.target.dataset.id);
    });
}

function start_loader() {
    document.getElementById("chat_history_download_btn").style.opacity = "0.7"
    document.getElementById("chat_history_download_btn").style.pointerEvents = "none"

    $("#livechat-modal-chats-customer-name-div").html('Loading...')

    $("#livechat-chat-messages").html('<div id = "botloader" style="display: flex; height: 400px; background-color: white; align-items: center;justify-content: center;">\
        <img class="livechat-chat-history-chat-switch-loader" alt="loader">\
        </div>')

    $('.livechat-chat-history-chat-switch-loader').attr('src', '/static/LiveChatApp/img/waiting1.gif')
}

function add_chat_history_events() {
    $(".chat_history_btn").on("click", (event) => {
       
        start_loader()
        var id = event.target.id.split("_")[1];
        state.current_history_id = id;
        var current_session = id
        set_session_id(event.target.id);
        load_chat_history_modal(event.target.id);
        initialize_chat_history_table(state.page, true);
        var trailing_list = state.trailing_list

        if(trailing_list.length == 1){

            document.getElementById("previous_chat_history_btn").style.opacity = "0.7"
            $("#previous_chat_history_btn").attr("data-original-title", "");

             document.getElementById("next_chat_history_btn").style.opacity = "0.7"
            $("#next_chat_history_btn").attr("data-original-title", "");


        } else if(trailing_list.indexOf(""+current_session) == 0) {
            document.getElementById("previous_chat_history_btn").style.opacity = "0.7"
            $("#previous_chat_history_btn").attr("data-original-title", "");

            document.getElementById("next_chat_history_btn").style.opacity = "1.0"
            $("#next_chat_history_btn").attr("data-original-title", "Next Chat");

        } else if (trailing_list.indexOf(""+current_session) == trailing_list.length - 1)
        {
            document.getElementById("next_chat_history_btn").style.opacity = "0.7"
            $("#next_chat_history_btn").attr("data-original-title", "");

            document.getElementById("previous_chat_history_btn").style.opacity = "1.0"
            $("#previous_chat_history_btn").attr("data-original-title", "Previous Chat");
        } else {
            document.getElementById("next_chat_history_btn").style.opacity = "1.0"
            $("#next_chat_history_btn").attr("data-original-title", "Next Chat");

            document.getElementById("previous_chat_history_btn").style.opacity = "1.0"
            $("#previous_chat_history_btn").attr("data-original-title", "Previous Chat");
        }
        
    });

$(".live-chat-history-prev-btn").on("click", (event) => {

    previous_chat_functionality()
        
    });

$(".live-chat-history-next-btn").on("click", (event) => {

    next_chat_functionality()
    
});

$(document).on("keydown", (e) => {

    const chat_history_modal = document.getElementById("livechat-chat-details");

    if (chat_history_modal.style.display == "block") {

        if (e.which == 37) { 
           previous_chat_functionality()
           return false;
        }
        if (e.which == 39) { 
           next_chat_functionality()
           return false;
        }
    }
});

}

function add_nps_events() {
    $(".livechat-nps-details-btn").on("click", (event) => {
        load_nps_modal(event.target);
    });
}

function previous_chat_functionality() {
        var current_session = state.current_history_id;
        var trailing_list = state.trailing_list
        var current_session_index = trailing_list.indexOf(""+current_session)
        if(current_session_index > 0)
        {   
            $("[data-toggle='tooltip']").tooltip('hide');
            start_loader()
            current_session = trailing_list[current_session_index-1]
            state.current_history_id = current_session
            set_session_id("chat-details-btn_"+current_session);
            load_chat_history_modal("chat-details-btn_"+current_session);
            initialize_chat_history_table(state.page, true);

            if(trailing_list.indexOf(""+current_session) == 0) {
                document.getElementById("previous_chat_history_btn").style.opacity = "0.7"
                $("#previous_chat_history_btn").attr("data-original-title", "");
            } else {
                document.getElementById("previous_chat_history_btn").style.opacity = "1.0"
                $("#previous_chat_history_btn").attr("data-original-title", "Previous Chat");
            }

            document.getElementById("next_chat_history_btn").style.opacity = "1.0"
            $("#next_chat_history_btn").attr("data-original-title", "Next Chat");
        }
}

function next_chat_functionality() {
        var current_session = state.current_history_id;
        var trailing_list = state.trailing_list
        var current_session_index = trailing_list.indexOf(""+current_session)
        if(current_session_index < trailing_list.length - 1)
        {   
            $("[data-toggle='tooltip']").tooltip('hide');
            start_loader()
            current_session = trailing_list[current_session_index + 1]
            state.current_history_id = current_session

            set_session_id("chat-details-btn_"+current_session);
            load_chat_history_modal("chat-details-btn_"+current_session);
            initialize_chat_history_table(state.page, true);

            if(trailing_list.indexOf(""+current_session) == trailing_list.length - 1) {
                document.getElementById("next_chat_history_btn").style.opacity = "0.7"
                $("#next_chat_history_btn").attr("data-original-title", "");

            } else {
                document.getElementById("next_chat_history_btn").style.opacity = "1.0"
                $("#next_chat_history_btn").attr("data-original-title", "Next Chat");
            }

            document.getElementById("previous_chat_history_btn").style.opacity = "1.0"
            $("#previous_chat_history_btn").attr("data-original-title", "Previous Chat");
        }
}

function update_chat_history_modal(audit_list) {
    const chat_history_modal = document.getElementById("livechat-chat-details");

    if (chat_history_modal.style.display == "block") {
        let id = document.getElementsByClassName("live-chat-message-wrapper")[0]
            .dataset.id;

        let audit = audit_list.filter((value, index, arr) => {
            return value.pk == id;
        });

        if (audit.length > 0) {
            audit = audit[0];

            if (audit.is_session_exp) {
                const elem = document.getElementById(
                    "livechat-ongoing-chat-strip"
                );

                if (elem) {
                    elem.remove();
                }
                document.getElementById(
                    "chat_history_download_btn"
                ).style.display = "inline-block";
                // document.getElementById("chat_history_cross_btn").style.display = "none";
            }
        }
    }
}

function initialize_datatable(start_point, total_audits) {
    $("#audit-trail-table").DataTable({
        language: {
            info: `Showing _START_ to _END_ entries out of ${total_audits}`,
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
            return `Showing ${start} to ${end} entries out of ${total_audits}`;
        },
        scrollX: true,
    });

    const table = $("#audit-trail-table").DataTable();

    const value = document.getElementById("audit-trail-table-search").value;

    if (value != "") {
        table.search(value).draw();
    }

    $("#audit-trail-table-search").keyup(function () {
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
                    html += `<li class="active-page"><a data-page="${page}" class="audit-trail-pagination" style="color: #0254d7;" href="javascript:void(0)">${page}</a></li>`;
                } else if (pagination.num_pages == page) {
                    html += `<li class="active-page" style="border-radius: 0 6px 6px 0;"><a data-page="${page}" class="audit-trail-pagination" style="color: #0254d7;" href="javascript:void(0)">${page}</a></li>`;
                } else {
                    html += `<li class="active-page" style="border-radius: 0px;"><a data-page="${page}" class="audit-trail-pagination" style="color: #0254d7;" href="javascript:void(0)">${page}</a></li>`;
                }
            } else if (
                page > pagination.number - 5 &&
                page < pagination.number + 5
            ) {
                html += `<li><a class="audit-trail-pagination" href="javascript:void(0)" data-page="${page}">${page}</a></li>`;
            }
        }
    }

    $("#audit-trail-table_wrapper").append(html);

    add_pagination_events();
}

function add_pagination_events() {
    $(".audit-trail-pagination").on("click", (event) => {
        state.current_history_id = ''
        initialize_chat_history_table(event.target.dataset.page);
    });
}

export function apply_audit_trail_filter() {
    const agent_username = $("#select-agent-username").val();
    const chat_status = $("#select-chat-status").val();
    const channel_name = $("#select-channel").val();
    const selected_category_pk = $("#select-category").val();
    const chat_termination = $("#select-chat-termination").val();

    let start_date = document
        .getElementById("chat-history-default-start-date")
        .value.trim();

    let end_date = document
        .getElementById("chat-history-default-end-date")
        .value.trim();

    start_date = change_date_format_original(start_date);
    end_date = change_date_format_original(end_date);

    if (
        start_date == "" ||
        end_date == "" ||
        !is_valid_date(start_date) ||
        !is_valid_date(end_date)
    ) {
        showToast("Please enter valid dates", 4000);
        return;
    }

    const start_datetime = new Date(start_date);
    const end_datetime = new Date(end_date);
    if (start_datetime > end_datetime) {
        showToast("Start Date should be less than End Date", 4000);
        return;
    }

    state.filter.is_applied = true;
    state.filter.agent_username = agent_username;
    state.filter.chat_status = chat_status;
    state.filter.channel_name = channel_name;
    state.filter.selected_category_pk = selected_category_pk;
    state.filter.chat_termination = chat_termination;
    state.filter.start_date = start_date;
    state.filter.end_date = end_date;

    $("#apply-filter-audit-trail").modal("hide");
    initialize_chat_history_table(1);
}

function reset_audit_trail_filter() {
    // document.getElementById("select-agent-username").innerHTML = "";
    // document.getElementById("select-channel").selectedIndex = 0;
    // document.getElementById("select-category").selectedIndex = 0;
    // document.getElementById("select-chat-termination").selectedIndex = 0;

    $('#select-agent-username').multiselect('clearSelection');
    $('#select-agent-username').multiselect('rebuild');
    $('#select-chat-status').val("0").selectpicker('refresh');
    $('#select-channel').val("All").selectpicker('refresh');
    $('#select-category').val("0").selectpicker('refresh');
    $('#select-chat-termination').val("All").selectpicker('refresh');

    // const html =
    //     '<option value="0" selected>Choose one</option><option value="1">Online</option><option value="2">Offline</option>';

    // document.getElementById("select-chat-status").innerHTML = html;

    document.getElementById("chat-history-default-start-date").value =
        DEFAULT_LIVECHAT_FILTER_START_DATETIME;

    document.getElementById("chat-history-default-end-date").value =
        DEFAULT_LIVECHAT_FILTER_END_DATETIME;
}

function get_message_history(id) {
    return new Promise((resolve, reject) => {
        const json_string = JSON.stringify({
            session_id: id,
        });
        const params = get_params(json_string);

        let config = {
              headers: {
                'X-CSRFToken': getCsrfToken(),
              }
            }

        axios
            .post("/livechat/get-livechat-message-history/", params, config)
            .then((response) => {
                response = custom_decrypt(response.data);
                response = JSON.parse(response);

                // console.log(response);

                resolve(response);
            });
    });
}

async function load_chat_history_modal(id) {
    const elem = document.getElementById(id);
    id = id.split("_")[1];

    document.getElementById("chat_history_download_btn").dataset.id = id;
    // document.getElementById("livechat-chat-messages").innerHTML = "";

    $("#livechat-chat-details").modal("show");

    const response = await get_message_history(id);
    set_internal_chat_token_details(response, id);

    var html = get_chat_html(response, id);
    
    $("#livechat-chat-messages").html('')
    $("#livechat-chat-messages").append(html);
    
    $('#style-2-'+ id).animate({ scrollTop: 9999999 }, 200);

    $("#livechat-modal-chats-customer-name-div").html(response["customer_name"])
    
    document.getElementById("chat_history_download_btn").style.opacity = "1"
    document.getElementById("chat_history_download_btn").style.pointerEvents = "auto"

    // Appending supervisor/admin's reply messages
    if (response.is_session_exp) {
        for (var item = 0; item < response.message_history.length; item++) {
            let message = response.message_history[item];
            if (message.sender == "Supervisor") {
                if(message.attached_file_src != ''){
                    append_supervisor_file_realtime(message.attached_file_src, id, message.file, message.message,  message.reply_message_id, message.time);
                } else if(message.message != '') {
                    append_supervisor_message_realtime(message.message, id, message.sender_name, message.reply_message_id, message.time);
                }

            }
        }
    }


    if(elem)
    {
        if (elem.classList.contains("realtime-chat-btn")) {
        close_realtime_chat_socket();
        setTimeout(function(){ create_socket_ongoing_chat(id); }, 300);
        }
    }
    setTimeout(
        function(){ add_chat_scroll_event(
        response.client_id,
        id,
        response.joined_date,
        response.active_url
    ) }
     , 300)
    $("#livechat-history-message-box-container-div").append(get_reply_message_html());
    document.querySelector('#admin-query').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            send_supervisor_message();
        }
    });
    add_supervisor_mic_functionality();


}

function load_nps_modal(elem) {
    const nps_rate = elem.dataset.value;
    const nps_text = elem.dataset.text;

    document.getElementById(
        "livechat_nps_rating"
    ).innerHTML = `NPS Rating: ${nps_rate}`;
    document.getElementById(
        "livechat_nps_rating_text"
    ).innerHTML = `NPS Feedback: ${nps_text}`;

    $("#nps-details").modal("show");
}

function get_chat_html(response, pk) {
    let html = ``;

    if (!response.is_session_exp) {
        html += `<div id="livechat-ongoing-chat-strip">This is an ongoing chat</div>`;

        document.getElementById("chat_history_download_btn").style.display =
            "none";
        // document.getElementById("chat_history_cross_btn").style.display = "block";
    } else {
        document.getElementById("chat_history_download_btn").style.display =
            "inline-block";
        // document.getElementById("chat_history_cross_btn").style.display = "none";
        
    }

    html += `<div class="col-12 mb-2" id="livechat-history-message-box-container-div" style="margin-bottom: 0px !important;height: calc(100vh - 15rem) !important;">`;

    if (response.is_session_exp) {
        html += `<div class="live-chat-area-admin" id="live-chat-area-admin-section">`;
    } else {
        html += `<div class="live-chat-area-admin" id="live-chat-area-admin-section">`;
    }

    html += get_chat_loader(pk);
    html += `<div class="live-chat-day-date-indicator" id="live-chat-indicator-${pk}">Today</div>`;

    html += `<div class="live-chat-message-wrapper" id="style-2-${pk}" data-id="${pk}" style="height: inherit !important;">
                <input type="hidden"  value = "${pk}"/>
                <input type="hidden"  value = "0"/>
    `;

    if (response.is_session_exp) {
        html += get_messages_html(response);
    }

    return html;
}

export function get_reply_message_html() {
    const theme_color = get_theme_color();
    return `<div class="live-chat-admin-chat-history-modal-text-box-wrapper" id="live-chat-admin-chat-history-modal-reply-text-box">
                <div class="live-chat-message-reply-on-message-wrapper">
                    <div class="live-chat-message-reply-on-text-div">
                        Reply on
                    </div>
                    <div class="live-chat-message-reply-on-message-text-div" id="reply-message-value">
                    </div>
                    <button class="live-chat-message-reply-on-message-wrapper-delete-div" onclick="cancel_reply_on_message_function();">
                        <svg width="12" height="12" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M15.5378 0.720217C15.318 0.499833 15.0194 0.375981 14.7081 0.375981C14.3968 0.375981 14.0983 0.499833 13.8784 0.720217L8.12318 6.46364L2.36798 0.708448C2.1481 0.488064 1.84957 0.364212 1.53825 0.364212C1.22693 0.364212 0.928398 0.488064 0.70851 0.708448C0.249507 1.16745 0.249507 1.90892 0.70851 2.36792L6.46371 8.12312L0.70851 13.8783C0.249507 14.3373 0.249507 15.0788 0.70851 15.5378C1.16751 15.9968 1.90898 15.9968 2.36798 15.5378L8.12318 9.78259L13.8784 15.5378C14.3374 15.9968 15.0788 15.9968 15.5378 15.5378C15.9969 15.0788 15.9969 14.3373 15.5378 13.8783L9.78265 8.12312L15.5378 2.36792C15.9851 1.92069 15.9851 1.16745 15.5378 0.720217Z" fill="black" fill-opacity="0.54"/>
                            </svg>
                    </button>
                    </div>
                    <div class="live-chat-text-box-wrapper" id="livechat-text-box-div" style="display: inline-flex;visibility: visible;">
                        <div class="live-chat-text-box textarea-desktop" role="text-area">
                            <textarea class="live-chat-text-area" placeholder="Type here...
                              " autofocus="" id="admin-query" style="box-sizing: border-box; overflow-y: auto;"></textarea>
                        </div>
                        <div class="live-chat-text-box textarea-mobile" role="text-area">
                            <textarea class="live-chat-text-area" placeholder="Type a Message" autofocus="" id="query-mobile"></textarea>
                        </div>
                        <div class="live-chat-text-format-icons">

                            <div class="live-chat-text-format-icon-wrapper attachment tooltip-textarea" data-toggle="modal" data-target="#livechat-file-upload-modal" onclick="append_livechat_file_upload_modal()">
                                <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" id="custom-button-attach" class="live-chat-text-format-icon"> 
                              <path d="M9.80019 0C12.1197 0 14 1.8804 14 4.2C14 5.27611 13.5925 6.28904 12.8773 7.05847L12.7444 7.19489L6.63569 13.3037L6.5985 13.3383L6.5595 13.3698C6.09107 13.7731 5.49259 14 4.86049 14C3.42198 14 2.25584 12.8338 2.25584 11.3952C2.25584 10.7643 2.48194 10.1674 2.8827 9.7002L2.9865 9.58617L2.99706 9.57782L8.10054 4.46516C8.37365 4.19155 8.81685 4.19116 9.09044 4.46429C9.36403 4.73742 9.36442 5.18063 9.09131 5.45424L3.98783 10.5669L3.98017 10.5727C3.77277 10.7945 3.65577 11.0848 3.65577 11.3952C3.65577 12.0606 4.19515 12.6 4.86049 12.6C5.12575 12.6 5.3763 12.5146 5.58232 12.36L5.6678 12.2895L5.66834 12.2906L11.7597 6.19995L11.8707 6.08487C12.3363 5.57409 12.6001 4.90875 12.6001 4.2C12.6001 2.6536 11.3465 1.4 9.80019 1.4C9.05708 1.4 8.36203 1.69022 7.8437 2.19701L7.73538 2.30889L7.72244 2.31797L1.19503 8.84819C0.921738 9.12162 0.478543 9.12171 0.205127 8.84841C-0.0682891 8.5751 -0.0683882 8.13189 0.204905 7.85846L6.72088 1.33927L6.75351 1.30915C7.54021 0.480039 8.63244 0 9.80019 0Z" fill="#2F405B"></path>
                          </svg>
                                <span class="tooltiptext" style="background-color: `+ theme_color.one +`">Attach File</span>
                            </div>

                            <div class="live-chat-text-format-icon-wrapper mic tooltip-textarea" onclick="activate_supervisor_mic()">
                                <svg width="12" height="15" viewBox="0 0 12 15" fill="none" xmlns="http://www.w3.org/2000/svg" class="live-chat-text-format-icon">
                          <path id="btn-mic-up" d="M8.60545 7.01785V2.81596C8.60545 1.26337 7.35538 0 5.81889 0C5.7696 0.000296166 5.7205 0.00616947 5.67253 0.0175078C4.95348 0.0523697 4.27535 0.362311 3.77844 0.883203C3.28154 1.40409 3.00388 2.09607 3.00293 2.81596V7.01785C3.00293 8.56275 4.25929 9.81911 5.80419 9.81911C7.34908 9.81911 8.60545 8.56275 8.60545 7.01785ZM4.40356 7.01785V2.81596C4.40356 2.04352 5.03174 1.41534 5.80419 1.41534C5.84248 1.41535 5.88069 1.41183 5.91834 1.40483C6.63616 1.45735 7.20482 2.07013 7.20482 2.81596V7.01785C7.20482 7.7903 6.57664 8.41848 5.80419 8.41848C5.03174 8.41848 4.40356 7.7903 4.40356 7.01785Z" fill="#2F405B"></path>
                          <path id="btn-mic-down" d="M1.6018 7.01785H0.201172C0.201172 9.86953 2.34483 12.2254 5.10337 12.572V14.021H6.504V12.572C9.26254 12.2254 11.4062 9.87023 11.4062 7.01785H10.0056C10.0056 9.33519 8.12103 11.2197 5.80369 11.2197C3.48635 11.2197 1.6018 9.33519 1.6018 7.01785Z" fill="#2F405B"></path>
                        </svg>
                                <span class="tooltiptext" style="background-color: `+ theme_color.one +`">Microphone</span>
                            </div>
                            <div class="live-chat-text-format-icon-wrapper send tooltip-textarea" onclick="send_supervisor_message()" id="submit-response">
                                <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" class="live-chat-text-format-icon">
                          <path id="fill-submit-btn" d="M13.683 6.4793L0.864958 0.0616166C0.764494 0.011306 0.651648 -0.00885246 0.540008 0.00356875C0.428368 0.01599 0.322693 0.0604612 0.235708 0.131628C0.152638 0.201343 0.0906346 0.292879 0.0566685 0.395945C0.0227024 0.499011 0.0181203 0.609522 0.0434371 0.715053L1.58743 6.41512L8.17708 6.41512V7.58197L1.58743 7.58197L0.0201316 13.2645C-0.00362467 13.3527 -0.00639775 13.4451 0.0120354 13.5345C0.0304685 13.6239 0.0695937 13.7078 0.126265 13.7793C0.182935 13.8508 0.255571 13.908 0.33833 13.9462C0.42109 13.9845 0.511664 14.0028 0.602771 13.9997C0.693978 13.9991 0.783784 13.9771 0.864958 13.9355L13.683 7.51779C13.7785 7.46883 13.8586 7.39445 13.9145 7.30283C13.9704 7.21122 14 7.10592 14 6.99855C14 6.89117 13.9704 6.78587 13.9145 6.69426C13.8586 6.60264 13.7785 6.52826 13.683 6.4793Z" fill="rgb(81,255,71,0.8)" style="fill: rgba(81, 255, 71, 0.8);"></path>
                        </svg>
                                <span class="tooltiptext" style="background-color: `+ theme_color.one +`">Send</span>
                            </div>
                        </div>

                    </div>
                </div>`;
}

function get_chat_loader(pk) {
    return `
            <div class="loader-custom" id="chat_loader-${pk}" style="position: absolute; left: 50%; transform: translateX(-50%);">
                <div id="loader-inside-div">
                    <div>
                    </div>
                    <div>
                    </div>
                    <div>
                    </div>
                    <div>
                    </div>
                </div>
            </div>
    `;
}

function get_messages_html(response, pk) {
    let html = ``;
    let active_url_msg = true;
    response.message_history.forEach((message) => {
        if (message.sender == "Agent") {
            if (message.is_video_call_message) return;
            if (message.is_guest_agent_message) {
                if (message.attached_file_src) {
                    html += append_file_to_agent_attach(
                        message.attached_file_src,
                        message.message,
                        message.time,
                        message.sender_name,
                        message.sender,
                        pk,
                        false,
                        false,
                        true,
                        false,
                        false,
                        message.message_id,
                        true,
                    );
                } else {
                    html += prepend_customer_message(
                        message.message,
                        message.sender_name,
                        message.time,
                        pk,
                        false,
                        message.message_id
                    );
                }
            } else {
                if (message.attached_file_src) {
                    html += append_file_to_agent_attach(
                        message.attached_file_src,
                        message.message,
                        message.time,
                        message.sender_name,
                        message.sender,
                        pk,
                        false,
                        false,
                        true,
                        false,
                        false,
                        message.message_id,
                        true,
                    );
                } else {
                    html += prepend_agent_message(
                        message.message,
                        message.sender_name[0],
                        message.time,
                        pk,
                        message.message_id
                    );
                }
            }
        } else if (message.sender == "Customer") {
            if (message.attached_file_src) {
                html += append_file_to_agent_attach(
                    message.attached_file_src,
                    message.message,
                    message.time,
                    message.sender_name,
                    message.sender,
                    pk,
                    false,
                    false,
                    true,
                    false,
                    false,
                    message.message_id,
                    true,
                );
            } else {
                html += prepend_customer_message(
                    message.message,
                    message.sender_name,
                    message.time,
                    pk,
                    false,
                    message.message_id
                );
            }
        } else if (message.sender == "System") {
            if (active_url_msg == true){
                html += append_system_message(response.active_url);
                active_url_msg = false;
            }
            if (message.is_video_call_message || message.is_cobrowsing_message || message.is_voice_call_message) {
                    if (message.message_for == 'primary_agent') {
                        html += get_video_call_text_response(message.message);
                    }
            } else if(message.message.includes("Customer details updated") || message.message.includes("Reinitiating Request Sent")){
                html += `<div class="live-chat-customer-details-update-message-div">
                            ${message.message}
                        </div>`;
            } else if(message.is_customer_report_message_notification) {
                html += get_report_message_notif_html(message.message);
            } else if(!message.is_customer_warning_message){
                let text_message = message.message;
                // if(message.message == "Due to inactivity chat has ended") {
                //     text_message = "System auto resolved the chat"
                // }

                html += get_system_text_response_html(
                    text_message,
                    message.time
                );
            }
        } else if (message.sender == "Bot") {
            html += prepend_agent_message(
                message.message,
                message.sender_name[0],
                message.time,
                pk,
                message.message_id
            );
        }
    });

    return html;
}

function append_system_message(active_url) {
    return `
        <div class="easychat-system-message-div"><div class="easychat-system-message easychat-system-message-line" style="color:263238" >Request Raised from: ${active_url}</div></div>`;
}

function add_chat_scroll_event(client_id, pk, joined_date, active_url) {
    $("#style-2-"+pk).on("scroll", (event) => {
        on_chat_history_div_scroll(
            event.target,
            client_id,
            pk,
            joined_date,
            active_url
        );
    });
}

function scroll_chat_to_bottom(pk) {
    const elem = document.getElementById(`style-2-${pk}`);
    if (elem) {
        $(elem).scrollTop($(elem)[0].scrollHeight);
    }
}

export function get_refresh_interval() {
    return state.refresh_interval;
}

function get_session_id(){
    return state.session_id;
}

function set_session_id(id) {
    var session_id = id.split("_")[1];
    state.session_id = session_id;
}

export function send_supervisor_message() {
    const session_id = get_session_id();

    var message_id = "";

    var sentence = $("#admin-query").val();
    sentence = $($.parseHTML(sentence)).text();
    if (sentence.length == 0) {
        // error!
        $("#query").val("");
        return;
    }
    $("#admin_query").val("");

    if (!is_url(sentence)) {
        sentence = stripHTMLtags(sentence);
        if (!window.IS_SPECIAL_CHARACTER_ALLOWED_IN_CHAT) {
            sentence = remove_special_characters_from_str(sentence);
            if (sentence.trim() == "") {
                return;
            }
        }
    }

    document.getElementById("admin-query").value = "";
    var reply_message_id = document.getElementById("admin-query").getAttribute("reply_message");
    cancel_reply_on_message_function();

    var json_string = JSON.stringify({
        message: sentence,
        sender: "Supervisor",
        attached_file_src: "",
        thumbnail_url: "",
        session_id: session_id,
        sender_name: state.supervisor_name,
        reply_message_id: reply_message_id,
        sender_username: state.sender_username,
    });

    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/save-supervisor-chat/", false);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {
                console.log("chat sent by supervisor saved");
                message_id = response["message_id"];
            }
        }
    };
    xhttp.send(params);

    var is_ongoing_chat = document.getElementById("livechat-ongoing-chat-strip");
    var message = sentence;

    if(is_ongoing_chat){

        var sentence = JSON.stringify({
            message: JSON.stringify({
                text_message: sentence,
                type: "text",
                channel: "Web",
                path: "",
                sender_name: state.supervisor_name,
                session_id: session_id,
                reply_message_id: reply_message_id,
                sender_username: state.sender_username,
                message_id: message_id,
            }),
            sender: "Supervisor",
        });

        send_message_to_socket(sentence);

        send_message_to_guest_agent_socket(sentence);
    } else {
        append_supervisor_message_realtime(sentence, session_id, state.supervisor_name, reply_message_id);
    }

    send_supervisor_message_to_internal_chat(reply_message_id, message, session_id);
}

export function reset_file_upload_modal_chathistory() {
    document.getElementById("send_attachment_chathistory").classList.add("disabled");
    document.getElementById("send_attachment_chathistory").style.pointerEvents = "none";
    document.getElementById("live_chat_file_wrapper").innerHTML = "";
    state.attachment.file_src = "";
}

export function upload_file_attachment_chathistory(e) {
    state.attachment.form_data = new FormData();
    state.attachment.data = document.querySelector(
        "#livechat-chathistory-file-attachment-input"
    ).files[0];

    if (
        !is_file_supported(state.attachment.data.name) ||
        !check_malicious_file(state.attachment.data.name)
    ) {
        showToast("Invalid File Format!", 3000);
        document.querySelector("#livechat-chathistory-file-attachment-input").value = "";
        return;
    }

    if (!check_file_size(state.attachment.data.size)) {
        showToast("Please Enter a file of size less than 5MB!", 3000);
        document.querySelector("#livechat-chathistory-file-attachment-input").value = "";
        return;
    }

    append_file_to_modal(state.attachment.data.name);

    $("#file-upload-progress-bar").progressbar({
        max: 100,
        value: 100,
    });

    document.getElementById("file-upload-cancel-btn").addEventListener("click", function () {
        reset_file_upload_modal_chathistory();
    });

    document.getElementById("send_attachment_chathistory").classList.remove("disabled");
    document.getElementById("send_attachment_chathistory").style.pointerEvents = "auto";
    document.querySelector("#livechat-chathistory-file-attachment-input").value = "";
}

$(document).on("click", "#send_attachment_chathistory", function(){
    reset_file_upload_modal_chathistory();
    $("#livechat-file-upload-modal").modal("toggle");

    var upload_attachment_data = state.attachment.data;

    const special_char_regex = /[-'/`~!#*$@%+=,^&(){}[\]|;:<>"?\\]/g;
    let attachment_name = upload_attachment_data.name;
    
    if (window.IS_SPECIAL_CHARACTER_ALLOWED_IN_FILE_NAME) {
        attachment_name = attachment_name.replace(special_char_regex, '_');
    } else if (special_char_regex.test(attachment_name)) {
        showToast(`<p> File not supported due to presence of special characters in the name </p>`, 3000);
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
        upload_chathistory_file_attachment_to_server();
    };

    reader.onerror = function(error) {
        console.log('Error: ', error);
    };

});

function upload_chathistory_file_attachment_to_server() {
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
            
                state.attachment.file_src = response.src;
                state.attachment.file_name = response.name;

                if (is_image(state.attachment.file_src)) {
                    const reader = new FileReader();
                    reader.addEventListener(
                        "load",
                        function () {
                            state.attachment.form_data = "";
                            state.attachment.data = "";
                            send_supervisor_file(
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
                    send_supervisor_file(state.attachment.file_src, response.thumbnail_url);
                }
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

function send_supervisor_file(
    attached_file_src,
    thumbnail_url,
    img_file = ""
) {
    if (true || $("#chathistory-query-file").val().length < 3000) {
        var sentence = $("#chathistory-query-file").val();
        sentence = $($.parseHTML(sentence)).text().trim();
        var message_id = "";
        $("#chathistory-query-file").val("");

        if (!is_url(sentence)) {
            sentence = stripHTMLtags(sentence);
            if (!window.IS_SPECIAL_CHARACTER_ALLOWED_IN_CHAT) {
                sentence = remove_special_characters_from_str(sentence);
                if (sentence.trim() == "" && attached_file_src=="") {
                    return;
                }
            }
        }
        const session_id = get_session_id();

        var reply_message_id = document.getElementById("admin-query").getAttribute("reply_message");

        cancel_reply_on_message_function();

        var json_string = JSON.stringify({
            message: sentence,
            sender: "Supervisor",
            attached_file_src: attached_file_src,
            thumbnail_url: thumbnail_url,
            session_id: session_id,
            sender_name: state.supervisor_name,
            reply_message_id: reply_message_id,
            sender_username: state.sender_username,
            is_uploaded_file: true,
        });
        json_string = encrypt_variable(json_string);
        json_string = encodeURIComponent(json_string);

        var csrf_token = getCsrfToken();
        var xhttp = new XMLHttpRequest();
        var params = "json_string=" + json_string;
        xhttp.open("POST", "/livechat/save-supervisor-chat/", true);
        xhttp.setRequestHeader("X-CSRFToken", csrf_token);
        xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                let response = JSON.parse(this.responseText);
                response = custom_decrypt(response);
                response = JSON.parse(response);
                if (response["status_code"] == "200") {
                    message_id = response["message_id"];
                }
            }
        };
        xhttp.send(params);

        var is_ongoing_chat = document.getElementById("livechat-ongoing-chat-strip");

        if(is_ongoing_chat) {

            var file_path = JSON.stringify({
                message: JSON.stringify({
                    text_message: sentence,
                    type: "file",
                    channel: "Web",
                    path: attached_file_src,
                    thumbnail: thumbnail_url,
                    agent_name: state.supervisor_name,
                    session_id: session_id,
                    reply_message_id: reply_message_id,
                    sender_username: state.sender_username,
                    message_id: message_id,
                }),
                sender: "Supervisor",
            });

            send_message_to_socket(file_path);

            send_message_to_guest_agent_socket(file_path);

        } else {
            append_supervisor_file_realtime(attached_file_src, session_id, thumbnail_url, sentence, reply_message_id);
        }

        send_supervisor_attachment_to_internal_chat(reply_message_id, sentence, attached_file_src, thumbnail_url, session_id);
    }
}

function set_internal_chat_token_details(response, id) {
    state.receiver_username = response["receiver_username"];
    state.sender_username = response["sender_username"];
    state.receiver_websocket_token = response["receiver_websocket_token"];
    state.sender_websocket_token = response["sender_websocket_token"];
    close_chat_socket();
    create_websocket(state.receiver_websocket_token);  
}

function send_supervisor_message_to_internal_chat(reply_message_id, reply_message, session_id) {

    var message_details = get_actual_message_details(reply_message_id);

    var json_string = JSON.stringify({
        message: message_details[0],
        reply_message_text: reply_message,
        sender: "user",
        attached_file_src: message_details[1],
        thumbnail_url: message_details[2],
        receiver_username: state.receiver_username,
        is_replied_message: true,
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

    const receiver_websocket_token = state.receiver_websocket_token;
    const sender_websocket_token = state.sender_websocket_token;

    var sender_name = state.supervisor_name;
    if(!sender_name) {
        sender_name = state.sender_username;
    }
    var message_packet = JSON.stringify({
        text_message: message_details[0],
        type: "text",
        path: message_details[1],
        thumbnail: message_details[2],
        receiver_token: receiver_websocket_token,
        receiver_username: state.receiver_username,
        sender_websocket_token: sender_websocket_token,
        sender_name: sender_name,
        sender_username: state.sender_username,
        is_group: false,
        reply_message_text: reply_message,
        is_replied_message: true,
        time: return_time(),
        reply_file_path: "",
    });

    send_message_to_internal_chat_socket(message_packet, "User", false);
}

function send_supervisor_attachment_to_internal_chat(reply_message_id, sentence, attached_file_src, thumbnail_url, session_id) {
    var message_details = get_actual_message_details(reply_message_id);

        var json_string = JSON.stringify({
            message: message_details[0],
            sender: "user",
            attached_file_src:  message_details[1],
            thumbnail_url: message_details[2],
            receiver_username: state.receiver_username,
            is_replied_message: true,
            reply_message_text: sentence,
            reply_attached_file_src: attached_file_src,
            reply_thumbnail_file_src: thumbnail_url,
            is_uploaded_file: true,
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

        var sender_name = state.supervisor_name;
        if(!sender_name) {
            sender_name = state.sender_username;
        }
        const receiver_websocket_token = state.receiver_websocket_token;
        const sender_websocket_token = state.sender_websocket_token;
        let text_message = sentence;
        var message = JSON.stringify({
            text_message: message_details[0],
            type: "file",
            path: message_details[1],
            thumbnail: message_details[2],
            receiver_token: receiver_websocket_token,
            receiver_username: state.receiver_username,
            sender_websocket_token: sender_websocket_token,
            sender_name: sender_name,
            sender_username: state.sender_username,
            is_group: false,
            reply_message_text: sentence,
            is_replied_message: true,
            time: return_time(),
            reply_file_path: attached_file_src,
            reply_file_thumbnail: thumbnail_url,
            });

        send_message_to_internal_chat_socket(message, "User", false);

}

export function get_actual_message_details(message_id) {

    var text_message = "";
    var attachment_file_path = "";
    var thumbnail_file_path = "";
    var attachment_name = ""
    var json_string = JSON.stringify({
        message_id: message_id, 
    }); 
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/get-livechat-message-details/", false);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token); 
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response.status_code == "200") {
                text_message = response["text_message"];
                attachment_file_path = response["attachment_file_path"];
                thumbnail_file_path = response["thumbnail_file_path"];
                attachment_name = response["attachment_file_name"];
            }
        }
    };
    xhttp.send(params); 
    return [text_message, attachment_file_path, thumbnail_file_path, attachment_name];
}

/* Mic Functionality For Supervisor */

function add_supervisor_mic_functionality() {
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
            deactivate_supervisor_mic();
            alert(
                "You will not be able to use voicebot feature as you haven't allowed microphone access."
            );
        }
    };

    mic.instance.onend = function () {

        if (state.mic.prev_text == document.getElementById("admin-query").value) {
            state.mic.end = new Date().getTime();
        }
        if (state.mic.prev_text != document.getElementById("admin-query").value) {
            state.mic.end = new Date().getTime();
            state.mic.start = new Date().getTime();
            state.mic.prev_text = document.getElementById("admin-query").value;
        }

        if (state.mic.end - state.mic.start >= 5000) {
            state.mic.recognizing = false;
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

        if (event.results[0].isFinal) {
            text = " " + text;
            document.getElementById("admin-query").value += text;
            state.mic.ignore_onend = true;
        }
    };
}

export function activate_supervisor_mic() {
    const session_id = get_session_id();

    const mic = state.mic;
    if (mic.recognizing) {
        mic.recognizing = false;
        mic.instance.stop();
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
        deactivate_supervisor_mic();
    }
}

function deactivate_supervisor_mic () {
    const mic = state.mic;

    if (mic.recognizing) mic.recognizing = false;
    if (mic.instance) mic.instance.stop();

    document.getElementById("btn-mic-up").style.fill = "#2F405B";
    document.getElementById("btn-mic-down").style.fill = "#2F405B";
}

/* Mic Functionality End */