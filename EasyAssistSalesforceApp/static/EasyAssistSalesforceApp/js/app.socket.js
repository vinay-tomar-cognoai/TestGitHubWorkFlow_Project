var EASYASSIST_SESSION_ID = null;
var check_for_agent_assistance = null;
var client_heartbeat_timer = null;
var is_agent_connected = false;
var client_websocket = null;
var client_websocket_open = false;
var hidden_element_count = null;
var EASYASSIST_TAG_LIST = ["input", "select", "textarea", "div", "span", "label"];
var check_for_agent_guide_timer = null;
var html_page_counter = 0;
var session_closed_by_agent = false;
var is_cobrowse_meeting_on = false;
var agent_mouse_top = 0;
var agent_mouse_left = 0;
var agent_revoke_edit_access = false;
function start_cobrowsing_activity_check() {
    var check_cobrowse_session_timer = setInterval(function(e) {
        if (get_easyassist_cookie("easyassist_session_id") != undefined) {
            clearTimeout(check_cobrowse_session_timer);
            EASYASSIST_SESSION_ID = get_easyassist_cookie("easyassist_session_id");
            initiate_cobrowsing();
        }
    }, 1000);
}

/*WebSocket Utilities - Starts*/

function reset_easyassist_global_var() {
    EASYASSIST_SESSION_ID = null;
    check_for_agent_assistance = null;
    client_heartbeat_timer = null;
    is_agent_connected = false;
    client_websocket = null;
    client_websocket_open = false;
    hidden_element_count = null;
    session_closed_by_agent = false;
}

function open_easyassist_websocket() {
    client_websocket_open = true;
    //console.log("easyassist WebSocket is opened");
    sync_html_data();
}

function close_easyassist_websocket() {
    client_websocket_open = false;
    client_websocket = null;
    //console.log("easyassist WebSocket is closed");
    var description = "WebSocket is closed at client side";
    // save_easyassist_system_audit_trail("socket", description);
}

function check_socket_status(e) {
    console.error("WebSocket error observed:", e);
    var description = "error occured client websocket. " + e.data;
    // save_easyassist_system_audit_trail("socket", description);
}

function close_easyassist_socket() {
    if (client_websocket == null) {
        return;
    }
    client_websocket.close();
}

function create_easyassist_socket(jid, sender) {
    ws_scheme = EASYASSIST_HOST_PROTOCOL == "http" ? "ws" : "wss"
    url = ws_scheme + '://' + EASYASSIST_COBROWSE_HOST + '/ws/cobrowse/' + jid + '/' + sender + "/";
    if(client_websocket == null){
        client_websocket = new WebSocket(url);
        client_websocket.onmessage = check_for_agent_guide;
        client_websocket.onerror = check_socket_status;
        client_websocket.onopen = open_easyassist_websocket;
        client_websocket.onclose = close_easyassist_websocket;
    }
    //console.log("socket has been created");
}

var packet_counter = 0;

function send_message_over_easyassist_socket(message, sender) {

    var allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;

    if (allow_cobrowsing == false) {
        return;
    }

    if (client_websocket_open && client_websocket != null) {

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
    } else {
        easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
        if (easyassist_session_id != null && easyassist_session_id != undefined && client_websocket == null) {
            create_easyassist_socket(easyassist_session_id, "client");
        }
    }
}

/*WebSocket Utilities - Closes*/

function terminate_easyassist_cobrowsing_session() {

    json_string = JSON.stringify({
        "type": "end_session",
    });

    encrypted_data = custom_encrypt(json_string)
    encrypted_data = {
        "Request": encrypted_data
    };

    if (client_websocket == null) {
        create_easyassist_socket(easyassist_session_id, "client");
        json_string = JSON.stringify({
            "type": "end_session",
        });

        encrypted_data = custom_encrypt(json_string)
        encrypted_data = {
            "Request": encrypted_data
        };
    }

    send_message_over_easyassist_socket(encrypted_data, "client");

    EASYASSIST_COBROWSE_META.allow_cobrowsing = false;
    if (client_heartbeat_timer != null && client_heartbeat_timer != undefined) {
        clearInterval(client_heartbeat_timer);
    }
    document.getElementById("agent-mouse-pointer").style.display = "none";
    close_easyassist_socket();
    delete_easyassist_cookie("easyassist_session_id");
    delete_easyassist_cookie("easyassist_agent_connected");
    delete_easyassist_cookie("easyassist_cobrowsing_allowed");
    delete_easyassist_cookie("easyassist_edit_access");
    delete_easyassist_cookie("easyassist_customer_id");
    show_floating_sidenav_easyassist_button();
    hide_floating_sidenav_menu();
    hide_easyassist_feedback_form();
    reset_easyassist_global_var();
    hide_easyassist_livechat_iframe();
    refresh_easyassist_livechat_iframe();
    add_easyassist_formassist_stuck_timer_handler();
    show_easyassist_toast("Session has ended.");
    start_cobrowsing_activity_check();
    document.getElementsByClassName("easyassist-tooltiptext")[0].style.display = "none";
}

// function mark_client_disconnected() {

//     var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

//     if (easyassist_session_id == null || easyassist_session_id == undefined) {
//         return;
//     }

//     json_string = JSON.stringify({
//         "id": easyassist_session_id
//     });

//     encrypted_data = custom_encrypt(json_string);
//     encrypted_data = {
//         "Request": encrypted_data
//     };
//     var params = JSON.stringify(encrypted_data);
//     var xhttp = new XMLHttpRequest();
//     xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist-salesforce/close-session/", true);
//     xhttp.setRequestHeader('Content-Type', 'application/json');
//     xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
//     xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
//     xhttp.onreadystatechange = function() {
//         if (this.readyState == 4 && this.status == 200) {
//             response = JSON.parse(this.responseText);
//             response = custom_decrypt(response.Response);
//             response = JSON.parse(response);
//             if (response.status == 200) {
//                 terminate_easyassist_cobrowsing_session();
//             }
//         }
//     }
//     xhttp.send(params);
// }

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

    hidden_element_count = count_hidden_element_in_document(EASYASSIST_TAG_LIST);

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
        encrypted_data = custom_encrypt(json_string);
    }

    encrypted_data = {
        "is_encrypted": is_encrypted,
        "html_page_counter": html_page_counter,
        "Request": encrypted_data
    };

    if (client_websocket == null) {
        create_easyassist_socket(easyassist_session_id, "client");
    }

    send_message_over_easyassist_socket(encrypted_data, "client");

    html_page_counter += 1;
}

function delay_sync_html_data() {
    setTimeout(function(e) {
        sync_html_data();
    }, 500);
}

/*function sync_html_data(){

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if(easyassist_session_id==null || easyassist_session_id==undefined){
        return;
    }

    var screenshot = screenshot_page();
    // screenshot = EasyAssistLZString.compress(screenshot);

    hidden_element_count = count_hidden_element_in_document(EASYASSIST_TAG_LIST);

    var total_length = screenshot.length;
    var start_index = 0;
    var chunk_index = 0;
    var chunk_length = 6000;

    while(start_index < total_length){

        is_last_chunk = false;

        if(start_index + chunk_length >= total_length){
            is_last_chunk = true;
        }

        chunk = screenshot.substring(start_index, start_index + chunk_length);

        json_string = JSON.stringify({
            "type": "html",
            "page": html_page_counter,
            "chunk": chunk_index,
            "is_chunk": true,
            "is_last_chunk": is_last_chunk,
            "html": chunk,
            "id": EASYASSIST_SESSION_ID,
            "active_url": window.location.href
        });

        encrypted_data = custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        if(client_websocket==null){
            create_easyassist_socket(easyassist_session_id, "client");
        }

        send_message_over_easyassist_socket(encrypted_data, "client");
        start_index += chunk_length;
        chunk_index += 1;
    }

    html_page_counter += 1;
}*/

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

    });

    encrypted_data = custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    if (client_websocket == null) {
        create_easyassist_socket(easyassist_session_id, "client");
    }

    send_message_over_easyassist_socket(encrypted_data, "client");
}


function sync_scroll_position() {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }
    document.getElementById("agent-mouse-pointer").style.top = window.scrollY+ agent_mouse_top + "px" ;
    document.getElementById("agent-mouse-pointer").style.left = window.scrollX + agent_mouse_left + "px";
    json_string = JSON.stringify({
        "type": "scroll",
        "active_url": window.location.href,
        "data_scroll_x": window.scrollX,
        "data_scroll_y": window.scrollY
    });

    encrypted_data = custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    if (client_websocket == null) {
        create_easyassist_socket(easyassist_session_id, "client");
    }

    send_message_over_easyassist_socket(encrypted_data, "client");
}

function notify_agent_lead_is_converted() {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    var is_converted = true;

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        is_converted = false;
    }

    json_string = JSON.stringify({
        "type": "lead_status",
        "is_converted": is_converted
    });

    encrypted_data = custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    if (client_websocket == null) {
        create_easyassist_socket(easyassist_session_id, "client");
    }

    send_message_over_easyassist_socket(encrypted_data, "client");
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

    tag_name_list = ["span", "label", "input", "select", "textarea"];

    var html_elements_value_list = [];

    for (var tag_index = 0; tag_index < tag_name_list.length; tag_index++) {

        tag_elements = document.getElementsByTagName(tag_name_list[tag_index]);

        for (var tag_element_index = 0; tag_element_index < tag_elements.length; tag_element_index++) {

            if (tag_elements[tag_element_index].offsetParent == null) {
                continue;
            }

            tag_name = tag_elements[tag_element_index].tagName;
            element_id = tag_elements[tag_element_index].getAttribute("easyassist-element-id");
            tag_type = tag_elements[tag_element_index].getAttribute("type");
            value = tag_elements[tag_element_index].value;

            if (tag_name.toLowerCase() == "select") {
                var selected_option = tag_elements[tag_element_index].options[tag_elements[tag_element_index].selectedIndex];
                if (selected_option != null && selected_option != undefined) {
                    var selected_option_inner_html = selected_option.innerHTML;
                    var selected_option_value = selected_option.value;
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

            obfuscated_fields = window.EASYASSIST_COBROWSE_META.obfuscated_fields;
            var is_obfuscated_element = false;
            var element_masking_type = "no-masking";
            for (var mask_index = 0; mask_index < obfuscated_fields.length; mask_index++) {
                element_value = tag_elements[tag_element_index].getAttribute(obfuscated_fields[mask_index]["key"]);
                if (element_value != null && element_value != undefined && element_value == obfuscated_fields[mask_index]["value"]) {
                    is_obfuscated_element = true;
                    element_masking_type = obfuscated_fields[mask_index]["masking_type"];
                    break;
                }
            }

            var is_numeric = false;
            if (is_obfuscated_element == false && isNaN(parseInt(value.toString())) == false) {
                is_numeric = true;
            }

            if (is_obfuscated_element) {
                value = easyassist_obfuscate(value.toString(), element_masking_type.toString());
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

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    if (client_websocket == null) {
        create_easyassist_socket(easyassist_session_id, "client");
    }

    send_message_over_easyassist_socket(encrypted_data, "client");
}

function send_data_to_server(event) {

    hide_easyassist_ripple_effect();

    setTimeout(function(e) {

        if (event.type == "scroll") {
            sync_scroll_position();
        } else if (event.type == "resize") {
            sync_html_data();
        } else {
            tag_name = document.activeElement.tagName;
            var temp_count = count_hidden_element_in_document(EASYASSIST_TAG_LIST);
            if (temp_count != hidden_element_count) {
                hidden_element_count = temp_count;
                sync_html_data();
            } else if (tag_name.toLowerCase() == "input") {
                sync_html_element_value_change();
            } else if (tag_name.toLowerCase() == "select") {
                sync_html_element_value_change();
            } else if (tag_name.toLowerCase() == "textarea") {
                sync_html_element_value_change();
            } else {
                //console.log("active element tag: ", tag_name);
            }
        }

    }, 1000);

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

    encrypted_data = custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "client");
}


function client_heartbeat() {

    var temp_count = count_hidden_element_in_document(EASYASSIST_TAG_LIST);

    if (temp_count != hidden_element_count) {
        hidden_element_count = temp_count;
        sync_html_data();
        return;
    }

    json_string = JSON.stringify({
        "type": "heartbeat",
        "active_url": window.location.href
    });

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "client");
}

function sync_client_scroll_position(agent_packet){

    scrollX = agent_packet.data_scroll_x;
    scrollY = agent_packet.data_scroll_y;
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
        agent_packet = custom_decrypt(agent_packet);
        agent_packet = JSON.parse(agent_packet);
    }

    if (message.header.sender == "agent") {

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

                for (var option_index = 0; option_index < change_element.options.length; option_index++) {
                    change_element.options[option_index].removeAttribute("selected");
                    if (change_element.options[option_index].innerHTML == value) {
                        change_element.options[option_index].setAttribute("selected", "selected");
                    }
                }

                // try {
                //     change_element_id = change_element.getAttribute("id");
                //     $("#"+change_element_id).change();
                //     delay_sync_html_data();
                // } catch(err) {}

            } else if (tag_name == "input") {

                if (tag_type == "checkbox") {
                    change_element.click();
                } else if (tag_type == "radio") {
                    change_element.checked = value;
                } else {
                    change_element.value = value;
                }

                // try {
                //     change_element_id = change_element.getAttribute("id");
                //     $("#"+change_element_id).change();
                // } catch(err) {}

            } else {

                change_element.innerHTML = value;
                // try{
                //     change_element_id = change_element.getAttribute("id");
                //     $("#"+change_element_id).change();
                // } catch(err) {}
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
        }

    } else {

        return;

    }
}

function initiate_cobrowsing() {
    easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if (easyassist_session_id != undefined && EASYASSIST_SESSION_ID != null) {
        hide_floating_sidenav_easyassist_button();
        remove_easyassist_formassist_stuck_timer_handler();
        create_easyassist_socket(easyassist_session_id, "client");
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

        try {
            var MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver;
            var observer = new MutationObserver(function(e) {
                delay_sync_html_data();
            });

            observer.observe(document.body, {
                childList: true
            });
        } catch (err) {
            console.warn(err);
        }
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

        if (EASYASSIST_COBROWSE_META.choose_product_category == true) {
            show_easyassist_product_category_modal();
        } else {
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

    if (EASYASSIST_COBROWSE_META.field_stuck_event_handler == false) {
        return;
    }

    window.addEventListener("mousemove", reset_easyassist_element_stuck_timer, true);

    form_input_elements = document.getElementsByTagName("input");
    for (var index = 0; index < form_input_elements.length; index++) {
        if (form_input_elements[index].getAttribute("class") == "easyassist-input-field") {
            continue;
        }
        form_input_elements[index].addEventListener("focusin", reset_easyassist_element_stuck_timer, true);
        form_input_elements[index].addEventListener("keypress", reset_easyassist_element_stuck_timer, true);
    }

    form_textarea_elements = document.getElementsByTagName("textarea");
    for (var index = 0; index < form_textarea_elements.length; index++) {
        form_textarea_elements[index].addEventListener("focusin", reset_easyassist_element_stuck_timer, true);
        form_textarea_elements[index].addEventListener("keypress", reset_easyassist_element_stuck_timer, true);
    }

    form_select_elements = document.getElementsByTagName("select");
    for (var index = 0; index < form_select_elements.length; index++) {
        form_select_elements[index].addEventListener("mousedown", reset_easyassist_element_stuck_timer, true);
        form_select_elements[index].addEventListener("change", reset_easyassist_element_stuck_timer, true);
    }
}

function remove_easyassist_formassist_stuck_timer_handler() {

    window.removeEventListener("mousemove", reset_easyassist_element_stuck_timer, true);

    form_input_elements = document.getElementsByTagName("input");
    for (var index = 0; index < form_input_elements.length; index++) {
        form_input_elements[index].removeEventListener("focusin", reset_easyassist_element_stuck_timer, true);
        form_input_elements[index].removeEventListener("keypress", reset_easyassist_element_stuck_timer, true);
    }
    form_textarea_elements = document.getElementsByTagName("textarea");
    for (var index = 0; index < form_textarea_elements.length; index++) {
        form_textarea_elements[index].removeEventListener("focusin", reset_easyassist_element_stuck_timer, true);
        form_textarea_elements[index].removeEventListener("keypress", reset_easyassist_element_stuck_timer, true);
    }
    form_select_elements = document.getElementsByTagName("select");
    for (var index = 0; index < form_select_elements.length; index++) {
        form_select_elements[index].removeEventListener("mousedown", reset_easyassist_element_stuck_timer, true);
        form_select_elements[index].removeEventListener("change", reset_easyassist_element_stuck_timer, true);
    }
}

setTimeout(function(e) {
    add_easyassist_formassist_stuck_timer_handler();
    show_floating_sidenav_easyassist_button();
    update_easyassist_url_history();
}, 2000);


function capture_client_pageshot() {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    var screenshot = screenshot_page();

    json_string = JSON.stringify({
        "id": easyassist_session_id,
        "content": screenshot,
        "type_screenshot": "pageshot"
    });

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist-salesforce/capture-client-screen/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status != 200) {
                var description = "Capture client pageshot API (/easy-assist-salesforce/capture-client-screen/) failed with status code " + response.status;
                // save_easyassist_system_audit_trail("api_failure", description);
            }

            json_string = JSON.stringify({
                "type": "pageshot",
                "active_url": window.location.href,
                "result": response.status
            });

            encrypted_data = custom_encrypt(json_string);

            encrypted_data = {
                "Request": encrypted_data
            };

            if (client_websocket == null) {
                create_easyassist_socket(easyassist_session_id, "client");
            }

            send_message_over_easyassist_socket(encrypted_data, "client");

            //console.log("client pageshot saved");
        } else if (this.readyState == 4) {
            var description = "Capture client pageshot API (/easy-assist-salesforce/capture-client-screen/) failed with status code " + this.status.toString();
            // save_easyassist_system_audit_trail("api_failure", description);
        }
    }
    xhttp.send(params);
}

function capture_client_screenshot() {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    document.querySelector("#easyassist-ripple_effect").style.border = "none";

    html2canvas(document.querySelector("body")).then(function(canvas) {
        // Get base64URL
        img_data = canvas.toDataURL('image/png');
        var screenshot = screenshot_page();
        json_string = JSON.stringify({
            "id": easyassist_session_id,
            "content": img_data,
            "type_screenshot": "screenshot"
        });

        encrypted_data = custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        var params = JSON.stringify(encrypted_data);
        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist-salesforce/capture-client-screen/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
        xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response.Response);
                response = JSON.parse(response);

                json_string = JSON.stringify({
                    "type": "screenshot",
                    "active_url": window.location.href,
                    "result": response.status
                });

                encrypted_data = custom_encrypt(json_string);

                encrypted_data = {
                    "Request": encrypted_data
                };

                if (client_websocket == null) {
                    create_easyassist_socket(easyassist_session_id, "client");
                }

                send_message_over_easyassist_socket(encrypted_data, "client");

                if (response.status != 200) {
                    var description = "Capture client screenshot API (/easy-assist-salesforce/capture-client-screen/) failed with status code " + response.status;
                    // save_easyassist_system_audit_trail("api_failure", description);
                }

                //console.log("client screenshot saved");
            } else if (this.readyState == 4) {
                var description = "Capture client screenshot API (/easy-assist-salesforce/capture-client-screen/) failed with status code " + this.status.toString();
                // save_easyassist_system_audit_trail("api_failure", description);
            }
            document.querySelector("#easyassist-ripple_effect").style.border = "1px solid red";
        }
        xhttp.send(params);
    });
}

////////////////////////////   Screen sharing cobrowse //////////////

function go_to_sceensharing_tab(response) {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }
    if(response.allow_screen_sharing_cobrowse == true || response.allow_screen_sharing_cobrowse == "true") {

        window.open(EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + '/easy-assist-salesforce/screensharing-cobrowse/?id=' + easyassist_session_id, '_blank');
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
        verify_inputs = document.getElementsByClassName("easyassist-verfication-otp-input")
        for (var i = 0; i < verify_inputs.length; i++) {
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

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist-salesforce/update-agent-assistant-request/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
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
                var description = "Update Agent Assistant Request API (/easy-assist-salesforce/update-agent-assistant-request/) failed with status code " + response.status + ", Invalid Verification Code";
                // save_easyassist_system_audit_trail("api_failure", description);
            }
        } else if (this.readyState == 4) {
            var description = "Update Agent Assistant Request API (/easy-assist-salesforce/update-agent-assistant-request/) failed with status code " + this.status.toString();
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

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist-salesforce/update-agent-meeting-request/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
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

function submit_client_feedback(feedback_type) {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    var rating = "None";
    if(feedback_type!="no_feedback"){
        if (window.EASYASSIST_CLIENT_FEEDBACK == null) {
            return;
        }
        rating = window.EASYASSIST_CLIENT_FEEDBACK;
    }
    window.EASYASSIST_CLIENT_FEEDBACK = null;

    feedback = document.getElementById("easyassist-client-feedback").value;

    json_string = JSON.stringify({
        "session_id": easyassist_session_id,
        "rating": rating,
        "feedback": feedback
    });

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist-salesforce/submit-client-feedback/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status != 200) {
                var description = "Submit client feedback API (/easy-assist-salesforce/submit-client-feedback/) failed with status code " + response.status;
                // save_easyassist_system_audit_trail("api_failure", description);
            }

            terminate_easyassist_cobrowsing_session();
        } else if (this.readyState == 4) {
            var description = "Submit client feedback API (/easy-assist-salesforce/submit-client-feedback/) failed with status code " + this.status.toString();
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

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist-salesforce/sync/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
        }
    }
    xhttp.send(params);
}

function open_meeting_window(){
        set_easyassist_cookie("is_cobrowse_meeting_on", "true");
        var session_id = get_easyassist_cookie("easyassist_session_id")
        var url = EASYASSIST_COBROWSE_META.easyassist_host + "/easy-assist-salesforce/meeting/" +session_id + "?is_meeting_cobrowsing=true"
        window.open(url, "_blank");
    }

function check_for_agent_highlight() {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    var allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    json_string = JSON.stringify({
        "id": easyassist_session_id
    });

    encrypted_data = custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist-salesforce/highlight/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status == 500) {
                clearInterval(check_for_agent_guide_timer);
                terminate_easyassist_cobrowsing_session();
                return;
            }
            
            if (response.status != 200) {
                clearInterval(check_for_agent_guide_timer);
                // terminate_easyassist_cobrowsing_session();
                var description = "Client activity check API (/easy-assist-salesforce/highlight/) failed with status code " + response.status;
                // save_easyassist_system_audit_trail("api_failure", description);
                return;
            }

            if (response.is_session_closed == true) {
                console.log("session closed due to inactivity");
                show_easyassist_toast("Session closed due to inactivity.");
                terminate_easyassist_cobrowsing_session();
                return;
            }

            if (response.is_archived == true) {
                console.log("session closed by agent");
                // terminate_easyassist_cobrowsing_session();
                if(session_closed_by_agent == false) {
                    session_closed_by_agent = true;
                    show_easyassist_toast(response.agent_name + " has ended the session.");
                    document.getElementById("agent-mouse-pointer").style.display = "none";
                    hide_floating_sidenav_menu();
                    show_easyassist_feedback_form();
                }
                return;
            }

            try {
                if (response.agent_name != null) {
                    document.getElementById("easyassist-agent-information-agent-name").innerHTML = "Name: <strong>" + response.agent_name + "</strong>";
                    document.getElementById("easyassist-agent-information-agent-location").innerHTML = "Address: <strong>" + response.agent_location + "</strong>";
                }
            } catch(err) { }

            if (response.agent_assistant_request_status == true) {
                agent_requested_for_assistant = true;
                if(document.getElementById("easyassist-co-browsing-request-assist-modal").style.display!="flex"){
                    verify_inputs = document.getElementsByClassName("easyassist-verfication-otp-input")
                    for (var i = 0; i < verify_inputs.length; i++) {
                        verify_inputs[i].value = "";
                        verify_inputs[i].style.color = 'inherit';
                        verify_inputs[i].style.borderColor = 'inherit';
                    }
                    document.getElementById("easyassist-co-browsing-request-assist-modal").style.display = "flex";
                    verify_inputs[0].focus();
                }
            }

            if (response.agent_meeting_request_status == true) {
                agent_meeting_request_status = true;
                if(document.getElementById("easyassist-co-browsing-request-meeting-modal").style.display!="flex"){
                    document.getElementById("easyassist-co-browsing-request-meeting-modal").style.display = "flex";
                }
            }
            if (response.allow_agent_meeting == "true") {
                cobrowsing_meeting = get_easyassist_cookie("is_cobrowse_meeting_on")
                if(cobrowsing_meeting == '' || cobrowsing_meeting == null || cobrowsing_meeting == undefined){
                    cobrowsing_meeting = false
                }
                if(cobrowsing_meeting == false || cobrowsing_meeting == 'false'){
                    open_meeting_window();
                    EASYASSIST_COBROWSE_META.allow_meeting = true;
                }
            } else {
                EASYASSIST_COBROWSE_META.allow_meeting = false;
            }

            // else if (response.agent_assistant_request_status == true) {
            //     agent_requested_for_assistant = false;
            // }

            if (response.allow_agent_cobrowse == "true") {
                EASYASSIST_COBROWSE_META.allow_cobrowsing = true;
            } else {
                EASYASSIST_COBROWSE_META.allow_cobrowsing = false;
            }

            if (EASYASSIST_COBROWSE_META.allow_meeting == false && EASYASSIST_COBROWSE_META.allow_cobrowsing == false) {
                return;
            }

            if (response.agent_name == null && EASYASSIST_COBROWSE_META.lead_generation == false) {
                show_easyassist_toast("Our customer service agent will join the session soon.");
                return;
            }
            if (response.is_agent_connected == true) {
                hide_easyassist_agent_joining_modal();
                show_floating_sidenav_menu();
                if(EASYASSIST_COBROWSE_META.enable_masked_field_warning == true)
                    document.getElementsByClassName("easyassist-tooltiptext")[0].style.display = "inline";
                agent_connected_cookie = get_easyassist_cookie("easyassist_agent_connected");
                if (is_agent_connected == false && agent_connected_cookie != "true") {
                    show_easyassist_toast(response.agent_name + " has joined the session.");
                    set_easyassist_cookie("easyassist_agent_connected", "true");
                    is_agent_connected = true;
                }
            } else if (response.is_agent_connected == false) {
                if (is_agent_connected == true) {
                    show_easyassist_toast(response.agent_name + " has left the session.");
                    is_agent_connected = false;
                    document.getElementsByClassName("easyassist-tooltiptext")[0].style.display = "none";
                }
            }

        } else if (this.readyState == 4) {
            var description = "Client activity check API (/easy-assist-salesforce/highlight/) failed with status code " + this.status.toString();
            // save_easyassist_system_audit_trail("api_failure", description);
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

            encrypted_data = custom_encrypt(json_string);

            encrypted_data = {
                "Request": encrypted_data
            };

            var params = JSON.stringify(encrypted_data);

            var xhttp = new XMLHttpRequest();
            xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist-salesforce/agent/save-document/", true);
            xhttp.setRequestHeader('Content-Type', 'application/json');
            xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
            xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
            xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    response = JSON.parse(this.responseText);
                    response = custom_decrypt(response.Response);
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
        document.getElementById("revoke-edit-access-button").style.display = "block";
    } else {
        set_easyassist_cookie("easyassist_edit_access", "false");
        document.getElementById("revoke-edit-access-button").style.display = "none";
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
    encrypted_data = custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "client");
    agent_revoke_edit_access = false;
}

function revoke_easyassist_edit_access() {
    if(agent_revoke_edit_access)
        show_easyassist_toast("Edit Access has been revoked by the agent.");
    else
        show_easyassist_toast("Edit Access has been revoked from agent.");
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

    encrypted_data = custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist-salesforce/get-cobrowsing-chat-history/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            window.CLIENT_NAME = response.client_name;
            send_client_name(response.client_name);
            if(response.status==200 && response.chat_history.length > 0) {
                chat_history = response.chat_history;
                allincall_chat_window = document.getElementById("easyassist-livechat-iframe").contentWindow;
                for(var index=0; index<chat_history.length; index++){
                    sender = chat_history[index]["sender"];
                    message = chat_history[index]["message"];
                    message=show_hyperlink_inside_text(message);
                    datetime = chat_history[index]["datetime"];
                    var time = datetime.split(" ")[3] + " " + datetime.split(" ")[4];
                    attachment = chat_history[index]["attachment"];
                    attachment_file_name = chat_history[index]["attachment_file_name"];
                    if(sender == "client") {
                        allincall_chat_window.postMessage(JSON.stringify({
                            "client_name": response.client_name,
                            "message": message,
                            "attachment": attachment,
                            "attachment_file_name": attachment_file_name,
                            "show_client_message": true,
                            "time": time
                        }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);
                    } else {
                        allincall_chat_window.postMessage(JSON.stringify({
                            "agent_name": sender,
                            "message": message,
                            "attachment": attachment,
                            "attachment_file_name": attachment_file_name,
                            "show_agent_message": true,
                            "time": time
                        }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);
                    }
                }
            }
        }
    }
    xhttp.send(params);
}

var easyassist_socket_activity_interval_check = setInterval(function(e) {

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    var allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;
    if (allow_cobrowsing == false) {
        return;
    }

    if (client_websocket == null) {
        start_cobrowsing_activity_check();
    } else {
        if (client_websocket.readyState === client_websocket.OPEN) {
            //console.log("socket is open and working fine");
        } else if (client_websocket.readyState === client_websocket.CLOSED) {
            start_cobrowsing_activity_check();
        } else if (client_websocket.readyState === client_websocket.CLOSING) {
            client_websocket.close();
            start_cobrowsing_activity_check();
        }
    }

}, 5000);

start_cobrowsing_activity_check();

function check_is_lead_converted(){
    var active_url = window.location.href.replace(window.location.protocol+"//", "");
    var urls_list_lead_converted = window.EASYASSIST_COBROWSE_META.urls_list_lead_converted;

    for(var index=0; index<urls_list_lead_converted.length ; index++){
        var target_url = urls_list_lead_converted[index];
        if(active_url.indexOf(target_url) == 0){
            mark_lead_as_converted();
        }
    }
}

function mark_lead_as_converted() {

    if (get_easyassist_cookie("easyassist_session_id") == undefined) {
        return;
    }

    json_string = JSON.stringify({
        "session_id": get_easyassist_cookie("easyassist_session_id"),
        "active_url": window.location.href
    });

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist-salesforce/mark-lead-as-converted/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer " + easyassist_authtoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                set_easyassist_cookie("is_lead_converted", get_easyassist_cookie("easyassist_session_id"));
                notify_agent_lead_is_converted();
            }
        }
    }
    xhttp.send(params);
}

setTimeout(function(){
    if(get_easyassist_cookie("is_lead_converted") != get_easyassist_cookie("easyassist_session_id")){
        check_is_lead_converted();
    }
}, 3000);
