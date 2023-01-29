var sync_search_field_interval = null;
var global_session_id = null;
var update_cobrowsing_request_status_interval = null;
var client_server_websocket = null;
var client_server_websocket_open = false;
var client_server_heartbeat_timer = null;
var agent_remarks = null;
var show_request_meeting_modal_toast = false;
var close_session_id = null;
var archive_session_id = null;
var get_active_agent_list_interval = {};
var update_all_lead_count_interval = null;
var update_all_lead_status_interval = null;
const regEmail = /^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/;
var number_of_visible_chips = 5;
var highlighted_lines = {};
var processor_errors = {};
var system_commands = window.SYSTEM_COMMANDS ? window.SYSTEM_COMMANDS : ['subprocess.call', 'subprocess.check_output', 'import threading', 'threading.Thread', 'ssh'];
var chat_logo_input_file_global = undefined;
var total_active_cobrowse_leads = 0;
var update_active_queue_lead_status_interval = null;
const UPDATE_ACTIVE_QUEUE_LEAD_STATUS_INTERVAL_TIME = 10000;
const UPDATE_ACTIVE_LEAD_COUNT_INTERVAL_TIME = 5000;
const UPDATE_ACTIVE_LEAD_STATUS_INTERVAL_TIME = 5000
const UPDATE_AGENT_DETAILS_INTERVAL_TIME = 10000;
var on_canned_response_page = false;
let on_outbound_analytics_page = false;
let on_agent_management_page = false;
const EMPTY_START_DATE_ERROR_TOAST = "Please enter a Start Date to continue";
const EMPTY_END_DATE_ERROR_TOAST = "Please enter an End Date to continue";
const TODAY_DATE_ERROR_TOAST = "cannot be today's date, please select any other date";
const NO_TITLE_SELECTED_TOAST = "Please select a title to continue";
const NO_AGENT_SELECTED_TOAST = "Please select an agent to continue";
const NO_SUPERVISOR_SELECTED_TOAST = "Please select a supervisor to continue";
const INVALID_START_DATE_ERROR_TOAST = "Start Date is ahead of End Date, please choose a valid date range";

$(function() {
    $("#easyassist-language-support-selected").selectpicker({
        noneSelectedText: 'Select Language'
    });
    $("#easyassist-product-category-selected").selectpicker({
        noneSelectedText: 'Select Product Category'
    });
    $("#selected-supervisor-div").selectpicker({
        noneSelectedText: 'Choose Supervisor'
    });
    $(':not(.tooltip-navbar)[data-toggle="tooltip"]').tooltip();

    $('#go_live_date').datepicker();
    $('.datepicker:not(#go_live_date)').datepicker({
        endDate: '+0d',
    });

    $(".positive_numeric").on("keypress input", function(event) {
        var keyCode = event.which;
     
        if ( (keyCode != 8 || keyCode ==32 ) && (keyCode < 48 || keyCode > 57)) { 
            return false;
        }

        var self = $(this);
        self.val(self.val().replace(/\D/g, ""));
    });
    $(".mobile_number").on("keypress", easyassist_mobile_number_validation);
});

document.querySelector("#content-wrapper").addEventListener(
    "scroll", 
    function() {
        var datepicket_dropdown = document.querySelector(".datepicker-dropdown");
        if(datepicket_dropdown){
            document.body.removeChild(datepicket_dropdown);
            $('.datepicker').blur();
        }
    }
)

var user_last_activity_time_obj = new Date()

function set_cookie(cookiename, cookievalue, path = "") {
    var domain = window.location.hostname.substring(window.location.host.indexOf(".") + 1);

    if (window.location.hostname.split(".").length == 2 || window.location.hostname == "127.0.0.1") {
        domain = window.location.hostname;
    }

    if (path == "") {
        document.cookie = cookiename + "=" + cookievalue + ";domain=" + domain;
    } else {
        document.cookie = cookiename + "=" + cookievalue + ";path=" + path + ";domain=" + domain;
    }
}

function easyassist_mobile_number_validation(event){
    var element = event.target;
    var value = element.value;
    var count = value.length;
    if ((event.keyCode >= 48 && event.keyCode <= 57) || (event.keyCode >= 96 && event.keyCode <= 105)) { 
        if(count >= 10){
            event.preventDefault();
        }
    }
}

function get_cookie(cookiename) {
    var cookie_name = cookiename + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var cookie_array = decodedCookie.split(';');
    for (let i = 0; i < cookie_array.length; i++) {
        var c = cookie_array[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(cookie_name) == 0) {
            return c.substring(cookie_name.length, c.length);
        }
    }
    return "";
}

// Custom user session

/*
    get_delayed_date_object
    delay current date by delay_period
    var date_obj = new Date();                                      -> current date
    date_obj.setMinutes( date_obj.getMinutes() + delay_period );    -> delay by delay_period
*/

function get_delayed_date_object(delay_period) {
    var date_obj = new Date();
    date_obj.setMinutes(date_obj.getMinutes() + delay_period);
    return date_obj
}

/*
    send_session_timeout_request
    is_online_from_this_time                -> delayed by 3 minuits date object
    user_last_activity_time_obj -> user's last activity time
    if(user_last_activity_time_obj > is_online_from_this_time) -> is user active from last 3 minutes
*/

function send_session_timeout_request() {

    if (get_cookie("is_online") == "0") {
        return;
    }

    var is_online_from_this_time = get_delayed_date_object(-3);

    if (user_last_activity_time_obj > is_online_from_this_time) {
        var CSRF_TOKEN = $('input[name="csrfmiddlewaretoken"]').val();
        $.ajax({
            url: "/chat/set-session-time-limit/",
            type: "POST",
            headers: {
                'X-CSRFToken': CSRF_TOKEN
            },
            data: {},
            success: function(response) {
                set_cookie("is_online", "1", "/");
            },
            error: function(xhr, textstatus, errorthrown) {
                set_cookie("is_online", "0", "/");
            }
        });
    }
}

function resetTimer(e) {
    var delay_by_nine_hours = get_delayed_date_object(-540);
    if (user_last_activity_time_obj < delay_by_nine_hours) { // if user is active in last minute ( after inactive for 9 minuits )
        user_last_activity_time_obj = new Date();
        send_session_timeout_request();
    }
    user_last_activity_time_obj = new Date()
}

function set_user_inactivity_detector() {
    resetTimer();
    window.onmousemove = resetTimer;
    window.onmousedown = resetTimer;
    window.onclick = resetTimer;
    window.onkeypress = resetTimer;
    window.addEventListener('scroll', resetTimer, true);

    document.addEventListener("visibilitychange", function() {
        if (document.hidden == false) {
            resetTimer();
        }
    }, false);

    setInterval(send_session_timeout_request, 3 * 60 * 1000);
    send_session_timeout_request();
}

set_user_inactivity_detector();

function accept_location_request(pos) {
    let agent_latitude = pos.coords.latitude;
    let agent_longitude = pos.coords.longitude;
    let location = get_cookie("agent_location");
    if (location == null || location == undefined || location == "None" || location.toString().trim() == "") {
        show_agent_location_details(agent_latitude, agent_longitude, (data) => {
            check_and_mark_agent_active_status("none");
        })
    }
}

function cancel_location_request(pos) {
    agent_location = null
}

function check_and_mark_agent_active_status(element) {

    let location = get_cookie("agent_location");
    if (location == undefined || location == null) {
        location = "None";
    }

    var request_params = {};

    if (element == "none") {
        if (document.getElementById("checkbox-mark-as-active") != null && document.getElementById("checkbox-mark-as-active").checked == true) {
            request_params = {
                "location": location,
                "active_status": true
            };
        } else {
            return;
        }
    } else {
        request_params = {
            "location": location,
            "active_status": element.checked
        };
    }

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/change-active-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status != 200) {
                show_easyassist_toast("Unable to update the active status");
            } else {
                if (element != "none") {
                    window.location.reload(true);
                } else {
                    var video_meeting_count = response["video_meeting_count"];

                    try {
                        if (video_meeting_count > 0) {
                            document.getElementById("total_video_meeting_count").innerHTML = video_meeting_count;
                            document.getElementById("total_video_meeting_count").parentElement.style.display = '';
                        } else {
                            document.getElementById("total_video_meeting_count").parentElement.style.display = 'none';
                        }
                    } catch (err) {}
                }
            }
        }
    }
    xhttp.send(params);
}

function show_agent_location_details(latitude, longitude, callback) {
    let promises = get_agent_current_location(latitude, longitude);
    Promise.all([promises])
        .then(function(results) {
            if (results[0]) {
                set_cookie("agent_location", results[0], "/");
            }
            callback()
        });
}

function get_agent_current_location(latitude, longitude) {

    if (latitude == "None" || longitude == "None") {
        return new Promise(function(resolve, reject) {
            resolve("None");
        });
    }
    var geocoder = new google.maps.Geocoder();
    var latlng = new google.maps.LatLng(latitude, longitude);
    return new Promise(function(resolve, reject) {
        geocoder.geocode({ 'latLng': latlng }, function(results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                if (results[results.length - 4]) {
                    var address = results[results.length - 4].formatted_address;
                    resolve(address);
                } else {
                    resolve("None");
                }
            } else {
                resolve("None");
            }
        });
    });
}

function save_agent_details(element) {
    let error_message_element = document.getElementById("save-details-error");
    error_message_element.innerHTML = "";
    var full_name = document.getElementById("agent-name").value;
    var mobile_number = document.getElementById("agent-mobile-number").value;
    var old_password = document.getElementById("old-password").value;
    var new_password = document.getElementById("new-password").value;
    var support_level = document.getElementById("agent-support-level").value;
    var agent_email = document.getElementById("agent-email").value;
    var confirm_password = document.getElementById("confirm-password").value;

    const regName = /^[^\s][a-zA-Z ]+$/;
    const regMob = /^[6-9]{1}\d{9}$/;
    const regPass = /^(?=.*[A-Z])(?=.*[!@#$&*])(?=.*\d)(?=.*[a-z]).{8,}/;

    if (!full_name.trim()) {
        show_easyassist_toast("Please enter name to continue");
        return;
    }

    if (!regName.test(full_name)) {
        show_easyassist_toast("Please enter a valid name");
        return;
    }

    if (!mobile_number.trim()) {
        show_easyassist_toast("Please enter mobile number to continue");
        return;
    }

    if (!regMob.test(mobile_number)) {
        show_easyassist_toast("Please enter valid 10-digit mobile number");
        return;
    }

    if (old_password != "" || new_password != "" || confirm_password != "") {
        
        if(old_password == "") {
            show_easyassist_toast("Enter the Old Password");
            return;
        }

        if(new_password == "") {
            show_easyassist_toast("Enter the New Password");
            return;
        }

        if(confirm_password == "") {
            show_easyassist_toast("Enter the Confirm Password");
            return;
        }

        if (!regPass.test(new_password)) {
            show_easyassist_toast("Minimum length of password is 8 and must have at least one lowercase and one uppercase alphabetical character or has at least one lowercase and one numeric character or has at least one uppercase and one numeric character.");
            return;
        }
        let agent_name = agent_email.split('@')[0];
        if (new_password.indexOf(agent_name) >= 0) {
            show_easyassist_toast("Your new password is too similar to your username please use strong password.");
            return
        }
    }
    support_level = support_level.trim();
    if (support_level.toLowerCase() != 'l1' && support_level.toLowerCase() != 'l2' && support_level.toLowerCase() != 'l3') {
        show_easyassist_toast("Enter correct support level");
        return;
    }

    if(new_password != confirm_password) {
        show_easyassist_toast("New Password and Confirm Password does not match.");
        return;
    }

    let request_params = {
        "agent_name": full_name,
        "agent_mobile_number": mobile_number,
        "old_password": old_password,
        "new_password": new_password,
        "agent_support_level": support_level
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/save-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                if (response.is_password_changed) {
                    show_easyassist_toast("Password has been reset successfully. Please login again.");
                } else {
                    show_easyassist_toast("Saved successfully.");
                }
                setTimeout(function(e) {
                    window.location.reload();
                }, 2000);
            } else if (response.status == 101) {
                show_easyassist_toast("Your old password is incorrect. Kindly enter valid password.");
            } else if (response.status == 102) {
                show_easyassist_toast("Your new password is similar to your old password please use another strong password.");
            } else if (response.status == 301) {
                show_easyassist_toast(response.message);
            }
        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}

function save_admin_details(element) {

    var full_name = document.getElementById("admin-name").value;
    var old_password = document.getElementById("old-password").value;
    var new_password = document.getElementById("new-password").value;
    var confirm_password = document.getElementById("confirm-password").value;

    const regName = /^[^\s][a-zA-Z ]+$/;
    const regPass = /^(((?=.*[a-z])(?=.*[A-Z]))|((?=.*[a-z])(?=.*\d))|((?=.*[A-Z])(?=.*\d)))(?=.{8,})(?!.*[\s])/;
    
    if (!full_name.trim()) {
        show_easyassist_toast("Please enter name to continue.");
        return;
    }

    if (!regName.test(full_name)) {
        show_easyassist_toast("Please enter a valid name");
        return;
    }
     
    if (old_password != "" || new_password != "" || confirm_password != "") {
    
        if(old_password == "") {
            show_easyassist_toast("Enter the Old Password")
            return;
        }

        if(new_password == "") {
            show_easyassist_toast("Enter the New Password")
            return;
        }

        if(confirm_password == "") {
            show_easyassist_toast("Enter the Confirm Password");
            return;
        }

        if (!regPass.test(new_password)) {
            show_easyassist_toast("Minimum length of password is 8 and must have at least one lowercase and one uppercase alphabetical character or has at least one lowercase and one numeric character or has at least one uppercase and one numeric character.");
            return;
        }
    }

    if(new_password != confirm_password) {
        show_easyassist_toast("New Password and Confirm Password does not match.");
        return;
    }

    let request_params = {
        "agent_name": full_name,
        "old_password": old_password,
        "new_password": new_password
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/save-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                if (response.is_password_changed) {
                    show_easyassist_toast("Password has been reset successfully. Please login again.");
                } else {
                    show_easyassist_toast("Saved successfully.");
                }
                setTimeout(function(e) {
                    window.location.reload();
                }, 2000);
            } else if (response.status == 101) {
                show_easyassist_toast("Your old password is incorrect. Kindly enter valid password.");
            } else if (response.status == 102) {
                show_easyassist_toast("Your new password is similar to your old password please use another strong password.");
            } else if (response.status == 301) {
                show_easyassist_toast(response.message);
            }
        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}

function generate_drop_link(element) {
    let client_page_link = document.getElementById("client-page-link").value;
    let customer_name = document.getElementById("customer-name").value.trim();
    let customer_mobile_number = document.getElementById("customer-mobile-number").value.trim();
    let customer_email_id = document.getElementById("customer-email-id").value.trim();
    let url_error_element = document.getElementById("generate-drop-link-url-error");
    let name_error_element = document.getElementById("generate-drop-link-name-error");
    let mobile_error_element = document.getElementById("generate-drop-link-mobile-error");
    let email_error_element = document.getElementById("generate-drop-link-email-error");
    let general_error_message = document.getElementById("generate-drop-link-general-error");
    url_error_element.innerHTML = "";
    name_error_element.innerHTML = "";
    mobile_error_element.innerHTML = "";
    email_error_element.innerHTML = "";
    general_error_message.innerHTML = "";

    if(!client_page_link.length || !is_droplink_url_valid(client_page_link)){
        url_error_element.innerHTML =  "Please enter a valid Website URL";
        return;
    }

    if(!customer_name.length || !check_valid_name(customer_name)){
        name_error_element.innerHTML = "Please enter a valid Customer Name";
        return;
    }

    if(!customer_mobile_number || !check_valid_mobile_number(customer_mobile_number)){
        mobile_error_element.innerHTML = "Please enter a valid 10 digit mobile number";
        return;
    }

    if(IS_DROPLINK_EMAIL_MANDATORY == "True" && !customer_email_id.length && !check_valid_email(customer_email_id)){
        email_error_element.innerHTML = "Please enter a valid Customer Email ID";
        return;
    } else if(customer_email_id && !check_valid_email(customer_email_id)) {
        email_error_element.innerHTML = "Please enter a valid Customer Email ID";
        return;
    }

    let request_params = {
        "client_page_link": client_page_link,
        "customer_name": sanitize_input_string(customer_name),
        "customer_mobile_number": stripHTML(customer_mobile_number),
        "customer_email_id": sanitize_input_string(customer_email_id),
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Generating...";

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/generate-drop-link/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                document.getElementById("drop-link").value = response.generated_link;
                document.getElementById("generate-drop-link-button").innerHTML = "Close";
                document.getElementById("generate-drop-link-cobrowse-start-session-link-cancel").style.display = "none";
                document.getElementById("generate-drop-link-button").setAttribute("onclick","refresh_page()");
                document.getElementById("success-message-div").classList.remove("d-none");
                let modal_body_element = document.getElementById("generate_drop_link_modal");
                modal_body_element.scrollBehavior = "smooth"
                modal_body_element.scrollTop = modal_body_element.scrollHeight;
            } else if(response.status == 301){
                url_error_element.innerHTML = response.message;
                element.innerHTML = "Generate Link";
            } else if(response.status == 302){
                name_error_element.innerHTML = response.message;
                element.innerHTML = "Generate Link";
            } else if(response.status == 303){
                mobile_error_element.innerHTML = response.message;
                element.innerHTML = "Generate Link";
            } else if(response.status == 304){
                email_error_element.innerHTML = response.message;
                element.innerHTML = "Generate Link";
            } else {
               general_error_message.innerHTML = "Drop link could not be generated due to an internal issue on our end, please contact support if the issue persists";
               element.innerHTML = "Generate Link";
            }
        }
    }
    xhttp.send(params);

}


function add_new_agent(element) {

    var error_message_element = document.getElementById("add-new-agent-error");
    error_message_element.innerHTML = "";

    var full_name = document.getElementById("inline-form-input-agent-name").value.trim();
    full_name = stripHTML(full_name);

    var email = document.getElementById("inline-form-input-agent-email").value.trim();
    email = stripHTML(email);

    var mobile = document.getElementById("inline-form-input-agent-mobile").value.trim();
    mobile = stripHTML(mobile);

    const regName = /^[a-zA-Z ]+$/;
    const regMob = /^[6-9]{1}\d{9}$/;

    var platform_url = window.location.protocol + '//' + window.location.host;

    if (!full_name) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Full name cannot be empty.";
        return;
    }
    
    if (!regName.test(full_name)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter full name (only A-Z, a-z and space is allowed)";
        return;
    }

    full_name = remove_special_characters_from_str(full_name);

    if (!regEmail.test(email)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid Email Id.";
        return;
    }

    email = remove_special_characters_from_str(email);

    if (mobile != null && mobile != "" && !regMob.test(mobile)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid 10-digit mobile number";
        return;
    }

    mobile = remove_special_characters_from_str(mobile);

    var user_type = document.getElementById("inline-form-input-user-type");
    if (user_type != null && user_type != undefined) {
        if (user_type.value == "None") {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Please select valid user type";
            return;
        } else {
            user_type = user_type.value;
        }
    } else {
        user_type = "agent";
    }
    
    var support_level = document.getElementById("inline-form-input-agent-support-level").value;
    if (user_type == "admin_ally"){
        support_level = "L1";
    }
    if (support_level == "None") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please select valid agent support level";
        return;
    }

    let selected_supervisor_pk_list = [];
    
    if (user_type == "agent" || user_type == "admin_ally")
        selected_supervisor_pk_list = $("#inline-form-input-supervisor-pk").val();

    if (EASYASSIST_AGENT_ROLE == "admin_ally" && user_type =="agent" && selected_supervisor_pk_list.length == 0) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "No supervisor selected.";
        return;
    }    

    if (selected_supervisor_pk_list.length == 0)
        selected_supervisor_pk_list = [-1];
    
    var selected_language_pk_list = $("#easyassist-language-support-selected").val();

    if (selected_language_pk_list == undefined || selected_language_pk_list == null) {

        selected_language_pk_list = [];
    }

    var selected_product_category_pk_list = $("#easyassist-product-category-selected").val();

    if (selected_product_category_pk_list == undefined || selected_product_category_pk_list == null) {

        selected_product_category_pk_list = [];
    }

    var assign_followup_lead_to_agent_element = document.getElementById("assign_followup_lead_to_agent");
    var assign_followup_lead_to_agent;
    if (assign_followup_lead_to_agent_element) {
        assign_followup_lead_to_agent = assign_followup_lead_to_agent_element.checked;
    }

    let request_params = {
        "agent_name": full_name,
        "agent_email": email,
        "agent_mobile": mobile,
        "support_level": support_level,
        "user_type": user_type,
        "platform_url": platform_url,
        "selected_supervisor_pk_list": selected_supervisor_pk_list,
        "selected_language_pk_list": selected_language_pk_list,
        "selected_product_category_pk_list": selected_product_category_pk_list
    };

    if (assign_followup_lead_to_agent != undefined) {
        request_params["assign_followup_lead_to_agent"] = assign_followup_lead_to_agent;
    }

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/add-new-agent/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Saved successfully.";
                setTimeout(function(e) {
                    window.location.reload();
                }, 500);
            } else if (response.status == 301) {
                error_message_element.style.color = "orange";
                if (user_type == "agent") {
                    error_message_element.innerHTML = "Agent matching details already exists.";
                } else {
                    error_message_element.innerHTML = "Supervisor matching details already exists.";
                }
            } else if (response.status == 303) {
                error_message_element.style.color = "red";
                response_message = response.message;
                if (user_type == "admin_ally") {
                    if(response_message["matched_error"] == "language") {
                        error_message_element.innerHTML = "Supported language mismatch detected between supervisor " + response_message["supervisor"] +" and selected admin ally. Please update and try again.";
                    } else {
                        error_message_element.innerHTML = "Product category mismatch detected between supervisor " + response_message["supervisor"] +" and selected admin ally. Please update and try again.";
                    }
                } else {
                    if(response_message["matched_error"] == "language") {
                        error_message_element.innerHTML = "Supported language mismatch detected between supervisor " + response_message["supervisor"] +" and selected agent. Please update and try again.";
                    } else {
                        error_message_element.innerHTML = "Product category mismatch detected between supervisor " + response_message["supervisor"] +" and selected agent. Please update and try again.";
                    }
                }
            } else if (response.status == 401) {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = response["message"];
            } else if (response.status == 307) {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = response["message"];
            } else if (response.status == 309) {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = response["message"];
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Unable to save the details";
            }

        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}

function update_agent_details(element, pk) {

    let error_message_element = document.getElementById("save-agent-details-error");
    error_message_element.innerHTML = "";

    let full_name = document.getElementById("agent-name").value.trim();
    full_name = stripHTML(full_name);
    full_name = remove_special_characters_from_str(full_name);

    let email = document.getElementById("agent-email").value.trim();
    email = stripHTML(email);
    email = remove_special_characters_from_str(email);

    let mobile = document.getElementById("agent-mobile").value.trim();
    mobile = stripHTML(mobile);
    mobile = remove_special_characters_from_str(mobile);

    const regName = /^[^\s][a-zA-Z ]+$/;
    const regMob = /^[6-9]{1}\d{9}$/;

    let platform_url = window.location.protocol + '//' + window.location.host;

    if (!full_name) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Full name cannot be empty.";
        return;
    }

    if (!regName.test(full_name)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter full name (only A-Z, a-z and space is allowed)";
        return;
    }

    if (!regEmail.test(email)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid Email id.";
        return;
    }

    if (mobile != null && mobile != "" && !regMob.test(mobile)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid 10-digit mobile number";
        return;
    }

    let support_level = document.getElementById("agent-support-level").value;
    if (support_level == "None") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please select valid agent support level";
        return;
    }

    let user_type = document.getElementById("input-user-type");
    if (user_type != null && user_type != undefined) {
        if (user_type.value == "None") {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Please select valid user type";
            return;
        } else {
            user_type = user_type.value;
        }
    } else {
        user_type = "agent";
    }

    let selected_supervisor_pk_list = [];
    if (user_type == "agent" || user_type == "admin_ally")
        selected_supervisor_pk_list = $("#agent-supervisor-list").val();
    
    if (EASYASSIST_AGENT_ROLE == "admin_ally" && user_type =="agent" && selected_supervisor_pk_list.length == 0) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "No supervisor selected.";
        return;
    }   
    
    if (selected_supervisor_pk_list.length == 0)
        selected_supervisor_pk_list = [-1];

    let selected_language_pk_list = $("#language-support-selected").val();

    if (selected_language_pk_list == undefined || selected_language_pk_list == null) {

        selected_language_pk_list = [];
    }

    let selected_product_category_pk_list = $("#product-category-selected").val();

    if (selected_product_category_pk_list == undefined || selected_product_category_pk_list == null) {

        selected_product_category_pk_list = [];
    }

    let assign_followup_lead_to_agent_element = document.getElementById("assign-followup-lead-to-agent");
    let assign_followup_lead_to_agent;
    if(assign_followup_lead_to_agent_element) {
        assign_followup_lead_to_agent = assign_followup_lead_to_agent_element.checked;
    }

    let request_params = {
        "pk": pk,
        "agent_name": full_name,
        "agent_email": email,
        "agent_mobile": mobile,
        "support_level": support_level,
        "user_type": user_type,
        "platform_url": platform_url,
        "selected_supervisor_pk_list": selected_supervisor_pk_list,
        "selected_language_pk_list": selected_language_pk_list,
        "selected_product_category_pk_list": selected_product_category_pk_list
    };
    
    if(assign_followup_lead_to_agent != undefined) {
        request_params["assign_followup_lead_to_agent"] = assign_followup_lead_to_agent;
    }

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/update-agent-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Saved successfully.";
                setTimeout(function(e) {
                    window.location.reload();
                }, 500);
            } else if (response.status == 303) {
                error_message_element.style.color = "red";
                response_message = response.message;
                if (user_type == "admin_ally") {
                    if(response_message["matched_error"] == "language") {
                        error_message_element.innerHTML = "Supported language mismatch detected between supervisor " + response_message["supervisor"] +" and selected admin ally. Please update and try again.";
                    } else {
                        error_message_element.innerHTML = "Product category mismatch detected between supervisor " + response_message["supervisor"] +" and selected admin ally. Please update and try again.";
                    }
                } else {
                    if(response_message["matched_error"] == "language") {
                        error_message_element.innerHTML = "Supported language mismatch detected between supervisor " + response_message["supervisor"] +" and selected agent. Please update and try again.";
                    } else {
                        error_message_element.innerHTML = "Product category mismatch detected between supervisor " + response_message["supervisor"] +" and selected agent. Please update and try again.";
                    }
                }
            } else if (response.status == 307 || response.status == 311 || response.status == 309) {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = response["message"];
            } else if (response.status == 301) {
                error_message_element.style.color = "orange";
                error_message_element.innerHTML = "Agent matching details already exists.";
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Unable to save the details";
            }
        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}

function fetch_agents_for_lead_transfer() {
    var followup_lead_elements = document.getElementsByClassName('single-followup-cb');
    var selected_leads_id = [];
    for (var i = 0; i < followup_lead_elements.length; i++) {
        if (followup_lead_elements[i].checked) {
            selected_leads_id.push(followup_lead_elements[i].id.split("_")[3]);
        }
    }

    $("#lead-transfer-agents-dropdown").find('option').remove().end();
    $("#lead-transfer-agents-dropdown").selectpicker('refresh');

    if (selected_leads_id.length == 0) {
        show_easyassist_toast("Please select a lead to transfer");
        return;
    }

    let request_params = {
        "selected_leads_id": selected_leads_id
    };
    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/get-agents-for-followup-lead-transfer/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                
                let agents_list_for_lead_transfer = response["agents_list_for_lead_transfer"];
                let lead_transfer_agent_dropdown = document.getElementById("lead-transfer-agents-dropdown");
                let lead_transfer_agent_dropdown_div = document.getElementById("lead-transfer-agents-dropdown-div");
                let no_agents_available_message = document.getElementById("lead-transfer-no-agents-available");
            
                if(agents_list_for_lead_transfer.length > 0) {
                    
                    $(lead_transfer_agent_dropdown_div).removeClass('disabled');
                    $(lead_transfer_agent_dropdown_div).removeAttr('disabled');
                    no_agents_available_message.style.display = "none";
                    
                    for(let index = 0; index < agents_list_for_lead_transfer.length; index++) {
                        var val = agents_list_for_lead_transfer[index]["pk"];
                        var name = agents_list_for_lead_transfer[index]["username"];
                        $(lead_transfer_agent_dropdown).append('<option value="'+val+'">'+name+'</option>');
                    }

                } else {
                    $(lead_transfer_agent_dropdown_div).addClass('disabled');
                    $(lead_transfer_agent_dropdown_div).attr('disabled', true);
                    no_agents_available_message.style.display = "";
                }
                $(lead_transfer_agent_dropdown).selectpicker('refresh');
            } else {
                show_easyassist_toast("Enable to fetch agents for transferring lead.");
                console.error("Enable to fetch agents for transferring lead.");
            }
        }
    }
    xhttp.send(params);
}

function transfer_leads_to_agent() {
    var followup_lead_elements = document.getElementsByClassName('single-followup-cb');
    var selected_leads_id = [];
    for (var i = 0; i < followup_lead_elements.length; i++) {
        if (followup_lead_elements[i].checked) {
            selected_leads_id.push(followup_lead_elements[i].id.split("_")[3]);
        }
    }

    if (selected_leads_id.length == 0) {
        show_easyassist_toast("Please select a lead to transfer.");
        return;
    }

    let lead_transfer_agent_dropdown = document.getElementById("lead-transfer-agents-dropdown");
    let agent_pk = lead_transfer_agent_dropdown.value;
    if (agent_pk == undefined || agent_pk == "" || agent_pk == null) {
        show_easyassist_toast("Please select a agent to transfer the lead.");
        return;
    }

    let request_params = {
        "selected_leads_id": selected_leads_id,
        "agent_pk": agent_pk
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/transfer-followup-leads-to-agent/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            $("#transfer_lead_modal").modal("hide");
            if (response.status == 200) {
                show_transfer_lead_toast("successful");
                setTimeout(() => {
                    window.location.reload();
                }, 600);
            } else if (response.status == 300) {
                show_transfer_lead_toast("failure");
                console.error(response.message);
            } else {
                show_transfer_lead_toast("failure");
                console.error("Enable to transfer lead to selected agent.");
            }
        }
    }
    xhttp.send(params);
}

$(document).on("change", ".user-checkbox-collection", function(e) {
    let user_checkbox_collection = document.getElementsByClassName("user-checkbox-collection");
    document.getElementById("button-deactivate-account").style.display = "none";
    document.getElementById("button-activate-account").style.display = "none";
    let total_active_account = 0;
    let total_inactive_account = 0;
    for (let index = 0; index < user_checkbox_collection.length; index++) {
        if (user_checkbox_collection[index].checked == false) {
            continue;
        }
        if (user_checkbox_collection[index].nextElementSibling.value == "true") {
            total_active_account = 1;
        } else {
            total_inactive_account = 1;
        }
        if (total_inactive_account && total_active_account) {
            break;
        }
    }

    if (total_inactive_account > 0) {
        document.getElementById("button-activate-account").style.display = "flex";
    }
    if (total_active_account > 0) {
        document.getElementById("button-deactivate-account").style.display = "flex";
    }
});

$(document).on("change", ".supervisor-checkbox-collection", function(e) {
    let user_checkbox_collection = document.getElementsByClassName("supervisor-checkbox-collection");
    document.getElementById("supervisor-button-deactivate-account").style.display = "none";
    document.getElementById("supervisor-button-activate-account").style.display = "none";

    let total_active_account = 0;
    let total_inactive_account = 0;
    for (let index = 0; index < user_checkbox_collection.length; index++) {
        if (user_checkbox_collection[index].checked == false) {
            continue;
        }
        if (user_checkbox_collection[index].nextElementSibling.value == "True" || user_checkbox_collection[index].nextElementSibling.value == true) {
            total_active_account = 1;
        } else {
            total_inactive_account = 1;
        }
        if (total_inactive_account && total_active_account) {
            break;
        }
    }

    if (total_inactive_account > 0) {
        document.getElementById("supervisor-button-activate-account").style.display = "flex";
    }
    if (total_active_account > 0) {
        document.getElementById("supervisor-button-deactivate-account").style.display = "flex";
    }
});

function deactivate_user(element, is_agent=false) {
    let user_checkbox_collection = document.getElementsByClassName("supervisor-checkbox-collection");
    if(is_agent) {
        user_checkbox_collection = document.getElementsByClassName("user-checkbox-collection");
    }
    let agent_id_list = [];
    for (let index = 0; index < user_checkbox_collection.length; index++) {
        if (user_checkbox_collection[index].checked) {
            agent_id_list.push(user_checkbox_collection[index].id.split("-")[2]);
        }
    }

    if (agent_id_list.length == 0) {
        return;
    }

    let request_params = {
        "agent_id_list": agent_id_list,
        "activate": false
    };
    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/change-agent-activate-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 301) {
                show_easyassist_toast(response.message);
                return;
            }
            if (response.status != 200) {
                show_easyassist_toast("Unable to change agent activate status");
            }
            window.location.reload();
        }
    }
    xhttp.send(params);
}

function resend_password(pk) {
    let platform_url = window.location.protocol + '//' + window.location.host;

    let request_params = {
        "user_pk": pk,
        "platform_url": platform_url
    };
    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/resend-account-password/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_easyassist_toast(response.message);
            } else {
                show_easyassist_toast("Could not send the password. Please try again.");
            }
        }
    }
    xhttp.send(params);
}

function show_agent_details(status) {
    let request_params = get_url_vars();
    let updated_request_params = "";
    if ("pk" in request_params) {
        updated_request_params += "pk=" + request_params["pk"];
    }

    if (updated_request_params.length > 0) {
        updated_request_params += "&";
    }

    updated_request_params += filter_agent_status(status);
    if (updated_request_params.length > 0)
        window.location.href = window.location.pathname + "?" + updated_request_params;
    else
        window.location.href = window.location.pathname;
    
}

function filter_agent_status(status) {
    if (status == "online") {
        return "is_active=" + true;
    } else if (status == "offline") {
        return "is_active=" + false;
    } else if (status == "active") {
        return "is_account_active=" + true;
    } else if (status == "inactive") {
        return "is_account_active=" + false;
    } else if(status == "available-agents") {
        return "available_agents=" + true;
    } else if(status == "busy-agents") {
        return "busy_agents=" + true;
    } else {
        return "";
    }
}

function upload_user_excel_details(element) {
    var file = user_details_upload_input_file_global;
    var error_element = document.getElementById("user_details_upload_input_error");

    try {
        error_element.nextElementSibling.remove();
    } catch (err) {}

    if (file == undefined || file == null) {
        error_element.style.color = "red";
        error_element.innerHTML = "Please choose a file of excel format.";
        return;
    }

    var malicious_file_report = check_malicious_file(file.name)
    if (malicious_file_report.status == true) {
        show_easyassist_toast(malicious_file_report.message)
        return false
    }

    var filename = file.name;
    if(check_file_name(filename)) {
        show_easyassist_toast("Please don't use special characters other than hyphen (-) and underscore (_) in the file name");
        remove_uploaded_file();
        return;
    }
    var fileExtension = "";
    if (filename.lastIndexOf(".") > 0) {
        fileExtension = filename.substring(filename.lastIndexOf(".") + 1, filename.length);
    }
    fileExtension = fileExtension.toLowerCase();
    var excel_extensions = ["xls", "xlsx", "xlsm", "xlt", "xltm"];
    if (!excel_extensions.includes(fileExtension)) {
        error_element.style.color = "red";
        error_element.innerHTML = "Please choose a file of excel format.";
        return;
    }

    element.innerText = "Uploading...";
    var reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = function() {

        let base64_str = reader.result.split(",")[1];

        var json_string = {
            "filename": file.name,
            "base64_file": base64_str,
        };

        json_string = JSON.stringify(json_string);

        let encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/upload-user-details/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                let response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response.status == 200) {
                    error_element.style.color = "green";
                    error_element.innerHTML = "Uploaded successfully.";
                    setTimeout(function() {
                        window.location.reload();
                    }, 1000);
                } else if (response["status"] == 300) {
                    error_element.style.color = "red";
                    error_element.innerHTML = "File format not supported. Please don't use .(dot) in filename except for extension."
                } else if (response["status"] == 301) {
                    error_element.style.color = "red";
                    error_element.innerHTML = "File is empty. Please add agent details to create agents."
                } else if (response["status"] == 302) {
                    error_element.style.color = "red";
                    error_element.innerHTML = response.message
                    var html_error_file = [
                        '<a href="/' + response["file_path"] + '">',
                        '<svg width="19" height="17" viewBox="0 0 19 17" fill="none" xmlns="http://www.w3.org/2000/svg">',
                        '<path d="M11.4584 0H5.38271C4.94133 0 4.58337 0.357958 4.58337 0.799333V4.12637H11.4584V0Z" fill="#169154"/>',
                        '<path d="M4.58337 12.3997V15.7006C4.58337 16.142 4.94133 16.5 5.38225 16.5H11.4584V12.3997H4.58337Z" fill="#18482A"/>',
                        '<path d="M4.58337 4.12637H11.4584V8.25229H4.58337V4.12637Z" fill="#0C8045"/>',
                        '<path d="M4.58337 8.25236H11.4584V12.4003H4.58337V8.25236Z" fill="#17472A"/>',
                        '<path d="M17.534 0H11.4584V4.12637H18.3334V0.799333C18.3334 0.357958 17.9754 0 17.534 0Z" fill="#29C27F"/>',
                        '<path d="M11.4584 12.3997V16.5H17.5345C17.9754 16.5 18.3334 16.142 18.3334 15.7011V12.4002H11.4584V12.3997Z" fill="#27663F"/>',
                        '<path d="M11.4584 4.12637H18.3334V8.25229H11.4584V4.12637Z" fill="#19AC65"/>',
                        '<path d="M11.4584 8.25236H18.3334V12.4003H11.4584V8.25236Z" fill="#129652"/>',
                        '<path d="M8.39621 12.8334H0.770458C0.345125 12.8334 0 12.4883 0 12.063V4.4372C0 4.01187 0.345125 3.66674 0.770458 3.66674H8.39621C8.82154 3.66674 9.16667 4.01187 9.16667 4.4372V12.063C9.16667 12.4883 8.82154 12.8334 8.39621 12.8334Z" fill="#0C7238"/>',
                        '<path d="M2.66157 5.95826H3.75515L4.64248 7.67884L5.58023 5.95826H6.60186L5.19432 8.24992L6.63394 10.5416H5.5564L4.58932 8.74034L3.62636 10.5416H2.53278L3.99623 8.24167L2.66157 5.95826Z" fill="white"/>',
                        '</svg>',
                        '<span class="error-file-text"> Error File</span>',
                        '</a>',
                    ].join('');
                    error_element.insertAdjacentHTML("afterend", html_error_file)
                } else {
                    error_element.style.color = "red";
                    error_element.innerHTML = "Could not upload the excel document. Please try again.";
                }
            } else {
                error_element.style.color = "red";
                error_element.innerHTML = "Could not upload the excel document. Please try again.";
            }
            element.innerText = "Upload";
        }
        xhttp.send(params);

    };

    reader.onerror = function(error) {
        console.log('Error: ', error);
    };

}

function export_user_excel_details(element) {
    const params = "";

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/export-user-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path"] != null) {
                let export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else {
                show_easyassist_toast("Unable to download agent details");
            }
        }
    }
    xhttp.send(params);
}

function export_supervisor_excel_details(element) {
    const params = "";

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/export-supervisor-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path"] != null) {
                let export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else {
                show_easyassist_toast("Unable to download supervisor details");
            }
        }
    }
    xhttp.send(params);
}

function download_user_details_excel_template(element) {
    const params = "";

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/download-user-details-excel-template/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path"] != null) {
                let export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else {
                show_easyassist_toast("Unable to download template");
            }
        }
    }
    xhttp.send(params);
}


function change_disabled_on_floating_button_settings(checked) {
    $("#show_floating_easyassist_button").attr("disabled", checked);
    $("#floating_button_position").attr("disabled", checked);
    $("#floating_button_bg_color").attr("disabled", checked);
}

function change_disabled_on_connect_agent_icon_settings(checked) {
    $("#connect_with_agent_icon_upload_button").attr("disabled", checked);
    $("#show_easyassist_connect_agent_icon").attr("disabled", checked);
}

function change_disabled_on_agent_unavailable_settings(checked) {
    $("#disable_connect_button_if_agent_unavailable").attr("disabled", checked);
}

function change_disabled_on_agent_available_settings(checked) {
    $("#show_only_if_agent_available").attr("disabled", checked);
}

function set_on_change_events_settings() {

    let checked = $("#show_only_if_agent_available").is(":checked");
    change_disabled_on_agent_unavailable_settings(checked);

    checked = $("#disable_connect_button_if_agent_unavailable").is(":checked");
    change_disabled_on_agent_available_settings(checked);

    $("#show_only_if_agent_available").change(function() {
        let is_checked = $("#show_only_if_agent_available").is(":checked");
        change_disabled_on_agent_unavailable_settings(is_checked);
    });

    $("#disable_connect_button_if_agent_unavailable").change(function() {
        let is_checked = $("#disable_connect_button_if_agent_unavailable").is(":checked");
        change_disabled_on_agent_available_settings(is_checked);
    });
}

set_on_change_events_settings();

// "source_easyassist_connect_agent_icon": document.getElementById("source_easyassist_connect_agent_icon").value,

function save_cobrowsing_meta_details_cobrowsing(element) {

    var error_message_element = document.getElementById("save-cobrowsing-meta-details-error-cobrowsing");
    error_message_element.innerHTML = "";

    if (document.getElementById("enable_predefined_remarks").checked && (!predefined_remarks_array || predefined_remarks_array.length == 0)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Enter the required fields in predefined remarks to save the changes";
        return;
    }

    var predefined_remarks_list_with_buttons = document.getElementById("predefined_remarks_with_buttons").value;
    if (document.getElementById("enable_predefined_remarks_with_buttons").checked && (!predefined_remarks_list_with_buttons || predefined_remarks_list_with_buttons.length == 0)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Enter the required fields in predefined remarks to save the changes";
        return;
    }

    var archive_on_common_inactivity_threshold = document.getElementById("archive_on_common_inactivity_threshold");
    if (archive_on_common_inactivity_threshold && (archive_on_common_inactivity_threshold.value <= 0 || archive_on_common_inactivity_threshold.value > 60)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Session Inactivity: Values between 1 and 60 are allowed.";
        return;
    }
    
    var drop_link_expiry_time = document.getElementById("drop_link_expiry_time");
    if (drop_link_expiry_time && (drop_link_expiry_time.value <= 0 || drop_link_expiry_time.value > 60)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Generate Drop Link Expiry: Time between 1 and 60 min are allowed.";
        return;
    }

    var urls_consider_lead_converted = document.getElementById("urls_consider_lead_converted").value;
    if(urls_consider_lead_converted.length != 0) {
        let lead_converted_urls_list = urls_consider_lead_converted.split(",")
        for (let link in lead_converted_urls_list) {
            let is_valid = is_url_valid(lead_converted_urls_list[link].trim())
            if (is_valid == false) {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "The entered URL is not valid: " + lead_converted_urls_list[link];
                return;
            }
        }
    }

    var restricted_urls = document.getElementById("restricted_urls").value;
    if(restricted_urls.length != 0) {
        let restricted_urls_list = restricted_urls.split(",")
        for (let link in restricted_urls_list) {
            let is_valid = is_url_valid(restricted_urls_list[link].trim())
            if (is_valid == false) {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "The entered URL is not valid: " + restricted_urls_list[link];
                return;
            }
        }
    }

    var reconnecting_window_timer_input_field = document.getElementById("reconnecting_window_timer_input_field");
    if (!reconnecting_window_timer_input_field.value) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a positive integer for reconnecting window timer.";
        return;
    }

    let request_params = {
        "enable_edit_access": document.getElementById("enable_edit_access").checked,
        "masking_type": document.getElementById("input-masking-type").value,
        "allow_screen_recording": document.getElementById("allow_screen_recording").checked,
        "recording_expires_in_days": (document.getElementById("recording_expires_in_days") == undefined || document.getElementById("recording_expires_in_days") == null) ? 15 : document.getElementById("recording_expires_in_days").value,
        "lead_conversion_checkbox_text": remove_special_characters_from_str(stripHTML(document.getElementById("lead_conversion_checkbox_text").value)),
        "allow_video_calling_cobrowsing": document.getElementById("allow_video_calling_cobrowsing").checked,
        "allow_screen_sharing_cobrowse": document.getElementById("allow_screen_sharing_cobrowse").checked,
        "enable_predefined_remarks": document.getElementById("enable_predefined_remarks").checked,
        "enable_predefined_subremarks": document.getElementById("enable_predefined_subremarks").checked,
        "enable_predefined_remarks_with_buttons": document.getElementById("enable_predefined_remarks_with_buttons").checked,
        "predefined_remarks_list": predefined_remarks_array,
        "predefined_remarks_with_buttons": document.getElementById("predefined_remarks_with_buttons").value,
        "predefined_remarks_optional":  document.getElementById("input-predefined-remark-optional-checkbox").checked,
        "enable_screenshot_agent": document.getElementById("enable_screenshot_agent").checked,
        "enable_invite_agent_in_cobrowsing": document.getElementById("enable_invite_agent_in_cobrowsing").checked,
        "enable_agent_connect_message": document.getElementById("enable_agent_connect_message").checked,
        "agent_connect_message": remove_special_characters_from_str(stripHTML(document.getElementById("agent_connect_message").value)),
        "enable_masked_field_warning": document.getElementById("enable_masked_field_warning").checked,
        "masked_field_warning_text": remove_special_characters_from_str(stripHTML(document.getElementById("masked_field_warning_text").value)),
        "enable_voip_with_video_calling": document.getElementById("enable_voip_with_video_calling").checked,
        "enable_voip_calling": document.getElementById("enable_voip_calling").checked,
        "voip_calling_text": remove_special_characters_from_str(stripHTML(document.getElementById("voip_calling_text").value)),
        "voip_with_video_calling_text": remove_special_characters_from_str(stripHTML(document.getElementById("voip_with_video_calling_text").value)),
        "enable_auto_voip_with_video_calling_for_first_time": document.getElementById("enable_auto_voip_with_video_calling_for_first_time").checked,
        "enable_auto_voip_calling_for_first_time": document.getElementById("enable_auto_voip_calling_for_first_time").checked,
        "show_verification_code_modal": document.getElementById("show_verification_code_modal").checked,
        "enable_verification_code_popup": document.getElementById("enable_verification_code_popup").checked,
        "assistant_message": remove_special_characters_from_str(stripHTML(document.getElementById("assistant_message").value)),
        "urls_consider_lead_converted": document.getElementById("urls_consider_lead_converted").value,
        "restricted_urls": document.getElementById("restricted_urls").value,
        "archive_on_common_inactivity_threshold": document.getElementById("archive_on_common_inactivity_threshold").value,
        "drop_link_expiry_time": document.getElementById("drop_link_expiry_time").value,
        "enable_low_bandwidth_cobrowsing": document.getElementById("enable_low_bandwidth_cobrowsing").checked,
        "enable_manual_switching": document.getElementById("enable_manual_switching").checked,
        "low_bandwidth_cobrowsing_threshold": document.getElementById("low_bandwidth_cobrowsing_threshold").value,
        "enable_smart_agent_assignment": document.getElementById("enable_smart_agent_assignment").checked,
        "reconnecting_window_timer_input": document.getElementById("reconnecting_window_timer_input_field").value,
        "customer_initiate_video_call": document.getElementById("customer_initiate_video_call").checked,
        "customer_initiate_voice_call": document.getElementById("customer_initiate_voice_call").checked,
        "customer_initiate_video_call_as_pip": document.getElementById("customer_initiate_video_call_as_pip").checked,
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/save-cobrowsing-meta-details/cobrowsing/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Saved successfully.";
                setTimeout(function() {
                    error_message_element.style.display = "none"
                    let params = new URLSearchParams(window.location.search)
                    if(params.has('days') || params.has('years') || params.has('month') || params.has('calendar_updated')){
                        window.location.href = window.location.href.replace( /[\?#].*|$/, "#pills-options-tab");
                    } else {
                        window.location.href = window.location.href.replace( /[\?#].*|$/, "#pills-options-tab");
                        location.reload();
                    }
                }, 1000);
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Unable to save the details";
            }
        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}

function save_subremarks(element, type) {
    var error_message_element = document.getElementById("save-subremarks-error");
    error_message_element.innerHTML = "";

    var predefined_subremarks_list = []; 
    var remark = $('#subRemarkModal').find('#subremark-remark-field').html();
    var subremarks_element_list = $('#subRemarkModal').find('.subremark-value');
    for(let idx = 0; idx < subremarks_element_list.length; idx++){
        predefined_subremarks_list.push({"remark":subremarks_element_list[idx].value});
    }
    
    //remove special characters
    predefined_subremarks_list.forEach((ele) => {
        var val = ele['remark'];
        val = remove_special_characters_from_str(val);
        ele['remark'] = val;
    });
    
    //length and duplicate check
    for(let idx = 0; idx < predefined_subremarks_list.length; idx ++) {
        var value = predefined_subremarks_list[idx]["remark"];
        if(value.length < 2) {
            show_easyassist_toast("Predefined Sub-remark should be atleast 2 characters long");
            return;
        }

        var cnt = 0;
        predefined_subremarks_list.forEach(function(sub_remark) {
            if(sub_remark == value) {
                cnt ++;
            }
        });

        if(cnt > 1) {
            show_easyassist_toast("Duplicate Sub-remarks are not allowed");
            return;
        }
    }

    for(let idx = 0; idx < predefined_remarks_array.length; idx++) {
        if(predefined_remarks_array[idx].remark == remark) {
            predefined_remarks_array[idx].subremark = predefined_subremarks_list;
            break;
        }
    }

    element.innerHTML = "Saving...";
    setTimeout(function() {
        element.innerHTML = "Save";
        $('#subRemarkModal').modal('hide');
    }, 500);
}

function save_cobrowsing_meta_details_meeting(element) {

    let error_message_element = document.getElementById("save-cobrowsing-meta-details-error-meeting");
    error_message_element.innerHTML = "";

    var meeting_url = document.getElementById("meeting_url").value;
    if (!is_url_valid(meeting_url)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "The entered meeting URL is not valid.";
        return;
    }

    var no_agent_connects_meeting_toast_threshold = document.getElementById("no_agent_connects_meeting_toast_threshold");
    if (no_agent_connects_meeting_toast_threshold && no_agent_connects_meeting_toast_threshold.value <= 0) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "No Agent permit meeting toast time should be greater than 0.";
        return;
    }

    var no_agent_connects_meeting_toast_text_ele = document.getElementById("no_agent_connects_meeting_toast_text");
    var no_agent_connects_meeting_toast_text = "";
    if(no_agent_connects_meeting_toast_text_ele) {
        no_agent_connects_meeting_toast_text = remove_special_characters_from_str(stripHTML(no_agent_connects_meeting_toast_text_ele.value))
        if(no_agent_connects_meeting_toast_text.length == 0 || no_agent_connects_meeting_toast_text.length >= 1024) {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "No agent permit meeting toast text length should be greater than 1 and less than 1024 characters.";
            return;
        }
    }

    let request_params = {
        "proxy_server": document.getElementById("proxy_pass_server").value,
        "meeting_url": document.getElementById("meeting_url").value,
        "meeting_default_password": stripHTML(document.getElementById("meeting_default_password").value),
        "show_cobrowsing_meeting_lobby": document.getElementById("show_cobrowsing_meeting_lobby").checked,
        "meet_background_color": document.getElementById("meet_background_color").value,
        "allow_meeting_feedback": document.getElementById("allow_meeting_feedback").checked,
        "allow_meeting_end_time": document.getElementById("allow_meeting_end_time").checked,
        "meeting_end_time": document.getElementById("meeting_end_time").value,
        "allow_capture_screenshots": document.getElementById("allow_capture_screenshots").checked,
        "enable_invite_agent_in_meeting": document.getElementById("enable_invite_agent_in_meeting").checked,
        "allow_video_meeting_only": document.getElementById("allow_video_meeting_only").checked,
        "enable_no_agent_connects_toast_meeting": document.getElementById("no_agent_connects_toast_meeting").checked,
        "no_agent_connects_meeting_toast_threshold": document.getElementById("no_agent_connects_meeting_toast_threshold").value,
        "no_agent_connects_meeting_toast_text": no_agent_connects_meeting_toast_text,
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/save-cobrowsing-meta-details/meeting/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Saved successfully.";
                setTimeout(function() {
                    error_message_element.style.display = "none"
                    let params = new URLSearchParams(window.location.search)
                    if(params.has('days') || params.has('years') || params.has('month') || params.has('calendar_updated')){
                        window.location.href = window.location.href.replace( /[\?#].*|$/, "#pills-options-tab");
                    } else {
                        window.location.href = window.location.href.replace( /[\?#].*|$/, "#pills-options-tab");
                        location.reload();
                    }
                }, 1000);
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Unable to save the details";
            }
        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}


function save_cobrowsing_meta_details_general(element) {
    var product_category_list = document.getElementById("product_category_list").value;
    if ((document.getElementById("choose_product_category").checked || document.getElementById("enable_tag_based_assignment_for_outbound").checked) && (!product_category_list || product_category_list.length == 0)) {
        show_easyassist_toast("Enter the required fields in product category to save the changes");
        return;
    }

    var disable_connect_button_if_agent_unavailable = document.getElementById("disable_connect_button_if_agent_unavailable").checked;
    var message_if_agent_unavailable = document.getElementById("message_if_agent_unavailable").value;
    if (disable_connect_button_if_agent_unavailable && (!message_if_agent_unavailable || message_if_agent_unavailable.length == 0)) {
        show_easyassist_toast("Enter the required message to be shown to the customers to save the changes");
        return;
    }

    var show_easyassist_connect_agent_icon = document.getElementById("show_easyassist_connect_agent_icon").checked;
    if (show_easyassist_connect_agent_icon && !window.is_icon_for_connect_with_agent) {
        show_easyassist_toast("Upload the logo to save the changes");
        return;
    }

    var cobrowsingconsole_theme_color_el = document.getElementById("cobrowsing-console-theme-color");
    var cobrowsing_console_theme_color = null;
    if (cobrowsingconsole_theme_color_el.jscolor.toHEXString() != '#FFFFFF') {
        cobrowsing_console_theme_color = {
            "red": cobrowsingconsole_theme_color_el.jscolor.rgb[0],
            "green": cobrowsingconsole_theme_color_el.jscolor.rgb[1],
            "blue": cobrowsingconsole_theme_color_el.jscolor.rgb[2],
            "rgb": cobrowsingconsole_theme_color_el.jscolor.toRGBString(),
            "hex": cobrowsingconsole_theme_color_el.jscolor.toHEXString(),
        };
    }

    var no_agent_connects_toast_threshold = document.getElementById("no_agent_connects_toast_threshold");
    if (no_agent_connects_toast_threshold && (no_agent_connects_toast_threshold.value <= 0 || no_agent_connects_toast_threshold.value > 60)) {
        show_easyassist_toast("No Agent connects session toast : Values between 1 and 60 are allowed.");
        return;
    }

    var no_agent_connect_timer_reset_count = document.getElementById("no_agent_connect_timer_reset_count");
    if (no_agent_connect_timer_reset_count && (parseInt(no_agent_connect_timer_reset_count.value) < 0 || !no_agent_connect_timer_reset_count.value.length)) {
        show_easyassist_toast("No. of times 'No Agent Connect Timer' resets cannot be negative.");
        return;
    }

    var no_agent_connect_timer_reset_message = document.getElementById("no_agent_connect_timer_reset_message");
    if (no_agent_connect_timer_reset_message && (no_agent_connect_timer_reset_message.value.trim().length == 0 || no_agent_connect_timer_reset_message.value.trim().length > 1024)) {
        show_easyassist_toast("Length of 'Timer reset toast' should be between 0 to 1024 characters.");
        return;
    }

    var auto_archive_lead_timer_input = document.getElementById("auto-archive-lead-timer-input");
    if (auto_archive_lead_timer_input && (auto_archive_lead_timer_input.value <= 0 || auto_archive_lead_timer_input.value > 120)) {
        show_easyassist_toast("Auto Archive Timer value should be between 1-120 minutes.");
        return;
    }
    
    var auto_archive_popup_text = document.getElementById("auto-archive-popup-text");
    if (auto_archive_popup_text && auto_archive_popup_text.value.trim() != "" && auto_archive_popup_text.value.trim().length > 160) {
        show_easyassist_toast("Auto archive pop up text cannot be greater than 160 characters.");
        return;
    }

    var maximum_active_leads_threshold = document.getElementById("maximum_active_leads_threshold");
    if (!maximum_active_leads_threshold.value) {
        show_easyassist_toast("Please enter a positive integer for Max leads.");
        return;
    }

    if (maximum_active_leads_threshold && maximum_active_leads_threshold.value <= 0) {
        show_easyassist_toast("Max leads cannot be a negative number or zero. Choose a number greater than or equal to 1.");
        return;
    }

    var decimal_re = /\./;
    if (maximum_active_leads_threshold && (maximum_active_leads_threshold.value.match(decimal_re) != null)) {
        show_easyassist_toast("Max leads cannot be a decimal number. Choose a number greater than or equal to 1.");
        return;
    }
    
    var auto_assign_unattended_lead_timer = document.getElementById("auto_assign_unattended_lead_timer_input");
    if (auto_assign_unattended_lead_timer && !auto_assign_unattended_lead_timer.value) {
        show_easyassist_toast("Auto-assign timer cannot be left blank.");
        return;
    }

    var auto_assign_unattended_lead_transfer_count = document.getElementById("auto_assign_unattended_lead_transfer_count");
    if (auto_assign_unattended_lead_transfer_count && (auto_assign_unattended_lead_transfer_count.value < 1 || auto_assign_unattended_lead_transfer_count.value > 30)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "\"Lead Transfer Count\" value should be between 1-30.";
        return;
    }

    if (auto_assign_unattended_lead_timer && auto_assign_unattended_lead_timer.value <= 0) {
        show_easyassist_toast("Auto-assign timer cannot be a negative number or zero. Choose a number greater than or equal to 1.");
        return;
    }

    var decimal_re = /\./;
    if (auto_assign_unattended_lead_timer && (auto_assign_unattended_lead_timer.value.match(decimal_re) != null)) {
        show_easyassist_toast("Auto-assign timer cannot be a decimal number. Choose a number greater than or equal to 1.");
        return;
    }

    var unattended_lead_archive_timer_input = document.getElementById("unattended-lead-archive-timer-input");
    if (unattended_lead_archive_timer_input && (unattended_lead_archive_timer_input.value <= 0 || unattended_lead_archive_timer_input.value > 120)) {
        show_easyassist_toast("Auto end session timer value should be between 1-120 minutes.");
        return;
    }

    var auto_assign_unattended_lead_message = document.getElementById("auto_assign_unattended_lead_message");
    var enable_auto_assign_unattended_lead = document.getElementById("enable_auto_assign_unattended_lead");
    if(auto_assign_unattended_lead_message && enable_auto_assign_unattended_lead && enable_auto_assign_unattended_lead.checked) {
        if(auto_assign_unattended_lead_message.value.trim().length == 0 || auto_assign_unattended_lead_message.value.trim().length >= 1024) {
            show_easyassist_toast("Lead auto-assigned to another agent message length should be greater than 1 and less than 1024 characters.");
            return;
        }
    }
    
    var auto_assign_lead_end_session_message = document.getElementById("auto_assign_lead_end_session_message");
    var enable_auto_assign_to_one_agent = document.getElementById("enable_auto_assign_to_one_agent");
    if(auto_assign_lead_end_session_message && enable_auto_assign_unattended_lead && enable_auto_assign_to_one_agent &&
         enable_auto_assign_to_one_agent.checked && enable_auto_assign_unattended_lead.checked) {
        if(auto_assign_lead_end_session_message.value.trim().length == 0 || auto_assign_lead_end_session_message.value.trim().length >= 1024) {
            show_easyassist_toast("Auto end session message length should be greater than 1 and less than 1024 characters.");
            return;
        }
    }

    var exit_intent_popup_count_ele = document.getElementById("exit-intent-popup-count");
    if (exit_intent_popup_count_ele && exit_intent_popup_count_ele.value.match(decimal_re) != null) {
        show_easyassist_toast("Value of number of times exit intent should popup cannot be a decimal");
        return;
    }

    var password_prefix_value = document.getElementById("cobrowsing_default_password_prefix").value;
    const regexPasswordPrefix = /^[0-9a-zA-Z]+$/;
    if (!password_prefix_value.match(regexPasswordPrefix)) {
        show_easyassist_toast("Password prefix can only comprise of alphabets and numbers.");
        return;
    }

    var deploy_chatbot_flag_element = document.getElementById("deploy_chatbot_flag");
    if (deploy_chatbot_flag_element.checked) {
        var deploy_chatbot_url = document.getElementById("deploy_chatbot_url").value;
        deploy_chatbot_url = stripHTML(deploy_chatbot_url);
        if(deploy_chatbot_url == ""){
            show_easyassist_toast("Chatbot CJS script cannot be empty.");
            return;
        }
        try{
            new window.URL(deploy_chatbot_url);
        } catch (error){
            console.error("ERROR: ", error);
            show_easyassist_toast("Chatbot CJS script is not valid. Please enter valid CJS script.");
            return
        }
    }

    var go_live_date = document.getElementById("go_live_date").value;
    if(!go_live_date) {
        show_easyassist_toast("Please enter valid Go-Live date");
        return;
    }
    go_live_date = get_iso_formatted_date(go_live_date);

    var easyassit_font_family = document.getElementById("easyassit_font_family").value;
    var regex = /[+]/g;
    easyassit_font_family = easyassit_font_family.replace(regex, " ");

    var floating_button_left_right_position = document.getElementById("floating_button_left_right_position").value.trim();
    if(floating_button_left_right_position == "") {
        show_easyassist_toast("Please enter valid floating button position threshold");
        return;
    }
    

    var white_listed_domains = document.getElementById("whitelisted_domain").value;
    if(white_listed_domains.length != 0) {
        let white_listed_domains_list = white_listed_domains.split(",")
        for (let link in white_listed_domains_list) {
            let is_valid = is_url_valid(white_listed_domains_list[link].trim())
            if (white_listed_domains_list[link].trim() == "*") is_valid = true;
            if (is_valid == false) {
                show_easyassist_toast("The entered URL in whitelisted domains field is not valid: " + white_listed_domains_list[link]);
                return;
            }
        }
    }

    var greeting_bubble_text = document.getElementById("greeting_bubble_text").value;
    if(greeting_bubble_text.length > 100){
        show_easyassist_toast("Greeting Bubble Text should be less than 100 characters.");
        return;
    }
    if(greeting_bubble_text.length == 0){
        show_easyassist_toast("Greeting Bubble Text cannot be left empty.");
        return;
    }
    
    var inactivity_auto_popup_number = document.getElementById("inactivity_auto_popup_number");
    if (inactivity_auto_popup_number && inactivity_auto_popup_number.value <= 0) {
        show_easyassist_toast("Value of number of times inactivity pop-up number should be greater than 0.");
        return;
    }
    if (inactivity_auto_popup_number && (inactivity_auto_popup_number.value.match(decimal_re) != null)) {
        show_easyassist_toast("Value of number of times inactivity pop-up number should not be a decimal.");
        return;
    }

    let request_params = {
        "enable_inbound": document.getElementById("enable_inbound").checked,
        "cobrowsing_console_theme_color": cobrowsing_console_theme_color,
        "enable_greeting_bubble": document.getElementById("enable_greeting_bubble").checked,
        "greeting_bubble_auto_popup_timer": document.getElementById("greeting_bubble_auto_popup_timer").value,
        "greeting_bubble_text": remove_special_characters_from_str(stripHTML(document.getElementById("greeting_bubble_text").value)),
        "show_floating_easyassist_button": document.getElementById("show_floating_easyassist_button").checked,
        "floating_button_position": document.getElementById("floating_button_position").value,
        "floating_button_bg_color": document.getElementById("floating_button_bg_color").value,
        "show_easyassist_connect_agent_icon": document.getElementById("show_easyassist_connect_agent_icon").checked,
        "show_only_if_agent_available": document.getElementById("show_only_if_agent_available").checked,
        "disable_connect_button_if_agent_unavailable": document.getElementById("disable_connect_button_if_agent_unavailable").checked,
        "message_if_agent_unavailable": remove_special_characters_from_str(stripHTML(document.getElementById("message_if_agent_unavailable").value)),
        "message_on_non_working_hours": remove_special_characters_from_str(stripHTML(document.getElementById("message_on_non_working_hours").value)),
        "field_stuck_event_handler": document.getElementById("field_stuck_event_handler").checked,
        "field_recursive_stuck_event_check": document.getElementById("field_recursive_stuck_event_check").checked,
        "get_sharable_link": document.getElementById("get_sharable_link").checked,
        "lead_generation": document.getElementById("lead_generation").checked,
        "field_stuck_timer": document.getElementById("field_stuck_timer").value,
        "archive_on_unassigned_time_threshold": remove_special_characters_from_str(stripHTML(document.getElementById("auto-archive-lead-timer-input").value)),
        "archive_message_on_unassigned_time_threshold": remove_special_characters_from_str(stripHTML(document.getElementById("auto-archive-popup-text").value.trim())),
        "inactivity_auto_popup_number": document.getElementById("inactivity_auto_popup_number").value,
        "connect_message": remove_special_characters_from_str(stripHTML(document.getElementById("connect_message").value)),
        "whitelisted_domain": document.getElementById("whitelisted_domain").value,
        "allow_only_support_documents": document.getElementById("allow_only_support_documents").checked,
        "allow_language_support": document.getElementById("allow_language_support").checked,
        "supported_language_list": document.getElementById("supported_language_list").value,
        "go_live_date": go_live_date,
        "choose_product_category": document.getElementById("choose_product_category").checked,
        "product_category_list": document.getElementById("product_category_list").value,
        "allow_support_documents": document.getElementById("allow_support_documents").checked,
        "share_document_from_livechat": document.getElementById("share_document_from_livechat").checked,
        "enable_chat_functionality": document.getElementById("enable_chat_functionality").checked,
        "enable_preview_functionality": document.getElementById("enable_preview_functionality").checked,
        "enable_chat_bubble": document.getElementById("enable_chat_bubble").checked,
        "message_on_choose_product_category_modal": remove_special_characters_from_str(stripHTML(document.getElementById("message_on_choose_product_category_modal").value)),
        "enable_non_working_hours_modal_popup": document.getElementById("enable_non_working_hours_modal_popup").checked,
        "no_agent_connects_toast": document.getElementById("no_agent_connects_toast").checked,
        "no_agent_connects_toast_threshold": document.getElementById("no_agent_connects_toast_threshold").value,
        "no_agent_connects_toast_text": remove_special_characters_from_str(stripHTML(document.getElementById("no_agent_connects_toast_text").value)),
        "no_agent_connect_timer_reset_message": remove_special_characters_from_str(stripHTML(document.getElementById("no_agent_connect_timer_reset_message").value)),
        "no_agent_connect_timer_reset_count": remove_special_characters_from_str(stripHTML(document.getElementById("no_agent_connect_timer_reset_count").value)),
        "auto_assigned_unattended_lead_archive_timer": remove_special_characters_from_str(stripHTML(document.getElementById("unattended-lead-archive-timer-input").value)),        
        "show_floating_button_after_lead_search": document.getElementById("show_floating_button_after_lead_search").checked,
        "enable_tag_based_assignment_for_outbound": document.getElementById("enable_tag_based_assignment_for_outbound").checked,
        "enable_followup_leads_tab": document.getElementById("enable_followup_leads_tab").checked,
        "allow_popup_on_browser_leave": document.getElementById("allow_popup_on_browser_leave").checked,
        "enable_recursive_browser_leave_popup": document.getElementById("enable_recursive_browser_leave_popup").checked,
        "exit_intent_popup_count": document.getElementById("exit-intent-popup-count").value,
        "maximum_active_leads": document.getElementById("maximum_active_leads").checked,
        "maximum_active_leads_threshold": document.getElementById("maximum_active_leads_threshold").value,
        "password_prefix": document.getElementById("cobrowsing_default_password_prefix").value,
        "deploy_chatbot_flag": document.getElementById("deploy_chatbot_flag").checked,
        "deploy_chatbot_url": stripHTML(document.getElementById("deploy_chatbot_url").value),
        "easyassit_font_family": easyassit_font_family,
        "floating_button_left_right_position": floating_button_left_right_position,
        "enable_auto_offline_agent": document.getElementById("auto_offline_agent").checked,
        "enable_auto_assign_unattended_lead": document.getElementById("enable_auto_assign_unattended_lead").checked,
        "enable_auto_assign_to_one_agent": document.getElementById("enable_auto_assign_to_one_agent").checked,
        "assign_agent_under_same_supervisor": document.getElementById("assign_agent_under_same_supervisor").checked,
        "auto_assign_unattended_lead_timer": remove_special_characters_from_str(stripHTML(document.getElementById("auto_assign_unattended_lead_timer_input").value)),
        "auto_assign_unattended_lead_transfer_count": remove_special_characters_from_str(stripHTML(document.getElementById("auto_assign_unattended_lead_transfer_count").value)),
        "auto_assign_unattended_lead_message": remove_special_characters_from_str(stripHTML(document.getElementById("auto_assign_unattended_lead_message").value)),
        "auto_assign_lead_end_session_message": remove_special_characters_from_str(stripHTML(document.getElementById("auto_assign_lead_end_session_message").value)),
        "display_agent_profile":document.getElementById("display_agent_profile").checked,
        "allow_agent_to_customer_cobrowsing": document.getElementById("allow_agent_to_customer_cobrowsing").checked,
        "allow_agent_to_screen_record_customer_cobrowsing": document.getElementById("allow_agent_to_screen_record_customer_cobrowsing").checked,
        "allow_agent_to_audio_record_customer_cobrowsing": document.getElementById("allow_agent_to_audio_record_customer_cobrowsing").checked,
    };

    if (document.getElementById("allow_agent_to_customer_cobrowsing").checked) {
        show_easyassist_toast('Since the Reverse Cobrowsing toggle has been enabled, some of the settings will be disabled.')
    }

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/save-cobrowsing-meta-details/general/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_easyassist_toast("Saved successfully.");
                setTimeout(function() {
                    let params = new URLSearchParams(window.location.search)
                    if(params.has('days') || params.has('years') || params.has('month') || params.has('calendar_updated')){
                        window.location.href = window.location.href.replace( /[\?#].*|$/, "#pills-options-tab");
                    } else {
                        window.location.href = window.location.href.replace( /[\?#].*|$/, "#pills-options-tab");
                        location.reload();
                    }
                }, 1000);
            } else {
                show_easyassist_toast("Unable to save the details");
            }
        }

        element.innerHTML = "Save";
    }
    xhttp.send(params);
}


function reset_cobrowsing_meta_details(element) {

    var settings_option_tabs = document.getElementById("pills-options");
    
    var error_message_element = null;
    
    let request_params = {
        "reset": true,
        "general": true,
        "cobrowse": true,
        "meeting": true,
    };

    let cognomeet_request_params = {
        "cognomeet_access_token": window.COGNOMEET_ACCESS_TOKEN,
        "reset_config": true
    };

    save_config_in_cognomeet(cognomeet_request_params);

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/reset-cobrowsing-meta-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_easyassist_toast("Reset successfully.");
                setTimeout(function() {
                    window.location.href = window.location.origin + window.location.pathname;
                    location.reload();
                }, 1000);
            } else {
                show_easyassist_toast("Unable to reset details");
            }
        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}

function delete_cobrowse_logo() {
    let encrypted_data = "";
    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/delete-cobrowser-logo/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        setTimeout(function() {
            window.location.href = window.location.origin + window.location.pathname +  "#pills-options-tab";
        }, 300);
    }
    xhttp.send(params);
}

function upload_cobrowse_logo(el) {
    var file = cobrowse_logo_input_file_global;
    if (file == undefined || file == null) {
        show_easyassist_toast("Please choose a file.");
        return;
    }

    var malicious_file_report = check_malicious_file(file.name)
    if (malicious_file_report.status == true) {
        show_easyassist_toast(malicious_file_report.message)
        return false
    }

    if (check_image_file(file.name) == false) {
        return false;
    }

    if (file.size / 1000000 > 5) {
        show_easyassist_toast("File size cannot exceed 5 MB");
        $("#cobrowse_logo_input")[0].value = "";
        return;
    }

    el.innerText = "Uploading..."
    var reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = function() {

        let base64_str = reader.result.split(",")[1];

        var json_string = {
            "filename": file.name,
            "base64_file": base64_str,
        };

        json_string = JSON.stringify(json_string);

        let encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/upload-cobrowser-logo/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                let response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response["status"] == 200)
                {
                    document.getElementById('cobrowse-logo-image-data').innerHTML = 
                    '<div class="row">\
                      <div class="col-md-6 col-sm-12" style="padding-left: 0.7em;display: flex;align-items: center;">\
                        <button class="mb-2 mr-sm-2" data-toggle="modal" type="button" data-target="#cobrowse_logo_upload_modal" id="cobrowse_logo_upload_button">Change Logo\
                        </button>\
                      </div>\
                      <div class="col-md-6 col-sm-12">\
                        <img src="/'+ response.file_path +'" id="cobrowse-logo-image" style="height: 9em; display: inline-box; width: 100%;">\
                      </div>\
                    </div>'
                    document.getElementById("cobrowseLogoImage").src = window.location.origin + '/' + response.file_path;
                    document.getElementById("cobrowse_image_file_upload_bar").style.display = "none";
                    document.getElementById("modal_cobrowse_image_buttons").innerHTML = 
                        '<button class="btn btn-outline-primary mr-auto" onclick="delete_cobrowse_logo()" style="margin-right: auto !important;">Delete</button>\
                        <button class="btn btn-text-only" type="button" data-dismiss="modal" id="cobrowse_logo_upload_modal_close">Cancel</button>\
                        <button class="btn btn-primary" onclick="upload_cobrowse_logo(this)">Upload</button>';
                    document.getElementById("cobrowse_logo_upload_modal_close").click();
                    el.innerText = "Upload";
                } else {
                    if (response["status"] == 300) {
                        show_easyassist_toast("Invalid file format")
                    } else {
                       show_easyassist_toast("Internal server error. Please try again later.") 
                    }

                }
            } else {
                document.getElementById("cobrowse_logo_upload_modal_close").click()
                el.innerText = "Upload";
            }
        }
        xhttp.send(params);

    };

    reader.onerror = function(error) {
        console.log('Error: ', error);
    };
}


function upload_connect_with_agent_icon() {
    var file = connect_with_agent_icon_input_file_global;

    if (file == undefined || file == null) {
        show_easyassist_toast("Please choose a file.");
        return;
    }

    var malicious_file_report = check_malicious_file(file.name)
    if (malicious_file_report.status == true) {
        show_easyassist_toast(malicious_file_report.message)
        return false
    }

    if (check_image_file(file.name) == false) {
        return false;
    }

    if (file.size / 1000000 > 5) {
        show_easyassist_toast("File size cannot exceed 5 MB");
        return;
    }

    var reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = function() {

        let base64_str = reader.result.split(",")[1];

        var json_string = {
            "filename": file.name,
            "base64_file": base64_str,
        };

        json_string = JSON.stringify(json_string);

        let encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/upload-connect-with-agent-icon/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                setTimeout(function() {
                    window.location.href = window.location.origin + window.location.pathname +  "#pills-options-tab";
                }, 300);
            } else {
                window.location.reload();
            }
        }
        xhttp.send(params);

    };

    reader.onerror = function(error) {
        console.log('Error: ', error);
    };
}

function add_new_masking_field(element) {
    let error_message_element = document.getElementById("add-new-masking-field-error");
    error_message_element.innerHTML = "";

    let field_key = document.getElementById("inline-form-input-masking-field-key").value.trim();
    let field_value = document.getElementById("inline-form-input-masking-field-value").value.trim();
    let masking_type = document.getElementById("inline-form-input-masking-type").value.trim();
    const regex = /^[^\s]+$/;

    if (!regex.test(field_key)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid masking field key (without whitespaces)";
        return;
    }

    if(!field_value) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Masking field value cannot be empty";
        return;
    }

    if (masking_type == null || masking_type == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please choose a masking type";
        return;
    }

    let request_params = {
        "field_key": field_key,
        "field_value": field_value,
        "masking_type": masking_type
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/add-new-obfuscated-field/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Saved successfully";
                setTimeout(function(e) {
                    window.location.href = window.location.href.replace(/[\?#].*|$/, "#pills-settings-tab");
                    window.location.reload();
                }, 2000);
            } else if (response.status == 301) {
                error_message_element.style.color = "orange";
                error_message_element.innerHTML = "Field matching details already exists";
            } else if (response.status == 302) {
                error_message_element.style.color = "orange";
                error_message_element.innerHTML = "Masking field value cannot be empty";
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Unable to save the details";
            }
        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}

function save_masking_field(element, field_id) {
    var error_message_element = document.getElementById("edit-masking-field-error-" + field_id);
    error_message_element.innerHTML = "";
    error_message_element.style.display = "none";

    var field_key = document.getElementById("edit-masking-field-key-" + field_id).value;
    var field_value = document.getElementById("edit-masking-field-value-" + field_id).value;
    var masking_type = document.getElementById("edit-masking-type-" + field_id).value;
    const regex = /^[^\s]+$/;


    if (!regex.test(field_key)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid masking field key (without whitespaces).";
        error_message_element.style.display = "";
        return;
    }

    if (masking_type == null || masking_type == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please choose a masking type.";
        error_message_element.style.display = "";
        return;
    }

    let request_params = {
        "field_key": field_key,
        "field_value": field_value,
        "masking_type": masking_type,
        "field_id": field_id,
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/edit-obfuscated-field/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Saved successfully.";
                error_message_element.style.display = "";
                setTimeout(function(e) {
                    window.location.href = window.location.href.replace(/[\?#].*|$/, "#pills-settings-tab");
                    window.location.reload();
                }, 2000);
            } else if (response.status == 301) {
                error_message_element.style.color = "orange";
                error_message_element.innerHTML = "Masking field does not exists.";
                error_message_element.style.display = "";
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Unable to save the details.";
                error_message_element.style.display = "";
            }
        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}

function delete_masking_field(element, field_id) {

    var obfuscated_field_id_list = [field_id];

    if (obfuscated_field_id_list.length == 0) {
        return;
    }

    element.innerText = "Deleting...";
    let request_params = {
        "obfuscated_field_id_list": obfuscated_field_id_list
    };
    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/delete-obfuscated-fields/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status != 200) {
                show_easyassist_toast("Unable to delete obfuscated fields");
            }

            element.innerText = "Delete";
            window.location.href = window.location.href.replace(/[\?#].*|$/, "#pills-settings-tab");
            window.location.reload();
        }
    }
    xhttp.send(params);
}

function add_new_search_tag_field(element) {
    let error_message_element = document.getElementById("add-new-search-tag-field-error");
    error_message_element.innerHTML = "";

    var tag = document.getElementById("inline-form-input-search-tag").value;
    var tag_label = document.getElementById("inline-form-input-search-tag-label").value;
    var tag_key = document.getElementById("inline-form-input-search-tag-key").value;
    var tag_value = document.getElementById("inline-form-input-search-tag-value").value;
    var tag_type = document.getElementById("inline-form-input-search-tag-type").value;
    let unique_identifier = document.getElementById("enable-mark-unique-identifier").checked;
    
    tag_label = stripHTML(tag_label);
    tag_label = remove_special_characters_from_str(tag_label);

    const regex = /^[^\s]+$/;

    if (tag == null || tag == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please choose a tag.";
        return;
    }

    if (tag_label == null || tag_label.trim() == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid tag label.";
        return;
    }

    if (!regex.test(tag_key)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid tag key (without whitespaces).";
        return;
    }

    if (!regex.test(tag_value)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid tag value (without whitespaces).";
        return;
    }

    if (tag_type == null || tag_type == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please choose a tag type.";
        return;
    }
    let request_params = {
        "tag": tag,
        "tag_label": tag_label,
        "tag_key": tag_key,
        "tag_value": tag_value,
        "tag_type": tag_type,
        "unique_identifier":unique_identifier,
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/add-new-search-tag-field/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Saved successfully.";
                setTimeout(function(e) {
                    window.location.href = window.location.href.replace(/[\?#].*|$/, "#pills-settings-tab");
                    window.location.reload();
                }, 2000);
            } else if (response.status == 301) {
                error_message_element.style.color = "orange";
                error_message_element.innerHTML = "Field matching details already exists.";
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Unable to save the details.";
            }
        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}

function save_search_tag_field(element, field_id) {
    let error_message_element = document.getElementById("edit-search-tag-field-error-" + field_id);
    error_message_element.innerHTML = "";
    error_message_element.style.display = "none";

    var tag = document.getElementById("edit-search-tag-" + field_id).value;
    var tag_label = document.getElementById("edit-search-tag-label-" + field_id).value;
    var tag_key = document.getElementById("edit-search-tag-key-" + field_id).value;
    var tag_value = document.getElementById("edit-search-tag-value-" + field_id).value;
    var tag_type = document.getElementById("edit-search-tag-type-" + field_id).value;
    let edit_unique_identifier = document.getElementById("edit-unique-identifier-" + field_id).checked;
    
    tag_label = stripHTML(tag_label);
    tag_label = remove_special_characters_from_str(tag_label);

    const regex = /^[^\s]+$/;

    if (tag == null || tag == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please choose a tag.";
        error_message_element.style.display = "";
        return;
    }

    if (tag_label == null || tag_label.trim() == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid tag label.";
        error_message_element.style.display = "";
        return;
    }

    if (!regex.test(tag_key)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid tag key (without whitespaces).";
        error_message_element.style.display = "";
        return;
    }

    if (!regex.test(tag_value)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid tag value (without whitespaces).";
        error_message_element.style.display = "";
        return;
    }

    if (tag_type == null || tag_type == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please choose a tag type.";
        error_message_element.style.display = "";
        return;
    }
    let request_params = {
        "tag": tag,
        "tag_label": tag_label,
        "tag_key": tag_key,
        "tag_value": tag_value,
        "tag_type": tag_type,
        "field_id": field_id,
        "unique_identifier": edit_unique_identifier,
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/edit-search-tag-field/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Saved successfully.";
                error_message_element.style.display = "";
                setTimeout(function(e) {
                    window.location.href = window.location.href.replace(/[\?#].*|$/, "#pills-settings-tab");
                    window.location.reload();
                }, 2000);
            } else if (response.status == 301) {
                error_message_element.style.color = "orange";
                error_message_element.innerHTML = "Field matching details does not exists.";
                error_message_element.style.display = "";
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Unable to save the details.";
                error_message_element.style.display = "";
            }
        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}

function delete_search_tag_field(element, field_id) {
    var search_tag_field_id_list = [field_id];

    if (search_tag_field_id_list.length == 0) {
        return;
    }

    let request_params = {
        "search_tag_field_id_list": search_tag_field_id_list
    };
    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    element.innerText = "Deleting ...";
    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/delete-search-tag-fields/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status != 200) {
                show_easyassist_toast("Unable to delete search tag fields");
            }
            element.innerText = "Delete";

            window.location.href = window.location.href.replace(/[\?#].*|$/, "#pills-settings-tab");
            window.location.reload();
        }
    }
    xhttp.send(params);
}

function add_auto_fetch_field(element) {
    let error_message_element = document.getElementById("add-new-auto-fetch-field-error");
    error_message_element.innerHTML = "";

    var fetch_field_key = document.getElementById("inline-form-input-fetch-field-key").value;
    var fetch_field_value = document.getElementById("inline-form-input-fetch-field-value").value;
    var modal_field_key = document.getElementById("inline-form-input-modal-field-key").value;
    var modal_field_value = document.getElementById("inline-form-input-modal-field-value").value;
    const regex = /^[^\s]+$/;

    if (!regex.test(fetch_field_key)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid fetch field key (without whitespaces).";
        return;
    }

    if (!regex.test(fetch_field_value)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid fetch field value (without whitespaces).";
        return;
    }

    if (!regex.test(modal_field_key)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid modal field key (without whitespaces).";
        return;
    }

    if (!regex.test(modal_field_value)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid modal field value (without whitespaces).";
        return;
    }

    let request_params = {
        "fetch_field_key": fetch_field_key,
        "fetch_field_value": fetch_field_value,
        "modal_field_key": modal_field_key,
        "modal_field_value": modal_field_value
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/add-new-auto-fetch-field/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Saved successfully.";
                setTimeout(function(e) {
                    window.location.href = window.location.href.replace(/[\?#].*|$/, "#pills-settings-tab");
                    window.location.reload();
                }, 2000);
            } else if (response.status == 301) {
                error_message_element.style.color = "orange";
                error_message_element.innerHTML = "Field matching details already exists.";
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Unable to save the details.";
            }
        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}

function save_auto_fetch_field(element, field_id) {
    var error_message_element = document.getElementById("edit-auto-fetch-field-error-" + field_id);
    error_message_element.innerHTML = "";
    error_message_element.style.display = "none";

    var fetch_field_key = document.getElementById("edit-auto-fetch-field-key-" + field_id).value;
    var fetch_field_value = document.getElementById("edit-auto-fetch-field-value-" + field_id).value;
    var modal_field_key = document.getElementById("edit-auto-fetch-field-modal-key-" + field_id).value;
    var modal_field_value = document.getElementById("edit-auto-fetch-field-modal-value-" + field_id).value;
    const regex = /^[^\s]+$/;

    if (!regex.test(fetch_field_key)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid fetch field key (without whitespaces).";
        error_message_element.style.display = "";
        return;
    }

    if (!regex.test(fetch_field_value)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid fetch field value (without whitespaces).";
        error_message_element.style.display = "";
        return;
    }

    if (!regex.test(modal_field_key)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid modal field key (without whitespaces).";
        error_message_element.style.display = "";
        return;
    }

    if (!regex.test(modal_field_value)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid modal field value (without whitespaces).";
        error_message_element.style.display = "";
        return;
    }

    let request_params = {
        "fetch_field_key": fetch_field_key,
        "fetch_field_value": fetch_field_value,
        "modal_field_key": modal_field_key,
        "modal_field_value": modal_field_value,
        "field_id": field_id,
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/edit-auto-fetch-field/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Saved successfully.";
                error_message_element.style.display = "";
                setTimeout(function(e) {
                    window.location.href = window.location.href.replace(/[\?#].*|$/, "#pills-settings-tab");
                    window.location.reload();
                }, 2000);
            } else if (response.status == 301) {
                error_message_element.style.color = "orange";
                error_message_element.innerHTML = "Field matching details does not exists.";
                error_message_element.style.display = "";
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Unable to save the details.";
                error_message_element.style.display = "";
            }
        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}

function delete_auto_fetch_field(element, field_id) {

    var auto_fetch_field_id_list = [field_id];

    if (auto_fetch_field_id_list.length == 0) {
        return;
    }

    let request_params = {
        "auto_fetch_field_id_list": auto_fetch_field_id_list
    };
    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    element.innerText = "Deleting ...";

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/delete-auto-fetch-fields/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status != 200) {
                show_easyassist_toast("Unable to delete auto fetch fields");
            }

            element.innerText = "Delete";
            window.location.href = window.location.href.replace(/[\?#].*|$/, "#pills-settings-tab");
            window.location.reload();
        }
    }
    xhttp.send(params);
}

/////////////////////////// update_captured_lead //////////////////////

var searched_session_id_list = [];

function update_captured_lead() {

    let search_error = document.getElementById("search-primary-value-error");
    search_error.style.color = "none";
    search_error.innerHTML = "";

    let search_field = document.getElementById("search-primary-value");
    if (search_field.value == "") {
        search_error.style.color = "red";
        search_error.innerHTML = "Please enter valid search value";
        return;
    }

    let request_params = {
        "session_id_list": searched_session_id_list,
        "search_value": remove_special_characters_from_str(stripHTML(search_field.value))
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/search-lead/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status == 200) {
                let cobrowse_io_details = response.cobrowse_io_details;
                let show_verification_code = response.show_verification_code;
                let allow_cobrowsing_meeting = response.allow_cobrowsing_meeting;
                let allow_video_meeting_only = response.allow_video_meeting_only;
                if (cobrowse_io_details.length == 0) {
                    return;
                }
                var search_message = '';

                for (let index = 0; index < cobrowse_io_details.length; index++) {

                    var active_inactive = '<i class="fas fa-fw fa-check-square text-success"></i>';
                    if (cobrowse_io_details[index]["is_active"] == false) {
                        active_inactive = '<i class="fas fa-fw fa-times-circle text-danger"></i>';
                    }

                    var request_button = "";
                    var meeting_button = "";
                    if (cobrowse_io_details[index]["is_active"] == true) {

                        if (cobrowse_io_details[index]["allow_agent_cobrowse"] == "true") {
                            // connect agent with client screen
                            request_button = '<button class="btn btn-success float-md-right" onclick="assign_lead_to_agent(\'' + cobrowse_io_details[index]['session_id'] + '\',  \'' + cobrowse_io_details[index]['share_client_session'] + '\')">Connect</button>';
                            search_message = '<div><p style="color:green;"><b>Request for assistance has been accepted by the Customer</b></p> </div>';
                        } else if (cobrowse_io_details[index]["allow_agent_cobrowse"] == "false") {
                            // requested for assistance but client doesn't allowed
                            request_button = '<button class="btn btn-primary float-md-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request Co-browsing</button>';
                            search_message = '<p style="color:red;"><b>Request for assistance has been denied by the customer. Kindly make sure, you are connected with client on call.</b></p>';
                        } else {
                            if (cobrowse_io_details[index]["agent_assistant_request_status"] == true) {
                                // requested for assistance but state has not been changed
                                request_button = '<button class="btn btn-primary float-md-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Resend Request</button>';
                                search_message = '<p style="color:orange;"><b>Request for assistance has been sent to the customer.</b></p>';
                            } else {
                                request_button = '<button class="btn btn-primary float-md-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request Co-browsing</button>';
                            }
                        }

                        if (allow_video_meeting_only == true || allow_cobrowsing_meeting == true) {
                            if (cobrowse_io_details[index]["allow_agent_meeting"] == "true") {
                                // connect agent with client screen
                                meeting_button += '<button class="btn btn-success float-md-right" onclick="connect_with_client(\'' + cobrowse_io_details[index]['session_id'] + '\')">Connect</button>';
                            } else if (cobrowse_io_details[index]["allow_agent_meeting"] == "false") {
                                // requested for assistance but client doesn't allowed
                                meeting_button += '<button class="btn btn-primary float-md-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                                search_message = '<p style="color:red;"><b>Request for meeting has been denied by the customer.</b></p>';
                            } else {
                                if (cobrowse_io_details[index]["agent_meeting_request_status"] == true) {
                                    meeting_button += '<button class="btn btn-primary float-md-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Resend Request</button>';
                                    search_message = '<p style="color:orange;"><b>Request for meeting has been sent to the customer.</b></p>';
                                } else {
                                    meeting_button += '<button class="btn btn-primary float-md-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                                }
                            }
                        }
                    }
                    document.getElementById("active_inactive_" + cobrowse_io_details[index]["session_id"]).innerHTML = active_inactive
                    if (allow_video_meeting_only == false) {
                        document.getElementById("request_button_" + cobrowse_io_details[index]["session_id"]).innerHTML = request_button
                        if (allow_cobrowsing_meeting == true) {
                            document.getElementById("meeting_button_" + cobrowse_io_details[index]["session_id"]).innerHTML = meeting_button
                        }
                        if (show_verification_code) {
                            document.getElementById("otp_" + cobrowse_io_details[index]["session_id"]).innerHTML = cobrowse_io_details[index]["otp"]
                        }
                    } else {
                        document.getElementById("meeting_button_" + cobrowse_io_details[index]["session_id"]).innerHTML = meeting_button
                    }
                    let easyassist_table = document.querySelector(".easy-assist-table");
                    easyassist_table.nextElementSibling.innerHTML = search_message
                }
            }
        }
    }
    xhttp.send(params);
}

function search_for_captured_lead() {
    let session_details_element = document.getElementById("running-session-details");
    session_details_element.innerHTML = "";

    let search_error = document.getElementById("search-primary-value-error");
    search_error.style.color = "none";
    search_error.innerHTML = "";

    let search_field = document.getElementById("search-primary-value");
    if (search_field.value == "") {
        search_error.style.color = "red";
        search_error.innerHTML = "Please enter valid search value";
        return;
    }

    let request_params = {
        "search_value": remove_special_characters_from_str(stripHTML(search_field.value))
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/search-lead/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                let cobrowse_io_details = response.cobrowse_io_details;
                let show_verification_code = response.show_verification_code;
                let allow_cobrowsing_meeting = response.allow_cobrowsing_meeting;
                let allow_video_meeting_only = response.allow_video_meeting_only;
                if (cobrowse_io_details.length == 0) {
                    session_details_element.innerHTML = "No active customer with that details found. Please wait for some time, or ask the customer to refresh the page and then try again.";
                } else {
                    var session_details_table = "";
                    if (allow_video_meeting_only == true) {
                        session_details_table = '<p>Session Details</p>\
                                    <table class="table easy-assist-table">\
                                      <thead>\
                                          <tr>\
                                              <th>Request Date & Time</th>\
                                            <th>Active/Inactive</th>\
                                            <th>Meeting</th>\
                                        </tr>\
                                    </thead>';
                    } else if (allow_cobrowsing_meeting == true) {
                        if (show_verification_code == false) {
                            session_details_table = '<p>Session Details</p>\
                                    <table class="table easy-assist-table">\
                                      <thead>\
                                          <tr>\
                                              <th>Request Date & Time</th>\
                                            <th>Active/Inactive</th>\
                                            <th>Cobrowsing</th>\
                                            <th>Meeting</th>\
                                        </tr>\
                                    </thead>';
                        } else {
                            session_details_table = '<p>Session Details</p>\
                                    <table class="table easy-assist-table">\
                                      <thead>\
                                          <tr>\
                                              <th>Request Date & Time</th>\
                                            <th>Active/Inactive</th>\
                                            <th>Support Code</th>\
                                            <th>Cobrowsing</th>\
                                            <th>Meeting</th>\
                                        </tr>\
                                    </thead>';
                        }
                    } else {
                        if (show_verification_code == false) {
                            session_details_table = '<p>Session Details</p>\
                                    <table class="table easy-assist-table">\
                                      <thead>\
                                          <tr>\
                                              <th>Request Date & Time</th>\
                                            <th>Active/Inactive</th>\
                                            <th>Cobrowsing</th>\
                                        </tr>\
                                    </thead>';
                        } else {
                            session_details_table = '<p>Session Details</p>\
                                    <table class="table easy-assist-table">\
                                      <thead>\
                                          <tr>\
                                              <th>Request Date & Time</th>\
                                            <th>Active/Inactive</th>\
                                            <th>Support Code</th>\
                                            <th>Cobrowsing</th>\
                                        </tr>\
                                    </thead>';
                        }

                    }
                    var search_message = '<p></p>';

                    for (let index = 0; index < cobrowse_io_details.length; index++) {

                        searched_session_id_list.push(cobrowse_io_details[index]["session_id"])

                        var active_inactive = '<i class="fas fa-fw fa-check-square text-success"></i>';
                        if (cobrowse_io_details[index]["is_active"] == false) {
                            active_inactive = '<i class="fas fa-fw fa-times-circle text-danger"></i>';
                        }

                        var request_button = "";
                        var meeting_button = "";
                        if (cobrowse_io_details[index]["is_active"] == true) {
                            if (cobrowse_io_details[index]["allow_agent_cobrowse"] == "true") {
                                // connect agent with client screen
                                request_button = '<button class="btn btn-success float-md-right" onclick="assign_lead_to_agent(\'' + cobrowse_io_details[index]['session_id'] + '\', \'' + cobrowse_io_details[index]['share_client_session'] + '\')">Connect</button>';
                                search_message = '<div><p style="color:green;"><b>Request for assistance has been accepted by the customer.</b></p></div>';
                                search_field.setAttribute("disabled", "disabled");
                            } else if (cobrowse_io_details[index]["allow_agent_cobrowse"] == "false") {
                                // requested for assistance but client doesn't allowed
                                request_button = '<button class="btn btn-primary float-md-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request Co-browsing</button>';
                                search_message = '<p style="color:red;"><b>Request for assistance has been denied by the customer. Kindly make sure, you are connected with client on call.</b></p>';
                            } else {
                                if (cobrowse_io_details[index]["agent_assistant_request_status"] == true) {
                                    // requested for assistance but state has not been changed
                                    request_button = '<button class="btn btn-primary float-md-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Resend Request</button>';
                                    search_field.setAttribute("disabled", "disabled");
                                    search_message = '<p style="color:orange;"><b>Request for assistance has been sent to the customer</b></p>';
                                } else {
                                    request_button = '<button class="btn btn-primary float-md-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request Co-browsing</button>';
                                }
                            }
                            if (allow_video_meeting_only == true || allow_cobrowsing_meeting == true) {
                                if (cobrowse_io_details[index]["allow_agent_meeting"] == "true") {
                                    // connect agent with client screen
                                    meeting_button += '<button class="btn btn-success float-md-right" onclick="connect_with_client(\'' + cobrowse_io_details[index]['session_id'] + '\')">Connect</button>';
                                } else if (cobrowse_io_details[index]["allow_agent_meeting"] == "false") {
                                    // requested for assistance but client doesn't allowed
                                    meeting_button += '<button class="btn btn-primary float-md-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                                    search_message = '<p style="color:red;"><b>Request for meeting has been denied by the customer.</b></p>';
                                } else {
                                    if (cobrowse_io_details[index]["agent_meeting_request_status"] == true) {
                                        meeting_button += '<button class="btn btn-primary float-md-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Resend Request</button>';
                                        search_message = '<p style="color:orange;"><b>Request for meeting has been sent to the customer.</b></p>';
                                    } else {
                                        meeting_button += '<button class="btn btn-primary float-md-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                                    }
                                }
                            }
                        }
                        if (allow_video_meeting_only == true) {
                            session_details_table += '<tbody>\
                                  <tr>\
                                      <td>' + cobrowse_io_details[index]["datetime"] + '</td>\
                                      <td id = "active_inactive_' + cobrowse_io_details[index]["session_id"] + '">' + active_inactive + '</td>\
                                      <td id = "meeting_button_' + cobrowse_io_details[index]["session_id"] + '">' + meeting_button + '</td>\
                                  </tr>\
                                </tbody>';
                        } else if (allow_cobrowsing_meeting == true) {
                            if (show_verification_code == false) {
                                session_details_table += '<tbody>\
                                  <tr>\
                                      <td>' + cobrowse_io_details[index]["datetime"] + '</td>\
                                      <td id = "active_inactive_' + cobrowse_io_details[index]["session_id"] + '">' + active_inactive + '</td>\
                                      <td id = "request_button_' + cobrowse_io_details[index]["session_id"] + '">\
                                        ' + request_button + '\
                                      </td><td id = "meeting_button_' + cobrowse_io_details[index]["session_id"] + '">' + meeting_button + '</td>\
                                  </tr>\
                                </tbody>';
                            } else {
                                session_details_table += '<tbody>\
                                  <tr>\
                                      <td>' + cobrowse_io_details[index]["datetime"] + '</td>\
                                      <td id = "active_inactive_' + cobrowse_io_details[index]["session_id"] + '">' + active_inactive + '</td>\
                                      <td id = "otp_' + cobrowse_io_details[index]["session_id"] + '">' + cobrowse_io_details[index]["otp"] + '</td>\
                                      <td id = "request_button_' + cobrowse_io_details[index]["session_id"] + '">\
                                        ' + request_button + '\
                                      </td><td id = "meeting_button_' + cobrowse_io_details[index]["session_id"] + '">' + meeting_button + '</td>\
                                  </tr>\
                                </tbody>';
                            }
                        } else {
                            if (show_verification_code == false) {
                                session_details_table += '<tbody>\
                                  <tr>\
                                      <td>' + cobrowse_io_details[index]["datetime"] + '</td>\
                                      <td id = "active_inactive_' + cobrowse_io_details[index]["session_id"] + '">' + active_inactive + '</td>\
                                      <td id = "request_button_' + cobrowse_io_details[index]["session_id"] + '">\
                                        ' + request_button + '\
                                  </tr>\
                                </tbody>';
                            } else {
                                session_details_table += '<tbody>\
                                  <tr>\
                                      <td>' + cobrowse_io_details[index]["datetime"] + '</td>\
                                      <td id = "active_inactive_' + cobrowse_io_details[index]["session_id"] + '">' + active_inactive + '</td>\
                                      <td id = "otp_' + cobrowse_io_details[index]["session_id"] + '">' + cobrowse_io_details[index]["otp"] + '</td>\
                                      <td id = "request_button_' + cobrowse_io_details[index]["session_id"] + '">\
                                        ' + request_button + '\
                                  </tr>\
                                </tbody>';
                            }

                        }
                    }

                    session_details_table += '</table>';
                    session_details_table += search_message;
                    session_details_element.innerHTML = session_details_table;
                    document.getElementById("search_lead_button").setAttribute("disabled", "disabled");

                    if (sync_search_field_interval == null) {
                        sync_search_field_interval = setInterval(function(e) {
                            update_captured_lead();
                        }, 5000);
                    }
                }

                update_table_attribute();
            }
        }
    }
    xhttp.send(params);
}

function assign_lead_to_agent(session_id, share_client_session=null) {
    if (window.ALLOW_SCREEN_SHARING_COBROWSE == "True") {
        window.location = "/easy-assist/agent/screensharing-cobrowse/" + session_id;
    } else if (share_client_session == "true") {
        window.location = "/easy-assist/customer/" + session_id;
    } else {
        window.location = "/easy-assist/agent/" + session_id;
    }
    hide_transfer_cobrowsing_session_btn(session_id);
}

function request_for_cobrowsing(session_id) {
    let request_params = {
        "session_id": session_id
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/request-assist/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                if (document.getElementById("search_lead_modal").style.display == "block") {
                    update_captured_lead();
                } else if (document.getElementById("request_for_inbound_cobrowsing_modal").style.display == "block") {
                    update_inbound_cobrowsing(session_id);
                } else {
                    show_easyassist_toast("Request for cobrowsing has been sent to the customer");
                }
            }
        }
    }
    xhttp.send(params);
}

function request_for_meeting(session_id) {
    let request_params = {
        "session_id": session_id
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/request-assist-meeting/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                if (document.getElementById("search_lead_modal").style.display == "block") {
                    update_captured_lead();
                } else if (document.getElementById("request_for_inbound_cobrowsing_modal").style.display == "block") {
                    update_inbound_cobrowsing(session_id);
                }
            }
        }
    }
    xhttp.send(params);
}

$("#search_lead_modal").on("hidden.bs.modal", function() {
    // put your default event here
    let request_params = {};
    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/mark-inactive/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status != 200) {
                show_easyassist_toast("Unable to mark inactive");
            }
            window.location.reload();
        }
    }
    xhttp.send(params);
});

//////////////////////////////// In bound request modal updation  ////////////////////////////////

function update_inbound_cobrowsing(session_id) {

    let request_params = {
        "search_value": "None",
        "session_id_list": [session_id],
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/search-lead/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status == 200) {
                let cobrowse_io_details = response.cobrowse_io_details;
                let show_verification_code = response.show_verification_code;

                if (cobrowse_io_details.length == 0) {
                    return;
                }
                var search_message_cobrowsing = '';
                var search_message_meeting = '';

                for (let index = 0; index < cobrowse_io_details.length; index++) {

                    var active_inactive = '<span class="text-success">Active</span>';
                    if (cobrowse_io_details[index]["is_active"] == false) {
                        active_inactive = '<span class="text-danger">Inactive</span>';
                    }

                    var request_button = "";
                    var meeting_button = "";
                    var resend_meeting_request_button = "";
                    if (cobrowse_io_details[index]["is_active"] == true) {
                        if (cobrowse_io_details[index]["allow_agent_cobrowse"] == "true") {
                            // connect agent with client screen
                            request_button = '<button class="btn btn-success float-right" onclick="assign_lead_to_agent(\'' + cobrowse_io_details[index]['session_id'] + '\', \'' + cobrowse_io_details[index]['share_client_session'] + '\')">Connect</button>';
                            search_message_cobrowsing = '<p style="color:green;"><b>Request for cobrowsing has been accepted by the Customer</b></p>';
                        } else if (cobrowse_io_details[index]["allow_agent_cobrowse"] == "false") {
                            // requested for assistance but client doesn't allowed
                            request_button = '<button class="btn btn-primary float-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Cobrowsing</button>';
                            search_message_cobrowsing = '<p style="color:red;"><b>Request for assistance has been denied by the customer. Kindly make sure, you are connected with client on call.</b></p>';
                        } else {
                            if (cobrowse_io_details[index]["agent_assistant_request_status"] == true) {
                                // requested for assistance but state has not been changed
                                request_button = '<button class="btn btn-primary float-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Re-send Request</button>';
                                search_message_cobrowsing = '<p style="color:orange;"><b>Request for assistance has been sent to the customer.</b></p>';
                            } else {
                                request_button = '<button class="btn btn-primary float-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Cobrowsing</button>';
                            }
                        }

                        if (cobrowse_io_details[index]["allow_agent_meeting"] == "true") {
                            // connect agent with client screen
                            meeting_button += '<button class="btn btn-success float-right" onclick="connect_with_client(\'' + cobrowse_io_details[index]['session_id'] + '\')">Connect</button>';
                            resend_meeting_request_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Re-send Request</button>';
                            search_message_meeting = '<p style="color:green;"><b>Request for meeting has been accepted by the Customer</b></p>';
                        } else if (cobrowse_io_details[index]["allow_agent_meeting"] == "false") {
                            // requested for assistance but client doesn't allowed
                            meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                            search_message_meeting = '<p style="color:red;"><b>Request for meeting has been denied by the customer.</b></p>';
                        } else {
                            if (cobrowse_io_details[index]["agent_meeting_request_status"] == true) {
                                meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Re-send Request</button>';
                                search_message_meeting = '<p style="color:orange;"><b>Request for meeting has been sent to the customer.</b></p>';
                            } else {
                                meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                            }
                        }
                    }
                    document.getElementById("active_inactive_" + cobrowse_io_details[index]["session_id"]).innerHTML = active_inactive;
                    document.getElementById("request_button_" + cobrowse_io_details[index]["session_id"]).innerHTML = request_button;
                    document.getElementById("meeting_button_" + cobrowse_io_details[index]["session_id"]).innerHTML = meeting_button;
                    document.getElementById("resend_meeting_request_button_" + cobrowse_io_details[index]["session_id"]).innerHTML = resend_meeting_request_button;

                    if (resend_meeting_request_button.length == 0) {
                        document.getElementById("resend_meeting_request_button_" + cobrowse_io_details[index]["session_id"]).style.display = 'none';
                    } else {
                        document.getElementById("resend_meeting_request_button_" + cobrowse_io_details[index]["session_id"]).style.display = 'block';
                    }

                    if (show_verification_code) {
                        document.getElementById("otp_" + cobrowse_io_details[index]["session_id"]).innerHTML = cobrowse_io_details[index]["otp"]
                    }
                    let easyassist_table_cobrowsing = document.getElementById('cobrowsing-table');
                    let easyassist_table_meeting = document.getElementById('meeting-table');
                    easyassist_table_cobrowsing.nextElementSibling.innerHTML = search_message_cobrowsing;
                    easyassist_table_meeting.nextElementSibling.innerHTML = search_message_meeting;
                }
            }
        }
    }
    xhttp.send(params);
}

function remarks_validation(remarks, close_session_text_error_el, remarks_type, min_length, max_length) {
    if (min_length > 0) {
        if (!remarks) {
            close_session_text_error_el.innerHTML = remarks_type + " cannot be empty."
            close_session_text_error_el.style.display = 'block';
            return "invalid";
        }
    }
    if (remarks.length > max_length) {
        close_session_text_error_el.innerHTML = remarks_type + " cannot be more than 200 characters."
        close_session_text_error_el.style.display = 'block';
        return "invalid";
    }
    return "valid";
}

function close_easyassist_cobrowsing_session(element) {

    let close_session_remark_error_el = document.getElementById("close-session-remarks-error");
    let close_session_text_error_el = document.getElementById("close-session-text-error");
    let is_helpful = document.getElementById("mask-successfull-cobrowsing-session").checked;

    close_session_text_error_el.style.display = "none";
    if (close_session_remark_error_el) {
        close_session_remark_error_el.style.display = "none";
    }

    let comment_desc = "";
    let comments = "";
    let subcomments = "";

    if(ENABLE_PREDEFINED_REMARKS == "True") {
        comments = document.getElementById("close-session-remarks").value;
        comment_desc = document.getElementById("close-session-remarks-text").value.trim();

        if(ENABLE_PREDEFINED_SUBREMARKS == "True") {
            subcomments = document.getElementById("close-session-subremarks").value;
        }

        if(REMARKS_OPTIONAL == "False") {
            if (comments.length == 0) {
                close_session_remark_error_el.innerHTML = "Please select a remark";
                close_session_remark_error_el.style.display = 'block';
                return;
            }

            if (remarks_validation(comments, close_session_text_error_el, "Remarks", 1, 200) == "invalid") {
                return;
            }

            if(ENABLE_PREDEFINED_SUBREMARKS == "True") {
                if(remarks_validation(subcomments, close_session_text_error_el, "Sub-remarks", 1, 200) == "invalid") {
                    return;
                }
            }

            if(!comment_desc.length) {
                close_session_text_error_el.innerHTML = "Comments cannot be empty";
                close_session_text_error_el.style.display = 'block';
                return;
            }

        }

        if (comments == "others") {
            
            if(!comment_desc.length) {
                close_session_text_error_el.innerHTML = "Comments cannot be empty";
                close_session_text_error_el.style.display = 'block';
                return;
            }
    
            if(comment_desc && !is_input_text_valid(comment_desc)) {
                close_session_text_error_el.innerHTML = "Please enter a valid comment (Only a-z A-z 0-9 .,@ are allowed)";
                close_session_text_error_el.style.display = 'block';
                return;
            }

            if (remarks_validation(comment_desc, close_session_text_error_el, "Comments", 1, 200) == "invalid") {
                return
            }
        } else {
            
            if(comment_desc && !is_input_text_valid(comment_desc)) {
                close_session_text_error_el.innerHTML = "Please enter a valid comment (Only a-z A-z 0-9 .,@ are allowed)";
                close_session_text_error_el.style.display = 'block';
                return;
            }
            
            if (remarks_validation(comment_desc, close_session_text_error_el, "Comments", 0, 200) == "invalid") {
                return
            }
        }

        comments = remove_special_characters_from_str(comments);
        subcomments = remove_special_characters_from_str(subcomments);
        comment_desc = remove_special_characters_from_str(comment_desc);

    } else {
        // ENABLE_PREDEFINED_REMARKS_WITH_BUTTONS == "True" included
        comments = document.getElementById("close-session-remarks-text").value.trim();
        if(!comments.length) {
            close_session_text_error_el.innerHTML = "Remarks cannot be empty";
            close_session_text_error_el.style.display = 'block';
            return;
        }

        if(!is_input_text_valid(comments)) {
            close_session_text_error_el.innerHTML = "Please enter a valid remark (Only a-z A-z 0-9 .,@ are allowed)";
            close_session_text_error_el.style.display = 'block';
            return;
        }
        
        comments = remove_special_characters_from_str(comments);

        if (remarks_validation(comments, close_session_text_error_el, "Remarks", 1, 200) == "invalid") {
            return;
        }
    }

    element.innerHTML = "Closing...";
    let json_string = JSON.stringify({
        "id": close_session_id,
        "comments": comments,
        "subcomments": subcomments,
        "comment_desc": comment_desc,
        "is_agent_code_required": true,
        "is_helpful": is_helpful
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/close-session/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                update_active_lead_status();
                element.innerHTML = "End Session";
                $("#close_session_modal").modal("hide");
                let agent_code_text = `Your virtual agent code: ${response.agent_code}`;
                if(document.getElementsByClassName("virtual-agent-code")[0]) {
                    document.getElementsByClassName("virtual-agent-code")[0].innerHTML = agent_code_text;
                }
                if(document.getElementsByClassName("virtual-agent-code-ul")[0].children[0]) {
                    document.getElementsByClassName("virtual-agent-code-ul")[0].children[0].innerHTML = agent_code_text;
                }
            } else {
                element.innerHTML = "End Session";
                document.getElementById("close-session-text-error").innerHTML = "Unable to end Session. Please try again later";
                close_session_text_error_el.style.display = "block";
            }
        }
    }
    xhttp.send(params);
}

function archive_easyassist_cobrowsing_session(element) {

    let archive_lead_remark_error_el = document.getElementById("archive-lead-remarks-error");
    let archive_lead_text_error_el = document.getElementById("archive-lead-text-error");
    let close_session_text_error_el = document.getElementById("close-session-text-error");

    archive_lead_text_error_el.style.display = "none";
    if (archive_lead_remark_error_el) {
        archive_lead_remark_error_el.style.display = "none";
    }

    let comment_desc = ""
    let comments = "";
    let subcomments = "";

    if(ENABLE_PREDEFINED_REMARKS == "True") {
        comments = document.getElementById("archive-lead-remarks").value.trim();
        comment_desc = document.getElementById("archive-lead-remarks-text").value.trim();
        if(ENABLE_PREDEFINED_SUBREMARKS == "True") {
            subcomments = document.getElementById("archive-lead-subremarks").value.trim();
        }

        comments = remove_special_characters_from_str(comments);
        subcomments = remove_special_characters_from_str(subcomments);
        comment_desc = remove_special_characters_from_str(comment_desc);

        if(REMARKS_OPTIONAL == "False") {
            if (comments.length == 0) {
                archive_lead_remark_error_el.innerHTML = "Please select a remark";
                archive_lead_remark_error_el.style.display = 'block';
                return;
            }

            if (remarks_validation(comments, archive_lead_text_error_el, "Remarks", 1, 200) == "invalid") {
                return;
            }

            if(ENABLE_PREDEFINED_SUBREMARKS == "True") {
                if(remarks_validation(subcomments, archive_lead_text_error_el, "Sub-remarks", 1, 200) == "invalid") {
                    return;
                }
            }

            if(!comment_desc.length) {
                close_session_text_error_el.innerHTML = "Remarks cannot be empty";
                close_session_text_error_el.style.display = 'block';
                return;
            }
        }

        if (comments == "others") {
            
            if(!comment_desc.length) {
                archive_lead_text_error_el.innerHTML = "Comments cannot be empty";
                archive_lead_text_error_el.style.display = 'block';
                return;
            }
    
            if(!is_input_text_valid(comment_desc)) {
                archive_lead_text_error_el.innerHTML = "Please enter a valid comment (Only a-z A-z 0-9 .,@ are allowed)";
                archive_lead_text_error_el.style.display = 'block';
                return;
            }

            if (remarks_validation(comment_desc, archive_lead_text_error_el, "Comments", 0, 200) == "invalid") {
                return;
            }
        } else {
            
            if(comment_desc && !is_input_text_valid(comment_desc)) {
                close_session_text_error_el.innerHTML = "Please enter a valid comment (Only a-z A-z 0-9 .,@ are allowed)";
                close_session_text_error_el.style.display = 'block';
                return;
            }

            if (remarks_validation(comment_desc, close_session_text_error_el, "Comments", 0, 200) == "invalid") {
                return;
            }
        }
    } else {
        comments = document.getElementById("archive-lead-remarks-text").value.trim();
        
        if(!comments.length) {
            archive_lead_text_error_el.innerHTML = "Remarks cannot be empty";
            archive_lead_text_error_el.style.display = 'block';
            return;
        }

        if(!is_input_text_valid(comments)) {
            archive_lead_text_error_el.innerHTML = "Please enter a valid remark (Only a-z A-z 0-9 .,@ are allowed)";
            archive_lead_text_error_el.style.display = 'block';
            return;
        }
        
        comments = remove_special_characters_from_str(comments);

        if (remarks_validation(comments, archive_lead_text_error_el, "Remarks", 1, 200) == "invalid") {
            return;
        }
    }

    element.innerHTML = "Archiving..";
    let json_string = JSON.stringify({
        "id": archive_session_id,
        "comments": comments,
        "comment_desc": comment_desc,
        "subcomments": subcomments,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/close-session/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                window.location = "/easy-assist/sales-ai/dashboard/";
            } else {
                element.innerHTML = "Archive";
                archive_lead_remark_error_el.innerHTML = "Unable to end Session. Please try again later";
                archive_lead_remark_error_el.style.display = "block";
            }
        }
    }
    xhttp.send(params);
}

function call_convert_lead_manually_api() {
    
    let manual_conversion_remark_error_el = document.getElementById("manual-conversion-remarks-error");
    let manual_conversion_text_error_el = document.getElementById("manual-conversion-text-error");

    manual_conversion_text_error_el.style.display = "none";
    manual_conversion_text_error_el.style.color = "red";
    if (manual_conversion_remark_error_el) {
        manual_conversion_remark_error_el.style.display = "none";
        manual_conversion_remark_error_el.style.color = "red";
    }

    let comments = "";
    let subcomments = "";
    let comment_desc = ""

    if(window.ENABLE_PREDEFINED_REMARKS == "True") {
        comments = document.getElementById("manual-conversion-remarks").value.tirm();
        comment_desc = document.getElementById("manual-conversion-remarks-text").value.trim();
        if(window.ENABLE_PREDEFINED_SUB_REMARKS == "True") {
            subcomments = document.getElementById("manual-conversion-subremarks").value.trim();
        }

        comments = remove_special_characters_from_str(comments);
        subcomments = remove_special_characters_from_str(subcomments);
        comment_desc = remove_special_characters_from_str(comment_desc);

        if(window.REMARKS_OPTIONAL == "False") {
            if (comments.length == 0) {
                manual_conversion_remark_error_el.innerHTML = "Please select a remark";
                manual_conversion_remark_error_el.style.display = 'block';
                return;
            }

            if (remarks_validation(comments, manual_conversion_text_error_el, "Remarks", 1, 200) == "invalid") {
                return;
            }
            
            if(window.ENABLE_PREDEFINED_SUB_REMARKS == "True") {
                if(remarks_validation(subcomments, manual_conversion_text_error_el, "Sub-remarks", 1, 200) == "invalid") {
                    return;
                }
            }

            if(!comment_desc.length) {
                manual_conversion_remark_error_el.innerHTML = "Comments cannot be empty";
                manual_conversion_remark_error_el.style.display = 'block';
                return;
            }
        }

        if (comments == "others") {
            
            if(!comment_desc.length) {
                manual_conversion_remark_error_el.innerHTML = "Comments cannot be empty";
                manual_conversion_remark_error_el.style.display = 'block';
                return;
            }

            if(!is_input_text_valid(comment_desc)) {
                manual_conversion_remark_error_el.innerHTML = "Please enter a valid comment (Only a-z A-z 0-9 .,!@ are allowed)";
                manual_conversion_remark_error_el.style.display = 'block';
                return;
            }

            if (remarks_validation(comment_desc, manual_conversion_text_error_el, "Comments", 1, 200) == "invalid") {
                return;
            }
        } else {

            if(comment_desc && !is_input_text_valid(comment_desc)) {
                manual_conversion_remark_error_el.innerHTML = "Please enter a valid comment (Only a-z A-z 0-9 .,!@ are allowed)";
                manual_conversion_remark_error_el.style.display = 'block';
                return;
            }

            if (remarks_validation(comment_desc, manual_conversion_text_error_el, "Comments", 0, 200) == "invalid") {
                return;
            }
        }
    } else {
        comments = document.getElementById("manual-conversion-remarks-text").value.trim();
        
        if(!comments.length) {
            manual_conversion_remark_error_el.innerHTML = "Remarks cannot be empty";
            manual_conversion_remark_error_el.style.display = 'block';
            return;
        }

        if(!is_input_text_valid(comments)) {
            manual_conversion_remark_error_el.innerHTML = "Please enter a valid remark (Only a-z A-z 0-9 .,!@ are allowed)";
            manual_conversion_remark_error_el.style.display = 'block';
            return;
        }

        comments = remove_special_characters_from_str(comments);

        if (remarks_validation(comments, manual_conversion_text_error_el, "Remarks", 1, 200) == "invalid") {
            return;
        }
    }

    let is_helpful = document.getElementById("mask-successfull-cobrowsing-session").checked;

    let json_string = JSON.stringify({
        "id": window.CONVERT_LEAD_SESSION_ID,
        "comments": comments,
        "subcomments": subcomments,
        "comment_desc": comment_desc,
        "is_helpful": is_helpful,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const encrypted_params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/manually-convert-lead/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_lead_manually_converted_toast();
                setTimeout(() => {
                    window.location.reload();
                }, 650);
            } else if (response.status == 300) {
                show_easyassist_toast(response.message);
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                show_easyassist_toast("Lead could not be converted manually");
                $("#convert-lead-manually-modal").modal("hide");
            }        
        }
    }
    xhttp.send(encrypted_params);
}

function check_is_lead_manually_converted(session_id) {

    window.CONVERT_LEAD_SESSION_ID = session_id;
    
    let json_string = JSON.stringify({
        "id": session_id,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const encrypted_params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/check-lead-manually-converted/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                if(response.is_lead_manually_converted) {
                    show_easyassist_toast(response.lead_converted_by_agent + " has already converted the lead manually");
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    show_manual_lead_conversion_modal();
                }
            }
        }
    }
    xhttp.send(encrypted_params);
}

function show_lead_manually_converted_toast() {
    document.getElementById("lead-converted-manually-toast").style.display = "flex";
}

function connect_with_client(session_id) {
    if (session_id == null || session_id == undefined) {

        return;
    }
    window.open("/easy-assist/meeting/" + session_id + "?is_meeting_cobrowsing=true", "_blank");
    hide_transfer_cobrowsing_session_btn(session_id);
}

function hide_transfer_cobrowsing_session_btn(session_id) {
    try {
        document.getElementById("transfer-session-btn-" + session_id).style.display = 'none';
    } catch (err) {}
}

function request_for_inbound_cobrowsing(session_id) {
    global_session_id = session_id;

    let cobrowsing_tab = document.getElementById("cobrowsing-tab");
    let meeting_tab = document.getElementById("meeting-tab");
    cobrowsing_tab.innerHTML = "";
    meeting_tab.innerHTML = "";

    let request_params = {
        "search_value": "None",
        "session_id_list": [session_id],
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/search-lead/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                let cobrowse_io_details = response.cobrowse_io_details;
                let show_verification_code = response.show_verification_code;
                let allow_cobrowsing_meeting = response.allow_cobrowsing_meeting;
                let allow_video_meeting_only = response.allow_video_meeting_only;
                if (cobrowse_io_details.length == 0) {
                    meeting_tab.innerHTML = "No active customer with that details found. Please wait for some time, or ask the customer to refresh the page and then try again.";
                    cobrowsing_tab.innerHTML = "No active customer with that details found. Please wait for some time, or ask the customer to refresh the page and then try again.";
                } else {
                    var meeting_table_details = '<div class="modal-body" style="margin: 0px 14px !important">\
                                                    <div class="row">';
                    var cobrowsing_table_details = '<div class="modal-body" style="margin: 0px 14px !important">\
                                                        <div class="row">';
                    if (show_verification_code == false) {
                        meeting_table_details += '<p>Session Details</p>\
                                <table class="table easy-assist-table" id="meeting-table">\
                                    <thead>\
                                        <tr>\
                                            <th>Date</th>\
                                            <th>Time</th>\
                                            <th>Status</th>\
                                        </tr>\
                                    </thead>';
                        cobrowsing_table_details += '<p>Session Details</p>\
                                                    <table class="table easy-assist-table" id="cobrowsing-table">\
                                                    <thead>\
                                                        <tr>\
                                                        <th>Date</th>\
                                                        <th>Time</th>\
                                                        <th>Status</th>\
                                                        </tr>\
                                                    </thead>';
                    } else {
                        meeting_table_details += '<p>Session Details</p>\
                                <table class="table easy-assist-table" id="meeting-table">\
                                    <thead>\
                                        <tr>\
                                            <th>Date</th>\
                                            <th>Time</th>\
                                            <th>Status</th>\
                                        </tr>\
                                    </thead>';
                        cobrowsing_table_details += '<p>Session Details</p>\
                                                        <table class="table easy-assist-table" id="cobrowsing-table">\
                                                        <thead>\
                                                            <tr>\
                                                                <th>Date</th>\
                                                                <th>Time</th>\
                                                                <th>Status</th>\
                                                                <th>Code</th>\
                                                            </tr>\
                                                        </thead>';
                    }

                    var search_message_cobrowsing = '<p></p>';
                    var search_message_meeting = '<p></p>';

                    for (let index = 0; index < cobrowse_io_details.length; index++) {

                        var active_inactive = '<span class="text-success">Active</span>';
                        if (cobrowse_io_details[index]["is_active"] == false) {
                            active_inactive = '<span class="text-danger">Inactive</span>';
                        }

                        var request_button = "";
                        var meeting_button = "";
                        var resend_meeting_request_button = "";
                        if (cobrowse_io_details[index]["is_active"] == true) {
                            if (cobrowse_io_details[index]["allow_agent_cobrowse"] == "true") {
                                // connect agent with client screen
                                request_button = '<button class="btn btn-success float-right" onclick="assign_lead_to_agent(\'' + cobrowse_io_details[index]['session_id'] + '\', \'' + cobrowse_io_details[index]['share_client_session'] + '\')">Connect</button>';
                                search_message_cobrowsing = '<p style="color:green;"><b>Request for assistance has been accepted by the Customer</b></p>';
                            } else if (cobrowse_io_details[index]["allow_agent_cobrowse"] == "false") {
                                // requested for assistance but client doesn't allowed
                                request_button = '<button class="btn btn-primary float-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Cobrowsing</button>';
                                search_message_cobrowsing = '<p style="color:red;"><b>Request for assistance has been denied by the customer. Kindly make sure, you are connected with client on call.</b></p>';
                            } else {
                                if (cobrowse_io_details[index]["agent_assistant_request_status"] == true) {
                                    // requested for assistance but state has not been changed
                                    request_button = '<button class="btn btn-primary float-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Re-send Request</button>';
                                    search_message_cobrowsing = '<p style="color:orange;"><b>Request for assistance has been sent to the customer.</b></p>';
                                } else {
                                    request_button = '<button class="btn btn-primary float-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Cobrowsing</button>';
                                }
                            }

                            if (cobrowse_io_details[index]["allow_agent_meeting"] == "true") {
                                // connect agent with client screen
                                meeting_button += '<button class="btn btn-success float-right" onclick="connect_with_client(\'' + cobrowse_io_details[index]['session_id'] + '\')">Connect</button>';
                                resend_meeting_request_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Re-send Request</button>';
                                search_message_meeting = '<p style="color:green;"><b>Request for meeting has been accepted by the Customer</b></p>';
                            } else if (cobrowse_io_details[index]["allow_agent_meeting"] == "false") {
                                // requested for assistance but client doesn't allowed
                                meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                                search_message_meeting = '<p style="color:red;"><b>Request for meeting has been denied by the customer.</b></p>';
                            } else {
                                if (cobrowse_io_details[index]["agent_meeting_request_status"] == true) {
                                    meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Re-send Request</button>';
                                    search_message_meeting = '<p style="color:orange;"><b>Request for meeting has been sent to the customer.</b></p>';
                                } else {
                                    meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                                }
                            }
                        }

                        if (show_verification_code == false) {
                            cobrowsing_table_details += '<tbody>\
                                                            <tr>\
                                                                <td>' + cobrowse_io_details[index]["datetime"].split(' ').slice(0, 3).join(' ') + '</td>\
                                                                <td>' + cobrowse_io_details[index]["datetime"].split(' ').slice(3).join(' ') + '</td>\
                                                                <td id="active_inactive_' + cobrowse_io_details[index]['session_id'] + '">' + active_inactive + '</td>\
                                                            </tr>\
                                                        </tbody>';
                            meeting_table_details += '<tbody>\
                                                        <tr>\
                                                            <td>' + cobrowse_io_details[index]["datetime"].split(' ').slice(0, 3).join(' ') + '</td>\
                                                            <td>' + cobrowse_io_details[index]["datetime"].split(' ').slice(3).join(' ') + '</td>\
                                                            <td id="active_inactive_' + cobrowse_io_details[index]['session_id'] + '">' + active_inactive + '</td>\
                                                        </tr>\
                                                    </tbody>';
                        } else {
                            cobrowsing_table_details += '<tbody>\
                                                            <tr>\
                                                                <td>' + cobrowse_io_details[index]["datetime"].split(' ').slice(0, 3).join(' ') + '</td>\
                                                                <td>' + cobrowse_io_details[index]["datetime"].split(' ').slice(3).join(' ') + '</td>\
                                                                <td id="active_inactive_' + cobrowse_io_details[index]['session_id'] + '">' + active_inactive + '</td>\
                                                                <td id="otp_' + cobrowse_io_details[index]['session_id'] + '">' + cobrowse_io_details[index]["otp"] + '</td>\
                                                            </tr>\
                                                        </tbody>';
                            meeting_table_details += '<tbody>\
                                                        <tr>\
                                                            <td>' + cobrowse_io_details[index]["datetime"].split(' ').slice(0, 3).join(' ') + '</td>\
                                                            <td>' + cobrowse_io_details[index]["datetime"].split(' ').slice(3).join(' ') + '</td>\
                                                            <td id="active_inactive_' + cobrowse_io_details[index]['session_id'] + '">' + active_inactive + '</td>\
                                                        </tr>\
                                                    </tbody>';
                        }

                        cobrowsing_table_details += '</table><div>' + search_message_cobrowsing + '</div></div></div>';
                        meeting_table_details += '</table><div>' + search_message_meeting + '</div></div></div>';

                        cobrowsing_table_details += '<div class="modal-footer">\
                                                        <button class="btn btn-secondary" type="button" data-dismiss="modal" id="end_session_cancel_btn">Cancel</button>';
                        cobrowsing_table_details += '<div id="request_button_' + cobrowse_io_details[index]['session_id'] + '" class="div-width-100">' + request_button;
                        cobrowsing_table_details += '</div></div>'
                        meeting_table_details += '<div class="modal-footer">\
                                                        <button class="btn btn-secondary" type="button" data-dismiss="modal" id="end_session_cancel_btn">Cancel</button>';
                        meeting_table_details += '<div id="resend_meeting_request_button_' + cobrowse_io_details[index]['session_id'] + '"  class="div-width-100">' + resend_meeting_request_button + '</div>';
                        meeting_table_details += '<div id="meeting_button_' + cobrowse_io_details[index]['session_id'] + '" class="div-width-100">' + meeting_button;
                        meeting_table_details += '</div>'

                        cobrowsing_tab.innerHTML = cobrowsing_table_details;
                        meeting_tab.innerHTML = meeting_table_details;

                        if (resend_meeting_request_button.length == 0) {
                            document.getElementById("resend_meeting_request_button_" + cobrowse_io_details[index]["session_id"]).style.display = 'none';
                        } else {
                            document.getElementById("resend_meeting_request_button_" + cobrowse_io_details[index]["session_id"]).style.display = 'block';
                        }

                        if (allow_video_meeting_only) {
                            document.getElementById("cobrowsing-request-tab-button").style.display = "none";

                            var meeting_request_tab_btn = document.getElementById("meeting-request-tab-button");
                            meeting_request_tab_btn.click();
                            meeting_request_tab_btn.classList.remove("btn");
                            meeting_request_tab_btn.classList.remove("btn-primary");
                            meeting_request_tab_btn.classList.add("toggle-header");
                            meeting_request_tab_btn.disabled = true;

                        } else if (allow_cobrowsing_meeting == false) {
                            document.getElementById("meeting-request-tab-button").style.display = "none";
                            var cobrowsing_request_tab_btn = document.getElementById("cobrowsing-request-tab-button");
                            cobrowsing_request_tab_btn.classList.remove("btn");
                            cobrowsing_request_tab_btn.classList.remove("btn-primary");
                            cobrowsing_request_tab_btn.classList.add("toggle-header");
                            cobrowsing_request_tab_btn.disabled = true;
                        }
                    }

                    if (sync_search_field_interval == null) {
                        sync_search_field_interval = setInterval(function(e) {
                            update_inbound_cobrowsing(session_id);
                        }, 5000);
                    }
                }

                update_table_attribute();
                $("#request_for_inbound_cobrowsing_modal").modal("show");
            }
        }
    }
    xhttp.send(params);
}

$("#request_for_inbound_cobrowsing_modal").on("hidden.bs.modal", function() {
    if (sync_search_field_interval != null) {
        clearInterval(sync_search_field_interval);
        sync_search_field_interval = null;
    }
});


function save_agent_session_remarks(session_id) {
    if (document.getElementById("agent-session-remarks") == null) return;
    var agent_session_remarks = document.getElementById("agent-session-remarks").value;
    if (agent_session_remarks.trim() == "") {
        show_easyassist_toast("Please enter some remarks before saving.");
        return;
    }
    agent_remarks = agent_session_remarks;
    let request_params = {
        "session_id": session_id,
        "agent_comments": agent_session_remarks
    };
    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/save-agent-comments/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status != 200) {
                show_easyassist_toast("Unable to save agent comments");
            } else {
                show_easyassist_toast("Remarks saved");
            }
        }
    }
    xhttp.send(params);
}

function activate_user(element, is_agent=false) {
    let user_checkbox_collection = document.getElementsByClassName("supervisor-checkbox-collection");
    if(is_agent) {
        user_checkbox_collection = document.getElementsByClassName("user-checkbox-collection");
    }
    
    let agent_id_list = [];

    for (let index = 0; index < user_checkbox_collection.length; index++) {
        if (user_checkbox_collection[index].checked) {
            agent_id_list.push(user_checkbox_collection[index].id.split("-")[2]);
        }
    }

    if (agent_id_list.length == 0) {
        return;
    }

    let request_params = {
        "agent_id_list": agent_id_list,
        "activate": true
    };
    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/change-agent-activate-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status != 200) {
                show_easyassist_toast("Unable to change agent activate status");
            }
            window.location.reload();
        }
    }
    xhttp.send(params);
}

var load_more_captured_screenshot = false;
var cobrowse_session_captured_screenshot_page = 1;

function show_captured_screenshot_details(session_id) {

    $("#see_agent_comments").modal('hide');

    var screenshot_modal = document.getElementById("see_captured_screenshot");

    if (load_more_captured_screenshot == false) {
        cobrowse_session_captured_screenshot_page = 1;
        document.getElementById("tbody-captured-screenshot-details").innerHTML = "Loading...";
    }

    let json_string = JSON.stringify({
        "id": session_id,
        "page": cobrowse_session_captured_screenshot_page
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/get-meta-information/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {

                if (response.meta_information_list.length == 0) {
                    document.getElementById("tbody-captured-screenshot-details").innerHTML = "No captured screenshot";
                    return;
                }

                var tbody_html = '';
                let meta_information_list = response.meta_information_list;
                for (let index = 0; index < meta_information_list.length; index++) {
                    let meta_id = meta_information_list[index]["id"];
                    tbody_html += [
                        '<tr>',
                            '<td>',
                                '<a href="/easy-assist/download-file/' + meta_id + '" download style="text-transform: capitalize">' + meta_information_list[index]["type"] + '</a>',
                            '</td>',
                            '<td>' + meta_information_list[index]["datetime"] + '</td>',
                            '<td>',
                                '<a href="/easy-assist/download-file/' + meta_id + '" download title="Export As Image"><i class="fas fa-fw fa-file-download"></i></a>',
                            '</td>',
                        '</tr>'
                    ].join('');
                }

                if (response.is_last_page == false) {
                    var load_more_btn_container = screenshot_modal.getElementsByClassName('load_more_btn_container')[0];
                    load_more_btn_container.style.display = "block";
                    var load_more_btn = load_more_btn_container.children[0];
                    load_more_btn.setAttribute('onclick', 'load_more_captured_screenshot_details(this, \'' + session_id + '\')');
                }

                if (cobrowse_session_captured_screenshot_page == 1) {
                    document.getElementById("tbody-captured-screenshot-details").innerHTML = tbody_html;
                    if (load_more_btn && load_more_btn.parentElement) {
                        load_more_btn.parentElement.classList.remove("mt-4");
                    }
                } else {
                    document.getElementById("tbody-captured-screenshot-details").innerHTML += tbody_html;
                    if (load_more_btn && load_more_btn.parentElement) {
                        load_more_btn.parentElement.classList.add("mt-4");
                    }
                }
                update_table_attribute();
            } else {
                show_easyassist_toast("Unable to load the details. Kindly try again.");
            }
            load_more_captured_screenshot = false;
        }
    }
    xhttp.send(params);
}

function load_more_captured_screenshot_details(element, session_id) {
    element.parentElement.style.display = "none";
    cobrowse_session_captured_screenshot_page += 1;
    load_more_captured_screenshot = true;
    show_captured_screenshot_details(session_id);
}


var load_more_agent_comments = false;
var cobrowse_session_agent_comments_page = 1;

function show_agents_comment_for_session(session_id) {

    $("#see_captured_screenshot").modal('hide');

    var agent_comments_modal = document.getElementById("see_agent_comments");

    if (load_more_agent_comments == false) {
        cobrowse_session_agent_comments_page = 1;
        document.getElementById("tbody-agent-comments-details").innerHTML = "Loading...";
    }

    let json_string = JSON.stringify({
        "id": session_id,
        "page": cobrowse_session_agent_comments_page
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/get-cobrowse-agent-comments/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {

                if (response.agent_comments_list.length == 0) {
                    document.getElementById("agent-comments-table").style.display = "none";
                    document.getElementById("no-comments-empty-message").style.display = "block";
                    return;
                } else {
                    document.getElementById("agent-comments-table").style = "max-height: 305px;";
                    document.getElementById("no-comments-empty-message").style.display = "none";
                }

                let enable_predefined_remarks = response["enable_predefined_remarks"]
                var tbody_html = '';
                let agent_comments_list = response.agent_comments_list;
                for (let index = 0; index < agent_comments_list.length; index++) {

                    if (enable_predefined_remarks == false) {
                        tbody_html += '<tr><td>' + agent_comments_list[index]["agent"] + '</td>\
                        <td>' + agent_comments_list[index]["datetime"] + '</td>\
                        <td>' + agent_comments_list[index]["comments"] + '</td>\
                        </tr>';
                    } else {
                        tbody_html += '<tr><td>' + agent_comments_list[index]["agent"] + '</td>\
                        <td>' + agent_comments_list[index]["datetime"] + '</td>\
                        <td>' + agent_comments_list[index]["comments"] + '</td>'
                        if(response.enable_predefined_subremarks == true) {
                            tbody_html += '<td>' + agent_comments_list[index]["subcomments"] + '</td>'
                        }
                        tbody_html += '<td>' + agent_comments_list[index]["comment_desc"] + '</td>\
                        </tr>';
                        
                    }
                }

                if (response.is_last_page == false) {
                    var load_more_btn_container = agent_comments_modal.getElementsByClassName('load_more_btn_container')[0];
                    load_more_btn_container.style.display = "block";
                    var load_more_btn = load_more_btn_container.children[0];
                    load_more_btn.setAttribute('onclick', 'load_more_agent_comments_details(this, \'' + session_id + '\')');
                }

                if (cobrowse_session_agent_comments_page == 1) {
                    document.getElementById("tbody-agent-comments-details").innerHTML = tbody_html;
                    if (load_more_btn && load_more_btn.parentElement) {
                        load_more_btn.parentElement.classList.remove("mt-4");
                    }
                } else {
                    document.getElementById("tbody-agent-comments-details").innerHTML += tbody_html;
                    if (load_more_btn && load_more_btn.parentElement) {
                        load_more_btn.parentElement.classList.add("mt-4");
                    }
                }
                update_table_attribute();
            } else {
                show_easyassist_toast("Unable to load the details. Kindly try again.");
            }
            load_more_agent_comments = false;
        }
    }
    xhttp.send(params);
}

function load_more_agent_comments_details(element, session_id) {
    element.parentElement.style.display = "none";
    cobrowse_session_agent_comments_page += 1;
    load_more_agent_comments = true;
    show_agents_comment_for_session(session_id);
}


var load_more_system_audit_trail = false;
var system_audit_trail_page = 1;

function show_system_audit_trail_details(session_id) {

    var audit_trail_modal = document.getElementById("see_system_audit_trail_modal_id");

    if (load_more_system_audit_trail == false) {
        system_audit_trail_page = 1;
        document.getElementById("tbody_see_system_audit_trail").innerHTML = "Loading...";
    }

    let json_string = JSON.stringify({
        "id": session_id,
        "page": system_audit_trail_page
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/get-system-audit-trail-basic-activity/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {

                if (response.basic_activity_audit_trail_obj_list.length == 0) {
                    document.getElementById("tbody_see_system_audit_trail").innerHTML = "Audit trail not available";
                    return;
                }

                var tbody_html = '';
                let basic_activity_audit_trail_obj_list = response.basic_activity_audit_trail_obj_list;
                for (let index = 0; index < basic_activity_audit_trail_obj_list.length; index++) {
                    tbody_html += '<tr><td>' + basic_activity_audit_trail_obj_list[index]["datetime"] + '</td>\
                    <td>' + basic_activity_audit_trail_obj_list[index]["description"] + '</td>\
                    </tr>';
                }

                if (response.is_last_page == false) {
                    var load_more_btn_container = audit_trail_modal.getElementsByClassName('load_more_btn_container')[0];
                    load_more_btn_container.style.display = "block";
                    var load_more_btn = load_more_btn_container.children[0];
                    load_more_btn.setAttribute('onclick', 'load_more_system_audit_trail_details(this, \'' + session_id + '\')');
                }

                if (system_audit_trail_page == 1) {
                    document.getElementById("tbody_see_system_audit_trail").innerHTML = tbody_html;
                    if (load_more_btn && load_more_btn.parentElement) {
                        load_more_btn.parentElement.classList.remove("mt-4");
                    }
                } else {
                    document.getElementById("tbody_see_system_audit_trail").innerHTML += tbody_html;
                    if (load_more_btn && load_more_btn.parentElement) {
                        load_more_btn.parentElement.classList.add("mt-4");
                    }
                }
                update_table_attribute();
            } else {
                show_easyassist_toast("Unable to load the details. Kindly try again.");
            }
            load_more_system_audit_trail = false;
        }
    }
    xhttp.send(params);
}

function load_more_system_audit_trail_details(element, session_id) {
    element.parentElement.style.display = "none";
    system_audit_trail_page += 1;
    load_more_system_audit_trail = true;
    show_system_audit_trail_details(session_id);
}

function check_and_mark_agent_as_admin(element) {

    let request_params = {
        "active_status": element.checked
    };
    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/switch-agent-mode/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status != 200) {
                show_easyassist_toast("Unable to update the active status");
            } else {
                window.location = "/easy-assist/sales-ai/dashboard/";
            }
        }
    }
    xhttp.send(params);
}

function check_attachment_image_file(file_extension) {
    var image_files = ["png", "jpg", "jpeg"];

    if (image_files.includes(file_extension)) {
        return true;
    }
    return false;
}

function get_cobrowsing_attachment_html(sender, sender_name, file_src, file_name, time, message, session_id,display_agent_profile, agent_profile_pic_source) {
    var extension = file_name.split(".")[1];
    var html = "";
    let profile = ""
    if(display_agent_profile && agent_profile_pic_source != "" && agent_profile_pic_source != undefined){
        let src = "/" + agent_profile_pic_source;
        profile = [
            '<img src = "'+ src + '" width="9" height="12"/>'
            ]
    } else {
        profile = ['<svg width="9" height="12" viewBox="0 0 9 12" fill="none" xmlns="http://www.w3.org/2000/svg">',
                    '<path d="M4.50001 0.571426C3.17682 0.571426 2.10417 1.79731 2.10417 3.30952C2.10417 4.82173 3.17682 6.04762 4.50001 6.04762C5.82319 6.04762 6.89584 4.82173 6.89584 3.30952C6.89584 1.79731 5.82319 0.571426 4.50001 0.571426Z" fill="white"/>',
                    '<path d="M1.68487 7.14285C1.12266 7.14285 0.666677 7.66344 0.666672 8.30624L0.666672 8.5119C0.666672 9.54021 1.13186 10.31 1.84546 10.8065C2.54718 11.2947 3.49042 11.5238 4.50001 11.5238C5.50959 11.5238 6.45283 11.2947 7.15455 10.8065C7.86815 10.31 8.33334 9.54021 8.33334 8.5119L8.33334 8.3062C8.33333 7.66341 7.87735 7.14285 7.31516 7.14285H1.68487Z" fill="white"/>',
                    '</svg>'].join();
    }
    if (check_attachment_image_file(extension)) {
        if (sender == "client") {
            html = [
                '<div class="chat-client-attachment-wrapper">',
                '<div style="display: flex; flex-direction: row;">',
                '<div class="chat-client-image">',
                '<svg width="9" height="12" viewBox="0 0 9 12" fill="none" xmlns="http://www.w3.org/2000/svg">',
                '<path d="M4.50001 0.571426C3.17682 0.571426 2.10417 1.79731 2.10417 3.30952C2.10417 4.82173 3.17682 6.04762 4.50001 6.04762C5.82319 6.04762 6.89584 4.82173 6.89584 3.30952C6.89584 1.79731 5.82319 0.571426 4.50001 0.571426Z" fill="white"/>',
                '<path d="M1.68487 7.14285C1.12266 7.14285 0.666677 7.66344 0.666672 8.30624L0.666672 8.5119C0.666672 9.54021 1.13186 10.31 1.84546 10.8065C2.54718 11.2947 3.49042 11.5238 4.50001 11.5238C5.50959 11.5238 6.45283 11.2947 7.15455 10.8065C7.86815 10.31 8.33334 9.54021 8.33334 8.5119L8.33334 8.3062C8.33333 7.66341 7.87735 7.14285 7.31516 7.14285H1.68487Z" fill="white"/>',
                '</svg>',
                '</div>',
                '<div class="live-chat-agent-message-bubble-image-attachment">',
                '<div class="slideshow-container" value="1">',
                '<div class="client-name-div">' + sender_name + '</div>',
                '<div class="mySlides livechat-slider-card">',
                '<img src="' + file_src + '?session_id=' + session_id + '">',
                '<div style="text-align: left; position: relative;">',
                '<h5 style="overflow-wrap: break-word; ">' + file_name + '</h5>',
                '<a href="' + file_src + '?session_id=' + session_id + '" style="position: absolute; top: 6px; right: 8px; cursor: pointer;" download>',
                '<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">',
                '<path d="M11.875 11.25H3.125C2.77982 11.25 2.5 11.5298 2.5 11.875C2.5 12.2202 2.77982 12.5 3.125 12.5H11.875C12.2202 12.5 12.5 12.2202 12.5 11.875C12.5 11.5298 12.2202 11.25 11.875 11.25Z" fill="#757575">', '</path>',
                '<path d="M2.5 10.625V11.875C2.5 12.2202 2.77982 12.5 3.125 12.5C3.47018 12.5 3.75 12.2202 3.75 11.875V10.625C3.75 10.2798 3.47018 10 3.125 10C2.77982 10 2.5 10.2798 2.5 10.625Z" fill="#757575">', '</path>',
                '<path d="M11.25 10.625V11.875C11.25 12.2202 11.5298 12.5 11.875 12.5C12.2202 12.5 12.5 12.2202 12.5 11.875V10.625C12.5 10.2798 12.2202 10 11.875 10C11.5298 10 11.25 10.2798 11.25 10.625Z" fill="#757575">', '</path>',
                '<path d="M7.50003 9.375C7.37046 9.37599 7.24378 9.33667 7.13753 9.2625L4.63753 7.5C4.50279 7.40442 4.41137 7.25937 4.38326 7.09658C4.35515 6.93379 4.39264 6.76649 4.48753 6.63125C4.5349 6.56366 4.59518 6.50611 4.66491 6.46194C4.73463 6.41777 4.81242 6.38785 4.89377 6.37391C4.97512 6.35996 5.05843 6.36227 5.13889 6.38069C5.21934 6.39911 5.29535 6.43329 5.36253 6.48125L7.50003 7.975L9.62503 6.375C9.75764 6.27555 9.92432 6.23284 10.0884 6.25628C10.2525 6.27973 10.4006 6.36739 10.5 6.5C10.5995 6.63261 10.6422 6.7993 10.6187 6.96339C10.5953 7.12749 10.5076 7.27555 10.375 7.375L7.87503 9.25C7.76685 9.33114 7.63526 9.375 7.50003 9.375Z" fill="#757575">', '</path>',
                '<path d="M7.5 8.125C7.33424 8.125 7.17527 8.05915 7.05806 7.94194C6.94085 7.82473 6.875 7.66576 6.875 7.5V2.5C6.875 2.33424 6.94085 2.17527 7.05806 2.05806C7.17527 1.94085 7.33424 1.875 7.5 1.875C7.66576 1.875 7.82473 1.94085 7.94194 2.05806C8.05915 2.17527 8.125 2.33424 8.125 2.5V7.5C8.125 7.66576 8.05915 7.82473 7.94194 7.94194C7.82473 8.05915 7.66576 8.125 7.5 8.125Z" fill="#757575">', '</path>',
                '</svg>',
                '</a>',
                // '<p style="overflow-wrap: break-word;">' + message + '</p>',
                '</div>',
                '</div>',
                '</div>',
                '</div>',
                '</div>',
                '<span class="message-time-bot">' + time + '</span>',
                '</div>',
            ].join('');
        } else {
            html = [
                '<div class="chat-agent-attachment-wrapper">',
                '<div style="display: flex; flex-direction: row; justify-content: flex-end">',
                '<div class="live-chat-agent-message-bubble-image-attachment">',
                '<div class="slideshow-container" value="1">',
                '<div class="agent-name-div">' + sender_name + '</div>',
                '<div class="mySlides livechat-slider-card">',
                '<img src="' + file_src + '?session_id=' + session_id + '">',
                '<div style="text-align: left; position: relative;">',
                '<h5 style="overflow-wrap: break-word; ">' + file_name + '</h5>',
                '<a href="' + file_src + '?session_id=' + session_id + '" style="position: absolute; top: 6px; right: 8px; cursor: pointer;" download>',
                '<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">',
                '<path d="M11.875 11.25H3.125C2.77982 11.25 2.5 11.5298 2.5 11.875C2.5 12.2202 2.77982 12.5 3.125 12.5H11.875C12.2202 12.5 12.5 12.2202 12.5 11.875C12.5 11.5298 12.2202 11.25 11.875 11.25Z" fill="#757575">', '</path>',
                '<path d="M2.5 10.625V11.875C2.5 12.2202 2.77982 12.5 3.125 12.5C3.47018 12.5 3.75 12.2202 3.75 11.875V10.625C3.75 10.2798 3.47018 10 3.125 10C2.77982 10 2.5 10.2798 2.5 10.625Z" fill="#757575">', '</path>',
                '<path d="M11.25 10.625V11.875C11.25 12.2202 11.5298 12.5 11.875 12.5C12.2202 12.5 12.5 12.2202 12.5 11.875V10.625C12.5 10.2798 12.2202 10 11.875 10C11.5298 10 11.25 10.2798 11.25 10.625Z" fill="#757575">', '</path>',
                '<path d="M7.50003 9.375C7.37046 9.37599 7.24378 9.33667 7.13753 9.2625L4.63753 7.5C4.50279 7.40442 4.41137 7.25937 4.38326 7.09658C4.35515 6.93379 4.39264 6.76649 4.48753 6.63125C4.5349 6.56366 4.59518 6.50611 4.66491 6.46194C4.73463 6.41777 4.81242 6.38785 4.89377 6.37391C4.97512 6.35996 5.05843 6.36227 5.13889 6.38069C5.21934 6.39911 5.29535 6.43329 5.36253 6.48125L7.50003 7.975L9.62503 6.375C9.75764 6.27555 9.92432 6.23284 10.0884 6.25628C10.2525 6.27973 10.4006 6.36739 10.5 6.5C10.5995 6.63261 10.6422 6.7993 10.6187 6.96339C10.5953 7.12749 10.5076 7.27555 10.375 7.375L7.87503 9.25C7.76685 9.33114 7.63526 9.375 7.50003 9.375Z" fill="#757575">', '</path>',
                '<path d="M7.5 8.125C7.33424 8.125 7.17527 8.05915 7.05806 7.94194C6.94085 7.82473 6.875 7.66576 6.875 7.5V2.5C6.875 2.33424 6.94085 2.17527 7.05806 2.05806C7.17527 1.94085 7.33424 1.875 7.5 1.875C7.66576 1.875 7.82473 1.94085 7.94194 2.05806C8.05915 2.17527 8.125 2.33424 8.125 2.5V7.5C8.125 7.66576 8.05915 7.82473 7.94194 7.94194C7.82473 8.05915 7.66576 8.125 7.5 8.125Z" fill="#757575">', '</path>',
                '</svg>',
                '</a>',
                // '<p style="overflow-wrap: break-word;">' + message + '</p>',
                '</div>',
                '</div>',
                '</div>',
                '</div>',
                '<div class="chat-agent-image">',
                profile,
                '</div>',
                '</div>',
                '<span class="message-time-bot">' + time + '</span>',
                '</div>',
            ].join('');
        }
    } else {
        var document_file_svg = "";
        var message_html = "";
        if (extension == "pdf") {
            document_file_svg = [
                '<svg width="35" height="30" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">',
                '<path d="M31.6312 2.71948L38.934 10.332V39.2805H11.6537V39.375H39.0272V10.4278L31.6312 2.71948Z" fill="#909090">', '</path>',
                '<path d="M31.5406 2.625H11.5604V39.2805H38.9339V10.3333L31.5393 2.625" fill="#F4F4F4">', '</path>',
                '<path d="M11.3596 4.59375H2.97272V13.5542H29.354V4.59375H11.3596Z" fill="#7A7B7C">', '</path>',
                '<path d="M29.4943 13.4019H3.14328V4.43494H29.4943V13.4019Z" fill="#DD2025">', '</path>',
                '<path d="M11.8808 5.95087H10.1653V12.2509H11.5146V10.1259L11.8125 10.143C12.102 10.138 12.3888 10.0862 12.6617 9.98943C12.901 9.90713 13.1211 9.77721 13.3088 9.60749C13.4997 9.44582 13.6503 9.24177 13.7485 9.01162C13.8801 8.62902 13.9271 8.22241 13.8863 7.81987C13.8781 7.53231 13.8277 7.24752 13.7367 6.97462C13.6538 6.77762 13.5308 6.60003 13.3756 6.45315C13.2204 6.30627 13.0362 6.19332 12.835 6.12149C12.6609 6.05849 12.4811 6.01277 12.2982 5.98499C12.1596 5.96361 12.0197 5.95221 11.8795 5.95087H11.8808ZM11.6314 8.96174H11.5146V7.01924H11.7679C11.8797 7.01118 11.9919 7.02834 12.0962 7.06946C12.2004 7.11058 12.2941 7.17461 12.3703 7.2568C12.5283 7.46814 12.6126 7.72537 12.6105 7.98918C12.6105 8.31205 12.6105 8.60474 12.3192 8.8108C12.1092 8.92626 11.8703 8.97824 11.6314 8.96043" fill="#464648">', '</path>',
                '<path d="M16.4495 5.93381C16.3038 5.93381 16.162 5.94431 16.0623 5.94825L15.7499 5.95612H14.7262V12.2561H15.931C16.3915 12.2687 16.8499 12.1907 17.2803 12.0264C17.6267 11.889 17.9334 11.6676 18.1728 11.382C18.4056 11.0938 18.5727 10.7583 18.6624 10.3989C18.7655 9.99189 18.8158 9.57326 18.812 9.15337C18.8374 8.65745 18.7991 8.16032 18.6978 7.67419C18.6017 7.31635 18.4217 6.98656 18.1728 6.71212C17.9775 6.49052 17.7384 6.31177 17.4706 6.18712C17.2406 6.0807 16.9987 6.00227 16.75 5.9535C16.6512 5.93716 16.551 5.9297 16.4508 5.93119L16.4495 5.93381ZM16.2119 11.0985H16.0807V7.077H16.0977C16.3683 7.04587 16.6421 7.09469 16.8852 7.21744C17.0633 7.35961 17.2084 7.53874 17.3105 7.74244C17.4207 7.95681 17.4842 8.1921 17.4969 8.43281C17.5087 8.72156 17.4969 8.95781 17.4969 9.15337C17.5022 9.37865 17.4877 9.60395 17.4535 9.82669C17.4131 10.0554 17.3383 10.2766 17.2317 10.4829C17.1111 10.6748 16.9481 10.8364 16.7553 10.9554C16.5934 11.0602 16.4016 11.109 16.2093 11.0946" fill="#464648">', '</path>',
                '<path d="M22.8769 5.95612H19.6875V12.2561H21.0367V9.75712H22.743V8.58637H21.0367V7.12687H22.8742V5.95612" fill="#464648">', '</path>',
                '<path d="M28.5875 26.5847C28.5875 26.5847 32.7717 25.8261 32.7717 27.2554C32.7717 28.6847 30.1795 28.1033 28.5875 26.5847ZM25.4939 26.6936C24.8291 26.8405 24.1812 27.0556 23.5606 27.3355L24.0856 26.1542C24.6106 24.9729 25.1553 23.3625 25.1553 23.3625C25.7817 24.4169 26.5106 25.4069 27.3314 26.3183C26.7124 26.4106 26.099 26.5367 25.4939 26.6963V26.6936ZM23.8375 18.1624C23.8375 16.9168 24.2405 16.5769 24.5541 16.5769C24.8678 16.5769 25.2209 16.7278 25.2327 17.8093C25.1305 18.8968 24.9028 19.9688 24.5541 21.004C24.0766 20.1349 23.8294 19.158 23.8362 18.1663L23.8375 18.1624ZM17.7357 31.9646C16.4521 31.1968 20.4277 28.833 21.1482 28.7569C21.1443 28.7582 19.0797 32.7679 17.7357 31.9646ZM33.9936 27.4247C33.9805 27.2935 33.8624 25.8405 31.2768 25.9022C30.199 25.8848 29.1218 25.9608 28.0572 26.1293C27.0259 25.0903 26.1378 23.9184 25.4165 22.6446C25.8709 21.3313 26.146 19.9627 26.2342 18.5758C26.1961 17.0008 25.8194 16.0978 24.6119 16.111C23.4044 16.1241 23.2285 17.1806 23.3873 18.753C23.5429 19.8096 23.8363 20.8413 24.2601 21.8216C24.2601 21.8216 23.7023 23.5581 22.9647 25.2853C22.2271 27.0126 21.7231 27.9182 21.7231 27.9182C20.4404 28.3358 19.2329 28.9561 18.1465 29.7557C17.065 30.7624 16.6253 31.5354 17.195 32.3085C17.6858 32.9753 19.4039 33.1262 20.9395 31.1141C21.7555 30.0749 22.5009 28.9822 23.1708 27.8434C23.1708 27.8434 25.5123 27.2016 26.2407 27.0257C26.9691 26.8498 27.8498 26.7107 27.8498 26.7107C27.8498 26.7107 29.9879 28.8619 32.0498 28.7858C34.1118 28.7096 34.012 27.5533 33.9989 27.4273" fill="#DD2025">', '</path>',
                '<path d="M31.4397 2.72607V10.4344H38.833L31.4397 2.72607Z" fill="#909090">', '</path>',
                '<path d="M31.5408 2.625V10.3333H38.9341L31.5408 2.625Z" fill="#F4F4F4">', '</path>',
                '<path d="M11.7797 5.84982H10.0642V12.1498H11.4187V10.0262L11.718 10.0433C12.0075 10.0383 12.2943 9.98642 12.5672 9.8897C12.8064 9.80737 13.0265 9.67745 13.2142 9.50776C13.4038 9.34565 13.553 9.14164 13.65 8.91189C13.7816 8.52929 13.8286 8.12268 13.7878 7.72014C13.7796 7.43258 13.7292 7.14778 13.6382 6.87489C13.5553 6.67789 13.4324 6.5003 13.2771 6.35342C13.1219 6.20654 12.9378 6.09359 12.7365 6.02176C12.5617 5.95815 12.381 5.91198 12.1971 5.88395C12.0585 5.86257 11.9186 5.85116 11.7784 5.84982H11.7797ZM11.5303 8.8607H11.4135V6.9182H11.6681C11.7799 6.91014 11.8921 6.9273 11.9964 6.96842C12.1006 7.00954 12.1943 7.07356 12.2706 7.15576C12.4285 7.36709 12.5128 7.62433 12.5107 7.88814C12.5107 8.21101 12.5107 8.5037 12.2194 8.70976C12.0095 8.82521 11.7705 8.8772 11.5316 8.85939" fill="white">', '</path>',
                '<path d="M16.3486 5.83277C16.203 5.83277 16.0612 5.84327 15.9615 5.8472L15.653 5.85508H14.6293V12.1551H15.8341C16.2946 12.1677 16.7531 12.0897 17.1834 11.9254C17.5298 11.788 17.8365 11.5665 18.0759 11.281C18.3087 10.9928 18.4758 10.6573 18.5655 10.2979C18.6686 9.89085 18.7189 9.47222 18.7151 9.05233C18.7405 8.55641 18.7022 8.05928 18.6009 7.57314C18.5048 7.21531 18.3248 6.88551 18.0759 6.61108C17.8806 6.38948 17.6415 6.21073 17.3737 6.08608C17.1437 5.97966 16.9018 5.90122 16.6531 5.85245C16.5543 5.83612 16.4541 5.82865 16.3539 5.83014L16.3486 5.83277ZM16.115 10.9975H15.9838V6.97595H16.0008C16.2714 6.94482 16.5452 6.99364 16.7883 7.11639C16.9664 7.25857 17.1115 7.43769 17.2136 7.64139C17.3238 7.85577 17.3873 8.09106 17.4 8.33177C17.4118 8.62052 17.4 8.85677 17.4 9.05233C17.4053 9.2776 17.3908 9.50291 17.3566 9.72564C17.3162 9.95432 17.2414 10.1756 17.1348 10.3819C17.0142 10.5737 16.8512 10.7354 16.6584 10.8544C16.4965 10.9591 16.3047 11.008 16.1124 10.9935" fill="white">', '</path>',
                '<path d="M22.7758 5.85507H19.5864V12.1551H20.9356V9.65607H22.6419V8.48532H20.9356V7.02582H22.7731V5.85507" fill="white">', '</path>',
                '</svg>',
            ].join('');
        } else {
            document_file_svg = [
                '<svg width="30" height="30" viewBox="0 0 18 22" fill="none" xmlns="http://www.w3.org/2000/svg">',
                '<path d="M11.9321 0H3.3949C2.14766 0 1.13257 1.01579 1.13257 2.26228V10.6278H0.91157C0.408194 10.6278 0 11.0357 0 11.5395V17.0681C0 17.5718 0.408194 17.9796 0.91157 17.9796H1.13257V18.9934C1.13257 20.2412 2.14766 21.2557 3.39486 21.2557H15.0434C16.2898 21.2557 17.3049 20.2412 17.3049 18.9934V5.35422L11.9321 0ZM1.5081 12.2989C1.82671 12.2482 2.24178 12.2196 2.67996 12.2196C3.40808 12.2196 3.88025 12.3503 4.25022 12.6289C4.64836 12.9249 4.89846 13.3974 4.89846 14.0742C4.89846 14.8078 4.6313 15.3144 4.26133 15.6271C3.85763 15.9626 3.24311 16.1217 2.49237 16.1217C2.04287 16.1217 1.72426 16.0933 1.50814 16.0648V12.2989H1.5081ZM15.0434 19.8702H3.3949C2.91194 19.8702 2.51869 19.477 2.51869 18.9934V17.9796H13.3776C13.8809 17.9796 14.2892 17.5718 14.2892 17.0681V11.5395C14.2892 11.0357 13.881 10.6278 13.3776 10.6278H2.51869V2.26228C2.51869 1.78007 2.91194 1.38682 3.3949 1.38682L11.4137 1.37844V4.34249C11.4137 5.20825 12.1162 5.91139 12.9825 5.91139L15.8862 5.90305L15.9189 18.9933C15.9189 19.477 15.5263 19.8702 15.0434 19.8702ZM5.29308 14.1936C5.29308 13.0444 6.02685 12.1856 7.15902 12.1856C8.33674 12.1856 8.97943 13.0673 8.97943 14.1255C8.97943 15.3824 8.21723 16.1446 7.09647 16.1446C5.95878 16.1446 5.29308 15.2859 5.29308 14.1936ZM11.5131 15.4221C11.7747 15.4221 12.0647 15.3651 12.2356 15.2969L12.3663 15.9737C12.2072 16.0537 11.8486 16.1391 11.3824 16.1391C10.0567 16.1391 9.37409 15.3144 9.37409 14.2222C9.37409 12.9138 10.3072 12.1856 11.4675 12.1856C11.9171 12.1856 12.2582 12.2766 12.4118 12.3559L12.2356 13.0444C12.0591 12.97 11.8145 12.902 11.5075 12.902C10.8189 12.902 10.2843 13.3175 10.2843 14.1707C10.2843 14.9385 10.7394 15.4221 11.5131 15.4221Z" fill="#0254D7"/>',
                '<path d="M3.97708 14.1026C3.98264 13.3057 3.51612 12.8854 2.77088 12.8854C2.57734 12.8854 2.45227 12.902 2.3783 12.9194V15.4276C2.45227 15.4451 2.57183 15.4451 2.67989 15.4451C3.46502 15.4506 3.97708 15.0184 3.97708 14.1026Z" fill="#0254D7"/>',
                '<path d="M8.0637 14.1534C8.0637 13.4655 7.73367 12.8735 7.13644 12.8735C6.5504 12.8735 6.20886 13.4314 6.20886 14.1763C6.20886 14.9274 6.56182 15.4561 7.14204 15.4561C7.72812 15.4561 8.0637 14.8988 8.0637 14.1534Z" fill="#0254D7"/>',
                '</svg>',
            ].join('');
        }
        if (message) {
            message_html = '<div class="upload-file-text-area">' + message + '</div>';
        }

        if (sender == "client") {
            html = [
                '<div class="chat-client-attachment-wrapper">',
                '<div style="display: flex; flex-direction: row;">',
                '<div class="chat-client-image">',
                '<svg width="9" height="12" viewBox="0 0 9 12" fill="none" xmlns="http://www.w3.org/2000/svg">',
                '<path d="M4.50001 0.571426C3.17682 0.571426 2.10417 1.79731 2.10417 3.30952C2.10417 4.82173 3.17682 6.04762 4.50001 6.04762C5.82319 6.04762 6.89584 4.82173 6.89584 3.30952C6.89584 1.79731 5.82319 0.571426 4.50001 0.571426Z" fill="white"/>',
                '<path d="M1.68487 7.14285C1.12266 7.14285 0.666677 7.66344 0.666672 8.30624L0.666672 8.5119C0.666672 9.54021 1.13186 10.31 1.84546 10.8065C2.54718 11.2947 3.49042 11.5238 4.50001 11.5238C5.50959 11.5238 6.45283 11.2947 7.15455 10.8065C7.86815 10.31 8.33334 9.54021 8.33334 8.5119L8.33334 8.3062C8.33333 7.66341 7.87735 7.14285 7.31516 7.14285H1.68487Z" fill="white"/>',
                '</svg>',
                '</div>',
                '<div class="live-chat-client-message-bubble file-attachement-download">',
                '<div style="display: flex; justify-content: space-around; align-items: center;">',
                '<div>',
                document_file_svg,
                '</div>',
                '<div class="file-attachment-path">',
                '<span class="custom-text-attach">' + file_name + '</span>',
                '</div>',
                '<a href="' + file_src + '?session_id=' + session_id + '" download>',
                '<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">',
                '<path d="M11.875 11.25H3.125C2.77982 11.25 2.5 11.5298 2.5 11.875C2.5 12.2202 2.77982 12.5 3.125 12.5H11.875C12.2202 12.5 12.5 12.2202 12.5 11.875C12.5 11.5298 12.2202 11.25 11.875 11.25Z" fill="#757575">', '</path>',
                '<path d="M2.5 10.625V11.875C2.5 12.2202 2.77982 12.5 3.125 12.5C3.47018 12.5 3.75 12.2202 3.75 11.875V10.625C3.75 10.2798 3.47018 10 3.125 10C2.77982 10 2.5 10.2798 2.5 10.625Z" fill="#757575">', '</path>',
                '<path d="M11.25 10.625V11.875C11.25 12.2202 11.5298 12.5 11.875 12.5C12.2202 12.5 12.5 12.2202 12.5 11.875V10.625C12.5 10.2798 12.2202 10 11.875 10C11.5298 10 11.25 10.2798 11.25 10.625Z" fill="#757575">', '</path>',
                '<path d="M7.50003 9.375C7.37046 9.37599 7.24378 9.33667 7.13753 9.2625L4.63753 7.5C4.50279 7.40442 4.41137 7.25937 4.38326 7.09658C4.35515 6.93379 4.39264 6.76649 4.48753 6.63125C4.5349 6.56366 4.59518 6.50611 4.66491 6.46194C4.73463 6.41777 4.81242 6.38785 4.89377 6.37391C4.97512 6.35996 5.05843 6.36227 5.13889 6.38069C5.21934 6.39911 5.29535 6.43329 5.36253 6.48125L7.50003 7.975L9.62503 6.375C9.75764 6.27555 9.92432 6.23284 10.0884 6.25628C10.2525 6.27973 10.4006 6.36739 10.5 6.5C10.5995 6.63261 10.6422 6.7993 10.6187 6.96339C10.5953 7.12749 10.5076 7.27555 10.375 7.375L7.87503 9.25C7.76685 9.33114 7.63526 9.375 7.50003 9.375Z" fill="#757575">', '</path>',
                '<path d="M7.5 8.125C7.33424 8.125 7.17527 8.05915 7.05806 7.94194C6.94085 7.82473 6.875 7.66576 6.875 7.5V2.5C6.875 2.33424 6.94085 2.17527 7.05806 2.05806C7.17527 1.94085 7.33424 1.875 7.5 1.875C7.66576 1.875 7.82473 1.94085 7.94194 2.05806C8.05915 2.17527 8.125 2.33424 8.125 2.5V7.5C8.125 7.66576 8.05915 7.82473 7.94194 7.94194C7.82473 8.05915 7.66576 8.125 7.5 8.125Z" fill="#757575">', '</path>',
                '</svg>',
                '</a>',
                '</div>',
                message_html,
                '</div>',
                '</div>',
                '<span class="message-time-bot">' + time + '</span>',
                '</div>',
            ].join('');
        } else {
            html = [
                '<div class="chat-agent-attachment-wrapper">',
                '<div style="display: flex; flex-direction: row; justify-content: flex-end;">',
                '<div class="live-chat-agent-message-bubble file-attachement-download">',
                '<div style="display: flex; justify-content: space-around; align-items: center;">',
                '<div>',
                document_file_svg,
                '</div>',
                '<div class="file-attachment-path">',
                '<span class="custom-text-attach">' + file_name + '</span>',
                '</div>',
                '<a href="' + file_src + '?session_id=' + session_id + '" download>',
                '<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">',
                '<path d="M11.875 11.25H3.125C2.77982 11.25 2.5 11.5298 2.5 11.875C2.5 12.2202 2.77982 12.5 3.125 12.5H11.875C12.2202 12.5 12.5 12.2202 12.5 11.875C12.5 11.5298 12.2202 11.25 11.875 11.25Z" fill="#757575">', '</path>',
                '<path d="M2.5 10.625V11.875C2.5 12.2202 2.77982 12.5 3.125 12.5C3.47018 12.5 3.75 12.2202 3.75 11.875V10.625C3.75 10.2798 3.47018 10 3.125 10C2.77982 10 2.5 10.2798 2.5 10.625Z" fill="#757575">', '</path>',
                '<path d="M11.25 10.625V11.875C11.25 12.2202 11.5298 12.5 11.875 12.5C12.2202 12.5 12.5 12.2202 12.5 11.875V10.625C12.5 10.2798 12.2202 10 11.875 10C11.5298 10 11.25 10.2798 11.25 10.625Z" fill="#757575">', '</path>',
                '<path d="M7.50003 9.375C7.37046 9.37599 7.24378 9.33667 7.13753 9.2625L4.63753 7.5C4.50279 7.40442 4.41137 7.25937 4.38326 7.09658C4.35515 6.93379 4.39264 6.76649 4.48753 6.63125C4.5349 6.56366 4.59518 6.50611 4.66491 6.46194C4.73463 6.41777 4.81242 6.38785 4.89377 6.37391C4.97512 6.35996 5.05843 6.36227 5.13889 6.38069C5.21934 6.39911 5.29535 6.43329 5.36253 6.48125L7.50003 7.975L9.62503 6.375C9.75764 6.27555 9.92432 6.23284 10.0884 6.25628C10.2525 6.27973 10.4006 6.36739 10.5 6.5C10.5995 6.63261 10.6422 6.7993 10.6187 6.96339C10.5953 7.12749 10.5076 7.27555 10.375 7.375L7.87503 9.25C7.76685 9.33114 7.63526 9.375 7.50003 9.375Z" fill="#757575">', '</path>',
                '<path d="M7.5 8.125C7.33424 8.125 7.17527 8.05915 7.05806 7.94194C6.94085 7.82473 6.875 7.66576 6.875 7.5V2.5C6.875 2.33424 6.94085 2.17527 7.05806 2.05806C7.17527 1.94085 7.33424 1.875 7.5 1.875C7.66576 1.875 7.82473 1.94085 7.94194 2.05806C8.05915 2.17527 8.125 2.33424 8.125 2.5V7.5C8.125 7.66576 8.05915 7.82473 7.94194 7.94194C7.82473 8.05915 7.66576 8.125 7.5 8.125Z" fill="#757575">', '</path>',
                '</svg>',
                '</a>',
                '</div>',
                message_html,
                '</div>',
                '<div class="chat-agent-image">',
                profile,
                '</div>',
                '</div>',
                '<span class="message-time-bot">' + time + '</span>',
                '</div>',
            ].join('');
        }

    }
    return html;
}

function show_agents_chat_history_for_session(session_id) {

    let json_string = JSON.stringify({
        "session_id": session_id
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/get-cobrowsing-chat-history/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response.chat_history.length > 0) {
                var chat_html = '<div class="chat-area"><div class="chat-message-wrapper">';
                let chat_history = response.chat_history;
                let client_name = response.client_name
                for (let index = 0; index < chat_history.length; index++) {
                    let sender = chat_history[index]["sender"];
                    let message = chat_history[index]["message"];
                    let datetime = chat_history[index]["datetime"];
                    let attachment = chat_history[index]["attachment"];
                    let attachment_file_name = chat_history[index]["attachment_file_name"];
                    let is_invited_agent = chat_history[index]["is_invited_agent"];
                    let chat_type = chat_history[index]["chat_type"]
                    let sender_name = chat_history[index]["sender_name"]
                    let display_agent_profile = chat_history[index]["display_agent_profile"]
                    let agent_profile_pic_source = chat_history[index]["agent_profile_pic_source"]

                    if(chat_type == "chat_bubble"){
                        chat_html += '<p class="easyassist-chat-bubble">' + message + '</p>';
                    } else if (sender == "client") {
                        if (attachment != null) {
                            chat_html += get_cobrowsing_attachment_html(sender, client_name, attachment, attachment_file_name, datetime, message, session_id);
                        } else {
                            chat_html += [
                                '<div class="chat-client-message-wrapper">',
                                '<div class="chat-client-image"><svg width="9" height="12" viewBox="0 0 9 12" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path d="M4.50001 0.571426C3.17682 0.571426 2.10417 1.79731 2.10417 3.30952C2.10417 4.82173 3.17682 6.04762 4.50001 6.04762C5.82319 6.04762 6.89584 4.82173 6.89584 3.30952C6.89584 1.79731 5.82319 0.571426 4.50001 0.571426Z" fill="white"/>',
                                '<path d="M1.68487 7.14285C1.12266 7.14285 0.666677 7.66344 0.666672 8.30624L0.666672 8.5119C0.666672 9.54021 1.13186 10.31 1.84546 10.8065C2.54718 11.2947 3.49042 11.5238 4.50001 11.5238C5.50959 11.5238 6.45283 11.2947 7.15455 10.8065C7.86815 10.31 8.33334 9.54021 8.33334 8.5119L8.33334 8.3062C8.33333 7.66341 7.87735 7.14285 7.31516 7.14285H1.68487Z" fill="white"/>',
                                '</svg>',
                                '</div>',
                                '<div class="chat-client-message-bubble">',
                                '<div class="client-name-div">' + client_name + '</div>',
                                message,
                                '</div>',
                                '<div class="chat-client-message-time">' + datetime + '</div>',
                                '</div>'
                            ].join('');
                        }
                    } else {
                        var msg_sender_name = sender_name;
                        if (is_invited_agent) {
                            msg_sender_name = sender_name + " (Invited)";
                        }

                        if (attachment != null) {
                            chat_html += get_cobrowsing_attachment_html(sender, msg_sender_name, attachment, attachment_file_name, datetime, message, session_id, display_agent_profile, agent_profile_pic_source);
                        } else {
                            msg_sender_name = sender_name;
                            if (is_invited_agent) {
                                msg_sender_name = sender_name + " (Invited)";
                            }
                            let profile = ""
                            if(display_agent_profile && agent_profile_pic_source != "" && agent_profile_pic_source != undefined){
                                let src = "/" + agent_profile_pic_source;
                                profile = [
                                    '<img src = "'+ src + '" width="9" height="12"/>'
                                ]
                            } else {
                                profile = ['<svg width="9" height="12" viewBox="0 0 9 12" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path d="M4.50001 0.571426C3.17682 0.571426 2.10417 1.79731 2.10417 3.30952C2.10417 4.82173 3.17682 6.04762 4.50001 6.04762C5.82319 6.04762 6.89584 4.82173 6.89584 3.30952C6.89584 1.79731 5.82319 0.571426 4.50001 0.571426Z" fill="white"/>',
                                '<path d="M1.68487 7.14285C1.12266 7.14285 0.666677 7.66344 0.666672 8.30624L0.666672 8.5119C0.666672 9.54021 1.13186 10.31 1.84546 10.8065C2.54718 11.2947 3.49042 11.5238 4.50001 11.5238C5.50959 11.5238 6.45283 11.2947 7.15455 10.8065C7.86815 10.31 8.33334 9.54021 8.33334 8.5119L8.33334 8.3062C8.33333 7.66341 7.87735 7.14285 7.31516 7.14285H1.68487Z" fill="white"/>',
                                '</svg>'].join();
                            }
                            
                            chat_html += [
                                '<div class="chat-agent-message-wrapper">',
                                '<div class="chat-agent-image">',
                                profile,
                                '</div>',
                                '<div class="chat-agent-message-bubble">',
                                '<div class="agent-name-div">' + msg_sender_name + '</div>',
                                '<div>',
                                message,
                                '</div>',
                                '</div>',
                                '<div class="chat-agent-message-time">',
                                datetime,
                                '</div>',
                                '</div>'
                            ].join('');
                        }
                    }
                }
                chat_html += "</div></div>"
                document.getElementById("session-chat-history-container").innerHTML = chat_html;
            } else {
                document.getElementById("session-chat-history-container").innerHTML = "<p>No chat history</p>";
            }
        }
    }
    xhttp.send(params);
}

function capture_cobrowsing_general_feedback(action_element) {

    function clear_cobrowsing_feedback_form() {
        document.getElementById('cobrowsing-feedback-textarea').value = "";
        document.getElementById("cobrowsing-feedback-file").value = "";
    }

    function generate_cobrowsing_random_string(length) {
        var result = '';
        var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        var charactersLength = characters.length;
        for (let i = 0; i < length; i++) {
            result += characters.charAt(Math.floor(Math.random() * charactersLength));
        }
        return result;
    }


    function easyassist_custom_encrypt_variable(data) {
        let utf_data = CryptoJS.enc.Utf8.parse(data);
        let encoded_data = utf_data;
        let random_key = generate_cobrowsing_random_string(16);
        var iv = CryptoJS.lib.WordArray.random(16);
        var encrypted = CryptoJS.AES.encrypt(encoded_data, CryptoJS.enc.Utf8.parse(random_key), {
            iv: iv
        });
        var return_value = random_key;
        return_value += "." + encrypted.toString();
        return_value += "." + CryptoJS.enc.Base64.stringify(iv);
        return return_value;
    }

    let cobrowsing_feedback_error_element = document.getElementById("cobrowsing-feedback-error");
    cobrowsing_feedback_error_element.innerHTML = "";

    let description = document.getElementById('cobrowsing-feedback-textarea').value.trim();
    if (description == "") {
        cobrowsing_feedback_error_element.style.color = "red";
        cobrowsing_feedback_error_element.innerHTML = "*Description cannot be empty";
        return;
    }

    let feedback_category = document.getElementById("cobrowsing-feedback-category").value;
    if (feedback_category == "None") {
        cobrowsing_feedback_error_element.style.color = "red";
        cobrowsing_feedback_error_element.innerHTML = "*Category cannot be empty";
        return;
    }

    let feedback_priority = document.getElementById("cobrowsing-feedback-priority").value;
    if (feedback_priority == "None") {
        cobrowsing_feedback_error_element.style.color = "red";
        cobrowsing_feedback_error_element.innerHTML = "*Priority cannot be empty";
        return;
    }

    let is_feedback_screenshot_attached = true;
    if (!($("#cobrowsing-feedback-file"))[0].files[0]) {
        is_feedback_screenshot_attached = false;
    }

    action_element.innerHTML = "submitting...";

    if (is_feedback_screenshot_attached) {

        var input_upload_image = ($("#cobrowsing-feedback-file"))[0].files[0]
        var malicious_file_report = check_malicious_file(input_upload_image.name)
        if (malicious_file_report.status == true) {
            show_easyassist_toast(malicious_file_report.message)
            action_element.innerHTML = "Submit";
            return false;
        }
        if (check_image_file(input_upload_image.name) == false) {
            action_element.innerHTML = "Submit";
            return false;
        }
        var formData = new FormData();
        var CSRF_TOKEN = $('input[name="csrfmiddlewaretoken"]').val();
        formData.append("input_upload_image", input_upload_image);
        $.ajax({
            url: "/chat/upload-image/",
            type: "POST",
            headers: {
                'X-CSRFToken': CSRF_TOKEN
            },
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response["status"] == 200) {
                    let json_string = JSON.stringify({
                        description: description,
                        category: feedback_category,
                        priority: feedback_priority,
                        app: "EasyAssist",
                        src: response['src'],
                    });
                    json_string = easyassist_custom_encrypt_variable(json_string);
                    $.ajax({
                        url: "/chat/capture-general-feedback/",
                        type: "POST",
                        data: {
                            data: json_string,
                        },
                        success: function(response) {
                            if (response['status'] == 200) {
                                show_easyassist_toast("Feedback saved successfully.");
                                clear_cobrowsing_feedback_form();
                                $('#cobrowsing_feedback_modal').modal('hide');
                            } else {
                                show_easyassist_toast("Unable to save feedback.");
                            }
                            action_element.innerHTML = "Submit";
                        },
                        error: function(xhr, textstatus, errorthrown) {
                            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
                        }
                    });

                } else if (response["status"] == 300) {
                    show_easyassist_toast("File format is invalid.");
                    action_element.innerHTML = "Submit";

                } else {
                    show_easyassist_toast("Unable to upload file. Please try again later.");
                    action_element.innerHTML = "Submit";
                }
            },
            error: function(xhr, textstatus, errorthrown) {
                console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
                action_element.innerHTML = "Submit";
            }
        });
    } else {
        let json_string = JSON.stringify({
            description: description,
            category: feedback_category,
            priority: feedback_priority,
            app: "EasyAssist",
            src: "",
        });
        json_string = easyassist_custom_encrypt_variable(json_string);
        $.ajax({
            url: "/chat/capture-general-feedback/",
            type: "POST",
            data: {
                data: json_string,
            },
            success: function(response) {
                if (response['status'] == 200) {
                    show_easyassist_toast("Feedback saved successfully.");
                    clear_cobrowsing_feedback_form();
                    $('#cobrowsing_feedback_modal').modal('hide');
                } else {
                    show_easyassist_toast("Unable to save feedback");
                }
                action_element.innerHTML = "Submit";
            },
            error: function(xhr, textstatus, errorthrown) {
                console.error(errorthrown);
                action_element.innerHTML = "Submit";
            }
        });
    }
}

setInterval(function(e) {
    check_and_mark_agent_active_status("none");
}, 15000);

check_and_mark_agent_active_status("none");

function export_support_history() {

    let general_error_message = document.getElementById("general-error-message");
    general_error_message.style.color = "red";
    general_error_message.innerHTML = "";

    let selected_filter_value = document.getElementById("select-date-range").value;

    if (selected_filter_value == "0") {
        general_error_message.innerHTML = "Please select valid date range filter";
        return;
    }

    let startdate = $('#startdate').val();
    let enddate = $('#enddate').val();
    startdate = get_iso_formatted_date(startdate);
    enddate = get_iso_formatted_date(enddate);

    let email_field = document.getElementById('filter-data-email');

    var startdate_obj = new Date(startdate)
    var enddate_obj = new Date(enddate)
    var today_date = new Date()
    if (selected_filter_value == "4") {
        if (!startdate.length) {
            general_error_message.innerHTML = EMPTY_START_DATE_ERROR_TOAST;
            return;
        } else if (!enddate.length) {
            general_error_message.innerHTML = EMPTY_END_DATE_ERROR_TOAST;
            return;
        } else if (startdate_obj.getTime() > enddate_obj.getTime()) {
            general_error_message.innerHTML = "Start date cannot be greater than the end date";
            return;
        } else if (enddate_obj.getTime() > today_date.getTime()) {
            general_error_message.innerHTML = "End date cannot be past today's date";
            return;
        }
    }

    if (selected_filter_value == "4") {
        let email_value_list = email_field.value;
        email_value_list = email_value_list.split(",")
        if (email_value_list.length == 0) {
            general_error_message.innerHTML = "Please enter valid Email ID";
            return;
        }

        for (let index = 0; index < email_value_list.length; index++) {

            if (!regEmail.test(email_value_list[index])) {
                general_error_message.innerHTML = "Please enter valid Email ID";
                return;
            }
        }
    }
    
    if(!document.getElementById("support_history").checked && !document.getElementById("chat_history").checked) {
        general_error_message.innerHTML = "Please select a report to export";
        return;
    }

    var json_string = JSON.stringify({
        "selected_filter_value": selected_filter_value,
        "startdate": startdate,
        "enddate": enddate,
        "email": email_field.value,
        "is_support_history": document.getElementById("support_history").checked,
        "is_chat_history": document.getElementById("chat_history").checked,
    });
    
    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/export-support-history/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response); 
            
            if (response.status == 200 && response["export_path_exist"] && response["chat_export_path_exist"] && response["export_path"] != "None") {
                let export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else if (response.support_status == 200 && response["export_path_exist"] && response["export_path"] != "None") {
                let export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
                if (response.chat_status == 300) {
                    general_error_message.style.color = "green";
                    general_error_message.innerHTML = "Your request has been recorded. You will get the chat history in your email within the next 24 hours.";
                    setTimeout(function() {
                        $('#modal-mis-filter').modal('hide');
                    }, 2000);
                }
            } else if (response.chat_status == 200 && response["chat_export_path_exist"] && response["chat_export_path"] != "None") {
                let export_path = response["chat_export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else if (response.support_status == 300 || response.chat_status == 300) {
                general_error_message.style.color = "green";
                general_error_message.innerHTML = "Your request has been recorded. You will get the email within next 24 hours.";
                setTimeout(function() {
                    $('#modal-mis-filter').modal('hide');
                }, 2000);
            } else if (response.status == 302 ) {
                show_easyassist_toast(response.message);
            } else {
                general_error_message.style.color = "red";
                general_error_message.innerHTML = "Unable to download history";
            }
        }
    }
    xhttp.send(params);
}

function export_unattended_leads(el) {

    let general_error_message = document.getElementById("general-error-message");
    general_error_message.style.color = "red";
    general_error_message.innerHTML = "";

    let selected_filter_value = document.getElementById("select-date-range").value;

    if (selected_filter_value == "0") {
        general_error_message.innerHTML = "Please select valid date range filter";
        return;
    }

    let startdate = $('#startdate').val();
    let enddate = $('#enddate').val();
    startdate = get_iso_formatted_date(startdate);
    enddate = get_iso_formatted_date(enddate);

    let email_field = document.getElementById('filter-data-email');

    var startdate_obj = new Date(startdate)
    var enddate_obj = new Date(enddate)
    var today_date = new Date()
    if (selected_filter_value == "4") {
        if (!startdate.length) {
            general_error_message.innerHTML = EMPTY_START_DATE_ERROR_TOAST;
            return;
        } else if (!enddate.length) {
            general_error_message.innerHTML = EMPTY_END_DATE_ERROR_TOAST;
            return;
        } else if (startdate_obj.getTime() > enddate_obj.getTime()) {
            general_error_message.innerHTML = "Start date cannot be greater than the end date";
            return;
        } else if (enddate_obj.getTime() > today_date.getTime()) {
            general_error_message.innerHTML = "End date cannot be past today's date";
            return;
        }
    }

    if (selected_filter_value == "4") {
        let email_value_list = email_field.value;
        email_value_list = email_value_list.split(",")
        if (email_value_list.length == 0) {
            general_error_message.innerHTML = "Please enter valid Email ID";
            return;
        }

        for (let index = 0; index < email_value_list.length; index++) {

            if (!regEmail.test(email_value_list[index])) {
                general_error_message.innerHTML = "Please enter valid Email ID";
                return;
            }
        }
    }

    el.innerHTML = "Exporting...";
    el.disabled = true;

    var json_string = JSON.stringify({
        "selected_filter_value": selected_filter_value,
        "startdate": startdate,
        "enddate": enddate,
        "email": email_field.value,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/export-unattended-leads-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path_exist"] && response["export_path"] != "None") {
                let export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else if (response.status == 300) {
                general_error_message.style.color = "green";
                general_error_message.innerHTML = "Your request has been recorded. You will get the Email in next 24 hrs.";
                setTimeout(function() {
                    $('#modal-mis-filter').modal('hide');
                }, 2000);
            } else if (response.status == 302 ) {
                show_easyassist_toast(response.message);
            } else {
                general_error_message.style.color = "red";
                general_error_message.innerHTML = "Unable to download support history";
            }
            el.innerHTML = "Export";
            el.disabled = false;
        }
    }
    xhttp.send(params);
}

function export_manually_converted_leads(el) {

    let general_error_message = document.getElementById("general-error-message");
    general_error_message.style.color = "red";
    general_error_message.innerHTML = "";

    let selected_filter_value = document.getElementById("select-date-range").value;

    if (selected_filter_value == "0") {
        general_error_message.innerHTML = "Please select valid date range filter";
        return;
    }

    let startdate = $('#startdate').val();
    let enddate = $('#enddate').val();
    startdate = get_iso_formatted_date(startdate);
    enddate = get_iso_formatted_date(enddate);

    let email_field = document.getElementById('filter-data-email');

    var startdate_obj = new Date(startdate)
    var enddate_obj = new Date(enddate)
    var today_date = new Date()
    if (selected_filter_value == "4") {
        if (!startdate.length) {
            general_error_message.innerHTML = EMPTY_START_DATE_ERROR_TOAST;
            return;
        } else if (!enddate.length) {
            general_error_message.innerHTML = EMPTY_END_DATE_ERROR_TOAST;
            return;
        } else if (startdate_obj.getTime() > enddate_obj.getTime()) {
            general_error_message.innerHTML = "Start date cannot be greater than the end date";
            return;
        } else if (enddate_obj.getTime() > today_date.getTime()) {
            general_error_message.innerHTML = "End date cannot be past today's date";
            return;
        }
    }

    if (selected_filter_value == "4") {
        let email_value_list = email_field.value;
        email_value_list = email_value_list.split(",")
        if (email_value_list.length == 0) {
            general_error_message.innerHTML = "Please enter valid Email ID";
            return;
        }

        for (let index = 0; index < email_value_list.length; index++) {

            if (!regEmail.test(email_value_list[index])) {
                general_error_message.innerHTML = "Please enter valid Email ID";
                return;
            }
        }
    }

    el.innerHTML = "Exporting...";
    el.disabled = true;

    var json_string = JSON.stringify({
        "selected_filter_value": selected_filter_value,
        "startdate": startdate,
        "enddate": enddate,
        "email": email_field.value,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/export-manually-converted-leads-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path_exist"] && response["export_path"] != "None") {
                let export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else if (response.status == 300) {
                general_error_message.style.color = "green";
                general_error_message.innerHTML = "Your request has been recorded. You will get the Email in next 24 hrs.";
                setTimeout(function() {
                    $('#modal-mis-filter').modal('hide');
                }, 2000);
            } else if (response.status == 302 ) {
                show_easyassist_toast(response.message);
            } else {
                general_error_message.style.color = "red";
                general_error_message.innerHTML = "Unable to download support history";
            }
            el.innerHTML = "Export";
            el.disabled = false;
        }
    }
    xhttp.send(params);
}

function export_declined_leads(el) {

    let general_error_message = document.getElementById("general-error-message");
    general_error_message.style.color = "red";
    general_error_message.innerHTML = "";

    let selected_filter_value = document.getElementById("select-date-range").value;

    if (selected_filter_value == "0") {
        general_error_message.innerHTML = "Please select valid date range filter";
        return;
    }

    let startdate = $('#startdate').val();
    let enddate = $('#enddate').val();
    startdate = get_iso_formatted_date(startdate);
    enddate = get_iso_formatted_date(enddate);

    let email_field = document.getElementById('filter-data-email');

    var startdate_obj = new Date(startdate)
    var enddate_obj = new Date(enddate)
    var today_date = new Date()
    if (selected_filter_value == "4") {
        if (!startdate.length) {
            general_error_message.innerHTML = EMPTY_START_DATE_ERROR_TOAST;
            return;
        } else if (!enddate.length) {
            general_error_message.innerHTML = EMPTY_END_DATE_ERROR_TOAST;
            return;
        } else if (startdate_obj.getTime() > enddate_obj.getTime()) {
            general_error_message.innerHTML = "Start date cannot be greater than the end date";
            return;
        } else if (enddate_obj.getTime() > today_date.getTime()) {
            general_error_message.innerHTML = "End date cannot be past today's date";
            return;
        }
    }

    if (selected_filter_value == "4") {
        let email_value_list = email_field.value;
        email_value_list = email_value_list.split(",")
        if (email_value_list.length == 0) {
            general_error_message.innerHTML = "Please enter valid Email ID";
            return;
        }

        for (let index = 0; index < email_value_list.length; index++) {

            if (!regEmail.test(email_value_list[index])) {
                general_error_message.innerHTML = "Please enter valid Email ID";
                return;
            }
        }
    }

    el.innerHTML = "Exporting...";
    el.disabled = true;

    var json_string = JSON.stringify({
        "selected_filter_value": selected_filter_value,
        "startdate": startdate,
        "enddate": enddate,
        "email": email_field.value,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/export-declined-leads-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path_exist"] && response["export_path"] != "None") {
                let export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else if (response.status == 300) {
                general_error_message.style.color = "green";
                general_error_message.innerHTML = "Your request has been recorded. You will get the Email in next 24 hrs.";
                setTimeout(function() {
                    $('#modal-mis-filter').modal('hide');
                }, 2000);
            } else if (response.status == 302 ) {
                show_easyassist_toast(response.message);
            } else {
                general_error_message.style.color = "red";
                general_error_message.innerHTML = "Unable to download support history";
            }
            el.innerHTML = "Export";
            el.disabled = false;
        }
    }
    xhttp.send(params);
}


function export_followup_leads(el) {

    let general_error_message = document.getElementById("general-error-message");
    general_error_message.style.color = "red";
    general_error_message.innerHTML = "";

    let selected_filter_value = document.getElementById("select-date-range").value;

    if (selected_filter_value == "0") {
        general_error_message.innerHTML = "Please select valid date range filter";
        return;
    }

    let startdate = $('#startdate').val();
    let enddate = $('#enddate').val();
    startdate = get_iso_formatted_date(startdate);
    enddate = get_iso_formatted_date(enddate);

    let email_field = document.getElementById('filter-data-email');

    var startdate_obj = new Date(startdate)
    var enddate_obj = new Date(enddate)
    var today_date = new Date()
    if (selected_filter_value == "4") {
        if (!startdate.length) {
            general_error_message.innerHTML = EMPTY_START_DATE_ERROR_TOAST;
            return;
        } else if (!enddate.length) {
            general_error_message.innerHTML = EMPTY_END_DATE_ERROR_TOAST;
            return;
        } else if (startdate_obj.getTime() > enddate_obj.getTime()) {
            general_error_message.innerHTML = "Start date cannot be greater than the end date";
            return;
        } else if (enddate_obj.getTime() > today_date.getTime()) {
            general_error_message.innerHTML = "End date cannot be past today's date";
            return;
        }
    }

    if (selected_filter_value == "4") {
        let email_value_list = email_field.value;
        email_value_list = email_value_list.split(",")
        if (email_value_list.length == 0) {
            general_error_message.innerHTML = "Please enter valid Email ID";
            return;
        }

        for (let index = 0; index < email_value_list.length; index++) {

            if (!regEmail.test(email_value_list[index])) {
                general_error_message.innerHTML = "Please enter valid Email ID";
                return;
            }
        }
    }

    el.innerHTML = "Exporting...";
    el.disabled = true;

    var json_string = JSON.stringify({
        "selected_filter_value": selected_filter_value,
        "startdate": startdate,
        "enddate": enddate,
        "email": email_field.value,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/export-followup-leads-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path_exist"] && response["export_path"] != "None") {
                let export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else if (response.status == 300) {
                general_error_message.style.color = "green";
                general_error_message.innerHTML = "Your request has been recorded. You will get the Email in next 24 hrs.";
                setTimeout(function() {
                    $('#modal-mis-filter').modal('hide');
                }, 2000);
            } else if (response.status == 302 ) {
                show_easyassist_toast(response.message);
            } else {
                general_error_message.style.color = "red";
                general_error_message.innerHTML = "Unable to download support history";
            }
            el.innerHTML = "Export";
            el.disabled = false;
        }
    }
    xhttp.send(params);
}


function export_audit_trail(el) {

    let general_error_message = document.getElementById("general-error-message");
    general_error_message.style.color = "red";
    general_error_message.innerHTML = "";

    let selected_filter_value = document.getElementById("select-date-range").value;

    if (selected_filter_value == "0") {
        general_error_message.innerHTML = "Please select valid date range filter";
        return;
    }

    let startdate = $('#startdate').val();
    let enddate = $('#enddate').val();
    startdate = get_iso_formatted_date(startdate);
    enddate = get_iso_formatted_date(enddate);

    let email_field = document.getElementById('filter-data-email');

    var startdate_obj = new Date(startdate)
    var enddate_obj = new Date(enddate)
    var today_date = new Date()
    if (selected_filter_value == "4") {
        if (!startdate.length) {
            general_error_message.innerHTML = EMPTY_START_DATE_ERROR_TOAST;
            return;
        } else if (!enddate.length) {
            general_error_message.innerHTML = EMPTY_END_DATE_ERROR_TOAST;
            return;
        } else if (startdate_obj.getTime() > enddate_obj.getTime()) {
            general_error_message.innerHTML = "Start date cannot be greater than the end date";
            return;
        } else if (enddate_obj.getTime() > today_date.getTime()) {
            general_error_message.innerHTML = "End date cannot be past today's date";
            return;
        }
    }

    if (selected_filter_value == "4") {
        let email_value_list = email_field.value;
        email_value_list = email_value_list.split(",")
        if (email_value_list.length == 0) {
            general_error_message.innerHTML = "Please enter valid Email ID";
            return;
        }

        for (let index = 0; index < email_value_list.length; index++) {

            if (!regEmail.test(email_value_list[index])) {
                general_error_message.innerHTML = "Please enter valid Email ID";
                return;
            }
        }
    }

    el.innerHTML = "Exporting...";
    el.disabled = true;

    var json_string = JSON.stringify({
        "selected_filter_value": selected_filter_value,
        "startdate": startdate,
        "enddate": enddate,
        "email": email_field.value,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/export-audit-trail-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path_exist"] && response["export_path"] != "None") {
                let export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else if (response.status == 300) {
                general_error_message.style.color = "green";
                general_error_message.innerHTML = "Your request has been recorded. You will get the Email in next 24 hrs.";
                setTimeout(function() {
                    $('#modal-mis-filter').modal('hide');
                }, 2000);
            } else {
                general_error_message.style.color = "red";
                general_error_message.innerHTML = "Unable to download audit trail";
            }
            el.innerHTML = "Export";
            el.disabled = false;
        }
    }
    xhttp.send(params);
}

function export_agent_audit_trail(el) {

    let general_error_message = document.getElementById("general-error-message");
    general_error_message.style.color = "red";
    general_error_message.innerHTML = "";

    let selected_filter_value = document.getElementById("select-date-range").value;

    if (selected_filter_value == "0") {
        general_error_message.innerHTML = "Please select valid date range filter";
        return;
    }

    let startdate = $('#startdate').val();
    let enddate = $('#enddate').val();
    startdate = get_iso_formatted_date(startdate);
    enddate = get_iso_formatted_date(enddate);

    let email_field = document.getElementById('filter-data-email');

    var startdate_obj = new Date(startdate)
    var enddate_obj = new Date(enddate)
    var today_date = new Date()
    if (selected_filter_value == "4") {
        if (!startdate.length) {
            general_error_message.innerHTML = EMPTY_START_DATE_ERROR_TOAST;
            return;
        } else if (!enddate.length) {
            general_error_message.innerHTML = EMPTY_END_DATE_ERROR_TOAST;
            return;
        } else if (startdate_obj.getTime() > enddate_obj.getTime()) {
            general_error_message.innerHTML = "Start date cannot be greater than the end date";
            return;
        } else if (enddate_obj.getTime() > today_date.getTime()) {
            general_error_message.innerHTML = "End date cannot be past today's date";
            return;
        }
    }

    if (selected_filter_value == "4") {
        let email_value_list = email_field.value;
        email_value_list = email_value_list.split(",")
        if (email_value_list.length == 0) {
            general_error_message.innerHTML = "Please enter valid Email ID";
            return;
        }

        for (let index = 0; index < email_value_list.length; index++) {

            if (!regEmail.test(email_value_list[index])) {
                general_error_message.innerHTML = "Please enter valid Email ID";
                return;
            }
        }
    }

    el.innerHTML = "Exporting...";
    el.disabled = true;

    var json_string = JSON.stringify({
        "selected_filter_value": selected_filter_value,
        "startdate": startdate,
        "enddate": enddate,
        "email": email_field.value,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/export-agent-audit-trail-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path_exist"] && response["export_path"] != "None") {
                let export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else if (response.status == 300) {
                general_error_message.style.color = "green";
                general_error_message.innerHTML = "Your request has been recorded. You will get the Email in next 24 hrs.";
                setTimeout(function() {
                    $('#modal-mis-filter').modal('hide');
                }, 2000);
            } else {
                general_error_message.style.color = "red";
                general_error_message.innerHTML = "Unable to download agent audit trail";
            }
            el.innerHTML = "Export";
            el.disabled = false;
        }
    }
    xhttp.send(params);
}

function export_agent_online_audit_trail(el) {

    let general_error_message = document.getElementById("general-error-message");
    general_error_message.style.color = "red";
    general_error_message.innerHTML = "";

    let selected_filter_value = document.getElementById("select-date-range").value;

    if (selected_filter_value == "0") {
        general_error_message.innerHTML = "Please select valid date range filter";
        return;
    }

    let startdate = $('#startdate').val();
    let enddate = $('#enddate').val();
    startdate = get_iso_formatted_date(startdate);
    enddate = get_iso_formatted_date(enddate);

    let email_field = document.getElementById('filter-data-email');

    var startdate_obj = new Date(startdate)
    var enddate_obj = new Date(enddate)
    var today_date = new Date()
    if (selected_filter_value == "4") {
        if (!startdate.length) {
            general_error_message.innerHTML = EMPTY_START_DATE_ERROR_TOAST;
            return;
        } else if (!enddate.length) {
            general_error_message.innerHTML = EMPTY_END_DATE_ERROR_TOAST;
            return;
        } else if (startdate_obj.getTime() > enddate_obj.getTime()) {
            general_error_message.innerHTML = "Start date cannot be greater than the end date";
            return;
        } else if (enddate_obj.getTime() > today_date.getTime()) {
            general_error_message.innerHTML = "End date cannot be past today's date";
            return;
        }
    }

    if (selected_filter_value == "4") {
        let email_value_list = email_field.value;
        email_value_list = email_value_list.split(",")
        if (email_value_list.length == 0) {
            general_error_message.innerHTML = "Please enter valid Email ID";
            return;
        }

        for (let index = 0; index < email_value_list.length; index++) {

            if (!regEmail.test(email_value_list[index])) {
                general_error_message.innerHTML = "Please enter valid Email ID";
                return;
            }
        }
    }

    el.innerHTML = "Exporting...";
    el.disabled = true;

    var json_string = JSON.stringify({
        "selected_filter_value": selected_filter_value,
        "startdate": startdate,
        "enddate": enddate,
        "email": email_field.value,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/export-agent-online-audit-trail-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path_exist"] && response["export_path"] != "None") {
                let export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else if (response.status == 300) {
                general_error_message.style.color = "green";
                general_error_message.innerHTML = "Your request has been recorded. You will get the Email in next 24 hrs.";
                setTimeout(function() {
                    $('#modal-mis-filter').modal('hide');
                }, 2000);
            } else {
                general_error_message.style.color = "red";
                general_error_message.innerHTML = "Unable to download agent online audit trail";
            }
            el.innerHTML = "Export";
            el.disabled = false;
        }
    }
    xhttp.send(params);
}

function download_meeting_recording(meeting_id) {

    var json_string = JSON.stringify({
        "meeting_id": meeting_id
    });

    var encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/download-meeting-recording/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                if (response.file_id == undefined) {
                    show_easyassist_toast("Recording will be available after 24 hours");
                } else {
                    window.open(window.location.origin + '/easy-assist/download-file/' + response.file_id)
                }
            } else if (response.status == 301) {
                show_easyassist_toast("Recording will be available after 24 hours");
            }
        }
    }
    xhttp.send(params);
}

function export_meeting_support_history(el) {

    let general_error_message = document.getElementById("general-error-message");
    general_error_message.style.color = "red";
    general_error_message.innerHTML = "";

    let selected_filter_value = document.getElementById("select-date-range").value;

    if (selected_filter_value == "0") {
        general_error_message.innerHTML = "Please select valid date range filter";
        return;
    }

    let startdate = $('#startdate').val();
    let enddate = $('#enddate').val();
    startdate = get_iso_formatted_date(startdate);
    enddate = get_iso_formatted_date(enddate);

    let email_field = document.getElementById('filter-data-email');

    var startdate_obj = new Date(startdate);
    var enddate_obj = new Date(enddate);
    var today_date = new Date();
    if (selected_filter_value == "4") {
        if (!startdate.length) {
            general_error_message.innerHTML = EMPTY_START_DATE_ERROR_TOAST;
            return;
        } else if (!enddate.length) {
            general_error_message.innerHTML = EMPTY_END_DATE_ERROR_TOAST;
            return;
        } else if (startdate_obj.getTime() > enddate_obj.getTime()) {
            general_error_message.innerHTML = "Start date cannot be greater than the end date";
            return;
        } else if (enddate_obj.getTime() > today_date.getTime()) {
            general_error_message.innerHTML = "End date cannot be past today's date";
            return;
        }
    }

    if (selected_filter_value == "4") {
        let email_value_list = email_field.value;
        email_value_list = email_value_list.split(",")
        if (email_value_list.length == 0) {
            general_error_message.innerHTML = "Please enter valid Email ID";
            return;
        }

        for (let index = 0; index < email_value_list.length; index++) {

            if (!regEmail.test(email_value_list[index])) {
                general_error_message.innerHTML = "Please enter valid Email ID";
                return;
            }
        }
    }

    el.innerHTML = "Exporting...";
    el.disabled = false;

    var json_string = JSON.stringify({
        "selected_filter_value": selected_filter_value,
        "startdate": startdate,
        "enddate": enddate,
        "email": email_field.value,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/export-meeting-support-history/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path"] != null) {
                let export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else if (response.status == 300) {
                general_error_message.style.color = "green";
                general_error_message.innerHTML = "Your request has been recorded. You will get the Email in next 24 hrs.";
                setTimeout(function() {
                    $('#modal-mis-filter').modal('hide');
                }, 2000);
            } else if (response.status == 302 ) {
                show_easyassist_toast(response.message);
            } else {
                show_easyassist_toast("Unable to download meeting support history");
            }
            el.innerHTML = "Export";
            el.disabled = false;
        }
    }
    xhttp.send(params);
}

function export_screen_recording_history(el) {

    let general_error_message = document.getElementById("general-error-message");
    general_error_message.style.color = "red";
    general_error_message.innerHTML = "";

    let selected_filter_value = document.getElementById("select-date-range").value;

    if (selected_filter_value == "0") {
        general_error_message.innerHTML = "Please select valid date range filter";
        return;
    }

    let startdate = $('#startdate').val();
    let enddate = $('#enddate').val();
    startdate = get_iso_formatted_date(startdate);
    enddate = get_iso_formatted_date(enddate);

    let email_field = document.getElementById('filter-data-email');

    var startdate_obj = new Date(startdate);
    var enddate_obj = new Date(enddate);
    var today_date = new Date();
    if (selected_filter_value == "4") {
        if (!startdate.length) {
            general_error_message.innerHTML = EMPTY_START_DATE_ERROR_TOAST;
            return;
        } else if (!enddate.length) {
            general_error_message.innerHTML = EMPTY_END_DATE_ERROR_TOAST;
            return;
        } else if (startdate_obj.getTime() > enddate_obj.getTime()) {
            general_error_message.innerHTML = "Start date cannot be greater than the end date";
            return;
        } else if (enddate_obj.getTime() > today_date.getTime()) {
            general_error_message.innerHTML = "End date cannot be past today's date";
            return;
        }
    }

    if (selected_filter_value == "4") {
        let email_value_list = email_field.value;
        email_value_list = email_value_list.split(",")
        if (email_value_list.length == 0) {
            general_error_message.innerHTML = "Please enter valid Email ID";
            return;
        }

        for (let index = 0; index < email_value_list.length; index++) {

            if (!regEmail.test(email_value_list[index])) {
                general_error_message.innerHTML = "Please enter valid Email ID";
                return;
            }
        }
    }

    el.innerHTML = "Exporting...";
    el.disabled = false;

    var json_string = JSON.stringify({
        "selected_filter_value": selected_filter_value,
        "startdate": startdate,
        "enddate": enddate,
        "email": email_field.value,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/export-screen-recording-history/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path"] != null) {
                let export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else if (response.status == 300) {
                general_error_message.style.color = "green";
                general_error_message.innerHTML = "Your request has been recorded. You will get the Email in next 24 hrs.";
                setTimeout(function() {
                    $('#modal-mis-filter').modal('hide');
                }, 2000);
            } else {
                show_easyassist_toast("Unable to download screen recording history");
            }
            el.innerHTML = "Export";
            el.disabled = false;
        }
    }
    xhttp.send(params);
}

function export_inbound_analytics(el) {

    let general_error_message = document.getElementById("general-error-message");
    general_error_message.style.color = "red";
    general_error_message.innerHTML = "";

    let selected_filter_value = document.getElementById("select-date-range").value;

    if (selected_filter_value == "0") {
        general_error_message.innerHTML = "Please select valid date range filter";
        return;
    }

    let startdate = $('#startdate').val();
    let enddate = $('#enddate').val();
    startdate = get_iso_formatted_date(startdate);
    enddate = get_iso_formatted_date(enddate);
    
    let email_field = document.getElementById('filter-data-email');

    var startdate_obj = new Date(startdate);
    var enddate_obj = new Date(enddate);
    var today_date = new Date();
    if (selected_filter_value == "4") {
        if (!startdate.length) {
            general_error_message.innerHTML = EMPTY_START_DATE_ERROR_TOAST;
            return;
        } else if (!enddate.length) {
            general_error_message.innerHTML = EMPTY_END_DATE_ERROR_TOAST;
            return;
        } else if (startdate_obj.getTime() > enddate_obj.getTime()) {
            general_error_message.innerHTML = "Start date cannot be greater than the end date";
            return;
        } else if (enddate_obj.getTime() > today_date.getTime()) {
            general_error_message.innerHTML = "From Date and To Date cannot be a future date.";
            return;
        } else if(startdate_obj.toLocaleDateString() == today_date.toLocaleDateString()) {
            general_error_message.innerHTML =  "Start date " + TODAY_DATE_ERROR_TOAST;
            return;
        } else if (enddate_obj.toLocaleDateString() == today_date.toLocaleDateString()) {
            general_error_message.innerHTML =  "End date " + TODAY_DATE_ERROR_TOAST;
            return;
        }
    }

    if (selected_filter_value == "4") {
        let email_value_list = email_field.value;
        email_value_list = email_value_list.split(",")
        if (email_value_list.length == 0) {
            general_error_message.innerHTML = "Please enter valid Email ID";
            return;
        }

        for (let index = 0; index < email_value_list.length; index++) {

            if (!regEmail.test(email_value_list[index])) {
                general_error_message.innerHTML = "Please enter valid Email ID";
                return;
            }
        }
    }

    el.innerHTML = "Exporting...";
    el.disabled = false;

    var json_string = JSON.stringify({
        "selected_filter_value": selected_filter_value,
        "startdate": startdate,
        "enddate": enddate,
        "email": email_field.value,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/export-inbound-analytics/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
       
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            
            if (response.status == 200 && response["export_path"] != null) {
                let export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else if (response.status == 300) {
                general_error_message.style.color = "green";
                general_error_message.innerHTML = "Your request has been recorded. You will get the Email in next 24 hrs.";
                setTimeout(function() {
                    $('#modal-mis-filter').modal('hide');
                }, 2000);
            } else {
                show_easyassist_toast("Unable to download inbound analytics");
            }
            el.innerHTML = "Export";
            el.disabled = false;
        }
    }
    xhttp.send(params);
}

function export_outbound_search_lead_analytics(el) {

    let general_error_message = document.getElementById("general-error-message");
    general_error_message.style.color = "red";
    general_error_message.innerHTML = "";

    let selected_filter_value = document.getElementById("select-date-range").value;

    if (selected_filter_value == "0") {
        general_error_message.innerHTML = "Please select valid date range filter";
        return;
    }

    let startdate = $('#startdate').val();
    let enddate = $('#enddate').val();
    startdate = get_iso_formatted_date(startdate);
    enddate = get_iso_formatted_date(enddate);

    let email_field = document.getElementById('filter-data-email');

    var startdate_obj = new Date(startdate);
    var enddate_obj = new Date(enddate);
    var today_date = new Date();
    if (selected_filter_value == "4") {
        if (!startdate.length) {
            general_error_message.innerHTML = EMPTY_START_DATE_ERROR_TOAST;
            return;
        } else if (!enddate.length) {
            general_error_message.innerHTML = EMPTY_END_DATE_ERROR_TOAST;
            return;
        } else if (startdate_obj.getTime() > enddate_obj.getTime()) {
            general_error_message.innerHTML = "Start date cannot be greater than the end date";
            return;
        } else if (enddate_obj.getTime() > today_date.getTime()) {
            general_error_message.innerHTML = "From Date and To Date cannot be a future date.";
            return;
        } else if(startdate_obj.toLocaleDateString() == today_date.toLocaleDateString()) {
            general_error_message.innerHTML =  "Start date " + TODAY_DATE_ERROR_TOAST;
            return;
        } else if (enddate_obj.toLocaleDateString() == today_date.toLocaleDateString()) {
            general_error_message.innerHTML =  "End date " + TODAY_DATE_ERROR_TOAST;
            return;
        }
    }

    if (selected_filter_value == "4") {
        let email_value_list = email_field.value;
        email_value_list = email_value_list.split(",")
        if (email_value_list.length == 0) {
            general_error_message.innerHTML = "Please enter valid Email ID";
            return;
        }

        for (let index = 0; index < email_value_list.length; index++) {

            if (!regEmail.test(email_value_list[index])) {
                general_error_message.innerHTML = "Please enter valid Email ID";
                return;
            }
        }
    }

    el.innerHTML = "Exporting...";
    el.disabled = false;

    var json_string = JSON.stringify({
        "selected_filter_value": selected_filter_value,
        "startdate": startdate,
        "enddate": enddate,
        "email": email_field.value,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/export-outbound-analytics/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path"] != null) {
                let export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else if (response.status == 300) {
                general_error_message.style.color = "green";
                general_error_message.innerHTML = "Your request has been recorded. You will get the Email in next 24 hrs.";
                setTimeout(function() {
                    $('#modal-mis-filter').modal('hide');
                }, 2000);
            } else {
                show_easyassist_toast("Unable to download outbound analytics");
            }
            el.innerHTML = "Export";
            el.disabled = false;
        }
    }
    xhttp.send(params);
}

function export_reverse_analytics(el) {

    let general_error_message = document.getElementById("general-error-message");
    general_error_message.style.color = "red";
    general_error_message.innerHTML = "";

    let selected_filter_value = document.getElementById("select-date-range").value;

    if (selected_filter_value == "0") {
        general_error_message.innerHTML = "Please select valid date range filter";
        return;
    }

    let startdate = $('#startdate').val();
    let enddate = $('#enddate').val();
    startdate = get_iso_formatted_date(startdate);
    enddate = get_iso_formatted_date(enddate);

    let email_field = document.getElementById('filter-data-email');

    var startdate_obj = new Date(startdate);
    var enddate_obj = new Date(enddate);
    var today_date = new Date();
    if (selected_filter_value == "4") {
        if (!startdate.length) {
            general_error_message.innerHTML = EMPTY_START_DATE_ERROR_TOAST;
            return;
        } else if (!enddate.length) {
            general_error_message.innerHTML = EMPTY_END_DATE_ERROR_TOAST;
            return;
        } else if (startdate_obj.getTime() > enddate_obj.getTime()) {
            general_error_message.innerHTML = "Start date cannot be greater than the end date";
            return;
        } else if (enddate_obj.getTime() > today_date.getTime()) {
            general_error_message.innerHTML = "From Date and To Date cannot be a future date.";
            return;
        } else if(startdate_obj.toLocaleDateString() == today_date.toLocaleDateString()) {
            general_error_message.innerHTML =  "Start date " + TODAY_DATE_ERROR_TOAST;
            return;
        } else if (enddate_obj.toLocaleDateString() == today_date.toLocaleDateString()) {
            general_error_message.innerHTML =  "End date " + TODAY_DATE_ERROR_TOAST;
            return;
        }
    }

    if (selected_filter_value == "4") {
        let email_value_list = email_field.value;
        email_value_list = email_value_list.split(",")
        if (email_value_list.length == 0) {
            general_error_message.innerHTML = "Please enter valid Email ID";
            return;
        }

        for (let index = 0; index < email_value_list.length; index++) {

            if (!regEmail.test(email_value_list[index])) {
                general_error_message.innerHTML = "Please enter valid Email ID";
                return;
            }
        }
    }

    el.innerHTML = "Exporting...";
    el.disabled = false;

    var json_string = JSON.stringify({
        "selected_filter_value": selected_filter_value,
        "startdate": startdate,
        "enddate": enddate,
        "email": email_field.value,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/export-reverse-analytics/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path"] != null) {
                let export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else if (response.status == 300) {
                general_error_message.style.color = "green";
                general_error_message.innerHTML = "Your request has been recorded. You will get the Email in next 24 hrs.";
                setTimeout(function() {
                    $('#modal-mis-filter').modal('hide');
                }, 2000);
            } else {
                show_easyassist_toast("Unable to download reverse analytics");
            }
            el.innerHTML = "Export";
            el.disabled = false;
        }
    }
    xhttp.send(params);
}

function export_general_analytics(el) {

    let general_error_message = document.getElementById("general-error-message");
    general_error_message.style.color = "red";
    general_error_message.innerHTML = "";

    let selected_filter_value = document.getElementById("select-date-range").value;

    if (selected_filter_value == "0") {
        general_error_message.innerHTML = "Please select valid date range filter";
        return;
    }

    let startdate = $('#startdate').val();
    let enddate = $('#enddate').val();
    startdate = get_iso_formatted_date(startdate);
    enddate = get_iso_formatted_date(enddate);

    let email_field = document.getElementById('filter-data-email');

    var startdate_obj = new Date(startdate);
    var enddate_obj = new Date(enddate);
    var today_date = new Date();
    if (selected_filter_value == "4") {
        if (!startdate.length) {
            general_error_message.innerHTML = EMPTY_START_DATE_ERROR_TOAST;
            return;
        } else if (!enddate.length) {
            general_error_message.innerHTML = EMPTY_END_DATE_ERROR_TOAST;
            return;
        } else if (startdate_obj.getTime() > enddate_obj.getTime()) {
            general_error_message.innerHTML = "Start date cannot be greater than the end date";
            return;
        } else if (enddate_obj.getTime() > today_date.getTime()) {
            general_error_message.innerHTML = "From Date and To Date cannot be a future date.";
            return;
        } else if(startdate_obj.toLocaleDateString() == today_date.toLocaleDateString()) {
            general_error_message.innerHTML =  "Start date " + TODAY_DATE_ERROR_TOAST;
            return;
        } else if (enddate_obj.toLocaleDateString() == today_date.toLocaleDateString()) {
            general_error_message.innerHTML =  "End date " + TODAY_DATE_ERROR_TOAST;
            return;
        }
    }

    if (selected_filter_value == "4") {
        let email_value_list = email_field.value;
        email_value_list = email_value_list.split(",")
        if (email_value_list.length == 0) {
            general_error_message.innerHTML = "Please enter valid Email ID";
            return;
        }

        for (let index = 0; index < email_value_list.length; index++) {

            if (!regEmail.test(email_value_list[index])) {
                general_error_message.innerHTML = "Please enter valid Email ID";
                return;
            }
        }
    }

    el.innerHTML = "Exporting...";
    el.disabled = false;

    var json_string = JSON.stringify({
        "selected_filter_value": selected_filter_value,
        "startdate": startdate,
        "enddate": enddate,
        "email": email_field.value,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/export-general-analytics/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path"] != null) {
                let export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else if (response.status == 300) {
                general_error_message.style.color = "green";
                general_error_message.innerHTML = "Your request has been recorded. You will get the Email in next 24 hrs.";
                setTimeout(function() {
                    $('#modal-mis-filter').modal('hide');
                }, 2000);
            } else {
                show_easyassist_toast("Unable to download general analytics");
            }
            el.innerHTML = "Export";
            el.disabled = false;
        }
    }
    xhttp.send(params);
}

$("#user_details_upload_modal").on("hidden.bs.modal", function() {
    remove_uploaded_file();
});

var support_file_upload_data_list = [];
var support_file_upload_total_count = 0;
var support_file_read_completed_count = 0;
var support_file_reading_index = 0;
var customer_support_file_save_request_interval;
var read_files_customer_support_interval;

function customer_support_file_save_request() {
    if (support_file_read_completed_count == support_file_upload_total_count) {
        clearInterval(customer_support_file_save_request_interval)
        let json_string = JSON.stringify(support_file_upload_data_list);

        let encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/upload-customer-support-files/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                let response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);
                let customer_support_file_upload_error = document.getElementById("customer-support-file-upload-error");
                if (response["status"] == 200) {
                    if (response["file_upload_fail"].length > 0) {
                        customer_support_file_upload_error.innerHTML = "";
                        if (response["file_upload_success"].length > 0) {
                            customer_support_file_upload_error.innerHTML += "Successfully Uploaded";
                            customer_support_file_upload_error.style.color = "red";
                            for (let index_success = 0; index_success < response["file_upload_success"].length; index_success++) {
                                customer_support_file_upload_error.innerHTML += "<br>" + response["file_upload_success"][index_success]
                            }
                        }
                        customer_support_file_upload_error.innerHTML += "<br><b>Not Uploaded</b>";
                        for (let index_success = 0; index_success < response["file_upload_fail"].length; index_success++) {
                            customer_support_file_upload_error.style.color = "red";
                            if (response["file_upload_fail"][index_success].error == "unsupported_file_format") {
                                customer_support_file_upload_error.innerHTML += "<br>" + response["file_upload_fail"][index_success].file_name + " - Unsupported file format";
                            } else if (response["file_upload_fail"][index_success].error == "file_already_exist") {
                                customer_support_file_upload_error.innerHTML += "<br>" + response["file_upload_fail"][index_success].file_name + " - File with same name already exist";
                            } else {
                                customer_support_file_upload_error.innerHTML += "<br>" + response["file_upload_fail"][index_success].file_name + " - Server error";
                            }
                        }
                    } else {
                        customer_support_file_upload_error.innerHTML = "Files uploaded successfully";
                        setTimeout(function() {
                            $('#customer_support_document_modal').modal('toggle');
                            location.reload();
                        }, 1000);
                    }
                    $("#customer-support-file-upload").val("");
                } else {
                    customer_support_file_upload_error.style.color = "red";
                    customer_support_file_upload_error.innerHTML = "File Not Uploaded"
                    $("#customer-support-file-upload").val("");
                }
            }
        }
        xhttp.send(params);
    }
}

function read_files_customer_support() {

    if (support_file_read_completed_count == support_file_upload_total_count) {
        clearInterval(read_files_customer_support_interval);
        return;
    }

    if (support_file_reading_index == support_file_read_completed_count) {
        var input_uploaded_files = customer_support_input_file_global;
        var file = input_uploaded_files[support_file_reading_index];

        var reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = function() {

            let base64_str = reader.result.split(",")[1];
            let filename = sanitize_filename(file.name);
            
            support_file_upload_data_list.push({
                "filename": filename,
                "base64_file": base64_str,
            });
            support_file_read_completed_count++;
        };

        reader.onerror = function(error) {
            console.log('Error: ', error);
            support_file_read_completed_count++;
        };

        support_file_reading_index++;
    }

}

function upload_selected_customer_support_document() {

    let customer_support_file_upload_error = document.getElementById("customer-support-file-upload-error");
    customer_support_file_upload_error.innerHTML = ""
    customer_support_file_upload_error.style.color = "green";
    customer_support_file_upload_error.innerHTML = "<br>Uploading..."

    let input_uploaded_files = customer_support_input_file_global;

    if (input_uploaded_files == undefined || input_uploaded_files.length == 0) {
        customer_support_file_upload_error.style.color = "red";
        customer_support_file_upload_error.innerHTML = "Please select file to upload"
        return;
    }

    if (input_uploaded_files.length > 5) {
        customer_support_file_upload_error.style.color = "red";
        customer_support_file_upload_error.innerHTML = "Maximum 5 files can be uploaded at a time"
        return;
    }

    let file_name = '';
    let file_check = false;
    $.each(input_uploaded_files, function(index, file) {
        file_name = file.name;
        file_check = check_file_extension(file_name);
        if (file_check == false) {
            customer_support_file_upload_error.style.color = "red";
            customer_support_file_upload_error.innerHTML = "You can only upload Images, Docs, and PDFs. Please choose the files again.";
            return;
        }
        var malicious_file_report = check_malicious_file(file_name)
        if (malicious_file_report.status == true) {
            customer_support_file_upload_error.style.color = "red";
            customer_support_file_upload_error.innerHTML = malicious_file_report.message
            file_check = false;
            return;
        }
        if (file.size / 1000000 > 5) {
            file_check = false;
            customer_support_file_upload_error.style.color = "red";
            customer_support_file_upload_error.innerHTML = "File size cannot exceed 5 MB";
            return;
        }
        var filename = sanitize_filename(file.name);
        filename = filename.substring(0, filename.lastIndexOf("."));
        if (!filename.length) {
            file_check = false;
            customer_support_file_upload_error.style.color = "red";
            customer_support_file_upload_error.innerHTML = "File name can only consist of alphabets, numbers and underscores";
            return;
        }
    });
    if (file_check == false) return;

    support_file_upload_data_list = []
    support_file_upload_total_count = customer_support_input_file_global.length
    support_file_read_completed_count = 0;
    support_file_reading_index = 0;

    read_files_customer_support_interval = setInterval(read_files_customer_support, 500);
    customer_support_file_save_request_interval = setInterval(customer_support_file_save_request, 3000)
}

function delete_customer_support_document_details(element, support_document_id) {

    var request_params = {
        "support_document_id": support_document_id,
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    element.innerText = "Deleting...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/sales-ai/delete-support-document/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status == 200) {
                element.innerText = "Delete";
                $("#delete-support-document-modal-" + support_document_id).modal("hide");
                setTimeout(function() {
                    window.location.reload()
                }, 1000);
            } else if (response.status == 301) {
                show_easyassist_toast("Unable to delete document. Please try again.");
            }
        }
    }
    xhttp.send(params);
}

function save_customer_support_document_details(delete_document = false) {
    let user_checkbox_collection_usable = document.getElementsByClassName("user-checkbox-collection-usable");
    let user_checkbox_collection_filename = document.getElementsByClassName("user-checkbox-collection-filename");
    let customer_support_document_update_dict = {};
    let all_files_valid = true;

    for (let index = 0; index < user_checkbox_collection_usable.length; index++) {

        let user_input = {};

        if (user_checkbox_collection_usable[index].checked) {
            user_input["is_usable"] = 1;
        } else {
            user_input["is_usable"] = 0;
        }

        let file_name = user_checkbox_collection_filename[index].value;
        file_name = file_name.trim();
        
        if(!file_name.length) {
            show_easyassist_toast("Please enter file name to continue");
            return;
        }

        if(file_name.lastIndexOf(".") == -1) {
            show_easyassist_toast("File extension is missing in " + file_name);
            return;
        }

        let file_extension_check = check_file_extension(file_name);

        if (!file_extension_check) {
            show_easyassist_toast("File extension is invalid in " + file_name +". Only .png .jpg .jpeg .pdf .doc and .docx are allowed");
            return;
        }

        file_name = file_name.substring(0, file_name.lastIndexOf(".")).trim();

        if(file_name.indexOf('.') != file_name.lastIndexOf('.')) {
            show_easyassist_toast("Please do not use dot(.) in file name");
            return;
        }

        if(check_file_name(user_checkbox_collection_filename[index].value)) {
            show_easyassist_toast(file_name + " is invalid file name. Only A-Z, a-z, 0-9, - and _ are allowed");
            return;
        }

        let uploaded_file_name = sanitize_filename(user_checkbox_collection_filename[index].value);
        if(uploaded_file_name.trim().length == 0) {
            all_files_valid = false;
            break;
        }
        user_input["file_name"] = uploaded_file_name;

        customer_support_document_update_dict[user_checkbox_collection_usable[index].id] = user_input;
    }

    if(all_files_valid == false) {
        show_easyassist_toast("Please enter valid file name");
        return;
    }

    let json_string = JSON.stringify(customer_support_document_update_dict);

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/update-support-document-detail/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                show_easyassist_toast("Saved successfully")
            } else if (response["status"] == 302) {
                show_easyassist_toast(response.message);
            } else {
                show_easyassist_toast("Something went wrong!");
            }
        }
    }
    xhttp.send(params);
}

function save_customer_support_document_preference() {
    var user_checkbox_collection_usable = document.getElementsByClassName("user-checkbox-collection-usable");
    var user_checkbox_collection_filename = document.getElementsByClassName("user-checkbox-collection-filename");
    var customer_support_document_update_dict = {};

    for (let index = 0; index < user_checkbox_collection_usable.length; index++) {

        var user_input = {};

        if (user_checkbox_collection_usable[index].checked) {
            user_input["is_usable"] = 1;
        } else {
            user_input["is_usable"] = 0;
        }

        user_input["file_name"] = user_checkbox_collection_filename[index].value

        customer_support_document_update_dict[user_checkbox_collection_usable[index].id] = user_input;
    }

    var json_string = JSON.stringify(customer_support_document_update_dict);

    var encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/update-support-document-detail/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                location.reload();
            } else {
                show_easyassist_toast("Something went wrong!!");
            }
        }
    }
    xhttp.send(params);
}

function meeting_time_format(time) {
    try{
        var regex = /^\d\d?:\d\d?[AP]{1}[M]{1}$/;
        if(!regex.test(time)){
            return null;
        }
        var PM = time.match('PM') ? true : false

        time = time.split(':')
        if (PM) {
            var hour, min;
            if (time[0] < 12) {
                hour = 12 + parseInt(time[0], 10)
                min = time[1].replace('PM', '')
            } else {
                hour = 12
                min = time[1].replace('PM', '')
            }
        } else {
            hour = time[0]
            if (hour < 12) {
                min = time[1].replace('AM', '')
            } else {
                hour = "00"
                min = time[1].replace('AM', '')
            }
        }

        if(hour.length == 1){
            hour = "0" + hour;
        }
        if(min.length == 1){
            min = "0" + min;
        }

        return hour + ':' + min;
    }catch(err){
        console.log("Error meeting_time_format : ", err);
        return null;
    }
}

function meeting_time_input_validate(event) {
    var keyCode = event.which;
    var target = event.target;
    var value = target.value;

    event.target.value = event.target.value.toUpperCase();

    if(value.length == 7){
        return false;
    }

    var allowed_characters = [65, 77, 80, 97, 109, 112];
    if(allowed_characters.indexOf(keyCode) >= 0){
        return true;
    }

    if( keyCode == 58 ) {
        if(value == "" || value.indexOf(":") >= 0){
            return false;
        }
        return true;
    }

    if ( (keyCode != 8 || keyCode == 32 ) && (keyCode < 48 || keyCode > 57)) { 
        return false;
    }
    return true;
}

function generate_sharable_link(element,meet_type=null) {

    let error_message_element = document.getElementById("generate-link-details-error");
    error_message_element.innerHTML = "";

    let full_name = document.getElementById("client-full-name").value;
    let mobile_number = document.getElementById("client-modile-number").value;
    let email = document.getElementById("client-email-id").value;

    const regName = /^[a-zA-Z ]+$/;
    const regMob = /^[6-9]{1}\d{9}$/;

    if (email != "") {
        if (!regEmail.test(email)) {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Please enter valid Email ID.";
            return;
        }

        if(email.length > 50) {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Email ID should not be more than 50 characters.";
            return;
        }
    }


    if (!regName.test(full_name)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter Full Name";
        return;
    }

    if (!regMob.test(mobile_number)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid 10-digit mobile number";
        return;
    }

    let meeting_description = document.getElementById("client-meeting-description").value;
    meeting_description = stripHTML(meeting_description);
    meeting_description = remove_special_characters_from_str(meeting_description);
    if (meeting_description == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter the meeting description.";
        return;
    }

    let meeting_start_date = document.getElementById("client-meeting-start-date").value;
    if (meeting_start_date == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter the meeting date.";
        return;
    }

    meeting_start_date = get_iso_formatted_date(meeting_start_date);
    let meet_date_year = meeting_start_date.split("-")[0]
    let meet_date_month = meeting_start_date.split("-")[1]
    let meet_date_date = meeting_start_date.split("-")[2]

    if (meet_date_year < new Date().getFullYear()) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid meeting date.";
        return;
    } else if (meet_date_year == new Date().getFullYear() && meet_date_month < (new Date().getMonth() + 1)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid meeting date."
        return;
    } else if (meet_date_year == new Date().getFullYear() && meet_date_month == (new Date().getMonth() + 1) && meet_date_date < new Date().getDate()) {
        error_message_element.innerHTML = "Please enter a valid meeting date.";
        error_message_element.style.color = "red";
        return;
    }

    var current_time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });

    let meeting_start_time = document.getElementById("client-meeting-start-time").value;
    if (meeting_start_time == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter the start time.";
        return;
    }

    meeting_start_time = meeting_time_format(meeting_start_time)

    if(meeting_start_time == null){
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter start time in valid format.";
        return;
    }

    if (meeting_start_time < current_time) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "You have entered a time in the past. Please enter a valid start time.";
        return;
    }

    if (meeting_start_time.substr(3) > 59) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid start time.";
        return;
    }

    let meeting_end_time = document.getElementById("client-meeting-end-time").value;
    if (meeting_end_time == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter the end time.";
        return;
    }
    meeting_end_time = meeting_time_format(meeting_end_time)

    if(meeting_end_time == null){
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter end time in valid format.";
        return;
    }

    if (meeting_end_time.substr(3) > 59) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid end time.";
        return;
    }

    if (meeting_end_time < current_time) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "You have entered a time in the past. Please enter a valid end time.";
        return;
    }

    if (meeting_start_time >= meeting_end_time) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Start time should be less than end time.";
        return;
    }
    let meeting_password = document.getElementById("client-meeting-password").value;

    let dyte_access_token = null
    if(window.COGNOMEET_ACCESS_TOKEN != undefined && window.COGNOMEET_ACCESS_TOKEN != null){
        dyte_access_token = COGNOMEET_ACCESS_TOKEN;
    }

    let request_params = {
        "full_name": full_name,
        "mobile_number": mobile_number,
        "meeting_description": meeting_description,
        "meeting_start_date": meeting_start_date,
        "meeting_end_time": meeting_end_time,
        "meeting_start_time": meeting_start_time,
        "meeting_password": meeting_password,
        "email": email,
        "dyte_access_token": dyte_access_token
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    if(meet_type == 'dyte'){
        generate_dyte_meet(element, encrypted_data);
    }
    else{
        generate_jitsi_meet(element, encrypted_data);
    }    
}

function generate_jitsi_meet(element, encrypted_data){

    let error_message_element = document.getElementById("generate-link-details-error");
    error_message_element.innerHTML = "";

    var params = JSON.stringify(encrypted_data);
    element.innerHTML = "Generating...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/generate-video-meeting/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                let video_link = response["video_link"];
                document.getElementById("video-conferencing-link").value = video_link;
                document.getElementById("product-page-url").setAttribute("cobrowse-session", response["session_id"]);
                show_video_conferencing_details();
                generate_cobrowsing_link();
                element.style.display = "none";
                element.parentElement.children[0].innerHTML = 'OK';
                document.getElementById("schedule-meeting-text").style.display = "none";
            } else {
                error_message_element.innerHTML = "Unable to generate video meeting link";
            }
        }
    }

    xhttp.send(params);
}

function generate_dyte_meet(element, encrypted_data){

    let error_message_element = document.getElementById("generate-link-details-error");
    error_message_element.innerHTML = "";

    console.log('Dyte meet denerated', encrypted_data);
    var params = JSON.stringify(encrypted_data);
    element.innerHTML = "Generating...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/cogno-meet/generate-meeting/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                let video_link = response["video_link"];
                document.getElementById("video-conferencing-link").value = video_link;
                document.getElementById("product-page-url").setAttribute("cobrowse-session", response["session_id"]);
                show_video_conferencing_details();
                generate_cobrowsing_link();
                element.style.display = "none";
                element.parentElement.children[0].innerHTML = 'OK';
                document.getElementById("schedule-meeting-text").style.display = "none";
            } else if(response["status"] == 504){
                error_message_element.innerHTML = "Due to a technical issue we were not able to schedule the meeting, please try again after sometime";
            } else {
                error_message_element.innerHTML = "Unable to generate video meeting link";
            }
        }
    }

    xhttp.send(params);

}


function save_meeting_link(element, meeting_id) {

    let error_message_element = document.getElementById("generate-link-details-error-" + meeting_id);
    error_message_element.innerHTML = "";

    let full_name = document.getElementById("client-full-name-" + meeting_id).value;
    let mobile_number = document.getElementById("client-modile-number-" + meeting_id).value;
    let email = document.getElementById("client-email-id-" + meeting_id).value;

    const regName = /^[a-zA-Z ]+$/;
    const regMob = /^[6-9]{1}\d{9}$/;
    if (email != "") {
        if (!regEmail.test(email)) {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Please enter valid Email id.";
            return;
        }

        if(email.length > 50) {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Email ID should not be more than 50 characters.";
            return;
        }
    }

    if (!regName.test(full_name)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter full name";
        return;
    }

    if (!regMob.test(mobile_number)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid 10-digit mobile number";
        return;
    }

    let meeting_description = document.getElementById("client-meeting-description-" + meeting_id).value;
    meeting_description = stripHTML(meeting_description);
    meeting_description = remove_special_characters_from_str(meeting_description);
    if (meeting_description == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter the meeting description.";
        return;
    }

    let meeting_start_date = document.getElementById("client-meeting-start-date-" + meeting_id).value;
    if (meeting_start_date == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter the meeting date.";
        return;
    }

    meeting_start_date = get_iso_formatted_date(meeting_start_date);
    let meet_date_year = meeting_start_date.split("-")[0]
    let meet_date_month = meeting_start_date.split("-")[1]
    let meet_date_date = meeting_start_date.split("-")[2]

    if (meet_date_year < new Date().getFullYear()) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid meeting date.";
        return;
    } else if (meet_date_year == new Date().getFullYear() && meet_date_month < (new Date().getMonth() + 1)) {
        error_message_element.innerHTML = "Please enter a valid meeting date.";
        error_message_element.style.color = "red";
        return;
    } else if (meet_date_year == new Date().getFullYear() && meet_date_month == (new Date().getMonth() + 1) && meet_date_date < new Date().getDate()) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid meeting date."
        return;
    }

    var current_time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });

    let meeting_start_time = document.getElementById("client-meeting-start-time-" + meeting_id).value;
    if (meeting_start_time == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter the start time.";
        return;
    }

    meeting_start_time = meeting_time_format(meeting_start_time)

    if(meeting_start_time == null){
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter start time in valid format.";
        return;
    }

    if (meeting_start_time < current_time) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "You have entered a time in the past. Please enter a valid start time.";
        return;
    }

    let meeting_end_time = document.getElementById("client-meeting-end-time-" + meeting_id).value;
    if (meeting_end_time == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter the end time.";
        return;
    }
    meeting_end_time = meeting_time_format(meeting_end_time)

    if(meeting_end_time == null){
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter end time in valid format.";
        return;
    }

    if (meeting_end_time < current_time) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "You have entered a time in the past. Please enter a valid end time.";
        return;
    }

    if (meeting_start_time >= meeting_end_time) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Start time should be less than end time.";
        return;

    }
    let meeting_password = document.getElementById("client-meeting-password-" + meeting_id).value;
    let request_params = {
        "meeting_id": meeting_id,
        "full_name": full_name,
        "mobile_number": mobile_number,
        "meeting_description": meeting_description,
        "meeting_start_date": meeting_start_date,
        "meeting_end_time": meeting_end_time,
        "meeting_start_time": meeting_start_time,
        "meeting_password": meeting_password,
        "email": email
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);
    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/save-video-meeting/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                window.location = window.location.href;
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Unable to save video meeting";
            }
            element.innerHTML = "Save";
        }
    }
    xhttp.send(params);
}


function assign_meeting_to_another_agent(element, meeting_id) {

    let assign_agent_element = document.getElementById("select-assign-agent-" + meeting_id);
    let agent_id = assign_agent_element.value;
    
    let request_params = {
        "meeting_id": meeting_id,
        "agent_id": agent_id
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);
    element.innerHTML = "Assigning...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/assign-video-meeting/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            
            if (response["status"] == 200) {
                agent_email = assign_agent_element.options[assign_agent_element.selectedIndex].text;
                var notification_obj = {
                    "notification_message": 'A meeting has been assigned to ' + agent_email + ".",
                    "product_name": response.product_name
                }
                send_notification(notification_obj);
                play_notification_sound();
                setTimeout('', 1000);
            }
            element.innerHTML = "Assigned";
            window.location.reload()
        }
    }
    xhttp.send(params);
}

function get_active_agent_list(session_id, language_support_pk, product_category_pk) {

    var selected_lang_pk = "-1";
    var select_agent_inner_html = '';
    if (language_support_pk) {
        selected_lang_pk = language_support_pk;
    }
    var assign_agent_error = document.getElementById('assign-session-error');
    var selected_product_category_pk = "-1";
    if (product_category_pk) {
        selected_product_category_pk = product_category_pk;
    }
    let json_string = JSON.stringify({
        "id": session_id,
        "selected_lang_pk": selected_lang_pk,
        "selected_product_category_pk": selected_product_category_pk
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/get-support-agents/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        select_agent_inner_html = '<option value="">Select Agent</option>';
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                var support_agents = response.support_agents;

                var current_selected_value = document.getElementById('select-assign-agent').value;

                if (support_agents.length > 0) {
                    for (let index = 0; index < support_agents.length; index++) {
                        if (support_agents[index].id == current_selected_value) {
                            select_agent_inner_html += '<option value="' + support_agents[index].id + '" selected> ' + support_agents[index].username + '</option>';
                        } else {
                            select_agent_inner_html += '<option value="' + support_agents[index].id + '"> ' + support_agents[index].username + '</option>';
                        }
                    }
                    assign_agent_error.style.display = 'none';
                    document.getElementById('assign-cobrowsing-agent-button').removeAttribute('disabled');
                } else {
                    assign_agent_error.innerHTML = 'Currently agents are not available. Please try again after sometime.';
                    assign_agent_error.style.display = 'block';
                    document.getElementById('assign-cobrowsing-agent-button').setAttribute('disabled', 'disabled');
                }
                document.getElementById('select-assign-agent').innerHTML = select_agent_inner_html;
            }
        }
    }
    xhttp.send(params);
}

function get_active_agent_list_live(session_id, language_support_pk, product_category_pk) {
    if (get_active_agent_list_interval[session_id]) {
        clearInterval(get_active_agent_list_interval[session_id]);
    }
    get_active_agent_list_interval[session_id] = setInterval(get_active_agent_list, 5000, session_id, language_support_pk, product_category_pk)
    get_active_agent_list(session_id, language_support_pk, product_category_pk)
}

function assign_cobrowsing_session_to_another_agent(element, session_id) {

    let assign_agent_element = document.getElementById("select-assign-agent");
    let agent_id = assign_agent_element.value;
    if (agent_id == undefined || agent_id.length == 0) {
        document.getElementById("assign-session-error").innerHTML = "No Agent Selected. Please Select an Agent";
        document.getElementById("assign-session-error").style.display = "block";
        return;
    }

    let request_params = {
        "session_id": session_id,
        "agent_id": agent_id
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);
    element.innerHTML = "Assigning...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/assign-cobrowsing-session/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                window.location.reload()
            } else if (response["status"] == 400) {
                document.getElementById("assign-session-error").innerHTML = "Failed to assign session. Agent is offline.";
                document.getElementById("assign-session-error").style.display = "block";
                element.innerHTML = "Assign";
            } else {
                document.getElementById("assign-session-error").innerHTML = "Internal server error.";
                document.getElementById("assign-session-error").style.display = "block";
                element.innerHTML = "Assign";
            }

        }
    }
    xhttp.send(params);
}



function get_client_agent_chats(meeting_id) {

    var json_string = JSON.stringify({
        "meeting_id": meeting_id
    });

    var encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/get-client-agent-chats/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                let message_history = response["message_history"]
                var chat_html = '<div class="chat-area"><div class="chat-message-wrapper">';

                for (let index = 0; index < message_history.length; index++) {
                    let sender = message_history[index]["sender"];
                    let message = message_history[index]["message"]
                    let datetime = message_history[index]["time"]
                    let type = message_history[index]["type"];
                    let sender_name = message_history[index]["sender_name"];

                    if (sender == "client") {
                        if (type == "attachment") {
                            chat_html += ['<div class="chat-client-message-wrapper">',
                                '<div class="chat-client-image"><svg width="9" height="12" viewBox="0 0 9 12" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path d="M4.50001 0.571426C3.17682 0.571426 2.10417 1.79731 2.10417 3.30952C2.10417 4.82173 3.17682 6.04762 4.50001 6.04762C5.82319 6.04762 6.89584 4.82173 6.89584 3.30952C6.89584 1.79731 5.82319 0.571426 4.50001 0.571426Z" fill="white"/>',
                                '<path d="M1.68487 7.14285C1.12266 7.14285 0.666677 7.66344 0.666672 8.30624L0.666672 8.5119C0.666672 9.54021 1.13186 10.31 1.84546 10.8065C2.54718 11.2947 3.49042 11.5238 4.50001 11.5238C5.50959 11.5238 6.45283 11.2947 7.15455 10.8065C7.86815 10.31 8.33334 9.54021 8.33334 8.5119L8.33334 8.3062C8.33333 7.66341 7.87735 7.14285 7.31516 7.14285H1.68487Z" fill="white"/>',
                                '</svg>',
                                '</div>',
                                '<div class="chat-client-message-bubble">',
                                '<div class="client-name-div">' + sender_name + '</div>',
                                '<div class="file-upload-img-div-client">',
                                '<svg width="19" height="26" viewBox="0 0 19 26" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path fill-rule="evenodd" clip-rule="evenodd" d="M11.0832 0V6.73434C11.0832 7.38877 11.6109 7.91654 12.2654 7.91654H18.9997V24.1507C18.9997 24.8052 18.4719 25.3329 17.8175 25.3329H1.1822C0.527768 25.3329 0 24.8052 0 24.1507V1.1822C0 0.527769 0.527768 0 1.1822 0H11.0832ZM13.8067 0.337772L18.6411 5.19325C18.8733 5.42547 19 5.72102 19 6.03768V6.33323H12.6668V0H12.9623C13.279 0 13.5745 0.126665 13.8067 0.337772Z" fill="url(#paint0_linear)"/>',
                                '<defs>',
                                '<linearGradient id="paint0_linear" x1="1.89293" y1="2.37496" x2="18.5174" y2="25.3331" gradientUnits="userSpaceOnUse">',
                                '<stop stop-color="#0254D7"/>',
                                '<stop offset="1" stop-color="#4A8DF8"/>',
                                '</linearGradient>',
                                '</defs>',
                                '</svg>',
                                // '<div class="file-name-div-client">',
                                //     attachment_file_name,
                                // '</div>',
                                message,
                                '</div>',
                                '</div>',
                                '<div class="chat-client-message-time">' + datetime + '</div>',
                                '</div>'
                            ].join('');
                        } else {
                            chat_html += ['<div class="chat-client-message-wrapper">',
                                '<div class="chat-client-image"><svg width="9" height="12" viewBox="0 0 9 12" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path d="M4.50001 0.571426C3.17682 0.571426 2.10417 1.79731 2.10417 3.30952C2.10417 4.82173 3.17682 6.04762 4.50001 6.04762C5.82319 6.04762 6.89584 4.82173 6.89584 3.30952C6.89584 1.79731 5.82319 0.571426 4.50001 0.571426Z" fill="white"/>',
                                '<path d="M1.68487 7.14285C1.12266 7.14285 0.666677 7.66344 0.666672 8.30624L0.666672 8.5119C0.666672 9.54021 1.13186 10.31 1.84546 10.8065C2.54718 11.2947 3.49042 11.5238 4.50001 11.5238C5.50959 11.5238 6.45283 11.2947 7.15455 10.8065C7.86815 10.31 8.33334 9.54021 8.33334 8.5119L8.33334 8.3062C8.33333 7.66341 7.87735 7.14285 7.31516 7.14285H1.68487Z" fill="white"/>',
                                '</svg>',
                                '</div>',
                                '<div class="chat-client-message-bubble">',
                                '<div class="client-name-div">' + sender_name + '</div>',
                                message,
                                '</div>',
                                '<div class="chat-client-message-time">' + datetime + '</div>',
                                '</div>'
                            ].join('');
                        }
                    } else {
                        if (type == "attachment") {
                            chat_html += ['<div class="chat-agent-message-wrapper">',
                                '<div class="chat-agent-image"><svg width="9" height="12" viewBox="0 0 9 12" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path d="M4.50001 0.571426C3.17682 0.571426 2.10417 1.79731 2.10417 3.30952C2.10417 4.82173 3.17682 6.04762 4.50001 6.04762C5.82319 6.04762 6.89584 4.82173 6.89584 3.30952C6.89584 1.79731 5.82319 0.571426 4.50001 0.571426Z" fill="white"/>',
                                '<path d="M1.68487 7.14285C1.12266 7.14285 0.666677 7.66344 0.666672 8.30624L0.666672 8.5119C0.666672 9.54021 1.13186 10.31 1.84546 10.8065C2.54718 11.2947 3.49042 11.5238 4.50001 11.5238C5.50959 11.5238 6.45283 11.2947 7.15455 10.8065C7.86815 10.31 8.33334 9.54021 8.33334 8.5119L8.33334 8.3062C8.33333 7.66341 7.87735 7.14285 7.31516 7.14285H1.68487Z" fill="white"/>',
                                '</svg>',
                                '</div>',
                                '<div class="chat-agent-message-bubble">',
                                '<div class="agent-name-div">' + sender_name + '</div>',
                                '<div class="file-upload-img-div-agent">',
                                '<svg width="19" height="26" viewBox="0 0 19 26" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path fill-rule="evenodd" clip-rule="evenodd" d="M11.0832 0V6.73434C11.0832 7.38877 11.6109 7.91654 12.2654 7.91654H18.9997V24.1507C18.9997 24.8052 18.4719 25.3329 17.8175 25.3329H1.1822C0.527768 25.3329 0 24.8052 0 24.1507V1.1822C0 0.527769 0.527768 0 1.1822 0H11.0832ZM13.8067 0.337772L18.6411 5.19325C18.8733 5.42547 19 5.72102 19 6.03768V6.33323H12.6668V0H12.9623C13.279 0 13.5745 0.126665 13.8067 0.337772Z" fill="white"/>',
                                '<defs>',
                                '<linearGradient id="paint0_linear" x1="1.89293" y1="2.37496" x2="18.5174" y2="25.3331" gradientUnits="userSpaceOnUse">',
                                '<stop stop-color="#0254D7"/>',
                                '<stop offset="1" stop-color="#4A8DF8"/>',
                                '</linearGradient>',
                                '</defs>',
                                '</svg>',
                                // '<div class="file-name-div-agent">',
                                //     attachment_file_name,
                                // '</div>',
                                message,
                                '</div>',
                                '</div>',
                                '<div class="chat-agent-message-time">',
                                datetime,
                                '</div>',
                                '</div>'
                            ].join('');

                        } else {
                            chat_html += ['<div class="chat-agent-message-wrapper">',
                                '<div class="chat-agent-image"><svg width="9" height="12" viewBox="0 0 9 12" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path d="M4.50001 0.571426C3.17682 0.571426 2.10417 1.79731 2.10417 3.30952C2.10417 4.82173 3.17682 6.04762 4.50001 6.04762C5.82319 6.04762 6.89584 4.82173 6.89584 3.30952C6.89584 1.79731 5.82319 0.571426 4.50001 0.571426Z" fill="white"/>',
                                '<path d="M1.68487 7.14285C1.12266 7.14285 0.666677 7.66344 0.666672 8.30624L0.666672 8.5119C0.666672 9.54021 1.13186 10.31 1.84546 10.8065C2.54718 11.2947 3.49042 11.5238 4.50001 11.5238C5.50959 11.5238 6.45283 11.2947 7.15455 10.8065C7.86815 10.31 8.33334 9.54021 8.33334 8.5119L8.33334 8.3062C8.33333 7.66341 7.87735 7.14285 7.31516 7.14285H1.68487Z" fill="white"/>',
                                '</svg>',
                                '</div>',
                                '<div class="chat-agent-message-bubble">',
                                '<div class="agent-name-div">' + sender_name + '</div>',
                                message,
                                '</div>',
                                '<div class="chat-agent-message-time">',
                                datetime,
                                '</div>',
                                '</div>'
                            ].join('');
                        }
                    }

                }
                chat_html += "</div></div>"
                document.getElementById("client-agent-chat-history").innerHTML = chat_html
            } else if (response["status"] == 301) {
                show_easyassist_toast("No Chat Record Found.")
            } else {
                show_easyassist_toast("Something went wrong!!");
            }
        }
    }
    xhttp.send(params);
}
//// notification management

const register_service_worker = async () => {
    await navigator.serviceWorker.register('/service-worker-cobrowse.js').then(function() {
            return navigator.serviceWorker.ready;
        })
        .then(function(registration) {
            // adding log for testing purpose
            console.log(registration); // service worker is ready and working...
        });
};


const request_notification_permission = async () => {
    if (Notification.permission !== "granted") {
        await window.Notification.requestPermission();
        // value of permission can be 'granted', 'default', 'denied'
        // granted: user has accepted the request
        // default: user has dismissed the notification permission popup by clicking on x
        // denied: user has denied the request.
    }
};

const setup_service_worker = async () => {
    try {
        await request_notification_permission();
        await register_service_worker();
    } catch (err) {}
};

if ('serviceWorker' in navigator) {
    window.addEventListener('load', async function() {
        setup_service_worker();
    });
}

var last_notification_played_timestamp = null;

function play_notification_sound() {
    if (last_notification_played_timestamp != null) {
        var temp_seconds = parseInt((Date.now() - last_notification_played_timestamp) / 1000)
        if (temp_seconds <= 1) {
            return
        }
    }
    last_notification_played_timestamp = Date.now()
    try {
        let audio_src = '/files/sounds/notification.mp3';
        let audio_obj = new Audio(audio_src);
        audio_obj.play();
    } catch (err) {
        setTimeout(play_notification_sound, 1000);
    }
}

function send_desktop_notification(notification_obj) {

    if (!("Notification" in window)) {

        show_easyassist_toast("This browser does not support desktop notification");

    } else if (Notification.permission === "granted") {

        var notification = new Notification(notification_obj.product_name, {
            body: notification_obj.notification_message
        });
        notification.onclick = function() {
            window.location.href = "/easy-assist/sales-ai/dashboard/"
        }

    } else if (Notification.permission !== "denied") {

        Notification.requestPermission().then(function(permission) {
            if (permission === "granted") {
                var notification = new Notification(notification_obj.product_name, {
                    body: notification_obj.notification_message
                });
                notification.onclick = function() {
                    window.location.href = "/easy-assist/sales-ai/dashboard/"
                }
            }
        });

    }
}

async function send_notification(notification_obj) {
    try {
        await navigator.serviceWorker.ready.then(function(serviceWorker) {
            serviceWorker.showNotification(notification_obj.product_name, {
                body: notification_obj.notification_message
            });
        }, function() {
            send_desktop_notification(notification_obj);
        });
    } catch (err) {
        send_desktop_notification(notification_obj);
    }
}

function check_and_reload_page() {

    if (window.location.href.indexOf("easy-assist/sales-ai/dashboard") != -1 && EASYASSIST_AGENT_ROLE == 'agent') {

        window.location.reload();
    }
}


///////////////////////    CognoAI Signal Development  /////////////////////////////////////

function create_client_server_signal(websocket_token, sender) {
    websocket_token = CryptoJS.MD5(websocket_token).toString();
    let ws_scheme = window.location.protocol == "http:" ? "ws" : "wss";
    let url = ws_scheme + '://' + window.location.host + '/ws/cognoai-signal/' + websocket_token + '/' + sender + "/";
    if (client_server_websocket == null) {
        client_server_websocket = new WebSocket(url);
        client_server_websocket.onmessage = sync_client_server_signal;
        client_server_websocket.onerror = client_server_signal_error;
        client_server_websocket.onopen = client_server_signal_open;
        client_server_websocket.onclose = close_client_server_signal;
    }
}

function client_server_signal_error(e) {

    try {
        client_server_websocket.close();
    } catch (err) {
        client_server_websocket.onmessage = null;
        client_server_websocket = null;
        setTimeout(function() {
            create_client_server_signal(WEBSOCKET_TOKEN, "client");
        }, 1000)
    }
}

function client_server_signal_open(e) {

    client_server_websocket_open = true;
    if (client_server_heartbeat_timer == null) {
        client_server_heartbeat_timer = setInterval(function(e) {
            client_server_signal_heartbeat();
        }, 5000);
    }
}


function send_client_server_signal(message, sender) {

    if (client_server_websocket_open && client_server_websocket != null) {
        client_server_websocket.send(JSON.stringify({
            "message": {
                "header": {
                    "sender": sender
                },
                "body": message
            }
        }));
    }
}


function client_server_signal_heartbeat() {

    let json_string = JSON.stringify({
        "type": "heartbeat",
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_client_server_signal(encrypted_data, "client");
}

function close_client_server_signal(e) {

    if (client_server_websocket == null) {
        return;
    }
    client_server_websocket_open = false;
    client_server_websocket = null;
    setTimeout(function() {
        create_client_server_signal(WEBSOCKET_TOKEN, "client");
    }, 1000);
}

function sync_client_server_signal(e) {

    var data = JSON.parse(e.data);
    let message = JSON.parse(data.message);
    let data_packet = message.body.Request;

    data_packet = easyassist_custom_decrypt(data_packet);
    data_packet = JSON.parse(data_packet);

    if (message.header.sender == "server") {
        if (data_packet.type == "notification") {
            check_notification(data_packet.response);
        } else if (data_packet.type == "page_refresh") {
            check_and_reload_page();
        } else if (data_packet.type == "agent_status_change_message") {
            show_easyassist_toast(data_packet.response)
            setTimeout(function() {
                window.location.reload(true);
            }, 3000);
        }
    } else {

        return;

    }
}

create_client_server_signal(WEBSOCKET_TOKEN, "client");
////////////////////////////////////////////////////////////////////////////////////////////

function check_notification(response) {

    if (response.status == 200) {
        var notification_list = response.notification_list;
        update_active_lead_status();
        for (let index = 0; index < notification_list.length; index++) {
            send_notification(notification_list[index]);
            setTimeout('', 1000)
        }
        if (notification_list.length) {
            play_notification_sound();
        }
    }
}

/////////////////////////////// Language Support ///////////////////////////////////////////

function save_cobrowse_agent_details(element) {

    var error_message_element = document.getElementById("save-cobrowsing-agent-details-error");
    error_message_element.innerHTML = "";
    var selected_language_pk_list = $("#easyassist-language-support-selected").val();
    if (selected_language_pk_list == null || selected_language_pk_list == undefined) {
        selected_language_pk_list = [];
    }
    var selected_product_category_list = $('#easyassist-product-category-selected').val();
    if (selected_product_category_list == null || selected_product_category_list == undefined) {
        selected_product_category_list = [];
    }
    let request_params = {
        "selected_language_pk_list": selected_language_pk_list,
        "selected_product_category_list": selected_product_category_list
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/save-cobrowse-agent-advanced-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Changes saved successfully.";
                setTimeout(function(e) {
                    window.location.reload();
                }, 1000);
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Unable to save the details";
            }
        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}


function get_scheduled_meeting_list() {
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/scheduled-meetings-list/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            let html = "";
            if (response.status == 200) {
                let meeting_list = response.meeting_list;
                if (meeting_list.length == 0) {
                    html += "<div class=\"text-center\">";
                    html += "No Scheduled Meeting";
                    html += "</div>";
                    $('#todays_meeting_modal .modal-body').html(html);
                } else {
                    for (let idx = 0; idx < meeting_list.length; idx++) {
                        let meeting_start_date = meeting_list[idx]["start_date"];
                        let meeting_start_time = meeting_list[idx]["start_time"];
                        let meeting_end_time = meeting_list[idx]["end_time"];

                        if(!meeting_start_date) {
                            meeting_start_date = "-";
                        }
                        if(!meeting_start_time) {
                            meeting_start_time = "-";
                        }
                        if(!meeting_end_time) {
                            meeting_end_time = "-";
                        }

                        html += "<tr>";
                        html += "<td>" + meeting_list[idx]["description"] + "</td>";
                        html += "<td>" + meeting_start_date + "</td>";
                        html += "<td>" + meeting_start_time + "</td>";
                        html += "<td>" + meeting_end_time + "</td>";
                        if (meeting_list[idx]["is_expired"]) {
                            html += "<td>Completed</td>"
                        } else {
                            html += "<td><a class=\"btn btn-info ml-3\" href=\"/easy-assist/meeting/" + meeting_list[idx]["id"] + "\" target=\"_blank\" style=\"color:#fff!important;cursor:pointer;\">Join</a></td>";
                        }
                        html += "</tr>";
                    }
                    html = "\
                    <table class=\"table table-bordered\" id=\"dataTable\" width=\"100%\" cellspacing=\"0\">\
                        <thead>\
                            <tr>\
                                <th>Meeting</th>\
                                <th>Meeting Date</th>\
                                <th> Start Time</th>\
                                <th>End Time</th>\
                                <th><span class=\"ml-3\">Status</span></th>\
                            </tr>\
                        </thead>\
                        <tbody>" + html + "</tbody>\
                    </table>";
                    $('#todays_meeting_modal .modal-body').html(html);
                    update_table_attribute();
                }
                $('#todays_meeting_modal').modal('show');
            }
        }
    }
    xhttp.send(null);
}

function delete_video_conferencing_form(form_id) {

    let request_params = {
        "form_id": form_id,
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/sales-ai/delete-video-conferencing-form/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                window.location.reload();
            } else if (response.status == 300) {
                show_easyassist_toast("Unable to delete form. Form does not exist.");
            } else {
                show_easyassist_toast("Unable to delete form. Please try again.");
            }
            $('#delete-form-modal-' + form_id).modal('hide');
        }
    }
    xhttp.send(params);
}

function change_form_agents(form_id, selected_agents) {

    let request_params = {
        "form_id": form_id,
        "selected_agents": selected_agents,
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var form_name = document.getElementById("cobrowse-form-name-" + form_id).innerHTML;

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/sales-ai/change-cobrowse-form-agent/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_easyassist_toast("List of agents for \"" + form_name + "\" is successfully updated.");
                FORM_AGENTS[form_id] = selected_agents;
            } else if (response.status == 300) {
                show_easyassist_toast("Unable to change form agent. Please try again");
            } else {
                show_easyassist_toast("Unable to change form agent. Please try again");
            }
        }
    }
    xhttp.send(params);
}

function show_close_cobrowse_session_modal(session_id) {
    close_session_id = session_id;
    $('#close_session_modal').modal('show');
}

function show_archive_cobrowse_session_modal(session_id) {
    archive_session_id = session_id;
    $('#archive_lead_modal').modal('show');
}

function get_url_vars() {
    var vars = {};
    window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m, key, value) {
        vars[key] = value;
    });
    return vars;
}

function update_table_attribute() {
    var table_elements = document.getElementsByTagName('table');
    for (let idx = 0; idx < table_elements.length; idx++) {
        var thead_el = table_elements[idx].getElementsByTagName('thead');
        if (thead_el.length == 0) {
            continue;
        }
        thead_el = thead_el[0];
        var tbody_el = table_elements[idx].getElementsByTagName('tbody');
        if (tbody_el.length == 0) {
            continue;
        }

        tbody_el = tbody_el[0];
        for (let row_index = 0; row_index < tbody_el.rows.length; row_index++) {
            if (tbody_el.rows[row_index].children.length != thead_el.rows[0].children.length) {
                continue;
            }
            for (let col_index = 0; col_index < tbody_el.rows[row_index].children.length; col_index++) {
                var column_element = tbody_el.rows[row_index].children[col_index];
                var th_text = thead_el.rows[0].children[col_index].innerText;
                column_element.setAttribute("data-content", th_text);
            }
        }
    }
}

$(document).ready(function() {
    update_table_attribute();
});

function get_url_multiple_vars() {
    var vars = {};
    window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m, key, value) {
        if (!(key in vars)) {
            vars[key] = [];
        }
        vars[key].push(value);
    });
    return vars;
}

function load_more_page(page_number) {
    function add_url_param(url, key, value) {
        var newParam = key + "=" + value;
        var result = url.replace(new RegExp("(&|\\?)" + key + "=[^\&|#]*"), '$1' + newParam);
        if (result === url) {
            result = (url.indexOf("?") != -1 ? url.split("?")[0] + "?" + newParam + "&" + url.split("?")[1] :
                (url.indexOf("#") != -1 ? url.split("#")[0] + "?" + newParam + "#" + url.split("#")[1] :
                    url + '?' + newParam));
        }
        return result;
    }
    window.location.href = add_url_param(window.location.href, "page", page_number);
}

function save_static_file() {
    var access_token = document.getElementById("admin_list_select_static").value;
    var selected_file_relative_path = document.getElementById("file_list_select").value;
    var selected_file_new_data = editor.getValue();

    let json_string = JSON.stringify({
        "access_token": access_token,
        "selected_file_relative_path": selected_file_relative_path,
        "selected_file_new_data": selected_file_new_data
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/save-static-file-content/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                let file_content = response.file_content
                editor.setValue(file_content);
                show_easyassist_toast("File Saved Successfully")
            } else {
                console.error("ERROR : ", response)
            }
        }
    }
    xhttp.send(params);
}

function reset_static_file() {
    var selected_file_relative_path = document.getElementById("file_list_select").value;
    var access_token = document.getElementById("admin_list_select_static").value;

    let json_string = JSON.stringify({
        "selected_file_relative_path": selected_file_relative_path,
        "access_token": access_token
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/reset-static-file-content/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                let file_content = response.file_content
                editor.setValue(file_content);
                show_easyassist_toast("File Reseted Successfully")
            } else {
                console.error("ERROR : ", response)
            }
        }
    }
    xhttp.send(params);
}

function fetch_static_file_content(element) {
    var relative_path = element.value;

    if (relative_path == "none") {
        editor.setValue("");
        document.getElementById("file_save_button").style.display = "none";
        return;
    }

    let json_string = JSON.stringify({
        "relative_path": relative_path
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/fetch-static-file-content/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                editor.setValue(response.file_content);
                if (response.file_type == "js") {
                    editor.session.setMode("ace/mode/javascript");
                } else {
                    editor.session.setMode("");
                }
                document.getElementById("file_save_button").style.display = "unset";
            } else {
                console.error("ERROR : ", response)
            }
        }
    }
    xhttp.send(params);

}

function fetch_static_file_list_for_admin(access_token) {

    let json_string = JSON.stringify({
        "access_token": access_token
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/fetch-static-file-list/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                let file_obj_list = response.file_obj_list
                var select_content = "<option value='none' selected>Select File</option>"
                for (let index = 0; index < file_obj_list.length; index++) {
                    var file_name = file_obj_list[index].name.trim();
                    var file_path = file_obj_list[index].relative_path.trim();
                    var option_content = '<option value="' + file_path + '">' + file_name + '</option>';
                    select_content += option_content;
                }

                document.getElementById("file_list_select").innerHTML = select_content;
                document.getElementById("file-list-container").style.display = "block";
                $('#file_list_select').selectpicker('refresh')
                // });
            } else {
                console.error("ERROR : ", response)
            }
        }
    }
    xhttp.send(params);
}

function admin_list_select_change_static(element) {
    var access_token_key = element.value;
    var file_list_container = document.getElementById("file-list-container");

    if (access_token_key == "none") {
        file_list_container.style.display = "none";
    } else {
        fetch_static_file_list_for_admin(access_token_key);
        document.getElementById("file_save_button").style.display = "unset";
    }
}

function save_assign_task_process(el) {
    var assign_task_process_id = document.getElementById("assign-task-process-id").value;
    var access_token_key = document.getElementById("admin_list_select").value;
    var processor_code = editor.getValue();

    if (!assign_task_process_id || access_token_key == "none") {
        show_easyassist_toast("Please select an admin");
        return;
    }

    var json_string = JSON.stringify({
        "process_id": assign_task_process_id,
        "access_token_key": access_token_key,
        "processor_code": processor_code,
    });

    var encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    el.innerText = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/save-assign-task-processor-code/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_easyassist_toast("Successfully updated assign task process");
            } else if (response.status == 301) {
                show_easyassist_toast("Invalid assign task process");
            } else if (response.status == 401) {
                show_easyassist_toast("Assign task process does not belong to selected admin");
            } else {
                show_easyassist_toast("Something went wrong. Please try again.");
            }
            el.innerText = "Save";
        }
    }
    xhttp.send(params);
}

/////////////////////// AGENT DETAILS API INTEGRATION ////////////////////////

function save_agent_details_api_process(el) {
    var agent_details_api_process_id = stripHTML(document.getElementById("api-details-process-id").value);
    var access_token_key = stripHTML(document.getElementById("admin_list_select").value);
    var agent_details_api_processor_code = editor.getValue();
    document.getElementById("agent-details-api-output-console").value = "";
    show_agent_details_api_console(false);

    if (!agent_details_api_process_id || access_token_key == "none") {
        show_easyassist_toast("Please select an admin.");
        return;
    }

    if(check_for_system_commands(agent_details_api_processor_code)) {
        show_easyassist_toast("Code contains system-commands. Please remove them and run again.");
        show_agent_details_api_console();
        document.getElementById("agent-details-api-output-console").value = "Error(s):";
        show_processor_errors();
        scroll_to_bottom("content-wrapper");
        return;
    }

    var json_string = JSON.stringify({
        "agent_details_api_process_id": agent_details_api_process_id,
        "access_token_key": access_token_key,
        "agent_details_api_processor_code": agent_details_api_processor_code
    });

    var encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    el.innerText = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/save-agent-details-api-processor-code/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_easyassist_toast("Successfully updated agent details API process.");
            } else if (response.status == 400) {
                show_easyassist_toast(response.message);
            } else {
                show_easyassist_toast("Something went wrong. Please try again.");
            }
            el.innerText = "Save";
        }
    }
    xhttp.send(params);
}

function show_agent_details_api_console(should_show=true) {
    if(should_show) {
        document.getElementById("agent-details-api-output-console").style.display = "inherit";
    } else {
        document.getElementById("agent-details-api-output-console").style.display = "none";
    }
}

function execute_agent_details_api(el) {
    var access_token_key = stripHTML(document.getElementById("admin_list_select").value);
    var agent_details_api_processor_code = editor.getValue();
    var agent_unique_identifier = stripHTML(document.getElementById("agent-unique-identifier-input").value.trim());
    show_agent_details_api_console(false);
    document.getElementById("agent-details-api-output-console").value = "";

    if(check_for_system_commands(agent_details_api_processor_code)) {
        show_easyassist_toast("Code contains system-commands. Please remove them and run again.");
        show_agent_details_api_console();
        document.getElementById("agent-details-api-output-console").value = "Error(s):";
        show_processor_errors();
        scroll_to_bottom("content-wrapper");
        return;
    }

    if (access_token_key == "none") {
        show_easyassist_toast("Please select an admin.");
        return;
    }

    if(!agent_unique_identifier) {
        show_easyassist_toast("Please enter an agent unique identifier.");
        return;
    }

    var json_string = JSON.stringify({        
        "access_token_key": access_token_key,
        "agent_details_api_processor_code": agent_details_api_processor_code,
        "agent_unique_identifier": agent_unique_identifier
    });

    var encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    el.innerText = "Running...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/run-agent-details-api-processor-code/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            document.getElementById("agent-details-api-output-console").value = "";
            var console_output = "Output:\n\n"
            if (response.status == 200) {
                if(response.message != null) {
                    try {
                        var api_response = response.message;
                        if(api_response["status_code"] == 200) {
                            console_output += `Execution time: ${response.total_execution_time}\n\nstatus_code: ${api_response["status_code"]}\n\nresponse_body: ${api_response["response_body"]}\n`;
                            document.getElementById("agent-details-api-output-console").value = console_output;
                        } else {
                            console_output += `Execution time: ${response.total_execution_time}\n\nstatus_code: ${api_response["status_code"]}\n\nresponse_body: ${api_response["response_body"]}\n\nerror_message: ${api_response["error_message"]}\n`;
                            document.getElementById("agent-details-api-output-console").value = console_output;
                        }
                    } catch (error) {
                        console.error("Could not parse agent details API response.")
                    }
                } else {
                    console_output += `Execution time: ${response.total_execution_time}\n\nError: Some error occurred while executing processor code.\n`
                    document.getElementById("agent-details-api-output-console").value = console_output;
                }
                show_agent_details_api_console();
                scroll_to_bottom("content-wrapper");
            } else if (response.status == 300) {
                console_output += `Execution time: ${response.total_execution_time}\n\nError(s): ${response.message}\n`;
                document.getElementById("agent-details-api-output-console").value = console_output;
                show_agent_details_api_console();
                scroll_to_bottom("content-wrapper");
            } else if (response.status == 301) {
                console_output += `Time Limit Exceeded Error(s): ${response.message}\n`;
                document.getElementById("agent-details-api-output-console").value = console_output;
                show_agent_details_api_console();
                scroll_to_bottom("content-wrapper");
            } else if (response.status == 400) {
                show_easyassist_toast(response.message);
            } else if (response.status == 500) {
                show_easyassist_toast("Some error occurred, please try again.")
                console.error("Internal server error");
            }
            el.innerText = "Run";
        }
    }
    xhttp.send(params);
}

function scroll_to_bottom(id) {
    var objDiv = document.getElementById(id);
    objDiv.scrollTop = objDiv.scrollHeight;
}

function check_for_system_commands(code) {
    var Range = ace.require('ace/range').Range;
    var code_lines = code.split('\n')
    var contains_system_commands = false;

    for (var i = 0; i < code_lines.length; ++i) {
        var line = code_lines[i];
        for (cmd of system_commands) {
            var err_index = line.indexOf(cmd);
            if (err_index != -1) {
                contains_system_commands = true;
                if (!highlighted_lines[i]) {
                    var id = editor.session.addMarker(new Range(i, 0, i, 1), "my-marker", "fullLine");
                    highlighted_lines[i] = id;
                    processor_errors[i] = "Line " + (i + 1) + " : " + err_index + " Contains " + cmd + " command which is a system command.";
                }
                break;
            } else {
                editor.session.removeMarker(highlighted_lines[i]);
                highlighted_lines[i] = undefined;
                processor_errors[i] = "";
            }
        }
    }
    return contains_system_commands;
}

function show_processor_errors() {
    var processor_output_console = document.getElementById("agent-details-api-output-console");

    for (key in processor_errors) {
        if (processor_errors[key] != "") {
            processor_output_console.value += '\n\n' + processor_errors[key];
        }
    }

    processor_output_console.style.display = 'block';
}

//////////////////////////////////////////////////////////////////////////////

function update_log_file() {

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/sales-ai/update-log-file/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {

                editor.setValue(response["code"])
                editor.clearSelection();
            }
        }
    }
    xhttp.send("{}");
}

function download_log_file(el) {

    var json_string = JSON.stringify({});

    var encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    el.innerText = "Downloading...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/download-log-file/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                if (response.file_id == undefined) {
                    show_easyassist_toast("No log file found");
                } else {
                    window.open(window.location.origin + '/easy-assist/download-file/' + response.file_id)
                }
            } else {
                show_easyassist_toast("Something went wrong. Please try again.");
            }
            el.innerText = "Download";
        }
    }
    xhttp.send(params);
}


function get_active_meeting_agent(meeting_id) {

    var assign_agent_error = document.getElementById('assign-meeting-session-error-' + meeting_id);
    assign_agent_error.style.display = 'none';
    let json_string = JSON.stringify({
        "meeting_id": meeting_id,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/get-meeting-support-agents/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                var select_agent_inner_html = '<option value="">Select Agent</option>';
                let support_agents = response.support_agents;
                if (support_agents.length > 0) {
                    for (let index = 0; index < support_agents.length; index++) {
                        select_agent_inner_html += '<option value="' + support_agents[index].id + '"> ' + support_agents[index].username + '</option>';
                    }
                    document.getElementById('assign-meeting-btn-' + meeting_id).removeAttribute('disabled');
                } else {
                    assign_agent_error.innerHTML = 'Currently agents are not available. Please try again after sometime.';
                    assign_agent_error.style.display = 'block';
                    document.getElementById('assign-meeting-btn-' + meeting_id).setAttribute('disabled', 'disabled');
                }
                document.getElementById('select-assign-agent-' + meeting_id).innerHTML = select_agent_inner_html;
            }
        }
    }
    xhttp.send(params);
}

function generate_api_document() {

    const regName = /^[^\s][a-zA-Z-]+$/;
    var client_id = document.getElementById("inline-form-input-client-id").value;

    if (!regName.test(client_id)) {
        show_easyassist_toast("Only character/des(-) are allowed")
        return;
    }

    var json_string = JSON.stringify({
        "client_id": client_id
    });

    var encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/generate-crm-api-documents/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                window.location.reload()
            } else {
                show_easyassist_toast("Something went wrong");
            }
        }
    }
    xhttp.send(params);
}


function show_agent_online_audit_trail(agent_username, date) {

    var json_string = JSON.stringify({
        "agent_username": agent_username,
        "date": date,
    });

    var encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent-online-audit-trail/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status == 200) {
                var html_table = "";
                var audit_trail_list = response.audit_trail_list;

                $("#agent-specific-audit-trail-table").dataTable().fnDestroy()
                if (audit_trail_list.length) {
                    for (let idx = 0; idx < audit_trail_list.length; idx++) {
                        html_table += [
                            '<tr>',
                            '<td>' + agent_username + '</td>',
                            '<td>' + audit_trail_list[idx]['login_time'] + '</td>',
                            '<td>' + audit_trail_list[idx]['logout_time'] + '</td>',
                            '<td>' + audit_trail_list[idx]['online_duration'] + '</td>',
                            '</tr>',
                        ].join('')
                    }
                }

                $('#agent-specific-audit-trail-table tbody').html(html_table);
                try {
                    if (audit_trail_list.length > 10) {
                        $('#agent-specific-audit-trail-table').DataTable({
                            'ordering': false,
                            "searching": false,
                            "bPaginate": true,
                            "bLengthChange": false
                        });
                    } else {
                        $('#agent-specific-audit-trail-table').DataTable({
                            'ordering': false,
                            "searching": false,
                            "bInfo": false,
                            "bPaginate": false,
                            "bLengthChange": false
                        });
                    }
                } catch (err) {
                    console.log(err);
                }

                update_table_attribute();
                $('#agent-audit-trail-container').hide();
                $('#agent-specif-table-container').show();
            }
        }
    }
    xhttp.send(params);
}

/************** Custom Filter ********************/
function scrollToBottom() {
    var scroll_element = document.getElementById("tbody-filter-parameters");
    scroll_element.scrollTop = scroll_element.scrollHeight;
} 

function revome_selected_filter_chip(el) {
    var selected_filter_parameters = $(el).closest('.filter-parameter-column')[0];
    var removed_value = $(el).closest('.filter-chip').find('span').html();
    var filter_key = selected_filter_parameters.getAttribute('filter-key');
    var filter_data = selected_filter_parameters.getAttribute('filter-data');
    filter_data = JSON.parse(filter_data);

    var new_filter_data = [];
    for (let idx = 0; idx < filter_data.length; idx++) {
        if (filter_data[idx] == removed_value) {
            continue;
        }
        new_filter_data.push(filter_data[idx]);
    }

    applied_filter_key_value_map[filter_key] = new_filter_data;

    if (filter_key == "title") {
        custom_title_filter_dropdown.update_value(new_filter_data);
    } else if (filter_key == "agent") {
        $("#selected-agent-filter").multiselect('deselect', removed_value);
    } else if (filter_key == "action") {
        custom_action_filter_dropdown.update_value(new_filter_data);
    }

    selected_filter_parameters.setAttribute('filter-data', JSON.stringify(new_filter_data));
    if (new_filter_data.length == 0) {
        $(selected_filter_parameters).find('.remove-filter-row-btn').click();
    } else {
        el.parentElement.remove();
    }
    var filter_chip_html = generate_filter_chips(filter_key, new_filter_data, true);
    selected_filter_parameters.getElementsByClassName('filter-chip-column')[0].innerHTML = filter_chip_html;
}

function update_applied_filter() {
    var url_params = get_url_multiple_vars();
    var params_keys = Object.keys(url_params);
    let is_filter_applied = false;
    var filter_html = "";

    for (let idx = 0; idx < params_keys.length; idx++) {
        if (params_keys[idx] == "page") {
            continue;
        }

        var filter_key = params_keys[idx];
        if (filter_key == "startdate") {
            filter_key = "Start Date";
        } else if (filter_key == "enddate") {
            filter_key = "End Date";
        }

        is_filter_applied = true;

        var filter_values = url_params[params_keys[idx]];

        var html_filter_chip = "";

        for (let index = 0; index < filter_values.length; index++) {
            html_filter_chip += [
                ' <div class="filter-chip">',
                '<span>' + perform_html_encoding(decodeURI(filter_values[index])) + '</span>',
                '<button class="filter-chip-remove-icon" onclick=\'remove_applied_filter_by_value(this, \"' + params_keys[idx] + '\");\'>',
                '<svg width="9" height="9" viewBox="0 0 9 9" fill="none" xmlns="http://www.w3.org/2000/svg">',
                '<path d="M5.38146 4.50006L8.06896 1.8188C8.18665 1.70112 8.25276 1.54149 8.25276 1.37505C8.25276 1.20862 8.18665 1.04899 8.06896 0.931305C7.95127 0.813615 7.79165 0.747498 7.62521 0.747498C7.45877 0.747498 7.29915 0.813615 7.18146 0.931305L4.50021 3.61881L1.81896 0.931305C1.70127 0.813615 1.54164 0.747498 1.37521 0.747498C1.20877 0.747498 1.04915 0.813615 0.931456 0.931305C0.813766 1.04899 0.747649 1.20862 0.747649 1.37505C0.747649 1.54149 0.813766 1.70112 0.931456 1.8188L3.61896 4.50006L0.931456 7.18131C0.872876 7.23941 0.826379 7.30853 0.794649 7.38469C0.762919 7.46086 0.746582 7.54255 0.746582 7.62506C0.746582 7.70756 0.762919 7.78925 0.794649 7.86542C0.826379 7.94158 0.872876 8.0107 0.931456 8.0688C0.989558 8.12739 1.05868 8.17388 1.13485 8.20561C1.21101 8.23734 1.2927 8.25368 1.37521 8.25368C1.45771 8.25368 1.5394 8.23734 1.61557 8.20561C1.69173 8.17388 1.76085 8.12739 1.81896 8.0688L4.50021 5.38131L7.18146 8.0688C7.23956 8.12739 7.30868 8.17388 7.38485 8.20561C7.46101 8.23734 7.5427 8.25368 7.62521 8.25368C7.70771 8.25368 7.78941 8.23734 7.86557 8.20561C7.94173 8.17388 8.01085 8.12739 8.06896 8.0688C8.12754 8.0107 8.17403 7.94158 8.20576 7.86542C8.23749 7.78925 8.25383 7.70756 8.25383 7.62506C8.25383 7.54255 8.23749 7.46086 8.20576 7.38469C8.17403 7.30853 8.12754 7.23941 8.06896 7.18131L5.38146 4.50006Z" fill="#0254D7"/>',
                '</svg>',
                '</button>',
                '</div>',
            ].join('');
        }

        filter_html += [
            '<div class="col-md-12 col-sm-12 filter-result-item">',
                '<div class="filter-name-text">',
                    '<span>' + filter_key + '</span>',
                    '<button class="filter-remove-icon filter-show-on-mobile" onclick=\'remove_applied_filter(\"' + params_keys[idx] + '\");\'>',
                        '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">',
                            '<path d="M1.5 1.5L10.5 10.5M1.5 10.5L10.5 1.5L1.5 10.5Z" stroke="#DC0000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>',
                        '</svg>',
                    '</button>',
                '</div>',
                '<div class="chip-area">',
                    html_filter_chip,
                '</div>',
                '<button class="filter-remove-icon filter-hide-on-mobile" style="background: transparent !important;" onclick=\'remove_applied_filter("' + params_keys[idx] + '");\'>',
                    '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">',
                        '<path d="M1.5 1.5L10.5 10.5M1.5 10.5L10.5 1.5L1.5 10.5Z" stroke="#DC0000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>',
                    '</svg>',
                '</button>',
            '</div>',
        ].join('');
    }

    filter_html += [
        '<div class="col-md-12 col-sm-12 mb-2 filter-padding-0" style="text-align: right;">',
        '<button class="clear-all-filter-btn" type="button" onclick="remove_all_applied_filter()">Clear All</button>',
        '</div>',
    ].join('');

    if (is_filter_applied) {
        document.getElementById("applied-filter-result-container").innerHTML = filter_html;
        document.getElementById("applied-filter-div").style.display = 'flex';
    } else {
        document.getElementById("applied-filter-div").style.display = 'none';
    }
}

function remove_applied_filter(filter_key) {
    var url_params = get_url_multiple_vars();
    var params_keys = Object.keys(url_params);

    var key_value = "";
    for (let idx = 0; idx < params_keys.length; idx++) {
        if (params_keys[idx] == filter_key) {
            continue;
        }

        for (let index = 0; index < url_params[params_keys[idx]].length; index++) {
            key_value += params_keys[idx] + "=" + url_params[params_keys[idx]][index] + "&";
        }
    }

    window.location = window.location.protocol + "//" + window.location.host + window.location.pathname + "?" + key_value + "&calendar_updated#pills-options-tab";
}

function remove_all_applied_filter() {
    var url_params = get_url_multiple_vars();
    var params_keys = Object.keys(url_params);

    var key_value = "";
    for (let idx = 0; idx < params_keys.length; idx++) {
        if (params_keys[idx] == "page") {
            key_value += params_keys[idx] + "=" + url_params[params_keys[idx]][0] + "&";
        }
    }
    window.location = window.location.protocol + "//" + window.location.host + window.location.pathname + "?" + key_value + "&calendar_updated#pills-options-tab";
}

function remove_applied_filter_by_value(el, filter_key) {
    var current_filter_value = $(el).parent().find('span').text();
    var url_params = get_url_multiple_vars();
    var params_keys = Object.keys(url_params);
    var key_value = "";
    for (let idx = 0; idx < params_keys.length; idx++) {
        if (params_keys[idx] == filter_key) {
            let filter_values = url_params[params_keys[idx]];
            for (let index = 0; index < filter_values.length; index++) {
                var filter_value = decodeURI(filter_values[index])
                if (filter_value == current_filter_value) {
                    continue;
                }
                key_value += params_keys[idx] + "=" + filter_value + "&";
            }
        } else {
            let filter_values = url_params[params_keys[idx]];
            for (let index = 0; index < filter_values.length; index++) {
                filter_value = decodeURI(filter_values[index])
                key_value += params_keys[idx] + "=" + filter_value + "&";
            }
        }
    }
    window.location = window.location.protocol + "//" + window.location.host + window.location.pathname + "?" + key_value + "&calendar_updated#pills-options-tab";
}

function check_filter_already_applied(preview_filter_value, current_filter_value) {

    if (JSON.stringify(preview_filter_value) === JSON.stringify(current_filter_value)) {
        return true;
    }
    return false;
}

function update_applied_filter_by_key(updated_filter_key, updated_filter_value) {
    var filter_parameters = document.getElementsByClassName("filter-parameter-column");
    var selected_filter_parameters = null;

    for (let idx = 0; idx < filter_parameters.length; idx++) {
        var filter_key = filter_parameters[idx].getAttribute('filter-key');

        if (filter_key == updated_filter_key) {
            selected_filter_parameters = filter_parameters[idx];
            break;
        }
    }

    if (selected_filter_parameters == null) {
        return;
    }
    selected_filter_parameters.setAttribute('filter-data', JSON.stringify(updated_filter_value));

    var filter_chip_html = "";
    filter_chip_html = generate_filter_chips(filter_key, updated_filter_value);
    selected_filter_parameters.getElementsByClassName('filter-chip-column')[0].innerHTML = filter_chip_html;
}

function generate_filter_chips(filter_key, filter_value_array, is_hidden_chip_required=true) {
    var filter_chip_html = "";
    for(let idx = 0; idx < filter_value_array.length; idx ++) {
        var chip_style = "";
        if(idx >= number_of_visible_chips && is_hidden_chip_required){
            chip_style = 'style="display: none;"';
        }
        filter_chip_html += [
            '<div class="filter-chip"'+chip_style+'>',
                '<span>' + filter_value_array[idx] + '</span>',
                '<button class="filter-chip-remove-icon" type="button" onclick="revome_selected_filter_chip(this)">',
                    '<svg width="9" height="9" viewBox="0 0 9 9" fill="none" xmlns="http://www.w3.org/2000/svg">',
                        '<path d="M5.38146 4.50006L8.06896 1.8188C8.18665 1.70112 8.25276 1.54149 8.25276 1.37505C8.25276 1.20862 8.18665 1.04899 8.06896 0.931305C7.95127 0.813615 7.79165 0.747498 7.62521 0.747498C7.45877 0.747498 7.29915 0.813615 7.18146 0.931305L4.50021 3.61881L1.81896 0.931305C1.70127 0.813615 1.54164 0.747498 1.37521 0.747498C1.20877 0.747498 1.04915 0.813615 0.931456 0.931305C0.813766 1.04899 0.747649 1.20862 0.747649 1.37505C0.747649 1.54149 0.813766 1.70112 0.931456 1.8188L3.61896 4.50006L0.931456 7.18131C0.872876 7.23941 0.826379 7.30853 0.794649 7.38469C0.762919 7.46086 0.746582 7.54255 0.746582 7.62506C0.746582 7.70756 0.762919 7.78925 0.794649 7.86542C0.826379 7.94158 0.872876 8.0107 0.931456 8.0688C0.989558 8.12739 1.05868 8.17388 1.13485 8.20561C1.21101 8.23734 1.2927 8.25368 1.37521 8.25368C1.45771 8.25368 1.5394 8.23734 1.61557 8.20561C1.69173 8.17388 1.76085 8.12739 1.81896 8.0688L4.50021 5.38131L7.18146 8.0688C7.23956 8.12739 7.30868 8.17388 7.38485 8.20561C7.46101 8.23734 7.5427 8.25368 7.62521 8.25368C7.70771 8.25368 7.78941 8.23734 7.86557 8.20561C7.94173 8.17388 8.01085 8.12739 8.06896 8.0688C8.12754 8.0107 8.17403 7.94158 8.20576 7.86542C8.23749 7.78925 8.25383 7.70756 8.25383 7.62506C8.25383 7.54255 8.23749 7.46086 8.20576 7.38469C8.17403 7.30853 8.12754 7.23941 8.06896 7.18131L5.38146 4.50006Z" fill="#0254D7"/>',
                    '</svg>',
                '</button>',
            '</div>',
        ].join('');    
    }
    if(is_hidden_chip_required) {
        if (filter_value_array.length > number_of_visible_chips) {
            var number_of_hidden_chips = filter_value_array.length - number_of_visible_chips;
            filter_chip_html = filter_chip_html + '<div class="filter-chip" id="show-hidden-filters-'+ filter_key +'" style="cursor: pointer;" onclick="show_hidden_chips(this.id)"> <span id="count-filters">+'+ number_of_hidden_chips +'</span></div>';
        }
    }
    return filter_chip_html;
}

function show_hidden_chips(id) {
    var chips_parent = document.getElementById(id).parentNode;
    var filter_chips = chips_parent.getElementsByClassName("filter-chip");
    for (let i = 0; i < filter_chips.length; i++) {
        if(filter_chips[i].style.display == "none") {
            filter_chips[i].style.display = "inline-flex";
        }
    }
    document.getElementById(id).style.display = "none";
}

/************** End of Custom Filter ********************/

function activate_support_history_sidebar() {
    try {
        document.getElementById('submenu2').classList.add('show');
        document.getElementById('submenu2-cobrowse-history').classList.add("active");
    } catch (err) {
        if (document.getElementById("menu-support-history")) {
            document.getElementById("menu-support-history").classList.add("active")
        }
    }
}

function activate_analytics_sidebar() {
    try {
        document.getElementById('submenu1').classList.add('show');
        document.getElementById('submenu1-cobrowse-analytics').classList.add("active");
    } catch (err) {
        if (document.getElementById("menu-cobrowse-analytics")) {
            document.getElementById("menu-cobrowse-analytics").classList.add("active")
        }
    }
}

function initialize_custom_tabs() {
    let btn_tabs = document.getElementsByClassName("rectangle-btn");

    for (let index = 0; index < btn_tabs.length; index++) {
        btn_tabs[index].classList.remove("active-page");
    }

    for (let index = 0; index < btn_tabs.length; index++) {
        if (btn_tabs[index].pathname == window.location.pathname) {
            btn_tabs[index].classList.add("active-page");

            try {
                btn_tabs[index].scrollIntoView(false);
            } catch (err) {}
        }
    }
}

function get_today_date() {
    var today = new Date();
    var dd = today.getDate();
    var mm = today.getMonth() + 1;
    var yyyy = today.getFullYear();
    if (dd < 10) {
        dd = '0' + dd;
    }

    if (mm < 10) {
        mm = '0' + mm;
    }
    today = yyyy + '-' + mm + '-' + dd;

    return today;
}

function send_otp_for_masking_pii_data(element, event) {
    event.preventDefault();

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/send-masking-pii-data-otp/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                $("#otp_verification_masking_pi_modal").modal('show');
            } else {
                show_easyassist_toast("Something went wrong. Please try again");
            }
        }
    }
    xhttp.send("{}");
}

function resend_pii_data_otp(element) {
    element.innerHTML = "Sending...";

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/send-masking-pii-data-otp/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_easyassist_toast("OTP is send.");
                element.innerHTML = "RESEND OTP";
            } else {
                show_easyassist_toast("Something went wrong. Please try again");
            }
        }
    }
    xhttp.send("{}");
}

function valid_deploy_link(str) {
    var pattern = new RegExp('^((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|' +
        '((\\d{1,3}\\.){3}\\d{1,3}))' +
        '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*' +
        '(\\?[;&a-z\\d%_.~+=-]*)?' +
        '(\\#[-a-z\\d_]*)?$', 'i');
    return !!pattern.test(str);
}

function save_extension(element, access_token_value) {
    let extension_name = document.getElementById("extension-name").value.trim();
    let deploy_links = document.getElementById("extension-deploy-domains").value.trim();

    const regExtensionName = /^[A-Za-z]+$/;

    if (extension_name == "") {
        show_easyassist_toast("Extension name can not be empty.");
        return;
    }
    else if(!regExtensionName.test(extension_name)){
        show_easyassist_toast("Numerics and special characters are not allowed.");
        return;
    }    
    if (deploy_links == "") {
        show_easyassist_toast("Deploy links can not be empty.");
        return;
    }

    let deploy_links_list = deploy_links.split(",")

    for (let link in deploy_links_list) {
        let res = is_valid_chrome_extension_url(deploy_links_list[link].trim())
        if (res == false) {
            show_easyassist_toast("Please enter a valid deploy link (like: www.example.com). This link is not valid " + deploy_links_list[link])
            return;
        }
    }

    element.innerHTML = "Saving..."
    let request_params = {
        "extension_name": extension_name,
        "deploy_links": deploy_links,
        "access_token": access_token_value
    }
    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/save-extension/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_easyassist_toast("Created successfully. Click 'Download' to download the extension.");
                element.innerHTML = "Save";
                var html = '<a href="' + response.path + '" id="download-button" class="btn btn-width-100">Download</a>'
                html += `<button class="btn btn-width-100" id="save-button" style="background: #10B981!important;" onclick="save_extension(this,  '` + access_token_value + `' )">Save</button>`;
                document.getElementById("extension_download").innerHTML = html;
            } else {
                element.innerHTML = "Save";
                show_easyassist_toast("Something went wrong. Please try again");
            }
        } else {
            element.innerHTML = "Save";
        }
    }
    xhttp.send(params);

}

function verify_pii_data_otp(element) {

    var otp_inputs = document.getElementsByClassName("pii-data-otp")
    var otp = "";
    for (let idx = 0; idx < otp_inputs.length; idx++) {
        if (otp_inputs[idx].value >= '0' && otp_inputs[idx].value <= '9') {
            otp += otp_inputs[idx].value;
        }
    }

    if (otp.length != 6) {
        show_easyassist_toast("Please enter otp before submitting.");
        return;
    }

    element.innerHTML = 'Verifying..';
    let request_params = {
        "otp": otp,
    };
    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/verify-masking-pii-data-otp/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            element.innerHTML = "Submit";

            if (response.status == 200) {
                show_easyassist_toast("Customer data will be saved in original format without being masked");
                setTimeout(function() {
                    window.location.href = window.location.href.replace(/[\?#].*|$/, "#pills-settings-tab");
                    window.location.reload();
                }, 2000);
            } else if (response.status == 301) {
                show_easyassist_toast("You have entered wrong otp. Please try again.");
            } else {
                show_easyassist_toast("Something went wrong. Please try again");
            }
        }
    }
    xhttp.send(params);
}

function enable_masking_of_pii_data(element) {

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/enable-masking-pii-data/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                element.disabled = true;
                show_easyassist_toast("Customer data will be masked due to privacy concerns");
                setTimeout(function() {
                    window.location.href = window.location.href.replace(/[\?#].*|$/, "#pills-settings-tab");
                    window.location.reload();
                }, 2000);
            } else if (response.status == 401) {
                show_easyassist_toast("You are not authorize to enable masking of pii data");
            } else {
                show_easyassist_toast("Something went wrong. Please try again");
            }
        }
    }
    xhttp.send("{}");
}

function update_active_lead_status() {

    let page_number = parseInt(window.localStorage.getItem("active_customers_current_page"));

    if(!page_number) {
        page_number = 1
    }
    
    let request_params = {
        "page_number": page_number
    }

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/get-all-active-lead-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                
                var cobrowse_lead_details = response.cobrowse_lead_details;
                var inactive_session_ids = [];
                var total_active_session = 0;
                var lead_data_html = "";

                var transfer_lead_previous_selected_rows = new Set();
                var transfer_lead_elements = document.getElementsByClassName("transfer-lead-radio");
                for(let idx = 0; idx < transfer_lead_elements.length; idx ++) {
                    var session_id = transfer_lead_elements[idx].getAttribute("session_id");
                    if(transfer_lead_elements[idx].checked) {
                        transfer_lead_previous_selected_rows.add(session_id);
                    }
                }
                for (let idx = 0; idx < cobrowse_lead_details.length; idx++) {
                    var lead_data = cobrowse_lead_details[idx];
                    if(lead_data.allow_agent_cobrowse == "true") {
                        total_active_session++;
                    }else{
                        inactive_session_ids.push(lead_data.session_id);
                    }
                    lead_data_html += cognoai_create_lead_card(lead_data, transfer_lead_previous_selected_rows);
                }
                if(stripHTML(lead_data_html) == ""){
                    lead_data_html = '<tr class="odd"><td valign="top" colspan="100%" style="text-align: center;">No data available in table</td></tr>';
                }
                if(document.getElementById("cognoai-lead-table-body")){
                    document.getElementById("cognoai-lead-table-body").innerHTML = lead_data_html;
                    let paginator_obj = new EasyAssistPaginator("table-pagination-div", "active_customers_current_page", update_active_lead_status, "active-customers-pagination", response.paginated_data, response.start, response.end, response.total_cobrowse_io_objs);
                }

                total_active_cobrowse_leads = cobrowse_lead_details.length;

                if (total_active_session) {
                    for (let idx = 0; idx < inactive_session_ids.length; idx++) {
                        try {
                            var cobrowse_connect_col = document.getElementById("easy-assist-" + inactive_session_ids[idx] + "-connect");
                            cobrowse_connect_col.getElementsByTagName("button")[0].disabled = true;
                            cobrowse_connect_col.getElementsByTagName("button")[0].setAttribute('title', "You can start only one cobrowsing session at a time.");
                        } catch (err) {}
                    }
                }

                if (total_active_cobrowse_leads > 0) {
                    document.getElementById("total_cobrowsing_count").innerHTML = total_active_cobrowse_leads;
                    document.getElementById("total_cobrowsing_count").parentElement.style.display = '';
                } else {
                    document.getElementById("total_cobrowsing_count").parentElement.style.display = "none";
                }

                for(let idx = 0; idx < transfer_lead_elements.length; idx ++) {
                    transfer_lead_elements[idx].addEventListener("click", function(event) {
                        var target = event.target;

                        var session_id = target.getAttribute("session_id");
                        var language_pk = target.parentElement.querySelector("input[name=cobrowse-language-pk]").value;
                        var product_category_pk = target.parentElement.querySelector("input[name=cobrowse-product-category-pk]").value;

                        var superviosr_transfer_lead_btn = document.getElementById("supervisor-transfer-lead-btn");
                        var is_prev_checked = target.getAttribute("is_checked");

                        if(is_prev_checked) {
                            superviosr_transfer_lead_btn.classList.add("disabled");
                            $(target).prop("checked", false);
                            target.removeAttribute("is_checked");
                        }

                        if(target.checked) {
                            target.setAttribute("is_checked", "true");

                            superviosr_transfer_lead_btn.classList.remove("disabled");
                            superviosr_transfer_lead_btn.onclick = function() {
                                get_active_agent_list_live(session_id, language_pk, product_category_pk)
                                show_transfer_agent_by_supervisor_modal(superviosr_transfer_lead_btn, session_id);
                            }
                        }
                    });
                }
            }
        }
    }
    xhttp.send(params);
}

$(document).ready(function() {
    update_all_lead_count_interval = setInterval(update_active_lead_count, UPDATE_ACTIVE_LEAD_COUNT_INTERVAL_TIME);
    update_active_lead_count();
    if(!on_canned_response_page){
        window.localStorage.removeItem("canned_response_page");
        window.localStorage.removeItem("searched_keyword");
        window.localStorage.removeItem("is_admin_filter_applied");
        window.localStorage.removeItem("is_supervisor_filter_applied");
        window.localStorage.removeItem("selected_supervisors");
    }

    if(!on_outbound_analytics_page) {
        window.sessionStorage.removeItem("outbound-analytics-filter-value");
    }

    if(!on_agent_management_page) {
        clear_agent_management_storage();
    }
});

function get_total_cobrowsing_rows() {
    try {

        if (window.location.href.indexOf("easy-assist/sales-ai/dashboard") <= -1) {
            return 0;
        }

        var total_rows = $('#dataTable tbody tr').length;
        if (total_rows > 1 || total_rows == 0) {
            return total_rows;
        }

        var total_cols = $($('#dataTable tbody tr')[0]).find('td').length;
        if (total_cols == 1) {
            return 0;
        } else {
            return 1;
        }
    } catch (err) {
        console.log(err);
        return 0;
    }
}

function get_available_agent_list_for_supervisor(element) {

    var parent_element = element.parentElement;
    var session_id = $(parent_element).find('input[name="cobrowse-session-id"]').val();
    var language_support_pk = $(parent_element).find('input[name="cobrowse-language-pk"]').val();
    var product_category_pk = $(parent_element).find('input[name="cobrowse-product-category-pk"]').val();
    var entered_agent_name = element.value;
    var agent_suggestion_box = $(parent_element).find('.suggestion-id-div')[0];

    $(parent_element).find('.tooltiptext-custom').hide();

    if (entered_agent_name.length < 3) {
        agent_suggestion_box.style.display = "none";
        return;
    }

    var selected_lang_pk = "-1";
    if (language_support_pk) {
        selected_lang_pk = language_support_pk;
    }
    var selected_product_category_pk = "-1";
    if (product_category_pk) {
        selected_product_category_pk = product_category_pk;
    }
    let json_string = JSON.stringify({
        "id": session_id,
        "selected_lang_pk": selected_lang_pk,
        "selected_product_category_pk": selected_product_category_pk
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/get-support-agents/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                var support_agents = response.support_agents;

                if (support_agents.length) {
                    var html = "";
                    var is_searched_agent_found = false;
                    var agent_suggestion_box = $(parent_element).find('.suggestion-id-div')[0];
                    for (let idx = 0; idx < support_agents.length; idx++) {
                        var agent_id = support_agents[idx].id;
                        var agent_username = support_agents[idx].username;

                        if (agent_username.indexOf(entered_agent_name) == -1) {
                            continue;
                        }
                        is_searched_agent_found = true;
                        html += [
                            '<a onclick="show_transfer_agent_by_supervisor_modal(this, \'' + session_id + '\', \'' + agent_id + '\');" href="javascript:void(0)">',
                            agent_username,
                            '</a>',
                        ].join('');
                    }
                    if (is_searched_agent_found) {
                        agent_suggestion_box.innerHTML = html;
                        agent_suggestion_box.style.display = "";
                    } else {
                        html = [
                            '<a href="javascript:void(0)">',
                            'No active agent found',
                            '</a>',
                        ].join('');
                        agent_suggestion_box.innerHTML = html;
                        agent_suggestion_box.style.display = "";
                        $(parent_element).find('.tooltiptext-custom').hide();
                    }
                } else {
                    html = "";
                    html += [
                        '<a href="javascript:void(0)">',
                        'No active agent found',
                        '</a>',
                    ].join('');
                    agent_suggestion_box.innerHTML = html;
                    agent_suggestion_box.style.display = "";
                    $(parent_element).find('.tooltiptext-custom').hide();
                }
            }
        }
    }
    xhttp.send(params);
}

function show_transfer_agent_by_supervisor_modal(element, session_id) {

    document.getElementById("assign-cobrowsing-agent-button").setAttribute("onclick", "transfer_lead_by_supervisor(this, '" + session_id + "')");
    $('#assign_session_modal').modal('show');
}

function show_assign_agent_by_supervisor_modal(element, session_id) {

    document.getElementById("assign-cobrowsing-agent-button").setAttribute("onclick", "assign_lead_by_supervisor_adminally(this, '" + session_id + "')");
    var error_element = document.getElementById("assign-session-error");
    error_element.innerHTML = "";
    error_element.style.display = "none";
    $('#assign_session_modal').modal('show');
}

function transfer_lead_by_supervisor(element, session_id) {

    var error_element = document.getElementById("assign-session-error");
    error_element.innerHTML = "";

    var assign_agent_element = document.getElementById("select-assign-agent");
    let agent_id = assign_agent_element.value;
    if (agent_id == undefined || agent_id.length == 0) {
        error_element.innerHTML = "No Agent Selected. Please Select an Agent";
        error_element.style.display = "block";
        return;
    }

    let agent_username = assign_agent_element.options[assign_agent_element.selectedIndex].text;

    let json_string = JSON.stringify({
        "session_id": session_id,
        "agent_id": agent_id,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/supervisor-assign-lead/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_element.innerHTML = "Lead transferred to " + agent_username;
                error_element.style.color = "green";
                setTimeout(function() {
                    window.location.reload();
                }, 1000);
            } else if (response.status == 501 || response.status == 301 || response.status == 302 || response.status == 303 || response.status == 304) {
                error_element.innerHTML = response.message;
                error_element.style.color = "red";
            } else {
                error_element.innerHTML = "Something went wrong";
                error_element.style.color = "red";
            }

            error_element.style.display = "block";
        }
    }
    xhttp.send(params);
}


function cognoai_create_lead_card(lead_data, transfer_lead_previous_selected_rows) {
    var cognoai_lead_card_html = "";
    try{
        var is_agent_active = false;
        if(document.getElementById("checkbox-mark-as-active")){
            is_agent_active = document.getElementById("checkbox-mark-as-active").checked;
        }

        // table row start
        cognoai_lead_card_html += '<tr id="easy-assist-' + lead_data.session_id + '" class="tr-hover">'

        if(EASYASSIST_AGENT_ROLE == "supervisor") {
            var checked_status = "";
            var is_checked_status = "";
            if(transfer_lead_previous_selected_rows.has(lead_data.session_id)) {
                checked_status = "checked";
                is_checked_status = 'is_checked="true"';
            }

            var language_pk = lead_data.supported_language_pk;
            var product_category_pk = lead_data.product_category_pk;

            if(language_pk == null) {
                language_pk = "";
            }

            if(product_category_pk == null) {
                product_category_pk = "";
            }

            cognoai_lead_card_html += `
                <td class="transfer-lead-radio-table-data">
                    <input type="radio" name="transfer_lead_radio" class="transfer-lead-radio" session_id="${lead_data.session_id}" ${checked_status} ${is_checked_status}>
                    <input type="hidden" name="cobrowse-language-pk" value="${language_pk}">
                    <input type="hidden" name="cobrowse-product-category-pk" value="${product_category_pk}">
                </td>`;
        }

        // Customer Details
        if(lead_data.is_lead){
            //
            cognoai_lead_card_html += '<td data-content="Customer Details" id="easy-assist-' + lead_data.session_id + '-customer-details">' + lead_data.get_sync_data + '</td>'
        } else {
            //
            cognoai_lead_card_html += '<td data-content="Customer Details" id="easy-assist-' + lead_data.session_id + '-customer-details">Name: ' + lead_data.full_name + '<br> Mobile Number: ' + lead_data.mobile_number + '</td>'
        }


        // Product
        var product_name = lead_data.product_name;
        var product_name_slice = product_name.slice(0,40);
        if(product_name.length > product_name_slice.length){
            product_name_slice += "...";
        }
        cognoai_lead_card_html += '<td data-content="Product" id="easy-assist-' +  lead_data.session_id + '-product"><a href="' + lead_data.product_url + '" target="_blank">' + product_name_slice + '</a></td>'


        // Category
        if(lead_data.allow_agent_to_customer_cobrowsing == false){
            if(lead_data.choose_product_category || lead_data.enable_tag_based_assignment_for_outbound){
                cognoai_lead_card_html += '<td data-content="Category" id="easy-assist-' +  lead_data.session_id + '-product-category">';
                if(lead_data.product_category){
                    cognoai_lead_card_html += lead_data.product_category;
                } else {
                    cognoai_lead_card_html += '-';
                }
                cognoai_lead_card_html += '</td>';
            }
        }


        // Language
        if(lead_data.allow_agent_to_customer_cobrowsing == false){
            if(lead_data.allow_language_support){
                cognoai_lead_card_html += '<td data-content="Language" id="easy-assist-' +  lead_data.session_id + '-support-language">';
                if(lead_data.supported_language){
                    cognoai_lead_card_html += lead_data.supported_language;
                } else {
                    cognoai_lead_card_html += '-';
                }
                cognoai_lead_card_html += '</td>';
            }
        }


        // Request DateTime
        cognoai_lead_card_html += '<td data-content="Request Date & Time" id="easy-assist-' +  lead_data.session_id + '-request-datetime">' + lead_data.request_datetime + '</td>';
        
        if(EASYASSIST_AGENT_ROLE != 'agent'){
            // Start DateTime
            cognoai_lead_card_html += '<td data-content="Start Date & Time" id="easy-assist-' +  lead_data.session_id + '-start-datetime">';
            if(lead_data.cobrowsing_start_datetime){
                cognoai_lead_card_html += lead_data.cobrowsing_start_datetime;
            } else {
                cognoai_lead_card_html += '-';
            }
            cognoai_lead_card_html += '</td>';
        }


        // Lead Status
        if (lead_data.is_active == false) {
            //
            cognoai_lead_card_html += '<td data-content="Status" id="easy-assist-' +  lead_data.session_id + '-status" class="text-danger">Inactive</td>';
        } else {

            // Reverse Cobrowsing Status
            if (lead_data.allow_agent_to_customer_cobrowsing == true) {
                if (!lead_data.cobrowsing_start_datetime) {
                    cognoai_lead_card_html += '<td data-content="Status" id="easy-assist-' +  lead_data.session_id + '-status" class="text-warning">Waiting for Customer</td>';
                } else if (lead_data.is_active == true) {
                    cognoai_lead_card_html += '<td data-content="Status" id="easy-assist-' +  lead_data.session_id + '-status" class="text-success">Connected</td>';
                } else {
                    cognoai_lead_card_html += '<td data-content="Status" id="easy-assist-' +  lead_data.session_id + '-status" class="text-danger">Inactive</td>';
                }
            } else if (lead_data.allow_video_meeting_only) {
                // Allow Video Meeting Only
                if (lead_data.meeting_start_datetime == null) {
                    if (lead_data.allow_agent_meeting == null) {
                        if (lead_data.agent_assistant_request_status) {
                            cognoai_lead_card_html += '<td data-content="Status" id="easy-assist-' +  lead_data.session_id + '-status" class="text-warning">Meeting Request Sent</td>';
                        } else {
                            cognoai_lead_card_html += '<td data-content="Status" id="easy-assist-' +  lead_data.session_id + '-status" class="text-warning">Request in queue</td>';
                        }
                    } else if (lead_data.allow_agent_meeting == "false") {
                        cognoai_lead_card_html += '<td data-content="Status" id="easy-assist-' +  lead_data.session_id + '-status" class="text-danger">Request denied by customer</td>';
                    } else {
                        cognoai_lead_card_html += '<td data-content="Status" id="easy-assist-' +  lead_data.session_id + '-status" class="text-danger">Waiting for Agent</td>';
                    }
                } else if (lead_data.is_active) {
                    cognoai_lead_card_html += '<td data-content="Status" id="easy-assist-' +  lead_data.session_id + '-status" class="text-success">Connected with an Agent</td>';
                } else {
                    cognoai_lead_card_html += '<td data-content="Status" id="easy-assist-' +  lead_data.session_id + '-status" class="text-danger">Inactive</td>';
                }
            } else {
                // Cobrowsing
                if (lead_data.cobrowsing_start_datetime == null) {
                    if (lead_data.allow_agent_cobrowse == null) {
                        if (lead_data.agent_assistant_request_status) {
                            cognoai_lead_card_html += '<td data-content="Status" id="easy-assist-' +  lead_data.session_id + '-status" class="text-warning">Cobrowsing Request Sent</td>';
                        } else {
                            cognoai_lead_card_html += '<td data-content="Status" id="easy-assist-' +  lead_data.session_id + '-status" class="text-warning">Request in queue</td>';
                        }
                    } else if (lead_data.allow_agent_cobrowse == "false") {
                        cognoai_lead_card_html += '<td data-content="Status" id="easy-assist-' +  lead_data.session_id + '-status" class="text-danger">Request denied by customer</td>';
                    } else {
                        cognoai_lead_card_html += '<td data-content="Status" id="easy-assist-' +  lead_data.session_id + '-status" class="text-warning">Waiting for Agent</td>';
                    }
                } else if (lead_data.is_active) {
                    cognoai_lead_card_html += '<td data-content="Status" id="easy-assist-' +  lead_data.session_id + '-status" class="text-success">Connected with an Agent</td>';
                } else {
                    cognoai_lead_card_html += '<td data-content="Status" id="easy-assist-' +  lead_data.session_id + '-status" class="text-danger">Inactive</td>';
                }
            }
        }


        // Time Duration
        cognoai_lead_card_html += '<td data-content="Time Duration" id="easy-assist-' +  lead_data.session_id + '-time-duration">' + lead_data.total_time_spent + '</td>'
        
        // Auto-assign timer
        if(lead_data.enable_auto_assign_unattended_lead) {
            if(lead_data.auto_assign_time_details.is_highlight_required) {
                cognoai_lead_card_html += '<td data-content="Auto-assign Time" id="easy-assist-' +  lead_data.session_id + '-auto-assign-duration" style="color: red;">' + lead_data.auto_assign_time_details.remaining_time_str + '</td>'
            } else {
                cognoai_lead_card_html += '<td data-content="Auto-assign Time" id="easy-assist-' +  lead_data.session_id + '-auto-assign-duration">' + lead_data.auto_assign_time_details.remaining_time_str + '</td>'
            }
            
        }
        
        if (lead_data.enable_lead_status) {
            if (!lead_data.is_reverse_cobrowsing) {

                if (lead_data.allow_video_meeting_only) {
                    if (lead_data.is_lead_reassigned) {
                        cognoai_lead_card_html += '<td data-content="Lead Status" id="easy-assist-' + lead_data.session_id + '-status" style="color: #FF7A1A;">Re-assigned</td>'
                    } else {
                        cognoai_lead_card_html += '<td data-content="Lead Status" id="easy-assist-' + lead_data.session_id + '-status">-</td>'
                    }
                } else if (lead_data.agent_role != "agent") {
                    if (lead_data.transfer_lead_time_details != "" && lead_data.lead_type == "transferred") {
                        cognoai_lead_card_html += `<td data-content="Lead Status" class="text-center" id="easy-assist-${lead_data.session_id}-status" 
                            style="color: #34D399;"> <p style="cursor: pointer;" rel="tooltip" data-placement="bottom"
                            title="From: ${lead_data.agent_email}"> Transferred</p></td>`;
                        if (lead_data.transfer_lead_time_details.is_highlight_required) {
                            cognoai_lead_card_html += '<td data-content="Transfer Expiry Time" id="easy-assist-' + lead_data.session_id + '-transfer-lead-duration" style="color: red;">' + lead_data.transfer_lead_time_details.remaining_time_str + '</td>'
                        } else {
                            cognoai_lead_card_html += '<td data-content="Transfer Expiry Time" id="easy-assist-' + lead_data.session_id + '-transfer-lead-duration">' + lead_data.transfer_lead_time_details.remaining_time_str + '</td>'
                        }
                    } else if (lead_data.lead_type == 'invited') {
                        cognoai_lead_card_html += '<td data-content="Lead Status" id="easy-assist-' + lead_data.session_id + '-status" style="color: #0090E1;"> <p style="cursor: pointer;" rel="tooltip" data-placement="bottom"\
                                                    title="From: ' + lead_data.inviting_agent + '">Invited</p></td>'
                        if (lead_data.enable_session_transfer_in_cobrowsing) {
                            cognoai_lead_card_html += '<td data-content="Transfer Expiry Time" id="easy-assist-' + lead_data.session_id + '-transfer-lead-duration"> - </td>'
                        }
                    } else if (lead_data.is_lead_reassigned) {
                        cognoai_lead_card_html += '<td data-content="Lead Status" id="easy-assist-' + lead_data.session_id + '-status" style="color: #FF7A1A;">Re-assigned</td>'
                        if (lead_data.enable_session_transfer_in_cobrowsing) {
                            cognoai_lead_card_html += '<td data-content="Transfer Expiry Time" id="easy-assist-' + lead_data.session_id + '-transfer-lead-duration"> - </td>'
                        }
                    } else {
                        cognoai_lead_card_html += '<td data-content="Lead Status" id="easy-assist-' + lead_data.session_id + '-status">-</td>'
                        if (lead_data.enable_session_transfer_in_cobrowsing) {
                            cognoai_lead_card_html += '<td data-content="Transfer Expiry Time" id="easy-assist-' + lead_data.session_id + '-transfer-lead-duration"> - </td>'
                        }
                    }
                } else {
                    if (lead_data.invited_agent && lead_data.lead_type == 'invited') {
                        cognoai_lead_card_html += '<td data-content="Lead Status" id="easy-assist-' + lead_data.session_id + '-status" style="color: #0090E1;"> <p style="cursor: pointer;" rel="tooltip" data-placement="bottom"\
                                                    title="From: ' + lead_data.inviting_agent + '">Invited</p></td>'
                        if (lead_data.enable_session_transfer_in_cobrowsing) {
                            cognoai_lead_card_html += '<td data-content="Transfer Expiry Time" id="easy-assist-' + lead_data.session_id + '-transfer-lead-duration"> - </td>'
                        }
                    } else if (lead_data.transferred_agent && lead_data.transfer_lead_time_details != "" && lead_data.lead_type == "transferred") {
                        cognoai_lead_card_html += `<td data-content="Lead Status" id="easy-assist-${lead_data.session_id}-status" 
                            style="color: #34D399;"> <p style="cursor: pointer;" rel="tooltip" data-placement="bottom"
                            title="From: ${lead_data.agent_username}"> Transferred</p></td>`;
                        if (lead_data.transfer_lead_time_details.is_highlight_required) {
                            cognoai_lead_card_html += '<td data-content="Transfer Expiry Time" id="easy-assist-' + lead_data.session_id + '-transfer-lead-duration" style="color: red;">' + lead_data.transfer_lead_time_details.remaining_time_str + '</td>'
                        } else {
                            cognoai_lead_card_html += '<td data-content="Transfer Expiry Time" id="easy-assist-' + lead_data.session_id + '-transfer-lead-duration">' + lead_data.transfer_lead_time_details.remaining_time_str + '</td>'
                        }
                    } else if (lead_data.is_lead_reassigned) {
                        cognoai_lead_card_html += '<td data-content="Lead Status" id="easy-assist-' + lead_data.session_id + '-status" style="color: #FF7A1A;">Re-assigned</td>'
                        if (lead_data.enable_session_transfer_in_cobrowsing) {
                            cognoai_lead_card_html += '<td data-content="Transfer Expiry Time" id="easy-assist-' + lead_data.session_id + '-transfer-lead-duration"> - </td>'
                        }
                    } else {
                        cognoai_lead_card_html += '<td data-content="Lead Status" id="easy-assist-' + lead_data.session_id + '-status">-</td>'
                        if (lead_data.enable_session_transfer_in_cobrowsing) {
                            cognoai_lead_card_html += '<td data-content="Transfer Expiry Time" id="easy-assist-' + lead_data.session_id + '-transfer-lead-duration"> - </td>'
                        }
                    }
                }
            } else {
                cognoai_lead_card_html += '<td data-content="Lead Status" id="easy-assist-' + lead_data.session_id + '-status">-</td>'
                if (lead_data.enable_session_transfer_in_cobrowsing) {
                    cognoai_lead_card_html += '<td data-content="Transfer Expiry Time" id="easy-assist-' + lead_data.session_id + '-transfer-lead-duration"> - </td>'
                }
            }
        } else {
            if(lead_data.enable_session_transfer_in_cobrowsing) {
                if (lead_data.transfer_lead_time_details != "" && lead_data.lead_type == "transferred" && lead_data.transfer_lead_time_details.is_highlight_required) {
                    cognoai_lead_card_html += '<td data-content="Transfer Expiry Time" id="easy-assist-' + lead_data.session_id + '-transfer-lead-duration" style="color: red;">' + lead_data.transfer_lead_time_details.remaining_time_str + '</td>'
                } else {
                    cognoai_lead_card_html += '<td data-content="Transfer Expiry Time" id="easy-assist-' + lead_data.session_id + '-transfer-lead-duration">' + lead_data.transfer_lead_time_details.remaining_time_str + '</td>'
                }
            }
        }

        if(lead_data.allow_video_meeting_only && lead_data.enable_session_transfer_in_cobrowsing) {
            cognoai_lead_card_html += '<td data-content="Transfer Expiry Time" id="easy-assist-' + lead_data.session_id + '-transfer-lead-duration"> - </td>'
        }

        if (lead_data.enable_auto_assign_unattended_lead) {
            if(lead_data.unattended_lead_transfer_audit_trail.length) {
            cognoai_lead_card_html += '<td data-content="Assigned Agents" class="text-center unattended-lead-transfer-count-header" id="easy-assist-' +  lead_data.session_id + '-auto-assign-agent-count"> \
                <button class="btn btn-info unattended-lead-transfer-count-btn" rel="tooltip" data-placement="bottom" title="Click to view Auto Assign Audit Trail." data-toggle="modal" \
                    onclick="open_agent_audit_trail_modal(' + JSON.stringify(lead_data.unattended_lead_transfer_audit_trail).split('"').join("&quot;") + ');" style="color: white;">' 
                        + lead_data.unattended_lead_transfer_audit_trail.length + 
                '</button> </td>';
            } else {
                cognoai_lead_card_html += '<td data-content="Assigned Agents" id="easy-assist-' +  lead_data.session_id + '-auto-assign-agent-count">-</td>';
            }
        }

        // Agent
        if(EASYASSIST_AGENT_ROLE != 'agent'){
            cognoai_lead_card_html += '<td data-content="Agent" id="easy-assist-' +  lead_data.session_id + '-agent">' + lead_data.agent_username + '</td>'
        }
        
        // Supervisors
        if(EASYASSIST_AGENT_ROLE == 'admin_ally'){
            cognoai_lead_card_html += '<td data-content="Supervisors" id="easy-assist-' +  lead_data.session_id + '-agent_supervisors">' + lead_data.agent_supervisors + '</td>'
        }

        // Notify
        if(EASYASSIST_AGENT_ROLE == 'admin'){
            cognoai_lead_card_html += [
                '<td data-content="Notify" id="easy-assist-' +  lead_data.session_id + '-notify">',
                    '<button class="btn btn-info" style="background-color: #17a673 !important; color: white;" onclick="notify_agent(\'' +  lead_data.session_id + '\')">',
                        lead_data.agent_notified_count,
                    '</button>',
                '</td>',
            ].join('');
        }

        // Connect/Archive
        if(EASYASSIST_AGENT_ROLE == 'agent'){
            if(!lead_data.is_reverse_cobrowsing){
                if(lead_data.is_active){
                    if(lead_data.show_verification_code_modal == false) {
                        if(lead_data.allow_video_meeting_only){
                            cognoai_lead_card_html += [
                                '<td data-content="Connect/Archive" id="easy-assist-' +  lead_data.session_id + '-connect">',
                                    '<button class="btn btn-primary btn-sm" onclick="request_for_inbound_cobrowsing(\'' + lead_data.session_id + '\')">Click to Connect</button>',
                                '</td>'
                            ].join('');
                        } else if ( lead_data.allow_screen_sharing_cobrowse ){
                            cognoai_lead_card_html += [
                                '<td data-content="Connect/Archive" id="easy-assist-' +  lead_data.session_id + '-connect">',
                                    '<a href="/easy-assist/agent/screensharing-cobrowse/' + lead_data.session_id + '"><button type="button" class="btn btn-success btn-sm">Connect</button></a>',
                                '</td>'
                            ].join('');
                        } else {
                            if(lead_data.allow_cobrowsing_meeting == false){
                                if(lead_data.transferred_agent == window.ACTIVE_AGENT_USERNAME && lead_data.lead_type == "transferred") {
                                    cognoai_lead_card_html += [
                                        '<td data-content="Connect/Archive" id="easy-assist-' +  lead_data.session_id + '-connect">',
                                            '<button type="button" onclick="update_cobrowse_tranfer_agent_logs(\'' + lead_data.session_id + '\')" class="btn btn-success btn-sm">Connect</button>',
                                        '</td>'
                                    ].join('');
                                } else {
                                    cognoai_lead_card_html += [
                                        '<td data-content="Connect/Archive" id="easy-assist-' +  lead_data.session_id + '-connect">',
                                            '<button type="button" onclick="assign_lead_to_agent(\'' + lead_data.session_id + '\', \'' + lead_data.share_client_session + '\')" class="btn btn-success btn-sm">Connect</button>',
                                        '</td>'
                                    ].join('');
                                }
                            } else {
                                if(lead_data.transferred_agent == window.ACTIVE_AGENT_USERNAME && lead_data.lead_type == "transferred") {
                                    cognoai_lead_card_html += [
                                        '<td data-content="Connect/Archive" id="easy-assist-' +  lead_data.session_id + '-connect">',
                                            '<button type="button" onclick="update_cobrowse_tranfer_agent_logs(\'' + lead_data.session_id + '\')" class="btn btn-success btn-sm">Connect</button>',
                                        '</td>'
                                    ].join('');
                                } else {
                                    cognoai_lead_card_html += [
                                        '<td data-content="Connect/Archive" id="easy-assist-' +  lead_data.session_id + '-connect">',
                                            '<a href="javascript:void(0)"><button type="button" class="btn btn-primary btn-sm" onclick="request_for_inbound_cobrowsing(\'' + lead_data.session_id + '\')">Click to Connect</button></a>',
                                        '</td>'
                                    ].join('');
                                }
                            }
                        }
                    } else if ( lead_data.allow_agent_cobrowse == "true" ) {
                        if(lead_data.allow_screen_sharing_cobrowse){
                            cognoai_lead_card_html += [
                                '<td data-content="Connect/Archive" id="easy-assist-' + lead_data.session_id + '-connect">',
                                    '<a href="/easy-assist/agent/screensharing-cobrowse/' + lead_data.session_id + '"><button type="button" class="btn btn-success btn-sm">Connect</button></a>',
                                '</td>'
                            ].join('');
                        } else {
                            if(lead_data.lead_type == "transferred") {
                                cognoai_lead_card_html += [
                                    '<td data-content="Connect/Archive" id="easy-assist-' +  lead_data.session_id + '-connect">',
                                        '<button type="button" onclick="update_cobrowse_tranfer_agent_logs(\'' + lead_data.session_id + '\')" class="btn btn-success btn-sm">Connect</button>',
                                    '</td>'
                                ].join('');
                            } else {
                                cognoai_lead_card_html += [
                                    '<td data-content="Connect/Archive" id="easy-assist-' +  lead_data.session_id + '-connect">',
                                        '<button type="button" onclick="assign_lead_to_agent(\'' + lead_data.session_id + '\', \'' + lead_data.share_client_session + '\')" class="btn btn-success btn-sm">Connect</button>',
                                    '</td>'
                                ].join('');
                            }
                        }
                    } else {
                        cognoai_lead_card_html += '<td data-content="Connect/Archive" id="easy-assist-' +  lead_data.session_id + '-connect">';
                        if(lead_data.allow_video_meeting_only){
                            if(is_agent_active){
                                cognoai_lead_card_html += [
                                    '<a href="javascript:void(0)">',
                                        '<button type="button" class="btn btn-primary btn-sm" onclick="request_for_inbound_cobrowsing(\'' + lead_data.session_id + '\')">Click to Connect</button>',
                                    '</a>'
                                ].join('');
                            } else {
                                cognoai_lead_card_html += [
                                    '<a href="javascript:void(0)">',
                                        '<button type="button" class="btn btn-primary btn-sm" onclick="request_for_inbound_cobrowsing(\'' + lead_data.session_id + '\')" disabled>Click to Connect</button>',
                                    '</a>'
                                ].join('');
                            }
                        } else {
                            // Droplink Lead
                            if(lead_data.is_droplink_lead && lead_data.enable_verification_code_popup == false){
                                if(is_agent_active){
                                    if(lead_data.allow_agent_cobrowse == "true"){
                                        cognoai_lead_card_html += [
                                            '<a href="javascript:void(0)" tabindex="0" data-toggle="tooltip" title="Cobrowsing request already sent" data-placement="bottom" style="display: block; width: fit-content;">',
                                                '<button type="button" class="btn btn-primary btn-sm" onclick="request_for_cobrowsing(\'' + lead_data.session_id + '\')" disabled style="pointer-events: none;"> Re-send Request</button>',
                                            '</a>'
                                        ].join('');
                                    } else {
                                        cognoai_lead_card_html += [
                                            '<a href="javascript:void(0)">',
                                                '<button type="button" class="btn btn-primary btn-sm" onclick="request_for_cobrowsing(\'' + lead_data.session_id + '\')">Re-send Request</button>',
                                            '</a>'
                                        ].join('');
                                    }
                                } else {
                                    cognoai_lead_card_html += [
                                        '<a href="javascript:void(0)">',
                                            '<button type="button" class="btn btn-primary btn-sm" onclick="request_for_cobrowsing(\'' + lead_data.session_id + '\')" disabled>Re-send Request</button>',
                                        '</a>'
                                    ].join('');
                                }
                            } else {
                                if(is_agent_active){
                                    cognoai_lead_card_html += [
                                        '<a href="javascript:void(0)">',
                                            '<button type="button" class="btn btn-primary btn-sm" onclick="request_for_inbound_cobrowsing(\'' + lead_data.session_id + '\')">Click to Connect</button>',
                                        '</a>'
                                    ].join('');
                                } else {
                                    cognoai_lead_card_html += [
                                        '<a href="javascript:void(0)">',
                                            '<button type="button" class="btn btn-primary btn-sm" onclick="request_for_inbound_cobrowsing(\'' + lead_data.session_id + '\')" disabled>Click to Connect</button>',
                                        '</a>'
                                    ].join('');
                                }
                            }
                        }
                        cognoai_lead_card_html += '</td>';
                    }
                } else {
                    cognoai_lead_card_html += [
                        '<td data-content="Connect/Archive" id="easy-assist-' +  lead_data.session_id + '-connect">',
                            '<a href="#" class="btn btn-danger btn-icon-split" onclick="show_archive_cobrowse_session_modal(\'' + lead_data.session_id + '\');">',
                                '<span class="icon text-white-50">',
                                    '<i class="fas fa-trash"></i>',
                                '</span>',
                            '<span class="text">Archive</span>',
                            '</a>',
                        '</td>'
                    ].join('');
                }
            } else {
                cognoai_lead_card_html += '<td>--</td>';
            }
        }
        
        // Transfer Session
        if(EASYASSIST_AGENT_ROLE == 'agent' ) {
            cognoai_lead_card_html += '<td id="easy-assist-' +  lead_data.session_id + '-transfer" style="text-align: center;">';
            if (lead_data.agent_username == ACTIVE_AGENT_USERNAME) {
                if(lead_data.is_active){
                    if(lead_data.allow_video_meeting_only){
                        if(!lead_data.meeting_start_datetime){
                            cognoai_lead_card_html += '<a id="transfer-session-btn-' +  lead_data.session_id + '" data-toggle="tooltip" style="cursor: pointer; visibility: hidden; margin-right: 10px;" title="Transfer Session" onclick="show_assign_session_modal(\'' + lead_data.session_id + '\');get_active_agent_list_live(\'' + lead_data.session_id + '\', ' + lead_data.supported_language_pk + ', ' + lead_data.product_category_pk + ')"><i class="fas fa-fw fa-users"></i></a>';
                        }
                    } else {
                        if(!lead_data.cobrowsing_start_datetime){
                            cognoai_lead_card_html += '<a data-toggle="tooltip" style="cursor: pointer; visibility: hidden; margin-right: 10px;" title="Transfer Session" onclick="show_assign_session_modal(\'' + lead_data.session_id + '\');get_active_agent_list_live(\'' + lead_data.session_id + '\', ' + lead_data.supported_language_pk +', ' + lead_data.product_category_pk + ')"><i class="fas fa-fw fa-users"></i></a>';
                        }
                    }
                    
                    cognoai_lead_card_html += [
                        '<a data-toggle="tooltip" style="cursor: pointer; visibility: hidden; margin-right: 10px;" title="End Session" onclick="show_close_cobrowse_session_modal(\'' + lead_data.session_id + '\')">',
                            '<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<circle cx="7.5" cy="7.5" r="7.5" fill="#FF4646"/>',
                                '<path d="M11 4.86503L10.135 4L7.5 6.63497L4.86503 4L4 4.86503L6.63497 7.5L4 10.135L4.86503 11L7.5 8.36503L10.135 11L11 10.135L8.36503 7.5L11 4.86503Z" fill="white"/>',
                            '</svg>',
                        '</a>'
                    ].join('');
                } else {
                    cognoai_lead_card_html += [
                        '<a data-toggle="tooltip" style="cursor: pointer; display: none; margin-right: 10px;" title="Transfer Session" onclick="show_assign_session_modal(\'' + lead_data.session_id + '\')"><i class="fas fa-fw fa-users"></i></a>',
                        '<a data-toggle="tooltip" style="cursor: pointer; display: none; margin-right: 10px;" title="End Session" onclick="show_close_cobrowse_session_modal(\'' + lead_data.session_id + '\')">',
                            '<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<circle cx="7.5" cy="7.5" r="7.5" fill="#FF4646"/>',
                                '<path d="M11 4.86503L10.135 4L7.5 6.63497L4.86503 4L4 4.86503L6.63497 7.5L4 10.135L4.86503 11L7.5 8.36503L10.135 11L11 10.135L8.36503 7.5L11 4.86503Z" fill="white"/>',
                            '</svg>',
                        '</a>'
                    ].join('');
                }
            } else {
                if(lead_data.is_active && lead_data.enable_session_transfer_in_cobrowsing && lead_data.lead_type == "transferred"){
                    cognoai_lead_card_html += [
                        '<a data-toggle="tooltip" style="cursor: pointer; visibility: hidden; margin-right: 10px;" title="Reject request" onclick="reject_cobrowse_tranfer_agent_lead(\'' + lead_data.session_id + '\')">',
                            '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path d="M3.23047 3L14.7703 15" stroke="#FF281A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
                                '<path d="M14.7695 3L3.2297 15" stroke="#FF281A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
                            '</svg>',
                        '</a>'
                    ]
                }
            } 
            cognoai_lead_card_html += '</td>';
        }

        cognoai_lead_card_html += '</tr>';
    } catch (err) {
        console.log("ERROR: cognoai_create_lead_card ", err);
        cognoai_lead_card_html = "";
    }
    return cognoai_lead_card_html;
}

function open_agent_audit_trail_modal(audit_trail_list) {
    if(!audit_trail_list) {
        $("#auto_assign_transfer_audit_trail_table tbody").empty();
        $("#auto_assign_audit_trail").modal("show");
        return;
    }
    let tbody_data = "";
    $("#auto_assign_transfer_audit_trail_table tbody").empty();
    for(let i=0; i < audit_trail_list.length; i++) {
        let auto_assign_details = audit_trail_list[i].auto_assign_datetime.split(" ");
        let auto_assign_date = auto_assign_details[0];
        let auto_assign_time = auto_assign_details[1] + " " + auto_assign_details[2];
        tbody_data += `<tr>
        <td data-content="SL No.">${i+1}</td>
        <td data-content="Date Time">${auto_assign_date}<br/>${auto_assign_time}</td>
        <td data-content="Auto Assigned Agent">${audit_trail_list[i].agent_username}</td>
        </tr>`;
    }
    $("#auto_assign_transfer_audit_trail_table tbody").append(tbody_data);
    $("#auto_assign_audit_trail").modal("show");
}


/************************* START BUG REPORT *************************/

function easyassist_ignore_element_from_screenshot(element){
    var blacklisted_classes = ["tooltip"];
    var blacklisted_ids = ["report_problem_icon"];

    var is_element_to_remove = false;
    blacklisted_classes.forEach(function(class_name){
        if(element.classList.contains(class_name)){
            is_element_to_remove = true;
        }
    });

    blacklisted_ids.forEach(function(id){
        if(element.getAttribute("id") == id){
            is_element_to_remove = true;
        }
    });

    return is_element_to_remove;
}

function easyassist_capture_screenshot(agent_name) {

    var body = document.body,
        doc_html = document.documentElement;
    var new_body_height = Math.max(body.scrollHeight, body.offsetHeight,
        doc_html.clientHeight, doc_html.scrollHeight, doc_html.offsetHeight);

    html2canvas(body, {
        x: window.scrollX,
        y: Math.abs(body.getBoundingClientRect().top),
        width: window.innerWidth,
        height: window.innerHeight,
        logging: false,
        onclone: function(clone_document_node) {
            clone_document_node.body.style.height = String(new_body_height) + "px";
        },
        ignoreElements: function(element) {
            return easyassist_ignore_element_from_screenshot(element);
        },
    }).then(function(canvas) {
        // Get base64URL
        var img_data = canvas.toDataURL('image/png');
        var img_tag = document.getElementById("screen-capture-img-div").querySelector("img");
        img_tag.src = img_data;
    });
}

function easyassist_report_bug(element) {
    var error_element = document.getElementById("easyassist-report-bug-error")

    var image_data = document.getElementById("screen-capture-img-div").querySelector("img").src;

    if(document.getElementById("checkbox-include-screenshot-text").checked == false){
        image_data = "";
    }

    var bug_description = document.getElementById("bug-description").value;
    bug_description = remove_special_characters_from_str(bug_description);
    bug_description = stripHTML(bug_description);
    if (bug_description == "") {
        error_element.innerHTML = "Please describe your issue in above textbox."
        return;
    }

    if (bug_description.length > 200) {
        error_element.innerHTML = "Issue describe cannot be more than 200 characters."
        return;
    }

    var meta_data = {};
    try{
        meta_data["imp_info"] = {
            "href": window.location.href,
            "internet_speed": avg_speedMbps + " mbps",
        }
        meta_data["variable_value"] = {
            "client_server_websocket_ready_state": client_server_websocket.readyState,
            "sync_search_field_interval": sync_search_field_interval,
            "global_session_id": global_session_id,
            "update_cobrowsing_request_status_interval": update_cobrowsing_request_status_interval,
            "client_server_websocket_open": client_server_websocket_open,
            "client_server_heartbeat_timer": client_server_heartbeat_timer,
            "agent_remarks": agent_remarks,
            "show_request_meeting_modal_toast": show_request_meeting_modal_toast,
            "close_session_id": close_session_id,
            "archive_session_id": archive_session_id,
            "get_active_agent_list_interval": get_active_agent_list_interval,
            "update_all_lead_status_interval": update_all_lead_status_interval,
            "user_last_activity_time_obj": user_last_activity_time_obj,
            "websocket_token": window.WEBSOCKET_TOKEN,
            "active_agent_username": window.ACTIVE_AGENT_USERNAME,
            "easyassist_agent_role": window.EASYASSIST_AGENT_ROLE,
        }
    }catch(err){
        console.log("ERROR : ", err);
    }

    element.innerHTML = "Submitting..."
    error_element.innerHTML = ""
    var request_params = {
        "image_data": image_data,
        "username": window.ACTIVE_AGENT_USERNAME,
        "session_id": null,
        "description": bug_description,
        "meta_data": meta_data,
    }
    var json_params = JSON.stringify(request_params);
    var encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/report-bug/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_element.innerHTML = "Issue reported successfully."
                error_element.style.color = "green";
                setTimeout(function(){
                    $("#report_problem_modal").modal("hide");
                }, 2000);
            } else {
                element.innerHTML = "Submit";
                error_element.innerHTML = "Something went wrong. Please try again."
            }
        } else {
            element.innerHTML = "Submit";
            error_element.innerHTML = "Something went wrong. Please try again."
        }
    }
    xhttp.send(params);
}

$('#report_problem_modal').on('hidden.bs.modal', function () {
    var error_element = document.getElementById("easyassist-report-bug-error")
    error_element.innerHTML = ""
    error_element.style.color = "red";
    var bug_description_element = document.getElementById("bug-description");
    bug_description_element.value = "";
});

/************************* END BUG REPORT *************************/

/************************* START INTERNET SPEED *************************/

var avg_speedMbps = 0;
var speedMbps = 0;
var internet_iteration = 1;

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function check_internet_speed(){

    var image_addr = "https://static.allincall.in/static/EasyAssistApp/img/1MBFile.jpg";
    var download_size = 1093957; //bytes

    var start_time = 0, end_time = 0;
    var download = new Image();
    download.onload = function () {
        end_time = (new Date()).getTime();
        if (end_time > start_time) {
            var duration = (end_time - start_time) / 1000;
            var bitsLoaded = download_size * 8;
            var speedBps = (bitsLoaded / duration).toFixed(2);
            var speedKbps = (speedBps / 1024).toFixed(2);
            speedMbps = (speedKbps / 1024).toFixed(2);
        }
    }

    start_time = (new Date()).getTime();
    var cache_buster = "?nnn=" + start_time;
    download.src = image_addr + cache_buster;
}

async function initiate_internet_speed_detection() {

    var total_value = 0;
    for(let i_index = 0; i_index < internet_iteration; i_index++) {

        check_internet_speed();
        await sleep(5000);
        total_value = parseInt(total_value) + parseInt(speedMbps);
        speedMbps = 0;
    }

    avg_speedMbps = 0;

    if (internet_iteration > 0) {

        avg_speedMbps = (total_value / internet_iteration).toFixed(2);
    }

    // Adding this console for testing purpose
    console.log("Your average internet speed is " + avg_speedMbps + " Mbps.");
}

initiate_internet_speed_detection();

/************************* END INTERNET SPEED *************************/

/************************* START CUSTOMER SIDE SETTINGS *************************/


function easyassist_font_family_list(selected_font) {

    console.log("selected_font = ", selected_font)
    let encrypted_data = {};
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "https://www.googleapis.com/webfonts/v1/webfonts?key=AIzaSyAxUTWdP9EaAtUAdWscKgu8KXLwzW4tXOI", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);

            var html_string = '';
            var font_item_list = [];
            font_item_list = response['items']
            var selected_in_list = false;
            for (let idx = 0; idx < font_item_list.length; idx++) {
                var font_family = font_item_list[idx]['family'];
                if(font_family){
                    var regex = /\s/g;
                    font_family = font_family.replace(regex, "+");
                    if (font_item_list[idx]['family'] == selected_font) {
                        html_string += '<option value=' + font_family + ' selected>' + font_item_list[idx]['family'] + '</option>';
                        selected_in_list = true;
                    } else {
                        html_string += '<option value=' + font_family + '>' + font_item_list[idx]['family'] + '</option>';
                    }
                }
            }
            if(selected_in_list == false){
                html_string += '<option value=' + 'Silka' + ' selected>' + 'Silka'  + '</option>';
            } else {
                html_string += '<option value=' + 'Silka' + '>' + 'Silka'  + '</option>';
            }
            if(document.getElementById("easyassit_font_family")) {
                document.getElementById("easyassit_font_family").innerHTML = html_string;
                $('#easyassit_font_family').selectpicker('refresh');
                easyassist_download_and_apply_test_font();
            }
        }
    }
    xhttp.send(params);
}

function easyassist_download_and_apply_test_font(){
    var selected_font = document.getElementById("easyassit_font_family").value;
    var regex = /[+]/g;
    selected_font = selected_font.replace(regex, " ");
    console.log("selected_font " , selected_font);
    if(selected_font == 'Silka'){
        selected_font = 'Silka, sans-serif'
        document.getElementById("font_test_input").style.fontFamily = selected_font;
        return;
    }

    var css = document.createElement("link");
    css.type = 'text/css';
    css.rel = "stylesheet";
    css.setAttribute("class", "easyassist-client-script");
    css.href = "https://fonts.googleapis.com/css?family=" + selected_font;
    document.getElementsByTagName('head')[0].appendChild(css);
    document.getElementById("font_test_input").style.fontFamily = selected_font;
}

/************************* END CUSTOMER SIDE SETTINGS *************************/

function easyassist_chars_limit_validation(event, label, is_numeric=false) {
    var element = event.target;
    var value = element.value;
    var count = value.length;
    if(!label) {
        label = "Text";
    }

    var allowed_maximum_characters = 25;
    if(is_numeric) {
        allowed_maximum_characters = 4;
    }

    if(count >= allowed_maximum_characters){
        event.preventDefault();
        show_easyassist_toast(label + " should not be more than " + allowed_maximum_characters + " characters");
    }
}

function easyassist_chars_limit_validataion_on_paste(event, label, is_numeric) {
    var element = event.target;
    var value = element.value;

    var clipboard_data = event.clipboardData || event.originalEvent.clipboardData || window.clipboardData;
    var pasted_data = clipboard_data.getData('text') + value;
    var count = pasted_data.length;

    if(!label) {
        label = "Text";
    }

    var allowed_maximum_characters = 25;
    if(is_numeric) {
        allowed_maximum_characters = 4;
    }

    if(count > allowed_maximum_characters){
        event.preventDefault();
        show_easyassist_toast(label + " should not be more than " + allowed_maximum_characters + " characters");
    }
}

var CobrowseSupportLanguage = (function () {
    function CobrowseSupportLanguage(value_list) {
        this.value_list = value_list;
        this.tag_container = document.getElementById("support_language_tag_list");
        this.drag_obj = null;
        this.active_edit_tag = null;
        this.active_edit_input = null;

        this.initialize();
    }
    CobrowseSupportLanguage.prototype.initialize = function(){
        var _this = this;
        var input_element = document.getElementById("input_language_support");
        input_element.addEventListener('keypress', function(event){
            if (event.key === 'Enter' || event.keyCode==13) {
                var new_value = event.target.value;
                new_value = _this.process_tag(new_value);
                var validation = _this.validate_tag(new_value, input_element);
                if(validation == true){
                    _this.add_tag(new_value);
                }
            }
        })
        _this.render_tags();
    }
    CobrowseSupportLanguage.prototype.validate_tag = function(value, input_element=null){
        var _this = this;
        value = _this.process_tag(value);
        if(value == ""){
            show_easyassist_toast("Please enter support language");
            input_element.value = ""
        } else if(value.length < 2) {
            show_easyassist_toast("Support language should be atleast 2 characters long");
            return false;
        } else if(value.length > 25) {
            show_easyassist_toast("Support language should not be more than 25 characters");
            return false;
        } else {
            let numeric_regex = /\d+/;
            if(numeric_regex.test(value)) {
                show_easyassist_toast('Support language cannot be numeric or alphanumeric');
                return false;
            }
            if(_this.value_list.indexOf(value) >= 0){
                show_easyassist_toast('Support language already exist');
                if(input_element){
                    input_element.value = "";
                }
                return false;
            } else {
                if(value.length == 1) {
                    if(input_element){
                        input_element.value = '';
                        input_element.focus();
                    }
                    show_easyassist_toast('Support language tag length should be greater than one');
                    return false;
                }
                if(input_element){
                    input_element.value = '';
                    input_element.focus();
                }
                return true;
            }
        }
    }
    CobrowseSupportLanguage.prototype.process_tag = function(value){
        if(value && value.length==0) return "";

        var processed_value = "";
        processed_value = value.trim().replace( /(<([^>]+)>)/ig, '');
        processed_value = stripHTML(processed_value);
        processed_value = remove_special_characters_from_str(processed_value);
        processed_value = processed_value.toLowerCase();
        if(processed_value.length > 0){
            processed_value = processed_value[0].toUpperCase() + processed_value.substr(1);
        }
        return processed_value;
    }
    CobrowseSupportLanguage.prototype.add_tag = function(new_value){
        var _this = this;
        _this.value_list.push(new_value);
        _this.render_tags();
    }
    CobrowseSupportLanguage.prototype.remove_tag = function(tag_value){
        var _this = this;
        tag_value = _this.process_tag(tag_value);
        if(tag_value.toLowerCase() == "english") {
            show_easyassist_toast("English is default Support Language and Can't be removed")
        } else {
            _this.value_list = _this.value_list.filter(item => _this.process_tag(item) != tag_value);
            _this.render_tags();
        }
    }
    CobrowseSupportLanguage.prototype.update_tag = function(tag_old_value, tag_new_value){
        var _this = this;

        tag_new_value = _this.process_tag(tag_new_value);

        for(let index=0; index<_this.value_list.length; index++){
            if(_this.value_list[index].toLowerCase() == tag_old_value.toLowerCase()){
                _this.value_list[index] = tag_new_value;
            }
        }

        _this.render_tags();
    }
    CobrowseSupportLanguage.prototype.onmouseover_tag = function(element){
        var handler = element.querySelector("svg");
        handler.style.display = "";
    }
    CobrowseSupportLanguage.prototype.onmouseout_tag = function(element){
        var handler = element.querySelector("svg");
        handler.style.display = "none";
    }
    CobrowseSupportLanguage.prototype.render_tags = function(){
        var _this = this;
        _this.tag_container.innerHTML = '';
        _this.value_list.map((item, index) => {
            _this.tag_container.innerHTML += [
                '<li class="bg-primary support-language-li" onmouseover="window.LANGUAGE_TAG_OBJ.onmouseover_tag(this)" onmouseout="window.LANGUAGE_TAG_OBJ.onmouseout_tag(this)">',
                '<svg class="drag-handle" width="14" height="16" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom: 2px; display: none;">',
                    '<path fill-rule="evenodd" clip-rule="evenodd" d="M9.91658 3.5C9.91658 4.14167 9.39158 4.66667 8.74992 4.66667C8.10825 4.66667 7.58325 4.14167 7.58325 3.5C7.58325 2.85834 8.10825 2.33334 8.74992 2.33334C9.39158 2.33334 9.91658 2.85834 9.91658 3.5ZM5.24996 2.33334C4.60829 2.33334 4.08329 2.85834 4.08329 3.50001C4.08329 4.14167 4.60829 4.66667 5.24996 4.66667C5.89163 4.66667 6.41663 4.14167 6.41663 3.50001C6.41663 2.85834 5.89163 2.33334 5.24996 2.33334ZM4.08325 7C4.08325 6.35834 4.60825 5.83334 5.24992 5.83334C5.89159 5.83334 6.41659 6.35834 6.41659 7C6.41659 7.64167 5.89159 8.16667 5.24992 8.16667C4.60825 8.16667 4.08325 7.64167 4.08325 7ZM5.24992 11.6667C5.89159 11.6667 6.41659 11.1417 6.41659 10.5C6.41659 9.85834 5.89159 9.33334 5.24992 9.33334C4.60825 9.33334 4.08325 9.85834 4.08325 10.5C4.08325 11.1417 4.60825 11.6667 5.24992 11.6667ZM8.74992 5.83334C8.10825 5.83334 7.58325 6.35834 7.58325 7C7.58325 7.64167 8.10825 8.16667 8.74992 8.16667C9.39158 8.16667 9.91658 7.64167 9.91658 7C9.91658 6.35834 9.39158 5.83334 8.74992 5.83334ZM7.58325 10.5C7.58325 9.85834 8.10825 9.33334 8.74992 9.33334C9.39158 9.33334 9.91658 9.85834 9.91658 10.5C9.91658 11.1417 9.39158 11.6667 8.74992 11.6667C8.10825 11.6667 7.58325 11.1417 7.58325 10.5Z" fill="white"/>',
                '</svg>',
                '<span style="font-weight: bold;" ondblclick="window.LANGUAGE_TAG_OBJ.start_edit_mode(this)" value_element="true">',
                    item,
                '</span>',
                '<span style="color:white;cursor: pointer;font-weight: bold;vertical-align: text-bottom;" onclick="window.LANGUAGE_TAG_OBJ.remove_tag(\'' + item + '\')"> x </span>',
                '</li>',
            ].join('');
        });
        _this.drag_obj = new CognoAiDragableTagInput(
            _this.tag_container, 
            function(event){
                _this.drag_finish_callback(event)
            }
        );
    }
    CobrowseSupportLanguage.prototype.get_tag_list = function(){
        var _this = this;

        var elements = _this.tag_container.children;
        var tag_list = [];
        for(let index=0; index<elements.length; index++){
            var language_name = elements[index].querySelector("[value_element]").innerHTML;
            tag_list.push(language_name);
        }
        return tag_list;
    }
    CobrowseSupportLanguage.prototype.drag_finish_callback = function(event){
        var _this = this;

        if(_this.active_edit_tag && _this.active_edit_input){
            _this.active_edit_input.insertAdjacentElement("afterend", _this.active_edit_tag);
        }

        var elements = _this.tag_container.children;
        _this.value_list = [];
        for(let index=0; index<elements.length; index++){
            try{
                var language_name = elements[index].querySelector("[value_element]").innerHTML;
                _this.value_list.push(language_name);
            }catch(err){}
        }
    }
    CobrowseSupportLanguage.prototype.start_edit_mode = function(element){
        var _this = this;
        var old_value = element.innerText.trim();

        _this.active_edit_tag = element.closest(".support-language-li");

        // pre condition
        if(old_value.toLowerCase() == "english"){
            show_easyassist_toast("English is default Support Language and Can't be changed")
            return
        }

        // is any element is hiddne then display it
        for(let index=0; index<_this.tag_container.children.length; index++){
            _this.tag_container.children[index].style.display = "";
        }

        // already any other elment is in edit mode then remove that
        var tag_list_input_element = document.querySelectorAll(".tag-list-input-element");
        for(let index=0; index<tag_list_input_element.length; index++){
            tag_list_input_element[index].parentElement.removeChild(tag_list_input_element[index]);
        }

        // hide this li element
        var li_element = element.parentElement;
        li_element.style.display = "none";
        
        // create input for this li element
        var input_element = document.createElement("input");
        input_element.classList.add("tag-list-input-element");
        input_element.value = element.innerText.trim();
        input_element.focus();

        _this.active_edit_input = input_element;

        // insert input element before new hidden element
        _this.tag_container.insertBefore(input_element, li_element);

        // handle keypress event on this new input
        input_element.addEventListener("keypress", function(event){
            if (event.key === 'Enter' || event.keyCode==13) {
                var new_value = event.target.value;

                if(new_value.trim() == ""){
                    event.target.value = "";
                    show_easyassist_toast("Please enter support language");
                    return
                }

                if(old_value.toLowerCase() == new_value.toLowerCase()){
                    _this.render_tags();
                    return
                }

                var validation = _this.validate_tag(new_value, input_element);
                if(validation == true){
                    _this.update_tag(old_value, new_value);
                }
            }
        });
    }
    return CobrowseSupportLanguage;
})();

var CobrowseProductCategory = (function () {
    function CobrowseProductCategory(value_list) {
        this.value_list = value_list;
        this.tag_container = document.getElementById("product_category_tag_list");
        this.drag_obj = null;
        this.active_edit_tag = null;
        this.active_edit_input = null;
        this.initialize();
    }
    CobrowseProductCategory.prototype.initialize = function(){
        var _this = this;
        var input_element = document.getElementById("input_product_category");
        input_element.addEventListener('keypress', function(event){
            if (event.key === 'Enter' || event.keyCode==13) {
                var new_value = event.target.value;
                new_value = _this.process_tag(new_value);
                var validation = _this.validate_tag(new_value, input_element);
                if(validation == true){
                    _this.add_tag(new_value);
                }
            }
        })
        _this.render_tags();
    }
    CobrowseProductCategory.prototype.validate_tag = function(value, input_element=null){
        var _this = this;
        value = _this.process_tag(value);
        
        if(value == ""){
            show_easyassist_toast("Please enter product category");
            input_element.value = ""
        } else if(value.length < 2) {
            show_easyassist_toast("Product category should be atleast 2 characters long");
            return false;
        }  else if(value.length > 25) {
            show_easyassist_toast("Product category should not be more than 25 characters");
            return false;
        } else {
            if (_this.value_list.indexOf(value) >= 0) {
                show_easyassist_toast('Product category already exist');
                return false;
            } else {
                if(input_element){
                    input_element.value = '';
                    input_element.focus();
                }
                return true
            }
        }
    }
    CobrowseProductCategory.prototype.process_tag = function(value){
        if(value && value.length==0) return "";

        var processed_value = "";
        processed_value = value.trim().replace( /(<([^>]+)>)/ig, '');
        processed_value = stripHTML(processed_value);
        processed_value = remove_special_characters_from_str(processed_value);
        processed_value = processed_value.toLowerCase();
        if(processed_value.length > 0){
            processed_value = processed_value[0].toUpperCase() + processed_value.substr(1);
        }
        return processed_value;
    }
    CobrowseProductCategory.prototype.add_tag = function(new_value){
        var _this = this;
        _this.value_list.push(new_value);
        _this.render_tags();
    }
    CobrowseProductCategory.prototype.remove_tag = function(tag_value){
        var _this = this;
        tag_value = _this.process_tag(tag_value);
        _this.value_list = _this.value_list.filter(item => _this.process_tag(item) != tag_value);
        _this.render_tags();
    }
    CobrowseProductCategory.prototype.update_tag = function(tag_old_value, tag_new_value){
        var _this = this;

        tag_new_value = _this.process_tag(tag_new_value);

        for(let index=0; index<_this.value_list.length; index++){
            if(_this.value_list[index].toLowerCase() == tag_old_value.toLowerCase()){
                _this.value_list[index] = tag_new_value;
            }
        }

        _this.render_tags();
    }
    CobrowseProductCategory.prototype.onmouseover_tag = function(element){
        var handler = element.querySelector("svg");
        handler.style.display = "";
    }
    CobrowseProductCategory.prototype.onmouseout_tag = function(element){
        var handler = element.querySelector("svg");
        handler.style.display = "none";
    }
    CobrowseProductCategory.prototype.render_tags = function(){
        var _this = this;
        _this.tag_container.innerHTML = '';
        _this.value_list.map((item, index) => {
            _this.tag_container.innerHTML += [
                '<li class="bg-primary product-category-li" onmouseover="window.PRODUCT_CATEGORY_TAG_OBJ.onmouseover_tag(this)" onmouseout="window.PRODUCT_CATEGORY_TAG_OBJ.onmouseout_tag(this)">',
                    '<svg class="drag-handle" width="14" height="16" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom: 2px; display: none;">',
                        '<path fill-rule="evenodd" clip-rule="evenodd" d="M9.91658 3.5C9.91658 4.14167 9.39158 4.66667 8.74992 4.66667C8.10825 4.66667 7.58325 4.14167 7.58325 3.5C7.58325 2.85834 8.10825 2.33334 8.74992 2.33334C9.39158 2.33334 9.91658 2.85834 9.91658 3.5ZM5.24996 2.33334C4.60829 2.33334 4.08329 2.85834 4.08329 3.50001C4.08329 4.14167 4.60829 4.66667 5.24996 4.66667C5.89163 4.66667 6.41663 4.14167 6.41663 3.50001C6.41663 2.85834 5.89163 2.33334 5.24996 2.33334ZM4.08325 7C4.08325 6.35834 4.60825 5.83334 5.24992 5.83334C5.89159 5.83334 6.41659 6.35834 6.41659 7C6.41659 7.64167 5.89159 8.16667 5.24992 8.16667C4.60825 8.16667 4.08325 7.64167 4.08325 7ZM5.24992 11.6667C5.89159 11.6667 6.41659 11.1417 6.41659 10.5C6.41659 9.85834 5.89159 9.33334 5.24992 9.33334C4.60825 9.33334 4.08325 9.85834 4.08325 10.5C4.08325 11.1417 4.60825 11.6667 5.24992 11.6667ZM8.74992 5.83334C8.10825 5.83334 7.58325 6.35834 7.58325 7C7.58325 7.64167 8.10825 8.16667 8.74992 8.16667C9.39158 8.16667 9.91658 7.64167 9.91658 7C9.91658 6.35834 9.39158 5.83334 8.74992 5.83334ZM7.58325 10.5C7.58325 9.85834 8.10825 9.33334 8.74992 9.33334C9.39158 9.33334 9.91658 9.85834 9.91658 10.5C9.91658 11.1417 9.39158 11.6667 8.74992 11.6667C8.10825 11.6667 7.58325 11.1417 7.58325 10.5Z" fill="white"/>',
                    '</svg>',
                    '<span style="font-weight: bold;" ondblclick="window.PRODUCT_CATEGORY_TAG_OBJ.start_edit_mode(this)" value_element="true">',
                        item,
                    '</span>',
                    '<span style="color:white;cursor: pointer;font-weight: bold;vertical-align: text-bottom;"onclick="window.PRODUCT_CATEGORY_TAG_OBJ.remove_tag(\'' + item + '\')"> x </span>',
                '</li>'
            ].join('');
        });
        _this.drag_obj = new CognoAiDragableTagInput(
            _this.tag_container, 
            function(event){
                _this.drag_finish_callback(event)
            }
        );
    }

    CobrowseProductCategory.prototype.get_tag_list = function(){
        var _this = this;

        var elements = _this.tag_container.children;
        var tag_list = [];
        for(let index=0; index<elements.length; index++){
            var language_name = elements[index].querySelector("[value_element]").innerHTML;
            tag_list.push(language_name);
        }
        return tag_list;
    }
    CobrowseProductCategory.prototype.drag_finish_callback = function(event){
        var _this = this;

        if(_this.active_edit_tag && _this.active_edit_input){
            _this.active_edit_input.insertAdjacentElement("afterend", _this.active_edit_tag);
        }

        var elements = _this.tag_container.children;
        _this.value_list = [];
        for(let index=0; index<elements.length; index++){
            try{
                var language_name = elements[index].querySelector("[value_element]").innerHTML;
                _this.value_list.push(language_name);
            }catch(err){}
        }
    }
    CobrowseProductCategory.prototype.start_edit_mode = function(element){
        var _this = this;
        var old_value = element.innerText.trim();

        _this.active_edit_tag = element.closest(".product-category-li");

        // is any element is hiddne then display it
        for(let index=0; index<_this.tag_container.children.length; index++){
            _this.tag_container.children[index].style.display = "";
        }

        // already any other elment is in edit mode then remove that
        var tag_list_input_element = document.querySelectorAll(".tag-list-input-element");
        for(let index=0; index<tag_list_input_element.length; index++){
            tag_list_input_element[index].parentElement.removeChild(tag_list_input_element[index]);
        }

        // hide this li element
        var li_element = element.parentElement;
        li_element.style.display = "none";
        
        // create input for this li element
        var input_element = document.createElement("input");
        input_element.classList.add("tag-list-input-element");
        input_element.value = element.innerText.trim();
        input_element.focus();

        _this.active_edit_input = input_element;

        // insert input element before new hidden element
        _this.tag_container.insertBefore(input_element, li_element);

        // handle keypress event on this new input
        input_element.addEventListener("keypress", function(event){
            if (event.key === 'Enter' || event.keyCode==13) {
                var new_value = event.target.value;

                if(new_value.trim() == ""){
                    event.target.value = "";
                    show_easyassist_toast("Please enter product category");
                    return
                }

                if(old_value.toLowerCase() == new_value.toLowerCase()){
                    _this.render_tags();
                    return
                }

                var validation = _this.validate_tag(new_value, input_element);
                if(validation == true){
                    _this.update_tag(old_value, new_value);
                }
            }
        });
    }
    return CobrowseProductCategory;
})();

class CognoAiDragableTagInput {
    constructor(container, drag_finish_callback) {
        this.container = container
        this.element = null;
        this.currX = 0;
        this.currY = 0;
        this.clientX = 0;
        this.clientY = 0;
        this.pageX = 0;
        this.offset = 12;
        this.is_dragging = false;
        this.drag_container = null;
        this.prevX = 0;
        this.prevY = 0;
        this.drag_finish_callback = drag_finish_callback;

        var _this = this;

        document.addEventListener("mouseleave", function(e) {
            _this.drag_element('out', e);
            e.preventDefault();
        });

        _this.drag_container = document;

        _this.drag_container.addEventListener("mousemove", function(e) {
            _this.drag_element('move', e);
        });

        _this.drag_container.addEventListener("mouseup", function(e) {
            _this.drag_element('up', e);
        });

        _this.initialize();
    }
    initialize(){
        var _this = this;
        var elements = _this.container.querySelectorAll(".drag-handle");
        if(elements.length == 0){
            elements = _this.container.children;
        }
        for(let index=0; index<elements.length; index++){
            var element = elements[index];
            var target_element = _this.get_target_element(element);

            element.addEventListener("mousedown", function(e) {
                _this.drag_element('down', e);
            });

            element.addEventListener("mouseup", function(e) {
                _this.drag_element('up', e);
            });

            target_element.addEventListener("touchstart", function(e) {
                _this.prevX = e.touches[0].clientX;
                _this.prevY = e.touches[0].clientY;
                _this.drag_element('down', e);
            });

            target_element.addEventListener("touchmove", function(e) {
                var data = {
                    movementX: e.touches[0].clientX - _this.prevX,
                    movementY: e.touches[0].clientY - _this.prevY,
                    clientX: e.touches[0].clientX,
                    clientY: e.touches[0].clientY,
                }
                _this.prevX = e.touches[0].clientX;
                _this.prevY = e.touches[0].clientY;
                _this.drag_element('move', data);
            });

            target_element.addEventListener("touchend", function(e) {
                _this.prevX = 0;
                _this.prevY = 0;
                _this.drag_element('out', e);
            });

            element.style.cursor = "move";
        }
    }
    get_target_element(element){
        var _this = this;
        var handle = element;
        while(handle.parentElement != _this.container)
            handle = handle.parentElement;
        return handle;
    }
    drag_element(direction, e) {
        var _this = this;
        if (direction == 'down') {
            _this.is_dragging = true;
            _this.element = _this.get_target_element(e.target);
            if(!_this.dummy_element){
                _this.dummy_element = document.createElement("span");
                _this.dummy_element.className = "cognoai-drag-dummy-element";
            }
        }

        if (direction == 'up' || direction == "out") {
            if(_this.is_dragging == false) {
                return;
            }

            _this.dummy_element.insertAdjacentElement("beforebegin", _this.element);
            _this.element.classList.remove("cognoai-drag-helper");
            _this.element.style.top = "";
            _this.element.style.left = "";
            _this.currX = 0;
            _this.currY = 0;
            _this.offset = 12;
            _this.is_dragging = false;
            _this.drag_container = null;
            _this.prevX = 0;
            _this.prevY = 0;
            _this.is_dragging = false;

            _this.element = null;
            if(_this.dummy_element.parentElement){
                _this.dummy_element.parentElement.removeChild(_this.dummy_element);
            }
            _this.dummy_element = null;

            if(_this.drag_finish_callback){
                try{
                    _this.drag_finish_callback()
                }catch(err){}
            }
        }

        if (direction == 'move') {
            if (_this.is_dragging) {

                var left = _this.element.offsetLeft;
                var top = _this.element.offsetTop;

                _this.element.classList.add("cognoai-drag-helper");
                _this.currX = e.movementX + left;
                _this.currY = e.movementY + top;

                _this.clientX = e.clientX;
                _this.clientY = e.clientY;

                _this.pageX = e.pageX;

                _this.drag();
                _this.compute();
            }
        }
    }

    drag() {
        var _this = this;

        _this.element.style.left = _this.currX + "px";
        _this.element.style.top = _this.currY + "px";
    }

    compute(){
        var _this = this;

        _this.element.hidden = true;
        let elemBelow = document.elementFromPoint(_this.clientX, _this.clientY);
        _this.element.hidden = false;

        try{
            var target_element = _this.get_target_element(elemBelow);
            if(target_element){

                var pWidth = $(target_element).innerWidth(); //use .outerWidth() if you want borders
                var pOffset = $(target_element).offset(); 
                var x = _this.pageX - pOffset.left;
                if(pWidth/2 > x){
                    target_element.insertAdjacentElement("beforebegin", _this.dummy_element);
                } else {
                    target_element.insertAdjacentElement("afterend", _this.dummy_element);
                }
            }
        } catch(err){}
    }
}

function add_filter_event_listener(){
    var search_boxs = document.querySelectorAll(".dataTables_filter [type=search]");
    search_boxs.forEach((search_box)=>{
        search_box.addEventListener("input", function(event){
            var value = event.target.value;
            var pagination_entry_container = document.querySelector(".show-pagination-entry-container");

            if(pagination_entry_container){
                var showing_entry_count = document.querySelectorAll("tbody tr[role='row']").length;
                var end_point = pagination_entry_container.getAttribute("end_point");
                var start_point = pagination_entry_container.getAttribute("start_point");
                var total_entry = end_point - start_point + 1;

                if(value.length != 0){
                    var text = "Showing " + showing_entry_count + " entries (filtered from " + total_entry + " total entries)";
                    pagination_entry_container.innerHTML = text;
                } else {
                    pagination_entry_container.innerHTML = pagination_entry_container.getAttribute("filter_default_text");
                }
            }
        }); 
    })
}

function get_shorter_file_name(filename, file_name_required_length) {
    if (filename.lastIndexOf(".") > 0) {
        var fileExtension = filename.substring(filename.lastIndexOf("."), filename.length);
        filename = filename.substring(0, file_name_required_length) + "..." + fileExtension;
    } else {
        filename = filename.substring(0, file_name_required_length) + "...";
    }
    return filename;
}

$(document).ready(function() {
    var text_elements = [
        // Text field
        ["font_test_input", "Font text"],
        ["cobrowsing_default_password_prefix", "Password prefix"],
        ["meeting_default_password", "Meeting password"],

        // Number field
        ["maximum_active_leads_threshold", "Maximum leads"],
        ["floating_button_left_right_position", "Icon position"],
        ["no_agent_connects_toast_threshold", "Toast time"],
        ["field_stuck_timer", "Session in-activity time interval"],
        ["recording_expires_in_days", "Screen recording expires days"],
        ["low_bandwidth_cobrowsing_threshold", "Low band network limit"],
        ["drop_link_expiry_time", "Droplink expire time"],
        ["reconnecting_window_timer_input_field", "Reconnecting window timer"],
        ["greeting_bubble_auto_popup_timer", "Number of times greeting bubble pops up"],
        ["inactivity_auto_popup_number", "Number of times connect with an agent auto pop up after in-activity"],

        // chrome extension
        ["extension-name", "Extension name"],
    ];

    text_elements.forEach(function(element_detail) {
        var element_id = element_detail[0];
        var label = element_detail[1];

        var input_element = document.getElementById(element_id);
        if(input_element) {
            var is_numeric = false;
            if(input_element.getAttribute("type") == "number") {
                is_numeric = true;
            }
            input_element.addEventListener("keypress", function(event) {
                easyassist_chars_limit_validation(event, label, is_numeric);
            });

            input_element.addEventListener("paste", function(event) {
                easyassist_chars_limit_validataion_on_paste(event, label, is_numeric);
            });
        }
    });

    if(window.location.pathname.indexOf("/easy-assist/sales-ai/settings") == 0){
        try{
            window.LANGUAGE_TAG_OBJ = new CobrowseSupportLanguage(support_language_array);
        } catch (err){}
        try{
            window.PRODUCT_CATEGORY_TAG_OBJ = new CobrowseProductCategory(product_categories_array);
        } catch (err){}
    }

    add_filter_event_listener();
});

function show_agent_profile_errors(message) {
    document.querySelector(".error-message-div").innerHTML  = message;
    document.querySelector(".error-message-div").style.display = "flex";
}

function hide_agent_profile_errors() {
    document.querySelector(".error-message-div").innerHTML  = "";
    document.querySelector(".error-message-div").style.display = "none";    
}

function upload_agent_profile_picture() {
    var src_file =  agent_profile_input_file_global

    if ((window.profile_picture_source == "" || window.profile_picture_source == undefined) && (src_file == undefined || src_file == "")) {
        show_agent_profile_errors("Please upload a file.");
        return false;
    }

    if(src_file == undefined || src_file == "") {
        $('#upload-profile-pic-Modal').modal('hide');
        return;
    }
    
    var reader = new FileReader();
    reader.readAsDataURL(src_file);
    reader.onload = function() {

        let updated_src = document.querySelector('.updated-profile').src;
        let base64_str = updated_src.split(",")[1];

        var json_string = {
            "filename": src_file.name,
            "base64_file": base64_str,
        };

        json_string = JSON.stringify(json_string);

        let encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        var params = JSON.stringify(encrypted_data);
        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/upload-agent-profile-picture/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) { 
                let response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    $('#upload-profile-pic-Modal').modal('hide');
                        show_easyassist_agent_profile_toast("Profile picture uploaded succesfully",false);
                        setTimeout(() => {
                        window.location.reload();
                        }, 650);
                } else if(response["status"] == 301) {
                    $('#agent-profile-input').val('');
                    show_agent_profile_errors("Please upload a file.");
                } else {
                    $('#agent-profile-input').val('');
                    show_agent_profile_errors("Your uploaded file is corrupted.");
                }
            } 
    }
    xhttp.send(params);

    };

    reader.onerror = function(error) {
        console.log('Error: ', error);
    };
}

function delete_agent_profile_picture() {
    let encrypted_data = "";
    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/delete-agent-profile-picture/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) { 
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                $('#upload-profile-pic-Modal').modal('hide');
                show_easyassist_agent_profile_toast("Profile picture is removed succesfully",true);
                setTimeout(() => {
                    window.location.reload();
                }, 650);
            } else {
                show_easyassist_agent_profile_toast("An issue occured while removing the profile picture.",true);
            }
        }
    }
    xhttp.send(params);
}

function check_for_malicious_agent_profile_picture(src) {
    return new Promise((resolve, reject) => {
        var src_file = agent_profile_input_file_global
        let base64_str = src.split(",")[1];
      
        var json_string = {
          "filename": src_file.name,
          "base64_file": base64_str,
        };
      
        json_string = JSON.stringify(json_string);
      
        let encrypted_data = easyassist_custom_encrypt(json_string);
      
        encrypted_data = {
          "Request": encrypted_data
        };
    
        var params = JSON.stringify(encrypted_data);
        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/check-malicious-agent-profile-picture/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function () {
          if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 300) {
                resolve(true)
            } else {
                resolve(false)
            }
          }
        }
        xhttp.send(params);
    })
  }

function upload_chat_icon() {
    var file = document.getElementById("chat_icon_input").files[0];
    var icon_error = document.getElementById("icon-error-div");
    
    if (!chat_logo_input_file_global || file == undefined || file == null) {
        icon_error.innerHTML = "Please choose a file.";
        $("#icon-error-div").css({"display":"block"});
        chat_logo_input_file_global = undefined;
        return;
    }

    var cleaned_filename = sanitize_filename(file.name)
    if (chat_logo_input_file_global && check_image_file(cleaned_filename, ["png", "PNG"], false) == false) {
        icon_error.innerHTML = "Please upload valid image file. Only '.png' files are allowed.";
        $("#icon-error-div").css({"display":"block"});
        chat_logo_input_file_global = undefined;
        return;
    }

    if (chat_logo_input_file_global && chat_logo_input_file_global.size/1000 > 30) {
        icon_error.innerHTML = "File size cannot exceed 30 KB";
        $("#icon-error-div").css({"display":"block"});
        chat_logo_input_file_global = undefined;
        return;
    }

    var filename = sanitize_filename(file.name);

    var reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = function () {

        let base64_str = reader.result.split(",")[1];

        var json_string = {
            "filename": filename,
            "base64_file": base64_str,
        };

        json_string = JSON.stringify(json_string);

        let encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/upload-chat-bubble-icon/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                let response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    chat_logo_input_file_global = undefined;
                    $(".default-chat-icon").css({"display":"flex"});
                    document.getElementById("default-chat-icon-image").src = '/' + response["file_path"];
                    $(".reset-chat-icon").css({"display":"flex"});
                    $(".reset-icon").css({"display":"none"});
                    $("#icon-error-div").css({"display":"none"});
                    $("#progress-modal-chat-icon").css({"display":"none"});
                    $('#chat_icon_upload_modal').modal("hide");
                    location.reload();
                } else {
                    document.getElementById("icon-error-div").innerHTML = "Unable to upload the icon."
                    chat_logo_input_file_global = undefined;
                }
            }
        }
        xhttp.send(params);

    };
    reader.onerror = function (error) {
        console.log('Error: ', error);
    };
}

function set_default_icon() {

    var xhttp = new XMLHttpRequest();
        xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/reset-chat-bubble-icon/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                let response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    $(".default-chat-icon").css({"display":"none"});
                    $(".reset-icon").css("display","flex");
                    $(".reset-chat-icon").css("display","none")
                    chat_logo_input_file_global = undefined;
                } else {
                    show_easyassist_toast("Unable to reset chat bubble icon.");
                }
            }
        }
        xhttp.send();
}

function remove_chat_icon() {
    $('#chat_icon_upload_modal .file-name-div').html("");
    $('#chat_icon_upload_modal .modal-upload-file').hide();
    document.getElementById("chat_icon_input").value = "";
    chat_logo_input_file_global = undefined;
}

function update_cobrowse_tranfer_agent_logs(session_id){
    json_string = JSON.stringify({
        "session_id": session_id,
    });
    
    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/update-transfer-session-log/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if(response["status"] == 200){
                assign_lead_to_agent(session_id);
            } else {
                show_easyassist_toast("Unable to transfer the session.")
            }
        }
    }
    xhttp.send(params);   
}

function reject_cobrowse_tranfer_agent_lead(session_id){
    json_string = JSON.stringify({
        "session_id": session_id,
        "reject_request": true
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/update-transfer-session-log/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if(response["status"] == 200){
                show_easyassist_toast("Session transfer request rejected")
                setTimeout(function(){
                    location.reload();
                }, 1500)
            } else {
                show_easyassist_toast("Unable to reject the request")
            }
        }
    }
    xhttp.send(params);   
}

// Request in queue functions starts here

function update_active_queue_lead_status() {

    let page_number = parseInt(window.localStorage.getItem("request_in_queue_current_page"));

    if(!page_number) {
        page_number = 1
    }
    
    let request_params = {
        "page_number": page_number
    }
    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);
    
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/get-all-active-queue-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                var cobrowse_request_lead_details = response.cobrowse_request_lead_details
                var request_lead_data_html = ""
                if(cobrowse_request_lead_details) {
                    
                    for (let idx = 0; idx < cobrowse_request_lead_details.length; idx++) {
                        var request_lead_data = cobrowse_request_lead_details[idx];
                        request_lead_data_html += cognoai_create_request_queue_lead_card(request_lead_data);
                    }

                    if(stripHTML(request_lead_data_html) == ""){
                        request_lead_data_html = '<tr class="odd" style="text-align: center;"><td valign="top" colspan="9">No data available in table</td></tr>';
                    }
                    
                    if(document.getElementById("cognoai-unassign-lead-table-body")){
                        document.getElementById("cognoai-unassign-lead-table-body").innerHTML = request_lead_data_html;
                        apply_pagination(response.pagination_data, response.start, response.end, response.total_request_io);
                    }   

                    var assign_button_elements = document.getElementsByClassName("supervisor-assign-button");
                    for(let idx = 0; idx < assign_button_elements.length; idx ++) {
                        assign_button_elements[idx].addEventListener("click", function(event) {
                            var target = event.target;
                            var session_id = target.getAttribute("session_id");
                            var language_pk = target.parentElement.querySelector("input[name=cobrowse-language-pk]").value;
                            var product_category_pk = target.parentElement.querySelector("input[name=cobrowse-product-category-pk]").value;
                            var supervisor_assign_lead_btn = document.getElementById("easy-assist-" + session_id + "-assign_session");
                    
                            get_active_agent_list_live(session_id, language_pk, product_category_pk)
                            show_assign_agent_by_supervisor_modal(supervisor_assign_lead_btn, session_id);
                        });
                    }

                    var total_active_queue_leads = response.total_request_io;

                if(window.localStorage.getItem("requests_in_queue") && window.localStorage.getItem("requests_in_queue") < total_active_queue_leads )
                {
                    play_notification_sound();    
                }
                
                window.localStorage.setItem("requests_in_queue", total_active_queue_leads)

                if (total_active_queue_leads > 0) {
                    document.getElementById("total_request_in_queue").innerHTML = total_active_queue_leads;
                    document.getElementById("request_in_queue_count_bubble_wrapper").classList.remove("easyassist_hidden_div");
                } else {
                    document.getElementById("request_in_queue_count_bubble_wrapper").classList.add("easyassist_hidden_div");
                }

                if (total_active_cobrowse_leads > 0) {
                    document.getElementById("total_cobrowsing_count").innerHTML = total_active_cobrowse_leads;
                    document.getElementById("total_cobrowsing_count").parentElement.style.display = '';
                } else {
                    document.getElementById("total_cobrowsing_count").parentElement.style.display = "none";
                }

                } else {
                    request_lead_data_html = '<tr class="odd"><td valign="top" colspan="9" style="text-align:center !important" >No data available in table</td></tr>';
                    if(document.getElementById("cognoai-unassign-lead-table-body")){
                        document.getElementById("cognoai-unassign-lead-table-body").innerHTML = request_lead_data_html;
                    }
                    window.localStorage.removeItem("requests_in_queue")
                }
            }

        }
    }
    xhttp.send(params);
}

function assign_cobrowsing_session_to_agent(element, session_id) {

    let assign_agent_element = document.getElementById("select-assign-agent");

    let request_params = {
        "session_id": session_id,
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);
    element.innerHTML = "Assigning...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/self-assign-cobrowsing-session/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                easyassist_show_long_toast(" Lead has been successfully assigned to "+ response["agent_username"]+".",3000)
                update_active_queue_lead_status();
            } else if (response["status"] == 501) {
                easyassist_show_long_toast(" Lead has been already assigned to "+ response["agent_username"]+".",3000)
                update_active_queue_lead_status();
            } else if (response["status"] == 400) {
                easyassist_show_long_toast("Failed to assign session. Agent is offline.", 3000);
            } else if (response["status"] == 401) {
                easyassist_show_long_toast("Maximum lead capacity reached, please end an ongoing session and try again later.", 3000);
            } else {
                easyassist_show_long_toast("Internal server error.",3000)
            }
        }
        element.innerHTML = "Assign to me";
    }
    xhttp.send(params);
}

function easyassist_show_long_toast(message, time) {
    // This will not work beyond 8 sec
    var easyassist_snackbar_custom = document.getElementById("easyassist-snackbar");
    easyassist_snackbar_custom.innerHTML = message;
    easyassist_snackbar_custom.className = "show";

    setTimeout(function () {
        easyassist_snackbar_custom.className = easyassist_snackbar_custom.className.replace("show", "");
    }, time);
}

function cognoai_create_request_queue_lead_card(lead_data) {
    var cognoai_lead_card_html = "";
    try{
        let is_agent_active = false;
        if(document.getElementById("checkbox-mark-as-active")){
            is_agent_active = document.getElementById("checkbox-mark-as-active").checked;
        }

        cognoai_lead_card_html += '<td data-content="Customer Details" id="easy-assist-' + lead_data.session_id + '-customer-details">Name: ' + lead_data.full_name + '<br> Mobile Number: ' + lead_data.mobile_number + '</td>'
        

        // Product
        var product_name = lead_data.product_name;
        var product_name_slice = product_name.slice(0,40);
        if(product_name.length > product_name_slice.length){
            product_name_slice += "...";
        }
        cognoai_lead_card_html += '<td data-content="Product" id="easy-assist-' +  lead_data.session_id + '-product"><a href="' + lead_data.product_url + '" target="_blank">' + product_name_slice + '</a></td>'


        // Category
        if(!lead_data.allow_agent_to_customer_cobrowsing){
            if(lead_data.choose_product_category){
                cognoai_lead_card_html += '<td data-content="Category" id="easy-assist-' +  lead_data.session_id + '-product-category">';
                if(lead_data.product_category){
                    cognoai_lead_card_html += lead_data.product_category;
                } else {
                    cognoai_lead_card_html += '-';
                }
                cognoai_lead_card_html += '</td>';
            }
        }


        // Language
        if(lead_data.allow_language_support){
                cognoai_lead_card_html += '<td data-content="Language" id="easy-assist-' +  lead_data.session_id + '-support-language">';
                if(lead_data.supported_language){
                    cognoai_lead_card_html += lead_data.supported_language;
                } else {
                    cognoai_lead_card_html += '-';
                }
                cognoai_lead_card_html += '</td>';
            }
    
        // Request DateTime
        cognoai_lead_card_html += '<td data-content="Request Date & Time" id="easy-assist-' +  lead_data.session_id + '-request-datetime">' + lead_data.request_datetime + '</td>';

        // Queue Time
        cognoai_lead_card_html += '<td data-content="Queue Time" id="easy-assist-' +  lead_data.session_id + '-time-duration">' + lead_data.queue_time + '</td>'
        
        if(EASYASSIST_AGENT_ROLE == 'agent'){
            
            if(is_agent_active) {
                cognoai_lead_card_html += [
                    '<td data-content="Assign Lead" id="easy-assist-' +  lead_data.session_id + '-assign_session">',
                        '<button class="btn btn-primary btn-sm" onclick="assign_cobrowsing_session_to_agent(this,\'' + lead_data.session_id + '\')">Assign to me</button>',
                    '</td>'
                ].join('');
            } else {
                cognoai_lead_card_html += [
                    '<td data-content="Assign Lead" id="easy-assist-' +  lead_data.session_id + '-assign_session">',
                        '<button class="btn btn-primary btn-sm" disabled>Assign to me</button>',
                    '</td>'
                ].join('');
            }
        }

        if(EASYASSIST_AGENT_ROLE != "admin" && EASYASSIST_AGENT_ROLE != "agent"){
            var language_pk = lead_data.supported_language_pk;
            var product_category_pk = lead_data.product_category_pk;
    
            if(language_pk == null) {
                language_pk = "";
            }
    
            if(product_category_pk == null) {
                product_category_pk = "";
            }
    
            cognoai_lead_card_html += `
                <td id="easy-assist-${lead_data.session_id}-assign_session">
                    <input type="hidden" name="cobrowse-language-pk" value='${language_pk}'>
                    <input type="hidden" name="cobrowse-product-category-pk" value='${product_category_pk}'>
                    <button session_id='${lead_data.session_id}' class="btn btn-primary btn-sm supervisor-assign-button">Assign Session</button>
                </td>`;
        }        

        cognoai_lead_card_html += '</tr>';
    } catch (err) {
        console.log("ERROR: cognoai_create_request_queue_lead_card ", err);
        cognoai_lead_card_html = "";
    }
    return cognoai_lead_card_html;
}

function assign_lead_by_supervisor_adminally(element, session_id) {

    var error_element = document.getElementById("assign-session-error");
    error_element.innerHTML = "";
    error_element.style.display = "none";

    var assign_agent_element = document.getElementById("select-assign-agent");
    let agent_id = assign_agent_element.value;
    if (agent_id == undefined || agent_id.length == 0) {
        error_element.innerHTML = "No Agent Selected. Please Select an Agent";
        error_element.style.display = "block";
        return;
    }

    let json_string = JSON.stringify({
        "session_id": session_id,
        "agent_id": agent_id,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/assign-queue-lead/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                easyassist_show_long_toast(response.message, 3000);
                $('#assign_session_modal').modal('hide');
                update_active_queue_lead_status();
            } else if (response["status"] == 307) {
                error_element.innerHTML = response.message;
                error_element.style.color = "red";
                error_element.style.display = "block";
                update_active_queue_lead_status();
            } else if(response.status == 501) {
                error_element.innerHTML = response.message;
                error_element.style.color = "red";
                error_element.style.display = "block";
            } else if (response.status == 301 || response.status == 302 || response.status == 303 || response.status == 304) {
                error_element.innerHTML = response.message;
                error_element.style.color = "red";
                error_element.style.display = "block";
            } else {
                easyassist_show_long_toast("Unable to assign the lead.", 2000);
            }
        }
    }
    xhttp.send(params);
}

function apply_pagination(pagination, start, end, total_objs) {
    let html = `<div class="row mt-3">`
                
    if (pagination.has_other_pages) {
        html += `<div class="col-md-6 col-sm-12 show-pagination-entry-container" filter_default_text="Showing 1 to 20 of 22 entries" start_point="1" end_point="20">
                Showing ${start} to ${end} entries out of ${total_objs}
                </div>
                <div class="col-md-6 col-sm-12">
                <div class="d-flex justify-content-end">
                <nav aria-label="Page navigation example">
                    <ul class="pagination">
                    <li id="previous-button" class="disabled page-item">
                        <span>
                            <a class="previous-button page-link" href="javascript:void(0)" aria-label="Previous">
                                <span aria-hidden="true">Previous</span>
                                <span class="sr-only">Previous</span>
                            </a>
                        </span>
                    </li>`;

        for (let page = 1; page < pagination.page_range; ++page) {
            if (pagination.number == page) {
                if (page == 1) {
                    html += `<li class="purple darken-3 active page-item" id="page-${page}" ><a data-page="${page}" class="queue-pagination purple darken-3 page-item page-link" href="javascript:void(0)">${page}</a></li>`;
                } else if (pagination.num_pages == page) {
                    html += `<li class="purple darken-3 page-item active" id="page-${page}" style="border-radius: 0 6px 6px 0;"><a data-page="${page}" class="queue-pagination purple darken-3 page-item page-link" href="javascript:void(0)">${page}</a></li>`;
                } else {
                    html += `<li class="active purple darken-3 page-item" style="border-radius: 0px;" id="page-${page}"><a data-page="${page}" class="queue-pagination purple darken-3 page-item page-link" href="javascript:void(0)">${page}</a></li>`;
                }
            } else if (page > pagination.number - 5 && page < pagination.number + 5) {
                html += `<li class="purple darken-3 page-item" id="page-${page}"><a class="queue-pagination purple darken-3 page-item page-link" href="javascript:void(0)" data-page="${page}">${page}</a></li>`;
            }
        }
        html += `<li id="next-button" class="page-item">
                    <a class="next-button page-link" href="javascript:void(0)" aria-label="Next">
                        <span aria-hidden="true">Next</span>
                        <span class="sr-only">Next</span>
                    </a>
                </li>
                </ul>
                </nav>
                </div>
                </div>`;
    } else {
        html += `</div>`
    }

    document.getElementById("table-pagination_div").innerHTML = html;

    add_pagination_events(pagination.page_range);
}

function add_pagination_events(page_range) {
    let previous_button_ele = document.getElementById("previous-button");
    let next_button_ele = document.getElementById("next-button");
    $(".queue-pagination").on("click", (event) => {
        var current_page = event.target.dataset.page;
        if(document.getElementById('page-'+current_page.toString())) {
            $('#page-'+current_page.toString()).css({"background": "black"});
        }
        if(current_page > 1) {
            if(document.getElementById('page-'+(current_page-1).toString())) {
                document.getElementById('page-'+(current_page-1).toString()).classList.remove("active");
            }
        }
        window.localStorage.setItem("request_in_queue_current_page", current_page);
        if(parseInt(window.localStorage.getItem("request_in_queue_current_page")) > 1) {
            if(previous_button_ele && previous_button_ele.classList.contains("disabled")) {
                previous_button_ele.classList.remove("disabled");
            }
        } else {
            if(previous_button_ele && !previous_button_ele.classList.contains("disabled")) {
                document.getElementById("previous-button").classList.add("disabled");
            }
        }
    
        if(parseInt(window.localStorage.getItem("request_in_queue_current_page")) < page_range - 1) {
            if(next_button_ele && next_button_ele.classList.contains("disabled")) {
                document.getElementById("next-button").classList.remove("disabled");
            }
        } else {
            if(!next_button_ele && next_button_ele.classList.contains("disabled")) {
                document.getElementById("next-button").classList.add("disabled");
            }
        }
        update_active_queue_lead_status();
    });

    if(parseInt(window.localStorage.getItem("request_in_queue_current_page")) > 1) {
        if(previous_button_ele && previous_button_ele.classList.contains("disabled")) {
            previous_button_ele.classList.remove("disabled");
        }
        $(".previous-button").on("click", (event) => {
            let page_number = parseInt(window.localStorage.getItem("request_in_queue_current_page")) - 1;        
            window.localStorage.setItem("request_in_queue_current_page", page_number);
            update_active_queue_lead_status();
        });
    } else {
        if(previous_button_ele && !previous_button_ele.classList.contains("disabled")) {
            document.getElementById("previous-button").classList.add("disabled");
        }
    }

    if(parseInt(window.localStorage.getItem("request_in_queue_current_page")) < page_range-1) {
        if(next_button_ele && next_button_ele.classList.contains("disabled")) {
            document.getElementById("next-button").classList.remove("disabled");
        }
        $(".next-button").on("click", (event) => {
            let page_number = parseInt(window.localStorage.getItem("request_in_queue_current_page")) + 1;        
            window.localStorage.setItem("request_in_queue_current_page", page_number);
            update_active_queue_lead_status()
        });
    } else {
        if(next_button_ele && !next_button_ele.classList.contains("disabled")) {
            document.getElementById("next-button").classList.add("disabled");
        }
    }
}

$(".assign_agent_session_modal").on("hidden.bs.modal", function() {
    for (let session_id_key in get_active_agent_list_interval) {
        clearInterval(get_active_agent_list_interval[session_id_key]);
    }
});

// Request in queue functions ends here

$(".transfer_session_modal").on("hidden.bs.modal", function() {
    for (let session_id_key in get_active_agent_list_interval) {
        clearInterval(get_active_agent_list_interval[session_id_key]);
    }
});

function update_active_lead_count() {

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/get-all-active-lead-count/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {    
                
                let total_active_leads = response["total_active_leads"]

                if (total_active_leads > 0) {
                    document.getElementById("total_cobrowsing_count").innerHTML = total_active_leads;
                    document.getElementById("total_cobrowsing_count").parentElement.style.display = '';
                } else {
                    document.getElementById("total_cobrowsing_count").parentElement.style.display = "none";
                }

                if(window.ENABLE_REQUEST_IN_QUEUE == "True") {
                    let total_active_queue_leads = response.total_active_requests_in_queue;

                    if(window.localStorage.getItem("requests_in_queue") && window.localStorage.getItem("requests_in_queue") < total_active_queue_leads )
                    {
                        play_notification_sound();    
                    }
                    
                    window.localStorage.setItem("requests_in_queue", total_active_queue_leads)

                    if (total_active_queue_leads > 0) {
                        document.getElementById("total_request_in_queue").innerHTML = total_active_queue_leads;
                        document.getElementById("request_in_queue_count_bubble_wrapper").classList.remove("easyassist_hidden_div");
                    } else {
                        document.getElementById("request_in_queue_count_bubble_wrapper").classList.add("easyassist_hidden_div");
                    }
                }

            } else {
                console.log("Unable to update the active lead count");
            }
        }
    }
    xhttp.send("{}");
}

function generate_cognomeet_access_token() {
    if(window.IS_COGNOMEET_ACCESS_TOKEN_GENERATED != "False") {
        return;
    }

    if(window.ADMIN_AGENT_USERNAME == "" || window.ADMIN_AGENT_USERNAME == undefined) {
        return;
    }

    let request_params = {
        "admin_agent_username": window.ADMIN_AGENT_USERNAME
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/cogno-meet/create-access-token/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                save_cognomeet_access_token(response.access_token_key);
            } else {
                console.log(response);
            }
        }
    }
    xhttp.send(params);
}

function save_cognomeet_access_token(access_token) {

    let request_params = {
        "cogno_meet_access_token": access_token
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/save-cognomeet-access-token/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                console.log("Access token saved!")
            } else {
                console.log(response);
            }
        }
    }
    xhttp.send(params);
}

function start_proxy_cobrowsing_session(element) {

    let website_url = document.getElementById("proxy-cobrowse-website-url-data").value;
    let customer_name = document.getElementById("proxy-cobrowse-customer-name-data").value.trim();
    let customer_mobile = document.getElementById("proxy-cobrowse-customer-mobile-data").value.trim();
    let customer_email_id = document.getElementById("proxy-cobrowse-customer-email-data").value.trim();
    let url_error_element = document.getElementById("generate-proxy-drop-link-url-error");
    let name_error_element = document.getElementById("generate-proxy-drop-link-name-error");
    let mobile_error_element = document.getElementById("generate-proxy-drop-link-mobile-error");
    let email_error_element = document.getElementById("generate-proxy-drop-link-email-error");
    
    url_error_element.innerHTML = "";
    name_error_element.innerHTML = "";
    mobile_error_element.innerHTML = "";
    email_error_element.innerHTML = "";

    if(!website_url.length){
        url_error_element.innerHTML = "Please enter website url.";
        return;
    }

    if (!is_droplink_url_valid(website_url)) {
        url_error_element.innerHTML = "Please enter a valid website url";
        return;
    }

    if(!customer_name.length){
        name_error_element.innerHTML = "Please enter customer name.";
        return;
    }

    if(!check_valid_name(customer_name)){
        name_error_element.innerHTML = "Please enter a valid customer name.";
        return;
    }

    if(!customer_mobile){
        mobile_error_element.innerHTML = "Please enter customer mobile number.";
        return;
    }


    if(!check_valid_mobile_number(customer_mobile)){
        mobile_error_element.innerHTML = "Please enter a valid 10 digit mobile number.";
        return;
    }

    if(customer_email_id && !check_valid_email(customer_email_id)){
        email_error_element.innerHTML = "Please enter a valid customer email id.";
        return;
    }

    let json_params = JSON.stringify({
        "website_url": website_url,
        "customer_name": sanitize_input_string(customer_name),
        "customer_mobile": customer_mobile,
        "customer_email_id": sanitize_input_string(customer_email_id)
    });

    let encrypted_data = easyassist_custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    element.innerHTML = "Generating.."

    const params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/cognoai-cobrowse/initialize/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                document.getElementById("proxy-drop-link").value = response.generated_link;
                document.getElementById("proxy-cobrowse-start-session-link-cancel").style.display = "none";
                document.getElementById("proxy-cobrowse-start-session-link-button").innerHTML = "Close";
                document.getElementById("proxy-cobrowse-start-session-link-button").setAttribute("onclick","refresh_page()");
                document.getElementById("success-message-div").classList.remove("d-none");
                let modal_body_element = document.getElementById("start-proxy-cobrowse-session-body");
                modal_body_element.scrollBehavior = "smooth"
                modal_body_element.scrollTop = modal_body_element.scrollHeight;
            } else if(response.status == 301){
                url_error_element.innerHTML = response.message;
            } else if(response.status == 302){
                email_error_element.innerHTML = response.message;
            } else if(response.status == 303){
                mobile_error_element.innerHTML = response.message;
            } else if(response.status == 304){
                name_error_element.innerHTML = response.message;
            } else if(response.status == 305){
                url_error_element.innerHTML = response.message;
            } else {
                show_easyassist_toast("Not able to start cobrowsing. Please try again.");
            }
        }
    }
    element.innerHTML = "Generate Link"
    xhttp.send(params);
}

function copy_shareable_link_to_clipboard(id) {
    let copy_text = document.getElementById(id);
    copy_text.select();
    copy_text.setSelectionRange(0, 99999); /* For mobile devices */

    navigator.clipboard.writeText(copy_text.value);
    show_easyassist_toast("Shareable link has been copied");
}

class EasyAssistPaginator {
    /*
        paginator_div_id: Paginator div id in which we want to add the next and previous button.
        storage_obj_name: Name of the local storage key against which we need to save the page number.
        callback_function: The function which will be called on the click of the next and previous button.
        class_name: The class name which is present on the page number buttons at the bottom of the table 
                    on which we want to add on click listeners. These listeners would call an API to get 
                    the data of the selected page. For eg:- active-customer      
        paginated_data: It is the paginated data which contains all the details related to the pagination.
        start: It is the starting page number to be shown at the bottom of the table.
        end: It is the ending page number to be shown at the bottom of the table.
        total_objs: It is the total number of data to be shown inside the table and entries.
    */

    constructor(paginator_div_id, storage_obj_name, callback_function, class_name, paginated_data, start, end, total_objs) {
        let paginator_div = document.getElementById(paginator_div_id);
        this.paginator_div = paginator_div;
        this.apply_pagination(paginated_data, start, end, total_objs, class_name);
        this.add_pagination_events(paginated_data.page_range, class_name, storage_obj_name, callback_function);
    }

    apply_pagination(paginated_data, start, end, total_objs, class_name) {
        let html = `<div class="row mt-3">`
                    
        if (paginated_data.has_other_pages) {
            html += `<div class="col-md-6 col-sm-12 show-pagination-entry-container">
                    Showing ${start} to ${end} entries out of ${total_objs}
                    </div>
                    <div class="col-md-6 col-sm-12">
                    <div class="d-flex justify-content-end">
                    <nav aria-label="Page navigation example">
                        <ul class="pagination">
                        <li id="previous-button" class="disabled page-item">
                            <span>
                                <a class="previous-button page-link" href="javascript:void(0)" aria-label="Previous">
                                    <span aria-hidden="true">Previous</span>
                                    <span class="sr-only">Previous</span>
                                </a>
                            </span>
                        </li>`;
    
            for (let page = 1; page < paginated_data.page_range; ++page) {
                if (paginated_data.number == page) {
                    if (page == 1) {
                        html += `<li class="purple darken-3 active page-item" id="page-${page}" ><a data-page="${page}" class="${class_name} purple darken-3 page-item page-link" href="javascript:void(0)">${page}</a></li>`;
                    } else if (paginated_data.num_pages == page) {
                        html += `<li class="purple darken-3 page-item active" id="page-${page}" style="border-radius: 0 6px 6px 0;"><a data-page="${page}" class="${class_name} purple darken-3 page-item page-link" href="javascript:void(0)">${page}</a></li>`;
                    } else {
                        html += `<li class="active purple darken-3 page-item" style="border-radius: 0px;" id="page-${page}"><a data-page="${page}" class="${class_name} purple darken-3 page-item page-link" href="javascript:void(0)">${page}</a></li>`;
                    }
                } else if (page > paginated_data.number - 5 && page < paginated_data.number + 5) {
                    html += `<li class="purple darken-3 page-item" id="page-${page}"><a class="${class_name} purple darken-3 page-item page-link" href="javascript:void(0)" data-page="${page}">${page}</a></li>`;
                }
            }
            html += `<li id="next-button" class="page-item">
                        <a class="next-button page-link" href="javascript:void(0)" aria-label="Next">
                            <span aria-hidden="true">Next</span>
                            <span class="sr-only">Next</span>
                        </a>
                    </li>
                    </ul>
                    </nav>
                    </div>
                    </div>`;
        } else {
            html += `</div>`
        }
    
        this.paginator_div.innerHTML = html;
    }
    
    add_pagination_events(page_range, class_name, storage_obj_name, callback_function) {
        let previous_button_ele = document.getElementById("previous-button");
        let next_button_ele = document.getElementById("next-button");
        $("." + class_name).on("click", (event) => {
            let current_page = event.target.dataset.page;
            if(document.getElementById('page-'+current_page.toString())) {
                $('#page-'+current_page.toString()).css({"background": "black"});
            }
            if(current_page > 1) {
                if(document.getElementById('page-'+(current_page-1).toString())) {
                    document.getElementById('page-'+(current_page-1).toString()).classList.remove("active");
                }
            }
            window.localStorage.setItem(storage_obj_name, current_page);
            if(parseInt(window.localStorage.getItem(storage_obj_name)) > 1) {
                if(previous_button_ele && previous_button_ele.classList.contains("disabled")) {
                    previous_button_ele.classList.remove("disabled");
                }
            } else {
                if(previous_button_ele && !previous_button_ele.classList.contains("disabled")) {
                    document.getElementById("previous-button").classList.add("disabled");
                }
            }
        
            if(parseInt(window.localStorage.getItem(storage_obj_name)) < page_range - 1) {
                if(next_button_ele && next_button_ele.classList.contains("disabled")) {
                    document.getElementById("next-button").classList.remove("disabled");
                }
            } else {
                if(!next_button_ele && next_button_ele.classList.contains("disabled")) {
                    document.getElementById("next-button").classList.add("disabled");
                }
            }

            callback_function();
        });
    
        if(parseInt(window.localStorage.getItem(storage_obj_name)) > 1) {
            if(previous_button_ele && previous_button_ele.classList.contains("disabled")) {
                previous_button_ele.classList.remove("disabled");
            }
            $(".previous-button").on("click", (event) => {
                let page_number = parseInt(window.localStorage.getItem(storage_obj_name)) - 1;        
                window.localStorage.setItem(storage_obj_name, page_number);
                callback_function();
            });
        } else {
            if(previous_button_ele && !previous_button_ele.classList.contains("disabled")) {
                document.getElementById("previous-button").classList.add("disabled");
            }
        }
    
        if(parseInt(window.localStorage.getItem(storage_obj_name)) < page_range-1) {
            if(next_button_ele && next_button_ele.classList.contains("disabled")) {
                document.getElementById("next-button").classList.remove("disabled");
            }
            $(".next-button").on("click", (event) => {
                let page_number = parseInt(window.localStorage.getItem(storage_obj_name)) + 1;        
                window.localStorage.setItem(storage_obj_name, page_number);
                callback_function();
            });
        } else {
            if(next_button_ele && !next_button_ele.classList.contains("disabled")) {
                document.getElementById("next-button").classList.add("disabled");
            }
        }
    }
}

function create_active_agent_details_card(agent_details, previous_selected_rows, filter_online) {
    let agent_card_html = "<tr>";
    
    if(window.agent_role == "admin") {
        let checked_status = "";

        if(previous_selected_rows.has(agent_details.pk.toString())) {
            checked_status = "checked";
        }
        
        agent_card_html += `<td class="align-middle text-center" id="table-checkbox-td">
                                <label style="padding-left: 18px;" class="easyassist-switch-checkbox-label">
                                    <input type="checkbox" class="easyassist-switch-checkbox-label user-checkbox-collection" id="checkbox-user-${agent_details.pk }" agent_pk="${agent_details.pk }" ${checked_status} autocomplete="off">
                                    <input type="hidden" value="${ agent_details.is_account_active }" >
                                    <span class="easyassist-switch-checkbox"></span>
                                </label>
                            </td>`;        
    }

    agent_card_html += `<td data-content="Name" class="align-middle">
                            <div class="table-max-min-width">
                                ${agent_details.first_name}
                                <div class="d-none" id="mobile-view-edit-button">
                                    <a onclick="populate_agent_details('${agent_details.pk}', '${agent_details.first_name}', '${agent_details.email}', '${agent_details.mobile_number}', '${agent_details.assign_followup_leads}', '${agent_details.supported_languages}', '${agent_details.product_categories}', '${agent_details.supervisors}', '${agent_details.support_level}')" style="margin-top: -2rem;display: inline-block;margin-right: 0.5em;">
                                        <svg class="svg-hide-on-desktop" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M17.0604 0.939564C18.3132 2.19232 18.3132 4.22343 17.0604 5.47618L6.33146 16.2052C6.08325 16.4534 5.77457 16.6325 5.43593 16.7249L0.849981 17.9756C0.348084 18.1124 -0.112448 17.6519 0.0244331 17.15L1.27515 12.5641C1.3675 12.2254 1.54664 11.9167 1.79484 11.6685L12.5238 0.939564C13.7766 -0.313188 15.8077 -0.313188 17.0604 0.939564ZM11.6547 3.7104L2.74567 12.6194C2.66293 12.7021 2.60322 12.805 2.57244 12.9179L1.6313 16.3687L5.08212 15.4276C5.195 15.3968 5.2979 15.3371 5.38063 15.2543L14.2894 6.34506L11.6547 3.7104ZM13.4746 1.89039L12.6049 2.75927L15.2396 5.39482L16.1096 4.52535C16.8372 3.79773 16.8372 2.61802 16.1096 1.89039C15.382 1.16277 14.2023 1.16277 13.4746 1.89039Z"/>
                                        </svg>
                                    </a>
                                </div>
                            </div>
                        </td>
                        <td data-content="Email ID" class="align-middle table-max-min-width">${ agent_details.email }</td>
                        <td data-content="Mobile" class="align-middle">`;
    
    if(agent_details.mobile_number) {
        agent_card_html += `${agent_details.mobile_number}`;
    } else {
        agent_card_html += `-`;
    }

    agent_card_html += "</td>";

    if(agent_details.choose_product_category || agent_details.enable_tag_based_assignment_for_outbound ) {
        agent_card_html += `<td data-content="Category" class="align-middle">
            <div data-toggle="tooltip" class="truncate-text" title="${ agent_details.product_categories}" data-placement="bottom" style="white-space: nowrap;">`;
    
        if(agent_details.product_categories) {
            agent_card_html += `${agent_details.product_categories}`;
        } else {
            agent_card_html += '-';
        }
            
        agent_card_html += `</div>
                        </td>`;
    }

    if(agent_details.allow_language_support) {
        agent_card_html += `<td data-content="Language" class="align-middle">
            <div data-toggle="tooltip" class="truncate-text" title="${agent_details.supported_languages}" data-placement="bottom">`;
    
        if(agent_details.supported_languages) {
            agent_card_html += `${agent_details.supported_languages}`;
        } else {
            agent_card_html += '-';
        }
            
        agent_card_html += `</div>
                        </td>`;
    }

    agent_card_html += '<td data-content="Status" class="align-middle">';
    if(agent_details.is_active && agent_details.is_online && filter_online || 
        agent_details.allow_agent_to_customer_cobrowsing && agent_details.is_active) {
        agent_card_html += '<p class="mb-0" style="color:#38B27F; font-weight: 500;">Online</p>';
    } else if(agent_details.is_active && agent_details.is_online) {
        if(!agent_details.allow_agent_to_customer_cobrowsing && agent_details.is_cobrowsing_active || agent_details.is_cognomeet_active) {
            agent_card_html += '<p class="mb-0" style="color:#F5C828; font-weight: 500;">Busy</p>';
        } else if(!agent_details.allow_agent_to_customer_cobrowsing) {
            agent_card_html += '<p class="mb-0" style="color:#0254D7; font-weight: 500;">Available</p>';
        } else {
            agent_card_html += '<p class="mb-0" style="color:#38B27F; font-weight: 500;">Online</p>';
        }
    } else {
        agent_card_html += '<p class="mb-0" style="color:#858796; font-weight: 500;">Offline</p>';
    }

    agent_card_html += '</td>';
    let disabled_class = "";
    if(window.agent_role != "admin_ally") {
        let agent_status = "";
        if(!agent_details.is_account_active) {
            disabled_class = "toggle-disabled"; 
            agent_status += `<input class="toggle-disabled" type="checkbox" id="toggle-agent-${agent_details.pk}-status" disabled></input>`;
        } else if(agent_details.is_active && agent_details.is_online) {
            agent_status += `<input type="checkbox" id="toggle-agent-${agent_details.pk}-status" onclick="toggle_agent_status(this, ${agent_details.pk})" checked></input>`;
        } else if(agent_details.is_active && agent_details.allow_agent_to_customer_cobrowsing) {
            agent_status += `<input type="checkbox" id="toggle-agent-${agent_details.pk}-status" onclick="toggle_agent_status(this, ${agent_details.pk})" checked></input>`;
        } else {
            agent_status += `<input type="checkbox" id="toggle-agent-${agent_details.pk}-status" onclick="toggle_agent_status(this, ${agent_details.pk})"></input>`;
        }
        agent_card_html += `<td data-content="Mark as active" class="align-middle agent-status-toggle min-width">                                        
                <label class="easyassist-custom-toggle-switch ${disabled_class}">
                    ${agent_status}
                    <span class="easyassist-custom-toggle-slider easyassist-custom-toggle-round"></span>
                </label>
            </td>`;
    }

    agent_card_html += '<td data-content="Account Status" class="align-middle">';

    if(agent_details.is_account_active) {
        agent_card_html += '<p class="mb-0" style="color:#38B27F; font-weight: 500;">Active</p>';
    } else {
        agent_card_html += '<p class="mb-0" style="color:#F56565; font-weight: 500;">Inactive</p>';
    }
    
    agent_card_html += '</td>';

    if(window.agent_role == "admin_ally") {
        agent_card_html += `<td data-content="Supervisors" class="align-middle">
            <div data-toggle="tooltip" title="${agent_details.supervisors }" data-placement="bottom" class="easyassist-supervisor-list-ellips" style="max-width: 150px;">`;
        
        if(agent_details.supervisors) {
            agent_card_html += agent_details.supervisors;
        } else {
            agent_card_html += '-';
        }
        
        agent_card_html += `</div>
                        </td>`;
    }
    if(window.agent_role != "agent") {
        agent_card_html += `<td class="align-middle admin-view-agent-btn">
                <a style="white-space: nowrap;" class="" href="javascript:void(0)" data-toggle="modal" data-target="#resend-password-modal" onclick="resend_password_agent('${agent_details.pk}')" id="resend-password-btn-${ agent_details.pk }">Resend Password</a>
            </td>
            <td class="align-middle td-hide-on-small-device">
                <div class="align-middle edit-delete-btn-class" style="visibility: hidden;display: flex;">
                    <a data-toggle="tooltip" data-placement="bottom" title="Edit" style="cursor: pointer; margin-right: 1em;" onclick="populate_agent_details('${agent_details.pk}', '${agent_details.first_name}', '${agent_details.email}', '${agent_details.mobile_number}', '${agent_details.assign_followup_leads}', '${agent_details.supported_languages}', '${agent_details.product_categories}', '${agent_details.supervisors}', '${agent_details.support_level}')">
                        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M13.2692 0.730772C14.2436 1.70513 14.2436 3.28489 13.2692 4.25925L4.92447 12.604C4.73142 12.7971 4.49134 12.9364 4.22794 13.0082L0.661097 13.981C0.270732 14.0875 -0.0874597 13.7293 0.0190035 13.3389L0.99178 9.77206C1.06361 9.50867 1.20294 9.26858 1.39599 9.07553L9.74075 0.730772C10.7151 -0.243591 12.2949 -0.243591 13.2692 0.730772ZM9.06478 2.88586L2.13552 9.81506C2.07117 9.87941 2.02473 9.95944 2.00078 10.0472L1.26879 12.7312L3.95276 11.9992C4.04056 11.9753 4.12059 11.9288 4.18494 11.8645L11.114 4.93504L9.06478 2.88586ZM10.4803 1.4703L9.80385 2.1461L11.853 4.19597L12.5297 3.51972C13.0956 2.95379 13.0956 2.03623 12.5297 1.4703C11.9638 0.904373 11.0462 0.904373 10.4803 1.4703Z"/>
                        </svg>                                                    
                    </a>
                </div>
            </td>`;
    }
    
    agent_card_html += '</tr>';

    return agent_card_html;
}

function populate_agent_filter_details(response) {
    document.getElementById("total-agents-count").innerHTML = `Total:<span>${response["total_agent_count"]}</span>`;
    document.getElementById("online-agents-count").innerHTML = `Online:<span>${response["online_agent_count"]}</span>`;
    document.getElementById("offline-agents-count").innerHTML = `Offline:<span>${response["offline_agent_count"]}</span>`;
    if(window.allow_agent_to_customer_cobrowsing == "False") {
        document.getElementById("available-agents-count").innerHTML = `Available:<span>${response["available_agents_count"]}</span>`;
        document.getElementById("busy-agents-count").innerHTML = `Busy:<span>${response["busy_agents_count"]}</span>`;
    }
    document.getElementById("active-agents-count").innerHTML = `Active:<span>${response["active_agent_account_count"]}</span>`;
    document.getElementById("inactive-agents-count").innerHTML = `Inactive:<span>${response["inactive_agent_account_count"]}</span>`;
}

function update_active_agents_details(applied_filter="", element_id="", agent_pk="") {
    if(agent_pk && agent_pk != window.localStorage.getItem("filtered_agent_pk")){
        window.localStorage.setItem("filtered_agent_pk", agent_pk);
        window.localStorage.removeItem("applied_agent_filter");
        window.localStorage.removeItem("applied_filter_element_id");
    }

    remove_previous_element_active_class();
    let applied_filter_element_id = window.localStorage.getItem("applied_filter_element_id");
    let applied_agent_filter = window.localStorage.getItem("applied_agent_filter");
    let data_table_heading_element = document.getElementById("agent-data-table-heading");
    let back_button_element = document.getElementById("agent-table-back-button");

    if(applied_filter) {
        window.localStorage.setItem("applied_agent_filter", applied_filter);
        window.localStorage.setItem("applied_filter_element_id", element_id);
        let element = document.getElementById(element_id);
        if(!element.classList.contains("active")) {
            element.classList.add("active");
        }
    }

    if(applied_agent_filter && !applied_filter) {
        applied_filter = applied_agent_filter;
        if(applied_filter_element_id) {
            let storage_element = document.getElementById(applied_filter_element_id);
            storage_element.classList.add("active");
        }
    }

    if(applied_filter && applied_filter != "all"){
        document.getElementById("total-agents-count").classList.remove("active");
    }

    if(!applied_agent_filter && !applied_filter) {
        if(!document.getElementById("total-agents-count").classList.contains("active")) {
            document.getElementById("total-agents-count").classList.add("active");
        }
    }

    let agent_pk_obj = window.localStorage.getItem("filtered_agent_pk");
    if(agent_pk_obj) {
        agent_pk = agent_pk_obj;
    }

    let json_params = JSON.stringify({
        "applied_filter": sanitize_input_string(applied_filter),
        "agent_pk": sanitize_input_string(agent_pk)
    });

    let encrypted_data = easyassist_custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/update-active-agents-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status_code"] == 200) {
                if(window.agent_role != "supervisor") {
                    let admin_supervisor_table_div = document.getElementById("supervisor-admin-ally-table");
                    let agent_creation_div = document.getElementById("agent-creation-div");    
                    if(agent_pk) {
                        if(!admin_supervisor_table_div.classList.contains("d-none")) {
                            admin_supervisor_table_div.classList.add("d-none");
                        }
                        if(!agent_creation_div.classList.contains("d-none")) {
                            agent_creation_div.classList.add("d-none");
                        }
                    } else {
                        if(admin_supervisor_table_div.classList.contains("d-none")) {
                            admin_supervisor_table_div.classList.remove("d-none");
                        }
                        
                        if(agent_creation_div.classList.contains("d-none")) {
                            agent_creation_div.classList.remove("d-none");
                        }

                        if(!back_button_element.classList.contains("d-none")) {
                            back_button_element.classList.add("d-none");
                            document.getElementById("export-agent-btn").style.display = "";
                        }
                    }
                }
                

                let empty_table_div = document.getElementById("empty-table-area");
                let agent_table_div = document.getElementById("admin-agent-management-table-area");
                let previous_selected_rows = new Set();
                let previous_selected_elements = document.getElementsByClassName("user-checkbox-collection");
                for(let idx = 0; idx < previous_selected_elements.length; idx ++) {
                    let agent_pk = previous_selected_elements[idx].getAttribute("agent_pk");
                    if(previous_selected_elements[idx].checked) {
                        previous_selected_rows.add(agent_pk);
                    }
                }
                let current_top_scroll_position = document.querySelector("#content-wrapper").scrollTop;
                $("#data-table-agent").dataTable().fnClearTable();
                $("#data-table-agent").DataTable().destroy();
                let cobrowse_agent_details = response.cobrowse_agent_details;
                
                populate_agent_filter_details(response);

                let requested_agent_firstname = response.requested_agent_firstname;
                if(requested_agent_firstname) {
                    data_table_heading_element.setAttribute("title",requested_agent_firstname);
                    requested_agent_firstname = " under " + requested_agent_firstname;
                    if(back_button_element.classList.contains("d-none")) {
                        back_button_element.classList.remove("d-none");
                        document.getElementById("export-agent-btn").style.display = "none";
                    }
                }

                if(response.filter_available_agent) {
                    data_table_heading_element.innerHTML = "Available Agents" + requested_agent_firstname;
                } else if(response.filter_busy_agent) {
                    data_table_heading_element.innerHTML = "Busy Agents" + requested_agent_firstname;
                } else if(response.filter_active_account) {
                    data_table_heading_element.innerHTML = "Active Agents" + requested_agent_firstname;
                } else if(response.filter_deactivated_account) {
                    data_table_heading_element.innerHTML = "Inactive Agents" + requested_agent_firstname;
                } else if(response.filter_online) {
                    data_table_heading_element.innerHTML = "Online Agents" + requested_agent_firstname;
                } else if(response.filter_offline) {
                    data_table_heading_element.innerHTML = "Offline Agents" + requested_agent_firstname;
                } else {
                    data_table_heading_element.innerHTML = "Agents" + requested_agent_firstname;
                } 

                let agent_details_html = ""
                if(cobrowse_agent_details.length) {                   
                    for (let idx = 0; idx < cobrowse_agent_details.length; idx++) {
                        let agent_details = cobrowse_agent_details[idx];
                        agent_details_html += create_active_agent_details_card(agent_details, previous_selected_rows, response.filter_online);
                    }

                    if(!empty_table_div.classList.contains("d-none")) {
                        empty_table_div.classList.add("d-none");
                    } 
                    
                    if(agent_table_div.classList.contains("d-none")) {
                        agent_table_div.classList.remove("d-none");
                    } 

                    if(document.getElementById("agent-details-table-body")){
                        document.getElementById("agent-details-table-body").innerHTML = agent_details_html;
                        $("#data-table-agent").DataTable({
                            "bPaginate": true,
                            "bLengthChange": false,
                            "bFilter": true,
                            "bInfo": true,
                            "bAutoWidth": true,
                            "ordering": false,
                            "pagingType": "simple_numbers",
                        });

                        document.querySelector("#content-wrapper").scrollTop = current_top_scroll_position;
                        
                        let searched_value = window.localStorage.getItem("searched_agent");
                        if(searched_value) {
                            $('#data-table-agent').dataTable().fnFilter(searched_value);
                            remove_page_storage_obj();
                        }

                        if(!searched_value){
                            let current_page =  parseInt(window.localStorage.getItem("agent_table_current_page"));
                            if(current_page) {
                                $('#data-table-agent').dataTable().fnPageChange(current_page);
                            }
                        }

                    }

                } else {
                    if(empty_table_div.classList.contains("d-none")) {
                        empty_table_div.classList.remove("d-none");
                    }

                    if(!agent_table_div.classList.contains("d-none")) {
                        agent_table_div.classList.add("d-none");
                    } 
                }
            }

        }
    }

    xhttp.send(params);  
}

function toggle_agent_status(element, agent_pk) {

    let request_params = {
        "agent_pk": sanitize_input_string(agent_pk),
        "active_status": element.checked
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/toggle-agent-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status_code == 200) {
                show_easyassist_toast(response.status_message);
            } else if (response.status_code == 302) {
                show_easyassist_toast(response.status_message);
                element.checked = false;
            } else {
                show_easyassist_toast("Unable to update the active status");
                element.checked = false;
            }
        }
    }
    xhttp.send(params);
    update_active_agents_details();
}

function clear_agent_management_storage(){
    window.localStorage.removeItem("filtered_agent_pk");
    window.localStorage.removeItem("applied_agent_filter");
    window.localStorage.removeItem("applied_filter_element_id");
}

function remove_previous_element_active_class() {
    let applied_filter_element_id = window.localStorage.getItem("applied_filter_element_id");
    if(applied_filter_element_id) {
        let storage_element = document.getElementById(applied_filter_element_id);
        storage_element.classList.remove("active");
    }
}

function populate_agent_details(agent_pk, agent_name, agent_email, agent_mobile, assign_followup_leads, languages, products, supervisors, support_level) {
    
    document.getElementById("save-agent-details-error").innerHTML = "";

    if( document.getElementById("input-user-type")) {
        document.getElementById("input-user-type").value = "agent";
    }

    document.getElementById("agent-name").value = agent_name;
    document.getElementById("agent-email").value = agent_email;
    
    if(agent_mobile != "null") {
        document.getElementById("agent-mobile").value = agent_mobile;
    } else {
        document.getElementById("agent-mobile").value = "";
    }

    if(document.getElementById("selected-supervisor-div-agent")) {
        document.getElementById("selected-supervisor-div-agent").style.display = "inline";
    }
    
    if(assign_followup_leads == "true" && document.getElementById("assign-followup-lead-to-agent")){
        document.getElementById("assign-followup-lead-to-agent").checked = true;
    }
    
    let language_dropdown_element = document.getElementById("language-support-selected");
    $('#language-support-selected').selectpicker('deselectAll');
    $('#product-category-selected').selectpicker('deselectAll');
    $('#agent-supervisor-list').selectpicker('deselectAll');
    
    if(language_dropdown_element) {
        let language_dropdown_options = language_dropdown_element.options;
        languages = languages.replaceAll(" ", "");
        languages = languages.split(",");
        for (let i =0; i < language_dropdown_options.length; i++) {
            let option = language_dropdown_options[i];
            if(languages.includes(option.innerHTML)) {
                option.selected = true;
            }
        }
    }

    let product_dropdown_element = document.getElementById("product-category-selected");
    if(product_dropdown_element) {
        let product_dropdown_options = product_dropdown_element.options;
        products = products.replaceAll(" ", "");
        products = products.split(",");
        
        for (let i =0; i < product_dropdown_options.length; i++) {
            let option = product_dropdown_options[i];
            if(products.includes(option.innerHTML)) {
                option.selected = true;
            }
        }   
    }

    let supervisor_dropdown_element = document.getElementById("agent-supervisor-list");
    if(supervisor_dropdown_element) {
        let supervisor_dropdown_options = supervisor_dropdown_element.options;
        supervisors = supervisors.replaceAll(" ", "");
        supervisors = supervisors.split(",");
        
        for (let i =0; i < supervisor_dropdown_options.length; i++) {
            let option = supervisor_dropdown_options[i];
            let option_value = option.innerHTML.split('(');
            if(supervisors.includes(option.innerHTML)) {
                option.selected = true;
            } else if(option_value.length > 1 && supervisors.includes(option_value[0].trim())) {
                option.selected = true;
            }
        }
    }

    let agent_support_level_element = document.getElementById("agent-support-level");
    if(agent_support_level_element) {
        agent_support_level_element.value = support_level;
    }
    
    document.getElementById("save-agent-button").setAttribute("onclick", "update_agent_details(this,'" + agent_pk + "')")
    $("#save-agent-modal").modal('show');
    $('.selectpicker').selectpicker('refresh');
}

function update_admin_ally_supervisor_details(element, pk) {

    let error_message_element = document.getElementById("save-agent-details-error-" + pk);
    error_message_element.innerHTML = "";

    let full_name = document.getElementById("inline-form-input-agent-name-" + pk).value.trim();
    full_name = stripHTML(full_name);
    full_name = remove_special_characters_from_str(full_name);

    let email = document.getElementById("inline-form-input-agent-email-" + pk).value.trim();
    email = stripHTML(email);
    email = remove_special_characters_from_str(email);

    let mobile = document.getElementById("inline-form-input-agent-mobile-" + pk).value.trim();
    mobile = stripHTML(mobile);
    mobile = remove_special_characters_from_str(mobile);

    const regex_name = /^[^\s][a-zA-Z ]+$/;
    const regex_mobile = /^[6-9]{1}\d{9}$/;

    let platform_url = window.location.protocol + '//' + window.location.host;

    if (!full_name) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Full name cannot be empty.";
        return;
    }

    if (!regex_name.test(full_name)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter full name (only A-Z, a-z and space is allowed)";
        return;
    }

    if (!regEmail.test(email)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid Email id.";
        return;
    }

    if (mobile != null && mobile != "" && !regex_mobile.test(mobile)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid 10-digit mobile number";
        return;
    }

    let support_level = document.getElementById("inline-form-input-agent-support-level-" + pk).value;
    if (support_level == "None") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please select valid agent support level";
        return;
    }

    let user_type = document.getElementById("inline-form-input-user-type-" + pk);
    if (user_type != null && user_type != undefined) {
        if (user_type.value == "None") {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Please select valid user type";
            return;
        } else {
            user_type = user_type.value;
        }
    } else {
        user_type = "agent";
    }

    let selected_supervisor_pk_list = [];
    if (user_type == "agent" || user_type == "admin_ally")
        selected_supervisor_pk_list = $("#inline-form-input-supervisor-pk-" + pk).val();
    
    if (EASYASSIST_AGENT_ROLE == "admin_ally" && user_type =="agent" && selected_supervisor_pk_list.length == 0) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "No supervisor selected.";
        return;
    }   
    
    if (selected_supervisor_pk_list.length == 0)
        selected_supervisor_pk_list = [-1];

    let selected_language_pk_list = $("#easyassist-language-support-selected-" + pk).val();

    if (selected_language_pk_list == undefined || selected_language_pk_list == null) {

        selected_language_pk_list = [];
    }

    let selected_product_category_pk_list = $("#easyassist-product-category-selected-" + pk).val();

    if (selected_product_category_pk_list == undefined || selected_product_category_pk_list == null) {

        selected_product_category_pk_list = [];
    }

    let assign_followup_lead_to_agent_element = document.getElementById("edit_assign_followup_lead_to_agent_pk_" + pk);
    let assign_followup_lead_to_agent;
    if(assign_followup_lead_to_agent_element) {
        assign_followup_lead_to_agent = assign_followup_lead_to_agent_element.checked;
    }

    let request_params = {
        "pk": pk,
        "agent_name": full_name,
        "agent_email": email,
        "agent_mobile": mobile,
        "support_level": support_level,
        "user_type": user_type,
        "platform_url": platform_url,
        "selected_supervisor_pk_list": selected_supervisor_pk_list,
        "selected_language_pk_list": selected_language_pk_list,
        "selected_product_category_pk_list": selected_product_category_pk_list
    };
    
    if(assign_followup_lead_to_agent != undefined) {
        request_params["assign_followup_lead_to_agent"] = assign_followup_lead_to_agent;
    }

    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/update-agent-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Saved successfully.";
                setTimeout(function(e) {
                    window.location.reload();
                }, 500);
            } else if (response.status == 303) {
                error_message_element.style.color = "red";
                response_message = response.message;
                if (user_type == "admin_ally") {
                    if(response_message["matched_error"] == "language") {
                        error_message_element.innerHTML = "Supported language mismatch detected between supervisor " + response_message["supervisor"] +" and selected admin ally. Please update and try again.";
                    } else {
                        error_message_element.innerHTML = "Product category mismatch detected between supervisor " + response_message["supervisor"] +" and selected admin ally. Please update and try again.";
                    }
                } else {
                    if(response_message["matched_error"] == "language") {
                        error_message_element.innerHTML = "Supported language mismatch detected between supervisor " + response_message["supervisor"] +" and selected agent. Please update and try again.";
                    } else {
                        error_message_element.innerHTML = "Product category mismatch detected between supervisor " + response_message["supervisor"] +" and selected agent. Please update and try again.";
                    }
                }
            } else if (response.status == 307 || response.status == 311 || response.status == 309) {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = response["message"];
            } else if (response.status == 301) {
                error_message_element.style.color = "orange";
                error_message_element.innerHTML = "Agent matching details already exists.";
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Unable to save the details";
            }
        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}