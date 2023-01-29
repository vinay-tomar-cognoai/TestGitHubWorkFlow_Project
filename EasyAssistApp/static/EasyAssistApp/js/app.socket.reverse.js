var easyassist_send_client_weak_connection_message_interval = null;
var AGENT_NAME = "";
var EASYASSIST_SESSION_ID = null;
var check_for_agent_assistance = null;
var client_heartbeat_timer = null;
var is_agent_connected = false;
var hidden_element_count = null;
var EASYASSIST_TAG_LIST = ["input", "select", "textarea", "div", "span", "label"];
var check_for_agent_guide_timer = null;
var html_page_counter = 0;
var session_closed_by_agent = false;
var is_cobrowse_meeting_on = false;
var agent_mouse_top = 0;
var agent_mouse_left = 0;
var agent_revoke_edit_access = false;
var cobrowsing_meta_data_page = 1;
var load_more_meta = false;

var client_websocket = null;
var client_websocket_open = false;
var sync_utils_client_websocket_open = null;
var sync_utils_client_websocket = null;
var packet_counter = 0;

var easyassist_speed_mbps = 0;
var easyassist_internet_iteration = 3;
var internet_connectivity_timer = null;
var INTERNET_CON_TIMER = 30000;
var check_cobrowse_session_timer = null;
var easyassist_selected_invite_agent_id=null;

window.AGENT_NAME = '';
window.AGENT_USERNAME = '';

function start_cobrowsing_activity_check() {
    if(check_cobrowse_session_timer != null){
        return;
    }
    check_cobrowse_session_timer = setInterval(function(e) {
        if (get_easyassist_cookie("easyassist_session_id") != undefined) {
            clearInterval(check_cobrowse_session_timer);
            check_cobrowse_session_timer = null;
            EASYASSIST_SESSION_ID = get_easyassist_cookie("easyassist_session_id");
            initiate_cobrowsing();
        }
    }, 1000);
}

/*WebSocket Utilities - Starts*/

function reset_easyassist_global_var() {
    try{
        EASYASSIST_SESSION_ID = null;
        check_for_agent_assistance = null;
        client_heartbeat_timer = null;
        is_agent_connected = false;
        hidden_element_count = null;
        session_closed_by_agent = false;
    }catch(err){}
}

function easyassist_create_socket(jid, sender) {
    ws_scheme = EASYASSIST_HOST_PROTOCOL == "http" ? "ws" : "wss"
    url = ws_scheme + '://' + EASYASSIST_COBROWSE_HOST + '/ws/cobrowse/' + jid + '/' + sender + "/";
    if (client_websocket == null) {
        client_websocket = new WebSocket(url);
        client_websocket.onmessage = check_for_agent_guide;
        client_websocket.onerror = function(e){
                console.error("WebSocket error observed:", e);
                client_websocket_open = false;
                easyassist_close_socket();
            }
        client_websocket.onopen = function(){
                client_websocket_open = true; 
                console.log("client_websocket created successfully") 
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
        client_websocket_open.onmessage = null;
        client_websocket_open = null;
    }

}

function easyassist_send_message_over_socket(message, sender) {
    try{
        var allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;

        if (allow_cobrowsing == false) {
            return;
        }

        var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
        if(easyassist_session_id == undefined || easyassist_session_id == null){
            return;
        }

        if(client_websocket_open == false || client_websocket == null){
            if(easyassist_send_message_over_socket.caller.name == "easyassist_socket_callback"){
                return;
            }
            setTimeout(function easyassist_socket_callback(){
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
        sync_utils_client_websocket.onmessage = check_for_agent_guide;
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

        var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
        if(easyassist_session_id == undefined || easyassist_session_id == null){
            return;
        }

        if(sync_utils_client_websocket_open == false || sync_utils_client_websocket == null){
            if(easyassist_send_message_over_sync_utils_socket.caller.name == "easyassist_socket_callback"){
                return;
            }
            setTimeout(function easyassist_socket_callback(){
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

function easyassist_initialize_web_socket() {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        if(check_cobrowse_session_timer == null){
            start_cobrowsing_activity_check();
        }
        return;
    }

    var allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;
    if (allow_cobrowsing == false) {
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

function easyassist_delete_all_cookie(){
    delete_easyassist_cookie("easyassist_session_id");
    delete_easyassist_cookie("easyassist_agent_connected");
    delete_easyassist_cookie("easyassist_cobrowsing_allowed");
    delete_easyassist_cookie("easyassist_edit_access");
    delete_easyassist_cookie("easyassist_customer_id");
    delete_easyassist_cookie("cobrowse_meeting_id");
    delete_easyassist_cookie("is_lead_converted");
    delete_easyassist_cookie("easyassist_client_disconnected_modal_shown");
    delete_easyassist_cookie("easyassist_client_weak_internet_connection_shown");
    delete_easyassist_cookie("easyassist_agent_weak_internet_connection_shown");
    delete_easyassist_cookie("easyassist_agent_disconnected_modal_shown");
    delete_easyassist_cookie("is_cobrowse_meeting_on");
    delete_easyassist_cookie("ea_cust_connected");
}

function terminate_easyassist_cobrowsing_session() {

    try{
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
            if(parse_dom_tree_interval != null && parse_dom_tree_interval != undefined) {
                clearInterval(parse_dom_tree_interval);
            }
            if (client_heartbeat_timer != null && client_heartbeat_timer != undefined) {
                clearInterval(client_heartbeat_timer);
            }
            if(easyassist_send_client_weak_connection_message_interval != null &&
                easyassist_send_client_weak_connection_message_interval != undefined){
                clearInterval(easyassist_send_client_weak_connection_message_interval);
            }
            if (check_for_agent_guide_timer != null && check_for_agent_guide_timer != undefined) {
                clearInterval(check_for_agent_guide_timer);
            }
        } catch(err) {
            console.log(err);
        }

        remove_easyassist_blur_fields();
        end_cobrowse_video_meet();
        easyassist_delete_all_cookie();
        easyassist_close_socket();
        easyassist_close_sync_utils_socket();
        show_floating_sidenav_easyassist_button();
        hide_floating_sidenav_menu();
        hide_easyassist_feedback_form();
        reset_easyassist_global_var();
        hide_easyassist_livechat_iframe();
        refresh_easyassist_livechat_iframe();
        add_easyassist_formassist_stuck_timer_handler();

        if(document.getElementById("agent-mouse-pointer")){
            document.getElementById("agent-mouse-pointer").style.display = "none";
        }

        try {
            toggle_voip_ringing_sound();
        } catch(err) {}

        if(document.getElementById('report_problem_icon')){
            document.getElementById('report_problem_icon').style.display = "";
        }

        show_easyassist_toast("Session has ended.");
    }catch(err){
        easyassist_delete_all_cookie();
        console.error("Error on termination", err)
    }
}

function sync_html_data() {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    var allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;

    if (allow_cobrowsing == false) {
        return;
    }

    var screenshot = screenshot_page();

    // screenshot = EasyAssistLZString.compress(screenshot);

    // hidden_element_count = count_hidden_element_in_document(EASYASSIST_TAG_LIST);

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

    is_encrypted = false;
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
}

function sync_current_html_value(dom_node, node_visited_status) {

    var easyassist_element_id = dom_node.getAttribute("easyassist-element-id");

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }
    var is_obfuscated = dom_node.getAttribute("easyassist-obfuscate");
    var element_text = dom_node.innerText;
    if(node_visited_status == "text_change") {
        if(is_obfuscated == "partial-masking" || is_obfuscated == "full-masking")
            element_text = easyassist_obfuscate(dom_node.innerText, is_obfuscated);
        else
            element_text = dom_node.innerText;
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

    sync_html_element_value_change();
}

function sync_removed_html_node(element_ids) {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

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
}

function sync_new_html_node(parent_node, child_node, element_index) {

    var parent_element_id = parent_node.getAttribute('easyassist-element-id');

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }
    var is_obfuscated = child_node.getAttribute("easyassist-obfuscate");
    var child_clone_node = child_node.cloneNode(true);
    if(is_obfuscated == "partial-masking" || is_obfuscated == "full-masking") {
        obfuscate_data_using_recursion(child_clone_node);
    }
    var child_element_id = child_node.getAttribute('easyassist-element-id');
    var child_list = [];
    for(idx = 0; idx < parent_node.children.length; idx ++) {
        child_list.push(parent_node.children[idx].getAttribute('easyassist-element-id'));
    }

    if(child_clone_node.tagName == "link") {
        convert_urls_to_absolute([child_clone_node]);
    }

    json_string = JSON.stringify({
        "type": "sync-new-node",
        "parent_element_id": parent_element_id,
        "child_element_id": child_element_id,
        "child_html": child_clone_node.outerHTML,
        "child_index": element_index,
        "child_list": child_list,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    easyassist_send_message_over_socket(encrypted_data, "client");
}

function send_livechat_message_to_agent(message, attachment, attachment_file_name) {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    json_string = JSON.stringify({
        "type": "chat",
        "message": message,
        "attachment": attachment,
        "attachment_file_name": attachment_file_name,
        "name": window.AGENT_NAME,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
}


function sync_scroll_position() {

    if(get_easyassist_cookie("easyassist_edit_access") == "true") {
        return;
    }
    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }
    // document.getElementById("agent-mouse-pointer").style.top = window.scrollY+ agent_mouse_top + "px" ;
    // document.getElementById("agent-mouse-pointer").style.left = window.scrollX + agent_mouse_left + "px";
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
}

function sync_scroll_position_inside_div(event) {
    try {
        if(get_easyassist_cookie("easyassist_edit_access") == "true") {
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
    } catch(err) {}
}

function sync_html_element_value_change() {

    var active_element = document.activeElement;

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    var allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;

    if (allow_cobrowsing == false){
        return;
    }

    // tag_name_list = ["span", "label", "input", "select", "textarea"];
    tag_name_list = ["input", "select", "textarea"];

    var html_elements_value_list = [];

    for(let tag_index = 0; tag_index < tag_name_list.length; tag_index++) {

        tag_elements = document.getElementsByTagName(tag_name_list[tag_index]);

        for(let tag_element_index = 0; tag_element_index < tag_elements.length; tag_element_index++) {

            tag_name = tag_elements[tag_element_index].tagName;
            element_id = tag_elements[tag_element_index].getAttribute("easyassist-element-id");
            tag_type = tag_elements[tag_element_index].getAttribute("type");
            value = tag_elements[tag_element_index].value;

            if (tag_type != 'checkbox' && tag_type != 'radio' && tag_elements[tag_element_index].offsetParent == null) {
                continue;
            }

            if (tag_name.toLowerCase() == "select") {
                var selected_option = tag_elements[tag_element_index].options[tag_elements[tag_element_index].selectedIndex];
                if (selected_option != null && selected_option != undefined) {
                    var selected_option_inner_html = selected_option.innerHTML;
                    value = selected_option_inner_html;
                }
            } else if (tag_name.toLowerCase() == "label") {
                label_id = tag_elements[tag_element_index].getAttribute("id");
                if (label_id == undefined || label_id == null) {
                    continue
                }

                value = tag_elements[tag_element_index].innerHTML;
            } else if (tag_name.toLowerCase() == "span") {
                span_id = tag_elements[tag_element_index].getAttribute("id");
                if (span_id == undefined || span_id == null) {
                    continue
                }

                value = tag_elements[tag_element_index].innerHTML;
            }

            if (tag_type == "checkbox" || tag_type == "radio") {
                value = tag_elements[tag_element_index].checked;
            }

            is_active = false;
            if (active_element == tag_elements[tag_element_index]) {
                is_active = true;
            }

            is_obfuscated_element = is_this_obfuscated_element(tag_elements[tag_element_index]);

            var is_numeric = false;
            if (is_obfuscated_element == false && isNaN(parseInt(value.toString())) == false) {
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
                "is_obfuscated_element": is_obfuscated_element
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
}

function send_data_to_server(event) {

    hide_easyassist_ripple_effect();

    if (event.type == "scroll") {
        sync_scroll_position();
    } else if (event.type == "resize") {
        sync_html_data();
    } else {
        tag_name = document.activeElement.tagName;
        if (tag_name.toLowerCase() == "input") {
            sync_html_element_value_change();
        } else if (tag_name.toLowerCase() == "select") {
            sync_html_element_value_change();
        } else if (tag_name.toLowerCase() == "textarea") {
            sync_html_element_value_change();
        } else {
            //console.log("active element tag: ", tag_name);
        }
    }
}

function sync_mouse_position(event) {

    json_string = JSON.stringify({
        "type": "mouse",
        "position":{
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
}


function client_heartbeat() {

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

function sync_client_scroll_position(agent_packet){

    var scrollX = agent_packet.data_scroll_x;
    var scrollY = agent_packet.data_scroll_y;
    window.scrollTo(scrollX, scrollY);
    
}
function check_for_agent_guide(e) {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    var data = JSON.parse(e.data);
    message = data.message;
    agent_packet = message.body.Request;

    if (message.body.is_encrypted == false) {
        agent_packet = JSON.parse(agent_packet);
    } else {
        agent_packet = easyassist_custom_decrypt(agent_packet);
        agent_packet = JSON.parse(agent_packet);
    }

    if (message.header.sender == "agent") {

        easyassist_reset_internet_connectivity_check_timer();

        // agent has requested to highlight given element
          if (agent_packet.type == "highlight"){
            var edit_access = get_easyassist_cookie("easyassist_edit_access");
            edit_access  = edit_access?edit_access:"false";
            clientX = agent_packet.position.clientX;
            clientY = agent_packet.position.clientY;

            pageX = agent_packet.position.pageX;
            pageY = agent_packet.position.pageY;

            agent_window_x_offset = agent_packet.position.agent_window_x_offset;
            agent_window_y_offset = agent_packet.position.agent_window_y_offset;

            window.scrollTo(agent_window_x_offset, agent_window_y_offset);

            agent_window_width = agent_packet.position.agent_window_width;
            agent_window_height = agent_packet.position.agent_window_height;

            screen_width = agent_packet.position.screen_width;
            screen_height = agent_packet.position.screen_height;

            clientX = (clientX * window.innerWidth) / (agent_window_width);
            clientY = (clientY * window.innerHeight) / (agent_window_height);

            pageX = (pageX * window.outerWidth) / (agent_window_width);
            pageY = (pageY * window.outerHeight) / (agent_window_height);

            if(edit_access == "false")
                show_easyassist_ripple_effect(clientX, clientY);

            // agent has requested to take screenshot
        } else if (agent_packet.type == "screenshot") {

            capture_client_screenshot();

            // agent has requested to take pageshot
        } else if (agent_packet.type == "pageshot") {

            capture_client_pageshot();

        } else if (agent_packet.type == "html") {

            sync_html_data();

        } else if (agent_packet.type == "sync-scroll") {

            sync_client_scroll_position(agent_packet);
        } else if (agent_packet.type == "mouse") {
            document.getElementById("agent-mouse-pointer").style.display = "inline-block";
            agent_mouse_top = agent_packet.position.clientY;
            agent_mouse_left = agent_packet.position.clientX;
            document.getElementById("agent-mouse-pointer").style.top = agent_packet.position.clientY + window.scrollY + "px";
            document.getElementById("agent-mouse-pointer").style.left = agent_packet.position.clientX + window.scrollX +"px";

        } else if (agent_packet.type == "chat") {
            show_easyassist_livechat_iframe();
            chat_message = JSON.stringify(agent_packet);
            allincall_chat_window = document.getElementById("easyassist-livechat-iframe").contentWindow;
            allincall_chat_window.postMessage(JSON.stringify({
                "agent_name": agent_packet.agent_name,
                "message": agent_packet.message,
                "attachment": agent_packet.attachment,
                "attachment_file_name": agent_packet.attachment_file_name,
                "show_agent_message": true,
                "sender": agent_packet.sender,
            }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);

        } else if (agent_packet.type == "request-edit-access") {

            show_easyassist_request_edit_access_form();

        } else if (agent_packet.type == "revoke-edit-access") {
            agent_revoke_edit_access = true;
            revoke_easyassist_edit_access();

        } else if (agent_packet.type == "sync-form") {

            tag_name = agent_packet.tag_name;
            tag_type = agent_packet.tag_type;
            element_id = agent_packet.easyassist_element_id;
            value = agent_packet.value;
            query_selector = tag_name + "[easyassist-element-id='" + element_id + "']";
            change_element = document.querySelector(query_selector);

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

                remove_event_listner_into_element(change_element, "change", sync_html_element_value_change);

                if (tag_type == "checkbox") {
                    change_element.click();
                } else if (tag_type == "radio") {
                    change_element.click();
                } else {
                    change_element.value = value;
                }

                add_event_listner_into_element(change_element, "change", sync_html_element_value_change);

            } else if(tag_name == "textarea") {
                change_element.value = value;

            } else {
                change_element.innerHTML = value;

            }
        } else if (agent_packet.type == "button-click") {
            easyassist_element_id = agent_packet.easyassist_element_id;
            if (agent_packet.element_id != "") {
                click_element = document.getElementById(agent_packet.element_id);
                if (click_element != null && click_element != undefined) 
                    click_element.click();
            }
            else if (easyassist_element_id != "") {
                click_element = document.querySelector('[easyassist-element-id="' + easyassist_element_id + '"]');
                if (click_element != null && click_element != undefined) 
                    click_element.click();
            }
        } else if(agent_packet.type == "end_voip_meeting") {
            if(agent_packet.auto_end_meeting) {
                show_easyassist_toast("Call ended");
            } else {
                show_easyassist_toast("Customer ended the call");
            }
            setTimeout(function() {
                end_cobrowse_video_meet(true);
            }, 1000);
        } else if(agent_packet.type == "voip_meeting_ready") {
            show_easyassist_toast("Customer joined the call");
            set_easyassist_cookie("is_agent_voip_meeting_joined", get_easyassist_cookie("easyassist_session_id"));
        }  else if(agent_packet.type == "customer_joined") {
            actions_after_connected_successfully();
        } else if (agent_packet.type == "livechat-typing") {
            easyassist_set_livechat_typing(agent_packet.name, agent_packet.role)
        } else if (agent_packet.type == "agent_weak_connection") {
            if(get_easyassist_cookie("easyassist_session_id")){
                if(get_easyassist_cookie("easyassist_agent_weak_internet_connection_shown") == undefined || get_easyassist_cookie("easyassist_agent_weak_internet_connection_shown") == "false"){
                    easyassist_show_agent_weak_internet_connection();
                    set_easyassist_cookie("easyassist_agent_weak_internet_connection_shown", "true")
                }
            }
        } else if (agent_packet.type == "invited_agent_joined"){
            show_easyassist_toast("Agent " + agent_packet.invited_agent_name + " has joined the session.")
        }  else if (agent_packet.type == "invited_agent_left"){
            show_easyassist_toast("Agent " + agent_packet.invited_agent_name + " has left the session.")
        } else if (agent_packet.type == "div-scroll") {
            easyassist_sync_agent_div_scroll(agent_packet);
        }
    } else {

        return;

    }
}

function easyassist_sync_agent_div_scroll(data_packet){
    try {

        value_top = data_packet.value_top;
        value_left = data_packet.value_left;
        element_id = data_packet.element_id;
        element_attr_id = data_packet.id;
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

function initiate_cobrowsing() {
    try {
        easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
        if (easyassist_session_id != undefined && EASYASSIST_SESSION_ID != null) {
            hide_floating_sidenav_easyassist_button();
            load_chat_history();

            window.onclick = send_data_to_server;
            window.onresize = send_data_to_server;
            window.onmousedown = send_data_to_server;
            window.onkeyup = send_data_to_server;
            window.onscroll = send_data_to_server;
            window.onmousemove = function(event) {
                sync_mouse_position(event);
            }

            // $("#easyassist-livechat-iframe")[0].contentWindow.document.onmousemove = function(event) {
            //    sync_mouse_position(event, is_from_chat_window=true);
            // }

            client_heartbeat_timer = setInterval(function(e) {
                client_heartbeat();
            }, 5000);

            check_for_agent_guide_timer = setInterval(function(e) {
                check_for_agent_highlight();
            }, EASYASSIST_COBROWSE_META.highlight_api_call_frequency * 1000);

            check_for_agent_highlight();

            if(EASYASSIST_COBROWSE_META.allow_agent_to_screen_record_customer_cobrowsing == true){
                startRecording();
            }
            easyassist_initiate_internet_speed_detection();
            if(document.getElementById('report_problem_icon')){
                document.getElementById('report_problem_icon').style.display = "";
            }
        }
    } catch(err) {
        console.log(err);
        setTimeout(function() {
            initiate_cobrowsing();
        }, 1000);
    }
}

var global_element_stuck_timer = null;

function start_easyassist_element_stuck_timer() {
    if (EASYASSIST_COBROWSE_META.agents_available == false) {
        return;
    }
    global_element_stuck_timer = setTimeout(function(e) {
        if (get_easyassist_cookie("easyassist_session_id") != undefined) {
            return;
        }

        if (EASYASSIST_COBROWSE_META.field_recursive_stuck_event_check == false) {
            remove_easyassist_formassist_stuck_timer_handler();
        }
        var easyassist_cobrowsing_modal = document.getElementById("easyassist-co-browsing-modal-id");
        if(easyassist_cobrowsing_modal && easyassist_cobrowsing_modal.style.display == "none") {
            show_easyassist_browsing_modal();
        }
    }, EASYASSIST_COBROWSE_META.field_stuck_timer * 1000);
}

function reset_easyassist_element_stuck_timer() {
    stop_easyassist_element_stuck_timer();
    start_easyassist_element_stuck_timer();
}

function stop_easyassist_element_stuck_timer() {
    if (global_element_stuck_timer != null) {
        clearTimeout(global_element_stuck_timer);
    }
}

function add_easyassist_formassist_stuck_timer_handler() {

    try{
        if (EASYASSIST_COBROWSE_META.field_stuck_event_handler == false) {
            return;
        }

        window.addEventListener("mousemove", reset_easyassist_element_stuck_timer, true);

        form_input_elements = document.getElementsByTagName("input");
        for(let index = 0; index < form_input_elements.length; index++) {
            if (form_input_elements[index].getAttribute("class") == "easyassist-input-field") {
                continue;
            }
            form_input_elements[index].addEventListener("focusin", reset_easyassist_element_stuck_timer, true);
            form_input_elements[index].addEventListener("keypress", reset_easyassist_element_stuck_timer, true);
        }

        form_textarea_elements = document.getElementsByTagName("textarea");
        for(let index = 0; index < form_textarea_elements.length; index++) {
            form_textarea_elements[index].addEventListener("focusin", reset_easyassist_element_stuck_timer, true);
            form_textarea_elements[index].addEventListener("keypress", reset_easyassist_element_stuck_timer, true);
        }

        form_select_elements = document.getElementsByTagName("select");
        for(let index = 0; index < form_select_elements.length; index++) {
            form_select_elements[index].addEventListener("mousedown", reset_easyassist_element_stuck_timer, true);
            form_select_elements[index].addEventListener("change", reset_easyassist_element_stuck_timer, true);
        }
    }catch(err){}
}

function remove_easyassist_formassist_stuck_timer_handler() {

    window.removeEventListener("mousemove", reset_easyassist_element_stuck_timer, true);

    form_input_elements = document.getElementsByTagName("input");
    for(let index = 0; index < form_input_elements.length; index++) {
        form_input_elements[index].removeEventListener("focusin", reset_easyassist_element_stuck_timer, true);
        form_input_elements[index].removeEventListener("keypress", reset_easyassist_element_stuck_timer, true);
    }
    form_textarea_elements = document.getElementsByTagName("textarea");
    for(let index = 0; index < form_textarea_elements.length; index++) {
        form_textarea_elements[index].removeEventListener("focusin", reset_easyassist_element_stuck_timer, true);
        form_textarea_elements[index].removeEventListener("keypress", reset_easyassist_element_stuck_timer, true);
    }
    form_select_elements = document.getElementsByTagName("select");
    for(let index = 0; index < form_select_elements.length; index++) {
        form_select_elements[index].removeEventListener("mousedown", reset_easyassist_element_stuck_timer, true);
        form_select_elements[index].removeEventListener("change", reset_easyassist_element_stuck_timer, true);
    }
}

setTimeout(function(e) {
    add_easyassist_formassist_stuck_timer_handler();
    show_floating_sidenav_easyassist_button();
    update_easyassist_url_history();
}, 2000);

function go_to_sceensharing_tab(response) {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }
    if(response.allow_screen_sharing_cobrowse == true || response.allow_screen_sharing_cobrowse == "true") {

        window.open(EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + '/easy-assist/screensharing-cobrowse/?id=' + easyassist_session_id, '_blank');
    }
}
function update_agent_assistant_request(status) {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    var client_otp = "None";

    if (status == "true" && EASYASSIST_COBROWSE_META.enable_verification_code_popup == true) {
        client_otp = "";
        verify_inputs = easyassist_get_eles_by_class_name("easyassist-verfication-otp-input")
        for(let i = 0; i < verify_inputs.length; i++) {
            client_otp += verify_inputs[i].value
        }
        if (client_otp == "" || client_otp == undefined || client_otp == null) {
            document.getElementById("easyassist-request-assist-otp-error").innerHTML = "Please enter valid OTP";
            document.getElementById("easyassist-request-assist-otp-error").previousSibling.style.paddingBottom = "1em";
            return;
        }
    }

    json_string = JSON.stringify({
        "id": easyassist_session_id,
        "otp": client_otp,
        "status": status
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
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
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                document.getElementById("easyassist-co-browsing-request-assist-modal").style.display = "none";
                if(document.getElementById("easyassist-request-assist-otp-error")) {
                    document.getElementById("easyassist-request-assist-otp-error").innerHTML = "";
                    document.getElementById("easyassist-request-assist-otp-error").previousSibling.style.paddingBottom = "1em";
                }

                if (status == "true") {
                    // show_easyassist_toast("Agent will be joining");
                    show_easyassist_agent_joining_modal();
                    set_easyassist_cookie("easyassist_cobrowsing_allowed", "true");
                } else {
                    set_easyassist_cookie("easyassist_cobrowsing_allowed", "false");
                }
                check_for_agent_highlight();
                go_to_sceensharing_tab(response);
            } else {
                if(document.getElementById("easyassist-request-assist-otp-error")) {
                    document.getElementById("easyassist-request-assist-otp-error").innerHTML = "Please enter valid OTP";
                    document.getElementById("easyassist-request-assist-otp-error").previousSibling.style.paddingBottom = "1em";
                }
                //var description = "Update Agent Assistant Request API (/easy-assist/update-agent-assistant-request/) failed with status code " + response.status + ", Invalid Verification Code";
                // save_easyassist_system_audit_trail("api_failure", description);
            }
        } else if (this.readyState == 4) {
            //var description = "Update Agent Assistant Request API (/easy-assist/update-agent-assistant-request/) failed with status code " + this.status.toString();
            // save_easyassist_system_audit_trail("api_failure", description);
        }
    }
    xhttp.send(params);
}

function update_agent_meeting_request(status) {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    document.getElementById("easyassist-request-meeting-error").innerHTML = "";

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
                document.getElementById("easyassist-co-browsing-request-meeting-modal").style.display = "none";
                if (response.meeting_allowed == "true") {
                    set_easyassist_cookie("easyassist_meeting_allowed", "true");
                } else {
                    set_easyassist_cookie("easyassist_meeting_allowed", "false");
                }
                check_for_agent_highlight();
            } else {
                document.getElementById("easyassist-request-meeting-error").innerHTML = "Some error occured we can not connect you with our agent.";
            }
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

function submit_agent_feedback(feedback_type) {

    var close_session_remark_error_el = document.getElementById("close-session-remarks-error");
    var close_session_text_error_el = document.getElementById("close-session-text-error");

    if(close_session_text_error_el) {
        close_session_text_error_el.style.display = "none";
    }
    if(close_session_remark_error_el) {
        close_session_remark_error_el.style.display = "none";
    }


    stop_screen_recording();
    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    comment_desc = ""
    try{
        feedback = document.getElementById("close-session-remarks").value.trim();

        if(feedback.length == 0) {
            close_session_remark_error_el.innerHTML = "Please select a remark";
            close_session_remark_error_el.style.display = 'block';
            return;
        }
        comment_desc = document.getElementById("easyassist-close-session-remarks").value;
    } catch(err){
        feedback = document.getElementById("easyassist-close-session-remarks").value;
    }

    is_helpful = document.getElementById("easyassist-mask-successfull-cobrowsing-session").checked;

    if(remarks_validation(feedback, close_session_text_error_el, "Comments", 1, 200) == "invalid"){
        return
    }

    if(window.EASYASSIST_COBROWSE_META.enable_predefined_remarks == true || 
        window.EASYASSIST_COBROWSE_META.enable_predefined_remarks == "true" || 
        window.EASYASSIST_COBROWSE_META.enable_predefined_remarks == "True"){
        if(feedback == "others"){
            if(remarks_validation(comment_desc, close_session_text_error_el, "Comments", 1, 200) == "invalid"){
                return
            }
        } else {
            if(remarks_validation(comment_desc, close_session_text_error_el, "Comments", 0, 200) == "invalid"){
                return
            }
        }
    }

    document.getElementById("easyassist-close-session-remarks").value = "";

    json_string = JSON.stringify({
        "session_id": easyassist_session_id,
        "is_helpful": is_helpful,
        "feedback": feedback,
        "comment_desc": comment_desc
    });
    
    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/reverse/agent-close-session/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status != 200) {
                //var description = "Submit client feedback API (/easy-assist/submit-client-feedback/) failed with status code " + response.status;
                // save_easyassist_system_audit_trail("api_failure", description);
            }

            terminate_easyassist_cobrowsing_session();
        } else if (this.readyState == 4) {
            //var description = "Submit client feedback API (/easy-assist/submit-client-feedback/) failed with status code " + this.status.toString();
            // save_easyassist_system_audit_trail("api_failure", description);
        }
    }
    xhttp.send(params);
}


function confirm_payment_init() {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined || EASYASSIST_COBROWSE_META.allow_cobrowsing == false) {
        return;
    }

    var screenshot = screenshot_page();

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

function open_meeting_window(){
        set_easyassist_cookie("is_cobrowse_meeting_on", "true");
        var session_id = get_easyassist_cookie("easyassist_session_id")
        var url = EASYASSIST_COBROWSE_META.easyassist_host + "/easy-assist/meeting/" +session_id + "?is_meeting_cobrowsing=true"
        window.open(url, "_blank");
    }

function check_for_agent_highlight() {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    var allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;

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

    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/reverse/check-agent-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status == 500) {
                clearInterval(check_for_agent_guide_timer);
                terminate_easyassist_cobrowsing_session();
                return;
            }
            
            if (response.status != 200) {
                clearInterval(check_for_agent_guide_timer);
                return;
            }

            if (response.is_archived == true) {
                show_easyassist_toast("Customer has ended the session.");
                document.getElementById("agent-mouse-pointer").style.display = "none";
                hide_floating_sidenav_menu();
                show_easyassist_feedback_form();
                return;
            } else {
                show_floating_sidenav_menu();
            }

            window.AGENT_NAME = response["agent_name"];
            window.AGENT_USERNAME = response["agent_username"];

        }
    }
    xhttp.send(params);
}

function send_attachment_to_agent_for_validation(event){

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

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

            base64_str = reader.result.split(",")[1];

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
                      send_livechat_message_to_agent("uploaded attachment", response["file_path"], file.name);
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

function update_agent_request_edit_access(action) {

    var allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;

    if (allow_cobrowsing == false) {
        return;
    }

    if (action == "true") {
        set_easyassist_cookie("easyassist_edit_access", "true");
        if (EASYASSIST_COBROWSE_META.is_mobile == true) {
            document.getElementById("revoke-edit-access-button").parentElement.parentElement.style.display = "inherit";
        } else {
            document.getElementById("revoke-edit-access-button").style.display = "flex";
        }
    } else {
        set_easyassist_cookie("easyassist_edit_access", "false");

        if (EASYASSIST_COBROWSE_META.is_mobile == true) {
            document.getElementById("revoke-edit-access-button").parentElement.parentElement.style.display = "none";
        } else {
            document.getElementById("revoke-edit-access-button").style.display = "none";
        }
    }

    hide_easyassist_request_edit_access_form();
    if(agent_revoke_edit_access) {
        json_string = JSON.stringify({
            "type": "request-edit-access",
            "is_allowed": action,
            "agent_revoke_edit_access": agent_revoke_edit_access
        });
    }
    else {
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

function revoke_easyassist_edit_access() {
    if(agent_revoke_edit_access)
        show_easyassist_toast("Edit Access has been revoked by the customer.");
    else
        show_easyassist_toast("Edit Access has been revoked from customer.");
    update_agent_request_edit_access("none");
}

function send_client_name(client_name) {
  allincall_chat_window = document.getElementById("easyassist-livechat-iframe").contentWindow;
  var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    allincall_chat_window.postMessage(JSON.stringify({
        "session_id" : easyassist_session_id,
        "id": "client_name",
        "name": client_name
    }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);

}

function show_hyperlink_inside_text(text) {
    var urlRegex =/(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
    return text.replace(urlRegex, function(url) {
        return '<a href="' + url +'" target="_blank">' + url + '</a>';
    });
}

function load_chat_history() {
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
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/reverse/get-cobrowsing-chat-history/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            window.CLIENT_NAME = response.client_name;
            send_client_name(response.client_name);
            if(response.status==200 && response.chat_history.length > 0) {
                chat_history = response.chat_history;
                allincall_chat_window = document.getElementById("easyassist-livechat-iframe").contentWindow;
                for(let index=0; index<chat_history.length; index++){
                    sender = chat_history[index]["sender"];
                    message = chat_history[index]["message"];
                    message=show_hyperlink_inside_text(message);
                    datetime = chat_history[index]["datetime"];
                    is_admin_message = chat_history[index]["is_admin_message"];
                    sender_name = chat_history[index]["sender_name"]; 
                    var time = datetime.split(" ")[3] + " " + datetime.split(" ")[4];
                    attachment = chat_history[index]["attachment"];
                    attachment_file_name = chat_history[index]["attachment_file_name"];
                    if(sender == "client") {
                        allincall_chat_window.postMessage(JSON.stringify({
                            "agent_name": response.client_name,
                            "message": message,
                            "attachment": attachment,
                            "attachment_file_name": attachment_file_name,
                            "show_agent_message": true,
                            "time": time,
                            "sender": sender,
                        }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);
                    } else {
                        if(is_admin_message){
                            allincall_chat_window.postMessage(JSON.stringify({
                                "agent_name": sender_name,
                                "message": message,
                                "attachment": attachment,
                                "attachment_file_name": attachment_file_name,
                                "show_client_message": true,
                                "time": time,
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
                                "sender": sender,
                            }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);
                        }

                    }
                }
            }
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

function easyassist_notify_agent_lead_is_converted() {
    var COBROWSE_SESSION_ID = get_easyassist_cookie("easyassist_session_id");
    if (get_easyassist_cookie("is_lead_converted") == COBROWSE_SESSION_ID) {
        document.getElementById("easyassist-mask-successfull-cobrowsing-session").checked = true;
        document.getElementById("easyassist-mask-successfull-cobrowsing-session").disabled = true;
    }
}

/******************* LEAD CONVERTED LOGIC - END ************************/

//////////////////////  Screen Recording   /////////////////////////////////////////////

var screen_recorder_on = false, is_recording_cancel=false;
let recorder, stream, audioTrack, videoTrack, displayStream, audioStream;

async function startRecording() {

    if (screen_recorder_on == false && is_recording_cancel == false) {
        alert('The cobrowsing session will be recorded and shared for audit purposes. Please click on “OK” and select the screen to share.')
    } else {
        alert("To resume the cobrowsing session, kindly allow to record and share your screen.")
        is_recording_cancel = false
    }

    try {

        if(EASYASSIST_COBROWSE_META.allow_agent_to_audio_record_customer_cobrowsing == true){
            try {
                audioStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
                [audioTrack] = audioStream.getAudioTracks();
            } catch (err){
                screen_recorder_on = false;
                is_recording_cancel = true;
                alert("Microphone Permission is not given please allow microphone use.")
                startRecording();
                return;
            }
        }

        try {
            displayStream = await navigator.mediaDevices.getDisplayMedia({ video: { mediaSource: "screen" } });
            [videoTrack] = displayStream.getVideoTracks();
        } catch {
            screen_recorder_on = false;
            is_recording_cancel = true;
            startRecording();
            return;
        }

        if(EASYASSIST_COBROWSE_META.allow_agent_to_audio_record_customer_cobrowsing == true){
            stream = new MediaStream([videoTrack, audioTrack]);
        }else{
            stream = new MediaStream([videoTrack]);
        }

        stream.getVideoTracks()[0].onended = function() {
            is_recording_cancel = true
            screen_recorder_on = false
            startRecording();
        };
        recorder = new MediaRecorder(stream);
    } catch {
        screen_recorder_on = false;
        startRecording();
        return;
    }

    screen_recorder_on = true;
    recorder.ondataavailable = blob => save_cobrowseing_recorded_data(blob);
    recorder.start(5000);
}

function save_cobrowseing_recorded_data(blob) {

    var COBROWSE_SESSION_ID = get_easyassist_cookie("easyassist_session_id")
    var filename = COBROWSE_SESSION_ID + '.webm';
    var file = new File([blob.data], filename, {
        type: 'video/webm'
    });
    var formData = new FormData();
    formData.append("uploaded_data", file);
    formData.append("session_id", COBROWSE_SESSION_ID);
    formData.append("screen_recorder_on", screen_recorder_on);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/save-reverse-cobrowsing-screen-recorded-data/", true);
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                console.log("Data packet saved successfully.");
            }else{
                console.log("Unable to save data packet");
            }
        }
    }
    xhttp.send(formData);

}

function stop_screen_recording(){
    try{
        screen_recorder_on = false;
        recorder.stop();
        stream.getVideoTracks()[0].stop();
        stream.getAudioTracks()[0].stop();
    }catch (err){}
}
//////////////////////  Screen Recording End  /////////////////////////////////////////////

function send_end_meeting_messsage_over_socket(auto_end_meeting) {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

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

function send_client_meeting_joined_over_socket() {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

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

function send_voip_meeting_ready_over_socket() {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

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

    easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
}

function easyassist_set_livechat_typing(name, role){
    allincall_chat_window = document.getElementById("easyassist-livechat-iframe").contentWindow;
    allincall_chat_window.postMessage(JSON.stringify({
        "id": "livechat-typing",
        "role": role,
        "name": name
    }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);
}


function easyassist_start_internet_connectivity_check_timer() {
    internet_connectivity_timer = setInterval(function(e) {
        if(get_easyassist_cookie("easyassist_session_id")){
            if(get_easyassist_cookie("easyassist_agent_disconnected_modal_shown") == undefined || get_easyassist_cookie("easyassist_agent_disconnected_modal_shown") == "false"){
                easyassist_show_agent_disconnected_modal();
                set_easyassist_cookie("easyassist_agent_disconnected_modal_shown", "true")
            }
        }
        easyassist_reset_internet_connectivity_check_timer();
    }, INTERNET_CON_TIMER);
}

function easyassist_stop_internet_connectivity_check_timer() {
    if (internet_connectivity_timer != null && internet_connectivity_timer != undefined) {
        clearInterval(internet_connectivity_timer);
    }
}

function easyassist_reset_internet_connectivity_check_timer() {
    easyassist_stop_internet_connectivity_check_timer();
    easyassist_start_internet_connectivity_check_timer();
}

function actions_after_connected_successfully(){
    var connected_successfully = get_easyassist_cookie("ea_cust_connected");
    if(connected_successfully == "true") return;

    show_easyassist_toast("Customer has joined the session");

    set_easyassist_cookie("ea_cust_connected", "true");

    var message = EASYASSIST_COBROWSE_META.agent_connect_message;
    message = message.replaceAll("agent_name", window.AGENT_NAME);

    if(EASYASSIST_COBROWSE_META.enable_agent_connect_message == true){
        send_livechat_message_to_agent(EASYASSIST_COBROWSE_META.agent_connect_message, "None", "None");
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
        easyassist_send_client_weak_connection_message_interval = setInterval(easyassist_send_client_weak_connection_message, 5000);
        easyassist_send_client_weak_connection_message()
    }
}

function easyassist_send_client_weak_connection_message(){
    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

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

start_cobrowsing_activity_check();

/******************* Screenshot Capture - START ************************/

function easyassist_capture_client_screenshot() {
    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    hide_easyassist_capture_screenshot_modal();

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
            set_value_attr_into_screenshot(clone_document_node);
        },
        ignoreElements: function(element) {
            return check_easyassist_dom_node(element);
        },
    }).then(function(canvas) {
        img_data = canvas.toDataURL('image/png');
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

                if (response.status == 200) {
                    show_easyassist_toast("Screenshot captured successfully");

                    json_string = JSON.stringify({
                        "type": "screenshot",
                        "agent_name": window.AGENT_NAME
                    });

                    encrypted_data = easyassist_custom_encrypt(json_string);

                    encrypted_data = {
                        "Request": encrypted_data
                    };

                    easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");

                }
                if (response.status != 200) {
                    show_easyassist_toast("Unable to capture the screenshot. Please try again.");
                }

            } else if (this.readyState == 4) {
                show_easyassist_toast("Unable to capture the screenshot. Please try again.");
            }
        }
        xhttp.send(params);
    });
}

function fetch_cobrowsing_meta_information() {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    show_easyassist_captured_screenshot_view_modal();

    var captured_information_modal_info = document.getElementById("easyassist-captured-screenshot-view-error");

    if (load_more_meta == false) {
        cobrowsing_meta_data_page = 1;
        captured_information_modal_info.innerHTML = "Loading ...";
        document.getElementById("easyassist-captured-screenshot-view-table-div").style.display = "none";
    }

    json_string = JSON.stringify({
        "id": easyassist_session_id,
        "page": cobrowsing_meta_data_page
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/reverse/get-meta-information/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
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
                        tbody_html += [
                            '<tr>',
                                '<td style="text-transform: capitalize;">' + meta_information_list[index]["type"] + '</td>',
                                '<td>' + meta_information_list[index]["datetime"] + '</td>',
                                '<td style="text-align: center">',
                                    '<a href="' + EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + '/easy-assist/agent/export/' + meta_id + '/?type=img" download title="Export As Image">',
                                        '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                            '<path d="M10 0C15.5 0 20 4.5 20 10C20 15.5 15.5 20 10 20C4.5 20 0 15.5 0 10C0 4.5 4.5 0 10 0ZM6 15H14V13H6V15ZM14 8H11.5V4H8.5V8H6L10 12L14 8Z" fill="#757575"/>',
                                        '</svg>',
                                    '</a>',
                                '</td>',
                            '</tr>',

                        ].join('');
                    }

                    if (response.is_last_page == false) {
                        tbody_html += [
                            '<tr onclick="load_more_meta_information(this)">',
                                '<td colspan="3" class="text-center">',
                                    '<button class="easyassist-modal-primary-btn" style="border-radius: .35rem !important;">Load More</button>',
                                '</td>',
                            '</tr>',
                        ].join('');
                    }

                    if (cobrowsing_meta_data_page == 1) {
                        document.getElementById("easyassist-captured-screenshot-view-table-body").innerHTML = tbody_html;
                    } else {
                        document.getElementById("easyassist-captured-screenshot-view-table-body").innerHTML += tbody_html;
                    }
                    document.getElementById("easyassist-captured-screenshot-view-table-div").style.display = "";
                    // easyassist_captured_screenshot_view_button.innerHTML = "Cancel";
                    // easyassist_captured_screenshot_view_button.onclick = hide_easyassist_captured_screenshot_view_modal;
                } else {
                    captured_information_modal_info.innerHTML = "No screenshots";
                    document.getElementById("easyassist-captured-screenshot-view-table-div").style.display = "none";
                }
            } else {
                captured_information_modal_info.innerHTML = "Unable to load the details. Please try again.";
                document.getElementById("easyassist-captured-screenshot-view-table-div").style.display = "none";
                // easyassist_captured_screenshot_view_button.innerHTML = "Try Again";
                // easyassist_captured_screenshot_view_button.onclick = fetch_cobrowsing_meta_information;
            }
            load_more_meta = false;
        } else if (this.readyState == 4){
            captured_information_modal_info.innerHTML = "Unable to load the details. Please try again.";
            document.getElementById("easyassist-captured-screenshot-view-table-div").style.display = "none";
            // easyassist_captured_screenshot_view_button.innerHTML = "Try Again";
            // easyassist_captured_screenshot_view_button.onclick = fetch_cobrowsing_meta_information;
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

/******************* Screenshot Capture - END ************************/


/******************* Invite Agent - START ************************/

function easyassist_search_invite_agent(){
    var agent_search_box = document.getElementById("easyassist-invite-agent-search-box");
    var search_text = agent_search_box.value.toLowerCase();
    var agent_list = document.getElementById("easyassist-invite-agent-list-content").children;

    var count_value_matched = 0;

    for(let index=2 ; index<agent_list.length ; index++){
        var agent_option = agent_list[index];
        var agent_name = agent_option.firstElementChild.innerHTML.toLowerCase();

        if(agent_name.indexOf(search_text) >= 0){
            agent_option.style.display = "";
            count_value_matched++;
        } else {
            agent_option.style.display = "none";
        }
    }

    if(count_value_matched == 0){
        document.getElementById("easyassist-no-agent-option").style.display = "";
    } else {
        document.getElementById("easyassist-no-agent-option").style.display = "none";
    }
}

function easyassist_select_invite_agent(selected_element, agent_name, agent_id){
    easyassist_selected_invite_agent_id = agent_id;
    document.getElementById("easyassist-invite-agent-button").innerHTML = agent_name;
    document.getElementById("easyassist-invite-agent-error").innerHTML = "";

    var agent_list = document.getElementById("easyassist-invite-agent-list-content").children;

    for(let element of agent_list){
        element.classList.remove('ea-theme-bg');
        if(element == selected_element){
            element.classList.add('ea-theme-bg');
        }
    }
}

function easyassist_get_list_of_support_agents() {

    document.getElementById("easyassist-invite-agent-error").innerHTML = "";
    document.getElementById("easyassist-invite-agent-error").style.color = "red";

    easyassist_selected_invite_agent_id = null;
    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    show_easyassist_invite_agent_modal();

    json_string = JSON.stringify({
        "id": get_easyassist_cookie("easyassist_session_id")
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/reverse/get-support-agents/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            var support_agents = response.support_agents;

            if(support_agents.length == 0){
                document.getElementById("easyassist-invite-agent-error").innerHTML = "No agents found.";
                document.getElementById("easyassist-invite-agent-list-div").style.display = "none";
            } else {
                document.getElementById("easyassist-invite-agent-list-div").style.display = "";
                var agent_list_html = "";
                agent_list_html += '\
                    <li class="searchInput">\
                        <input type="text" id="easyassist-invite-agent-search-box" class="dropdownsearch" placeholder="Search for an Agent" onkeyup="easyassist_search_invite_agent()" autocomplete="off">\
                    </li>';
                agent_list_html += '\
                    <li id="easyassist-no-agent-option" class="easyassist-agent-options" style="display:none;">\
                        <span> No agents found </span>\
                    </li>';

                for(let index=0 ; index<support_agents.length ; index++){
                    var agent_detail = support_agents[index];
                    agent_list_html += '<li onclick="easyassist_select_invite_agent(this, \'' + agent_detail.username + '\', \'' + agent_detail.id + '\')" class="easyassist-agent-options"><span>' + agent_detail.username + '</span></li>';
                }

                document.getElementById("easyassist-invite-agent-list-content").innerHTML = agent_list_html;
                document.getElementById("easyassist-invite-agent-list-content").style.display = "none";
            }
        }
    }
    xhttp.send(params);
}

function easyassit_share_cobrowsing_session(element) {

    document.getElementById("easyassist-invite-agent-error").innerHTML = "";
    document.getElementById("easyassist-invite-agent-error").style.color = "red";

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if(easyassist_session_id == undefined || easyassist_session_id == null){
        return;
    }

    var support_agents = [];
    if(easyassist_selected_invite_agent_id){
        support_agents.push(easyassist_selected_invite_agent_id);
    }

    if(support_agents.length == 0){
        document.getElementById("easyassist-invite-agent-error").innerHTML = "Please select support agent with whom you want to share the session.";
        document.getElementById("easyassist-invite-agent-error").style.color = "red";
        return;
    }

    json_string = JSON.stringify({
        "id": easyassist_session_id,
        "support_agents": support_agents
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    element.innerHTML = "Inviting...";

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/reverse/share-session/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                document.getElementById("easyassist-invite-agent-error").innerHTML = "Invitation has been sent to the agent. Please inform the agent to join the session.";
                document.getElementById("easyassist-invite-agent-error").style.color = "green";
            } else {
                document.getElementById("easyassist-invite-agent-error").innerHTML = "Something went wrong. Please try again.";
                document.getElementById("easyassist-invite-agent-error").style.color = "red";
            }
            element.innerHTML = "Invite";
        } else if (this.readyState == 4){
            document.getElementById("easyassist-invite-agent-error").innerHTML = "Something went wrong. Please try again.";
            document.getElementById("easyassist-invite-agent-error").style.color = "red";
            element.innerHTML = "Invite";
        }
    }
    xhttp.send(params);
}

/******************* Invite Agent - END ************************/


/******************* Support Document - START ************************/


function easyassist_get_support_material() {

    show_easyassist_support_document_modal();

    if(document.getElementById("easyassist-support-document-modal").querySelector('tbody').children.length) {
        return;
    }

    var support_material_modal_info = document.getElementById("easyassist-support-document-error");

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

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

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/reverse/get-support-material/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
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
                        var file_path = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/" + support_document_obj["file_path"];
                        var message = file_name;
                        // div_inner_html += '<tr>';
                        // div_inner_html += '<td style="vertical-align:middle;"> <a class="support-document-link" href="' + file_path + '" target="_blank" >' + file_name + '</a> </td>';
                        // div_inner_html += '<td> <input class="support-document-message-text" type="text" value="' + message + '" style="width: 100%;"> </td>';
                        // div_inner_html += '\
                        //     <td>\
                        //         <button class="btn btn-action" onclick="send_support_material_doc(this)">\
                        //             <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        //                 <path d="M15.6377 7.40491L0.988524 0.070419C0.873708 0.0129211 0.744741 -0.0101171 0.617152 0.00407857C0.489563 0.0182742 0.368792 0.0690985 0.269381 0.150432C0.174443 0.230106 0.103582 0.334718 0.064764 0.452509C0.0259456 0.570299 0.0207089 0.696597 0.0496425 0.817204L1.81421 7.33157H9.34524V8.66511H1.81421L0.0230075 15.1595C-0.00414248 15.2602 -0.00731172 15.3659 0.0137547 15.4681C0.0348212 15.5702 0.0795356 15.666 0.144302 15.7477C0.209069 15.8294 0.292081 15.8948 0.386663 15.9386C0.481246 15.9823 0.584759 16.0032 0.688881 15.9996C0.793118 15.999 0.895753 15.9739 0.988524 15.9263L15.6377 8.59177C15.7468 8.53581 15.8383 8.4508 15.9023 8.3461C15.9662 8.24139 16 8.12106 16 7.99834C16 7.87562 15.9662 7.75528 15.9023 7.65058C15.8383 7.54588 15.7468 7.46087 15.6377 7.40491Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                        //             </svg>\
                        //         </button>\
                        //     </td>';
                        // div_inner_html += '<tr>';

                        div_inner_html += [
                            '<tr>',
                                '<td style="vertical-align:middle;min-width: 4.5em;"> <a class="support-document-link" href="' + file_path + '" target="_blank" >' + file_name + '</a> </td>',
                                '<td> <input class="support-document-message-text" type="text" value="' + message + '" style="width: 100% !important;"> </td>',
                                '<td style="text-align: center">',
                                    '<button class="btn btn-action" onclick="easyassist_send_support_material_doc(this)" style="background: none; width: 50px;">',
                                        '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                            '<path d="M15.6377 7.40491L0.988524 0.070419C0.873708 0.0129211 0.744741 -0.0101171 0.617152 0.00407857C0.489563 0.0182742 0.368792 0.0690985 0.269381 0.150432C0.174443 0.230106 0.103582 0.334718 0.064764 0.452509C0.0259456 0.570299 0.0207089 0.696597 0.0496425 0.817204L1.81421 7.33157H9.34524V8.66511H1.81421L0.0230075 15.1595C-0.00414248 15.2602 -0.00731172 15.3659 0.0137547 15.4681C0.0348212 15.5702 0.0795356 15.666 0.144302 15.7477C0.209069 15.8294 0.292081 15.8948 0.386663 15.9386C0.481246 15.9823 0.584759 16.0032 0.688881 15.9996C0.793118 15.999 0.895753 15.9739 0.988524 15.9263L15.6377 8.59177C15.7468 8.53581 15.8383 8.4508 15.9023 8.3461C15.9662 8.24139 16 8.12106 16 7.99834C16 7.87562 15.9662 7.75528 15.9023 7.65058C15.8383 7.54588 15.7468 7.46087 15.6377 7.40491Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                                        '</svg>',
                                    '</button>',
                                '</td>',
                            '</tr>',

                        ].join('');


                        document.getElementById("easyassist-support-document-div").querySelector('table').innerHTML = div_inner_html;
                        document.getElementById("easyassist-support-document-div").style.display = "";
                    }
                } else {
                    support_material_modal_info.innerHTML = "No Support Document Found.";
                    document.getElementById("easyassist-support-document-div").style.display = "none";
                }
            } else {
                support_material_modal_info.innerHTML = "Unable to load the details. Please Try again.";
                document.getElementById("easyassist-support-document-div").style.display = "none";
            }
        } else if (this.readyState == 4){
            support_material_modal_info.innerHTML = "Unable to load the details. Please Try again.";
            document.getElementById("easyassist-support-document-div").style.display = "none";
        }
    }
    xhttp.send(params);
}


function append_attachment_message_into_chatbox(message, attachment, attachment_file_name) {
    allincall_chat_window.postMessage(JSON.stringify({
        "agent_name": window.AGENT_NAME,
        "message": message,
        "attachment": attachment,
        "attachment_file_name": attachment_file_name,
        "show_client_message": true,
        "sender": window.AGENT_USERNAME,
    }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);
}

function easyassist_send_support_material_doc(element) {
    var action_cell = element.parentElement;
    var message_cell = action_cell.previousElementSibling;
    var attachment_cell = message_cell.previousElementSibling;

    var attachment = attachment_cell.children[0].href;

    var message = message_cell.children[0].value;
    var attachment_file_name = attachment_cell.children[0].text;

    send_livechat_message_to_agent(message, attachment, attachment_file_name);
    append_attachment_message_into_chatbox(message, attachment, attachment_file_name);

    hide_easyassist_support_document_modal();
    show_easyassist_livechat_iframe();
}

/******************* Support Document - END ************************/


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

    var COBROWSE_SESSION_ID = get_easyassist_cookie("easyassist_session_id");
    if(COBROWSE_SESSION_ID == undefined || COBROWSE_SESSION_ID == null){
        COBROWSE_SESSION_ID = "";
    }

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
            "internet_speed": easyassist_avg_speed_mbps + " mbps",
        }
        meta_data["variable_value"] = {
            "easyassist_send_client_weak_connection_message_interval": easyassist_send_client_weak_connection_message_interval,
            "AGENT_NAME": AGENT_NAME,
            "EASYASSIST_SESSION_ID": EASYASSIST_SESSION_ID,
            "check_for_agent_assistance": check_for_agent_assistance,
            "is_agent_connected": is_agent_connected,
            "hidden_element_count": hidden_element_count,
            "check_for_agent_guide_timer": check_for_agent_guide_timer,
            "html_page_counter": html_page_counter,
            "session_closed_by_agent": session_closed_by_agent,
            "is_cobrowse_meeting_on": is_cobrowse_meeting_on,
            "agent_mouse_top": agent_mouse_top,
            "agent_mouse_left": agent_mouse_left,
            "agent_revoke_edit_access": agent_revoke_edit_access,
            "cobrowsing_meta_data_page": cobrowsing_meta_data_page,
            "load_more_meta": load_more_meta,
            "client_websocket_readystate": client_websocket.readyState,
            "client_websocket_open": client_websocket_open,
            "sync_utils_client_websocket_open": sync_utils_client_websocket_open,
            "sync_utils_client_websocket_readystate": sync_utils_client_websocket.readyState,
            "packet_counter": packet_counter,
            "easyassist_internet_iteration": easyassist_internet_iteration,
            "internet_connectivity_timer": internet_connectivity_timer,
            "INTERNET_CON_TIMER": INTERNET_CON_TIMER,
            "check_cobrowse_session_timer": check_cobrowse_session_timer,
            "easyassist_selected_invite_agent_id": easyassist_selected_invite_agent_id,
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
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/report-bug/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_element.innerHTML = "Issue reported successfully."
                error_element.style.color = "green";
                setTimeout(function(){
                    hide_easyassist_report_bug_modal();
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

/************************* END BUG REPORT *************************/
