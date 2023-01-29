
import axios from "axios";
import { get_character_limit } from "../common";
import { custom_decrypt, EncryptVariable, showToast, is_valid_date , change_date_format_original, stripHTML, getCsrfToken, get_params, is_mobile} from "../utils";


const state = {
    calendar_date: {
        current_month: window.SELECTED_MONTH,
        current_year: window.SELECTED_YEAR,
        selected_month_mobile:'',
        selected_year_mobile:'',
    },
    prev_month_calendar_obj_count: window.PREVIOUS_MONTH_CALENDAR_OBJECT_COUNT,
    next_month_calendar_obj_count: window.NEXT_MONTH_CALENDAR_OBJECT_COUNT,
}

$(window).ready(function () {

    if (!window.location.pathname.includes('calender')) {
        return;
    }

    state.calendar_date.current_month = window.SELECTED_MONTH;
    state.calendar_date.current_year = window.SELECTED_YEAR;
    state.prev_month_calendar_obj_count= window.PREVIOUS_MONTH_CALENDAR_OBJECT_COUNT,
    state.next_month_calendar_obj_count= window.NEXT_MONTH_CALENDAR_OBJECT_COUNT,

    $("#prev-month-id").on("click", function (e) {
        prev_next_month_calendar("PREV");
    });
    $("#next-month-id").on("click", function (e) {
        prev_next_month_calendar("NEXT");
    });
    $("#prev-month-agent-id").on("click", function (e) {
        if (state.prev_month_calendar_obj_count != '0') 
            
            prev_next_month_calendar("PREV");
        else {
            showToast('Calendar not created for that Month', 4000);
        }    
    });
    $("#next-month-agent-id").on("click", function (e) {
        if (state.next_month_calendar_obj_count != '0') {
            prev_next_month_calendar("NEXT");
        }
        else {
            showToast('Calendar not created for that Month', 4000);
        }    
    });

    initialize_date_picker();
    
    $(".edit-day-type-field input").click(function(e){
        let calendar_id = e.target.id;
        calendar_id = calendar_id.split('-')[5]
        if($(this).is(":checked"))  {
            $(".working-time").show();
            $(".holidays-content").hide();
            $("#day-type-working-id-"+calendar_id).show();
            $("#day-type-holiday-id-"+calendar_id).hide();
        } 
        else{
            $(".working-time").hide();
            $(".holidays-content").show();
            $("#day-type-working-id-"+calendar_id).hide();
            $("#day-type-holiday-id-"+calendar_id).show();
        }
    })

    $("#mobile-calendar-month-select li").click(function(){
        $("#mobile-calendar-month-select li").removeClass("active-ui-selected");
        $(this).addClass("active-ui-selected");
    });

    $("#mobile-calendar-year-select li").click(function(){
        $("#mobile-calendar-year-select li").removeClass("active-ui-selected");
        $(this).addClass("active-ui-selected");
    });

    $('#mobile-select-month-year-modal').on('show.bs.modal', function(event) {
        setTimeout(function() {
            let $elem_month = $('#mobile-month-select-id')
            let $container_month = $("#mobile-calendar-month-select")
            $container_month.scrollTop(0)
            let temp1 = $container_month.offset().top
            $container_month.scrollTop($elem_month.position().top - temp1);

            let $elem_year = $('#mobile-year-select-id')
            let $container_year = $("#mobile-calendar-year-select")
            $container_year.scrollTop(0)
            let temp2 = $container_year.offset().top
            $container_year.scrollTop($elem_year.position().top - temp2);
            }, 300)
    });

    $(".mobile-select-month-div li").on('click', function(e) {
        state.calendar_date.selected_month_mobile = e.target.value;
    });
    $(".mobile-select-year-div li").on('click', function(e) {
        state.calendar_date.selected_year_mobile = e.target.value;
    });

    if(is_mobile()) {
        $(".month-day-detail").on('click', function(e) {
            replace_event_card(e)
        }); 
    }

});

function prev_next_month_calendar(signal) {
    let month = get_current_month();
    let year = get_current_year();
    let current_month;
    let current_year;

    if (signal == "PREV") {
        let prev_month_year = get_prev_month(month, year);
    
        current_month = prev_month_year.month;
        current_year = prev_month_year.year;
    }
    else if (signal == "NEXT") {
        let next_month_year = get_next_month(month, year);
    
        current_month = next_month_year.month;
        current_year = next_month_year.year;
    }
    
    window.location.href =
    "?selected_month=" +
    current_month +
    "&selected_year=" +
    current_year;
}

function get_prev_month(month, year) {
    month = Number(month)
    year = Number(year)

    if (month == 1) {
        month = 12;
        year -= 1;  
    }
    else {
        month -= 1;
    }
    month = String(month)
    year = String(year)
    return {month, year};
}

function get_next_month(month, year) {
    month = Number(month)
    year = Number(year)

    if (month == 12) {
        month = 1;
        year += 1;  
    }
    else {
        month += 1;
    }
    month = String(month)
    year = String(year)
    return {month, year};
}

function add_holiday_calender() {

    var holiday_dates = $("#modal-holiday-date").val().trim()
    var description = $("#modal-holiday-description").val().trim()
    var auto_response = $("#modal-holiday-autoreponse").val().trim()

    if (holiday_dates == "") {
        showToast('Please enter holiday date(s).', 4000);
        return;
    }

    description = stripHTML(description);
    auto_response = stripHTML(auto_response);

    var holiday_date_array = holiday_dates.split(",");
    holiday_date_array.forEach(function(part, index) {
        this[index] = this[index].trim();

        this[index] = change_date_format_original(this[index])

        if (this[index] == "" || !is_valid_date(this[index])) {

            showToast('Please enter valid date.', 4000);
            return;
        }

    }, holiday_date_array);

    if(description == "") {
        showToast('Please enter Description to proceed', 4000);
        return;
    }

    if(auto_response == "") {
        showToast('Please enter Auto Response to proceed', 4000);
        return;
    }

    const char_limit = get_character_limit();

    if (description.length > char_limit.medium) {
        showToast(`Exceeding character limit of ${char_limit.medium} characters in description`, 2000);
        return;
    }

    if (auto_response.length > char_limit.large) {
        showToast(`Exceeding character limit of ${char_limit.large} characters in description`, 2000);
        return;
    }

    if (holiday_dates == '') {
        holiday_date_array = [];
    }
    var json_string = JSON.stringify({
        holiday_date_array: holiday_date_array,
        description: description,
        auto_response: auto_response,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string;
    xhttp.open("POST", '/livechat/add-holiday-calender/', true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token); 
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status_code"] == "200") {

                showToast("Added successfully", 3000)
                setTimeout(()=>{location.reload();}, 2000);
            } else if (response["status_code"] == "300"){
                showToast("Holiday for given date already exists.", 2000)
            } else if (response["status_code"] == "400") {
                showToast("Holiday dates(s) not selected.", 2000)
            }
            else {

                showToast("Unable to add new holiday due to internal server error.", 3000);
            }
        }
    }
    xhttp.send(params);
}

function delete_calender_event(pk) {

    var json_string = JSON.stringify({
        pk: pk
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string;
    xhttp.open("POST", '/livechat/delete-calender-event/', true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status_code"] == "200") {

                showToast("Deleted successfully", 3000);
                setTimeout(()=>{location.reload();}, 2000);
            } else {

                showToast("Unable to delete due to internal server error.", 3000);
            }
        }
    }
    xhttp.send(params);
}

function edit_calender_event(pk) {

    let selected_event = document.getElementById("calendar-edit-day-type-input-" + pk).checked
    let start_time = "";
    let end_time = "";
    let description = "";
    let auto_response = "";

    selected_event = selected_event == true ? "1" : "2"
    if (selected_event == "1") {

        start_time = $("#edit-start-working-time-" + pk).val()
        end_time = $("#edit-end-working-time-" + pk).val()

        if (start_time == "" || end_time == "") {
            showToast("Please enter working hours.", 2000);
            return;
        }

        if (start_time >= end_time) {

            showToast("Please enter valid working hours.", 2000);
            return;
        }
    } else {

        description = $("#modal-holiday-description-" + pk).val()
        auto_response = $("#modal-holiday-autoreponse-" + pk).val()

        if(description == "") {
            showToast('Please enter Description to proceed', 4000);
            return;
        }

        if(auto_response == "") {
            showToast('Please enter Auto Response to proceed', 4000);
            return;
        }
    }
    
    var json_string = JSON.stringify({
        pk: pk,
        selected_event: selected_event,
        start_time: start_time,
        end_time: end_time,
        description: description,
        auto_response: auto_response,
    });
    
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string;
    xhttp.open("POST", '/livechat/edit-calender-event/', true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status_code"] == "200") {

                showToast("Changes saved successfully", 3000);
                setTimeout(()=>{location.reload();}, 2000);
            } else {

                showToast("Unable to update changes due to internal server error.", 3000);
            }
        }
    }
    xhttp.send(params);
}

function add_working_hours(e) {

    let mode = document.getElementById("select-work-mode").value;
    if (mode == "") {
        showToast("Please select the method.", 2000);
        return;
    }
    let month = ""
    if (mode == "1" || mode == "3") {
        month = document.getElementById("select-working-month").value;
    }
    let year = document.getElementById("select-working-year").value;
    let start_time = document.getElementById("start-working-time").value;
    let end_time = document.getElementById("end-working-time").value;

    if (start_time == "" || end_time == "") {
        showToast("Please enter working hours.", 2000);
        return;
    }

    if (start_time >= end_time) {

        showToast("Please enter valid working hours.", 2000);
        return;
    }

    let days_list = []
    let count = 0;
    let week_days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    for (var i = 0; i < 7; i++) {
        value = document.getElementById("indeterminate-checkbox-" + i).checked;
        if (value == false) {
            count = count + 1
            days_list.push(week_days[i])
        }
    }
    if (count == 7) {
        showToast("Please select working days.", 2000);
        return;
    }
    var json_string = JSON.stringify({
        "month": month,
        "year": year,
        "start_time": start_time,
        "end_time": end_time,
        "days_list": days_list,
        "mode": mode
    });
    e.innerHTML = "Adding..."
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string;
    xhttp.open("POST", '/livechat/create-working-hours/', true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token); 
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            e.innerHTML = "Add"
            if (response["status_code"] == "200") {
                alert("Working hours created successfully.")
                // showToast({ "html": "Working hours created successfully." }, 3000);
                setTimeout(()=>{location.reload();}, 2000);
            } else if (response["status_code"] == "300") {

                showToast("Working hours already exists.", 2000);
            } else {

                showToast("Unable to update changes due to internal server error.", 3000);
            }
        }
    }
    xhttp.send(params);
}

function set_default_calender() {

    let curren_date = new Date();
    let current_month = curren_date.getMonth() + 1;
    let current_year = curren_date.getFullYear();

    let mode = "1";
    let month = String(current_month)
    let year = String(current_year)

    let start_time = "00:00";
    let end_time = "23:59";

    let days_list = ['Sunday'];

    var json_string = JSON.stringify({
        "month": month,
        "year": year,
        "start_time": start_time,
        "end_time": end_time,
        "days_list": days_list,
        "mode": mode
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string;
    xhttp.open("POST", '/livechat/create-working-hours/', true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token); 
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status_code"] == "200") {

                showToast("Working hours created by default.", 3000);
                setTimeout(()=>{location.reload();}, 2000);
            }
        }
    }
    xhttp.send(params);
}

function load_calendar_for_other_months(selected_month, selected_year) {
    let mode = "1";
    let month = String(selected_month)
    let year = String(selected_year)

    let start_time = "00:00";
    let end_time = "23:59";

    let days_list = ['Sunday'];

    const json_string = JSON.stringify({
        "month": month,
        "year": year,
        "start_time": start_time,
        "end_time": end_time,
        "days_list": days_list,
        "mode": mode
    });

    const params = get_params(json_string);
    let config = {
        headers: {
          'X-CSRFToken': getCsrfToken(),
        }
    }
    axios.post('/livechat/create-working-hours/', params, config)
        .then(response => {
            response = custom_decrypt(response.data)
            response = JSON.parse(response)
            
            if (response.status_code == '200') {
                showToast("Working hours created by default.", 3000);
                setTimeout(()=>{location.reload();}, 2000);
            } else {
                showToast('Failed to create working hours. Please try again later', 2000);
            }
        })
        .catch((err) => {
            console.log(err);
            showToast('Failed to create working hours. Please try again later', 2000);
        });
}

function initialize_date_picker() {
    let curr_month = get_current_month();
    let curr_year = get_current_year();

    curr_month = Number(curr_month) - 1;
    curr_year = Number(curr_year);

    $('#modal-holiday-date').datepicker({ 
        format: "dd-mm-yyyy",
        multidate: true,
        multidateSeparator: " , ",
        defaultViewDate: { 
            year: curr_year, 
            month: curr_month, 
            day: 1 
        }
    });
}

function get_current_month() {
    return state.calendar_date.current_month;
}
function get_current_year() {
    return state.calendar_date.current_year;
}

function get_selected_month_mobile() {
    if (state.calendar_date.selected_month_mobile != "") {
        return state.calendar_date.selected_month_mobile;
    }
    return state.calendar_date.current_month;
}
function get_selected_year_mobile() {
    if (state.calendar_date.selected_year_mobile != "") {
        return state.calendar_date.selected_year_mobile;
    }
    return state.calendar_date.current_year;
}

function replace_event_card(e) {
    const element = e.currentTarget;
    let event_type = element.dataset.event_type;
    let event_date = element.dataset.event_date.split('-');
    let start_time = element.dataset.start_time;
    let end_time = element.dataset.end_time;
    let description = element.dataset.description;

    let changing_element = document.getElementById("mobile-calendar-card");
    let html = `<div class="mobile-calendar-date-status" id="mobile-calendar-card">`
    if (event_type == '1') {
        html += 
        `<div class="date-current-status-timing-div">
        <div class="date-status-div">
        <p>${event_date[0]} ${event_date[1]} ${event_date[2]}
        <span class="current-date-day">&nbsp; ${event_date[3]} </span>
        <span class="current-status">Working</span>
        </p>
        </div>
        <div class="date-event-timing">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M7.00001 13.6666C6.0889 13.6666 5.22779 13.4916 4.41668 13.1416C3.60557 12.7916 2.89723 12.3139 2.29168 11.7083C1.68612 11.1028 1.20834 10.3944 0.858343 9.58331C0.508343 8.7722 0.333344 7.91109 0.333344 6.99998C0.333344 6.08887 0.508343 5.22776 0.858343 4.41665C1.20834 3.60554 1.68612 2.8972 2.29168 2.29165C2.89723 1.68609 3.60557 1.20831 4.41668 0.858313C5.22779 0.508313 6.0889 0.333313 7.00001 0.333313C7.91112 0.333313 8.77223 0.508313 9.58334 0.858313C10.3945 1.20831 11.1028 1.68609 11.7083 2.29165C12.3139 2.8972 12.7917 3.60554 13.1417 4.41665C13.4917 5.22776 13.6667 6.08887 13.6667 6.99998C13.6667 7.91109 13.4917 8.7722 13.1417 9.58331C12.7917 10.3944 12.3139 11.1028 11.7083 11.7083C11.1028 12.3139 10.3945 12.7916 9.58334 13.1416C8.77223 13.4916 7.91112 13.6666 7.00001 13.6666ZM9.45001 10.2166L10.2 9.46665L7.55001 6.79998V3.44998H6.55001V7.19998L9.45001 10.2166Z" fill="#CBCACA"/>
        </svg>
        <span class="date-working-hour-timing">${start_time} 
        <span class="time-hyphen"></span>${end_time} 
        </span>
        </div>
        </div>`;
    }
    else if (event_type == '2') {
        html += 
        `<div class="date-current-status-timing-div status-holiday">
        <div class="date-status-div">
        <p>${event_date[0]} ${event_date[1]} ${event_date[2]}
        <span class="current-date-day">&nbsp;${event_date[3]} </span> 
        <span class="current-status">Holiday</span>
        </p>
        </div>
        <div class="date-event-timing">
        ${description}
        </div>
    </div>`
    }
    html += `</div>`
    changing_element.innerHTML = html;
}

export {
    add_holiday_calender,
    delete_calender_event,
    edit_calender_event,
    add_working_hours,
    set_default_calender,
    load_calendar_for_other_months,
    prev_next_month_calendar,
    get_selected_month_mobile,
    get_selected_year_mobile
};