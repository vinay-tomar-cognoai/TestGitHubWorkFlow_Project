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
var AGENT_WEAK_CONNECTION_DETECTED = false;

var easyassist_speed_mbps = 0;
var easyassist_internet_iteration = 2;
var is_client_network_bandwidth_measured = false;
var check_cobrowse_session_timer = null;

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
            AGENT_WEAK_CONNECTION_DETECTED = true;
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
            }
        client_websocket.onclose = function() {
                client_websocket_open = false;
                client_websocket = null; 
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

function easyassist_send_message_over_socket(message, sender) {
    try{
        var allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;

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

            var packet = JSON.stringify({
                "message": {
                    "header": {
                        "sender": sender,
                        "packet": packet_counter
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
    ws_scheme = EASYASSIST_HOST_PROTOCOL == "http" ? "ws" : "wss"
    url = ws_scheme + '://' + EASYASSIST_COBROWSE_HOST + '/ws/cobrowse/sync-utils/' + jid + '/' + sender + "/";
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
        var allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;

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

            var packet = JSON.stringify({
                "message": {
                    "header": {
                        "sender": sender,
                        "packet": packet_counter
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

    var allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;
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
            let code;
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

function easyassist_agent_socket_message_handler(data_packet) {

    easyassist_reset_internet_connectivity_check_timer();

    if (data_packet.type == "highlight") {

        easyassist_sync_agent_highlight(data_packet);

    } else if (data_packet.type == "screenshot") {

        easyassist_capture_client_screenshot(data_packet.agent_name);

    } else if (data_packet.type == "pageshot") {

        easyassist_capture_client_pageshot();

    } else if (data_packet.type == "html") {

        easyassist_send_html_request_received_message_over_socket();
        if(data_packet.is_agent_weak_connection == true) {
            AGENT_WEAK_CONNECTION_DETECTED = true;
        } else {
            AGENT_WEAK_CONNECTION_DETECTED = false;
        }
        easyassist_set_agent_weak_connection_cookie();
        easyassist_sync_html_data();

    } else if (data_packet.type == "sync-scroll") {

        easyassist_sync_client_scroll_position(data_packet);

    } else if (data_packet.type == "mouse") {
        
        easyassist_sync_agent_mouse(data_packet);

    } else if (data_packet.type == "chat") {

        easyassist_sync_agent_chat(data_packet);

    }  else if (agent_packet.type == "livechat-typing") {

        easyassist_sync_typing_loader(data_packet);

    } else if (data_packet.type == "request-edit-access") {

        easyassist_show_request_edit_access_form();

    } else if (data_packet.type == "revoke-edit-access") {
        
        agent_revoke_edit_access = true;
        easyassist_revoke_edit_access();

    } else if (data_packet.type == "sync-form") {

        easyassist_agent_sync_form(data_packet);

    } else if (data_packet.type == "button-click") {

        easyassist_sync_button_click_event(data_packet);

    } else if (data_packet.type == "end_voip_meeting") {

        easyassist_end_voip_meeting(data_packet);

    } else if (data_packet.type == "voip_meeting_ready") {

        easyassist_voip_meeting_ready(data_packet);

    } else if (data_packet.type == "div-scroll") {

        easyassist_sync_agent_div_scroll(data_packet);

    } else if (data_packet.type == "support_agent_connected") {

        easyassist_show_toast("Agent " + data_packet.agent_name + " has joined the session.");

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

        AGENT_WEAK_CONNECTION_DETECTED = data_packet.is_agent_weak_connection;
        easyassist_set_agent_weak_connection_cookie();

        if(data_packet.is_html_needed) {
            easyassist_sync_html_data();
        }

    } else if (data_packet.type == "client_low_bandwidth_html_request") {

        AGENT_WEAK_CONNECTION_DETECTED = true;
        easyassist_sync_html_data();

    } else if (data_packet.type == "get_lead_status") {

        easyassist_check_is_lead_converted();

    } else if(data_packet.type == "html_received") {

        easyassist_start_parse_dom_tree_interval();
    }
}

function easyassist_set_agent_weak_connection_cookie() {
    if(AGENT_WEAK_CONNECTION_DETECTED) {
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
    try{
        let agent_packet = message.body.Request;
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

    if (message.header.sender == "agent") {

        easyassist_agent_socket_message_handler(agent_packet);
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
            window.onmousemove = function(event) {
                easyassist_sync_mouse_position(event);
            }

            easyassist_client_heartbeat_timer = setInterval(function(e) {
                easyassist_client_heartbeat();
            }, 5000);

            let easyassist_messages_to_customer_utils_timer = setInterval(function(e) {
                easyassist_messages_to_customer_utils();
            }, 5000);

            easyassist_check_for_agent_guide_timer = setInterval(function(e) {
                easyassist_check_for_agent_highlight();
            }, EASYASSIST_COBROWSE_META.highlight_api_call_frequency * 1000);

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

function easyassist_update_agent_assistant_request(status) {

    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    var client_otp = "None";

    if (status == "true" && EASYASSIST_COBROWSE_META.enable_verification_code_popup == true) {
        client_otp = "";
        let verify_inputs = easyassist_get_eles_by_class_name("easyassist-verfication-otp-input")
        for(let i = 0; i < verify_inputs.length; i++) {
            client_otp += verify_inputs[i].value
        }
        if (client_otp == "" || client_otp == undefined || client_otp == null) {
            document.getElementById("easyassist-request-assist-otp-error").innerHTML = "Please enter valid OTP";
            document.getElementById("easyassist-request-assist-otp-error").previousSibling.style.paddingBottom = "1em";
            return;
        }
    }

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
                var description = "Update Agent Assistant Request API (/easy-assist/update-agent-assistant-request/) failed with status code " + response.status + ", Invalid Verification Code";
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
            document.getElementById("easyassist-agent-information-agent-name").innerHTML = "Name: <strong>" + agent_details.agent_name + "</strong>";
            document.getElementById("easyassist-agent-information-agent-location").innerHTML = "Address: <strong>" + agent_location + "</strong>";
        }
    } catch (err) {
        console.log("easyassist_update_agent_location_detail: ", err)
    }
}

function easyassist_check_for_agent_highlight() {

    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    // var allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    json_string = JSON.stringify({
        "id": easyassist_session_id
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

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
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status == 500) {
                console.log("Interval Clearted", response);
                clearInterval(easyassist_check_for_agent_guide_timer);
                easyassist_terminate_cobrowsing_session();
                return;
            }

            if (response.status != 200) {
                console.log("Interval Cleared", response);
                clearInterval(easyassist_check_for_agent_guide_timer);
                var description = "Client activity check API (/easy-assist/highlight/) failed with status code " + response.status;
                return;
            }

            /*************** Session Archive START *************/

            if (response.is_archived == true) {

                if(easyassist_session_expired_flag == true) return;

                easyassist_session_expired_flag = true;

                document.getElementById("agent-mouse-pointer").style.display = "none";
                easyassist_hide_floating_sidenav_menu();

                if(response.session_ended_by_agent == true && response.cobrowsing_start_datetime != null){
                    easyassist_show_toast(response.agent_name + " has ended the session.");
                    var session_archived_datetime = new Date(response.session_archived_datetime);
                    let time_delta = parseInt((new Date() - session_archived_datetime) / 1000)
                    if (time_delta >= 5 * 60) {
                        var feedback_modal = document.getElementById("easyassist-co-browsing-feedback-modal");
                        document.getElementById("feedback-modal-header-text").innerHTML = "Please provide the feedback for the last Cobrowsing session";
                        document.getElementById("feedback-modal-header-text").style.paddingTop = "30px";
                        feedback_modal.querySelector(".easyassist-customer-feedback-modal-header").classList.add("feedback-modal-padding")
                    }
                    easyassist_show_feedback_form();
                } else {
                    easyassist_show_toast("Session closed due to inactivity.");
                    easyassist_terminate_cobrowsing_session();
                }

                return
            }

            /*************** Session Archive END *************/

            easyassist_update_agent_location_detail({ "agent_name": response.agent_name, "agent_location": response.agent_location })

            if (response.agent_assistant_request_status == true) {
                let agent_requested_for_assistant = true;
                set_easyassist_cookie("agent_requested_for_assistant", "true")
                if (document.getElementById("easyassist-co-browsing-request-assist-modal").style.display != "flex") {
                    try {
                        verify_inputs = easyassist_get_eles_by_class_name("easyassist-verfication-otp-input")
                        for(let i = 0; i < verify_inputs.length; i++) {
                            verify_inputs[i].value = "";
                            verify_inputs[i].style.color = 'inherit';
                            verify_inputs[i].style.borderColor = 'inherit';
                        }
                        document.getElementById("easyassist-co-browsing-request-assist-modal").style.display = "flex";
                        verify_inputs[0].focus();
                        delete_easyassist_cookie("easyassist_session_created_on");
                        easyassist_hide_floating_sidenav_button();
                    } catch (err) {}
                }
            }

            if (response.agent_meeting_request_status == true) {
                let agent_meeting_request_status = true;
                set_easyassist_cookie("agent_meeting_request_status", "true")
                if (EASYASSIST_COBROWSE_META.allow_video_meeting_only == true) {
                    if (document.getElementById("easyassist-co-browsing-request-meeting-modal").style.display != "flex") {
                        document.getElementById("easyassist-co-browsing-request-meeting-modal").style.display = "flex";
                    }
                } else {
                    if (EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {
                        if (document.getElementById("easyassist-voip-video-calling-request-modal").style.display != "flex") {
                            document.getElementById("easyassist-voip-video-calling-request-modal").style.display = "flex";
                        }
                    } else if (EASYASSIST_COBROWSE_META.enable_voip_calling) {
                        if (document.getElementById("easyassist-voip-calling-request-modal").style.display != "flex") {
                            document.getElementById("easyassist-voip-calling-request-modal").style.display = "flex";
                        }
                    } else {
                        if (document.getElementById("easyassist-co-browsing-request-meeting-modal").style.display != "flex") {
                            document.getElementById("easyassist-co-browsing-request-meeting-modal").style.display = "flex";
                        }
                    }
                }
                delete_easyassist_cookie("easyassist_session_created_on");
                easyassist_hide_floating_sidenav_button();
            }
            if (response.allow_agent_meeting == "true") {
                if (EASYASSIST_COBROWSE_META.allow_video_meeting_only == true) {
                    let cobrowsing_meeting = get_easyassist_cookie("is_cobrowse_meeting_on")
                    if (cobrowsing_meeting == '' || cobrowsing_meeting == null || cobrowsing_meeting == undefined) {
                        cobrowsing_meeting = false
                    }
                    if (cobrowsing_meeting == false || cobrowsing_meeting == 'false') {
                        easyassist_open_meeting_window();
                        EASYASSIST_COBROWSE_META.allow_meeting = true;
                    }
                } else {
                    if (EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {
                        easyassist_show_cobrowse_meeting_option();
                    } else if (EASYASSIST_COBROWSE_META.enable_voip_calling) {
                        cobrowsing_meeting = get_easyassist_cookie("is_cobrowse_meeting_on")
                        if (cobrowsing_meeting == '' || cobrowsing_meeting == null || cobrowsing_meeting == undefined) {
                            cobrowsing_meeting = false
                        }
                        if (cobrowsing_meeting == false || cobrowsing_meeting == 'false') {
                            easyassist_open_voip_meeting_window();
                        }
                    } else {
                        cobrowsing_meeting = get_easyassist_cookie("is_cobrowse_meeting_on")
                        if (cobrowsing_meeting == '' || cobrowsing_meeting == null || cobrowsing_meeting == undefined) {
                            cobrowsing_meeting = false
                        }
                        if (cobrowsing_meeting == false || cobrowsing_meeting == 'false') {
                            easyassist_open_meeting_window();
                            EASYASSIST_COBROWSE_META.allow_meeting = true;
                        }
                    }
                }
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

            if (response.agent_name == null && EASYASSIST_COBROWSE_META.lead_generation == false) {
                easyassist_show_toast("Our customer service agent will join the session soon.");
                return;
            }
            if (response.is_agent_connected == true) {
                easyassist_hide_agent_joining_modal();
                easyassist_show_floating_sidenav_menu();
                if (EASYASSIST_COBROWSE_META.enable_masked_field_warning == true) {
                    easyassist_get_eles_by_class_name("easyassist-tooltiptext")[0].style.display = "inline";
                }
                let agent_connected_cookie = get_easyassist_cookie("easyassist_agent_connected");
                if (is_agent_connected == false && agent_connected_cookie != "true") {
                    easyassist_show_toast("Agent " + response.agent_name + " has joined the session.");
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
            
        } else if (this.readyState == 4) {
            var description = "Client activity check API (/easy-assist/highlight/) failed with status code " + this.status.toString();
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
    delete_easyassist_cookie("agent_meeting_request_status");
}

function easyassist_terminate_cobrowsing_session(show_message = true) {
    try {

        json_string = JSON.stringify({
            "type": "end_session",
        });

        encrypted_data = easyassist_custom_encrypt(json_string)
        encrypted_data = {
            "Request": encrypted_data
        };

        easyassist_send_message_over_socket(encrypted_data, "client");

        EASYASSIST_COBROWSE_META.allow_cobrowsing = false;

        try {
            if (parse_dom_tree_interval != null && parse_dom_tree_interval != undefined) {
                clearInterval(parse_dom_tree_interval);
                let parse_dom_tree_interval = null;
            }
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
        } catch (err) {
            console.log(err);
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

        if(document.getElementById("agent-mouse-pointer")){
            document.getElementById("agent-mouse-pointer").style.display = "none";
        }
        if(easyassist_get_eles_by_class_name("easyassist-tooltiptext").length > 0){
            easyassist_get_eles_by_class_name("easyassist-tooltiptext")[0].style.display = "none";
        }

        if (show_message) {
            easyassist_show_toast("Session has ended.");
        }
    } catch (err) {
        easyassist_delete_all_cookie();
        console.error("Error on termination", err)
    }
}

function remove_special_characters_from_str(text) {
    var regex = /:|;|'|"|=|-|\$|\*|%|!|`|~|&|\^|\(|\)|\[|\]|\{|\}|\[|\]|#|<|>|\/|\\/g;
    text = text.replace(regex, "");
    return text;
}

function easyassist_submit_client_feedback(feedback_type) {

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

    json_string = JSON.stringify({
        "session_id": easyassist_session_id,
        "rating": rating,
        "feedback": feedback
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
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
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status != 200) {
                // var description = "Submit client feedback API (/easy-assist/submit-client-feedback/) failed with status code " + response.status;
            }

            easyassist_terminate_cobrowsing_session();
        } else if (this.readyState == 4) {

            easyassist_terminate_cobrowsing_session();
            var description = "Submit client feedback API (/easy-assist/submit-client-feedback/) failed with status code " + this.status.toString();
        }
    }
    xhttp.send(params);
}


function easyassist_check_agent_available_status(callback=null) {
    json_string = JSON.stringify({
        "access_token": window.EASYASSIST_COBROWSE_META.access_token
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
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
            response = JSON.parse(this.responseText);
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
                        document.getElementById("easyassist-side-nav-options-co-browsing").setAttribute("onclick", "easyassist_show_product_category_modal()");
                    } else {
                        document.getElementById("easyassist-side-nav-options-co-browsing").setAttribute("onclick", "easyassist_show_browsing_modal()");
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

function easyassist_messages_to_customer_utils() {
    if (EASYASSIST_COBROWSE_META.no_agent_connects_toast) {
        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
        if (easyassist_session_id == null || easyassist_session_id == undefined) {
            return;
        }
        if (EASYASSIST_COBROWSE_META.show_floating_button_after_lead_search == true) {
            var easyassist_session_created_on = get_easyassist_cookie("easyassist_session_created_on");
            if (easyassist_session_created_on != undefined && easyassist_session_created_on != null) {
                if (easyassist_session_created_on == "lead") {
                    return
                }
            }
        }

        if (get_easyassist_cookie("easyassist_agent_connected") == "true" || 
            get_easyassist_cookie("agent_requested_for_assistant") == "true" ||
            get_easyassist_cookie("agent_meeting_request_status") == "true" ) {
            return;
        }

        var easyassist_request_timestamp = parseInt(get_easyassist_cookie("easyassist_request_timestamp"));
        var timestamp_now = Date.now()
        var target_threshold_in_second = EASYASSIST_COBROWSE_META.no_agent_connects_toast_threshold * 60;
        var temp_threshold = timestamp_now - easyassist_request_timestamp;
        temp_threshold = parseInt(temp_threshold / 1000)
        if (temp_threshold > target_threshold_in_second) {
            if (easyassist_get_messages_to_customer_cookie("no_agent_connects_toast_text") == -1) {
                easyassist_show_toast(EASYASSIST_COBROWSE_META.no_agent_connects_toast_text);
                easyassist_set_messages_to_customer_cookie("no_agent_connects_toast_text")
            }
        }
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

        if (EASYASSIST_COBROWSE_META.field_recursive_stuck_event_check == false) {
            easyassist_remove_formassist_stuck_timer_handler();
        }

        var easyassist_cobrowsing_modal = document.getElementById("easyassist-co-browsing-modal-id");
        if (easyassist_cobrowsing_modal && easyassist_cobrowsing_modal.style.display == "none") {
            easyassist_show_cobrowsing_modal();
        }
    }, EASYASSIST_COBROWSE_META.field_stuck_timer * 1000);
}

function easyassist_reset_element_stuck_timer() {
    easyassist_stop_element_stuck_timer();
    easyassist_start_element_stuck_timer();
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

        window.addEventListener("mousemove", easyassist_reset_element_stuck_timer, true);

        let form_input_elements = document.getElementsByTagName("input");
        for(let index = 0; index < form_input_elements.length; index++) {
            if (form_input_elements[index].getAttribute("class") == "easyassist-input-field") {
                continue;
            }
            form_input_elements[index].addEventListener("focusin", easyassist_reset_element_stuck_timer, true);
            form_input_elements[index].addEventListener("keypress", easyassist_reset_element_stuck_timer, true);
        }

        let form_textarea_elements = document.getElementsByTagName("textarea");
        for(let index = 0; index < form_textarea_elements.length; index++) {
            form_textarea_elements[index].addEventListener("focusin", easyassist_reset_element_stuck_timer, true);
            form_textarea_elements[index].addEventListener("keypress", easyassist_reset_element_stuck_timer, true);
        }

        let form_select_elements = document.getElementsByTagName("select");
        for(let index = 0; index < form_select_elements.length; index++) {
            form_select_elements[index].addEventListener("mousedown", easyassist_reset_element_stuck_timer, true);
            form_select_elements[index].addEventListener("change", easyassist_reset_element_stuck_timer, true);
        }
    }catch(err){}
}

function easyassist_remove_formassist_stuck_timer_handler() {

    window.removeEventListener("mousemove", easyassist_reset_element_stuck_timer, true);

    form_input_elements = document.getElementsByTagName("input");
    for(let index = 0; index < form_input_elements.length; index++) {
        form_input_elements[index].removeEventListener("focusin", easyassist_reset_element_stuck_timer, true);
        form_input_elements[index].removeEventListener("keypress", easyassist_reset_element_stuck_timer, true);
    }
    form_textarea_elements = document.getElementsByTagName("textarea");
    for(let index = 0; index < form_textarea_elements.length; index++) {
        form_textarea_elements[index].removeEventListener("focusin", easyassist_reset_element_stuck_timer, true);
        form_textarea_elements[index].removeEventListener("keypress", easyassist_reset_element_stuck_timer, true);
    }
    form_select_elements = document.getElementsByTagName("select");
    for(let index = 0; index < form_select_elements.length; index++) {
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

    json_string = JSON.stringify({
        "html": screenshot,
        "id": EASYASSIST_SESSION_ID,
        "active_url": window.location.href,
        "init_transaction": true
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
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
            response = JSON.parse(this.responseText);
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

    var active_url = window.location.href.replace(window.location.protocol + "//", "");
    active_url = active_url.toLowerCase();
    var urls_list_lead_converted = window.EASYASSIST_COBROWSE_META.urls_list_lead_converted;

    for(let index = 0; index < urls_list_lead_converted.length; index++) {
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
    
    json_string = JSON.stringify({
        "session_id": get_easyassist_cookie("easyassist_session_id"),
        "active_url": window.location.href
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
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
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
        }
    }
    xhttp.send(params);
}

setTimeout(function() {
    if (get_easyassist_cookie("is_lead_converted") != get_easyassist_cookie("easyassist_session_id")) {
        easyassist_check_is_lead_converted();
    }
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

    json_string = JSON.stringify({
        "type": "heartbeat",
        "active_url": window.location.href
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
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

    json_string = JSON.stringify({
        "type": "lead_status",
        "is_converted": is_converted
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
}

/************************ END UTILS SOCKET MESSAGE ****************************/

/******************************** EDIT ACCESS *********************************/

function easyassist_update_agent_request_edit_access(action) {

    var allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;

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
    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
    agent_revoke_edit_access = false;
}

function easyassist_revoke_edit_access(data_packet) {
    try{
        if (agent_revoke_edit_access) {
            easyassist_show_toast("Edit Access has been revoked by the agent.");
        } else {
            easyassist_show_toast("Edit Access has been revoked from agent.");
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

    json_string = JSON.stringify({
        "id": easyassist_session_id,
        "content": screenshot,
        "type_screenshot": "pageshot"
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
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
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status != 200) {
                var description = "Capture client pageshot API (/easy-assist/capture-client-screen/) failed with status code " + response.status;
            }

            json_string = JSON.stringify({
                "type": "pageshot",
                "active_url": window.location.href,
                "result": response.status
            });

            encrypted_data = easyassist_custom_encrypt(json_string);

            encrypted_data = {
                "Request": encrypted_data
            };

            easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");

        } else if (this.readyState == 4) {
            var description = "Capture client pageshot API (/easy-assist/capture-client-screen/) failed with status code " + this.status.toString();
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

    if(EASYASSIST_COBROWSE_META.allow_screen_sharing_cobrowse == false && easyassist_check_weak_connection_enabled()) {
        easyassist_create_value_attr_into_document();
    }

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
            if(EASYASSIST_COBROWSE_META.allow_screen_sharing_cobrowse == false) {
                easyassist_set_value_attr_into_screenshot(clone_document_node);
            }
        },
        ignoreElements: function(element) {
            return easyassist_check_dom_node(element);
        },
    }).then(function(canvas) {
        // Get base64URL
        let img_data = canvas.toDataURL('image/png');
        // var screenshot = easyassist_screenshot_page();
        json_string = JSON.stringify({
            "id": easyassist_session_id,
            "content": img_data,
            "type_screenshot": "screenshot"
        });

        encrypted_data = easyassist_custom_encrypt(json_string);

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
                response = JSON.parse(this.responseText);
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
                        easyassist_show_toast("Agent " + agent_name + " has captured a screenshot")
                    } else {
                        easyassist_show_toast("Agent " + " has captured a screenshot")
                    }
                }
                if (response.status != 200) {
                    var description = "Capture client screenshot API (/easy-assist/capture-client-screen/) failed with status code " + response.status;
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

                var description = "Capture client screenshot API (/easy-assist/capture-client-screen/) failed with status code " + this.status.toString();
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

    json_string = JSON.stringify({
        "session_id": easyassist_session_id
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

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
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            window.CLIENT_NAME = response.client_name;
            easyassist_send_client_name(response.client_name);
            if (response.status == 200 && response.chat_history.length > 0) {
                let chat_history = response.chat_history;
                let allincall_chat_window = document.getElementById("easyassist-livechat-iframe").contentWindow;
                for(let index = 0; index < chat_history.length; index++) {
                    let sender = chat_history[index]["sender"];
                    message = chat_history[index]["message"];
                    message = easyassist_show_hyperlink_inside_text(message);
                    let datetime = chat_history[index]["datetime"];
                    var time = datetime.split(" ")[3] + " " + datetime.split(" ")[4];
                    let attachment = chat_history[index]["attachment"];
                    let attachment_file_name = chat_history[index]["attachment_file_name"];
                    let chat_type = chat_history[index]["chat_type"];
                    if (sender == "client") {
                        allincall_chat_window.postMessage(JSON.stringify({
                            "client_name": response.client_name,
                            "message": message,
                            "attachment": attachment,
                            "attachment_file_name": attachment_file_name,
                            "show_client_message": true,
                            "time": time,
                            "chat_type": chat_type,
                        }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);
                    } else {
                        allincall_chat_window.postMessage(JSON.stringify({
                            "agent_name": sender,
                            "message": message,
                            "attachment": attachment,
                            "attachment_file_name": attachment_file_name,
                            "show_agent_message": true,
                            "time": time,
                            "chat_type": chat_type,
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

    var allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;

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

            json_string = JSON.stringify({
                "filename": file.name,
                "base64_file": base64_str
            });

            encrypted_data = easyassist_custom_encrypt(json_string);

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
                    response = JSON.parse(this.responseText);
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
        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

        if (easyassist_session_id == null || easyassist_session_id == undefined) {
            return;
        }

        json_string = JSON.stringify({
            "type": "chat",
            "message": message,
            "attachment": attachment,
            "attachment_file_name": attachment_file_name,

        });

        encrypted_data = easyassist_custom_encrypt(json_string);

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
    json_string = JSON.stringify({
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

function easyassist_sync_agent_chat(data_packet) {
    try {
        if(data_packet.chat_type != "chat_bubble")
            easyassist_show_livechat_iframe();
        let chat_message = JSON.stringify(data_packet);
        allincall_chat_window = document.getElementById("easyassist-livechat-iframe").contentWindow;
        allincall_chat_window.postMessage(JSON.stringify({
            "agent_name": data_packet.agent_name,
            "message": data_packet.message,
            "attachment": data_packet.attachment,
            "attachment_file_name": data_packet.attachment_file_name,
            "show_agent_message": true,
            "chat_type": data_packet.chat_type,
        }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);
    } catch(err){
        console.log("easyassist_sync_agent_chat: ", err);
    }
}

function easyassist_sync_typing_loader(data_packet) {
    try {
        allincall_chat_window = document.getElementById("easyassist-livechat-iframe").contentWindow;
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
        allincall_chat_window = document.getElementById("easyassist-livechat-iframe").contentWindow;
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

function easyassist_send_data_to_server(event) {

    try {
        if(event.type == "click") {
            if(easyassist_check_weak_connection_enabled()) {
                setTimeout(function() {
                    var html_elements_value_list = easyassist_get_input_element();
                    if(html_elements_value_list.length != easyassist_total_input_elements) {
                        easyassist_sync_html_data();
                    }
                }, 1000);
            }

        } else if (event.type == "scroll") {
            easyassist_sync_scroll_position();
        } else if (event.type == "resize") {
            easyassist_sync_html_data();
        } else {
            let tag_name = document.activeElement.tagName;
            if (tag_name.toLowerCase() == "input") {
                easyassist_sync_html_element_value_change();
            } else if (tag_name.toLowerCase() == "select") {
                easyassist_sync_html_element_value_change();
            } else if (tag_name.toLowerCase() == "textarea") {
                easyassist_sync_html_element_value_change();
            } else {
                //console.log("active element tag: ", tag_name);
            }
        }

        if(event.target.id == "easyassist-ripple_effect") {
            easyassist_hide_ripple_effect();
        }
    } catch(err) {
        console.log("easyassist_send_data_to_server: ", err);
    }
}

function easyassist_sync_html_data() {

    try {
        if(EASYASSIST_COBROWSE_META.allow_screen_sharing_cobrowse) {
            return;
        }

        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

        if (easyassist_session_id == null || easyassist_session_id == undefined) {
            return;
        }

        var allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;

        if (allow_cobrowsing == false) {
            return;
        }

        var screenshot = easyassist_screenshot_page();

        //screenshot = EasyAssistLZString.compress(screenshot);

        json_string = JSON.stringify({
            "type": "html",
            "window_width": window.innerWidth,
            "window_height": window.innerHeight,
            "page": html_page_counter,
            "is_chunk": false,
            "html": screenshot,
            "id": EASYASSIST_SESSION_ID,
            "active_url": window.location.href
        });

        let is_encrypted = false;
        encrypted_data = json_string;

        if (is_encrypted == true) {
            encrypted_data = easyassist_custom_encrypt(json_string);
        }

        encrypted_data = {
            "is_encrypted": is_encrypted,
            "html_page_counter": html_page_counter,
            "Request": encrypted_data
        };

        easyassist_send_message_over_socket(encrypted_data, "client");

        html_page_counter += 1;
    } catch(err) {
        console.log("easyassist_sync_html_data: ", err);
    }
}

function easyassist_send_html_request_received_message_over_socket() {
    try {
        json_string = JSON.stringify({
            "type": "html_request_received",
        });

        encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
    } catch(err) {
        console.log(err);
    }
}

function easyassist_sync_html_node(dom_node, node_visited_status) {

    try {
        var easyassist_element_id = dom_node.getAttribute("easyassist-element-id");

        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

        if (easyassist_session_id == null || easyassist_session_id == undefined) {
            return;
        }
        var is_obfuscated = dom_node.getAttribute("easyassist-obfuscate");
        var element_text = dom_node.innerText;
        if (node_visited_status == "text_change") {
            if (is_obfuscated == "partial-masking" || is_obfuscated == "full-masking")
                element_text = easyassist_obfuscate(dom_node.innerText, is_obfuscated);
            else
                element_text = dom_node.innerText;

        }
        if (element_text) {
            element_text = element_text.trim();
        }

        json_string = JSON.stringify({
            "type": "sync-node",
            "easyassist_element_id": easyassist_element_id,
            "style": dom_node.getAttribute('style'),
            "class": dom_node.className,
            "node_visited_status": node_visited_status,
            "text": element_text,
            "src": dom_node.src,
            "disabled": dom_node.disabled,
        });

        encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        easyassist_send_message_over_socket(encrypted_data, "client");

        easyassist_sync_html_element_value_change();
    } catch(err) {
        console.log("easyassist_sync_html_node: ", err);
    }
}

function easyassist_sync_removed_html_node(element_ids) {

    try {
        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

        if (easyassist_session_id == null || easyassist_session_id == undefined) {
            return;
        }

        json_string = JSON.stringify({
            "type": "sync-removed-node",
            "element_ids": element_ids
        });

        encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        easyassist_send_message_over_socket(encrypted_data, "client");
    } catch(err) {
        console.log("easyassist_sync_removed_html_node: ", err);
    }
}

function easyassist_sync_new_html_node(parent_node, child_node, element_index) {

    try {
        var parent_element_id = parent_node.getAttribute('easyassist-element-id');

        if (easyassist_session_id == null || easyassist_session_id == undefined) {
            return;
        }
        var is_obfuscated = child_node.getAttribute("easyassist-obfuscate");
        var child_clone_node = child_node.cloneNode(true);
        if (is_obfuscated == "partial-masking" || is_obfuscated == "full-masking") {
            easyassist_obfuscate_data_using_recursion(child_clone_node);
        }
        var child_element_id = child_node.getAttribute('easyassist-element-id');
        var child_list = [];
        for(let idx = 0; idx < parent_node.children.length; idx++) {
            child_list.push(parent_node.children[idx].getAttribute('easyassist-element-id'));
        }

        var parent_node_text = "";
        if (child_list.length == 1) {
            try {
                for(let idx = 0; idx < parent_node.childNodes.length; idx++) {
                    if (parent_node.childNodes[idx].nodeType == Node.TEXT_NODE) {
                        parent_node_text += parent_node.childNodes[idx].textContent.trim();
                    }
                }
            } catch (err) {
                console.log("new node " + err);
            }
        }
        if (child_clone_node.tagName == "link") {
            easyassist_convert_urls_to_absolute([child_clone_node]);
        }

        json_string = JSON.stringify({
            "type": "sync-new-node",
            "parent_element_id": parent_element_id,
            "child_element_id": child_element_id,
            "child_html": child_clone_node.outerHTML,
            "child_index": element_index,
            "child_list": child_list,
            "parent_text_length": parent_node_text.length
        });

        encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        easyassist_send_message_over_socket(encrypted_data, "client");
    } catch(err) {
        console.log("easyassist_sync_new_html_node: ", err);
    }
}

function easyassist_sync_scroll_position() {

    try {

        if (get_easyassist_cookie("easyassist_edit_access") == "true") {
            return;
        }

        if(easyassist_check_weak_connection_enabled()) {
            return;
        }

        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

        if (easyassist_session_id == null || easyassist_session_id == undefined) {
            return;
        }

        json_string = JSON.stringify({
            "type": "scroll",
            "active_url": window.location.href,
            "data_scroll_x": window.scrollX,
            "data_scroll_y": window.scrollY
        });

        encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        easyassist_send_message_over_socket(encrypted_data, "client");
    } catch(err) {
        console.log("easyassist_sync_scroll_position: ", err);
    }
}

function easyassist_sync_scroll_position_inside_div(event) {
    try {

        if(easyassist_check_weak_connection_enabled()) {
            return;
        }

        if (get_easyassist_cookie("easyassist_edit_access") == "true") {
            return;
        }
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

        easyassist_send_message_over_socket(encrypted_data, "client");
    } catch (err) {
        console.log("easyassist_sync_scroll_position_inside_div: ", err);
    }
}

function easyassist_sync_html_element_value_change() {

    try {
        var active_element = document.activeElement;

        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

        if (easyassist_session_id == null || easyassist_session_id == undefined) {
            return;
        }

        var allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;

        if (allow_cobrowsing == false) {
            return;
        }

        // tag_name_list = ["span", "label", "input", "select", "textarea"];
        let tag_name_list = ["input", "select", "textarea"];

        var html_elements_value_list = [];

        for(let tag_index = 0; tag_index < tag_name_list.length; tag_index++) {

            let tag_elements = document.getElementsByTagName(tag_name_list[tag_index]);

            for(let tag_element_index = 0; tag_element_index < tag_elements.length; tag_element_index++) {

                tag_name = tag_elements[tag_element_index].tagName;
                let element_id = tag_elements[tag_element_index].getAttribute("easyassist-element-id");
                let tag_type = tag_elements[tag_element_index].getAttribute("type");
                let value = tag_elements[tag_element_index].value;

                if(tag_name.toLowerCase() != "select" && tag_type != 'checkbox' && tag_type != 'radio') {
                    if (tag_elements[tag_element_index].offsetParent == null) {
                        continue;
                    }
                }

                if (tag_name.toLowerCase() == "select") {
                    var selected_option = tag_elements[tag_element_index].options[tag_elements[tag_element_index].selectedIndex];
                    if (selected_option != null && selected_option != undefined) {
                        var selected_option_inner_html = selected_option.innerHTML;
                        // var selected_option_value = selected_option.value;
                        value = selected_option_inner_html;
                    }
                } else if (tag_name.toLowerCase() == "label") {
                    let label_id = tag_elements[tag_element_index].getAttribute("id");
                    if (label_id == undefined || label_id == null) {
                        continue
                    }

                    value = tag_elements[tag_element_index].innerHTML;
                } else if (tag_name.toLowerCase() == "span") {
                    let span_id = tag_elements[tag_element_index].getAttribute("id");
                    if (span_id == undefined || span_id == null) {
                        continue
                    }

                    value = tag_elements[tag_element_index].innerHTML;
                }

                if (tag_type == "checkbox" || tag_type == "radio") {
                    value = tag_elements[tag_element_index].checked;
                }

                let is_active = false;
                if (active_element == tag_elements[tag_element_index]) {
                    is_active = true;
                }

                let is_obfuscated_element = easyassist_obfuscated_element_check(tag_elements[tag_element_index]);
                var is_numeric = false;
                if (is_obfuscated_element[0] == false && isNaN(parseInt(value.toString())) == false) {
                    is_numeric = true;
                }

                if (is_obfuscated_element[0]) {
                    value = easyassist_obfuscate(value.toString(), is_obfuscated_element[1].toString());
                }
                if (is_numeric) {
                    value = easyassist_obfuscate(value.toString());
                }

                html_elements_value_list.push({
                    "tag_type": tag_type,
                    "tag_name": tag_name,
                    "easyassist_element_id": element_id,
                    "value": value,
                    "is_active": is_active,
                    "is_obfuscated_element": is_obfuscated_element[0]
                });
            }
        }

        json_string = JSON.stringify({
            "type": "element_value",
            "active_url": window.location.href,
            "html_elements_value_list": html_elements_value_list
        })

        encrypted_data = easyassist_custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };

        easyassist_send_message_over_socket(encrypted_data, "client");
    } catch(err) {
        console.log("easyassist_sync_html_element_value_change: ", err);
    }
}

function easyassist_sync_mouse_position(event) {

    try {

        if(easyassist_check_weak_connection_enabled()) {
            return;
        }

        json_string = JSON.stringify({
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

        encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
    } catch(err) {
        console.log("easyassist_sync_mouse_position: ", err);
    }
}

function easyassist_sync_client_scroll_position(agent_packet) {

    try {
        var scrollX = agent_packet.data_scroll_x;
        var scrollY = agent_packet.data_scroll_y;
        window.scrollTo(scrollX, scrollY);
    } catch(err) {
        console.log("easyassist_sync_client_scroll_position: ", err);
    }

}

function easyassist_sync_agent_highlight(data_packet) {

    try {
        var edit_access = get_easyassist_cookie("easyassist_edit_access");
        edit_access = edit_access ? edit_access : "false";
        let clientX = data_packet.position.clientX;
        let clientY = data_packet.position.clientY;

        let pageX = data_packet.position.pageX;
        let pageY = data_packet.position.pageY;

        let agent_window_x_offset = data_packet.position.agent_window_x_offset;
        let agent_window_y_offset = data_packet.position.agent_window_y_offset;

        window.scrollTo(agent_window_x_offset, agent_window_y_offset);

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

function easyassist_agent_sync_form(data_packet) {
    try {

        tag_name = data_packet.tag_name;
        tag_type = data_packet.tag_type;
        element_id = data_packet.easyassist_element_id;
        value = data_packet.value;
        let query_selector = tag_name + "[easyassist-element-id='" + element_id + "']";
        let change_element = document.querySelector(query_selector);

        if (tag_name == "select") {

            if (change_element.options == undefined || change_element.options == null) {
                return;
            }

            remove_easyassist_event_listner_into_element(change_element, "change", easyassist_sync_html_element_value_change);

            var option_value = value;
            for(let option_index = 0; option_index < change_element.options.length; option_index++) {
                change_element.options[option_index].removeAttribute("selected");
                if (change_element.options[option_index].innerHTML == value || change_element.options[option_index].value == value) {
                    change_element.options[option_index].setAttribute("selected", "selected");
                    option_value = change_element.options[option_index].value;
                } 
            }

            change_element.value = option_value;
            var change_event = new Event('change');
            change_element.dispatchEvent(change_event);

            add_easyassist_event_listner_into_element(change_element, "change", easyassist_sync_html_element_value_change);

        } else if (tag_name == "input") {

            remove_easyassist_event_listner_into_element(change_element, "change", easyassist_sync_html_element_value_change);

            if (tag_type == "checkbox") {
                change_element.click();
            } else if (tag_type == "radio") {
                change_element.click();
            } else {
                change_element.value = value;
                change_element.dispatchEvent(new Event("change"));
                change_element.focus();
            }

            add_easyassist_event_listner_into_element(change_element, "change", easyassist_sync_html_element_value_change);

        } else if (tag_name == "textarea") {
            change_element.value = value;

        } else {
            change_element.innerHTML = value;

        }
    } catch(err){
        console.log("easyassist_agent_sync_form: ", err);
    }
}

function easyassist_sync_button_click_event(data_packet){
    try {

        var easyassist_element_id = data_packet.easyassist_element_id;
        var click_element = null;

        if (data_packet.element_id != "") {
            click_element = document.getElementById(data_packet.element_id);
        }

        if (click_element == null && easyassist_element_id != "") {
            click_element = document.querySelector('[easyassist-element-id="' + easyassist_element_id + '"]');
        }

        if(click_element == null || click_element == undefined) {
            return;
        }

        if(click_element.tagName.toLowerCase() == "input") {
            remove_easyassist_event_listner_into_element(click_element, "change", easyassist_sync_html_element_value_change);
        }

        click_element.click();

        if(click_element.tagName.toLowerCase() == "input") {
            add_easyassist_event_listner_into_element(click_element, "change", easyassist_sync_html_element_value_change);
        }
    } catch(err){
        console.log("easyassist_sync_button_click_event: ", err);
    }
}


function easyassist_sync_agent_div_scroll(data_packet){
    try {

        let value_top = data_packet.value_top;
        let value_left = data_packet.value_left;
        element_id = data_packet.element_id;
        let element_attr_id = data_packet.id;
        element = null;
        if (element_attr_id != null && element_attr_id != undefined) {
            element = document.getElementById(element_attr_id);
        } else {
            element = document.querySelector("[easyassist-element-id='" + element_id + "']")
        }
        element.scrollTop = value_top;
        element.scrollLeft = value_left;
    } catch(err){
        console.log("easyassist_sync_agent_div_scroll: ", err);
    }
}

/******************************* MEETING + VOIP MEETING *******************************************/

if(EASYASSIST_COBROWSE_META.allow_video_meeting_only == true){
    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if(easyassist_session_id != "" || easyassist_session_id != null || easyassist_session_id != undefined){
        let is_cobrowsing_meeting = setInterval(function(){
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

    json_string = JSON.stringify({
        "session_id": easyassist_session_id,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
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
            response = JSON.parse(this.responseText);
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

    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

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
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/update-agent-meeting-request/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
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
    var url = EASYASSIST_COBROWSE_META.easyassist_host + "/easy-assist/meeting/" + session_id + "?is_meeting_cobrowsing=true"
    window.open(url, "_blank");
}

function easyassist_open_voip_meeting_window() {
    set_easyassist_cookie("is_cobrowse_meeting_on", "true");
    var session_id = get_easyassist_cookie("easyassist_session_id")
    var url = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/client-cobrowse-meeting/" + session_id;
    window.open(url, "_blank");
}


function easyassist_show_cobrowse_meeting_option() {
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
        cobrowse_meeting_window = cobrowse_meeting_iframe.contentWindow;
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
        if(EASYASSIST_COBROWSE_META.enable_voip_calling) {
            return;
        }

        var cobrowse_meeting_id = get_easyassist_cookie("cobrowse_meeting_id");
        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
        if (cobrowse_meeting_id != easyassist_session_id) {
            return;
        }
        document.getElementById("easyassist-cobrowse-meeting-iframe-container").style.display = 'none';
        var cobrowse_meeting_iframe = document.getElementById("easyassist-cobrowse-meeting-iframe-container").children[0];
        cobrowse_meeting_window = cobrowse_meeting_iframe.contentWindow;
        cobrowse_meeting_window.postMessage(JSON.stringify({
            "message": "end_meeting",
            "name": window.CLIENT_NAME
        }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);
        easyassist_send_end_meeting_messsage_over_socket(auto_end_meeting)
    } catch (err) {
        console.log(err)
    }
}

function easyassist_reset_voip_meeting() {
    set_easyassist_cookie("cobrowse_meeting_id", "");
    delete_easyassist_cookie("is_meeting_audio_muted");
    delete_easyassist_cookie("is_agent_voip_meeting_joined");
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

    json_string = JSON.stringify({
        "type": "end_voip_meeting",
        "auto_end_meeting": auto_end_meeting,
    });

    encrypted_data = easyassist_custom_encrypt(json_string)
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

    json_string = JSON.stringify({
        "type": "voip_meeting_joined",
    });

    encrypted_data = easyassist_custom_encrypt(json_string)
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

    json_string = JSON.stringify({
        "type": "voip_meeting_ready",
    });

    encrypted_data = easyassist_custom_encrypt(json_string)
    encrypted_data = {
        "Request": encrypted_data
    };

    easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
}

function easyassist_end_voip_meeting(data_packet){
    try{
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

    json_string = JSON.stringify({
        "type": "client_weak_connection",
    });

    encrypted_data = easyassist_custom_encrypt(json_string)
    encrypted_data = {
        "Request": encrypted_data
    };

    easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
}

easyassist_start_cobrowsing_activity_check();
