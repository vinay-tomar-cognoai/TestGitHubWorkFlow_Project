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
} from "../utils";

import {
    get_theme_color,
} from "./console";

const state = {
    page: 1,
    initial_refresh: true,
    refresh_interval: 0,
    current_chat_requests_count: 0,
};

$(window).ready(function () {
    if (!window.location.pathname.includes('requests-in-queue')) {
        return;
    }

    state.refresh_interval = parseInt(REFRESH_INTERVAL);

    setInterval(() => {
        initialize_queue_requests_table(state.page);
    }, state.refresh_interval * 1000);

    state.initial_refresh = false;

    $(".live-chat-request-queue-goto-inbox-button").on("click", (event) => {
        window.location = "/livechat/";
    });

});

export async function initialize_queue_requests_table(page) {
    if (state.initial_refresh) {
        toggle_loader("show");
    }

    state.page = page;

    const response = await get_queue_requests(page); 
    toggle_loader("hide");

    if (response.queue_requests.length > 0) {
        const table_html = get_table_html(response);

        document.getElementById("livechat_queue_requests_no_data").style.display = "none";

        $("#livechat_queue_requests_table_div").html(table_html);
        $("#livechat_queue_requests_table_div").css("display", "block");

        initialize_timer(response.queue_requests);
        state.current_chat_requests_count = parseInt(response.total_requests);
        initialize_datatable(response.start_point, response.total_requests);
        apply_pagination(response.pagination_data);

        document.getElementById("live-chat-page-name").innerHTML = "Requests in Queue (" + response.total_requests + ")";

        if(is_mobile()) {
            document.getElementById("requests-count-header-mobile").innerHTML = "Requests in Queue (" + response.total_requests + ")";
        }

    } else {
        document.getElementById(
            "livechat_queue_requests_table_div"
        ).style.display = "none";
        document.getElementById("livechat_queue_requests_no_data").style.display =
            "block";

        document.getElementById("live-chat-page-name").innerHTML = "Requests in Queue";

        if(is_mobile()) {
            document.getElementById("requests-count-header-mobile").innerHTML = "Requests in Queue";
        }
    }
}

function toggle_loader(value) {
    value = value == "show" ? "block" : "none";

    document.getElementById("livechat_queue_requests_loader").style.display = value;
}

export function get_queue_requests(page) {
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
            .post("/livechat/get-livechat-queue-requests/", params, config)
            .then((response) => {
                response = custom_decrypt(response.data);
                response = JSON.parse(response);
                
                resolve(response);
            });
    });

}

function get_table_html(response) {
    let table_html = `<table role="grid" id="queue-requests-table" class="display dataTable no-footer" aria-describedby="table-agent-details_info">`;

    table_html += get_table_header();
    table_html += get_table_body(response.queue_requests, response.is_agent_online);
    table_html += `</table>`;
    return table_html;
}

function get_table_header() {
    return `
        <thead role="rowgroup">
            <tr role="row">
                <th role="columnheader" class="sorting_disabled" rowspan="1" colspan="1">Customer Name</th>
                <th role="columnheader" class="sorting_disabled" rowspan="1" colspan="1">Channel</th>
                <th role="columnheader" class="sorting_disabled" rowspan="1" colspan="1">Chat Category</th>
                <th role="columnheader" class="sorting_disabled" rowspan="1" colspan="1">Queue Time </th>
                <th role="columnheader" class="sorting_disabled" rowspan="1" colspan="1">Initiated Date-Time</th>
                <th role="columnheader" class="sorting_disabled" rowspan="1" colspan="1"> </th>

            </tr>
        </thead>`;
}

function get_table_body(request_list, is_agent_online) {
    let body_html = ``;
    request_list.forEach((request) => {
        body_html += `<tr role="row">`;

        body_html += get_col(request.username);
        body_html += get_col(request.channel);
        body_html += get_col(request.category);
        body_html += '<td role="cell" id="timer-'+ request.pk +'"></td>';
        body_html += get_col(request.joined_date);
        if(is_agent_online) {
            body_html += get_col(
                `<button id=${request.pk} class="livechat-rewuest-queue-assign-to-me-btn" onclick="self_assign_request(this);" >Assign to me</button></button>`
            );
        }
        else {
            body_html += get_col(
                `<button id=${request.pk} class="livechat-rewuest-queue-assign-to-me-btn" onclick="self_assign_request(this);" disabled>Assign to me</button></button>`
            );
        }

        body_html += "</tr>";
    });

    return body_html;
}

function get_col(value) {
    return `
            <td role="cell">${value}</td>`;
}

function initialize_timer(request_list) {

    request_list.forEach((request) => {
            var request_time = new Date(request.timestamp).getTime();

            var timer = setInterval(function() {
                var current_time = new Date().getTime();
                var time_diff = (current_time - request_time);
                time_diff = (request.queue_timer * 1000) - time_diff;

                var minutes = Math.floor((time_diff % (1000 * 60 * 60)) / (1000 * 60));
                var seconds = Math.floor((time_diff % (1000 * 60)) / 1000);
                minutes = minutes < 10 ? '0' + minutes : minutes;
                seconds = seconds < 10 ? '0' + seconds : seconds;

                if(document.getElementById("timer-"+request.pk)) {
                    document.getElementById("timer-"+request.pk).innerHTML = minutes + ':' + seconds;
                }

                if (time_diff <= 0) {
                    if(document.getElementById("timer-"+request.pk)) {
                        document.getElementById("timer-"+request.pk).innerHTML = '00:00';
                    }
                    $(`#${request.pk}`).attr("disabled", true);
                    clearInterval(timer);
                }

            }, 1000);
    });
}

function initialize_datatable(start_point, total_requests) {
    $("#queue-requests-table").DataTable({
        language: {
            info: `Showing _START_ to _END_ entries out of ${total_requests}`,
            infoEmpty: "No records available",
            infoFiltered: "(filtered from _MAX_ total records)",
        },
        bPaginate: false,
        ordering: false,
        searching: false,
        infoCallback: function (settings, start, end, max, total, pre) {
            if (settings.oPreviousSearch["sSearch"] != "") {
                return pre;
            }
            end = start_point - 1 + end;
            start = start_point - 1 + start;
            return `Showing ${start} to ${end} entries out of ${total_requests}`;
        },
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
                    html += `<li class="active-page"><a data-page="${page}" class="queue-requests-pagination" style="color: #0254d7;" href="javascript:void(0)">${page}</a></li>`;
                } else if (pagination.num_pages == page) {
                    html += `<li class="active-page" style="border-radius: 0 6px 6px 0;"><a data-page="${page}" class="queue-requests-pagination" style="color: #0254d7;" href="javascript:void(0)">${page}</a></li>`;
                } else {
                    html += `<li class="active-page" style="border-radius: 0px;"><a data-page="${page}" class="queue-requests-pagination" style="color: #0254d7;" href="javascript:void(0)">${page}</a></li>`;
                }
            } else if (
                page > pagination.number - 5 &&
                page < pagination.number + 5
            ) {
                html += `<li><a class="queue-requests-pagination" href="javascript:void(0)" data-page="${page}">${page}</a></li>`;
            }
        }
    }

    $("#queue-requests-table_wrapper").append(html);

    add_pagination_events();
}

function add_pagination_events() {
    $(".queue-requests-pagination").on("click", (event) => {
        initialize_queue_requests_table(event.target.dataset.page);
    });
}

export function self_assign_request(element) {
    var session_id = element.id;
    const theme_color = get_theme_color();
    $(element).text("Assigning...");
    $(element).css("background", theme_color.three);
    $(element).css("color", theme_color.one);

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
        .post("/livechat/livechat-self-assign-request/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            console.log(response);
            if(response.status == 200) {
                if(response.chat_assigned) {

                    initialize_queue_requests_table(state.page);
                    $('#request-assigned-text').html(response.customer_name + ' has been successfully assigned');
                    $('#livechat_request_queue_assign_chat_modal').modal('show');
                    setTimeout(function() {
                        $('#livechat_request_queue_assign_chat_modal').modal('hide')
                    }, 10000);

                } else {

                    initialize_queue_requests_table(state.page);
                    $('#livechat_request_queue_already_assign_modal').modal('show');
                    setTimeout(function() {
                        $('#livechat_request_queue_already_assign_modal').modal('hide')
                    }, 10000);

                }
            }
        })        
        .catch((err) => {
            console.log(err);
        });

}

export function get_queue_requests_page() {
    return state.page;
}

export function get_current_chat_requests_count() {
    return state.current_chat_requests_count;
}
