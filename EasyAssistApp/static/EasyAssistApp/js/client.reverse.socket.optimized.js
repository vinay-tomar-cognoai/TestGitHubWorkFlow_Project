var easyassist_tree_mirror = null;
//var client_base_href = null;

var easyassist_drawing_canvas = null;
var easyassist_drag_element = null;

var easyassist_send_agent_weak_connection_message_interval = null;
var framesContainer = document.querySelector('#frames-container');
//var currentFrameIdx = 0;
var playbackIntervalId = null;
//var cobrowseSocket = null;
var is_page_reloaded = false;
var sync_client_web_screen_timer = null;
var cobrowsing_meta_data_page = 1;
var load_more_meta = false;
var client_websocket_open = false;
var client_websocket = null;
var chunk_html_dict = {};
var internet_connectivity_timer = null;
var INTERNET_CON_TIMER = 30000;
var client_mouse_element = document.getElementById("client-mouse-pointer");
var margin_left_client_frame_container = 0;
var margin_top_client_frame_container = 0;
var requested_for_edit_access = false;
var ALLOW_SCREENSHARING_COBROWSE = false;
var easyassist_tickmarks_clicked=new Array(11).fill(false);
var close_nav_timeout = null;
var sync_utils_client_websocket_open = false;
var sync_utils_client_websocket = null;
window.EASYASSIST_CLIENT_FEEDBACK = null;
var client_iframe_width = 0;
var client_iframe_height = 0;
var EASYASSIST_IFRAME_ID = 0;
var meeting_join_modal_shown = false;
var global_event_target_element = null;

var agent_pointer_position = {
    pageX: 0,
    pageY: 0,
    clientX: 0,
    clientY: 0,
    upper_hidden_pixel: 0,
}

var user_last_activity_time_obj = new Date()

var EASYASSIST_FUNCTION_FAIL_DEFAULT_CODE = 500;
var EASYASSIST_FUNCTION_FAIL_DEFAULT_MESSAGE = "Due to some network issue, we are unable to process your request. Please Refresh the page.";
var easyassist_function_fail_time = 0;
var easyassist_function_fail_count = 0;


var agent_scale_factor = 1;
var frame_container_parent_height = 0;
var frame_container_parent_width = 0;
var session_has_ended = false;

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

                var description = "error occured customer websocket. " + e.data;
                save_easyassist_system_audit_trail("socket", description);
            }
        client_websocket.onopen = function(){
                console.log("client_websocket created successfully") 
                client_websocket_open = true;
                easyassist_request_html_page();
            }
        client_websocket.onclose = function() {
                client_websocket_open = false;
                client_websocket = null;

                var description = "customer websocket is closed";
                save_easyassist_system_audit_trail("socket", description);
            }
    }
}

function easyassist_close_socket() {

    if (client_websocket == null) {
        return;
    }

    try{
        client_websocket.close();
    }catch(err){
        client_websocket.onmessage = null;
        client_websocket = null;
    }

}

function send_message_over_easyassist_socket(message, sender) {
    try{
        if(client_websocket_open == false || client_websocket == null){
            if(send_message_over_easyassist_socket.caller.name == "easyassist_socket_callback"){
                return;
            }
            setTimeout(function easyassist_socket_callback(){
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

                var description = "error occured customer websocket utils. " + e.data;
                save_easyassist_system_audit_trail("socket", description);
            }
        sync_utils_client_websocket.onopen = function(){
                console.log("sync_utils_client_websocket created successfully") 
                sync_utils_client_websocket_open = true;
                if(window.IS_AGENT == "False"){
                    send_customer_join_over_socket();
                }
            }
        sync_utils_client_websocket.onclose = function() {
                sync_utils_client_websocket_open = false;
                sync_utils_client_websocket = null;

                var description = "customer utils websocket is closed";
                save_easyassist_system_audit_trail("socket", description);
            }
    }
}

function close_sync_utils_easyassist_socket() {

    if(sync_utils_client_websocket == null) {
        return;
    }

    try{
        sync_utils_client_websocket.close();
    }catch(err){
        sync_utils_client_websocket.onmessage = null;
        sync_utils_client_websocket = null;
    }

}

function send_message_over_sync_utils_easyassist_socket(message, sender) {
    try{
        if(sync_utils_client_websocket_open == false || sync_utils_client_websocket == null){
            if(send_message_over_sync_utils_easyassist_socket.caller.name == "easyassist_socket_callback"){
                return;
            }
            setTimeout(function easyassist_socket_callback(){
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
    }catch(err){
        console.error("ERROR : send_message_over_sync_utils_easyassist_socket ", err);
    }
}

function easyassist_request_html_page(){

    json_string = JSON.stringify({
        "type": "html",
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");
}

/******************* END EASYASSIST UTILITY WEBSOCKET ************************/

var easyassist_socket_not_open_count = 0;
var easyassist_socket_utils_not_open_count = 0;
var easyassist_socket_activity_interval_check = setInterval(easyassist_initialize_web_socket, 1000);

function easyassist_initialize_web_socket() {

    var easyassist_session_id = COBROWSE_SESSION_ID;
    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    if (client_websocket == null) {
        create_easyassist_socket(COBROWSE_SESSION_ID, "agent");
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
        create_sync_utils_easyassist_socket(COBROWSE_SESSION_ID, "agent");
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

/******************* WEBSOCKET END ************************/

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
    if(window.IS_AGENT == "True") {
        if(check_voip_video_meeting_enabled() || check_voip_enabled() || check_video_calling_enabled()) {
            check_is_meeting_active_over_socket();
        }
    }
    document.getElementById("mySidenav").style.display = "";
    document.getElementById("maximise-button").style.display = "none";
}

function closeNav() {
    document.getElementById("mySidenav").style.display = "none";
    document.getElementById("maximise-button").style.display = "";
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

    if(window.IS_AGENT == "True"){
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
    delete_easyassist_cookie("easyassist_client_disconnected_modal_shown");
    delete_easyassist_cookie("easyassist_client_weak_internet_connection_shown");
    delete_easyassist_cookie("is_pdf_modal_open");
    easyassist_clear_local_storage();
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
        reset_internet_connectivity_check_timer();
    }, INTERNET_CON_TIMER);
}

function open_close_session_modal() {
    if(window.ENABLE_CHAT_BUBBLE == "True") {
        livechat_iframe = document.getElementById("allincall-chat-box");
        if(livechat_iframe.classList.contains("animate__slideInUp")) {
            livechat_iframe.classList.remove("animate__slideInUp");
        }

        if (window.FLOATING_BUTTON_POSITION == "right") {
            livechat_iframe.classList.add("allincall-scale-out-br-right-side")
        } else {
            livechat_iframe.classList.add("allincall-scale-out-br");
        }
        
    } else {
        document.getElementById("allincall-chat-box").style.display = "none";
    }
    $("#close_session_modal").modal("show");
    framesContainer.style.filter = "blur(3px)";
}

$("#close_session_modal").on("hidden.bs.modal", function() {
    reset_easyassist_rating_bar();
    gain_focus();
});

function gain_focus(){
  framesContainer.style.filter = null;
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

    // STORAGE SOLN REV
    // window.addEventListener("storage", function (e) {

    //     if(e.key == "easyassist_session") {
    //         var new_value = e.newValue;
    //         if(new_value.hasOwnProperty(COBROWSE_SESSION_ID)) {
    //             new_value = new_value[COBROWSE_SESSION_ID]
    //             if(new_value.hasOwnProperty("is_cobrowse_meeting_active")) {
    //                 if(new_value["is_cobrowse_meeting_active"] == "" && get_easyassist_cookie("is_cobrowse_meeting_active") == COBROWSE_SESSION_ID) {
    //                     if(window.IS_AGENT == "True") {
    //                         set_easyassist_cookie("is_cobrowse_meeting_active", "");
    //                         hide_side_nav_call_icon();
    //                         set_easyassist_current_session_local_storage_obj("is_call_ongoing_invited_agent", "false");
    //                     }
    //                 }
    //             }
    //         }
    //     }
    // }, false);
    // ele = document.getElementById("join-voice-call-meeting-btn")
    // if(ele != undefined){
    //     ele.style.display = "none"
    // }

    // delete_easyassist_cookie("voice_call_triggered")

    sync_client_web_screen_timer = setInterval(function(e) {
        agent_heartbeat();
    }, 5000);

    sync_client_web_screen_agent_timer = setInterval(function(e) {
        sync_client_web_screen_agent();
    }, 10000);
    send_agent_name();
    sync_client_web_screen_agent();
    reset_internet_connectivity_check_timer();
    load_chat_history();

    if(window.IS_AGENT == "True" && window.AGENT_JOINED_FIRST_TIME == "True"){
        let local_storage_obj = get_easyassist_current_session_local_storage_obj();
        if(local_storage_obj && !local_storage_obj.hasOwnProperty("agent_joined_chat_bubble_sent")) {
            setTimeout(easyassist_invite_agent_joined, 3000);
            set_easyassist_current_session_local_storage_obj("agent_joined_chat_bubble_sent", "true");
        }
    }
    
    check_is_meeting_active_over_socket(true);

    if(window.IS_AGENT == "False"){
        update_edit_access_icon_properties();
        easyassist_save_customer_location();
    }

    setTimeout(function(){
        var local_storage_obj = get_easyassist_current_session_local_storage_obj();
        if(local_storage_obj && local_storage_obj.hasOwnProperty("new_message_seen")) {
            if(local_storage_obj["new_message_seen"] == "false") {
                $(".chat-talk-bubble").removeClass("bounce2");
                try {
                    document.getElementById("talktext-p").innerHTML = local_storage_obj["last_message"]
                } catch(err) {}
                $(".chat-talk-bubble").css({"display":"block"});
                $(".chat-talk-bubble").addClass("bounce2");
                play_greeting_bubble_popup_sound();
            }
            setTimeout(function(){
                $(".chat-talk-bubble").removeClass("bounce2");
            },1500);
         }
        },2500);

    easyassist_initialize_drawing_canvas();
    easyassist_initialize_drag_element();

    setTimeout(function() {
        check_edit_access_apply_coview_listener();
    }, 8000);
};

window.addEventListener('resize', function() { 
    if(client_iframe_width && client_iframe_height) {
        resize_iframe_container(client_iframe_width, client_iframe_height);
    }
    easyassist_drag_element.relocate_element();
});

function create_and_iframe(html) {
    // html = EasyAssistLZString.decompress(html);
    EASYASSIST_IFRAME_ID += 1;

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
        renderFrame(dataset);
    };
    is_page_reloaded = false;
    edit_access_update();
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

    if(ALLOW_SCREENSHARING_COBROWSE == 'True' || ALLOW_SCREENSHARING_COBROWSE == 'true' || ALLOW_SCREENSHARING_COBROWSE == true) {
        return ;
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

    easyassist_resize_drawing_canvas(frame_container_parent_width, frame_container_parent_height)
}

function update_edit_access_icon_properties() {
    if (document.getElementById("easyassist-edit-access-icon") != undefined) {
        if (get_easyassist_cookie("request_edit_access") == COBROWSE_SESSION_ID) {
            if(IS_MOBILE == "True") {
                document.getElementById("easyassist-edit-access-icon").setAttribute("data-target", "");
                document.getElementById("easyassist-edit-access-icon").setAttribute("onclick", "hide_cobrowsing_modals(this);revoke_easyassist_edit_access();");
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
                document.getElementById("easyassist-edit-access-icon").setAttribute("onclick", "hide_cobrowsing_modals(this);revoke_easyassist_edit_access();");
                document.getElementById("easyassist-edit-access-icon").children[1].children[1].innerText = "Revoke Edit Access";
                document.getElementById("easyassist-edit-access-icon").style.backgroundColor = find_light_color(FLOATING_BUTTON_BG_COLOR, 300);
            }
        } else {
            if(IS_MOBILE == "True") {
                document.getElementById("easyassist-edit-access-icon").setAttribute("data-target", "#request_for_edit_access_modal");
                document.getElementById("easyassist-edit-access-icon").setAttribute("onclick", "hide_cobrowsing_modals(this);");
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
                document.getElementById("easyassist-edit-access-icon").setAttribute("onclick", "hide_cobrowsing_modals(this);");
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
    if (get_easyassist_cookie("request_edit_access") == COBROWSE_SESSION_ID) {
        action = "initial";
    } else {
        action = "none";
    }
    frame_child = framesContainer.children[0];
    frame_child.style.pointerEvents = "initial";
    frame_child.style.webkitUserSelect = action;
    frame_child.style.mozUserSelect = action;
    frame_child.style.msUserSelect = action;
    frame_child.style.oUserSelect = action;
    frame_child.style.userSelect = action;
}

function sync_client_web_screen(e) {

    try{
        var data = JSON.parse(e.data);
        message = data.message;
        client_packet = message.body.Request;
    } catch (err){
        console.log(err);
        console.log("message = ", message);
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
        if (client_packet.type == "restricted_url") {
            show_easyassist_loader(true);
        }

        // if(client_packet.type == "voice_call_triggered"){
        //     set_easyassist_cookie("voice_call_triggered", "true")
        //     $('#request_voip_meeting_modal_invited_agent .modal-text').text('Would You like to join voice call?')
        //     $('#request_voip_meeting_modal_invited_agent .modal-footer').html('<button class="btn btn-secondary" type="button" data-dismiss="modal">No</button>' +
        //     '<button class="btn btn-primary" id="request_button" type="button" onclick="join_meeting_invited_agent();">Yes</button>');
        //     $('#request_voip_meeting_modal_invited_agent').modal('show');
        // }

        // if(client_packet.type == "reset_cookies"){
        //     delete_easyassist_cookie("voice_call_triggered")
        //     reset_voip_meeting();
        // }

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

        } else if (client_packet.type == "pageshot") {
            if(window.IS_AGENT == "True"){
                return;
            }
            if (client_packet.result == 200) {
                show_easyassist_toast("Screenshot captured successfully. Please click on View Screenshot to download it");
            } else {
                show_easyassist_toast("Unable to capture the client screenshot. Kindly try again later or connect with application administrator.");
            }

        } else if (client_packet.type == "mouse") {

            if(ALLOW_SCREENSHARING_COBROWSE == 'True' || ALLOW_SCREENSHARING_COBROWSE == 'true' || ALLOW_SCREENSHARING_COBROWSE == true) {

                return ;
            }
            // client_mouse_element.style.top = client_packet.position.clientY + "px";
            // client_mouse_element.style.left = (margin_left_client_frame_container + client_packet.position.clientX) + "px";
            var factor_y = frame_container_parent_height / client_iframe_height;
            var client_pos_y = (margin_top_client_frame_container + client_packet.position.clientY * factor_y);
            var client_pos_x = (margin_left_client_frame_container + client_packet.position.clientX * agent_scale_factor);
            client_mouse_element.style.top = client_pos_y + "px";
            client_mouse_element.style.left = client_pos_x + "px";

        }  else if(client_packet.type == "client_tab_not_focus") {
            
            if(client_packet.action == "navigation") {
                easyassist_show_long_toast("You cannot perform this action as the agent is focused on a different tab.<br>\
                    Please request the agent to navigate back to the co-browsing tab and try again.")
            } else {
                easyassist_show_long_toast("Document preview is currently disabled as the agent is focused on a different tab.<br>\
                    Please request the agent to navigate back to the co-browsing tab and try again.")
            }
        
        } else if (client_packet.type == "apply_coview_listener") {
            set_easyassist_current_session_local_storage_obj("pdf_modal_easyassist_id", client_packet.element_id);
            easyassist_apply_pdf_coview_pointer_events(client_packet.element_id);
            set_easyassist_cookie("is_pdf_modal_open", "true");

        } else if (client_packet.type == "remove_coview_listener") {

            delete_easyassist_cookie("is_pdf_modal_open");
            easyassist_apply_pdf_coview_pointer_events(client_packet.element_id, "none");
            set_easyassist_current_session_local_storage_obj("pdf_modal_easyassist_id", "");

        } else if(client_packet.type == "client_tab_close") {

            show_easyassist_client_end_page_loader();

        } else if (client_packet.type == "chat") {
            set_client_response(client_packet.message, client_packet.attachment, client_packet.attachment_file_name, client_packet.name, client_packet.sender, client_packet.chat_type, client_packet.agent_profile_pic_source);

        } else if (client_packet.type == "element_value") {
            if(ALLOW_SCREENSHARING_COBROWSE == 'True' || ALLOW_SCREENSHARING_COBROWSE == 'true' || ALLOW_SCREENSHARING_COBROWSE == true) {

                return ;
            }

            if (framesContainer.children.length > 0) {

                frame_child = framesContainer.children[0];

                html_elements_value_list = client_packet.html_elements_value_list;

                for(let html_element_index = 0; html_element_index < html_elements_value_list.length; html_element_index++) {

                    html_element = html_elements_value_list[html_element_index];
                    tag_name = html_element.tag_name;
                    tag_type = html_element.tag_type;
                    easyassist_element_id = html_element.easyassist_element_id;
                    value = html_element.value;
                    is_active = html_element.is_active;

                    frame_element = easyassist_get_element_from_easyassist_id(easyassist_element_id);

                    if (frame_element == null || frame_element == undefined) {
                        console.log("Element not found");
                        continue;
                    }

                    if (tag_name.toLowerCase() == "select") {

                        // if (html_element.is_obfuscated_element) {
                        //     var obfuscated_option = document.createElement("option");
                        //     obfuscated_option.value = "******";
                        //     obfuscated_option.innerHTML = "******";
                        //     frame_element.appendChild(obfuscated_option);
                        //     value = "******";
                        // }

                        for(let option_index = 0; option_index < frame_element.options.length; option_index++) {
                            frame_element.options[option_index].removeAttribute("selected");
                            if (frame_element.options[option_index].innerHTML == value) {
                                frame_element.options[option_index].setAttribute("selected", "selected");
                            }
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
                }
            }

        } else if (client_packet.type == "request-edit-access") {
            if(window.IS_AGENT == "True"){

                /*

                if (client_packet.is_allowed == "none") {
                    if("agent_revoke_edit_access" in client_packet) {
                        show_easyassist_toast("Edit access has been revoked by customer");
                    }else {
                        show_easyassist_toast("Agent has revoked edit access from customer");
                    }
                } else {
                    if (client_packet.is_allowed == "true") {
                        show_easyassist_toast("Agent has provided edit access to the customer.");
                    } else if (client_packet.is_allowed == "false") {
                        show_easyassist_toast("Agent has denied edit access to the customer.");
                    }
                }

                */
                return;
            }

            if(ALLOW_SCREENSHARING_COBROWSE == 'True' || ALLOW_SCREENSHARING_COBROWSE == 'true' || ALLOW_SCREENSHARING_COBROWSE == true) {

                return ;
            }

            frame_child = framesContainer.children[0];

            if (client_packet.is_allowed == "none") {
                delete_easyassist_cookie("request_edit_access");
                if("agent_revoke_edit_access" in client_packet) {
                    save_easyassist_system_audit_trail("edit_access", "agent_revoked_edit_access");
                    show_easyassist_toast("Edit access has been revoked");
                }else {
                    save_easyassist_system_audit_trail("edit_access", "client_revoked_edit_access");
                    show_easyassist_toast("Agent has revoked edit access");
                }
            } else if (requested_for_edit_access == true) {
                requested_for_edit_access = false;

                if (client_packet.is_allowed == "true") {
                    set_easyassist_cookie("request_edit_access", COBROWSE_SESSION_ID);
                    save_easyassist_system_audit_trail("edit_access", "client_provided_edit_access");
                    show_easyassist_toast("Agent has provided edit access to you");
                } else if (client_packet.is_allowed == "false") {
                    delete_easyassist_cookie("request_edit_access");
                    save_easyassist_system_audit_trail("edit_access", "client_denied_edit_access");
                    show_easyassist_toast("Agent has denied edit access to the form.");
                }
            }

            edit_access_update();
            easyassist_update_edit_access();
            update_edit_access_icon_properties();
            check_edit_access_apply_coview_listener();

        } else if(client_packet.type == "end_voip_meeting") {
            if(client_packet.auto_end_meeting) {
                show_easyassist_toast("Call ended");
            } else {
                show_easyassist_toast("Agent ended the call");
            }
            // reset_voip_meeting();
            // delete_easyassist_cookie("voice_call_triggered");
            setTimeout(function() {
                end_cobrowse_video_meet(true);
            }, 1000);
        } else if(client_packet.type == "voip_meeting_ready") {
            show_easyassist_toast("Agent joined the call");
            set_easyassist_cookie("is_customer_voip_meeting_joined", COBROWSE_SESSION_ID);
        } else if(client_packet.type == "div-scroll") {
            try {
                value_top = client_packet.value_top;
                value_left = client_packet.value_left;
                element_id = client_packet.element_id;
                element_attr_id = client_packet.id;
                element = null;

                element = easyassist_get_element_from_easyassist_id(element_id);

                if (element == null || element == undefined) {
                    console.log("Element not found");
                } else {
                    element.scrollTop = value_top;
                    element.scrollLeft = value_left;
                }
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
                let element = framesContainer.children[0].contentDocument.querySelector("[easyassist-element-id='" + parent_element_id + "']");

                for(let idx = 0; idx < element.children.length; idx ++) {
                    var child_id = element.children[idx].getAttribute('easyassist-element-id');
                    if(child_id != undefined && child_id != null && !child_list.has(child_id)) {
                        element.children[idx].remove();
                    }
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
        }  else if (client_packet.type == "livechat-typing") {
            allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow;
            allincall_chat_window.postMessage(JSON.stringify({
                "id": "livechat-typing",
                "role": client_packet.role,
                "name": client_packet.name
            }), window.location.protocol + "//" + window.location.host);
        } else if( client_packet.type == "client_weak_connection" ){
            if(window.IS_AGENT == "True"){
                return;
            }
            if(get_easyassist_cookie("easyassist_session_id")){
                if(get_easyassist_cookie("easyassist_client_weak_internet_connection_shown") == undefined || get_easyassist_cookie("easyassist_client_weak_internet_connection_shown") == "false"){
                    show_client_weak_internet_connectio_modal();
                    set_easyassist_cookie("easyassist_client_weak_internet_connection_shown", "true")
                }
            }
        } else if (client_packet.type == "screenshot") {
            if(window.IS_AGENT == "True"){
                return;
            }
            var agent_name = client_packet.agent_name;
            if (agent_name && agent_name.length) {
                show_easyassist_toast("Agent " + agent_name + " took a screenshot")
            } else {
                show_easyassist_toast("Agent " + "took a screenshot")
            }
        } else if(client_packet.type == "html_initialize") {

            initialize_easyassist_iframe(client_packet.props);
            easyassist_tree_mirror[client_packet.f].apply(easyassist_tree_mirror, client_packet.args);
            hide_easyassist_client_end_page_loader();

        } else if(client_packet.type == "html_change") {

            easyassist_update_styled_component_css(client_packet.css_text);

            easyassist_tree_mirror[client_packet.f].apply(easyassist_tree_mirror, client_packet.args);

        } else if(client_packet.type == "client_screen_resize") {

            resize_iframe_container(client_packet.window_width, client_packet.window_height);

        }  else if(client_packet.type == "sync_canvas") {

            easyassist_sync_agent_canvas(client_packet);

        } else if(client_packet.type == "reset_canvas") {

            easyassist_reset_agent_canvas();

        } else if (client_packet.type == "is_meeting_active_response") {
            if (window.IS_AGENT == "True") {
                if (client_packet.is_meeting_active) {
                    // flag maintained at invited agents end which depicts if call is ongoing or not.
                    set_easyassist_current_session_local_storage_obj("is_call_ongoing_invited_agent", "true");
                    if(client_packet.show_modal) {
                        // show "agent and client are already connected" modal
                        show_meeting_join_modal_to_agent();
                    }
                    show_side_nav_call_icon();
                } else {
                    hide_side_nav_call_icon();
                    set_easyassist_current_session_local_storage_obj("is_call_ongoing_invited_agent", "false");
                }
            }
        } else if (client_packet.type == "invited_agent_call_request") {
            if(window.IS_AGENT == "True") {
                reset_call_modal_text();
                set_easyassist_current_session_local_storage_obj("is_call_ongoing_invited_agent", "true");
                show_side_nav_call_icon();
                if(client_packet.is_call_ongoing) {
                    show_meeting_join_modal_to_agent();
                } else {
                    $("#request_meeting_modal_invited_agent").modal("show");
                }
            }
        }
    } else {

        if(window.IS_AGENT == "True"){

            if (client_packet.type == "sync-scroll") {
                if(ALLOW_SCREENSHARING_COBROWSE == 'True' || ALLOW_SCREENSHARING_COBROWSE == 'true' || ALLOW_SCREENSHARING_COBROWSE == true) {

                    return ;
                }
                let scrollX = client_packet.data_scroll_x;
                let scrollY = client_packet.data_scroll_y;
                if (framesContainer.children.length > 0) {
                    prev_frame = framesContainer.children[0];
                    prev_frame.contentWindow.scrollTo(scrollX, scrollY);
                }

            } else if (client_packet.type == "chat") {
                // I am invited agent && and received message is not mine but from another invited agent
                if(window.INVITED_AGENT_USERNAME != client_packet.sender){
                    set_client_response(client_packet.message, client_packet.attachment, client_packet.attachment_file_name, client_packet.agent_name, client_packet.sender, client_packet.chat_type,client_packet.agent_profile_pic_source);
                }
            } else if (client_packet.type == "livechat-typing"){
                if(client_packet.name != window.INVITED_AGENT_NAME){
                    allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow;
                    allincall_chat_window.postMessage(JSON.stringify({
                        "id": "livechat-typing",
                        "role": client_packet.role,
                        "name": client_packet.name
                    }), window.location.protocol + "//" + window.location.host);
                }
            }  else if (client_packet.type == "sync-form") {

                var tag_name = client_packet.tag_name;
                var tag_type = client_packet.tag_type;
                var element_id = client_packet.easyassist_element_id;
                var value = client_packet.value;
                var element_attr_id = client_packet.element_attr_id;
                var change_element = null;

                if (element_attr_id != null && element_attr_id != undefined) {
                    var frame = framesContainer.children[0];
                    change_element = frame.contentDocument.querySelector("[id='" + element_attr_id + "']");
                } 

                if(change_element == null) {
                    change_element = easyassist_get_element_from_easyassist_id(element_id);
                }

                if(change_element == null || change_element == undefined) {
                    console.log("Danger: Element does not exist");
                    return;
                }

                if (tag_name == "select") {

                    if (change_element.options == undefined || change_element.options == null) {
                        return;
                    }

                    var option_value = value;
                    for(let option_index = 0; option_index < change_element.options.length; option_index++) {
                        change_element.options[option_index].removeAttribute("selected");
                        if (change_element.options[option_index].innerHTML == value) {
                            change_element.options[option_index].setAttribute("selected", "selected");
                            option_value = change_element.options[option_index].value;
                        } else if(change_element.options[option_index].value == value) {
                            change_element.options[option_index].setAttribute("selected", "selected");
                            option_value = change_element.options[option_index].value;
                        }
                    }

                    change_element.value = option_value;

                } else if (tag_name == "input") {

                    if (tag_type == "checkbox") {
                        change_element.click();
                    } else if (tag_type == "radio") {
                        change_element.click();
                    } else {
                        change_element.value = value;
                    }

                } else if(tag_name == "textarea") {
                    change_element.value = value;

                } else {
                    change_element.innerHTML = value;

                }
            } else if(client_packet.type == "div-scroll") {
                try {
                    var value_top = client_packet.value_top;
                    var value_left = client_packet.value_left;
                    let element_id = client_packet.element_id;
                    let element_attr_id = client_packet.element_id_attr;
                    let element = null;

                    if (element_attr_id != null && element_attr_id != undefined) {
                        let frame = framesContainer.children[0];
                        element = frame.contentDocument.querySelector("[id='" + element_attr_id + "']");
                    } 

                    if(element == null) {
                        element = easyassist_get_element_from_easyassist_id(element_id);
                    }

                    if (element == null || element == undefined) {
                        console.log("Element not found");
                    } else {
                        element.scrollTop = value_top;
                        element.scrollLeft = value_left;
                    }

                } catch(err) {}

            }
        } else if (window.IS_AGENT == "False") {
            
            if (client_packet.type == "chat") {
                // I am customer && received a message from invited agent
                if(client_packet.sender != "client"){
                    set_client_response(client_packet.message, client_packet.attachment, client_packet.attachment_file_name, client_packet.agent_name, client_packet.sender, client_packet.chat_type,client_packet.agent_profile_pic_source);
                }
            } else if (client_packet.type == "invited_agent_joined"){
                show_easyassist_toast("Agent " + client_packet.invited_agent_name + " has joined the session.")
            } else if (client_packet.type == "invited_agent_left"){
                show_easyassist_toast("Agent " + client_packet.invited_agent_name + " has left the session.")
            } else if (client_packet.type == "livechat-typing"){
                if(client_packet.name != window.CLIENT_NAME){
                    allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow;
                    allincall_chat_window.postMessage(JSON.stringify({
                        "id": "livechat-typing",
                        "role": client_packet.role,
                        "name": client_packet.name
                    }), window.location.protocol + "//" + window.location.host);
                }
            }
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

    return;

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

function is_edit_access() {
    if(window.IS_AGENT == "True") return false;
    if(get_easyassist_cookie("request_edit_access") == COBROWSE_SESSION_ID)
        return true;
    return false;
}

function renderFrame(dataset) {

    //console.log("frame is loaded rendering ifrmae");

    setTimeout(function() {

        // event.preventDefault();

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

            resize_iframe_container(dataset.window_width, dataset.window_height);

            frame.hidden = false;
            document.getElementById("easyassist-loader").style.display = 'none';

            var scrollX = parseInt(dataset.scrollX);
            var scrollY = parseInt(dataset.scrollY);
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
                if(is_edit_access()) {
                    add_easyassist_event_listner_into_element(frame.contentDocument.body, "mousedown", easyassist_update_global_event_target);
                    add_easyassist_event_listner_into_element(frame.contentDocument.body, "click", button_click_client_element);
                }
            } catch {
                console.log("Iframe body does not exist")
            }

            $("#allincall-chat-box")[0].contentWindow.document.onmousemove = function(event) {
                sync_mouse_position(event, is_from_chat_window = true);
            }

        }

        easyassist_update_edit_access();

        document.getElementById("easyassist-loader").style.display = "none";

    }, 800);
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

        if(dom_node.classList.contains("page-count") || dom_node.classList.contains("page-move") || dom_node.classList.contains("modal-body") || dom_node.classList.contains("page-move-mobile") ) {
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


function easyassist_update_edit_access() {

    if(get_easyassist_cookie("is_pdf_modal_open") == "true")
        return;

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
            dom_node.classList.remove('easyassist-blured-element');
            dom_node.disabled = false;
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

        if(dom_node.hasAttribute("easyassist-obfuscate")) {
            if(window.IS_AGENT == "False") {
                // If Customer
                dom_node.classList.remove('easyassist-blured-element');
                dom_node.disabled = false;
            }
        }

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
            remove_easyassist_event_listner_into_element(dom_node, "change", detect_agent_value_change);

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

function button_click_client_element(event) {

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

    event.preventDefault();

    easyassist_element_id = easyassist_get_easyassist_id_from_element(currentBtn);
    if (easyassist_element_id == null || easyassist_element_id == undefined) {
        easyassist_element_id = "";
    }
    json_string = JSON.stringify({
        "type": "button-click",
        "element_id": "",
        "easyassist_element_id": easyassist_element_id
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
        })

        encrypted_data = easyassist_custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };

        send_message_over_easyassist_socket(encrypted_data, "agent");
    } catch(err) {}
}


function take_client_screenshot(type) {

    json_string = JSON.stringify({
        "type": type
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

function close_agent_confirm_session(element, is_feedback) {

    var comments_error = document.getElementById("colose-session-remarks-error");
    comments_error.style.display = "none";
    comments_error.innerHTML = "";

    comments = document.getElementById("close-session-remarks").value;
    if(comments) {
        comments = comments.trim();
    }

    if (window.EASYASSIST_CLIENT_FEEDBACK == null || is_feedback == false) {
        rating = "None";
    } else {
        rating = window.EASYASSIST_CLIENT_FEEDBACK;
    }

    try {
        if(comments.length > 200) {
            comments_error.innerHTML = "Remarks cannot be more than 200 characters";
            comments_error.style.display = "block";
            return;
        }
    } catch(err) {}

    comments = remove_special_characters_from_str(comments);

    window.EASYASSIST_CLIENT_FEEDBACK = null;
    

    json_string = JSON.stringify({
        "session_id": COBROWSE_SESSION_ID,
        "comments": comments,
        "rating": rating
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    if(is_feedback == true)
        element.innerHTML = "Submitting...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/reverse/client-close-session/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status == 200) {

                delete_easyassist_cookie("easyassist_client_weak_internet_connection_shown");
                delete_easyassist_cookie("easyassist_client_disconnected_modal_shown");
                clearInterval(easyassist_send_agent_weak_connection_message_interval);

                json_string = JSON.stringify({
                    "type": "end_session",
                });

                encrypted_data = easyassist_custom_encrypt(json_string)
                encrypted_data = {
                    "Request": encrypted_data
                };

                send_message_over_easyassist_socket(encrypted_data, "client");

                window.location.reload();
            } else {
                element.innerHTML = "Close";
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

    if (load_more_meta == false) {
        cobrowsing_meta_data_page = 1;
        document.getElementById("meta_information_body").innerHTML = "Loading...";
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
                var tbody_html = '';
                meta_information_list = response.meta_information_list;
                for(let index = 0; index < meta_information_list.length; index++) {
                    meta_id = meta_information_list[index]["id"];
                    //if (meta_information_list[index]["type"] == "screenshot") {
                    tbody_html += '<tr><td>' + meta_information_list[index]["type"] + '</td><td>' + meta_information_list[index]["datetime"] + '</td><td><!--<a href="/easy-assist/agent/export/' + meta_id + '/?type=img" target="_blank" title="Export As Image"><i class="fas fa-fw fa-download"></i></a>-->&nbsp;<a href="/easy-assist/agent/export/' + meta_id + '/?type=png" target="_blank" title="Export As PNG"><i class="fas fa-fw fa-file-download"></i></a></td></tr>';
                    //} else {
                    //    tbody_html += '<tr><td>' + meta_information_list[index]["type"] + '</td><td>' + meta_information_list[index]["datetime"] + '</td></tr>';
                    //}
                }

                if (response.is_last_page == false) {
                    tbody_html += '<tr onclick="load_more_meta_information(this)"><td colspan="2"><button class="btn btn-primary float-right">Load More</button></td></tr>';
                }

                if (cobrowsing_meta_data_page == 1) {
                    document.getElementById("meta_information_body").innerHTML = tbody_html;
                } else {
                    document.getElementById("meta_information_body").innerHTML += tbody_html;
                }
            } else {
                console.error("Unable to load the details. Kindly try again.");
            }
            load_more_meta = false;
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


function share_cobrowsing_session(element) {

    document.getElementById("share-session-error").innerHTML = "";

    support_agents = $("#multiple-support-agent").val();

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

    element.innerHTML = "sharing..";
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
            }
            element.innerHTML = "Share";
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


////////////////////////////////////////////////////

/*WebSocket Utilities - Starts*/

function open_easyassist_websocket() {
    client_websocket_open = true;
    //console.log("easyassist WebSocket is opened");

    json_string = JSON.stringify({
        "type": "html"
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    //console.log("request for html has been sent: ", new Date());
    send_message_over_easyassist_socket(encrypted_data, "agent");

    send_customer_join_over_socket();
}

function close_easyassist_websocket() {
    client_websocket_open = false;
    //console.log("easyassist WebSocket is closed");
    var description = "agent websocket is closed";
}

function check_socket_status(e) {
    console.error("WebSocket error observed:", e);
    var description = "error occured agent websocket. " + e.data;
}

function close_easyassist_socket() {
    if (client_websocket == null) {
        return;
    }
    client_websocket.close();
}

if (window.addEventListener) {
    window.addEventListener('load', initiate_internet_speed_detection, false);
} else if (window.attachEvent) {
    window.attachEvent('onload', initiate_internet_speed_detection);
}

var speedMbps = 0;
var internet_iteration = 3;

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
    if (avg_speedMbps < 1) {
        show_weak_internet_connectivity_modal();
        if(window.IS_AGENT == "False"){
            easyassist_send_agent_weak_connection_message_interval = setInterval(easyassist_send_agent_weak_connection_message, 5000);
            easyassist_send_agent_weak_connection_message();
        }
    }
}

function easyassist_send_agent_weak_connection_message() {

    json_string = JSON.stringify({
        "type": "agent_weak_connection",
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function sync_client_web_screen_agent() {

    if(window.IS_AGENT == "True"){
        sync_invited_agents_tatus();
        return;
    }

    json_string = JSON.stringify({
        "session_id": COBROWSE_SESSION_ID
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/reverse/check-client-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status == 200) {
                if (response.is_archived){
                    session_has_ended = true;
                    open_close_session_modal();
                }
                if (response.allow_agent_meeting == "true") {
                    if(ENABLE_VOIP_WITH_VIDEO_CALLING == "True") {
                        show_cobrowse_meeting_option();
                    } else if(ENABLE_VOIP_CALLING == "True") {
                        easyassist_open_voip_meeting_window();    
                    } else {
                        open_meeting_window();
                    }
                }
                if (response.agent_meeting_request_status == true) {
                    if(window.IS_AGENT == "False"){
                        $('#request_voip_meeting_modal').modal('show');
                    }
                }
            } else if (response.status == 500) {
                show_easyassist_toast("Matching session is already expired or doesn't exists");
            }
        }
    }
    xhttp.send(params);
}

function sync_invited_agents_tatus() {

    json_string = JSON.stringify({
        "session_id": COBROWSE_SESSION_ID
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/reverse/sync-invited-agent-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status == 200) {
                if (response.is_archived){
                    open_close_session_modal();
                    return;
                }
                // TODO comment below if block as it is part of previous logic
                // if (response.allow_agent_meeting == "true") {
                //     if(meeting_join_modal_shown == false){
                //         show_meeting_join_modal_to_agent();
                //         meeting_join_modal_shown = true;
                //     }
                // }
            } else if (response.status == 500) {
                show_easyassist_toast("Matching session is already expired or doesn't exists");
            }
        }
    }
    xhttp.send(params);
}

function show_meeting_join_modal_to_agent() {
    if(is_meeting_tab_open()) {
        return;
    }
    $('#inform_voip_meeting_modal').modal('show');
    // ele = document.getElementById("join-voice-call-meeting-btn")
    // if(ele != undefined){
    //     ele.style.display = "block"
    // }
}

function join_meeting_invited_agent(is_check_required=true) {

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
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/reverse/check-meeting-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if(response.status == 301) {
                $('#request_meeting_modal_invited_agent .modal-text').text('The call is not accepted by the customer yet, You can join the call once the customer accepts it.')
                $('#request_meeting_modal_invited_agent .modal-footer').html('<button class="btn btn-primary" type="button" data-dismiss="modal" onclick="ok_button_handler()">OK</button>');
            } else if (response.status == 200) {
                if(response.is_meeting_allowed == false){

                    set_easyassist_current_session_local_storage_obj("is_ok_button_clicked_invited_agent", "false");
                    if(ENABLE_VOIP_WITH_VIDEO_CALLING == "True") {
                        $('#request_meeting_modal_invited_agent .modal-text').text('Customer has denied the video call, request you to wait till customer accepts it.');
                    } else if(ENABLE_VOIP_CALLING == "True") {
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

    $("#request_meeting_modal_invited_agent").modal("hide");
    $("#inform_voip_meeting_modal").modal("hide");

    set_easyassist_current_session_local_storage_obj("is_ok_button_clicked_invited_agent", "false");
    reset_call_modal_text();
    hide_side_nav_call_icon();
    
    delete_easyassist_cookie("is_cobrowse_meeting_on");
    
    set_easyassist_cookie("is_cobrowse_meeting_active", COBROWSE_SESSION_ID);
    set_easyassist_current_session_local_storage_obj("is_cobrowse_meeting_active", COBROWSE_SESSION_ID);
    set_easyassist_cookie("cobrowse_meeting_id", COBROWSE_SESSION_ID);

    if(ENABLE_VOIP_WITH_VIDEO_CALLING == "True") {
        // set_easyassist_cookie("is_cobrowse_meeting_active", COBROWSE_SESSION_ID)
        // set_easyassist_cookie("cobrowse_meeting_id", COBROWSE_SESSION_ID);
        set_easyassist_cookie("is_customer_voip_meeting_joined", COBROWSE_SESSION_ID);
        set_easyassist_cookie("easyassist_meeting_allowed", "true");
        // delete_easyassist_cookie("is_cobrowse_meeting_active");
        show_cobrowse_meeting_option();
    } else if(ENABLE_VOIP_CALLING == "True") {
        delete_easyassist_cookie("is_cobrowse_meeting_on");
        easyassist_open_voip_meeting_window();
    } else {
        delete_easyassist_cookie("is_cobrowse_meeting_on");
        open_meeting_window();
    }
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

function save_cobrowsing_chat_history(chat_message, sender, attachment, attachment_file_name, sender, chat_type, agent_profile_pic_source) {
    
    json_string = {
        "session_id": COBROWSE_SESSION_ID,
        "sender": sender,
        "message": chat_message,
        "attachment": attachment,
        "attachment_file_name": attachment_file_name,
        "agent_username": sender,
        "chat_type": chat_type,
        "agent_profile_pic_source": "",
    };

    if(sender != "client") {
        json_string["agent_profile_pic_source"] = agent_profile_pic_source;
    }

    json_string = JSON.stringify(json_string);
    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/reverse/save-cobrowsing-chat/", true);
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
    
    var agent_name = $('#agent_name').val();
    var sender = 'client';
    var agent_username = "client";
    agent_profile_pic_source = ""
    if(window.IS_AGENT == "True"){
         agent_name = window.INVITED_AGENT_NAME;
         sender = window.INVITED_AGENT_USERNAME;
         agent_profile_pic_source = window.INVITED_AGENT_PROFILE_PIC_SOURCE
    } else {
        agent_name = window.CLIENT_NAME;
    }

    if(window.IS_AGENT == "False"){
        save_cobrowsing_chat_history(message, "agent", attachment, attachment_file_name, "client", chat_type, agent_profile_pic_source);
    }  
    json_string = JSON.stringify({
          "agent_name": agent_name,
          "type": "chat",
          "message": message,
          "attachment": attachment,
          "attachment_file_name": attachment_file_name,
          "sender": sender,
          "chat_type": chat_type,
          "agent_profile_pic_source": agent_profile_pic_source,
      });
    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    //console.log("request for html has been sent: ", new Date());
    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function open_livechat_agent_window() {
    if(window.ENABLE_CHAT_BUBBLE == "True") {
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
    set_easyassist_current_session_local_storage_obj("new_message_seen","true");
    set_easyassist_current_session_local_storage_obj("last_message","");
    if($("#chat-minimize-icon-wrapper")) {
        $("#chat-minimize-icon-wrapper").css({"display":"none"});
    }
    focus_livechat_input();
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
                if(get_easyassist_cookie("is_customer_voip_meeting_joined") == COBROWSE_SESSION_ID) {
                    if(get_easyassist_cookie("is_meeting_audio_muted") == "true") {
                        document.getElementById("agent-meeting-mic-off-btn").click();
                    }
                    document.getElementById("easyassist-voip-loader").style.display = 'none';
                    clearInterval(voip_meeting_ready_interval);
                }
            }, 1000);
        } else if(event.data == "voip_meeting_ended") {
            reset_voip_meeting();
        } else if (event.data.event_id === "livechat-typing") {
            easyassist_send_livechat_typing_indication()
            return
        }

        if(event.data.event == "voip_function_error") {
            easyassist_show_function_fail_modal(code=event.data.error_code);
        }

        if (event.data.event_id === "cobrowsing-agent-chat-message") {
                message = event.data.data.message;
                attachment = event.data.data.attachment;
                attachment_file_name = event.data.data.attachment_file_name;
                send_chat_message_from_agent(message, attachment, attachment_file_name, "chat_message");
                return;
            }
            else if(event.data.event_id == "open_pdf_render_modal"){
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
            }


            if (event.data == "close-bot") {
                close_chatbot_animation();
                if(window.ENABLE_CHAT_BUBBLE == "True" && window.IS_MOBILE == "False") {
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
    if(window.ENABLE_CHAT_BUBBLE == "True" && window.IS_MOBILE == "False") {
        livechat_iframe = document.getElementById("allincall-chat-box");
        if(livechat_iframe.classList.contains("animate__slideInUp")) {
            livechat_iframe.classList.remove("animate__slideInUp");
        }

        if (window.FLOATING_BUTTON_POSITION == "right") {
            livechat_iframe.classList.add("allincall-scale-out-br-right-side");
        } else {
            livechat_iframe.classList.add("allincall-scale-out-br");
        }
        setTimeout(function(){
            livechat_iframe.style.display = "none";
        },600)
    } else {
        document.getElementById("allincall-chat-box").style.display = "none";
        document.getElementById("allincall-chat-box").style.animationName = "bottom-left-right-anime-close";
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

function chat_notification(message,attachment_file_name,sender_name){

    let is_current_tab_focussed = check_current_tab_active();

    //Check for is current tab is not in focus and Notificaiton are allowed on the browser
    if(!is_current_tab_focussed && typeof Notification !== "undefined"){

        let notification_title = `${sender_name} messaged you!`;
        let notification_body = get_notification_body(message, attachment_file_name); 
    
        send_chat_notification(notification_title,notification_body);
    }    
}

function set_client_response(message, attachment, attachment_file_name, name, sender, chat_type, agent_profile_pic_source) {
    if(IS_MOBILE == "True" && chat_type != "chat_bubble") {
        if (chat_type == "agent_connect_message") {
            play_greeting_bubble_popup_sound();
        }
        document.getElementById("allincall-chat-box").style.display = "block";
        set_easyassist_current_session_local_storage_obj("new_message_seen","true");
    }
    if(window.ENABLE_CHAT_BUBBLE == "True" && IS_MOBILE == "False" && chat_type != "chat_bubble") {
        var chat_box = document.getElementById("chat-minimize-icon-wrapper");
        set_easyassist_current_session_local_storage_obj("new_message_seen","false");
        if (chat_type != "agent_connect_message") {
            try { 
                append_chat_bubble_message(name, message, attachment, attachment_file_name);
            } catch (err) {
                console.log(err)
            }
        } else {
            document.getElementById("allincall-chat-box").style.display = "block";

            let is_current_tab_focussed = check_current_tab_active();
            if( is_current_tab_focussed ){
                play_greeting_bubble_popup_sound();
            }

            document.getElementById("allincall-chat-box").classList.add("animate__animated");
            document.getElementById("allincall-chat-box").classList.add("animate__slideInUp");
            set_easyassist_current_session_local_storage_obj("new_message_seen","true");
            if(chat_box) {
                chat_box.style.display = "none";
            }
        }
    } else {
        if(chat_type != "chat_bubble" && document.getElementById("allincall-chat-box")) {
            document.getElementById("allincall-chat-box").style.display = "block";
        }
    }

    chat_notification(message,attachment_file_name,name);
    
    allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow;
    allincall_chat_window.postMessage(JSON.stringify({
        "message": message,
        "attachment": attachment,
        "attachment_file_name": attachment_file_name,
        "show_client_message": true,
        "name": name,
        "sender": sender,
        "chat_type": chat_type,
        "agent_profile_pic_source": agent_profile_pic_source,
    }), window.location.protocol + "//" + window.location.host);

    if(window.IS_AGENT == "False"){
        save_cobrowsing_chat_history(message, "client", attachment, attachment_file_name, sender, chat_type, agent_profile_pic_source);
    }
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

    show_easyassist_toast("Request for edit access has been sent to agent");
}

function detect_agent_value_change(event) {
    if (get_easyassist_cookie("request_edit_access") == COBROWSE_SESSION_ID) {
        element = event.target;
        tag_type = element.getAttribute("type");
        tag_name = element.tagName.toLowerCase();
        element_id = easyassist_get_easyassist_id_from_element(element);
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
            "element_attr_id": element.id,
        });

        encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        send_message_over_easyassist_socket(encrypted_data, "agent");
    }
}

function send_agent_name() {
    allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow
    allincall_chat_window.postMessage(JSON.stringify({
        "id": "agent_name",
        "name": window.AGENT_NAME,
        "session_id": COBROWSE_SESSION_ID
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
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/reverse/get-cobrowsing-chat-history/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response.chat_history.length > 0) {
                chat_history = response.chat_history;
                allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow;
                for(let index = 0; index < chat_history.length; index++) {
                    sender = chat_history[index]["sender"];
                    message = chat_history[index]["message"];
                    sender_name = chat_history[index]["sender_name"];
                    message=show_hyperlink_inside_text(message);
                    datetime = chat_history[index]["datetime"];
                    var time = datetime.split(" ")[3] + " " + datetime.split(" ")[4];
                    attachment = chat_history[index]["attachment"];
                    attachment_file_name = chat_history[index]["attachment_file_name"];
                    var chat_type = chat_history[index]["chat_type"];
                    agent_profile_pic_source = chat_history[index]["agent_profile_pic_source"]
                    if (window.IS_AGENT == "False" && sender == "client") {
                        
                        allincall_chat_window.postMessage(JSON.stringify({
                            "message": message,
                            "attachment": attachment,
                            "attachment_file_name": attachment_file_name,
                            "show_agent_message": true,
                            "name": window.CLIENT_NAME,
                            "time": time,
                            "sender": sender,
                            "chat_type": chat_type,
                        }), window.location.protocol + "//" + window.location.host);
                    } else {
                        if(sender == window.INVITED_AGENT_USERNAME){
                            allincall_chat_window.postMessage(JSON.stringify({
                                "message": message,
                                "attachment": attachment,
                                "attachment_file_name": attachment_file_name,
                                "show_agent_message": true,
                                "time": time,
                                "name": sender_name,
                                "sender": sender,
                                "chat_type": chat_type,
                                "agent_profile_pic_source": agent_profile_pic_source,
                            }), window.location.protocol + "//" + window.location.host);
                        } else {
                            if(sender == "client"){
                                sender_name = window.CLIENT_NAME;
                            }
                            allincall_chat_window.postMessage(JSON.stringify({
                                "message": message,
                                "attachment": attachment,
                                "attachment_file_name": attachment_file_name,
                                "show_client_message": true,
                                "time": time,
                                "name": sender_name,
                                "sender": sender,
                                "chat_type": chat_type,
                                "agent_profile_pic_source": agent_profile_pic_source,
                            }), window.location.protocol + "//" + window.location.host);
                        }
                    }
                }
            }
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
    } catch(err) {
        screen_recorder_on = false;
        e.children[0].setAttribute("fill", '#191717');
        e.children[1].innerHTML = "Start screen recording"
        return;
    }

    recorder.ondataavailable = blob => save_cobrowseing_recorded_data(blob);

    recorder.start(5000);
}

function save_cobrowseing_recorded_data(blob) {

    var filename = COBROWSE_SESSION_ID + '.webm';
    var file = new File([blob.data], filename, {
        type: 'video/webm'
    });
    var formData = new FormData();
    formData.append("uploaded_data", file);
    formData.append("session_id", COBROWSE_SESSION_ID);
    formData.append("screen_recorder_on", screen_recorder_on);

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
                console.log("Unable to save data packet");
            }
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        }
    });
}

function start_screen_recording(e) {

    if (screen_recorder_on) {
        e.children[0].setAttribute("fill", '#191717');
        e.children[1].innerHTML = "Start screen recording"
        screen_recorder_on = false;
        recorder.stop();
        stream.getVideoTracks()[0].stop();
        stream.getAudioTracks()[0].stop();
    } else {
        e.children[0].setAttribute("fill", 'red');
        e.children[1].innerHTML = "Stop screen recording"
        startRecording(e);
        screen_recorder_on = true;
    }
}

function connect_with_client(session_id) {
    $("#request_meeting_modal").modal("hide");
    if (session_id == null || session_id == undefined) {

        return;
    }
    var meet_url = "/easy-assist/meeting/" + session_id + "?is_meeting_cobrowsing=true&is_client=true";
    if(window.IS_AGENT == "True") {
        meet_url = "/easy-assist/meeting/" + session_id + "?is_meeting_cobrowsing=true&is_client=false&id=" + window.AGENT_IDENTIFIER;
    }
    window.open(meet_url, "_blank",);
}

function show_emoji_by_user_rating(element, user_rating) {

    rating_spans = element.parentNode.children;
    for(let index = 0; index < rating_spans.length; index ++) {
        if (parseInt(rating_spans[index].innerHTML) <= user_rating) {
            if(index <= 6){
                rating_spans[index].style.background = 'rgba(255, 70, 70, 1)';
            } else if( index <= 8){
                rating_spans[index].style.background = 'rgba(255, 153, 0, 1)';
            } else {
                rating_spans[index].style.background = 'rgba(5, 178, 54, 1)';
            }
            rating_spans[index].style.border = "none";
            // rating_spans[index].style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
            rating_spans[index].style.color = "#fff";
        } else if(!easyassist_tickmarks_clicked[index]){
            rating_spans[index].style.border = "1px solid #E6E6E6";
            rating_spans[index].style.background = "unset";
            rating_spans[index].style.color = "#2D2D2D";

        }
    }
}

function changeColor(element) {

    var rating_bar = document.getElementsByClassName("easyassist-tickmarks")[0];
    var rating_spans = rating_bar.querySelectorAll("span");

    var show_default_emoji = true;
    for(let index = 0; index < rating_spans.length; index ++) {
        if(!easyassist_tickmarks_clicked[index]) {
            rating_spans[index].style.color = "#2D2D2D";
            rating_spans[index].style.background = "unset";
            rating_spans[index].style.border = "1px solid #E6E6E6";
        }
    }
}

function rateAgent(element) {
    var rating_bar = document.getElementsByClassName("easyassist-tickmarks")[0];
    var rating_spans = rating_bar.querySelectorAll("span");
    var user_rating = parseInt(element.innerHTML);

    window.EASYASSIST_CLIENT_FEEDBACK = user_rating;

    for(let index = 0; index <= user_rating; index ++) {
        // var current_rating = parseInt(rating_spans[index].innerHTML);
        if(index <= 6){
            rating_spans[index].style.background = 'rgba(255, 70, 70, 1)';
        } else if( index <= 8){
            rating_spans[index].style.background = 'rgba(255, 153, 0, 1)';
        } else {
            rating_spans[index].style.background = 'rgba(5, 178, 54, 1)';
        }
        // rating_spans[index].style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        rating_spans[index].style.color = "#fff";
        easyassist_tickmarks_clicked[index] = true;
        rating_spans[index].style.border = "none";
    }

    for(let index = user_rating + 1; index < rating_spans.length; index ++) {
        var current_rating = parseInt(rating_spans[index].innerHTML);
        rating_spans[index].style.background = "unset"
        rating_spans[index].style.color = "#2D2D2D";
        easyassist_tickmarks_clicked[index] = false;
        rating_spans[index].style.border = "1px solid #E6E6E6";
    }
}

function reset_easyassist_rating_bar() {
    var rating_bar = document.getElementsByClassName("easyassist-tickmarks");
    if(rating_bar.length > 0){
        rating_bar = rating_bar[0];
        var rating_spans = rating_bar.querySelectorAll("span");
        for(let index = 0; index < rating_spans.length; index++) {
            rating_spans[index].style.background = "unset";
            rating_spans[index].style.color = "#2D2D2D";
            rating_spans[index].style.border = "1px solid #E6E6E6";
            easyassist_tickmarks_clicked[index] = false;
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

function easyassist_open_voip_meeting_window() {
    var is_cobrowsing_meeting_on = get_easyassist_cookie("is_cobrowse_meeting_on")
    if(is_cobrowsing_meeting_on == '' || is_cobrowsing_meeting_on == null || is_cobrowsing_meeting_on == undefined){
        is_cobrowsing_meeting_on = false
    }
    if(is_cobrowsing_meeting_on == false || is_cobrowsing_meeting_on == 'false') {
        set_easyassist_cookie("is_cobrowse_meeting_on", "true");
        var url = "";
        if(window.IS_AGENT == "False"){
            url = "/easy-assist/client-cobrowse-meeting/" + COBROWSE_SESSION_ID;
        }else{
            url = "/easy-assist/agent-cobrowse-meeting/" + COBROWSE_SESSION_ID + "?id=" + window.AGENT_IDENTIFIER;
        }
        window.open(url, "_blank");
    }
}

function show_cobrowse_meeting_option() {
    var is_cobrowse_meeting_active = get_easyassist_cookie("is_cobrowse_meeting_active");
    if(is_cobrowse_meeting_active == COBROWSE_SESSION_ID) {
        if(document.getElementById("cobrowse-voip-container").style.display == 'none') {
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
            var meeting_url = "";
            if(window.IS_AGENT == "False"){
                meeting_url = window.location.protocol + "//" + window.location.host + "/easy-assist/client-cobrowse-meeting/" + COBROWSE_SESSION_ID;
            } else {
                meeting_url = window.location.protocol + "//" + window.location.host + "/easy-assist/agent-cobrowse-meeting/" + COBROWSE_SESSION_ID + "?id=" + window.AGENT_IDENTIFIER;
            }
            cobrowsing_meeting_iframe.src = meeting_url;
        }
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

        if(status) {
            set_easyassist_cookie("is_meeting_audio_muted", false);
        } else {
            set_easyassist_cookie("is_meeting_audio_muted", true);
        }
        if(element.id == "agent-meeting-mic-on-btn") {
            document.getElementById("agent-meeting-mic-on-btn").style.display = 'none';
            document.getElementById("agent-meeting-mic-off-btn").style.display = '';
        } else if(element.id == "agent-meeting-mic-off-btn") {
            document.getElementById("agent-meeting-mic-off-btn").style.display = 'none';
            document.getElementById("agent-meeting-mic-on-btn").style.display = '';
        }
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
        if(element.id == "agent-meeting-video-on-btn") {
            document.getElementById("agent-meeting-video-on-btn").style.display = 'none';
            document.getElementById("agent-meeting-video-off-btn").style.display = '';
        } else if(element.id == "agent-meeting-video-off-btn") {
            document.getElementById("agent-meeting-video-off-btn").style.display = 'none';
            document.getElementById("agent-meeting-video-on-btn").style.display = '';
        }
    } catch(err) {
        console.log(err)
    }
}

function end_cobrowse_video_meet(auto_end_meeting=false) {
    try {
        if(ENABLE_VOIP_CALLING == "True") {
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
        send_end_meeting_messsage_over_socket(auto_end_meeting);
    } catch(err) {
        console.log(err);
    }
}

function reset_voip_meeting() {
    set_easyassist_cookie("is_cobrowse_meeting_active", "");
    delete_easyassist_cookie("is_meeting_audio_muted");
    delete_easyassist_cookie("is_customer_voip_meeting_joined");
    // ele = document.getElementById("join-voice-call-meeting-btn")
    // if(ele != undefined){
    //     ele.style.display = "none"
    // }
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
    try {
        captured_video_stream.getTracks().forEach(function(track) {
            track.stop();
        });
    } catch(err) {}
    setTimeout(function() {
        document.getElementById("cobrowse-meeting-iframe-container").children[0].src = "";
    }, 2000);
}

function toggle_meeting_iframe_visibility() {
    var meeting_iframe_container = document.getElementById("cobrowse-meeting-iframe-container");
    if(meeting_iframe_container.style.display == 'none') {
        meeting_iframe_container.style.display = 'block';
    } else {
        meeting_iframe_container.style.display = 'none';
    }
}

function update_agent_meeting_request(status) {

    var easyassist_session_id = COBROWSE_SESSION_ID;

    var request_meeting_error_el = null;

    json_string = JSON.stringify({
        "id": easyassist_session_id,
        "status": status
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);
    
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/reverse/update-agent-meeting-request/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            set_easyassist_cookie("is_cobrowse_meeting_on", "false");
            if (response.status == 200) {
                $('#request_voip_meeting_modal').modal('hide');
                // ele = document.getElementById("join-voice-call-meeting-btn")
                // if(ele != undefined){
                //     ele.style.display = "block"
                // }
                if (response.meeting_allowed == "true") {
                    set_easyassist_cookie("is_cobrowse_meeting_active", easyassist_session_id)
                    set_easyassist_cookie("cobrowse_meeting_id", easyassist_session_id);
                    set_easyassist_cookie("easyassist_meeting_allowed", "true");
                } else {
                    set_easyassist_cookie("easyassist_meeting_allowed", "false");
                }

                sync_client_web_screen_agent();
            }
        }
    }
    xhttp.send(params);
}

function send_end_meeting_messsage_over_socket(auto_end_meeting) {
    json_string = JSON.stringify({
        "type": "end_voip_meeting",
        "auto_end_meeting": auto_end_meeting,
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
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}


function open_meeting_window() {

    var is_cobrowsing_meeting_on = get_easyassist_cookie("is_cobrowse_meeting_on")
    if(is_cobrowsing_meeting_on == '' || is_cobrowsing_meeting_on == null || is_cobrowsing_meeting_on == undefined){
        is_cobrowsing_meeting_on = false
    }
    if(is_cobrowsing_meeting_on == false || is_cobrowsing_meeting_on == 'false') {
        set_easyassist_cookie("is_cobrowse_meeting_on", "true");

        var meet_url = "/easy-assist/meeting/" + COBROWSE_SESSION_ID + "?is_meeting_cobrowsing=true&is_client=true";
        if(window.IS_AGENT == "True") {
            meet_url = "/easy-assist/meeting/" + COBROWSE_SESSION_ID + "?is_meeting_cobrowsing=true&is_client=false&id=" + window.AGENT_IDENTIFIER;
        }
        window.open(meet_url, "_blank",);
    }
}

function send_customer_join_over_socket() {
    json_string = JSON.stringify({
        "type": "customer_joined",
        "agent_name": window.AGENT_NAME,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function easyassist_send_livechat_typing_indication() {
    var name = window.CLIENT_NAME;
    var role = "client";
    if(window.IS_AGENT == "True"){
        name = window.INVITED_AGENT_NAME;
        role = "agent";
    }

    json_string = JSON.stringify({
        "role": role,
        "name": name,
        "type": "livechat-typing"
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

/******************* CLIENT LOCATION START ************************/

function easyassist_save_customer_location(){
    if (window.navigator.geolocation) {
        var geolocation_options = {
            enableHighAccuracy: true,
            timeout: 15000,
            maximumAge: 0
        };
        window.navigator.geolocation.getCurrentPosition(easyassist_accept_location_request, easyassist_cancel_location_request, geolocation_options);
    }
}

function easyassist_accept_location_request(pos) {
    var latitude = pos.coords.latitude;
    var longitude = pos.coords.longitude;
    easyassist_save_client_location_details(latitude, longitude);
    
}

function easyassist_cancel_location_request(pos) {
    var latitude = null;
    var longitude = null;
    easyassist_save_client_location_details(latitude, longitude);
}

function easyassist_save_client_location_details(latitude, longitude) {
    request_params = {
        "session_id": COBROWSE_SESSION_ID,
        "latitude": latitude,
        "longitude": longitude,
    };
    json_params = JSON.stringify(request_params);

    console.log(json_params)

    encrypted_data = easyassist_custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/reverse/save-client-location/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                console.log("location saved successfully");
            } else {
                console.log("Failed to save customer's location");
            }
        }
    }
    xhttp.send(params);
}

/******************* CLIENT LOCATION END ************************/

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

function easyassist_invite_agent_joined() {

    var message = "Agent " + window.INVITED_AGENT_NAME + " has joined the chat";
    set_client_response(message, "None", "None", window.INVITED_AGENT_NAME, window.INVITED_AGENT_USERNAME, "chat_bubble");
    send_chat_message_from_agent(message, "None", "None", "chat_bubble");

    json_string = JSON.stringify({
        "type": "invited_agent_joined",
        "invited_agent_name": window.INVITED_AGENT_NAME,
        "invited_agent_username": window.INVITED_AGENT_USERNAME,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function check_is_meeting_active_over_socket(show_modal=false) {
    if(window.IS_AGENT == "True") {
        var json_string = JSON.stringify({
            "type": "is_meeting_active",
            "show_modal": show_modal
        });
    
        var encrypted_data = easyassist_custom_encrypt(json_string);
    
        encrypted_data = {
            "Request": encrypted_data
        };
    
        send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
    }
}

function open_call_joining_modal() {
    // TODO uncomment below if inconsistency arises
    // check_is_meeting_active_over_socket();
    setTimeout(() => {
        var local_storage_obj = get_easyassist_current_session_local_storage_obj();
        if(local_storage_obj != null && local_storage_obj.hasOwnProperty("is_call_ongoing_invited_agent")) {
            if (local_storage_obj["is_call_ongoing_invited_agent"] == "true") {
                show_meeting_join_modal_to_agent();
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

function is_meeting_tab_open() {
    // TODO check if this is working fine
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
    // TODO add back this condition
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
        document.getElementById("request-cobrowsing-meeting-btn-invited-agent").style.display = "none";
    }
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
        '<button class="btn btn-primary" id="request_button" type="button" onclick="join_meeting_invited_agent()">Yes</button>');
}

function ok_button_handler() {
    set_easyassist_current_session_local_storage_obj("is_ok_button_clicked_invited_agent", "true");
}

function check_voip_video_meeting_enabled() {
    if (ENABLE_VOIP_WITH_VIDEO_CALLING == "True" || ENABLE_VOIP_WITH_VIDEO_CALLING == true) {
        return true;
    }
    return false;
}

function check_voip_enabled() {
    if (ENABLE_VOIP_CALLING == "True" || ENABLE_VOIP_CALLING == true) {
        return true;
    }
    return false;
}

function check_video_calling_enabled() {
    if (ALLOW_COBROWSING_MEETING == "True" || ALLOW_COBROWSING_MEETING == true) {
        return true;
    }
    return false;
}

function easyassist_invite_agent_left() {

    let message = `Agent ${window.INVITED_AGENT_NAME} has left the chat`;
    set_client_response(message, "None", "None", window.INVITED_AGENT_NAME, window.INVITED_AGENT_USERNAME, "chat_bubble");
    send_chat_message_from_agent(message, "None", "None", "chat_bubble");

    json_string = JSON.stringify({
        "type": "invited_agent_left",
        "invited_agent_name": window.INVITED_AGENT_NAME,
        "invited_agent_username": window.INVITED_AGENT_USERNAME,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, "agent");
}

function close_agent_leave_session(element) {

    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID,
        "agent_username": window.INVITED_AGENT_USERNAME,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Leaving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/reverse/close-session/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            easyassist_invite_agent_left();
            easyassist_delete_session_cookie();
            var href = window.location.href.split("#")[0];
            if(href.indexOf('?') > 0){
                window.location.href = href + "&session_ended=true";
            } else {
                window.location.href = href + "?session_ended=true";
            }
        } else if ( this.readyState == 4 ) {
            easyassist_invite_agent_left();
            if(window.location.href.indexOf('?') > 0){
                window.location.href = href + "&session_ended=true";
            } else {
                window.location.href = href + "?session_ended=true";
            }
        }
    }
    xhttp.send(params);
}

function initialize_empty_iframe() {

    EASYASSIST_IFRAME_ID += 1;

    var iframe = document.createElement('iframe');
    iframe.src = "";
    iframe.id = "easyassist-iframe-" + EASYASSIST_IFRAME_ID;
    iframe.hidden = true;
    iframe.setAttribute("class", "client-data-frame");

    framesContainer.appendChild(iframe);

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

function initialize_easyassist_iframe(dataset) {

    var iframe = initialize_empty_iframe();

    var iframe_doc = iframe.contentDocument;

    while (iframe_doc.firstChild) {
        iframe_doc.removeChild(iframe_doc.firstChild);
    }

    easyassist_tree_mirror = new EasyAssistTreeMirror(iframe_doc, {
        createElement: function(tagName) {
          if (tagName == 'SCRIPT') {
            var node = iframe_doc.createElement('NO-SCRIPT');
            node.style.display = 'none';
            return node;
          }

          if (tagName == 'HEAD') {
            let node = iframe_doc.createElement('HEAD');
            node.appendChild(iframe_doc.createElement('BASE'));
            node.firstChild.href = dataset.base;

            var style_node = iframe_doc.createElement("STYLE");
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

                element_value = element_value[1];

                if(tag_name == "INPUT") {
                    var element_type = element.getAttribute("type");
                    if(element_type == "checkbox" || element_type == "radio") {
                        element.checked = element_value;
                    } else if(element_type == "number") {
                        element.setAttribute("type", "text");
                        element.value = element_value;
                    } else {
                        element.value = element_value;
                    }
                } else if(tag_name == "SELECT") {
                    element.value = element_value;
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
                renderFrame(dataset);
            },

            update_edit_access: easyassist_update_edit_access,
        },
    });
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

function easyassist_get_element_from_easyassist_id(element_id) {
    var element = null;

    try {
        element = easyassist_tree_mirror.idMap[element_id];
    } catch(err) {
        console.log("easyassist_get_element_from_easyassist_id: ", err);
    }

    return element;
}

function easyassist_get_easyassist_id_from_element(element) {
    var element_id = null;

    try {
        element_id = element.easyassist_element_id;
    } catch(err) {
        console.log("easyassist_get_easyassist_id_from_element: ", err);
    }

    return element_id;
}

/***************** EasyAssist Canvas ***********************/

class EasyAssistCanvas {
    constructor(canvas_element, color, line_width) {
        this.canvas = canvas_element;

        this.canvas.setAttribute("data-canvas", "easyassist-canvas");
        this.ctx = this.canvas.getContext("2d");
        this.color = color;
        this.line_width = line_width;
        this.reset_canvas_timer = null;
    }

    draw_dot(curr_x, curr_y, line_width) {
        this.ctx.beginPath();
        this.ctx.fillStyle = this.color;
        this.ctx.arc(curr_x, curr_y, line_width / 2, 0, 2 * Math.PI, true);
        this.ctx.fill();
        this.ctx.closePath();

        this.start_clear_canvas_interval();
    }

    draw_line(prev_x, prev_y, curr_x, curr_y, line_width) {
        this.ctx.lineCap = "round";
        this.ctx.beginPath();
        this.ctx.moveTo(prev_x, prev_y);
        this.ctx.lineTo(curr_x, curr_y);
        this.ctx.strokeStyle = this.color;
        this.ctx.lineWidth = line_width;
        this.ctx.stroke(); 
        this.ctx.closePath();

        this.start_clear_canvas_interval();
    }

    reset_canvas(points_queue) {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.reset_clear_canvas_interval();
    }

    resize_canvas(width, height) {
        this.canvas.width = width;
        this.canvas.height = height;
    }

    start_clear_canvas_interval() {
        var _this = this;

        _this.reset_clear_canvas_interval();

        _this.reset_canvas_timer = setTimeout(function() {
            _this.reset_canvas();
        }, 6000);
    }

    reset_clear_canvas_interval() {
        var _this = this;

        if(_this.reset_canvas_timer != null) {
            clearTimeout(_this.reset_canvas_timer);
            _this.reset_canvas_timer = null;
        }
    }
}

function easyassist_initialize_drawing_canvas() {
    try {
        var easyassist_canvas = document.getElementById("easyassist-drawing-canvas");
        if(!easyassist_canvas) {
            return;
        }

        easyassist_drawing_canvas = new EasyAssistCanvas(
            easyassist_canvas, FLOATING_BUTTON_BG_COLOR, 7);

        easyassist_resize_drawing_canvas(window.innerWidth, window.innerHeight, 0, 0);

    } catch(err) {
        console.log("easyassist_initialize_drawing_canvas", err);
    }
}

function easyassist_sync_agent_canvas(data_packet) {
    try {
        var prev_x = data_packet.prev_x * agent_scale_factor;
        var prev_y = data_packet.prev_y * agent_scale_factor;
        var curr_x = data_packet.curr_x * agent_scale_factor;
        var curr_y = data_packet.curr_y * agent_scale_factor;
        var shape = data_packet.shape;
        var line_width = data_packet.line_width;

        if(shape == "line") {
            easyassist_drawing_canvas.draw_line(prev_x, prev_y, curr_x, curr_y, line_width);
        } else {
            easyassist_drawing_canvas.draw_dot(curr_x, curr_y, line_width)
        }
    } catch(err) {
        console.log("easyassist_sync_agent_canvas: ", err);
    }
}

function easyassist_reset_agent_canvas() {
    try {
        easyassist_drawing_canvas.reset_canvas();
    } catch(err) {
        console.log("easyassist_reset_agent_canvas: ", err);
    }
}

function easyassist_resize_drawing_canvas(width, height, margin_left, margin_right) {
    try {
        easyassist_drawing_canvas.resize_canvas(width, height);

        var easyassist_canvas = document.getElementById("easyassist-drawing-canvas");
        easyassist_canvas.style.marginLeft = margin_left_client_frame_container + "px";
        easyassist_canvas.style.marginTop = margin_top_client_frame_container + "px";
    } catch(err) {
        console.log("easyassist_reset_agent_canvas: ", err);
    }
}

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

function show_easyassist_loader(show_restricted_message = false) {
    hide_easyassist_client_end_page_loader();
    if(window.COBROWSE_LOGO != "" && window.COBROWSE_LOGO != null && window.COBROWSE_LOGO != undefined) {
        document.getElementById("easyassist-loader").getElementsByClassName("loading-image")[0].innerHTML = `<img src="${window.COBROWSE_LOGO}" alt="Loading Image" width="220px">`
    } else {
        document.getElementById("easyassist-loader").getElementsByClassName("loading-image")[0].innerHTML = '<img src="https://static.allincall.in/static/EasyAssistApp/img/loadingImage.svg" alt="Loading Image" width="220px">'
    }
    document.getElementById("easyassist-loader").getElementsByClassName("loading-lines")[0].style.display = "block";
    document.getElementById("easyassist-loader").getElementsByClassName("loading-message")[0].innerHTML = "Loading Customer Experiences at Scale.";
    document.getElementById("easyassist-loader").style.display = "";
    
    if(show_restricted_message) {
        var loading_image = `<img src='/static/EasyAssistApp/img/restricted_page.png' alt="Restricted Page Image" width="220px"></img>`;
        document.getElementById("easyassist-loader").getElementsByClassName("loading-image")[0].innerHTML = loading_image;
        document.getElementById("easyassist-loader").getElementsByClassName("loading-lines")[0].style.display = "none";
        document.getElementById("easyassist-loader").getElementsByClassName("loading-message")[0].innerHTML = "You can not view this as the agent is on a restricted page.";
    }
}

// function hide_easyassist_loader() {
//     document.getElementById("easyassist-loader").style.display = "none";
// }

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

function play_greeting_bubble_popup_sound() {
    let allincall_chat_window = document.getElementById("allincall-chat-box");

    if (allincall_chat_window.classList.contains("animate__slideInUp")) {
        return;
    }

    chat_notification_sound();
}

function append_chat_bubble_message(agent_name, message, attachment, attachment_file_name){ 
    if(document.getElementById("allincall-chat-box").style.display == "none") {
        $("#chat-minimize-icon-wrapper").css({"display":"block"});
        $(".chat-talk-bubble").removeClass("bounce2");
        var message_box = document.getElementById("talktext-p");
        $(".chat-talk-bubble").css({"display":"block"});
        $(".chat-talk-bubble").addClass("bounce2");
        play_greeting_bubble_popup_sound();

        let received_message = "";
        let short_message = "";
        if(check_text_link(message)) {
            let parser = new DOMParser();
            let link_start_index = message.indexOf("<a");
            let link_end_index = message.indexOf("</a>");
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
}

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

function show_easyassist_client_end_page_loader() {
    document.getElementById("easyassist-client-end-page-loader").style.display = "";
}

function hide_easyassist_client_end_page_loader() {
    document.getElementById("easyassist-client-end-page-loader").style.display = "none";
}

function easyassist_show_long_toast(message) {

    var easyassist_snackbar_custom = document.getElementById("easyassist-snackbar");
    easyassist_snackbar_custom.innerHTML = message;
    easyassist_snackbar_custom.className = "show";

    setTimeout(function () {
        easyassist_snackbar_custom.className = easyassist_snackbar_custom.className.replace("show", "");
    }, 5000);
}