var easyassist_send_client_weak_connection_message_interval = null;
var EASYASSIST_SESSION_ID = null;
var check_for_agent_assistance = null;
var easyassist_client_heartbeat_timer = null;
var is_agent_connected = false;
var hidden_element_count = null;
var visible_element_count = null;

var client_websocket = null;
var client_websocket_open = false;
var sync_utils_client_websocket_open = false;
var sync_utils_client_websocket = null;
var packet_counter = 0;

var EASYASSIST_TAG_LIST = ["input", "select", "textarea", "div", "span", "label", "ul"];
var easyassist_check_for_agent_guide_timer = null;
var html_page_counter = 0;
var easyassist_session_expired_flag = false;
var is_cobrowse_meeting_on = false;
var agent_mouse_top = 0;
var agent_mouse_left = 0;
var agent_revoke_edit_access = false;
var captured_video_stream = null;

var internet_connectivity_timer = null;
var INTERNET_CON_TIMER = 30000;
var global_element_stuck_timer = null;

var easyassist_speed_mbps = 0;
var easyassist_internet_iteration = 2;
var is_client_network_bandwidth_measured = false;
var check_cobrowse_session_timer = null;

var easyassist_client_mouse_last_cordinates = null;
var easyassist_last_mouse_move_time = null;

var easyassist_sync_client_mouse_timeout = null;
var easyassist_sync_client_mouse_time = null;
var easyassist_sync_last_mouse_move_event = null;
var agent_wait_timer = null;
var easyassist_client_page_id = easyassist_get_client_page_id();
var easyassist_client_notification_list = [];
var is_cobrowsing_meeting = null;

var auto_msg_popup_on_client_call_declined = false;
var check_meeting_status_interval = null;

var call_initiate_by_agent = "false";

var is_request_from_inactivity_popup = false;
let is_cobrowsing_from_livechat = false;

function easyassist_get_client_page_id() {
    function easyassist_generate_unique_id() {
        var current_time = (new Date()).getTime();
        try {
            current_time = Date.now().toString(36);
        } catch(err) {
            current_time = (new Date()).getTime().toString(36);
        }

        var random_value = Math.random().toString(36).substring(2);
        return current_time + random_value;
    }

    try {
        var client_page_id = window.sessionStorage.getItem("easyassist_client_page_id");
        if(client_page_id == null) {
            client_page_id = easyassist_generate_unique_id();
            window.sessionStorage.setItem("easyassist_client_page_id", client_page_id);
        }

        return client_page_id;
    } catch(err) {
        console.log("easyassist_get_client_page_id: ", err);
    }
}

function easyassist_start_cobrowsing_activity_check() {
    if(check_cobrowse_session_timer != null){
        return;
    }
    check_cobrowse_session_timer = setInterval(function(e) {
        if (get_easyassist_cookie("easyassist_session_id") != undefined) {
            clearInterval(check_cobrowse_session_timer);
            check_cobrowse_session_timer = null;
            EASYASSIST_SESSION_ID = get_easyassist_cookie("easyassist_session_id");
            easyassist_initiate_cobrowsing();
        }

        if(get_easyassist_cookie("easyassist_agent_weak_connection") != undefined) {
            EasyAssistLowBandWidthHTML.set_agent_weak_connection_value(true);
        }
    }, 1000);
}

function easyassist_reset_global_var() {
    try{
        EASYASSIST_SESSION_ID = null;
        check_for_agent_assistance = null;
        easyassist_client_heartbeat_timer = null;
        is_agent_connected = false;
        hidden_element_count = null;
        visible_element_count = null;
        easyassist_session_expired_flag = false;
    }catch(err){}
}

/******************* EASYASSIST HTML WEBSOCKET ************************/

function easyassist_create_socket(jid, sender) {
    let ws_scheme = EASYASSIST_HOST_PROTOCOL == "http" ? "ws" : "wss"
    let url = ws_scheme + '://' + EASYASSIST_COBROWSE_HOST + '/ws/cobrowse/' + jid + '/' + sender + "/";
    if (client_websocket == null) {
        client_websocket = new WebSocket(url);
        client_websocket.onmessage = easyassist_check_for_agent_guide;
        client_websocket.onerror = function(e){
                console.error("WebSocket error observed:", e);
                client_websocket_open = false;
                easyassist_close_socket();
            }
        client_websocket.onopen = function(){
                client_websocket_open = true; 
                console.log("client_websocket created successfully");

                easyassist_send_client_page_details();
            }
        client_websocket.onclose = function() {
                client_websocket_open = false;
                client_websocket = null; 
                easyassist_disconnect_mutation_summary_client();
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

function easyassist_is_url_restricted() {

    var restricted_urls = window.EASYASSIST_COBROWSE_META.restricted_urls_list;
    var current_url = window.location.href.replace(/^https?\:\/\//i, "");
    
    if(check_proxy_cobrowsing()) {
        let domain = get_proxy_url_domain();
        if(domain) {
            current_url = domain;
        }
    }
    
    for(let index=0; index<restricted_urls.length; index++) {
        var url = restricted_urls[index].trim();
        if(url && current_url.indexOf(url) != -1) {
            return true;   
        }
    }
    return false;
}

function easyassist_send_message_over_socket(message, sender, restriction_bypass=false) {
    try{
        let allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;

        if (allow_cobrowsing == false) {
            return;
        }

        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
        if(easyassist_session_id == undefined || easyassist_session_id == null){
            return;
        }

        if(get_easyassist_cookie("easyassist_agent_connected") != "true"){
            return;
        }

        if(client_websocket_open == false || client_websocket == null){
            if(easyassist_send_message_over_socket.caller.name == "easyassist_socket_callee"){
                return;
            }
            setTimeout(function easyassist_socket_callee(){
                easyassist_send_message_over_socket(message, sender);
            }, 5000);
            console.log("client_websocket is not open");
            return;
        }

        if (client_websocket_open == true && client_websocket != null) {

            if(!restriction_bypass && easyassist_is_url_restricted()) {
                message = easyassist_get_restricted_data_packet();
            }
    
            var packet = JSON.stringify({
                "message": {
                    "header": {
                        "sender": sender,
                        "packet": packet_counter,
                        "client_page_id": easyassist_client_page_id,
                    },
                    "body": message
                }
            })

            client_websocket.send(packet);

            packet_counter += 1;
        }
    }catch(err){
        console.error("ERROR : easyassist_send_message_over_socket ", err);
    }
}

/******************* END EASYASSIST HTML WEBSOCKET ************************/

/******************* EASYASSIST UTILITY  WEBSOCKET ************************/

function easyassist_create_sync_utils_socket(jid, sender) {
    jid = "sync_utils_" + jid;
    let ws_scheme = EASYASSIST_HOST_PROTOCOL == "http" ? "ws" : "wss"
    let url = ws_scheme + '://' + EASYASSIST_COBROWSE_HOST + '/ws/cobrowse/sync-utils/' + jid + '/' + sender + "/";
    if (sync_utils_client_websocket == null) {
        sync_utils_client_websocket = new WebSocket(url);
        sync_utils_client_websocket.onmessage = easyassist_check_for_agent_guide;
        sync_utils_client_websocket.onerror = function(e){
                console.error("Socket Error : ", e);
                sync_utils_client_websocket_open = false;
                easyassist_close_sync_utils_socket();
            }
        sync_utils_client_websocket.onopen = function(){
                sync_utils_client_websocket_open = true; 
                console.log("sync_utils_client_websocket created successfully") 
            }
        sync_utils_client_websocket.onclose = function() {
                sync_utils_client_websocket_open = false;
                sync_utils_client_websocket = null;
            }
    }
}

function easyassist_close_sync_utils_socket() {

    if (sync_utils_client_websocket == null) {
        return;
    }

    try{
        sync_utils_client_websocket.close();
    }catch(err){
        sync_utils_client_websocket.onmessage = null;
        sync_utils_client_websocket = null;
    }

}

function easyassist_send_message_over_sync_utils_socket(message, sender) {

    try{
        let allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;

        if (allow_cobrowsing == false) {
            return;
        }

        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
        if(easyassist_session_id == undefined || easyassist_session_id == null){
            return;
        }

        if(get_easyassist_cookie("easyassist_agent_connected") != "true"){
            return;
        }

        if(sync_utils_client_websocket_open == false || sync_utils_client_websocket == null){
            if(easyassist_send_message_over_sync_utils_socket.caller.name == "easyassist_socket_callee"){
                return;
            }
            setTimeout(function easyassist_socket_callee(){
                easyassist_send_message_over_sync_utils_socket(message, sender);
            }, 5000);
            console.log("sync_utils_client_websocket is not open");
            return;
        }

        if (sync_utils_client_websocket_open == true && sync_utils_client_websocket != null) {
            
            var msg = easyassist_custom_decrypt(message["Request"]); 
            msg = JSON.parse(msg);
            var type = msg["type"];

            if(easyassist_is_url_restricted()) {
                if(type == "mouse") {
                    message = easyassist_get_restricted_data_packet();
                }
            }

            var packet = JSON.stringify({
                "message": {
                    "header": {
                        "sender": sender,
                        "packet": packet_counter,
                        "client_page_id": easyassist_client_page_id,
                    },
                    "body": message
                }
            })

            sync_utils_client_websocket.send(packet);

            packet_counter += 1;
        }
    }catch(err){
        console.error("ERROR : easyassist_send_message_over_sync_utils_socket ", err);
    }
}

/******************* END EASYASSIST UTILITY WEBSOCKET ************************/
var easyassist_socket_not_open_count = 0;
var easyassist_socket_utils_not_open_count = 0;
var easyassist_socket_activity_interval_check = setInterval(easyassist_initialize_web_socket, 1000);

function easyassist_initialize_web_socket(){

    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        if(check_cobrowse_session_timer == null){
            easyassist_start_cobrowsing_activity_check();
        }
        return;
    }

    let allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;
    if (allow_cobrowsing == false) {
        return;
    }

    if(get_easyassist_cookie("easyassist_agent_connected") != "true"){
        return;
    }

    if (client_websocket == null) {
        easyassist_create_socket(easyassist_session_id, "client");
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
        easyassist_create_sync_utils_socket(easyassist_session_id, "client");
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

function easyassist_clear_notification_list(processed_notification_list) {
    try {
        if(processed_notification_list.length == 0) {
            return;
        }

        var updated_notification_list = [];
        easyassist_client_notification_list.forEach(function(notification_obj) {
            var packet_id = notification_obj.packet_id;
            if(processed_notification_list.indexOf(packet_id) == -1) {
                updated_notification_list.push(notification_obj);
            }
        });

        easyassist_client_notification_list = updated_notification_list;
    } catch(err) {
        console.log("easyassist_clear_notification_list: ", err);
    }
}

function easyassist_send_client_clear_notification_over_socket(notification_id_list) {
    try {

        if(notification_id_list.length == 0) {
            return;
        }

        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
        if (easyassist_session_id == null || easyassist_session_id == undefined) {
            return;
        }

        let json_string = JSON.stringify({
            "type": "clear_client_notifications",
            "notification_ids": notification_id_list
        });

        let encrypted_data = easyassist_custom_encrypt(json_string)
        encrypted_data = {
            "Request": encrypted_data
        };

        easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");

    } catch(err) {
        console.log("easyassist_send_client_clear_notification_over_socket: ", err);
    }
}

function easyassist_process_client_notifications() {
    try {
        var current_tab_active = easyassist_check_current_tab_active();
        if(current_tab_active == false) {
            return; 
        }

        if(easyassist_client_notification_list.length == 0) {
            return;
        }

        var processed_notification_id_list = [];
        easyassist_client_notification_list.forEach(function(notification_obj) {
            var packet_id = notification_obj.packet_id;
            var data_packet = notification_obj.data_packet;
            var client_page_id = notification_obj.client_page_id;

            easyassist_process_data_packet(data_packet, client_page_id);

            processed_notification_id_list.push(packet_id);
        });

        easyassist_send_client_clear_notification_over_socket(processed_notification_id_list);
    } catch(err) {
        console.log("easyassist_process_client_notifications: ", err);
    }
}

function easyassist_send_close_agent_chatbot_over_socket() {
    try {

        let json_string = JSON.stringify({
            "type": "close_agent_chatbot",
        });

        let encrypted_data = easyassist_custom_encrypt(json_string)
        encrypted_data = {
            "Request": encrypted_data
        };

        easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");

    } catch(err) {
        console.log("easyassist_send_close_agent_chatbot_over_socket: ", err);
    }
}

function easyassist_agent_socket_message_handler(data_packet, client_page_id, packet_id) {

    function easyassist_check_notification_packet() {
        var notification_types = [
            "chat",
            "request-edit-access",
            "revoke-edit-access",
            "support_agent_connected",
            "edit_access_granted",
            "edit_access_revoked",
            "support_agent_leave",
            "agent_weak_connection",
            "agent_message",
            "call_initiate_by_agent"
        ];

        if(notification_types.indexOf(data_packet.type) >= 0) {
            return true;
        }
        return false;
    }

    easyassist_reset_internet_connectivity_check_timer();

    if(data_packet.type == "chat") {
        // Directly process agent chats
        easyassist_sync_agent_chat(data_packet);
    }

    if(easyassist_check_notification_packet()) {

        easyassist_client_notification_list.push({
            "packet_id": packet_id,
            "data_packet": data_packet,
            "client_page_id": client_page_id,
        });
        easyassist_process_client_notifications();
        return;
    }

    if(client_page_id && client_page_id != easyassist_client_page_id) {
        var allowed_packet_types = [
            "html",
            "iframe_html",
            "client_page_info",
            "end_voip_meeting",
            "livechat-typing",
        ];

        if(allowed_packet_types.indexOf(data_packet.type) == -1) {
            return;
        }
    }

    easyassist_process_data_packet(data_packet, client_page_id);
}

function easyassist_client_socket_message_handler(data_packet, client_page_id, packet_id) {

    if(data_packet.type == "chat") {

        if(client_page_id != easyassist_client_page_id) {
            easyassist_sync_client_chat(data_packet);
        }

    } else if(data_packet.type == "clear_client_notifications") {

        easyassist_clear_notification_list(data_packet.notification_ids);

    } else if (data_packet.type == "end_voip_meeting") {
        set_easyassist_cookie("is_easyassist_meeting_on_client", "");
    }
}

function easyassist_check_data_packet_type_restricted(data_packet_type) {
    try {
        if(!easyassist_is_url_restricted()) {
            return false;
        }

        const restricted_types = [
            "mouse",
            "highlight",
            "request-edit-access",
            "sync_canvas",
            "sync-form",
            "div-scroll",
            "sync-scroll"
        ];

        if(restricted_types.indexOf(data_packet_type) > -1) {
            return true;
        }

        return false;
    } catch(err) {
        console.log("easyassist_check_data_packet_type_restricted: ", err);
    }
    return false;
}

function easyassist_process_data_packet(data_packet, client_page_id) {

    if(easyassist_check_data_packet_type_restricted(data_packet.type)) {
        return;
    }

    if (data_packet.type == "highlight") {

        easyassist_sync_agent_highlight(data_packet);

    } else if (data_packet.type == "open_pdf_render_modal") {
        if(easyassist_check_current_tab_active()) {
            easyassist_hide_livechat_iframe();
            easyassist_show_chat_bubble();
            easyassist_show_pdf_render_modal(data_packet.file_name,data_packet.file_src,data_packet.session_id);
        } else {
            easyassist_send_tab_not_focus_over_socket();
        }

    } else if (data_packet.type == "screenshot") {

        if(easyassist_is_url_restricted()) {
            easyassist_send_screenshot_405_status();
        } else {
            easyassist_capture_client_screenshot(data_packet.agent_name);
        }

    } else if (data_packet.type == "pageshot") {

        easyassist_capture_client_pageshot();

    } else if (data_packet.type == "html") {

        easyassist_disconnect_mutation_summary_client();

        if(client_page_id == easyassist_client_page_id) {

            easyassist_send_html_request_received_message_over_socket();
            if(data_packet.is_agent_weak_connection == true) {
                EasyAssistLowBandWidthHTML.set_agent_weak_connection_value(true);
            } else {
                EasyAssistLowBandWidthHTML.set_agent_weak_connection_value(false);
            }
            easyassist_set_agent_weak_connection_cookie();
            easyassist_sync_html_data();
        }

    } else if (data_packet.type == "sync-scroll") {

        easyassist_sync_client_scroll_position(data_packet);

    } else if (data_packet.type == "mouse") {

        easyassist_sync_agent_mouse(data_packet);

    } else if (data_packet.type == "chat") {
        // We come here after processiing client notification list.
        // Notification will be processed only if the tab is in focus.
        if(data_packet.chat_type != "chat_bubble") {
            if(EASYASSIST_COBROWSE_META.enable_chat_bubble) {
                easyassist_show_livechat_iframe(false);
            } else {
                easyassist_show_livechat_iframe();
            }
        }
    } else if (data_packet.type == "livechat-typing") {

        easyassist_sync_typing_loader(data_packet);

    } else if (data_packet.type == "request-edit-access") {

        easyassist_show_request_edit_access_form();

    } else if (data_packet.type == "revoke-edit-access") {
        
        agent_revoke_edit_access = true;
        easyassist_revoke_edit_access();

    } else if (data_packet.type == "sync-form") {

        easyassist_sync_agent_form_activity(
            data_packet, data_packet.type, easyassist_agent_sync_form);

    } else if (data_packet.type == "button-click") {

        easyassist_sync_agent_form_activity(
            data_packet, data_packet.type, easyassist_sync_button_click_event);

    } else if (data_packet.type == "end_voip_meeting") {

        set_easyassist_cookie("is_easyassist_meeting_on_client", "");
        easyassist_end_voip_meeting(data_packet);

    } else if (data_packet.type == "voip_meeting_ready") {

        easyassist_voip_meeting_ready(data_packet);

    } else if (data_packet.type == "div-scroll") {

        easyassist_sync_agent_form_activity(
            data_packet, data_packet.type, easyassist_sync_agent_div_scroll);

    } else if (data_packet.type == "support_agent_connected") {
        
        easyassist_show_toast("Agent " + data_packet.agent_name + " has joined the session.");

    } else if (data_packet.type == "transferred_agent_connected") {
        set_easyassist_current_session_local_storage_obj("agent_details_json", "");
        easyassist_show_toast("Agent " + data_packet.agent_name + " has joined the session.");
        easyassist_fetch_agent_details(false);

    } else if (data_packet.type == "edit_access_granted") {

        set_easyassist_cookie("easyassist_edit_access_granted", "true");
        if (EASYASSIST_COBROWSE_META.is_mobile == true) {
            document.getElementById("revoke-edit-access-button").parentElement.parentElement.style.display = "inherit";
        } else {
            document.getElementById("revoke-edit-access-button").style.display = "flex";
        }
        easyassist_show_edit_access_info_modal();
    } else if (data_packet.type == "edit_access_revoked") {

        if (EASYASSIST_COBROWSE_META.is_mobile == true) {
            document.getElementById("revoke-edit-access-button").parentElement.parentElement.style.display = "none";
        } else {
            document.getElementById("revoke-edit-access-button").style.display = "none";
        }

    } else if (data_packet.type == "support_agent_leave") {

        easyassist_show_toast("Agent " + data_packet.agent_name + " has left the session.");

    }  else if (data_packet.type == "agent_weak_connection") {

        if(get_easyassist_cookie("easyassist_session_id")){
            if(get_easyassist_cookie("easyassist_agent_weak_internet_connection_shown") == undefined || get_easyassist_cookie("easyassist_agent_weak_internet_connection_shown") == "false"){
                easyassist_show_agent_weak_internet_connection();
                set_easyassist_cookie("easyassist_agent_weak_internet_connection_shown", "true")
            }
        }

    } else if (data_packet.type == "agent_low_bandwidth_html_request") {

        EasyAssistLowBandWidthHTML.set_agent_weak_connection_value(data_packet.is_agent_weak_connection);
        easyassist_set_agent_weak_connection_cookie();

        if(data_packet.is_html_needed) {
            easyassist_sync_html_data();
        }

    } else if (data_packet.type == "client_low_bandwidth_html_request") {

        EasyAssistLowBandWidthHTML.set_agent_weak_connection_value(true);
        easyassist_sync_html_data();

    } else if (data_packet.type == "get_lead_status") {

        easyassist_check_is_lead_converted();

    } else if (data_packet.type == "agent_message") {

        easyassist_show_toast(data_packet.message);

    } else if(data_packet.type == "sync_canvas") {

        easyassist_sync_agent_canvas(data_packet);

    } else if(data_packet.type == "reset_canvas") {

        easyassist_reset_agent_canvas();

    } else if(data_packet.type == "client_page_info") {

        easyassist_send_client_page_details();

    } else if(data_packet.type == "iframe_html") {

        EasyAssistSyncIframe.easyassist_sync_all_iframes();

    } else if(data_packet.type == "call_initiate_by_agent"){
        // call_initiate_by_agent = "true";
        set_easyassist_current_session_local_storage_obj("call_initiate_by_agent", "true");
    } else if (data_packet.type == "invited_agent_disconnected") {

        var message = data_packet.invited_agent_name + " left the ongoing call.";
        easyassist_show_toast(message);

    }
}

function easyassist_sync_agent_canvas(data_packet) {
    try {

        var prev_x = data_packet.prev_x;
        var prev_y = data_packet.prev_y;
        var curr_x = data_packet.curr_x;
        var curr_y = data_packet.curr_y;
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

function easyassist_resize_easyassist_canvas() {
    try {
        easyassist_drawing_canvas.resize_canvas(window.innerWidth, window.innerHeight);
    } catch(err) {
        console.log("easyassist_resize_easyassist_canvas: ", err);
    }
}

function easyassist_set_agent_weak_connection_cookie() {
    if(EasyAssistLowBandWidthHTML.get_agent_weak_connection_value()) {
        set_easyassist_cookie("easyassist_agent_weak_connection", get_easyassist_cookie("easyassist_session_id"));
    } else {
        delete_easyassist_cookie("easyassist_agent_weak_connection");
    }
}

function easyassist_check_for_agent_guide(e) {

    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    var data = JSON.parse(e.data);
    let message = data.message;
    let agent_packet = "";
    
    if(!message.body) {
        return;
    }
    
    try{
        agent_packet = message.body.Request;
    }catch(err){
        console.trace();
        console.log("Please look at this report this to developer ", message)
    }

    if (message.body.is_encrypted == false) {
        agent_packet = JSON.parse(agent_packet);
    } else {
        agent_packet = easyassist_custom_decrypt(agent_packet);
        agent_packet = JSON.parse(agent_packet);
    }

    var client_page_id = message.header.client_page_id;
    var packet_id = message.header.packet_id;

    if (message.header.sender == "agent") {

        easyassist_agent_socket_message_handler(agent_packet, client_page_id, packet_id);

    } else {

        easyassist_client_socket_message_handler(agent_packet, client_page_id, packet_id);

    }
}

/************************* END SOCKET MESSAGE HANDLER ******************************/

function easyassist_initiate_cobrowsing() {

    try {
        easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
        if (easyassist_session_id != undefined && EASYASSIST_SESSION_ID != null) {
            if (EASYASSIST_COBROWSE_META.show_floating_button_after_lead_search == true) {
                var easyassist_session_created_on = get_easyassist_cookie("easyassist_session_created_on");
                if (easyassist_session_created_on != undefined && easyassist_session_created_on != null) {
                    if (easyassist_session_created_on == "request") {
                        easyassist_hide_floating_sidenav_button();
                    }
                } else {
                    easyassist_hide_floating_sidenav_button();
                }
            } else {
                easyassist_hide_floating_sidenav_button();
            }

            window.onclick = easyassist_send_data_to_server;
            window.onresize = easyassist_send_data_to_server;
            window.onmousedown = easyassist_send_data_to_server;
            window.onkeyup = easyassist_send_data_to_server;
            window.onscroll = easyassist_send_data_to_server;
            // window.onbeforeunload = null;
            window.onmousemove = function(event) {
                easyassist_sync_mouse_position(event);
            }

            if(!check_proxy_cobrowsing()){
                add_easyassist_event_listner_into_element(window, "focus", easyassist_client_page_focus_action);
                add_easyassist_event_listner_into_element(window, "blur", easyassist_send_page_blur_over_socket);
            }
            
            add_easyassist_event_listner_into_element(window, "beforeunload", easyassist_page_reload_action);

            easyassist_client_heartbeat_timer = setInterval(function(e) {
                easyassist_client_heartbeat();
            }, 5000);

            easyassist_check_for_agent_guide_timer = setInterval(function(e) {
                easyassist_check_for_agent_highlight();
            }, EASYASSIST_COBROWSE_META.highlight_api_call_frequency * 1000);

            let agent_connected_cookie = get_easyassist_cookie("easyassist_agent_connected");
            var session_creation_mode = get_easyassist_cookie("easyassist_session_created_on");
            if (agent_connected_cookie != "true" && session_creation_mode == "request") {
                easyassist_initiate_connection_with_timer_modal();
            }

            easyassist_remove_formassist_stuck_timer_handler();
            easyassist_load_chat_history();
            easyassist_check_for_agent_highlight();
        }
    } catch (err) {
        console.log("easyassist_initiate_cobrowsing: ", err);
        setTimeout(function() {
            easyassist_initiate_cobrowsing();
        }, 1000);
    }
}

function easyassist_client_page_focus_action() {
    try {
        easyassist_process_client_notifications();
        easyassist_send_page_focus_over_socket();
    }  catch(err) {
        console.log("easyassist_client_page_focus_action: ", err);
    }
}

function easyassist_send_page_focus_over_socket() {
    try {
        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
        if (easyassist_session_id == null || easyassist_session_id == undefined) {
            return;
        }

        let json_string = JSON.stringify({
            "type": "client_tab_focus",
        });

        let encrypted_data = easyassist_custom_encrypt(json_string)
        encrypted_data = {
            "Request": encrypted_data
        };

        easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");

    } catch(err) {
        console.log("easyassist_send_page_focus_over_socket: ", err);
    }
}

function easyassist_send_page_blur_over_socket() {
    try {
        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
        if (easyassist_session_id == null || easyassist_session_id == undefined) {
            return;
        }

        let json_string = JSON.stringify({
            "type": "client_tab_blur",
        });

        let encrypted_data = easyassist_custom_encrypt(json_string)
        encrypted_data = {
            "Request": encrypted_data
        };

        easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");

    } catch(err) {
        console.log("easyassist_send_page_focus_over_socket: ", err);
    }
}

function easyassist_send_tab_close_over_socket() {
    try {
        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
        if (easyassist_session_id == null || easyassist_session_id == undefined) {
            return;
        }

        let json_string = JSON.stringify({
            "type": "client_tab_close",
        });

        let encrypted_data = easyassist_custom_encrypt(json_string)
        encrypted_data = {
            "Request": encrypted_data
        };

        easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");

    } catch(err) {
        console.log("easyassist_send_tab_close_over_socket: ", err);
    }
}

function easyassist_update_agent_assistant_request(status) {

    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        document.getElementById("easyassist-co-browsing-request-assist-modal").style.display = "none";
        return;
    }

    var client_otp = "None";

    if (status == "true" && EASYASSIST_COBROWSE_META.enable_verification_code_popup == true) {
        client_otp = "";
        let verify_inputs = easyassist_get_eles_by_class_name("easyassist-verfication-otp-input")
        for (let i = 0; i < verify_inputs.length; i++) {
            client_otp += verify_inputs[i].value
        }
        if (client_otp == "" || client_otp == undefined || client_otp == null) {
            document.getElementById("easyassist-request-assist-otp-error").innerHTML = "Please enter valid OTP";
            document.getElementById("easyassist-request-assist-otp-error").previousSibling.style.paddingBottom = "1em";
            return;
        }
    }

    // Show verfication modal for agent cobrowsing request
    delete_easyassist_cookie("agent_requested_for_assistant");

    let json_string = JSON.stringify({
        "id": easyassist_session_id,
        "otp": client_otp,
        "status": status
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/update-agent-assistant-request/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                document.getElementById("easyassist-co-browsing-request-assist-modal").style.display = "none";
                if (document.getElementById("easyassist-request-assist-otp-error")) {
                    document.getElementById("easyassist-request-assist-otp-error").innerHTML = "";
                    document.getElementById("easyassist-request-assist-otp-error").previousSibling.style.paddingBottom = "1em";
                }

                if (status == "true") {
                    easyassist_show_agent_joining_modal();
                    easyassist_go_to_sceensharing_tab(response);
                    set_easyassist_cookie("easyassist_cobrowsing_allowed", "true");
                } else {
                    set_easyassist_cookie("easyassist_cobrowsing_allowed", "false");
                }
                easyassist_check_for_agent_highlight();
            } else {
                if (document.getElementById("easyassist-request-assist-otp-error")) {
                    document.getElementById("easyassist-request-assist-otp-error").innerHTML = "Please enter valid OTP";
                    document.getElementById("easyassist-request-assist-otp-error").previousSibling.style.paddingBottom = "1em";
                }
            }
        } else if (this.readyState == 4) {
            document.getElementById("easyassist-request-assist-otp-error").innerHTML = EASYASSIST_FUNCTION_FAIL_DEFAULT_MESSAGE;
            document.getElementById("easyassist-request-assist-otp-error").previousSibling.style.paddingBottom = "1em";
        }
    }
    xhttp.send(params);
}

function easyassist_update_agent_location_detail(agent_details){
    try {
        if (agent_details.agent_name != null) {
            var agent_location = agent_details.agent_location;
            if (agent_location == "None" || agent_location == "") {
                agent_location = "Location not shared";
            }
            if(EASYASSIST_COBROWSE_META.display_agent_profile && agent_details.agent_profile_pic_source != "") {
                let src = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/" + agent_details.agent_profile_pic_source;
                let agent_modal_html = [
                    '<img src = "'+ src + '"/>'
                ]
                document.querySelector(".agent-profile").innerHTML = agent_modal_html;
            }
        }

        if (document.getElementById("easyassist-agent-information-agent-name").innerHTML.trim() != agent_details.agent_name) {
            document.getElementById("easyassist-agent-information-agent-name").innerHTML = "Name: <strong>" + agent_details.agent_name + "</strong>";
            if (agent_details.agent_email != "None" && agent_details.show_agent_email) {
                var agent_email_element = document.getElementById("easyassist-agent-information-agent-email-id");
                agent_email_element.style.display = "block";
                agent_email_element.innerHTML = "Email: <strong>" + agent_details.agent_email + "</strong>";
            }
            document.getElementById("easyassist-agent-information-agent-location").innerHTML = "Address: <strong>" + agent_location + "</strong>";
            if (agent_details.agent_additional_details_response != null) {
                easyassist_append_agent_additional_details(agent_details.agent_additional_details_response);
            }
        }
    } catch (err) {
        console.log("easyassist_update_agent_location_detail: ", err)
    }
}

function easyassist_append_agent_additional_details(agent_additional_details_response) {
    try {
        var json_response = JSON.parse(agent_additional_details_response);
        var counter = 0;
        var html = "";

        for (var key in json_response) {
            if (json_response.hasOwnProperty(key)) {
                if (counter >= 10) {
                    break;
                }
                var detail_value = json_response[key];
                var detail_key = key;
                html += `<div class="easyassist-agent-information-text">${detail_key}: <strong>${detail_value}</strong></div>`;
                counter += 1;
            }
        }

        document.getElementById("easyassist-agent-additional-details").innerHTML = html;
        document.getElementById("easyassist-agent-additional-details").style.display = "inherit";

    } catch (error) {
        console.log("easyassist_append_agent_additional_details: ", error);
    }
}

function easyassist_agent_request_actions() {
    easyassist_hide_connection_with_timer_modal();
    easyassist_hide_minimized_timer_modal();
    easyassist_clear_agent_wait_timer();
}

function easyassist_allow_agent_assistant_request_hander() {
    try {
        easyassist_agent_request_actions();
        let is_current_tab_focussed = easyassist_check_current_tab_active();
        var request_assistant_modal = document.getElementById("easyassist-co-browsing-request-assist-modal");

        if(!is_current_tab_focussed) {
            return;
        }

        if(request_assistant_modal.style.display == "flex") {
            return;
        }

        if(get_easyassist_cookie("agent_requested_for_assistant") == "true") {
            return;
        }

        set_easyassist_cookie("agent_requested_for_assistant", "true");

        let verify_inputs = easyassist_get_eles_by_class_name("easyassist-verfication-otp-input")
        for (let idx = 0; idx < verify_inputs.length; idx++) {
            verify_inputs[idx].value = "";
            verify_inputs[idx].style.color = 'inherit';
            verify_inputs[idx].style.borderColor = 'inherit';
        }

        request_assistant_modal.style.display = "flex";
        delete_easyassist_cookie("easyassist_session_created_on");
        easyassist_hide_floating_sidenav_button();

        if(verify_inputs.length > 0) {
            verify_inputs[0].focus();
        }

    } catch(err) {
        console.log("easyassist_allow_agent_assistant_request_hander: ", err);
    }
}

function easyassist_agent_meeting_request_hander() {
    try {
        easyassist_agent_request_actions();

        let is_current_tab_focussed = easyassist_check_current_tab_active();

        if(!is_current_tab_focussed) {
            return;
        }

        if(get_easyassist_cookie("agent_meeting_request_status") == "true") {
            return;
        }

        set_easyassist_cookie("agent_meeting_request_status", "true");
        var meeting_request_modal = document.getElementById("easyassist-co-browsing-request-meeting-modal");
        if(EASYASSIST_COBROWSE_META.allow_video_meeting_only == false) {
            if (EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {
                meeting_request_modal = document.getElementById("easyassist-voip-video-calling-request-modal");
            } else if (EASYASSIST_COBROWSE_META.enable_voip_calling) {
                meeting_request_modal = document.getElementById("easyassist-voip-calling-request-modal");
            }
        }

        if(meeting_request_modal.style.display != "flex") {
            meeting_request_modal.style.display = "flex";
            close_modal();
        }
        
        delete_easyassist_cookie("easyassist_session_created_on");
        easyassist_hide_floating_sidenav_button();

    } catch(err) {
        console.log("easyassist_agent_meeting_request_hander: ", err);
    }
} 

function easyassist_client_allow_meeting_request_handler() {
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
        if (EASYASSIST_COBROWSE_META.allow_video_meeting_only == true) {
            if(easyassist_check_cobrowse_meeting_on() == false) {
                show_customer_side_call_icon(false);
                easyassist_open_meeting_window();
                EASYASSIST_COBROWSE_META.allow_meeting = true;
            }
        } else {
            if (EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {
                show_customer_side_call_icon(false);
                easyassist_start_voip_with_video_calling();
            } else if (EASYASSIST_COBROWSE_META.enable_voip_calling) {
                if(easyassist_check_cobrowse_meeting_on() == false) {
                    show_customer_side_call_icon(false);
                    easyassist_open_voip_meeting_window();
                }
            } else {
                if(easyassist_check_cobrowse_meeting_on() == false) {
                    show_customer_side_call_icon(false);
                    easyassist_open_meeting_window();
                }
            }
        }
    } catch(err) {
        console.log("easyassist_client_allow_meeting_request_handler: ", err);
    }
}

function easyassist_create_custom_snackbar() {

    var div = document.createElement("div");
    div.id = "easyassist-snackbar-custom";

    document.getElementsByTagName("body")[0].appendChild(div);
}

function easyassist_show_long_toast(message) {
    easyassist_create_custom_snackbar();

    var easyassist_snackbar_custom = document.getElementById("easyassist-snackbar-custom");
    easyassist_snackbar_custom.innerHTML = message;
    easyassist_snackbar_custom.className = "show";

    setTimeout(function () {
        easyassist_snackbar_custom.className = easyassist_snackbar_custom.className.replace("show", "");
    }, 5000);
}

function easyassist_check_for_agent_highlight() {

    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    let allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        easyassist_terminate_cobrowsing_session();
        return;
    }
    
    var title = window.location.href;
    if (document.querySelector("title") && document.querySelector("title").innerText.trim() != "") {
        title = document.querySelector("title").innerHTML;
    }
    
    var url = window.location.href;
        
    if(check_proxy_cobrowsing() && document.getElementById("proxy-iframe")) {
        let proxy_url = document.getElementById("proxy-iframe").contentWindow.location.href
        url = proxy_url.substring(proxy_url.indexOf(window.proxy_key) + window.proxy_key.length+1);
        if(url.indexOf("http://") != 0 || url.indexOf("https://") != 0) {
            let domain = new URL(window.proxy_active_url)
            url = domain.origin + '/' + url;
        }
        title = sanitize_input_string(document.getElementById('proxy-iframe').contentWindow.document.title);
    }
        
    let json_string = JSON.stringify({
        "id": easyassist_session_id,
        "drop_off_meta_data": {
            "product_details": {
                "title": title,
                "url": url
            }
        }
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/highlight/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function easyassist_highlight_api_response_handler() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            
            // is_current_tab_focussed = easyassist_check_current_tab_active();

            if (response.status == 500) {
                console.log("Interval Clearted", response);
                clearInterval(easyassist_check_for_agent_guide_timer);
                easyassist_terminate_cobrowsing_session();
                return;
            }

            if (response.status != 200) {
                console.log("Interval Cleared", response);
                clearInterval(easyassist_check_for_agent_guide_timer);
                return;
            }

            /*************** Session Archive START *************/

            if (response.is_archived == true) {
                easyassist_agent_request_actions();

                if(easyassist_session_expired_flag == true) return;

                easyassist_session_expired_flag = true;

                document.getElementById("agent-mouse-pointer").style.display = "none";
                easyassist_hide_floating_sidenav_menu();

                if (response.is_unassigned_lead == true) {

                    if (response.archive_message_on_unassigned_time_threshold) {
                        easyassist_show_long_toast(response.archive_message_on_unassigned_time_threshold);
                    }
                    
                    easyassist_terminate_cobrowsing_session(false);
                    return;
                }

                if(response.session_ended_by_agent == true && (response.cobrowsing_start_datetime != null || response.meeting_start_datetime != null)){
                    easyassist_show_toast(response.agent_name + " has ended the session.");
                    var session_archived_datetime = new Date(response.session_archived_datetime);
                    let time_delta = parseInt((new Date() - session_archived_datetime) / 1000)
                    if (time_delta >= 5 * 60) {
                        var feedback_modal = document.getElementById("easyassist-co-browsing-feedback-modal");
                        document.getElementById("feedback-modal-header-text").innerHTML = "Please provide the feedback for the last Cobrowsing session";
                        document.getElementById("feedback-modal-header-text").style.paddingTop = "30px";
                        feedback_modal.querySelector(".easyassist-customer-feedback-modal-header").classList.add("feedback-modal-padding")
                    }
                    if(is_cobrowsing_from_livechat){
                        end_livechat_cobrowsing_session(easyassist_session_id);
                    }
                    easyassist_show_feedback_form();
                } else {
                    if(response.is_auto_reassign_enabled && !response.is_modified_inbound_session) {
                        easyassist_show_long_toast(response.auto_assign_lead_end_session_message);
                    } else {
                        easyassist_show_toast("Agent has ended the session. Please try raising a new request.");
                    }
                    easyassist_terminate_cobrowsing_session(false);
                }

                return
            }

            /*************** Session Archive END *************/

            if(response.is_auto_reassign_enabled && response.notify_client_about_reassignment) {
                if(EASYASSIST_COBROWSE_META.no_agent_connects_toast) {
                    var timer_modal_body_ele = document.getElementById("easyassist-connection-timer-modal-body").children[0];
                    if (timer_modal_body_ele && !is_easyassist_connection_timer_closed()) {
                        timer_modal_body_ele.innerHTML = response.auto_assign_unattended_lead_message;
                        easyassist_maximize_connection_with_timer_modal();
                        set_easyassist_current_session_local_storage_obj("easyassist_agent_reassigned", "true");
                    }
                } else {
                    easyassist_show_toast(response.auto_assign_unattended_lead_message);
                }
            }

            if (response.agent_assistant_request_status == true) {
                agent_requested_for_assistant = true;
                easyassist_allow_agent_assistant_request_hander();
            }

            if (response.agent_meeting_request_status == true) {
                agent_meeting_request_status = true;
                easyassist_agent_meeting_request_hander();
            }

            if (response.allow_agent_meeting == "true") {
                easyassist_client_allow_meeting_request_handler();
            } else {
                EASYASSIST_COBROWSE_META.allow_meeting = false;
            }

            if (response.allow_agent_cobrowse == "true") {
                EASYASSIST_COBROWSE_META.allow_cobrowsing = true;
            } else {
                EASYASSIST_COBROWSE_META.allow_cobrowsing = false;
            }

            if (EASYASSIST_COBROWSE_META.allow_meeting == false && EASYASSIST_COBROWSE_META.allow_cobrowsing == false) {
                return;
            }

            if(response.is_cobrowsing_from_livechat){
                is_cobrowsing_from_livechat = true;
            }

            if (response.agent_name == null && EASYASSIST_COBROWSE_META.lead_generation == false) {
                easyassist_show_toast("Our customer service agent will join the session soon.");
                return;
            }
            if (response.is_agent_connected == true) {
                easyassist_hide_agent_joining_modal();
                easyassist_show_floating_sidenav_menu();
                easyassist_agent_request_actions();
                easyassist_fetch_agent_details();
                if (EASYASSIST_COBROWSE_META.enable_masked_field_warning == true) {
                    easyassist_get_eles_by_class_name("easyassist-tooltiptext")[0].style.display = "inline";
                }
                let agent_connected_cookie = get_easyassist_cookie("easyassist_agent_connected");
                if (is_agent_connected == false && agent_connected_cookie != "true") {
                    set_easyassist_cookie("easyassist_agent_connected", "true");
                    delete_easyassist_cookie("easyassist_session_created_on");
                    is_agent_connected = true;
                }
            } else if (response.is_agent_connected == false) {
                if (is_agent_connected == true) {
                    easyassist_show_toast(response.agent_name + " has left the session.");
                    is_agent_connected = false;
                    easyassist_get_eles_by_class_name("easyassist-tooltiptext")[0].style.display = "none";
                }
            }

            if(response.is_agent_connected && is_client_network_bandwidth_measured == false) {
                is_client_network_bandwidth_measured = true;
                easyassist_initiate_internet_speed_detection();
            }
            
        }
    }
    xhttp.send(params);
}

function end_livechat_cobrowsing_session(session_id) {

    let json_string = JSON.stringify({
        cobrowse_session_id: session_id,
    });

    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    let xhttp = new XMLHttpRequest();
    let params = "json_string=" + json_string;
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + '/livechat/end-cobrowsing-session/', true);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            
        }
    }
    xhttp.send(params);
}

function easyassist_fetch_agent_details(show_modal=true) {

    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    var local_storage_obj = get_easyassist_current_session_local_storage_obj();
    if (local_storage_obj && local_storage_obj.hasOwnProperty("agent_details_json") && local_storage_obj.agent_details_json) {
        return;
    }

    let json_string = JSON.stringify({
        "id": easyassist_session_id
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/fetch-connected-agent-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                var agent_details = {
                    "agent_name": response.agent_name,
                    "agent_location": response.agent_location,
                    "agent_email": response.agent_email,
                    "show_agent_email": response.show_agent_email,
                    "agent_additional_details_response": response.agent_additional_details_response,
                    "display_agent_profile": response.display_agent_profile,
                    "agent_profile_pic_source": response.agent_profile_pic_source,
                };

                document.getElementById("easyassist-agent-additional-details").style.display = "none";
                document.getElementById("easyassist-agent-additional-details").innerHTML = "";

                set_easyassist_current_session_local_storage_obj("agent_details_json", JSON.stringify(agent_details));

                easyassist_update_agent_location_detail(agent_details);

                if (response.show_agent_details_modal) {
                    if(show_modal) {
                        easyassist_show_agent_information_modal(true);
                        window.setTimeout(easyassist_hide_agent_information_modal, 10000);
                    }
                } else {
                    easyassist_show_toast("Agent " + response.agent_name + " has joined the session.");
                }

                easyassist_show_chat_bubble();

            } else {
                console.error("Agent details API failed.")
            }
        }
    }
    xhttp.send(params);
}

function easyassist_delete_all_cookie(){
    delete_easyassist_cookie("easyassist_session_id");
    delete_easyassist_cookie("easyassist_agent_connected");
    delete_easyassist_cookie("easyassist_cobrowsing_allowed");
    delete_easyassist_cookie("easyassist_edit_access");
    delete_easyassist_cookie("easyassist_edit_access_granted");
    delete_easyassist_cookie("easyassist_customer_id");
    delete_easyassist_cookie("cobrowse_meeting_id");
    delete_easyassist_cookie("is_lead_converted");
    delete_easyassist_cookie("page_leave_status");
    delete_easyassist_cookie("no_of_time_exit_modal_popup");
    delete_easyassist_cookie("easyassist_messages_sent_to_customer");
    delete_easyassist_cookie("easyassist_session_created_on");
    delete_easyassist_cookie("agent_requested_for_assistant");
    delete_easyassist_cookie("agent_meeting_request_status");
    delete_easyassist_cookie("easyassist_feedback_modal_shown");
    delete_easyassist_cookie("easyassist_client_disconnected_modal_shown");
    delete_easyassist_cookie("easyassist_client_weak_internet_connection_shown");
    delete_easyassist_cookie("easyassist_agent_weak_internet_connection_shown");
    delete_easyassist_cookie("easyassist_agent_disconnected_modal_shown");
    delete_easyassist_cookie("is_cobrowse_meeting_on");
    delete_easyassist_cookie("easyassist_function_fail_count");
    delete_easyassist_cookie("easyassist_agent_weak_connection");
    delete_easyassist_cookie("cobrowse_voip_meeting_shown");
    delete_easyassist_cookie("no_of_times_default_text_on_modal");
    delete_easyassist_cookie("inactivity_auto_popup_number");
    delete_easyassist_cookie("timer_modal_reset_count");
    delete_easyassist_cookie("is_timer_iterations_elapsed");
    easyassist_clear_local_storage();
}

function easyassist_terminate_cobrowsing_session(show_message = true) {
    try {

        let json_string = JSON.stringify({
            "type": "end_session",
        });

        let encrypted_data = easyassist_custom_encrypt(json_string)
        encrypted_data = {
            "Request": encrypted_data
        };

        easyassist_send_message_over_socket(encrypted_data, "client");
        easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");

        EASYASSIST_COBROWSE_META.allow_cobrowsing = false;

        try {
            if (easyassist_client_heartbeat_timer != null && easyassist_client_heartbeat_timer != undefined) {
                clearInterval(easyassist_client_heartbeat_timer);
                easyassist_client_heartbeat_timer = null;
            }
            if (easyassist_check_for_agent_guide_timer != null && easyassist_check_for_agent_guide_timer != undefined) {
                clearInterval(easyassist_check_for_agent_guide_timer);
                easyassist_check_for_agent_guide_timer = null;
            }
            if(easyassist_send_client_weak_connection_message_interval != null &&
                easyassist_send_client_weak_connection_message_interval != undefined){
                clearInterval(easyassist_send_client_weak_connection_message_interval);
                easyassist_send_client_weak_connection_message_interval = null;
            }

            easyassist_disconnect_mutation_summary_client();
        } catch (err) {
            console.log(err);
        }

        if (EASYASSIST_COBROWSE_META.enable_proxy_cobrowsing) {
            let first_index = window.location.href.indexOf("proxy-key");
            if (first_index > 0) {
                window.open("/easy-assist/cognoai-cobrowse/proxy-cobrowsing-end-page","_self");
            }
        }

        easyassist_end_cobrowse_video_meet();
        easyassist_delete_all_cookie();
        easyassist_close_socket();
        easyassist_close_sync_utils_socket();
        easyassist_hide_floating_sidenav_menu();
        easyassist_hide_feedback_form();
        easyassist_reset_global_var();
        easyassist_hide_livechat_iframe();
        easyassist_refresh_livechat_iframe();
        easyassist_add_formassist_stuck_timer_handler();
        easyassist_stop_internet_connectivity_check_timer();
        easyassist_hide_connection_with_timer_modal();
        easyassist_hide_minimized_timer_modal();
        easyassist_hide_cobrowse_mobile_navbar_menu();

        if(document.getElementById("agent-mouse-pointer")){
            document.getElementById("agent-mouse-pointer").style.display = "none";
        }
        if(easyassist_get_eles_by_class_name("easyassist-tooltiptext").length > 0){
            easyassist_get_eles_by_class_name("easyassist-tooltiptext")[0].style.display = "none";
        }

        if (show_message) {
            easyassist_show_toast("Session has ended");
        }
    } catch (err) {
        easyassist_delete_all_cookie();
        console.error("Error on termination", err)
    }
}

function easyassist_submit_client_feedback(feedback_type) {
    if(document.getElementById("chat-minimize-icon-wrapper")) {
        document.getElementById("chat-minimize-icon-wrapper").style.display = "none";
        document.getElementById("chat-talk-bubble").style.display = "none";
    }
    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    var rating = easyassist_get_user_rating();
    if (feedback_type != "no_feedback") {
        if (rating == null) {
            document.getElementById("easyassist-feedback-error").innerHTML = "Please provide a rating and then click on Submit";
            document.getElementById("easyassist-feedback-error").style.display = "block";
            return;
        }
    }
    
    var title = window.location.href;
    if (document.querySelector("title") && document.querySelector("title").innerText.trim() != "") {
        title = document.querySelector("title").innerHTML;
    }
    
    var url = window.location.href;
    if(check_proxy_cobrowsing() && document.getElementById("proxy-iframe")) {
        let proxy_url = document.getElementById("proxy-iframe").contentWindow.location.href
        url = proxy_url.substring(proxy_url.indexOf(window.proxy_key) + window.proxy_key.length+1);
        if(url.indexOf("http://") != 0 || url.indexOf("https://") != 0) {
            let domain = new URL(window.proxy_active_url)
            url = domain.origin + '/' + url;
        }
        title = sanitize_input_string(document.getElementById('proxy-iframe').contentWindow.document.title);
    }

    let feedback = document.getElementById("easyassist-client-feedback").value;

    feedback = remove_special_characters_from_str(feedback);

    try {
        if (feedback) {
            feedback = feedback.trim();
        }
        if (feedback.length > 200) {
            document.getElementById("easyassist-feedback-error").innerHTML = "Remarks cannot be more than 200 characters";
            document.getElementById("easyassist-feedback-error").style.display = "block";
            return;
        }
    } catch (err) {}

    let json_string = JSON.stringify({
        "session_id": easyassist_session_id,
        "rating": rating,
        "feedback": feedback,
        "drop_off_meta_data": {
            "product_details": {
                "title": title,
                "url": url
            }
        }
    });

    if (is_cobrowsing_from_livechat) {
        send_nps_for_livechat(easyassist_session_id, rating, feedback);
    }
    
    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/submit-client-feedback/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            easyassist_terminate_cobrowsing_session();
        } else if (this.readyState == 4) {

            easyassist_terminate_cobrowsing_session();
        }
    }
    xhttp.send(params);
}

function send_nps_for_livechat(session_id, rating, feedback) {

    let json_string = JSON.stringify({
        session_id: session_id,
        rating: rating,
        feedback: feedback,
    });

    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    let xhttp = new XMLHttpRequest();
    let params = "json_string=" + json_string;
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + '/livechat/save-cobrowsing-nps/', true);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            
        }
    }
    xhttp.send(params);
}


function easyassist_check_agent_available_status(callback=null) {
    let json_string = JSON.stringify({
        "access_token": window.EASYASSIST_COBROWSE_META.access_token
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/available-agent-list/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            try {
                if(callback) {
                    if(response.agent_available == true) {
                        callback();
                    }
                    return;
                }
            } catch(err) {
                console.log("easyassist_check_agent_available_status: ", err);
            }

            if (EASYASSIST_COBROWSE_META.show_only_if_agent_available == true) {
                if (response.status == 200 && response.agent_available == true) {
                    EASYASSIST_COBROWSE_META.agents_available = true;
                    document.getElementById("easyassist-side-nav-options-co-browsing").style.display = "inline-block";
                } else {
                    EASYASSIST_COBROWSE_META.agents_available = false;
                    easyassist_hide_floating_sidenav_button();
                }
            } else if (EASYASSIST_COBROWSE_META.disable_connect_button_if_agent_unavailable == true) {
                document.getElementById("easyassist-side-nav-options-co-browsing").style.display = "inline-block";
                if (response.status == 200 && response.agent_available == false) {
                    EASYASSIST_COBROWSE_META.agents_available = false;
                    document.getElementById("easyassist-side-nav-options-co-browsing").setAttribute("title", EASYASSIST_COBROWSE_META.message_if_agent_unavailable);
                    document.getElementById("easyassist-side-nav-options-co-browsing").setAttribute("onclick", "easyassist_show_toast('" + EASYASSIST_COBROWSE_META.message_if_agent_unavailable + "')");
                } else {
                    EASYASSIST_COBROWSE_META.agents_available = true;
                    document.getElementById("easyassist-side-nav-options-co-browsing").removeAttribute("title");
                    if (EASYASSIST_COBROWSE_META.choose_product_category == true) {
                        document.getElementById("easyassist-side-nav-options-co-browsing").setAttribute("onclick", "easyassist_show_product_category_modal(); easyassist_source_of_lead()");
                    } else {
                        document.getElementById("easyassist-side-nav-options-co-browsing").setAttribute("onclick", "easyassist_show_browsing_modal(); easyassist_source_of_lead()");
                    }
                }
            } else {
                easyassist_hide_floating_sidenav_button();
            }
        } else if (this.readyState == 4 && this.status == 500) {
            easyassist_hide_floating_sidenav_button();
        }
    }
    xhttp.send(params);
}

function easyassist_source_of_lead() {
    if(EASYASSIST_COBROWSE_META.show_floating_easyassist_button) {
        is_request_from_button = true;
        is_request_from_greeting_bubble = false;
        is_request_from_exit_intent = false;
        is_request_from_inactivity_popup = false;
    } else {
        is_request_from_button = false;
        is_request_from_greeting_bubble = false;
        is_request_from_exit_intent = false;
        is_request_from_inactivity_popup = false;
    }
}

function easyassist_set_messages_to_customer_cookie(value) {
    var easyassist_messages_sent_to_customer = get_easyassist_cookie("easyassist_messages_sent_to_customer")
    if (!easyassist_messages_sent_to_customer) {
        easyassist_messages_sent_to_customer = value
    } else {
        easyassist_messages_sent_to_customer = easyassist_messages_sent_to_customer + "," + value
    }
    set_easyassist_cookie("easyassist_messages_sent_to_customer", easyassist_messages_sent_to_customer)
}

function easyassist_get_messages_to_customer_cookie(value) {
    var easyassist_messages_sent_to_customer = get_easyassist_cookie("easyassist_messages_sent_to_customer");
    if (!easyassist_messages_sent_to_customer) {
        return -1;
    }
    return easyassist_messages_sent_to_customer.indexOf(value)
}

function increment_inactivity_auto_popup_number() {
    let inactivity_auto_popup_number = parseInt(get_easyassist_cookie("inactivity_auto_popup_number"));
    inactivity_auto_popup_number = inactivity_auto_popup_number + 1;
    set_easyassist_cookie("inactivity_auto_popup_number", inactivity_auto_popup_number.toString());
}

function set_inactivity_auto_popup_number_cookie() {
    let inactivity_auto_popup_number = get_easyassist_cookie("inactivity_auto_popup_number");
    if (inactivity_auto_popup_number == undefined || inactivity_auto_popup_number == null) {
        set_easyassist_cookie("inactivity_auto_popup_number", "0");
    }
}

function easyassist_start_element_stuck_timer() {
    if (EASYASSIST_COBROWSE_META.agents_available == false) {
        return;
    }
    global_element_stuck_timer = setTimeout(function(e) {
        if (get_easyassist_cookie("easyassist_session_id") != undefined) {
            return;
        }
       
        if (parseInt(get_easyassist_cookie("inactivity_auto_popup_number")) >= window.EASYASSIST_COBROWSE_META.inactivity_auto_popup_number) {
            easyassist_remove_formassist_stuck_timer_handler();
        }

        var easyassist_cobrowsing_modal = document.getElementById("easyassist-co-browsing-modal-id");
        if (easyassist_cobrowsing_modal && easyassist_cobrowsing_modal.style.display == "none") {
            if(EASYASSIST_COBROWSE_META.field_recursive_stuck_event_check == false ) {
                increment_inactivity_auto_popup_number();
                is_request_from_inactivity_popup = true;
                is_request_from_greeting_bubble = false;
                is_request_from_exit_intent = false;
                is_request_from_button = false;
                easyassist_show_cobrowsing_modal();

            } else {
                is_request_from_button = false;
                is_request_from_inactivity_popup = true;
                is_request_from_greeting_bubble = false;
                is_request_from_exit_intent = false;
                easyassist_show_cobrowsing_modal();
            }
        }
    }, EASYASSIST_COBROWSE_META.field_stuck_timer * 1000);
}

function easyassist_reset_element_stuck_timer() {
    set_inactivity_auto_popup_number_cookie();
    easyassist_stop_element_stuck_timer();
    if (parseInt(get_easyassist_cookie("inactivity_auto_popup_number")) < window.EASYASSIST_COBROWSE_META.inactivity_auto_popup_number) {
        easyassist_start_element_stuck_timer();
    }
}

function easyassist_stop_element_stuck_timer() {
    if (global_element_stuck_timer != null) {
        clearTimeout(global_element_stuck_timer);
    }
}

function easyassist_add_formassist_stuck_timer_handler() {

    try{
        if (EASYASSIST_COBROWSE_META.field_stuck_event_handler == false) {
            return;
        }

        if (EASYASSIST_COBROWSE_META.enable_url_based_inactivity_popup) {
            // ignoring the get request params in the url
            let customer_url = window.location.href.split("?")[0]
            let index = JSON.parse(EASYASSIST_COBROWSE_META.inactivity_popup_urls).indexOf(customer_url)
            if (index == -1) {
                return;
            }
        }

        window.addEventListener("mousemove", easyassist_reset_element_stuck_timer, true);

        let form_input_elements = document.getElementsByTagName("input");
        for (let index = 0; index < form_input_elements.length; index++) {
            if (form_input_elements[index].getAttribute("class") == "easyassist-input-field") {
                continue;
            }
            form_input_elements[index].addEventListener("focusin", easyassist_reset_element_stuck_timer, true);
            form_input_elements[index].addEventListener("keypress", easyassist_reset_element_stuck_timer, true);
        }

        let form_textarea_elements = document.getElementsByTagName("textarea");
        for (let index = 0; index < form_textarea_elements.length; index++) {
            form_textarea_elements[index].addEventListener("focusin", easyassist_reset_element_stuck_timer, true);
            form_textarea_elements[index].addEventListener("keypress", easyassist_reset_element_stuck_timer, true);
        }

        let form_select_elements = document.getElementsByTagName("select");
        for (let index = 0; index < form_select_elements.length; index++) {
            form_select_elements[index].addEventListener("mousedown", easyassist_reset_element_stuck_timer, true);
            form_select_elements[index].addEventListener("change", easyassist_reset_element_stuck_timer, true);
        }
    }catch(err){}
}

function easyassist_remove_formassist_stuck_timer_handler() {

    window.removeEventListener("mousemove", easyassist_reset_element_stuck_timer, true);

    let form_input_elements = document.getElementsByTagName("input");
    for (let index = 0; index < form_input_elements.length; index++) {
        form_input_elements[index].removeEventListener("focusin", easyassist_reset_element_stuck_timer, true);
        form_input_elements[index].removeEventListener("keypress", easyassist_reset_element_stuck_timer, true);
    }
    let form_textarea_elements = document.getElementsByTagName("textarea");
    for (let index = 0; index < form_textarea_elements.length; index++) {
        form_textarea_elements[index].removeEventListener("focusin", easyassist_reset_element_stuck_timer, true);
        form_textarea_elements[index].removeEventListener("keypress", easyassist_reset_element_stuck_timer, true);
    }
    let form_select_elements = document.getElementsByTagName("select");
    for (let index = 0; index < form_select_elements.length; index++) {
        form_select_elements[index].removeEventListener("mousedown", easyassist_reset_element_stuck_timer, true);
        form_select_elements[index].removeEventListener("change", easyassist_reset_element_stuck_timer, true);
    }
}

setTimeout(function(e) {
    try {
        easyassist_add_formassist_stuck_timer_handler();
        easyassist_show_floating_sidenav_button();
    } catch(err) {
        console.log(err);
    }
}, 2000);


function easyassist_confirm_payment_init() {

    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined || EASYASSIST_COBROWSE_META.allow_cobrowsing == false) {
        return;
    }

    var screenshot = easyassist_screenshot_page();

    let json_string = JSON.stringify({
        "html": screenshot,
        "id": EASYASSIST_SESSION_ID,
        "active_url": window.location.href,
        "init_transaction": true
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/sync/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
        }
    }
    xhttp.send(params);
}

/******************* LEAD CONVERTED LOGIC ************************/

function easyassist_check_is_lead_converted() {

    var COBROWSE_SESSION_ID = get_easyassist_cookie("easyassist_session_id");
    if(COBROWSE_SESSION_ID == undefined || COBROWSE_SESSION_ID == null){
        return;
    }

    var is_lead_converted = get_easyassist_cookie("is_lead_converted");
    if (is_lead_converted == COBROWSE_SESSION_ID) {
        easyassist_notify_agent_lead_is_converted();    
        return;
    }

    var active_url = window.location.href.replace(window.location.protocol + "//", "");
    
    if(check_proxy_cobrowsing()) {
        let domain = get_proxy_url_domain();
        if(domain) {
            active_url = domain;
        }
    }

    active_url = active_url.toLowerCase();
    var urls_list_lead_converted = window.EASYASSIST_COBROWSE_META.urls_list_lead_converted;

    for (let index = 0; index < urls_list_lead_converted.length; index++) {
        var target_url = urls_list_lead_converted[index];
        target_url = target_url.replace(/\s/g,'');
        target_url = target_url.toLowerCase();
        if (target_url != "" && active_url.indexOf(target_url) == 0) {
            easyassist_mark_lead_as_converted();
        }
    }

    easyassist_notify_agent_lead_is_converted();
}

function easyassist_mark_lead_as_converted() {

    if (get_easyassist_cookie("easyassist_session_id") == undefined) {
        return;
    }

    set_easyassist_cookie("is_lead_converted", get_easyassist_cookie("easyassist_session_id"));
    
    let json_string = JSON.stringify({
        "session_id": get_easyassist_cookie("easyassist_session_id"),
        "active_url": window.location.href
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/mark-lead-as-converted/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
        }
    }
    xhttp.send(params);
}

setTimeout(function() {
    easyassist_check_is_lead_converted();
}, 3000);

/******************* LEAD CONVERTED LOGIC - END ************************/

function easyassist_start_internet_connectivity_check_timer() {
    internet_connectivity_timer = setInterval(function(e) {
        if(get_easyassist_cookie("easyassist_session_id")) {
            if(get_easyassist_cookie("easyassist_agent_disconnected_modal_shown") == undefined || get_easyassist_cookie("easyassist_agent_disconnected_modal_shown") == "false"){
                if(document.getElementById("easyassist-co-browsing-feedback-modal").style.display != "flex"){
                    easyassist_show_agent_disconnected_modal();
                    set_easyassist_cookie("easyassist_agent_disconnected_modal_shown", "true")
                }
            }
        }
        // easyassist_show_toast("Looks like we are not receiving any updates from the agent side. Kindly check your internet connectivity or check whether the agent is still connected or not.");
        easyassist_reset_internet_connectivity_check_timer();
    }, INTERNET_CON_TIMER);
}

function easyassist_stop_internet_connectivity_check_timer() {
    try{
        if (internet_connectivity_timer != null && internet_connectivity_timer != undefined) {
            clearInterval(internet_connectivity_timer);
        }
    }catch(err){}
}

function easyassist_reset_internet_connectivity_check_timer() {
    easyassist_stop_internet_connectivity_check_timer();
    easyassist_start_internet_connectivity_check_timer();
}

/****************************** COBROWSING UTILS SOCKET MESSAGE *******************/

function easyassist_client_heartbeat() {

    let json_string = JSON.stringify({
        "type": "heartbeat",
        "active_url": window.location.href
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
}

function easyassist_notify_agent_lead_is_converted() {

    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    var is_converted = true;

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        is_converted = false;
    }

    var is_lead_converted = get_easyassist_cookie("is_lead_converted");

    if (is_lead_converted != easyassist_session_id) {
        is_converted = false;
    }

    let json_string = JSON.stringify({
        "type": "lead_status",
        "is_converted": is_converted
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
}

/************************ END UTILS SOCKET MESSAGE ****************************/

/******************************** EDIT ACCESS *********************************/

function easyassist_update_agent_request_edit_access(action) {
    let allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;

    if (allow_cobrowsing == false) {
        return;
    }
    if (action == "true") {
        set_easyassist_cookie("easyassist_edit_access", "true");
        // document.getElementById("revoke-edit-access-button").style.display = "inherit";
    } else {
        set_easyassist_cookie("easyassist_edit_access", "false");
        set_easyassist_cookie("easyassist_edit_access_granted", "false");
        // document.getElementById("revoke-edit-access-button").style.display = "none";
    }

    easyassist_hide_request_edit_access_form();
    let json_string;
    if (agent_revoke_edit_access) {
        json_string = JSON.stringify({
            "type": "request-edit-access",
            "is_allowed": action,
            "agent_revoke_edit_access": agent_revoke_edit_access
        });
    } else {
        json_string = JSON.stringify({
            "type": "request-edit-access",
            "is_allowed": action
        });
    }
    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
    agent_revoke_edit_access = false;
}

function easyassist_revoke_edit_access(data_packet) {
    try{
        if (agent_revoke_edit_access) {
            easyassist_show_toast("Edit Access has been revoked by the agent");
        } else {
            easyassist_show_toast("Edit Access has been revoked from agent");
        }
        easyassist_update_agent_request_edit_access("none");
    } catch(err){
        console.log("easyassist_revoke_edit_access: ", err);
    }
    
}

/****************************** END EDIT ACCESS *******************************/

/*************************** SCREENSHOT + PAGESHOT ***************************/

function easyassist_capture_client_pageshot() {

    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    var screenshot = easyassist_screenshot_page();

    let json_string = JSON.stringify({
        "id": easyassist_session_id,
        "content": screenshot,
        "type_screenshot": "pageshot"
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/capture-client-screen/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            let json_string = JSON.stringify({
                "type": "pageshot",
                "active_url": window.location.href,
                "result": response.status
            });

            encrypted_data = easyassist_custom_encrypt(json_string);

            encrypted_data = {
                "Request": encrypted_data
            };

            easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");

        }
    }
    xhttp.send(params);
}

function easyassist_capture_client_screenshot(agent_name) {

    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    document.querySelector("#easyassist-ripple_effect").style.border = "none";

    var body = document.body;
    let doc_html = document.documentElement;
    var new_body_height = Math.max(body.scrollHeight, body.offsetHeight,
        doc_html.clientHeight, doc_html.scrollHeight, doc_html.offsetHeight);
    
    if (window.EASYASSIST_COBROWSE_META.enable_proxy_cobrowsing && document.getElementById("proxy-iframe")) {
        body = document.getElementById("proxy-iframe").contentWindow.document.body;
        doc_html = document.getElementById("proxy-iframe").contentDocument.documentElement;
    }

    html2canvas(doc_html, {
        allowTaint: true,
        useCORS: true,
        scale: 2,
        x: window.scrollX,
        y: Math.abs(body.getBoundingClientRect().top),
        width: window.innerWidth,
        height: window.innerHeight,
        logging: false,
        onclone: function(clone_document_node) {
            clone_document_node.body.style.height = String(new_body_height) + "px";
            EasyAssistSyncHTML.easyassist_set_input_element_value(clone_document_node, true);  
        },
        ignoreElements: function(element) {
            return easyassist_check_dom_node(element);
        },
    }).then(function(canvas) {
        // Get base64URL
        let img_data = canvas.toDataURL('image/png');
        // var screenshot = easyassist_screenshot_page();
        let json_string = JSON.stringify({
            "id": easyassist_session_id,
            "content": img_data,
            "type_screenshot": "screenshot"
        });

        let encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        var params = JSON.stringify(encrypted_data);
        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/capture-client-screen/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
        xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                let response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);

                json_string = JSON.stringify({
                    "type": "screenshot",
                    "active_url": window.location.href,
                    "result": response.status
                });

                encrypted_data = easyassist_custom_encrypt(json_string);

                encrypted_data = {
                    "Request": encrypted_data
                };

                easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");

                if (response.status == 200) {
                    if (agent_name && agent_name.length) {
                        easyassist_show_toast("Agent " + agent_name + " took a screenshot")
                    } else {
                        easyassist_show_toast("Agent " + "took a screenshot")
                    }
                }

            } else if (this.readyState == 4) {

                json_string = JSON.stringify({
                    "type": "screenshot",
                    "active_url": window.location.href,
                    "result": 4
                });

                encrypted_data = easyassist_custom_encrypt(json_string);

                encrypted_data = {
                    "Request": encrypted_data
                };

                easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");

            }
            document.querySelector("#easyassist-ripple_effect").style.border = "1px solid red";
        }
        xhttp.send(params);
    });
}

/************************* END SCREENSHOT + PAGESHOT *************************/

/*********************************** CHAT *************************************/

function easyassist_load_chat_history() {
    easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    let json_string = JSON.stringify({
        "session_id": easyassist_session_id
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/get-cobrowsing-chat-history/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            window.CLIENT_NAME = response.client_name;
            easyassist_send_client_name(response.client_name);
            if (response.status == 200 && response.chat_history.length > 0) {
                let chat_history = response.chat_history;
                let allincall_chat_window = document.getElementById("easyassist-livechat-iframe").contentWindow;
                for (let index = 0; index < chat_history.length; index++) {
                    let sender = chat_history[index]["sender"];
                    let sender_name = chat_history[index]["sender_name"]
                    let message = chat_history[index]["message"];
                    message = easyassist_show_hyperlink_inside_text(message);
                    let datetime = chat_history[index]["datetime"];
                    var time = datetime.split(" ")[3] + " " + datetime.split(" ")[4];
                    let attachment = chat_history[index]["attachment"];
                    let attachment_file_name = chat_history[index]["attachment_file_name"];
                    let chat_type = chat_history[index]["chat_type"]
                    let profile_src = chat_history[index]['agent_profile_pic_source'];
                    
                    if (sender == "client") {
                        allincall_chat_window.postMessage(JSON.stringify({
                            "client_name": response.client_name,
                            "message": message,
                            "attachment": attachment,
                            "attachment_file_name": attachment_file_name,
                            "show_client_message": true,
                            "time": time,
                            "chat_type": chat_type,
                            "sender": sender,
                        }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);
                    } else {
                        allincall_chat_window.postMessage(JSON.stringify({
                            "agent_name": sender_name,
                            "message": message,
                            "attachment": attachment,
                            "attachment_file_name": attachment_file_name,
                            "show_agent_message": true,
                            "time": time,
                            "chat_type": chat_type,
                            "sender": sender,
                            "agent_profile_pic_source": profile_src,
                        }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);
                    }
                }
            }
        }
    }
    xhttp.send(params);
}

function easyassist_send_attachment_to_agent_for_validation(event) {

    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    let allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    if (allow_cobrowsing == false) {
        return;
    }

    function get_easyassist_file_base64(file) {
        var reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = function() {

            let base64_str = reader.result.split(",")[1];

            let json_string = JSON.stringify({
                "filename": file.name,
                "base64_file": base64_str,
                "session_id": easyassist_session_id,
            });

            let encrypted_data = easyassist_custom_encrypt(json_string);

            encrypted_data = {
                "Request": encrypted_data
            };

            var params = JSON.stringify(encrypted_data);

            var xhttp = new XMLHttpRequest();
            xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/agent/save-document/", true);
            xhttp.setRequestHeader('Content-Type', 'application/json');
            xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
            xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
            xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    let response = JSON.parse(this.responseText);
                    response = easyassist_custom_decrypt(response.Response);
                    response = JSON.parse(response);
                    if (response["status"] == 200) {
                        easyassist_send_livechat_message_to_agent("uploaded attachment", response["file_path"], file.name);
                    }
                }
            }
            xhttp.send(params);
        };

        reader.onerror = function(error) {
            console.log('Error: ', error);
        };
    }

    var selected_file = event.target.files[0];
    get_easyassist_file_base64(selected_file);
}

function easyassist_send_livechat_message_to_agent(message, attachment, attachment_file_name) {

    try {
        if(!EASYASSIST_COBROWSE_META.enable_chat_functionality) {
            return;
        }

        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

        if (easyassist_session_id == null || easyassist_session_id == undefined) {
            return;
        }

        let json_string = JSON.stringify({
            "type": "chat",
            "message": message,
            "attachment": attachment,
            "attachment_file_name": attachment_file_name,

        });

        let encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
    } catch(err) {
        console.log("easyassist_send_livechat_message_to_agent: ", err);
    }
}

function easyassist_send_livechat_typing_indication() {
    var name = window.CLIENT_NAME;
    let json_string = JSON.stringify({
        "role": "client",
        "name": name,
        "type": "livechat-typing"
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
}

function easyassist_sync_client_chat(data_packet) {
    try {
        let chat_message = JSON.stringify(data_packet);
        let allincall_chat_window = document.getElementById("easyassist-livechat-iframe").contentWindow;
        allincall_chat_window.postMessage(JSON.stringify({
            "agent_name": data_packet.agent_name,
            "message": data_packet.message,
            "attachment": data_packet.attachment,
            "attachment_file_name": data_packet.attachment_file_name,
            "show_client_message": true,
            "chat_type": data_packet.chat_type,
            "sender": data_packet.sender,
        }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);
    } catch(err){
        console.log("easyassist_sync_client_chat: ", err);
    }
}

function easyassist_send_chat_notification(notification_title,notification_body){
    if(Notification.permission === "granted"){
        easyassist_chat_notification_sound();
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
                easyassist_chat_notification_sound();
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

function easyassist_get_notification_body(message, attachment_file_name){

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

function easyassist_chat_notification(message,attachment_file_name,agent_name){

    let is_current_tab_focussed = easyassist_check_current_tab_active();

    //Check for is current tab is not in focus and Notificaiton are allowed on the browser
    if(!is_current_tab_focussed && typeof Notification !== "undefined"){

        let notification_title = `${agent_name} messaged you!`;
        let notification_body = easyassist_get_notification_body(message, attachment_file_name);       
    
        easyassist_send_chat_notification(notification_title,notification_body);
    }
}

function easyassist_sync_agent_chat(data_packet) {
    try {
        if(EASYASSIST_COBROWSE_META.is_mobile && data_packet.chat_type != "chat_bubble") {
            if (data_packet.chat_type == "agent_connect_message") {
                easyassist_play_greeting_bubble_popup();
            }
            document.getElementById("easyassist-livechat-iframe").style.display = "block";
            set_easyassist_current_session_local_storage_obj("new_message_seen","true");
        }
        if(EASYASSIST_COBROWSE_META.enable_chat_bubble && EASYASSIST_COBROWSE_META.is_mobile == false && data_packet.chat_type != "chat_bubble") {
            set_easyassist_current_session_local_storage_obj("new_message_seen","false");
            var chat_box = document.getElementById("chat-minimize-icon-wrapper");
            if ( data_packet.chat_type != "agent_connect_message") {
                try { 
                    easyassist_append_chat_bubble_message(data_packet.agent_name, data_packet.message, data_packet.attachment, data_packet.attachment_file_name);
                } catch (err) {
                    console.log(err)
                }
            } else {
                livechat_iframe = document.getElementById("easyassist-livechat-iframe");
                if(livechat_iframe.classList.contains("allincall-scale-out-br")) {
                    livechat_iframe.classList.remove("allincall-scale-out-br");
                }

                if (livechat_iframe.classList.contains("allincall-scale-out-br-right-side")) {
                    livechat_iframe.classList.remove("allincall-scale-out-br-right-side");
                }
                
                livechat_iframe.style.display = "block";
                let is_current_tab_focussed = easyassist_check_current_tab_active();
                if(is_current_tab_focussed ){
                    easyassist_play_greeting_bubble_popup();
                }
                livechat_iframe.classList.add("animate__animated");
                livechat_iframe.classList.add("animate__slideInUp");
                set_easyassist_current_session_local_storage_obj("new_message_seen","true");
                if(chat_box) {
                    chat_box.style.display = "none";
                }
            }
        }
                
        if (EASYASSIST_COBROWSE_META.enable_chat_bubble == false && data_packet.chat_type != "chat_bubble" && document.getElementById("easyassist-livechat-iframe").style.display == "none" || data_packet.chat_type == "agent_connect_message") {
            document.getElementById("easyassist-livechat-iframe").style.display = "block";
        }

        easyassist_chat_notification(data_packet.message,data_packet.attachment_file_name,data_packet.agent_name);

        let chat_message = JSON.stringify(data_packet);
        let allincall_chat_window = document.getElementById("easyassist-livechat-iframe").contentWindow;
        allincall_chat_window.postMessage(JSON.stringify({
            "agent_name": data_packet.agent_name,
            "agent_profile_pic_source": data_packet.agent_profile_pic_source,
            "message": data_packet.message,
            "attachment": data_packet.attachment,
            "attachment_file_name": data_packet.attachment_file_name,
            "show_agent_message": true,
            "chat_type": data_packet.chat_type,
            "sender": data_packet.sender,
        }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);
    } catch(err){
        console.log("easyassist_sync_agent_chat: ", err);
    }
}

function easyassist_sync_typing_loader(data_packet) {
    try {
        let allincall_chat_window = document.getElementById("easyassist-livechat-iframe").contentWindow;
        allincall_chat_window.postMessage(JSON.stringify({
            "id": "livechat-typing",
            "role": data_packet.role,
            "name": data_packet.name
        }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);
    } catch(err){
        console.log("easyassist_sync_typing_loader: ", err);
    }
}

function easyassist_send_client_name(client_name) {
    try {
        let allincall_chat_window = document.getElementById("easyassist-livechat-iframe").contentWindow;
        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
        allincall_chat_window.postMessage(JSON.stringify({
            "session_id": easyassist_session_id,
            "id": "client_name",
            "name": client_name
        }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);
    } catch(err) {
        console.log("easyassist_send_client_name: ", err);
    }
}

function easyassist_show_hyperlink_inside_text(text) {
    try {
        var urlRegex = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
        return text.replace(urlRegex, function(url) {
            return '<a href="' + url + '" target="_blank">' + url + '</a>';
        });
    } catch(err) {
        console.log("easyassist_show_hyperlink_inside_text: ", err);
    }
}

/********************************** END CHAT ***************************************/

/*********************************** SYNC HTML DATA ***************************/

function easyassist_sync_client_screen_dimension() {
    try {
        let json_string = JSON.stringify({
            "type": "client_screen_resize",
            "scrollX": window.scrollX,
            "scrollY": window.scrollY,
            "window_width": window.innerWidth,
            "window_height": window.innerHeight,
        });

        let encrypted_data = easyassist_custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };

        easyassist_send_message_over_socket(encrypted_data, "client");
    } catch(err) {
        console.log(err);
    }
}

function easyassist_get_input_element_value(element) {
    var element_value = [null, null];
    try {
        var tag_name = element.tagName;

        if(tag_name != "INPUT" && tag_name != "SELECT" && tag_name != "TEXTAREA") {
            return element_value;
        }

        var current_element_value = null;

        if(element.tagName == "INPUT") {
            var element_type = element.getAttribute("type");
            if(element_type == "button" || element_type == "submit") {
                return element_value;
            }

            if(element_type == "checkbox" || element_type == "radio") {
                current_element_value = element.checked;
            } else {
                current_element_value = element.value;
            }
        } else if(element.tagName == "SELECT") {
            current_element_value = element.value;
        } else {
            current_element_value = element.value;
        }

        var is_obfuscated_element = easyassist_obfuscated_element_check(element);
        var is_numeric = false;
        if (is_obfuscated_element[0] == false && isNaN(Number(current_element_value.toString())) == false) {
            is_numeric = true;
        }

        if (is_obfuscated_element[0]) {
            current_element_value = easyassist_obfuscate(current_element_value.toString(), is_obfuscated_element[1].toString());
        }
        if(is_numeric) {
            current_element_value = easyassist_obfuscate(current_element_value.toString());
        }

        element_value = [is_obfuscated_element[0], current_element_value];
    } catch(err) {
        console.log(err);
    }
    return element_value;
}

function easyassist_send_html_request_received_message_over_socket() {
    try {
        let json_string = JSON.stringify({
            "type": "html_request_received",
        });

        let encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        easyassist_send_message_over_socket(encrypted_data, "client");
    } catch(err) {
        console.log(err);
    }
}

function easyassist_sync_mouse_position(event) {

    try {

        if(easyassist_check_weak_connection_enabled()) {
            return;
        }

        var current_mouse_x = event.clientX;
        var current_mouse_y = event.clientY;
        var current_time = Date.now();
        if(easyassist_client_mouse_last_cordinates != null) {
            var previous_mouse_x = easyassist_client_mouse_last_cordinates.client_x;
            var previous_mouse_y = easyassist_client_mouse_last_cordinates.client_y;

            var distance = Math.abs(previous_mouse_x - current_mouse_x) + Math.abs(previous_mouse_y - current_mouse_y);

            var mouse_move_diff = current_time - easyassist_last_mouse_move_time;

            if(easyassist_last_mouse_move_time != null && mouse_move_diff <= 200) {

                easyassist_sync_last_mouse_move_event = event;
                current_time = Date.now();
                if(easyassist_sync_client_mouse_timeout != null && current_time - easyassist_sync_client_mouse_time <= 300) {
                    clearTimeout(easyassist_sync_client_mouse_timeout);
                }

                easyassist_sync_client_mouse_timeout = setTimeout(function() {
                    easyassist_sync_client_mouse_last_coordinate();
                }, 300);

                easyassist_sync_client_mouse_time = Date.now();

                if(distance <= 100) {
                    return;
                }
            }
        }

        easyassist_last_mouse_move_time = current_time;

        easyassist_client_mouse_last_cordinates = {
            client_x: current_mouse_x,
            client_y: current_mouse_y,
        };

        let json_string = JSON.stringify({
            "type": "mouse",
            "position": {
                "clientX": event.clientX,
                "clientY": event.clientY,
                "agent_window_width": window.outerWidth,
                "agent_window_height": window.outerHeight,
                "screen_width": screen.width,
                "screen_height": screen.height,
                "agent_window_x_offset": window.pageXOffset,
                "agent_window_y_offset": window.pageYOffset,
                "pageX": event.pageX,
                "pageY": event.pageY
            }
        });

        let encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
    } catch(err) {
        console.log("easyassist_sync_mouse_position: ", err);
    }
}

function easyassist_sync_client_mouse_last_coordinate() {
    try {

        let json_string = JSON.stringify({
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

        let encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
        easyassist_sync_client_mouse_timeout = null;
    } catch(err) {
        console.log("easyassist_sync_client_mouse_last_coordinate: ", err);
    }
}

function easyassist_sync_client_scroll_position(agent_packet) {

    function check_native_function(func) {
        try {
            if(func.toString().indexOf("[native code]") > -1) {
                return true;
            }
            return false;
        } catch(err) {
            console.log(err);
        }

        return false;
    }

    try {

        var iframe_id = agent_packet.iframe_id;
        var scrollX = agent_packet.data_scroll_x;
        var scrollY = agent_packet.data_scroll_y;

        var content_window = window;
        if(iframe_id != null) {
            var iframe = document.querySelector("[easyassist-iframe-id='" + iframe_id + "'");
            if(!iframe) {
                return;
            }

            content_window = iframe.contentWindow;
        }

        if(check_native_function(window.scrollTo)) {
            content_window.scrollTo(scrollX, scrollY);
        } else {
            content_window.scroll(scrollX, scrollY);
        }

    } catch(err) {
        console.log("easyassist_sync_client_scroll_position: ", err);
    }

}

function easyassist_sync_agent_highlight(data_packet) {

    try {
        
        let edit_access = get_easyassist_cookie("easyassist_edit_access");
        edit_access = edit_access ? edit_access : "false";
        let clientX = data_packet.position.clientX;
        let clientY = data_packet.position.clientY;

        let pageX = data_packet.position.pageX;
        let pageY = data_packet.position.pageY;

        let agent_window_x_offset = data_packet.position.agent_window_x_offset;
        let agent_window_y_offset = data_packet.position.agent_window_y_offset;

        easyassist_sync_client_scroll_position({
            "data_scroll_x": agent_window_x_offset,
            "data_scroll_y": agent_window_y_offset,
        });

        let agent_window_width = data_packet.position.agent_window_width;
        let agent_window_height = data_packet.position.agent_window_height;

        let screen_width = data_packet.position.screen_width;
        let screen_height = data_packet.position.screen_height;

        clientX = (clientX * window.innerWidth) / (agent_window_width);
        clientY = (clientY * window.innerHeight) / (agent_window_height);

        pageX = (pageX * window.outerWidth) / (agent_window_width);
        pageY = (pageY * window.outerHeight) / (agent_window_height);

        clientX = clientX - 18;
        clientY = clientY - 18;

        if (edit_access == "false") {
            easyassist_show_ripple_effect(clientX, clientY);
        }
    } catch (err) {
        console.log("easyassist_sync_agent_highlight: ", err);
    }
}

function easyassist_sync_agent_mouse(data_packet) {
    try {

        document.getElementById("agent-mouse-pointer").style.display = "inline-block";
        agent_mouse_top = data_packet.position.clientY;
        agent_mouse_left = data_packet.position.clientX;
        document.getElementById("agent-mouse-pointer").style.top = data_packet.position.clientY + "px";
        document.getElementById("agent-mouse-pointer").style.left = data_packet.position.clientX + "px";
    } catch(err) {
        console.log("easyassist_sync_agent_mouse: ", err);
    }
}

function easyassist_sync_agent_form_activity(data_packet, packet_type, callback) {

    try {
        var iframe_id = data_packet.iframe_id;
        if(iframe_id == null) {
            callback(data_packet);
            return;
        }

        var iframe = document.querySelector("[easyassist-iframe-id='" + iframe_id + "']");
        if(!iframe) {
            return;
        }

        var json_data = {
            "type": packet_type,
            "data": data_packet,
        };
        iframe.contentWindow.postMessage(json_data, "*");

    } catch(err) {
        console.log("easyassist_sync_agent_div_scroll_handler: ", err);
    }
}


/******************************* MEETING + VOIP MEETING *******************************************/

if(EASYASSIST_COBROWSE_META.allow_video_meeting_only == true){
    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if(easyassist_session_id != "" || easyassist_session_id != null || easyassist_session_id != undefined){
        is_cobrowsing_meeting = setInterval(function(){
            easyassist_check_cobrowsing_meeting_status()
        },60000);
    }
}

function easyassist_check_cobrowsing_meeting_status() {
    if(window.EASYASSIST_COBROWSE_META.allow_video_meeting_only == false){
        return;
    }
    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if(easyassist_session_id == "" || easyassist_session_id == null || easyassist_session_id == undefined){
        return;
    }

    let json_string = JSON.stringify({
        "session_id": easyassist_session_id,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/check-cobrowsing-meeting-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (window.EASYASSIST_COBROWSE_META.allow_video_meeting_only == true) {
                if (response.status == 200) {
                    delete_easyassist_cookie("easyassist_session_id")
                }
            }
        }
    }
    xhttp.send(params);
}

function easyassist_update_agent_meeting_request(status) {

    // call_initiate_by_agent = "false";
    set_easyassist_current_session_local_storage_obj("call_initiate_by_agent", "false");

    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    // Show request meeting modal on agent request
    delete_easyassist_cookie("agent_meeting_request_status");

    var request_meeting_error_el = null;
    if (EASYASSIST_COBROWSE_META.allow_video_meeting_only) {
        request_meeting_error_el = document.getElementById("easyassist-request-meeting-error");
    } else {
        if (EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {
            request_meeting_error_el = document.getElementById("easyassist-voip-with-video-meeting-error");
        } else if (EASYASSIST_COBROWSE_META.enable_voip_calling) {
            request_meeting_error_el = document.getElementById("easyassist-voip-meeting-error");
        } else {
            request_meeting_error_el = document.getElementById("easyassist-request-meeting-error");
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
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/update-agent-meeting-request/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            set_easyassist_cookie("is_cobrowse_meeting_on", "false");
            if (response.status == 200) {
                if (EASYASSIST_COBROWSE_META.allow_video_meeting_only == true) {
                    document.getElementById("easyassist-co-browsing-request-meeting-modal").style.display = "none";
                } else {
                    if (EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {
                        document.getElementById("easyassist-voip-video-calling-request-modal").style.display = "none";
                    } else if (EASYASSIST_COBROWSE_META.enable_voip_calling) {
                        document.getElementById("easyassist-voip-calling-request-modal").style.display = "none";
                    } else {
                        document.getElementById("easyassist-co-browsing-request-meeting-modal").style.display = "none";
                    }
                }
                if (response.meeting_allowed == "true") {
                    if (EASYASSIST_COBROWSE_META.enable_voip_with_video_calling || EASYASSIST_COBROWSE_META.enable_voip_calling) {
                        set_easyassist_cookie("cobrowse_meeting_id", easyassist_session_id);
                    }
                    set_easyassist_cookie("easyassist_meeting_allowed", "true");
                } else {
                    set_easyassist_cookie("easyassist_meeting_allowed", "false");
                }
                easyassist_check_for_agent_highlight();
            } else {
                request_meeting_error_el.innerHTML = "Some error occured we can not connect you with our agent.";
            }
        }
    }
    xhttp.send(params);
}

function easyassist_open_meeting_window() {
    set_easyassist_cookie("is_cobrowse_meeting_on", "true");
    var session_id = get_easyassist_cookie("easyassist_session_id")
    set_easyassist_cookie("is_easyassist_meeting_on_client", session_id);
    var url = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/meeting/" + session_id + "?is_meeting_cobrowsing=true"
    window.open(url, "_blank");
}

function easyassist_open_voip_meeting_window() {
    set_easyassist_cookie("is_cobrowse_meeting_on", "true");
    var session_id = get_easyassist_cookie("easyassist_session_id")
    set_easyassist_cookie("is_easyassist_meeting_on_client", session_id);
    var url = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/client-cobrowse-meeting/" + session_id;
    window.open(url, "_blank");
}


function easyassist_start_voip_with_video_calling() {
    var cobrowse_voip_meeting_shown = get_easyassist_cookie("cobrowse_voip_meeting_shown");
    if(cobrowse_voip_meeting_shown == null || cobrowse_voip_meeting_shown == undefined) {
        set_easyassist_cookie("cobrowse_voip_meeting_shown", easyassist_client_page_id);
    }

    cobrowse_voip_meeting_shown = get_easyassist_cookie("cobrowse_voip_meeting_shown");
    if(cobrowse_voip_meeting_shown == easyassist_client_page_id) {
        easyassist_show_cobrowse_meeting_option();
    }
}

function easyassist_show_cobrowse_meeting_option() {
    if (get_easyassist_cookie("easyassist_session_id") == undefined) {
        return;
    }
    set_easyassist_cookie("is_cobrowse_meeting_on", "true");
    var cobrowse_meeting_id = get_easyassist_cookie("cobrowse_meeting_id");
    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    set_easyassist_cookie("is_easyassist_meeting_on_client", easyassist_session_id);
    if (cobrowse_meeting_id == easyassist_session_id) {
        if (document.getElementById("easyassist-cobrowse-voip-container").style.display == 'none') {
            easyassist_send_client_meeting_joined_over_socket();
            document.getElementById("easyassist-voip-loader").style.display = 'flex';
            document.getElementById("easyassist-cobrowse-voip-container").style.display = '';
            var cobrowsing_meeting_iframe = document.getElementById("easyassist-cobrowse-meeting-iframe-container").children[0];
            var meeting_url = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/client-cobrowse-meeting/" + easyassist_session_id;
            cobrowsing_meeting_iframe.src = meeting_url;
            show_customer_side_call_icon(false);
        }
    }
}

function easyassist_show_customer_cobrowse_meeting_option() {
    if (get_easyassist_cookie("easyassist_session_id") == undefined) {
        return;
    }
    set_easyassist_cookie("is_cobrowse_meeting_on", "true");
    var cobrowse_meeting_id = get_easyassist_cookie("cobrowse_meeting_id");
    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if (cobrowse_meeting_id == easyassist_session_id) {
        if (document.getElementById("easyassist-cobrowse-voip-container").style.display == 'none') {
            easyassist_send_client_meeting_joined_over_socket();
            document.getElementById("easyassist-voip-loader").style.display = 'flex';
            document.getElementById("easyassist-cobrowse-voip-container").style.display = '';
            var cobrowsing_meeting_iframe = document.getElementById("easyassist-cobrowse-meeting-iframe-container").children[0];
            var meeting_url = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/client-cobrowse-meeting/" + easyassist_session_id;
            cobrowsing_meeting_iframe.src = meeting_url;
    }
}
}

function easyassist_toggle_meeting_iframe_visibility() {
    var meeting_iframe_container = document.getElementById("easyassist-cobrowse-meeting-iframe-container");
    if (meeting_iframe_container.style.display == 'none') {
        meeting_iframe_container.style.display = 'block';
    } else {
        meeting_iframe_container.style.display = 'none';
    }
}

function easyassist_toggle_client_voice(element, status) {
    try {
        var cobrowse_meeting_iframe = document.getElementById("easyassist-cobrowse-meeting-iframe-container").children[0];
        let cobrowse_meeting_window = cobrowse_meeting_iframe.contentWindow;
        cobrowse_meeting_window.postMessage(JSON.stringify({
            "message": "toggle_voice",
            "status": status,
            "name": window.CLIENT_NAME
        }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);
    } catch (err) {
        console.log(err);
    }
}

function easyassist_toggle_client_video(element, status) {
    try {
        var cobrowse_meeting_iframe = document.getElementById("easyassist-cobrowse-meeting-iframe-container").children[0];
        let cobrowse_meeting_window = cobrowse_meeting_iframe.contentWindow;
        cobrowse_meeting_window.postMessage(JSON.stringify({
            "message": "toggle_video",
            "name": window.CLIENT_NAME,
            "status": status,
        }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);

        var video_element = document.getElementById("easyassist-meeting-video-element");
        if (status) {
            document.getElementById("easyassist-cobrowse-meeting-iframe-container").style.display = 'flex';
            navigator.mediaDevices.getUserMedia({
                    video: true
                })
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
            } catch (err) {}
        }
    } catch (err) {
        console.log(err);
    }
}

function easyassist_end_cobrowse_video_meet(auto_end_meeting = false) {
    try {
        show_customer_side_call_icon(true);
        if(EASYASSIST_COBROWSE_META.enable_voip_calling) {
            return;
        }

        var cobrowse_meeting_id = get_easyassist_cookie("cobrowse_meeting_id");
        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
        if (cobrowse_meeting_id != easyassist_session_id) {
            return;
        }

        var meeting_iframe_container = document.getElementById("easyassist-cobrowse-meeting-iframe-container");
        if(meeting_iframe_container) {
            meeting_iframe_container.style.display = 'none';

            var cobrowse_meeting_iframe = meeting_iframe_container.children[0];
            let cobrowse_meeting_window = cobrowse_meeting_iframe.contentWindow;
            cobrowse_meeting_window.postMessage(JSON.stringify({
                "message": "end_meeting",
                "name": window.CLIENT_NAME
            }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);

            easyassist_send_end_meeting_messsage_over_socket(auto_end_meeting)
        }
    } catch (err) {
        console.log(err)
    }
}

function easyassist_reset_voip_meeting() {
    set_easyassist_cookie("cobrowse_meeting_id", "");
    delete_easyassist_cookie("is_meeting_audio_muted");
    delete_easyassist_cookie("is_agent_voip_meeting_joined");
    delete_easyassist_cookie("cobrowse_voip_meeting_shown");

    document.getElementById("easyassist-cobrowse-meeting-iframe-container").style.display = 'none';
    document.getElementById("easyassist-cobrowse-voip-container").style.display = 'none';
    document.getElementById("easyassist-client-meeting-mic-on-btn").style.display = 'none';
    document.getElementById("easyassist-client-meeting-mic-off-btn").style.display = '';
    if (EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {
        document.getElementById("easyassist-client-meeting-video-on-btn").style.display = '';
        document.getElementById("easyassist-client-meeting-video-off-btn").style.display = 'none';
        try {
            captured_video_stream.getTracks().forEach(function(track) {
                track.stop();
            });
        } catch (err) {}
    }

    setTimeout(function() {
        document.getElementById("easyassist-cobrowse-meeting-iframe-container").children[0].src = "";
    }, 2000);
}

function easyassist_send_end_meeting_messsage_over_socket(auto_end_meeting) {

    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    let json_string = JSON.stringify({
        "type": "end_voip_meeting",
        "auto_end_meeting": auto_end_meeting,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string)
    encrypted_data = {
        "Request": encrypted_data
    };

    easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
}

function easyassist_send_client_meeting_joined_over_socket() {

    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    let json_string = JSON.stringify({
        "type": "voip_meeting_joined",
    });

    let encrypted_data = easyassist_custom_encrypt(json_string)
    encrypted_data = {
        "Request": encrypted_data
    };

    easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
}

function easyassist_send_voip_meeting_ready_over_socket() {

    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    let json_string = JSON.stringify({
        "type": "voip_meeting_ready",
    });

    let encrypted_data = easyassist_custom_encrypt(json_string)
    encrypted_data = {
        "Request": encrypted_data
    };

    easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
}

function easyassist_end_voip_meeting(data_packet){
    try{
        show_customer_side_call_icon(true);
        if (data_packet.auto_end_meeting) {
            easyassist_show_toast("Call ended");
        } else {
            easyassist_show_toast(data_packet.agent_name + " ended the call");
        }
        setTimeout(function() {
            if (EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {
                easyassist_end_cobrowse_video_meet(true);
            }
        }, 1000);
    } catch(err){
        console.log("easyassist_end_voip_meeting: ", err);
    }
}

function easyassist_voip_meeting_ready(data_packet){
    try{
        easyassist_show_toast("Agent " + data_packet.agent_name + " joined the call");
        set_easyassist_cookie("is_agent_voip_meeting_joined", get_easyassist_cookie("easyassist_session_id"));
    } catch(err){
        console.log("easyassist_voip_meeting_ready: ", err);
    }
}

/******************************* Screen sharing cobrowse *******************************************/

function easyassist_go_to_sceensharing_tab(response) {

    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }
    if (response.allow_screen_sharing_cobrowse == true || response.allow_screen_sharing_cobrowse == "true") {

        window.open(EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + '/easy-assist/screensharing-cobrowse/?id=' + easyassist_session_id, '_blank');
    }
}

/******************************* Internet Connectivity Check *******************************************/

function easyassist_sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function easyassist_check_internet_speed(){
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
            easyassist_speed_mbps = (speedKbps / 1024).toFixed(2);
        }
    }

    start_time = (new Date()).getTime();
    var cache_buster = "?nnn=" + start_time;
    download.src = image_addr + cache_buster;
}

async function easyassist_initiate_internet_speed_detection() {

    var total_value = 0;
    for(let i_index = 0; i_index < easyassist_internet_iteration; i_index++) {

        easyassist_check_internet_speed();
        await easyassist_sleep(5000);
        total_value = parseInt(total_value) + parseInt(easyassist_speed_mbps);
        easyassist_speed_mbps = 0;
    }

    var easyassist_avg_speed_mbps = 0;

    if (easyassist_internet_iteration > 0) {

        easyassist_avg_speed_mbps = (total_value / easyassist_internet_iteration).toFixed(2);
    }

    // Adding this console for testing purpose
    console.log("Your average internet speed is " + easyassist_avg_speed_mbps + " Mbps.");
    if (easyassist_avg_speed_mbps < 1) {
        easyassist_show_client_weak_internet_connection();
        easyassist_send_client_weak_connection_message_interval = setInterval(easyassist_send_client_weak_connection_message, 30000);
        easyassist_send_client_weak_connection_message()
    }
}

function easyassist_send_client_weak_connection_message(){
    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    let json_string = JSON.stringify({
        "type": "client_weak_connection",
    });

    let encrypted_data = easyassist_custom_encrypt(json_string)
    encrypted_data = {
        "Request": encrypted_data
    };

    easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
}

easyassist_start_cobrowsing_activity_check();

/***************** START AGENT CONNECT TIMER MODAL *****************/
function easyassist_minimize_connection_with_timer_modal() {
    set_easyassist_current_session_local_storage_obj("easyassist_timer_modal_minimized", "true");
    easyassist_hide_connection_with_timer_modal();
    easyassist_show_minimized_timer_modal();
}

function easyassist_maximize_connection_with_timer_modal() {
    set_easyassist_current_session_local_storage_obj("easyassist_timer_modal_minimized", "false");
    easyassist_hide_minimized_timer_modal();
    easyassist_show_connection_with_timer_modal();
}

function easyassist_close_minimise_connection_modal() {
    set_easyassist_current_session_local_storage_obj("easyassist_timer_modal_minimized", "true");
    easyassist_hide_minimized_timer_modal();
}

function easyassist_close_timer_connection_modal() {
    set_easyassist_current_session_local_storage_obj("easyassist_timer_modal_minimized", "true");
    easyassist_hide_connection_with_timer_modal();
}

function easyassist_start_agent_wait_timer(waiting_time_seconds) {

    function update_agent_wait_timer() {
        try {
            if(waiting_time_seconds <= 0) {
                // restart timer
                set_repeted_text_count_cookie();
                set_easyassist_current_session_local_storage_obj("easyassist_initial_timer_exhausted", "true");

                var modal_header_child = document.getElementById("easyassist-connection-timer-header-div").children[0];
                modal_header_child.innerHTML = "Thank you for your patience, our agent will connect you";
                var modal_body_child = document.getElementById("easyassist-connection-timer-modal-body").children[0];
                modal_body_child.innerHTML = EASYASSIST_COBROWSE_META.no_agent_connects_toast_text;
                var minimized_modal_header_child = document.getElementById("easyassist-minimized-timer-header-div").children[0];
                minimized_modal_header_child.innerHTML = "Thank you for your patience, our agent will connect you in";
                
                let repeated_text_count = parseInt(get_easyassist_cookie("no_of_times_default_text_on_modal"));
                
                if(repeated_text_count > 0) {
                    easyassist_hide_minimized_timer_modal();
                    easyassist_show_connection_with_timer_modal();
                    decrement_repeted_text_count();
                }
                
                if(!easyassist_is_reset_count_exhausted()) {
                    easyassist_increment_timer_modal_reset_count();
                    easyassist_start_agent_wait_timer(EASYASSIST_COBROWSE_META.no_agent_connects_toast_threshold * 60);
                } else {
                    set_easyassist_cookie("is_timer_iterations_elapsed", "true");
                    easyassist_agent_request_actions();
                    easyassist_show_connection_timer_reset_modal();
                }
            }

            if(waiting_time_seconds<=15) {
                document.getElementById("easyassist-waiting-time-value").parentElement.style.color = "#E53E3E";
                document.getElementById("easyassist-minimized-waiting-time-value").parentElement.style.color = "#E53E3E";
            } else {
                document.getElementById("easyassist-waiting-time-value").parentElement.style.color = EASYASSIST_COBROWSE_META.floating_button_bg_color;
                document.getElementById("easyassist-minimized-waiting-time-value").parentElement.style.color = EASYASSIST_COBROWSE_META.floating_button_bg_color;
            }

            document.getElementById("easyassist-waiting-time-value").innerHTML = waiting_time_seconds;
            document.getElementById("easyassist-minimized-waiting-time-value").innerHTML = waiting_time_seconds;
            waiting_time_seconds = waiting_time_seconds - 1;
            set_easyassist_current_session_local_storage_obj("easyassist_timer_value", waiting_time_seconds);
        } catch(err) {
            console.log("easyassist_start_agent_wait_timer: ", err);
        }
    }

    easyassist_clear_agent_wait_timer();

    update_agent_wait_timer();
    agent_wait_timer = setInterval(function() {
        update_agent_wait_timer();
    }, 1000);
}

function easyassist_increment_timer_modal_reset_count() {
    let timer_modal_reset_count = parseInt(get_easyassist_cookie("timer_modal_reset_count"));
    set_easyassist_cookie("timer_modal_reset_count", timer_modal_reset_count + 1);
}

function easyassist_is_reset_count_exhausted() {
    if (EASYASSIST_COBROWSE_META.no_agent_connects_toast_reset_count == 0) {
        return true;
    }
    
    let reset_count = parseInt(get_easyassist_cookie("timer_modal_reset_count"));
    if (reset_count < EASYASSIST_COBROWSE_META.no_agent_connects_toast_reset_count) {
        return false;
    } else {
        return true;
    }    
}

function is_easyassist_connection_timer_closed() {
    let is_timer_iterations_elapsed = get_easyassist_cookie("is_timer_iterations_elapsed");
    if(is_timer_iterations_elapsed == "true") {
        return true;
    }
    return false;
}

function easyassist_clear_agent_wait_timer() {
    if(agent_wait_timer != null) {
        clearInterval(agent_wait_timer);
        agent_wait_timer = null;
    }
}

/***************** END AGENT CONNECT TIMER MODAL *****************/

function easyassist_check_current_tab_active() {
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
        console.log("easyassist_check_current_tab_active: ", err);
    }
}

function easyassist_send_client_page_details() {

    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    var title = window.location.href;
    let favicon = document.querySelectorAll('[rel="icon"]')[0];
    let favicon_url = null
    if (document.querySelector("title") && document.querySelector("title").innerText.trim() != "") {
        title = document.querySelector("title").innerText.trim();
        title = perform_html_encoding(title);
        favicon = document.querySelectorAll('[rel="icon"]')[0];
        if(!favicon){
            favicon = document.querySelectorAll('[rel="shortcut icon"]')[0];
        }
    }

    if (EASYASSIST_COBROWSE_META.enable_proxy_cobrowsing) {
        let first_index = window.location.href.indexOf("cognoai-cobrowse");
        if (first_index > 0) {
            title = document.getElementById('proxy-iframe').contentWindow.document.title;
            if(!title){
                title = window.proxy_active_url;
            }
            favicon = document.getElementById("proxy-iframe").contentWindow.document.querySelectorAll('[rel="icon"]')[0];
            if(!favicon){
                favicon = document.getElementById("proxy-iframe").contentWindow.document.querySelectorAll('[rel="shortcut icon"]')[0];
            }
        }
    }

    if(favicon){
        favicon_url = favicon.href
    }

    var is_tab_focussed = easyassist_check_current_tab_active();

    let json_string = JSON.stringify({
        "type": "client_page_details",
        "client_page_id": easyassist_client_page_id,
        "url": window.location.href,
        "title": title,
        "is_tab_focussed": is_tab_focussed,
        "favicon": favicon_url,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string)
    encrypted_data = {
        "Request": encrypted_data
    };

    easyassist_send_message_over_socket(encrypted_data, "client", true);
}


function easyassist_get_restricted_data_packet(){
    let json_string = JSON.stringify({
        "type": "restricted_url",
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    var message = {
        "Request": encrypted_data
    };

    return message;
}

function easyassist_send_screenshot_405_status() {
    let json_string = JSON.stringify({
        "type": "screenshot",
        "active_url": window.location.href,
        "result": 405
    });
    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
}

function easyassist_page_reload_action() {
    try {
        easyassist_send_tab_close_over_socket();
    } catch(err) {
        console.log("easyassist_page_reload_action: ", err);
    }
}

function open_invite_agent_modal(){
    try {
        if(EASYASSIST_COBROWSE_META.enable_voip_calling){
            document.getElementById("easyassist_agent_connect_modal").style.display = "flex";
        } else {
            document.getElementById("easyassist_agent_connect_video_call_modal").style.display = "flex";
        }    
    } catch (error) {
        
    }
}

function close_modal(){
    try {
        if(EASYASSIST_COBROWSE_META.enable_voip_calling){
            document.getElementById("easyassist_agent_connect_modal").style.display = "none";
        } else {
            document.getElementById("easyassist_agent_connect_video_call_modal").style.display = "none";
        }    
    } catch (error) {
        
    }
}

function request_for_meeting() {

    // if(call_initiate_by_agent == "true"){
    //     if(EASYASSIST_COBROWSE_META.enable_voip_calling){
    //     easyassist_show_toast("Agent has initiated a Voice call, request you to accept it");
    //     } else {
    //         easyassist_show_toast("Agent has initiated a Video call, request you to accept it");
    //     }
    //     document.getElementById("easyassist_agent_connect_modal").style.display = "none";
    //     return;
    // }

    var local_storage_obj = get_easyassist_current_session_local_storage_obj();
    if(local_storage_obj && local_storage_obj.hasOwnProperty("call_initiate_by_agent")) {
        if(local_storage_obj["call_initiate_by_agent"] == "true") {
            if(EASYASSIST_COBROWSE_META.enable_voip_calling){
                easyassist_show_toast("Agent has initiated a Voice call, request you to accept it");
            } else {
                easyassist_show_toast("Agent has initiated a Video call, request you to accept it");
            }
            document.getElementById("easyassist_agent_connect_modal").style.display = "none";
            return;
        }
    }

    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    send_customer_request_meeting_modal_invited_agent_show_request();

    let session_id = get_easyassist_cookie("easyassist_session_id");
    let is_easyassist_meeting_on_client = get_easyassist_cookie("is_easyassist_meeting_on_client");
    if(session_id == is_easyassist_meeting_on_client) {
        easyassist_show_toast("Meeting request has been sent."); 
        if(document.getElementById("easyassist_agent_connect_modal")) {
            document.getElementById("easyassist_agent_connect_modal").style.display = "none";
        }
        if(document.getElementById("easyassist_agent_connect_video_call_modal")) {
            document.getElementById("easyassist_agent_connect_video_call_modal").style.display = "none";
        }
        return;
    }

    let json_string = JSON.stringify({
        "id": easyassist_session_id
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    var request_meeting_error = document.getElementById("request_meeting_error");
    easyassist_send_call_initiate_over_socket();
    if(EASYASSIST_COBROWSE_META.enable_voip_calling) {
        if(request_meeting_error.offsetParent == null) {
            easyassist_show_toast("An voice call has been initiated to the agent.");
        }
    } else {
        request_meeting_error = document.getElementById("request_meeting_error_cobrowse_video_call");
        if(request_meeting_error.offsetParent == null) {
            easyassist_show_toast("A video call has been initiated to the customer.");
        }
    }

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/customer/request-assist-meeting/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                if(request_meeting_error.offsetParent) {
                    request_meeting_error.innerHTML = "Request has been sent to agent";
                    request_meeting_error.style.color = 'green';
                }

                if(check_meeting_status_interval != null) {
                    clearInterval(check_meeting_status_interval);
                    check_meeting_status_interval = null;
                }

                check_meeting_status_interval = setInterval(function() {
                    check_meeting_status()
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

function check_meeting_status() {
    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    let json_string = JSON.stringify({
        "id": easyassist_session_id
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/client/check-meeting-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            var request_meeting_error = document.getElementById("request_meeting_error");
            if (response.status == 200) {
                
                if (response.is_meeting_allowed == true) {

                    if(EASYASSIST_COBROWSE_META.enable_voip_calling) {
                        document.getElementById("easyassist_agent_connect_modal").style.display = "none";
                        set_easyassist_cookie("is_cobrowse_meeting_active", easyassist_session_id);
                        easyassist_open_voip_meeting_window();
                        request_meeting_error.innerHTML = 'Voice call request has been accepted by the agent. Please click on "Connect" to join the voice call.';
                        request_meeting_error.style.color = 'green';
                        let html = document.getElementById("request_meeting_button");
                        let button = '<button class="easyassist-modal-success-btn" type="button" onclick="easyassist_open_voip_meeting_window();close_modal();">Connect</button>\
                            <button class="easyassist-modal-primary-btn" type="button" style="background: '+ EASYASSIST_COBROWSE_META.floating_button_bg_color +' !important;" onclick="request_for_meeting(\'' + easyassist_session_id + '\')">Resend Request</button>';
                        html.innerHTML = button;
                        document.getElementById("voip-cross-icon").style.display = "";

                    } else if(EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {
                        set_easyassist_cookie("cobrowse_meeting_id", easyassist_session_id);
                        document.getElementById("easyassist_agent_connect_video_call_modal").style.display = "none";
                        request_meeting_error = document.getElementById("request_meeting_error_cobrowse_video_call");
                        request_meeting_error.innerHTML = "Meeting request has been accepted by the Agent. Please click on 'Connect' to join the meeting."
                        set_easyassist_cookie("is_cobrowse_meeting_active", easyassist_session_id);
                        easyassist_show_customer_cobrowse_meeting_option();

                        request_meeting_error.innerHTML = "";
                        request_meeting_error.style.color = 'green';
                        let html = document.getElementById("request_meeting_button_cobrowse_video_call");
                        let button = '<button class="easyassist-modal-success-btn" type="button" onclick="easyassist_show_customer_cobrowse_meeting_option();close_modal();">Connect</button>\
                            <button class="easyassist-modal-primary-btn" id="request_button" type="button" style="background: '+ EASYASSIST_COBROWSE_META.floating_button_bg_color +' !important;" onclick="request_for_meeting(\'' + easyassist_session_id + '\')">Resend Request</button>';
                        html.innerHTML = button;
    
                    } else {
                        document.getElementById("easyassist_agent_connect_video_call_modal").style.display = "none";
                        easyassist_open_meeting_window(easyassist_session_id);
                        request_meeting_error = document.getElementById("request_meeting_error_cobrowse_video_call");
                        request_meeting_error.innerHTML = "Meeting request has been accepted by the Agent. Please click on 'Connect' to join the meeting."
                        request_meeting_error.style.color = 'green';
                        let html = document.getElementById("request_meeting_button_cobrowse_video_call");
                        let button = '<button class="easyassist-modal-success-btn" type="button" onclick="easyassist_open_meeting_window(\'' + easyassist_session_id + '\');close_modal();">Connect</button>\
                            <button class="easyassist-modal-primary-btn" id="request_button" type="button" style="background: '+ EASYASSIST_COBROWSE_META.floating_button_bg_color +' !important;" onclick="request_for_meeting(\'' + easyassist_session_id + '\')">Resend Request</button>';
                        html.innerHTML = button

                    }
                    auto_msg_popup_on_client_call_declined = false;
                    if(check_meeting_status_interval != null) {
                        clearInterval(check_meeting_status_interval);
                        check_meeting_status_interval = null;
                    }
                }
                 else if (response.is_meeting_allowed == false) {
                    if(response.is_agent_answer == true){
                        if(EASYASSIST_COBROWSE_META.enable_voip_calling) {
                            if(auto_msg_popup_on_client_call_declined == true) {
                                // easyassist_show_toast("Customer declined the call");
                                // allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow
                                // allincall_chat_window.postMessage(JSON.stringify({
                                //     "id": "agent_name",
                                //     "name": window.AGENT_NAME,
                                //     "session_id": COBROWSE_SESSION_ID,
                                //     "agent_connect_message": VOIP_DECLINE_MEETING_MESSAGE
                                // }), window.location.protocol + "//" + window.location.host);
                                // open_livechat_agent_window();
                                
                            } else {
                                if(request_meeting_error.offsetParent == null) {
                                    easyassist_show_toast("Agent declined the call");
                                }
                                if(document.getElementById("easyassist_agent_connect_modal").style.display = "none"){
                                    document.getElementById("easyassist_agent_connect_modal").style.display = "flex";
                                }
                                request_meeting_error.innerHTML = "The voice call request has been rejected by the agent"
                                request_meeting_error.style.color = 'red';
                                let html = document.getElementById("request_meeting_button");
                                let button = '<button class="easyassist-modal-cancel-btn " style="color: '+ EASYASSIST_COBROWSE_META.floating_button_bg_color +' !important;" onclick="close_modal()">Close</button>\
                                    <button class="easyassist-modal-primary-btn" style="background: '+ EASYASSIST_COBROWSE_META.floating_button_bg_color +' !important;" id="request_button" type="button" onclick="request_for_meeting(\'' + easyassist_session_id + '\')">Resend Request</button>';
                                html.innerHTML = button
                                document.getElementById("voip-cross-icon").style.display = "none";
                            }
                        } else {
                            if(document.getElementById("easyassist_agent_connect_video_call_modal").style.display = "none"){
                                document.getElementById("easyassist_agent_connect_video_call_modal").style.display = "flex";
                            }
                            request_meeting_error = document.getElementById("request_meeting_error_cobrowse_video_call");
                            request_meeting_error.innerHTML = "Meeting request has been rejected by Agent."
                            request_meeting_error.style.color = 'red';
                            let html = document.getElementById("request_meeting_button_cobrowse_video_call");
                            let button = '<button class="easyassist-modal-cancel-btn" style="color: '+ EASYASSIST_COBROWSE_META.floating_button_bg_color +' !important;" type="button" onclick="close_modal()">Close</button>\
                                <button class="easyassist-modal-primary-btn" id="request_button" type="button" style="background: '+ EASYASSIST_COBROWSE_META.floating_button_bg_color +' !important;" onclick="request_for_meeting(\'' + easyassist_session_id + '\')">Resend Request</button>';
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

function easyassist_send_call_initiate_over_socket(){
    let json_string = JSON.stringify({
        "type": "call_initiate_by_customer",
    });

    let encrypted_data = easyassist_custom_encrypt(json_string)
    encrypted_data = {
        "Request": encrypted_data
    };

    easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
}

function send_customer_request_meeting_modal_invited_agent_show_request(){
    let json_string = JSON.stringify({
        "type": "customer_request_meeting_modal_invited_agent"
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
}

function show_customer_side_call_icon(should_show_icon) {
    if(should_show_icon) {
        if(document.getElementById("customer_side_call_initiate_icon")) {
            set_easyassist_current_session_local_storage_obj("hide_customer_call_initiation_icon", "false");
            if(EASYASSIST_COBROWSE_META.is_mobile == true) {
                document.getElementById("customer_side_call_initiate_icon").parentElement.parentElement.style.display = "inherit";
            } else {
                document.getElementById("customer_side_call_initiate_icon").style.display = "inherit";
            }
        }
    } else {
        if(document.getElementById("customer_side_call_initiate_icon")) {
            set_easyassist_current_session_local_storage_obj("hide_customer_call_initiation_icon", "true");
            if(EASYASSIST_COBROWSE_META.is_mobile == true) {
                document.getElementById("customer_side_call_initiate_icon").parentElement.parentElement.style.display = "none";
            } else {
                document.getElementById("customer_side_call_initiate_icon").style.display = "none";
            }
        }
    }
}

function hide_chat_bubble_greeting_div() {
    document.querySelector(".chat-talk-bubble").style.display = "none";
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

function easyassist_limit_characters(message, char_limit) {
    if (message.length > char_limit) {
        message = message.substring(0, char_limit) + "...";
    }
    return message;
}

function easyassist_append_chat_bubble_message(agent_name, message, attachment, attachment_file_name){    
    document.getElementById("chat-minimize-icon-wrapper").style.display = "block";
    document.querySelector(".chat-talk-bubble").classList.remove("bounce2");
    var message_box = document.getElementById("talktext-p");
    document.querySelector(".chat-talk-bubble").style.display = "block";
    document.querySelector(".chat-talk-bubble").classList.add("bounce2");
    easyassist_play_greeting_bubble_popup();

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
    if(message_box.innerHTML == "") {
        message_box.innerHTML = "..!link!..";
    }
    set_easyassist_current_session_local_storage_obj("last_message",received_message);
    setTimeout(function(){
        document.querySelector(".chat-talk-bubble").classList.remove("bounce2");
    },1500);
}

function check_proxy_cobrowsing() {
    let first_index = window.location.href.indexOf("proxy-key");
    if (first_index <= 0) 
        return false;
    return true;
}

function get_proxy_url_domain() {
    let proxy_iframe_src =  document.getElementById("proxy-iframe").contentWindow.location.href;
    let last_http_index = proxy_iframe_src.lastIndexOf("http");
    let domain = proxy_iframe_src.substring(last_http_index);
    if(domain) {
        let url_obj = new URL(domain);
        if(url_obj.protocol == "https:") {
            domain = domain.replace(/^https?:\/\//, '');
        } else {
            domain = domain.replace(/^http?:\/\//, '');
        }
        domain = domain.replace(/\/+/, '/');
        return domain.trim()
    }

    return "";
}

/*
In some sites the DOM renders again without page refresh, due to which agents are able to see the masked fields values while cobrowsing,
this is happening because the attribute which we use to set a field as masked get removed from the elements and then mutuation summary sync 
the non masked data on agent side. 
So to fix this we have used the mutation observer to observe subtree and child node changes of the body element. 
When there are changes in the elements present in the body then the observer triggers and we add back the masking attributes.
We are comenting this code to reduce the extra operations on the sites which are not re-rendering the DOM, this DOM re-rendering
occurs mostly in sites which involves ASP.net framework.
*/
// const muntation_summary_observer = new MutationObserver(mutation_records => {
//     easyassist_masked_field_attr_set()
// });

// muntation_summary_observer.observe(document.getElementsByTagName("body")[0], {
//     childList: true,
//     subtree: true,
// });

function easyassist_send_apply_event_listener_over_socket() {

    let modal_element = document.getElementById("easyassist_pdf_render_modal_wrapper");

    if(!modal_element) {
        return;
    }

    let json_string = JSON.stringify({
        "type": "apply_coview_listener",
        "element_id": easyassist_get_easyassist_id_from_element(modal_element).toString()
    });

    let encrypted_data = easyassist_custom_encrypt(json_string)
    encrypted_data = {
        "Request": encrypted_data
    };

    easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
}

function easyassist_send_remove_event_listener_over_socket() {

    if(get_easyassist_cookie("easyassist_edit_access") == "true")
        return;
    
    let modal_element = document.getElementById("easyassist_pdf_render_modal_wrapper");

    if(!modal_element) {
        return;
    }

    let json_string = JSON.stringify({
        "type": "remove_coview_listener",
        "element_id": easyassist_get_easyassist_id_from_element(modal_element).toString()
    });

    let encrypted_data = easyassist_custom_encrypt(json_string)
    encrypted_data = {
        "Request": encrypted_data
    };

    easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
}

function easyassist_send_tab_not_focus_over_socket(action="") {
    try {
        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
        if (easyassist_session_id == null || easyassist_session_id == undefined) {
            return;
        }

        let json_string = JSON.stringify({
            "type": "client_tab_not_focus",
            "action": action         
        });

        let encrypted_data = easyassist_custom_encrypt(json_string)
        encrypted_data = {
            "Request": encrypted_data
        };

        easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");

    } catch(err) {
        console.log("easyassist_send_tab_not_focus_over_socket: ", err);
    }
}