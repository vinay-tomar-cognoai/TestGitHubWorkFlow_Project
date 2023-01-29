var easyassist_send_client_weak_connection_message_interval = null;
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
var easyassist_avg_speed_mbps=0;

var easyassist_tree_mirror_client = null;

var easyassist_auto_change_event_timeout = null;
var easyassist_auto_change_event_time = null;

window.AGENT_NAME = '';
window.AGENT_USERNAME = '';
window.AGENT_PROFILE_PIC_SOURCE = "";

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

function easyassist_is_url_restricted() {

    var restricted_urls = window.EASYASSIST_COBROWSE_META.restricted_urls_list;
    var current_url = window.location.href.replace(/^https?\:\/\//i, "");
    
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

            if(!restriction_bypass && easyassist_is_url_restricted()) {
                message = easyassist_get_restricted_data_packet();
            }

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

// window.onload = function() {

//     window.addEventListener("storage", function (e) {
//         console.log(e);
//         if(e.key == "easyassist_session") {
//             var new_value = e.newValue;
//             var COBROWSE_SESSION_ID = get_easyassist_cookie("easyassist_session_id");
//             if(new_value.hasOwnProperty(COBROWSE_SESSION_ID)) {
//                 new_value = new_value[COBROWSE_SESSION_ID]
//                 if(new_value.hasOwnProperty("is_cobrowse_meeting_active")) {
//                     if(new_value["is_cobrowse_meeting_active"] == "" && get_easyassist_cookie("is_cobrowse_meeting_active") == COBROWSE_SESSION_ID) {
//                         set_easyassist_cookie("is_cobrowse_meeting_active", "");
//                     }
//                 }
//             }
//         }
//     }, false);
// };

function easyassist_delete_all_cookie(){
    delete_easyassist_cookie("easyassist_session_id");
    delete_easyassist_cookie("easyassist_agent_connected");
    delete_easyassist_cookie("easyassist_cobrowsing_allowed");
    delete_easyassist_cookie("easyassist_edit_access");
    delete_easyassist_cookie("easyassist_customer_id");
    delete_easyassist_cookie("cobrowse_meeting_id");
    delete_easyassist_cookie("is_cobrowse_meeting_active");
    delete_easyassist_cookie("is_lead_converted");
    delete_easyassist_cookie("easyassist_client_disconnected_modal_shown");
    delete_easyassist_cookie("easyassist_client_weak_internet_connection_shown");
    delete_easyassist_cookie("easyassist_agent_weak_internet_connection_shown");
    delete_easyassist_cookie("easyassist_agent_disconnected_modal_shown");
    delete_easyassist_cookie("is_cobrowse_meeting_on");
    delete_easyassist_cookie("ea_cust_connected");
    easyassist_clear_local_storage();
}

function easyassist_disconnect_mutation_summary_client() {
    try {
        if(easyassist_tree_mirror_client != null) {
            easyassist_tree_mirror_client.disconnect();
            easyassist_tree_mirror_client = null;
        }
    } catch(err) {
        console.log("easyassist_disconnect_mutation_summary_client: ", err);
    }
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

            easyassist_disconnect_mutation_summary_client();

            easyassist_reset_canvas();

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
        hide_floating_mobile_sidenav_menu();

        if(document.getElementById("agent-mouse-pointer")){
            document.getElementById("agent-mouse-pointer").style.display = "none";
        }
        
        try {
            toggle_voip_ringing_sound();
        } catch(err) {}

        if(document.getElementById('report_problem_icon')){
            document.getElementById('report_problem_icon').style.display = "none";
        }

        show_easyassist_toast("Session has ended");
    }catch(err){
        easyassist_delete_all_cookie();
        console.error("Error on termination", err)
    }
}

function easyassist_special_event_listner() {
    try {
        var inputs = document.querySelectorAll("input");
        for(let idx = 0; idx < inputs.length; idx ++) {
            const input = inputs[idx];
            const input_type = input.getAttribute("type");
            const descriptor = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(input), 'value');

            if(input_type == "hidden" || input_type == "button" || input_type == "submit") {
                continue;
            }

            try {
                Object.defineProperty(input, 'value', {
                    set: function(t) {
                        var current_time = Date.now();
                        if(easyassist_auto_change_event_timeout != null && current_time - easyassist_auto_change_event_time <= 200) {
                            clearTimeout(easyassist_auto_change_event_timeout);
                        }

                        if(input.has_easyassist_change_event != false) {
                            easyassist_auto_change_event_timeout = setTimeout(function() {
                                easyassist_sync_html_element_value_change();
                            }, 200);
                        }

                        easyassist_auto_change_event_time = Date.now();
                        return descriptor.set.apply(this, arguments);
                    },
                    get: function() {
                      return descriptor.get.apply(this);
                    }
                });
            } catch(err) {}
        }
    } catch(err) {
        console.log("easyassist_special_event_listner: ", err);
    }
}

function easyassist_sync_html_data() {
    try {
        var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

        if (easyassist_session_id == null || easyassist_session_id == undefined) {
            return;
        }

        var allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;

        if (allow_cobrowsing == false) {
            return;
        }

        
        easyassist_sync_html_data_utils();

    } catch(err) {
        console.log("easyassist_sync_html_data: ", err);
    }
}

function easyassist_get_css_from_stylesheet() {
    var css_text = "";
    try {
        if(EASYASSIST_COBROWSE_META.enable_cobrowsing_on_react_website == false) {
            return css_text;
        }

        var css = "";
        var style_elements_list = document.querySelectorAll("style[data-styled]");
        var style_elements = [];
        for(let idx = 0; idx < style_elements_list.length; idx ++) {
            style_elements.push(style_elements_list[idx]);
        }

        var inline_styles = document.querySelectorAll("style");

        for(let idx = 0; idx < inline_styles.length; idx ++) {
            if(inline_styles[idx] && inline_styles[idx].innerText) {
                if(inline_styles[idx].innerText.trim() == "") {
                    style_elements.push(inline_styles[idx]);
                }
            }
        }

        for(let idx = 0; idx < style_elements.length; idx ++) {
            var sheet = style_elements[idx].sheet;
            var rules = ('cssRules' in sheet)? sheet.cssRules : sheet.rules;
            if(!rules) {
                continue;
            }
            for(let rule_idx = 0; rule_idx < rules.length; rule_idx ++) {
                var rule = rules[rule_idx];

                if ('cssText' in rule) {
                    css += rule.cssText;
                } else {
                    css += rule.selectorText + '{'+rule.style.cssText+'}'
                }
            }
        }
        css_text = css;
    } catch(err) {
        console.error("easyassist_get_css_from_stylesheet: ", err);
    }
    return css_text;
}

function easyassist_sync_html_data_utils() {

    try {
        easyassist_set_event_listeners();

        if(easyassist_tree_mirror_client != null) {
            return;
        }

        try {
            easyassist_special_event_listner();
        } catch(err) {}

        var css_text = easyassist_get_css_from_stylesheet();

        easyassist_tree_mirror_client = new EasyAssistTreeMirrorClient(document, {
            initialize: function(rootId, children) {
                json_string = JSON.stringify({
                    type: "html_initialize",
                    f: 'initialize',
                    args: [rootId, children],
                    props: {
                        base: location.href.match(/^(.*\/)[^\/]*$/)[1],
                        scrollX: window.scrollX,
                        scrollY: window.scrollY,
                        window_width: window.innerWidth,
                        window_height: window.innerHeight,
                        css_text: css_text,
                    }
                });

                encrypted_data = easyassist_custom_encrypt(json_string);
                encrypted_data = {
                    "Request": encrypted_data
                };

                easyassist_send_message_over_socket(encrypted_data, "client");
            },

            applyChanged: function(removed, addedOrMoved, attributes, text) {
                if(!(removed.length || addedOrMoved.length || attributes.length || text.length)) {
                    return;
                }

                let css_text = easyassist_get_css_from_stylesheet();

                json_string = JSON.stringify({
                    type: "html_change",
                    f: 'applyChanged',
                    args: [removed, addedOrMoved, attributes, text],
                    base: location.href.match(/^(.*\/)[^\/]*$/)[1],
                    css_text: css_text,
                });

                encrypted_data = easyassist_custom_encrypt(json_string);

                encrypted_data = {
                    "Request": encrypted_data
                };

                easyassist_send_message_over_socket(encrypted_data, "client");
            },

            check_dom_node: function(element) {
                return easyassist_check_dom_node(element);
            },

            obfuscate_text_node: function(node) {
                let textContent = node.textContent;
                try{
                    let parent_masked_ele = node.parentElement.closest("[easyassist-obfuscate]")
                    if(parent_masked_ele){
                        textContent = easyassist_obfuscate(
                                        node.textContent,
                                        parent_masked_ele.getAttribute("easyassist-obfuscate")
                                    );
                    }
                }catch(err){}
                return textContent;
            },

            get_element_value: easyassist_get_input_element_value,
      });

    } catch(err) {
        console.log("easyassist_sync_html_data_utils: ", err);
    }
}

function easyassist_get_input_element_value(element, is_capture_screenshot_callback=false) {
    var element_value = [null, null];
    try {
        var tag_name = element.tagName;
        var is_obfuscated_element = easyassist_obfuscated_element_check(element);

        if(tag_name != "INPUT" && tag_name != "SELECT" && tag_name != "TEXTAREA" && !(is_capture_screenshot_callback && is_obfuscated_element[0])) {
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
        } else if(element.tagName == "TEXTAREA") {
            current_element_value = element.value;
        } else if (is_obfuscated_element[0] && is_capture_screenshot_callback) {
            current_element_value = element.textContent;
        }

        var is_numeric = false;
        if (is_obfuscated_element[0] == false && isNaN(parseInt(current_element_value.toString())) == false) {
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

function send_livechat_message_to_agent(message, attachment, attachment_file_name, chat_type) {

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
        "agent_profile_pic_source": window.AGENT_PROFILE_PIC_SOURCE,
        "chat_type": chat_type,
        "sender": window.AGENT_USERNAME,
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

function easyassist_sync_scroll_position_inside_div(event) {
    try {
        if(get_easyassist_cookie("easyassist_edit_access") == "true") {
            return;
        }

        var element_id = easyassist_get_easyassist_id_from_element(event.target);

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

        easyassist_send_message_over_socket(encrypted_data, "client");
    } catch(err) {}
}

function easyassist_sync_html_element_value_change() {

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
            element_id = easyassist_get_easyassist_id_from_element(tag_elements[tag_element_index]);

            if(element_id == null || element_id == undefined) {
                // console.log("Danger: Element id not found");
                continue;
            }

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

            is_obfuscated_element = easyassist_obfuscated_element_check(tag_elements[tag_element_index]);

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

function easyassist_send_data_to_server(event) {

    try {
        if(event.type == "click") {

            easyassist_set_event_listeners();

        } else if (event.type == "scroll") {
            sync_scroll_position();
        } else if (event.type == "resize") {
            easyassist_sync_client_screen_dimension();
            easyassist_resize_easyassist_canvas();
            easyassist_relocate_drag_element();
        } else {
            tag_name = document.activeElement.tagName;
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
    } catch(err) {
        console.log("easyassist_send_data_to_server: ", err);
    }
}

function easyassist_sync_client_screen_dimension() {
    try {
        json_string = JSON.stringify({
            "type": "client_screen_resize",
            "scrollX": window.scrollX,
            "scrollY": window.scrollY,
            "window_width": window.innerWidth,
            "window_height": window.innerHeight,
        });

        encrypted_data = easyassist_custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };

        easyassist_send_message_over_socket(encrypted_data, "client");
    } catch(err) {
        console.log(err);
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

        var scrollX = agent_packet.data_scroll_x;
        var scrollY = agent_packet.data_scroll_y;

        if(check_native_function(window.scrollTo)) {
            window.scrollTo(scrollX, scrollY);
        } else {
            window.scroll(scrollX, scrollY);
        }

    } catch(err) {
        console.log("sync_client_scroll_position: ", err);
    }
    
}

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
        console.log("check_current_tab_active: ", err);
    }
}

function easyassist_chat_notification_sound(){
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


function easyassist_chat_notification(message,attachment_file_name,customer_name){

    let is_current_tab_focussed = easyassist_check_current_tab_active();

    //Check for is current tab is not in focus and Notificaiton are allowed on the browser
    if(!is_current_tab_focussed && typeof Notification !== "undefined"){
            
        let notification_title = `${customer_name} messaged you!`;
        let notification_body = easyassist_get_notification_body(message, attachment_file_name);
        
        easyassist_send_chat_notification(notification_title,notification_body);
    }
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
    if(easyassist_is_url_restricted()) {
        var type = agent_packet.type;
        const restricted_types = ["mouse", "html", "button-click", "request-edit-access", "sync_canvas", "sync-form", "div-scroll", "sync-scroll"]; 
        const found = restricted_types.find(element => element == type);
        if(typeof found !== 'undefined')
            return;
    }

    if (message.header.sender == "agent") {

        easyassist_reset_internet_connectivity_check_timer();
        
        if (agent_packet.type == "open_pdf_render_modal") {
            if(easyassist_check_current_tab_active()) {
                easyassist_show_chat_bubble();
                easyassist_show_pdf_render_modal(agent_packet.file_name,agent_packet.file_src,agent_packet.session_id);
            } else {
                easyassist_send_tab_not_focus_over_socket();
            }

        } else if (agent_packet.type == "screenshot") {

            capture_client_screenshot();

            // agent has requested to take pageshot
        } else if (agent_packet.type == "pageshot") {

            capture_client_pageshot();

        } else if (agent_packet.type == "html") {

            easyassist_disconnect_mutation_summary_client();
            easyassist_sync_html_data();

        } else if (agent_packet.type == "sync-scroll") {

            sync_client_scroll_position(agent_packet);

        } else if (agent_packet.type == "mouse") {
            document.getElementById("agent-mouse-pointer").style.display = "inline-block";
            agent_mouse_top = agent_packet.position.clientY;
            agent_mouse_left = agent_packet.position.clientX;
            document.getElementById("agent-mouse-pointer").style.top = agent_packet.position.clientY + window.scrollY + "px";
            document.getElementById("agent-mouse-pointer").style.left = agent_packet.position.clientX + window.scrollX +"px";

        } else if (agent_packet.type == "chat") {
            if(EASYASSIST_COBROWSE_META.is_mobile && agent_packet.chat_type != "chat_bubble") {
                document.getElementById("easyassist-livechat-iframe").style.display = "block";
                set_easyassist_current_session_local_storage_obj("new_message_seen","true");
            }
            if(EASYASSIST_COBROWSE_META.enable_chat_bubble && EASYASSIST_COBROWSE_META.is_mobile == false && agent_packet.chat_type != "chat_bubble") {
                set_easyassist_current_session_local_storage_obj("new_message_seen","false");
                var chat_box = document.getElementById("chat-minimize-icon-wrapper");
                if (agent_packet.chat_type != "agent_connect_message") {
                    try { 
                        easyassist_append_chat_bubble_message(agent_packet.agent_name, agent_packet.message, agent_packet.attachment, agent_packet.attachment_file_name);
                    } catch (err) {
                        console.log(err)
                    }
                } else {
                    document.getElementById("easyassist-livechat-iframe").style.display = "block";

                    let is_current_tab_focussed = easyassist_check_current_tab_active();
                    if( is_current_tab_focussed ){
                        play_greeting_bubble_popup_sound();
                    }

                    document.getElementById("easyassist-livechat-iframe").classList.add("animate__animated");
                    document.getElementById("easyassist-livechat-iframe").classList.add("animate__slideInUp");
                    set_easyassist_current_session_local_storage_obj("new_message_seen","true");
                    if(chat_box) {
                        chat_box.style.display = "none";
                    }
                }
            }
            
            if (EASYASSIST_COBROWSE_META.enable_chat_bubble == false && document.getElementById("easyassist-livechat-iframe").style.display == "none") {
                document.getElementById("easyassist-livechat-iframe").style.display = "block";
            }

            easyassist_chat_notification(agent_packet.message,agent_packet.attachment_file_name,agent_packet.agent_name);

            allincall_chat_window = document.getElementById("easyassist-livechat-iframe").contentWindow;
            allincall_chat_window.postMessage(JSON.stringify({
                "agent_name": agent_packet.agent_name,
                "message": agent_packet.message,
                "attachment": agent_packet.attachment,
                "attachment_file_name": agent_packet.attachment_file_name,
                "show_agent_message": true,
                "sender": agent_packet.sender,
                "chat_type": agent_packet.chat_type,
                "agent_username": window.AGENT_USERNAME,
                "agent_profile_pic_source": agent_packet.agent_profile_pic_source,
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
            // query_selector = tag_name + "[easyassist-element-id='" + element_id + "']";
            // change_element = document.querySelector(query_selector);

            change_element = easyassist_get_element_from_easyassist_id(element_id);

            if(change_element == null || change_element == undefined) {
                console.log("Danger: Element does not exist");
                return;
            }

            if (tag_name == "select") {

                if (change_element.options == undefined || change_element.options == null) {
                    return;
                }

                remove_easyassist_event_listner_into_element(change_element, "change", easyassist_sync_html_element_value_change);

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
                var change_event = new Event('change');
                change_element.dispatchEvent(change_event);

                add_easyassist_event_listner_into_element(change_element, "change", easyassist_sync_html_element_value_change);

            } else if (tag_name == "input") {

                remove_easyassist_event_listner_into_element(change_element, "change", easyassist_sync_html_element_value_change);
                change_element.has_easyassist_change_event = false;

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
                change_element.has_easyassist_change_event = true;

            } else if(tag_name == "textarea") {
                change_element.value = value;

            } else {
                change_element.innerHTML = value;

            }
        } else if (agent_packet.type == "button-click") {
            easyassist_element_id = agent_packet.easyassist_element_id;
            
            var click_element = null;

            if (agent_packet.element_id != "") {
                click_element = document.getElementById(agent_packet.element_id);
            }

            if (click_element == null && easyassist_element_id != "") {
                // click_element = easyassist_tree_mirror_client.knownNodes.nodes[easyassist_element_id];
                click_element = easyassist_get_element_from_easyassist_id(easyassist_element_id);
            }

            if(click_element == null || click_element == undefined) {
                return;
            }

            if(click_element.tagName.toLowerCase() == "input") {
                remove_easyassist_event_listner_into_element(click_element, "change", easyassist_sync_html_element_value_change);
            }

            try{
                click_element.click();
            } catch(err) {
                try {
                    let mousedown_event = new MouseEvent('click', { view: window, cancelable: true, bubbles: true });
                    click_element.dispatchEvent(mousedown_event);
                } catch(err) {}
            }

            try {
                let mousedown_event = new MouseEvent('mousedown', { view: window, cancelable: true, bubbles: true });
                click_element.dispatchEvent(mousedown_event);
            } catch(err) {}

            try {
                let mousedown_event = new MouseEvent('mouseup', { view: window, cancelable: true, bubbles: true });
                click_element.dispatchEvent(mousedown_event);
            } catch(err) {}

            if(click_element.tagName.toLowerCase() == "input") {
                add_easyassist_event_listner_into_element(click_element, "change", easyassist_sync_html_element_value_change);
            }
        } else if(agent_packet.type == "end_voip_meeting") {
            if(agent_packet.auto_end_meeting) {
                show_easyassist_toast("Call ended");
            } else {
                show_easyassist_toast("Customer ended the call");
            }
            // reset_voip_meeting();
            // send_voice_call_end_meeting_over_socket();
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
        } else if (agent_packet.type == "is_meeting_active") {
            var is_cobrowse_meeting_active = get_easyassist_cookie("is_cobrowse_meeting_active");
            var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
            var cobrowsing_meeting_status = false;
            if(is_cobrowse_meeting_active == easyassist_session_id) {
                cobrowsing_meeting_status = true;
            }
            send_meeting_status_over_socket(cobrowsing_meeting_status, agent_packet.show_modal);
        } else if (agent_packet.type == "clear_meeting_cookie") {
            set_easyassist_cookie("is_cobrowse_meeting_active", "");
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
            // element = document.querySelector("[easyassist-element-id='" + element_id + "']")
            element = easyassist_get_element_from_easyassist_id(element_id);
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

            window.onclick = easyassist_send_data_to_server;
            window.onresize = easyassist_send_data_to_server;
            window.onmousedown = easyassist_send_data_to_server;
            window.onkeyup = easyassist_send_data_to_server;
            window.onscroll = easyassist_send_data_to_server;
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

            add_easyassist_event_listner_into_element(window, "beforeunload", easyassist_page_reload_action);

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
                var description = "Update Agent Assistant Request API (/easy-assist/update-agent-assistant-request/) failed with status code " + response.status + ", Invalid Verification Code";
                // save_easyassist_system_audit_trail("api_failure", description);
            }
        } else if (this.readyState == 4) {
            var description = "Update Agent Assistant Request API (/easy-assist/update-agent-assistant-request/) failed with status code " + this.status.toString();
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
    
    if( document.getElementById("chat-minimize-icon-wrapper")) {
        document.getElementById("chat-minimize-icon-wrapper").style.display = "none";
        document.getElementById("chat-talk-bubble").style.display = "none";
    }

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

    comment_desc = "";
    feedback = "";
    subcomments = "";

    if(EASYASSIST_COBROWSE_META.enable_predefined_remarks) {
        feedback = document.getElementById("close-session-remarks").value.trim();
        comment_desc = document.getElementById("easyassist-close-session-remarks").value.trim();
        
        if(EASYASSIST_COBROWSE_META.enable_predefined_subremarks) {
            subcomments = document.getElementById("easyassist-close-session-subremarks").value;
        }

        if(EASYASSIST_COBROWSE_META.predefined_remarks_optional == false) {
            if(remarks_validation(feedback, close_session_text_error_el, "Remarks", 1, 200) == "invalid"){
                return;
            }

            if(EASYASSIST_COBROWSE_META.enable_predefined_subremarks) {
                if(remarks_validation(subcomments, close_session_text_error_el, "Sub-Remarks", 1, 200) == "invalid") {
                    return;
                }
            }

            if(!comment_desc.length) {
                close_session_text_error_el.innerHTML = "Comments cannot be empty";
                close_session_text_error_el.style.display = 'block';
                return;
            }
        }

        if(feedback == "others"){

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

            if(remarks_validation(comment_desc, close_session_text_error_el, "Comments", 1, 200) == "invalid"){
                return;
            }
        } else {
            if(comment_desc && !is_input_text_valid(comment_desc)) {
                close_session_text_error_el.innerHTML = "Please enter a valid comment (Only a-z A-z 0-9 .,@ are allowed)";
                close_session_text_error_el.style.display = 'block';
                return;
            }

            if(remarks_validation(comment_desc, close_session_text_error_el, "Comments", 0, 200) == "invalid"){
                return;
            }
        }
    } else {
        feedback = document.getElementById("easyassist-close-session-remarks").value.trim();
        
        if(!feedback.length) {
            close_session_text_error_el.innerHTML = "Remarks cannot be empty";
            close_session_text_error_el.style.display = 'block';
            return;
        }

        if(!is_input_text_valid(feedback)) {
            close_session_text_error_el.innerHTML = "Please enter a valid remark (Only a-z A-z 0-9 .,@ are allowed)";
            close_session_text_error_el.style.display = 'block';
            return;
        }

        if(remarks_validation(feedback, close_session_text_error_el, "Remarks", 1, 200) == "invalid"){
            return;
        }
    }

    is_helpful = document.getElementById("easyassist-mask-successfull-cobrowsing-session").checked;

    document.getElementById("easyassist-close-session-remarks").value = "";

    json_string = JSON.stringify({
        "session_id": easyassist_session_id,
        "is_helpful": is_helpful,
        "feedback": feedback,
        "subcomments": subcomments,
        "comment_desc": comment_desc,
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
                var description = "Submit client feedback API (/easy-assist/submit-client-feedback/) failed with status code " + response.status;
                // save_easyassist_system_audit_trail("api_failure", description);
            }

            terminate_easyassist_cobrowsing_session();
        } else if (this.readyState == 4) {
            var description = "Submit client feedback API (/easy-assist/submit-client-feedback/) failed with status code " + this.status.toString();
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
                hide_floating_mobile_sidenav_menu();
                return;
            } else {
                show_floating_sidenav_menu();
            }

            window.AGENT_NAME = response["agent_name"];
            window.AGENT_USERNAME = response["agent_username"];
            window.AGENT_PROFILE_PIC_SOURCE = response["agent_profile_pic_source"];

        }
    }
    xhttp.send(params);
}

function easyassist_send_attachment_to_agent_for_validation(event){

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
                "base64_file": base64_str,
                "session_id": easyassist_session_id,
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
                      send_livechat_message_to_agent("uploaded attachment", response["file_path"], file.name, "chat_message");
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
        show_easyassist_toast("Edit Access has been revoked by the customer");
    else
        show_easyassist_toast("Edit Access has been revoked from customer");
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
                    var is_admin_message = chat_history[index]["is_admin_message"];
                    sender_name = chat_history[index]["sender_name"]; 
                    var time = datetime.split(" ")[3] + " " + datetime.split(" ")[4];
                    attachment = chat_history[index]["attachment"];
                    attachment_file_name = chat_history[index]["attachment_file_name"];
                    var chat_type = chat_history[index]["chat_type"];
                    agent_profile_pic_source = chat_history[index]["agent_profile_pic_source"]
                    if(sender == "client") {
                        allincall_chat_window.postMessage(JSON.stringify({
                            "agent_name": response.client_name,
                            "message": message,
                            "attachment": attachment,
                            "attachment_file_name": attachment_file_name,
                            "show_agent_message": true,
                            "time": time,
                            "sender": sender,
                            "chat_type": chat_type,
                            "agent_profile_pic_source": agent_profile_pic_source,
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
                                "chat_type": chat_type,
                                "agent_profile_pic_source": agent_profile_pic_source,
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
                                "chat_type": chat_type,
                                "agent_profile_pic_source": agent_profile_pic_source,
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

function send_invited_agent_meeting_request() {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    var is_cobrowse_meeting_active = get_easyassist_cookie("is_cobrowse_meeting_active");
    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    var is_call_ongoing = false;
    if(is_cobrowse_meeting_active == easyassist_session_id) {
        is_call_ongoing = true;
    }

    json_string = JSON.stringify({
        "type": "invited_agent_call_request",
        "is_call_ongoing": is_call_ongoing
    });

    encrypted_data = easyassist_custom_encrypt(json_string)
    encrypted_data = {
        "Request": encrypted_data
    };

    easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
}

function send_meeting_status_over_socket(cobrowsing_meeting_status, show_modal) {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    json_string = JSON.stringify({
        "type": "is_meeting_active_response",
        "is_meeting_active": cobrowsing_meeting_status,
        "show_modal": show_modal
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
    easyassist_change_options_visiblity();

    var message = "Agent " + window.AGENT_NAME + " has joined the chat";
    append_agent_message_into_chatbox(message, "None", "None", "chat_bubble");

    setTimeout(function(){
        message = EASYASSIST_COBROWSE_META.agent_connect_message;
        message = message.replaceAll("agent_name", window.AGENT_NAME);

        if(EASYASSIST_COBROWSE_META.enable_agent_connect_message == true){
            append_agent_message_into_chatbox(message, "None", "None", "agent_connect_message");
        }
    }, 2000)
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

    easyassist_avg_speed_mbps = 0;

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

function easyassist_set_input_element_value(screenshot, is_capture_screenshot_callback=false) {

    try {

        var element_list = screenshot.getElementsByTagName("*")
        for(let idx = 0; idx < element_list.length; idx ++) {

            var active_element = element_list[idx];

            var element_value = easyassist_get_input_element_value(active_element, is_capture_screenshot_callback=is_capture_screenshot_callback);

            var tag_name = active_element.tagName;
            var tag_type = active_element.getAttribute("type");

            if(element_value == null || (element_value.length != 2) || (element_value[1] == null)) {
                continue;
            }

            var is_obfuscated_element = element_value[0];
            var new_value = element_value[1];

            if(tag_type == "number") {
                active_element.type = "text";
            }

            if(tag_name == "INPUT") {
                if(tag_type == "checkbox" || tag_type == "radio") {
                    if(new_value == true) {
                        active_element.setAttribute("checked", "checked");
                    } else {
                        active_element.removeAttribute("checked");
                    }
                } else {
                    active_element.setAttribute("value", new_value);
                    active_element.value = new_value;
                }
            } else if(tag_name == "SELECT") {
                if(is_obfuscated_element) {
                    var option = '<option value="' + new_value + '">' + new_value + ' </option>';
                    active_element.innerHTML += option;
                }

                for(let index = 0; index < active_element.options.length; index ++) {
                    active_element.options[index].removeAttribute("selected");
                    if (active_element.options[index].value == element_value) {
                        active_element.options[index].setAttribute("selected", "selected");
                    }
                }

            } else if(tag_name == "TEXTAREA") {
                active_element.value = new_value;
                active_element.innerHTML = new_value;
            } else if(is_obfuscated_element && is_capture_screenshot_callback) {
                active_element.textContent = new_value;
            }
        }

        var masked_elements = screenshot.getElementsByClassName("easyassist-blured-element");
        for(let idx = 0; idx < masked_elements.length; idx ++) {
            masked_elements[idx].style.setProperty("border", "none", "important");
            masked_elements[idx].style.setProperty("box-shadow", "0 0 10px white", "important");
            masked_elements[idx].style.setProperty("color", "transparent", "important");
        }

    } catch(err) {
        console.log("easyassist_set_input_element_value: ", err);
    }
}

function easyassist_capture_client_screenshot() {
    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    hide_easyassist_capture_screenshot_modal();

    if(easyassist_is_url_restricted()){
        show_easyassist_toast("Screenshots are not allowed for restricted URLs")
        return;
    }

    var body = document.body;
    let doc_html = document.documentElement;
    var new_body_height = Math.max(body.scrollHeight, body.offsetHeight,
        doc_html.clientHeight, doc_html.scrollHeight, doc_html.offsetHeight);

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
            easyassist_set_input_element_value(clone_document_node, true);
        },
        ignoreElements: function(element) {
            return easyassist_check_dom_node(element);
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
        captured_information_modal_info.style.setProperty("display", "block", "important");
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
                captured_information_modal_info.style.setProperty("display", "none", "important");

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
                                    '<a href="' + EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + '/easy-assist/download-file/' + meta_id + '/?session_id=' + easyassist_session_id + '" download title="Export As Image">',
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
                } else {
                    captured_information_modal_info.innerHTML = "No screenshots";
                    captured_information_modal_info.style.setProperty("display", "block", "important");
                    document.getElementById("easyassist-captured-screenshot-view-table-div").style.display = "none";
                }
            } else {
                captured_information_modal_info.innerHTML = "Unable to load the details. Please try again.";
                captured_information_modal_info.style.setProperty("display", "block", "important");
                document.getElementById("easyassist-captured-screenshot-view-table-div").style.display = "none";
            }
            load_more_meta = false;
        } else if (this.readyState == 4){
            captured_information_modal_info.innerHTML = "Unable to load the details. Please try again.";
            captured_information_modal_info.style.setProperty("display", "block", "important");
            document.getElementById("easyassist-captured-screenshot-view-table-div").style.display = "none";
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

                        div_inner_html += [
                            '<tr>',
                                '<td style="vertical-align:middle;min-width: 7.5em;"> <a  class="support-document-link" href="' + file_path + '" target="_blank" style="color:'+EASYASSIST_COBROWSE_META.floating_button_bg_color+';" >' + file_name + '</a> </td>',
                                '<td> <input class="support-document-message-text" type="text" value="' + message + '" style="width: 100% !important;"> </td>',
                                '<td style="text-align: center;vertical-align: middle;">',
                                    '<button class="eassyassist-modal-send-support-document-button" onclick="easyassist_send_support_material_doc(this)">',
                                        '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                            '<path d="M15.6377 7.40491L0.988524 0.070419C0.873708 0.0129211 0.744741 -0.0101171 0.617152 0.00407857C0.489563 0.0182742 0.368792 0.0690985 0.269381 0.150432C0.174443 0.230106 0.103582 0.334718 0.064764 0.452509C0.0259456 0.570299 0.0207089 0.696597 0.0496425 0.817204L1.81421 7.33157H9.34524V8.66511H1.81421L0.0230075 15.1595C-0.00414248 15.2602 -0.00731172 15.3659 0.0137547 15.4681C0.0348212 15.5702 0.0795356 15.666 0.144302 15.7477C0.209069 15.8294 0.292081 15.8948 0.386663 15.9386C0.481246 15.9823 0.584759 16.0032 0.688881 15.9996C0.793118 15.999 0.895753 15.9739 0.988524 15.9263L15.6377 8.59177C15.7468 8.53581 15.8383 8.4508 15.9023 8.3461C15.9662 8.24139 16 8.12106 16 7.99834C16 7.87562 15.9662 7.75528 15.9023 7.65058C15.8383 7.54588 15.7468 7.46087 15.6377 7.40491Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                                        '</svg>',
                                    '</button>',
                                '</td>',
                            '</tr>',

                        ].join('');


                        document.getElementById("easyassist-support-document-div").querySelector('tbody').innerHTML = div_inner_html;
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


function append_agent_message_into_chatbox(message, attachment, attachment_file_name, chat_type) {
    allincall_chat_window.postMessage(JSON.stringify({
        "agent_name": window.AGENT_NAME,
        "agent_profile_pic_source": window.AGENT_PROFILE_PIC_SOURCE,
        "message": message,
        "attachment": attachment,
        "attachment_file_name": attachment_file_name,
        "show_client_message": true,
        "sender": window.AGENT_USERNAME,
        "chat_type": chat_type,
    }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);
    send_livechat_message_to_agent(message, attachment, attachment_file_name, chat_type);
}

function easyassist_send_support_material_doc(element) {
    var action_cell = element.parentElement;
    var message_cell = action_cell.previousElementSibling;
    var attachment_cell = message_cell.previousElementSibling;

    var attachment = attachment_cell.children[0].href;
    attachment = stripHTML(attachment);

    var message = message_cell.children[0].value;
    if (check_text_link(message) == false) {
        message = stripHTML(message);
        message = remove_special_characters_from_str(message);
    } else {
        message = easyassist_linkify(perform_url_encoding(message));
    }

    var attachment_file_name = attachment_cell.children[0].text;
    attachment_file_name = stripHTML(attachment_file_name);
    attachment_file_name = remove_special_characters_from_str(attachment_file_name)

    append_agent_message_into_chatbox(message, attachment, attachment_file_name, "chat_message");

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
    bug_description = stripHTML(bug_description);
    if (bug_description == "") {
        error_element.innerHTML = "Please describe your issue in above textbox."
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

function easyassist_get_element_from_easyassist_id(element_id) {
    var element = null;

    try {
        element = easyassist_tree_mirror_client.knownNodes.nodes[element_id];
    } catch(err) {
        console.log("easyassist_get_element_from_easyassist_id: ", err);
    }

    return element;
}

function easyassist_get_easyassist_id_from_element(element) {
    var element_id = null;

    try {
        if(easyassist_tree_mirror_client != null) {
            element_id = easyassist_tree_mirror_client.knownNodes.get(element);
        }
    } catch(err) {
        console.log("easyassist_get_easyassist_id_from_element: ", err);
    }
    return element_id;
}

function easyassist_send_canvas_coordinates_to_socket(prev_x, prev_y, curr_x, curr_y, line_width, shape) {
    try {
        json_string = JSON.stringify({
            "type": "sync_canvas",
            "prev_x": prev_x,
            "prev_y": prev_y,
            "curr_x": curr_x,
            "curr_y": curr_y,
            "line_width": line_width,
            "shape": shape,
        });

        encrypted_data = easyassist_custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };

        easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
    } catch(err) {
        console.log("easyassist_send_canvas_coordinates_to_socket: ", err);
    }
}

function easyassist_send_reset_canvas_over_socket() {
    try {
        json_string = JSON.stringify({
            "type": "reset_canvas",
        });

        encrypted_data = easyassist_custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };

        easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
    } catch(err) {
        console.log("easyassist_send_reset_canvas_over_socket: ", err);
    }
}

function easyassist_resize_easyassist_canvas() {
    try {
        easyassist_drawing_canvas.resize_canvas(window.innerWidth, window.innerHeight);
    } catch(err) {
        console.log("easyassist_resize_easyassist_canvas: ", err);
    }
}

// function send_call_initiate_notification() {

//     json_string = JSON.stringify({
//         "type": "voice_call_triggered",
//     });

//     encrypted_data = easyassist_custom_encrypt(json_string)
//     encrypted_data = {
//         "Request": encrypted_data
//     };

//     easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
// }

// function send_voice_call_end_meeting_over_socket(){
//     json_string = JSON.stringify({
//         "type": "reset_cookies",
//     });

//     encrypted_data = easyassist_custom_encrypt(json_string)
//     encrypted_data = {
//         "Request": encrypted_data
//     };

//     easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
// }
/************************* START DEBUG UTILS *************************/

function easyassist_is_invalid(node){
    var easyassist_element_id = node.__mutation_summary_node_map_id__;
    var mutation_id = easyassist_tree_mirror_client.knownNodes.get(node)
    // var element = easyassist_tree_mirror.idMap[easyassist_element_id];
    if(easyassist_element_id != mutation_id){
        console.log("---------------------------------");
        console.log("node = ", node);
        console.log("easyassist_element_id = ", easyassist_element_id);
        console.log("mutation_id = ", mutation_id);
    }
    return easyassist_element_id != mutation_id;
}

function easyassist_is_map_invalid(node=null){
    if(node==null){
        var doc_html = document.documentElement;
        node=doc_html;
    }

    if(easyassist_check_dom_node(node) == true) return false;

    var flag = easyassist_is_invalid(node);
    for(let index=0 ; index<node.children.length ; index++){
        flag |= easyassist_is_map_invalid(node.children[index]);
    }

    return flag;
}

/************************* END DEBUG UTILS *************************/


function easyassist_get_restricted_data_packet(){
    json_string = JSON.stringify({
        "type": "restricted_url",
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    var message = {
        "Request": encrypted_data
    };

    return message;
}

function easyassist_create_local_storage_obj() {
    if(localStorage.getItem("easyassist_session") == null){
        var local_storage_json_object = {};
        var COBROWSE_SESSION_ID = get_easyassist_cookie("easyassist_session_id");
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
        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

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
        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

        if(local_storage_obj) {
            local_storage_obj = JSON.parse(local_storage_obj);
            local_storage_obj[easyassist_session_id][key] = value;
            localStorage.setItem("easyassist_session", JSON.stringify(local_storage_obj));
        }
    }catch(err){
        console.log("ERROR: set_easyassist_current_session_local_storage_obj ", err);
    }
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
    play_greeting_bubble_popup_sound();

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
        document.querySelector(".chat-talk-bubble").classList.remove("bounce2");
    },1500);
}

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

function easyassist_page_reload_action() {
    try {
        easyassist_send_tab_close_over_socket();
    } catch(err) {
        console.log("easyassist_page_reload_action: ", err);
    }
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