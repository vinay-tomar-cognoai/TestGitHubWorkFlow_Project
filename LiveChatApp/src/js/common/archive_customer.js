import axios from "axios";
import { get_icons, showToast } from "../agent/console";

import {
    is_docs,
    is_video,
    is_txt,
    is_pdf,
    is_image,
    is_excel,
    get_video_path_html,
    get_doc_path_html,
    is_mobile,
    is_valid_date,
    change_date_format_original,
    get_params,
    custom_decrypt,
    stripHTML,
    getCsrfToken,
} from "../utils";

import {
    get_image_path_html_attach,
    get_system_text_response_html,
    get_video_call_text_response,
    return_time,
    get_attachment_html,
    get_reply_private_html,
    livechat_linkify,
    on_chat_history_div_scroll,
    get_customer_warning_system_text_html,
    get_report_message_notif_html, 

} from "../agent/chatbox";

const state = {
    taggings: {},
    months: [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ],
    days: [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday"
    ],
    
    filter: {
        is_applied: false,
        agent_username: window.agent_username,
        start_date: null,
        end_date: null,
    },
    page: 1,
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

    if (!window.location.pathname.includes('get-archived-customer-chat')) {
        return;
    }

    var url = new URL(window.location);
    var page = url.searchParams.get("page");
    if(page != undefined && page != null)
    {
        state.page = page 
    }

    initialize_chat_history_table_archive(state.page, false);


});


export async function initialize_chat_history_table_archive(
    page,
    auto_refresh = false
) {

    if(!auto_refresh)
    {
        toggle_loader("show");
        $("#livechat_archive_customer_no_data").css("display", "none");
        $("#livechat_archive_customer_table_div").css("display", "none");

    }

    state.page = page;

    const response = await get_chat_history(page);
    
    toggle_loader("hide");

    if (response.total_audits > 0) {
        const table_html = get_table_html(response);

        document.getElementById("livechat_archive_customer_no_data").style.display =
            "none";

        $("#livechat_archive_customer_table_div").html(table_html);
        $("#livechat_archive_customer_table_div").css("display", "block");
    
        initialize_datatable(response.start_point, response.total_audits);
        apply_pagination(response.pagination_data);

        $('.live-chat-history-prev-btn').unbind('click').click(function () {});
        $('.live-chat-history-next-btn').unbind('click').click(function () {});
        $(document).unbind('keydown')

        add_chat_history_events();
        add_nps_events();

    } else {
        document.getElementById(
            "livechat_archive_customer_table_div"
        ).style.display = "none";
        document.getElementById("livechat_archive_customer_no_data").style.display =
            "block";
    }
}

function toggle_loader(value) {
    value = value == "show" ? "block" : "none";

    document.getElementById("livechat_archive_customer_loader").style.display =
        value;
}

export function get_chat_history(page) {
    return new Promise((resolve, reject) => {
        let json_string = {
            page: page,
            current_history_id: state.current_history_id,
            archive_customer: "true"
        };

        if (state.filter.is_applied) {
            const filter = state.filter;

            json_string = {
                ...json_string,
                agent_username: filter.agent_username,
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
    let table_html = `<table role="table" id="archive-customer-table" class="display">`;
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
                    <th role="columnheader">NPS</th>
                    <th role="columnheader">Date</th>
                    <th role="columnheader">Duration</th>
                    <th role="columnheader"> </th>
                </tr>
            </thead>`;
}

function get_table_body(audit_list) {
    let body_html = ``;
    audit_list.forEach((audit) => {
        body_html += `<tr role="row">`;

        body_html += get_col(audit.username);

        if (audit.rate_value == "-1") {
            body_html += get_col(
                `<button class="livechat-nps-btn" style="visibility: unset !important; cursor: default; width: 100px;float:left;">  NA </button>`
            );
        } else {
            body_html += get_col(
                `<button id="nps-details-btn_${audit.pk}" class="livechat-nps-btn livechat-nps-details-btn" data-text="${audit.rate_text}" data-value="${audit.rate_value}" data-target="#nps-details-${audit.pk }"  style="visibility: unset !important; width: 100px;float:left;">${audit.rate_value}</button>`
            );
        }

        body_html += get_col(audit.joined_date);
        body_html += get_col(audit.chat_duration);

        body_html += get_col(
            `<button style ="padding-left: 0px;padding-right: 0px;width: 100px;"class="chat_history_btn" id="chat-details-btn_${audit.pk}">                  
                Chat History</button>`
        );


        body_html += "</tr>";
    });

    return body_html;
}

function get_col(value) {
    return `
            <td role="cell">${value}</td>`;
}


function initialize_datatable(start_point, total_archive) {

    $("#archive-customer-table").DataTable({
        language: {
            info: `Showing _START_ to _END_ entries out of ${total_archive}`,
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
            return `Showing ${start} to ${end} entries out of ${total_archive}`;
        },
    });

    var table = $('#archive-customer-table').DataTable();
    const value = document.getElementById("archive-customer-table-search").value;

    if (value != "") {
        table.search(value).draw();
    }

    $("#archive-customer-table-search").keyup(function () {
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
                    html += `<li class="active-page"><a data-page="${page}" class="archive-chat-pagination" style="color: #0254d7;" href="javascript:void(0)">${page}</a></li>`;
                } else if (pagination.num_pages == page) {
                    html += `<li class="active-page" style="border-radius: 0 6px 6px 0;"><a data-page="${page}" class="archive-chat-pagination" style="color: #0254d7;" href="javascript:void(0)">${page}</a></li>`;
                } else {
                    html += `<li class="active-page" style="border-radius: 0px;"><a data-page="${page}" class="archive-chat-pagination" style="color: #0254d7;" href="javascript:void(0)">${page}</a></li>`;
                }
            } else if (
                page > pagination.number - 5 &&
                page < pagination.number + 5
            ) {
                html += `<li><a class="archive-chat-pagination" href="javascript:void(0)" data-page="${page}">${page}</a></li>`;
            }
        }
    }

    $("#archive-customer-table_wrapper").append(html);

    add_pagination_events();
}


function add_pagination_events() {
    $(".archive-chat-pagination").on("click", (event) => {
        state.current_history_id = ''
        initialize_chat_history_table_archive(event.target.dataset.page);
    });
}


function start_loader() {
    document.getElementById("chat_history_download_btn").style.opacity = "0.7"
    document.getElementById("chat_history_download_btn").style.pointerEvents = "none"

    $("#livechat-modal-chats-customer-name-div").html('Loading...')

    $("#livechat-chat-messages").html(`<div id = "botloader" style="display: flex; height: 400px; background-color: white; align-items: center;justify-content: center;">\
        <img class="livechat-chat-history-chat-switch-loader"  alt="loader">\
        </div>`)

    $('.livechat-chat-history-chat-switch-loader').attr('src', '/static/LiveChatApp/img/waiting1.gif')

}

function set_session_id(id) {
    var session_id = id.split("_")[1];
    state.session_id = session_id;
}

function add_chat_history_events() {
    $(".chat_history_btn").on("click", (event) => {
        start_loader()
        var id = event.target.id.split("_")[1];
        state.current_history_id = id;
        var current_session = id
        set_session_id(event.target.id);
        load_chat_history_modal(event.target.id);
        initialize_chat_history_table_archive(state.page, true);
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
            initialize_chat_history_table_archive(state.page, true);

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
            initialize_chat_history_table_archive(state.page, true);

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


export function get_message_history(id) {
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
    // set_internal_chat_token_details(response, id);

    var html = get_chat_html(response, id);
    
    $("#livechat-chat-messages").html('')
    $("#livechat-chat-messages").append(html);

    $("#livechat-modal-chats-customer-name-div").html(response["customer_name"])
    $('#style-2-'+ id).animate({ scrollTop: 99999999 }, 200);
    document.getElementById("chat_history_download_btn").style.opacity = "1"
    document.getElementById("chat_history_download_btn").style.pointerEvents = "auto"

    //append supervisor/admin msg
    append_supervisor_message(response)

    setTimeout(
        function(){ add_chat_scroll_event(
        response.client_id,
        id,
        response.joined_date,
        response.active_url
    ) }
     , 300)

}

function append_supervisor_message(response) {

    response.message_history.forEach((message) => {

    if (message.sender == "Supervisor") {
        if (message.attached_file_src) {
            append_supervisor_file_archive(message.attached_file_src, "", "", message.message, message.reply_message_id, message.time)
        } else {
            append_supervisor_message_archive(message.message, "", message.sender, message.reply_message_id, message.time);
        }
    }
  });
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


export function get_chat_html(response, pk, chat_escalation_req=false) {
    let html = ``;

    document.getElementById("chat_history_download_btn").style.display =
        "inline-block";
    // document.getElementById("chat_history_cross_btn").style.display = "none";

    html += `<div class="col-12 mb-2 livechat-archive-chat-history-chats-parent-div" id="livechat-history-message-box-container-div" style="margin-bottom: 0px !important;height: calc(100vh - 15rem) !important;">`;

    html += `<div class="live-chat-area-admin" id="live-chat-area-admin-section">`;

    html += get_chat_loader(pk);
    html += `<div class="live-chat-day-date-indicator" id="live-chat-indicator-${pk}">Today</div>`;

    html += `<div class="live-chat-message-wrapper-archived" id="style-2-${pk}" data-id="${pk}" style="height: inherit !important;">
                <input type="hidden"  value = "${pk}"/>
                <input type="hidden"  value = "0"/>
    `;

    if (response.is_session_exp || chat_escalation_req) {
        html += get_messages_html(response);
    }

    return html;
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


export function get_messages_html(response, pk) {
    let html = ``;
    let active_url_msg = true;
    response.message_history.forEach((message) => {
        if (message.sender == "Agent") {
            if (message.is_video_call_message) return;
            if (message.is_guest_agent_message) {
                if (message.attached_file_src) {

                    html += append_file_to_agent(message.attached_file_src, 
                        message.message, message.time, 
                        message.sender_name, message.sender,
                        pk, false, false, true, message.message_id, false, false)

                    if (message.message.trim() != "") {
                        html += append_customer_message(message.message, message.sender_name,
                            message.time, pk, message.message_id, false, false)
                    }
                } else {
                    html += append_customer_message(message.message,message.sender_name,
                        message.time,pk, message.message_id,false, false)
                }
            } else {
                if (message.attached_file_src) {
                    html += append_file_to_agent(message.attached_file_src, 
                        message.message, message.time, 
                        message.sender_name, message.sender,
                        pk, false, false, false, message.message_id, false, false)
                } else {
                    html += append_agent_message(message.message, message.sender_name[0], message.time, pk, false, false, message.message_id, false, false)
                }
            }
        } else if (message.sender == "Customer") {
            if (message.attached_file_src) {
                html += append_file_to_agent(message.attached_file_src, message.message, message.time, message.sender_name, message.sender, pk, false, false, false, message.message_id, false, false)
            } else {
                html += append_customer_message(message.message,message.sender_name,
                        message.time, pk, message.message_id,false, false)
               
            }
        } else if (message.sender == "System") {
            if (active_url_msg == true){
                html += `<div class="easychat-system-message-div"><div class="easychat-system-message easychat-system-message-line" style="color:263238" >Request Raised from: ${response.active_url}</div></div>`;
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

                //if(message.message == "Agent resolved the chat") return;

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
            html += append_agent_message(message.message, message.sender_name[0], message.time, pk, false, false, message.message_id, false, false)
        }
    });

    return html;
}


export function add_chat_scroll_event(client_id, pk, joined_date, active_url) {
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


function get_file_name(value) {
    if (value.length > 20) {
        file_ext = value.split(".").pop();
        value = value.slice(0, 13);
        return value + "..." + file_ext;
    } else {
        return value;
    }
}

function get_image_path_html(attached_file_src) {
    
    attached_file_src = attached_file_src.includes(window.location.origin) ? attached_file_src : window.location.origin + attached_file_src 
    var html =
        '<img onclick="preview_livechat_attachment_image(this.src)" src="' + attached_file_src +
        '" style="height: 129px;width: 100%;border-radius: 1em;object-fit: cover;cursor:pointer;">';

    return html;
}

function append_file_to_agent(
    attached_file_src,
    message,
    time = return_time(),
    sender_name,
    sender,
    pk,
    is_blue_tick = false,
    is_ongoing_chat = false,
    is_guest_agent_message = false,
    message_id="",
    reply_private_container=true,
    returnresponse=true

) { 
    message = stripHTML(message);
    var len = attached_file_src.split("/").length;
    let html = "";
    var sender_name_html = "";
    if (sender == "Customer" || (sender == "Agent" && is_guest_agent_message))
        sender_name_html =
            '<div class="live-chat-client-name-with-message">' +
            sender_name +
            "</div>";
    const icons = get_icons();

    var blue_ticks = "";

    if (is_ongoing_chat) {
        var blue_ticks =
            '<svg style="margin:-5px 5px 0px 5px;" width="14" height="10" viewBox="0 0 14 10" fill="none" xmlns="http://www.w3.org/2000/svg">\
                              <path class="doubletick_livechat_agent-' +
            pk +
            '" d="M3.45714 6.51434L1.07304 4.18025C0.827565 3.93994 0.429579 3.93994 0.184102 4.18025C-0.0613675 4.42056 -0.0613675 4.81022 0.184102 5.05053L3.01268 7.81976C3.25815 8.06007 3.65614 8.06007 3.90161 7.81976L10.8159 1.05053C11.0614 0.810204 11.0614 0.420567 10.8159 0.18024C10.5704 -0.0600801 10.1724 -0.0600801 9.92697 0.18024L3.45714 6.51434Z" fill="#4d4d4d"/>\
                              <path class="doubletick_livechat_agent-' +
            pk +
            '" d="M5.6412 8.51434L5.07684 7.99999C4.83137 7.75969 4.42956 8.27404 4.18409 8.51434C3.93862 8.75465 3.93864 8.62614 4.18411 8.86645L5.19673 9.81976C5.44221 10.0601 5.8402 10.0601 6.08567 9.81976L13 3.05053C13.2454 2.8102 13.2454 2.42057 13 2.18024C12.7545 1.93992 12.3565 1.93992 12.111 2.18024L5.6412 8.51434Z" fill="#4d4d4d"/>\
                              </svg>';

        if (is_blue_tick) {
            blue_ticks =
                '<svg style="margin:-5px 5px 0px 5px;" width="14" height="10" viewBox="0 0 14 10" fill="none" xmlns="http://www.w3.org/2000/svg">\
                              <path d="M3.45714 6.51434L1.07304 4.18025C0.827565 3.93994 0.429579 3.93994 0.184102 4.18025C-0.0613675 4.42056 -0.0613675 4.81022 0.184102 5.05053L3.01268 7.81976C3.25815 8.06007 3.65614 8.06007 3.90161 7.81976L10.8159 1.05053C11.0614 0.810204 11.0614 0.420567 10.8159 0.18024C10.5704 -0.0600801 10.1724 -0.0600801 9.92697 0.18024L3.45714 6.51434Z" fill="#0254D7"/>\
                              <path d="M5.6412 8.51434L5.07684 7.99999C4.83137 7.75969 4.42956 8.27404 4.18409 8.51434C3.93862 8.75465 3.93864 8.62614 4.18411 8.86645L5.19673 9.81976C5.44221 10.0601 5.8402 10.0601 6.08567 9.81976L13 3.05053C13.2454 2.8102 13.2454 2.42057 13 2.18024C12.7545 1.93992 12.3565 1.93992 12.111 2.18024L5.6412 8.51434Z" fill="#0254D7"/>\
                              </svg>';
        }
    }

    if (sender == "Customer" || (sender == "Agent" && is_guest_agent_message)) {
        var reply_private_container = get_reply_private_html(reply_private_container, "client");
        if (is_pdf(attached_file_src)) {
            html =
                '<div class="live-chat-client-message-wrapper" id='+ message_id +'>\
                      <div class="live-chat-client-image">' +
                get_user_initial(sender_name) +
                "</div>" +
                sender_name_html + reply_private_container[0] +
                
                '<div class="live-chat-client-message-bubble file-attachement-download" style="margin-left: 0px">\
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
                          </div></div>'
                        + reply_private_container[1] +
                      '<div class="live-chat-client-message-time">\
                          ' +
                time +
                '\
                      </div>'+ reply_private_container[2] +'</div>';
        } else if (is_txt(attached_file_src)) {
            html =
                '<div class="live-chat-agent-message-wrapper" id='+ message_id +'>\
                          <div class="live-chat-agent-image">' +
                get_user_initial(sender_name) +
                "</div>" +
                sender_name_html +
                reply_private_container[0] +
                '<div class="live-chat-agent-message-bubble file-attachement-download" style="margin-left: 0px">\
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
                              </div></div>'
                              + reply_private_container[1] +
                          '<div class="live-chat-agent-message-time">\
                              ' +
                time +
                "\
                          </div>" + reply_private_container[2] + "</div>";
        } else if (is_docs(attached_file_src)) {
            html =
                '<div class="live-chat-client-message-wrapper" id='+ message_id +'>\
                      <div class="live-chat-client-image">' +
                get_user_initial(sender_name) +
                "</div>" +
                sender_name_html +
                reply_private_container[0] +
                '<div class="live-chat-client-message-bubble file-attachement-download" style="margin-left: 0px">\
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
                      </div></div>'
                      + reply_private_container[1] +
                      '<div class="live-chat-client-message-time">\
                          ' +
                time +
                "\
                      </div>"+ reply_private_container[2] +"</div>";
        } else if (is_image(attached_file_src)) {
            html =
                '<div class="live-chat-client-message-wrapper" id='+ message_id +'>\
                    <div class="live-chat-client-image">' +
                get_user_initial(sender_name) +
                "</div>" +
                sender_name_html +
                reply_private_container[0] +
                '<div class="live-chat-client-message-bubble-image-attachment">\
                        ' +
                get_image_path_html(attached_file_src) +
                '\
                        <div class="file-attach-name-area">\
                            <h5 id="custom-text-attach-img">' +
                attached_file_src.split("/")[len - 1] +
                '</h5>\
                            <a href="' +
                attached_file_src +
                '" target="_blank" download><span style="position: absolute; top: 0.6rem; right: 8px;"><svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M11.875 11.25H3.125C2.77982 11.25 2.5 11.5298 2.5 11.875C2.5 12.2202 2.77982 12.5 3.125 12.5H11.875C12.2202 12.5 12.5 12.2202 12.5 11.875C12.5 11.5298 12.2202 11.25 11.875 11.25Z" fill="#757575"/>\
                                <path d="M2.5 10.625V11.875C2.5 12.2202 2.77982 12.5 3.125 12.5C3.47018 12.5 3.75 12.2202 3.75 11.875V10.625C3.75 10.2798 3.47018 10 3.125 10C2.77982 10 2.5 10.2798 2.5 10.625Z" fill="#757575"/>\
                                <path d="M11.25 10.625V11.875C11.25 12.2202 11.5298 12.5 11.875 12.5C12.2202 12.5 12.5 12.2202 12.5 11.875V10.625C12.5 10.2798 12.2202 10 11.875 10C11.5298 10 11.25 10.2798 11.25 10.625Z" fill="#757575"/>\
                                <path d="M7.50003 9.375C7.37046 9.37599 7.24378 9.33667 7.13753 9.2625L4.63753 7.5C4.50279 7.40442 4.41137 7.25937 4.38326 7.09658C4.35515 6.93379 4.39264 6.76649 4.48753 6.63125C4.5349 6.56366 4.59518 6.50611 4.66491 6.46194C4.73463 6.41777 4.81242 6.38785 4.89377 6.37391C4.97512 6.35996 5.05843 6.36227 5.13889 6.38069C5.21934 6.39911 5.29535 6.43329 5.36253 6.48125L7.50003 7.975L9.62503 6.375C9.75764 6.27555 9.92432 6.23284 10.0884 6.25628C10.2525 6.27973 10.4006 6.36739 10.5 6.5C10.5995 6.63261 10.6422 6.7993 10.6187 6.96339C10.5953 7.12749 10.5076 7.27555 10.375 7.375L7.87503 9.25C7.76685 9.33114 7.63526 9.375 7.50003 9.375Z" fill="#757575"/>\
                                <path d="M7.5 8.125C7.33424 8.125 7.17527 8.05915 7.05806 7.94194C6.94085 7.82473 6.875 7.66576 6.875 7.5V2.5C6.875 2.33424 6.94085 2.17527 7.05806 2.05806C7.17527 1.94085 7.33424 1.875 7.5 1.875C7.66576 1.875 7.82473 1.94085 7.94194 2.05806C8.05915 2.17527 8.125 2.33424 8.125 2.5V7.5C8.125 7.66576 8.05915 7.82473 7.94194 7.94194C7.82473 8.05915 7.66576 8.125 7.5 8.125Z" fill="#757575"/>\
                                </svg>\
                                </span></a></div></div>'
                               + reply_private_container[1] +
                        '<div class="live-chat-client-message-time">\
                            ' +
                time +
                "\
                            </div>"+ reply_private_container[2] +"</div>";
        }
    } else {
        var reply_private_container = get_reply_private_html(reply_private_container, "agent");
        if (is_pdf(attached_file_src)) {
            html =
                `<div class="live-chat-agent-message-wrapper" id=${message_id}>
      <div class="live-chat-agent-image">${get_user_initial(
          sender_name
      )}</div>` +
                sender_name_html +
                reply_private_container[0] +
                `<div class="live-chat-agent-message-bubble file-attachement-download">
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

            html +=
                `</div>`
                 + reply_private_container[1] +
                `<div class="live-chat-agent-message-time">
                ${time}` +
                blue_ticks +
                `</div>`+ reply_private_container[2] +`</div>`;
        } else if (is_txt(attached_file_src)) {
            html =
                `<div class="live-chat-agent-message-wrapper" id=${message_id}>
      <div class="live-chat-agent-image">${get_user_initial(
          sender_name
      )}</div>` +
                sender_name_html +
                reply_private_container[0] +
                `<div class="live-chat-agent-message-bubble file-attachement-download">
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

            html +=
                `</div>`
                 + reply_private_container[1] +
                `<div class="live-chat-agent-message-time">
                ${time}` +
                blue_ticks +
                `</div>`+ reply_private_container[2] +`</div>`;
        } else if (is_docs(attached_file_src)) {
            html =
                `<div class="live-chat-agent-message-wrapper" id=${message_id}>
      <div class="live-chat-agent-image">${get_user_initial(
          sender_name
      )}</div>` +
                sender_name_html +
                reply_private_container[0] +
                `<div class="live-chat-agent-message-bubble file-attachement-download">
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

            html +=
                `</div>`
                + reply_private_container[1] +
                `<div class="live-chat-agent-message-time">
                ${time}` +
                blue_ticks +
                `</div>`+ reply_private_container[2] +`</div>`;
        } else if (is_excel(attached_file_src)) {
            html =
                `<div class="live-chat-agent-message-wrapper" id=${message_id}>
      <div class="live-chat-agent-image">${get_user_initial(
          sender_name
      )}</div>` +
                sender_name_html +
                reply_private_container[0] +
                `<div class="live-chat-agent-message-bubble file-attachement-download">
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

            html +=
                `</div>`
                + reply_private_container[1] +
                `<div class="live-chat-agent-message-time">
                ${time}` +
                blue_ticks +
                `</div>`+ reply_private_container[2] +`</div>`;
        } else if (is_image(attached_file_src)) {
            html =
                `<div class="live-chat-agent-message-wrapper" id=${message_id}>
      <div class="live-chat-agent-image">${get_user_initial(
          sender_name
      )}</div>` +
                sender_name_html +
                reply_private_container[0] +
                `<div class="live-chat-agent-message-bubble-image-attachment">
          <div class="slideshow-container" value="1">
              <div class="mySlides livechat-slider-card">
                  ${get_image_path_html(attached_file_src)}
                  <div style="text-align: left;">
                      <h5 style="overflow-wrap: break-word; ">${
                          attached_file_src.split("/")[len - 1]
                      }</h5><a href="${attached_file_src}" target="_blank" download><span style="position: absolute; top: 8.5rem; right: 8px;"><svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
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

            html +=
                `</div>
        </div>
      </div>

      </div>`
      + reply_private_container[1] +
      `<div class="live-chat-agent-message-time">
      ${time}` +
                blue_ticks +
                `</div>`+ reply_private_container[2] +`</div>`;
        } else if (is_video(attached_file_src)) {
            html =
                `<div class="live-chat-agent-message-wrapper" id=${message_id}>
      <div class="live-chat-agent-image">${get_user_initial(
          sender_name
      )}</div>` +
                sender_name_html +
                reply_private_container[0] +
                `<div class="live-chat-agent-message-bubble-image-attachment">
          <div class="slideshow-container" value="1">
              <div class="mySlides livechat-slider-card">
                  ${get_video_path_html(attached_file_src)}
                  <div style="text-align: left;">
                      <h5 style="overflow-wrap: break-word; ">${
                          attached_file_src.split("/")[len - 1]
                      }</h5>`;

            if (message != "") {
                html += `<p style="overflow-wrap: break-word;">${message}</p>`;
            }

            html +=
                `</div>
        </div>
      </div>

      </div>`
      + reply_private_container[1] +
      `<div class="live-chat-agent-message-time">
      ${time}` +
                blue_ticks +
                `</div>`+ reply_private_container[2] +`</div>`;
        }
    }

    if (returnresponse)
    { 
        document.getElementById("style-2-" + pk).innerHTML += html;
    } else {
        
        return html;
    }
}

function get_user_initial(user_name) {
    try {
        return user_name.trim()[0].toUpperCase();
    } catch (err) {
        return "N";
    }
}

function get_masked_message(message) {
    if (!message) return;
    
    const regex = /[a-fA-F0-9]{64}/g;

    message = message.replace(regex, function (hashed_msg) {
        return (
            hashed_msg.substring(0, 5) +
            "***" +
            hashed_msg.substring(hashed_msg.length - 2, hashed_msg.length)
        );
    });

    return message;
}

function append_customer_message(
    message,
    sender_name,
    time = return_time(),
    pk,
    message_id="",
    reply_private_container=true,
    returnresponse = true,
) {
    message = get_masked_message(message);
    message = stripHTML(message);
    message = livechat_linkify(message);
    message = message.trim();

    var reply_private_container = get_reply_private_html(reply_private_container, "client");

    var sender_name_html =
        '<div class="live-chat-client-name-with-message">' +
        sender_name +
        "</div>";
    const html =
        `<div class="live-chat-client-message-wrapper" id=${message_id}>
                  <div class="live-chat-client-image">` +
        get_user_initial(sender_name) +
        `</div>` +
        sender_name_html + reply_private_container[0] +
        `<div class="live-chat-client-message-bubble">
                    ${message}
                  </div>`
                + reply_private_container[1] +
                  `<div class="live-chat-client-message-time">${time}</div>`
                  + reply_private_container[2] +
                `</div>`;
    if (returnresponse) {
        document.getElementById(`style-2-${pk}`).innerHTML += html;
    }
    else {
        return html;
    }
}

function append_agent_message(
    message,
    sender_initial,
    time = return_time(),
    pk,
    is_blue_tick = false,
    is_ongoing_chat = false,
    message_id="",
    reply_private_container=true,
    returnresponse=true
) {
    message = message.replace(new RegExp("\r?\n", "g"), "<br>");
    message = livechat_linkify(message);
    message = message.trim();

    var blue_ticks = "";

    var reply_private_container = get_reply_private_html(reply_private_container, "agent");

    if (is_ongoing_chat) {
        var blue_ticks =
            '<svg style="margin:-5px 5px 0px 5px;" width="14" height="10" viewBox="0 0 14 10" fill="none" xmlns="http://www.w3.org/2000/svg">\
                              <path class="doubletick_livechat_agent-' +
            pk +
            '" d="M3.45714 6.51434L1.07304 4.18025C0.827565 3.93994 0.429579 3.93994 0.184102 4.18025C-0.0613675 4.42056 -0.0613675 4.81022 0.184102 5.05053L3.01268 7.81976C3.25815 8.06007 3.65614 8.06007 3.90161 7.81976L10.8159 1.05053C11.0614 0.810204 11.0614 0.420567 10.8159 0.18024C10.5704 -0.0600801 10.1724 -0.0600801 9.92697 0.18024L3.45714 6.51434Z" fill="#4d4d4d"/>\
                              <path class="doubletick_livechat_agent-' +
            pk +
            '" d="M5.6412 8.51434L5.07684 7.99999C4.83137 7.75969 4.42956 8.27404 4.18409 8.51434C3.93862 8.75465 3.93864 8.62614 4.18411 8.86645L5.19673 9.81976C5.44221 10.0601 5.8402 10.0601 6.08567 9.81976L13 3.05053C13.2454 2.8102 13.2454 2.42057 13 2.18024C12.7545 1.93992 12.3565 1.93992 12.111 2.18024L5.6412 8.51434Z" fill="#4d4d4d"/>\
                              </svg>';

        if (is_blue_tick) {
            blue_ticks =
                '<svg style="margin:-5px 5px 0px 5px;" width="14" height="10" viewBox="0 0 14 10" fill="none" xmlns="http://www.w3.org/2000/svg">\
                              <path d="M3.45714 6.51434L1.07304 4.18025C0.827565 3.93994 0.429579 3.93994 0.184102 4.18025C-0.0613675 4.42056 -0.0613675 4.81022 0.184102 5.05053L3.01268 7.81976C3.25815 8.06007 3.65614 8.06007 3.90161 7.81976L10.8159 1.05053C11.0614 0.810204 11.0614 0.420567 10.8159 0.18024C10.5704 -0.0600801 10.1724 -0.0600801 9.92697 0.18024L3.45714 6.51434Z" fill="#0254D7"/>\
                              <path d="M5.6412 8.51434L5.07684 7.99999C4.83137 7.75969 4.42956 8.27404 4.18409 8.51434C3.93862 8.75465 3.93864 8.62614 4.18411 8.86645L5.19673 9.81976C5.44221 10.0601 5.8402 10.0601 6.08567 9.81976L13 3.05053C13.2454 2.8102 13.2454 2.42057 13 2.18024C12.7545 1.93992 12.3565 1.93992 12.111 2.18024L5.6412 8.51434Z" fill="#0254D7"/>\
                              </svg>';
        }
    }

    const html =
        `<div class="live-chat-agent-message-wrapper" id=${message_id}>
                  <div class="live-chat-agent-image">${sender_initial}</div>`
                  + reply_private_container[0] +
                  `<div class="live-chat-agent-message-bubble">
                    ${message}
                  </div>`
                  + reply_private_container[1] +
                  `<div class="live-chat-agent-message-time">
                    ${time}` +
                    blue_ticks +
                    `</div>`
                    + reply_private_container[2] +
                `</div>`;

    if (returnresponse) {
        document.getElementById(`style-2-${pk}`).innerHTML += html;
    }
    else {
        return html;
    }
}

function append_system_message(active_url, message, time = return_time(), pk, returnresponse=true) {
    const html = `<div class="easychat-system-message-div" >
                <div class="easychat-system-message easychat-system-message-line" style="color:263238" >
                Request Raised from: ${active_url}</div></div>
                <div class="easychat-system-message-div" >
                <div class="easychat-system-message easychat-system-message-line" style="color:263238" >
                ${message}<span class="message-time-bot">&nbsp;${time}</span>
                </div></div>`;
    if(returnresponse) {
        document.getElementById("style-2-" + pk).innerHTML += html;
    } else {
        return html
    }
}

function append_supervisor_message_realtime(
    sentence,
    session_id,
    sender_name,
    reply_message_id,
    time = return_time()
    ) {

    try {

        sentence = stripHTML(sentence);
        sentence = livechat_linkify(sentence);
        sentence = sentence.trim();

        var reply_message_for = document.getElementById(reply_message_id).classList[0].split("-")[2];
        var children_elements = document.getElementById(reply_message_id).children;

        var actual_message_pos = 1;
        if(reply_message_for == "client") {
            actual_message_pos = 2;
        }

        var message_bubble_container = children_elements.item(actual_message_pos);
        var actual_message = message_bubble_container.children.item(0);
        var reply_private_container = message_bubble_container.children.item(1);
        var time_container = reply_private_container.children.item(1);

        var inner_time_html = reply_message_for == 'client' ? time_container.outerHTML : '';
        var outer_time_html = reply_message_for == 'agent' ? time_container.outerHTML : '';

        document.getElementById(reply_message_id).removeChild(message_bubble_container);

        var reply_message_html = 
                                '<div class="live-chat-'+ reply_message_for +'-message-bubble-reply-wrapper">'
                                + actual_message.outerHTML +
                                '<div class="live-chat-'+ reply_message_for +'-message-reply-text-container">\
                                    <div class="live-chat-'+ reply_message_for +'-message-reply-text-hover-text-div">\
                                        *This message is only visible to Agents, Supervisors & Admin*\
                                    </div>\
                                    <div class="live-chat-'+ reply_message_for +'-message-reply-text-bubble">'
                                        + sentence +
                                    '</div>\
                                    <div class="live-chat-'+ reply_message_for +'-message-reply-time-div">'
                                        + time +
                                    '</div>\
                                </div>'
                                + inner_time_html +
                                '</div>' +
                                outer_time_html;
        $("#"+reply_message_id+">div:nth-child(1)").after(reply_message_html);
    } catch (err) {}
}

function append_supervisor_file_realtime(
    attached_file_src,
    session_id,
    thumbnail_url,
    message,
    reply_message_id,
    time = return_time()    
    ) {

    try {
        var attachment_html = get_attachment_html(attached_file_src, session_id, thumbnail_url, message, time);

        var reply_message_for = document.getElementById(reply_message_id).classList[0].split("-")[2];
        var children_elements = document.getElementById(reply_message_id).children;

        var actual_message_pos = 1;
        if(reply_message_for == "client") {
            actual_message_pos = 2;
        }

        var message_bubble_container = children_elements.item(actual_message_pos);
        var actual_message = message_bubble_container.children.item(0);
        var reply_private_container = message_bubble_container.children.item(1);
        var time_container = reply_private_container.children.item(1);

        var inner_time_html = reply_message_for == 'client' ? time_container.outerHTML : '';
        var outer_time_html = reply_message_for == 'agent' ? time_container.outerHTML : '';

        document.getElementById(reply_message_id).removeChild(message_bubble_container);

        var reply_message_html = 
                                '<div class="live-chat-'+ reply_message_for +'-message-bubble-reply-wrapper">'
                                + actual_message.outerHTML +
                                '<div class="live-chat-'+ reply_message_for +'-message-reply-text-container">\
                                    <div class="live-chat-'+ reply_message_for +'-message-reply-text-hover-text-div">\
                                        *This message is only visible to Agents, Supervisors & Admin*\
                                    </div>\
                                    <div class="live-chat-'+ reply_message_for +'-message-reply-text-bubble">'
                                        + attachment_html +
                                    '</div>\
                                    <div class="live-chat-'+ reply_message_for +'-message-reply-time-div">'
                                        + time +
                                    '</div>\
                                </div>'
                                + inner_time_html +
                                '</div>' +
                                outer_time_html;
        $("#"+reply_message_id+">div:nth-child(1)").after(reply_message_html);
    } catch (err) {}

}

function archive_submit_filter() {
    var start_date, end_date;
    if (is_mobile()) {
        start_date = document
            .getElementById("archive-default-start-date-mobile")
            .value.trim();
        end_date = document
            .getElementById("archive-default-end-date-mobile")
            .value.trim();
    } else {
        start_date = document
            .getElementById("archive-default-start-date")
            .value.trim();
        end_date = document
            .getElementById("archive-default-end-date")
            .value.trim();
    }

    start_date = change_date_format_original(start_date);
    end_date = change_date_format_original(end_date);

    if (start_date == "" || !is_valid_date(start_date)) {
        showToast("Select valid start date", 2000);
        return;
    }
    if (end_date == "" || !is_valid_date(end_date)) {
        showToast("Select valid end date", 2000);
        return;
    }

    var start_datetime = new Date(start_date);
    var end_datetime = new Date(end_date);
    if (start_datetime > end_datetime) {
        showToast("Start Date should be less than End Date", 4000);
        return;
    }

    // window.location.href =
    //     "?start_date=" + start_date + "&end_date=" + end_date;

    state.filter.is_applied = true;
    state.filter.start_date = start_date;
    state.filter.end_date = end_date;
    initialize_chat_history_table_archive(1);
}

function show_tagging_details(id) {
    $("#chat-history-tagging-modal").modal("show");

    if (state.taggings[id]) {
        show_form_data(state.taggings[id]);
        return;
    }

    const json_string = JSON.stringify({
        id: id,
    });

    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/get-dispose-chat-form-data/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if (response.status == 200) {
                const form_filled = response.form_filled;

                state.taggings[id] = form_filled;
                show_form_data(form_filled);
            }
        });
}

function show_form_data(data) {
    let html = "";
    data.forEach((field) => {
        if (field.type == "1" || field.type == "8" || field.type == "9") {
            html += get_text_field(field.label, field.value, field.optional);
        } else if (field.type == "2") {
            html += get_radio_data(field.label, field.value, field.optional);
        } else if (field.type == "3") {
            html += get_checkbox_data(field.label, field.value, field.optional);
        } else if (field.type == "4") {
            html += get_date_data(field.label, field.value, field.optional);
        } else if (field.type == "5") {
            html += get_comment_data(field.label, field.value, field.optional);
        } else if (field.type == "6") {
            html += get_dropdown_data(field.label, field.value, field.optional);
        }
    });

    $("#livechat-dispose-chat-form-data").html(html);

    setTimeout(() => {
        document.querySelector('#chat-history-tagging-modal .modal-body').scrollTop = 0;
    }, 300)
}

function get_text_field(label, value, optional) {
    let html = `
	<div class="mb-3">
		<label>${label}
	`;

    if (!optional) {
        html += `
		<b>*</b>	
		`;
    }

    html += `
		</label>
		<input disabled class="form-control " type="text" placeholder="Placeholder Text" value="${value}">
	</div>
	`;

    return html;
}

function get_radio_data(label, value, optional) {
    let html = `
	<div class="mb-3 form-preview-radio-checkbox-div">
		<label>${label}
	`;

    if (!optional) {
        html += `
		<b>*</b>	
		`;
    }

    html += `
		</label>
		<div class="response-widget-dragable-output-item form-preview-radio-checkbox-item-div">
			<div class="widget-indigator-icon">
				<svg width="24" height="25" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d="M12 16C14.2091 16 16 14.2091 16 12C16 9.79086 14.2091 8 12 8C9.79086 8 8 9.79086 8 12C8 14.2091 9.79086 16 12 16Z" fill="#C4C4C4"/>
					<path fill-rule="evenodd" clip-rule="evenodd" d="M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12ZM20 12C20 16.4183 16.4183 20 12 20C7.58172 20 4 16.4183 4 12C4 7.58172 7.58172 4 12 4C16.4183 4 20 7.58172 20 12Z" fill="#C4C4C4"/>
				</svg>
			</div>
			<input disabled type="text" class="edit_radio_button_choices" value="${value}">
		</div>
	</div>
	`;

    return html;
}

function get_checkbox_data(label, value, optional) {
    let html = `
	<div class="mb-3 form-preview-radio-checkbox-div">
	<label>${label}
	`;

    if (!optional) {
        html += `
		<b>*</b>	
		`;
    }

    html += `</label>`;

    for (const val of value) {
        html += `
		<div class="response-widget-dragable-output-item form-preview-radio-checkbox-item-div">
			<div class="widget-indigator-icon">
				<svg width="24" height="25" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d="M18 3C19.6569 3 21 4.34315 21 6V18C21 19.6569 19.6569 21 18 21H6C4.34315 21 3 19.6569 3 18V6C3 4.34315 4.34315 3 6 3H18ZM16.4697 7.96967L10 14.4393L7.53033 11.9697C7.23744 11.6768 6.76256 11.6768 6.46967 11.9697C6.17678 12.2626 6.17678 12.7374 6.46967 13.0303L9.46967 16.0303C9.76256 16.3232 10.2374 16.3232 10.5303 16.0303L17.5303 9.03033C17.8232 8.73744 17.8232 8.26256 17.5303 7.96967C17.2374 7.67678 16.7626 7.67678 16.4697 7.96967Z" fill="#C4C4C4"/>
				</svg>
			</div>
			<input disabled type="text" class="edit_radio_button_choices" value="${val}">
		</div>
		`;
    }

    html += `</div>`;

    return html;
}

function get_date_data(label, value, optional) {

    const date_array = value.split("-");
    const date = new Date(date_array[2],date_array[0]-1,date_array[1]);

    let html = `
	<div class="mb-3 form-preview-date-div-container">
	<label>${label}
	`;

    if (!optional) {
        html += `
		<b>*</b>	
		`;
    }

    html += `
		</label>
		<div class="livechat-dispose-date-preview-wrapper">
			<div class="livechat-dispose-date-div date-disabled-text">${date.getDate()}</div>
			<div class="livechat-dispose-month-day-wrapper">
				<div class="livechat-dispose-month-div">
					<span>${state.months[date.getMonth()]} </span>
					<span>${date.getFullYear()}</span>
				</div>
				<div class="livechat-dispose-day-div">${state.days[date.getDay()]}</div>
			</div>
		</div>
	</div>
	`;

    return html;
}

function get_comment_data(label, value, optional) {
    let html = `
	<div class="mb-3 form-preview-comment-container">
		<label>${label}
	`;

    if (!optional) {
        html += `
		<b>*</b>	
		`;
    }

    html += `
		</label>
		<textarea value="${value}" disabled class="form-preview-comment-section-textarea" placeholder="Type here">${value}</textarea>
	</div>
	`;

    return html;
}

function get_dropdown_data(label, value, optional) {
    let html = `
	<div class="mb-3">
	<label>${label}
	`;

    if (!optional) {
        html += `
		<b>*</b>	
		`;
    }

    html += `
		</label>
		<select disabled class="form-control select-dropdown-icon">
			<option value="${value}">${value}</option>
		</select>
	</div>
	`;

    return html;
}

function append_supervisor_message_archive(
    sentence,
    session_id,
    sender_name,
    reply_message_id,
    time = return_time()
    ) {

    try {

        sentence = stripHTML(sentence);
        sentence = livechat_linkify(sentence);
        sentence = sentence.trim();

        var reply_message_for = document.getElementById(reply_message_id).classList[0].split("-")[2];
        var children_elements = document.getElementById(reply_message_id).children;

        var actual_message_pos = 1;
        if(reply_message_for == "client") {
            actual_message_pos = 2;
        }

        var actual_message = children_elements.item(actual_message_pos);
        var time_container = children_elements.item(actual_message_pos + 1);
        document.getElementById(reply_message_id).removeChild(actual_message);
        document.getElementById(reply_message_id).removeChild(time_container);

        var inner_time_html = reply_message_for == 'client' ? time_container.outerHTML : '';
        var outer_time_html = reply_message_for == 'agent' ? time_container.outerHTML : '';

        var reply_message_html = 
                                '<div class="live-chat-'+ reply_message_for +'-message-bubble-reply-wrapper">'
                                + actual_message.outerHTML +
                                '<div class="live-chat-'+ reply_message_for +'-message-reply-text-container">\
                                    <div class="live-chat-'+ reply_message_for +'-message-reply-text-hover-text-div">\
                                        *This message is only visible to Agents, Supervisors & Admin*\
                                    </div>\
                                    <div class="live-chat-'+ reply_message_for +'-message-reply-text-bubble">'
                                        + sentence +
                                    '</div>\
                                    <div class="live-chat-'+ reply_message_for +'-message-reply-time-div">'
                                        + time +
                                    '</div>\
                                </div>'
                                + inner_time_html +
                                '</div>' +
                                outer_time_html;
        $("#"+reply_message_id+">div:nth-child("+actual_message_pos+")").after(reply_message_html);
    } catch (err) {}
}

function append_supervisor_file_archive(
    attached_file_src,
    session_id,
    thumbnail_url,
    message,
    reply_message_id,
    time = return_time()    
    ) {

    try{

        var attachment_html = get_attachment_html(attached_file_src, session_id, thumbnail_url, message, time);

        var reply_message_for = document.getElementById(reply_message_id).classList[0].split("-")[2];
        var children_elements = document.getElementById(reply_message_id).children;

        var actual_message_pos = 1;
        if(reply_message_for == "client") {
            actual_message_pos = 2;
        }

        var actual_message = children_elements.item(actual_message_pos);
        var time_container = children_elements.item(actual_message_pos + 1);
        document.getElementById(reply_message_id).removeChild(actual_message);
        document.getElementById(reply_message_id).removeChild(time_container);

        var inner_time_html = reply_message_for == 'client' ? time_container.outerHTML : '';
        var outer_time_html = reply_message_for == 'agent' ? time_container.outerHTML : '';

        var reply_message_html = 
                                '<div class="live-chat-'+ reply_message_for +'-message-bubble-reply-wrapper">'
                                + actual_message.outerHTML +
                                '<div class="live-chat-'+ reply_message_for +'-message-reply-text-container">\
                                    <div class="live-chat-'+ reply_message_for +'-message-reply-text-hover-text-div">\
                                        *This message is only visible to Agents, Supervisors & Admin*\
                                    </div>\
                                    <div class="live-chat-'+ reply_message_for +'-message-reply-text-bubble">'
                                        + attachment_html +
                                    '</div>\
                                    <div class="live-chat-'+ reply_message_for +'-message-reply-time-div">'
                                        + time +
                                    '</div>\
                                </div>'
                                + inner_time_html +
                                '</div>' +
                                outer_time_html;
        $("#"+reply_message_id+">div:nth-child(1)").after(reply_message_html);
    } catch (err) {}
}


export {
    append_file_to_agent,
    get_user_initial,
    get_masked_message,
    append_customer_message,
    append_agent_message,
    archive_submit_filter,
    append_system_message,
    show_tagging_details,
    append_supervisor_message_realtime,
    append_supervisor_file_realtime,
    append_supervisor_message_archive,
    append_supervisor_file_archive,
};
