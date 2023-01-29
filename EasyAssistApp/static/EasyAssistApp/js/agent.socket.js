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

var client_websocket = null;
var client_websocket_open = false;
var sync_utils_client_websocket = null;
var sync_utils_client_websocket_open = false;

var auto_msg_popup_on_client_call_declined = false;
var recording_start_time = null;
var client_iframe_width = 0;
var client_iframe_height = 0;
var EASYASSIST_IFRAME_ID = 0;
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

////////////////////////////////////////////////////

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
        client_websocket.onopen = function(){
                console.log("client_websocket created successfully") 
                client_websocket_open = true;
                // if(ENABLE_LOW_BANDWIDTH_COBROWSING !== "True" && ENABLE_LOW_BANDWIDTH_COBROWSING !== true) {
                    send_recursively_html_request();
                // }
            }
        client_websocket.onclose = function() {
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
            client_websocket.send(JSON.stringify({
                "message": {
                    "header": {
                        "sender": sender
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
            sync_utils_client_websocket.send(JSON.stringify({
                "message": {
                    "header": {
                        "sender": sender
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
    }else{
        easyassist_socket_utils_not_open_count = 0;
    }

}

function send_recursively_html_request() {
    if(html_request_interval != null) {
        return;
    }

    if(!is_html_request_received_to_client) {
        send_html_request_over_socket();
    }

    html_request_interval = setInterval(function() {
        if(is_html_request_received_to_client) {
            clearInterval(html_request_interval);
            html_request_interval = null;
        } else {
            send_html_request_over_socket();
        }
    }, 5000);
}

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

function send_html_received_over_socket() {

    if(check_screen_sharing_cobrowsing_enabled()) {
        return;
    }

    json_string = JSON.stringify({
        "type": "html_received",
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    //console.log("request for html has been sent: ", new Date());
    send_message_over_easyassist_socket(encrypted_data, "agent");
}


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
    for(let i = 0; i < cookie_array.length; i++) {
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
    delete_easyassist_cookie("easyassist_client_weak_internet_connection_shown");
    clearInterval(easyassist_send_agent_weak_connection_message_interval);
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
        $("#mask-successfull-cobrowsing-session").attr("checked", true)
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

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if(easyassist_session_id != COBROWSE_SESSION_ID){
        easyassist_delete_session_cookie();
    }
    set_easyassist_cookie("easyassist_session_id", COBROWSE_SESSION_ID);

    sync_client_web_screen_timer = setInterval(function(e) {
        agent_heartbeat();
    }, 15000);

    sync_client_web_screen_agent_timer = setInterval(function(e) {
        sync_client_web_screen_agent();
    }, 10000);
    // sync_client_web_screen_agent();
    reset_internet_connectivity_check_timer();
    set_user_inactivity_detector();
    // get_support_material();
    // load_chat_history();
    update_edit_access_icon_properties();

    // screen_recording_cookie = get_easyassist_cookie("screen_recorder_on");
    // if(screen_recording_cookie != undefined && screen_recording_cookie == "true") {
    //     console.log(screen_recording_cookie);
    //     document.getElementById("screen-recording-btn").click();
    // }

    setTimeout(function() {
        load_allincall_chat_box();
    }, 30000);

    try {
        if(ALLOW_VIDEO_MEETING_ONLY != true && ALLOW_VIDEO_MEETING_ONLY != "true" && ALLOW_VIDEO_MEETING_ONLY != "True") {
            if(check_voip_video_meeting_enabled() || check_voip_enabled()) {
                check_and_start_voip_meeting();
            }
        }
    } catch(err) {}
};

window.addEventListener('resize', function() { 
    if(client_iframe_width && client_iframe_height) {
        // var iframe_container_margin_left = Math.max((window.innerWidth - client_iframe_width), 0) / 2;
        // var iframe_container_margin_top = Math.max((window.innerHeight - client_iframe_height), 0) / 2;
        // framesContainer.style.marginLeft = iframe_container_margin_left + "px";
        // framesContainer.style.marginTop = iframe_container_margin_top + "px";
        resize_iframe_container(client_iframe_width, client_iframe_height);
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
            check_voip_meeting_active_over_socket();
        }, 5000);
    }
}

function send_support_agent_connected_message(agent_name) {

    if(IS_ADMIN_AGENT == "True" || get_easyassist_cookie("support_agent_message") == "true")
        return;
    json_string = JSON.stringify({
        "type": "support_agent_connected",
        "agent_name": agent_name
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
        "agent_name": agent_name
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function check_voip_meeting_active_over_socket() {
    // This function is only used by invited agent, to ask for admin agent over socket if voip meeting is active
    json_string = JSON.stringify({
        "type": "voip_meeting_active",
        "is_invited_agent": true,
        "agent_id": AGENT_UNIQUE_ID,
        "agent_name": window.AGENT_NAME,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function send_voip_meeting_active_status_over_socket(meeting_status, invited_agent_id) {
    json_string = JSON.stringify({
        "type": "voip_meeting_active",
        "is_agent": true,
        "agent_id": invited_agent_id,
        "meeting_status": meeting_status,
        "agent_name": window.AGENT_NAME,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");

}

function create_and_iframe(html) {

    if(ALLOW_SCREENSHARING_COBROWSE == 'True' || ALLOW_SCREENSHARING_COBROWSE == 'true' || ALLOW_SCREENSHARING_COBROWSE == true) {

        return ;
    }

    EASYASSIST_IFRAME_ID += 1;

    // html = EasyAssistLZString.decompress(html);
    var blob = new Blob([html], {
        type: 'text/html'
    });
    var iframe = document.createElement('iframe');
    iframe.src = window.URL.createObjectURL(blob);
    iframe.id = "easyassist-iframe-" + EASYASSIST_IFRAME_ID;
    iframe.hidden = true;
    iframe.onload = function(event) {
        renderFrame(event);
        document.getElementById("easyassist-loader").style.display = "none";
        iframe.hidden = false;
    };

    iframe.setAttribute("class", "client-data-frame");

    // if(IS_MOBILE == "True") {
        // iframe.style.width = client_iframe_width.toString() + "px";
        // iframe.style.height = client_iframe_height.toString() + "px";
        // iframe.style.overflow = "auto";
    // }



    framesContainer.appendChild(iframe);
    is_page_reloaded = false;
    edit_access_update();

    // var iframe_container_margin_left = Math.max((window.innerWidth - client_iframe_width), 0) / 2;
    // var iframe_container_margin_top = Math.max((window.innerHeight - client_iframe_height), 0) / 2;
    // framesContainer.style.marginLeft = iframe_container_margin_left + "px";
    // framesContainer.style.marginTop = iframe_container_margin_top + "px";

    // margin_left_client_frame_container = parseInt(iframe_container_margin_left);
    // margin_top_client_frame_container = parseInt(iframe_container_margin_top);
}

function create_and_iframe_from_chunk(client_packet) {
    var html = "";
    for(let index = 0; index <= client_packet.chunk; index++) {
        //console.log(client_packet.page, index);
        html += chunk_html_dict[client_packet.page][index];
    }
    delete chunk_html_dict[client_packet.page];
    create_and_iframe(html);
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

    var agent_dimension =  easyassist_get_agent_frame_dimension(
        Math.min(window.innerWidth, client_iframe_width),
        Math.min(window.innerHeight, client_iframe_height),
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
    var iframe_container_margin_top = Math.max((window.innerHeight - framesContainer_parent_height), 0) / 2;
    framesContainer.style.marginLeft = iframe_container_margin_left + "px";
    framesContainer.style.marginTop = iframe_container_margin_top + "px";

    margin_left_client_frame_container = parseInt(iframe_container_margin_left);
    margin_top_client_frame_container = parseInt(iframe_container_margin_top);
    agent_scale_factor = max_scale_factor;
    frame_container_parent_width = framesContainer_parent_width;
    frame_container_parent_height = framesContainer_parent_height;
}

function update_edit_access_icon_properties() {
    if (document.getElementById("easyassist-edit-access-icon") != undefined) {
        if (get_easyassist_cookie("request_edit_access") == COBROWSE_SESSION_ID) {
            if(IS_MOBILE == "True") {
                document.getElementById("easyassist-edit-access-icon").setAttribute("data-target", "");
                document.getElementById("easyassist-edit-access-icon").setAttribute("onclick", "remove_onbeforeunload();revoke_easyassist_edit_access();hide_cobrowsing_modals(this)");
                document.getElementById("easyassist-edit-access-icon").parentElement.nextElementSibling.innerText = "Revoke Edit Access";
                document.getElementById("easyassist-edit-access-icon").parentElement.style.backgroundColor = find_light_color(FLOATING_BUTTON_BG_COLOR, 300);
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
                document.getElementById("easyassist-edit-access-icon").parentElement.nextElementSibling.innerText = "Request for Edit Access";
                document.getElementById("easyassist-edit-access-icon").parentElement.style.backgroundColor = "initial";
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
        "type": "livechat-typing"
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function sync_client_web_screen(e) {

    var data = JSON.parse(e.data);
    message = data.message;
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

    if (message.header.sender == "client") {

        reset_internet_connectivity_check_timer();

        if (client_packet.type == "html") {
            if(ALLOW_SCREENSHARING_COBROWSE == 'True' || ALLOW_SCREENSHARING_COBROWSE == 'true' || ALLOW_SCREENSHARING_COBROWSE == true) {

                return ;
            }
            if (client_packet.is_chunk == false) {
                //console.log("html page ", message.body.html_page_counter, new Date());
                client_iframe_width = client_packet.window_width;
                client_iframe_height = client_packet.window_height;
                create_and_iframe(client_packet.html);
                resize_iframe_container(client_packet.window_width, client_packet.window_height);
                //console.log("iframe created for page: ", message.body.html_page_counter, new Date());
            } else {
                if (client_packet.page in chunk_html_dict) {
                    chunk_html_dict[client_packet.page][client_packet.chunk] = client_packet.html;
                } else {
                    chunk_html_dict[client_packet.page] = {};
                    chunk_html_dict[client_packet.page][client_packet.chunk] = client_packet.html;
                }

                if (client_packet.is_last_chunk) {
                    create_and_iframe_from_chunk(client_packet);
                }
            }
        } else if (client_packet.type == "scroll") {
            if(ALLOW_SCREENSHARING_COBROWSE == 'True' || ALLOW_SCREENSHARING_COBROWSE == 'true' || ALLOW_SCREENSHARING_COBROWSE == true) {

                return ;
            }
            var scrollX = client_packet.data_scroll_x;
            var scrollY = client_packet.data_scroll_y;
            if (framesContainer.children.length > 0) {
                prev_frame = framesContainer.children[0];
                prev_frame.contentWindow.scrollTo(scrollX, scrollY);
            }

        } else if (client_packet.type == "pageshot" || client_packet.type == "screenshot") {

            if (client_packet.result == 200) {
                show_easyassist_toast("Screenshot captured successfully.");
            } else {
                show_easyassist_toast("Unable to capture the screenshot. Please try again.");
            }

        } else if (client_packet.type == "mouse") {

            if(check_screen_sharing_cobrowsing_enabled()) {
                return ;
            }

            // client_mouse_element.style.top = (margin_top_client_frame_container + client_packet.position.clientY) + "px";
            // client_mouse_element.style.left = (margin_left_client_frame_container + client_packet.position.clientX) + "px";
            var factor_y = frame_container_parent_height / client_iframe_height;
            var client_pos_y = (margin_top_client_frame_container + client_packet.position.clientY * factor_y);
            var client_pos_x = (margin_left_client_frame_container + client_packet.position.clientX * agent_scale_factor);
            client_mouse_element.style.top = client_pos_y + "px";
            client_mouse_element.style.left = client_pos_x + "px";

        } else if (client_packet.type == "chat") {

            set_client_response(client_packet.message, client_packet.attachment, client_packet.attachment_file_name);

        }  else if (client_packet.type == "livechat-typing") {

            set_livechat_typing(client_packet.name, client_packet.role)

        } else if (client_packet.type == "element_value") {
            if(ALLOW_SCREENSHARING_COBROWSE == 'True' || ALLOW_SCREENSHARING_COBROWSE == 'true' || ALLOW_SCREENSHARING_COBROWSE == true) {

                return ;
            }

            if (framesContainer.children.length > 0) {

                frame_child = framesContainer.children[0];

                html_elements_value_list = client_packet.html_elements_value_list;

                for(let html_element_index = 0; html_element_index < html_elements_value_list.length; html_element_index++) {

                    try {
                        html_element = html_elements_value_list[html_element_index];
                        tag_name = html_element.tag_name;
                        tag_type = html_element.tag_type;
                        easyassist_element_id = html_element.easyassist_element_id;
                        value = html_element.value;
                        is_active = html_element.is_active;

                        frame_element = frame_child.contentDocument.querySelector("[easyassist-element-id='" + easyassist_element_id + "']");

                        if (frame_element == null || frame_element == undefined) {
                            continue;
                        }

                        if (tag_name.toLowerCase() == "select") {

                            if (html_element.is_obfuscated_element) {
                                var obfuscated_option = document.createElement("option");
                                obfuscated_option.value = "******";
                                obfuscated_option.innerHTML = "******";
                                frame_element.appendChild(obfuscated_option);
                                value = "******";
                            }

                            var select_value_found = false;
                            for(let option_index = 0; option_index < frame_element.options.length; option_index++) {
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
                    show_easyassist_toast("Edit Access has been revoked.");
                }else {
                    save_easyassist_system_audit_trail("edit_access", "client_revoked_edit_access");
                    show_easyassist_toast("Customer has revoked edit access.");
                }
            } else if (requested_for_edit_access == true) {
                requested_for_edit_access = false;

                if (client_packet.is_allowed == "true") {
                    set_easyassist_cookie("request_edit_access", COBROWSE_SESSION_ID);
                    send_edit_access_status_over_socket();
                    show_easyassist_toast("Customer has provided edit access to you.");
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
                show_easyassist_toast("Customer ended the call");
            }
            setTimeout(function() {
                if(check_voip_video_meeting_enabled()) {
                    end_cobrowse_video_meet(true);
                }
            }, 1000);
        } else if(client_packet.type == "voip_meeting_joined") {
            toggle_voip_ringing_sound(false);
        } else if(client_packet.type == "voip_meeting_ready") {
            if(IS_ADMIN_AGENT == "True") {
                show_easyassist_toast("Customer joined the call");
            }
            set_easyassist_cookie("is_customer_voip_meeting_joined", COBROWSE_SESSION_ID);
        } else if(client_packet.type == "div-scroll") {
            try {
                value_top = client_packet.value_top;
                value_left = client_packet.value_left;
                element_id = client_packet.element_id;
                element_attr_id = client_packet.id;
                let element = null;
                if (element_attr_id != null && element_attr_id != undefined) {
                    element = framesContainer.children[0].contentDocument.getElementById(element_attr_id);
                } else {
                    element = framesContainer.children[0].contentDocument.querySelector("[easyassist-element-id='" + element_id + "']")
                }
                element.scrollTop = value_top;
                element.scrollLeft = value_left;
            } catch(err) {}
        } else if(client_packet.type == "sync-node") {
            try {
                var easyassist_element_id = client_packet.easyassist_element_id;
                var element_style = client_packet.style;
                var element_class = client_packet.class;
                var element_text = client_packet.text;
                var element_src = client_packet.src;

                var element = framesContainer.children[0].contentDocument.querySelector("[easyassist-element-id='" + easyassist_element_id + "']");
                if(element) {
                    element.className = element_class;
                    if(element_style != null) {
                        element.setAttribute('style', element_style);
                    } else {
                        element.setAttribute('style', "");
                    }
                    if(!is_edit_access()) {
                        element.style.pointerEvents = "none";
                    }
                    element.setAttribute('easyassist-element-id', easyassist_element_id);
                    if(element_src != null) {
                        element.setAttribute('src', element_src);
                    }
                    if(element.children.length == 0 && element_text != element.innerText) {
                        element.innerHTML = element_text;
                    }

                    if(client_packet.disabled == true) {
                        element.setAttribute("disabled", "true");
                    } else {
                        element.removeAttribute("disabled");
                    }
                }
            } catch(err) {}
        } else if(client_packet.type == "sync-removed-node") {
            try {
                var element_ids = client_packet.element_ids;
                for(let idx = 0; idx < element_ids.length; idx ++) {
                    let easyassist_element_id = element_ids[idx];
                    let element = framesContainer.children[0].contentDocument.querySelector("[easyassist-element-id='" + easyassist_element_id + "']");
                    if(element) {
                        element.remove();
                    }
                }
            } catch(err) {
                console.log(err);
            }
        } else if(client_packet.type == "sync-new-node") {
            try {
                var parent_element_id = client_packet.parent_element_id;
                var child_index = client_packet.child_index;
                var child_html = client_packet.child_html;
                var child_list = new Set(client_packet.child_list);
                var parent_text_length = client_packet.parent_text_length;
                let element = framesContainer.children[0].contentDocument.querySelector("[easyassist-element-id='" + parent_element_id + "']");

                for(let idx = 0; idx < element.children.length; idx ++) {
                    var child_id = element.children[idx].getAttribute('easyassist-element-id');
                    if(child_id != undefined && child_id != null && !child_list.has(child_id)) {
                        element.children[idx].remove();
                    }
                }

                if(element.children.length == 0 && parent_text_length == 0) {
                    element.innerHTML = "";
                }

                if(child_index == 0) {
                    element.insertAdjacentHTML("afterbegin", child_html);
                } else if(child_index >= element.children.length) {
                    element.insertAdjacentHTML("beforeend", child_html);
                } else {
                    var sibling_element = null;
                    for(let idx = 0; idx < element.children.length; idx ++) {
                        if(idx == child_index - 1) {
                            sibling_element = element.children[idx];
                            break;
                        }
                    }
                    if(sibling_element == null) {
                        element.insertAdjacentHTML("beforeend", child_html);
                    } else {
                        sibling_element.insertAdjacentHTML("afterend", child_html);
                    }
                }

                easyassist_update_edit_access();

            } catch(err) {
                console.log(err);
            }
        } else if( client_packet.type == "client_weak_connection" ){
            if(get_easyassist_cookie("easyassist_session_id")){
                if(get_easyassist_cookie("easyassist_client_weak_internet_connection_shown") == undefined || get_easyassist_cookie("easyassist_client_weak_internet_connection_shown") == "false"){
                    show_client_weak_internet_connectio_modal();
                    set_easyassist_cookie("easyassist_client_weak_internet_connection_shown", "true")
                }
            }
        } else if(client_packet.type == "html_request_received") {

            if(is_html_request_received_to_client == false){
                if(window.AGENT_JOINED_FIRST_TIME == "true" || window.AGENT_JOINED_FIRST_TIME == true || window.AGENT_JOINED_FIRST_TIME == "True"){
                    var message = "Agent " + window.AGENT_NAME + " has joined the chat";
                    send_chat_message_from_agent(message, "None", "None", "chat_bubble");
                }
                send_support_agent_connected_message(window.AGENT_NAME);
            }

            is_html_request_received_to_client = true;
        }
    } else {
        
        if(message.header.sender == "agent" ){
            if (client_packet.type == "chat"){
                if(window.AGENT_NAME != client_packet.agent_name){
                    set_agent_response(client_packet.message, client_packet.attachment, client_packet.attachment_file_name, client_packet.chat_type, client_packet.agent_name);
                }
            } else if (client_packet.type == "sync-form") {
                if(window.AGENT_NAME == client_packet.agent_name)
                    return;
                tag_name = client_packet.tag_name;
                tag_type = client_packet.tag_type;
                element_id = client_packet.easyassist_element_id;
                value = client_packet.value;
                query_selector = tag_name + "[easyassist-element-id='" + element_id + "']";
                client_iframe = document.getElementsByClassName("client-data-frame")[0].contentWindow.document;
                change_element = client_iframe.querySelector(query_selector);
    
                if (tag_name == "select") {
    
                    if (change_element.options == undefined || change_element.options == null) {
                        return;
                    }
    
                    for(let option_index = 0; option_index < change_element.options.length; option_index++) {
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
            } else if(client_packet.type == "voip_meeting_active") {
                voip_meeting_initiated_agent = client_packet.agent_name;
                if(client_packet.is_invited_agent) {
                    if(IS_ADMIN_AGENT == "True") {
                        var is_cobrowse_meeting_active = get_easyassist_cookie("is_cobrowse_meeting_active");
                        var voip_meeting_active_status = false;
                        if(is_cobrowse_meeting_active == COBROWSE_SESSION_ID) {
                            voip_meeting_active_status = true;
                        }
                        send_voip_meeting_active_status_over_socket(voip_meeting_active_status, client_packet.agent_id);
                    }
                } else if(client_packet.is_agent) {
                    if(IS_ADMIN_AGENT == "False" && AGENT_UNIQUE_ID == client_packet.agent_id) {
                        if(client_packet.meeting_status == true) {
                            show_invited_agent_voip_connect_modal();
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
                            show_invited_agent_voip_connect_modal();
                        }
                    }
                }
            } else if(client_packet.type == "div-scroll") {
                if(IS_ADMIN_AGENT == "False") {
                    try {
                        value_top = client_packet.value_top;
                        value_left = client_packet.value_left;
                        element_id = client_packet.element_id;
                        element_attr_id = client_packet.id;
                        element = null;
                        if (element_attr_id != null && element_attr_id != undefined) {
                            element = framesContainer.children[0].contentDocument.getElementById(element_attr_id);
                        } else {
                            element = framesContainer.children[0].contentDocument.querySelector("[easyassist-element-id='" + element_id + "']")
                        }
                        element.scrollTop = value_top;
                        element.scrollLeft = value_left;
                    } catch(err) {}
                }
            } else if (client_packet.type == "support_agent_connected") {
                if(window.AGENT_NAME != client_packet.agent_name)
                    show_easyassist_toast("Agent " + client_packet.agent_name + " has joined the session.");
            }  else if (client_packet.type == "support_agent_leave") {
                if(window.AGENT_NAME != client_packet.agent_name)
                    show_easyassist_toast("Agent " + client_packet.agent_name + " has left the session.");
            }  else if (client_packet.type == "livechat-typing") {
                if(window.AGENT_NAME != client_packet.name)
                    set_livechat_typing(client_packet.name, client_packet.role)
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

    json_string = JSON.stringify({
      "type": "sync-scroll",
      "active_url": window.location.href,
      "data_scroll_x": frame.contentWindow.scrollX,
      "data_scroll_y": frame.contentWindow.scrollY
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
      "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");
}

function renderFrame(event) {

    setTimeout(function() {

        event.preventDefault();

        if (framesContainer.children.length) {

            var frame = document.getElementById("easyassist-iframe-" + EASYASSIST_IFRAME_ID);
            if (!frame) {
                return;
            }

            for(let idx = 0; idx < EASYASSIST_IFRAME_ID; idx ++) {
                try {
                    if(document.getElementById("easyassist-iframe-" + idx)) {
                        document.getElementById("easyassist-iframe-" + idx).remove();
                    }
                } catch(err) {}
            }

            frame.hidden = false;

            send_html_received_over_socket();

            var scrollX = parseInt(frame.contentDocument.documentElement.dataset.scrollX);
            var scrollY = parseInt(frame.contentDocument.documentElement.dataset.scrollY);
            frame.contentDocument.addEventListener('contextmenu', event => event.preventDefault());
            frame.contentWindow.scrollTo(scrollX, scrollY);

            frame.contentDocument.onkeydown = function(e) {
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

            frame.contentWindow.document.onclick = function(event) {
                event_tag_name = event.target.tagName.toLowerCase();
                edit_access_update();
                if (get_easyassist_cookie("request_edit_access") != COBROWSE_SESSION_ID) {
                    event.preventDefault();
                    highlightElement(event, frame.contentWindow);
                } else {
                    if (is_valid_edit_element(event.target) == false) {
                        event.preventDefault();
                        highlightElement(event, frame.contentWindow);
                    }
                }
            }

            frame.contentWindow.document.onmousemove = function(event) {
                sync_mouse_position(event);
            }

            frame.contentWindow.document.onscroll = function(event) {
                sync_scroll_position(frame);
            }

            try {
                frame.contentDocument.body.onclick = button_click_client_element;
            } catch {
                console.log("Iframe body does not exist")
            }

            $("#allincall-chat-box")[0].contentWindow.document.onmousemove = function(event) {
                sync_mouse_position(event, is_from_chat_window = true);
            }

            easyassist_update_edit_access();
        }

    }, 800);
}

function easyassist_update_edit_access() {

    var iframe = document.getElementById("frames-container").children[0];
    var html_element = iframe.contentDocument.children[0];

    if(is_edit_access()) {
        easyassist_apply_edit_access(html_element);
    } else {
        easyassist_reset_edit_access(html_element);
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

        dom_node.style.pointerEvents = "none";

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
            remove_easyassist_event_listner_into_element(dom_node, "change", detect_agent_value_change);

        } else if(tag_name == "div") {
            var scroll_left = dom_node.getAttribute("easyassist-data-scroll-x");
            var scroll_top = dom_node.getAttribute("easyassist-data-scroll-y");
            dom_node.scrollLeft = scroll_left;
            dom_node.scrollTop = scroll_top;
        }

        remove_easyassist_event_listner_into_element(dom_node, "scroll", sync_scroll_position_inside_div);
        remove_easyassist_event_listner_into_element(dom_node, "click", button_click_client_element);

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

function button_click_client_element(event) {
    currentBtn = event.target;

    event.preventDefault();

    easyassist_element_id = currentBtn.getAttribute("easyassist-element-id");
    if (easyassist_element_id == null || easyassist_element_id == undefined) {
        easyassist_element_id = "";
    }
    json_string = JSON.stringify({
        "type": "button-click",
        "element_id": event.target.id,
        "easyassist_element_id": easyassist_element_id
    });
    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    send_message_over_easyassist_socket(encrypted_data, "agent");
}

function sync_scroll_position_inside_div(event) {
    try {
        json_string = JSON.stringify({
            "type": "div-scroll",
            "value_top": event.target.scrollTop,
            "value_left": event.target.scrollLeft,
            "element_id": event.target.getAttribute("easyassist-element-id"),
            "element_id_attr": event.target.id,
        })

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
        if (remarks.replace(/[^a-z0-9]/gi, '') == "") {
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

    comment_desc = ""
    try{
        comments = document.getElementById("close-session-remarks").value.trim();

        if(comments.length == 0) {
            close_session_remark_error_el.innerHTML = "Please select a remark";
            close_session_remark_error_el.style.display = 'block';
            return;
        }
        comment_desc = document.getElementById("close-session-remarks-text").value;
    } catch(err){
        comments = document.getElementById("close-session-remarks-text").value;
    }

    comment_desc = remove_special_characters_from_str(comment_desc);
    comments = remove_special_characters_from_str(comments);

    is_helpful = document.getElementById("mask-successfull-cobrowsing-session").checked;
    is_test = document.getElementById("mask-test-cobrowsing-session").checked;

    if(is_test == false && remarks_validation(comments, close_session_text_error_el, "Remarks", 1, 200) == "invalid"){
        return
    }

    if(window.ENABLE_PREDEFINED_REMARKS == true || window.ENABLE_PREDEFINED_REMARKS == "true" || window.ENABLE_PREDEFINED_REMARKS == "True"){
        if(comments == "others"){
            if(is_test == false  && remarks_validation(comment_desc, close_session_text_error_el, "Comments", 1, 200) == "invalid"){
                return
            }
        } else {
            if(is_test == false && remarks_validation(comment_desc, close_session_text_error_el, "Comments", 0, 200) == "invalid"){
                return
            }
        }
    }

    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID,
        "is_helpful": is_helpful,
        "is_test": is_test,
        "comments": comments,
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
                window.location = "/easy-assist/sales-ai/dashboard/";
            } else {
                element.innerHTML = "End Session";
            }
        }
    }
    xhttp.send(params);
}

function close_agent_leave_session(element) {

    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID,
        "is_leaving": true
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
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
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                send_support_agent_leave_message(window.AGENT_NAME);
                window.location = "/easy-assist/sales-ai/dashboard/";
                delete_easyassist_cookie("support_agent_message");
                delete_easyassist_cookie("easyassist_client_disconnected_modal_shown");
                delete_easyassist_cookie("easyassist_client_weak_internet_connection_shown");
                clearInterval(easyassist_send_agent_weak_connection_message_interval);
            } else {
                element.innerHTML = "Leave Session";
            }
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
                    for(let index = 0; index < meta_information_list.length; index++) {
                        meta_id = meta_information_list[index]["id"];
                        //if (meta_information_list[index]["type"] == "screenshot") {
                            tbody_html += [
                                '<tr>',
                                    '<td style="text-transform: capitalize;">' + meta_information_list[index]["type"] + '</td>',
                                    '<td>' + meta_information_list[index]["datetime"] + '</td>',
                                    '<td style="text-align: center">',
                                        '<!--<a href="/easy-assist/agent/export/' + meta_id + '/?type=img" target="_blank" title="Export As Image"><i class="fas fa-fw fa-download"></i></a> -->',
                                        '<a href="/easy-assist/agent/export/' + meta_id + '/?type=img" download title="Export As Image">',
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

    support_agents = [support_agent_id];

    if (support_agents.length == 0) {
        document.getElementById("share-session-error").innerHTML = "Please select atleast one support agent with whom you want to share the session.";
        return;
    }

    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID,
        "support_agents": support_agents
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

function check_screen_sharing_cobrowsing_enabled() {
    if(ALLOW_SCREENSHARING_COBROWSE == "True" || ALLOW_SCREENSHARING_COBROWSE == true || ALLOW_SCREENSHARING_COBROWSE == "true") {
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

    var image_addr = "https://upload.wikimedia.org/wikipedia/commons/b/b9/Pizigani_1367_Chart_1MB.jpg";
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
    var support_agent_error = document.getElementById("support-agent-error");
    var support_agent_container_id = document.getElementById("support-agent-container-id");
    var support_agent_button = document.getElementById("support-agent-button");

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
        support_agent_error.style.display = "none";
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
                              '<div class="support-agent-text">',
                                  username + ' - ' + level,
                              '</div>',
                              '<div class="support-agent-invite-btn">',
                                  '<a href="javascript:void(0);" onclick="share_cobrowsing_session(this, \'' + id + '\')">Invite</a>',
                              '</div>',
                            '</li>',
                        ].join('');
                    }
                    support_agents_container.classList.remove('justify-content-center');
                    support_agents_container.innerHTML = div_inner_html;
                    support_agent_error.style.display = "none";
                    support_agent_container_id.style.display = "";
                    support_agent_button.innerHTML = "Cancel";
                    support_agent_button.onclick = "";
                    $(support_agent_button).attr("data-dismiss", "modal")
                } else {
                    support_agent_error.style.display = "";
                    support_agent_error.innerHTML = "No active agents found.";
                    support_agent_container_id.style.display = "none";
                    support_agent_button.innerHTML = "Cancel";
                    support_agent_button.onclick = "";
                    $(support_agent_button).attr("data-dismiss", "modal")
                }
            } else {
                support_agent_error.style.display = "";
                support_agent_error.innerHTML = "Unable to load the details. Please try again.";
                support_agent_container_id.style.display = "none";
                support_agent_button.innerHTML = "Try Again";
                support_agent_button.onclick = get_list_of_support_agents;
                $(support_agent_button).attr("data-dismiss", "none")
            }
        } else if (this.readyState == 4){
            support_agent_error.style.display = "";
            support_agent_error.innerHTML = "Unable to load the details. Please try again.";
            support_agent_container_id.style.display = "none";
            support_agent_button.innerHTML = "Try Again";
            support_agent_button.onclick = get_list_of_support_agents;
            $(support_agent_button).attr("data-dismiss", "none")
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

function save_cobrowsing_chat_history(chat_message, sender, attachment, attachment_file_name, chat_type) {

    json_string = JSON.stringify({
        "session_id": COBROWSE_SESSION_ID,
        "sender": sender,
        "message": chat_message,
        "attachment": attachment,
        "attachment_file_name": attachment_file_name,
        "chat_type": chat_type,
    });

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
        }
    }
    xhttp.send(params);
}

function send_chat_message_from_agent(message, attachment, attachment_file_name, chat_type) {
      save_cobrowsing_chat_history(message, "agent", attachment, attachment_file_name, chat_type);
      var agent_name = window.AGENT_NAME;
      json_string = JSON.stringify({
          "agent_name": agent_name,
          "type": "chat",
          "message": message,
          "attachment": attachment,
          "attachment_file_name": attachment_file_name,
          "chat_type": chat_type,
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

function open_livechat_agent_window() {

    var allincall_chat_box = document.getElementById("allincall-chat-box");
    allincall_chat_box.style.display = "block";
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
        } else if (event.data.event_id === "livechat-typing") {
            easyassist_send_livechat_typing_indication()
            return
        }
        if (event.data == "close-bot") {
            close_chatbot_animation()
        } else {
            // The data hasn't been sent from your site!
            // Be careful! Do not use it.
            return;
        }
    }
});

function close_chatbot_animation() {
    document.getElementById("allincall-chat-box").style.animationName = "bottom-left-right-anime-close";
    document.getElementById("allincall-chat-box").style.display = "none";
}

function set_client_response(message, attachment, attachment_file_name) {
    try {
        if (document.getElementById("allincall-chat-box").style.display == "none") {
            document.getElementById("allincall-chat-box").style.display = "block";
            focus_livechat_input();
        }
        allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow;
        allincall_chat_window.postMessage(JSON.stringify({
            "message": message,
            "attachment": attachment,
            "attachment_file_name": attachment_file_name,
            "show_client_message": true,
            "name": window.CLIENT_NAME
        }), window.location.protocol + "//" + window.location.host);
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

function set_agent_response(message, attachment, attachment_file_name, chat_type, agent_name) {
    if (document.getElementById("allincall-chat-box").style.display == "none") {
        if(chat_type != "chat_bubble"){
            document.getElementById("allincall-chat-box").style.display = "block";
        }
    }
    allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow;
    allincall_chat_window.postMessage(JSON.stringify({
        "message": message,
        "attachment": attachment,
        "attachment_file_name": attachment_file_name,
        "show_other_agent_message": true,
        "name": agent_name,
        "chat_type": chat_type
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

    show_easyassist_toast("Request for edit access has been sent to customer.");
}

function detect_agent_value_change(event) {
    if (get_easyassist_cookie("request_edit_access") == COBROWSE_SESSION_ID) {
        element = event.target;
        tag_type = element.getAttribute("type");
        tag_name = element.tagName.toLowerCase();
        element_id = element.getAttribute("easyassist-element-id");
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
            "agent_name": AGENT_NAME
        });

        encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        send_message_over_easyassist_socket(encrypted_data, "agent");
    }
}

function append_attachment_message_into_chatbox(message, attachment, attachment_file_name) {
    if (document.getElementById("allincall-chat-box").style.display == "none") {
        document.getElementById("allincall-chat-box").style.display = "block";
    }
    allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow;
    allincall_chat_window.postMessage(JSON.stringify({
        "message": message,
        "attachment": attachment,
        "attachment_file_name": attachment_file_name,
        "show_agent_message": true,
        "name": window.AGENT_NAME
    }), window.location.protocol + "//" + window.location.host);
}

function send_support_material_doc(element) {
    var action_cell = element.parentElement;
    var message_cell = action_cell.previousElementSibling;
    var attachment_cell = message_cell.previousElementSibling;

    var attachment = attachment_cell.children[0].href;
    attachment = strip_html(attachment);

    var message = message_cell.children[0].value;
    message = strip_html(message);
    message = remove_special_characters_from_str(message);

    var attachment_file_name = attachment_cell.children[0].text;
    attachment_file_name = strip_html(attachment_file_name);
    attachment_file_name = remove_special_characters_from_str(attachment_file_name)

    send_chat_message_from_agent(message, attachment, attachment_file_name, "chat_message");
    append_attachment_message_into_chatbox(message, attachment, attachment_file_name);

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
                    for(let index = 0; index < support_document.length; index++) {
                        var support_document_obj = support_document[index];
                        var file_name = support_document_obj["file_name"];
                        var file_path = window.location.protocol + "//" + window.location.host + "/" + support_document_obj["file_path"];
                        var message = file_name;
                        div_inner_html += '<tr>';
                        div_inner_html += '<td style="vertical-align:middle;"> <a class="support-document-link" href="' + file_path + '" target="_blank" >' + file_name + '</a> </td>';
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
            AGENT_CONNECT_MESSAGE = response.agent_connect_message;

            if(check_voip_enabled() || check_voip_video_meeting_enabled()) {
                AGENT_CONNECT_MESSAGE = "";
            }

            window.AGENT_NAME = response.agent_name;
            window.CLIENT_NAME = response.client_name;
            if (response.status == 200 && response.chat_history.length > 0) {
                AGENT_CONNECT_MESSAGE = "";
                chat_history = response.chat_history;
                allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow;
                for(let index = 0; index < chat_history.length; index++) {
                    sender = chat_history[index]["sender"];
                    message = chat_history[index]["message"];
                    message=show_hyperlink_inside_text(message);
                    datetime = chat_history[index]["datetime"];
                    var time = datetime.split(" ")[3] + " " + datetime.split(" ")[4];
                    attachment = chat_history[index]["attachment"];
                    attachment_file_name = chat_history[index]["attachment_file_name"];
                    chat_type = chat_history[index]["chat_type"];
                    if (sender == "client") {
                        allincall_chat_window.postMessage(JSON.stringify({
                            "message": message,
                            "attachment": attachment,
                            "attachment_file_name": attachment_file_name,
                            "show_client_message": true,
                            "name": window.CLIENT_NAME,
                            "time": time,
                            "chat_type": chat_type,
                        }), window.location.protocol + "//" + window.location.host);
                    } else if(sender == window.AGENT_NAME) {
                        allincall_chat_window.postMessage(JSON.stringify({
                            "message": message,
                            "attachment": attachment,
                            "attachment_file_name": attachment_file_name,
                            "show_agent_message": true,
                            "time": time,
                            "name": sender,
                            "chat_type": chat_type,
                        }), window.location.protocol + "//" + window.location.host);
                    } else {
                        allincall_chat_window.postMessage(JSON.stringify({
                            "message": message,
                            "attachment": attachment,
                            "attachment_file_name": attachment_file_name,
                            "show_other_agent_message": true,
                            "time": time,
                            "name": sender,
                            "chat_type": chat_type,
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
    } catch {
        screen_recorder_on = false;
        if(IS_MOBILE == "True") {
            e.parentElement.nextElementSibling.innerText = "Start screen recording";
            e.parentElement.style.backgroundColor = 'initial';
        } else {
            e.style.backgroundColor = 'initial';
            e.children[1].children[1].innerHTML = "Start screen recording";
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
        stopRecordingDiv.style.display = "flex ";
    } else {
        if(IS_MOBILE == "True") {
            e.parentElement.nextElementSibling.innerText = "Stop screen recording";
            e.parentElement.style.backgroundColor = find_light_color(FLOATING_BUTTON_BG_COLOR, 300);
        } else {
            e.style.backgroundColor = find_light_color(FLOATING_BUTTON_BG_COLOR, 300);
            e.children[1].children[1].innerHTML = "Stop screen recording"
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
        document.getElementById('start-screen-recording-btn').style.backgroundColor = 'initial';
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
    window.open("/easy-assist/meeting/" + session_id + "?is_meeting_cobrowsing=true", "_blank",);
}

function voip_connect_with_client() {
    var url = window.location.protocol + "//" + window.location.host + "/easy-assist/agent-cobrowse-meeting/" + COBROWSE_SESSION_ID;
    window.open(url, "_blank",);
}

function request_for_meeting(session_id) {

    
    request_params = {
        "session_id": session_id
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var request_meeting_error = document.getElementById("request_meeting_error");

    if(check_voip_enabled()) {
        if(request_meeting_error.offsetParent == null) {
            show_easyassist_toast("An audio call has been initiated to the customer.");
        }
        document.getElementById("voip-call-icon").style.display = 'none';
        document.getElementById("voip-calling-icon").style.display = 'block';
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
                    request_meeting_error.innerHTML = "Request has been sent to customer.";
                    request_meeting_error.style.color = 'green';
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

                    if(check_voip_video_meeting_enabled()) {

                        toggle_voip_ringing_sound(false);
                        $("#request_meeting_modal").modal("hide");
                        set_easyassist_cookie("is_cobrowse_meeting_active", COBROWSE_SESSION_ID);
                        show_cobrowse_meeting_option();

                        clearInterval(check_meeting_status_interval);
                        request_meeting_error.innerHTML = "";
                        request_meeting_error.style.color = 'green';
                        var html = document.getElementById("request_meeting_button");
                        var button = '<button class="btn btn-secondary" type="button" data-dismiss="modal">Close</button>\
                            <button class="btn btn-primary" id="request_button" type="button" onclick="request_for_meeting(\'' + session_id + '\')">Request</button>';
                        html.innerHTML = button;

                    } else if(check_voip_enabled()) {

                        toggle_voip_ringing_sound(false);
                        $("#request_meeting_modal").modal("hide");
                        set_easyassist_cookie("is_cobrowse_meeting_active", COBROWSE_SESSION_ID);

                        voip_connect_with_client();

                        clearInterval(check_meeting_status_interval);
                        request_meeting_error.innerHTML = "";
                        request_meeting_error.style.color = 'green';
                        let html = document.getElementById("request_meeting_button");
                        // var button = '<button class="btn btn-secondary" type="button" data-dismiss="modal">Close</button>\
                        //     <button class="btn btn-primary" id="request_button" type="button" onclick="request_for_meeting(\'' + session_id + '\')">Request</button>';
                        let button = '<button class="btn btn-success" type="button" onclick="voip_connect_with_client(\'' + session_id + '\')">Connect</button>\
                            <button class="btn btn-primary" id="request_button" type="button" onclick="request_for_meeting(\'' + session_id + '\')">Resend Request</button>';
                        html.innerHTML = button;
                        document.getElementById("voip-calling-icon").style.display = 'none';
                        document.getElementById("voip-call-icon").style.display = 'block';

                    } else {

                        request_meeting_error.innerHTML = "Meeting request has been accepted by the customer. Please click on 'Connect' to join the meeting."
                        request_meeting_error.style.color = 'green';
                        let html = document.getElementById("request_meeting_button");
                        let button = '<button class="btn btn-success" type="button" onclick="connect_with_client(\'' + session_id + '\')">Connect</button>\
                            <button class="btn btn-primary" id="request_button" type="button" onclick="request_for_meeting(\'' + session_id + '\')">Resend Request</button>';
                        html.innerHTML = button
                        clearInterval(check_meeting_status_interval);
                        connect_with_client(session_id);

                    }
                    auto_msg_popup_on_client_call_declined = false;
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
                                request_meeting_error.innerHTML = "Meeting request has been rejected by customer."
                                request_meeting_error.style.color = 'red';
                                let html = document.getElementById("request_meeting_button");
                                let button = '<button class="btn btn-secondary" type="button" data-dismiss="modal">Close</button>\
                                    <button class="btn btn-primary" id="request_button" type="button" onclick="request_for_meeting(\'' + session_id + '\')">Resend Request</button>';
                                html.innerHTML = button
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
                        if(check_meeting_status_interval) {
                            clearInterval(check_meeting_status_interval);
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

    var is_cobrowse_meeting_active = get_easyassist_cookie("is_cobrowse_meeting_active");
    if(is_cobrowse_meeting_active == COBROWSE_SESSION_ID) {
        if(document.getElementById("cobrowse-voip-container").style.display == 'none') {
            send_agent_meeting_joined_over_socket();
            try {
                if(IS_MOBILE == "True") {
                    document.getElementById("request-cobrowsing-meeting-btn").parentNode.parentNode.style.display = "none";
                } else {
                    document.getElementById("request-cobrowsing-meeting-btn").style.display = 'none';
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
            .then((stream) => {
                captured_video_stream = stream;
                video_element.srcObject = stream;
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

        var is_cobrowse_meeting_active = get_easyassist_cookie("is_cobrowse_meeting_active");
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
        var custom_dropdown_options = "";
        var custom_dropdown_selected_option_wrapper = "";

        // Create elements
        custom_dropdown_wrapper = create_element('div', 'easyassist-custom-dropdown-container');
        custom_dropdown_option_container = create_element('ul', 'easyassist-custom-dropdown-option-container');
        custom_dropdown_selected_option_wrapper = create_element('div', 'easyassist-dropdown-selected');
        // select_element.wrap(custom_dropdown_wrapper);

        select_element.parentNode.prepend(custom_dropdown_wrapper);
        custom_dropdown_wrapper.appendChild(select_element)

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

        custom_dropdown_option_container.innerHTML = custom_dropdown_options;
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
    }
}

function find_light_color(color, percent) {
    var R = parseInt(color.substring(1,3),16);
    var G = parseInt(color.substring(3,5),16);
    var B = parseInt(color.substring(5,7),16);

    R = parseInt(R * (100 + percent) / 100);
    G = parseInt(G * (100 + percent) / 100);
    B = parseInt(B * (100 + percent) / 100);

    R = (R<255)?R:255;  
    G = (G<255)?G:255;  
    B = (B<255)?B:255;  

    var rgba_color = "rgba(" + R + "," + G + "," + B + ",0.4)"
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
    document.getElementById("voip-initiated-agent-name").innerHTML = "Agent " + voip_meeting_initiated_agent;
    $('#invited_agent_voip_meeting_connect_modal').modal('show');
}

function connect_voip_meeting() {
    set_easyassist_cookie("is_cobrowse_meeting_active", COBROWSE_SESSION_ID);
    show_cobrowse_meeting_option();
    hide_invited_agent_voip_connect_modal();
}

function hide_invited_agent_voip_connect_modal() {
    $('#invited_agent_voip_meeting_connect_modal').modal('hide');
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
