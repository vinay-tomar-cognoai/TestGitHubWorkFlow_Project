let edit_select_work_timing_element = document.getElementById("edit-select-work-timing");
let edit_start_time_element = document.getElementById("edit-start-time");
let edit_end_time_element = document.getElementById("edit-end-time");
let working_day_option_input_element = document.getElementById("working-day-option-input");
let holiday_option_input_element = document.getElementById("holiday-option-input");
let edit_description_text_element = document.getElementById("edit-description-text");
let edit_response_text_element = document.getElementById("edit-response-text");
let edit_calendar_event_element = document.getElementById("edit_calendar_event");

function add_holiday_calendar() {

    var holiday_date = $("#selectDate").val().trim()
    var description = $("#description-text").val().trim()
    var auto_response = $("#response-text").val().trim()

    holiday_date = change_date_format_original(holiday_date);

    if (holiday_date == "" || !is_valid_date(holiday_date)) {

        show_easyassist_toast('Please enter valid date.');
        return;
    }

    if (new Date(holiday_date).toLocaleDateString() < new Date().toLocaleDateString()) {
        show_easyassist_toast("Unable to add holiday as the selected date is in the past");
        return;
    }

    if (description == "" || auto_response == "") {

        show_easyassist_toast('Description or Auto Response can not be empty.');
        return;
    }

    if (description.length > 90) {
        show_easyassist_toast('Description should be less than 90 characters.');
        return;
    }

    if (auto_response.length > 90) {
        show_easyassist_toast('Auto Response should be less than 90 characters.');
        return;
    }

    let request_params = {
        "holiday_date": holiday_date,
        "description": remove_special_characters_from_str(stripHTML(description)),
        "auto_response": remove_special_characters_from_str(stripHTML(auto_response)),
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", '/easy-assist/add-holiday-calendar/', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {

                show_easyassist_toast("Added successfully");
                setTimeout(function () {
                    let params = new URLSearchParams(window.location.search)
                    if (params.has('calendar_updated')) {
                        location.reload()
                    } else {
                        window.location.href = window.location.href.replace(/[\?#].*|$/, "?calendar_updated#pills-options-tab");
                    }
                }, 2000);
            } else if (response["status_code"] == "300") {
                show_easyassist_toast("Holiday for given date already exists.");
            } else {

                show_easyassist_toast("Unable to add new holiday due to internal server error.");
            }
        }
    }
    xhttp.send(params);
}

function add_working_hours(e) {

    let mode = document.getElementById("select-add-work-timing").value;
    if (mode == "") {
        show_easyassist_toast("Please select the method.");
        return;
    }
    
    let month = ""
    if (mode == "1") {
        month = document.getElementById("selet-month-time").value.trim();
    }

    let year = document.getElementById("selet-year-time").value.trim();
    let start_time = document.getElementById("start-time").value.trim();
    let end_time = document.getElementById("end-time").value.trim();

    if (mode == "2") {
        year = document.getElementById("selet-yearly-time").value.trim();
    }

    if (start_time == "" || end_time == "") {
        show_easyassist_toast("Please enter working hours.");
        return;
    }

    if (convert_time_to_24h(start_time) >= convert_time_to_24h(end_time)){
        show_easyassist_toast("Please enter valid working hours.");
        return;
    }

    let days_list = []
    let count = 0;
    let week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for (let i = 0; i < 7; i++) {
        value = document.getElementById("week-day-" + i).checked;
        if (value == false) {
            count = count + 1
            days_list.push(week_days[i])
        }
    }
    
    if (count == 7) {
        show_easyassist_toast("Please select working days.");
        return;
    }

    e.innerHTML = "Adding..."

    let request_params = {
        "month": month,
        "year": year,
        "start_time": start_time,
        "end_time": end_time,
        "days_list": days_list,
        "mode": mode
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", '/easy-assist/create-working-hours/', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            e.innerHTML = "Add"
            if (response["status_code"] == "200") {
                show_easyassist_toast("Working hours created successfully.");
                setTimeout(function () {
                    let params = new URLSearchParams(window.location.search)
                    if (params.has('calendar_updated')) {
                        location.reload()
                    } else {
                        window.location.href = window.location.href.replace(/[\?#].*|$/, "?calendar_updated#pills-options-tab");
                    }
                }, 2000);
            } else if (response["status_code"] == "300") {
                show_easyassist_toast("Working hours already exists.");
            } else {
                show_easyassist_toast("Unable to update changes due to internal server error.");
            }
        }
    }
    xhttp.send(params);
}

function edit_calendar_event(pk) {

    let selected_event = edit_select_work_timing_element.value.trim()
    let start_time = "";
    let end_time = "";
    let description = "";
    let auto_response = "";

    if (selected_event == "1") {
        start_time = edit_start_time_element.value.trim();
        end_time = edit_end_time_element.value.trim();

        if (start_time == "" || end_time == "") {
            show_easyassist_toast("Please enter working hours.");
            return;
        }

        if (convert_time_to_24h(start_time) >= convert_time_to_24h(end_time)) {
            show_easyassist_toast("Please enter valid working hours.");
            return;
        }

    } else {

        description = edit_description_text_element.value;
        auto_response = edit_response_text_element.value;
        if (description == "") {
            show_easyassist_toast('Please enter description.');
            return;
        }

        if (auto_response == "") {
            show_easyassist_toast('Please enter auto response.');
            return;
        }

        if (description.length > 90) {
            show_easyassist_toast('Description should be less than 90 characters.');
            return;
        }

        if (auto_response.length > 90) {
            show_easyassist_toast('Auto Response should be less than 90 characters.');
            return;
        }
    }

    let request_params = {
        pk: pk,
        "selected_event": selected_event,
        "start_time": start_time,
        "end_time": end_time,
        "description": description,
        "auto_response": auto_response,
    };
    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", '/easy-assist/edit-calendar-event/', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {

                show_easyassist_toast("Changes saved successfully");
                $("#edit_work_timing").modal("hide");
                setTimeout(function () {
                    location.reload();
                }, 2000);
            } else if (response["status_code"] == "300") {
                show_easyassist_toast(response["status_message"]);
            } else {
                show_easyassist_toast("Unable to update changes due to internal server error.");
            }
        }
    }
    xhttp.send(params);
}

function change_date_format_original(date) {
    let date_parts = date.split("-");
    date = date_parts[2] + "-" + date_parts[1] + "-" + date_parts[0];
    return date.trim();
}

function is_valid_date(date) {
    let formatted_date = change_date_format_original(date)
    date = new Date(date);
    formatted_date = new Date(formatted_date);
    let check_date = date instanceof Date && !isNaN(date)
    let check_formatted_date = formatted_date instanceof Date && !isNaN(formatted_date)
    return check_date || check_formatted_date;
}

function handle_edit_calendar_event_change() {
    let description = edit_description_text_element.value.trim();
    let auto_response = edit_response_text_element.value.trim();


    if (description && auto_response) {
        edit_calendar_event_element.disabled = false;
    } else {
        edit_calendar_event_element.disabled = true;
    }
}

function display_calender_event(event){
    if(event.value == 2){
        working_day_option_input_element.style.display = "none";
        holiday_option_input_element.style.display = "block";
    } else{
        working_day_option_input_element.style.display = "flex";
        holiday_option_input_element.style.display = "none";
    }
}

function populate_edit_modal_data(calendar_pk, calendar_event_type, start_time, end_time, description, auto_response) {
    working_day_option_input_element.style.display = "none";
    holiday_option_input_element.style.display = "none";
    edit_select_work_timing_element.value = "";
    edit_start_time_element.value = start_time;
    edit_end_time_element.value = end_time;
    edit_description_text_element.value = description;
    edit_response_text_element.value = auto_response;

    if (calendar_event_type == '1') {
        edit_select_work_timing_element.value = "1";
        working_day_option_input_element.style.display = "";
    } else {
        edit_select_work_timing_element.value = "2";
        holiday_option_input_element.style.display = "";
    }

    edit_calendar_event_element.setAttribute("onclick", `edit_calendar_event('${calendar_pk}')`)
    $("#edit_work_timing").modal("show");
}

function convert_time_to_24h(str_time) {
    const [time, modifier] = str_time.split(" ");

    let [hours, minutes] = time.split(":");

    if (hours === "12") {
        hours = "00";
    }

    if (modifier === "PM") {
        hours = parseInt(hours, 10) + 12;
    }

    return `${hours}:${minutes}`;
}
