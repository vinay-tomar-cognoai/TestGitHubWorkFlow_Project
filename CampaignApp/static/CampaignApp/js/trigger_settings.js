$(document).ready(function() {
    if(window.location.href.includes('voice-bot/settings')) {
        update_campaign_progress_bar(CAMPAIGN_CHANNEL);
        update_campaign_sidebar('template');

        $('#campaign_schedule_ivr_start_date').datepicker({
            changeMonth: true,
            changeYear: true,
            dayNamesMin: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
            dateFormat: 'yy/mm/dd',
            minDate: 0,
        });

        $('#campaign_schedule_ivr_end_date').datepicker({
            changeMonth: true,
            changeYear: true,
            dayNamesMin: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
            todayHighlight: true,
            dateFormat: 'yy/mm/dd',
            minDate: 0,
        });

        $('#campaign_schedule_ivr_start_time').datetimepicker({
            format: 'LT',
            useCurrent: true,

        });

        $('#campaign_schedule_ivr_end_time').datetimepicker({
            format: 'LT',
            useCurrent: true,
        });

        $('#number-of-retry-no-answer-dropdown').multiselect({
            nonSelectedText: 'Number of retry',
            enableFiltering: false,
            enableCaseInsensitiveFiltering: false,
            selectAll: false,
            includeSelectAllOption: false,
        });

        $('#caller-id-selection-dropdown').multiselect({
            nonSelectedText: 'No Caller ID Available',
            enableFiltering: false,
            enableCaseInsensitiveFiltering: false,
            selectAll: false,
            includeSelectAllOption: false,
        });
    }
})

Date.prototype.sameDay = function(d) {
    return this.getFullYear() === d.getFullYear()
      && this.getDate() === d.getDate()
      && this.getMonth() === d.getMonth();
}

function check_selected_days() {
    for (var day of WORKING_DAYS) {
        console.log(day);
        document.getElementById('weekday-' + day).checked = true;
    }
}

function get_retry_settings () {

    var retry_mechanism = $('input[name="retry_mechanism_cb"]:checked').val();
    var no_of_retries = document.getElementById('number-of-retry-no-answer-dropdown').value;
    var retry_interval = document.getElementById('retry-interval-no-answer-status').value;
    var is_busy_enabled = document.getElementById('status-busy').checked;
    var is_no_answer_enabled = document.getElementById('status-no-answer').checked;
    var is_failed_enabled = document.getElementById('status-failed').checked;

    return {
        retry_mechanism,
        no_of_retries,
        retry_interval,
        is_busy_enabled,
        is_no_answer_enabled,
        is_failed_enabled,
    }
}

function save_trigger_settings (el, is_next_clicked) {
    var caller_id = document.getElementById('caller-id-selection-dropdown').value;
    var start_date = $('#campaign_schedule_ivr_start_date').datepicker('getDate');
    var end_date = $('#campaign_schedule_ivr_end_date').datepicker('getDate');
    var start_time = document.getElementById('campaign_schedule_ivr_start_time').value;
    var end_time = document.getElementById('campaign_schedule_ivr_end_time').value;

    if (caller_id == "") {
        show_campaign_toast('Caller ID is not configured. Please connect operations team to configure the Caller ID.');
        return;        
    }

    if (start_date == "") {
        show_campaign_toast('Start date cannot be empty');
        return;
    }

    if (start_time == "") {
        show_campaign_toast('Start time cannot be empty');
        return;
    }

    if (end_date == "") {
        show_campaign_toast('End date cannot be empty');
        return;
    }

    if (end_time == "") {
        show_campaign_toast('End time cannot be empty');
        return;
    }

    var today = new Date();
    today.setHours(0,0,0,0)
    if (start_date < today) {
        show_campaign_toast('Cannot schedule campaign for past date');
        return;
    }

    if (end_date < start_date) {
        show_campaign_toast('End date should be greater or equal to start date.');
        return;
    }

    if (end_date.sameDay(start_date) && !check_end_time(start_time, end_time, start_date)) {
        show_campaign_toast('End time must be greater than start time.');
        return;
    }

    var {
        retry_mechanism,
        no_of_retries,
        retry_interval,
        is_busy_enabled,
        is_no_answer_enabled,
        is_failed_enabled,
    } = get_retry_settings();

    if (retry_interval < 2) {
        show_campaign_toast('Minimum interval time should be 2 mins');
        return;
    }

    if (!is_busy_enabled && !is_no_answer_enabled && !is_failed_enabled) {
        show_campaign_toast("Please select atleast one 'On status'");
        return;
    }

    var campaign_id = get_url_multiple_vars()['campaign_id'][0];

    var request_params = {
        bot_pk: BOT_ID,
        campaign_id: campaign_id,
        caller_id: caller_id,
        start_date: format_date(start_date),
        end_date: format_date(end_date),
        start_time: start_time,
        end_time: end_time,
        retry_mechanism: retry_mechanism,
        no_of_retries: no_of_retries,
        retry_interval: retry_interval,
        is_busy_enabled: is_busy_enabled,
        is_no_answer_enabled: is_no_answer_enabled,
        is_failed_enabled: is_failed_enabled,
    };

    var json_params = JSON.stringify(request_params);
    
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/voice-bot/settings/save/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                if (is_next_clicked) {
                    setTimeout(function() {
                        var review_url = window.location.origin + '/campaign/voice-bot/review/?bot_pk=' + BOT_ID + '&campaign_id=' + campaign_id;
                        console.log(review_url);
                        window.location.href = review_url;
                    }, 1000);
                }
                var error_message = "Campaign has been saved successfully";
                show_campaign_toast(error_message);
            } else if (response.status == 400) {
                show_campaign_toast(response.message)
            } else {
                var error_message = "Not able to save campaign. Please try again";
                show_campaign_toast(error_message);
            }
            if(!is_next_clicked) {
                element.innerText = "Save as Draft";
            }
        }
    }
    xhttp.send(params);
}

function format_date(d, date_first=false) {
    month = '' + (d.getMonth() + 1),
    day = '' + d.getDate(),
    year = d.getFullYear();

    if (month.length < 2) 
        month = '0' + month;
    if (day.length < 2) 
        day = '0' + day;

    if (date_first){
        return [day, month, year].join('-');
    }
    return [year, month, day].join('-');
}

function check_end_time(start_time, end_time, date) {
    start_time = convert_12_to_24_hour(start_time);
    end_time = convert_12_to_24_hour(end_time);

    var start_date = new Date(date.getFullYear(), date.getMonth(), date.getDate(), start_time.split(':')[0], start_time.split(':')[1]);
    var end_date = new Date(date.getFullYear(), date.getMonth(), date.getDate(), end_time.split(':')[0], end_time.split(':')[1]);

    return start_date.getTime() < end_date.getTime();
}

function convert_12_to_24_hour (time12h) {
    const [time, modifier] = time12h.split(' ');
  
    let [hours, minutes] = time.split(':');
  
    if (hours === '12') {
      hours = '00';
    }
  
    if (modifier === 'PM') {
      hours = parseInt(hours, 10) + 12;
    }
  
    return `${hours}:${minutes}`;
  }

function update_app_id() {
    var caller_id_select_element = document.getElementById("caller-id-selection-dropdown");
    var app_id = caller_id_select_element.options[caller_id_select_element.selectedIndex].getAttribute("app-id");
    document.getElementById("display_app_id").value = app_id;
}