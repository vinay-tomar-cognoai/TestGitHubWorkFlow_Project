import {
    EncryptVariable,
    get_delayed_date_object,
    set_cookie,
    get_cookie,
    showToast,
    is_mobile,
    stripHTML,
    custom_decrypt,
    getCsrfToken,
} from "./utils";

import {
    get_selected_month_mobile, get_selected_year_mobile
} from "./admin/calender";

import {
    get_theme_color,
} from "./agent/console";

import {
    get_queue_requests_page,
    initialize_queue_requests_table,
    get_current_chat_requests_count,
} from "./agent/queue_requests";
import { empty_local_db } from "./agent/local_db";

const state = {
    all_canned_response_checked: false,
    upload_file_limit_size: 1024000,
    user_last_activity_time_obj: new Date(),
    character_limit: {
        large: 500,
        small: 25,
        medium: 100,
    },
    no_internet: false,
};

function resetTimer(e) {
    var delay_by_nine_minutes = get_delayed_date_object(-18);
    if (state.user_last_activity_time_obj < delay_by_nine_minutes) {
        // if user is active in last minute ( after inactive for 9 minuits )
        state.user_last_activity_time_obj = new Date();
        send_session_timeout_request();
    }
    state.user_last_activity_time_obj = new Date();
}

function send_session_timeout_request() {

    if (get_cookie("is_online") == "0") {
        return;
    }

    var is_online_from_this_time = get_delayed_date_object(-3);

    if (state.user_last_activity_time_obj > is_online_from_this_time) {
        var CSRF_TOKEN = $('input[name="csrfmiddlewaretoken"]').val();
        $.ajax({
            url: "/chat/set-session-time-limit/",
            type: "POST",
            headers: {
                "X-CSRFToken": CSRF_TOKEN,
            },
            data: {},
            success: function (response) {
                set_cookie("is_online", "1", "/");
            },
            error: function (xhr, textstatus, errorthrown) {
                set_cookie("is_online", "0", "/");
            },
        });
    }
}

function update_user_last_seen() {
    var params = "";
    var xhttp = new XMLHttpRequest();
    var csrf_token = getCsrfToken();

    xhttp.open("POST", "/livechat/update-last-seen/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                const status_changed_by_admin_supervisor = response.status_changed_by_admin_supervisor;
                const status_set = response.status_set;
                
                if (status_changed_by_admin_supervisor) {
                    if (IS_USER_ONLINE && status_set == "Offline" && USER_STATUS == '3') {
                        showToast("You have been marked offline by admin/supervisor.", 2000);
                        setTimeout(function () {
                            window.location.reload();
                        }, 2000);
                    }
                } else if (!IS_USER_ONLINE && status_set == "Online" && USER_STATUS == '3') {
                    showToast("You have been marked online by admin/supervisor.", 2000);
                    setTimeout(function () {
                        window.location.reload();
                    }, 2000);
                }
            } 
        } else if(this.status == 401 || this.status == 403) {
            window.location.reload();
        } else if (this.status == 0) {
            show_no_internet_notification();
        }
    };
    xhttp.send(params);
}
    
function apply_calender_filter() {
    let selected_month, selected_year;
    if (is_mobile()) {
        selected_month = get_selected_month_mobile();
        selected_year = get_selected_year_mobile();
    } else {
        selected_month = $("#select-calender-month").val();
        selected_year = $("#select-calender-year").val();
    }
    if (selected_month == "Select" || selected_year == "Select") {
        showToast("Please select valid options", 2000);
        return;
    }

    window.location.href =
        "?selected_month=" +
        selected_month +
        "&selected_year=" +
        selected_year;
}

function get_character_limit() {
    return state.character_limit;
}

function set_character_count(el) {
    const count = el.value.length;
    const id = `${el.id}-char-count`;

    document.getElementById(id).innerHTML = count;
}

function upload_excel(uploaded_file){
return new Promise(function (resolve, reject) {
    var CSRF_TOKEN = $('input[name="csrfmiddlewaretoken"]').val();
    var json_string = JSON.stringify(uploaded_file)
    json_string = EncryptVariable(json_string)

    var encrypted_data = {
        "Request": json_string
    }

    var params = JSON.stringify(encrypted_data);

    $.ajax({
        url: "/livechat/upload-excel/",
        type: "POST",
        contentType: "application/json",
        headers: {
            'X-CSRFToken': CSRF_TOKEN
        },
        data: params,
        processData: false,
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response.status == 200) {
                resolve(response);
            } else if (response.status == 300) {
                showToast("File format is Invalid", 2000);
            } else {
                showToast("Internal Server Error. Please try again later.", 2000);
            }
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        }
    });
})
}

function check_chat_requests_queue() {
    var params = "";
    var xhttp = new XMLHttpRequest();
    var csrf_token = getCsrfToken();

    xhttp.open("POST", "/livechat/check-chat-requests-queue/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token); 
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);

            if (response["status"] == 200) {

                if(document.getElementById("live-chat-requests-in-queue")) {

                    update_queue_request_notif_icon(response);
                }
            }
        }
    };
    xhttp.send(params);
}

function update_queue_request_notif_icon(response) {
    const theme_color = get_theme_color();

    if(response["chats_available"]) {

        if (window.location.href.includes('requests-in-queue')) {

            if(!get_current_chat_requests_count()) {

                initialize_queue_requests_table(get_queue_requests_page());
            }

            var html = `<svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M10.7142 14.8927C11.661 14.8927 12.4285 15.6602 12.4285 16.607V17.1785C12.4285 19.4316 10.3033 21.7499 6.71419 21.7499C3.12501 21.7499 0.999817 19.4316 0.999817 17.1785V16.607C0.999817 15.6602 1.76733 14.8927 2.71414 14.8927H10.7142ZM10.7142 16.0356H2.71414C2.39854 16.0356 2.14271 16.2914 2.14271 16.607V17.1785C2.14271 18.8215 3.77947 20.6071 6.71419 20.6071C9.64885 20.6071 11.2857 18.8215 11.2857 17.1785V16.607C11.2857 16.2914 11.0298 16.0356 10.7142 16.0356ZM14.7143 12.607C15.1877 12.607 15.5714 12.9908 15.5714 13.4641C15.5714 13.9375 15.1877 14.3213 14.7143 14.3213C14.2408 14.3213 13.8571 13.9375 13.8571 13.4641C13.8571 12.9908 14.2408 12.607 14.7143 12.607ZM6.71419 7.46406C8.44992 7.46406 9.85708 8.87116 9.85708 10.607C9.85708 12.3427 8.44992 13.7498 6.71419 13.7498C4.9784 13.7498 3.5713 12.3427 3.5713 10.607C3.5713 8.87116 4.9784 7.46406 6.71419 7.46406ZM6.71419 8.60693C5.6096 8.60693 4.71417 9.50237 4.71417 10.607C4.71417 11.7115 5.6096 12.607 6.71419 12.607C7.81877 12.607 8.71421 11.7115 8.71421 10.607C8.71421 9.50237 7.81877 8.60693 6.71419 8.60693ZM14.7143 5.74976C15.9766 5.74976 17 6.77314 17 8.0355C17 8.87042 16.758 9.33802 16.1383 9.9874L15.8365 10.2955C15.4051 10.7452 15.2857 10.9876 15.2857 11.4641C15.2857 11.7797 15.0298 12.0355 14.7143 12.0355C14.3987 12.0355 14.1428 11.7797 14.1428 11.4641C14.1428 10.6292 14.3848 10.1616 15.0045 9.5122L15.3063 9.20414C15.7377 8.75436 15.8571 8.51196 15.8571 8.0355C15.8571 7.40429 15.3454 6.89263 14.7143 6.89263C14.0831 6.89263 13.5714 7.40429 13.5714 8.0355C13.5714 8.3511 13.3155 8.60693 13 8.60693C12.6844 8.60693 12.4285 8.3511 12.4285 8.0355C12.4285 6.77314 13.4519 5.74976 14.7143 5.74976Z" fill="${theme_color.one}"/>
                        <circle cx="19" cy="3" r="3" fill="#FF0000"/>
                        </svg>

                        <span style="color: ${theme_color.one} !important;" id="sidebarlink">Requests in Queue</span></a>`

            document.getElementById("live-chat-requests-in-queue").innerHTML = html;

        } else {
            var html = `<svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M10.7142 14.8927C11.661 14.8927 12.4285 15.6602 12.4285 16.607V17.1785C12.4285 19.4316 10.3033 21.7499 6.71419 21.7499C3.12501 21.7499 0.999817 19.4316 0.999817 17.1785V16.607C0.999817 15.6602 1.76733 14.8927 2.71414 14.8927H10.7142ZM10.7142 16.0356H2.71414C2.39854 16.0356 2.14271 16.2914 2.14271 16.607V17.1785C2.14271 18.8215 3.77947 20.6071 6.71419 20.6071C9.64885 20.6071 11.2857 18.8215 11.2857 17.1785V16.607C11.2857 16.2914 11.0298 16.0356 10.7142 16.0356ZM14.7143 12.607C15.1877 12.607 15.5714 12.9908 15.5714 13.4641C15.5714 13.9375 15.1877 14.3213 14.7143 14.3213C14.2408 14.3213 13.8571 13.9375 13.8571 13.4641C13.8571 12.9908 14.2408 12.607 14.7143 12.607ZM6.71419 7.46406C8.44992 7.46406 9.85708 8.87116 9.85708 10.607C9.85708 12.3427 8.44992 13.7498 6.71419 13.7498C4.9784 13.7498 3.5713 12.3427 3.5713 10.607C3.5713 8.87116 4.9784 7.46406 6.71419 7.46406ZM6.71419 8.60693C5.6096 8.60693 4.71417 9.50237 4.71417 10.607C4.71417 11.7115 5.6096 12.607 6.71419 12.607C7.81877 12.607 8.71421 11.7115 8.71421 10.607C8.71421 9.50237 7.81877 8.60693 6.71419 8.60693ZM14.7143 5.74976C15.9766 5.74976 17 6.77314 17 8.0355C17 8.87042 16.758 9.33802 16.1383 9.9874L15.8365 10.2955C15.4051 10.7452 15.2857 10.9876 15.2857 11.4641C15.2857 11.7797 15.0298 12.0355 14.7143 12.0355C14.3987 12.0355 14.1428 11.7797 14.1428 11.4641C14.1428 10.6292 14.3848 10.1616 15.0045 9.5122L15.3063 9.20414C15.7377 8.75436 15.8571 8.51196 15.8571 8.0355C15.8571 7.40429 15.3454 6.89263 14.7143 6.89263C14.0831 6.89263 13.5714 7.40429 13.5714 8.0355C13.5714 8.3511 13.3155 8.60693 13 8.60693C12.6844 8.60693 12.4285 8.3511 12.4285 8.0355C12.4285 6.77314 13.4519 5.74976 14.7143 5.74976Z" fill="#4D4D4D"/>
                        <circle cx="19" cy="3" r="3" fill="#FF0000"/>
                        </svg>

                        <span style="color: #858796" id="sidebarlink">Requests in Queue</span></a>`

            document.getElementById("live-chat-requests-in-queue").innerHTML = html;

        }

    } else {

        if (window.location.href.includes('requests-in-queue')) {
            var html = `<svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M10.7142 10.8927C11.661 10.8927 12.4285 11.6602 12.4285 12.607V13.1785C12.4285 15.4316 10.3033 17.7499 6.71419 17.7499C3.12501 17.7499 0.999817 15.4316 0.999817 13.1785V12.607C0.999817 11.6602 1.76733 10.8927 2.71414 10.8927H10.7142ZM10.7142 12.0356H2.71414C2.39854 12.0356 2.14271 12.2914 2.14271 12.607V13.1785C2.14271 14.8215 3.77947 16.6071 6.71419 16.6071C9.64885 16.6071 11.2857 14.8215 11.2857 13.1785V12.607C11.2857 12.2914 11.0298 12.0356 10.7142 12.0356ZM14.7143 8.60697C15.1877 8.60697 15.5714 8.99075 15.5714 9.46413C15.5714 9.9375 15.1877 10.3213 14.7143 10.3213C14.2408 10.3213 13.8571 9.9375 13.8571 9.46413C13.8571 8.99075 14.2408 8.60697 14.7143 8.60697ZM6.71419 3.46406C8.44992 3.46406 9.85708 4.87116 9.85708 6.60695C9.85708 8.34274 8.44992 9.74984 6.71419 9.74984C4.9784 9.74984 3.5713 8.34274 3.5713 6.60695C3.5713 4.87116 4.9784 3.46406 6.71419 3.46406ZM6.71419 4.60693C5.6096 4.60693 4.71417 5.50237 4.71417 6.60695C4.71417 7.71154 5.6096 8.60697 6.71419 8.60697C7.81877 8.60697 8.71421 7.71154 8.71421 6.60695C8.71421 5.50237 7.81877 4.60693 6.71419 4.60693ZM14.7143 1.74976C15.9766 1.74976 17 2.77314 17 4.0355C17 4.87042 16.758 5.33802 16.1383 5.9874L15.8365 6.29546C15.4051 6.74524 15.2857 6.98764 15.2857 7.46411C15.2857 7.77971 15.0298 8.03554 14.7143 8.03554C14.3987 8.03554 14.1428 7.77971 14.1428 7.46411C14.1428 6.62918 14.3848 6.16158 15.0045 5.5122L15.3063 5.20414C15.7377 4.75436 15.8571 4.51196 15.8571 4.0355C15.8571 3.40429 15.3454 2.89263 14.7143 2.89263C14.0831 2.89263 13.5714 3.40429 13.5714 4.0355C13.5714 4.3511 13.3155 4.60693 13 4.60693C12.6844 4.60693 12.4285 4.3511 12.4285 4.0355C12.4285 2.77314 13.4519 1.74976 14.7143 1.74976Z" fill="${theme_color.one}"/>
                        </svg>

                        <span style="color: ${theme_color.one} !important;" id="sidebarlink">Requests in Queue</span></a>`

            document.getElementById("live-chat-requests-in-queue").innerHTML = html;

        } else {
            var html = `<svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M10.7142 10.8927C11.661 10.8927 12.4285 11.6602 12.4285 12.607V13.1785C12.4285 15.4316 10.3033 17.7499 6.71419 17.7499C3.12501 17.7499 0.999817 15.4316 0.999817 13.1785V12.607C0.999817 11.6602 1.76733 10.8927 2.71414 10.8927H10.7142ZM10.7142 12.0356H2.71414C2.39854 12.0356 2.14271 12.2914 2.14271 12.607V13.1785C2.14271 14.8215 3.77947 16.6071 6.71419 16.6071C9.64885 16.6071 11.2857 14.8215 11.2857 13.1785V12.607C11.2857 12.2914 11.0298 12.0356 10.7142 12.0356ZM14.7143 8.60697C15.1877 8.60697 15.5714 8.99075 15.5714 9.46413C15.5714 9.9375 15.1877 10.3213 14.7143 10.3213C14.2408 10.3213 13.8571 9.9375 13.8571 9.46413C13.8571 8.99075 14.2408 8.60697 14.7143 8.60697ZM6.71419 3.46406C8.44992 3.46406 9.85708 4.87116 9.85708 6.60695C9.85708 8.34274 8.44992 9.74984 6.71419 9.74984C4.9784 9.74984 3.5713 8.34274 3.5713 6.60695C3.5713 4.87116 4.9784 3.46406 6.71419 3.46406ZM6.71419 4.60693C5.6096 4.60693 4.71417 5.50237 4.71417 6.60695C4.71417 7.71154 5.6096 8.60697 6.71419 8.60697C7.81877 8.60697 8.71421 7.71154 8.71421 6.60695C8.71421 5.50237 7.81877 4.60693 6.71419 4.60693ZM14.7143 1.74976C15.9766 1.74976 17 2.77314 17 4.0355C17 4.87042 16.758 5.33802 16.1383 5.9874L15.8365 6.29546C15.4051 6.74524 15.2857 6.98764 15.2857 7.46411C15.2857 7.77971 15.0298 8.03554 14.7143 8.03554C14.3987 8.03554 14.1428 7.77971 14.1428 7.46411C14.1428 6.62918 14.3848 6.16158 15.0045 5.5122L15.3063 5.20414C15.7377 4.75436 15.8571 4.51196 15.8571 4.0355C15.8571 3.40429 15.3454 2.89263 14.7143 2.89263C14.0831 2.89263 13.5714 3.40429 13.5714 4.0355C13.5714 4.3511 13.3155 4.60693 13 4.60693C12.6844 4.60693 12.4285 4.3511 12.4285 4.0355C12.4285 2.77314 13.4519 1.74976 14.7143 1.74976Z" fill="#4D4D4D"/>
                        </svg>

                        <span style="color: #858796" id="sidebarlink">Requests in Queue</span></a>`

            document.getElementById("live-chat-requests-in-queue").innerHTML = html;

        }                    
    }
}

export function show_no_internet_notification () {
    state.no_internet = true;

    Object.entries(localStorage).map(
        x => x[0]
    ).filter(
        x => x.startsWith('ongoing_chat')
    ).map(
        x => localStorage.removeItem(x))

    empty_local_db();
    
    $('#no_interet_loader_div').show();
    $('#no_interet_loader_div_2').show();
}

export function get_no_internet() {
    return state.no_internet;
}

export {
    resetTimer,
    send_session_timeout_request,
    update_user_last_seen,
    apply_calender_filter,
    get_character_limit,
    set_character_count,
    upload_excel,
    check_chat_requests_queue,
};
