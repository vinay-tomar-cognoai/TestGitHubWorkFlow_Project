var sync_search_field_interval = null;
var global_session_id = null;
var update_cobrowsing_request_status_interval = null;
var client_server_websocket = null;
var client_server_websocket_open = false;
var client_server_heartbeat_timer = null;
var agent_remarks = null;

$(function() {
    $("#easyassist-language-support-selected").selectpicker({
        noneSelectedText: 'Select Language'
    });
    $("#easyassist-product-category-selected").selectpicker({
        noneSelectedText: 'Select Product Category'
    });
    $('[data-toggle="tooltip"]').tooltip();
    $("#support-history-table").DataTable({
        "ordering": false
    });
    $("#audit-trail-table").DataTable({
        "ordering": false
    });
});

var user_last_activity_time_obj = new Date()

function set_cookie(cookiename, cookievalue, path = "") {
    var domain = window.location.hostname.substring(window.location.host.indexOf(".") + 1);

    if(window.location.hostname.split(".").length==2){
        domain = window.location.hostname;
    }

    if (path == "") {
        document.cookie = cookiename + "=" + cookievalue + ";SameSite=None; Secure";
    } else {
        document.cookie = cookiename + "=" + cookievalue + ";path=" + path + ";SameSite=None; Secure";
    }
}

function get_cookie(cookiename) {
    var cookie_name = cookiename + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var cookie_array = decodedCookie.split(';');
    for (var i = 0; i < cookie_array.length; i++) {
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

function accept_location_request(pos){
    agent_latitude = pos.coords.latitude;
    agent_longitude = pos.coords.longitude;
    let location = get_cookie("agent_location");
    if (location == null || location == undefined || location == "None" || location.toString().trim() == "") {
        show_agent_location_details(agent_latitude,agent_longitude,(data)=>{
            check_and_mark_agent_active_status("none");
    })
    }
}

function cancel_location_request(pos){
    agent_location=null
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

    json_params = JSON.stringify(request_params);

    encrypted_data = custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/change-active-status/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status != 200) {
                show_easyassist_toast("Unable to update the active status");
            } else {
                if (element != "none") {
                    window.location.reload();
                } else {
                    var cobrowsing_count = response["cobrowsing_count"];
                    var video_meeting_count = response["video_meeting_count"];

                    if(cobrowsing_count > 0) {
                        document.getElementById("total_cobrowsing_count").innerHTML = cobrowsing_count;
                        document.getElementById("total_cobrowsing_count").style.display = 'inline-flex';
                    } else {
                        document.getElementById("total_cobrowsing_count").style.display = 'none';
                    }

                    // if(video_meeting_count > 0) {
                    //     document.getElementById("total_video_meeting_count").innerHTML = video_meeting_count;
                    //     document.getElementById("total_video_meeting_count").style.display = 'inline-flex';
                    // } else {
                    //     document.getElementById("total_video_meeting_count").style.display = 'none';
                    // }
                }
            }
        }
    }
    xhttp.send(params);
}

function show_agent_location_details(latitude,longitude,callback){

    let promises = get_agent_current_location(latitude, longitude);
    Promise.all([promises])
    .then(function(results){
        if (results[0]) {
            set_cookie("agent_location", results[0], "/");
        }
        callback()
    });
}

function get_agent_current_location(latitude, longitude) {

    if(latitude == "None" || longitude == "None") {
        return new Promise(function(resolve, reject) {
            resolve("None");
        });
    }
    var geocoder = new google.maps.Geocoder();
    var latlng = new google.maps.LatLng(latitude, longitude);
    return new Promise(function(resolve, reject) {
        geocoder.geocode({'latLng': latlng}, function(results, status) {
            if(status == google.maps.GeocoderStatus.OK) {
                if(results[results.length-4]) {
                    var address = results[results.length-4].formatted_address;
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
    error_message_element = document.getElementById("save-details-error");
    error_message_element.innerHTML = "";
    var full_name = document.getElementById("agent-name").value;
    var mobile_number = document.getElementById("agent-mobile-number").value;
    var old_password = document.getElementById("old-password").value;
    var new_password = document.getElementById("new-password").value;
    var support_level= document.getElementById("agent-support-level").value;

    const regName = /^[^\s][a-zA-Z ]+$/;
    const regMob = /^[6-9]{1}[0-9]{9}$/;
    const regPass = /^(((?=.*[a-z])(?=.*[A-Z]))|((?=.*[a-z])(?=.*[0-9]))|((?=.*[A-Z])(?=.*[0-9])))(?=.{8,})(?!.*[\s])/;

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

    if (old_password != "" || new_password != "") {
        if (!regPass.test(new_password)) {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Minimum length of password is 8 and must have at least one lowercase and one uppercase alphabetical character or has at least one lowercase and one numeric character or has at least one uppercase and one numeric character.";
            return;
        }
    }
    support_level=support_level.trim();
    if(support_level.toLowerCase()!='l1' && support_level.toLowerCase()!='l2' && support_level.toLowerCase()!='l3'){
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Enter correct support level";
        return;
    }

    request_params = {
        "agent_name": full_name,
        "agent_mobile_number": mobile_number,
        "old_password": old_password,
        "new_password": new_password,
        "agent_support_level":support_level
    };

    json_params = JSON.stringify(request_params);

    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/save-details/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                if (response.is_password_changed) {
                    error_message_element.innerHTML = "Password has been reset successfully. Please login again.";
                } else {
                    error_message_element.innerHTML = "Saved successfully.";
                }
                setTimeout(function(e) {
                    window.location.reload();
                }, 2000);
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = response.message;
            }
        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}

function save_admin_details(element) {
    error_message_element = document.getElementById("save-details-error");
    error_message_element.innerHTML = "";

    var full_name = document.getElementById("admin-name").value;
    var old_password = document.getElementById("old-password").value;
    var new_password = document.getElementById("new-password").value;

    const regName = /^[^\s][a-zA-Z ]+$/;
    const regPass = /^(((?=.*[a-z])(?=.*[A-Z]))|((?=.*[a-z])(?=.*[0-9]))|((?=.*[A-Z])(?=.*[0-9])))(?=.{8,})(?!.*[\s])/;


    if (!regName.test(full_name)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter full name";
        return;
    }

    if (old_password != "" || new_password != "") {
        if (!regPass.test(new_password)) {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Minimum length of password is 8 and must have at least one lowercase and one uppercase alphabetical character or has at least one lowercase and one numeric character or has at least one uppercase and one numeric character.";
            return;
        }
    }

    request_params = {
        "agent_name": full_name,
        "old_password": old_password,
        "new_password": new_password
    };

    json_params = JSON.stringify(request_params);

    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/save-details/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                if (response.is_password_changed) {
                    error_message_element.innerHTML = "Password has been reset successfully. Please login again.";
                } else {
                    error_message_element.innerHTML = "Saved successfully.";
                }
                setTimeout(function(e) {
                    window.location.reload();
                }, 2000);
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = response.message;
            }
        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}

function generate_drop_link(element) {
    var client_page_link = document.getElementById("client-page-link").value;
    var customer_name = document.getElementById("customer-name").value.trim();
    var customer_mobile_number = document.getElementById("customer-mobile-number").value.trim();
    var customer_email_id  = document.getElementById("customer-email-id").value.trim();

    var error_message_element = document.getElementById("generate-drop-link-error");

    client_page_link = client_page_link.trim();
    customer_name = customer_name.trim();
    const regex = /^[^\s]+$/;
    const regName = /^[^\s][a-zA-Z ]+$/;
    const regEmail = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
    const regMob = /^[6-9]{1}[0-9]{9}$/;

    if (!regex.test(client_page_link)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a client page link (without whitespaces)";
        return;
    }

    if (!regName.test(customer_name)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter full name (only A-Z, a-z and space is allowed)";
        return;
    }

    if (!regMob.test(customer_mobile_number)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid 10-digit mobile number";
        return;
    }

    if (customer_email_id != null && customer_email_id != "" && !regEmail.test(customer_email_id)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid email id.";
        return;
    }

    request_params = {
        "client_page_link": client_page_link,
        "customer_name": customer_name,
        "customer_mobile_number": customer_mobile_number,
        "customer_email_id": customer_email_id,
    };

    json_params = JSON.stringify(request_params);

    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Generating...";

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/generate-drop-link/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                if(response.generated_link=='Error'){
                    error_message_element.style.color = "red";
                    error_message_element.innerHTML = "Please use a valid url";
                }else{
                    error_message_element.style.color = "green";
                    error_message_element.innerHTML = "Link has been generated successfully.";
                    document.getElementById("drop-link").value = response.generated_link;
                    document.getElementById("generate-drop-link-data-div").style.display = "block";
                    document.getElementById("generate-drop-link-after").style.display = "block";
                    document.getElementById("generate-drop-link-before").style.display = "none";
                }
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Could not generate a drop link";
            }
        }
        element.innerHTML = "Generate Link";
    }
    xhttp.send(params);

}


function add_new_agent(element) {

    error_message_element = document.getElementById("add-new-agent-error");
    error_message_element.innerHTML = "";

    var full_name = document.getElementById("inline-form-input-agent-name").value.trim();
    full_name = stripHTML(full_name);
    full_name = remove_special_characters_from_str(full_name);

    var email = document.getElementById("inline-form-input-agent-email").value.trim();
    email = stripHTML(email);
    email = remove_special_characters_from_str(email);

    var mobile = document.getElementById("inline-form-input-agent-mobile").value.trim();
    mobile = stripHTML(mobile);
    mobile = remove_special_characters_from_str(mobile);
    
    const regName = /^[^\s][a-zA-Z ]+$/;
    const regEmail = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
    const regMob = /^[6-9]{1}[0-9]{9}$/;

    var platform_url = window.location.protocol + '//' + window.location.host;

    if (!regName.test(full_name)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter full name (only A-Z, a-z and space is allowed)";
        return;
    }

    if (!regEmail.test(email)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid email id.";
        return;
    }

    if (mobile != null && mobile != "" && !regMob.test(mobile)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid 10-digit mobile number";
        return;
    }

    var support_level = document.getElementById("inline-form-input-agent-support-level").value;
    if (support_level == "None") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please select valid agent support level";
        return;
    }

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

    selected_supervisor_pk_list = [];
    if(user_type == "agent")
        selected_supervisor_pk_list = $("#inline-form-input-supervisor-pk").val();
    if(selected_supervisor_pk_list.length == 0)
        selected_supervisor_pk_list = [-1];

    var selected_language_pk_list = $("#easyassist-language-support-selected").val();

    if (selected_language_pk_list == undefined || selected_language_pk_list == null) {

        selected_language_pk_list = [];
    }

    var selected_product_category_pk_list = $("#easyassist-product-category-selected").val();

    if (selected_product_category_pk_list == undefined || selected_product_category_pk_list == null) {

        selected_product_category_pk_list = [];
    }

    request_params = {
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

    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/add-new-agent/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Saved successfully.";
                setTimeout(function(e) {
                    window.location.reload();
                }, 500);
            } else if (response.status == 301) {
                error_message_element.style.color = "orange";
                if(user_type == "agent") {
                    error_message_element.innerHTML = "Agent matching details already exists.";
                } else {
                    error_message_element.innerHTML = "Supervisor matching details already exists.";
                }
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Unable to save the details";
            }
        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}

function update_agent_details(element,pk) {

    error_message_element = document.getElementById("save-agent-details-error-"+pk);
    error_message_element.innerHTML = "";

    var full_name = document.getElementById("inline-form-input-agent-name-"+pk).value.trim();
    full_name = stripHTML(full_name);
    full_name = remove_special_characters_from_str(full_name);

    var email = document.getElementById("inline-form-input-agent-email-"+pk).value.trim();
    email = stripHTML(email);
    email = remove_special_characters_from_str(email);

    var mobile = document.getElementById("inline-form-input-agent-mobile-"+pk).value.trim();
    mobile = stripHTML(mobile);
    mobile = remove_special_characters_from_str(mobile);

    const regName = /^[^\s][a-zA-Z ]+$/;
    const regEmail = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
    const regMob = /^[6-9]{1}[0-9]{9}$/;

    var platform_url = window.location.protocol + '//' + window.location.host;

    if (!regName.test(full_name)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter full name (only A-Z, a-z and space is allowed)";
        return;
    }

    if (!regEmail.test(email)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid email id.";
        return;
    }

    if (mobile != null && mobile != "" && !regMob.test(mobile)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid 10-digit mobile number";
        return;
    }

    var support_level = document.getElementById("inline-form-input-agent-support-level-"+pk).value;
    if (support_level == "None") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please select valid agent support level";
        return;
    }

    var user_type = document.getElementById("inline-form-input-user-type-"+pk);
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

    var selected_supervisor_pk_list = [];
    if(user_type == "agent")
        selected_supervisor_pk_list = $("#inline-form-input-supervisor-pk-"+pk).val();
    if(selected_supervisor_pk_list.length == 0)
        selected_supervisor_pk_list = [-1];
    
    var selected_language_pk_list = $("#easyassist-language-support-selected-"+pk).val();

    if (selected_language_pk_list == undefined || selected_language_pk_list == null) {

        selected_language_pk_list = [];
    }

    var selected_product_category_pk_list = $("#easyassist-product-category-selected-"+pk).val();

    if (selected_product_category_pk_list == undefined || selected_product_category_pk_list == null) {

        selected_product_category_pk_list = [];
    }

    request_params = {
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
    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
   xhttp.open("POST", "/easy-assist-salesforce/agent/update-agent-details/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Saved successfully.";
                setTimeout(function(e) {
                    window.location.reload();
                }, 500);
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

$(document).on("change", ".user-checkbox-collection", function(e) {
    var user_checkbox_collection = document.getElementsByClassName("user-checkbox-collection");
    document.getElementById("button-deactivate-account").style.display = "none";
    document.getElementById("button-activate-account").style.display = "none";
    for (var index = 0; index < user_checkbox_collection.length; index++) {
        if (user_checkbox_collection[index].checked) {
            document.getElementById("button-deactivate-account").style.display = "block";
            document.getElementById("button-activate-account").style.display = "block";
            break;
        }
    }
});

function deactivate_user(element) {
    var user_checkbox_collection = document.getElementsByClassName("user-checkbox-collection");
    var agent_id_list = [];
    for (var index = 0; index < user_checkbox_collection.length; index++) {
        if (user_checkbox_collection[index].checked) {
            agent_id_list.push(user_checkbox_collection[index].id.split("-")[2]);
        }
    }

    if (agent_id_list.length == 0) {
        return;
    }

    request_params = {
        "agent_id_list": agent_id_list,
        "activate": false
    };
    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/change-agent-activate-status/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
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

function resend_password(element) {
    console.log("resending password");
    var pk = element.id.split("-")[3];
    var platform_url = window.location.protocol + '//' + window.location.host;

    request_params = {
        "user_pk": pk,
        "platform_url": platform_url
    };
    json_params = JSON.stringify(request_params);
    console.log(json_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/resend-account-password/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
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
    var first_index = window.location.href.indexOf("?");
    var redirect_location = window.location.href.substring(0, first_index);
    console.log(first_index + " " + redirect_location);
    if (status == "online") {
        window.location.href = redirect_location + "?salesforce_token=" + window.SALESFORCE_TOKEN + "&is_active=" + true;
    } else if (status == "offline") {
        window.location.href = redirect_location + "?salesforce_token=" + window.SALESFORCE_TOKEN + "&is_active=" + false;
    } else {
        window.location.href = redirect_location + "?salesforce_token=" + window.SALESFORCE_TOKEN;
    }
}

function upload_user_excel_details(element) {
    var file = ($("#user_details_upload_input"))[0].files[0];
    var error_element = document.getElementById("user_details_upload_input_error");

    if(file == undefined || file == null) {
        error_element.style.color = "red";
        error_element.innerHTML = "Please choose a file of excel format.";
        return;
    }

    if(check_malicious_file(file.name) == true) {
        return false;
    }

    var filename = file.name;
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

    var reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = function() {

        base64_str = reader.result.split(",")[1];

        var json_string = {
            "filename": file.name,
            "base64_file": base64_str,
        };

        json_string = JSON.stringify(json_string);

        encrypted_data = custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/agent/upload-user-details/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response.status == 200) {
                    error_element.style.color = "green";
                    error_element.innerHTML = "Uploaded successfully.";
                    setTimeout(function() {
                        window.location.reload();
                    }, 1000);
                } else if(response["status"] == 300) {
                    error_element.style.color = "red";
                    error_element.innerHTML = "File format not supported. Please don't use .(dot) in filename except for extension."
                } else {
                    error_element.style.color = "red";
                    error_element.innerHTML = "Could not upload the excel document. Please try again.";
                }
            } else {
                error_element.style.color = "red";
                error_element.innerHTML = "Could not upload the excel document. Please try again.";
            }
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
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/agent/export-user-details/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path"] != null) {
                export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else {
                show_easyassist_toast("Unable to download agent details");
            }
        }
    }
    xhttp.send(params);
}

function download_user_details_excel_template(element) {
    const params = "";

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/agent/download-user-details-excel-template/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path"] != null) {
                export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else {
                show_easyassist_toast("Unable to download template");
            }
        }
    }
    xhttp.send(params);
}


function change_disabled_on_floating_button_settings(checked) {
    $("#show_floating_button_checkbox").attr("disabled", checked);
    $("#select-floating-button-position").attr("disabled", checked);
    $("#floating-button-background-color").attr("disabled", checked);
}

function change_disabled_on_connect_agent_icon_settings(checked) {
    $("#connect_with_agent_icon_upload_button").attr("disabled", checked);
    $("#show_easyassist_connect_agent_icon_checkbox").attr("disabled", checked);
}

function change_disabled_on_agent_unavailable_settings(checked) {
    $("#disable_connect_button_if_agent_unavailable").attr("disabled", checked);
}

function change_disabled_on_agent_available_settings(checked) {
    $("#show_only_if_agent_available").attr("disabled", checked);
}

function set_on_change_events_settings() {

    var checked = $("#show_floating_button_checkbox").is(":checked");
    change_disabled_on_connect_agent_icon_settings(checked);

    checked = $("#show_easyassist_connect_agent_icon_checkbox").is(":checked");
    change_disabled_on_floating_button_settings(checked)

    $("#show_floating_button_checkbox").change(function() {
        var checked = $("#show_floating_button_checkbox").is(":checked");
        change_disabled_on_connect_agent_icon_settings(checked);
    });

    $("#show_easyassist_connect_agent_icon_checkbox").change(function() {
        var checked = $("#show_easyassist_connect_agent_icon_checkbox").is(":checked");
        change_disabled_on_floating_button_settings(checked);
    });

    checked = $("#show_only_if_agent_available").is(":checked");
    change_disabled_on_agent_unavailable_settings(checked);

    checked = $("#disable_connect_button_if_agent_unavailable").is(":checked");
    change_disabled_on_agent_available_settings(checked);

    $("#show_only_if_agent_available").change(function() {
        var checked = $("#show_only_if_agent_available").is(":checked");
        change_disabled_on_agent_unavailable_settings(checked);
    });

    $("#disable_connect_button_if_agent_unavailable").change(function() {
        var checked = $("#disable_connect_button_if_agent_unavailable").is(":checked");
        change_disabled_on_agent_available_settings(checked);
    });
}

set_on_change_events_settings();

// "source_easyassist_connect_agent_icon": document.getElementById("source_easyassist_connect_agent_icon").value,

function save_cobrowsing_meta_details(element, reset) {
    error_message_element = document.getElementById("save-cobrowsing-meta-details-error");
    error_message_element.innerHTML = "";

    var cobrowsingconsole_theme_color_el = document.getElementById("cobrowsing-console-theme-color");
    var cobrowsing_console_theme_color = null;
    if(cobrowsingconsole_theme_color_el.jscolor.toHEXString() != '#FFFFFF') {
        cobrowsing_console_theme_color = {
            "red": cobrowsingconsole_theme_color_el.jscolor.rgb[0],
            "green": cobrowsingconsole_theme_color_el.jscolor.rgb[1],
            "blue": cobrowsingconsole_theme_color_el.jscolor.rgb[2],
            "rgb": cobrowsingconsole_theme_color_el.jscolor.toRGBString(),
            "hex": cobrowsingconsole_theme_color_el.jscolor.toHEXString(),
        };
    }

    request_params = {
        "reset": reset,
        "cobrowsing_console_theme_color": cobrowsing_console_theme_color,
        "show_floating_easyassist_button": document.getElementById("show_floating_button_checkbox").checked,
        "floating_button_position": document.getElementById("select-floating-button-position").value,
        "floating_button_bg_color": document.getElementById("floating-button-background-color").value,
        "show_easyassist_connect_agent_icon": document.getElementById("show_easyassist_connect_agent_icon_checkbox").checked,
        "show_only_if_agent_available": document.getElementById("show_only_if_agent_available").checked,
        "disable_connect_button_if_agent_unavailable": document.getElementById("disable_connect_button_if_agent_unavailable").checked,
        "message_if_agent_unavailable": remove_special_characters_from_str(stripHTML(document.getElementById("message_if_agent_unavailable").value)),
        "start_time": document.getElementById("start_time").value,
        "end_time": document.getElementById("end_time").value,
        "message_on_non_working_hours": remove_special_characters_from_str(stripHTML(document.getElementById("message_on_non_working_hours").value)),
        "enable_edit_access": document.getElementById("enable_edit_access_checkbox").checked,
        "field_stuck_event_handler": document.getElementById("enable_field_stuck_timer_checkbox").checked,
        "field_recursive_stuck_event_check": document.getElementById("enable_recursive_field_stuck_timer_checkbox").checked,
        "get_sharable_link": document.getElementById("get_sharable_link_checkbox").checked,
        "lead_generation": document.getElementById("lead_generation_checkbox").checked,
        "field_stuck_timer": document.getElementById("field_stuck_timer").value,
        "connect_message": remove_special_characters_from_str(stripHTML(document.getElementById("connect_message").value)),
        "assistant_message": remove_special_characters_from_str(stripHTML(document.getElementById("assistant_message").value)),
        "whitelisted_domain": document.getElementById("whitelisted_domain").value,
        "urls_consider_lead_converted": document.getElementById("urls_consider_lead_converted").value,
        "proxy_server": document.getElementById("proxy_pass_server").value,
        "masking_type": document.getElementById("input-masking-type").value,
        "enable_verification_code_popup": document.getElementById("enable-verification-code-popup").checked,
        "allow_only_support_documents": document.getElementById("allow-only-support-documents-input").checked,
        "allow_language_support": document.getElementById("allow_language_support").checked,
        "supported_language_list": document.getElementById("support_language_list").value,
        "allow_generate_meeting": document.getElementById("allow-generate-meeting-input").checked,
        "meeting_url": document.getElementById("meeting-url-input").value,
        "meeting_default_password": document.getElementById("meeting-default-password").value,
        "allow_screen_recording": document.getElementById("allow_screen_recording").checked,
        "recording_expires_in_days": (document.getElementById("recording_expires_in_days") == undefined || document.getElementById("recording_expires_in_days") == null) ? 15 : document.getElementById("recording_expires_in_days").value,
        "go_live_date": document.getElementById("go_live_date").value,
        "lead_conversion_checkbox_text": document.getElementById("lead_conversion_checkbox_text").value,
        "allow_video_calling_cobrowsing": document.getElementById("allow-vc-cobrowsing-input").checked,
        "allow_screen_sharing_cobrowse": document.getElementById("allow_screen_sharing_cobrowse").checked,
        "show_cobrowsing_meeting_lobby": document.getElementById("show-cobrowsing-lobby-input").checked,
        "meet_background_color": document.getElementById("meet-background-color").value,
        "choose_product_category": document.getElementById("choose_product_category").checked,
        "product_category_list": document.getElementById("product_category_list").value,
        "allow_meeting_feedback": document.getElementById("allow-meeting-feedback-cobrowsing-input").checked,
        "allow_meeting_end_time": document.getElementById("allow-meeting-end-time-input").checked,
        "meeting_end_time": document.getElementById("meet-end-time").value,
        "enable_predefined_remarks": document.getElementById("enable-predefined-remarks").checked,
        "predefined_remarks_list": document.getElementById("predefined-remarks-list").value,
        "allow_support_documents": document.getElementById("allow_support_documents_checkbox").checked,
        "allow_capture_screenshots_in_cobrowsing":document.getElementById("allow_capture_screenshots_in_cobrowsing_checkbox").checked,
        "share_document_from_livechat":document.getElementById("share_document_from_livechat_checkbox").checked,
        "enable_invite_agent_in_cobrowsing":document.getElementById("enable_invite_agent_in_cobrowsing_checkbox").checked,
        "allow_video_meeting_only": document.getElementById("allow-only-vc-input").checked,
        "enable_agent_connect_message": document.getElementById("enable-agent-connect-message").checked,
        "agent_connect_message": document.getElementById("agent_connect_message").value,
        "enable_masked_field_warning": document.getElementById("enable-masked-field-warning").checked,
        "masked_field_warning_text": document.getElementById("masked-field-warning-text").value
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/save-cobrowsing-meta-details/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Saved successfully.";
                setTimeout(function() {
                    window.location.href = window.location.href.replace( /[\?#].*|$/, "#pills-options-tab" );
                    window.location.href = window.location.href;
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

function delete_cobrowse_logo(){
    encrypted_data = "";
    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST",  window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/sales-ai/delete-cobrowser-logo/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            setTimeout(function() {
                    window.location.href = window.location.href.replace( /[\?#].*|$/, "#pills-options-tab" );
                    window.location.href = window.location.href;
                    window.location.reload();
            }, 300);
        }else{
             setTimeout(function() {
                    window.location.href = window.location.href.replace( /[\?#].*|$/, "#pills-options-tab" );
                    window.location.href = window.location.href;
                    window.location.reload();
            }, 300);        }
    }
    xhttp.send(params);
}

function upload_cobrowse_logo(){
    var file = ($("#cobrowse_logo_input"))[0].files[0];

    if(file == undefined || file == null) {
        show_easyassist_toast("Please choose a file.");
        return;
    }

    if(check_malicious_file(file.name) == true) {
        return false;
    }

    if(file.size/1000000 > 5){
      show_easyassist_toast("File size cannot exceed 5 MB");
      $("#cobrowse_logo_input")[0].value = "";
      return;
    }

    var reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = function() {

        base64_str = reader.result.split(",")[1];

        var json_string = {
            "filename": file.name,
            "base64_file": base64_str,
        };

        json_string = JSON.stringify(json_string);

        encrypted_data = custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST",  window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/sales-ai/upload-cobrowser-logo/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response.Response);
                response = JSON.parse(response);
                setTimeout(function() {
                    window.location.href = window.location.href.replace( /[\?#].*|$/, "#pills-options-tab" );
                    window.location.reload();
                }, 300);
            }else{
                 setTimeout(function() {
                    window.location.href = window.location.href.replace( /[\?#].*|$/, "#pills-options-tab" );
                    window.location.reload();
                }, 300);
                window.location.reload();
            }
        }
        xhttp.send(params);

    };

    reader.onerror = function(error) {
        console.log('Error: ', error);
    };
}


function upload_connect_with_agent_icon() {
    var file = ($("#connect_with_agent_icon_input"))[0].files[0];

    if(file == undefined || file == null) {
        show_easyassist_toast("Please choose a file.");
        return;
    }

    if(check_malicious_file(file.name) == true) {
        return false;
    }

    var reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = function() {

        base64_str = reader.result.split(",")[1];

        var json_string = {
            "filename": file.name,
            "base64_file": base64_str,
        };

        json_string = JSON.stringify(json_string);

        encrypted_data = custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/sales-ai/upload-connect-with-agent-icon/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response.Response);
                response = JSON.parse(response);
                setTimeout(function() {
                    window.location.href = window.location.href.replace( /[\?#].*|$/, "#pills-options-tab" );
                    window.location.href = window.location.href;
                    window.location.reload();
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
    error_message_element = document.getElementById("add-new-masking-field-error");
    error_message_element.innerHTML = "";

    var field_key = document.getElementById("inline-form-input-masking-field-key").value;
    var field_value = document.getElementById("inline-form-input-masking-field-value").value;
    var masking_type = document.getElementById("inline-form-input-masking-type").value;
    const regex = /^[^\s]+$/;


    if (!regex.test(field_key)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid masking field key (without whitespaces).";
        return;
    }

    if (!regex.test(field_value)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid masking field value (without whitespaces).";
        return;
    }

    if (masking_type == null || masking_type == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please choose a masking type.";
        return;
    }

    request_params = {
        "field_key": field_key,
        "field_value": field_value,
        "masking_type": masking_type
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/add-new-obfuscated-field/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Saved successfully.";
                setTimeout(function(e) {
                  window.location.href = window.location.href.replace( /[\?#].*|$/, "#pills-settings-tab" );
                  window.location.href = window.location.href;
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

$(document).on("change", ".masking-field-checkbox-collection", function(e) {
    var field_checkbox_collection = document.getElementsByClassName("masking-field-checkbox-collection");
    document.getElementById("button-delete-masking-field").style.display = "none";
    for (var index = 0; index < field_checkbox_collection.length; index++) {
        if (field_checkbox_collection[index].checked) {
            document.getElementById("button-delete-masking-field").style.display = "block";
            break;
        }
    }
});

function delete_masking_field(element) {
    var field_checkbox_collection = document.getElementsByClassName("masking-field-checkbox-collection");
    var obfuscated_field_id_list = [];
    for (var index = 0; index < field_checkbox_collection.length; index++) {
        if (field_checkbox_collection[index].checked) {
            obfuscated_field_id_list.push(field_checkbox_collection[index].id.split("-")[3]);
        }
    }

    if (obfuscated_field_id_list.length == 0) {
        return;
    }

    request_params = {
        "obfuscated_field_id_list": obfuscated_field_id_list
    };
    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/delete-obfuscated-fields/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status != 200) {
                show_easyassist_toast("Unable to delete obfuscated fields");
            }
            window.location.href = window.location.href.replace( /[\?#].*|$/, "#pills-settings-tab" );
            window.location.href = window.location.href;
            window.location.reload();
        }
    }
    xhttp.send(params);
}

function add_new_search_tag_field(element) {
    error_message_element = document.getElementById("add-new-search-tag-field-error");
    error_message_element.innerHTML = "";

    var tag = document.getElementById("inline-form-input-search-tag").value;
    var tag_label = document.getElementById("inline-form-input-search-tag-label").value;
    var tag_key = document.getElementById("inline-form-input-search-tag-key").value;
    var tag_value = document.getElementById("inline-form-input-search-tag-value").value;
    var tag_type = document.getElementById("inline-form-input-search-tag-type").value;

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
    request_params = {
        "tag": tag,
        "tag_label": tag_label,
        "tag_key": tag_key,
        "tag_value": tag_value,
        "tag_type": tag_type
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/add-new-search-tag-field/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Saved successfully.";
                setTimeout(function(e) {
                  window.location.href = window.location.href.replace( /[\?#].*|$/, "#pills-settings-tab" );
                  window.location.href = window.location.href;
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

$(document).on("change", ".search-tag-field-checkbox-collection", function(e) {
    var field_checkbox_collection = document.getElementsByClassName("search-tag-field-checkbox-collection");
    document.getElementById("button-delete-search-tag-field").style.display = "none";
    for (var index = 0; index < field_checkbox_collection.length; index++) {
        if (field_checkbox_collection[index].checked) {
            document.getElementById("button-delete-search-tag-field").style.display = "block";
            break;
        }
    }
});

function delete_search_tag_field(element) {
    var field_checkbox_collection = document.getElementsByClassName("search-tag-field-checkbox-collection");
    var search_tag_field_id_list = [];
    for (var index = 0; index < field_checkbox_collection.length; index++) {
        if (field_checkbox_collection[index].checked) {
            search_tag_field_id_list.push(field_checkbox_collection[index].id.split("-")[4]);
        }
    }

    if (search_tag_field_id_list.length == 0) {
        return;
    }

    request_params = {
        "search_tag_field_id_list": search_tag_field_id_list
    };
    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/delete-search-tag-fields/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status != 200) {
                show_easyassist_toast("Unable to delete search tag fields");
            }
            window.location.href = window.location.href.replace( /[\?#].*|$/, "#pills-settings-tab" );
            window.location.href = window.location.href;
            window.location.reload();
        }
    }
    xhttp.send(params);
}

function add_auto_fetch_field(element) {
    error_message_element = document.getElementById("add-new-auto-fetch-field-error");
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

    request_params = {
        "fetch_field_key": fetch_field_key,
        "fetch_field_value": fetch_field_value,
        "modal_field_key": modal_field_key,
        "modal_field_value": modal_field_value
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/add-new-auto-fetch-field/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Saved successfully.";
                setTimeout(function(e) {
                    window.location.href = window.location.href.replace( /[\?#].*|$/, "#pills-settings-tab" );
                    window.location.href = window.location.href;
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

$(document).on("change", ".auto-fetch-field-checkbox-collection", function(e) {
    var field_checkbox_collection = document.getElementsByClassName("auto-fetch-field-checkbox-collection");
    document.getElementById("button-delete-auto-fetch-field").style.display = "none";
    for (var index = 0; index < field_checkbox_collection.length; index++) {
        if (field_checkbox_collection[index].checked) {
            document.getElementById("button-delete-auto-fetch-field").style.display = "block";
            break;
        }
    }
});

function delete_auto_fetch_field(element) {
    var field_checkbox_collection = document.getElementsByClassName("auto-fetch-field-checkbox-collection");
    var auto_fetch_field_id_list = [];
    for (var index = 0; index < field_checkbox_collection.length; index++) {
        if (field_checkbox_collection[index].checked) {
            auto_fetch_field_id_list.push(field_checkbox_collection[index].id.split("-")[4]);
        }
    }

    if (auto_fetch_field_id_list.length == 0) {
        return;
    }

    request_params = {
        "auto_fetch_field_id_list": auto_fetch_field_id_list
    };
    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/delete-auto-fetch-fields/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status != 200) {
                show_easyassist_toast("Unable to delete auto fetch fields");
            }
            window.location.href = window.location.href.replace( /[\?#].*|$/, "#pills-settings-tab" );
            window.location.href = window.location.href;
            window.location.reload();
        }
    }
    xhttp.send(params);
}

/////////////////////////// update_captured_lead //////////////////////

function update_captured_lead() {

    search_error = document.getElementById("search-primary-value-error");
    search_error.style.color = "none";
    search_error.innerHTML = "";

    search_field = document.getElementById("search-primary-value");
    if (search_field.value == "") {
        search_error.style.color = "red";
        search_error.innerHTML = "Please enter valid search value";
        return;
    }

    request_params = {
        "search_value": remove_special_characters_from_str(stripHTML(search_field.value))
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/search-lead/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status == 200) {
                cobrowse_io_details = response.cobrowse_io_details;
                show_verification_code = response.show_verification_code;
                allow_cobrowsing_meeting = response.allow_cobrowsing_meeting;
                allow_video_meeting_only = response.allow_video_meeting_only;
                if (cobrowse_io_details.length == 0) {
                    return;
                }
                var search_message = '';
                var agent_remarks_box = '';

                for (var index = 0; index < cobrowse_io_details.length; index++) {

                    var active_inactive = '<i class="fas fa-fw fa-check-square text-success"></i>';
                    if (cobrowse_io_details[index]["is_active"] == false) {
                        active_inactive = '<i class="fas fa-fw fa-times-circle text-danger"></i>';
                    }

                    var request_button = "";
                    var meeting_button = "";
                    if (cobrowse_io_details[index]["is_active"] == true) {

                        if (cobrowse_io_details[index]["allow_agent_cobrowse"] == "true") {
                            // connect agent with client screen
                            request_button = '<button class="btn btn-success float-right" onclick="assign_lead_to_agent(\'' + cobrowse_io_details[index]['session_id'] + '\')">Connect</button>';
                            search_message = '<p style="color:green;"><b>Request for assistance has been accepted by the Customer</b></p> <p style="color:orange;"><b>Please don\'t close this until, you have completed the co-browsing session with the Customer.</b></p>';
                        } else if (cobrowse_io_details[index]["allow_agent_cobrowse"] == "false") {
                            // requested for assistance but client doesn't allowed
                            request_button = '<button class="btn btn-primary float-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request Co-browsing</button>';
                            search_message = '<p style="color:red;"><b>Request for assistance has been denied by the customer. Kindly make sure, you are connected with client on call.</b></p>';
                        } else {
                            if (cobrowse_io_details[index]["agent_assistant_request_status"] == true) {
                                // requested for assistance but state has not been changed
                                request_button = '<button class="btn btn-primary float-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Resend Request</button>';
                                search_message = '<p style="color:orange;"><b>Request for assistance has been sent to the customer.</b></p>';
                            } else {
                                request_button = '<button class="btn btn-primary float-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request Co-browsing</button>';
                            }
                        }

                        if(allow_video_meeting_only == true){
                            if (cobrowse_io_details[index]["allow_agent_meeting"] == "true") {
                                // connect agent with client screen
                                meeting_button += '<button class="btn btn-success float-right" onclick="connect_with_client(\'' + cobrowse_io_details[index]['session_id'] + '\')">Connect</button>';
                            } else if (cobrowse_io_details[index]["allow_agent_meeting"] == "false") {
                                // requested for assistance but client doesn't allowed
                                meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                                search_message = '<p style="color:red;"><b>Request for meeting has been denied by the customer.</b></p>';
                            } else {
                                if (cobrowse_io_details[index]["agent_meeting_request_status"] == true) {
                                    meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Resend Request</button>';
                                    search_message = '<p style="color:orange;"><b>Request for meeting has been sent to the customer.</b></p>';
                                } else {
                                    meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                                }
                            }
                        } else if (allow_cobrowsing_meeting == true) {
                            if (cobrowse_io_details[index]["allow_agent_meeting"] == "true") {
                                // connect agent with client screen
                                meeting_button += '<button class="btn btn-success float-right" onclick="connect_with_client(\'' + cobrowse_io_details[index]['session_id'] + '\')">Connect</button>';
                            } else if (cobrowse_io_details[index]["allow_agent_meeting"] == "false") {
                                // requested for assistance but client doesn't allowed
                                meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                                search_message = '<p style="color:red;"><b>Request for meeting has been denied by the customer.</b></p>';
                            } else {
                                if (cobrowse_io_details[index]["agent_meeting_request_status"] == true) {
                                    meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Resend Request</button>';
                                    search_message = '<p style="color:orange;"><b>Request for meeting has been sent to the customer.</b></p>';
                                } else {
                                    meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                                }
                            }
                        }
                    }
                    document.getElementById("active_inactive_" + cobrowse_io_details[index]["session_id"]).innerHTML = active_inactive
                    if(allow_video_meeting_only == false){
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
                    easyassist_table = document.querySelector(".easy-assist-table");
                    easyassist_table.nextElementSibling.innerHTML = search_message
                }
            }
        }
    }
    xhttp.send(params);
}

function search_for_captured_lead() {
    session_details_element = document.getElementById("running-session-details");
    session_details_element.innerHTML = "";

    search_error = document.getElementById("search-primary-value-error");
    search_error.style.color = "none";
    search_error.innerHTML = "";

    search_field = document.getElementById("search-primary-value");
    if (search_field.value == "") {
        search_error.style.color = "red";
        search_error.innerHTML = "Please enter valid search value";
        return;
    }

    request_params = {
        "search_value": remove_special_characters_from_str(stripHTML(search_field.value))
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    // element.innerHTML = "Searching...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/search-lead/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                cobrowse_io_details = response.cobrowse_io_details;
                show_verification_code = response.show_verification_code;
                allow_cobrowsing_meeting = response.allow_cobrowsing_meeting;
                allow_video_meeting_only = response.allow_video_meeting_only;
                if (cobrowse_io_details.length == 0) {
                    session_details_element.innerHTML = "No active customer with that details found. Please wait after some time and try again. Or ask the customer to refresh the page and try again";
                } else {
                    if(allow_video_meeting_only == true){
                        if (show_verification_code == false) {
                            session_details_table = '<p>Session Details</p>\
                                    <table class="table easy-assist-table">\
                                      <thead>\
                                          <tr>\
                                              <th>Request DateTime</th>\
                                            <th>Active/Inactive</th>\
                                            <th>Meeting</th>\
                                        </tr>\
                                    </thead>';
                        } else {
                            session_details_table = '<p>Session Details</p>\
                                    <table class="table easy-assist-table">\
                                      <thead>\
                                          <tr>\
                                              <th>Request DateTime</th>\
                                            <th>Active/Inactive</th>\
                                            <th>Meeting</th>\
                                        </tr>\
                                    </thead>';
                        }
                    } else if (allow_cobrowsing_meeting == true){
                        if (show_verification_code == false) {
                            session_details_table = '<p>Session Details</p>\
                                    <table class="table easy-assist-table">\
                                      <thead>\
                                          <tr>\
                                              <th>Request DateTime</th>\
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
                                              <th>Request DateTime</th>\
                                            <th>Active/Inactive</th>\
                                            <th>Support Code</th>\
                                            <th>Cobrowsing</th>\
                                            <th>Meeting</th>\
                                        </tr>\
                                    </thead>';
                        }
                    }else{
                        if (show_verification_code == false) {
                            session_details_table = '<p>Session Details</p>\
                                    <table class="table easy-assist-table">\
                                      <thead>\
                                          <tr>\
                                              <th>Request DateTime</th>\
                                            <th>Active/Inactive</th>\
                                            <th>Cobrowsing</th>\
                                        </tr>\
                                    </thead>';
                        } else {
                            session_details_table = '<p>Session Details</p>\
                                    <table class="table easy-assist-table">\
                                      <thead>\
                                          <tr>\
                                              <th>Request DateTime</th>\
                                            <th>Active/Inactive</th>\
                                            <th>Support Code</th>\
                                            <th>Cobrowsing</th>\
                                        </tr>\
                                    </thead>';
                        }

                    }
                    var search_message = '<p></p>';

                    for (var index = 0; index < cobrowse_io_details.length; index++) {

                        var active_inactive = '<i class="fas fa-fw fa-check-square text-success"></i>';
                        if (cobrowse_io_details[index]["is_active"] == false) {
                            active_inactive = '<i class="fas fa-fw fa-times-circle text-danger"></i>';
                        }

                        var request_button = "";
                        var meeting_button = "";
                        if (cobrowse_io_details[index]["is_active"] == true) {
                            if (cobrowse_io_details[index]["allow_agent_cobrowse"] == "true") {
                                // connect agent with client screen
                                request_button = '<button class="btn btn-success float-right" onclick="assign_lead_to_agent(\'' + cobrowse_io_details[index]['session_id'] + '\')">Connect</button>';
                                search_message = '<p style="color:green;"><b>Request for assistance has been accepted by the customer.</b></p> <p style="color:orange;"><b>Please don\'t close this until, you have completed the co-browsing session with the Customer.</b></p>';
                                search_field.setAttribute("disabled", "disabled");
                            } else if (cobrowse_io_details[index]["allow_agent_cobrowse"] == "false") {
                                // requested for assistance but client doesn't allowed
                                request_button = '<button class="btn btn-primary float-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request Co-browsing</button>';
                                search_message = '<p style="color:red;"><b>Request for assistance has been denied by the customer. Kindly make sure, you are connected with client on call.</b></p>';
                            } else {
                                if (cobrowse_io_details[index]["agent_assistant_request_status"] == true) {
                                    // requested for assistance but state has not been changed
                                    request_button = '<button class="btn btn-primary float-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Resend Request</button>';
                                    search_field.setAttribute("disabled", "disabled");
                                    search_message = '<p style="color:orange;"><b>Request for assistance has been sent to the customer</b></p>';
                                } else {
                                    request_button = '<button class="btn btn-primary float-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request Co-browsing</button>';
                                }
                            }
                            if (allow_video_meeting_only == true){
                                if (cobrowse_io_details[index]["allow_agent_meeting"] == "true") {
                                    // connect agent with client screen
                                    meeting_button += '<button class="btn btn-success float-right" onclick="connect_with_client(\'' + cobrowse_io_details[index]['session_id'] + '\')">Connect</button>';
                                } else if (cobrowse_io_details[index]["allow_agent_meeting"] == "false") {
                                    // requested for assistance but client doesn't allowed
                                    meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                                    search_message = '<p style="color:red;"><b>Request for meeting has been denied by the customer.</b></p>';
                                } else {
                                    if (cobrowse_io_details[index]["agent_meeting_request_status"] == true) {
                                        meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Resend Request</button>';
                                        search_message = '<p style="color:orange;"><b>Request for meeting has been sent to the customer.</b></p>';
                                    } else {
                                        meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                                    }
                                }
                            } else if (allow_cobrowsing_meeting == true){
                                if (cobrowse_io_details[index]["allow_agent_meeting"] == "true") {
                                    // connect agent with client screen
                                    meeting_button += '<button class="btn btn-success float-right" onclick="connect_with_client(\'' + cobrowse_io_details[index]['session_id'] + '\')">Connect</button>';
                                } else if (cobrowse_io_details[index]["allow_agent_meeting"] == "false") {
                                    // requested for assistance but client doesn't allowed
                                    meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                                    search_message = '<p style="color:red;"><b>Request for meeting has been denied by the customer.</b></p>';
                                } else {
                                    if (cobrowse_io_details[index]["agent_meeting_request_status"] == true) {
                                        meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Resend Request</button>';
                                        search_message = '<p style="color:orange;"><b>Request for meeting has been sent to the customer.</b></p>';
                                    } else {
                                        meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                                    }
                                }
                            }
                        }
                        if(allow_video_meeting_only == true){
                            if (show_verification_code == false) {
                                session_details_table += '<tbody>\
                                  <tr>\
                                      <td>' + cobrowse_io_details[index]["datetime"] + '</td>\
                                      <td id = "active_inactive_' + cobrowse_io_details[index]["session_id"] + '">' + active_inactive + '</td>\
                                      <td id = "meeting_button_' + cobrowse_io_details[index]["session_id"] + '">' + meeting_button + '</td>\
                                  </tr>\
                                </tbody>';
                            } else {
                                session_details_table += '<tbody>\
                                  <tr>\
                                      <td>' + cobrowse_io_details[index]["datetime"] + '</td>\
                                      <td id = "active_inactive_' + cobrowse_io_details[index]["session_id"] + '">' + active_inactive + '</td>\
                                      <td id = "meeting_button_' + cobrowse_io_details[index]["session_id"] + '">' + meeting_button + '</td>\
                                  </tr>\
                                </tbody>';
                            }
                        } else if (allow_cobrowsing_meeting == true){
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
                        }else{
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
            }
        }
        // element.innerHTML = "<i class=\"fas fa-fw fa-search\"></i> Search";
    }
    xhttp.send(params);
}

function assign_lead_to_agent(session_id) {

    request_params = {
        "session_id": session_id
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/assign-lead/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {

                if(response.allow_screen_sharing_cobrowse == "true" || response.allow_screen_sharing_cobrowse == true) {

                    window.location = "/easy-assist-salesforce/agent/screensharing-cobrowse/" + session_id + "?salesforce_token=" + window.SALESFORCE_TOKEN;
                } else {

                    window.location = "/easy-assist-salesforce/agent/" + session_id + "?salesforce_token=" + window.SALESFORCE_TOKEN;
                }
            }
        }
    }
    xhttp.send(params);
}

function request_for_cobrowsing(session_id) {
    request_params = {
        "session_id": session_id
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/request-assist/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
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

function request_for_meeting(session_id) {
    request_params = {
        "session_id": session_id
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/request-assist-meeting/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
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
    request_params = {};
    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/mark-inactive/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
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

    request_params = {
        "session_id": session_id,
        "search_value": "None"
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/search-lead/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status == 200) {
                cobrowse_io_details = response.cobrowse_io_details;
                show_verification_code = response.show_verification_code;
                allow_cobrowsing_meeting = response.allow_cobrowsing_meeting;
                allow_video_meeting_only = response.allow_video_meeting_only;
                if (cobrowse_io_details.length == 0) {
                    return;
                }
                var search_message = '';
                var agent_remarks_box = '';

                for (var index = 0; index < cobrowse_io_details.length; index++) {

                    var active_inactive = '<i class="fas fa-fw fa-check-square text-success"></i>';
                    if (cobrowse_io_details[index]["is_active"] == false) {
                        active_inactive = '<i class="fas fa-fw fa-times-circle text-danger"></i>';
                    }

                    var request_button = "";
                    var meeting_button = "";
                    if (cobrowse_io_details[index]["is_active"] == true) {
                        if (cobrowse_io_details[index]["allow_agent_cobrowse"] == "true") {
                            // connect agent with client screen
                            request_button = '<button class="btn btn-success float-right" onclick="assign_lead_to_agent(\'' + cobrowse_io_details[index]['session_id'] + '\')">Connect</button>';
                            search_message = '<p style="color:green;"><b>Request for assistance has been accepted by the Customer</b></p> <p style="color:orange;"><b>Please don\'t close this until, you have completed the co-browsing session with the Customer.</b></p>';
                        } else if (cobrowse_io_details[index]["allow_agent_cobrowse"] == "false") {
                            // requested for assistance but client doesn't allowed
                            request_button = '<button class="btn btn-primary float-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request Co-browsing</button>';
                            search_message = '<p style="color:red;"><b>Request for assistance has been denied by the customer. Kindly make sure, you are connected with client on call.</b></p>';
                        } else {
                            if (cobrowse_io_details[index]["agent_assistant_request_status"] == true) {
                                // requested for assistance but state has not been changed
                                request_button = '<button class="btn btn-primary float-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Resend Request</button>';
                                search_message = '<p style="color:orange;"><b>Request for assistance has been sent to the customer.</b></p>';
                            } else {
                                request_button = '<button class="btn btn-primary float-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request Co-browsing</button>';
                            }
                        }

                        if(allow_video_meeting_only == true){
                            if (cobrowse_io_details[index]["allow_agent_meeting"] == "true") {
                                // connect agent with client screen
                                meeting_button += '<button class="btn btn-success float-right" onclick="connect_with_client(\'' + cobrowse_io_details[index]['session_id'] + '\')">Connect</button>';
                            } else if (cobrowse_io_details[index]["allow_agent_meeting"] == "false") {
                                // requested for assistance but client doesn't allowed
                                meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                                search_message = '<p style="color:red;"><b>Request for meeting has been denied by the customer.</b></p>';
                            } else {
                                if (cobrowse_io_details[index]["agent_meeting_request_status"] == true) {
                                    meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Resend Request</button>';
                                    search_message = '<p style="color:orange;"><b>Request for meeting has been sent to the customer.</b></p>';
                                } else {
                                    meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                                }
                            }

                        } else if (allow_cobrowsing_meeting == true){
                            if (cobrowse_io_details[index]["allow_agent_meeting"] == "true") {
                                // connect agent with client screen
                                meeting_button += '<button class="btn btn-success float-right" onclick="connect_with_client(\'' + cobrowse_io_details[index]['session_id'] + '\')">Connect</button>';
                            } else if (cobrowse_io_details[index]["allow_agent_meeting"] == "false") {
                                // requested for assistance but client doesn't allowed
                                meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                                search_message = '<p style="color:red;"><b>Request for meeting has been denied by the customer.</b></p>';
                            } else {
                                if (cobrowse_io_details[index]["agent_meeting_request_status"] == true) {
                                    meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Resend Request</button>';
                                    search_message = '<p style="color:orange;"><b>Request for meeting has been sent to the customer.</b></p>';
                                } else {
                                    meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                                }
                            }
                        }
                    }
                    document.getElementById("active_inactive_" + cobrowse_io_details[index]["session_id"]).innerHTML = active_inactive
                    if(allow_video_meeting_only == false){
                        document.getElementById("request_button_" + cobrowse_io_details[index]["session_id"]).innerHTML = request_button
                        if (allow_cobrowsing_meeting == true){
                            document.getElementById("meeting_button_" + cobrowse_io_details[index]["session_id"]).innerHTML = meeting_button
                        }
                        if (show_verification_code) {
                            document.getElementById("otp_" + cobrowse_io_details[index]["session_id"]).innerHTML = cobrowse_io_details[index]["otp"]
                        }
                    } else {
                        document.getElementById("meeting_button_" + cobrowse_io_details[index]["session_id"]).innerHTML = meeting_button
                    }
                    easyassist_table = document.querySelector(".easy-assist-table");
                    easyassist_table.nextElementSibling.innerHTML = search_message
                }
            }
        }
    }
    xhttp.send(params);
}

function close_easyassist_cobrowsing_session(session_id){
        comments = "";
        json_string = JSON.stringify({
            "id":session_id,
            "comments": comments
        });

        encrypted_data = custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };
        const params = JSON.stringify(encrypted_data);
        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/agent/close-session/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response.status == 200) {
                    window.location = "/easy-assist/sales-ai/dashboard/";
                }
            }
        }
        xhttp.send(params);
}

function connect_with_client(session_id) {
    if (session_id == null || session_id == undefined) {

        return;
    }
    window.open("/easy-assist-salesforce/meeting/" + session_id + "?is_meeting_cobrowsing=true&salesforce_token=" + window.SALESFORCE_TOKEN, "_blank");
}


function update_cobrowsing_request_status(session_id) {

    if (session_id == null || session_id == undefined) {

        return;
    }
    request_params = {
        "session_id": session_id,
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/get-lead-status/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {

                if (response.cobrowsing_start_datetime == "None") {

                    document.getElementById("easy-assist-" + session_id + "-status").innerHTML = 'Waiting for Agent'
                    document.getElementById("easy-assist-" + session_id + "-status").setAttribute("class", "text-warning");
                } else if (response.is_active_timer && response.is_active) {

                    document.getElementById("easy-assist-" + session_id + "-status").innerHTML = 'Connected with agent'
                    document.getElementById("easy-assist-" + session_id + "-status").setAttribute("class", "text-success");
                } else {

                    document.getElementById("easy-assist-" + session_id + "-status").innerHTML = 'Inactive'
                    document.getElementById("easy-assist-" + session_id + "-status").setAttribute("class", "text-danger");
                }
                document.getElementById("easy-assist-" + session_id + "-time-duration").innerHTML = response.total_time_spent

                if (response.is_active && response.is_active_timer) {

                    if (response.share_client_session) {

                        document.getElementById("easy-assist-" + session_id + "-connect").innerHTML = '<a href="/easy-assist-salesforce/customer/' + response.pk + '?salesforce_token=' + window.SALESFORCE_TOKEN + '"><button type="button" class="btn btn-success btn-sm">Connect</button></a>'
                    } else {

                        if (response.allow_agent_cobrowse == "true") {

                            document.getElementById("easy-assist-" + session_id + "-connect").innerHTML = '<a href="/easy-assist-salesforce/agent/' + response.pk + '?salesforce_token=' + window.SALESFORCE_TOKEN + '"><button type="button" class="btn btn-success btn-sm">Connect</button></a>'
                        } else {

                            if(response.allow_video_meeting == false) {
                                document.getElementById("easy-assist-" + session_id + "-connect").innerHTML = '<a href="javascript:void(0)"><button type="button" class="btn btn-primary btn-sm" onclick="request_for_inbound_cobrowsing(\'' + response.pk + '\', \'' + response.mobile_number + '\')">Request for cobrowsing</button></a>';
                            }
                        }
                    }
                } else {

                    document.getElementById("easy-assist-" + session_id + "-connect").innerHTML = '<td><a href="#" class="btn btn-danger btn-icon-split" data-toggle="modal" data-target="#archive-client-' + response.pk + '"><span class="icon text-white-50"><i class="fas fa-trash"></i></span><span class="text">Archive</span></a></td>'
                    clearInterval(update_cobrowsing_request_status_interval)
                }
            }
        }
    }
    xhttp.send(params);
}

function request_for_inbound_cobrowsing(session_id) {
    global_session_id = session_id;

    session_details_element = document.getElementById("inbound-running-session-details");
    session_details_element.innerHTML = "";

    request_params = {
        "session_id": session_id,
        "search_value": "None"
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    // element.innerHTML = "Searching...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/search-lead/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);

            console.log(response)

            if (response.status == 200) {
                cobrowse_io_details = response.cobrowse_io_details;
                show_verification_code = response.show_verification_code;
                allow_cobrowsing_meeting = response.allow_cobrowsing_meeting;
                allow_video_meeting_only = response.allow_video_meeting_only;
                if (cobrowse_io_details.length == 0) {
                    session_details_element.innerHTML = "No active customer with that details found. Please wait after some time and try again. Or ask the customer to refresh the page and try again";
                } else {
                    var session_details_table = '';
                    if(allow_video_meeting_only == true){
                        if (show_verification_code == false) {
                            session_details_table = '<p>Session Details</p>\
                                    <table class="table easy-assist-table">\
                                      <thead>\
                                          <tr>\
                                              <th>Request DateTime</th>\
                                              <th>Active/Inactive</th>\
                                              <th>Meeting</th>\
                                          </tr>\
                                      </thead>';
                        } else {
                            session_details_table = '<p>Session Details</p>\
                                    <table class="table easy-assist-table">\
                                      <thead>\
                                          <tr>\
                                              <th>Request DateTime</th>\
                                              <th>Active/Inactive</th>\
                                              <th>Meeting</th>\
                                          </tr>\
                                      </thead>';
                        }

                    } else if(allow_cobrowsing_meeting == true){
                        if (show_verification_code == false) {
                            session_details_table = '<p>Session Details</p>\
                                    <table class="table easy-assist-table">\
                                      <thead>\
                                          <tr>\
                                              <th>Request DateTime</th>\
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
                                              <th>Request DateTime</th>\
                                              <th>Active/Inactive</th>\
                                              <th>Support Code</th>\
                                              <th>Cobrowsing</th>\
                                              <th>Meeting</th>\
                                          </tr>\
                                      </thead>';
                        }
                    }else{
                        if (show_verification_code == false) {
                            session_details_table = '<p>Session Details</p>\
                                    <table class="table easy-assist-table">\
                                      <thead>\
                                          <tr>\
                                              <th>Request DateTime</th>\
                                              <th>Active/Inactive</th>\
                                              <th>Cobrowsing</th>\
                                          </tr>\
                                      </thead>';
                        } else {
                            session_details_table = '<p>Session Details</p>\
                                    <table class="table easy-assist-table">\
                                      <thead>\
                                          <tr>\
                                              <th>Request DateTime</th>\
                                              <th>Active/Inactive</th>\
                                              <th>Support Code</th>\
                                              <th>Cobrowsing</th>\
                                          </tr>\
                                      </thead>';
                        }
                    }

                    var search_message = '<p></p>';
                    var agent_remarks_box = '';

                    for (var index = 0; index < cobrowse_io_details.length; index++) {

                        var active_inactive = '<i class="fas fa-fw fa-check-square text-success"></i>';
                        if (cobrowse_io_details[index]["is_active"] == false) {
                            active_inactive = '<i class="fas fa-fw fa-times-circle text-danger"></i>';
                        }

                        var request_button = "";
                        var meeting_button = "";
                        if (cobrowse_io_details[index]["is_active"] == true) {
                            if (cobrowse_io_details[index]["allow_agent_cobrowse"] == "true") {
                                // connect agent with client screen
                                request_button = '<button class="btn btn-success float-right" onclick="assign_lead_to_agent(\'' + cobrowse_io_details[index]['session_id'] + '\')">Connect</button>';
                                search_message = '<p style="color:green;"><b>Request for assistance has been accepted by the Customer</b></p> <p style="color:orange;"><b>Please don\'t close this until, you have completed the co-browsing session with the Customer.</b></p>';
                            } else if (cobrowse_io_details[index]["allow_agent_cobrowse"] == "false") {
                                // requested for assistance but client doesn't allowed
                                request_button = '<button class="btn btn-primary float-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request Co-browsing</button>';
                                search_message = '<p style="color:red;"><b>Request for assistance has been denied by the customer. Kindly make sure, you are connected with client on call.</b></p>';
                            } else {
                                if (cobrowse_io_details[index]["agent_assistant_request_status"] == true) {
                                    // requested for assistance but state has not been changed
                                    request_button = '<button class="btn btn-primary float-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Resend Request</button>';
                                    search_message = '<p style="color:orange;"><b>Request for assistance has been sent to the customer.</b></p>';
                                } else {
                                    request_button = '<button class="btn btn-primary float-right" onclick="request_for_cobrowsing(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request Co-browsing</button>';
                                }
                            }

                            if(allow_video_meeting_only == true){
                                if (cobrowse_io_details[index]["allow_agent_meeting"] == "true") {
                                    // connect agent with client screen
                                    meeting_button += '<button class="btn btn-success float-right" onclick="connect_with_client(\'' + cobrowse_io_details[index]['session_id'] + '\')">Connect</button>';
                                } else if (cobrowse_io_details[index]["allow_agent_meeting"] == "false") {
                                    // requested for assistance but client doesn't allowed
                                    meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                                    search_message = '<p style="color:red;"><b>Request for meeting has been denied by the customer.</b></p>';
                                } else {
                                    if (cobrowse_io_details[index]["agent_meeting_request_status"] == true) {
                                        meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Resend Request</button>';
                                        search_message = '<p style="color:orange;"><b>Request for meeting has been sent to the customer.</b></p>';
                                    } else {
                                        meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                                    }
                                }
                            } else if(allow_cobrowsing_meeting == true){
                                if (cobrowse_io_details[index]["allow_agent_meeting"] == "true") {
                                    // connect agent with client screen
                                    meeting_button += '<button class="btn btn-success float-right" onclick="connect_with_client(\'' + cobrowse_io_details[index]['session_id'] + '\')">Connect</button>';
                                } else if (cobrowse_io_details[index]["allow_agent_meeting"] == "false") {
                                    // requested for assistance but client doesn't allowed
                                    meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                                    search_message = '<p style="color:red;"><b>Request for meeting has been denied by the customer.</b></p>';
                                } else {
                                    if (cobrowse_io_details[index]["agent_meeting_request_status"] == true) {
                                        meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Resend Request</button>';
                                        search_message = '<p style="color:orange;"><b>Request for meeting has been sent to the customer.</b></p>';
                                    } else {
                                        meeting_button += '<button class="btn btn-primary float-right" onclick="request_for_meeting(\'' + cobrowse_io_details[index]['session_id'] + '\')">Request for Meeting</button>';
                                    }
                                }
                            }
                        }
                        if(allow_video_meeting_only == true){
                            if (show_verification_code == false) {
                                session_details_table += '<tbody>\
                                  <tr>\
                                      <td>' + cobrowse_io_details[index]["datetime"] + '</td>\
                                      <td id="active_inactive_' + cobrowse_io_details[index]['session_id'] + '">' + active_inactive + '</td>\
                                      <td id="meeting_button_' + cobrowse_io_details[index]['session_id'] + '">'+ meeting_button +'</td>\
                                  </tr>\
                                </tbody>';
                            } else {
                                session_details_table += '<tbody>\
                                  <tr>\
                                      <td>' + cobrowse_io_details[index]["datetime"] + '</td>\
                                      <td id="active_inactive_' + cobrowse_io_details[index]['session_id'] + '">' + active_inactive + '</td>\
                                      <td id="meeting_button_' + cobrowse_io_details[index]['session_id'] + '">'+ meeting_button +'</td>\
                                  </tr>\
                                </tbody>';
                            }
                        } else if(allow_cobrowsing_meeting == true){
                            if (show_verification_code == false) {
                                session_details_table += '<tbody>\
                                  <tr>\
                                      <td>' + cobrowse_io_details[index]["datetime"] + '</td>\
                                      <td id="active_inactive_' + cobrowse_io_details[index]['session_id'] + '">' + active_inactive + '</td>\
                                      <td id="request_button_' + cobrowse_io_details[index]['session_id'] + '">\
                                        ' + request_button + '\
                                      </td><td id="meeting_button_' + cobrowse_io_details[index]['session_id'] + '">'+ meeting_button +'</td>\
                                  </tr>\
                                </tbody>';
                            } else {
                                session_details_table += '<tbody>\
                                  <tr>\
                                      <td>' + cobrowse_io_details[index]["datetime"] + '</td>\
                                      <td id="active_inactive_' + cobrowse_io_details[index]['session_id'] + '">' + active_inactive + '</td>\
                                      <td id="otp_' + cobrowse_io_details[index]['session_id'] + '">' + cobrowse_io_details[index]["otp"] + '</td>\
                                      <td id="request_button_' + cobrowse_io_details[index]['session_id'] + '">\
                                        ' + request_button + '\
                                      </td><td id="meeting_button_' + cobrowse_io_details[index]['session_id'] + '">'+ meeting_button +'</td>\
                                  </tr>\
                                </tbody>';
                            }
                        }else{
                            if (show_verification_code == false) {
                                session_details_table += '<tbody>\
                                  <tr>\
                                      <td>' + cobrowse_io_details[index]["datetime"] + '</td>\
                                      <td id="active_inactive_' + cobrowse_io_details[index]['session_id'] + '">' + active_inactive + '</td>\
                                      <td id="request_button_' + cobrowse_io_details[index]['session_id'] + '">\
                                        ' + request_button + '\
                                  </tr>\
                                </tbody>';
                            } else {
                                session_details_table += '<tbody>\
                                  <tr>\
                                      <td>' + cobrowse_io_details[index]["datetime"] + '</td>\
                                      <td id="active_inactive_' + cobrowse_io_details[index]['session_id'] + '">' + active_inactive + '</td>\
                                      <td id="otp_' + cobrowse_io_details[index]['session_id'] + '">' + cobrowse_io_details[index]["otp"] + '</td>\
                                      <td id="request_button_' + cobrowse_io_details[index]['session_id'] + '">\
                                        ' + request_button + '\
                                  </tr>\
                                </tbody>';
                            }

                        }
                        $('.end_cobrowsing_session_button').remove();
                        if(agent_remarks==null){
                            agent_remarks_box = '<label for="close-session-remarks">Remarks</label><textarea class="form-control" id="agent-session-remarks"></textarea>';
                        }else{
                            agent_remarks_box = '<label for="close-session-remarks">Remarks</label><textarea class="form-control" id="agent-session-remarks">'+agent_remarks+'</textarea>';
                        }
                        agent_remarks_box += '<button class="btn btn-primary float-right" style="margin-top: 15px" onclick="save_agent_session_remarks(\'' + cobrowse_io_details[index]['session_id'] + '\')">Save Remarks</button>';
                        if(allow_video_meeting_only) {
                            document.getElementById("inbound_cobrowsing_modal_title").innerHTML = "Request for initiating meeting?";
                        } else {
                            document.getElementById("inbound_cobrowsing_modal_title").innerHTML = "Request for initiating co-browsing?";
                        }
                    }

                    session_details_table += '</table>';
                    session_details_table += search_message;
                    session_details_element.innerHTML = session_details_table;
                    session_details_element.innerHTML += agent_remarks_box;

                    if (sync_search_field_interval == null) {
                        sync_search_field_interval = setInterval(function(e) {
                            update_inbound_cobrowsing(session_id);
                        }, 5000);
                    }
                }

                $("#request_for_inbound_cobrowsing_modal").modal("show");
            }
        }
        // element.innerHTML = "<i class=\"fas fa-fw fa-search\"></i> Search";
    }
    xhttp.send(params);
}

$("#request_for_inbound_cobrowsing_modal").on("hidden.bs.modal", function() {
    if (sync_search_field_interval != null) {
        clearInterval(sync_search_field_interval);
        sync_search_field_interval = null;

        update_cobrowsing_request_status_interval = setInterval(function() {
            update_cobrowsing_request_status(global_session_id)
        }, 5000);
    }
});


function save_agent_session_remarks(session_id) {
    if (document.getElementById("agent-session-remarks") == null) return;
    var agent_session_remarks = document.getElementById("agent-session-remarks").value;
    if (agent_session_remarks.trim() == "") {
        show_easyassist_toast("Please enter some remarks before saving.");
        return;
    }
    agent_remarks=agent_session_remarks;
    request_params = {
        "session_id": session_id,
        "agent_comments": agent_session_remarks
    };
    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/save-agent-comments/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status != 200) {
                show_easyassist_toast("Unable to save agent comments");
            } else {
                document.getElementById("agent-session-remarks").value = "";
                show_easyassist_toast("Remarks saved");
            }
        }
    }
    xhttp.send(params);
}

function activate_user(element) {

    var user_checkbox_collection = document.getElementsByClassName("user-checkbox-collection");

    var agent_id_list = [];

    for (var index = 0; index < user_checkbox_collection.length; index++) {
        if (user_checkbox_collection[index].checked) {
            agent_id_list.push(user_checkbox_collection[index].id.split("-")[2]);
        }
    }

    if (agent_id_list.length == 0) {
        return;
    }

    request_params = {
        "agent_id_list": agent_id_list,
        "activate": true
    };
    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/change-agent-activate-status/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
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

    if (load_more_captured_screenshot == false) {
        cobrowse_session_captured_screenshot_page = 1;
        document.getElementById("tbody-captured-screenshot-details").innerHTML = "Loading...";
    }

    json_string = JSON.stringify({
        "id": session_id,
        "page": cobrowse_session_captured_screenshot_page
    });

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/agent/get-meta-information/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {

                if (response.meta_information_list.length == 0) {
                    document.getElementById("tbody-captured-screenshot-details").innerHTML = "No captured screenshot";
                    return;
                }

                var tbody_html = '';
                meta_information_list = response.meta_information_list;
                for (var index = 0; index < meta_information_list.length; index++) {
                    meta_id = meta_information_list[index]["id"];
                    //if (meta_information_list[index]["type"] == "screenshot") {
                    tbody_html += '<tr><td>' + meta_information_list[index]["type"] + '</td><td>' + meta_information_list[index]["datetime"] + '</td><td><!--<a href="/easy-assist-salesforce/agent/export/' + meta_id + '/?type=img" target="_blank" title="Export As Image"><i class="fas fa-fw fa-download"></i></a>-->&nbsp;<a href="/easy-assist-salesforce/agent/export/' + meta_id + '/?type=html&salesforce_token=' + window.SALESFORCE_TOKEN + '" target="_blank" title="Export As HTML"><i class="fas fa-fw fa-file-download"></i></a></td></tr>';
                    //} else {
                    //    tbody_html += '<tr><td>' + meta_information_list[index]["type"] + '</td><td>' + meta_information_list[index]["datetime"] + '</td></tr>';
                    //}
                }

                if (response.is_last_page == false) {
                    tbody_html += '<tr onclick="load_more_captured_screenshot_details(this, \'' + session_id + '\')"><td colspan="2"><button class="btn btn-primary float-right">Load More</button></td></tr>';
                }

                if (cobrowse_session_captured_screenshot_page == 1) {
                    document.getElementById("tbody-captured-screenshot-details").innerHTML = tbody_html;
                } else {
                    document.getElementById("tbody-captured-screenshot-details").innerHTML += tbody_html;
                }
            } else {
                show_easyassist_toast("Unable to load the details. Kindly try again.");
            }
            load_more_captured_screenshot = false;
        }
    }
    xhttp.send(params);
}

function load_more_captured_screenshot_details(element, session_id) {
    element.parentElement.removeChild(element);
    cobrowse_session_captured_screenshot_page += 1;
    load_more_captured_screenshot = true;
    show_captured_screenshot_details(session_id);
}


var load_more_agent_comments = false;
var cobrowse_session_agent_comments_page = 1;

function show_agents_comment_for_session(session_id) {

    $("#see_captured_screenshot").modal('hide');

    if (load_more_agent_comments == false) {
        cobrowse_session_agent_comments_page = 1;
        document.getElementById("tbody-agent-comments-details").innerHTML = "Loading...";
    }

    json_string = JSON.stringify({
        "id": session_id,
        "page": cobrowse_session_agent_comments_page
    });

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/agent/get-cobrowse-agent-comments/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {

                if (response.agent_comments_list.length == 0) {
                    document.getElementById("agent-comments-table").style.display = "none";
                    document.getElementById("no-comments-empty-message").style.display = "block";
                    return;
                }else{
                    document.getElementById("agent-comments-table").style= "max-height: 305px;overflow-y: scroll;";
                    document.getElementById("no-comments-empty-message").style.display = "none";
                }

                var tbody_html = '';
                agent_comments_list = response.agent_comments_list;
                for (var index = 0; index < agent_comments_list.length; index++) {
                    tbody_html += '<tr><td>' + agent_comments_list[index]["agent"] + '</td>\
                    <td>' + agent_comments_list[index]["comments"] + '</td>\
                    <td>' + agent_comments_list[index]["datetime"] + '</td>\
                    </tr>';
                }

                if (response.is_last_page == false) {
                    tbody_html += '<tr onclick="load_more_agent_comments_details(this, \'' + session_id + '\')"><td colspan="2"><button class="btn btn-primary float-right">Load More</button></td></tr>';
                }

                if (cobrowse_session_agent_comments_page == 1) {
                    document.getElementById("tbody-agent-comments-details").innerHTML = tbody_html;
                } else {
                    document.getElementById("tbody-agent-comments-details").innerHTML += tbody_html;
                }
            } else {
                show_easyassist_toast("Unable to load the details. Kindly try again.");
            }
            load_more_agent_comments = false;
        }
    }
    xhttp.send(params);
}

function load_more_agent_comments_details(element, session_id) {
    element.parentElement.removeChild(element);
    cobrowse_session_agent_comments_page += 1;
    load_more_agent_comments = true;
    show_agents_comment_for_session(session_id);
}


var load_more_system_audit_trail = false;
var system_audit_trail_page = 1;

function show_system_audit_trail_details(session_id) {

    if (load_more_system_audit_trail == false) {
        system_audit_trail_page = 1;
        document.getElementById("tbody_see_system_audit_trail").innerHTML = "Loading...";
    }

    json_string = JSON.stringify({
        "id": session_id,
        "page": system_audit_trail_page
    });

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/agent/get-system-audit-trail-basic-activity/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {

                if (response.basic_activity_audit_trail_obj_list.length == 0) {
                    document.getElementById("tbody_see_system_audit_trail").innerHTML = "Audit trail not available";
                    return;
                }

                var tbody_html = '';
                basic_activity_audit_trail_obj_list = response.basic_activity_audit_trail_obj_list;
                for (var index = 0; index < basic_activity_audit_trail_obj_list.length; index++) {
                    tbody_html += '<tr><td>' + basic_activity_audit_trail_obj_list[index]["datetime"] + '</td>\
                    <td>' + basic_activity_audit_trail_obj_list[index]["description"] + '</td>\
                    </tr>';
                }

                if (response.is_last_page == false) {
                    tbody_html += '<tr onclick="load_more_system_audit_trail_details(this, \'' + session_id + '\')"><td colspan="2"><button class="btn btn-primary float-right">Load More</button></td></tr>';
                }

                if (system_audit_trail_page == 1) {
                    document.getElementById("tbody_see_system_audit_trail").innerHTML = tbody_html;
                } else {
                    document.getElementById("tbody_see_system_audit_trail").innerHTML += tbody_html;
                }
            } else {
                show_easyassist_toast("Unable to load the details. Kindly try again.");
            }
            load_more_system_audit_trail = false;
        }
    }
    xhttp.send(params);
}

function load_more_system_audit_trail_details(element, session_id) {
    element.parentElement.removeChild(element);
    system_audit_trail_page += 1;
    load_more_system_audit_trail = true;
    show_system_audit_trail_details(session_id);
}

function check_and_mark_agent_as_admin(element) {
    console.log(window.SALESFORCE_TOKEN);
    request_params = {
        "active_status": element.checked
    };
    json_params = JSON.stringify(request_params);

    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/switch-agent-mode/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status != 200) {
                show_easyassist_toast("Unable to update the active status");
            } else {
                if (element.checked) {
                    window.location = "/easy-assist-salesforce/sales-ai/dashboard/?salesforce_token=" + window.SALESFORCE_TOKEN;
                } else {
                    window.location = "/easy-assist-salesforce/sales-ai/dashboard/?salesforce_token=" + window.SALESFORCE_TOKEN;
                }
            }
        }
    }
    xhttp.send(params);
}

function show_agents_chat_history_for_session(session_id) {

    json_string = JSON.stringify({
        "session_id": session_id
    });

    encrypted_data = custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/agent/get-cobrowsing-chat-history/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response.chat_history.length > 0) {
                chat_html = '';
                chat_history = response.chat_history;
                for (var index = 0; index < chat_history.length; index++) {
                    sender = chat_history[index]["sender"];
                    message = chat_history[index]["message"];
                    datetime = chat_history[index]["datetime"];
                    attachment = chat_history[index]["attachment"];

                    if (sender == "client") {
                        if (attachment != null) {
                            var chat_temp_html = '<a href="' + attachment + '" target="_blank"><img src="/static/EasyAssistSalesforceApp/img/documents2.png" style="height: 100%;width: 40%;border-radius: 1em;object-fit: contain;"></a>';
                            chat_html += '<div style="width:98%;display:inline-block;"><div class="easychat-livechat-customer-attachment" style="float:left;">' + chat_temp_html + '<div class="easychat-livechat-message" style="color: black;">' + message + '</div><span class="message-time-user" style="color:black;">' + sender + ' | ' + datetime + '</span></div></div>';
                        } else {
                            chat_html += '<div class="easychat-bot-message-div" ><div class="easychat-bot-message easychat-bot-message-line" style="color:#00488D;" ><div class="easychat-show-less-text">' + message + '</div><span class="message-time-bot">' + sender + ' | ' + datetime + '</span></div></div>';
                        }
                    } else {
                        if (attachment != null) {
                            var chat_temp_html = '<a href="' + attachment + '" target="_blank"><img src="/static/EasyAssistSalesforceApp/img/documents2.png" style="height: 100%;width: 40%;border-radius: 1em;object-fit: contain;"></a>';
                            chat_html += '<div style="width:98%;display:inline-block;"><div class="easychat-livechat-customer-attachment" style="float:right; color: black;">' + chat_temp_html + '<div class="easychat-livechat-message">' + message + '</div><span class="message-time-user" style="color:black;">' + sender + ' | ' + datetime + '</span></div></div>';
                        } else {
                            chat_html += '<div class="easychat-user-message-div"><div class="easychat-user-message easychat-user-message-line" style="background-color:white !important;"><div class="easychat-show-less-text" style="color:black;">' + message + '</div><span class="message-time-user" style="color:black;">' + sender + ' | ' + datetime + '</span></div></div>';
                        }
                    }

                    document.getElementById("session-chat-history-container").innerHTML = chat_html;
                }
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
        for (var i = 0; i < length; i++) {
            result += characters.charAt(Math.floor(Math.random() * charactersLength));
        }
        return result;
    }


    function custom_encrypt_variable(data) {
        utf_data = CryptoJS.enc.Utf8.parse(data);
        encoded_data = utf_data;
        random_key = generate_cobrowsing_random_string(16);
        var iv = CryptoJS.lib.WordArray.random(16);
        var encrypted = CryptoJS.AES.encrypt(encoded_data, CryptoJS.enc.Utf8.parse(random_key), {
            iv: iv
        });
        var return_value = random_key;
        return_value += "." + encrypted.toString();
        return_value += "." + CryptoJS.enc.Base64.stringify(iv);
        return return_value;
    }

    cobrowsing_feedback_error_element = document.getElementById("cobrowsing-feedback-error");
    cobrowsing_feedback_error_element.innerHTML = "";
    flag_error = false;

    description = document.getElementById('cobrowsing-feedback-textarea').value.trim();
    if (description == "") {
        cobrowsing_feedback_error_element.style.color = "red";
        cobrowsing_feedback_error_element.innerHTML = "*Description cannot be empty";
        return;
    }

    feedback_category = document.getElementById("cobrowsing-feedback-category").value;
    if (feedback_category == "None") {
        cobrowsing_feedback_error_element.style.color = "red";
        cobrowsing_feedback_error_element.innerHTML = "*Category cannot be empty";
        return;
    }

    feedback_priority = document.getElementById("cobrowsing-feedback-priority").value;
    if (feedback_priority == "None") {
        cobrowsing_feedback_error_element.style.color = "red";
        cobrowsing_feedback_error_element.innerHTML = "*Priority cannot be empty";
        return;
    }

    is_feedback_screenshot_attached = true;
    if (!($("#cobrowsing-feedback-file"))[0].files[0]) {
        is_feedback_screenshot_attached = false;
    }

    action_element.innerHTML = "submitting...";

    if (is_feedback_screenshot_attached) {

        var input_upload_image = ($("#cobrowsing-feedback-file"))[0].files[0]
        if(check_malicious_file(input_upload_image.name) == true) {
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
                    json_string = JSON.stringify({
                        description: description,
                        category: feedback_category,
                        priority: feedback_priority,
                        app: "EasyAssist",
                        src: response['src'],
                    });
                    json_string = custom_encrypt_variable(json_string);
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
                            } else {
                                show_easyassist_toast("Unable to save feedback.");
                            }
                            action_element.innerHTML = "Submit";
                        },
                        error: function(xhr, textstatus, errorthrown) {}
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
        json_string = JSON.stringify({
            description: description,
            category: feedback_category,
            priority: feedback_priority,
            app: "EasyAssist",
            src: "",
        });
        json_string = custom_encrypt_variable(json_string);
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


function export_support_history(el) {

    el.innerHTML = "Exporting...";
    el.disabled = true;

    var filter_params_dict = {};
    var url = decodeURIComponent(window.location.href);

    var params_str = url.split("/").slice(-1)[0].substr(1);
    var params_list = params_str.split("&");
    for (var index = 0; index < params_list.length; index++) {
        if (params_list[index].indexOf("=") == -1) {
            continue;
        }
        var key = params_list[index].split("=")[0];
        var value = params_list[index].split("=")[1];

        if (!(key in filter_params_dict)) {
            filter_params_dict[key] = []
        }

        filter_params_dict[key].push(value);
    }

    var json_string = JSON.stringify(filter_params_dict);

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/sales-ai/export-support-history/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path"] != null) {
                export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path + "?salesforce_token=" + window.SALESFORCE_TOKEN
            } else {
                show_easyassist_toast("Unable to download support history");
            }
            el.innerHTML = "Export";
            el.disabled = false;
        }
    }
    xhttp.send(params);
}

function export_unattended_leads(el) {

    el.innerHTML = "Exporting...";
    el.disabled = true;

    var filter_params_dict = {};
    var url = decodeURIComponent(window.location.href);

    var params_str = url.split("/").slice(-1)[0].substr(1);
    var params_list = params_str.split("&");
    for (var index = 0; index < params_list.length; index++) {
        if (params_list[index].indexOf("=") == -1) {
            continue;
        }
        var key = params_list[index].split("=")[0];
        var value = params_list[index].split("=")[1];

        if (!(key in filter_params_dict)) {
            filter_params_dict[key] = []
        }

        filter_params_dict[key].push(value);
    }

    var json_string = JSON.stringify(filter_params_dict);

    var encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/sales-ai/export-unattended-leads-details/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path"] != null) {
                export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path + "?salesforce_token=" + window.SALESFORCE_TOKEN;
            } else {
                show_easyassist_toast("Unable to download unattended leads details");
            }
            el.innerHTML = "Export";
            el.disabled = false;
        }
    }
    xhttp.send(params);
}

function export_meeting_support_history(el) {

    el.innerHTML = "Exporting...";
    el.disabled = true;

    var filter_params_dict = {};
    var url = decodeURIComponent(window.location.href);

    var params_str = url.split("/").slice(-1)[0].substr(1);
    var params_list = params_str.split("&");
    for (var index = 0; index < params_list.length; index++) {
        if (params_list[index].indexOf("=") == -1) {
            continue;
        }
        var key = params_list[index].split("=")[0];
        var value = params_list[index].split("=")[1];

        if (!(key in filter_params_dict)) {
            filter_params_dict[key] = []
        }

        filter_params_dict[key].push(value);
    }

    var json_string = JSON.stringify(filter_params_dict);

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/sales-ai/export-meeting-support-history/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path"] != null) {
                export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path + "?salesforce_token=" + window.SALESFORCE_TOKEN;
            } else {
                show_easyassist_toast("Unable to download meeting support history");
            }
                el.innerHTML = "Export";
                el.disabled = false;
        }
    }
    xhttp.send(params);
}

function check_file_extension(filename) {
    var fileExtension = "";
    if (filename.lastIndexOf(".") > 0) {
        fileExtension = filename.substring(filename.lastIndexOf(".") + 1, filename.length);
    }
    fileExtension = fileExtension.toLowerCase();
    var image_extensions = ["png", "jpg", "jpeg", "svg", "bmp", "gif", "tiff", "exif", "jfif"];
    var ppt_extensions = ["ppt", "pptx", "pptm"];
    var docs_extensions = ["doc", "docx", "odt", "rtf", "txt"];
    var pdf_extensions = ["pdf"];
    var excel_extensions = ["xls", "xlsx", "xlsm", "xlt", "xltm"];
    var video_extensions = ["avi", "flv", "wmv", "mov", "mp4"];

    if (image_extensions.includes(fileExtension)) return true;
    if (ppt_extensions.includes(fileExtension)) return true;
    if (docs_extensions.includes(fileExtension)) return true;
    if (pdf_extensions.includes(fileExtension)) return true;
    if (excel_extensions.includes(fileExtension)) return true;
    if (video_extensions.includes(fileExtension)) return true;
    return false;
}

var support_file_upload_data_list = [];
var support_file_upload_total_count = 0;
var support_file_read_completed_count = 0;
var support_file_reading_index = 0;
var customer_support_file_save_request_interval;
var read_files_customer_support_interval;

function customer_support_file_save_request() {
    if (support_file_read_completed_count == support_file_upload_total_count) {
        clearInterval(customer_support_file_save_request_interval)
        json_string = JSON.stringify(support_file_upload_data_list);

        encrypted_data = custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/sales-ai/upload-customer-support-files/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    if (response["file_upload_fail"].length > 0) {
                        customer_support_file_upload_error = document.getElementById("customer-support-file-upload-error");
                        customer_support_file_upload_error.innerHTML = "";
                        if (response["file_upload_success"].length > 0) {
                            customer_support_file_upload_error.innerHTML += "Successfully Uploaded";
                            for (var index_success = 0; index_success < response["file_upload_success"].length; index_success++) {
                                customer_support_file_upload_error.innerHTML += "<br>" + response["file_upload_success"][index_success]
                            }
                        }
                        customer_support_file_upload_error.innerHTML += "<br>Not Uploaded";
                        for (var index_success = 0; index_success < response["file_upload_fail"].length; index_success++) {
                            customer_support_file_upload_error.innerHTML += "<br>" + response["file_upload_fail"][index_success]
                        }
                    } else {
                        customer_support_file_upload_error.innerHTML = "Files uploaded successfully!";
                        setTimeout(function() {
                            $('#customer_support_document_modal').modal('toggle');
                            location.reload();
                        }, 1000);
                    }
                    $("#customer-support-file-upload").val("");
                } else {
                    customer_support_file_upload_error.innerHTML = "File Not Uploaded."
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
        var input_uploaded_files = ($("#customer-support-file-upload"))[0].files;
        var file = input_uploaded_files[support_file_reading_index];

        var reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = function() {

            base64_str = reader.result.split(",")[1];

            support_file_upload_data_list.push({
                "filename": file.name,
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

    customer_support_file_upload_error = document.getElementById("customer-support-file-upload-error");
    customer_support_file_upload_error.innerHTML = ""
    customer_support_file_upload_error.style.color = "";
    customer_support_file_upload_error.innerHTML = "<br>Loading..."

    var input_uploaded_files = ($("#customer-support-file-upload"))[0].files;

    if (input_uploaded_files.length == 0) {
        customer_support_file_upload_error.style.color = "red";
        customer_support_file_upload_error.innerHTML = "Please select file to upload."
        return;
    }

    if (input_uploaded_files.length > 10) {
        customer_support_file_upload_error.style.color = "red";
        customer_support_file_upload_error.innerHTML = "Maximum 10 files can be uploaded at a time."
        return;
    }

    var file_name = '', file_check = false;
    $.each(input_uploaded_files, function(index, file) {
        file_name = file.name;
        file_check = check_file_extension(file_name);
        if (file_check == false) {
            customer_support_file_upload_error.style.color = "red";
            customer_support_file_upload_error.innerHTML = "You can only upload Images, PPTs, Docs, PDFs, Excels and Videos. Please choose the files again.";
            return;
        }
        if(check_malicious_file(file_name) == true) {
            return;
        }
    });
    if (file_check == false) return;

    support_file_upload_data_list = []
    support_file_upload_total_count = ($("#customer-support-file-upload"))[0].files.length
    support_file_read_completed_count = 0;
    support_file_reading_index = 0;

    read_files_customer_support_interval = setInterval(read_files_customer_support, 500);
    customer_support_file_save_request_interval = setInterval(customer_support_file_save_request, 3000)
}

$(".user-checkbox-collection-delete").change(function() {
    var user_checkbox_collection_delete = document.getElementsByClassName("user-checkbox-collection-delete");
    var delete_count = 0;
    for (var index = 0; index < user_checkbox_collection_delete.length; index++) {
        if (user_checkbox_collection_delete[index].checked) {
            delete_count++;
            break;
        }
    }
    if (delete_count > 0) {
        document.getElementById("customer-support-delete-button").style.display = "inline-block";
    } else {
        document.getElementById("customer-support-delete-button").style.display = "none";
    }
})

function save_customer_support_document_details(delete_document = false) {
    var user_checkbox_collection_usable = document.getElementsByClassName("user-checkbox-collection-usable");
    var user_checkbox_collection_delete = document.getElementsByClassName("user-checkbox-collection-delete");
    var user_checkbox_collection_filename = document.getElementsByClassName("user-checkbox-collection-filename");
    var customer_support_document_update_dict = {};

    for (var index = 0; index < user_checkbox_collection_usable.length; index++) {

        var user_input = {};


        if (delete_document == false) {
            if (user_checkbox_collection_usable[index].checked) {
                user_input["is_usable"] = 1;
            } else {
                user_input["is_usable"] = 0;
            }

            user_input["file_name"] = user_checkbox_collection_filename[index].value
        } else {
            if (user_checkbox_collection_delete[index].checked) {
                user_input["is_deleted"] = 1;
            } else {
                user_input["is_deleted"] = 0;
            }
        }

        customer_support_document_update_dict[user_checkbox_collection_usable[index].id] = user_input;
    }

    var json_string = JSON.stringify(customer_support_document_update_dict);

    var encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/sales-ai/update-support-document-detail/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
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

function save_customer_support_document_preference() {
    var user_checkbox_collection_usable = document.getElementsByClassName("user-checkbox-collection-usable");
    var user_checkbox_collection_delete = document.getElementsByClassName("user-checkbox-collection-delete");
    var user_checkbox_collection_filename = document.getElementsByClassName("user-checkbox-collection-filename");
    var customer_support_document_update_dict = {};

    for (var index = 0; index < user_checkbox_collection_usable.length; index++) {

        var user_input = {};

        if (user_checkbox_collection_usable[index].checked) {
            user_input["is_usable"] = 1;
        } else {
            user_input["is_usable"] = 0;
        }


        if (user_checkbox_collection_delete[index].checked) {
            user_input["is_deleted"] = 1;
        } else {
            user_input["is_deleted"] = 0;
        }

        user_input["file_name"] = user_checkbox_collection_filename[index].value

        customer_support_document_update_dict[user_checkbox_collection_usable[index].id] = user_input;
    }

    var json_string = JSON.stringify(customer_support_document_update_dict);

    var encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/sales-ai/update-support-document-detail/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
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
    var PM = time.match('PM') ? true : false

    time = time.split(':')
    if (PM) {
        if (time[0] < 12) {
            var hour = 12 + parseInt(time[0], 10)
            var min = time[1].replace('PM', '')
        } else {
            var hour = 12
            var min = time[1].replace('PM', '')
        }
    } else {
        var hour = time[0]
        if (hour < 12) {
            var min = time[1].replace('AM', '')
        } else {
            hour = "00"
            var min = time[1].replace('AM', '')
        }
    }

    meeting_format = hour + ':' + min
    return meeting_format
}

function generate_sharable_link(element) {

    error_message_element = document.getElementById("generate-link-details-error");
    error_message_element.innerHTML = "";

    full_name = document.getElementById("client-full-name").value;
    mobile_number = document.getElementById("client-modile-number").value;
    email = document.getElementById("client-email-id").value;

    const regName = /^[a-zA-Z ]+$/;
    const regMob = /^[6-9]{1}[0-9]{9}$/;
    const regEmail = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;

    if(email != "" ){
        if (!regEmail.test(email)) {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Please enter valid Email ID.";
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

    meeting_description = document.getElementById("client-meeting-description").value;
    meeting_description = stripHTML(meeting_description);
    meeting_description = remove_special_characters_from_str(meeting_description);
    if (meeting_description == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter the meeting description.";
        return;
    }

    meeting_start_date = document.getElementById("client-meeting-start-date").value;
    if (meeting_start_date == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter the meeting date.";
        return;
    }

    meet_date_year = meeting_start_date.split("-")[0]
    meet_date_month = meeting_start_date.split("-")[1]
    meet_date_date = meeting_start_date.split("-")[2]

    if (meet_date_year < new Date().getFullYear()) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid meeting date.";
        return;
    } else if (meet_date_year == new Date().getFullYear() && meet_date_month < (new Date().getMonth() + 1)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid meeting date.";
        return;
    } else if (meet_date_year == new Date().getFullYear() && meet_date_month == (new Date().getMonth() + 1) && meet_date_date < new Date().getDate()) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid meeting date.";
        return;
    }

    var current_time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

    meeting_start_time = document.getElementById("client-meeting-start-time").value;
    if (meeting_start_time == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter the start time.";
        return;
    }
    meeting_start_time = meeting_time_format(meeting_start_time)

    if(meeting_start_time < current_time){
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "You have entered a time in the past. Please enter a valid start time.";
        return;
    }

    meeting_end_time = document.getElementById("client-meeting-end-time").value;
    if (meeting_end_time == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter the end time.";
        return;
    }
    meeting_end_time = meeting_time_format(meeting_end_time)
    if(meeting_end_time < current_time){
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "You have entered a time in the past. Please enter a valid end time.";
        return;
    }

    if (meeting_start_time >= meeting_end_time) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Start time should be less than end time.";
        return;
    }
    meeting_password = document.getElementById("client-meeting-password").value;

    request_params = {
        "full_name": full_name,
        "mobile_number": mobile_number,
        "meeting_description": meeting_description,
        "meeting_start_date": meeting_start_date,
        "meeting_end_time": meeting_end_time,
        "meeting_start_time": meeting_start_time,
        "meeting_password": meeting_password,
        "email": email
    };

    json_params = JSON.stringify(request_params);

    encrypted_data = custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);
    element.innerHTML = "Generating...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/generate-video-meeting/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                video_link = response["video_link"] + "?salesforce_token=" + window.SALESFORCE_TOKEN;
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


function save_meeting_link(element, meeting_id) {

    error_message_element = document.getElementById("generate-link-details-error-" + meeting_id);
    error_message_element.innerHTML = "";

    full_name = document.getElementById("client-full-name-" + meeting_id).value;
    mobile_number = document.getElementById("client-modile-number-" + meeting_id).value;
    email = document.getElementById("client-email-id-" + meeting_id).value;

    const regName = /^[a-zA-Z ]+$/;
    const regMob = /^[6-9]{1}[0-9]{9}$/;
    const regEmail = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;

    if (!regEmail.test(email)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid email id.";
        return;
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

    meeting_description = document.getElementById("client-meeting-description-" + meeting_id).value;
    meeting_description = stripHTML(meeting_description);
    meeting_description = remove_special_characters_from_str(meeting_description);
    if (meeting_description == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter the meeting description.";
        return;
    }

    meeting_start_date = document.getElementById("client-meeting-start-date-" + meeting_id).value;
    if (meeting_start_date == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter the meeting date.";
        return;
    }

    meet_date_year = meeting_start_date.split("-")[0]
    meet_date_month = meeting_start_date.split("-")[1]
    meet_date_date = meeting_start_date.split("-")[2]

    if (meet_date_year < new Date().getFullYear()) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid meeting date.";
        return;
    } else if (meet_date_year == new Date().getFullYear() && meet_date_month < (new Date().getMonth() + 1)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid meeting date.";
        return;
    } else if (meet_date_year == new Date().getFullYear() && meet_date_month == (new Date().getMonth() + 1) && meet_date_date < new Date().getDate()) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid meeting date.";
        return;
    }

    var current_time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

    meeting_start_time = document.getElementById("client-meeting-start-time-" + meeting_id).value;
    if (meeting_start_time == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter the start time.";
        return;
    }

    meeting_start_time = meeting_time_format(meeting_start_time)

    if(meeting_start_time < current_time){
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "You have entered a time in the past. Please enter a valid start time.";
        return;
    }

    meeting_end_time = document.getElementById("client-meeting-end-time-" + meeting_id).value;
    if (meeting_end_time == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter the end time.";
        return;
    }
    meeting_end_time = meeting_time_format(meeting_end_time)

    if(meeting_end_time < current_time){
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "You have entered a time in the past. Please enter a valid end time.";
        return;
    }

    if (meeting_start_time >= meeting_end_time) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Start time should be less than end time.";
        return;

    }
    meeting_password = document.getElementById("client-meeting-password-" + meeting_id).value;
    request_params = {
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

    json_params = JSON.stringify(request_params);

    encrypted_data = custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);
    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/save-video-meeting/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                window.location = window.location.href;
            } else {
                error_message_element.innerHTML = "Unable to save video meeting";
            }
            element.innerHTML = "Save";
        }
    }
    xhttp.send(params);
}


function assign_meeting_to_another_agent(element, meeting_id) {

    assign_agent_element = document.getElementById("select-assign-agent-"+meeting_id);
    agent_id = assign_agent_element.value;
    agent_email = assign_agent_element.options[assign_agent_element.selectedIndex].text;

    request_params = {
        "meeting_id": meeting_id,
        "agent_id": agent_id
    };

    json_params = JSON.stringify(request_params);

    encrypted_data = custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);
    element.innerHTML = "Assigning...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/assign-video-meeting/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                send_notification('A meeting has been assigned to ' + agent_email + ".");
                play_notification_sound();
                setTimeout('', 1000);
            }
            element.innerHTML = "Assigned";
            window.location.reload()
        }
    }
    xhttp.send(params);
}



function assign_cobrowsing_session_to_another_agent(element, session_id) {

    assign_agent_element = document.getElementById("select-assign-agent-"+session_id);
    agent_id = assign_agent_element.value;
    agent_email = assign_agent_element.options[assign_agent_element.selectedIndex].text;

    request_params = {
        "session_id": session_id,
        "agent_id": agent_id
    };

    json_params = JSON.stringify(request_params);

    encrypted_data = custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);
    element.innerHTML = "Assigning...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/assign-cobrowsing-session/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                send_notification('A meeting has been assigned to ' + agent_email + ".");
                play_notification_sound();
                setTimeout('', 1000);
                window.location.reload()
            } else if(response["status"] == 400) {
                document.getElementById("assign-session-error").innerHTML = "Failed to assign session. Agent is offline.";
                document.getElementById("assign-session-error").style.display = "block";
            } else {
                document.getElementById("assign-session-error").innerHTML = "Internal server error.";
                document.getElementById("assign-session-error").style.display = "block";
            }
            element.innerHTML = "Assigned";
        }
    }
    xhttp.send(params);
}



function get_client_agent_chats(meeting_audit_trail_id) {

    var json_string = JSON.stringify({
        "meeting_audit_trail_id": meeting_audit_trail_id
    });

    var encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/get-client-agent-chats/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                message_history = response["message_history"]
                html = ""
                for (var i = 0; i < message_history.length; i++) {
                    sender = message_history[i]["sender"]
                    if (sender == "agent") {
                        html += '<div class="cobrowse-msg right-cobrowse-msg">\
                                    <div class="cobrowse-msg-img" style="background-image: url(/static/EasyAssistSalesforceApp/img/chat_icon.svg)"></div>\
                                        <div class="cobrowse-msg-bubble">\
                                            <div class="cobrowse-msg-info">'

                        html += '<div class="cobrowse-msg-info-name">' + sender + '</div>'
                        html += '<div class="cobrowse-msg-info-time">' + message_history[i]["time"] + '</div>'
                        html += '</div><div class="cobrowse-msg-text">' + message_history[i]["message"] + '</div></div></div>'
                    } else {
                        html += '<div class="cobrowse-msg left-cobrowse-msg">\
                                                    <div class="cobrowse-msg-img" style="background-image: url(/static/EasyAssistSalesforceApp/img/chat_icon.svg)"></div>\
                                                    <div class="cobrowse-msg-bubble">\
                                                        <div class="cobrowse-msg-info">'
                        html += '<div class="cobrowse-msg-info-name">' + sender + '</div>'
                        html += '<div class="cobrowse-msg-info-time">' + message_history[i]["time"] + '</div>'
                        html += '</div><div class="cobrowse-msg-text">' + message_history[i]["message"] + '</div></div></div>'
                    }
                }
                document.getElementById("client-agent-chat-history").innerHTML = html
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
    const sw_registration = await navigator.serviceWorker.register('/service-worker-cobrowse.js').then(function() {
        return navigator.serviceWorker.ready;
    })
    .then(function(registration) {
        // adding log for testing purpose
        console.log(registration); // service worker is ready and working...
    });
};


const request_notification_permission = async () => {
    if (Notification.permission !== "granted") {
        const permission = await window.Notification.requestPermission();
        // value of permission can be 'granted', 'default', 'denied'
        // granted: user has accepted the request
        // default: user has dismissed the notification permission popup by clicking on x
        // denied: user has denied the request.
    }
};

const setup_service_worker = async () => {
    try {
        const permission = await request_notification_permission();
        const sw_registration = await register_service_worker();
    } catch(err) { }
};

if ('serviceWorker' in navigator) {
    window.addEventListener('load', async function() {
        setup_service_worker();
    });
}

function play_notification_sound() {
    // let audio_src = 'https://www.soundjay.com/button/sounds/beep-24.mp3';
    let audio_src = '/files/sounds/notification.mp3';
    let audio_obj = new Audio(audio_src);
    audio_obj.play();
}

function send_desktop_notification(notification_message, redirect_url) {
    if (!("Notification" in window)) {

        alert("This browser does not support desktop notification");
    
    }else if (Notification.permission === "granted") {
    
        var notification = new Notification('Cogno Cobrowse', {
            body: notification_message
        });
        if (redirect_url != null) {
            notification.onclick = function(){
                window.open(redirect_url, "_blank");
            }
        }
    }else {
    
        Notification.requestPermission().then(function (permission) {
            if (permission === "granted") {
                var notification = new Notification('Cogno Cobrowse', {
                    body: notification_message
                });
                if (redirect_url != null) {
                    notification.onclick = function(){
                        window.open(redirect_url, "_blank");
                    }
                }
            }
        });
    
    }
}

async function send_sw_notification(notification_message, redirect_url) {
    try {
        await navigator.serviceWorker.ready.then(function(serviceWorker) {
            serviceWorker.showNotification("Cogno Cobrowse", {
                body: notification_message,
                data: {
                    url: redirect_url
                }
            });
            
        }, function() {
            send_desktop_notification(notification_message, redirect_url);
        });
    } catch(err) {
        send_desktop_notification(notification_message, redirect_url);
    }
}

function send_notification(notification_message) {

    request_params = {
        "notification_message": notification_message
    };

    json_params = JSON.stringify(request_params);

    encrypted_data = custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/send-salesforce-notification/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                send_sw_notification(notification_message, response["redirect_url"]);
            } else {
                send_sw_notification(notification_message, null);
            }
            check_and_reload_page();
        }
    }
    xhttp.send(params);
}

function check_and_reload_page() {

    if (window.location.href.indexOf("easy-assist-salesforce/sales-ai/dashboard") != -1 && EASYASSIST_AGENT_ROLE == 'agent') {

        window.location.reload();
    }
}


///////////////////////    CognoAI Signal Development  /////////////////////////////////////

function create_client_server_signal(websocket_token, sender) {
    var websocket_token = CryptoJS.MD5(websocket_token).toString();
    ws_scheme = window.location.protocol == "http:" ? "ws" : "wss";
    url = ws_scheme + '://' + window.location.host + '/ws/cognoai-signal/' + websocket_token + '/' + sender + "/";
    if (client_server_websocket == null) {
        client_server_websocket = new WebSocket(url);
        client_server_websocket.onmessage = sync_client_server_signal;
        client_server_websocket.onerror = client_server_signal_error;
        client_server_websocket.onopen = client_server_signal_open;
        client_server_websocket.onclose = close_client_server_signal;
    }
}

function client_server_signal_error(e) {

    console.error("WebSocket error observed:", e);
}

function client_server_signal_open(e) {

    client_server_websocket_open = true;
    client_server_heartbeat_timer = setInterval(function(e) {
        client_server_signal_heartbeat();
    }, 5000);
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
    } else {
        create_client_server_signal("easyassist", "client");
    }
}


function client_server_signal_heartbeat() {

    json_string = JSON.stringify({
        "type": "heartbeat",
    });

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_client_server_signal(encrypted_data, "client");
}

function close_client_server_signal(e) {

    if (client_server_websocket == null) {
        return;
    }
    clearInterval(client_server_heartbeat_timer);
    client_server_websocket_open = false;
    client_server_websocket.close();
}

function sync_client_server_signal(e) {

    var data = JSON.parse(e.data);
    message = JSON.parse(data.message);
    data_packet = message.body.Request;

    data_packet = custom_decrypt(data_packet);
    data_packet = JSON.parse(data_packet);

    if (message.header.sender == "server") {
        if (data_packet.type == "notification") {

            check_notification(data_packet.response);
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
        for (var index = 0; index < notification_list.length; index++) {
            send_notification(notification_list[index]);
            play_notification_sound();
            setTimeout('', 1000);
        }
    }
}
// function check_notification(element) {
//  request_params = {};
//  json_params = JSON.stringify(request_params);
//  encrypted_data = custom_encrypt(json_params);
//  encrypted_data = {
//      "Request": encrypted_data
//  };
//  const params = JSON.stringify(encrypted_data);

//  var xhttp = new XMLHttpRequest();
//  xhttp.open("POST", "/easy-assist-salesforce/agent/check-notification/", true);
//  xhttp.setRequestHeader('Content-Type', 'application/json');
//  xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
//  xhttp.onreadystatechange = function() {
//      if (this.readyState == 4 && this.status == 200) {
//          response = JSON.parse(this.responseText);
//          response = custom_decrypt(response.Response);
//          response = JSON.parse(response);
//          if (response.status == 200) {
//              var notification_list = response.notification_list;
//              for(var index=0 ; index<notification_list.length ; index++){
//                  send_notification(notification_list[index]);
//                  play_notification_sound();
//                  setTimeout('', 1000);
//              }
//              if (notification_list.length) {

//                  check_and_reload_page();
//              }
//          }
//      }
//  }
//  xhttp.send(params);
// }

// setInterval(check_notification, 6000);
// check_notification();


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
    request_params = {
        "selected_language_pk_list": selected_language_pk_list,
        "selected_product_category_list":selected_product_category_list
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/agent/save-cobrowse-agent-advanced-details/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
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
    xhttp.open("POST", "/easy-assist-salesforce/scheduled-meetings-list/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            let html = "";
            if(response.status == 200) {
                let meeting_list = response.meeting_list;
                if(meeting_list.length == 0) {
                    html += "<div class=\"text-center\">";
                    html += "No Scheduled Meeting";
                    html += "</div>";
                    $('#todays_meeting_modal .modal-body').html(html);
                } else {
                    for(let idx = 0; idx < meeting_list.length; idx ++) {
                        html += "<tr>";
                        html += "<td>" + meeting_list[idx]["description"] + "</td>";
                        html += "<td>" + meeting_list[idx]["start_date"] + "</td>";
                        html += "<td>" + meeting_list[idx]["start_time"] + "</td>";
                        html += "<td>" + meeting_list[idx]["end_time"] + "</td>";
                        if(meeting_list[idx]["is_expired"]) {
                            html += "<td>Completed</td>"
                        } else {
                            html += "<td><a class=\"btn btn-info ml-3\" href=\"/easy-assist-salesforce/meeting/" + meeting_list[idx]["id"] + "/?salesforce_token=" + window.SALESFORCE_TOKEN + "\" target=\"_blank\" style=\"color:#fff!important;cursor:pointer;\">Join</a></td>";
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
                }
                $('#todays_meeting_modal').modal('show');
            }
        }
    }
    xhttp.send(null);
}

function delete_video_conferencing_form(form_id) {

    request_params = {
        "form_id": form_id,
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/sales-ai/delete-video-conferencing-form/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                window.location.reload();
            } else if(response.status == 300) {
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

    request_params = {
        "form_id": form_id,
        "selected_agents": selected_agents,
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var form_name = document.getElementById("cobrowse-form-name-" + form_id).innerHTML;

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/sales-ai/change-cobrowse-form-agent/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_easyassist_toast("List of agents for \"" + form_name + "\" is successfully updated.");
                FORM_AGENTS[form_id] = selected_agents;
            } else if(response.status == 300) {
                show_easyassist_toast("Unable to change form agent. Please try again");
            } else {
                show_easyassist_toast("Unable to change form agent. Please try again");
            }
        }
    }
    xhttp.send(params);
}

function check_malicious_file(file_name) {
    if(file_name.split('.').length != 2) {
        show_easyassist_toast("Please do not use .(dot) except for extension");
        return true;
    }

    var allowed_files_list = [
        "png", "jpg", "jpeg", "svg", "bmp", "gif", "tiff", "exif", "jfif", "webm", "mpg",
        "mp2", "mpeg", "mpe", "mpv", "ogg", "mp4", "m4p", "m4v", "avi", "wmv", "mov", "qt",
        "flv", "swf", "avchd","mp3", "aac", "pdf", "xls", "xlsx", "json", "xlsm", "xlt", "xltm", "zip"
    ];

    var file_extension = file_name.substring(file_name.lastIndexOf(".") + 1, file_name.length);
    file_extension = file_extension.toLowerCase();

    if(allowed_files_list.includes(file_extension) == false) {
        show_easyassist_toast("." + file_extension + " files are not allowed");
        return true;
    }
    return false;
}

function stripHTML(text){
   var regex = /(<([^>]+)>)/ig;
   return text.replace(regex, "");
}

function remove_special_characters_from_str(text) {
    var regex = /:|;|'|"|=|-|\$|\*|%|!|~|\^|\(|\)|\[|\]|\{|\}|\[|\]|#|<|>|\/|\\/g;
    text = text.replace(regex, "");
    return text;
}
