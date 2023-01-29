import axios from "axios";

import {
    change_date_format_original,
    custom_decrypt,
    get_params,
    is_valid_date,
    showToast,
    validate_email,
    EncryptVariable,
    encrypt_variable,
    getCsrfToken,
} from "../utils";


const state = {
    filter: {
        is_applied: false,
        agent_username: null,
        start_date: null,
        end_date: null,
    },
    page: 1,
    refresh_interval: 0,
    supervisor_name: window.SUPERVISOR_NAME,
};

$(window).ready(function () {
    if (!window.location.pathname.includes('cobrowsing-history')) {
        unset_cobrowsing_filter();
        return;
    }

    load_cobrowsing_filters();

    state.refresh_interval = parseInt(REFRESH_INTERVAL);

    setInterval(() => {
        initialize_cb_history_table(state.page, true);
    }, state.refresh_interval * 1000);

    $("#apply_cobrowsing_history_filter_btn").on("click", function (e) {
        apply_cobrowsing_history_filter();
    });
    
    $("#apply_cobrowsing_history_filter_btn_mobile").on("click", function (e) {
        apply_cobrowsing_history_filter_for_mobile();
    });
    

    $("#refresh_cobrowsing_history_btn").on("click", () => {
        initialize_cb_history_table(state.page);
    });

    $("#reset_cobrowsing_history_filter").on("click", () => {
        reset_cobrowsing_history_filter();
    });
});

export async function initialize_cb_history_table(
    page,
    auto_refresh = false
) {
    if (!auto_refresh) {
        toggle_loader("show");
        $("#livechat_cobrowsing_history_no_data").css("display", "none");
        $("#livechat_cobrowsing_history_table_div").css("display", "none");
    }

    state.page = page;

    const response = await get_cobrowsing_history(page);

    console.log(response);

    toggle_loader("hide");

    if (response.total_audits > 0) {
        const table_html = get_table_html(response);

        document.getElementById("livechat_cobrowsing_history_no_data").style.display = "none";

        $("#livechat_cobrowsing_history_table_div").html(table_html);
        $("#livechat_cobrowsing_history_table_div").css("display", "block");

        initialize_datatable(response.start_point, response.total_audits);
        apply_pagination(response.pagination_data);
        
        $('.dowload_audio_recording').on('click', (e) => {
            window.location = e.target.dataset.id;
        })

    } else {

        document.getElementById("livechat_cobrowsing_history_table_div").style.display = "none";
        
        document.getElementById("livechat_cobrowsing_history_no_data").style.display = "block";
    }
}

function toggle_loader(value) {
    value = value == "show" ? "block" : "none";

    document.getElementById("livechat_cobrowsing_history_loader").style.display =
        value;
}

export function get_cobrowsing_history(page) {
    return new Promise((resolve, reject) => {
        let json_string = {
            page: page,
            call_type: 'video_call',
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
            .post("/livechat/get-cobrowsing-history/", params, config)
            .then((response) => {
                response = custom_decrypt(response.data);
                response = JSON.parse(response);

                resolve(response);
            });
    });
}

function get_table_html(response) {
    let table_html = `<table role="table" id="cobrowsing-history-table" class="display">`;

    table_html += get_table_header();
    table_html += get_table_body(response.cobrowsing_object_list);
    table_html += `</table>`;
    return table_html;
}

function get_table_header() {
    return `
            <thead role="rowgroup">
                <tr role="row">
                    <th role="columnheader">Customer Name</th>
                    ${ IS_AGENT == false ? '<th role="columnheader">Agent Username</th>' : '<th role="columnheader" style="display: none;">Agent Username</th>'}
                    <th role="columnheader">Start Date-Time</th>
                    <th role="columnheader">End Date-Time</th>
                    <th role="columnheader">Total Duration</th>
                    <th role="columnheader">Status</th>
                </tr>
            </thead>`;
}

function get_table_body(audit_list) {
    let body_html = ``;
    audit_list.forEach((audit) => {
        body_html += `<tr role="row">`;

        body_html += get_col(audit.username);

        if (!IS_AGENT)
            body_html += get_col(audit.agent_username);
        else
            body_html += `<td role="cell" style="display: none;">${audit.agent_username}</td>`

        body_html += get_col(audit.start_date_time);
        body_html += get_col(audit.end_date_time);
        body_html += get_col(audit.call_duration);

        if (audit.meeting_status == 'Completed')
            body_html += get_col(audit.meeting_status);
        else {
            body_html += get_col(`<button class="livechat-ongoing-chat-notif" style="background: white; color: #38B224 !important; border: none !important; cursor: default;">
                                <svg width="11" height="11" viewBox="0 0 11 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <circle cx="5.5" cy="5.5" r="5.5" fill="#38B224"/>
                                </svg>
                                Ongoing
                            </button>`)
        }
        
        body_html += "</tr>";
    });

    return body_html;
}

function get_col(value) {
    return `
            <td role="cell">${value}</td>`;
}


function initialize_datatable(start_point, total_audits) {
    $("#cobrowsing-history-table").DataTable({
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
    });

    const table = $("#cobrowsing-history-table").DataTable();

    const value = document.getElementById("cobrowsing-history-table-search").value;

    if (value != "") {
        table.search(value).draw();
    }

    $("#cobrowsing-history-table-search").keyup(function () {
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

    $("#cobrowsing-history-table_wrapper").append(html);

    add_pagination_events();
}

function add_pagination_events() {
    $(".audit-trail-pagination").on("click", (event) => {
        initialize_cb_history_table(event.target.dataset.page);
    });
}

export function apply_cobrowsing_history_filter_for_mobile() {

    let start_date = document
        .getElementById("cobrowsing-history-default-start-date-mobile")
        .value.trim();

    let end_date = document
        .getElementById("cobrowsing-history-default-end-date-mobile")
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
    state.filter.start_date = start_date;
    state.filter.end_date = end_date;

    set_cobrowsing_filter();

    $("#apply-agent-mobile-filter-cobrowsing-history").modal("hide");
    initialize_cb_history_table(1);
}

export function apply_cobrowsing_history_filter() {
    const agent_username = $("#select-agent-username").val();


    let start_date = document
        .getElementById("cobrowsing-history-default-start-date")
        .value.trim();

    let end_date = document
        .getElementById("cobrowsing-history-default-end-date")
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
    state.filter.start_date = start_date;
    state.filter.end_date = end_date;

    set_cobrowsing_filter();

    $("#apply-filter-cobrowsing-history").modal("hide");
    initialize_cb_history_table(1);
}
// filter
function reset_cobrowsing_history_filter() {
    // document.getElementById("select-agent-username").innerHTML = "";

    // let new_option = new Option("All", "All", true, false);
    // $("#select-agent-username").append(new_option).trigger("change");

    // AGENT_LIST.forEach((agent) => {
    //     new_option = new Option(agent, agent, false, false);
    //     $("#select-agent-username").append(new_option).trigger("change");
    // });
    $('#select-agent-username').val("All").selectpicker('refresh');
    
    document.getElementById("cobrowsing-history-default-start-date").value =
        DEFAULT_LIVECHAT_FILTER_START_DATETIME;

    document.getElementById("cobrowsing-history-default-end-date").value =
        DEFAULT_LIVECHAT_FILTER_END_DATETIME;
}


export function get_refresh_interval() {
    return state.refresh_interval;
}


function close_cobrowsing_history_export_modal() {
    $('#modal-export-cobrowsing-history').modal('toggle');
}


export function export_cobrowsing_filter() {

    let selected_filter_value = document.getElementById("select-date-range").value;

    if (selected_filter_value == "0") {
        alert("Please select valid date range filter");
        return;
    }

    let startdate = $("#export-filter-default-start-date").val().trim();
    let enddate = $("#export-filter-default-end-date").val().trim();
    let email_field = document.getElementById("filter-data-email");
    startdate = change_date_format_original(startdate)
    enddate = change_date_format_original(enddate)

    if ((selected_filter_value == "4" || (selected_filter_value == "5" && !window.IS_REPORT_GENERATION_VIA_KAFKA_ENABLED)) && validate_email("filter-data-email") == false) {
        showToast("Please enter valid email ID", 4000);
        return;
    }

    if (
        selected_filter_value == "4" &&
        (startdate == "" || enddate == "" || !is_valid_date(startdate) || !is_valid_date(enddate))
    ) {
        showToast("Please enter valid dates", 4000);
        return;
    }
    var start_datetime = new Date(startdate);
    var end_datetime = new Date(enddate);
    if (start_datetime > end_datetime) {
        showToast("Start Date should be less than End Date", 4000);
        return;
    }
    var json_string = JSON.stringify({
        selected_filter_value: selected_filter_value,
        startdate: startdate,
        enddate: enddate,
        email: email_field.value,
    });
    if (selected_filter_value == "5") {
        var json_string = JSON.stringify({
            selected_filter_value: selected_filter_value,
            email: email_field.value,
        });
    }
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
        url: "/livechat/export-cobrowsing-data/",
        type: "POST",
        headers: {
            'X-CSRFToken': CSRF_TOKEN
        },
        data: {
            json_string: json_string,
        },
        success: function (response) {
            var response = custom_decrypt(response);
            response = JSON.parse(response);
            if ((response["status"] = 200)) {
                if (response["export_path"] == null) {
                    alert("Sorry, unable to process your request. Kindly try again later.");
                } else if (response["export_path"] == "request_saved") {
                    showToast("We have saved your request and will send data over provided email ID in a short period.", 5000);
                    close_cobrowsing_history_export_modal();
                }  else if (response["export_path"] == "request_saved_custom_range") {
                    showToast("We haved saved your request and will send data over provided email ID within 24 hours.", 5000);
                    close_cobrowsing_history_export_modal();
                } else if (response["export_path"] == "request_saved_today") {
                    showToast(
                        "We have saved your request and will send data over provided email ID within 5 mins.",
                        5000
                    );
                    document.getElementById("custom-range-filter-email").style.display = "none";
                    document.getElementById("filter-data-email").value = "";
                    document.getElementById("select-date-range").value = "0";
                    close_cobrowsing_history_export_modal();
                } else {
                    if (response["export_path_exist"]) {
                        window.open(response["export_path"], "_blank");
                    } else {
                        alert("Requested data doesn't exists. Kindly try again later.");
                    }
                }
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}

function set_cobrowsing_filter() {
    localStorage.setItem(`cobrowsing_is_applied`, state.filter.is_applied);
    localStorage.setItem(`cobrowsing_agent_username`, state.filter.agent_username);
    localStorage.setItem(`cobrowsing_start_date`, state.filter.start_date)
    localStorage.setItem(`cobrowsing_end_date`, state.filter.end_date)
}

function unset_cobrowsing_filter() {
    localStorage.removeItem(`cobrowsing_is_applied`);
    localStorage.removeItem(`cobrowsing_agent_username`);
    localStorage.removeItem(`cobrowsing_start_date`);
    localStorage.removeItem(`cobrowsing_end_date`);
}

function load_cobrowsing_filters() {

    let filter = state.filter;

    if(localStorage.getItem(`cobrowsing_is_applied`)) {

        filter.is_applied = (localStorage.getItem(`cobrowsing_is_applied`) === "true" );
        
        if(!window.IS_USER_AGENT) {
            filter.agent_username = localStorage.getItem(`cobrowsing_agent_username`);
            $(`#select-agent-username option[value="${filter.agent_username}"]`).attr("selected", "selected");
        }

        filter.start_date = localStorage.getItem(`cobrowsing_start_date`);
        filter.end_date = localStorage.getItem(`cobrowsing_end_date`);

        const format = {
            dateFormat: 'dd-mm-yy', 
			prevText: "Previous"
        }

        setTimeout(() => {
            $('#cobrowsing-history-default-start-date').val(change_date_format_original(filter.start_date.trim()));
            $('#cobrowsing-history-default-end-date').val(change_date_format_original(filter.end_date.trim()));
            $('#cobrowsing-history-default-start-date-mobile').val(change_date_format_original(filter.start_date.trim()));
            $('#cobrowsing-history-default-end-date-mobile').val(change_date_format_original(filter.end_date.trim()));
        }, 500);
    }
}
