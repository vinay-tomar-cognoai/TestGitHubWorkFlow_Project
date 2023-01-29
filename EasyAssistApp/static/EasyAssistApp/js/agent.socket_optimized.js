var easyassist_tree_mirror = null;
var easyassist_iframe_tree_mirror = {};

var client_base_href = null;

var easyassist_send_agent_weak_connection_message_interval = null;
var framesContainer = document.querySelector('#frames-container');
var currentFrameIdx = 0;
var playbackIntervalId = null;
var cobrowseSocket = null;
var is_page_reloaded = false;
var sync_client_web_screen_timer = null;
var cobrowsing_meta_data_page = 1;
var load_more_meta = false;
var chunk_html_dict = {};
var internet_connectivity_timer = null;
var INTERNET_CON_TIMER = 30000;
var client_mouse_element = document.getElementById("client-mouse-pointer");
var margin_left_client_frame_container = 0;
var margin_top_client_frame_container = 0;
var requested_for_edit_access = false;
var ALLOW_SCREENSHARING_COBROWSE = false;
var session_has_ended = false;
var close_nav_timeout = null;
var check_meeting_status_interval = null;
var captured_video_stream = null;
var voip_meeting_initiated_agent = "";
var call_initiate_by_customer = "false";

var client_websocket = null;
var client_websocket_open = false;
var sync_utils_client_websocket = null;
var sync_utils_client_websocket_open = false;

var auto_msg_popup_on_client_call_declined = false;
var recording_start_time = null;
var client_iframe_width = 0;
var client_iframe_height = 0;
var EASYASSIST_IFRAME_ID_GLOBAL = 0;
var AGENT_WEAK_CONNECTION_DETECTED = null;
var AGENT_WEAK_CONNECTION_MODAL_SHOWN = false;
var is_html_requested = false;
var internet_connectivity_check_interval = null;

var EASYASSIST_FUNCTION_FAIL_DEFAULT_CODE = 500;
var EASYASSIST_FUNCTION_FAIL_DEFAULT_MESSAGE = "Due to some network issue, we are unable to process your request. Please Refresh the page.";
var easyassist_function_fail_time = 0;
var easyassist_function_fail_count = 0;
var is_html_request_received_to_client = false;
var html_request_interval = null;
var connected_successfully = false;
var chat_box_loaded = false;
var avg_speedMbps = 0;

var agent_pointer_position = {
    pageX: 0,
    pageY: 0,
    clientX: 0,
    clientY: 0,
    upper_hidden_pixel: 0,
}

var agent_scale_factor = 1;
var frame_container_parent_height = 0;
var frame_container_parent_width = 0;

var easyassist_agent_mouse_last_cordinates = null;
var easyassist_last_mouse_move_time = null;

var easyassist_sync_agent_mouse_timeout = null;
var easyassist_sync_agent_mouse_time = null;
var easyassist_sync_last_mouse_move_event = null;

var global_event_target_element = null;
var easyassist_drag_element = null;
var ACTIVE_TAB_CLIENT_PAGE_ID = null;
var CLIENT_TAB_MANAGER_INSTANCE = null;
var client_show_focus_toast_timeout = null;

var meeting_initiate_by_customer_status = "false"

var transfer_interval = null;

/* This is done for the IOS specific devices, 
In IOS devices after interacting with the DOM the audio was not playing, 
to fix this issue we simply play and stop the audio when the user touch the screen for the first time, so this will 
trigger the audio file initially and will allow the audio to play after that.*/
document.body.addEventListener('touchstart', function() {
    let audio_element = document.getElementById("easyassist-greeting-bubble-popup-sound");
    if(audio_element) {
        audio_element.play()
        audio_element.pause()
        audio_element.currentTime = 0
    }
}, false);

////////////////////////////////////////////////////

function easyassist_generate_unique_id() {
    var current_time = Date.now().toString(36);
    var random_value = Math.random().toString(36).substring(2);
    return current_time + random_value;
}

/******************* EASYASSIST HTML WEBSOCKET ************************/

function create_easyassist_socket(jid, sender) {
    ws_scheme = window.location.protocol == "http:" ? "ws" : "wss";
    url = ws_scheme + '://' + window.location.host + '/ws/cobrowse/' + jid + '/' + sender + "/";
    if (client_websocket == null) {
        client_websocket = new WebSocket(url);
        client_websocket.onmessage = sync_client_web_screen;
        client_websocket.onerror = function(e){
                console.error("WebSocket error observed:", e);
                client_websocket_open = false;
                easyassist_close_socket();

                var description = "error occured agent websocket. " + e.data;
                save_easyassist_system_audit_trail("socket", description);
        }
        client_websocket.onopen = function () {
            console.log("client_websocket created successfully")
            client_websocket_open = true;
            // if(ENABLE_LOW_BANDWIDTH_COBROWSING !== "True" && ENABLE_LOW_BANDWIDTH_COBROWSING !== true) {
            send_client_page_info_request();
            // }
        }
        client_websocket.onclose = function () {
            client_websocket_open = false;
            client_websocket = null;

            var description = "agent websocket is closed";
            save_easyassist_system_audit_trail("socket", description);
        }
    }
}

function easyassist_close_socket() {

    if (client_websocket == null) {
        return;
    }

    try {

        client_websocket.close();

    } catch(err) {

        client_websocket.onmessage = null;
        client_websocket = null;
    }
}

function send_message_over_easyassist_socket(message, sender) {
    try{
        if(client_websocket_open == false || client_websocket == null){
            if(send_message_over_easyassist_socket.caller.name == "easyassist_socket_callee"){
                return;
            }
            setTimeout(function easyassist_socket_callee(){
                send_message_over_easyassist_socket(message, sender);
            }, 5000);
            console.log("client_websocket is not open");
            return;
        }

        if (client_websocket_open == true && client_websocket != null) {
            var packet_id = easyassist_generate_unique_id();

            client_websocket.send(JSON.stringify({
                "message": {
                    "header": {
                        "sender": sender,
                        "client_page_id": ACTIVE_TAB_CLIENT_PAGE_ID,
                        "packet_id": packet_id,
                    },
                    "body": message
                }
            }));
        }
    }catch(err){
        console.error("ERROR : send_message_over_easyassist_socket ", err);
    }
}

/******************* END EASYASSIST HTML WEBSOCKET ************************/

/******************* EASYASSIST UTILITY  WEBSOCKET ************************/

function create_sync_utils_easyassist_socket(jid, sender) {
    jid = "sync_utils_" + jid;
    ws_scheme = window.location.protocol == "http:" ? "ws" : "wss";
    url = ws_scheme + '://' + window.location.host + '/ws/cobrowse/sync-utils/' + jid + '/' + sender + "/";
    if (sync_utils_client_websocket == null) {
        sync_utils_client_websocket = new WebSocket(url);
        sync_utils_client_websocket.onmessage = sync_client_web_screen;
        sync_utils_client_websocket.onerror = function(e){
                console.error("WebSocket error observed:", e);
                sync_utils_client_websocket_open = false;
                close_sync_utils_easyassist_socket();

                var description = "error occured agent websocket utils. " + e.data;
                save_easyassist_system_audit_trail("socket", description);
            }
        sync_utils_client_websocket.onopen = function(){
                console.log("sync_utils_client_websocket created successfully") 
                sync_utils_client_websocket_open = true;
            }
        sync_utils_client_websocket.onclose = function() {
                sync_utils_client_websocket_open = false;
                sync_utils_client_websocket = null;

                var description = "agent utils websocket is closed";
                save_easyassist_system_audit_trail("socket", description);
            }
    }
}

function close_sync_utils_easyassist_socket() {

    if(sync_utils_client_websocket == null) {
        return;
    }

    try {

        sync_utils_client_websocket.close();

    } catch(err) {

        sync_utils_client_websocket.onmessage = null;
        sync_utils_client_websocket = null;
    }

}

function send_message_over_sync_utils_easyassist_socket(message, sender) {
    try{
        if(sync_utils_client_websocket_open == false || sync_utils_client_websocket == null){
            if(send_message_over_sync_utils_easyassist_socket.caller.name == "easyassist_socket_callee"){
                return;
            }
            setTimeout(function easyassist_socket_callee(){
                send_message_over_sync_utils_easyassist_socket(message, sender);
            }, 5000);
            console.log("sync_utils_client_websocket is not open");
            return;
        }

        if (sync_utils_client_websocket_open == true && sync_utils_client_websocket != null) {
            var packet_id = easyassist_generate_unique_id();

            sync_utils_client_websocket.send(JSON.stringify({
                "message": {
                    "header": {
                        "sender": sender,
                        "client_page_id": ACTIVE_TAB_CLIENT_PAGE_ID,
                        "packet_id": packet_id,
                    },
                    "body": message
                }
            }));
        }
    } catch(err) {
        console.error("ERROR : send_message_over_sync_utils_easyassist_socket ", err);
    }
}

var easyassist_socket_not_open_count = 0;
var easyassist_socket_utils_not_open_count = 0;
var easyassist_socket_activity_interval_check = setInterval(easyassist_initialize_web_socket, 1000);

function easyassist_initialize_web_socket() {

    var easyassist_session_id = COBROWSE_SESSION_ID;
    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    if (client_websocket == null) {
        create_easyassist_socket(easyassist_session_id, "agent");
    }
    if (client_websocket.readyState !== client_websocket.OPEN){
        easyassist_socket_not_open_count++;
        if(easyassist_socket_not_open_count >= 5){
            easyassist_show_function_fail_modal(code=601);
        }
    } else {
        easyassist_socket_not_open_count = 0;
    }

    if (sync_utils_client_websocket == null) {
        create_sync_utils_easyassist_socket(easyassist_session_id, "agent");
    }
    if (sync_utils_client_websocket.readyState !== sync_utils_client_websocket.OPEN){
        easyassist_socket_utils_not_open_count++;
        if(easyassist_socket_utils_not_open_count >= 5){
            easyassist_show_function_fail_modal(code=601);
        }
    } else {
        easyassist_socket_utils_not_open_count = 0;
    }
}

// function send_recursively_html_request() {
//     if(html_request_interval != null) {
//         return;
//     }

//     if(!is_html_request_received_to_client) {
//         send_html_request_over_socket();
//     }

//     html_request_interval = setInterval(function() {
//         if(is_html_request_received_to_client) {
//             clearInterval(html_request_interval);
//             html_request_interval = null;
//         } else {
//             send_html_request_over_socket();
//         }
//     }, 8000);
// }

function send_html_request_over_socket() {

    if(check_screen_sharing_cobrowsing_enabled()) {
        return;
    }

    json_string = JSON.stringify({
        "type": "html",
        "is_agent_weak_connection": AGENT_WEAK_CONNECTION_DETECTED,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    //console.log("request for html has been sent: ", new Date());
    send_message_over_easyassist_socket(encrypted_data, "agent");
}

// function send_html_received_over_socket() {

//     if(check_screen_sharing_cobrowsing_enabled()) {
//         return;
//     }

//     json_string = JSON.stringify({
//         "type": "html_received",
//     });

//     encrypted_data = easyassist_custom_encrypt(json_string);
//     encrypted_data = {
//         "Request": encrypted_data
//     };

//     //console.log("request for html has been sent: ", new Date());
//     send_message_over_easyassist_socket(encrypted_data, "agent");
// }


/******************* END EASYASSIST UTILITY WEBSOCKET ************************/

var user_last_activity_time_obj = new Date()

function set_cookie(cookiename, cookievalue, path = "") {
    var domain = window.location.hostname.substring(window.location.host.indexOf(".") + 1);

    if(window.location.hostname.split(".").length==2){
        domain = window.location.hostname;
    }

    if (path == "") {
        document.cookie = cookiename + "=" + cookievalue + ";domain=" + domain;
    } else {
        document.cookie = cookiename + "=" + cookievalue + ";path=" + path + ";domain=" + domain;
    }
}

function openNav() {
    if(IS_ADMIN_AGENT == "False") {
        if(check_voip_video_meeting_enabled() || check_voip_enabled() || check_video_calling_enabled()) {
            check_voip_meeting_active_over_socket();
        }
    }
    try {
        document.getElementById("mySidenav").style.display = "";
        document.getElementById("maximise-button").style.display = "none";
        // document.getElementById("maximise-button").parentElement.style.top = "10%";
    } catch(err) {}
}

function closeNav() {
    try {
        document.getElementById("mySidenav").style.display = "none";
        document.getElementById("maximise-button").style.display = "";
        // document.getElementById("maximise-button").parentElement.style.top = "40%";
    } catch(err) {}
}

function create_close_nav_timeout(){
    if(close_nav_timeout == null){
        close_nav_timeout = setTimeout(closeNav, 15*1000);
    }
}

function clear_close_nav_timeout(){
    clearTimeout(close_nav_timeout);
    close_nav_timeout = null;
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
    var delay_by_nine_minutes = get_delayed_date_object(-18);
    if (user_last_activity_time_obj < delay_by_nine_minutes) { // if user is active in last minute ( after inactive for 9 minuits )
        user_last_activity_time_obj = new Date()
        send_session_timeout_request();
    }
    user_last_activity_time_obj = new Date()
}

function sync_mouse_position(event, is_from_chat_window = false) {

    if(IS_ADMIN_AGENT == "False") {
        return
    }
    if(easyassist_check_weak_connection_enabled()) {
        return;
    }

    if (is_from_chat_window == true) {
        var chat_window_position = $("#allincall-chat-box").position();
        upper_hidden_pixel = agent_pointer_position.upper_hidden_pixel;
        agent_pointer_position.pageX = event.pageX + chat_window_position.left - margin_left_client_frame_container;
        agent_pointer_position.pageY = event.pageY + chat_window_position.top + upper_hidden_pixel;
    } else {
        agent_pointer_position.pageX = event.pageX;
        agent_pointer_position.pageY = event.pageY;
        agent_pointer_position.clientX = event.clientX;
        agent_pointer_position.clientY = event.clientY;
        agent_pointer_position.upper_hidden_pixel = event.pageY - event.clientY;
    }

    var current_mouse_x = agent_pointer_position.clientX;
    var current_mouse_y = agent_pointer_position.clientY;
    var current_time = Date.now();

    if(easyassist_agent_mouse_last_cordinates != null) {
        var previous_mouse_x = easyassist_agent_mouse_last_cordinates.client_x;
        var previous_mouse_y = easyassist_agent_mouse_last_cordinates.client_y;

        var distance = Math.abs(previous_mouse_x - current_mouse_x) + Math.abs(previous_mouse_y - current_mouse_y);

        var mouse_move_diff = current_time - easyassist_last_mouse_move_time;

        if(easyassist_last_mouse_move_time != null && mouse_move_diff <= 200) {

            easyassist_sync_last_mouse_move_event = agent_pointer_position;
            current_time = Date.now();
            if(easyassist_sync_agent_mouse_timeout != null && current_time - easyassist_sync_agent_mouse_time <= 300) {
                clearTimeout(easyassist_sync_agent_mouse_timeout);
            }

            easyassist_sync_agent_mouse_timeout = setTimeout(function() {
                easyassist_sync_agent_mouse_last_coordinate();
            }, 300);

            easyassist_sync_agent_mouse_time = Date.now();

            if(distance <= 100) {
                return;
            }
        }
    }

    easyassist_last_mouse_move_time = current_time;

    easyassist_agent_mouse_last_cordinates = {
        client_x: current_mouse_x,
        client_y: current_mouse_y,
    };

    json_string = JSON.stringify({
        "type": "mouse",
        "position": agent_pointer_position
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function easyassist_sync_agent_mouse_last_coordinate() {
    try {

        json_string = JSON.stringify({
            "type": "mouse",
            "position": {
                "clientX": easyassist_sync_last_mouse_move_event.clientX,
                "clientY": easyassist_sync_last_mouse_move_event.clientY,
                "agent_window_width": window.outerWidth,
                "agent_window_height": window.outerHeight,
                "screen_width": screen.width,
                "screen_height": screen.height,
                "agent_window_x_offset": window.pageXOffset,
                "agent_window_y_offset": window.pageYOffset,
                "pageX": easyassist_sync_last_mouse_move_event.pageX,
                "pageY": easyassist_sync_last_mouse_move_event.pageY
            }
        });

        encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
        easyassist_sync_agent_mouse_timeout = null;
    } catch(err) {
        console.log("easyassist_sync_agent_mouse_last_coordinate: ", err);
    }
}

function strip_html(text){
   var regex = /(<([^>]+)>)/ig;
   text = text.replace(regex, "");

   return text;
}

function remove_special_characters_from_str(text) {
    var regex = /:|;|'|"|=|-|\$|\*|%|!|`|~|&|\^|\(|\)|\[|\]|\{|\}|\[|\]|#|<|>|\/|\\/g;
    text = text.replace(regex, "");
    return text;
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

function reset_internet_connectivity_check_timer() {
    stop_internet_connectivity_check_timer();
    start_internet_connectivity_check_timer();
}

function stop_internet_connectivity_check_timer() {
    if (internet_connectivity_timer != null && internet_connectivity_timer != undefined) {
        clearInterval(internet_connectivity_timer);
    }
}

function set_easyassist_cookie(cookiename, cookievalue) {

    var domain = window.location.hostname;
    var max_age = 24 * 60 * 60;

    if (window.location.protocol == "https:") {
        document.cookie = cookiename + "=" + cookievalue + ";max-age=" + max_age + ";path=/;domain=" + domain + ";secure";
    } else {
        document.cookie = cookiename + "=" + cookievalue + ";max-age=" + max_age + ";path=/;";
    }
}

function get_easyassist_cookie(cookiename) {
    var matches = document.cookie.match(new RegExp(
        "(?:^|; )" + cookiename.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? matches[1] : undefined;
}

function delete_easyassist_cookie(cookiename) {

    var domain = window.location.hostname;

    if (window.location.protocol == "https:") {
        document.cookie = cookiename + "=;path=/;domain=" + domain + ";secure;expires = Thu, 01 Jan 1970 00:00:00 GMT";
    } else {
        document.cookie = cookiename + "=;path=/;expires = Thu, 01 Jan 1970 00:00:00 GMT";
    }
}

function easyassist_delete_session_cookie(){
    delete_easyassist_cookie("is_lead_converted");
    delete_easyassist_cookie("request_edit_access");
    delete_easyassist_cookie("easyassist_client_disconnected_modal_shown");
    delete_easyassist_cookie("is_pdf_modal_open");
    delete_easyassist_cookie("easyassist_client_weak_internet_connection_shown");
    clearInterval(easyassist_send_agent_weak_connection_message_interval);
    easyassist_clear_local_storage();

    window.sessionStorage.removeItem("client_page_info_list");
}

function start_internet_connectivity_check_timer() {
    internet_connectivity_timer = setInterval(function(e) {
        if(get_easyassist_cookie("easyassist_session_id")){
            if(get_easyassist_cookie("easyassist_client_disconnected_modal_shown") == undefined || get_easyassist_cookie("easyassist_client_disconnected_modal_shown") == "false"){
                show_client_disconnect_modal();
                set_easyassist_cookie("easyassist_client_disconnected_modal_shown", "true")
            }
        }
        // show_easyassist_toast("We are not receiving any updates from client. Kindly check your internet connectivity.");
        // show_easyassist_toast("Looks like we are not receiving any updates from the customer side. Kindly check your internet connectivity or check whether the customer is still connected or not.");
        reset_internet_connectivity_check_timer();
    }, INTERNET_CON_TIMER);
}

function open_close_session_modal() {
    easyassist_update_lead_converted_status();
    check_is_lead_converted();
    try {
        document.getElementById('mySidenav').parentNode.style.display = "none";
        document.getElementById('mySidenav').style.display="none";
        if(document.getElementById("allincall-chat-box")) {            
            close_chatbot_animation();
        }
        if(document.getElementById('mySidenav-session-end')) {
            document.getElementById('mySidenav-session-end').style.display="none";
        }
    } catch(err) {}
    $("#close_session_modal").modal("show");
    framesContainer.style.filter = "blur(3px)";
}

function gain_focus(){
  framesContainer.style.filter = null;
  if(!session_has_ended){
    try {
        document.getElementById('mySidenav').parentNode.style.display = "inline-block";
        document.getElementById('mySidenav').style.display="flex";
    } catch(err) {}
  } else {
    try {
        if(document.getElementById('mySidenav-session-end')) {
            document.getElementById('mySidenav-session-end').style.display="flex";
        }
    } catch(err) {}
  }
}

function check_is_lead_converted() {
    if (get_easyassist_cookie("is_lead_converted") == COBROWSE_SESSION_ID) {
        $("#mask-successfull-cobrowsing-session").prop("checked", true)
        $("#mask-successfull-cobrowsing-session").attr("disabled", "disabled")
    }
}

function easyassist_update_lead_converted_status() {
    json_string = JSON.stringify({
        "type": "get_lead_status"
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

window.onload = function() {

    is_page_reloaded = true;

    delete_easyassist_cookie("is_pdf_modal_open");

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if(easyassist_session_id != COBROWSE_SESSION_ID){
        easyassist_delete_session_cookie();
    }
    set_easyassist_cookie("easyassist_session_id", COBROWSE_SESSION_ID);

    easyassist_create_local_storage_obj();

    if (IS_MOBILE == "True") {
        easyassist_create_custom_navbar();
    }

    local_storage_obj = get_easyassist_current_session_local_storage_obj();
                    
    if (local_storage_obj && local_storage_obj.hasOwnProperty("is_session_transferred_request_sent")) {
        if (local_storage_obj["is_session_transferred_request_sent"] == "true") {
            toggle_transfer_log_check_interval();
        } else {
            toggle_transfer_log_check_interval(false);
        }
    }

    sync_client_web_screen_timer = setInterval(function(e) {
        agent_heartbeat();
    }, 15000);

    sync_client_web_screen_agent_timer = setInterval(function(e) {
        sync_client_web_screen_agent();
    }, 10000);
    
    reset_internet_connectivity_check_timer();
    set_user_inactivity_detector();
    
    update_edit_access_icon_properties();

    setTimeout(function() {
        load_allincall_chat_box();
    }, 5000);

    easyassist_initialize_canvas();
    easyassist_initialize_drag_element();
    easyassist_initialize_client_tab_manager();

    ele = document.getElementById("join-customer-voice-call-meeting-btn")
    if(ele != undefined){
        if(IS_MOBILE == "True") {
            ele.parentNode.parentNode.style.display = "none";
        } else {
            ele.style.display = "none"
        }
    }

    if(IS_ADMIN_AGENT == "True"){
        delete_easyassist_cookie("customer_meeting_request_status");
    }

    if(IS_ADMIN_AGENT == "True"){
        var local_storage_obj = get_easyassist_current_session_local_storage_obj();
        if(local_storage_obj != null && local_storage_obj.hasOwnProperty("hide_agent_call_initiation_icon")) {
            if(local_storage_obj["hide_agent_call_initiation_icon"] == "true") {
                if(IS_MOBILE == "True") {
                    document.getElementById("request-cobrowsing-meeting-btn").parentNode.parentNode.style.display = "none";
                } else {
                    document.getElementById("request-cobrowsing-meeting-btn").style.display = 'none';
                }
            }
        }

        setInterval(function () {
            if(get_easyassist_cookie("is_cobrowse_meeting_active") == ""){
                set_easyassist_current_session_local_storage_obj("hide_agent_call_initiation_icon", "false");
                if(IS_MOBILE == "True") {
                    document.getElementById("request-cobrowsing-meeting-btn").parentNode.parentNode.style.display = "flex";
                } else {
                    document.getElementById("request-cobrowsing-meeting-btn").style.display = 'inherit';
                }
            }
        }, 1000);
    }

    $(':not(.tooltip-navbar)[data-toggle="tooltip"]').tooltip();

    try {
        if(ALLOW_VIDEO_MEETING_ONLY != true && ALLOW_VIDEO_MEETING_ONLY != "true" && ALLOW_VIDEO_MEETING_ONLY != "True") {
            if(check_voip_video_meeting_enabled() || check_voip_enabled()) {
                check_and_start_voip_meeting();
            } else if (check_video_calling_enabled()) {
                if(IS_ADMIN_AGENT == "False") {
                    check_voip_meeting_active_over_socket(true);
                }
            }
        }
        check_meeting_initiate_by_customer();
    } catch(err) {}

    setTimeout(() => {
        var local_storage_obj = get_easyassist_current_session_local_storage_obj();
        if(local_storage_obj != null && local_storage_obj.hasOwnProperty("is_call_ongoing_invited_agent")) {
            if(get_easyassist_cookie("meeting_initiate_by_customer_status") == "true"){
                if (local_storage_obj["is_call_ongoing_invited_agent"] == "true") {
                    show_side_nav_call_icon_for_customer_init_call();
                } else {
                    hide_side_nav_call_icon_for_customer_init_call();
                }
                delete_easyassist_cookie("meeting_initiate_by_customer_status");
            }
            else {
                if (local_storage_obj["is_call_ongoing_invited_agent"] == "true") {
                    show_side_nav_call_icon();
                } else {
                    hide_side_nav_call_icon();
                }
            }
        }
    }, 10000);

    setTimeout(function(){
        var local_storage_obj = get_easyassist_current_session_local_storage_obj();
        if(local_storage_obj && local_storage_obj.hasOwnProperty("new_message_seen")) {
            if(local_storage_obj["new_message_seen"] == "false" && document.getElementById("chat-minimize-icon-wrapper")) {
                $(".chat-talk-bubble").removeClass("bounce2");
                document.getElementById("talktext-p").innerHTML = local_storage_obj["last_message"];
                $(".chat-talk-bubble").css({"display":"block"});
                $(".chat-talk-bubble").addClass("bounce2");
                play_greeting_bubble_popup_sound();
            }
            setTimeout(function(){
                $(".chat-talk-bubble").removeClass("bounce2");
            },1500);
        }
    },2500);

    setTimeout(function() {
        check_edit_access_apply_coview_listener();
    }, 8000);

};

window.addEventListener('resize', function() { 
    if(client_iframe_width && client_iframe_height) {
        resize_iframe_container(client_iframe_width, client_iframe_height);
    }

    if(easyassist_drag_element) {
        easyassist_drag_element.relocate_element();
    }
});

function check_and_start_voip_meeting() {
    var enable_auto_calling = false;
    if(ENABLE_AUTO_CALLING == "True" || ENABLE_AUTO_CALLING == "true" || ENABLE_AUTO_CALLING == true) {
        enable_auto_calling = true;
    }

    if(IS_ADMIN_AGENT == "True") {
        var is_voip_meeting_shown = get_easyassist_cookie("is_voip_meeting_shown");
        if(is_voip_meeting_shown != COBROWSE_SESSION_ID && enable_auto_calling) {
            auto_msg_popup_on_client_call_declined = true;
            set_easyassist_cookie("is_voip_meeting_shown", COBROWSE_SESSION_ID);
            request_for_meeting(COBROWSE_SESSION_ID);
        } else {
            show_cobrowse_meeting_option();
        }
    } else {
        setTimeout(function() {
            check_voip_meeting_active_over_socket(true);
        }, 5000);
    }
}

function send_support_agent_connected_message(agent_name) {

    if(IS_ADMIN_AGENT == "True" || get_easyassist_cookie("support_agent_message") == "true")
        return;
    json_string = JSON.stringify({
        "type": "support_agent_connected",
        "agent_name": agent_name,
        "agent_username": window.AGENT_USERNAME,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
    set_easyassist_cookie("support_agent_message", "true");
}

function send_support_agent_leave_message(agent_name) {

    if(IS_ADMIN_AGENT == "True")
        return;
    json_string = JSON.stringify({
        "type": "support_agent_leave",
        "agent_name": agent_name,
        "agent_username": window.AGENT_USERNAME,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function check_voip_meeting_active_over_socket(show_modal=false) {
    // This function is only used by invited agent, to ask for admin agent over socket if voip meeting is active
    json_string = JSON.stringify({
        "type": "voip_meeting_active",
        "is_invited_agent": true,
        "agent_id": AGENT_UNIQUE_ID,
        "agent_name": window.AGENT_NAME,
        "show_modal": show_modal,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function send_voip_meeting_active_status_over_socket(meeting_status, invited_agent_id, show_modal, is_meeting_initiate_by_customer) {
    json_string = JSON.stringify({
        "type": "voip_meeting_active",
        "is_agent": true,
        "agent_id": invited_agent_id,
        "meeting_status": meeting_status,
        "agent_name": window.AGENT_NAME,
        "is_meeting_initiate_by_customer": is_meeting_initiate_by_customer,
        "show_modal": show_modal,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");

}

function create_and_iframe(html, client_page_id) {

    if(ALLOW_SCREENSHARING_COBROWSE == 'True' || ALLOW_SCREENSHARING_COBROWSE == 'true' || ALLOW_SCREENSHARING_COBROWSE == true) {

        return ;
    }

    // html = EasyAssistLZString.decompress(html);
    var blob = new Blob([html], {
        type: 'text/html'
    });

    var iframe =  initialize_empty_iframe()
    iframe.src = window.URL.createObjectURL(blob);
    iframe.onload = function(event) {
        dataset = {
            window_width: client_iframe_width,
            window_height: client_iframe_height,
            scrollX: 0,
            scrollY: 0,
        };
        renderFrame(dataset, client_page_id);
    };

    is_page_reloaded = false;
    edit_access_update();
}

function create_and_iframe_from_chunk(client_packet, client_page_id) {
    var html = "";
    for (let index = 0; index <= client_packet.chunk; index++) {
        html += chunk_html_dict[client_packet.page][index];
    }

    delete chunk_html_dict[client_packet.page];
    create_and_iframe(html, client_page_id);
}

function easyassist_get_agent_frame_dimension(width, height, aspect_ratio) {
    var low_width = 1.00, high_width = width;
    var ans_width = width, ans_height = height;

    for(let i = 0; i < 1000; i ++) {
        var new_width = (low_width + high_width) / 2;
        var new_height = new_width * aspect_ratio;

        if(new_height <= height) {
            ans_width = new_width;
            ans_height = new_height;
            low_width = new_width;
        } else {
            high_width = new_width;
        }
    }

    return [ans_width, ans_height];
}

function resize_iframe_container(width, height) {

    if(check_screen_sharing_cobrowsing_enabled()) {
        return;
    }

    client_iframe_width = width;
    client_iframe_height = height;

    var frame_container = document.getElementById("frames-container");
    frame_container.children[0].style.width = "100%";
    frame_container.children[0].style.height = "100%";
    frame_container.children[0].style.overflow = "auto";
    agent_screen_width = window.innerWidth;

    var ratio = height / width;
    ratio = ratio.toFixed(4);

    var offset_height = document.getElementById("easyassist-tab-container").offsetHeight;
    var agent_window_height = window.innerHeight - offset_height;

    var agent_dimension =  easyassist_get_agent_frame_dimension(
        Math.min(window.innerWidth, client_iframe_width),
        Math.min(agent_window_height, client_iframe_height),
        ratio);

    var framesContainer_parent_width = agent_dimension[0];
    var framesContainer_parent_height = agent_dimension[1];

    framesContainer.parentElement.style.width = (framesContainer_parent_width).toString() + "px";
    framesContainer.parentElement.style.height = (framesContainer_parent_height).toString() + "px";

    var max_scale_factor = framesContainer_parent_width / client_iframe_width;
    max_scale_factor = Math.min(max_scale_factor, 1);

    framesContainer.style.transform = "scale(" + max_scale_factor + ")";

    framesContainer.style.width = client_iframe_width.toString() + "px";
    framesContainer.style.height = client_iframe_height.toString() + "px";

    var iframe_container_margin_left = Math.max((window.innerWidth - framesContainer_parent_width), 0) / 2;
    var iframe_container_margin_top = Math.max((agent_window_height - framesContainer_parent_height), 0) / 2;
    framesContainer.style.marginLeft = iframe_container_margin_left + "px";
    framesContainer.style.marginTop = iframe_container_margin_top + "px";

    margin_left_client_frame_container = parseInt(iframe_container_margin_left);
    margin_top_client_frame_container = parseInt(iframe_container_margin_top);
    agent_scale_factor = max_scale_factor;
    frame_container_parent_width = framesContainer_parent_width;
    frame_container_parent_height = framesContainer_parent_height;

    easyassist_resize_drawing_canvas();
}

function easyassist_resize_drawing_canvas() {
    try {
        var easyassist_canvas = document.getElementById("easyassist-drawing-canvas");
        easyassist_canvas.width = frame_container_parent_width;
        easyassist_canvas.height = frame_container_parent_height;
        easyassist_canvas.style.marginLeft = margin_left_client_frame_container + "px";
        easyassist_canvas.style.marginTop = margin_top_client_frame_container + "px";
    } catch(err) {
        console.log("easyassist_resize_drawing_canvas: ", err);
    }
}

function easyassist_initialize_canvas() {
    try {
        var easyassist_canvas_element = document.getElementById("easyassist-drawing-canvas");
        if(!easyassist_canvas_element) {
            return;
        }

        var cursor_icon = [
            '<svg width="30" height="30" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="' + FLOATING_BUTTON_BG_COLOR + '">',
                '<path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />',
            '</svg>',
        ].join('');
        var encoded_cursor_icon = "data:image/svg+xml;base64," + btoa(cursor_icon);
        easyassist_canvas_element.style.cursor = "url('" + encoded_cursor_icon + "') 5 25, default";

        if(!easyassist_canvas_element.getAttribute("data-canvas")) {
            window.easyassist_canvas = new EasyAssistCanvas(
                easyassist_canvas_element, FLOATING_BUTTON_BG_COLOR, 7);    
        }
    } catch(err) {
        console.log("easyassist_initialize_canvas: ", err);
    }
}

function easyassist_activate_canvas(element) {
    try {
        if(IS_MOBILE == "False") {
            element.style.backgroundColor = find_light_color(FLOATING_BUTTON_BG_COLOR, 300);
        } else {
            
            if (window.FLOATING_BUTTON_POSITION == "top" || window.FLOATING_BUTTON_POSITION == "bottom") {
                element.parentElement.parentElement.style.backgroundColor = find_light_color(FLOATING_BUTTON_BG_COLOR, 300);
            } else {
                element.parentElement.style.backgroundColor = find_light_color(FLOATING_BUTTON_BG_COLOR, 300);
            }
        
        }
        var easyassist_canvas_element = document.getElementById("easyassist-drawing-canvas");
        easyassist_canvas_element.style.display = "flex";
        easyassist_canvas_element.style.pointerEvents = "";
        
        element.setAttribute("onclick", "easyassist_deactivate_canvas(this);hide_cobrowsing_modals(this)");
        document.getElementById("easyassist-toggle-canvas-label").innerHTML = "Exit Drawing Mode";
        

    } catch(err) {
        console.log("easyassist_activate_canvas: ", err);
    }
}

function easyassist_deactivate_canvas(element) {
    try {
        
        if(IS_MOBILE == "False") {
            element.style.backgroundColor = "";
        } else {
            if (window.FLOATING_BUTTON_POSITION == "top" || window.FLOATING_BUTTON_POSITION == "bottom") {
                element.parentElement.parentElement.style.backgroundColor = "";
            } else {
                element.parentElement.style.backgroundColor = "";
            }
        }
        var easyassist_canvas_element = document.getElementById("easyassist-drawing-canvas");
        easyassist_canvas_element.style.pointerEvents = "none";
        easyassist_canvas_element.style.display = "none";

        element.setAttribute("onclick", "easyassist_activate_canvas(this);hide_cobrowsing_modals(this)");
        document.getElementById("easyassist-toggle-canvas-label").innerHTML = "Enter Drawing Mode";
       
        easyassist_canvas.clear_drawing();

    } catch(err) {
        console.log("easyassist_deactivate_canvas: ", err);
    }
}

class EasyAssistCanvas {
    constructor(canvas_element, color, line_width) {
        this.canvas = canvas_element;
        this.reset_canvas_timer = null;

        this.canvas.setAttribute("data-canvas", "easyassist-canvas");
        this.ctx = this.canvas.getContext("2d");
        this.color = color;
        this.line_width = line_width;

        this.prevX = 0;
        this.currX = 0;
        this.prevY = 0;
        this.currY = 0;

        var _this = this;

        _this.canvas.addEventListener("mousemove", function(e) {
            _this.findxy('move', e);
        });

        _this.canvas.addEventListener("mousedown", function(e) {
            _this.findxy('down', e);
        });

        _this.canvas.addEventListener("mouseup", function(e) {
            _this.findxy('up', e);
        });

        _this.canvas.addEventListener("mouseout", function(e) {
            _this.findxy('out', e);
        });

        _this.canvas.addEventListener("touchmove", function(e) {
            var data = {
                clientX: e.touches[0].clientX,
                clientY: e.touches[0].clientY,
            }
            _this.findxy('move', data);
        });

        _this.canvas.addEventListener("touchstart", function(e) {
            var data = {
                clientX: e.touches[0].clientX,
                clientY: e.touches[0].clientY,
            }
            _this.findxy('down', data);
        });

        _this.canvas.addEventListener("touchend", function(e) {
            _this.findxy('out', e);
        });
    }

    findxy(direction, e) {
        var canvas_offset_top = this.canvas.getBoundingClientRect().top + window.scrollY;

        if (direction == 'down') {
            this.prevX = e.clientX - this.canvas.offsetLeft;
            this.prevY = e.clientY - canvas_offset_top;
            this.currX = e.clientX - this.canvas.offsetLeft;
            this.currY = e.clientY - canvas_offset_top;

            this.is_drawing = true;

            this.draw_dot();
            this.reset_clear_canvas_interval();
        }

        if (direction == 'up' || direction == "out") {
            this.is_drawing = false;
            this.start_clear_canvas_interval();
        }

        if (direction == 'move') {
            if (this.is_drawing) {
                this.prevX = this.currX;
                this.prevY = this.currY;
                this.currX = e.clientX - this.canvas.offsetLeft;
                this.currY = e.clientY - canvas_offset_top;
                this.draw_line();
            }
        }
    }

    draw_dot() {
        this.draw_dot_utils(this.currX, this.currY);

        send_canvas_coordinates_to_socket(
            this.prevX, this.prevY, this.currX, this.currY, this.line_width, 'dot');
    }

    draw_dot_utils(curr_x, curr_y) {
        this.ctx.beginPath();
        this.ctx.fillStyle = this.color;
        this.ctx.arc(curr_x, curr_y, this.line_width / 2, 0, 2 * Math.PI, true);
        this.ctx.fill();
        this.ctx.closePath();
    }

    draw_line() {
        this.draw_line_utils(this.prevX, this.prevY, this.currX, this.currY)

        send_canvas_coordinates_to_socket(
            this.prevX, this.prevY, this.currX, this.currY, this.line_width, 'line');
    }

    draw_line_utils(prev_x, prev_y, curr_x, curr_y) {
        this.ctx.lineCap = "round";
        this.ctx.beginPath();
        this.ctx.moveTo(prev_x, prev_y);
        this.ctx.lineTo(curr_x, curr_y);
        this.ctx.strokeStyle = this.color;
        this.ctx.lineWidth = this.line_width;
        this.ctx.stroke(); 
        this.ctx.closePath();
    }

    start_clear_canvas_interval() {
        var _this = this;

        _this.reset_clear_canvas_interval();

        _this.reset_canvas_timer = setTimeout(function() {
            _this.clear_drawing();
        }, 2000);
    }

    reset_clear_canvas_interval() {
        var _this = this;

        if(_this.reset_canvas_timer != null) {
            clearTimeout(_this.reset_canvas_timer);
            _this.reset_canvas_timer = null;
        }
    }

    clear_drawing() {
        var _this = this;
        _this.ctx.clearRect(0, 0, _this.canvas.width, _this.canvas.height);

        _this.reset_clear_canvas_interval();
        
        send_reset_canvas_over_socket();
    }

    reset_canvas() {
        var _this = this;
        _this.ctx.clearRect(0, 0, _this.canvas.width, _this.canvas.height);
    }
}

function send_canvas_coordinates_to_socket(prev_x, prev_y, curr_x, curr_y, line_width, shape) {
    try {
        json_string = JSON.stringify({
            "type": "sync_canvas",
            "prev_x": (prev_x) * (1 / agent_scale_factor),
            "prev_y": (prev_y) * (1 / agent_scale_factor),
            "curr_x": (curr_x) * (1 / agent_scale_factor),
            "curr_y": (curr_y) * (1 / agent_scale_factor),
            "line_width": line_width,
            "shape": shape,
            "agent_username": window.AGENT_USERNAME,
        });

        encrypted_data = easyassist_custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };

        send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
    } catch(err) {
        console.log("send_canvas_coordinates_to_socket: ", err);
    }
}

function send_reset_canvas_over_socket() {
    try {
        json_string = JSON.stringify({
            "type": "reset_canvas",
            "agent_username": window.AGENT_USERNAME,
        });

        encrypted_data = easyassist_custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };

        send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
    } catch(err) {
        console.log("send_reset_canvas_over_socket: ", err);
    }
}

function easyassist_sync_agent_canvas(data_packet) {
    try {
        var prev_x = data_packet.prev_x * agent_scale_factor;
        var prev_y = data_packet.prev_y * agent_scale_factor;
        var curr_x = data_packet.curr_x * agent_scale_factor;
        var curr_y = data_packet.curr_y * agent_scale_factor;
        var shape = data_packet.shape;

        if(shape == "line") {
            easyassist_canvas.draw_line_utils(prev_x, prev_y, curr_x, curr_y);
        } else {
            easyassist_canvas.draw_dot_utils(curr_x, curr_y);
        }
    } catch(err) {
        console.log("easyassist_sync_agent_canvas: ", err);
    }
}

function easyassist_reset_agent_canvas() {
    try {
        easyassist_canvas.reset_canvas();
    } catch(err) {
        console.log("easyassist_reset_agent_canvas: ", err);
    }
}

function update_edit_access_icon_properties() {
    if (document.getElementById("easyassist-edit-access-icon") != undefined) {
        if (get_easyassist_cookie("request_edit_access") == COBROWSE_SESSION_ID) {
            if(IS_MOBILE == "True") {
                document.getElementById("easyassist-edit-access-icon").setAttribute("data-target", "");
                document.getElementById("easyassist-edit-access-icon").setAttribute("onclick", "remove_onbeforeunload();revoke_easyassist_edit_access();hide_cobrowsing_modals(this)");
                try {
                    document.getElementById("easyassist-edit-access-icon").parentElement.nextElementSibling.innerText = "Revoke Edit Access";
                } catch(err) {}
                if (window.FLOATING_BUTTON_POSITION == "top" || window.FLOATING_BUTTON_POSITION == "bottom") {
                    document.getElementById("easyassist-edit-access-icon").parentElement.parentElement.style.backgroundColor = find_light_color(FLOATING_BUTTON_BG_COLOR, 300);
                } else {
                    document.getElementById("easyassist-edit-access-icon").parentElement.style.backgroundColor = find_light_color(FLOATING_BUTTON_BG_COLOR, 300);
                }
            } else {
                document.getElementById("easyassist-edit-access-icon").setAttribute("data-target", "");
                document.getElementById("easyassist-edit-access-icon").setAttribute("onclick", "remove_onbeforeunload();revoke_easyassist_edit_access();hide_cobrowsing_modals(this)");
                document.getElementById("easyassist-edit-access-icon").children[1].children[1].innerText = "Revoke Edit Access";
                document.getElementById("easyassist-edit-access-icon").style.backgroundColor = find_light_color(FLOATING_BUTTON_BG_COLOR, 300);
            }
        } else {
            if(IS_MOBILE == "True") {
                document.getElementById("easyassist-edit-access-icon").setAttribute("data-target", "#request_for_edit_access_modal");
                document.getElementById("easyassist-edit-access-icon").setAttribute("onclick","remove_onbeforeunload();hide_cobrowsing_modals(this)");
                try {    
                    document.getElementById("easyassist-edit-access-icon").parentElement.nextElementSibling.innerText = "Request for Edit Access";
                } catch(err) {}
                if (window.FLOATING_BUTTON_POSITION == "top" || window.FLOATING_BUTTON_POSITION == "bottom") {
                    document.getElementById("easyassist-edit-access-icon").parentElement.parentElement.style.backgroundColor = "initial";
                } else {
                    document.getElementById("easyassist-edit-access-icon").parentElement.style.backgroundColor = "initial";
                }
            } else {
                document.getElementById("easyassist-edit-access-icon").setAttribute("data-target", "#request_for_edit_access_modal");
                document.getElementById("easyassist-edit-access-icon").setAttribute("onclick","hide_cobrowsing_modals(this);remove_onbeforeunload();");
                document.getElementById("easyassist-edit-access-icon").children[1].children[1].innerText = "Request for Edit Access";
                document.getElementById("easyassist-edit-access-icon").style.backgroundColor = 'initial';
            }
        }
    }
}

function revoke_easyassist_edit_access() {
    json_string = JSON.stringify({
        "type": "revoke-edit-access"
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function edit_access_update() {
    if (get_easyassist_cookie("request_edit_access") == COBROWSE_SESSION_ID && IS_ADMIN_AGENT == "True") {
        action = "initial";
    } else {
        action = "none";
    }

    try {
        frame_child = framesContainer.children[0];
        frame_child.style.pointerEvents = "initial";
        frame_child.style.webkitUserSelect = action;
        frame_child.style.mozUserSelect = action;
        frame_child.style.msUserSelect = action;
        frame_child.style.oUserSelect = action;
        frame_child.style.userSelect = action;
    } catch(err) {
        console.log(err);
    }
}

function easyassist_send_livechat_typing_indication() {
    var name = window.AGENT_NAME;
    json_string = JSON.stringify({
        "role": "agent",
        "name": name,
        "type": "livechat-typing",
        "agent_username": window.AGENT_USERNAME,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function actions_after_connected_successfully(){
    if(connected_successfully == true) return;
    connected_successfully = true;

    if(window.AGENT_JOINED_FIRST_TIME == "true" || window.AGENT_JOINED_FIRST_TIME == true || window.AGENT_JOINED_FIRST_TIME == "True"){
        let local_storage_obj = get_easyassist_current_session_local_storage_obj();
        if(local_storage_obj && !local_storage_obj.hasOwnProperty("agent_joined_chat_bubble_sent")) {
            let message = "Agent " + window.AGENT_NAME + " has joined the chat";
            send_chat_message_from_agent(message, "None", "None", "chat_bubble");
            set_easyassist_current_session_local_storage_obj("agent_joined_chat_bubble_sent", "true");
        }
        if(window.IS_ADMIN_AGENT == "True" && window.ENABLE_AGENT_CONNECT_MESSAGE == "True"){
            setTimeout(function(){
                append_agent_message_into_chatbox(window.AGENT_CONNECT_MESSAGE, "None", "None", "agent_connect_message");
            }, 1500);
        }
        send_support_agent_connected_message(window.AGENT_NAME);
    }
}

function sync_client_web_screen(e) {

    var data = JSON.parse(e.data);
    message = data.message;

    if(!message.body) {
        return;
    }
    
    try{
        client_packet = message.body.Request;
    }catch(err){
        console.trace();
        console.log("Please look at this report this to developer ", message)
    }

    //console.log(message.header.packet, " ---- ", new Date());

    if (message.body.is_encrypted == false) {
        client_packet = JSON.parse(client_packet);
    } else {
        client_packet = easyassist_custom_decrypt(client_packet);
        client_packet = JSON.parse(client_packet);
    }

    var client_page_id = message.header.client_page_id;

    if (message.header.sender == "client") {
        var agent_active_tab_id = null;
        if(CLIENT_TAB_MANAGER_INSTANCE != null) {
            agent_active_tab_id = CLIENT_TAB_MANAGER_INSTANCE.get_agent_active_tab_id();
        }

        var html_packet_types = [
            "html_request_received",
            "html_initialize",
            "html_change",
            "client_screen_resize",
            "div-scroll",
            "element_value",
            "scroll",
            "mouse",
            "html",
            "close_agent_chatbot"
        ];

        reset_internet_connectivity_check_timer();

        if(client_page_id == agent_active_tab_id) {
            if (client_packet.type == "restricted_url") {
                var loading_image = `<img src='/static/EasyAssistApp/img/restricted_page.png' alt="Restricted Page Image" width="220px"></img>`;
                document.getElementById("easyassist-client-page-loader").getElementsByClassName("loading-image")[0].innerHTML = loading_image;
                document.getElementById("easyassist-client-page-loader").getElementsByClassName("loading-lines")[0].style.display = "none";
                document.getElementById("easyassist-client-page-loader").getElementsByClassName("loading-message")[0].innerHTML = "You can not view this as the client is on a restricted page.";
            }
        }

        if(client_page_id && agent_active_tab_id) {
            if(html_packet_types.indexOf(client_packet.type) >= 0) {
                if(client_page_id != agent_active_tab_id) {
                    return;
                }
            }
        }

        if (client_packet.type == "html") {
            if(ALLOW_SCREENSHARING_COBROWSE == 'True' || ALLOW_SCREENSHARING_COBROWSE == 'true' || ALLOW_SCREENSHARING_COBROWSE == true) {

                return ;
            }
            if (client_packet.is_chunk == false) {
                //console.log("html page ", message.body.html_page_counter, new Date());
                client_iframe_width = client_packet.window_width;
                client_iframe_height = client_packet.window_height;
                create_and_iframe(client_packet.html, client_page_id);
                // resize_iframe_container(client_packet.window_width, client_packet.window_height);
                //console.log("iframe created for page: ", message.body.html_page_counter, new Date());
            } else {
                if (client_packet.page in chunk_html_dict) {
                    chunk_html_dict[client_packet.page][client_packet.chunk] = client_packet.html;
                } else {
                    chunk_html_dict[client_packet.page] = {};
                    chunk_html_dict[client_packet.page][client_packet.chunk] = client_packet.html;
                }

                if (client_packet.is_last_chunk) {
                    create_and_iframe_from_chunk(client_packet, client_page_id);
                }
            }
        } else if (client_packet.type == "scroll") {
            if(ALLOW_SCREENSHARING_COBROWSE == 'True' || ALLOW_SCREENSHARING_COBROWSE == 'true' || ALLOW_SCREENSHARING_COBROWSE == true) {

                return ;
            }
            let easyassist_iframe_id = client_packet.easyassist_iframe_id;
            let scrollX = client_packet.data_scroll_x;
            let scrollY = client_packet.data_scroll_y;
            if (framesContainer.children.length > 0) {
                if(easyassist_iframe_id == null) {
                    prev_frame = framesContainer.children[0];
                } else {
                    prev_frame = framesContainer.children[0].contentDocument.querySelector("[easyassist-iframe-id='" + easyassist_iframe_id + "']");
                }
                prev_frame.contentWindow.scrollTo(scrollX, scrollY);
            }

        } else if (client_packet.type == "pageshot") {

            if (client_packet.result == 200) {
                show_easyassist_toast("Screenshot captured successfully");
            } else {
                show_easyassist_toast("Unable to capture the screenshot. Please try again.");
            }

        } else if (client_packet.type == "screenshot") {

            if (client_packet.result == 200) {
                show_easyassist_toast("Screenshot captured successfully");
            } else if (client_packet.result == 405) {
                show_easyassist_toast("Screenshots are not allowed for restricted URLs");
            }else {
                show_easyassist_toast("Unable to capture the screenshot. Please try again.");
            }

        } else if (client_packet.type == "mouse") {

            if(check_screen_sharing_cobrowsing_enabled()) {
                return;
            }

            var factor_y = frame_container_parent_height / client_iframe_height;
            var frame_container_offset_top = $("#frames-container").offset().top;
            var client_pos_y = (frame_container_offset_top + client_packet.position.clientY * factor_y);
            var client_pos_x = (margin_left_client_frame_container + client_packet.position.clientX * agent_scale_factor);
            client_mouse_element.style.top = client_pos_y + "px";
            client_mouse_element.style.left = client_pos_x + "px";
            
        } else if (client_packet.type == "chat") {

            set_client_response(client_packet.message, client_packet.attachment, client_packet.attachment_file_name);

        } else if (client_packet.type == "close_agent_chatbot") {
            close_chatbot_animation();
            easyassist_show_chat_bubble();
        }  else if (client_packet.type == "livechat-typing") {

            set_livechat_typing(client_packet.name, client_packet.role)

        } else if (client_packet.type == "apply_coview_listener") {
            set_easyassist_current_session_local_storage_obj("pdf_modal_easyassist_id", client_packet.element_id);
            easyassist_apply_pdf_coview_pointer_events(client_packet.element_id);
            set_easyassist_cookie("is_pdf_modal_open", "true");

        } else if (client_packet.type == "remove_coview_listener") {
            
            delete_easyassist_cookie("is_pdf_modal_open");
            easyassist_apply_pdf_coview_pointer_events(client_packet.element_id, "none");
            set_easyassist_current_session_local_storage_obj("pdf_modal_easyassist_id", "");
            
        } else if (client_packet.type == "element_value") {
            if(ALLOW_SCREENSHARING_COBROWSE == 'True' || ALLOW_SCREENSHARING_COBROWSE == 'true' || ALLOW_SCREENSHARING_COBROWSE == true) {

                return ;
            }

            if (framesContainer.children.length > 0) {

                frame_child = framesContainer.children[0];

                let easyassist_iframe_id = client_packet.easyassist_iframe_id;

                html_elements_value_list = client_packet.html_elements_value_list;

                for (let html_element_index = 0; html_element_index < html_elements_value_list.length; html_element_index++) {

                    try {
                        html_element = html_elements_value_list[html_element_index];
                        tag_name = html_element.tag_name;
                        tag_type = html_element.tag_type;
                        easyassist_element_id = html_element.easyassist_element_id;
                        value = html_element.value;
                        is_active = html_element.is_active;

                        frame_element = easyassist_get_element_from_easyassist_id(easyassist_element_id, easyassist_iframe_id);

                        if (frame_element == null || frame_element == undefined) {
                            console.log("Element not found");
                            continue;
                        }

                        if (tag_name.toLowerCase() == "select") {

                            if (html_element.is_obfuscated_element) {
                                value = "******";
                                var is_masked_option_exist = false;
                                var option_list = frame_element.options;
                                for (let option_index = 0; option_index < option_list.length; option_index++) {
                                    if(value == option_list[option_index].innerHTML) {
                                        is_masked_option_exist = true;
                                    }
                                }

                                if(!is_masked_option_exist) {
                                    var obfuscated_option = document.createElement("option");
                                    obfuscated_option.value = "******";
                                    obfuscated_option.innerHTML = "******";    
                                    frame_element.appendChild(obfuscated_option);
                                }
                            }

                            var select_value_found = false;
                            for (let option_index = 0; option_index < frame_element.options.length; option_index++) {
                                frame_element.options[option_index].removeAttribute("selected");
                                if (frame_element.options[option_index].innerHTML == value) {
                                    select_value_found = true;
                                    frame_element.options[option_index].setAttribute("selected", "selected");
                                }
                            }

                            if (frame_element.options.length && select_value_found == false) {

                                frame_element.options[0].innerHTML = value;
                            }

                            if (is_active) {
                                frame_element.style.outline = "solid 2px #E83835 !important";
                            } else {
                                frame_element.style.outline = "none";
                            }
                        } else if (tag_name.toLowerCase() == "input") {
                            if (tag_type == "checkbox" || tag_type == "radio") {
                                frame_element.checked = value;
                            } else {
                                frame_element.value = value;
                            }

                            if (is_active) {
                                frame_element.parentElement.style.outline = "solid 2px #E83835 !important";
                            } else {
                                frame_element.parentElement.style.outline = "none";
                            }
                        } else if (tag_name.toLowerCase() == "textarea") {
                            frame_element.value = value;
                            if (is_active) {
                                frame_element.parentElement.style.outline = "solid 2px #E83835 !important";
                            } else {
                                frame_element.parentElement.style.outline = "none";
                            }
                        } else if (tag_name.toLowerCase() == "label") {
                            frame_element.innerHTML = value;
                        } else if (tag_name.toLowerCase() == "span") {
                            frame_element.innerHTML = value;
                        }
                    } catch(err) {
                        console.log(err);
                    }
                }
            }

        } else if (client_packet.type == "request-edit-access") {
            if(ALLOW_SCREENSHARING_COBROWSE == 'True' || ALLOW_SCREENSHARING_COBROWSE == 'true' || ALLOW_SCREENSHARING_COBROWSE == true) {

                return ;
            }

            frame_child = framesContainer.children[0];

            if (client_packet.is_allowed == "none") {
                delete_easyassist_cookie("request_edit_access");
                send_edit_access_revoked_over_socket();
                if("agent_revoke_edit_access" in client_packet) {
                    save_easyassist_system_audit_trail("edit_access", "agent_revoked_edit_access");
                    show_easyassist_toast("Edit Access has been revoked");
                }else {
                    save_easyassist_system_audit_trail("edit_access", "client_revoked_edit_access");
                    show_easyassist_toast("Customer has revoked edit access");
                }
            } else if (requested_for_edit_access == true) {
                requested_for_edit_access = false;

                if (client_packet.is_allowed == "true") {
                    delete_easyassist_cookie("is_pdf_modal_open");
                    set_easyassist_cookie("request_edit_access", COBROWSE_SESSION_ID);
                    send_edit_access_status_over_socket();
                    show_easyassist_toast("Customer has provided edit access to you");
                    save_easyassist_system_audit_trail("edit_access", "client_provided_edit_access");
                } else if (client_packet.is_allowed == "false") {
                    delete_easyassist_cookie("request_edit_access");
                    show_easyassist_toast("Customer has denied edit access to the form.");
                    save_easyassist_system_audit_trail("edit_access", "client_denied_edit_access");
                }
            }

            edit_access_update();
            easyassist_update_edit_access();
            update_edit_access_icon_properties();
            check_edit_access_apply_coview_listener();
        } else if (client_packet.type == "lead_status") {
            var is_converted = client_packet.is_converted;
            if (is_converted == true) {
                set_easyassist_cookie("is_lead_converted", COBROWSE_SESSION_ID);
            } else {
                delete_easyassist_cookie("is_lead_converted");
            }
            check_is_lead_converted();
        } else if(client_packet.type == "end_voip_meeting") {
            if(client_packet.auto_end_meeting) {
                show_easyassist_toast("Call ended");
            } else {
                // if(window.IS_ADMIN_AGENT == "False") {
                //     show_easyassist_toast("Call has ended");    
                // } else {
                //     show_easyassist_toast("Customer ended the call");
                // }
                show_easyassist_toast("Customer ended the call");
            }
            setTimeout(function() {
                if(check_voip_video_meeting_enabled()) {
                    end_cobrowse_video_meet(true);
                }
            }, 1000);
        } else if(client_packet.type == "reset_cookies_audio_call_ended"){
            // reset_voip_meeting();
        }
        else if(client_packet.type == "call_initiate_by_customer"){
            // call_initiate_by_customer = "true";
            set_easyassist_current_session_local_storage_obj("call_initiate_by_customer", "true");
        }
        else if(client_packet.type == "voip_meeting_joined") {
            toggle_voip_ringing_sound(false);
        } else if(client_packet.type == "voip_meeting_ready") {
            if(IS_ADMIN_AGENT == "True") {
                show_easyassist_toast("Customer joined the call");
            }
            set_easyassist_cookie("is_customer_voip_meeting_joined", COBROWSE_SESSION_ID);
        } else if(client_packet.type == "div-scroll") {
            try {
                let easyassist_iframe_id = client_packet.easyassist_iframe_id;
                value_top = client_packet.value_top;
                value_left = client_packet.value_left;
                element_id = client_packet.element_id;
                element_attr_id = client_packet.id;
                element = null;

                element = easyassist_get_element_from_easyassist_id(element_id, easyassist_iframe_id);

                if (element == null || element == undefined) {
                    console.log("Element not found");
                }else{
                    element.scrollTop = value_top;
                    element.scrollLeft = value_left;
                }
            } catch(err) {}
        } else if( client_packet.type == "client_weak_connection" ){
            if(get_easyassist_cookie("easyassist_session_id")){
                if(get_easyassist_cookie("easyassist_client_weak_internet_connection_shown") == undefined || get_easyassist_cookie("easyassist_client_weak_internet_connection_shown") == "false"){
                    show_client_weak_internet_connectio_modal();
                    set_easyassist_cookie("easyassist_client_weak_internet_connection_shown", "true")
                }
            }
        } else if(client_packet.type == "html_request_received") {

            is_html_request_received_to_client = true;

        } else if(client_packet.type == "html_initialize") {

            if(client_packet.easyassist_iframe_id == null) {
                initialize_easyassist_iframe(client_packet.props, client_page_id);
                easyassist_tree_mirror[client_packet.f].apply(easyassist_tree_mirror, client_packet.args);
            } else {
                initialize_easyassist_sub_iframe(client_packet.easyassist_iframe_id, client_packet.props, client_page_id);
                easyassist_iframe_tree_mirror[client_packet.easyassist_iframe_id][client_packet.f].apply(easyassist_iframe_tree_mirror[client_packet.easyassist_iframe_id], client_packet.args);
            }

        } else if(client_packet.type == "html_change") {

            if(client_packet.easyassist_iframe_id == null) {
                easyassist_update_styled_component_css(client_packet.props.css_text);

                easyassist_tree_mirror[client_packet.f].apply(easyassist_tree_mirror, client_packet.args);
            } else {
                easyassist_iframe_tree_mirror[client_packet.easyassist_iframe_id][client_packet.f].apply(easyassist_iframe_tree_mirror[client_packet.easyassist_iframe_id], client_packet.args);
            }

        } else if(client_packet.type == "client_screen_resize") {

            resize_iframe_container(client_packet.window_width, client_packet.window_height);

        } else if(client_packet.type == "heartbeat") {

            actions_after_connected_successfully();

        } else if(client_packet.type == "client_page_details") {

            CLIENT_TAB_MANAGER_INSTANCE.check_and_create_new_client_page_tab(client_packet);
            easyassist_hide_cobrowsing_loader();
        } else if(client_packet.type == "client_tab_focus") {
         
            CLIENT_TAB_MANAGER_INSTANCE.client_focus_element_action(client_page_id, true);
        
            easyassist_clear_show_focus_toast_timeout();
        } else if(client_packet.type == "client_tab_not_focus") {
            
            if(client_packet.action == "navigation") {
                easyassist_show_long_toast("You cannot perform this action as the customer is focused on a different tab.<br>\
                    Please request the customer to navigate back to the co-browsing tab and try again.")
            } else {
                easyassist_show_long_toast("Document preview is currently disabled as the customer is focused on a different tab.<br>\
                    Please request the customer to navigate back to the co-browsing tab and try again.")
            }
        
        } else if(client_packet.type == "client_tab_blur") {

            CLIENT_TAB_MANAGER_INSTANCE.client_focus_element_action(client_page_id, false);

            easyassist_start_show_focus_toast_timeout();

        } else if(client_packet.type == "client_tab_close") {

            CLIENT_TAB_MANAGER_INSTANCE.client_tab_close_action(client_page_id);

        } else if(client_packet.type == "customer_request_meeting_modal_invited_agent") {
            if(IS_ADMIN_AGENT == "False"){
                set_easyassist_current_session_local_storage_obj("is_call_ongoing_invited_agent", "true");
                reset_customer_init_call_modal_text();
                show_side_nav_call_icon_for_customer_init_call();
                if(!is_meeting_tab_open()) {
                    document.getElementById("customer_request_meeting_modal_invited_agent").style.display = "block";                     
                }
            }
        }
    } else {
        if(message.header.sender == "agent" ) {
            if (client_packet.type == "chat"){
                if(window.AGENT_USERNAME != client_packet.sender){
                    set_agent_response(client_packet.message, client_packet.attachment, client_packet.attachment_file_name, client_packet.chat_type, client_packet.agent_name,client_packet.agent_profile_pic_source);
                }
            } else if (client_packet.type == "sync-form") {
                if(window.AGENT_USERNAME == client_packet.agent_username)
                    return;

                tag_name = client_packet.tag_name;
                tag_type = client_packet.tag_type;
                element_id = client_packet.easyassist_element_id;
                value = client_packet.value;
                // query_selector = tag_name + "[easyassist-element-id='" + element_id + "']";
                // client_iframe = document.getElementsByClassName("client-data-frame")[0].contentWindow.document;
                // change_element = client_iframe.querySelector(query_selector);

                change_element = easyassist_get_element_from_easyassist_id(element_id);
                if(change_element == null || change_element == undefined) {
                    return;
                }
    
                if (tag_name == "select") {
    
                    if (change_element.options == undefined || change_element.options == null) {
                        return;
                    }
    
                    for (let option_index = 0; option_index < change_element.options.length; option_index++) {
                        change_element.options[option_index].removeAttribute("selected");
                        if (change_element.options[option_index].innerHTML == value) {
                            change_element.options[option_index].setAttribute("selected", "selected");
                        }
                    }
    
                } else if (tag_name == "input") {
    
                    if (tag_type == "checkbox") {
                        change_element.checked = value;
                    } else if (tag_type == "radio") {
                        change_element.checked = value;
                    } else {
                        change_element.value = value;
                    }
    
                } else {
    
                    change_element.innerHTML = value;
                }
            } else if(client_packet.type == "check_meeting_initiate_by_customer"){
                if(client_packet.is_invited_agent) {
                if(IS_ADMIN_AGENT == "True") {
                    if(get_easyassist_cookie("is_meeting_initiate_by_customer") == "true"){
                        var meeting_initiate_by_customer = "true";
                        send_meeting_initiate_by_customer_status_over_socket(meeting_initiate_by_customer)
                    }

                }
            }
            else if(client_packet.is_agent) {
                if(IS_ADMIN_AGENT == "False") {
                    if(client_packet.status == "true"){
                    set_easyassist_cookie("meeting_initiate_by_customer_status", "true");
                    }
                }
            }
        } 
            else if(client_packet.type == "voip_meeting_active") {
                voip_meeting_initiated_agent = client_packet.agent_name;
                if(client_packet.is_invited_agent) {
                    if(IS_ADMIN_AGENT == "True") {
                        let is_cobrowse_meeting_active = get_easyassist_cookie("is_cobrowse_meeting_active");
                        var voip_meeting_active_status = false;
                        if(is_cobrowse_meeting_active == COBROWSE_SESSION_ID) {
                            voip_meeting_active_status = true;
                        }
                        if(get_easyassist_cookie("is_meeting_initiate_by_customer") == "true"){
                            var is_meeting_initiate_by_customer = "true";
                        }
                        else{
                            var is_meeting_initiate_by_customer = "false";
                        }
                        send_voip_meeting_active_status_over_socket(voip_meeting_active_status, client_packet.agent_id, client_packet.show_modal, is_meeting_initiate_by_customer);
                    }
                } else if(client_packet.is_agent) {
                    if(IS_ADMIN_AGENT == "False" && AGENT_UNIQUE_ID == client_packet.agent_id) {
                        if(client_packet.meeting_status == true) {
                            if(client_packet.is_meeting_initiate_by_customer == "true"){
                                set_easyassist_current_session_local_storage_obj("is_call_ongoing_invited_agent", "true");
                                if(client_packet.show_modal) {
                                    show_invited_agent_customer_voip_connect_modal();
                                }
                                show_side_nav_call_icon_for_customer_init_call();
                            } else {
                                set_easyassist_current_session_local_storage_obj("is_call_ongoing_invited_agent", "true");
                                    
                                if(client_packet.show_modal) {
                                    show_invited_agent_voip_connect_modal();
                                }
                                show_side_nav_call_icon();
                            }
                        } else {
                            hide_side_nav_call_icon();
                            set_easyassist_current_session_local_storage_obj("is_call_ongoing_invited_agent", "false");
                        }
                    }
                }
            } else if(client_packet.type == "voip_meeting_ready") {
                if(AGENT_UNIQUE_ID != client_packet.agent_id) {
                    voip_meeting_initiated_agent = client_packet.agent_name;
                    if(IS_ADMIN_AGENT == "True") {
                        show_easyassist_toast("Agent " + client_packet.agent_name + " joined the call");
                    } else {
                        let is_cobrowse_meeting_active = get_easyassist_cookie("is_cobrowse_meeting_active");
                        if(is_cobrowse_meeting_active != COBROWSE_SESSION_ID) {
                            // TODO possible cause of double modal issue
                            show_invited_agent_voip_connect_modal();
                        }
                    }
                }
            } else if(client_packet.type == "div-scroll") {
                if(IS_ADMIN_AGENT == "False") {
                    try {
                        let easyassist_iframe_id = client_packet.easyassist_iframe_id
                        value_top = client_packet.value_top;
                        value_left = client_packet.value_left;
                        element_id = client_packet.element_id;
                        element_attr_id = client_packet.id;
                        element = null;
                        if (element_attr_id != null && element_attr_id != undefined) {
                            element = framesContainer.children[0].contentDocument.getElementById(element_attr_id);
                        }

                        if(!element){
                            // element = framesContainer.children[0].contentDocument.querySelector("[easyassist-element-id='" + element_id + "']")
                            element = easyassist_get_element_from_easyassist_id(element_id, easyassist_iframe_id);
                        }
                        element.scrollTop = value_top;
                        element.scrollLeft = value_left;
                    } catch(err) {}
                }
            }  else if(client_packet.type == "sync-scroll"){
                if(IS_ADMIN_AGENT == "False") {
                    if(ALLOW_SCREENSHARING_COBROWSE == 'True' || ALLOW_SCREENSHARING_COBROWSE == 'true' || ALLOW_SCREENSHARING_COBROWSE == true) {
                        return ;
                    }

                    let scrollX = client_packet.data_scroll_x;
                    let scrollY = client_packet.data_scroll_y;
                    if (framesContainer.children.length > 0) {
                        prev_frame = framesContainer.children[0];
                        prev_frame.contentWindow.scrollTo(scrollX, scrollY);
                    }
                }
            } else if (client_packet.type == "transferred_agent_connected") {
                if(window.AGENT_USERNAME != client_packet.agent_username) {
                    show_easyassist_toast("Agent " + client_packet.agent_name + " has joined the session.");
                }
            } else if (client_packet.type == "transferred_agent_request") {
                if(window.AGENT_USERNAME != client_packet.agent_username) {
                    set_easyassist_current_session_local_storage_obj("invite_button_id_to_hide", client_packet.agent_id);
                }
            } else if (client_packet.type == "transferred_agent_response") {
                if(window.AGENT_USERNAME != client_packet.agent_username) {
                    set_easyassist_current_session_local_storage_obj("invite_button_id_to_hide", "");
                }
            } else if (client_packet.type == "support_agent_connected") {
                if(window.AGENT_USERNAME != client_packet.agent_username)
                    show_easyassist_toast("Agent " + client_packet.agent_name + " has joined the session.");
            } else if (client_packet.type == "support_agent_leave") {
                if(window.AGENT_USERNAME != client_packet.agent_username)
                    show_easyassist_toast("Agent " + client_packet.agent_name + " has left the session.");
            } else if (client_packet.type == "livechat-typing") {
                if(window.AGENT_USERNAME != client_packet.agent_username)
                    set_livechat_typing(client_packet.name, client_packet.role)

            } else if(client_packet.type == "sync_canvas") {
                
                if(client_packet.agent_username != window.AGENT_USERNAME) {
                    easyassist_sync_agent_canvas(client_packet);
                }

            } else if(client_packet.type == "reset_canvas") {

                if(client_packet.agent_username != window.AGENT_USERNAME) {
                    easyassist_reset_agent_canvas();
                }

            } else if (client_packet.type == "invited_agent_call_request") {
                if(IS_ADMIN_AGENT == "False") {
                    reset_call_modal_text();
                    set_easyassist_current_session_local_storage_obj("is_call_ongoing_invited_agent", "true");
                    show_side_nav_call_icon();
                    if(client_packet.is_call_ongoing) {
                        show_invited_agent_voip_connect_modal();
                    } else {
                        $("#request_meeting_modal_invited_agent").modal("show");
                    }
                }
            } else if(client_packet.type == "customer_request_meeting_modal_invited_agent") {
                if(IS_ADMIN_AGENT == "False"){
                    set_easyassist_current_session_local_storage_obj("is_call_ongoing_invited_agent", "true");
                    reset_customer_init_call_modal_text();
                    show_side_nav_call_icon_for_customer_init_call();
                    document.getElementById("customer_request_meeting_modal_invited_agent").style.display = "block";                     
                }
            } else if(client_packet.type == "join_customer_voice_call_meeting_btn_hide"){
                if(IS_ADMIN_AGENT == "False"){
                    if(check_voip_enabled()){
                        if(IS_MOBILE == "True") {
                            document.getElementById("join-customer-voice-call-meeting-btn").parentNode.parentNode.style.display = "none";
                        } else {
                            document.getElementById("join-customer-voice-call-meeting-btn").style.display = "none";
                        }
                    } else {
                        if(IS_MOBILE == "True") {
                            document.getElementById("join-customer-cobrowsing-video-call-meeting-btn").parentNode.parentNode.style.display = "none";
                        } else {
                            document.getElementById("join-customer-cobrowsing-video-call-meeting-btn").style.display = "none";
                        }
                    }             
                }
            } else if(client_packet.type == "invited_agent_disconnected") {
                
                var message = "";

                if(IS_ADMIN_AGENT == "True") {
                    message = client_packet.invited_agent_name + " left the ongoing call.";
                } else {
                    try {
                        if (window.INVITED_AGENT_USERNAME != "" && window.INVITED_AGENT_USERNAME == client_packet.agent_username) {
                            message = "You left the ongoing call."
                        } else {
                            message = client_packet.invited_agent_name + " left the ongoing call.";
                        }
                    } catch (error) {
                        message = client_packet.invited_agent_name + " left the ongoing call.";
                    }                
                }
                show_easyassist_toast(message);
                
            }
        }

        return;

        if (client_packet.init_transaction == true) {
            document.getElementById("frames-container").style.display = "none";
            document.getElementById("transaction-payment-loader").style.display = "block";
            return;
        }

        document.getElementById("frames-container").style.display = "block";
        document.getElementById("transaction-payment-loader").style.display = "none";

        if (client_packet.is_client_connected == false) {
            show_easyassist_toast("Looks like we are not receiving any updates from customer side. Kindly check your internet connectivity or check whether customer is still connected or not.");
        }
    }
}

function agent_heartbeat() {
    json_string = JSON.stringify({
        "type": "heartbeat"
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function highlightElement(event, frame_window) {

    if(easyassist_check_weak_connection_enabled()) {
        return;
    }

    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID,
        "type": "highlight",
        "position": {
            "clientX": event.clientX,
            "clientY": event.clientY,
            "agent_window_width": frame_window.innerWidth,
            "agent_window_height": frame_window.innerHeight,
            "screen_width": screen.width,
            "screen_height": screen.height,
            "agent_window_x_offset": frame_window.pageXOffset,
            "agent_window_y_offset": frame_window.pageYOffset,
            "pageX": event.pageX,
            "pageY": event.pageY
        }
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");
}

function is_edit_access() {
    if(get_easyassist_cookie("request_edit_access") == COBROWSE_SESSION_ID && IS_ADMIN_AGENT == "True")
        return true;
    return false;
}

function is_valid_edit_element(element) {
    event_tag_name = element.tagName.toLowerCase();
    event_tag_type = element.getAttribute("type");
    var is_valid = false;
    if (event_tag_name == "input") {
        if (event_tag_type != "submit") {
            is_valid = true;
        }
    } else if (event_tag_name == "textarea") {
        is_valid = true;
    } else if (event_tag_name == "select") {
        is_valid = true;
    } else if(event_tag_name == "label") {
        is_valid = true;
    } else {
        is_valid = false;
    }
    return is_valid;
}

function sync_scroll_position(frame){

    if (get_easyassist_cookie("request_edit_access") != COBROWSE_SESSION_ID) {
        return ;
    }

    if(easyassist_check_weak_connection_enabled()) {
        return;
    }

    var iframe_id = frame.getAttribute("easyassist-iframe-id");

    json_string = JSON.stringify({
      "type": "sync-scroll",
      "active_url": window.location.href,
      "data_scroll_x": frame.contentWindow.scrollX,
      "data_scroll_y": frame.contentWindow.scrollY,
      "iframe_id": iframe_id,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
      "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");
}

function easyassist_iframe_add_event_listeners(iframe) {
    try {

        iframe.contentDocument.addEventListener('contextmenu', event => event.preventDefault());

        iframe.contentDocument.onkeydown = function(e) {
            e = e || window.event; //Get event
            edit_access_update();
            if (get_easyassist_cookie("request_edit_access") != COBROWSE_SESSION_ID) {
                e.preventDefault();
                e.stopPropagation();
            } else {
                if (is_valid_edit_element(e.target) == false) {
                    e.preventDefault();
                    e.stopPropagation();
                }
            }
        };

        iframe.contentWindow.document.onclick = function(event) {
            event_tag_name = event.target.tagName.toLowerCase();
            edit_access_update();
            if (get_easyassist_cookie("request_edit_access") != COBROWSE_SESSION_ID) {
                event.preventDefault();
                highlightElement(event, iframe.contentWindow);
            } else {
                if (is_valid_edit_element(event.target) == false) {
                    event.preventDefault();
                    highlightElement(event, iframe.contentWindow);
                }
            }
        }

        iframe.contentWindow.document.onmousemove = function(event) {
            sync_mouse_position(event);
        }

        iframe.contentWindow.document.onscroll = function(event) {
            sync_scroll_position(iframe);
        }

        try {
            if(is_edit_access()) {
                add_easyassist_event_listner_into_element(iframe.contentDocument.body, "mousedown", easyassist_update_global_event_target);
                add_easyassist_event_listner_into_element(iframe.contentDocument.body, "click", button_click_client_element);
            }
        } catch {
            console.log("Iframe body does not exist")
        }

        easyassist_update_edit_access(iframe);
    } catch(err) {
        console.log("easyassist_iframe_add_event_listeners:", err);
    }
}

function renderFrame(dataset, requested_client_page_id) {

    setTimeout(function() {

        var agent_active_tab_id = CLIENT_TAB_MANAGER_INSTANCE.get_agent_active_tab_id();
        if(agent_active_tab_id != requested_client_page_id) {
            return;
        }

        var frame = document.getElementById("easyassist-iframe-" + EASYASSIST_IFRAME_ID_GLOBAL);
        if (!frame) {
            return;
        }

        for(let idx = 0; idx < EASYASSIST_IFRAME_ID_GLOBAL; idx ++) {
            try {
                if(document.getElementById("easyassist-iframe-" + idx)) {
                    document.getElementById("easyassist-iframe-" + idx).remove();
                }
            } catch(err) {}
        }

        resize_iframe_container(dataset.window_width, dataset.window_height);

        frame.hidden = false;
        hide_easyassist_client_page_loader();

        var scrollX = parseInt(dataset.scrollX);
        var scrollY = parseInt(dataset.scrollY);
        frame.contentWindow.scrollTo(scrollX, scrollY);

        $("#allincall-chat-box")[0].contentWindow.document.onmousemove = function(event) {
            sync_mouse_position(event, is_from_chat_window = true);
        }

        easyassist_send_iframe_html_request();

    }, 500);
}

function easyassist_apply_pdf_coview_pointer_events(element_id, pointer_event="") {
    
    if(is_edit_access())
        return;

    let iframe = document.getElementById("frames-container").children[0];
    iframe.style.pointerEvents = pointer_event;
    
    let child_iframes = iframe.contentDocument.querySelectorAll("iframe");
    child_iframes.forEach(function(child_iframe) {
        child_iframe.style.pointerEvents = pointer_event;
    });

    let element = easyassist_get_element_from_easyassist_id(element_id);
    easyassist_update_pointer_event(element, pointer_event);
}

function easyassist_update_pointer_event(dom_node, pointer_event="") {
    try {
        dom_node.style.pointerEvents = pointer_event;
        
        if(dom_node.classList.contains("page-count") || dom_node.classList.contains("page-move") || dom_node.classList.contains("modal-body") || dom_node.classList.contains("page-move-mobile")) {
            dom_node.style.pointerEvents = "none";
        }
        
        if(dom_node.id == "easyassist-pdf-coview-cross-button" && pointer_event != "none") {
            add_easyassist_event_listner_into_element(dom_node, "click", button_click_client_element);
        }

        if(dom_node.id == "easyassist-pdf-coview-cross-button" && pointer_event == "none") {
            remove_easyassist_event_listner_into_element(dom_node, "click", button_click_client_element);
        }

        let children_node = dom_node.children;
        for(let idx = 0; idx < children_node.length; idx ++) {    
            easyassist_update_pointer_event(children_node[idx], pointer_event);
        }

    } catch(err) {
        console.log("easyassist_update_pointer_event: ", err);
    }
}

function easyassist_update_edit_access(iframe=null) {
    
    if(get_easyassist_cookie("is_pdf_modal_open") == "true")
        return;

    function update_edit_access(frame) {
        var html_element = frame.contentDocument.children[0];

        if(is_edit_access()) {
            easyassist_apply_edit_access(html_element);
        } else {
            easyassist_reset_edit_access(html_element);
        }
    }

    if(iframe == null) {
        iframe = document.getElementById("frames-container").children[0];
        update_edit_access(iframe);

        var child_iframes = iframe.contentDocument.querySelectorAll("iframe");
        child_iframes.forEach(function(child_iframe) {
            update_edit_access(child_iframe); 
        });
    } else {
        update_edit_access(iframe);
    }    
}

function easyassist_apply_edit_access(dom_node) {

    try {
        if(dom_node.hasAttribute("easyassist-obfuscate")) {
            dom_node.style.pointerEvents = "none";
            return;
        }
        dom_node.style.pointerEvents = "";

        var tag_name = dom_node.tagName.toLowerCase();
        if(tag_name == "input") {
            add_easyassist_event_listner_into_element(dom_node, "keyup", detect_agent_value_change);
            // add_easyassist_event_listner_into_element(dom_node, "change", detect_agent_value_change);

        } else if(tag_name == "select") {
            add_easyassist_event_listner_into_element(dom_node, "change", detect_agent_value_change);

        } else if(tag_name == "marquee") {
            dom_node.start();

        } else if(tag_name == "textarea") {
            add_easyassist_event_listner_into_element(dom_node, "keyup", detect_agent_value_change);
            add_easyassist_event_listner_into_element(dom_node, "change", detect_agent_value_change);

        } else if(tag_name == "div") {
            var scroll_left = dom_node.getAttribute("easyassist-data-scroll-x");
            var scroll_top = dom_node.getAttribute("easyassist-data-scroll-y");
            dom_node.scrollLeft = scroll_left;
            dom_node.scrollTop = scroll_top;

        } else if(tag_name == "body") {
            add_easyassist_event_listner_into_element(dom_node, "mousedown", easyassist_update_global_event_target);
            add_easyassist_event_listner_into_element(dom_node, "click", button_click_client_element);

        }

        add_easyassist_event_listner_into_element(dom_node, "scroll", sync_scroll_position_inside_div);

        var node_children = dom_node.children;
        for(let idx = 0; idx < node_children.length; idx ++) {
            easyassist_apply_edit_access(node_children[idx]);
        }
    } catch(err) {
        console.log("easyassist_apply_edit_access: ", err);
    }
}

function easyassist_reset_edit_access(dom_node) {

    try {

        if(dom_node.tagName != "HTML"){
            dom_node.style.pointerEvents = "none";
        }

        var tag_name = dom_node.tagName.toLowerCase();
        if(tag_name == "input") {
            remove_easyassist_event_listner_into_element(dom_node, "keyup", detect_agent_value_change);
            remove_easyassist_event_listner_into_element(dom_node, "change", detect_agent_value_change);

        } else if(tag_name == "select") {
            remove_easyassist_event_listner_into_element(dom_node, "change", detect_agent_value_change);

        } else if(tag_name == "marquee") {
            dom_node.start();

        } else if(tag_name == "textarea") {
            remove_easyassist_event_listner_into_element(dom_node, "change", detect_agent_value_change);
            remove_easyassist_event_listner_into_element(dom_node, "keyup", detect_agent_value_change);

        } else if(tag_name == "div") {
            var scroll_left = dom_node.getAttribute("easyassist-data-scroll-x");
            var scroll_top = dom_node.getAttribute("easyassist-data-scroll-y");
            dom_node.scrollLeft = scroll_left;
            dom_node.scrollTop = scroll_top;

        } else if(tag_name == "body") {
            remove_easyassist_event_listner_into_element(dom_node, "mousedown", easyassist_update_global_event_target);
            remove_easyassist_event_listner_into_element(dom_node, "click", button_click_client_element);
        }

        remove_easyassist_event_listner_into_element(dom_node, "scroll", sync_scroll_position_inside_div);

        var node_children = dom_node.children;
        for(let idx = 0; idx < node_children.length; idx ++) {
            easyassist_reset_edit_access(node_children[idx]);
        }
    } catch(err) {
        console.log("easyassist_reset_edit_access: ", err);
    }
}

function add_easyassist_event_listner_into_element(html_element, event_type, target_function){
    html_element.removeEventListener(event_type, target_function);
    html_element.addEventListener(event_type, target_function);
}

function remove_easyassist_event_listner_into_element(html_element, event_type, target_function){
    html_element.removeEventListener(event_type, target_function);
}

function easyassist_get_iframe_id(event) {
    try {
        if(!event.view || !event.view.frameElement) {
            return null;
        }

        var iframe = event.view.frameElement;
        var iframe_id = null;

        if(iframe) {
            iframe_id = iframe.getAttribute("easyassist-iframe-id");
        }

        return iframe_id;
    } catch(err) {
        console.log("easyassist_get_iframe_id: ", err);
    }
    return null;
}

function button_click_client_element(event) {

    var iframe_id = easyassist_get_iframe_id(event);

    var is_mobile_firefox = false;
    if(navigator.userAgent && navigator.userAgent.indexOf("Firefox") > -1) {
        if(IS_MOBILE == "True") {
            is_mobile_firefox = true;
        }
    }

    var currentBtn = event.target;

    if(is_mobile_firefox && global_event_target_element != null) {
        currentBtn = global_event_target_element;
    }
    if(currentBtn.tagName == "INPUT" && ["checkbox", "radio"].indexOf(currentBtn.getAttribute("type")) >=0){
        // event.preventDefault();
    } else {
        event.preventDefault();
    }

    easyassist_element_id = easyassist_get_easyassist_id_from_element(currentBtn);

    if (easyassist_element_id == null || easyassist_element_id == undefined) {
        console.log("Danger: element id not found");
        easyassist_element_id = "";
    }

    json_string = JSON.stringify({
        "type": "button-click",
        "element_id": "",
        "easyassist_element_id": easyassist_element_id,
        "iframe_id": iframe_id,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");
}

function easyassist_update_global_event_target(event) {
    try {
        if(event.type == "mousedown") {
            global_event_target_element = event.target;
        }
    } catch(err) {
        console.log("easyassist_update_global_event_target: ", err);
    }
}

function sync_scroll_position_inside_div(event) {
    try {
        if (get_easyassist_cookie("request_edit_access") != COBROWSE_SESSION_ID) {
            return ;
        }

        var iframe_id = easyassist_get_iframe_id(event);

        var element_id = easyassist_get_easyassist_id_from_element(event.target);
        if(element_id == null) {
            console.log("Danger Scroll: Element id not found")
            return;
        }

        json_string = JSON.stringify({
            "type": "div-scroll",
            "value_top": event.target.scrollTop,
            "value_left": event.target.scrollLeft,
            "element_id": element_id,
            "element_id_attr": event.target.id,
            "iframe_id": iframe_id,
        });

        encrypted_data = easyassist_custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };

        send_message_over_easyassist_socket(encrypted_data, "agent");
    } catch(err) {}
}

function playback(interval) {
    clearInterval(playbackIntervalId);

    if (!framesContainer.children.length) {
        return;
    }

    var i = 0;
    playbackIntervalId = setInterval(function() {
        var iframe = framesContainer.children[i];
        if (i > 0) {
            framesContainer.children[i - 1].hidden = true;
        } else if (i == 0) {
            framesContainer.children[framesContainer.children.length - 1].hidden = true;
        }
        iframe.hidden = false;

        i++;
        i %= framesContainer.children.length;
    }, interval);
}

function take_client_screenshot(type) {

    json_string = JSON.stringify({
        "type": type,
        "agent_name": window.AGENT_NAME
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");

    return;

    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID,
        "screenshot_type": type
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/take-client-screenshot/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            //console.log(response);
        }
    }
    xhttp.send(params);
}

function remarks_validation(remarks, close_session_text_error_el, remarks_type, min_length, max_length){
    if(min_length > 0){
        if(!remarks){
            close_session_text_error_el.innerHTML = remarks_type + " cannot be empty."
            close_session_text_error_el.style.display = 'block';
            return "invalid";
        }
    }
    if(remarks.length > max_length) {
        close_session_text_error_el.innerHTML = remarks_type + " cannot be more than 200 characters."
        close_session_text_error_el.style.display = 'block';
        return "invalid";
    }
    return "valid";
}

function close_agent_confirm_session(element) {

    close_session_remark_error_el = document.getElementById("close-session-remarks-error");
    close_session_text_error_el = document.getElementById("close-session-text-error");

    close_session_text_error_el.style.display = "none";
    if(close_session_remark_error_el) {
        close_session_remark_error_el.style.display = "none";
    }

    is_helpful = document.getElementById("mask-successfull-cobrowsing-session").checked;
    is_test = document.getElementById("mask-test-cobrowsing-session").checked;

    comment_desc = "";
    comments = "";
    subcomments = "";

    if(ENABLE_PREDEFINED_REMARKS == "True") {
        comments = document.getElementById("close-session-remarks").value;
        comment_desc = document.getElementById("close-session-remarks-text").value.trim();

        if(ENABLE_PREDEFINED_SUBREMARKS == "True") {
            subcomments = document.getElementById("close-session-subremarks").value;
        }

        if(PREDEFINED_REMARKS_OPTIONAL == "False") {
            if (comments.length == 0) {
                close_session_remark_error_el.innerHTML = "Please select a remark";
                close_session_remark_error_el.style.display = 'block';
                return;
            }

            if(remarks_validation(comments, close_session_text_error_el, "Remarks", 1, 200) == "invalid") {
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

        if(comments == "others"){

            if(!comment_desc.length) {
                close_session_text_error_el.innerHTML = "Comments cannot be empty";
                close_session_text_error_el.style.display = 'block';
                return;
            }
    
            if(!is_input_text_valid(comment_desc)) {
                close_session_text_error_el.innerHTML = "Please enter a valid comment (Only a-z A-z 0-9 .,@ are allowed)";
                close_session_text_error_el.style.display = 'block';
                return;
            }

            if(is_test == false  && remarks_validation(comment_desc, close_session_text_error_el, "Comments", 1, 200) == "invalid"){
                return;
            }
        } else {
            if(comment_desc && !is_input_text_valid(comment_desc)) {
                close_session_text_error_el.innerHTML = "Please enter a valid comment (Only a-z A-z 0-9 .,@ are allowed)";
                close_session_text_error_el.style.display = 'block';
                return;
            }

            if(is_test == false && remarks_validation(comment_desc, close_session_text_error_el, "Comments", 0, 200) == "invalid"){
                return;
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

        if(remarks_validation(comments, close_session_text_error_el, "Remarks", 1, 200) == "invalid") {
            return;
        }
    }

    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID,
        "is_helpful": is_helpful,
        "is_test": is_test,
        "comments": comments,
        "subcomments": subcomments,
        "comment_desc": comment_desc
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Closing...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/close-session/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                delete_easyassist_cookie("easyassist_client_disconnected_modal_shown");
                delete_easyassist_cookie("easyassist_client_weak_internet_connection_shown");
                clearInterval(easyassist_send_agent_weak_connection_message_interval);

                json_string = JSON.stringify({
                    "type": "end_session",
                });

                encrypted_data = easyassist_custom_encrypt(json_string)
                encrypted_data = {
                    "Request": encrypted_data
                };


                end_cobrowse_video_meet();
                send_message_over_easyassist_socket(encrypted_data, "client");
                send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
                if(response.is_cobrowsing_from_livechat) {
                    window.location = "/livechat/cobrowsing-end/";
                } else {
                    window.location = "/easy-assist/sales-ai/dashboard/";
                }
            } else {
                element.innerHTML = "End Session";
            }
        } else {
            element.innerHTML = "End Session";
        }
    }
    xhttp.send(params);
}

function close_agent_leave_session(element) {

    let json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID,
        "is_leaving": true
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Leaving...";
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
                send_chat_message_from_agent("Agent " + window.AGENT_NAME + " has left the chat", "None", "None", "chat_bubble");
                send_support_agent_leave_message(window.AGENT_NAME);
                delete_easyassist_cookie("support_agent_message");
                easyassist_delete_session_cookie();
                
                if(response.is_cobrowsing_from_livechat) {
                    window.location = "/livechat/cobrowsing-end/";
                } else {
                    window.location = "/easy-assist/sales-ai/dashboard/";
                }
            } else {
                element.innerHTML = "Leave";
            }
        } else {
            element.innerHTML = "Leave";
        }
    }
    xhttp.send(params);
}

function capture_client_screenshot_confirm() {
    take_client_screenshot("screenshot");
}

function capture_client_pageshot_confirm() {
    take_client_screenshot("pageshot");
}


function fetch_cobrowsing_meta_information() {

    var captured_information_modal_info = document.getElementById("captured_information_modal_info");
    var meta_information_button = document.getElementById("meta_information_button");

    if (load_more_meta == false) {
        cobrowsing_meta_data_page = 1;
        captured_information_modal_info.innerHTML = "Loading ...";
    }

    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID,
        "page": cobrowsing_meta_data_page
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
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
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                captured_information_modal_info.innerHTML = "";
                var tbody_html = '';
                meta_information_list = response.meta_information_list;
                if(meta_information_list.length) {
                    for (let index = 0; index < meta_information_list.length; index++) {
                        meta_id = meta_information_list[index]["id"];
                        //if (meta_information_list[index]["type"] == "screenshot") {
                            tbody_html += [
                                '<tr>',
                                    '<td style="text-transform: capitalize;">' + meta_information_list[index]["type"] + '</td>',
                                    '<td>' + meta_information_list[index]["datetime"] + '</td>',
                                    '<td style="text-align: center">',
                                        '<!--<a href="/easy-assist/download-file/' + meta_id + '/?session_id=' + COBROWSE_SESSION_ID + '" target="_blank" title="Export As Image"><i class="fas fa-fw fa-download"></i></a> -->',
                                        '<a href="/easy-assist/download-file/' + meta_id + '/?session_id=' + COBROWSE_SESSION_ID + '" download title="Export As Image">',
                                            '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                                '<path d="M10 0C15.5 0 20 4.5 20 10C20 15.5 15.5 20 10 20C4.5 20 0 15.5 0 10C0 4.5 4.5 0 10 0ZM6 15H14V13H6V15ZM14 8H11.5V4H8.5V8H6L10 12L14 8Z" fill="#757575"/>',
                                            '</svg>',
                                        '</a>',
                                    '</td>',
                                '</tr>',

                            ].join('');
                        //} else {
                        //    tbody_html += '<tr><td>' + meta_information_list[index]["type"] + '</td><td>' + meta_information_list[index]["datetime"] + '</td></tr>';
                        //}
                    }

                    if (response.is_last_page == false) {
                        tbody_html += [
                            '<tr onclick="load_more_meta_information(this)">',
                                '<td colspan="3" class="text-center">',
                                    '<button class="btn btn-primary">Load More</button>',
                                '</td>',
                            '</tr>',
                        ].join('');
                    }

                    if (cobrowsing_meta_data_page == 1) {
                        document.getElementById("meta_information_body").innerHTML = tbody_html;
                    } else {
                        document.getElementById("meta_information_body").innerHTML += tbody_html;
                    }
                    document.getElementById("meta_information_head").style.display = "";
                    meta_information_button.innerHTML = "Cancel";
                    meta_information_button.onclick = "";
                    $(meta_information_button).attr("data-dismiss", "modal")
                } else {
                    captured_information_modal_info.innerHTML = "No screenshots";
                    document.getElementById("meta_information_head").style.display = "none";
                }
            } else {
                captured_information_modal_info.innerHTML = "Unable to load the details. Please try again.";
                document.getElementById("meta_information_head").style.display = "none";
                meta_information_button.innerHTML = "Try Again";
                meta_information_button.onclick = fetch_cobrowsing_meta_information;
                $(meta_information_button).attr("data-dismiss", "none")
            }
            load_more_meta = false;
        } else if (this.readyState == 4){
            captured_information_modal_info.innerHTML = "Unable to load the details. Please try again.";
            document.getElementById("meta_information_head").style.display = "none";
            meta_information_button.innerHTML = "Try Again";
            meta_information_button.onclick = fetch_cobrowsing_meta_information;
            $(meta_information_button).attr("data-dismiss", "none")
        }
    }
    xhttp.send(params);
}

function load_more_meta_information(element) {
    element.parentElement.removeChild(element);
    cobrowsing_meta_data_page += 1;
    load_more_meta = true;
    fetch_cobrowsing_meta_information();
}


function share_cobrowsing_session(element, support_agent_id) {

    document.getElementById("share-session-error").innerHTML = "";
    
    let local_storage_obj = get_easyassist_current_session_local_storage_obj();
    
    if (local_storage_obj && local_storage_obj.hasOwnProperty("invite_button_id_to_hide") && local_storage_obj["invite_button_id_to_hide"] == support_agent_id) {
        easyassist_show_long_toast("A transfer request has already been sent to this agent, please try again later.");
        $("#askfor_support_modal").modal('hide');
        return ;
    }

    support_agents = [support_agent_id];

    if (support_agents.length == 0) {
        document.getElementById("share-session-error").innerHTML = "Please select atleast one support agent with whom you want to share the session.";
        return;
    }

    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID,
        "support_agents": support_agents,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Inviting..";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/share-session/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                $("#askfor_support_modal").modal('hide');
                set_desktop_notification_for_agents(support_agents);
                show_easyassist_toast("Support Request has been sent.");
                get_list_of_support_agents();
            } else if (response.status == 301) {
                easyassist_show_long_toast("A transfer request has already been sent to this agent, please try again later.");
            } else {
                show_easyassist_toast("An issue occurred while inviting the agent. Please try again.")
                $("#askfor_support_modal").modal('hide');
            }
            element.innerHTML = "Invite";
        }
    }
    xhttp.send(params);
}

function set_desktop_notification_for_agents(agent_id_list) {
    if (agent_id_list.length == 0) {
        return;
    }
    json_string = JSON.stringify({
        "session_id": COBROWSE_SESSION_ID,
        "agent_id_list": agent_id_list,
        "support_request_notify": true
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/set-notification-for-agent/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status != 200) {
                show_easyassist_toast("Unable to set notification for agent");
            }
        }
    }
    xhttp.send(params);
}

if (window.addEventListener) {
    window.addEventListener('load', start_internet_connectivity_check_interval, false);
} else if (window.attachEvent) {
    window.attachEvent('onload', start_internet_connectivity_check_interval);
}

function check_iframe_cobrowsing_enabled() {
    if(ENABLE_IFRAME_COBROWSING == "True" || ENABLE_IFRAME_COBROWSING == true) {
        return true;
    }
    return false;
}

function check_screen_sharing_cobrowsing_enabled() {
    if(ALLOW_SCREENSHARING_COBROWSE == "True" || ALLOW_SCREENSHARING_COBROWSE == true || ALLOW_SCREENSHARING_COBROWSE == "true") {
        return true;
    }
    return false;
}

function check_video_calling_enabled() {
    if(ALLOW_COBROWSING_MEETING == "True" || ALLOW_COBROWSING_MEETING == true || ALLOW_COBROWSING_MEETING == "true") {
        return true;
    }
    return false;
}

function check_voip_enabled() {
    if(ENABLE_VOIP_CALLING == "True" || ENABLE_VOIP_CALLING == true || ENABLE_VOIP_CALLING == "true") {
        return true;
    }
    return false;
}

function check_voip_video_meeting_enabled() {
    if(ENABLE_VOIP_WITH_VIDEO_CALLING == "True" || ENABLE_VOIP_WITH_VIDEO_CALLING == true || ENABLE_VOIP_WITH_VIDEO_CALLING == "true") {
        return true;
    }
    return false;
}

function start_internet_connectivity_check_interval() {

    if(window.ENABLE_LOW_BANDWIDTH_COBROWSING == "True" && check_screen_sharing_cobrowsing_enabled() == false) {
        initiate_internet_speed_detection();
        internet_connectivity_check_interval = setInterval(function() {
            initiate_internet_speed_detection();
        }, 20000);
    } else {
        initiate_internet_speed_detection();
    }
}

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
    if (avg_speedMbps < (LOW_BANDWIDTH_COBROWSING_THRESHOLD / 1024)) {
        if(AGENT_WEAK_CONNECTION_MODAL_SHOWN == false) {
            show_weak_internet_connectivity_modal();
            AGENT_WEAK_CONNECTION_MODAL_SHOWN = true;
        }
        easyassist_send_agent_weak_connection_message(true);

        if(easyassist_send_agent_weak_connection_message_interval) {
            clearInterval(easyassist_send_agent_weak_connection_message_interval);
        }
        easyassist_send_agent_weak_connection_message_interval = setInterval(function() {
            easyassist_send_agent_weak_connection_message(true);
        }, 30000);

        if(internet_connectivity_check_interval != null) {
            clearInterval(internet_connectivity_check_interval);
        }
    } else {
        // easyassist_send_agent_low_bandwidth_message(false);
    }
}

function sync_client_web_screen_agent() {
    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/sync/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status == 200) {

                if (response.init_transaction == true) {
                    document.getElementById("frames-container").style.display = "none";
                    document.getElementById("transaction-payment-loader").style.display = "block";
                    return;
                }

                // document.getElementById("frames-container").style.display = "flex";
                document.getElementById("transaction-payment-loader").style.display = "none";

                if (response.is_active == false || response.is_archived == true) {

                    if (document.getElementById("close_session_modal").style.display != "block"){
                        session_has_ended=true;
                        client_mouse_element.style.display = "none";
                        open_close_session_modal();
                        framesContainer.style.filter = "blur(3px)";
                        if(response.is_active == false)
                            show_easyassist_toast("Looks like customer has left the session. Please provide your comments before ending session.");
                        else
                            show_easyassist_toast("Looks like admin agent has closed the session. Please provide your comments before ending session.");
                    }

                } else if (response.is_client_connected == false) {
                    // show_easyassist_toast("Looks like we are not receiving any updates from customer side. Kindly check your internet connectivity or check whether customer is still connected or not.");
                    // show_easyassist_toast("Looks like we are not receiving any updates from the customer side. Kindly check your internet connectivity or check whether the customer is still connected or not.");
                    if(get_easyassist_cookie("easyassist_session_id")){
                        if(get_easyassist_cookie("easyassist_client_disconnected_modal_shown") == undefined || get_easyassist_cookie("easyassist_client_disconnected_modal_shown") == "false"){
                            show_client_disconnect_modal();
                            set_easyassist_cookie("easyassist_client_disconnected_modal_shown", "true")
                        }
                    }
                }
                if (response.customer_meeting_request_status == true) {
                    easyassist_customer_meeting_request_hander();
                }
                if (response.allow_customer_meeting == "true" && IS_ADMIN_AGENT == "True") {
                    easyassist_agent_allow_meeting_request_handler();
                }

            } else if (response.status == 500) {
                show_easyassist_toast("Matching session is already expired or doesn't exists");
                window.location = "/easy-assist/sales-ai/dashboard/";
            }
        }
    }
    xhttp.send(params);
}

function get_list_of_support_agents() {

    var support_agents_container = document.getElementById("div-support-agents-container");
    var support_agent_error_div = document.getElementById("support-agent-error-div");
    var support_agent_error = document.getElementById("support-agent-error");
    var support_agent_container_id = document.getElementById("support-agent-container-id");
    
    var selected_lang_pk = "-1";
    var selection_enabled = false;

    support_agents_container.classList.add('justify-content-center');
    support_agent_error.innerHTML = "";
    support_agents_container.innerHTML = "";

    if (ALLOW_LANGUAGE_SUPPORT == 'True' || ALLOW_LANGUAGE_SUPPORT == true || ALLOW_LANGUAGE_SUPPORT == "true") {
        selected_lang_pk = $("#easyassist-language-support-selected").val();
        selection_enabled = true;
    }

    var selected_product_category_pk = "-1";
    if (CHOOSE_PRODUCT_CATEGORY == 'True' || CHOOSE_PRODUCT_CATEGORY == true || CHOOSE_PRODUCT_CATEGORY == "true") {
        selected_product_category_pk = $("#easyassist-product-category-selected").val();
        selection_enabled = true;
    }

    if(selection_enabled == true && selected_lang_pk == "-1" && selected_product_category_pk == "-1"){
        support_agent_container_id.style.display = "none";
        support_agent_error_div.classList.add("d-none");
        return
    }

    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID,
        "selected_lang_pk": selected_lang_pk,
        "selected_product_category_pk": selected_product_category_pk
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

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
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            div_inner_html = "";
            if (response.status == 200) {
                support_agents = response.support_agents;
                if (support_agents.length > 0) {
                    for(let index = 0; index < support_agents.length; index ++) {
                        id = support_agents[index]["id"];
                        username = support_agents[index]["username"];
                        level = support_agents[index]["level"];
                        div_inner_html += [
                            '<li>',
                                '<div id = "' + id + '-support-agent-username"" class="support-agent-text">',
                                  username + ' - ' + level,
                                '</div>',
                                '<div class="buttons-group-div">',
                                  '<button class="agent-invite-btn" id = "' + id + '-invite-btn" onclick="share_cobrowsing_session(this, \'' + id + '\')">Invite</a>',
                                  '<button class="transfer-session-btn" onclick="update_transfer_agent_log(this, \'' + id + '\')">Transfer</button>',
                                  '<p id = "' + id + '-transfer-request-text"" style="display:none; color:#34D399 !important">Transfer request sent</p>',
                                  '</div>',
                            '</li>',
                        ].join('');
                    }
                    support_agents_container.classList.remove('justify-content-center');
                    support_agents_container.innerHTML = div_inner_html;
                    
                    let local_storage_obj = get_easyassist_current_session_local_storage_obj();
                    
                    if(local_storage_obj && local_storage_obj.hasOwnProperty("is_session_transferred_request_sent")){
                        if(local_storage_obj["is_session_transferred_request_sent"] == "true") {
                            $(".transfer-session-btn").css({"display":"none"});
                            $("#" + local_storage_obj["invite_button_id_to_hide"] + "-invite-btn").css({"display":"none"});
                            $("#" + local_storage_obj["invite_button_id_to_hide"] + "-transfer-request-text").css({"display":""})
                        } else {
                            $(".transfer-session-btn").css({"display":""});
                            $("#" + local_storage_obj["invite_button_id_to_hide"] + "-invite-btn").css({"display":""});
                            $("#" + local_storage_obj["invite_button_id_to_hide"] + "-transfer-request-text").css({"display":"none"})
                        }
                    }
                    
                    if(get_easyassist_cookie("is_cobrowse_meeting_active") == COBROWSE_SESSION_ID) {
                        $(".transfer-session-btn").addClass("half-opacity");
                    }

                    if(ENABLE_SESSION_TRANSFER_IN_COBROWSING == "False" || IS_ADMIN_AGENT == "False") {
                        $(".transfer-session-btn").addClass("d-none");
                    }
        
                    if (local_storage_obj && local_storage_obj.hasOwnProperty("invite_button_id_to_hide")) {
                        if (local_storage_obj["invite_button_id_to_hide"] != "") {
                            $("#" + local_storage_obj["invite_button_id_to_hide"] + "-invite-btn").css("opacity", "0.6");
                        } else {
                            $("#" + local_storage_obj["invite_button_id_to_hide"] + "-invite-btn").css("opacity", "");
                        }
                    }
                  
                    support_agent_error_div.classList.add("d-none");
                    support_agent_container_id.style.display = "";
                } else {
                    support_agent_error_div.classList.remove("d-none") ;
                    support_agent_error.innerHTML = "No active agents found.";
                    support_agent_container_id.style.display = "none";
                }
            } else {
                support_agent_error_div.classList.remove("d-none") ;
                support_agent_error.innerHTML = "Unable to load the details. Please try again.";
                support_agent_container_id.style.display = "none";
            }
        } else if (this.readyState == 4){
            support_agent_error_div.classList.remove("d-none") ;
            support_agent_error.innerHTML = "Unable to load the details. Please try again.";
            support_agent_container_id.style.display = "none";
        }
    }
    xhttp.send(params);
}

function save_easyassist_system_audit_trail(category, description) {

    if (category.trim() == "") {
        return;
    }

    if (description.trim() == "") {
        return;
    }

    json_string = JSON.stringify({
        "category": category,
        "description": description,
        "session_id": COBROWSE_SESSION_ID
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/save-system-audit/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
        }
    }
    xhttp.send(params);
}

function save_cobrowsing_chat_history(chat_message, sender, attachment, attachment_file_name, chat_type, agent_profile_pic_source) {

    json_string = {
        "session_id": COBROWSE_SESSION_ID,
        "sender": sender,
        "message": chat_message,
        "attachment": attachment,
        "attachment_file_name": attachment_file_name,
        "chat_type": chat_type,
    };

    if (sender != "client") {
        json_string["agent_profile_pic_source"] = agent_profile_pic_source;
    }

    json_string = JSON.stringify(json_string);
                
    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/save-cobrowsing-chat/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if(response['status'] == 301) {
                var error_element = document.getElementById("send-document-error");
                error_element.style.color = "red";
                error_element.innerHTML = response['message'];
            }
        }
    }
    xhttp.send(params);
}

function send_chat_message_from_agent(message, attachment, attachment_file_name, chat_type) {
    
    if(!is_chat_functionality_enabled()) {
        return;
    }
    
    var agent_name = window.AGENT_NAME;
    var agent_profile_pic_source = window.AGENT_PROFILE_PIC_SOURCE;
    save_cobrowsing_chat_history(message, "agent", attachment, attachment_file_name, chat_type, agent_profile_pic_source);
    json_string = JSON.stringify({
        "agent_name": agent_name,
        "agent_profile_pic_source": agent_profile_pic_source,
        "type": "chat",
        "message": message,
        "attachment": attachment,
        "attachment_file_name": attachment_file_name,
        "chat_type": chat_type,
        "sender": window.AGENT_USERNAME,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    //console.log("request for html has been sent: ", new Date());
    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function load_allincall_chat_box(focus=false) {
    var allincall_chat_box = document.getElementById("allincall-chat-box");

    if(allincall_chat_box.getAttribute('src') == "") {
        allincall_chat_box.src = "/easy-assist/sales-ai/livechat/?session_id=" + COBROWSE_SESSION_ID;
        allincall_chat_box.onload = function() {
            chat_box_loaded = true;
            load_chat_history();

            if(focus) {
                var allincall_chat_window = allincall_chat_box.contentWindow;
                focus_livechat_input();

                if(IS_MOBILE == "False") {
                    allincall_chat_window.postMessage(JSON.stringify({
                        "focus_textbox": "focus-textbox"
                    }), window.location.protocol + "//" + window.location.host);
                }
            }
        }
    }
}

function is_chat_functionality_enabled() {
    if(window.ENABLE_CHAT_FUNCTIONALITY == "True" || window.ENABLE_CHAT_FUNCTIONALITY == true) {
        return true;
    }
    return false;
}

function open_livechat_agent_window() {

    if(!is_chat_functionality_enabled()) {
        return;
    }
    var allincall_chat_box = document.getElementById("allincall-chat-box");
    if(window.ENABLE_CHAT_BUBBLE == "True" && window.IS_MOBILE == "False"){
        if(allincall_chat_box.classList.contains("allincall-scale-out-br")) {
            allincall_chat_box.classList.remove("allincall-scale-out-br");
        }

        if (allincall_chat_box.classList.contains("allincall-scale-out-br-right-side")) {
            allincall_chat_box.classList.remove("allincall-scale-out-br-right-side");
        }
        
        allincall_chat_box.style.display = "block";
        allincall_chat_box.classList.add("animate__animated");
        allincall_chat_box.classList.add("animate__slideInUp");
    } else {
        allincall_chat_box.style.display = "block";
    }
    set_easyassist_current_session_local_storage_obj("new_message_seen","true");
    set_easyassist_current_session_local_storage_obj("last_message","");
    if( $("#chat-minimize-icon-wrapper")){
        $("#chat-minimize-icon-wrapper").css({"display":"none"});
    }
    if(allincall_chat_box.getAttribute('src') == "") {
        load_allincall_chat_box(true);
    } else {
        var allincall_chat_window = allincall_chat_box.contentWindow;

        focus_livechat_input();

        if(IS_MOBILE == "False") {
            allincall_chat_window.postMessage(JSON.stringify({
                "focus_textbox": "focus-textbox"
            }), window.location.protocol + "//" + window.location.host);
        }
    }
}

function focus_livechat_input() {
    try {
        var inner_doc = document.getElementById("allincall-chat-box").contentWindow.document;
        if(IS_MOBILE == "False") {
            $(inner_doc).ready(function() {
              inner_doc.getElementById("user_input").focus();
            });
        }
    } catch(err) {
        console.log("focus_livechat_input: ", err);
    }
}

window.addEventListener('message', function(event) {
    // IMPORTANT: Check the origin of the data!
    if (~event.origin.indexOf(window.location.protocol + "//" + window.location.host)) {
        if(event.data == "voip_meeting_ready") {
            send_voip_meeting_ready_over_socket();
            voip_meeting_ready_interval = setInterval(function() {
                if(get_easyassist_cookie("is_customer_voip_meeting_joined") == COBROWSE_SESSION_ID || IS_ADMIN_AGENT == 'False') {
                    if(get_easyassist_cookie("is_meeting_audio_muted") == "true") {
                        document.getElementById("agent-meeting-mic-off-btn").click();
                    }
                    document.getElementById("easyassist-voip-loader").style.display = 'none';
                    clearInterval(voip_meeting_ready_interval);
                }
            }, 1000);
        } else if(event.data == "voip_meeting_ended") {
            reset_voip_meeting();
        }

        if(event.data.event == "voip_function_error") {
            easyassist_show_function_fail_modal(code=event.data.error_code);
        }

        if(event.data.event == "voip_audio_status") {
            if(event.data.is_muted) {
                document.getElementById("agent-meeting-mic-off-btn").style.display = "none";
                document.getElementById("agent-meeting-mic-on-btn").style.display = "";
            } else {
                document.getElementById("agent-meeting-mic-on-btn").style.display = "none";
                document.getElementById("agent-meeting-mic-off-btn").style.display = "";
            }

            set_easyassist_cookie("is_meeting_audio_muted", event.data.is_muted);
        }

        if(event.data.event == "voip_video_status") {
            if(document.getElementById("agent-meeting-video-off-btn")) {
                if(event.data.is_muted) {
                    document.getElementById("agent-meeting-video-off-btn").style.display = "none";
                    document.getElementById("agent-meeting-video-on-btn").style.display = "";
                } else {
                    document.getElementById("agent-meeting-video-on-btn").style.display = "none";
                    document.getElementById("agent-meeting-video-off-btn").style.display = "";
                }
            }
        }

        if (event.data.event_id === "cobrowsing-agent-chat-message") {
            message = event.data.data.message;
            attachment = event.data.data.attachment;
            attachment_file_name = event.data.data.attachment_file_name;
            send_chat_message_from_agent(message, attachment, attachment_file_name, "chat_message");
            return;
        } else if(event.data.event_id == "open_pdf_render_modal"){
            close_chatbot_animation();
            easyassist_show_chat_bubble();
            json_string = JSON.stringify({
                "type": "open_pdf_render_modal",
                "file_name": event.data.file_name,
                "file_src": event.data.file_src,
                "session_id": event.data.session_id,
            });
        
            encrypted_data = easyassist_custom_encrypt(json_string);
        
            encrypted_data = {
                "Request": encrypted_data
            };
        
            send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
            return
        }else if (event.data.event_id === "livechat-typing") {
            easyassist_send_livechat_typing_indication()
            return
        }
        if (event.data == "close-bot") {
            close_chatbot_animation();
            if(window.ENABLE_CHAT_BUBBLE == "True" && window.IS_MOBILE == "False"){
                $(".chat-talk-bubble").css({"display":"none"});
                $("#chat-minimize-icon-wrapper").css({"display":"none"});
            }
        } else if (event.data == "minimize-chatbot") {
            $(".chat-talk-bubble").css({"display":"none"});
            $("#chat-minimize-icon-wrapper").css({"display":"block"});
        } else {
            // The data hasn't been sent from your site!
            // Be careful! Do not use it.
            return;
        }
    }
});

function close_chatbot_animation() {
    if(window.ENABLE_CHAT_BUBBLE == "True" && window.IS_MOBILE != "True"){
        livechat_iframe = document.getElementById("allincall-chat-box");
        if(livechat_iframe.classList.contains("animate__slideInUp")) {
            livechat_iframe.classList.remove("animate__slideInUp");
        }
        if (window.FLOATING_BUTTON_POSITION == "right") {
            livechat_iframe.classList.add("allincall-scale-out-br-right-side")
        } else {
            livechat_iframe.classList.add("allincall-scale-out-br");
        }
    }
    else {
        document.getElementById("allincall-chat-box").style.animationName = "bottom-left-right-anime-close";
        document.getElementById("allincall-chat-box").style.display = "none";
    }
}

function check_current_tab_active() {
    try {
        var hidden = null;
        if (typeof document.hidden !== "undefined") { // Opera 12.10 and Firefox 18 and later support
            hidden = "hidden";
        } else if (typeof document.msHidden !== "undefined") {
            hidden = "msHidden";
        } else if (typeof document.webkitHidden !== "undefined") {
            hidden = "webkitHidden";
        }

        if (document[hidden]) {
            return false;
        }
        return true;
    } catch(err) {
        console.log("check_current_tab_active: ", err);
    }
}

function chat_notification_sound(){
    let greeting_bubble_popup_sound_element = document.getElementById("easyassist-greeting-bubble-popup-sound");

    if (!greeting_bubble_popup_sound_element) {
        return;
    }

    try {
        if (greeting_bubble_popup_sound_element.paused) {
            greeting_bubble_popup_sound_element.play();
        } else {
            greeting_bubble_popup_sound_element.currentTime = 0;
        }
    } catch (err) {
        console.log(err)
    }
}

function send_chat_notification(notification_title,notification_body){
    if(Notification.permission === "granted"){
        chat_notification_sound();
        let notification = new Notification(notification_title, {
            body: notification_body,
            silent: true,
            });
            notification.onclick = function() {
                window.focus();
            };
    }
    else if (Notification.permission !== "denied") {
        Notification.requestPermission().then(function(permission) {
            if (permission === "granted") {
                chat_notification_sound();
                let notification = new Notification(notification_title, {
                    body: notification_body,
                    silent: true,        
                    });
                    notification.onclick = function() {
                        window.focus();
                    };
            }
        });    
    }
}

function get_notification_body(message, attachment_file_name){

    if(check_text_link(message)) {
        // for multiple url links
        while(message.indexOf("<a") != -1){
            let parser = new DOMParser();
            let link_start_index = message.indexOf("<a");
            let link_end_index = message.indexOf("</a>");
            let html_parsed_obj = parser.parseFromString(message.substring(link_start_index, link_end_index), 'text/html');
            let url_message = html_parsed_obj.querySelector('a').href;
            message = message.substring(0,link_start_index) + url_message + message.substring(link_end_index+4, message.length);
        }
    }

    if(attachment_file_name != "None") {
        var extension = attachment_file_name.split(".")[1];
        let short_file_name = attachment_file_name
        if(short_file_name.length > 10) {
            short_file_name = get_shorter_file_name(attachment_file_name, 10);
        }
        if(message) {
            message = short_file_name.slice(0,short_file_name.length-4) + "." + extension + "\n" + message;
        } else {
            message = short_file_name.slice(0,short_file_name.length-4) + "." + extension;
        }
    } 
    
    return message;
}

function chat_notification(message,attachment_file_name,invite_agent_name){

    let is_current_tab_focussed = check_current_tab_active();

    //Check for is current tab is not in focus and Notificaiton are allowed on the browser
    if(!is_current_tab_focussed && typeof Notification !== "undefined"){
    
        let sender_name;
        if(invite_agent_name != null){
            sender_name = invite_agent_name;
        }
        else{  
            sender_name = window.CLIENT_NAME;            
            if(sender_name == ""){
                sender_name = "Customer";
            }           
        }        

        let notification_title = `${sender_name} messaged you!`;
        let notification_body = get_notification_body(message, attachment_file_name);       

        send_chat_notification(notification_title,notification_body);
    }    
}

function set_client_response(message, attachment, attachment_file_name) {
    try {
        if(IS_MOBILE == "True") {
            document.getElementById("allincall-chat-box").style.display = "block";
            set_easyassist_current_session_local_storage_obj("new_message_seen","true");
        }
        if(window.ENABLE_CHAT_BUBBLE == "True" && IS_MOBILE == "False") {
            set_easyassist_current_session_local_storage_obj("new_message_seen","false");
            try {
                let customer_name = window.CLIENT_NAME;
                if(customer_name == "") {
                    customer_name = "Customer"
                }
                append_chat_bubble_message(customer_name, message, attachment, attachment_file_name);
            } catch (err) {
                console.log(err)
            }
        }
        chat_notification(message,attachment_file_name,null);
        if(chat_box_loaded == true){
            var allincall_chat_box = document.getElementById("allincall-chat-box");
            if (window.ENABLE_CHAT_BUBBLE == "False" && allincall_chat_box.style.display == "none" ) {
                allincall_chat_box.style.display = "block";
                // We are setting new_message_seen as true here to avoid the scenario in which a aagent is inside the session
                // and someone changes the configuration
                set_easyassist_current_session_local_storage_obj("new_message_seen","true");
                focus_livechat_input();
            }
            allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow;
            allincall_chat_window.postMessage(JSON.stringify({
                "message": message,
                "attachment": attachment,
                "attachment_file_name": attachment_file_name,
                "show_client_message": true,
                "name": window.CLIENT_NAME,
                "sender": "client",
            }), window.location.protocol + "//" + window.location.host);
        }
    } catch(err) {
        console.log(err);
    }

    if(IS_ADMIN_AGENT == "True") {
        save_cobrowsing_chat_history(message, "client", attachment, attachment_file_name, "chat_message");
    }
}

function set_livechat_typing(name, role){
    allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow;
    allincall_chat_window.postMessage(JSON.stringify({
        "id": "livechat-typing",
        "role": role,
        "name": name
    }), window.location.protocol + "//" + window.location.host);
}

function set_agent_response(message, attachment, attachment_file_name, chat_type, agent_name, agent_profile_pic_source) {
    if(IS_MOBILE == "True" && chat_type != "chat_bubble" ) {
        document.getElementById("allincall-chat-box").style.display = "block";
        set_easyassist_current_session_local_storage_obj("new_message_seen","true");
    }
    if(window.ENABLE_CHAT_BUBBLE == "True" && IS_MOBILE == "False" && chat_type != "chat_bubble") {
        set_easyassist_current_session_local_storage_obj("new_message_seen","false");
        if ( chat_type != "agent_connect_message") {
            try { 
                append_chat_bubble_message(agent_name, message, attachment, attachment_file_name);
            } catch (err) {
                console.log(err)
            }
        } else {
            document.getElementById("allincall-chat-box").style.display = "block";
            document.getElementById("allincall-chat-box").classList.add("animate__animated");
            document.getElementById("allincall-chat-box").classList.add("animate__slideInUp");
            set_easyassist_current_session_local_storage_obj("new_message_seen","true");
            if($("#chat-minimize-icon-wrapper")) {
                $("chat-minimize-icon-wrapper").css({"display":"none"});
            }
        }
    } else {
        if(chat_type != "chat_bubble" && document.getElementById("allincall-chat-box")) {
            document.getElementById("allincall-chat-box").style.display = "block";
        }
    }

    allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow;
    chat_notification(message,attachment_file_name,agent_name);
    allincall_chat_window.postMessage(JSON.stringify({
        "message": message,
        "attachment": attachment,
        "attachment_file_name": attachment_file_name,
        "show_other_agent_message": true,
        "name": agent_name,
        "agent_profile_pic_source": agent_profile_pic_source,
        "chat_type": chat_type,
        "sender": "invited_agent",
    }), window.location.protocol + "//" + window.location.host);
}

function capture_request_edit_access() {
    requested_for_edit_access = true;
    json_string = JSON.stringify({
        "type": "request-edit-access",
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
    save_easyassist_system_audit_trail("edit_access", "agent_requested_edit_access");

    show_easyassist_toast("Request for edit access has been sent to customer");
}

function detect_agent_value_change(event) {
    if (get_easyassist_cookie("request_edit_access") == COBROWSE_SESSION_ID) {

        var iframe_id = easyassist_get_iframe_id(event);

        element = event.target;
        tag_type = element.getAttribute("type");
        tag_name = element.tagName.toLowerCase();

        element_id = easyassist_get_easyassist_id_from_element(element);
        if(element_id == null || element_id == undefined) {
            console.log("Danger: Element does not exist");
            return;
        }

        value = element.value;

        if (tag_name == "select") {
            var selected_option = element.options[element.selectedIndex];
            if (selected_option != null && selected_option != undefined) {
                value = selected_option.innerHTML;
            }
        }

        if (tag_type == "checkbox" || tag_type == "radio") {
            value = element.checked;
        }

        json_string = JSON.stringify({
            "type": "sync-form",
            "tag_type": tag_type,
            "tag_name": tag_name,
            "easyassist_element_id": element_id,
            "value": value,
            "agent_name": AGENT_NAME,
            "agent_username": window.AGENT_USERNAME,
            "iframe_id": iframe_id,
        });

        encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        send_message_over_easyassist_socket(encrypted_data, "agent");
    }
}

function append_agent_message_into_chatbox(message, attachment, attachment_file_name, chat_type) {
    
    if(!is_chat_functionality_enabled()) {
        return;
    }

    if (document.getElementById("allincall-chat-box").style.display == "none") {
        if(window.ENABLE_CHAT_BUBBLE == "True"){
            livechat_iframe = document.getElementById("allincall-chat-box");
            if(livechat_iframe.classList.contains("allincall-scale-out-br")) {
                livechat_iframe.classList.remove("allincall-scale-out-br");
            }

            if(livechat_iframe.classList.contains("allincall-scale-out-br-right-side")) {
                livechat_iframe.classList.remove("allincall-scale-out-br-right-side");
            }

            livechat_iframe.style.display = "block";
            livechat_iframe.classList.add("animate__animated");
            livechat_iframe.classList.add("animate__slideInUp");
        } else {
            document.getElementById("allincall-chat-box").style.display = "block";
        }
    }
    allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow;
    allincall_chat_window.postMessage(JSON.stringify({
        "message": message,
        "attachment": attachment,
        "attachment_file_name": attachment_file_name,
        "show_agent_message": true,
        "name": window.AGENT_NAME,
        "sender": window.AGENT_USERNAME,
        "chat_type": chat_type,
    }), window.location.protocol + "//" + window.location.host);

    send_chat_message_from_agent(message, attachment, attachment_file_name, chat_type);
}

function send_support_material_doc(element) {
    var action_cell = element.parentElement;
    var message_cell = action_cell.previousElementSibling;
    var attachment_cell = message_cell.previousElementSibling;

    var attachment = attachment_cell.children[0].href;
    attachment = strip_html(attachment);

    var message = message_cell.children[0].value;
    if (check_text_link(message) == false) {
        message = strip_html(message);
        message = remove_special_characters_from_str(message);
    } else {
        message = easyassist_linkify(perform_url_encoding(message));
    }

    var attachment_file_name = attachment_cell.children[0].text;
    attachment_file_name = strip_html(attachment_file_name);
    attachment_file_name = remove_special_characters_from_str(attachment_file_name)

    append_agent_message_into_chatbox(message, attachment, attachment_file_name, "chat_message");

    $('#support_material_modal').modal('toggle');
}

function get_support_material() {

    if(document.getElementById("support_material_table_body").children.length) {
        return;
    }
    var support_material_modal_info = document.getElementById("support_material_modal_info");
    var support_material_modal_button = document.getElementById("support_material_modal_button");

    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/get-support-material/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            div_inner_html = "";
            if (response.status == 200) {
                support_material_modal_info.innerHTML = "";
                var support_document = response.support_document;

                if (support_document.length > 0) {
                    for (let index = 0; index < support_document.length; index++) {
                        var support_document_obj = support_document[index];
                        var file_name = support_document_obj["file_name"];
                        var file_path = window.location.protocol + "//" + window.location.host + "/" + support_document_obj["file_path"];
                        var message = file_name;
                        div_inner_html += '<tr>';
                        div_inner_html += '<td style="vertical-align:middle;"> <a class="support-document-link" href="' + file_path + '" target="_blank" style="color:'+FLOATING_BUTTON_BG_COLOR+';" >' + file_name + '</a> </td>';
                        div_inner_html += '<td> <input class="support-document-message-text" type="text" value="' + message + '" style="width: 100%;"> </td>';
                        div_inner_html += '\
                            <td>\
                                <button class="btn btn-action" onclick="send_support_material_doc(this)">\
                                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                        <path d="M15.6377 7.40491L0.988524 0.070419C0.873708 0.0129211 0.744741 -0.0101171 0.617152 0.00407857C0.489563 0.0182742 0.368792 0.0690985 0.269381 0.150432C0.174443 0.230106 0.103582 0.334718 0.064764 0.452509C0.0259456 0.570299 0.0207089 0.696597 0.0496425 0.817204L1.81421 7.33157H9.34524V8.66511H1.81421L0.0230075 15.1595C-0.00414248 15.2602 -0.00731172 15.3659 0.0137547 15.4681C0.0348212 15.5702 0.0795356 15.666 0.144302 15.7477C0.209069 15.8294 0.292081 15.8948 0.386663 15.9386C0.481246 15.9823 0.584759 16.0032 0.688881 15.9996C0.793118 15.999 0.895753 15.9739 0.988524 15.9263L15.6377 8.59177C15.7468 8.53581 15.8383 8.4508 15.9023 8.3461C15.9662 8.24139 16 8.12106 16 7.99834C16 7.87562 15.9662 7.75528 15.9023 7.65058C15.8383 7.54588 15.7468 7.46087 15.6377 7.40491Z" fill="' + FLOATING_BUTTON_BG_COLOR + '"/>\
                                    </svg>\
                                </button>\
                            </td>';
                        div_inner_html += '<tr>';
                        document.getElementById("support_material_table_body").innerHTML = div_inner_html;
                        document.getElementById("support_material_table").style.display = "inline-table";
                        document.getElementById("support_material_table_head").style.display = "";
                        support_material_modal_button.innerHTML = "Cancel";
                        support_material_modal_button.onclick = "";
                        $(support_material_modal_button).attr("data-dismiss", "modal");
                    }
                } else {
                    support_material_modal_info.innerHTML = "No Support Document Found.";
                    document.getElementById("support_material_table_head").style.display = "none";
                    support_material_modal_button.innerHTML = "Cancel";
                    support_material_modal_button.onclick = "";
                    $(support_material_modal_button).attr("data-dismiss", "modal");
                }
            } else {
                support_material_modal_info.innerHTML = "Unable to load the details. Please Try again.";
                document.getElementById("support_material_table_head").style.display = "none";
                support_material_modal_button.innerHTML = "Try Again";
                support_material_modal_button.onclick = get_support_material;
                $(support_material_modal_button).attr("data-dismiss", "none");
            }
        } else if (this.readyState == 4){
            support_material_modal_info.innerHTML = "Unable to load the details. Please Try again.";
            document.getElementById("support_material_table_head").style.display = "none";
            support_material_modal_button.innerHTML = "Try Again";
            support_material_modal_button.onclick = get_support_material;
            $(support_material_modal_button).attr("data-dismiss", "none");
        }
    }
    xhttp.send(params);
}

function send_agent_name() {
  allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow
  allincall_chat_window.postMessage(JSON.stringify({
      "id": "agent_name",
      "name": window.AGENT_NAME,
      "session_id": COBROWSE_SESSION_ID,
      "agent_connect_message": AGENT_CONNECT_MESSAGE
  }), window.location.protocol + "//" + window.location.host);
}

function show_hyperlink_inside_text(text) {
    var urlRegex =/(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
    return text.replace(urlRegex, function(url) {
        return '<a href="' + url +'" target="_blank">' + url + '</a>';
    });
}

function load_chat_history() {
    json_string = JSON.stringify({
        "session_id": COBROWSE_SESSION_ID
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

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
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            // AGENT_CONNECT_MESSAGE = response.agent_connect_message;

            // if(check_voip_enabled() || check_voip_video_meeting_enabled()) {
            //     AGENT_CONNECT_MESSAGE = "";
            // }

            window.AGENT_NAME = response.agent_name;
            window.CLIENT_NAME = response.client_name;
            if (response.status == 200 && response.chat_history.length > 0) {
                // AGENT_CONNECT_MESSAGE = "";
                chat_history = response.chat_history;
                allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow;
                for (let index = 0; index < chat_history.length; index++) {
                    sender = chat_history[index]["sender"];
                    sender_name = chat_history[index]["sender_name"];
                    message = chat_history[index]["message"];
                    message=show_hyperlink_inside_text(message);
                    datetime = chat_history[index]["datetime"];
                    var time = datetime.split(" ")[3] + " " + datetime.split(" ")[4];
                    attachment = chat_history[index]["attachment"];
                    attachment_file_name = chat_history[index]["attachment_file_name"];
                    chat_type = chat_history[index]["chat_type"];
                    agent_profile_pic_source = chat_history[index]["agent_profile_pic_source"]
                    
                    if (sender == "client") {
                        allincall_chat_window.postMessage(JSON.stringify({
                            "message": message,
                            "attachment": attachment,
                            "attachment_file_name": attachment_file_name,
                            "show_client_message": true,
                            "name": window.CLIENT_NAME,
                            "time": time,
                            "chat_type": chat_type,
                            "sender": sender,
                        }), window.location.protocol + "//" + window.location.host);
                    } else if(sender == window.AGENT_USERNAME) {
                        allincall_chat_window.postMessage(JSON.stringify({
                            "message": message,
                            "attachment": attachment,
                            "attachment_file_name": attachment_file_name,
                            "show_agent_message": true,
                            "time": time,
                            "name": sender_name,
                            "chat_type": chat_type,
                            "sender": sender,
                            "agent_profile_pic_source": agent_profile_pic_source,
                        }), window.location.protocol + "//" + window.location.host);
                    } else {
                        allincall_chat_window.postMessage(JSON.stringify({
                            "message": message,
                            "attachment": attachment,
                            "attachment_file_name": attachment_file_name,
                            "show_other_agent_message": true,
                            "time": time,
                            "name": sender_name,
                            "chat_type": chat_type,
                            "sender": sender,
                            "agent_profile_pic_source": agent_profile_pic_source,
                        }), window.location.protocol + "//" + window.location.host);
                    }
                }
            }
            setTimeout(function() {
                send_agent_name();
            }, 2000);
            
        }
    }
    xhttp.send(params);
}


//////////////////////  Screen Recording   /////////////////////////////////////////////

var screen_recorder_on = false;
let recorder, stream, audioTrack, videoTrack, displayStream, audioStream;

async function startRecording(e) {

    try {

        displayStream = await navigator.mediaDevices.getDisplayMedia({
            video: { mediaSource: "screen" }
        });

        [videoTrack] = displayStream.getVideoTracks();

        audioStream = await navigator.mediaDevices.getUserMedia({
            audio: true,
            video: false
        });
        [audioTrack] = audioStream.getAudioTracks();
        stream = new MediaStream([videoTrack, audioTrack]);
        recorder = new MediaRecorder(stream);
        stream.getVideoTracks()[0].onended = function() {
            stop_screen_recording();
        }
        show_easyassist_toast("Recording has started. This session is being recorded for quality and training purposes.");
        easyassist_send_customer_message("This session is being recorded for quality and training purposes.");
    } catch {
        screen_recorder_on = false;
        if(IS_MOBILE == "True") {
            e.parentElement.nextElementSibling.innerText = "Start screen recording";
            e.parentElement.style.backgroundColor = 'initial';
        } else {
            document.getElementById('stop-recording-svg-id').style.display = "none";
            document.getElementById('start-recording-svg-id').style.display = "block";
            document.getElementById('screen-recording-tooltip').innerHTML = "Start screen recording"
        }
        // set_easyassist_cookie("screen_recorder_on", screen_recorder_on);
        return;
    }

    save_cobrowseing_recorded_data(null, true);

    recorder.ondataavailable = blob => save_cobrowseing_recorded_data(blob);

    recorder.start(5000);
}

var recording_data_save_error_shown = false;

function save_cobrowseing_recorded_data(blob, is_first_packet=false) {

    var filename = COBROWSE_SESSION_ID + '.webm';
    var file = null;
    if(blob != null) {
        file = new File([blob.data], filename, {
            type: 'video/webm'
        });
    }
    var formData = new FormData();
    formData.append("uploaded_data", file);
    formData.append("session_id", COBROWSE_SESSION_ID);
    formData.append("screen_recorder_on", screen_recorder_on);
    formData.append("is_first_packet", is_first_packet);

    $.ajax({
        url: "/easy-assist/save-cobrowsing-screen-recorded-data/",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        headers: {
            'X-CSRFToken': get_csrfmiddlewaretoken()
        },
        success: function(response) {
            if (response["status"] == 200) {
                console.log("Data packet saved successfully.");
            } else {
                if(recording_data_save_error_shown == false){
                    easyassist_show_function_fail_modal(code=606);
                    recording_data_save_error_shown = true;
                }
                console.log("Unable to save data packet");
            }
        },
        error: function(xhr, textstatus, errorthrown) {
            if(recording_data_save_error_shown == false){
                easyassist_show_function_fail_modal(code=606);
                recording_data_save_error_shown = true;
            }
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        }
    });
}

function start_screen_recording(e) {

    if (screen_recorder_on) {
        var stopRecordingDiv = document.getElementById('stop-recording-div-toast');
        if(stopRecordingDiv.style.display === "flex") {
            stopRecordingDiv.style.display = "none";
        } else {
            stopRecordingDiv.style.display = "flex";
        }
    } else {
        if(IS_MOBILE == "True") {
            e.parentElement.nextElementSibling.innerText = "Stop screen recording";
            e.parentElement.style.backgroundColor = find_light_color(FLOATING_BUTTON_BG_COLOR, 300);
        } else {
            document.getElementById('start-recording-svg-id').style.display = "none";
            document.getElementById('stop-recording-svg-id').style.display = "block";
            document.getElementById('screen-recording-tooltip').innerHTML = "Stop screen recording"
        }
        startRecording(e);
        screen_recorder_on = true;
    }
    // set_easyassist_cookie("screen_recorder_on", screen_recorder_on);
}

function stop_screen_recording(event=null) {
    document.getElementById('stop-recording-btn').parentNode.style.display = "none";
    
    if(event != null) {
        event.preventDefault();
        event.stopPropagation();
    }

    if(IS_MOBILE == "True") {
        document.getElementById('screen-recording-tooltip').innerText = "Start screen recording";
        document.getElementById('start-screen-recording-btn').style.backgroundColor = 'initial';
    } else {
        document.getElementById('stop-recording-svg-id').style.display = "none";
        document.getElementById('start-recording-svg-id').style.display = "block";
        document.getElementById('screen-recording-tooltip').innerHTML = "Start screen recording"
    }
    screen_recorder_on = false;
    recorder.stop();
    stream.getVideoTracks()[0].stop();
    stream.getAudioTracks()[0].stop();
}

function connect_with_client(session_id) {
    $("#request_meeting_modal").modal("hide");
    if (session_id == null || session_id == undefined) {

        return;
    }
    set_easyassist_cookie("is_cobrowse_meeting_on", "true");
    window.open("/easy-assist/meeting/" + session_id + "?is_meeting_cobrowsing=true", "_blank",);
}

function voip_connect_with_client() {
    var url = window.location.protocol + "//" + window.location.host + "/easy-assist/agent-cobrowse-meeting/" + COBROWSE_SESSION_ID;
    window.open(url, "_blank",);
}

function request_for_meeting(session_id) {

    // if(call_initiate_by_customer == "true"){
    //     if(check_voip_enabled()){
    //         show_easyassist_toast("Customer has initiated a Voice call, request you to accept it")
    //     } else{
    //         show_easyassist_toast("Customer has initiated a Video call, request you to accept it")
    //     }
    //     $("#request_meeting_modal").modal('hide');
    //     return;
    // }

    var local_storage_obj = get_easyassist_current_session_local_storage_obj();
    if(local_storage_obj != null) {
        if(local_storage_obj.hasOwnProperty("call_initiate_by_customer")) {
            if (local_storage_obj["call_initiate_by_customer"] == "true") {
                if(check_voip_enabled()){
                    show_easyassist_toast("Customer has initiated a Voice call, request you to accept it")
                } else{
                    show_easyassist_toast("Customer has initiated a Video call, request you to accept it")
                }
                $("#request_meeting_modal").modal('hide');
                return;
            }
        }
    }

    request_params = {
        "session_id": session_id
    };

    send_invited_agent_call_request_packet();
    let is_cobrowse_meeting_active = get_easyassist_cookie("is_cobrowse_meeting_active");
    if(is_cobrowse_meeting_active == COBROWSE_SESSION_ID) {
        show_easyassist_toast("Meeting request has been sent.");
        $("#request_meeting_modal").modal("hide");
        return;
    }
    json_params = JSON.stringify(request_params);
    encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var request_meeting_error = document.getElementById("request_meeting_error");
    send_call_initiate_over_socket();
    if(check_voip_enabled()) {
        if(request_meeting_error.offsetParent == null) {
            show_easyassist_toast("An voice call has been initiated to the customer.");
        }
        document.getElementById("voip-call-icon").style.display = 'none';
        document.getElementById("voip-calling-icon").style.display = 'flex';
        setTimeout(function() {
            toggle_voip_ringing_sound(true);
        }, 2000);
    }

    if(check_voip_video_meeting_enabled()) {
        if(request_meeting_error.offsetParent == null) {
            show_easyassist_toast("A video call has been initiated to the customer.");
        }
        setTimeout(function() {
            toggle_voip_ringing_sound(true);
        }, 2000);
    }

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/request-assist-meeting/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                if(request_meeting_error.offsetParent) {
                    request_meeting_error.innerHTML = "Request has been sent to customer";
                    request_meeting_error.style.color = 'green';
                }

                if(check_meeting_status_interval != null) {
                    clearInterval(check_meeting_status_interval);
                    check_meeting_status_interval = null;
                }

                check_meeting_status_interval = setInterval(function() {
                    check_meeting_status(session_id)
                }, 5000)
            } else {
                // $("#request_meeting_modal").modal("hide");
                request_meeting_error.innerHTML = "Due to some internal server, we are unable to process your request. Please try again.";
                request_meeting_error.style.color = 'red';
            }
        } else if (this.readyState == 4) {
            // $("#request_meeting_modal").modal("hide");
            request_meeting_error.innerHTML = "Due to some network issue, we are unable to process your request. Please try again.";
            request_meeting_error.style.color = 'red';
        }
    }
    xhttp.send(params);
}


function check_meeting_status(session_id) {
    request_params = {
        "session_id": session_id
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/check-meeting-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                var request_meeting_error = document.getElementById("request_meeting_error");
                if (response.is_meeting_allowed == true) {

                    // checking if video call as PiP is enabled
                    if(check_voip_video_meeting_enabled()) {

                        toggle_voip_ringing_sound(false);
                        $("#request_meeting_modal").modal("hide");
                        set_easyassist_cookie("is_cobrowse_meeting_active", COBROWSE_SESSION_ID);
                        show_cobrowse_meeting_option();

                        request_meeting_error.innerHTML = "";
                        request_meeting_error.style.color = 'green';
                        let html = document.getElementById("request_meeting_button");
                        let button = '<button class="btn btn-secondary" type="button" data-dismiss="modal">Close</button>\
                            <button class="btn btn-primary" id="request_button" type="button" onclick="request_for_meeting(\'' + session_id + '\')">Request</button>';
                        html.innerHTML = button;

                    } else if(check_voip_enabled()) {

                        toggle_voip_ringing_sound(false);
                        $("#request_meeting_modal").modal("hide");
                        set_easyassist_cookie("is_cobrowse_meeting_active", COBROWSE_SESSION_ID);
                        voip_connect_with_client();

                        request_meeting_error.innerHTML = "";
                        request_meeting_error.style.color = 'green';
                        let html = document.getElementById("request_meeting_button");
                        let button = '<button class="btn btn-success" type="button" onclick="voip_connect_with_client(\'' + session_id + '\')">Connect</button>\
                            <button class="btn btn-primary" id="request_button" type="button" onclick="request_for_meeting(\'' + session_id + '\')">Resend Request</button>';
                        html.innerHTML = button;
                        document.getElementById("voip-cross-icon").style.display = "";
                        document.getElementById("voip-calling-icon").style.display = 'none';
                        document.getElementById("voip-call-icon").style.display = 'block';

                    } else {

                        set_easyassist_cookie("is_cobrowse_meeting_active", COBROWSE_SESSION_ID);
                        request_meeting_error.innerHTML = "Meeting request has been accepted by the customer. Please click on 'Connect' to join the meeting."
                        request_meeting_error.style.color = 'green';
                        let html = document.getElementById("request_meeting_button");
                        let button = '<button class="btn btn-success" type="button" onclick="connect_with_client(\'' + session_id + '\')">Connect</button>\
                            <button class="btn btn-primary" id="request_button" type="button" onclick="request_for_meeting(\'' + session_id + '\')">Resend Request</button>';
                        html.innerHTML = button
                        connect_with_client(session_id);

                    }
                    auto_msg_popup_on_client_call_declined = false;
                    if(check_meeting_status_interval != null) {
                        clearInterval(check_meeting_status_interval);
                        check_meeting_status_interval = null;
                    }
                } else if (response.is_meeting_allowed == false) {
                    if(response.is_client_answer == true){
                        if(check_voip_enabled()) {

                            toggle_voip_ringing_sound(false);
                            toggle_voip_beep_sound(true);
                            document.getElementById("voip-calling-icon").style.display = 'none';
                            document.getElementById("voip-call-icon").style.display = 'block';
                            if(auto_msg_popup_on_client_call_declined == true) {
                                show_easyassist_toast("Customer declined the call");
                                allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow
                                allincall_chat_window.postMessage(JSON.stringify({
                                    "id": "agent_name",
                                    "name": window.AGENT_NAME,
                                    "session_id": COBROWSE_SESSION_ID,
                                    "agent_connect_message": VOIP_DECLINE_MEETING_MESSAGE
                                }), window.location.protocol + "//" + window.location.host);
                                open_livechat_agent_window();
                            } else {
                                if(request_meeting_error.offsetParent == null) {
                                    show_easyassist_toast("Customer declined the call");
                                }
                                request_meeting_error.innerHTML = "The voice call request has been rejected by the customer"
                                request_meeting_error.style.color = 'red';
                                let html = document.getElementById("request_meeting_button");
                                let button = '<button class="btn btn-secondary" type="button" data-dismiss="modal">Close</button>\
                                    <button class="btn btn-primary" id="request_button" type="button" onclick="request_for_meeting(\'' + session_id + '\')">Resend Request</button>';
                                html.innerHTML = button
                                document.getElementById("voip-cross-icon").style.display = "none";
                            }

                        } else if(check_voip_video_meeting_enabled()) {

                            toggle_voip_ringing_sound(false);
                            toggle_voip_beep_sound(true);
                            if(auto_msg_popup_on_client_call_declined == true) {
                                show_easyassist_toast("Customer declined the call");
                                allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow
                                allincall_chat_window.postMessage(JSON.stringify({
                                    "id": "agent_name",
                                    "name": window.AGENT_NAME,
                                    "session_id": COBROWSE_SESSION_ID,
                                    "agent_connect_message": VOIP_DECLINE_MEETING_MESSAGE
                                }), window.location.protocol + "//" + window.location.host);
                                open_livechat_agent_window();
                            } else {
                                if(request_meeting_error.offsetParent == null) {
                                    show_easyassist_toast("Customer declined the call");
                                }
                                request_meeting_error.innerHTML = "Meeting request has been rejected by customer."
                                request_meeting_error.style.color = 'red';
                                let html = document.getElementById("request_meeting_button");
                                let button = '<button class="btn btn-secondary" type="button" data-dismiss="modal">Close</button>\
                                    <button class="btn btn-primary" id="request_button" type="button" onclick="request_for_meeting(\'' + session_id + '\')">Resend Request</button>';
                                html.innerHTML = button
                            }

                        } else {

                            request_meeting_error.innerHTML = "Meeting request has been rejected by customer."
                            request_meeting_error.style.color = 'red';
                            let html = document.getElementById("request_meeting_button");
                            let button = '<button class="btn btn-secondary" type="button" data-dismiss="modal">Close</button>\
                                <button class="btn btn-primary" id="request_button" type="button" onclick="request_for_meeting(\'' + session_id + '\')">Resend Request</button>';
                            html.innerHTML = button;

                        }
                        auto_msg_popup_on_client_call_declined = false;
                        if(check_meeting_status_interval != null) {
                            clearInterval(check_meeting_status_interval);
                            check_meeting_status_interval = null;
                        }
                    }
                }
            }
        } else if (this.readyState == 4) {
            request_meeting_error.innerHTML = "Due to some network issue, we are unable to process your request. Please refresh the page and try again."
            request_meeting_error.style.color = 'red';
        }
    }
    xhttp.send(params);
}

function show_cobrowse_meeting_option() {
    if(check_voip_enabled()) {
        return;
    }
    // the below code is used to initialize the PiP iFrame for the call. It also first makes the video call icon present in the side menu options to disappear.
    let is_cobrowse_meeting_active = get_easyassist_cookie("is_cobrowse_meeting_active");
    if(is_cobrowse_meeting_active == COBROWSE_SESSION_ID) {
        if(document.getElementById("cobrowse-voip-container").style.display == 'none') {
            send_agent_meeting_joined_over_socket();
            try {
                if(get_easyassist_cookie("is_meeting_initiate_by_customer") == "true"){
                    if(IS_MOBILE == "True") {
                        document.getElementById("request-cobrowsing-meeting-btn").parentNode.parentNode.style.display = "none";
                    } else {
                        document.getElementById("request-cobrowsing-meeting-btn").style.display = 'none';
                    }
                }
                if(IS_ADMIN_AGENT == "FALSE") {
                    hide_side_nav_call_icon();
                }
            } catch(err) {}
            document.getElementById("easyassist-voip-loader").style.display = 'flex';
            document.getElementById("cobrowse-voip-container").style.display = '';
            var cobrowsing_meeting_iframe = document.getElementById("cobrowse-meeting-iframe-container").children[0];
            var meeting_url = window.location.protocol + "//" + window.location.host + "/easy-assist/agent-cobrowse-meeting/" + COBROWSE_SESSION_ID;
            cobrowsing_meeting_iframe.src = meeting_url;
        }
    } 
}

function toggle_meeting_iframe_visibility() {
    var meeting_iframe_container = document.getElementById("cobrowse-meeting-iframe-container");
    if(meeting_iframe_container.style.display == 'none') {
        meeting_iframe_container.style.display = 'block';
    } else {
        meeting_iframe_container.style.display = 'none';
    }
}

function toggle_agent_voice(element, status) {
    try {
        var cobrowse_meeting_iframe = document.getElementById("cobrowse-meeting-iframe-container").children[0];
        cobrowse_meeting_window = cobrowse_meeting_iframe.contentWindow;
        cobrowse_meeting_window.postMessage(JSON.stringify({
            "message": "toggle_voice",
            "name": window.CLIENT_NAME,
            "status": status,
        }), window.location.protocol + "//" + window.location.host);
    } catch(err) {
        console.log(err);
    }
}

function toggle_agent_video(element, status) {
    try {
        var cobrowse_meeting_iframe = document.getElementById("cobrowse-meeting-iframe-container").children[0];
        cobrowse_meeting_window = cobrowse_meeting_iframe.contentWindow;
        cobrowse_meeting_window.postMessage(JSON.stringify({
            "message": "toggle_video",
            "name": window.CLIENT_NAME,
            "status": status,
        }), window.location.protocol + "//" + window.location.host);
        var video_element = document.getElementById("cobrowse-meeting-video-element");
        if(status == true) {
            document.getElementById("cobrowse-meeting-iframe-container").style.display = 'flex';
            navigator.mediaDevices.getUserMedia({ video: true })
            .then((stream_local) => {
                captured_video_stream = stream_local;
                video_element.srcObject = stream_local;
                video_element.parentNode.style.display = 'block';
            })
            .catch(function() {
                video_element.srcObject = null;
                video_element.parentNode.style.display = 'none';
            });
        } else {
            video_element.srcObject = null;
            video_element.parentNode.style.display = 'none';
            try {
                captured_video_stream.getTracks().forEach(function(track) {
                    track.stop();
                });
            } catch(err) {}
        }
    } catch(err) {
        console.log(err)
    }
}

function end_cobrowse_video_meet(auto_end_meeting=false) {
    try {
        if(check_voip_enabled()) {
            return;
        }

        let is_cobrowse_meeting_active = get_easyassist_cookie("is_cobrowse_meeting_active");
        if(is_cobrowse_meeting_active != COBROWSE_SESSION_ID) {
            return;
        }
        document.getElementById("cobrowse-meeting-iframe-container").style.display = 'none';
        var cobrowse_meeting_iframe = document.getElementById("cobrowse-meeting-iframe-container").children[0];
        cobrowse_meeting_window = cobrowse_meeting_iframe.contentWindow;
        cobrowse_meeting_window.postMessage(JSON.stringify({
            "message": "end_meeting",
            "name": window.CLIENT_NAME
        }), window.location.protocol + "//" + window.location.host);
        if(IS_ADMIN_AGENT == "True") {
            send_end_meeting_messsage_over_socket(auto_end_meeting);
        }
    } catch(err) {
        console.log(err);
    }
}

function reset_voip_meeting() {
    set_easyassist_cookie("is_cobrowse_meeting_active", "");
    delete_easyassist_cookie("is_meeting_audio_muted");
    delete_easyassist_cookie("is_customer_voip_meeting_joined");
    delete_easyassist_cookie("is_meeting_initiate_by_customer");
    send_join_customer_voice_call_meeting_btn_hide_request();
    try {
        if(IS_MOBILE == "True") {
            document.getElementById("request-cobrowsing-meeting-btn").parentNode.parentNode.style.display = "flex";
        } else {
            document.getElementById("request-cobrowsing-meeting-btn").style.display = 'inherit';
        }
    } catch(err) {}

    document.getElementById("cobrowse-meeting-iframe-container").style.display = 'none';
    document.getElementById("cobrowse-voip-container").style.display = 'none';
    document.getElementById("agent-meeting-mic-on-btn").style.display = 'none';
    document.getElementById("agent-meeting-mic-off-btn").style.display = '';
    if(check_voip_video_meeting_enabled()) {
        document.getElementById("agent-meeting-video-on-btn").style.display = 'none';
        document.getElementById("agent-meeting-video-off-btn").style.display = '';
        try {
            captured_video_stream.getTracks().forEach(function(track) {
                track.stop();
            });
        } catch(err) {}
    }
    setTimeout(function() {
        document.getElementById("cobrowse-meeting-iframe-container").children[0].src = "";
    }, 2000);
}

function send_end_meeting_messsage_over_socket(auto_end_meeting) {
    json_string = JSON.stringify({
        "type": "end_voip_meeting",
        "auto_end_meeting": auto_end_meeting,
        "agent_name": window.AGENT_NAME,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function send_agent_meeting_joined_over_socket() {
    json_string = JSON.stringify({
        "type": "voip_meeting_joined",
        "agent_id": AGENT_UNIQUE_ID,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function send_voip_meeting_ready_over_socket() {
    json_string = JSON.stringify({
        "type": "voip_meeting_ready",
        "agent_id": AGENT_UNIQUE_ID,
        "agent_name": window.AGENT_NAME,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

/***************** EasyAssist Custom Select ***********************/

class EasyassistCustomSelect {
    constructor(selector, placeholder, background_color) {
        this.placeholder = placeholder;
        this.background_color = background_color;

        var select_element = document.querySelector(selector);
        var selected_list_class = "easyassist-option-selected";
        var show_option_container_class = "easyassist-dropdown-show";
        var custom_dropdown_selected_option = "";
        var dropdown_option_selected = false;

        var custom_dropdown_wrapper = "";
        var custom_dropdown_option_container = "";
        var custom_dropdown_selected_option_wrapper = "";

        // Create elements
        custom_dropdown_wrapper = create_element('div', 'easyassist-custom-dropdown-container');
        custom_dropdown_option_container = create_element('ul', 'easyassist-custom-dropdown-option-container');
        custom_dropdown_selected_option_wrapper = create_element('div', 'easyassist-dropdown-selected');
        // select_element.wrap(custom_dropdown_wrapper);

        select_element.parentNode.prepend(custom_dropdown_wrapper);
        custom_dropdown_wrapper.appendChild(select_element)

        if(this.placeholder){
            select_element.selectedIndex = -1;
        }

        var select_option_records = get_custom_dropdown_option_html();
        dropdown_option_selected = select_option_records.dropdown_option_selected;
        custom_dropdown_selected_option = select_option_records.dropdown_selected_option;

        custom_dropdown_option_container.innerHTML = select_option_records.option_html;
        select_element.insertAdjacentElement('afterend', custom_dropdown_option_container)

        if(dropdown_option_selected) {
            custom_dropdown_selected_option_wrapper.innerHTML = custom_dropdown_selected_option;
        } else if(this.placeholder) { 
            custom_dropdown_selected_option_wrapper.innerHTML = this.placeholder;
        } else {
            custom_dropdown_selected_option_wrapper.innerHTML = custom_dropdown_selected_option;
        }

        select_element.insertAdjacentElement('afterend', custom_dropdown_selected_option_wrapper);

        // Add eventlistener
        document.addEventListener('click', function(e) {
            if(e.target == custom_dropdown_selected_option_wrapper) {
                custom_dropdown_option_container.classList.toggle(show_option_container_class);
            } else {
                custom_dropdown_option_container.classList.remove(show_option_container_class);
            }
        });

        custom_dropdown_add_event_listener();

        var _this = this;
        Object.defineProperty(select_element, 'reinitialize', {
            value: function() {
                select_option_records = get_custom_dropdown_option_html();
                dropdown_option_selected = select_option_records.dropdown_option_selected;
                custom_dropdown_selected_option = select_option_records.dropdown_selected_option;

                custom_dropdown_option_container.innerHTML = select_option_records.option_html;

                if(dropdown_option_selected) {
                    custom_dropdown_selected_option_wrapper.innerHTML = custom_dropdown_selected_option;
                } else if(_this.placeholder) { 
                    custom_dropdown_selected_option_wrapper.innerHTML = _this.placeholder;
                } else {
                    custom_dropdown_selected_option_wrapper.innerHTML = custom_dropdown_selected_option;
                }
                custom_dropdown_add_event_listener();
            }
        });

        function reset_dropdown() {
            for(let idx = 0; idx < custom_dropdown_option_container.children.length; idx ++) {
                custom_dropdown_option_container.children[idx].classList.remove(selected_list_class);
                custom_dropdown_option_container.children[idx].style.removeProperty('background-color');
            }
        }

        function create_element(html_tag, css_class) {
            let html_element = document.createElement(html_tag);
            html_element.className = css_class;
            return html_element;
        }

        function get_custom_dropdown_option_html() {
            let custom_dropdown_options = "";
            let dropdown_option_selected = false;
            let custom_dropdown_selected_option = "";

            for(let idx = 0; idx < select_element.children.length; idx ++) {
                let option_el = select_element.children[idx];
                let option_text = option_el.text.trim();
                let option_value = option_el.value;

                if(option_el.selected) {
                    dropdown_option_selected = true;
                    custom_dropdown_selected_option = option_text;
                    custom_dropdown_options += [
                        '<li  class="' + selected_list_class + '">',
                            '<span>' + option_text + '</span>',
                            '<input type="hidden" value="' + option_value + '">',
                        '</li>',
                    ].join('');
                } else {
                    custom_dropdown_options += [
                        '<li>',
                            '<span>' + option_text + '</span>',
                            '<input type="hidden" value="' + option_value + '">',
                        '</li>',
                    ].join('');
                }
            }
            return {
                option_html: custom_dropdown_options,
                dropdown_option_selected: dropdown_option_selected,
                dropdown_selected_option: custom_dropdown_selected_option,
            };
        }

        function custom_dropdown_add_event_listener() {
            for(let idx = 0; idx < custom_dropdown_option_container.children.length; idx ++) {
                let li_element = custom_dropdown_option_container.children[idx];
                li_element.addEventListener('click', function(e) {
                    let selected_option_text = this.innerHTML;
                    reset_dropdown();
                    li_element.classList.add(selected_list_class);
                    li_element.style.setProperty('background-color', background_color, 'important');
                    custom_dropdown_selected_option_wrapper.innerHTML = selected_option_text;
                    custom_dropdown_option_container.classList.toggle(show_option_container_class);

                    // Update selecte drodown
                    let option_value = li_element.children[1].value;
                    select_element.value = option_value;
                    var change_event = new Event('change');
                    select_element.dispatchEvent(change_event);
                });

                li_element.addEventListener('mouseover', function(e) {
                    li_element.style.setProperty('background-color', background_color, 'important');
                });

                li_element.addEventListener('mouseout', function(e) {
                    if(!li_element.classList.contains(selected_list_class)) {
                        li_element.style.removeProperty('background-color');
                    }
                })
            }
        }
    }
}

function find_light_color(color, percent, opacity=0.4) {
    var R = parseInt(color.substring(1,3),16);
    var G = parseInt(color.substring(3,5),16);
    var B = parseInt(color.substring(5,7),16);

    R = parseInt(R * (100 + percent) / 100);
    G = parseInt(G * (100 + percent) / 100);
    B = parseInt(B * (100 + percent) / 100);

    R = (R<255)?R:255;  
    G = (G<255)?G:255;  
    B = (B<255)?B:255;  

    /*
        var RR = ((R.toString(16).length==1)?"0"+R.toString(16):R.toString(16));
        var GG = ((G.toString(16).length==1)?"0"+G.toString(16):G.toString(16));
        var BB = ((B.toString(16).length==1)?"0"+B.toString(16):B.toString(16));
    */

    var rgba_color = "rgba(" + R + "," + G + "," + B + "," + opacity.toString() + ")";
    return rgba_color;
}

function toggle_voip_ringing_sound(play_music) {
    try {
        var audio_player = document.getElementById("voip-ring-sound");
        if(!audio_player) {
            return;
        }
        if(play_music) {
            audio_player.play();
        } else {
            audio_player.pause();
        }
    } catch(err) {}
}

function toggle_voip_beep_sound(play_music) {
    try {
        var audio_player = document.getElementById("voip-beep-sound");
        if(!audio_player) {
            return;
        }
        if(play_music) {
            audio_player.play();
        } else {
            audio_player.pause();
        }
    } catch(err) {}
}

function show_invited_agent_voip_connect_modal() {
    if(is_meeting_tab_open()) {
        return;
    }
    document.getElementById("voip-initiated-agent-name").innerHTML = "Agent " + voip_meeting_initiated_agent;
    $('#invited_agent_voip_meeting_connect_modal').modal('show');
}

function show_invited_agent_customer_voip_connect_modal() {

    if(is_meeting_tab_open()) {
        return;
    }
    var customer_req_meeting_modal = document.getElementById("customer_request_meeting_modal_invited_agent");
    if(customer_req_meeting_modal && customer_req_meeting_modal.style.display != "none") {
        $(customer_req_meeting_modal).modal("hide");
        customer_req_meeting_modal.style.display == "none";
    }
    document.getElementById("customer-call-voip-initiated-agent-name").innerHTML = "Agent " + voip_meeting_initiated_agent;
    $('#invited_agent_customer_voip_meeting_connect_modal').modal('show');
}

function is_meeting_tab_open() {
    var local_storage_obj = get_easyassist_current_session_local_storage_obj();
    if(local_storage_obj != null) {

        if(check_voip_video_meeting_enabled() && local_storage_obj.hasOwnProperty("is_video_pip_meeting_open")) {
            if (local_storage_obj["is_video_pip_meeting_open"] == "true") {
                return true;
            }
        } else if(check_voip_enabled() && local_storage_obj.hasOwnProperty("is_voice_meeting_tab_open")) {
            if (local_storage_obj["is_voice_meeting_tab_open"] == "true") {
                return true;
            }
        } else if(check_video_calling_enabled() && local_storage_obj.hasOwnProperty("is_video_meeting_tab_open")) {
            if (local_storage_obj["is_video_meeting_tab_open"] == "true") {
                return true;
            }
        }
    }
    return false;
}

function show_side_nav_call_icon() {

    if(is_meeting_tab_open()) {
        hide_side_nav_call_icon();
        return;
    }

    if(IS_MOBILE == "True") {
        document.getElementById("request-cobrowsing-meeting-btn-invited-agent").parentNode.parentNode.style.display = "flex";
    } else {
        document.getElementById("request-cobrowsing-meeting-btn-invited-agent").style.display = "inherit";
    }
}

function hide_side_nav_call_icon() {
    var local_storage_obj = get_easyassist_current_session_local_storage_obj();
    if(local_storage_obj != null && local_storage_obj.hasOwnProperty("is_ok_button_clicked_invited_agent")) {
        if(local_storage_obj["is_ok_button_clicked_invited_agent"] == "true") {
            return;
        }
    }

    if(IS_MOBILE == "True") {
        document.getElementById("request-cobrowsing-meeting-btn-invited-agent").parentNode.parentNode.style.display = "none";
    } else {
        if(document.getElementById("request-cobrowsing-meeting-btn-invited-agent"))
            document.getElementById("request-cobrowsing-meeting-btn-invited-agent").style.display = "none";
    }
}

function open_call_joining_modal() {
    check_voip_meeting_active_over_socket();
    setTimeout(() => {
        var local_storage_obj = get_easyassist_current_session_local_storage_obj();
        if(local_storage_obj != null && local_storage_obj.hasOwnProperty("is_call_ongoing_invited_agent")) {
            if (local_storage_obj["is_call_ongoing_invited_agent"] == "true") {
                show_invited_agent_voip_connect_modal();
            } else {
                reset_call_modal_text();
                $("#request_meeting_modal_invited_agent").modal("show");
            }
        } else {
            // show normal modal
            reset_call_modal_text();
            $("#request_meeting_modal_invited_agent").modal("show");
        }
    }, 300);
}

function customer_init_open_call_joining_modal() {
    check_voip_meeting_active_over_socket();
    setTimeout(() => {
        var local_storage_obj = get_easyassist_current_session_local_storage_obj();
        if(local_storage_obj != null && local_storage_obj.hasOwnProperty("is_call_ongoing_invited_agent")) {
            if (local_storage_obj["is_call_ongoing_invited_agent"] == "true") {
                show_invited_agent_customer_voip_connect_modal();
            } else {
                reset_customer_init_call_modal_text();
                document.getElementById("customer_request_meeting_modal_invited_agent").style.display = "block";
            }
        } else {
            // show normal modal
            reset_customer_init_call_modal_text();
            document.getElementById("customer_request_meeting_modal_invited_agent").style.display = "block";
        }
    }, 300);
}

function reset_call_modal_text() {
    if(check_voip_video_meeting_enabled()) {
        $('#request_meeting_modal_invited_agent .modal-text').text('Would you like to connect on a video call?');
    } else if (check_voip_enabled()) {
        $('#request_meeting_modal_invited_agent .modal-text').text('Would you like to connect on a voice call?');
    } else {
        $('#request_meeting_modal_invited_agent .modal-text').text('Would you like to connect on a video call?');
    }
    $('#request_meeting_modal_invited_agent .modal-footer').html('<button class="btn btn-secondary" type="button" data-dismiss="modal">No</button>' + 
        '<button class="btn btn-primary" id="request_button" type="button" onclick="connect_voip_meeting()">Yes</button>');
}

function connect_voip_meeting(is_check_required=true) {

    if(!is_check_required) {
        launch_call_for_invited_agent();
        return;
    }

    request_params = {
        "session_id": COBROWSE_SESSION_ID
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/check-meeting-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if(response.status == 301) {
                $('#request_meeting_modal_invited_agent .modal-text').text('The call is not accepted by the customer yet, You can join the call once the customer accepts it.');
                $('#request_meeting_modal_invited_agent .modal-footer').html('<button class="btn btn-primary" type="button" data-dismiss="modal" onclick="ok_button_handler()">OK</button>');
            } else if (response.status == 200) {
                if(response.is_meeting_allowed == false){
                    set_easyassist_current_session_local_storage_obj("is_ok_button_clicked_invited_agent", "false");
                    if(check_voip_video_meeting_enabled()) {
                        $('#request_meeting_modal_invited_agent .modal-text').text('Customer has denied the video call, request you to wait till customer accepts it.');
                    } else if (check_voip_enabled()) {
                        $('#request_meeting_modal_invited_agent .modal-text').text('Customer has denied the voice call, request you to wait till customer accepts it');
                    } else {
                        $('#request_meeting_modal_invited_agent .modal-text').text('Customer has denied the video call, request you to wait till customer accepts it.');
                    }
                    $('#request_meeting_modal_invited_agent .modal-footer').html('<button class="btn btn-primary" type="button" data-dismiss="modal">OK</button>');
                } else {
                    launch_call_for_invited_agent();
                }
            }
        } 
    }
    xhttp.send(params);
}

function launch_call_for_invited_agent() {
    set_easyassist_current_session_local_storage_obj("is_ok_button_clicked_invited_agent", "false");
    $("#request_meeting_modal_invited_agent").modal("hide");
    reset_call_modal_text();
    hide_side_nav_call_icon();
    set_easyassist_cookie("is_cobrowse_meeting_active", COBROWSE_SESSION_ID);
    if(check_voip_video_meeting_enabled()) {
        show_cobrowse_meeting_option();
    } else if (check_voip_enabled()) {
        voip_connect_with_client();
    } else {
        connect_with_client(COBROWSE_SESSION_ID);
    }
    hide_invited_agent_voip_connect_modal();
}

function ok_button_handler() {
    set_easyassist_current_session_local_storage_obj("is_ok_button_clicked_invited_agent", "true");
}

function customer_init_ok_button_handler() {
    set_easyassist_current_session_local_storage_obj("customer_init_is_ok_button_clicked_invited_agent", "true");
}

function hide_invited_agent_voip_connect_modal() {
    $('#invited_agent_voip_meeting_connect_modal').modal('hide');
}

function easyassist_send_customer_message(message) {

    json_string = JSON.stringify({
        "type": "agent_message",
        "message": message
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function send_edit_access_status_over_socket() {

    json_string = JSON.stringify({
        "type": "edit_access_granted",
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function send_edit_access_revoked_over_socket() {

    json_string = JSON.stringify({
        "type": "edit_access_revoked",
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function easyassist_send_agent_low_bandwidth_message(status) {
    
    $('#check_for_internet_modal').modal('hide');

    if(check_screen_sharing_cobrowsing_enabled()) {
        return;
    }

    if(ENABLE_LOW_BANDWIDTH_COBROWSING != "True") {
        return;
    }

    json_string = JSON.stringify({
        "type": "agent_low_bandwidth_html_request",
        "is_agent_weak_connection": status,
        "is_html_needed": true,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");

    AGENT_WEAK_CONNECTION_DETECTED = status;

    easyassist_update_switch_cobrowsing_mode_btn();
}

function easyassist_send_agent_normal_mode_cobrowsing_message() {

    $('#normal_mode_cobrowsing_toggle_modal').modal('hide');

    json_string = JSON.stringify({
        "type": "agent_low_bandwidth_html_request",
        "is_html_needed": true,
        "is_agent_weak_connection": false,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");

    AGENT_WEAK_CONNECTION_DETECTED = false;

    easyassist_update_switch_cobrowsing_mode_btn();
}

function easyassist_update_switch_cobrowsing_mode_btn() {
    try {
        if(document.getElementById("lite_mode_switch_btn") == undefined) {
            return;
        }

        if(IS_MOBILE == "True") {
            if(AGENT_WEAK_CONNECTION_DETECTED == true) {
                document.getElementById("lite_mode_switch_btn").style.display = "none";
                document.getElementById("normal_mode_swtich_btn").style.display = "";
            } else {
                document.getElementById("lite_mode_switch_btn").style.display = "";
                document.getElementById("normal_mode_swtich_btn").style.display = "none";
            }
        } else {
            if(AGENT_WEAK_CONNECTION_DETECTED == true) {
                document.getElementById("lite_mode_switch_btn").style.display = "none";
                document.getElementById("normal_mode_swtich_btn").style.display = "flex";
            } else {
                document.getElementById("lite_mode_switch_btn").style.display = "flex";
                document.getElementById("normal_mode_swtich_btn").style.display = "none";
            }
        }
    } catch(err) {
        console.log(err);
    }
}

function easyassist_send_client_low_bandwidth_message(status) {

    $('#client_internet_connection_weak_message_modal').modal('hide');

    if(check_screen_sharing_cobrowsing_enabled()) {
        return;
    }

    if(ENABLE_LOW_BANDWIDTH_COBROWSING != "True") {
        return;
    }

    if(status == false) {
        return;
    }

    json_string = JSON.stringify({
        "type": "client_low_bandwidth_html_request",
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function easyassist_send_agent_weak_connection_message(status) {

    json_string = JSON.stringify({
        "type": "agent_weak_connection",
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function is_landscape_view() {
    return (window.innerHeight > window.innerWidth);
}

function show_weak_internet_connectivity_modal() {
    $('#client_internet_connection_weak_message_modal').modal('hide');
    $('#check_for_internet_modal').modal('show');
}

function show_client_weak_internet_connectio_modal() {
    $("#check_for_internet_modal").modal("hide");
    $("#client_internet_connection_weak_message_modal").modal("show");
}

function show_client_disconnect_modal() {
    if(session_has_ended == true) {
        return;
    }

    $('#client_internet_connection_weak_message_modal').modal('hide');
    $("#check_for_internet_modal").modal("hide");
    $("#client_disconnected_message_modal").modal("show");
}

function easyassist_check_weak_connection_enabled() {
    if(ENABLE_LOW_BANDWIDTH_COBROWSING == "True" && AGENT_WEAK_CONNECTION_DETECTED) {
        return true;
    }
    return false;
}

function easyassist_show_function_fail_modal(code=EASYASSIST_FUNCTION_FAIL_DEFAULT_CODE, message=EASYASSIST_FUNCTION_FAIL_DEFAULT_MESSAGE) {
    var current_time = Date.now();
    var difference = (current_time - easyassist_function_fail_time) / 1000;

    if(difference < 30) {
        return;
    } else if(difference >= 300) {
        easyassist_function_fail_count = 0;
    }

    if(message == null) {
        message = EASYASSIST_FUNCTION_FAIL_DEFAULT_MESSAGE;
    }

    if(easyassist_function_fail_count <= 6) {
        if(code != null) {
            message = message + " [" + code + "]"
        }
        document.getElementById("easyassist_function_fail_message").innerHTML = message;
        easyassist_display_function_fail_modal();
    }

    easyassist_function_fail_count++;
    easyassist_function_fail_time = Date.now();
}

function easyassist_display_function_fail_modal(){
    $("#easyassist_function_fail_modal").modal("show");
}
function easyassist_hide_function_fail_modal() {
    $("#easyassist_function_fail_modal").modal("hide");
}

function initialize_empty_iframe(iframe=null) {

    if(!iframe) {
        EASYASSIST_IFRAME_ID_GLOBAL += 1;
        iframe = document.createElement('iframe');
        iframe.id = "easyassist-iframe-" + EASYASSIST_IFRAME_ID_GLOBAL;
        iframe.src = "";
        iframe.hidden = true;
        iframe.setAttribute("class", "client-data-frame");
        framesContainer.appendChild(iframe);
    }

    var iframe_doc = iframe.contentDocument;

    iframe_doc.open();
    iframe_doc.write("<!DOCTYPE html>");
    iframe_doc.write("<html>");
    iframe_doc.write("<head></head>");
    iframe_doc.write("<body>this is the iframe</body>");
    iframe_doc.write("</html>");
    iframe_doc.close();

    return iframe;
}

function initialize_easyassist_iframe(dataset, client_page_id) {

    var iframe = initialize_empty_iframe();

    var iframe_doc = iframe.contentDocument;

    while (iframe_doc.firstChild) {
        iframe_doc.removeChild(iframe_doc.firstChild);
    }

    easyassist_create_iframe_mirror(iframe, dataset, client_page_id, false);
}

function initialize_easyassist_sub_iframe(iframe_id, dataset, client_page_id) {

    var parent_iframe = framesContainer.children[0];
    var iframe = parent_iframe.contentWindow.document.querySelector("[easyassist-iframe-id='" + iframe_id + "']");
    if(!iframe) {
        return;
    }

    iframe = initialize_empty_iframe(iframe);

    var iframe_doc = iframe.contentDocument;

    while (iframe_doc.firstChild) {
        iframe_doc.removeChild(iframe_doc.firstChild);
    }

    easyassist_create_iframe_mirror(iframe, dataset, client_page_id, true, iframe_id)
}

function easyassist_create_iframe_mirror(iframe, dataset, client_page_id, is_child_iframe, iframe_id=null) {

    var iframe_doc = iframe.contentDocument;

    let tree_mirror_instance = new EasyAssistTreeMirror(iframe_doc, {
        createElement: function(tagName) {
          if (tagName == 'SCRIPT') {
            let node = iframe_doc.createElement('NO-SCRIPT');
            node.style.display = 'none';
            return node;
          }

          if (tagName == 'HEAD') {
            let node = iframe_doc.createElement('HEAD');
            node.appendChild(iframe_doc.createElement('BASE'));
            node.firstChild.href = dataset.base;

            let style_node = iframe_doc.createElement("STYLE");
            style_node.id = "easyassist-custom-style";
            style_node.innerHTML = dataset.css_text;
            node.appendChild(style_node);

            // console.log(dataset.css_text);
            return node;
          }
        },

        set_element_value: function(element, element_value) {
            try {
                if(element_value == null || element_value == undefined) {
                    return;
                }

                if(element_value.length != 2 || element_value[1] == null) {
                    return;
                }

                var tag_name = element.tagName;

                if(tag_name != "INPUT" && tag_name != "SELECT" && tag_name != "TEXTAREA") {
                    return;
                }

                var is_obfuscated_element = element_value[0];
                element_value = element_value[1];

                if(tag_name == "INPUT") {
                    var element_type = element.getAttribute("type");
                    if(element_type == "checkbox" || element_type == "radio") {
                        element.checked = element_value;
                    } else if(element_type == "number") {
                        element.setAttribute("type", "text");
                        element.value = element_value;
                    } else if(element_type == "date" && is_obfuscated_element){
                        element.value = element_value;
                        element.setAttribute("type", "text");
                    } else {
                        element.value = element_value;
                    }
                } else if(tag_name == "SELECT") {
                    if(is_obfuscated_element) {
                        var obfuscated_value = "******";
                        var obfuscated_option = document.createElement("option");
                        obfuscated_option.value = obfuscated_value
                        obfuscated_option.innerHTML = obfuscated_value    
                        element.appendChild(obfuscated_option);
                        element.value = obfuscated_value;
                    } else {
                        element.value = element_value;
                    }
                } else {
                    element.value = element_value;
                }
            } catch(err) {
                console.log(err);
            }
        },

        props: {
            iframe: iframe,
            base: dataset.base,
            render_frame: function() {
                if(is_child_iframe) {
                    return;
                }
                renderFrame(dataset, client_page_id);
            },

            add_event_listeners: function() {
                easyassist_iframe_add_event_listeners(iframe);
            },

            update_edit_access: easyassist_update_edit_access,
        },

        setAttribute: function(node, name, value) {
            try {
                if(check_iframe_cobrowsing_enabled() && is_child_iframe == false) {
                    if(node.tagName == "IFRAME" && name == "src") {
                        value = "";
                    }
                }

                node.setAttribute(name, value);
                return true;
            } catch(err) {
                return false;
            }
        },
    });

    if(is_child_iframe) {
        easyassist_iframe_tree_mirror[iframe_id] = tree_mirror_instance;
    } else {
        easyassist_tree_mirror = tree_mirror_instance;
    }
}

function easyassist_update_styled_component_css(css_text) {
    try {
        if(css_text != "") {
            var iframe_doc = document.getElementById("frames-container").children[0].contentDocument;
            iframe_doc.getElementById("easyassist-custom-style").innerHTML = css_text;
        }
    } catch(err) {
        console.log("easyassist_update_styled_component_css: ", err);
    }
}

function easyassist_get_element_from_easyassist_id(element_id, easyassist_iframe_id=null) {
    var element = null;

    try {
        if(easyassist_check_weak_connection_enabled()) {
            var iframe = framesContainer.children[0];
            element = iframe.contentWindow.document.querySelector("[easyassist-element-id='" + element_id + "']");
        } else {
            if(easyassist_iframe_id == null) {
                element = easyassist_tree_mirror.idMap[element_id];
            } else {
                element = easyassist_iframe_tree_mirror[easyassist_iframe_id].idMap[element_id];
            }
        }
    } catch(err) {
        console.log("easyassist_get_element_from_easyassist_id: ", err);
    }

    return element;
}

function easyassist_get_easyassist_id_from_element(element) {
    var element_id = null;

    try {
        if(easyassist_check_weak_connection_enabled()) {
            element_id = element.getAttribute("easyassist-element-id");
        } else {
            element_id = element.easyassist_element_id;
        }
    } catch(err) {
        console.log("easyassist_get_easyassist_id_from_element: ", err);
    }

    return element_id;
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

    var iframe = document.getElementById("frames-container").children[0];

    var body = iframe.contentDocument.body,
        doc_html = iframe.contentDocument.documentElement;

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
            "client_websocket_readystate": client_websocket.readyState,
            "sync_utils_client_websocket_readystate": sync_utils_client_websocket.readyState,
            "cobrowse_session_id": window.COBROWSE_SESSION_ID,
            "allow_language_support": window.ALLOW_LANGUAGE_SUPPORT,
            "choose_product_category": window.CHOOSE_PRODUCT_CATEGORY,
            "allow_screensharing_cobrowse": window.ALLOW_SCREENSHARING_COBROWSE,
            "is_admin_agent": window.IS_ADMIN_AGENT,
            "floating_button_bg_color": window.FLOATING_BUTTON_BG_COLOR,
            "enable_voip_with_video_calling": window.ENABLE_VOIP_WITH_VIDEO_CALLING,
            "enable_voip_calling": window.ENABLE_VOIP_CALLING,
            "voip_decline_meeting_message": window.VOIP_DECLINE_MEETING_MESSAGE,
            "allow_video_meeting_only": window.ALLOW_VIDEO_MEETING_ONLY,
            "is_pop_up": window.is_pop_up,
            "agent_unique_id": window.AGENT_UNIQUE_ID,
            "enable_auto_calling": window.ENABLE_AUTO_CALLING,
            "enable_remarks_with_button": window.ENABLE_REMARKS_WITH_BUTTON,
            "is_mobile": window.IS_MOBILE,
            "enable_predefined_remarks": window.ENABLE_PREDEFINED_REMARKS,
            "enable_low_bandwidth_cobrowsing": window.ENABLE_LOW_BANDWIDTH_COBROWSING,
            "low_bandwidth_cobrowsing_threshold": window.LOW_BANDWIDTH_COBROWSING_THRESHOLD,
            "agent_name": window.AGENT_NAME,
            "agent_username": window.AGENT_USERNAME,
            "client_name": window.CLIENT_NAME,
            "agent_joined_first_time": window.AGENT_JOINED_FIRST_TIME,
            "agent_connect_message": window.AGENT_CONNECT_MESSAGE,
            "easyassist_send_agent_weak_connection_message_interval": easyassist_send_agent_weak_connection_message_interval,
            "is_page_reloaded": is_page_reloaded,
            "sync_client_web_screen_timer": sync_client_web_screen_timer,
            "cobrowsing_meta_data_page": cobrowsing_meta_data_page,
            "load_more_meta": load_more_meta,
            "internet_connectivity_timer": internet_connectivity_timer,
            "INTERNET_CON_TIMER": INTERNET_CON_TIMER,
            "margin_left_client_frame_container": margin_left_client_frame_container,
            "margin_top_client_frame_container": margin_top_client_frame_container,
            "requested_for_edit_access": requested_for_edit_access,
            "session_has_ended": session_has_ended,
            "close_nav_timeout": close_nav_timeout,
            "check_meeting_status_interval": check_meeting_status_interval,
            "voip_meeting_initiated_agent": voip_meeting_initiated_agent,
            "client_websocket_open": client_websocket_open,
            "sync_utils_client_websocket_open": sync_utils_client_websocket_open,
            "auto_msg_popup_on_client_call_declined": auto_msg_popup_on_client_call_declined,
            "recording_start_time": recording_start_time,
            "client_iframe_width": client_iframe_width,
            "client_iframe_height": client_iframe_height,
            "EASYASSIST_IFRAME_ID": EASYASSIST_IFRAME_ID_GLOBAL,
            "AGENT_WEAK_CONNECTION_DETECTED": AGENT_WEAK_CONNECTION_DETECTED,
            "AGENT_WEAK_CONNECTION_MODAL_SHOWN": AGENT_WEAK_CONNECTION_MODAL_SHOWN,
            "is_html_requested": is_html_requested,
            "internet_connectivity_check_interval": internet_connectivity_check_interval,
            "EASYASSIST_FUNCTION_FAIL_DEFAULT_CODE": EASYASSIST_FUNCTION_FAIL_DEFAULT_CODE,
            "EASYASSIST_FUNCTION_FAIL_DEFAULT_MESSAGE": EASYASSIST_FUNCTION_FAIL_DEFAULT_MESSAGE,
            "easyassist_function_fail_time": easyassist_function_fail_time,
            "easyassist_function_fail_count": easyassist_function_fail_count,
            "is_html_request_received_to_client": is_html_request_received_to_client,
            "html_request_interval": html_request_interval,
            "connected_successfully": connected_successfully,
            "agent_scale_factor": agent_scale_factor,
            "frame_container_parent_height": frame_container_parent_height,
            "frame_container_parent_width": frame_container_parent_width,
            "easyassist_socket_not_open_count": easyassist_socket_not_open_count,
            "easyassist_socket_utils_not_open_count": easyassist_socket_utils_not_open_count,
            "easyassist_socket_activity_interval_check": easyassist_socket_activity_interval_check,
            "user_last_activity_time_obj": user_last_activity_time_obj,
            "internet_iteration": internet_iteration,
            "screen_recorder_on": screen_recorder_on,
            "recording_data_save_error_shown": recording_data_save_error_shown,
        }
    }catch(err){
        console.log("ERROR : ", err)
    }

    element.innerHTML = "Submitting...";
    error_element.innerHTML = ""
    var request_params = {
        "image_data": image_data,
        "username": window.AGENT_USERNAME,
        "session_id": COBROWSE_SESSION_ID,
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

/************************* START DEBUG UTILS *************************/

function easyassist_is_invalid(node){
    var easyassist_element_id = node.easyassist_element_id;
    var element = easyassist_tree_mirror.idMap[easyassist_element_id];
    if(element != node){
        console.log("---------------------------------");
        console.log("node = ", node);
        console.log("element = ", element);
    }
    return element != node;
}

function easyassist_is_map_invalid(node=null){
    if(node==null){
        var iframe = document.getElementById("frames-container").children[0];
        var doc_html = iframe.contentDocument.documentElement;
        node=doc_html;
    }

    var flag = easyassist_is_invalid(node);
    for(let index=0 ; index<node.children.length ; index++){
        flag |= easyassist_is_map_invalid(node.children[index]);
    }

    return flag;
}

/************************* END DEBUG UTILS *************************/

class EasyAssistDragElement {
    constructor(element) {
        this.element = element;
        this.element.setAttribute("data-easyassist-drag", "true");
        this.element.style.cursor = "move";
        this.horizontal_flip_selector_list = ["span", "svg", "iframe"];

        this.currX = 0;
        this.currY = 0;
        this.offset = 12;
        this.is_dragging = false;
        this.drag_container = null;
        this.prevX = 0;
        this.prevY = 0;

        var _this = this;
        _this.element.addEventListener("mousedown", function(e) {
            _this.drag_element('down', e);
        });

        _this.element.addEventListener("mouseup", function(e) {
            _this.drag_element('up', e);
        });

        document.addEventListener("mouseleave", function(e) {
            _this.drag_element('out', e);
            e.preventDefault();
        });

        _this.element.addEventListener("touchstart", function(e) {
            _this.prevX = e.touches[0].clientX;
            _this.prevY = e.touches[0].clientY;
            _this.drag_element('down', e);
        });

        _this.element.addEventListener("touchmove", function(e) {
            var data = {
                movementX: e.touches[0].clientX - _this.prevX,
                movementY: e.touches[0].clientY - _this.prevY,
            }
            _this.prevX = e.touches[0].clientX;
            _this.prevY = e.touches[0].clientY;
            _this.drag_element('move', data);
        });

        _this.element.addEventListener("touchend", function(e) {
            _this.prevX = 0;
            _this.prevY = 0;
            _this.drag_element('out', e);
        });
    }

    set_drag_container() {
        if(document.getElementsByClassName("easyassist-drag-element").length) {
            return;
        }

        this.drag_container = document.createElement("div");
        this.drag_container.classList.add("easyassist-drag-element");
        this.drag_container.style.position = "absolute";
        this.drag_container.setAttribute("easyassist_avoid_sync", "true");
        this.drag_container.style.top = "0";
        this.drag_container.style.left = "0";
        this.drag_container.style.width = "100%";
        this.drag_container.style.height = "100%";

        var _this = this;
        _this.drag_container.addEventListener("mousemove", function(e) {
            _this.drag_element('move', e);
        });

        _this.drag_container.addEventListener("mouseup", function(e) {
            _this.drag_element('up', e);
        });

        _this.element.classList.add("cobrowsing-moving");
        document.body.appendChild(this.drag_container);
    }

    remove_drag_container() {
        this.element.classList.remove("cobrowsing-moving");
        if(!this.drag_container) {
            return;
        }
        this.drag_container.remove();
        this.drag_container = null;
    }

    drag_element(direction, e) {
        if (direction == 'down') {
        
            this.is_dragging = true;
            this.set_drag_container();
        }

        if (direction == 'up' || direction == "out") {
            if(this.is_dragging == false) {
                return;
            }

            this.is_dragging = false;
            this.remove_drag_container();
            this.relocate_element();
        }

        if (direction == 'move') {
            event.preventDefault()
            if (this.is_dragging) {

                let originalStyles = window.getComputedStyle(this.element);
                this.currX = e.movementX + parseInt(originalStyles.left);
                this.currY = e.movementY + parseInt(originalStyles.top)

                this.drag();
            }
        }
    }

    drag(horizontal_flip = false) {
        this.currX = Math.max(this.currX, 0);

        this.element.style.left = this.currX + "px";
        this.element.style.top = this.currY + "px";

        if(horizontal_flip) {
            this.flip_element_horizontally("-1");
        } else {
            this.flip_element_horizontally("1");
        }
    }

    flip_element_horizontally(offset) {
        this.element.style.transform = "scaleX(" + offset + ")";
        for(let index = 0; index < this.horizontal_flip_selector_list.length; index ++) {
            var selector = this.horizontal_flip_selector_list[index];
            var tooltip_spans = this.element.getElementsByTagName(selector);
            for(let idx = 0; idx < tooltip_spans.length; idx ++) {
                tooltip_spans[idx].style.transform = "scaleX(" + offset + ")";
            }
        }
    }

    relocate_element() {
        var top = this.element.offsetTop;
        var left = this.element.offsetLeft;
        var flip_horizontal = false;

        if(top > window.innerHeight / 2) {
            top = window.innerHeight - this.element.clientHeight - this.offset;
        } else {
            top = this.offset;
        }

        if(left > window.innerWidth / 2) {
            var scrollbar_width = window.innerWidth - document.body.clientWidth;
            left = window.innerWidth - this.element.clientWidth - scrollbar_width;
            left = Math.max(left, 0);

            if(left == 0) {
                flip_horizontal = false;
            } else {
                flip_horizontal = true;
            }
        } else {
            left = 0;
            flip_horizontal = false;
        }

        this.currX = left;
        this.currY = top;
        this.drag(flip_horizontal);
    }
}

function easyassist_initialize_drag_element() {
    try {
        var element = document.getElementById("cobrowse-voip-container");
        if(!element) {
            return;
        }

        if(element.hasAttribute("data-easyassist-drag")) {
            return;
        }

        easyassist_drag_element = new EasyAssistDragElement(element);
    } catch(err) {
        console.log("easyassist_initialize_drag_element: ", err);
    }
}

class ClientTabManager {
    constructor() {
        var tab_container = document.getElementById("easyassist-tab-container");
        this.tab_container = tab_container;
        this.is_html_request_sent = false;
        this.client_tab_close_timeout_map = {};
        this.initialize();
    }

    initialize(){
        var _this = this;
        var client_page_info_list = window.sessionStorage.getItem("client_page_info_list");

        try{
            client_page_info_list = client_page_info_list == null ? [] : JSON.parse(client_page_info_list);
        } catch(err){
            client_page_info_list = [];
        }

        client_page_info_list.forEach(function(client_page_info){
            let title = client_page_info.title;
            let client_page_id = client_page_info.client_page_id;
            let favicon = client_page_info.favicon;

            _this.check_and_create_new_client_page_tab({
                "title": title,
                "favicon": favicon,
                "client_page_id": client_page_id,
                "is_tab_focussed": false,
            });

            _this.show_tab_close_btn(client_page_id);
        })
    }

    create_tab_element(title, favicon, client_page_id, is_tab_focussed) {
        var _this = this;
        try {
            var tab_container = _this.tab_container;

            var tab_button = document.createElement("button");
            tab_button.className = "btn easyassist-tab";
            tab_button.setAttribute("type", "button");
            tab_button.setAttribute("client_page_id", client_page_id);
            
            if(!favicon){
                favicon = '/static/EasyAssistApp/img/tab_favicon.svg'
            } 

            var tab_button_innerHTML = `
                <img alt=".." width="16px" hight="16px" src="${favicon}"></img>
                <span>${title}</span>
                <div style="display:flex !important; align-items:center;">
                    <svg width="14" class="tab-cross-btn" height="10" viewBox="0 0 10 11" fill="none" xmlns="http://www.w3.org/2000/svg" style="display: none;" name="tab-close-btn">
                        <path d="M9.72504 0.61163C9.58492 0.47119 9.39468 0.392266 9.19629 0.392266C8.9979 0.392266 8.80766 0.47119 8.66754 0.61163L5.00004 4.27163L1.33254 0.60413C1.19242 0.46369 1.00218 0.384766 0.803789 0.384766C0.605401 0.384766 0.415163 0.46369 0.275039 0.60413C-0.0174609 0.89663 -0.0174609 1.36913 0.275039 1.66163L3.94254 5.32913L0.275039 8.99663C-0.0174609 9.28913 -0.0174609 9.76163 0.275039 10.0541C0.567539 10.3466 1.04004 10.3466 1.33254 10.0541L5.00004 6.38663L8.66754 10.0541C8.96004 10.3466 9.43254 10.3466 9.72504 10.0541C10.0175 9.76163 10.0175 9.28913 9.72504 8.99663L6.05754 5.32913L9.72504 1.66163C10.01 1.37663 10.01 0.89663 9.72504 0.61163Z" fill="red"/>
                    </svg>
                    <svg height="14" width="14" class="blinking" name="client-active-dot" style="margin-left:2px; display: none;">
                      <circle cx="7" cy="7" r="4" fill="green" />
                    </svg>
                </div>`;
            
            tab_button.innerHTML = tab_button_innerHTML;
            tab_container.appendChild(tab_button);

            tab_button.addEventListener("click", function(event) {
                _this.set_page_tab_active(tab_button, client_page_id);
                if(tab_button.getAttribute("tab-close")) {
                    show_easyassist_client_end_page_loader();
                } else {
                    _this.show_client_page_loader(client_page_id);
                    send_html_request_over_socket();
                }
            });

            var tab_delete_btn = tab_button.querySelector("svg[name='tab-close-btn']");
            tab_delete_btn.addEventListener("click", function(event) {
                _this.close_client_page_tab(client_page_id);
                _this.hide_cross_button();
                event.preventDefault();
                event.stopPropagation();
            });

            _this.client_focus_element_action(client_page_id, is_tab_focussed);
            _this.load_first_tab(client_page_id);
        } catch(err) {
            console.log("easyassist_create_tab_element: ", err);
        }
    }

    create_add_tab_modal_element() {
        let _this = this;
        try {
            let tab_container = _this.tab_container;
            if(document.getElementById("add-proxy-session-tab")) {
                document.getElementById("add-proxy-session-tab").remove();
            }
            let tab_span = document.createElement("span");
            tab_span.className = "btn";
            tab_span.setAttribute("id", "add-proxy-session-tab");
            let tab_span_innerHTML = `
                <div>
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M11.0003 6.83332H6.83366V11C6.83366 11.4583 6.45866 11.8333 6.00033 11.8333C5.54199 11.8333 5.16699 11.4583 5.16699 11V6.83332H1.00033C0.541992 6.83332 0.166992 6.45832 0.166992 5.99999C0.166992 5.54166 0.541992 5.16666 1.00033 5.16666H5.16699V0.99999C5.16699 0.541656 5.54199 0.166656 6.00033 0.166656C6.45866 0.166656 6.83366 0.541656 6.83366 0.99999V5.16666H11.0003C11.4587 5.16666 11.8337 5.54166 11.8337 5.99999C11.8337 6.45832 11.4587 6.83332 11.0003 6.83332Z" fill="#4D4D4D"/>
                    </svg>                
                </div>`;

            tab_span.innerHTML = tab_span_innerHTML;
            tab_container.appendChild(tab_span);
            tab_span.style.cursor = "pointer";

            document.getElementById("add-proxy-session-tab").addEventListener("click", function(event) {
                document.getElementById("open-new-tab-modal").style.display = "block";
            });
        } catch(err) {
            console.log("easyassist_create_add_tab_modal_element: ", err);
        }
    }

    load_first_tab(client_page_id) {
        var _this = this;

        var tab_container = _this.tab_container;
        var total_tabs = tab_container.children.length;

        // If there is only one tab, load the html of that tab
        if(total_tabs > 1) {
            return;
        }

        var tab_button = tab_container.querySelector(`button[client_page_id='${client_page_id}']`);

        tab_button.click();
        this.is_html_request_sent = true;        
    }

    set_page_tab_active(current_tab_btn, client_page_id) {
        var _this = this;
        try {
            ACTIVE_TAB_CLIENT_PAGE_ID = client_page_id;

            var tab_container = _this.tab_container;

            var bg_color = find_light_color(FLOATING_BUTTON_BG_COLOR, 0, 0.06);
            var tab_btns = tab_container.querySelectorAll("button");
            tab_btns.forEach(function(tab_btn) {
                tab_btn.style.background = "";
                tab_btn.classList.remove("active");
            });

            current_tab_btn.classList.add("active");
            
        } catch(err) {
            console.log("easyassist_set_page_tab_active: ", err);
        }
    }

    update_tab_element(title, favicon, client_page_id, is_tab_focussed) {
        var _this = this;
        try {
            var tab_container = _this.tab_container;
            var tab_button = tab_container.querySelector(`button[client_page_id='${client_page_id}']`);

            _this.client_focus_element_action(client_page_id, is_tab_focussed);
            _this.hide_tab_close_btn(client_page_id);
            
            if(!favicon){
                favicon = '/static/EasyAssistApp/img/tab_favicon.svg'
            }
            
            tab_button.querySelector("span").innerText = title;
            tab_button.querySelector("img").src = favicon;

            if(tab_button.classList.contains("active")) {
                tab_button.click();
            }

        } catch(err) {
            console.log("update_tab_element: ", err);
        }
    }

    check_and_create_new_client_page_tab(data_packet) {
        var _this = this;
        try {
            var tab_container = _this.tab_container;

            var title = data_packet.title;
            title = perform_html_encoding(title);
            var client_page_id = data_packet.client_page_id;
            var is_tab_focussed = data_packet.is_tab_focussed;
            let favicon = data_packet.favicon;


            var tab_button = tab_container.querySelector(`button[client_page_id='${client_page_id}']`);

            if(tab_button) {
                _this.update_tab_element(title, favicon, client_page_id, is_tab_focussed)
            } else {
                _this.create_tab_element(title, favicon, client_page_id, is_tab_focussed)
            }

            _this.session_storage_update_client_tab_info(data_packet);
            if(window.ENABLE_PROXY_COBROWSING == "True" && IS_ADMIN_AGENT == "True"){
                _this.hide_cross_button();
            }
            if(window.ENABLE_PROXY_COBROWSING == "True" && IS_ADMIN_AGENT == "True" && window.COBROWSING_TYPE == "outbound-proxy-cobrowsing"){
                _this.create_add_tab_modal_element();
            }
        } catch(err) {
            console.log("check_and_create_new_client_page_tab: ", err);
        }
    }

    session_storage_update_client_tab_info(data_packet){
        var client_page_info_list = window.sessionStorage.getItem("client_page_info_list");

        try{
            client_page_info_list = client_page_info_list == null ? [] : JSON.parse(client_page_info_list);
        } catch(err){
            client_page_info_list = [];
        }

        var client_page_details = {
            "title": data_packet.title,
            "client_page_id": data_packet.client_page_id,
            "is_tab_focussed": data_packet.is_tab_focussed,
        };

        let target_client_page_id = data_packet.client_page_id;
        let client_page_already_exists = false;

        for(let idx=0; idx<client_page_info_list.length; idx++){
            if(client_page_info_list[idx].client_page_id == target_client_page_id){
                client_page_info_list[idx] = client_page_details;
                client_page_already_exists = true;
            }
        }

        if(client_page_already_exists === false){
            client_page_info_list.push(client_page_details);
        }

        window.sessionStorage.setItem("client_page_info_list", JSON.stringify(client_page_info_list));
    }

    session_storage_delete_client_tab_info(client_page_id){
        var client_page_info_list = window.sessionStorage.getItem("client_page_info_list");

        try{
            client_page_info_list = client_page_info_list == null ? [] : JSON.parse(client_page_info_list);
        } catch(err){
            client_page_info_list = [];
        }

        var new_client_page_info_list = [];
        for(let idx=0; idx<client_page_info_list.length; idx++){
            if(client_page_info_list[idx].client_page_id == client_page_id){
                continue;
            }

            new_client_page_info_list.push(client_page_info_list[idx]);
        }

        window.sessionStorage.setItem("client_page_info_list", JSON.stringify(new_client_page_info_list));
    }

    client_focus_element_action(client_page_id, is_tab_focussed) {
        var _this = this;
        try {
            if(is_tab_focussed) {
                _this.show_client_active_element(client_page_id);
                _this.hide_tab_close_btn(client_page_id);
            } else {
                _this.hide_client_active_element(client_page_id);
            }

        } catch(err) {
            console.log("client_focus_element_action: ", err);
        }
    }

    client_tab_close_action(client_page_id) {
        var _this = this;
        try {

            _this.hide_client_active_element(client_page_id);
            _this.show_tab_close_btn(client_page_id);

        } catch(err) {
            console.log("client_tab_close_action: ", err);
        }
    }

    show_client_page_loader(client_page_id) {
        var _this = this;
        _this.clear_close_tab_loader_timeout(client_page_id);
        show_easyassist_client_page_loader();
    }

    start_client_end_page_loader_timeout(client_page_id) {
        var _this = this;

        _this.clear_close_tab_loader_timeout(client_page_id);

        _this.client_tab_close_timeout_map[client_page_id] = setTimeout(function() {
            show_easyassist_client_end_page_loader();
            _this.client_tab_close_timeout_map[client_page_id] = null;
        }, 5000);
    }

    clear_close_tab_loader_timeout(client_page_id) {
        var _this = this;

        if(!(client_page_id in _this.client_tab_close_timeout_map)) {
            _this.client_tab_close_timeout_map[client_page_id] = null;
        }

        if(_this.client_tab_close_timeout_map[client_page_id] != null) {
            clearTimeout(_this.client_tab_close_timeout_map[client_page_id]);
            _this.client_tab_close_timeout_map[client_page_id] = null;
        }
    }

    show_tab_close_btn(client_page_id) {
        var _this = this;
        try {
            var tab_container = _this.tab_container;
            var tab_button = tab_container.querySelector(`button[client_page_id='${client_page_id}']`);

            var client_tab_close_btn = tab_button.querySelector("svg[name='tab-close-btn']");
            client_tab_close_btn.style.display = "";

            tab_button.setAttribute("tab-close", "true");   // Tab is closed by client

            if(tab_button.classList.contains("active")) {
                _this.start_client_end_page_loader_timeout(client_page_id);
            }
        } catch(err) {
            console.log("show_tab_close_btn: ", err);
        }
    }

    hide_tab_close_btn(client_page_id) {
        var _this = this;
        try {
            var tab_container = _this.tab_container;
            var tab_button = tab_container.querySelector(`button[client_page_id='${client_page_id}']`);

            var client_tab_close_btn = tab_button.querySelector("svg[name='tab-close-btn']");
            client_tab_close_btn.style.display = "none";

            tab_button.removeAttribute("tab-close");      // Tab is reopened or not in closing state
        } catch(err) {
            console.log("hide_tab_close_btn: ", err);
        }
    }

    show_client_active_element(client_page_id) {
        var _this = this;
        try {
            var tab_container = _this.tab_container;

            var tab_btns = tab_container.querySelectorAll("button");
            tab_btns.forEach(function(tab_btn) {
                if(tab_btn.querySelector("svg[name='client-active-dot']")){
                    tab_btn.querySelector("svg[name='client-active-dot']").style.display = "none";
                    tab_btn.classList.remove("client-active-tab");
                }
            });

            var tab_button = tab_container.querySelector(`button[client_page_id='${client_page_id}']`);

            var client_active_element = tab_button.querySelector("svg[name='client-active-dot']");
            client_active_element.style.display = "";
            tab_button.classList.add("client-active-tab");

        } catch(err) {
            console.log("show_client_active_element: ", err);
        }
    }

    hide_client_active_element(client_page_id) {
        var _this = this;
        try {
            var tab_container = _this.tab_container;
            var tab_button = tab_container.querySelector(`button[client_page_id='${client_page_id}']`);

            var client_active_element = tab_button.querySelector("svg[name='client-active-dot']");
            client_active_element.style.display = "none";
            tab_button.classList.remove("client-active-tab");
        } catch(err) {
            console.log("hide_client_active_element: ", err);
        }
    }

    close_client_page_tab(client_page_id) {
        var _this = this;
        try {
            var tab_container = _this.tab_container;
            var close_tab_btn = tab_container.querySelector(`button[client_page_id='${client_page_id}']`);

            var is_closed_tab_active = false;
            if(close_tab_btn.classList.contains("active")) {
                is_closed_tab_active = true;
            }

            close_tab_btn.remove();

            if(is_closed_tab_active) {
                if(tab_container.children.length) {
                    var next_tab_btn = tab_container.children[0];
                    next_tab_btn.click();
                }
            }

            _this.session_storage_delete_client_tab_info(client_page_id);

        }  catch(err) {
            console.log("close_client_page_tab: ", err);
        }
    }

    get_agent_active_tab_id() {
        var _this = this;
        try {
            var active_tab_btn = _this.tab_container.querySelector(".active");

            var client_page_id = null;
            if(active_tab_btn) {
                client_page_id = active_tab_btn.getAttribute("client_page_id");
            }
            return client_page_id;
        } catch(err) {
            console.log("get_agent_active_tab_id: ", err);
        }
    }

    get_active_client_tab_id() {
        var _this = this;
        try {
            var tab_container = _this.tab_container;

            var client_page_id = null;
            var client_active_tabs = tab_container.getElementsByClassName("client-active-tab");
            if(client_active_tabs.length) {
                client_page_id = client_active_tabs[0].getAttribute("client_page_id");
            }

            return client_page_id;
        } catch(err) {
            console.log("get_active_client_tab_id: ", err);
        }
        return null;
    }

    hide_cross_button() {
        let total_tabs = document.querySelectorAll(".easyassist-tab");
        if(total_tabs.length > 1){
            let elements = document.querySelectorAll(".tab-cross-btn");
            for (let index = 0 ; index < elements.length; index++) {
                elements[index].style.display = "flex";
            }
        } else {
            let elements = document.querySelectorAll(".tab-cross-btn");
            for (let index = 0 ; index < elements.length; index++) {
                elements[index].style.display = "none";
            }
        }
    }
}

function easyassist_initialize_client_tab_manager() {
    try {
        CLIENT_TAB_MANAGER_INSTANCE = new ClientTabManager();
    } catch(err) {
        console.log("initialize_client_tab_manager: ", err);
    }
}

function easyassist_start_show_focus_toast_timeout() {

    try {
        easyassist_clear_show_focus_toast_timeout();

        client_show_focus_toast_timeout = setTimeout(function() {
            var client_active_tab_id = CLIENT_TAB_MANAGER_INSTANCE.get_active_client_tab_id();

            if(client_active_tab_id == null) {
                show_easyassist_toast("Customer is not focussed on any of the tabs.");
            }

            client_show_focus_toast_timeout = null;
        }, 3000);
    } catch(err) {
        console.log("easyassist_start_show_focus_toast_timeout: ", err);
    }
}

function easyassist_clear_show_focus_toast_timeout() {

    try {
        if(client_show_focus_toast_timeout != null) {
            clearTimeout(client_show_focus_toast_timeout);
            client_show_focus_toast_timeout = null;
        }
    } catch(err) {
        console.log("easyassist_clear_show_focus_toast_timeout: ", err);
    }
}

function send_client_page_info_request() {
    try {
        /*
            Agent Client Connected = 1
            Agent Client Not Connected = Not possible
            Agent Connected Client Not Connected = Agent connect -> client drop | Client Connect -> page_details
            Agent Not connect Client Connected = Client sent -> Agent drop | Agent connect -> request Packet
        */

        if(check_screen_sharing_cobrowsing_enabled()) {
            return;
        }

        json_string = JSON.stringify({
            "type": "client_page_info",
        });

        encrypted_data = easyassist_custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };

        //console.log("request for html has been sent: ", new Date());
        send_message_over_easyassist_socket(encrypted_data, "agent");        
    } catch(err) {
        console.log("send_client_page_info_request: ", err);
    }
}

function easyassist_hide_cobrowsing_loader() {
    try {
        document.getElementById("easyassist-loader").style.display = "none";
    } catch(err) {
        console.log("easyassist_hide_cobrowsing_loader: ", err);
    }
}

function show_easyassist_client_page_loader() {
    hide_easyassist_client_end_page_loader();
    if(window.COBROWSE_LOGO != "" && window.COBROWSE_LOGO != null && window.COBROWSE_LOGO != undefined) {
        document.getElementById("easyassist-client-page-loader").getElementsByClassName("loading-image")[0].innerHTML = `<img src="${window.COBROWSE_LOGO}" alt="Loading Image" width="220px">`
    } else {
        document.getElementById("easyassist-client-page-loader").getElementsByClassName("loading-image")[0].innerHTML = '<img src="https://static.allincall.in/static/EasyAssistApp/img/loadingImage.svg" alt="Loading Image" width="220px">'
    }
    document.getElementById("easyassist-client-page-loader").getElementsByClassName("loading-lines")[0].style.display = "block";
    document.getElementById("easyassist-client-page-loader").getElementsByClassName("loading-message")[0].innerHTML = "Loading Customer Experiences at Scale.";
    document.getElementById("easyassist-client-page-loader").style.display = "";
}

function hide_easyassist_client_page_loader() {
    document.getElementById("easyassist-client-page-loader").style.display = "none";
}


function show_easyassist_client_end_page_loader() {
    hide_easyassist_client_page_loader();
    document.getElementById("easyassist-client-end-page-loader").style.display = "";
}

function hide_easyassist_client_end_page_loader() {
    document.getElementById("easyassist-client-end-page-loader").style.display = "none";
}


function easyassist_send_iframe_html_request() {
    try {
        if(check_screen_sharing_cobrowsing_enabled()) {
            return;
        }

        json_string = JSON.stringify({
            "type": "iframe_html",
        });

        encrypted_data = easyassist_custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };

        //console.log("request for html has been sent: ", new Date());
        send_message_over_easyassist_socket(encrypted_data, "agent");
    } catch(err) {
        console.log("easyassist_send_iframe_html_request: ", err);
    }
}

function send_invited_agent_call_request_packet(){

    let is_call_ongoing = false;
    let is_cobrowse_meeting_active = get_easyassist_cookie("is_cobrowse_meeting_active");
    if(is_cobrowse_meeting_active == COBROWSE_SESSION_ID) {
        is_call_ongoing = true;
    }

    let json_string = JSON.stringify({
        "type": "invited_agent_call_request",
        "is_call_ongoing": is_call_ongoing
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function easyassist_create_local_storage_obj() {
    if(localStorage.getItem("easyassist_session") == null){
        var local_storage_json_object = {};
        local_storage_json_object[COBROWSE_SESSION_ID] = {};
        localStorage.setItem("easyassist_session", JSON.stringify(local_storage_json_object));
    }
}

function easyassist_clear_local_storage() {
    localStorage.removeItem("easyassist_session");
}

function get_easyassist_current_session_local_storage_obj() {
    try {
        let local_storage_obj = null;
        let easyassist_session_id = COBROWSE_SESSION_ID;

        if(localStorage.getItem("easyassist_session") != null) {
            local_storage_obj = localStorage.getItem("easyassist_session");
            local_storage_obj = JSON.parse(local_storage_obj);
            if(local_storage_obj.hasOwnProperty(easyassist_session_id)) {
                local_storage_obj = local_storage_obj[easyassist_session_id];
            } else {
                return null; 
            }
        }
        return local_storage_obj;
    } catch (error) {
        return null;
    }
}

function set_easyassist_current_session_local_storage_obj(key, value) {
    try{
        let local_storage_obj = localStorage.getItem("easyassist_session");
        let easyassist_session_id = COBROWSE_SESSION_ID;

        if(local_storage_obj) {
            local_storage_obj = JSON.parse(local_storage_obj);
            local_storage_obj[easyassist_session_id][key] = value;
            localStorage.setItem("easyassist_session", JSON.stringify(local_storage_obj));
        }
    }catch(err){
        console.log("ERROR: set_easyassist_current_session_local_storage_obj ", err);
    }
}

function easyassist_customer_meeting_request_hander() {
    try {
        
        if(get_easyassist_cookie("customer_meeting_request_status") == "true") {
            return;
        }
        if(IS_ADMIN_AGENT == "True"){
            set_easyassist_cookie("customer_meeting_request_status", "true");
        }
        var meeting_request_modal = document.getElementById("co-browsing-video-call-request-meeting-modal");
        if(ALLOW_VIDEO_MEETING_ONLY == "False") {
             if (check_voip_enabled()) {
                meeting_request_modal = document.getElementById("voice-call-receiving-modal");
            }
        }
        var customer_request_meeting_modal_invited_agent = document.getElementById("customer_request_meeting_modal_invited_agent")

        if(meeting_request_modal.style.display != "flex") {
            meeting_request_modal.style.display = "flex";
            $("#request_meeting_modal").modal('hide');
        }

    } catch(err) {
        console.log("easyassist_agent_meeting_request_hander: ", err);
    }
}

function update_customer_meeting_request(status) {
    // call_initiate_by_customer = "false";
    set_easyassist_current_session_local_storage_obj("call_initiate_by_customer", "false");
    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    // Show request meeting modal on agent request
    delete_easyassist_cookie("customer_meeting_request_status");
    
    var request_meeting_error_el = null;

    if (ALLOW_VIDEO_MEETING_ONLY == true || ALLOW_VIDEO_MEETING_ONLY == "true" || ALLOW_VIDEO_MEETING_ONLY == "True") {
        request_meeting_error_el = document.getElementById("request_meeting_error");
    } else{
        if (check_voip_enabled()){
            request_meeting_error_el = document.getElementById("request_meeting_error");
            request_meeting_error_el.innerHTML = "";
        }
        else {
            request_meeting_error_el = document.getElementById("request_meeting_error");
        }
    }

    request_meeting_error_el.innerHTML = "";

    let json_string = JSON.stringify({
        "id": easyassist_session_id,
        "status": status
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/update-customer-meeting-request/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            set_easyassist_cookie("is_cobrowse_meeting_on", "false");
            if (response.status == 200) {
                if (ALLOW_VIDEO_MEETING_ONLY == true || ALLOW_VIDEO_MEETING_ONLY == "true" || ALLOW_VIDEO_MEETING_ONLY == "True") {
                    document.getElementById("co-browsing-video-call-request-meeting-modal").style.display = "none";
                } else {
                    if (check_voip_enabled()) {
                        document.getElementById("voice-call-receiving-modal").style.display = "none";
                    } else {
                        document.getElementById("co-browsing-video-call-request-meeting-modal").style.display = "none";
                    }
                }

                if (response.meeting_allowed == "true") {
                    if (check_voip_video_meeting_enabled() || check_voip_enabled()) {
                        set_easyassist_cookie("cobrowse_meeting_id", easyassist_session_id);
                    }
                    set_easyassist_cookie("easyassist_meeting_allowed", "true");
                    set_easyassist_cookie("is_cobrowse_meeting_active", COBROWSE_SESSION_ID);
                    set_easyassist_cookie("is_meeting_initiate_by_customer", "true");
                } else {
                    set_easyassist_cookie("easyassist_meeting_allowed", "false");
                }
                //easyassist_check_for_agent_highlight();
            } else {
                request_meeting_error_el.innerHTML = "Some error occured we can not connect you with our agent.";
            }
        }
    }
    xhttp.send(params);
}

function easyassist_agent_allow_meeting_request_handler() {
    function easyassist_check_cobrowse_meeting_on() {
        var cobrowsing_meeting = get_easyassist_cookie("is_cobrowse_meeting_on");
        if (cobrowsing_meeting == '' || cobrowsing_meeting == null || cobrowsing_meeting == undefined) {
            cobrowsing_meeting = false
        }
        if (cobrowsing_meeting == false || cobrowsing_meeting == 'false') {
            return false;
        }
        return true;
    }

    try {

        if (ALLOW_VIDEO_MEETING_ONLY == true || ALLOW_VIDEO_MEETING_ONLY == "true" || ALLOW_VIDEO_MEETING_ONLY == "True") {
            if(easyassist_check_cobrowse_meeting_on() == false) {
                connect_with_client(COBROWSE_SESSION_ID);
                // EASYASSIST_COBROWSE_META.allow_meeting = true;
            }
        } else {
            if (check_voip_enabled()) {
                if(easyassist_check_cobrowse_meeting_on() == false) {
                    if(IS_MOBILE == "True") {
                        document.getElementById("request-cobrowsing-meeting-btn").parentNode.parentNode.style.display = "none";
                    } else {
                        document.getElementById("request-cobrowsing-meeting-btn").style.display = 'none';
                    }
                    // add_customer_audio_call_icon_for_invited_agent()
                    set_easyassist_current_session_local_storage_obj("hide_agent_call_initiation_icon", "true");
                    easyassist_open_voip_meeting_window();
                }
            } else if (check_voip_video_meeting_enabled()){
                if(easyassist_check_cobrowse_meeting_on() == false) {
                    if(IS_MOBILE == "True") {
                        document.getElementById("request-cobrowsing-meeting-btn").parentNode.parentNode.style.display = "none";
                    } else {
                        document.getElementById("request-cobrowsing-meeting-btn").style.display = 'none';
                    }
                    show_cobrowse_meeting_option();
                    set_easyassist_current_session_local_storage_obj("hide_agent_call_initiation_icon", "true");
                }
            } else {
                if(easyassist_check_cobrowse_meeting_on() == false) {
                    if(IS_MOBILE == "True") {
                        document.getElementById("request-cobrowsing-meeting-btn").parentNode.parentNode.style.display = "none";
                    } else {
                        document.getElementById("request-cobrowsing-meeting-btn").style.display = 'none';
                    }
                    connect_with_client(COBROWSE_SESSION_ID);
                    set_easyassist_current_session_local_storage_obj("hide_agent_call_initiation_icon", "true");
                }
            }
        }
    }
    catch(err) {
        console.log("easyassist_agent_allow_meeting_request_handler: ", err);
    }
}

function easyassist_open_voip_meeting_window() {
    set_easyassist_cookie("is_cobrowse_meeting_on", "true");
    var session_id = COBROWSE_SESSION_ID
    var url = window.location.protocol + "//" + window.location.host + "/easy-assist/agent-cobrowse-meeting/" + session_id;
    window.open(url, "_blank");
}

function connect_customer_voip_meeting() {
    request_params = {
        "session_id": COBROWSE_SESSION_ID
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/check-customer-initiate-meeting-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if(response.status == 301){
                $('#customer_request_meeting_modal_invited_agent .modal-text').text('The call is not accepted by the agent yet, You can join the call once the agent accepts it.')
                $('#customer_request_meeting_modal_invited_agent .modal-footer').html('<button class="btn btn-primary" type="button" onclick="hide_invited_agent_voice_call_receiving_modal();customer_init_ok_button_handler();">OK</button>');
            }
            if (response.status == 200) {  
                if(response.is_meeting_allowed == false){
                    set_easyassist_current_session_local_storage_obj("customer_init_is_ok_button_clicked_invited_agent", "false");
                    if(check_voip_video_meeting_enabled()) {
                        $('#customer_request_meeting_modal_invited_agent .modal-text').text('Agent has denied the Video call, Request you to wait till agent accepts it.');
                    } else if (check_voip_enabled()) {
                        $('#customer_request_meeting_modal_invited_agent .modal-text').text('Agent has denied the Voice call, Request you to wait till agent accepts it.');
                    } else {
                        $('#customer_request_meeting_modal_invited_agent .modal-text').text('Agent has denied the Video call, Request you to wait till agent accepts it.');
                    }
                    $('#customer_request_meeting_modal_invited_agent .modal-footer').html('<button class="btn btn-primary" type="button" onclick="hide_invited_agent_voice_call_receiving_modal()">OK</button>');
                    hide_side_nav_call_icon_for_customer_init_call();
                }
                else{
                    set_easyassist_current_session_local_storage_obj("customer_init_is_ok_button_clicked_invited_agent", "false");
                    document.getElementById("customer_request_meeting_modal_invited_agent").style.display = "none";
                    $("#invited_agent_customer_voip_meeting_connect_modal").modal("hide");                    
                    
                    reset_customer_init_call_modal_text();
                    hide_side_nav_call_icon_for_customer_init_call();
                    set_easyassist_cookie("is_cobrowse_meeting_active", COBROWSE_SESSION_ID);

                    if(check_voip_video_meeting_enabled()) {
                        show_cobrowse_meeting_option();
                    } else if (check_voip_enabled()) {
                        voip_connect_with_client();
                    } else {
                        connect_with_client(COBROWSE_SESSION_ID);
                    }
                }
            }
        } 
    }
    xhttp.send(params);
}

function hide_invited_agent_voice_call_receiving_modal() {
    document.getElementById("customer_request_meeting_modal_invited_agent").style.display = 'none';
}

function send_customer_request_meeting_modal_invited_agent_show_request(){
    json_string = JSON.stringify({
        "type": "customer_request_meeting_modal_invited_agent",
        
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function add_customer_audio_call_icon_for_invited_agent() {
    json_string = JSON.stringify({
        "type": "add_customer_audio_call_icon_for_invited_agent",
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function send_join_customer_voice_call_meeting_btn_hide_request(){
    json_string = JSON.stringify({
        "type": "join_customer_voice_call_meeting_btn_hide",
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function send_call_initiate_over_socket() {

    json_string = JSON.stringify({
        "type": "call_initiate_by_agent",
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function show_side_nav_call_icon_for_customer_init_call(){
    
    if(is_meeting_tab_open()) {
        hide_side_nav_call_icon_for_customer_init_call();
        return;
    }

    if(IS_MOBILE == "True") {
        document.getElementById("request-cobrowsing-meeting-btn-invited-agent").parentNode.parentNode.style.display = "flex";
    } else {
        if(check_voip_enabled()){
            if(IS_MOBILE == "True") {
                document.getElementById("join-customer-voice-call-meeting-btn").parentNode.parentNode.style.display = "inherit";
            } else {
                document.getElementById("join-customer-voice-call-meeting-btn").style.display = "inherit";
            }
        }
        else{
            if(IS_MOBILE == "True") {
                document.getElementById("join-customer-cobrowsing-video-call-meeting-btn").parentNode.parentNode.style.display = "inherit";
            } else {
                document.getElementById("join-customer-cobrowsing-video-call-meeting-btn").style.display = "inherit";
            }
        }
    }
}

function hide_side_nav_call_icon_for_customer_init_call(){
    var local_storage_obj = get_easyassist_current_session_local_storage_obj();
    if(local_storage_obj != null && local_storage_obj.hasOwnProperty("customer_init_is_ok_button_clicked_invited_agent")) {
        if(local_storage_obj["customer_init_is_ok_button_clicked_invited_agent"] == "true") {
            return;
        }
    }

    if(IS_MOBILE == "True") {
        document.getElementById("request-cobrowsing-meeting-btn-invited-agent").parentNode.parentNode.style.display = "none";
    } else {
        if(check_voip_enabled()){
            if(IS_MOBILE == "True") {
                document.getElementById("join-customer-voice-call-meeting-btn").parentNode.parentNode.style.display = "none";
            } else {
                document.getElementById("join-customer-voice-call-meeting-btn").style.display = "none";
            }
        }
        else{
            if(IS_MOBILE == "True") {
                document.getElementById("join-customer-cobrowsing-video-call-meeting-btn").parentNode.parentNode.style.display = "none";
            } else {
                document.getElementById("join-customer-cobrowsing-video-call-meeting-btn").style.display = "none";
            }
        }
    }
}

function reset_customer_init_call_modal_text(){
    if(check_voip_video_meeting_enabled()) {
        $('#customer_request_meeting_modal_invited_agent .modal-text').text('A video call request has been initiated by the customer, by clicking on "connect" Customer and you will be connected on  a video conferencing.');
        $('#customer_request_meeting_modal_invited_agent .modal-footer').html('<button class="btn btn-secondary" type="button" onclick="hide_invited_agent_voice_call_receiving_modal()">Decline</button>' + 
        '<button class="btn btn-primary" id="request_button" type="button" onclick="connect_customer_voip_meeting()">Connect</button>');
    } else if (check_voip_enabled()) {
        $('#customer_request_meeting_modal_invited_agent .modal-text').text('Customer has initiated a voice call. Would you like to connect?');
        $('#customer_request_meeting_modal_invited_agent .modal-footer').html('<button class="btn btn-secondary" type="button" onclick="hide_invited_agent_voice_call_receiving_modal()">No</button>' + 
        '<button class="btn btn-primary" id="request_button" type="button" onclick="connect_customer_voip_meeting()">Yes</button>');
    } else {
        $('#customer_request_meeting_modal_invited_agent .modal-text').text('A video call request has been initiated by the customer, by clicking on "connect" Customer and you will be connected on  a video conferencing.');
        $('#customer_request_meeting_modal_invited_agent .modal-footer').html('<button class="btn btn-secondary" type="button" onclick="hide_invited_agent_voice_call_receiving_modal()">Decline</button>' + 
        '<button class="btn btn-primary" id="request_button" type="button" onclick="connect_customer_voip_meeting()">Connect</button>');
    }
    
}

function check_meeting_initiate_by_customer(){
    json_string = JSON.stringify({
        "type": "check_meeting_initiate_by_customer",
        "is_invited_agent": true
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function send_meeting_initiate_by_customer_status_over_socket(meeting_initiate_by_customer) {
    json_string = JSON.stringify({
        "type": "check_meeting_initiate_by_customer",
        "is_agent": true,
        "status": meeting_initiate_by_customer
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function hide_chat_bubble_greeting_div() {
    $(".chat-talk-bubble").css("display","none");
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

function play_greeting_bubble_popup_sound() {

    let livechat_iframe = document.getElementById("allincall-chat-box");

    if (livechat_iframe.classList.contains("animate__slideInUp")) {
        return;
    }

    chat_notification_sound();
}

function append_chat_bubble_message(agent_name, message, attachment, attachment_file_name){    
    $("#chat-minimize-icon-wrapper").css({"display":"block"});
    $(".chat-talk-bubble").removeClass("bounce2");
    var message_box = document.getElementById("talktext-p");
    $(".chat-talk-bubble").css({"display":"block"});
    $(".chat-talk-bubble").addClass("bounce2");
    
    let is_current_tab_focussed = check_current_tab_active();
    if( is_current_tab_focussed ){
        play_greeting_bubble_popup_sound();
    }

    let received_message = ""
    let short_message = "";
    if(check_text_link(message)) {
        let parser = new DOMParser();
        link_start_index = message.indexOf("<a");
        link_end_index = message.indexOf("</a>");
        let html_parsed_obj = parser.parseFromString(message.substring(link_start_index, link_end_index), 'text/html');
        url_message = html_parsed_obj.querySelector('a').href;
        short_message = message.substring(0,link_start_index) + "<u>" + url_message + "</u>" + message.substring(link_end_index, message.length);
        short_message = easyassist_limit_characters(short_message,50) ;        
    } else {
        short_message = easyassist_limit_characters(message, 50);
    }

    if(attachment != "None" && attachment != undefined) {
        var extension = attachment_file_name.split(".")[1];
        let short_file_name = attachment_file_name
        if(short_file_name.length > 10) {
            short_file_name = get_shorter_file_name(attachment_file_name, 10);
        }
        if(message) {
            received_message = "<b>" + agent_name + "</b>" + " : " + short_file_name.slice(0,short_file_name.length-4) + "." + extension + "<br>" + short_message;
        } else {
            received_message = "<b>" + agent_name + "</b>" + " : " + short_file_name.slice(0,short_file_name.length-4) + "." + extension;
        }
    } else {
        received_message = "<b>" + agent_name + "</b>" + " : " + short_message;
    }
    message_box.innerHTML = received_message;
    set_easyassist_current_session_local_storage_obj("last_message",received_message);
    setTimeout(function(){
        $(".chat-talk-bubble").removeClass("bounce2");
    },1500);
}

function easyassist_show_chat_bubble() {
    if(window.ENABLE_CHAT_BUBBLE == "True" && window.IS_MOBILE == "False") {
        $("#chat-minimize-icon-wrapper").css({"display":"block"});
    }
}

function easyassist_limit_characters(message, char_limit) {
    if (message.length > char_limit) {
        message = message.substring(0, char_limit) + "...";
    }
    return message;
}

function send_transfer_agent_connected_socket_message(agent_name, agent_username) {

    json_string = JSON.stringify({
        "type": "transferred_agent_connected",
        "agent_username": agent_username,
        "agent_name": agent_name,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function send_transfer_agent_request_socket_message(agent_id) {

    agent_username = document.getElementById(agent_id+"-support-agent-username").innerHTML
    json_string = JSON.stringify({
        "type": "transferred_agent_request",
        "agent_id": agent_id,
        "agent_username": agent_username.substring(0,agent_username.length-5),
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function send_transfer_agent_response_socket_message(agent_id, agent_username) {

    json_string = JSON.stringify({
        "type": "transferred_agent_response",
        "agent_id": agent_id,
        "agent_username": agent_username,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function update_transfer_agent_log(element, transfer_agent_id) {

    if (get_easyassist_cookie("is_cobrowse_meeting_active") == COBROWSE_SESSION_ID) {
        easyassist_show_long_toast("Session transfer is not allowed while connected on a call. Please disconnect the call and try again.")
        $("#askfor_support_modal").modal('hide');
        return;
    }

    send_transfer_agent_request_socket_message(transfer_agent_id);    

    json_string = JSON.stringify({
        "session_id": COBROWSE_SESSION_ID,
        "agent_id": transfer_agent_id
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Transferring...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/transfer-cobrowsing-session/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                toggle_transfer_log_check_interval();
                set_easyassist_current_session_local_storage_obj("is_session_transferred_request_sent", "true")
                set_easyassist_current_session_local_storage_obj("invite_button_id_to_hide", transfer_agent_id)
                $("#askfor_support_modal").modal('hide');
                easyassist_show_long_toast("Your session transfer request has been successfully sent to " + response["agent_name"]);
                get_list_of_support_agents();
            } else {
                console.log("Unable to place the transfer request.")
            }
            element.innerHTML = "Transfer";
        }
    }
    xhttp.send(params);
}

function check_update_for_transfer_session_log() {
    json_string = JSON.stringify({
        "session_id": COBROWSE_SESSION_ID,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/check-transfer-session-log/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                if (response["message"] == "accepted") {
                    window.IS_ADMIN_AGENT = "False"
                    document.getElementById("transfer-agent-modal-text").innerHTML = response["agent_username"] + " has joined the session. Do you want to leave the session?";
                    set_easyassist_current_session_local_storage_obj("is_session_transferred_request_sent", "false");
                    send_transfer_agent_connected_socket_message(response["agent_name"], response["agent_username"]);
                    hide_all_cobrowsing_modals();
                    $("#modal_session_transfer_success").modal("show");
                    toggle_transfer_log_check_interval(false);
                    if(get_easyassist_cookie("request_edit_access") == COBROWSE_SESSION_ID) {
                        revoke_easyassist_edit_access();
                    }
                    send_transfer_agent_response_socket_message(response["agent_id"], response["agent_username"]);
                } else if (response["message"] == "rejected") {
                    toggle_transfer_log_check_interval(false);
                    set_easyassist_current_session_local_storage_obj("is_session_transferred_request_sent", "false");
                    easyassist_show_long_toast("Agent " + response["agent_name"] + " has rejected the session transfer request.")
                    get_list_of_support_agents();
                    send_transfer_agent_response_socket_message(response["agent_id"], response["agent_username"]);
                } else if (response["message"] == "expired") {
                    toggle_transfer_log_check_interval(false);
                    set_easyassist_current_session_local_storage_obj("is_session_transferred_request_sent", "false");
                    easyassist_show_long_toast("Transfer request expired due to agent inactivity, please try again.")
                    get_list_of_support_agents();
                    send_transfer_agent_response_socket_message(response["agent_id"], response["agent_username"]);
                }
            } else {
                send_transfer_agent_response_socket_message(response["agent_id"]);
                console.log("Unable to retrive update.")
            }
        }
    }
    xhttp.send(params);
}

function toggle_transfer_log_check_interval(flag = true) {
    if (flag) {
        transfer_interval = setInterval(check_update_for_transfer_session_log, 3000);
    } else {
        clearInterval(transfer_interval);
    }
}

function easyassist_show_long_toast(message) {

    var easyassist_snackbar_custom = document.getElementById("easyassist-snackbar");
    easyassist_snackbar_custom.innerHTML = message;
    easyassist_snackbar_custom.className = "show";

    setTimeout(function () {
        easyassist_snackbar_custom.className = easyassist_snackbar_custom.className.replace("show", "");
    }, 5000);
}

function hide_all_cobrowsing_modals() {
    
    document.getElementById("allincall-chat-box").style.display = "none";

    var modals = [
        "#capture_pageshot_confirm_modal",
        "#capture_pageshot_confirm_modal",
        "#request_for_edit_access_modal",
        "#captured_information_modal",
        "#support_material_modal",
        "#request_meeting_modal",
        "#check_for_internet_modal",
        "#askfor_support_modal",
        "#close_session_modal",
        "#client_internet_connection_weak_message_modal",
        "#client_disconnected_message_modal"
    ];

    for (var modal_index = 0; modal_index < modals.length; modal_index++) {
        $(modals[modal_index]).modal("hide");
    }

    $("#cobrowse-mobile-modal").modal("hide");
}

// Proxy Cobrowsing code starts here

function open_new_proxy_session_tab(){
    let total_tabs = document.querySelectorAll(".easyassist-tab");
    let error_element = document.getElementById("error-message-proxy-link");
    error_element.innerHTML = "";

    let website_url = document.getElementById("proxy-cobrowse-website-url").value;
    website_url = website_url.trim();

    if(total_tabs.length >= 10){
        error_element.innerText = "Maximum tab limit reached please close any of the tab and try again.";
        return;
    }

    if(!website_url) {
        error_element.innerText = "Please enter website link to continue."
        return;
    }

    if(!check_valid_url(website_url)) {
        error_element.innerText = "Please enter valid website link."
        return false;
    }

    let json_params = JSON.stringify({
        "website_url": website_url,
        "session_id": get_easyassist_cookie("easyassist_session_id"),
    });

    let encrypted_data = easyassist_custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/cognoai-cobrowse/add-new-proxy-session-tab/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                document.getElementById("proxy-drop-link").value = response.generated_link;
                document.getElementById("success-message-div").classList.remove("d-none");
                document.getElementById("copy-link-button-div").classList.remove("d-none");
                document.getElementById("copy-link-button-div").classList.add("d-flex");
                document.getElementById("copy-link-heading").classList.remove("d-none");
                document.getElementById("open-website-link").setAttribute("disabled", true);
            } else if(response.status == 301){
                error_element.innerHTML = response.message;
            } else {
                show_easyassist_toast("Not able to start cobrowsing. Please try again.");
            }
        }
    }
    xhttp.send(params);
}

function copy_shareable_link_to_clipboard(id) {
    let copy_text = document.getElementById(id);
    let text_area_element = document.createElement('textarea');
    text_area_element.value = copy_text.value;
    document.body.appendChild(text_area_element);
    text_area_element.select();
    document.execCommand("copy");
    document.body.removeChild(text_area_element);
    show_easyassist_toast("Shareable link has been copied");
}

function toggle_copy_link_modal_visibility(close_modal=false) {
    if(close_modal){
        if(IS_MOBILE == "True" && document.getElementById("sidebar-mobile-modal-btn")){
            document.getElementById("sidebar-mobile-modal-btn").style = "flex";
        }
        document.getElementById("proxy-cobrowse-link-modal").style.display = "none";
    } else {
        document.getElementById("proxy-cobrowse-link-modal").style.display = "block";
    }
}

function hide_open_new_tab_cobrowsing_modal(){
    document.getElementById("open-new-tab-modal").style.display="none";
    document.getElementById("proxy-cobrowse-website-url").value = "";
    document.getElementById("proxy-drop-link").value = "";
    document.getElementById("error-message-proxy-link").value = "";
    document.getElementById("success-message-div").classList.add("d-none");
    document.getElementById("copy-link-button-div").classList.add("d-none");
    document.getElementById("copy-link-button-div").classList.remove("d-flex");
    document.getElementById("copy-link-heading").classList.add("d-none");
    document.getElementById("open-website-link").disabled = false
}
// Proxy Cobrowsing code ends here

function check_edit_access_apply_coview_listener() {
    
    if(is_edit_access()) 
        return;

    let local_storage_obj = get_easyassist_current_session_local_storage_obj()
    if(local_storage_obj.hasOwnProperty("pdf_modal_easyassist_id") && local_storage_obj["pdf_modal_easyassist_id"]) {
        set_easyassist_cookie("is_pdf_modal_open", "true");   
        easyassist_apply_pdf_coview_pointer_events(local_storage_obj["pdf_modal_easyassist_id"]);
        local_storage_obj["pdf_modal_easyassist_id"] = "";
    }
}