 var monthly_index_global = ""
 var selected_list_class = "easyassist-option-selected";
 var custom_days = []
 var update_schedule_list= []
 var entries_per_page = 10
 var global_metadata, global_data_obj, global_current_slot_pk, global_schedule_pk, global_uid
 DELETE_MODE = 'none'
 TABLE_SELECTED = false
 let selected_schedules_list = []
 RELOADED_PAGE = false
 ENTRIES_IN_PAGE = 25

function create_time_slot_blur_event() {

    $(".time_slots").blur(function(){
    var value = $(this).val()

    var time_slots_elements = document.getElementsByClassName("time_slots")

    for (var element of time_slots_elements) {
            if(element.value == value && $(element).attr('data-content') != $(this).attr('data-content'))
            {   show_campaign_toast('Time slot already exists, Please select a different slot')
                $(this).val('')
                return
            }
        }
  
})

}

$(document).ready(function() {
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    });
    let location_url = get_url_multiple_vars();
    let reload = location_url['r']
    RELOADED_PAGE = (reload) ? (reload[0] === "true") : false
    reset_current_wrapper()
    let page = location_url['p']
    reset_upcoming_schedules_table("", "", (page) ? parseInt(page[0]) : 1, true, false)
    
    update_campaign_progress_bar('Whatsapp Business');
    update_campaign_sidebar('review');

    window.addEventListener("resize", function() {
        if (window.innerWidth >= 600) {
            document.getElementById("accordionSidebar").classList.remove("toggled");
        }
    });
    if (window.innerWidth >= 600) {
        document.getElementById("accordionSidebar").classList.remove("toggled");
    }

    $('.custom-timepicker-input').val(getCurrentTime())

    $('[data-bs-toggle="tooltip"]').tooltip();

    document.getElementById("edit-single").checked = true;
    $('#audience-batch-select-dropdown').selectpicker({
        liveSearchPlaceholder: 'Search Audience Batch Name',
        noneResultsText: "No results matched",
        liveSearch: true,
        size: 4
    });
    $('#audience-batch-select-dropdown').selectpicker('refresh');

});

function initialize_datepicker_and_timepicker(mode="") {
    if(document.getElementById("campaign-schedule-list-select")) {
        var select_el = document.getElementById("campaign-schedule-list-select");
        var select_element_obj = new EasyassistCustomSelect(select_el, null, null);
    }

    var dayNamesMax = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    $('#campaign_datepicker').datepicker({
        changeMonth: true,
        changeYear: true,
        dayNamesMin: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        dateFormat: 'dd-mm-yy',
        yearRange: '2000:2100',
        minDate: 0,
        onSelect: function(dateText) {   
            $('#campaign_datepicker').addClass('active-picker-input')
            $('#campaign_datepicker').css("border","");
            call_update_dropdown_options()
            var changed_option = document.querySelectorAll("." + selected_list_class + " span")[0].innerHTML 
            document.getElementsByClassName("easyassist-dropdown-selected")[0].innerText = changed_option
            let current_date = $('#campaign_datepicker').datepicker('getDate');
            current_date.setDate(current_date.getDate() + 1)
            if(current_date >= $("#campaign_end_datepicker").datepicker('getDate')){
                $("#campaign_end_datepicker").datepicker("setDate", current_date)
                $("#campaign_end_datepicker").datepicker("option", "minDate", current_date)
            }else{
                $("#campaign_end_datepicker").datepicker("option", "minDate", current_date)
            }

        },
    });
        
        
    $('#campaign_datepicker').keydown(function(event) {event.preventDefault()});

    $('#campaign_datepicker').datepicker('setDate', new Date());
    call_update_dropdown_options()

    $('#campaign_end_datepicker').datepicker({
        changeMonth: true,
        changeYear: true,
        dayNamesMin: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        dateFormat: 'dd-mm-yy',
        yearRange: '2000:2100',
        minDate: 0,
    });
    
    $('#campaign_end_datepicker').keydown(function(event) {event.preventDefault()});
    let current_date = $('#campaign_datepicker').datepicker('getDate');
    current_date.setDate(current_date.getDate() + 1)
    $("#campaign_end_datepicker").datepicker("option", "minDate", current_date)
    $('#campaign_end_datepicker').datepicker('setDate', current_date);

    $('#campaign_filter_custom_start_date').datepicker({
        changeMonth: true,
        changeYear: true,
        dayNamesMin: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        dateFormat: 'dd-mm-yy',
        yearRange: '2000:2100',
        minDate: 0,
        maxDate: '+3Y',
        onSelect: function(date) {
            $('#campaign_filter_custom_start_date').addClass('active-picker-input')
            $('#campaign_filter_custom_start_date').css("border","");
            let current_date = $('#campaign_filter_custom_start_date').datepicker('getDate');

            if(current_date > $("#campaign_filter_custom_end_date").datepicker('getDate')){
                $("#campaign_filter_custom_end_date").datepicker("setDate", current_date)
                $("#campaign_filter_custom_end_date").datepicker("option", "minDate", current_date)
            }else{
                $("#campaign_filter_custom_end_date").datepicker("option", "minDate", current_date)
            }
        }
    });
    $('#campaign_filter_custom_start_date').keydown(function(event) {event.preventDefault()});
    $('#campaign_filter_custom_end_date').datepicker({
        changeMonth: true,
        changeYear: true,
        dayNamesMin: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        dateFormat: 'dd-mm-yy',
        yearRange: '2000:2100',
        minDate: 0,
        maxDate: '+3Y',
        onSelect: function(date) {
            $('#campaign_filter_custom_end_date').addClass('active-picker-input')
            $('#campaign_filter_custom_end_date').css("border","");
            end_date = $('#campaign_filter_custom_end_date').datepicker('getDate')
            start_date = $('#campaign_filter_custom_start_date').datepicker('getDate')
            if (!start_date){
                start_date = new Date() ;
            }
            start_date = format_date(start_date)
            end_date = format_date(end_date)
            RELOADED_PAGE = true;
            get_upcoming_schedules_data(start_date, end_date, 1, false)
        }


    });
    $('#campaign_filter_custom_end_date').keydown(function(event) {event.preventDefault()});
    $('#edit_campaign_datepicker').datepicker({
        changeMonth: true,
        changeYear: true,
        dayNamesMin: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        dateFormat: 'dd-mm-yy',
        yearRange: '2000:2100',
        minDate: 0,
        constrainInput:"true",
    });
    $('#edit_campaign_datepicker').keydown(function(event) {event.preventDefault()});
}

function set_date_value_for_filter(){
    let location_url = get_url_multiple_vars();
    let start_date = location_url['start_date']
    let end_date = location_url['end_date']
    $('#campaign_filter_custom_start_date').datepicker('setDate', (start_date) ? new Date(start_date[0]) : new Date());
    $('#campaign_filter_custom_end_date').datepicker('setDate', (end_date) ? new Date(end_date[0]) : new Date());
}

var dayNamesMax = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
var dayNamesMin = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

 function call_update_dropdown_options() {
    var date = $("#campaign_datepicker").datepicker('getDate');
    var dayOfWeek = date.getUTCDay();
    update_dropdown_options(dayOfWeek)
 }
 function update_dropdown_options(dayOfWeek) {

    var monthly_index = get_days_and_week_index(dayOfWeek)
    var all_dropdown_options = document.querySelectorAll(".easyassist-custom-dropdown-option-container li span")
    var selected_date = $("#campaign_datepicker").datepicker( 'getDate' )
    var annual_date = format_annual_date(selected_date)
    var weekend_or_weekday = "Every Weekend (Sat-Sun)"

    if (dayOfWeek >= 0 && dayOfWeek <=4) {
        weekend_or_weekday = "Every Weekday (Mon-Fri)"
    }
    $('#campaign-schedule-list-select option:contains("Weekly")').each(function(){
                all_dropdown_options[2].innerText = "Weekly on " + dayNamesMax[dayOfWeek] 
    });

    

    $('#campaign-schedule-list-select option:contains("Monthly")').each(function(){
                monthly_index_global = monthly_index
                all_dropdown_options[3].innerText = "Monthly on " + monthly_index + " " + dayNamesMax[dayOfWeek]

    });

    // $('#campaign-schedule-list-select option:contains("Annually")').each(function(){
    //             all_dropdown_options[4].innerText = "Annually on " + annual_date

    // });


    $('#campaign-schedule-list-select option:contains("Every")').each(function(){
                 all_dropdown_options[4].innerText = weekend_or_weekday
    });

    // $('#campaign-schedule-list-select option:contains("Weekly")').each(function(){
    //             var $this = $(ref);
    //             $this.text("Weekly on " + dayNamesMax[dayOfWeek]);    
    // });
 }


 function get_days_and_week_index(day_index) {
    var day_name = dayNamesMax[day_index]
    var week_indexes = ["First", "Second", "Third", "Fourth", "Last"]
    var d = $("#campaign_datepicker").datepicker( 'getDate' ),
        month = d.getMonth(),
        days = [],
        selected_date = $("#campaign_datepicker").datepicker( 'getDate' )
    d.setDate(1);
    // Get the first Monday in the month
    if (day_index == 6) {
        day_index = 0
    }
    else {
        day_index = day_index + 1
    }
    while (d.getDay() !== (day_index)) {
        d.setDate(d.getDate() + 1);
    }

    // Get all the other Mondays in the month
    while (d.getMonth() === month) {
        days.push(d.getDate() + "");
        d.setDate(d.getDate() + 7);
    }
    
    var index = days.indexOf(selected_date.getDate()+"")
    if (index == days.length - 1) {
        return "Last"
    } else {
        return week_indexes[index]
    }

}

function format_annual_date(date) {
    const day = date.toLocaleString('default', { day: '2-digit' });
    const month = date.toLocaleString('default', { month: 'short' });

    return day + " " + month
}

function format_date(d) {
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2) 
        month = '0' + month;
    if (day.length < 2) 
        day = '0' + day;

    return [year, month, day].join('-');
}

function initialize_timepicker_events() {

$('input[name="radio-group1"]').on("change", function(event) {
    if($('#ends_on').is(':checked')){
        $(".custom-campaign-date-card").show();
    } else {
        $('.custom-campaign-date-card').hide();
    }
});

$("#campaign-schedule-add-time-slot-input").focus(function() {

    $('.campaign-schedule-add-time-slot-btn').hide();


});
$("#campaign-schedule-add-time-slot-input").focusout(function() {
    // var value = $("#campaign-schedule-add-time-slot-input").val();
    $('.campaign-schedule-add-time-slot-btn').show();
    $("#campaign-schedule-add-time-slot-input").val(' ');


});

$("#campaign-schedule-add-time-slot-input").keydown(function(event) {
    var value = $("#campaign-schedule-add-time-slot-input").val();
    if (event.keyCode == '13') {
        event.preventDefault();

        var time_slots_elements = document.getElementsByClassName("time_slots")
        var total_slot_length = time_slots_elements.length
        total_slot_length += 1
        if(total_slot_length > 24){
            show_campaign_toast("Can't add more than 24 time slots")
            document.getElementById("campaign-schedule-add-time-slot-input").blur()
            return
        }

        for (var element of time_slots_elements) {
            if(element.value == value)
            {   show_campaign_toast('Time slot already exists, Please select a different slot')
                return
            }
        }
        $('.campaign-schedule-add-time-slot-btn').show();

        if (value.trim() != '')
        {
            $("#campaign-schedule-add-time-slot-input").val(' ');



            $("#campaign-schedule-slots-wrapper .campaign-schedule-input-item:last").before(`

                        <div class="campaign-schedule-input-item">
                                            <button class="campaign-schedule-remove-item-btn" onclick="remove_slots_function(this);">
                                                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                                                    <circle cx="8" cy="8" r="8" fill="#F8F8F8"/>
                                                    <path d="M3.89705 4.05379L3.96967 3.96967C4.23594 3.7034 4.6526 3.6792 4.94621 3.89705L5.03033 3.96967L8 6.939L10.9697 3.96967C11.2626 3.67678 11.7374 3.67678 12.0303 3.96967C12.3232 4.26256 12.3232 4.73744 12.0303 5.03033L9.061 8L12.0303 10.9697C12.2966 11.2359 12.3208 11.6526 12.1029 11.9462L12.0303 12.0303C11.7641 12.2966 11.3474 12.3208 11.0538 12.1029L10.9697 12.0303L8 9.061L5.03033 12.0303C4.73744 12.3232 4.26256 12.3232 3.96967 12.0303C3.67678 11.7374 3.67678 11.2626 3.96967 10.9697L6.939 8L3.96967 5.03033C3.7034 4.76406 3.6792 4.3474 3.89705 4.05379L3.96967 3.96967L3.89705 4.05379Z" fill="#E53E3E"/>
                                                    </svg>

                                            </button>
                                            <input type="text" data-content="`+Math.random()+`" class="campaign-schedule-input-field schedule-timepicker time_slots new_time_slots" value="${value}" />
                                        </div>

            `);


            $('.schedule-timepicker').datetimepicker({
                format: 'LT',
            });

            create_time_slot_blur_event()

            document.getElementById("campaign-schedule-add-time-slot-input").blur()
        } else {
            document.getElementById("campaign-schedule-add-time-slot-input").blur()
        }
    }

    });
}

function remove_slots_function(ele) {
    $(ele).parent().remove();

}

function get_day_as_per_choice(choice_selected, start_date) {

    var date = $("#campaign_datepicker").datepicker('getDate');
    var dayOfWeek = date.getUTCDay();
    var days = []
    var choice_display_val = document.getElementsByClassName("easyassist-dropdown-selected")[0].innerText
    if(choice_selected == "does_not_repeat") {
        return []
    }  else if (choice_selected == "daily") {
        return dayNamesMin
    } else if (choice_selected.indexOf("weekly") != -1) {
        days.push(dayNamesMin[dayOfWeek])
        return days
    } else if (choice_selected.indexOf("monthly") != -1) {
        days.push(dayNamesMin[dayOfWeek] + "-" + monthly_index_global)
        return days
    } else if(choice_selected.indexOf("annually") != -1) {
        return []  
    } else if(choice_display_val.indexOf("Every Weekday") != -1) {
        return ["Mon", "Tue", "Wed", "Thu", "Fri"]
    } else if(choice_display_val.indexOf("Every Weekend") != -1) {
        return ["Sun", "Sat"]
    } else {
        let all_days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        save_custom_modal();
        var end_date = $("#campaign_end_datepicker").datepicker('getDate')
        var today_date = start_date
        var days_gap = difference_in_dates(today_date, end_date)

        if(document.getElementById("ends_on").checked) {
            if(days_gap > 365) {
                $('#campaign_end_datepicker').removeClass('active-picker-input')
                $('#campaign_end_datepicker').css("border","1px solid #ff0000");
                $('#create_error_message').text("End date can't be greater than 1 year in custom choice.");
                document.getElementById('create_modal_error_message').style.display = "block";
                return "false";
            }
        }

        if(custom_days.length == 0)
        {   
            $('#campaign_end_datepicker').removeClass('active-picker-input')
            $('#campaign_end_datepicker').css("border","1px solid #ff0000");
            $('#create_error_message').text("Please select atleast one day in custom choice");
            document.getElementById('create_modal_error_message').style.display = "block";
            return "false";
        } else {
            if (Math.ceil(days_gap) < 6){
                let not_in_range = 0
                $.each(custom_days, function(idx, val){
                    let selected_date = all_days.indexOf(val);
                    if(selected_date < today_date.getDay() || selected_date > end_date.getDay()){
                        not_in_range += 1;
                    }
                })   
                if (custom_days.length == not_in_range){
                    $('#campaign_end_datepicker').removeClass('active-picker-input')
                    $('#campaign_end_datepicker').css("border","1px solid #ff0000");
                    $('#create_error_message').text("Day(s) chosen doesn't fall under the date range");
                    document.getElementById('create_modal_error_message').style.display = "block";
                    custom_days = "false"
                }
            }
            return custom_days
        }
    }
}

function difference_in_dates(date1, date2) {
    var difference_in_time = date2.getTime() - date1.getTime();
  
    // To calculate the no. of days between two dates
    var difference_in_days = difference_in_time / (1000 * 3600 * 24);
    return difference_in_days
}

function edit_schedule(metadata, data_obj, current_slot_pk) {
    if (document.getElementById("edit-single").checked) {
        edit_schedule_after_save("single_occurence", metadata, data_obj, current_slot_pk)
    }
    else if (document.getElementById("edit-current-remaining").checked) {
        edit_schedule_after_save("current_and_remaing", metadata, data_obj, current_slot_pk)
    }
}

function call_delete_schedule(schedule_pk, current_slot_pk, uid) {
    if (document.getElementById("delete-single").checked) {
        delete_schedule_after_click("single_occurence", schedule_pk, current_slot_pk, uid)
    }
    else if (document.getElementById("delete-multiple").checked) {
        delete_schedule_after_click("current_and_remaing", schedule_pk, current_slot_pk, uid)
    }
}

function delete_selected_items() {
    $("#campaign_multiple_schedule_delete_modal").modal("hide")
    if (DELETE_MODE == 'whole_campaign'){
        delete_schedule_after_click(DELETE_MODE, -1, -1, -1)
    } else{

        var selected_items = $('.campaign_select_row_cb[type=checkbox]:checked')
        var list_of_pks_to_be_deleted = []
        for (var i=0; i<selected_items.length; i++) {
            list_of_pks_to_be_deleted.push(selected_items[i].getAttribute("data-content"))
        }
        delete_schedule_after_click("selected_items", -1, -1, -1, list_of_pks_to_be_deleted)

    }
    

}


function delete_schedule_after_click(mode_occurence, schedule_pk, current_slot_pk, uid, selected_items=[]) {
    $("#campaign_schedule_delete_modal").modal('hide')
    var request_params = {
        'bot_pk': BOT_ID,
        'campaign_id': get_url_multiple_vars()['campaign_id'][0],
        'mode_occurence': mode_occurence,
        'schedule_pk': schedule_pk,
        'current_slot_pk': current_slot_pk,
        'uid': uid,
        'selected_items': selected_items
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/delete-schedule-campaign/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                var campaign_id = response["campaign_id"]
                show_create_delete_toast("deleted_successfull_note_toaster")
                selected_schedules_list = []
                clear_selected_campaign()
                reset_upcoming_schedules_table("", "", 1, true, false)

            } else {
                var error_message = response.message;
                show_campaign_toast(error_message);
            }
        }
    }
    xhttp.send(params);
    
}

function show_create_delete_toast(classname) {
    
    document.getElementsByClassName(classname)[0].style.display = "flex"
    setTimeout(function() {
        document.getElementsByClassName(classname)[0].style.display = "none"
    }, 3000);
}


function edit_schedule_after_save(mode_occurence, original_metadata, original_data_obj, current_slot_pk) {
    $("#campaign_schedule_edit_modal").modal('hide')

    var choice_selected = document.querySelectorAll("." + selected_list_class + " input")[0].value 
    var start_date = $("#edit_campaign_datepicker").datepicker( 'getDate' )

    let update_time_slot_value = document.getElementById('edit_campaign_timepicker').value;
    let time_value = update_time_slot_value.trim();
    let time_regex = /^(00|0[0-9]|1[012]):[0-5][0-9] ?((a|p)m|(A|P)M)$/;

    if (time_regex.test(time_value)==false){
        $('#edit_campaign_timepicker').removeClass('active-picker-input')
        $('#edit_campaign_timepicker').css("border","1px solid #ff0000");
        $('#edit_error_message').text('Please enter the time in the format of HH:MM');
        document.getElementById('edit_modal_error_message').style.display = "block";
        return;
    }

    if(mode_occurence == "single_occurence")
    {
        if(!check_current_date_time(start_date, [update_time_slot_value])) {
            return false;
        }
    }

    var end_date = ""
    if (choice_selected == "custom")
    {
        if(document.getElementById("ends_on").checked) {
            end_date = $("#campaign_end_datepicker").datepicker('getDate')
            end_date = format_date(end_date)
        }
    }
    $('.campaign-schedule-input-field.schedule_datepicker').removeClass('active-picker-input')
    var request_params = {
        'bot_pk': BOT_ID,
        'campaign_id': get_url_multiple_vars()['campaign_id'][0],
        'choice_selected': choice_selected,
        'start_date': format_date(start_date),
        'end_date': end_date,
        'mode_occurence': mode_occurence,
        'original_metadata': original_metadata,
        'current_slot_pk': current_slot_pk,
        'edited_uid': original_data_obj['edited_uid'],
        'update_time_slot_value': update_time_slot_value,
        'new_batch_pk': $('#audience-batch-select-dropdown').find(":selected").val(),
    };
    var json_params = JSON.stringify(request_params);
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/edit-schedule-campaign/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                selected_schedules_list = []
                show_create_delete_toast("edit_successfull_note_toaster")
                reset_upcoming_schedules_table("", "", 1, true, true)   
                $("#edit-schedule_campaign_modal").modal('hide')

            } else if(response["status"] == 400){
                $('#audience_batch_select_dropdown').removeClass('active-picker-input')
                $('#audience_batch_select_dropdown').css("border","1px solid #ff0000");
                $('#edit_error_message').text('The selected audience batch has different columns as compared to the previously selected batch. Please select another audience batch with the same columns as the previous audience batch associated with this scheduled campaign.');
                document.getElementById('edit_modal_error_message').style.display = "block";
            } else {
                var error_message = response.message;
                show_campaign_toast(error_message);
            }
        }
    }
    xhttp.send(params);
    
}

function check_current_date_time(selected_date, time_slots) {

    // var myDate=new Date()
    var flag = 0
    var today = new Date()
    time_slots.forEach((item, index) => {
        var time = item.split(':')
        var hrs = parseInt(time[0])
        if(item.indexOf("PM") != -1) {
            if (hrs != 12) {
                hrs += 12
            }
        } else {
            if (hrs == 12)  {
                hrs -= 12
            }
        }
        var minutes = parseInt(time[1][0] + time[1][1])
        selected_date.setHours(hrs, minutes, 0)

        if (today >= selected_date) {
            $('#edit_error_message').text('Date and Time slots must be greater than current date and time');
            document.getElementById('edit_modal_error_message').style.display = "block";
            flag = 1 
            return false
        }

    })

    if (flag == 0)
        return true
    else 
        return false

}

function create_new_schedule() {
    var choice_selected = document.querySelectorAll("." + selected_list_class + " input")[0].value 
    var start_date = $("#campaign_datepicker").datepicker( 'getDate' )
    var time_slots = []
    var time_slots_elements = document.getElementsByClassName("time_slots")

    for (var element of time_slots_elements) {
        if(element.value.trim() != ""){
            let time_value = element.value.trim();
            let time_regex = /^(00|0[0-9]|1[012]):[0-5][0-9] ?((a|p)m|(A|P)M)$/;
            if (time_regex.test(time_value) == true){
                time_slots.push(time_value)
            } else{
                $('#create_error_message').text('Please enter the time in the format of HH:MM')
                document.getElementById('create_modal_error_message').style.display = 'block';
                $('#create_campaign_timepicker').removeClass('active-picker-input')
                $('#create_campaign_timepicker').css("border","1px solid #ff0000");
                return;
            }
        }
    }

    if(time_slots.length == 0) {
        show_campaign_toast("Please add atleast one time slot")
        return false
    }

    if(!check_current_date_time(start_date, time_slots)) {
        $('#create_error_message').text('Date and Time should be greater than Present Date and Time')
        document.getElementById('create_modal_error_message').style.display = 'block';
        $('#create_campaign_timepicker').removeClass('active-picker-input')
        $('#create_campaign_timepicker').css("border","1px solid #ff0000");
        return
    }

    var end_date = ""
    if (choice_selected == "custom")
    {   
        if(document.getElementById("ends_on").checked) {
            end_date = $("#campaign_end_datepicker").datepicker('getDate')
            end_date = format_date(end_date)
        }
    }

    var days = get_day_as_per_choice(choice_selected, start_date)  

    if (days == "false") {
        return false
    } 
    var request_params = {
        'bot_pk': BOT_ID,
        'campaign_id': get_url_multiple_vars()['campaign_id'][0],
        'choice_selected': choice_selected,
        'start_date': format_date(start_date),
        'end_date': end_date,
        'time_slots': time_slots,
        'days': days,
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/create-schedule-campaign/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                update_campaign_schdule_page_url('', '')
                setTimeout(function() {
                    location.reload()
                    
                }, 500)
                // reset_upcoming_schedules_table("", "", 1, true, true)
                localStorage.setItem("status","created")
                
            }else if (response["status"] == 400){
                $('#campaign_datepicker').removeClass('active-picker-input')
                $('#campaign_datepicker').css("border","1px solid #ff0000");
                $('#create_campaign_timepicker').removeClass('active-picker-input')
                $('#create_campaign_timepicker').css("border","1px solid #ff0000");
                $('#create_error_message').text('A Schedule is already created at this time slot please choose some other time slot to schedule the campaign.');
                document.getElementById('create_modal_error_message').style.display = "block";
            } else {
                var error_message = response.message;
                show_campaign_toast(error_message);
            }
        }
    }
    xhttp.send(params);
}

function close_custom_modal() {
$("#campaign_schedule_custom_modal").modal('hide')
}

function save_custom_modal() {
    custom_days = []

    if(document.getElementById("ends_on").checked) {
        var end_date = $("#campaign_end_datepicker").datepicker('getDate')
        var start_date = $("#campaign_datepicker").datepicker( 'getDate' )
        var days_gap = difference_in_dates(start_date, end_date)
        if(days_gap > 365) {
            show_campaign_toast("End date can't be greater than 1 year")
            return
        }
    }

    checkbox_inputs = document.getElementsByClassName("week-checkbox-day")
    for(var input=0; input<checkbox_inputs.length; input++) {
        if(checkbox_inputs[input].checked) {
            custom_days.push(dayNamesMin[input])
        }
    }
    if(custom_days.length == 0) {
        return
    } else {
        $("#campaign_schedule_custom_modal").modal('hide')
    }

}

function clear_upcoming_schedule() {
    document.getElementById("campaign_schedule_table").innerHTML = ""
    document.getElementById("campaign_table_pagination_div").innerHTML = ""    
}

function reset_upcoming_schedules_table(start_date, end_date, page=1, update_table=true, show_fetch_toast=false, filter_applied=false) {

    get_upcoming_schedules_data(start_date, end_date, page, update_table, show_fetch_toast, filter_applied)

}

function get_upcoming_schedules_data(start_date, end_date, page=1, update_table=true, show_fetch_toast=false, filter_applied=false) {
    let location_url = get_url_multiple_vars()
    start_date = (location_url['start_date']) ? location_url['start_date'][0] : start_date
    end_date = (location_url['end_date']) ? location_url['end_date'][0] : end_date
    page = (page) ? page : 1
    var request_params = {
            'bot_pk': BOT_ID,
            'campaign_id': location_url['campaign_id'][0],
            'start_date': start_date,
            'end_date': end_date,
            'page': page,
        };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();

    xhttp.open("POST", "/campaign/get-upcoming-schedules/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                if (!response["page_exist"]) {
                    show_campaign_toast_short("page doesn't exist")
                } else {
                    if (localStorage.getItem("status") == "created"){
                        show_create_delete_toast("create_successfull_note_toaster")
                        localStorage.clear();
                    }
                    if (update_table) {
                        if (RELOADED_PAGE){
                            document.getElementById('campaign_dashboard_schedule_table').style.display="none";
                            activate_loader();
                            RELOADED_PAGE = false;
                            setTimeout(function() {
                                location.reload()
                            }, 3500)
                        } else{
                            if (page > get_last_pagination_no())
                            {
                                update_schedule_list_table(response["update_schedule_list"], page, response["total_entries"], response["total_pages"], page - 5, page, filter_applied)
                            } else if(page < get_first_pagination_no()){
                                update_schedule_list_table(response["update_schedule_list"], page, response["total_entries"], response["total_pages"], page - 1, page + 4, filter_applied)
                            } else {
                                update_schedule_list_table(response["update_schedule_list"], page, response["total_entries"], response["total_pages"], get_first_pagination_no() - 1, get_last_pagination_no(), filter_applied)
                        }
                        }
                        update_campaign_schdule_page_url(start_date, end_date, page)

                    }
                }
            } else {
                var error_message = response.message;
                show_campaign_toast(error_message);
            }
        }
    }
    xhttp.send(params);

}

function get_schedule_data_for_edit(schedule_pk, current_slot_pk,update_editor=true) {
    var request_params = {
        'bot_pk': BOT_ID,
        'schedule_pk': schedule_pk,
        'current_slot_pk': current_slot_pk,
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();

    xhttp.open("POST", "/campaign/get-single-schedule-data/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                if (update_editor == true) {
                    reset_add_campaign_div(response["campaign_schedule"], response["campaign_meta_data"], "edit", current_slot_pk, response["campaign_days"])
                }
            } else {
                var error_message = response.message;
                show_campaign_toast(error_message);
            }
        }
    }
    xhttp.send(params);

}

function update_schedule_list_table(schedule_list, page=1, total_entries, total_pages, start_page, end_page, filter_applied=false) {

    if (window.location.pathname.indexOf("/campaign/schedule") != 0) {
        return;
    }

    clear_upcoming_schedule()
    var table_element = document.getElementById("campaign_schedule_table")
    document.getElementById("complete_table_div").style.display = ""
    table_html = ""
    if(total_entries > 0 || filter_applied)
    {   
        document.getElementById("table_no_data_found").style.display = "none";
        
        table_html += get_table_headers()
        table_html += get_table_body(schedule_list)

        
        
    } else{
        document.getElementById("table_no_data_found").style.display = "flex";
        document.getElementById("campaign_dashboard_schedule_table").style.display = "none";
    }
    $('#campaign_schedule_table').append(table_html)  
    $("#campaign_schedule_table td").each( function() {
        if ( this.scrollWidth > this.clientWidth ) {
            $(this).attr({
                'data-toggle':'tooltip',
                'title': $(this).find('.overflow-text').text(),
                'delay': { show: 500, hide: 100 }
            });
        }
    });
    $('#campaign_schedule_table td[data-toggle="tooltip"]').tooltip({
        template: '<div class="tooltip table-tooltip" role="tooltip"><div class="arrow"></div><div class="tooltip-inner"></div></div>',
    });
     
    $('#campaign_table_pagination_div').append(get_pagination_div(page, total_entries, total_pages, start_page, end_page))

    if (document.getElementsByClassName("campaign_select_all_rows_cb")[0]){
        set_selector_functionality();
        main_table_selection_check();
    }
}

function apply_upcoming_schedule_filter(page=1) {
    start_date = $('#campaign_filter_custom_start_date').datepicker('getDate')   
    end_date = $('#campaign_filter_custom_end_date').datepicker('getDate')
    if (start_date == null || end_date == null) {
        let location_url = get_url_multiple_vars();
        let start_date = location_url['start_date']
        let end_date = location_url['end_date']
        update_campaign_schdule_page_url((start_date) ? start_date : '',(end_date) ? end_date : '')
        reset_upcoming_schedules_table("", "", page, true, true)
    } else {
        start_date = format_date(start_date)
        end_date = format_date(end_date)
        update_campaign_schdule_page_url(start_date, end_date)
        reset_upcoming_schedules_table(start_date, end_date, page, true, true, true)
    }

}

function clear_upcoming_schedule_filter() {
    $('#campaign_filter_custom_start_date').datepicker('setDate', null);
    $('#campaign_filter_custom_end_date').datepicker('setDate', null);
    RELOADED_PAGE = true
    update_campaign_schdule_page_url('', '')
    reset_upcoming_schedules_table("", "", 1, true, true)
    
}

function get_table_headers() {
    return `<thead>            
                <tr role="row">                
                    <th class="sorting_disabled text-left text-md-center" rowspan="1" colspan="1" style="width: 13px;">
                    
                    <input type="checkbox" id="global-selected-campaign-schedule" class="campaign_select_all_rows_cb" ${(TABLE_SELECTED) ? 'checked' : ''}>
                    </th>                
                    <th name="name" rowspan="1" colspan="1" >
                        Campaign Name 
                    </th>                
                    <th name="channel" rowspan="1" colspan="1" >
                        Audience Batch Name
                    </th>                
                    <th name="trigger_date" class="sorting_disabled" rowspan="1" colspan="1" >
                        Trigger Date
                    </th>                
                    <th name="trigger_time" class="sorting_disabled" rowspan="1" colspan="1" >
                        Trigger Time
                    </th>                
                    <th name="created_on" class="sorting_disabled" rowspan="1" colspan="1" >
                        Created on
                    </th>                
                    <th name="action" class="sorting_disabled" rowspan="1" colspan="1">
                        Action
                    </th>            
                </tr>        
            </thead>`

}

function get_table_body(schedule_list) {
html = '<tbody>'
    schedule_list.forEach((item, index) => {
        html += `<tr role="row" class="odd" ${(TABLE_SELECTED || selected_schedules_list.includes("schedule_number_"+item.current_slot_pk)) ? 'style="background: #F1F6FD;"': 'style="background: #fff;"'}>                    
                    <td class=" text-left text-md-center" data-content="" >
                        <input class="campaign_select_row_cb" id="schedule_number_${item.current_slot_pk}" data-content="${item.current_slot_pk}" type="checkbox" ${(TABLE_SELECTED || selected_schedules_list.includes("schedule_number_"+item.current_slot_pk)) ? ' checked' : ''}>
                    </td>                    
                    <td data-content="campaign_name">
                        <span class="campaign-name-text overflow-text">
                            ${item.campaign_name}
                        </span>
                        ${(item.last_modified) ? `<p class="updated-text">
                        Last Updated : ${item.last_modified}
                    </p>` : ``}
                        
                    </td>                    
                    <td data-content="channel">
                        <span class="overflow-text">
                            ${item.batch_name}
                        </span>
                    </td>                    
                    <td data-content="trigger_date">
                        ${item.trigger_date}
                    </td>                    
                    <td data-content="trigger_time">
                        ${item.trigger_time}
                    </td>                    
                    <td data-content="created_on">
                        ${item.created_on}
                    </td>                    
                    <td data-content="action_btns" class="campaign-schedule-table-action-btn">
                        <button class="campaign-schedule-edit-btn" onclick="get_schedule_data_for_edit(${item.schedule_pk}, ${item.current_slot_pk})"data-toggle="modal" data-target="#edit-schedule_campaign_modal">                            
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M13.3737 2.62638C14.2089 3.46154 14.2089 4.81562 13.3737 5.65079L6.22108 12.8034C6.05561 12.9689 5.84982 13.0883 5.62406 13.1499L2.56676 13.9837C2.23216 14.075 1.92514 13.7679 2.0164 13.4333L2.8502 10.376C2.91178 10.1503 3.0312 9.9445 3.19667 9.77903L10.3493 2.62638C11.1845 1.79121 12.5386 1.79121 13.3737 2.62638ZM9.76992 4.4736L3.83055 10.4129C3.7754 10.4681 3.73559 10.5367 3.71506 10.6119L3.08764 12.9125L5.38819 12.285C5.46344 12.2645 5.53204 12.2247 5.58719 12.1696L11.5264 6.23004L9.76992 4.4736ZM10.9832 3.26026L10.4034 3.83951L12.1598 5.59655L12.7398 5.0169C13.2249 4.53182 13.2249 3.74534 12.7398 3.26026C12.2548 2.77518 11.4683 2.77518 10.9832 3.26026Z" fill="#212121"/>
                            </svg>
                        </button>                        
                        <button class="campaign-schedule-delete-btn" id="delete_campaign_id_${item.schedule_pk}" value="${item.uid}" onclick="delete_occurence(${item.schedule_pk}, ${item.current_slot_pk})"data-toggle="modal">                            
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path fill-rule="evenodd" clip-rule="evenodd" d="M11.8099 5.36705H4.19299C3.87915 5.36705 3.70001 5.66873 3.88831 5.88013L4.04065 6.05116C4.38675 6.43972 4.57384 6.91231 4.57384 7.398V13.3839C4.57384 13.561 4.74435 13.7046 4.95468 13.7046H11.0483C11.2586 13.7046 11.4291 13.561 11.4291 13.3839V7.398C11.4291 6.91231 11.6162 6.43972 11.9623 6.05116L12.1146 5.88013C12.3029 5.66873 12.1238 5.36705 11.8099 5.36705ZM4.19299 4.40503C2.93765 4.40503 2.22107 5.61175 2.97428 6.45735L3.12662 6.62838C3.32438 6.85041 3.43129 7.12046 3.43129 7.398V13.3839C3.43129 14.0923 4.11334 14.6666 4.95468 14.6666H11.0483C11.8896 14.6666 12.5716 14.0923 12.5716 13.3839V7.398C12.5716 7.12046 12.6785 6.85041 12.8763 6.62838L13.0287 6.45735C13.7819 5.61175 13.0653 4.40503 11.8099 4.40503H4.19299Z" fill="#262626"/>
                                <path fill-rule="evenodd" clip-rule="evenodd" d="M9.52525 7.13086C9.84075 7.13086 10.0965 7.34622 10.0965 7.61187L10.0965 11.46C10.0965 11.7256 9.84075 11.941 9.52525 11.941C9.20974 11.941 8.95398 11.7256 8.95398 11.46L8.95398 7.61187C8.95398 7.34622 9.20974 7.13086 9.52525 7.13086Z" fill="#262626"/>
                                <path fill-rule="evenodd" clip-rule="evenodd" d="M6.47837 7.13086C6.79388 7.13086 7.04964 7.34622 7.04964 7.61187L7.04964 11.46C7.04964 11.7256 6.79388 11.941 6.47837 11.941C6.16287 11.941 5.9071 11.7256 5.9071 11.46L5.9071 7.61187C5.9071 7.34622 6.16287 7.13086 6.47837 7.13086Z" fill="#262626"/>
                                <path fill-rule="evenodd" clip-rule="evenodd" d="M4.82758 3.20598C5.11269 2.48578 5.91314 2 6.81475 2H9.18893C10.0905 2 10.891 2.48578 11.1761 3.20598L11.5906 4.25295C11.6903 4.50498 11.5286 4.77738 11.2293 4.86139C10.93 4.9454 10.6064 4.8092 10.5067 4.55717L10.0922 3.5102C9.96259 3.18283 9.59875 2.96203 9.18893 2.96203H6.81475C6.40493 2.96203 6.04109 3.18283 5.91149 3.5102L5.49701 4.55717C5.39724 4.8092 5.07372 4.9454 4.7744 4.86139C4.47509 4.77738 4.31333 4.50498 4.4131 4.25295L4.82758 3.20598Z" fill="#262626"/>
                                </svg>
                        </button>                    
                    </td>                
                </tr>`
    })

html += '</tbody>'  

return html 
}

function get_pagination_div(page, total_entries, total_pages, start_page=0, end_page=5) {
    if (total_pages < 1) {
        return ''
    }
    if(start_page < 0)
        start_page = 0
    class_add_page_highlight = ''
    var entry_from = (page - 1)*25
    var entry_to = entry_from + total_entries 
    if (total_entries > 0)
        entry_from = entry_from + 1

    var class_previous_disabled = '"'; 
    if(page - 1 <= 0){
        class_previous_disabled = 'disabled" style="cursor:default"'; 
    }
    ENTRIES_IN_PAGE = (entry_to - entry_from) + 1
    html = `<div class="col-md-6 col-sm-12 show-pagination-entry-container p-0 pagination-text" filter_default_text="Showing entries ${entry_from} to ${entry_to}">
                Showing entries ${entry_from} to ${entry_to}
            </div>
            <div class="col-md-6 col-sm-12 p-0">
                <div class="d-flex justify-content-end">
                    <nav aria-label="Page navigation example">
                        <ul class="pagination">
                            <li class="page-item ${class_previous_disabled}>
                                <a class="page-link previous_button" onclick="get_previous_page()" aria-label="Previous">Previous</a>
                            </li>`

    var temp_page = 0    
    if (total_pages < end_page)
        end_page = total_pages

    for(var page_no=start_page; page_no < end_page; page_no++) {
        var temp_page = page_no + 1

        if((page) == temp_page)
            class_add_page_highlight = 'page-selected'
        else {
            class_add_page_highlight = 'page-unselected'
        }
        html += `<li class="active purple darken-3 page-item"><a href="javascript:void(0)"  data-page="${temp_page}" onclick="change_page(${temp_page})" class="page-link pagination-no ${class_add_page_highlight}">${temp_page}</a></li>`

    } 

    var class_next_disabled = '"';
    if(page >= total_pages){
        class_next_disabled = ' disabled" style="cursor:default"';  
    }   
    
    html += `<li class="page-item${class_next_disabled}><a class="page-link next_button" onclick="get_next_page()" aria-label="Previous">Next</a></li>
                </ul>
            </nav>
        </div>
    </div>`
    return html
}

function change_page(page) {
    apply_upcoming_schedule_filter(page)
}

function get_next_page() {
    apply_upcoming_schedule_filter(get_current_page() + 1);
}

function get_previous_page() {
    apply_upcoming_schedule_filter(get_current_page() - 1);
}

function get_current_page() {
    var selected_pagination_tags = document.getElementsByClassName("pagination-no page-selected");
    curr_pagination_no = parseInt(selected_pagination_tags[0].innerText);
    return curr_pagination_no;
}

function get_last_pagination_no() {
    var all_pagination_tags = document.getElementsByClassName("pagination-no")
    var length = all_pagination_tags.length
    var last_pagination_no = 5
    if (all_pagination_tags.length > 0)
        last_pagination_no = parseInt(all_pagination_tags[length - 1].innerText)
    return last_pagination_no
}

function get_first_pagination_no() {
    var all_pagination_tags = document.getElementsByClassName("pagination-no")
    var first_pagination = 1
    if (all_pagination_tags.length > 0)
        first_pagination = parseInt(all_pagination_tags[0].innerText)
    return first_pagination
}

function reset_add_campaign_div(data_obj, metadata, mode, current_slot_pk, days) {
    html = ''
    html += get_date_picker_div()
    html += get_time_slots(metadata, mode, data_obj)
    html += get_add_time_slot_div()

    $("#audience-batch-select-dropdown").val(data_obj['batch_pk']).selectpicker("refresh");
    $('.filter-option-inner-inner').text($('#audience-batch-select-dropdown').find(":selected").text());

    $("#campaign-schedule-slots-wrapper").append(html)
    // initialize_datepicker_and_timepicker();
    $("#edit_campaign_datepicker").datepicker('setDate', data_obj["edited_start_date"])
    call_update_dropdown_options()
    
    var currently_selected = document.querySelectorAll("." + selected_list_class)[0]
    currently_selected.classList.remove(selected_list_class)

    $('input[value="' + data_obj["choice_selected"] +'"]').parent().addClass(selected_list_class) 

    $('#edit_campaign_timepicker').val(metadata[0]['time'])
    var changed_option = document.querySelectorAll("." + selected_list_class + " span")[0].innerHTML
    var element = document.getElementsByClassName("easyassist-dropdown-selected")[0] 
    element.innerText = changed_option
    // make_element_disabled(element)

    initialize_timepicker_events()
    create_time_slot_blur_event()
    change_save_onclick_edit(metadata, data_obj, current_slot_pk)

    if(data_obj["choice_selected"] == "custom") {
        if(data_obj["original_end_date"] != "") {
            $("#campaign_end_datepicker").datepicker(setDate, data_obj["original_end_date"])
            document.getElementById("ends_on").checked = true
        } 

        custom_days = days

    }

}

function change_save_onclick_edit(metadata, data_obj, current_slot_pk) {

    global_metadata = metadata
    global_data_obj = data_obj
    global_current_slot_pk = current_slot_pk
    
    // document.getElementById('campaign-schedule-save-btn').setAttribute('onclick','open_edit_modal()')
    // document.getElementById("edit_schedule_save_btn").setAttribute('onclick','edit_click_handler()');
    // document.getElementById("reset_modal_save_btn").setAttribute('onclick','reset_edit_handler()');
    
}


function edit_click_handler() {
    edit_schedule(global_metadata, global_data_obj, global_current_slot_pk)
}


function reset_edit_handler() {    
    $('#campaign_datepicker').datepicker('setDate', global_data_obj["edited_start_date"])
    document.getElementsByName(global_data_obj["edited_uid"])[0].value = global_data_obj["edited_trigger_time"]

    $('.new_time_slots').parent().remove();
}


function delete_occurence(schedule_pk, current_slot_pk) {
    global_schedule_pk = schedule_pk
    global_current_slot_pk = current_slot_pk
    global_uid = $('#delete_campaign_id_'+schedule_pk).val()
    $("#campaign_schedule_delete_modal").modal('show')
    // document.getElementById('delete_schedule_save_btn').setAttribute('onclick','delete_click_handler()');
}

function delete_click_handler() {
    call_delete_schedule(global_schedule_pk, global_current_slot_pk, global_uid)
}

function open_edit_modal() {
    $("#campaign_schedule_edit_modal").modal('show')
}

function get_date_picker_div() {

    html = '<div class="campaign-schedule-input-item">\
                <input type="text" class="campaign-schedule-input-field schedule_datepicker" id="campaign_datepicker">\
            </div>'
    return html
}

function get_time_slots(metadata, mode, data_obj) {

    html = ''
    var edited_uid = data_obj["edited_uid"]
    var edited_time = data_obj["edited_trigger_time"]
    var onclick_function = 'remove_slots_function(this);'
    if(mode == "edit") {
        onclick_function = ''
    }
    var edited_id_in_metadata = false
    metadata.forEach((item, index) => {
        if (item.uid == edited_uid) {
            edited_id_in_metadata = true
            html += '<div class="campaign-schedule-input-item" onclick="' + onclick_function +'">'
        } else {
            html += '<div class="campaign-schedule-input-item" style="pointer-events:none" onclick="' + onclick_function +'">'
        }
        if (item.uid == edited_uid) {
            html += '<input type="text" data-content="'+Math.random()+'"  class="campaign-schedule-input-field schedule-timepicker time_slots" name="' + item.uid + '" value="' + data_obj['edited_trigger_time'] + '" />'
        } else {
            html += '<input type="text" data-content="'+Math.random()+'" class="campaign-schedule-input-field schedule-timepicker time_slots" name="' + item.uid + '" value="' + item.time + '" />'
        }

        html += '</div>' 
    })

    if (edited_id_in_metadata == false) {
        html += '<div class="campaign-schedule-input-item" onclick="' + onclick_function +'">'
        html += '<input type="text" data-content="'+Math.random()+'" class="campaign-schedule-input-field schedule-timepicker time_slots" name="' + edited_uid + '" value="' + data_obj['edited_trigger_time'] + '" />'
        html += '</div>' 
        
    }

    return html

}

function get_add_time_slot_div() {

    html = '<div class="campaign-schedule-input-item">\
                <input type="text" class="campaign-schedule-add-time-slot-field schedule-timepicker" id="campaign-schedule-add-time-slot-input" value="" style="z-index: 1; background: transparent;">\
                <button class="campaign-schedule-add-time-slot-field campaign-schedule-add-time-slot-btn" style="z-index: 0; position: absolute;">\
                    Add Time Slot\
                </button>\
            </div>'

    return html
}



function reset_current_wrapper() {

    $('#campaign_schedule_delete_selected_items_btn').attr('disabled','disabled');
    document.getElementById("campaign_schedule_delete_selected_items_btn").style.opacity = "0.5"

    initialize_datepicker_and_timepicker()

    initialize_timepicker_events()

    create_time_slot_blur_event()

}


function selection_of_schedule_campaign_table(checked_on){
    selected_schedules_list = document.getElementsByClassName("campaign_select_row_cb");
    var checked = document.getElementsByClassName("campaign_select_all_rows_cb")[0].checked;
    let selected_schedules_list_length = selected_schedules_list.length
    let list_of_selected_ids = [];
    for (var i = 0; i < selected_schedules_list_length; i++) {
        selected_schedules_list[i].checked = checked;
        list_of_selected_ids.push(selected_schedules_list[i].id)
    }
    selected_schedules_list = list_of_selected_ids
    $(".campaign_select_row_cb").checked = true;
    $('#total_deleting_campaign_selected').text('All ' + selected_schedules_list_length + ' scheduled campaigns on this page are selected.')
    $('#total_deleting_campaign_selected_on_modal').text(selected_schedules_list_length)
    document.getElementById('all_selected_span').style.display = 'none'
    DELETE_MODE = 'selected_items'
    if(checked_on){
        $('#campaign_schedule_table tbody tr').css("background", "#F1F6FD");
        $('.all-selected-text-div').show();
        $('.campaign-table-row').css('min-height','calc(100vh - 246px)');
        $('.campaign-table-column').css('max-height','calc(100vh - 268px)');
    }else{
        clear_selected_campaign()
        $('#campaign_schedule_table tbody tr').css("background", "#fff");
        $('.all-selected-text-div').hide();
        $('.campaign-table-row').css('min-height','calc(100vh - 208px)');
        $('.campaign-table-column').css('max-height','calc(100vh - 211px)');
    }

    check_selectors()
}

function main_table_selection_check(){
    let checked_schedules_length = $('.campaign_select_row_cb[type=checkbox]:checked').length;
    if (checked_schedules_length == ENTRIES_IN_PAGE) {
        document.getElementsByClassName("campaign_select_all_rows_cb")[0].checked = true;
    }
}

//Selector functionality
function set_selector_functionality() {

    document.getElementsByClassName("campaign_select_all_rows_cb")[0].onchange = function(e){
        selection_of_schedule_campaign_table(this.checked)
    }


    $(".campaign_select_row_cb").change(function(){
        var checked = $(this).checked
        
        if (!checked) {
            document.getElementsByClassName("campaign_select_all_rows_cb")[0].checked = false
        }
        
        let checked_schedules_length = $('.campaign_select_row_cb[type=checkbox]:checked').length;
        $('#total_deleting_campaign_selected_on_modal').text(checked_schedules_length)
        document.getElementById('all_selected_span').style.display = 'none'
        if (checked_schedules_length == ENTRIES_IN_PAGE) {
            document.getElementsByClassName("campaign_select_all_rows_cb")[0].checked = true
            DELETE_MODE = 'none'
            $('.all-selected-text-div').show();
            $('#select_all_in_total_campaigns').show();
        }else{
            $('.all-selected-text-div').hide();
        }
        if ($(this).is(':checked')) {
            $(this).parent().parent().css("background", "#F1F6FD");
        }else {
            $(this).parent().parent().css("background", "#fff")
        }

        check_selectors()

    });

    check_selectors()
}

function check_selectors() {
    if ($('.campaign_select_row_cb[type=checkbox]:checked').length > 0) {
        $('#campaign_schedule_delete_selected_items_btn').removeAttr('disabled');
        document.getElementById("campaign_schedule_delete_selected_items_btn").style.opacity = "1"
    } else {
        $('#campaign_schedule_delete_selected_items_btn').attr('disabled','disabled');
        document.getElementById("campaign_schedule_delete_selected_items_btn").style.opacity = "0.5"
    }
}

$("#campaign-frequency-dropdown-div").click(function() {
    $("#schedule_campaign_modal .modal-body").animate({ scrollTop: 230 }, 20);
});

$('input[name="radio-group2"]').on("change", function(event) {
    if($('#ends_on').is(':checked')){
        $(".custom-campaign-end-date-card").show();
    } else {
        $('.custom-campaign-end-date-card').hide();
    }
});

function schedule_custom_options(select) {
    document.querySelector(".custom-frequency-div").style.display = select.value == "custom" ? 'block' : 'none';
}

function getCurrentTime() {
    const now = new Date();
    now.setMinutes(now.getMinutes() + 5)
    const hours = now.getHours();
    const minutes = now.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    let hours12 = (hours % 12 || 12) ;
    const minutesString = minutes < 10 ? `0${minutes}` : minutes;
    hours12 = hours12 < 10 ? `0${hours12}` : hours12;
    return `${hours12}:${minutesString} ${ampm}`;
}

$(".campaign-schedule-input-field.schedule_datepicker").on('change',function(){
    $(".campaign-schedule-input-field.schedule_datepicker").css("border", "")
    validateDateOnChange($(this).val(),this)
})

function validateDateOnChange(dateInput,inputElement) {
    var regex = new RegExp(/^(0[1-9]|[12][0-9]|3[01])[-](0[1-9]|1[012])[-](19|20)\d\d$/);
    if(regex.test(dateInput) == true){
        $(inputElement).addClass('active-picker-input')
    }else{
        $(inputElement).removeClass('active-picker-input')
    }
}

function timePicker() {
    let timeInput1 = $('.custom-timepicker-input');
    timeInput1.njTimepick();
    // $('.custom-timepicker-input').keydown(function(event) {event.preventDefault()});
}

$("#global-selected-campaign-schedule").click(function () {
    $(".campaign_select_row_cb").prop('checked', $(this).prop('checked'));
    if(this.checked){
        $('#campaign_schedule_table tbody tr').css("background", "#F1F6FD");
        $('.all-selected-text-div').show();
        $('.campaign-table-row').css('min-height','calc(100vh - 246px)');
        $('.campaign-table-column').css('max-height','calc(100vh - 268px)');
    }else{
        $('#campaign_schedule_table tbody tr').css("background", "#fff");
        $('.all-selected-text-div').hide();
        $('.campaign-table-row').css('min-height','calc(100vh - 246px)');
        $('.campaign-table-column').css('max-height','calc(100vh - 211px)');
    }
});

$('#select_all_in_total_campaigns').click(function(){
    DELETE_MODE = 'whole_campaign'
    TABLE_SELECTED = true;
    $('#total_deleting_campaign_selected').text('All scheduled campaigns are selected.')
    document.getElementById('all_selected_span').style.display = ''
    $('#total_deleting_campaign_selected_on_modal').text('')
    $('.campaign_select_all_rows_cb').prop('checked', true);
    $(".campaign_select_row_cb").prop('checked', true);
    $('#select_all_in_total_campaigns').hide();
    $('#clear_all_selected_campaigns_in_total').show();
    check_selectors();
});

function clear_selected_campaign(){
    DELETE_MODE = 'none';
    TABLE_SELECTED = false;
    selected_schedules_list = [];
    $(".campaign_select_row_cb").prop('checked', false);
    $('#global-selected-campaign-schedule').prop('checked', false);
    $('#campaign_schedule_table tbody tr').css("background", "#fff");
    $('.all-selected-text-div').hide();
    $('.campaign-table-row').css('min-height','calc(100vh - 208px)');
    $('.campaign-table-column').css('max-height','calc(100vh - 211px)');
    $('#clear_all_selected_campaigns_in_total').hide();
    $('#select_all_in_total_campaigns').show();
    check_selectors();
}

$('#clear_all_selected_campaigns_in_total').click(function(){
    clear_selected_campaign()
});

function update_campaign_schdule_page_url(start_date, end_date, page){
    let filters = get_url_multiple_vars();
    let newurl = `${window.location.protocol}//${window.location.host}${window.location.pathname}?bot_pk=${filters['bot_pk']}&campaign_id=${filters['campaign_id']}&channel=${filters['channel']}&bot_wsp_id=${filters['bot_wsp_id']}&start_date=${start_date}&end_date=${end_date}&r=${RELOADED_PAGE}&p=${page}`
    window.history.pushState({ path: newurl }, '', newurl);
}

$('#schedule_campaign_modal').on('hidden.bs.modal', function () {
    $("#campaign-frequency-dropdown-div .easyassist-custom-dropdown-option-container li").removeClass('easyassist-option-selected')
    $("#campaign-frequency-dropdown-div .easyassist-custom-dropdown-option-container li input[value='does_not_repeat']").parent().addClass('easyassist-option-selected')
    $('.easyassist-dropdown-selected').text('Does not repeat')
    $('#campaign_datepicker').css("border","");
    $('#campaign_end_datepicker').css("border","");
    $('#create_campaign_timepicker').css("border","");
    document.getElementById('weekdays_block').style.display = "none"
    $('#campaign-schedule-list-select').val('does_not_repeat');
    $('#campaign_end_datepicker').removeClass('active-picker-input')
    $('#campaign_datepicker').removeClass('active-picker-input')
    $('#create_campaign_timepicker').removeClass('active-picker-input')
    document.getElementById('create_modal_error_message').style.display = "none"
});

$('#edit-schedule_campaign_modal').on('hidden.bs.modal', function () {
    $('.campaign-schedule-input-field.schedule_datepicker').removeClass('active-picker-input')
    $('#audience_batch_select_dropdown').css("border","");
    $('#edit_campaign_timepicker').css("border","");
    $('#edit_campaign_timepicker').removeClass('active-picker-input')
    document.getElementById('edit_modal_error_message').style.display = "none";
});

$('#filter-schedule_campaign_modal').on('hidden.bs.modal', function () {
    $('#campaign_filter_custom_start_date').removeClass('active-picker-input')
    $('#campaign_filter_custom_end_date').removeClass('active-picker-input')
    $("#campaign_filter_custom_end_date").datepicker( "option", "minDate", 0);
    set_date_value_for_filter();
});

function activate_loader(){
    $('#campaign_schedule_delete_selected_items_btn').attr('disabled','disabled');
    document.getElementById("campaign_schedule_delete_selected_items_btn").style.opacity = "0.5"
    $('#filter_schedule_campaign_btn').attr('disabled','disabled');
    document.getElementById("filter_schedule_campaign_btn").style.opacity = "0.5"
    $('#create_schedule_campaign_btn').attr('disabled','disabled');
    document.getElementById("create_schedule_campaign_btn").style.opacity = "0.5"
    $('.all-selected-text-div').hide();
    $('#no-data-loader').show();
}

function reset_time_date_schedule_create(){
    $('#campaign_datepicker').datepicker('setDate', new Date());
    let current_date = $('#campaign_datepicker').datepicker('getDate');
    current_date.setDate(current_date.getDate() + 1)
    $("#campaign_end_datepicker").datepicker("option", "minDate", current_date)
    $('#campaign_end_datepicker').datepicker('setDate', current_date);
    $('.custom-timepicker-input').val(getCurrentTime())
}
$("#campaign-frequency-dropdown-div .easyassist-custom-dropdown-option-container li input[value='custom']").click(function(){
    document.getElementById('weekdays_block').style.display = "block"
})