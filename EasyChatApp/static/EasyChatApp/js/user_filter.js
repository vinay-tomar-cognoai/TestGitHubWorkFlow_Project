var AUDIO_PLAYER = document.querySelector(".audio-player");
var AUDIO = new Audio("");
var last_scroll_id = 0


$(document).ready(function () {
    $('#datepicker-1-0').datepicker({
        changeMonth: true,
        changeYear: true,
        dayNamesMin: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        beforeShow: function (textbox, instance) {
            $('.easychat-calendar-div-wrapper').append($('#ui-datepicker-div'));
            $("#timepicker-container-1-1 .custom-timepicker").hide();
            $("#timepicker-container-1-0 .custom-timepicker").hide();
        }
    });
});

$(document).ready(function () {
    $('#datepicker-1-1').datepicker({
        changeMonth: true,
        changeYear: true,
        dayNamesMin: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        beforeShow: function (textbox, instance) {
            $('.easychat-calendar-div-wrapper').append($('#ui-datepicker-div'));
            $("#timepicker-container-1-1 .custom-timepicker").hide();
            $("#timepicker-container-1-0 .custom-timepicker").hide();
        }
    });
});

function hide_selected_mis(el) {
    $(".selected-misdashboard").prop('checked', false);
    $(".easychat-user-custom-checkbox-div").hide();
    $(el).css("visibility", "hidden");
    $("#user_history_add_intent_btn").css("visibility", "hidden");
    $(".user-chat-history-checkbox").prop('checked', false);
    $('.easychat-query-add-intent-wrapper').removeAttr("style")
}

var ans_hr = "", ans_min = "", ans_ampm = "";
function handle_click_time(id) {
    let all_hrs = document.querySelectorAll("#timepicker-container-" + id + " .hr-clock ul li");
    let all_mins = document.querySelectorAll("#timepicker-container-" + id + " .min-clock ul li");
    let all_ampm = document.querySelectorAll("#timepicker-container-" + id + " .ampm-clock ul li");
    all_hrs.forEach(each_hr => {
        if (each_hr.childNodes[1].checked === true) {
            each_hr.childNodes[0].classList.add("datetimepicker-selected-time");
            ans_hr = each_hr.childNodes[0].innerText;
        }
        else
            each_hr.childNodes[0].classList.remove("datetimepicker-selected-time");
    })
    all_mins.forEach(each_min => {
        if (each_min.childNodes[1].checked === true) {
            each_min.childNodes[0].classList.add("datetimepicker-selected-time");
            ans_min = each_min.childNodes[0].innerText;
        }
        else
            each_min.childNodes[0].classList.remove("datetimepicker-selected-time");
    })
    all_ampm.forEach(each_ampm => {
        if (each_ampm.childNodes[1].checked === true) {
            each_ampm.childNodes[0].classList.add("datetimepicker-selected-time");
            ans_ampm = each_ampm.childNodes[0].innerText;
        }
        else
            each_ampm.childNodes[0].classList.remove("datetimepicker-selected-time");
    })
}

function handle_time_picker_click(id) {
    if (id === "1-0")
        document.querySelector("#timepicker-container-1-1 .custom-timepicker").style.display = "none";

    if (id === "1-1")
        document.querySelector("#timepicker-container-1-0 .custom-timepicker").style.display = "none";

    document.querySelector("#timepicker-container-" + id + " .custom-timepicker").style.display = "block";

}

function close_time_modal(id) {
    document.querySelector("#timepicker-container-" + id + " .custom-timepicker").style.display = "none";
}

function handle_save_time(id) {
    document.querySelector("#timepicker-container-" + id + " .custom-timepicker").style.display = "none";
    if (ans_hr && ans_ampm && ans_min)
        document.querySelector("#time-picker-btn-" + id).value = ans_hr + " : " + ans_min + " " + ans_ampm;
}

function changed_date(id, type, event) {
    var day_arr = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    var month_arr = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    var date = new Date(document.querySelector("#datepicker-" + id).value);
    var datenum = date.getDate();
    var month = date.getMonth();
    var year = date.getFullYear();
    var day = date.getDay();
    document.querySelector("#date-displayer-" + id + " .date").innerHTML = datenum;
    document.querySelector("#date-displayer-" + id + " .month-year").innerHTML = month_arr[month] + " " + year;
    if (day - 1 != -1) {
        document.querySelector("#date-displayer-" + id + " .day").innerHTML = day_arr[day - 1];
    } else {
        document.querySelector("#date-displayer-" + id + " .day").innerHTML = day_arr[6];
    }
    document.querySelector("#datepicker-" + id).style.opacity = "0";
    document.querySelector("#date-displayer-" + id + " .row").style.display = "flex";
}

function handle_close() {
    document.querySelector(".btns-sections").style.display = "none";
}

function refresh_timestamp() {
    var today = new Date();
    var today = String(today.getMonth() + 1).padStart(2, '0') + '/' + String(today.getDate()).padStart(2, '0') + '/' + today.getFullYear();
    document.getElementById("datepicker-1-0").value = today;
    document.getElementById("datepicker-1-1").value = today;
    changed_date('1-0', 'Double datetime', null);
    changed_date('1-1', 'Double datetime', null);
    document.getElementById("time-picker-btn-1-0").value = "12 : 00 AM";
    document.getElementById("time-picker-btn-1-1").value = "11 : 59 PM";
    document.getElementById("ui-datepicker-div").style.display = "none";
    close_time_modal('1-0');
    close_time_modal('1-1');
}

function compare_message_history_dates(start_date, end_date) {
    // function will return true if start_date <= end_date
    // MM/DD/YYYY format
    var start_date_day = start_date.split("/")[1];
    var start_date_month = start_date.split("/")[0];
    var start_date_year = start_date.split("/")[2];
    var end_date_day = end_date.split("/")[1];
    var end_date_month = end_date.split("/")[0];
    var end_date_year = end_date.split("/")[2];

    if (end_date_year < start_date_year) {
        return false;
    } else if (end_date_year == start_date_year) {
        if (end_date_month < start_date_month) {
            return false;
        } else if (end_date_month == start_date_month) {
            if (end_date_day < start_date_day) {
                return false;
            }
        }
    }
    return true;
}

function compare_message_history_datetime(start_date, end_date, start_time, end_time) {
    // function will return true if start_date_time <= end_date_time
    var start_date_day = start_date.split("/")[1];
    var start_date_month = start_date.split("/")[0];
    var start_date_year = start_date.split("/")[2];
    var end_date_day = end_date.split("/")[1];
    var end_date_month = end_date.split("/")[0];
    var end_date_year = end_date.split("/")[2];

    var start_time_ap = start_time.split(" ")[3];
    var end_time_ap = end_time.split(" ")[3];
    var start_time_hr = start_time.split(" ")[0];
    var end_time_hr = end_time.split(" ")[0];
    var start_time_min = start_time.split(" ")[2];
    var end_time_min = end_time.split(" ")[2];

    if (end_date_year < start_date_year) {
        return false;
    } else if (end_date_year == start_date_year) {
        if (end_date_month < start_date_month) {
            return false;
        } else if (end_date_month == start_date_month) {
            if (end_date_day < start_date_day) {
                return false;
            } else if (end_date_day == start_date_day) {
                if (end_time_ap == "AM" && start_time_ap == "PM") {
                    return false;
                } else if (end_time_ap == start_time_ap) {
                    if (end_time_hr < start_time_hr) {
                        return false;
                    } else if (end_time_hr == start_time_hr) {
                        if (end_time_min < start_time_min) {
                            return false;
                        }
                    }
                }
            }
        }
    }
    return true;
}

$(document).ready(function () {
    changed_date('1-0', 'Double datetime', null);
    changed_date('1-1', 'Double datetime', null);
    show_custom_date();
});

function reset_call_recording_audio() {

    $('.easychat-call-recording-btn').css('display', 'none');
    $(".easychat-message-history-recording-wrapper").hide();
    AUDIO.setAttribute("src", "");
    AUDIO.pause();
    return;
}

function setup_call_recording_audio(audio_url) {

    if (audio_url.trim() == "") {
        $('.easychat-call-recording-btn').css('display', 'none');
        $(".easychat-message-history-recording-wrapper").hide();
        return
    }

    $('.easychat-call-recording-btn').css('display', 'flex');

    document.getElementById("user_call_recording_download_src").href = audio_url

    // var AUDIO_PLAYER = document.querySelector(".audio-player");
    // AUDIO = new Audio(audio_url);
    AUDIO.setAttribute("src", audio_url)

    AUDIO.addEventListener("loadeddata", () => {
        AUDIO_PLAYER.querySelector(".time .length").textContent = get_time_code_from_num(
            AUDIO.duration
        );
        AUDIO.volume = .75;
    },
        false
    );

    //click on timeline to skip around
    let timeline = AUDIO_PLAYER.querySelector(".timeline");
    timeline.addEventListener("click", e => {
        let timelineWidth = window.getComputedStyle(timeline).width;
        let timeToSeek = e.offsetX / parseInt(timelineWidth) * AUDIO.duration;
        AUDIO.currentTime = timeToSeek;
    }, false);



    //check audio percentage and update time accordingly
    setInterval(() => {
        check_audio_percentage_and_update_time()
    }, 500);

    function check_audio_percentage_and_update_time() {
        let progressBar = AUDIO_PLAYER.querySelector(".progress");
        progressBar.style.width = AUDIO.currentTime / AUDIO.duration * 100 + "%";
        AUDIO_PLAYER.querySelector(".time .current").textContent = get_time_code_from_num(
            AUDIO.currentTime
        );
    }

    let PLAY_BUTTON = AUDIO_PLAYER.querySelector(".toggle-play");

    PLAY_BUTTON.addEventListener("click", () => {
        toggle_between_playing_and_pausing(PLAY_BUTTON, AUDIO)
    },
        false
    );

    $('.easychat-call-recording-btn').unbind('click');
    $('.easychat-call-recording-btn').click(function (event) {
        show_audio_player_div(PLAY_BUTTON, AUDIO);
        $('.user-search-cross-icon').click()
        $('#easychat-history-global-searchbar-btn, .user-search-cross-icon, #user_history_global_search').css('pointer-events', 'none')
    });

    $('.audio-player-cross-btn').unbind('click');
    $(".audio-player-cross-btn").click(function (event) {
        close_user_call_recording_player_div(PLAY_BUTTON, AUDIO);
        $('#easychat-history-global-searchbar-btn, .user-search-cross-icon, #user_history_global_search').css('pointer-events', 'auto')
    });
}

//toggle between playing and pausing on button click
function toggle_between_playing_and_pausing(play_btn, audio) {
    if (audio.paused) {
        play_btn.classList.remove("play");
        play_btn.classList.add("pause");
        audio.play();
    } else {
        play_btn.classList.remove("pause");
        play_btn.classList.add("play");
        audio.pause();
    }
}

function get_time_code_from_num(num) {
    let seconds = parseInt(num);
    let minutes = parseInt(seconds / 60);
    seconds -= minutes * 60;
    const hours = parseInt(minutes / 60);
    minutes -= hours * 60;

    if (hours === 0) {
        return `${minutes}:${String(seconds % 60).padStart(2, 0)}`;
    }

    return `${String(hours).padStart(2, 0)}:${minutes}:${String(seconds % 60).padStart(2, 0)}`;

}

function show_audio_player_div(PLAY_BUTTON, AUDIO) {

    toggle_between_playing_and_pausing(PLAY_BUTTON, AUDIO)
    $('.easychat-call-recording-btn').hide();
    $(".easychat-message-history-recording-wrapper").show();
}

function close_user_call_recording_player_div(PLAY_BUTTON, AUDIO) {

    if (!AUDIO.paused) {
        toggle_between_playing_and_pausing(PLAY_BUTTON, AUDIO)
    }

    $('.easychat-call-recording-btn').css('display', 'flex');
    $(".easychat-message-history-recording-wrapper").hide();
}

function get_user_messages(user_id, scroll_to_session_id = null) {

    window.history.replaceState(null, null, window.location.pathname + window.location.search.split('&')[0])
    document.getElementById("loader-user-message").style.display = 'flex'
    // document.getElementById("no-user-selected").style.display = 'none';
    document.getElementById("select-user-id").innerHTML = user_id;
    document.getElementById("load_user_messages").innerHTML = "";
    $('.user-search-cross-icon').click()
    hide_selected_mis($('.user-history-clearall-btn'));
    csrf_token = get_csrf_token();
    json_string = JSON.stringify({
        user_id: user_id,
        bot_pk: get_url_vars()["bot_id"]
    });
    json_string = EncryptVariable(json_string);
    $.ajax({
        url: "/chat/user-details/",
        type: "POST",
        headers: {
            "X-CSRFToken": csrf_token
        },
        data: {
            data: json_string
        },
        success: function (response) {
            document.getElementById("loader-user-message").style.display = 'none'
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status_code"] == 200) {

                var events_query = ["silence_response", "silence_termination_response"];

                message_list = response["message_history"]
                message_list = message_list.reverse()

                reset_call_recording_audio();

                if ("user_call_recording" in response && response["user_call_recording"] != "") {

                    call_recording_url = response["user_call_recording"]
                    setup_call_recording_audio(call_recording_url)
                }
                html = '<div id="no-user-selected" style="margin-top: 200px;display:none;"><center><h5>Select a user to see the message history.</h5></center></div>'
                // html += '<ul>'

                let max_file_size_allowed = response["max_file_size_allowed"]
                let country_code = []
                let session_ids_appended = []
                $('#user_chat_session_id_drop').show()
                $('#session_id_dropdown').empty().append('<div class="session-drop-data-not-found-div" id="session_drop_nodata_found">No result found</div>')
                $('.user-messages-search-wrapper').css('pointer-events', 'auto')
                $('.user-messages-search-wrapper').css('opacity', '1')
                for (var i = 0; i < message_list.length; i++) {
                    let session_id = message_list[i].session_id
                    if (!session_ids_appended.includes(session_id)) {
                        html += '<div class="easychat-session-created-message-wrapper" id="' + session_id + '">' +
                            '<div class="easychat-session-created-message-text-div">' +
                            '<span>New session started</span>, ' +
                            '<span class="user-chat-session-created-id-text"> Session ID: ' + session_id + '</span>, ' +
                            '<span class="user-chat-query-count-text">User query count: ' + message_list[i]['session_id_wise_data'][session_id] + '</span>'
                        if (message_list[i]["channel_name"] == "Web")
                            html += ', <span class="user-chat-device-type-text">Device: ' + message_list[i]['source_device'] + '</span>'
                        html += '</div>' +
                            '</div>'
                        session_ids_appended.push(session_id)
                        let session_id_dropdown_html = '<li class="easychat-user-message-history-session-ids-item">' +
                            '<span>' + session_id + '</span>' +
                            '</li>'
                        $('#session_id_dropdown').append(session_id_dropdown_html)
                    }
                    
                    var whatsapp_menu_sections_html = ""
                    if ("whatsapp_menu_sections" in message_list[i] && message_list[i]["whatsapp_menu_sections"].length) {
                        whatsapp_menu_sections_html += `<div class="easychat-query-reply-message-text-div" style="margin-top:-8px;">
                            <div class="easychat-query-reply-message-text search-div">
                                <div style="padding: 8px; min-width: 180px;">`;
                        
                        for (var j=0; j<message_list[i]["whatsapp_menu_sections"].length; j++) {
                            whatsapp_menu_sections_html += `<div class="whatsapp-item-header-div">` + message_list[i]["whatsapp_menu_sections"][j].section_title + `</div>`;

                            for (var k=0; k<message_list[i]["whatsapp_menu_sections"][j].buttons.length; k++) {

                                var button_title = message_list[i]["whatsapp_menu_sections"][j].buttons[k].name;
                                if (!button_title) {
                                    button_title = message_list[i]["whatsapp_menu_sections"][j].buttons[k];
                                }

                                whatsapp_menu_sections_html += `<div class="whatsapp-item-subheader-div"><span>` + button_title + `</span><svg width="19" height="18" viewBox="0 0 19 18" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3.98066 8.99997C3.98066 11.8942 6.33566 14.25 9.23066 14.25C12.1249 14.25 14.4807 11.8942 14.4807 8.99997C14.4807 6.10572 12.1249 3.74997 9.23066 3.74997C6.33566 3.74997 3.98066 6.10572 3.98066 8.99997ZM12.9807 8.99997C12.9807 11.0677 11.2984 12.75 9.23066 12.75C7.16291 12.75 5.48066 11.0677 5.48066 8.99997C5.48066 6.93222 7.16291 5.24997 9.23066 5.24997C11.2984 5.24997 12.9807 6.93222 12.9807 8.99997Z" fill="#C4C4C4"/></svg></div>`
                            }
                        }

                        whatsapp_menu_sections_html += `</div></div></div>`;
                        message_list[i]["message_recommendation"] = "";
                        message_list[i]["message_choices"] = "";
                    }
                    
                    if (message_list[i]["message_recommendation"] != "[]" && message_list[i]["message_recommendation"] != "") {
                        table_html = '<table style="max-width: 300px;margin-left: 37px;margin-top:10px;margin-bottom:16px"><thead>'

                        try {
                            message_recommendation = JSON.parse(message_list[i]["message_recommendation"]);
                        } catch (err) {
                            message_recommendation = [];
                        }

                        for (var j = 0; j < message_recommendation.length; j++) {
                            if (message_recommendation[j].name) {
                                table_html += '<tr><th>' + message_recommendation[j].name + '</th></tr>';
                            } else {
                                table_html += '<tr><th>' + message_recommendation[j] + '</th></tr>'
                            }
                        }
                        table_html += '</thead></table>'
                    } else {
                        table_html = "";
                    }

                    if (message_list[i]["message_choices"] != "") {
                        table_choices = '<table style="max-width: 300px;margin-left: 37px;margin-top:10px;margin-bottom:16px"><thead>'
                        message_choices = message_list[i]["message_choices"].split(",")
                        for (var k = 0; k < message_choices.length; k++) {
                            if (message_choices[k].includes("$$$")) {
                                table_choices += '<tr><th>' + message_choices[k].replace("$$$", " ") + '</th></tr>'
                            }
                            else {
                                table_choices += '<tr><th>' + message_choices[k] + '</th></tr>'
                            }
                        }
                        table_choices += '</thead></table>'
                    } else {
                        table_choices = "";
                    }

                    var msg_received = message_list[i]["message_received"].trim();

                    if (events_query.includes(msg_received)) {
                        msg_received = "";
                    }

                    if (msg_received) {
                        html += get_message_received_html(message_list[i])
                        // html += '<img src="/static/EasyChatApp/img/botIcon.svg" alt="" />'
                    }
                    
                    let attached_file_src = message_list[i]["attached_file_src"]
                    if (attached_file_src && attached_file_src.trim() != "") {
                        // attached_file_src = window.location.origin + attached_file_src
                        let attached_file_name = message_list[i]["attached_file_name"]
                        // html += '<div style="display: none; margin-top: 2%"><label><input type="checkbox" name="input-checkbox-selected-misdashboard-" id="input-checkbox-selected-misdashboard-' + message_list[i]["pk"] + '" class="filled-in selected-misdashboard" ><span></span></label></left></div>'
                        html += get_html_for_message_hitory_attachment(attached_file_name, attached_file_src)
                        msg_received = ""
                    }

                    if (msg_received != "") {
                        msg_received = get_masked_message(msg_received);
                        // html += '<div style="display: none; margin-top: 2%"><label><input type="checkbox" name="input-checkbox-selected-misdashboard-" id="input-checkbox-selected-misdashboard-' + message_list[i]["pk"] + '" class="filled-in selected-misdashboard" ><span></span></label></left></div>'
                        html += '<div class="easychat-query-send-message-text-div search-div" id="message-div-' + message_list[i]["pk"] + '">'
                        html += sanitize_html(msg_received) + '</div>'
                        html += '<a class="easychat-query-add-intent-wrapper" id="action-list-ul-' + message_list[i]["pk"] + '">'
                        html += '<svg width="24" height="24" viewBox="0 0 24 24" fill="black" xmlns="http://www.w3.org/2000/svg">' +
                            '<path d="M18 13H13V18C13 18.55 12.55 19 12 19C11.45 19 11 18.55 11 18V13H6C5.45 13 5 12.55 5 12C5 11.45 5.45 11 6 11H11V6C11 5.45 11.45 5 12 5C12.55 5 13 5.45 13 6V11H18C18.55 11 19 11.45 19 12C19 12.55 18.55 13 18 13Z" />' +
                            '</svg>' +
                            '<span>Add to intent</span></a>'
                        // html += '<ul class="action-list-ul" id="action-list-ul-' + message_list[i]["pk"] + '"><li class="action-list-li action-list-add-to-intent" tab-index=-1>Add to intent</li></ul>'
                    }
                    html += '</li></div></div>'

                    if (message_list[i]["pdf_search_results"].length) {
                        var pdf_search_list_html = '<div class="easychat-user-history-card-slider-div slick-pdf-slider">'
                        
                        pdf_search_results = message_list[i]["pdf_search_results"]
                        if(pdf_search_results.length == 1){
                            pdf_search_list_html = '<div class="easychat-user-history-card-slider-div slick-pdf-slider single-pdf-card">'  
                        }
                        for (var pdf_search_item = 0; pdf_search_item < pdf_search_results.length; pdf_search_item++) {
                            pdf_search_list_html += get_pdf_search_results_html(pdf_search_results[pdf_search_item], message_list[i]["widget_language_tuned_text"])
                        }
                        html += pdf_search_list_html
                        html += '</div>'
                    }
                    if (message_list[i]["form_data_widget"].length > 0) {
                        widget_form_name = JSON.parse(message_list[i]["form_data_widget"])[0]
                        form_fields_data = JSON.parse(message_list[i]["form_data_widget"])[1]
                        html += append_form_widget_data(widget_form_name, form_fields_data, message_list[i].pk)
                    }

                    order_of_response = message_list[i]["order_of_response"]
                    is_campaign = message_list[i]['is_campaign']
                    let sent_calendar_time = false

                    html += '<div class="easychat-query-reply-message-wrapper">'
                    if(is_campaign){
                        html += '<div class="easychat-query-reply-message-div" style="width: 40%!important">'
                    }else{
                        html += '                <div class="easychat-query-reply-message-div">'
                    }
                    html += '                    <div class="easychat-query-message-icon">'
                    html += '                        <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">'
                    html += '<path d="M8.15332 10.3333H22.7249C23.2631 10.3333 24.4243 10.8499 24.7633 12.9166V22.0592C24.7835 22.8866 24.279 24.5416 22.0993 24.5416H13.5622L9.16243 27.1249" stroke="#2D2D2D" stroke-width="1.29167"></path><path d="M9.18262 27.1249L8.87988 24.5416C8.07259 24.3263 6.45801 23.5083 6.45801 21.9583V12.9166C6.55219 12.0555 6.7002 10.3333 8.39551 10.3333" stroke="#2D2D2D" stroke-width="1.29167" stroke-linecap="round"></path><path d="M5.16667 20.6667V15.1367C4.13333 15.1367 3.875 15.8095 3.875 16.1458V19.0924C3.875 20.4164 4.73611 20.6936 5.16667 20.6667Z" stroke="#2D2D2D" stroke-width="0.645833" stroke-linecap="round"></path><path d="M25.8535 15.1338L25.8129 20.6636C26.8462 20.6712 27.1094 20.0004 27.1119 19.664L27.1336 16.7175C27.1433 15.3936 26.2843 15.1101 25.8535 15.1338Z" stroke="#2D2D2D" stroke-width="0.645833" stroke-linecap="round"></path><circle cx="10.9795" cy="16.1458" r="1.29167" stroke="black" stroke-width="1.29167"></circle><circle cx="10.9795" cy="16.1458" r="1.29167" stroke="#2D2D2D" stroke-width="1.29167"></circle><circle cx="20.0205" cy="16.1458" r="1.29167" stroke="#2D2D2D" stroke-width="1.29167"></circle><path d="M13.1592 19.375C14.0203 20.2361 16.1704 21.4417 17.8818 19.375" stroke="#2D2D2D" stroke-width="0.645833" stroke-linecap="round"></path><circle cx="15.5003" cy="5.16658" r="1.9375" stroke="#2D2D2D" stroke-width="1.29167"></circle><path d="M15.5 7.75V9.04167" stroke="#2D2D2D" stroke-width="0.645833" stroke-linecap="round"></path>'
                    html += '                        </svg>'
                    html += '                    </div>'
                    html += '                    <div class="easychat-query-reply-recommendation-div" >'
                    if (is_campaign) {
                        sent_image = message_list[i]["sent_image"]
                        if (sent_image && sent_image.length > 0) {
                            for (img = 0; img < sent_image.length; img++) {
                                sending_image = sent_image[img]
                                html += campaign_response_image_sent(sending_image)
                            }
                        }
                        sent_video = message_list[i]["sent_video"]
                        if (sent_video && sent_video.length > 0) {
                            for (vid = 0; vid < sent_video.length; vid++) {
                                sending_video = sent_video[vid]
                                html += campaign_response_video_sent(sending_video)
                            }

                        }
                        sent_docs = message_list[i]['sent_card']
                        if (sent_docs && sent_docs.length > 0) {
                            for (doc = 0; doc < sent_docs.length; doc++) {
                                sending_doc = sent_docs[doc]
                                document_name = message_list[i]['document_name']
                                if (document_name.length > 16){
                                    document_name = document_name.substring(0,16) + "....";
                                }
                                html += campaign_response_document(document_name)
                            }
                        }
                        if (message_list[i]["message_sent"].includes("$$$")) {
                            message_list[i]["message_sent"] = message_list[i]["message_sent"].split("$$$")
                            var j;
                            for (j = 0; j < message_list[i]["message_sent"].length - 1; j++) {
                                message_list[i]["message_sent"][j] = message_list[i]["message_sent"][j].replace(new RegExp('\r?\n', 'g'), '<br>');
                                var msg_sent = message_list[i]["message_sent"][j].trim();

                                if (msg_sent != "") {
                                    html += campaign_response_text_sent(message_list[i], msg_sent)
                                }
                            }
                            message_list[i]["message_sent"][j] = message_list[i]["message_sent"][j].replace(new RegExp('\r?\n', 'g'), '<br>');
                            msg_sent = message_list[i]["message_sent"][j].trim();
                            if (msg_sent != "") {
                                html += campaign_response_text_sent(message_list[i], msg_sent)
                            }


                        } else {
                            message_list[i]["message_sent"] = message_list[i]["message_sent"].replace(new RegExp('\r?\n', 'g'), '<br>');
                            message_list[i]["message_sent"] = message_list[i]["message_sent"].replace('</li></ul>', '');
                            var msg_sent = message_list[i]["message_sent"].trim();
                            if (msg_sent != "") {
                                html += campaign_response_text_sent(message_list[i], msg_sent)
                            }


                        }
                        if (message_list[i]["campaign_qr_cta"]['type_of_first_cta_button'] == 'call_us') {
                            sent_callus = message_list[i]["campaign_qr_cta"]['callus_text']
                            if (sent_callus && sent_callus.length > 0) {
                                if (sent_callus.includes('$$$')) {
                                    sent_callus = sent_callus.split('$$$')
                                    for (let cta = 0; cta < sent_callus.length; cta++) {
                                        html += campaign_response_action_button(sent_callus[cta], true)
                                    }
                                } else {
                                    html += campaign_response_action_button(sent_callus, true)
                                }
                            }
                            sent_cta_url = message_list[i]["campaign_qr_cta"]['cta_text']
                            if (sent_cta_url && sent_cta_url.length > 0) {
                                if (sent_cta_url.includes('$$$')) {
                                    sent_cta_url = sent_cta_url.split('$$$')
                                    for (let cta = 0; cta < sent_cta_url.length; cta++) {
                                        html += campaign_response_action_button(sent_cta_url[cta], false)
                                    }
                                } else {
                                    html += campaign_response_action_button(sent_cta_url, false)
                                }
                            }
                        } else {
                            sent_cta_url = message_list[i]["campaign_qr_cta"]['cta_text']
                            if (sent_cta_url && sent_cta_url.length > 0) {
                                if (sent_cta_url.includes('$$$')) {
                                    sent_cta_url = sent_cta_url.split('$$$')
                                    for (let cta = 0; cta < sent_cta_url.length; cta++) {
                                        html += campaign_response_action_button(sent_cta_url[cta], false)
                                    }
                                } else {
                                    html += campaign_response_action_button(sent_cta_url, false)
                                }
                            }
                            sent_callus = message_list[i]["campaign_qr_cta"]['callus_text']
                            if (sent_callus && sent_callus.length > 0) {
                                if (sent_callus.includes('$$$')) {
                                    sent_callus = sent_callus.split('$$$')
                                    for (let cta = 0; cta < sent_callus.length; cta++) {
                                        html += campaign_response_action_button(sent_callus[cta], true)
                                    }
                                } else {
                                    html += campaign_response_action_button(sent_callus, true)
                                }
                            }
                        }
                        sent_quick_reply = message_list[i]["campaign_qr_cta"]['quick_reply']
                        if (sent_quick_reply && sent_quick_reply.length > 0) {
                            for (let qr = 0; qr < sent_quick_reply.length; qr++){
                                let quick_reply_button = sent_quick_reply[qr]
                                if (message_list[i + 1] && message_list[i + 1]["message_received"] == quick_reply_button) {
                                    html += campaign_response_QR_sent(quick_reply_button, true)
                                } else {
                                    html += campaign_response_QR_sent(quick_reply_button, false)
                                }
                            }
                        }
                    }
                    else {
                        for (order = 0; order < order_of_response.length; order++) {

                            let bot_response_order = order_of_response[order].trim()
                            let widget_type = message_list[i]['widget_type']


                            //range_slider
                            if (bot_response_order == 'range_slider') {
                                if (widget_type == 'is_range_slider') {
                                    if (message_list[i]["widget_data"] == 'multi-range-slider') {
                                        html += bot_response_multiple_range_slider(message_list[i]["widget_language_tuned_text"])
                                    } else if (message_list[i]["widget_data"] == 'single-range-slider') {
                                        html += bot_response_single_range_slider(message_list[i]["widget_language_tuned_text"])
                                    }

                                }
                            }

                            //custom form
                            if (bot_response_order == 'form') {
                                if (widget_type == 'is_create_form_allowed') {
                                    html += '                        <div class="easychat-user-history-form-container-div">'
                                    html += '                            <div class="user-history-form-div">'
                                    html += '                                <h5 class="user-history-form-title">'
                                    html += message_list[i]["widget_data"][0]
                                    html += '                                </h5>'
                                    html += '                                <div class=" user-history-form-field">'

                                    let custom_form = JSON.parse(message_list[i]["widget_data"][1])

                                    for (form = 0; form < custom_form.length; form++) {
                                        html += '<div class="input-field-custom user-history-text-field">'
                                        custom_form_data = bot_response_custom_form_widget(custom_form[form]['input_type'], custom_form[form]['placeholder_or_options'], custom_form[form]['label_name'], custom_form[form]['optional'], custom_form[form], country_code, max_file_size_allowed, message_list[i]["widget_language_tuned_text"])
                                        country_code = custom_form_data[0]
                                        html += custom_form_data[1]
                                        html += '</div>'
                                    }
                                    html += '</div></div></div>'

                                }
                            }


                            //phone_widget
                            if (bot_response_order == 'phone_number') {
                                if (widget_type == 'is_phone_widget_enabled') {
                                    html += bot_response_phone_number(country_code, message_list[i]["widget_language_tuned_text"])
                                    country_code.push(message_list[i]["widget_data"])
                                }
                            }

                            //checkbox_button
                            if (bot_response_order == 'checkbox') {
                                if (widget_type == 'is_check_box') {
                                    html += bot_response_sent_check_box(message_list[i]["widget_data"])
                                }
                            }

                            //radio_button
                            if (bot_response_order == 'radio_button') {
                                if (widget_type == 'is_radio_button') {
                                    html += bot_response_sent_radio_button(message_list[i]["widget_data"])
                                }
                            }

                            //attachment widget
                            if (bot_response_order == 'file_attach') {
                                if (widget_type == 'is_attachment_required') {
                                    html += bot_response_attachment(message_list[i]["widget_data"], max_file_size_allowed, message_list[i]["widget_language_tuned_text"])
                                }
                            }

                            //drop_down
                            if (bot_response_order == 'drop_down') {
                                if (widget_type == 'is_drop_down') {
                                    html += bot_response_sent_drop_down(message_list[i]["widget_data"], message_list[i]["widget_language_tuned_text"])
                                }
                            }

                            //sending table
                            if (bot_response_order == 'table') {
                                let sent_table = message_list[i]["sent_table"]
                                if (sent_table && sent_table.length > 0) {
                                    html += bot_response_sent_table(sent_table)
                                }
                            }

                            //sending video recorder
                            if (bot_response_order == 'video_record') {
                                if (widget_type == 'is_video_recorder_allowed') {
                                    html += bot_response_video_recording(message_list[i]["widget_language_tuned_text"])
                                }
                            }

                            //sending calendar time
                            if (bot_response_order == 'calendar_picker' || bot_response_order == 'time_picker') {
                                if (!sent_calendar_time) {
                                    sent_calendar_time = true
                                    html += bot_response_calendar(widget_type, message_list[i]["widget_language_tuned_text"])
                                }
                            }

                            // sending card
                            if (bot_response_order == 'link_cards') {
                                let sent_card = message_list[i]["sent_card"]
                                if (sent_card && sent_card.length > 0) {

                                    let card_html = '<div class="easychat-user-history-card-slider-div slick-card-slider">'
                                    for (card = 0; card < sent_card.length; card++) {

                                        sending_card = sent_card[card]
                                        card_title = sending_card['title']
                                        card_text = sending_card['content']
                                        card_attach = sending_card['img_url']
                                        card_html += bot_response_sent_cards(card_title, card_text, card_attach)

                                    }
                                    card_html += '</div>'
                                    html += card_html
                                }
                            }

                            // sending image
                            if (bot_response_order == 'image') {
                                let sent_image = message_list[i]["sent_image"]

                                if (sent_image && sent_image.length > 0) {
                                    for (img = 0; img < sent_image.length; img++) {
                                        sending_image = sent_image[img]
                                        html += bot_response_sent_image(sending_image)
                                    }
                                }
                            }

                            // sending video
                            if (bot_response_order == 'video') {
                                let sent_video = message_list[i]["sent_video"]
                                if (sent_video && sent_video.length > 0) {
                                    for (vid = 0; vid < sent_video.length; vid++) {
                                        sending_video = sent_video[vid]
                                        html += get_video_sent_html(sending_video, message_list[i]["widget_language_tuned_text"])
                                    }

                                }
                            }

                            //choices
                            if (bot_response_order == 'quick_recommendations') {
                                html += '<div class="easychat-recommendation-selected-div">'

                                if (message_list[i]["message_recommendation"] != "[]" && message_list[i]["message_recommendation"] != "") {

                                    let message_recommendation = []
                                    try {
                                        message_recommendation = JSON.parse(message_list[i]["message_recommendation"]);
                                    } catch (err) {
                                        message_recommendation = [];
                                    }

                                    for (var j = 0; j < message_recommendation.length; j++) {
                                        if (message_recommendation[j]) {
                                            if((typeof message_recommendation[j] === "string")) {
                                                if (message_list[i + 1] && message_list[i + 1]["message_received"] == message_recommendation[j]) {
                                                    html += bot_response_recommendation_sent_html(message_recommendation[j], true);
                                                } else {
                                                    html += bot_response_recommendation_sent_html(message_recommendation[j], false);
                                                }
                                            } else if((typeof message_recommendation[j] === "object")) {
                                                if(message_recommendation[j] instanceof Array) {
                                                    if (message_list[i + 1] && message_list[i + 1]["message_received"] == message_recommendation[j][j].name) {
                                                        html += bot_response_recommendation_sent_html(message_recommendation[j][j].name, true);
                                                    } else {
                                                        html += bot_response_recommendation_sent_html(message_recommendation[j][j].name, false);
                                                    }
                                                } else {
                                                    if (message_list[i + 1] && message_list[i + 1]["message_received"] == message_recommendation[j].name) {
                                                        html += bot_response_recommendation_sent_html(message_recommendation[j].name, true);
                                                    } else {
                                                        html += bot_response_recommendation_sent_html(message_recommendation[j].name, false);
                                                    }
                                                }
                                            } else{
                                                if (message_list[i + 1] && message_list[i + 1]["message_received"] == message_recommendation[j]) {
                                                    html += bot_response_recommendation_sent_html(message_recommendation[j], true);
                                                } else {
                                                    html += bot_response_recommendation_sent_html(message_recommendation[j], false);
                                                }
                                            }
                                        }
                                        else {
                                            if (message_list[i + 1] && message_list[i + 1]["message_received"] == message_recommendation[j]) {
                                                html += bot_response_recommendation_sent_html(message_recommendation[j], true);
                                            } else {
                                                html += bot_response_recommendation_sent_html(message_recommendation[j], false);
                                            }
                                        }
                                    }
                                }

                                if (message_list[i]["message_choices"] != "") {
                                    let message_choices = message_list[i]["message_choices"].split(",")
                                    for (var k = 0; k < message_choices.length; k++) {
                                        if (message_choices[k].includes("$$$")) {
                                            message_choice = message_choices[k].replace("$$$", " ")
                                            if (message_list[i + 1] && message_list[i + 1]["message_received"] == message_choice) {
                                                html += bot_response_recommendation_sent_html(message_choice, true)
                                            } else {
                                                html += bot_response_recommendation_sent_html(message_choice, false)
                                            }
                                        }
                                        else {
                                            if (message_list[i + 1] && message_list[i + 1]["message_received"] == message_choices[k]) {
                                                html += bot_response_recommendation_sent_html(message_choices[k], true)
                                            } else {
                                                html += bot_response_recommendation_sent_html(message_choices[k], false)
                                            }
                                        }
                                    }
                                }
                                html += '</div>'
                            }

                            // sending message
                            if (bot_response_order == 'text') {
                                let msg_sent = ""
                                if (message_list[i]["message_sent"].includes("$$$")) {
                                    message_list[i]["message_sent"] = message_list[i]["message_sent"].split("$$$")
                                    var j;
                                    for (j = 0; j < message_list[i]["message_sent"].length - 1; j++) {
                                        message_list[i]["message_sent"][j] = message_list[i]["message_sent"][j].replace(new RegExp('\r?\n', 'g'), '<br>');
                                        msg_sent = message_list[i]["message_sent"][j].trim();

                                        if (msg_sent != "") {
                                            html += bot_response_text_sent(message_list[i], msg_sent)
                                        }
                                    }
                                    message_list[i]["message_sent"][j] = message_list[i]["message_sent"][j].replace(new RegExp('\r?\n', 'g'), '<br>');
                                    msg_sent = message_list[i]["message_sent"][j].trim();
                                    if (msg_sent != "") {
                                        html += bot_response_text_sent(message_list[i], msg_sent)
                                    }


                                } else {
                                    message_list[i]["message_sent"] = message_list[i]["message_sent"].replace(new RegExp('\r?\n', 'g'), '<br>');
                                    message_list[i]["message_sent"] = message_list[i]["message_sent"].replace('</li></ul>', '');
                                    msg_sent = message_list[i]["message_sent"].trim();
                                    if (msg_sent != "") {
                                        html += bot_response_text_sent(message_list[i], msg_sent)
                                    }


                                }

                                html += '</li>'
                            }
                        }
                        html += '</li>'
                    }

                    html += whatsapp_menu_sections_html;
                    html += '</div></div></div>'
                    // }
                }
                $('#session_id_dropdown_selected_text').text(session_ids_appended[0])
                $(".easychat-user-message-history-session-ids-item").click(function () {
                    let session_id = $(this).children().text()
                    $(".user-dropdown-session-selected-text").text(session_id);
                    $("#user_chat_session_id_drop").toggleClass("user-chat-dropdown-open")
                    $("#load_user_messages").scrollTo('#' + session_id, 1000);
                });
                // html += '</ul>'
                document.getElementById("load_user_messages").innerHTML = html;
                initializing_phone_dropdown(country_code);
                initializing_card_slider();


                document.querySelectorAll(".easychat-query-add-intent-wrapper").forEach(function (element) {
                    element.addEventListener("click", function (e) {
                        document.querySelectorAll(".selected-misdashboard").forEach(function (element) {
                            element.parentNode.style.display = "inline-block";
                        });
                        $(".easychat-user-custom-checkbox-div").show();
                        // document.getElementById("close-selected-mis").style.display = "block";
                        $('#chat-frame .content .messages ul li:last-child').css('padding-bottom', '70px')
                        $(".easychat-query-add-intent-wrapper").css('visibility', 'hidden')
                        $(".user-history-clearall-btn").css("visibility", "visible");
                    });
                });
                if (scroll_to_session_id) {
                    $(".user-dropdown-session-selected-text").text(scroll_to_session_id);
                    setTimeout(function () {
                        $("#load_user_messages").scrollTo('#' + scroll_to_session_id, 1000);
                    }, 500)
                }
            } else {
                M.toast({
                    "html": "Some error occured"
                }, 2000);
            }
        },
        error: function (jqXHR, exception) {
            console.log(jqXHR, exception);
        }
    });
}

$('#select-show-bot-intent').select2().on('select2:open', function (e) {
    $('.select2-search__field').attr('placeholder', 'Search Intent');
});

$(document).ready(function () {
    setTimeout(function () {
        $('.modal').removeAttr('tabindex')
    }, 500)
    if ($("#easychat-build-bot-toast-div").css('display') == 'flex') {
        $(".easychat-user-chat-contacts-list-wrapper").addClass("user-history-change-div-height");
        $(".easychat-user-chat-history-message-container").addClass("user-history-change-div-height");
    }
});

$(".easychat-user-chat-contacts-list-item").click(function () {
    $(".easychat-user-chat-contacts-list-item").removeClass("easychat-user-active-chat");
    $(this).addClass("easychat-user-active-chat");
});

function user_session_dropdown_search() {
    var input, filter, search_value, text_value;
    input = document.getElementById("session_id_drop_search");
    filter = input.value.toUpperCase();
    search_value = document.querySelectorAll('.easychat-user-message-history-session-ids-item span');
    let count = 0
    for (let i = 0; i < search_value.length; i++) {

        text_value = search_value[i].textContent || search_value[i].innerText;
        if (text_value.toUpperCase().indexOf(filter) > -1) {
            search_value[i].parentElement.style.display = "";
            count++;
        } else {
            search_value[i].parentElement.style.display = "none";
        }
    }
    if (count == 0) {
        document.getElementById('session_drop_nodata_found').style.display = "flex";
    } else {
        document.getElementById('session_drop_nodata_found').style.display = "none";
    }
}

$("#easychat-history-global-searchbar-btn").click(function () {
    $(".easychat-history-global-searchbar-container").addClass("active-user-global-search");
    $(this).hide();
    $(".user-search-cross-icon").show();
    $('#user_history_global_search').focus()
});

$(".user-search-cross-icon").click(function () {
    $(".easychat-history-global-searchbar-container").removeClass("active-user-global-search");
    $("#easychat-history-global-searchbar-btn").show();
    reset_search_results();
    $('#user_history_global_search').val('')
});

$("#call_recording_btn_message_history").click(function () {
    $(".easychat-history-global-searchbar-container").removeClass("active-user-global-search");
    $("#easychat-history-global-searchbar-btn").show();
    $("#easychat-history-global-searchbar-btn").css("pointerEvents", "none");
    $(".easychat-message-history-recording-wrapper").show();
    $(this).hide();
});

$(".audio-player-cross-btn").click(function () {
    $("#easychat-history-global-searchbar-btn").css("pointerEvents", "auto");
    $("#call_recording_btn_message_history").css("display", "flex");
    $(".easychat-message-history-recording-wrapper").hide();
});

$('#user_history_global_search').on('keyup', function (e) {
    if ($('#user_history_global_search').val() == '') {
        reset_search_results();
    }
})

$('#user_history_global_search').on('keydown', function (e) {
    if (e.keyCode !== 13) return;
    e.preventDefault();
    var search_box_text = $('#user_history_global_search');
    var replaced_text = '';
    var query = new RegExp("(" + search_box_text.val() + ")", "gim");
    if (search_box_text.val() != '') {
        $('.search-div').each(function () {
            replaced_text = $(this).html().replace(/(<mark.*?>|<\/mark>)/igm, "");
            $(this).html(replaced_text);
            newtext = $(this).html().replace(query, "<mark>$1</mark>");
            // newtext = newtext.replace(/(<mark [^<>]*)((<[^>]+>)+)([^<>]*>[^<>]*)((<[^>]+>)+)([^<>]*<\/mark>)/, "</mark><mark>");
            $(this).html(newtext);
        });
        $('mark').each(function (index) {
            $(this).attr("id", "result_" + (index + 1))
        })
        $('#search_results_track').show()
        $('.user-search-up-down-arrow-wrapper').css({ 'pointer-events': 'auto', 'opacity': '1' })
        $('#current_search_id').text('1')
        $('#total_search_result').text($('mark').length)
        $("#load_user_messages").scrollTo('#result_1', 250);
        $('#result_1').css('background-color', 'orange')
        if (!$('mark').length) {
            $('#current_search_id, #total_search_result').text('0')
            $('.user-search-up-down-arrow-wrapper').css({ 'pointer-events': 'none', 'opacity': '0.5' })
        }
    } else {
        reset_search_results();
    }
    last_scroll_id = 1
});

$(document).on("change", ".selected-misdashboard", function (e) {
    if ($(".selected-misdashboard:checked").length) {
        $('#user_history_add_intent_btn').css("visibility", "visible");
    } else {
        $('#user_history_add_intent_btn').css("visibility", "hidden");
    }
});

$("#user_chat_session_id_drop .user-dropdown-session-selected-btn").click(function () {
    $("#user_chat_session_id_drop").toggleClass("user-chat-dropdown-open")
});

$(document).mouseup(function (e) {
    const container = $(".easychat-user-message-history-session-id-dropdown-wrapper");
    if (container.length != 0 && !container.is(e.target) && container.has(e.target).length === 0) {
        if (container.hasClass('user-chat-dropdown-open')) {
            $(".user-dropdown-session-selected-btn").trigger('click');
        }
    }
});

jQuery.fn.scrollTo = function (elem, speed) {
    if (!$(elem).length) return;
    $(this).animate({
        scrollTop: $(this).scrollTop() - $(this).offset().top + $(elem).offset().top
    }, speed == undefined ? 1000 : speed);
    return this;
};

function get_message_sent_html(message_list, message) {
    message = get_masked_message(message);
    let html = '<div class="easychat-query-reply-message-wrapper">'
    html += '<div class="easychat-query-reply-message-div">'
    html += '<div class="easychat-query-message-icon">'
    html += '<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">' +
        '<path d="M8.15332 10.3333H22.7249C23.2631 10.3333 24.4243 10.8499 24.7633 12.9166V22.0592C24.7835 22.8866 24.279 24.5416 22.0993 24.5416H13.5622L9.16243 27.1249" stroke="#2D2D2D" stroke-width="1.29167"/>' +
        '<path d="M9.18262 27.1249L8.87988 24.5416C8.07259 24.3263 6.45801 23.5083 6.45801 21.9583V12.9166C6.55219 12.0555 6.7002 10.3333 8.39551 10.3333" stroke="#2D2D2D" stroke-width="1.29167" stroke-linecap="round"/>' +
        '<path d="M5.16667 20.6667V15.1367C4.13333 15.1367 3.875 15.8095 3.875 16.1458V19.0924C3.875 20.4164 4.73611 20.6936 5.16667 20.6667Z" stroke="#2D2D2D" stroke-width="0.645833" stroke-linecap="round"/>' +
        '<path d="M25.8535 15.1338L25.8129 20.6636C26.8462 20.6712 27.1094 20.0004 27.1119 19.664L27.1336 16.7175C27.1433 15.3936 26.2843 15.1101 25.8535 15.1338Z" stroke="#2D2D2D" stroke-width="0.645833" stroke-linecap="round"/>' +
        '<circle cx="10.9795" cy="16.1458" r="1.29167" stroke="black" stroke-width="1.29167"/>' +
        '<circle cx="10.9795" cy="16.1458" r="1.29167" stroke="#2D2D2D" stroke-width="1.29167"/>' +
        '<circle cx="20.0205" cy="16.1458" r="1.29167" stroke="#2D2D2D" stroke-width="1.29167"/>' +
        '<path d="M13.1592 19.375C14.0203 20.2361 16.1704 21.4417 17.8818 19.375" stroke="#2D2D2D" stroke-width="0.645833" stroke-linecap="round"/>' +
        '<circle cx="15.5003" cy="5.16658" r="1.9375" stroke="#2D2D2D" stroke-width="1.29167"/>' +
        '<path d="M15.5 7.75V9.04167" stroke="#2D2D2D" stroke-width="0.645833" stroke-linecap="round"/>' +
        '</svg>'
    html += '</div>'
    html += '<div class="easychat-query-reply-message-text-div">'
    html += '<div class="easychat-query-reply-message-text search-div">' + message + '</div>'
    html += '<div class="easychat-query-reply-message-time-div">' + message_list["date_time"] + ' | ' + message_list["channel_name"] + '</div>'
    html += '</div></div></div>'
    return html
}

function initializing_phone_dropdown(country) {
    for (code = 0; code < country.length; code++) {
        var telInput = $("#phone" + code.toString());
        // initialise plugin
        telInput.intlTelInput({
            initialCountry: country[code],
        });
    }
    country = []

}

function initializing_card_slider() {
    $('.slick-card-slider').slick({
        infinite: false,
        slidesToShow: 3,
        slidesToScroll: 1,
        centerMode: false,
        centerPadding: 0,
        prevArrow: '<button class="slide-arrow prev-arrow">&#10094;</button>',
        nextArrow: '<button class="slide-arrow next-arrow">&#10095;</button>',
        responsive: [
            {
              breakpoint: 1400,
              settings: {
                slidesToShow: 2,
              },
              breakpoint: 1100,
              settings: {
                slidesToShow: 2,
              }
            },
            
          ]
            // You can unslick at a given breakpoint now by adding:
            // settings: "unslick"
            // instead of a settings object
        
    });
    $('.slick-pdf-slider').slick({
        dots: false,
        infinite: false,
        speed: 500,
        slidesToShow: 3,
        slidesToScroll: 1,
        autoplay: false,
        autoplaySpeed: 2000,
        arrows: true,
        prevArrow: '<button class="slide-arrow prev-arrow">&#10094;</button>',
        nextArrow: '<button class="slide-arrow next-arrow">&#10095;</button>',
        responsive: [{
        breakpoint: 800,
        settings: {
        slidesToShow: 2,
        slidesToScroll: 1
        }
        },
        {
        breakpoint: 600,
        settings: {
        arrows: false,
        slidesToShow: 1,
        slidesToScroll: 1
        }
        }]
        });
    

}

function bot_response_text_sent(message_list, message) {
    message = get_masked_message(message);
    let html = `<div class="easychat-query-reply-message-text-div">
    <div class="easychat-query-reply-message-text search-div"> ${message} </div>
    <div class="easychat-query-reply-message-time-div">
    ${message_list["date_time"]} | ${message_list["channel_name"]} 
    </div></div>`
    return html
}

function get_image_sent_html(attached_file_path) {
    return `<div class="easychat-slider-wrapper easychat-user-history-image-div">
            <div class="easychat-query-reply-message-text-div">
            <div class="image-slider-wrapper-div">
            <div class="slideshow-container">
            <div class="mySlides fade">
            <a href="${attached_file_path}" target="_blank">
            <img src="${attached_file_path}" style="cursor:pointer;width: 100%;height: 180px;">
            </a></div></div></div></div></div>`
}

function single_calendar(widget_language_tuned_text) {
    return `<div class="easychat-user-history-calendar-div">
            <span class="date-span single-date">${widget_language_tuned_text["label_add"]} ${widget_language_tuned_text["label_date"]}</span>
            </div>`
}
function multi_calendar(widget_language_tuned_text) {
    return `<div class="easychat-user-history-calendar-div">
                <span class="date-span">${widget_language_tuned_text["label_from"]} ${widget_language_tuned_text["label_date"]}</span>
                <span class="date-span">${widget_language_tuned_text["label_to"]} ${widget_language_tuned_text["label_date"]}</span>
            </div>`


}
function single_time(widget_language_tuned_text) {
    return `<div class="easychat-user-history-calendar-div">
        <span class="date-span single-date">${widget_language_tuned_text["label_add"]} ${widget_language_tuned_text["label_time"]}</span>
        </div>`
}
function multi_time(widget_language_tuned_text) {
    let html = '<div class="easychat-user-history-calendar-div">'
    html += '                            <span class="date-span">' + widget_language_tuned_text["label_from"] + ' ' + widget_language_tuned_text["label_time"] + '</span>'
    html += '                            <span class="date-span">' + widget_language_tuned_text["label_to"] + ' ' + widget_language_tuned_text["label_time"] + '</span>'
    html += '                        </div>'
    return html
}
function single_time_calendar(widget_language_tuned_text) {
    let html = '<div class="easychat-user-history-calendar-div">'
    html += ' <span class="date-span">' + widget_language_tuned_text["label_date"] + '</span>'
    html += '<span class="date-span">' + widget_language_tuned_text["label_time"] + '</span>'
    html += '</div>'
    return html
}
function single_time_multi_calendar(widget_language_tuned_text){
    return `<div class="easychat-user-history-calendar-div" style="display:flex;flex-direction: column;">
                <span class="date-span single-date">${widget_language_tuned_text["label_add"]} ${widget_language_tuned_text["label_time"]}</span>
                <div style=" display: flex;width: 100%;justify-content: center;padding-top: 20px;
                ">
                <span class="date-span">${widget_language_tuned_text["label_from"]} ${widget_language_tuned_text["label_time"]}</span>
                <span class="date-span">${widget_language_tuned_text["label_to"]} ${widget_language_tuned_text["label_time"]}</span>
                </div>
            </div>`
}
function multi_time_single_calendar(widget_language_tuned_text){
    return `<div class="easychat-user-history-calendar-div" style="display:flex;flex-direction: column;">
                <span class="date-span single-date">${widget_language_tuned_text["label_add"]} ${widget_language_tuned_text["label_time"]}</span>
                <div style=" display: flex;width: 100%;justify-content: center;padding-top: 20px;
                ">
                <span class="date-span">${widget_language_tuned_text["label_from"]} ${widget_language_tuned_text["label_date"]}</span>
                <span class="date-span">${widget_language_tuned_text["label_to"]} ${widget_language_tuned_text["label_date"]}</span>
                </div>
            </div>`
}
function multi_calendar_time(widget_language_tuned_text) {
    return `<div class="easychat-user-history-calendar-div custom-date-value-div">
                <div class="custom-date-value-from-to-div">
                    <span>${widget_language_tuned_text["label_from"]}</span>
                <span class="date-span">${widget_language_tuned_text["label_date"]}</span>
                <span class="date-span">${widget_language_tuned_text["label_time"]}</span>
                </div>
                <div class="custom-date-value-from-to-div">
                <span>${widget_language_tuned_text["label_to"]}</span>
                <span class="date-span">${widget_language_tuned_text["label_date"]}</span>
                <span class="date-span">${widget_language_tuned_text["label_time"]}</span>
            </div></div>`
}
function bot_response_calendar(widget_type, widget_language_tuned_text) {
    let html = ''
    if (widget_type == 'single_time') {
        html += single_time(widget_language_tuned_text)
    } else if (widget_type == 'multi_time') {
        html += multi_time(widget_language_tuned_text)
    } else if (widget_type == 'single_date') {
        html += single_calendar(widget_language_tuned_text)
    } else if (widget_type == 'multi_date') {
        html += multi_calendar(widget_language_tuned_text)
    } else if (widget_type == 'multi_date_time') {
        html += multi_calendar_time(widget_language_tuned_text)
    } else if (widget_type == 'single_date_time') {
        html += single_time_calendar(widget_language_tuned_text)
    } else if (widget_type == 'single_time_multi_date') {
        html += single_time_multi_calendar(widget_language_tuned_text)
    } else if (widget_type == 'single_date_multi_time') {
        html += multi_time_single_calendar(widget_language_tuned_text)
    }
    return html
}

function bot_response_attachment(file_types, max_file_size_allowed, widget_language_tuned_text) {
    let html = ''
    html += '                       <div class="easychat-user-history-dragdrop-div">'
    html += '                           <div class="user-history-dragdrop-upload-div">'
    html += '                            <svg width="50" height="49" viewBox="0 0 50 49" fill="none" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">'
    html += '                                <rect x="0.760986" width="48.478" height="48.478" fill="url(#pattern0)"/>'
    html += '                                <defs>'
    html += '                                <pattern id="pattern0" patternContentUnits="objectBoundingBox" width="1" height="1">'
    html += '                                <use xlink:href="#image0_54_9678" transform="scale(0.00195312)"/>'
    html += '                                </pattern>'
    html += '<image id="image0_54_9678" width="512" height="512" xlink:href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAACAASURBVHic7d1rkFxnfefx39Onu6fnKll32VZsXWxJlrls4uDFgC3J9tpJ1oQFQgi7IUC2sikW2M0LMMtShMAmRZZsKLLspWIo2HJIsWQrgMOaYCyNjcFeiEmBQdaMJFsGgdHV1mVGM9N9+jz74misizWjnpnT5znPeb6fqi4blzX9p7vdz3fO1QiltP+wXWVN+xVJYjcaYzZK9lpJKyX1n3ksdjshyiqxkqyUSLJWShIpPvNoJ1IrkVrt9O8vpmJsksjERpqSNUcT2UkjHZP0nGSOGdljidWh'
    html += 'SsUcUDv5sWztmW1bzMEc/y8CpWBcD4Bs7N1rezTYvrNS0e2ydpuMrnM9EzCbdiJNxWcfzViy8/9xk5KekbTLGP3QJuZHkY2fOLS55+k3GdPOaGSgVAgAz+0/2PynSVR5qxL7mzJa4noeYL4SK0220sfp1sxbCObotJG+Z6XHJPNoqxo9dscGcziTnwx4jgDwkLXW7D/avsvKfkBWN7qeB8iclSZiabwpnZ5a0JaBFzNmnxINS/q6aUQ7tq01x7P88YAvCADPPH0kfq219j9JeonrWYA8JFY63ZTGptJdBRmLJX1H0tcTJV+5bVPPE5k/A1BQBIAnRo/aK6pJ/AlJv+F6FsCVqVg6MSlNNLv1DPYZydxnjP5m67XVbxtjMt34ABQJAVBw1lrz9JHWeyTzJ5L6XM8DFMFULJ2YkCZaXXwSY/ZJ9t4oqn72lg3mQBefCXCCACiwp56zixTH94jf+oGLaral50+nBw52USLpG1bmM1NRdN+vXmOmuvpsQE4IgILaf7j58sToy7LmKtezAEU31pSOn87szIHZHJXRX1bb1U/dfJ35edefDegiAqCA9h5pba1YfVnSItezAL5IrHR8QhqbzPisgYtrGukrSuyfb7uu/v+6/3RA9giAgtl3KP4Xxti/ltRwPQvgo6lYOjqWXnkwD0YatlZ/tH1z7eF8nhHIBgFQIE8diX9N1n5ZUtX1LIDPrJWOjqenD+bo2zL6w+0baztyfVZgngiAgth/sHljUjE7lF6nH0AGTk1Jz4/nskvgXDsTqw/etrn2WL5PC8wNAVAATx+Z3GiT6FEu5Qtkr9WWDp/Kb5fAGdZa+79la++/9Trz41yfGegQAeDY/v22kfTHj0l6uetZgLJqJ9LhsfSGQzlrSvqf7Vr1Q7evNydyf3ZgFhXXA4Su3d/+r2LxB7oqqkgrB6VGLfenrkt6T9SKR4ZH4zfn/uzALNgC4NDTh+M3Wtm/cT0HEApHBwe+wEhfk43fuW1z7zNuJgDOIgAcGTliB2s23i3pCtezACGxSg8MPOXuen7jMvrQ0Wurn3yTMW1nUyB47AJwpGbjj4jFH8idkbSkXxqoOxuhX1b/Zdlo/OjDT05e42wKBI8tAA7s/fnUlkpU+b443x9wx6YHBnb1hkKXdtrIfmDbpvonnU6BIBEADjx1qPl5GfMW13MAobNWOnjKydkB5zFWX1Kl+nvbNpqjbidBSAiAnO05NLkuMtGo+O0fKIS2lQ6elGL3e+N/ahL7G9xbAHnhGICcVVW9Wyz+QGFERloxIFXc/zp0pa2YR4ZHWne7HgRhcP+RD8jBg7Z/vBIflDTgehYA5xubko6Nu55imv3r1lTt9+54mSnMRCgftgDkaMy03yAWf6CQBnqkfndnBlzAvKXWE3/74X12jetJUF4EQI5Mxf626xkAzGxJv1SLXE/xgpe14/g7wyPNG1wPgnIiAHJy4IRdIqttrucAMLOKkZYNqEg7R1dbmeEdu+O7XA+C8iEActKcbG+VVJzfLQBcVD2ShnpcT3GeAWPsl4ZHm//W9SAoFwIgJ9bw2z/gi0W9UrViXY9xrsha86kdI62PuR4E5UEA5MQYSwAAnqgY6bK+4uwHmGaku3eOtP7UWlu84eAdAiAHu6yty2qj6zkAdK6vLvXmf/vgTrzvodH2f/+wtXx/Y0H4AOWg/lxzg7j4D+CdJX0q0gGBL7Cyv3/zaPseIgALwYcnB5U42uR6BgBzV42k/mJuBZBk3/GaPe3PEAGYLz44OTCy61zPAGB+FvUWciOAJMlY+zYiAPPFhyYHidFi1zMAmJ9alB4PUFREAOaLD0wODJf/Bbw21Ot6gtkRAZgPPiy5MIOuJwAwf/WosGcEvMBY+7abR9ufJgLQKT4oebBJwX9/AHApgw3XE3TCvp0tAegUHxIA6EBvNb1AUNGxOwCd4gMCAJ0wRbpd8OyIAHSCDwcAdKjfi90AKSIAl8IHAwA61BOlpwX6ggjAbPhQAMAcFPmaABfD2QGYCR8IAJiDhpd39eDsALwYHwYAmIOeWnEvDTwbdgfgQnwQAGAOjNII8BERgHPxIQCAOfJzN0CKCMA0H7dk5W541C6zNt5orNlgK0m/'
    html += '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'
    html += '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'
    html += 'JCm2lKr7Xo6FE3FpLeOHeiRFvdJqwZnupc8fEcAAIGoV6U1l6UPAIg8OrTeo1EBACg2n7YAEAAAAGTEp0s3EwAAAGSkQgAAABCeyEg1Ky/ODSIAAADIipGm2mq6HqMTBAAAABnqqRAAAAAEpxERAAAABKdWU+x6hk4QAAAABIgAAAAgQAQAAAABIgAAAAgQAQAAQIAIAAAAAkQAAAAQIAIAAIAAEQAAAASIAAAAIEAEAAAAASIAAAAIEAEAAECACAAAAAJEAAAAEKCq6wEA+C9JpGOnpaNj0qlJaTKWmrEUVaR6JA00pMW90opBqbfmeloAEgEAYAEOnpT2HZUOPC/F7c7+zNIBae0SacNyqRZ1dz4AMyMAAMzZwZPS9w5Iz43P/c8eG0sfP/iZtGmVdP1qqcrOSCB3BACAjrXa0neekfYfy+Zn/fBn0tNHpZvWSquGFv4zAXSO7gbQkeMT0ld/lM3if67xKenB0TQGAOSHLQAALunImLRzT3pgXzdYK33/Z9J4S7rxKsmY7jwPgLPYAgBgVkfG0t/Qu7X4n2vvYelbT6dBAKC7CAAAM5pe/Ds9wj8LzxwjAoA8EAAALsrF4j+NCAC6jwAA8CIuF/9pRADQXQQAgPMUYfGfRgQA3UMAAHhBkRb/aUQA0B0EAABJxVz8pxEBQPYIAACFXvynEQFAtggAIHA+LP7TiAAgOwQAEDCfFv9pRACQDQIACJSPi/80IgBYOAIACJDPi/80IgBYGAIACEwZFv9pRAAwfwQAEJAyLf7TiABgfggAIBBlXPynEQHA3BEAQADKvPhPIwKAuSEAgJILYfGfRgQAnSMAgBILafGfRgQAnSEAgJIKcfGfRgQAl0YAACUU8uI/jQgAZkcAACXD4n8WEQDMjAAASoTF/8WIAODiCACgJFj8Z0YEAC9GAAAlwOJ/aUQAcD4CAPAci3/niADgLAIA8BiL/9wRAUCKAAA8xeI/f0QAQAAAXmLxXzgiAKEjAADPsPhnhwhAyAgAwCMs/tkjAhAqAgDwBIt/9xABCBEBAHiAxb/7iACEhgAACo7FPz9EAEJCAAAFxuKfPyIAoSAAgIJi8XeHCEAICACggFj83SMCUHYEAFAwLP7FQQSgzAgAoEBY/IuHCEBZEQBAQbD4FxcRgDIiAIACYPEvPiIAZUMAAI6x+PuDCECZEACAQyz+/iECUBYEAOAIi7+/iACUAQEAOMDi7z8iAL4jAICcsfiXBxEAnxEAQI5Y/MuHCICvCAAgJyz+5UUEwEcEAJADFv/yIwLgGwIA6DIW/3AQAfAJAQB0EYt/eIgA+IIAALqExT9cRAB8QAAAXcDiDyIARUcAABlj8cc0IgBFRgAAGWLxx4WIABQVAQBk5PiEtIPFHxfxzDHp8Z+4ngI4HwEAZKBtpYf2Si0Wf8xg5JD0k+ddTwGcRQAAGdhzSDo16XoKFN33fsKuABQHAQBkYO8R1xPAB2NT0sFTrqcAUgQAsEBTsXRiwvUU8MWhk64nAFIEALBA41OuJ4BP+LygKAgAAMiTcT0AkCIAgAUa6HE9AXzSz+cFBUEAAAtUr0qLel1PAV+sGHA9AZAiAIAMrF/'
    html += 'megL4oK9HWj3kegogRQAAGdi4Quqru54CRfdPrpAMxwCgIAgAIAPVSHr1OqnCf1GYwdVLpXVsKUKB8HUFZGTlkHTLhjQGgHNdvVR61VrXUwDnIwCADF25WLrreukXLmNTL9IzRF61Xnr1erYOoXiqrgcAymagR7rlGul0M73s66lJqZ109zmfPy09e6K7z1EGPVVpw/LuP09fTVo6IC3rJwRRXAQA0CV9dWnd0nyea98RAqATjZr0i2tcTwEUAxulAAAIEAEAAECACAAAAAJEAAAAECACAACAABEAAAAEiAAAACBABAAAAAEiAAAACBABAABAgAgAAAACRAAAABAgAgAAgAARAAAABIgAAAAgQAQAAAABIgAAAAgQAQAAQIAIAAAAAkQAAAAQIAIAAIAAEQAAAASIAAAAIEAEAAAAASIAAAAIEAEAAECACAAAAAJEAAAAECACAACAABEAAAAEiAAAACBABAAAAAEiAAAACBABAABAgAgAAAACRAAAABAgAgAAgAARAAAABIgAAAAgQAQAAAABIgAAAAgQAQAAQIAIAAAAAkQAAAAQIAIAAIAAEQAAAASIAAAAIEAEAAAAASIAAAAIEAEAAECACAAAAAJEAAAAECACAACAABEAAAAEiAAAACBABAAAAAEiAAAACBABAABAgAgAAAACRAAAABAgAgAAgAARAAAABIgAAAAgQAQAAAABIgAAAAgQAQAAQIAIAAAAAkQAAAAQIAIAAIAAEQAAAASIAAAAIEAEAAAAASIAAAAIEAEAAECACAAAAAJEAAAAECACAACAABEAAAAEiAAAACBABAAAAAEiAAAACBABAABAgAgAAAACRAAAABAgAgAAgAARAAAABIgAAAAgQAQAAAABIgAAAAgQAQAAQIAIAAAAAkQAAAAQIAIAAIAAEQAAAASIAAAAIEAEAAAAASIAAAAIEAEAAECACAAAAAJEAAAAECACAACAABEAAAAEiAAAACBABAAAAAEiAAAACBABAABAgAgAAAACRAAAJVAxrifwA68TcBYBAJRAo+Z6Aj80qq4nAIqDAABKYKjhegI/DPW6ngAoDgIAKIGBHmkxi9slrbnM9QRAcRAAQElsWe16gmJb0ietGnQ9BVAcBABQEmuXSiuHXE9RTBUj3bhWMhwECLyAAABKwhhp6wZ2BVzIGOmmtdKyfteTAMVCAAAlUq9Kv3JdujUA0kDd6vaN0tplricBioeTYoCSqUbSq9dLm1dK+45Kz56QxpuSta4ny0dPNd3ff9USaf1yw7n/wAwIAKCklg6kD0myklqx03FyEUVSxIIPdIQAAAJglO4eAIBpHAMAAECACAAAAAJEAAAAECACAACAABEAAAAEiAAAACBABAAAAAEiAAAACBABAABAgAgAAAACRAAAABAgAgAAgAARAAAABIgAAAAgQAQAAAABIgAAAAgQAQAAQIAIAAAAAkQAAAAQIAIAAIAAEQAAAASIAAAAIEAEAAAAASIA8mBcDwAAyEucqO16hk4QADlIrOsJAAB5qTV10vUMnSAAckAAAEAw4jVrzITrITpBAOTAEgAAEIox1wN0igDIQZsAAIBQHHQ9QK'
    html += 'cIgBy0vDgcBACwYEYjrkfoFAGQg5gAAIAwWI26HqFTBEAO2gkHAgJAGCwBgPNNxa4nAAB0mzHJo65n6BQBkJPJlusJAADdZKVn1y1vsAUA55tkCwAAlJuxO1yPMBcEQE5acXosAACgnIwqX3c9w1wQADmxksabrqcAAHTJ+KSNvuJ6iLkgAHJEAABAOVlj/3bLCuPNVQAlAiBXzZiLAgFAGVUSc6/rGeaKAMjZyUnXEwAAMmW0a+2KqlcHAEoEQO7GmlLMwYAAUBrWmo8aY7z7ZicA8malU2wFAICSMPvWL4/+j+sp5oMAcODUJPcHAIAysFbvNcZ4+Y1OADhgJT132vUUAICFsNLXN6ysftn1HPNFADgy0eK0QADw2JQx7fe4HmIhCACHnj/N1QEBwEvGvn/98sYe12MsBAHgUDuRjo6nuwQAAN746rpltU+6HmKhCADHJlvSyQnXUwAAOmMPNJvVtxljvP/djQAogBMTHA8AAB44Yazu2nylOeZ6kCwQAAVgJR0bTw8MBAAU0qSR7lq3sv4D14NkhQAoCGulo2PSVOx6EgDAeaya1prfWrei9ojrUbJEABRIYqXDp9LjAgAAhTBujXmdz+f7z4QAKJjESofHpNMcEwAAThnpWGJ1+4YV1a+5nqUbCIACslY6MnbmaoHeH2cKAF56PLbtV1yzsvaY60G6hQAosFOT0qFTXCwIAHJkjfQXk8urr7p2ZeNp18N0U9X1AJjdZCw9e0Ja0if197ieBgBKba+xete6lbUHXA+SB7YAeCCx6RUDD56Uml7ecwoABUSl6AAABSJJREFUCm1CVn9UGa++NJTFX2ILgFemYunnJ6WBmjTUK9Ui1xMBgNcmjMynkyj6+Ial5oDrYfJGAPjGSmPN9MqBvXVpqCH18C4CwFwckvQ5Y6ufWLfSHHI9jCssHZ6ySk8VPN2UqpX0+ID+OlsFAGAGY7L2PpnK53+yPHpgmzHBX3aNACiBOEnvJ3BiQqpG6RaB3ppUj6RaRZJxPSEA5O6IjJ6w0sNKtPPAiup3WPTPRwCUTNxOH+NTZ/6BSSOgFkmVSnrUpzFShSgAUFDVSE/21fR3nfy7Vmob6aSsPWFUGTM22Vftre1Zs8g81+05fUcAlJ2VWu30AQBeMPYH2zfW3+96jLLjNEAAAAJEAAAAECACAACAABEAAAAEiAAAACBABAAAAAEiAAAACBABAABAgLwIgEYi63oGAADKxIsAaPdqwvUMAICc2Mpp1yOEwIsA0DMacz0CACAfRvaU6xlC4EUAbNtmYkmTrucAAHSftTrpeoYQeBEAZxx3PQAAIAcVnXA9Qgh8CoCnXA8AAMiBNftcjxACjwLAjLqeAACQh5jv+xx4FACWDwQAlF88NNbztOshQuBPAFj9wPUIAICue/KGG0zL9RAh8CYAxserj0hqup4DANA9RtrpeoZQeBMAd91gTkv6rus5AADdk1hDAOTEmwCQJFnKEABKLE7q0TddDxEKvwIgSb7oegQAQHcY6Ru3rzdcAyAnXgXA9i09uyR93/UcAIDsJdbc63qGkHgVAJIkIz4gAFA+Y3Ezus/1ECHxLgCqleq9krhTFA'
    html += 'CUirn3jpeZcddThMS7ALj5GnNE0qddzwEAyEwrUuvjrocIjXcBIEkmqn5cXBMAAErC/NUtm3r3u54iNF4GwLZrzE8l8xnXcwAAFqyZ2PhjrocIkZcBIEnNdvRBSUdczwEAmD9j9ee3bW7scT1HiLwNgDu3mOeMsR9wPQcAYL7sASXVP3Y9Rai8DQBJ2npt7TNGesT1HACA+ai8a9sWM+Z6ilB5HQDGGKuo+hZJR13PAgDonDHmU9s3VTnv3yGvA0A6c0CgMb8jybqeBQDQkSd6+qL3uR4idN4HgCRt31i930p/4noOAMAlHbFR+/U3rTETrgcJnXE9QFastWZ4tH2PZH/X9SwAgIs6nVjddtvm2mOuB0FJtgBI6fEARzdG/0ZGf+t6FgDAi7SM9AYW/+IoTQBI0puMaTf6qv9KEgeWAEBxTEjmjds21f7e9SA4q1QBIEk3rTETRzdWXy9j/tL1LAAAHU+M7uCI/+IpzTEAF7LWmof2xB+yVh9SCUMHAArPmH2K26/bvqVnl+tR8GKlDYBpD460tlWkz0ta7XoWAAiFsfqSGtV3bFtrjrueBRdX+gCQpG8+aVfHlfhzkv6Z61kAoOTGrOz7bt1U/x+uB8HsggiAaTt2x3cZk/w3yaxxPQsAlI01+qra1Xfdep35setZcGlBBYAk3b/XDjXa8X+U9E5JA67nAYAS+Edr9R9u3Vx7wPUg6FxwATDtwd12qVH8bmP0bklLXM8DAB561Frzse2boq8aY7gcu2eCDYBp3xqxgy3beoM15rclbRVnDADAbI7ImC8kSu69bWP9H1wPg/kLPgDO9fA+uyZutX69IrPdGt0itgwAgLXSjyTtlDFfX3QqevCGG0zL9VBYOAJgBh+2trJtX+tl7aTyEslulNVGSVdL5jLJDio9fqDX7ZQAkInnJY1LGpN0SNbsMbKjNjIjrUr0D3dsMIcdz4cu+P/SjihghBhptgAAAABJRU5ErkJggg=="/>'
    html += '                                </defs>'
    html += '                                </svg>'
    html += '                                <p class="dragdrop-span">'
    html += widget_language_tuned_text["file_attachment_text"]
    html += '                                </p>'
    html += '                                <p class="dragdrop-upload-file-format">'
    if (file_types.includes('image')) {
        html += '.jpeg, .png, .jpg, .gif'
    } else if (file_types.includes('word')) {
        html += '.doc, .docx, .odt, .pdf, .rtf, .tex, .wks, .wkp'
    } else if (file_types.includes('compressed')) {
        html += '.zip, .rar, .rpm, .z, .tar.gz, .pkg'
    } else if (file_types.includes('video')) {
        html += '.mp4'
    }
    html += '                                </p>'
    html += '                                <p class="max-file-para">'
    html += widget_language_tuned_text["file_size_limit_text"] + ' ' + max_file_size_allowed + 'MB'
    html += '                                </p>'
    html += '                           </div></div>'
    return html
}

function bot_response_sent_check_box(check_box) {
    let buttons = ''
    for (check = 0; check < check_box.length; check++) {
        buttons += '<span class="user-history-radio-item">'
        buttons += '<span class="checkbox-square"></span>'
        buttons += '<div style="width:150px">'
        buttons += check_box[check]
        buttons += '</div></span>'
    }
    return `<div class="easychat-user-history-radio-div">
                    ${buttons}
                </div>`
}

function bot_response_custom_form_widget(input_type, placeholder, labelname, optional, form, country_code, max_file_size_allowed, widget_language_tuned_text) {
    let html = ''

    html += '<label for="input-IW6fJ">'
    html += labelname

    if (optional == 'false') {
        html += '<span style="color: red;"> *</span>'
    }
    html += '                                        </label>'

    if (input_type == 'text_field') {
        html += '<input type="text" class="easychat-form-input easychat-user-history-form-input" placeholder="' + placeholder + '">'
    } else if (input_type == "dropdown_list") {
        placeholder = placeholder.split('$$$')
        html += bot_response_sent_drop_down(placeholder, widget_language_tuned_text)
    } else if (input_type == 'range') {
        if (form['range_type'] == 'Single Range Selector') {
            html += bot_response_single_range_slider(widget_language_tuned_text)
        } else {
            html += bot_response_multiple_range_slider(widget_language_tuned_text)
        }
    } else if (input_type == 'checkbox') {
        placeholder = placeholder.split('$$$')
        html += bot_response_sent_check_box(placeholder)
    } else if (input_type == "radio") {
        placeholder = placeholder.split('$$$')
        html += bot_response_sent_radio_button(placeholder)
    } else if (input_type == "date_picker") {
        if (form["calendar_type"] == "Single Type") {
            html += single_calendar(widget_language_tuned_text)
        } else {
            html += multi_calendar(widget_language_tuned_text)
        }
    } else if (input_type == 'time_picker') {
        if (form['calendar_type'] == "Single Type") {
            html += single_time(widget_language_tuned_text)
        } else {
            html += multi_time(widget_language_tuned_text)
        }
    } else if (input_type == "file_attach") {
        html += bot_response_attachment(placeholder, max_file_size_allowed, widget_language_tuned_text)
    } else if (input_type = 'phone_number') {
        html += bot_response_phone_number(country_code, widget_language_tuned_text)
        country_code.push(form['country_code'])
    }
    return [country_code, html]
}

function bot_response_phone_number(country_code, widget_language_tuned_text) {
    let html = `<div class="easychat-user-history-phone-number-div">
    <div class="phone-number-input-div">
    <input type="tel" id="phone${country_code.length.toString()}" class="input" placeholder="${widget_language_tuned_text["enter_phone_text"]}">
    </div></div>`
    return html
}

function bot_response_single_range_slider(widget_language_tuned_text) {
    return `<div class="easychat-user-history-range-slider-div">
                <div class="user-history-range-slider">
                    <p>${widget_language_tuned_text["select_value_text"]}</p>
                    <div class="range-slider-div">
                        <span></span>
                    </div>
                    <div class="easychat-user-history-range-value-div">
                        <div class="range-slider-value">
                            <div class="range-slider-selected-value">
                                <div class="selected-value-entered-div">
                                XX
                                </div>
                            <p class="range-selected-value-type-para">
                                ${widget_language_tuned_text["selected_value_text"]}
                            </p>
            </div></div></div></div></div>`
}

function bot_response_multiple_range_slider(widget_language_tuned_text) {
    return `<div class="easychat-user-history-range-slider-div">
                <div class="user-history-range-slider">
                    <p>${widget_language_tuned_text["select_value_text"]}</p>
                    <div class="range-slider-div">
                        <span></span>
                    </div>
                    <div class="easychat-user-history-range-value-div">
                        <div class="range-slider-value">
                            <div class="range-slider-selected-value min-max-range-value">
                                <div class="selected-value-entered-div">
                                    XX
                                </div>
                                <p class="range-selected-value-type-para">
                                    ${widget_language_tuned_text["min_text"]}
                                </p>
                            </div>
                            <span class="min-max-value-hyphen"></span>
                            <div class="range-slider-selected-value min-max-range-value">
                            <div class="selected-value-entered-div">
                                XX
                            </div>
                            <p class="range-selected-value-type-para">
                                ${widget_language_tuned_text["max_text"]}
                            </p>
                </div></div></div></div></div>`
}

function bot_response_video_recording(widget_language_tuned_text) {
    return `<div class="easychat-user-history-video-record-div">
                <div class="user-history-video-recorder">
                <video class="responsive-video" id="" controls="" autoplay="" style="height:10em;" type="video/webm"></video>
                <div class="user-history-start-stop-video-record-div">
                    <span class="video-record-start-btn">
                        ${widget_language_tuned_text["start_text"]}
                    </span>
                    <span class="video-record-stop-btn">
                        ${widget_language_tuned_text["cancel_text"]}
                    </span></div></div></div>`
}

function bot_response_sent_drop_down(drop_down, widget_language_tuned_text) {
    let buttons = ''
    for (option = 0; option < drop_down.length; option++) {
        buttons += '<li>' + drop_down[option] + '</li>'
    }
    return `<div class="easychat-user-history-dropdown-div">
                <div class="user-history-dropdown-search-div">
                    <div class="dropdown-search">
                        <svg width="13" height="12" viewBox="0 0 13 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M11.1667 10.3452L8.55959 7.73807C9.1861 6.98594 9.49851 6.02123 9.43185 5.04462C9.36519 4.06801 8.92458 3.1547 8.20168 2.49468C7.47878 1.83466 6.52925 1.47875 5.55062 1.50098C4.572 1.52322 3.63961 1.92189 2.94744 2.61407C2.25527 3.30624 1.85659 4.23862 1.83436 5.21725C1.81212 6.19588 2.16803 7.14541 2.82805 7.86831C3.48807 8.5912 4.40139 9.03181 5.378 9.09848C6.3546 9.16514 7.31932 8.85272 8.07145 8.22622L10.6786 10.8333L11.1667 10.3452ZM2.53616 5.30978C2.53616 4.69528 2.71838 4.09457 3.05979 3.58363C3.40119 3.07269 3.88643 2.67446 4.45416 2.43929C5.02189 2.20413 5.64661 2.1426 6.2493 2.26249C6.852 2.38237 7.40562 2.67829 7.84014 3.11281C8.27466 3.54733 8.57057 4.10094 8.69045 4.70364C8.81034 5.30634 8.74881 5.93105 8.51365 6.49878C8.27849 7.06651 7.88026 7.55176 7.36931 7.89316C6.85837 8.23456 6.25766 8.41678 5.64316 8.41678C4.81941 8.41587 4.02967 8.08823 3.44719 7.50575C2.86471 6.92328 2.53708 6.13353 2.53616 5.30978Z" fill="#4D4D4D"/>
                        </svg>
                        <span>${widget_language_tuned_text["dropdown_text"]}</span>
                    </div>
                </div>
                <div class="user-history-select-options">
                    <ul class="user-history-select-list">
                        ${buttons}
                    </ul>
                </div></div>`

}

function bot_response_sent_radio_button(radio_buttons) {
    let buttons = ''
    for (radio = 0; radio < radio_buttons.length; radio++) {
        buttons += '<span class="user-history-radio-item">'
        buttons += '<span class="radio-circle"></span>'
        buttons += '<div style="width:calc(100% - 24px);">'
        buttons += radio_buttons[radio]
        buttons += '</div></span>'
    }
    return `<div class="easychat-user-history-radio-div">
                ${buttons}
            </div>`
}

function bot_response_sent_table(table_data) {
    let data = ''
    for (col = 0; col < table_data.length; col++) {
        data += '<tr>'
        for (row = 0; row < table_data[col].length; row++) {
            if (col == 0) {
                data += '<th style="background-color:#0F52A1">' + stripHTML(un_entity(table_data[col][row])).trim() + '</th>'
            } else {
                data += '<td>' + stripHTML(un_entity(table_data[col][row])).trim() + '</td>'
            }
        }
        data += '</tr>'
    }
    return `<div class="easychat-table-div-wrapper easychat-user-history-table-div" style="margin-top:0rem;width:100%;border-radius:10px;">
                <table class="easychat-bot-table">
                    <tbody>
                        ${data}
                    </tbody>
                </table>
            </div>`
}

function bot_response_sent_cards(title, text, attached_file_src) {
    return `<div class="easychat-user-history-card-div">
                    <a href="${attached_file_src}" target="_blank">
                    <img class="easychat-user-history-card-img-top" src="${attached_file_src}" alt="Card image">
                        <div class="easychat-user-history-card-body">
                        <h5 class="easychat-user-history-card-title">${title}</h5>
                        <p class="easychat-user-history-card-text">
                            ${text}
                            </p>
                        <span href="#" class="know-more-link">Know more</span>
                </div></a></div>`
}

function bot_response_sent_image(attached_file_path) {
    return `<div class="easychat-slider-wrapper easychat-user-history-image-div">
                    <div class="image-slider-wrapper-div">
                            <div class="slideshow-container" >
                                <div class="mySlides fade" style="height:100%">
                                <a href="${attached_file_path}" target="_blank">
                                    <img src="${attached_file_path}" style="cursor:pointer;">
                                    </a>
                                </div>
                            </div></div></div>`
}

function get_video_sent_html(attached_file_path, widget_language_tuned_text) {
    attached_file_path = getEmbedVideoURL(attached_file_path)
    let html = ''
    if (attached_file_path.indexOf("embed") != -1) {
        html += '<div class=" easychat-user-history-video-div">'
        html += '<iframe class="easychat-user-video"  height="134" src="' + attached_file_path + '" frameborder="1" allowfullscreen>'
        html += '</iframe>'
        html += '</div>'
    } else {
        html += '<div class=" easychat-user-history-video-div">'
        html += '<video height="134" controls>'
        html += '<source onerror="handle_video_unload(this)" src="' + attached_file_path + '" type="video/mp4"></video>'
        html += '<div style="display: none; padding-bottom:0px; height: 134;"><div class="easychat-unable-to-load-content-wrapper">'
        html += '<svg width="52" height="53" viewBox="0 0 52 53" fill="none" xmlns="http://www.w3.org/2000/svg">'
        html += '<path fill-rule="evenodd" clip-rule="evenodd" d="M50.3928 0.0548387C50.2099 0.110774 48.9261 1.326 46.7228 3.52873C44.8589 5.39206 43.3175 6.89711 43.2975 6.87341C43.2775 6.84961 43.0868 6.57012 42.8736 6.25233C41.6225 4.38645 39.6289 2.99279 37.2852 2.34574L36.3582 2.08986H24.0334C12.3622 2.08986 11.6784 2.09905 11.1398 2.26326C9.71253 2.69851 8.44602 3.74413 7.82997 4.99615C7.17011 6.3369 7.20879 5.09456 7.2069 25.0335L7.20529 43.0472L3.73869 46.5071C1.83204 48.4101 0.210849 50.0823 0.136047 50.2231C0.0612447 50.3639 0 50.6569 0 50.8742C0 51.2067 0.0583063 51.3276 0.368039 51.6374C0.677866 51.9471 0.798744 52.0054 1.13123 52.0054C1.34853 52.0054 1.64148 51.9442 1.78236 51.8694C1.92315 51.7946 13.2643 40.4995 26.9849 26.7694C47.1745 6.56576 51.9419 1.74884 51.9856 1.50841C52.0152 1.34506 51.9977 1.05979 51.9465 0.874535C51.856 0.54641 51.3876 0.0528478 51.1644 0.0501932C51.1033 0.0495296 50.9679 0.0308527 50.8636 0.00885763C50.7593 -0.0132323 50.5474 0.0074355 50.3928 0.0548387ZM33.7527 6.23764C33.7547 8.14761 33.8801 8.88947 34.3691 9.88342C34.9289 11.0208 36.024 12.0438 37.1149 12.4481C37.3505 12.5354 37.5433 12.6297 37.5433 12.6576C37.5433 12.6856 31.2714 18.9798 23.6057 26.6448L9.66817 40.5812L9.69291 23.7057L9.71766 6.83018L9.9632 6.30874C10.3121 5.56802 10.637 5.22387 11.3009 4.89214L11.881 4.60223H22.8161H33.7511L33.7527 6.23764ZM36.9808 4.84986C38.7019 5.36096 40.4164 6.74409 41.2114 8.26242L41.4772 8.7701L40.6717 9.58639L39.8661 10.4027L39.1262 10.3553C38.2055 10.2962 37.5151 9.98154 36.985 9.37933C36.3831 8.69549 36.2865 8.30707 36.239 6.37985C36.1923 4.4823 36.1357 4.599 36.9808 4.84986ZM42.6415 18.0229C42.4994 18.1 42.3288 18.2583 42.2623 18.3747C42.1666 18.5423 42.1316 21.3716 42.094 32.0013L42.0466 45.4164L41.8011 45.9378C41.4453 46.6932 41.1206 47.0294 40.4074 47.3806L39.7754 47.6917L26.3583 47.7391C15.702 47.7768 12.8974 47.8115 12.7287 47.9079C12.2354 48.1897 12.08 49.0562 12.4221 49.6172C12.8061 50.2471 11.8966 50.2112 26.7139 50.1822C39.4461 50.1573 40.1778 50.1467 40.6719 49.9822C42.1016 49.506 43.3309 48.4767 43.9343 47.2504C44.5848 45.9286 44.5555 46.6419 44.5574 32.0693C44.5591 17.7767 44.5866 18.5135 44.0362 18.0807C43.725 17.8359 43.0387 17.8074 42.6415 18.0229Z" fill="#7B7A7B"/>'
        html += '</svg>'
        html += '<div class="unable-to-load-content-text-div">' + widget_language_tuned_text["unable_to_load_text"] + ' </div></div></div>'
        html += '</div>'
    }
    return html
}

function handle_video_unload(ele) {
    ele.parentElement.style.display = "none";
    ele.parentElement.nextElementSibling.style.display = "flex";
}

function bot_response_recommendation_sent_html(message_recommendation, is_selected) {
    let html = ''
    if (is_selected) {
        html += '<span class="selected-recommendation">' + message_recommendation + '</span>'
    } else {
        html += '<span>' + message_recommendation + '</span>'
    }

    return html
}

function get_recommendation_sent_html(message_recommendation, is_selected) {
    let html = ''
    if (is_selected) {
        html += '<div class="easychat-button-div selected">'
        html += '<span class="download_btn">' + message_recommendation + '</span>'
        html += '</div>'
    } else {
        html += '<div class="easychat-button-div">'
        html += '<span class="download_btn">' + message_recommendation + '</span>'
        html += '</div>'
    }

    return html
}
function get_pdf_search_results_html(pdf_search_list, widget_language_tuned_text) {
    let html = ''
    html += '<div class="mySlides fade easychat-slider-card easychat-pdf-search-card" style="width: 70% !important">'
    html += '<div class="easychat-pdf-searcher-header-wrapper pdf-wrapper-div">'
    html += '<div style="display: flex; gap: 0.5em;" class="easychat-pdf-searcher-header-div">'
    html += '<svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">'+
            '<rect width="40" height="40" fill="#B30B00"/>'+
            '<path d="M31.8392 22.8774C31.2573 21.8403 29.2468 21.5145 28.3244 21.3679C27.5974 21.2522 26.8552 21.2177 26.1199 21.2184C25.5425 21.2146 24.9736 21.243 24.412 21.2749C24.205 21.2888 24.0001 21.3067 23.7953 21.3244C23.5855 21.1072 23.3826 20.8828 23.1863 20.6533C21.9373 19.1748 20.9289 17.4981 20.1071 15.7557C20.3253 14.9139 20.4999 14.0353 20.6053 13.1228C20.7978 11.4574 20.8639 9.55951 20.2399 7.97177C20.0244 7.42378 19.4499 6.75664 18.7871 7.08885C18.0251 7.47089 17.8107 8.5533 17.7486 9.32058C17.6986 9.94076 17.7336 10.5625 17.8377 11.1723C17.9438 11.7863 18.1145 12.3693 18.3004 12.9514C18.4739 13.4852 18.6651 14.0148 18.8735 14.5395C18.7412 14.9525 18.6009 15.3584 18.4534 15.7538C18.1097 16.6551 17.7381 17.5113 17.3806 18.335C17.1922 18.7434 17.0077 19.1432 16.8272 19.534C16.2561 20.7886 15.636 22.0202 14.9401 23.2107C13.3169 23.7833 11.8603 24.4471 10.6506 25.2271C10.0017 25.6464 9.42846 26.1017 8.95107 26.6012C8.50035 27.0727 8.04228 27.6845 8.00219 28.3619C7.97967 28.7443 8.13108 29.1153 8.44429 29.3421C8.87504 29.6639 9.44587 29.6425 9.94563 29.5377C11.5827 29.1943 12.8399 27.7871 13.9104 26.601C14.6479 25.7841 15.4872 24.7467 16.3651 23.4921C16.3671 23.4892 16.369 23.4864 16.371 23.4835C17.8769 23.0166 19.5157 22.6225 21.255 22.3327C22.0496 22.201 22.8653 22.0932 23.6973 22.0174C24.2823 22.5654 24.9145 23.0644 25.6041 23.4811C26.1413 23.8115 26.7126 24.0906 27.3105 24.2987C27.9152 24.4963 28.5236 24.6576 29.1518 24.7596C29.469 24.805 29.7934 24.8256 30.1248 24.8131C30.8644 24.7852 31.9261 24.5015 31.9957 23.6041C32.0171 23.3294 31.9578 23.0885 31.8392 22.8774ZM14.1315 24.524C13.7851 25.0607 13.4509 25.5434 13.1361 25.968C12.3652 27.0171 11.4847 28.263 10.2098 28.7289C9.96767 28.8174 9.64887 28.9088 9.31283 28.889C9.01352 28.8714 8.71836 28.7393 8.73194 28.3994C8.73865 28.2215 8.82569 27.9945 8.95922 27.7716C9.10536 27.527 9.28632 27.3028 9.48229 27.0966C9.90219 26.6555 10.4331 26.2279 11.0438 25.832C11.9806 25.2242 13.0989 24.6772 14.3455 24.1891C14.2738 24.3025 14.2022 24.4153 14.1315 24.524ZM18.4793 11.0663C18.3832 10.505 18.3686 9.93597 18.4277 9.38878C18.4571 9.11518 18.5129 8.84813 18.5935 8.59786C18.6619 8.38543 18.8094 7.86699 19.0449 7.80039C19.433 7.69051 19.5523 8.52375 19.5962 8.75949C19.8463 10.1005 19.6259 11.5918 19.3258 12.9072C19.2781 13.1164 19.2249 13.3223 19.1704 13.5274C19.0775 13.2717 18.9888 13.0152 18.9072 12.7574C18.7315 12.1944 18.5708 11.6248 18.4793 11.0663ZM21.1439 21.6523C19.6857 21.8887 18.2985 22.1984 16.9946 22.564C17.1516 22.5201 17.869 21.1604 18.0291 20.8782C18.7831 19.5501 19.3999 18.1563 19.8431 16.6941C20.6257 18.2419 21.5756 19.7226 22.7425 21.0406C22.85 21.1602 22.9592 21.2784 23.0704 21.3952C22.4165 21.4656 21.773 21.5514 21.1439 21.6523ZM31.0054 23.5201C30.9521 23.8084 30.3364 23.9732 30.0491 24.0185C29.2 24.1521 28.3018 24.0452 27.4891 23.7723C26.9315 23.5851 26.3938 23.3302 25.8828 23.0235C25.3749 22.7167 24.8998 22.3557 24.4556 21.9577C25.0033 21.9248 25.5577 21.9032 26.1147 21.9138C26.6718 21.9194 27.2332 21.9475 27.7878 22.0198C28.8277 22.1358 29.993 22.4928 30.8115 23.1676C30.9727 23.3006 31.0241 23.4182 31.0054 23.5201Z" fill="white"/>'+
            '<path d="M19.658 33V28.24H21.226C21.7253 28.24 22.0987 28.366 22.346 28.618C22.598 28.87 22.724 29.206 22.724 29.626V29.997C22.724 30.417 22.598 30.7553 22.346 31.012C22.0987 31.264 21.7253 31.39 21.226 31.39H20.498V33H19.658ZM21.226 29.045H20.498V30.585H21.226C21.4313 30.585 21.5877 30.5337 21.695 30.431C21.807 30.3283 21.863 30.1837 21.863 29.997V29.626C21.863 29.444 21.807 29.3017 21.695 29.199C21.5877 29.0963 21.4313 29.045 21.226 29.045ZM23.6775 33V28.24H25.2875C25.8569 28.24 26.2909 28.3987 26.5895 28.716C26.8882 29.0333 27.0375 29.5 27.0375 30.116V31.117C27.0375 31.7377 26.8882 32.2067 26.5895 32.524C26.2909 32.8413 25.8569 33 25.2875 33H23.6775ZM25.2525 29.045H24.5175V32.195H25.2525C25.5839 32.195 25.8195 32.1133 25.9595 31.95C26.1042 31.7867 26.1765 31.509 26.1765 31.117V30.116C26.1765 29.7287 26.1042 29.4533 25.9595 29.29C25.8195 29.1267 25.5839 29.045 25.2525 29.045ZM30.5842 31.173H28.9882V33H28.1482V28.24H30.7942V29.045H28.9882V30.368H30.5842V31.173Z" fill="white"/>'+
            '</svg>'
    html += '<span>' + pdf_search_list["title"] + '</span>' 
    html += '</div>'
    html += '<div class="easychat-pdf-searcher-page-div">'
    html += '<span>Page : </span>'
    html += '<span>' + pdf_search_list["page_number"] + '</span>'
    html += '</div></div>'
    html += '<p class="pdf-search-card-desc-div pdf-desc-wrapper">'
    html += '<b>' + pdf_search_list["content"] + '</b>' + '</p>'
    html += '<div style="text-align: center; cursor: pointer;">'
    html += '<a target = "_blank" href=' + pdf_search_list["link"] + '><div class="pdf-search-card-doc-open-btn pdf-doc-btn">' + widget_language_tuned_text["pdf_view_document_text"] + '</div></a>'
    html += '</div></div>'
    return html
}
function get_message_received_html(message_list) {
    let html = '<div class="easychat-query-send-message-wrapper">'
    html += '<div class="easychat-query-send-message-div">'
    html += '<div class="easychat-user-custom-checkbox-div">' +
        '<input type="checkbox" name="input-checkbox-selected-misdashboard-" id="input-checkbox-selected-misdashboard-' + message_list["pk"] + '" class="filled-in selected-misdashboard">' +
        '<label for="input-checkbox-selected-misdashboard-' + message_list["pk"] + '"><span></span></label>' +
        '</div>'
    html += '<div class="easychat-query-message-icon">'
    html += '<svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">' +
        '<g filter="url(#filter0_dd_232_13203)">' +
        '<rect x="4" y="2" width="32" height="32" rx="16" fill="#F6F6F6"/>' +
        '<rect x="4.5" y="2.5" width="31" height="31" rx="15.5" stroke="#EBEBEB"/>' +
        '</g>' +
        '<g clip-path="url(#clip0_232_13203)">' +
        '<circle cx="20.0786" cy="14.6304" r="3.12377" stroke="#2D2D2D" stroke-width="1.42442"/>' +
        '<path d="M15.497 24.6039C15.3749 23.209 15.7167 20.3355 18.0602 20.0007H22.0881C23.0645 20.0007 24.9442 20.9214 24.6513 24.6039" stroke="#2D2D2D" stroke-width="1.42442" stroke-linecap="round"/>' +
        '</g>' +
        '<defs>' +
        '<filter id="filter0_dd_232_13203" x="0" y="0" width="40" height="40" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">' +
        '<feFlood flood-opacity="0" result="BackgroundImageFix"/>' +
        '<feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>' +
        '<feOffset dy="2"/>' +
        '<feGaussianBlur stdDeviation="2"/>' +
        '<feColorMatrix type="matrix" values="0 0 0 0 0.196487 0 0 0 0 0.196487 0 0 0 0 0.279476 0 0 0 0.06 0"/>' +
        '<feBlend mode="multiply" in2="BackgroundImageFix" result="effect1_dropShadow_232_13203"/>' +
        '<feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>' +
        '<feOffset/>' +
        '<feGaussianBlur stdDeviation="1"/>' +
        '<feColorMatrix type="matrix" values="0 0 0 0 0.196487 0 0 0 0 0.196487 0 0 0 0 0.279476 0 0 0 0.06 0"/>' +
        '<feBlend mode="multiply" in2="effect1_dropShadow_232_13203" result="effect2_dropShadow_232_13203"/>' +
        '<feBlend mode="normal" in="SourceGraphic" in2="effect2_dropShadow_232_13203" result="shape"/>' +
        '</filter>' +
        '<clipPath id="clip0_232_13203">' +
        '<rect width="15.8889" height="15.8889" fill="white" transform="translate(12 10)"/>' +
        '</clipPath>' +
        '</defs>' +
        '</svg></div>'

    return html
}

function campaign_response_text_sent(message_list, message) {
    message = get_masked_message(message);
    let html = `<div class="easychat-query-reply-message-text-div reply-message"style="width: 292px;">
    <div class="easychat-query-reply-message-text search-div reply-message-text">
        ${message}
    </div>
    <div class="easychat-query-reply-message-time-div">
        ${message_list["date_time"]} | ${message_list["channel_name"]}
    </div>
    </div>`
    return html
}

function campaign_response_QR_sent(choice, is_selected) {
    if (is_selected) {
        return `<div class="easychat-button-div selected">
        <span class="download_btn">${choice}</span>
        </div>`
    } else {
        return `<div class="easychat-button-div">
        <span class="download_btn">${choice}</span>
        </div>`
    }

}

function campaign_response_image_sent(image_url) {
    return `<div class="easychat-slider-wrapper ">
    <div class="image-slider-wrapper-div">
        <div class="slideshow-container" >
            <div class="mySlides fade" style="height:178px">
                <a href="${image_url}" target="_blank">
                    <img src="${image_url}" style="cursor:pointer;width: 100%;height: 180px;">
                    </a>
                </div>
            </div>
        </div>
    </div>`
}

function campaign_response_video_sent(video_url) {
    return `<div class="easychat-slider-wrapper easychat-user-history-image-div">
    <div class="image-slider-wrapper-div">
        <div class="slideshow-container" >
            <div class="easychat-user-history-video-div-1">
                <iframe class="easychat-user-video"  height="180" src="${video_url}" frameborder="1" allowfullscreen>
                </iframe>
            </div>
            </div>
        </div>
    </div>`
}

function campaign_response_action_button(button_message, is_call) {
    if (!is_call) {
        return `<div class="easychat-button-div">
            <span><svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M2.14233 2.85715H4.1419C4.37859 2.85715 4.57046 3.04903 4.57046 3.28572C4.57046 3.50269 4.40923 3.682 4.20005 3.71038L4.1419 3.71429H2.14212C1.46846 3.71397 0.915742 4.23224 0.861096 4.89199L0.856767 4.98279L0.858388 9.85747C0.858567 10.538 1.38736 11.0949 2.05637 11.1399L2.14439 11.1429L7.00025 11.1362C7.68005 11.1353 8.23604 10.6068 8.28119 9.93841L8.28415 9.85046V7.84686C8.28415 7.61016 8.47602 7.41828 8.7127 7.41828C8.92966 7.41828 9.10897 7.57952 9.13735 7.7887L9.14126 7.84686V9.85046C9.14126 10.9946 8.24448 11.9296 7.11511 11.9902L7.00142 11.9933L2.147 12L2.03082 11.9971C0.937967 11.9402 0.0617493 11.0644 0.00427707 9.9715L0.00127692 9.8577L0 5.00146L0.00251951 4.88575C0.0597139 3.79276 0.935842 2.91676 2.02854 2.86006L2.14233 2.85715ZM6.00135 2L9.45872 2.00083L9.51561 2.00658L9.56226 2.01575L9.62374 2.03423L9.69147 2.06398L9.7217 2.08127C9.87003 2.16983 9.97455 2.32367 9.99595 2.50305L10 2.57143V6.00403C10 6.31963 9.74417 6.57546 9.42859 6.57546C9.13555 6.57546 8.89404 6.35487 8.86103 6.07067L8.85719 6.00403L8.85681 3.9503L5.26051 7.54695C5.05453 7.75294 4.73041 7.76879 4.50625 7.59449L4.45242 7.54695C4.24643 7.34096 4.23059 7.01682 4.40488 6.79266L4.45242 6.73882L8.0477 3.14286H6.00135C5.70831 3.14286 5.46679 2.92227 5.43378 2.63807L5.42994 2.57143C5.42994 2.25584 5.68577 2 6.00135 2Z" fill="#2741FA"/>
            </svg>
            </span>
            <span class="download_btn">${button_message}</span>
            </div>`
    } else {
        return `<div class="easychat-button-div">
        <span><svg width="13" height="12" viewBox="0 0 13 12" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8.7287 10.0643C6.00514 10.0643 3.73554 6.53931 3.05464 4.49665C2.82767 3.81576 3.35726 3.43749 3.73553 3.13487C3.9171 2.9533 4.41643 2.90791 4.64338 3.13487L5.09731 3.81576C5.55124 4.49665 5.62688 4.5723 5.55123 4.72361C5.32428 5.4045 5.62688 5.93408 5.77819 6.08539L6.45907 6.76627L7.36693 7.56064C8.09321 8.19614 8.50174 7.67412 8.72871 7.56064L9.63656 8.35501C9.86351 8.58197 9.63654 8.95079 9.40959 9.26286L8.7287 10.0643Z" fill="#2741FA" stroke="#2741FA" stroke-width="0.680888" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M7.36719 3.8158C7.82111 3.8158 8.81975 4.13354 9.18289 5.40453" stroke="#2741FA" stroke-width="0.680888" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M7.82227 2C8.65446 2 10.455 2.6355 10.9997 5.17748" stroke="#2741FA" stroke-width="0.680888" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            </span>
            <span class="download_btn">Call Us</span>
        </div>`
    }

}

function campaign_response_document(document_name) {
    return `<div class="easychat-pdf-file-wrapper ">
    <div class="image-pdf-wrapper-div">
        <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="40" height="40" fill="#B30B00"/>
            <path d="M31.8392 22.8774C31.2573 21.8403 29.2468 21.5145 28.3244 21.3679C27.5974 21.2522 26.8552 21.2177 26.1199 21.2184C25.5425 21.2146 24.9736 21.243 24.412 21.2749C24.205 21.2888 24.0001 21.3067 23.7953 21.3244C23.5855 21.1072 23.3826 20.8828 23.1863 20.6533C21.9373 19.1748 20.9289 17.4981 20.1071 15.7557C20.3253 14.9139 20.4999 14.0353 20.6053 13.1228C20.7978 11.4574 20.8639 9.55951 20.2399 7.97177C20.0244 7.42378 19.4499 6.75664 18.7871 7.08885C18.0251 7.47089 17.8107 8.5533 17.7486 9.32058C17.6986 9.94076 17.7336 10.5625 17.8377 11.1723C17.9438 11.7863 18.1145 12.3693 18.3004 12.9514C18.4739 13.4852 18.6651 14.0148 18.8735 14.5395C18.7412 14.9525 18.6009 15.3584 18.4534 15.7538C18.1097 16.6551 17.7381 17.5113 17.3806 18.335C17.1922 18.7434 17.0077 19.1432 16.8272 19.534C16.2561 20.7886 15.636 22.0202 14.9401 23.2107C13.3169 23.7833 11.8603 24.4471 10.6506 25.2271C10.0017 25.6464 9.42846 26.1017 8.95107 26.6012C8.50035 27.0727 8.04228 27.6845 8.00219 28.3619C7.97967 28.7443
            8.13108 29.1153 8.44429 29.3421C8.87504 29.6639 9.44587 29.6425 9.94563 29.5377C11.5827 29.1943 12.8399 27.7871 13.9104 26.601C14.6479 25.7841 15.4872 24.7467 16.3651 23.4921C16.3671 23.4892 16.369 23.4864 16.371 23.4835C17.8769 23.0166 19.5157 22.6225 21.255 22.3327C22.0496 22.201 22.8653 22.0932 23.6973 22.0174C24.2823 22.5654 24.9145 23.0644 25.6041 23.4811C26.1413 23.8115 26.7126 24.0906 27.3105 24.2987C27.9152 24.4963 28.5236 24.6576 29.1518 24.7596C29.469 24.805 29.7934 24.8256 30.1248 24.8131C30.8644 24.7852 31.9261 24.5015 31.9957 23.6041C32.0171 23.3294 31.9578 23.0885 31.8392 22.8774ZM14.1315 24.524C13.7851 25.0607 13.4509 25.5434 13.1361 25.968C12.3652 27.0171 11.4847 28.263 10.2098 28.7289C9.96767 28.8174 9.64887 28.9088 9.31283 28.889C9.01352 28.8714 8.71836 28.7393 8.73194 28.3994C8.73865 28.2215 8.82569 27.9945 8.95922 27.7716C9.10536 27.527 9.28632 27.3028 9.48229 27.0966C9.90219 26.6555 10.4331 26.2279 11.0438 25.832C11.9806 25.2242 13.0989 24.6772 14.3455 24.1891C14.2738 24.3025 14.2022 24.4153 14.1315 24.524ZM18.4793 11.0663C18.3832 10.505 18.3686 9.93597 18.4277 9.38878C18.4571 9.11518 18.5129 8.84813 18.5935 8.59786C18.6619 8.38543 18.8094 7.86699 19.0449 7.80039C19.433 7.69051 19.5523 8.52375 19.5962 8.75949C19.8463 10.1005 19.6259 11.5918 19.3258 12.9072C19.2781 13.1164 19.2249 13.3223 19.1704 13.5274C19.0775 13.2717 18.9888 13.0152 18.9072 12.7574C18.7315 12.1944 18.5708 11.6248 18.4793 11.0663ZM21.1439 21.6523C19.6857 21.8887 18.2985 22.1984 16.9946 22.564C17.1516 22.5201 17.869 21.1604 18.0291 20.8782C18.7831 19.5501 19.3999 18.1563 19.8431 16.6941C20.6257 18.2419 21.5756 19.7226 22.7425 21.0406C22.85 21.1602 22.9592 21.2784 23.0704 21.3952C22.4165 21.4656 21.773 21.5514 21.1439 21.6523ZM31.0054 23.5201C30.9521 23.8084 30.3364 23.9732 30.0491 24.0185C29.2 24.1521 28.3018 24.0452 27.4891 23.7723C26.9315 23.5851 26.3938 23.3302 25.8828 23.0235C25.3749 22.7167 24.8998 22.3557 24.4556 21.9577C25.0033 21.9248 25.5577 21.9032 26.1147 21.9138C26.6718 21.9194 27.2332 21.9475 27.7878 22.0198C28.8277 22.1358 29.993 22.4928 30.8115 23.1676C30.9727 23.3006 31.0241 23.4182 31.0054 23.5201Z" fill="white"/>
            <path d="M19.658 33V28.24H21.226C21.7253 28.24 22.0987 28.366 22.346 28.618C22.598 28.87 22.724 29.206 22.724 29.626V29.997C22.724 30.417 22.598 30.7553 22.346 31.012C22.0987 31.264 21.7253 31.39 21.226 31.39H20.498V33H19.658ZM21.226 29.045H20.498V30.585H21.226C21.4313 30.585 21.5877 30.5337 21.695 30.431C21.807 30.3283 21.863 30.1837 21.863 29.997V29.626C21.863 29.444 21.807 29.3017 21.695 29.199C21.5877 29.0963 21.4313 29.045 21.226 29.045ZM23.6775 33V28.24H25.2875C25.8569 28.24 26.2909 28.3987 26.5895 28.716C26.8882 29.0333 27.0375 29.5 27.0375 30.116V31.117C27.0375 31.7377 26.8882 32.2067 26.5895 32.524C26.2909 32.8413 25.8569 33 25.2875 33H23.6775ZM25.2525 29.045H24.5175V32.195H25.2525C25.5839 32.195 25.8195 32.1133 25.9595 31.95C26.1042 31.7867 26.1765 31.509 26.1765 31.117V30.116C26.1765 29.7287 26.1042 29.4533 25.9595 29.29C25.8195 29.1267 25.5839 29.045 25.2525 29.045ZM30.5842 31.173H28.9882V33H28.1482V28.24H30.7942V29.045H28.9882V30.368H30.5842V31.173Z" fill="white"/>
            </svg>

    </div>
    <div class="text-pdf-wrapper-div">
        <h4>${document_name}</h4>
    </div>
</div>`
}

function search_chat_down() {
    last_scroll_id++;
    if ($('#result_' + last_scroll_id).length) {
        $("#load_user_messages").scrollTo('#result_' + last_scroll_id, 250);
        $('mark').css('background-color', '#ff0')
        $('#result_' + last_scroll_id).css('background-color', 'orange')
        $('#current_search_id').text(last_scroll_id)
    } else {
        last_scroll_id--;
    }
}

function search_chat_up() {
    last_scroll_id--;
    if ($('#result_' + last_scroll_id).length) {
        $("#load_user_messages").scrollTo('#result_' + last_scroll_id, 250);
        $('mark').css('background-color', '#ff0')
        $('#result_' + last_scroll_id).css('background-color', 'orange')
        $('#current_search_id').text(last_scroll_id)
    } else {
        last_scroll_id++;
    }
}

function reset_search_results() {
    $('.search-div').each(function () {
        let replaced_text = $(this).html().replace(/(<mark.*?>|<\/mark>)/igm, "");
        $(this).html(replaced_text);
    })
    $('#current_search_id, #total_search_result').text('0')
    $('#search_results_track').hide()
    $('.user-search-up-down-arrow-wrapper').css({ 'pointer-events': 'none', 'opacity': '0.5' })
}

function get_user_messages_static(user_id, scroll_to_session_id = null) {
    window.history.replaceState(null, null, window.location.pathname + window.location.search.split('&')[0])
    document.getElementById("loader-user-message").style.display = 'flex'
    document.getElementById("no-user-selected").style.display = 'none';
    document.getElementById("select-user-id").innerHTML = user_id;
    document.getElementById("load_user_messages").innerHTML = "";
    $('.user-search-cross-icon').click()
    hide_selected_mis($('.user-history-clearall-btn'));
    let message_list = [{
        'pk': 995,
        'message_received': 'lol',
        'message_recommendation': '[]',
        'message_choices': '',
        'message_sent': 'Glad I made you laugh! How may I assist you now?',
        'session_id': "55f1dd8d-27c9-4ea0-a25d-f792a26e0333",
        'session_id_wise_data': {
            '2e403ca9-5172-4a7e-a7bb-38ef86197c8d': 2,
            '55f1dd8d-27c9-4ea0-a25d-f792a26e0333': 1
        },
        'date_time': 'Jun 14 2021 11:53 AM',
        'channel_name': 'Web',
        'is_helpful': 'False',
        'widgets': '[]',
        'form_data_widget': ''
    }, {
        'pk': 994,
        'message_received': 'Date: 3f7c59288e3725f1887f7852c0b11ba3ebc014d32b0cb5fdd98cda7b2bb3b858',
        'message_recommendation': '[]',
        'message_choices': '',
        'message_sent': "I'm not sure if I can help you with your query. Can you please rephrase it? Alternatively, you can connect to our customer care team, who is always there to help you!",
        'session_id': "2e403ca9-5172-4a7e-a7bb-38ef86197c8d",
        'session_id_wise_data': {
            '2e403ca9-5172-4a7e-a7bb-38ef86197c8d': 2,
            '55f1dd8d-27c9-4ea0-a25d-f792a26e0333': 1
        },
        'date_time': 'Jun 14 2021 11:52 AM',
        'channel_name': 'Web',
        'is_helpful': 'False',
        'widgets': '[]',
        'form_data_widget': ''
    }, {
        'pk': 993,
        'message_received': 'tell me a joke',
        'message_recommendation': '[]',
        'message_choices': '',
        'message_sent': 'What do you call a bear with no teeth? A gummy bear.',
        'session_id': "2e403ca9-5172-4a7e-a7bb-38ef86197c8d",
        'session_id_wise_data': {
            '2e403ca9-5172-4a7e-a7bb-38ef86197c8d': 2,
            '55f1dd8d-27c9-4ea0-a25d-f792a26e0333': 1
        },
        'date_time': 'Jun 14 2021 11:52 AM',
        'channel_name': 'Web',
        'is_helpful': 'False',
        'widgets': '[]',
        'form_data_widget': ''
    }];
    message_list = message_list.reverse()
    html = '<div id="no-user-selected" style="margin-top: 200px;display:none;"><center><h5>Select a user to see the message history.</h5></center></div>'
    html += '<ul>'

    var table_html = "";
    var table_choices = "";
    var table_widgets = "";
    let session_ids_appended = []
    var events_query = ["silence_response", "silence_termination_response"];
    $('#user_chat_session_id_drop').show()
    $('#session_id_dropdown').empty().append('<div class="session-drop-data-not-found-div" id="session_drop_nodata_found">No result found</div>')
    $('.user-messages-search-wrapper').css('pointer-events', 'auto')
    $('.user-messages-search-wrapper').css('opacity', '1')
    document.getElementById("loader-user-message").style.display = 'none'
    for (var i = 0; i < message_list.length; i++) {
        let session_id = message_list[i].session_id
        if (!session_ids_appended.includes(session_id)) {
            html += '<div class="easychat-session-created-message-wrapper" id="' + session_id + '">' +
                '<div class="easychat-session-created-message-text-div">' +
                '<span>New session started</span>, ' +
                '<span class="user-chat-session-created-id-text"> Session ID: ' + session_id + '</span>, ' +
                '<span class="user-chat-query-count-text">User query count: ' + message_list[i]['session_id_wise_data'][session_id] + '</span>' +
                '</div>' +
                '</div>'
            session_ids_appended.push(session_id)
            let session_id_dropdown_html = '<li class="easychat-user-message-history-session-ids-item">' +
                '<span>' + session_id + '</span>' +
                '</li>'
            $('#session_id_dropdown').append(session_id_dropdown_html)
        }
        if (message_list[i]["message_recommendation"] != "[]" && message_list[i]["message_recommendation"] != "") {
            table_html = ''
            try {
                message_recommendation = JSON.parse(message_list[i]["message_recommendation"]);
            } catch (err) {
                message_recommendation = [];
            }

            for (var j = 0; j < message_recommendation.length; j++) {
                if (message_recommendation[j].name) {
                    table_html += get_recommendation_sent_html(message_recommendation[j].name, false);
                } else {
                    table_html += get_recommendation_sent_html(message_recommendation[j], false);
                }
            }
        } else {
            table_html = "";
        }


        if (message_list[i]["message_choices"] != "") {
            table_choices = ''
            message_choices = message_list[i]["message_choices"].split(",")
            for (var k = 0; k < message_choices.length; k++) {
                if (message_choices[k].includes("$$$")) {
                    table_choices += get_recommendation_sent_html(message_choices[k].replace("$$$", " "), false)
                }
                else {
                    table_choices += get_recommendation_sent_html(message_choices[k], false)
                }
            }
        } else {
            table_choices = "";
        }

        var msg_received = message_list[i]["message_received"].trim();

        if (events_query.includes(msg_received)) {
            msg_received = "";
        }

        if (msg_received) {
            html += get_message_received_html(message_list[i])
            // html += '<img src="/static/EasyChatApp/img/botIcon.svg" alt="" />'
        }

        let attached_file_src = message_list[i]["attached_file_src"]
        if (attached_file_src && attached_file_src.trim() != "") {
            // attached_file_src = window.location.origin + attached_file_src
            let attached_file_name = message_list[i]["attached_file_name"]
            // html += '<div style="display: none; margin-top: 2%"><label><input type="checkbox" name="input-checkbox-selected-misdashboard-" id="input-checkbox-selected-misdashboard-' + message_list[i]["pk"] + '" class="filled-in selected-misdashboard" ><span></span></label></left></div>'
            html += get_html_for_message_hitory_attachment(attached_file_name, attached_file_src)
            msg_received = ""
        }

        if (msg_received != "") {
            msg_received = get_masked_message(msg_received);
            // html += '<div style="display: none; margin-top: 2%"><label><input type="checkbox" name="input-checkbox-selected-misdashboard-" id="input-checkbox-selected-misdashboard-' + message_list[i]["pk"] + '" class="filled-in selected-misdashboard" ><span></span></label></left></div>'
            html += '<div class="easychat-query-send-message-text-div search-div" id="message-div-' + message_list[i]["pk"] + '">'
            html += sanitize_html(msg_received) + '</div>'
            html += '<a class="easychat-query-add-intent-wrapper" id="action-list-ul-' + message_list[i]["pk"] + '">'
            html += '<svg width="24" height="24" viewBox="0 0 24 24" fill="black" xmlns="http://www.w3.org/2000/svg">' +
                '<path d="M18 13H13V18C13 18.55 12.55 19 12 19C11.45 19 11 18.55 11 18V13H6C5.45 13 5 12.55 5 12C5 11.45 5.45 11 6 11H11V6C11 5.45 11.45 5 12 5C12.55 5 13 5.45 13 6V11H18C18.55 11 19 11.45 19 12C19 12.55 18.55 13 18 13Z" />' +
                '</svg>' +
                '<span>Add to intent</span></a>'
            // html += '<ul class="action-list-ul" id="action-list-ul-' + message_list[i]["pk"] + '"><li class="action-list-li action-list-add-to-intent" tab-index=-1>Add to intent</li></ul>'
        }
        html += '</li></div></div>'
        if (message_list[i]["form_data_widget"].length > 0) {
            widget_form_name = JSON.parse(message_list[i]["form_data_widget"])[0]
            form_fields_data = JSON.parse(message_list[i]["form_data_widget"])[1]
            html += append_form_widget_data(widget_form_name, form_fields_data, message_list[i].pk)
        }

        if (message_list[i]["message_sent"].includes("$$$")) {
            message_list[i]["message_sent"] = message_list[i]["message_sent"].split("$$$")
            var j;
            for (j = 0; j < message_list[i]["message_sent"].length - 1; j++) {
                message_list[i]["message_sent"][j] = message_list[i]["message_sent"][j].replace(new RegExp('\r?\n', 'g'), '<br>');
                var msg_sent = message_list[i]["message_sent"][j].trim();

                if (msg_sent != "") {
                    html += get_message_sent_html(message_list[i], msg_sent)
                }
            }
            message_list[i]["message_sent"][j] = message_list[i]["message_sent"][j].replace(new RegExp('\r?\n', 'g'), '<br>');
            msg_sent = message_list[i]["message_sent"][j].trim();
            if (msg_sent != "") {
                html += get_message_sent_html(message_list[i], msg_sent)
            }

            if (table_html != "") {
                html += table_html
            }
            if (table_choices != "") {
                html += table_choices
            }
            if (table_widgets != "") {
                html += table_widgets
            }
            html += '</li>'
        } else {
            message_list[i]["message_sent"] = message_list[i]["message_sent"].replace(new RegExp('\r?\n', 'g'), '<br>');
            message_list[i]["message_sent"] = message_list[i]["message_sent"].replace('</li></ul>', '');
            var msg_sent = message_list[i]["message_sent"].trim();
            if (msg_sent != "") {
                html += get_message_sent_html(message_list[i], msg_sent)
            }

            if (table_html != "") {
                html += table_html
            }
            if (table_choices != "") {
                html += table_choices
            }
            if (table_widgets != "") {
                html += table_widgets
            }
            html += '</li>'
        }
    }
    $('#session_id_dropdown_selected_text').text(session_ids_appended[0])
    $(".easychat-user-message-history-session-ids-item").click(function () {
        let session_id = $(this).children().text()
        $(".user-dropdown-session-selected-text").text(session_id);
        $("#user_chat_session_id_drop").toggleClass("user-chat-dropdown-open")
        $("#load_user_messages").scrollTo('#' + session_id, 1000);
    });
    // html += '</ul>'
    document.getElementById("load_user_messages").innerHTML = html;
    document.querySelectorAll(".easychat-query-add-intent-wrapper").forEach(function (element) {
        element.addEventListener("click", function (e) {
            document.querySelectorAll(".selected-misdashboard").forEach(function (element) {
                element.parentNode.style.display = "inline-block";
            });
            $(".easychat-user-custom-checkbox-div").show();
            // document.getElementById("close-selected-mis").style.display = "block";
            $('#chat-frame .content .messages ul li:last-child').css('padding-bottom', '70px')
            $(".easychat-query-add-intent-wrapper").css('visibility', 'hidden')
            $(".user-history-clearall-btn").css("visibility", "visible");
        });
    });
    if (scroll_to_session_id) {
        $(".user-dropdown-session-selected-text").text(scroll_to_session_id);
        setTimeout(function () {
            $("#load_user_messages").scrollTo('#' + scroll_to_session_id, 1000);
        }, 500)
    }
}
