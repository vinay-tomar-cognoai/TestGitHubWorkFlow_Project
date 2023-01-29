var framesContainer = document.querySelector('#frames-container');
var currentFrameIdx = 0;
var playbackIntervalId = null;
var cobrowseSocket = null;
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
var requested_for_edit_access = false;
var ALLOW_SCREENSHARING_COBROWSE = false;
var easyassist_tickmarks_clicked=new Array(11).fill(false);
var close_nav_timeout = null;
window.EASYASSIST_CLIENT_FEEDBACK = null;

var agent_pointer_position = {
    pageX: 0,
    pageY: 0,
    clientX: 0,
    clientY: 0,
    upper_hidden_pixel: 0,
}

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
    var delay_by_nine_minutes = get_delayed_date_object(-18);
    if (user_last_activity_time_obj < delay_by_nine_minutes) { // if user is active in last minute ( after inactive for 9 minuits )
        user_last_activity_time_obj = new Date()
        send_session_timeout_request();
    }
    user_last_activity_time_obj = new Date()
}

function sync_mouse_position(event, is_from_chat_window = false) {
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

    send_message_over_easyassist_socket(encrypted_data, "agent");
}

function strip_html(text){
   var regex = /(<([^>]+)>)/ig;
   text = text.replace(regex, "");

   return text;
}

function remove_special_characters_from_str(text) {
    var regex = /:|;|'|"|=|-|\$|\*|%|!|~|\^|\(|\)|\[|\]|\{|\}|\[|\]|#|<|>|\/|\\/g;
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

    if (window.location.protocol == "https:") {
        document.cookie = cookiename + "=" + cookievalue + ";max-age=86400" + ";path=/;domain=" + domain + ";secure";
    } else {
        document.cookie = cookiename + "=" + cookievalue + ";max-age=86400" + ";path=/;";
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

function start_internet_connectivity_check_timer() {
    internet_connectivity_timer = setInterval(function(e) {
        show_easyassist_toast("We are not receiving any updates from client. Kindly check your internet connectivity.");
        reset_internet_connectivity_check_timer();
    }, INTERNET_CON_TIMER);
}

function open_close_session_modal() {
    check_is_lead_converted();
    $("#close_session_modal").modal("show");
    framesContainer.style.filter = "blur(3px)";
}
function gain_focus(){
  framesContainer.style.filter = null;
}
function check_is_lead_converted() {
    if (get_easyassist_cookie("is_lead_converted") == COBROWSE_SESSION_ID) {
        $("#mask-successfull-cobrowsing-session").attr("checked", true)
        $("#mask-successfull-cobrowsing-session").attr("disabled", "disabled")
    }
}



window.onload = function() {
    is_page_reloaded = true;
    create_easyassist_socket(COBROWSE_SESSION_ID, "agent");
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
    update_edit_access_icon_properties();
};

function create_and_iframe(html) {
    // html = EasyAssistLZString.decompress(html);
    var blob = new Blob([html], {
        type: 'text/html'
    });
    var iframe = document.createElement('iframe');
    iframe.src = window.URL.createObjectURL(blob);
    iframe.hidden = true;
    iframe.onload = renderFrame;
    iframe.setAttribute("class", "client-data-frame");
    framesContainer.appendChild(iframe);
    is_page_reloaded = false;
    edit_access_update();
}

function create_and_iframe_from_chunk(client_packet) {
    var html = "";
    for (var index = 0; index <= client_packet.chunk; index++) {
        //console.log(client_packet.page, index);
        html += chunk_html_dict[client_packet.page][index];
    }
    delete chunk_html_dict[client_packet.page];
    create_and_iframe(html);
}

function resize_iframe_container(width, height) {

    if(ALLOW_SCREENSHARING_COBROWSE == 'True' || ALLOW_SCREENSHARING_COBROWSE == 'true' || ALLOW_SCREENSHARING_COBROWSE == true) {

        return ;
    }
    var frame_container = document.getElementById("frames-container");
    frame_container.style.width = width.toString() + "px";
    frame_container.style.height = height.toString() + "px";
    agent_screen_width = window.innerWidth;
    margin_left_client_frame_container = parseInt((agent_screen_width - width) / 2)
    frame_container.style.margin = "0px 0px 0px " + margin_left_client_frame_container + "px";
}

function update_edit_access_icon_properties() {
    if (document.getElementById("easyassist-edit-access-icon") != undefined) {
        if (get_easyassist_cookie("request_edit_access") == COBROWSE_SESSION_ID) {
            document.getElementById("easyassist-edit-access-icon").setAttribute("data-target", "");
            document.getElementById("easyassist-edit-access-icon").setAttribute("onclick", "revoke_easyassist_edit_access();");
            document.getElementById("easyassist-edit-access-icon").children[1].children[1].innerText = "Revoke Edit Access";
            document.getElementById("easyassist-edit-access-icon").style.backgroundColor = find_light_color(FLOATING_BUTTON_BG_COLOR, 300);
        } else {
            document.getElementById("easyassist-edit-access-icon").setAttribute("data-target", "#request_for_edit_access_modal");
            document.getElementById("easyassist-edit-access-icon").removeAttribute("onclick");
            document.getElementById("easyassist-edit-access-icon").children[1].children[1].innerText = "Request for Edit Access";
            document.getElementById("easyassist-edit-access-icon").style.backgroundColor = 'initial';
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

    send_message_over_easyassist_socket(encrypted_data, "agent");
}

function edit_access_update() {
    if (get_easyassist_cookie("request_edit_access") == COBROWSE_SESSION_ID) {
        action = "initial";
    } else {
        action = "none";
    }
    frame_child = framesContainer.children[0];
    frame_child.style.pointerEvents = action;
    frame_child.style.webkitUserSelect = action;
    frame_child.style.mozUserSelect = action;
    frame_child.style.msUserSelect = action;
    frame_child.style.oUserSelect = action;
    frame_child.style.userSelect = action;
}

function sync_client_web_screen(e) {

    var data = JSON.parse(e.data);
    message = data.message;
    client_packet = message.body.Request;

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
                resize_iframe_container(client_packet.window_width, client_packet.window_height);
                create_and_iframe(client_packet.html);
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
            scrollX = client_packet.data_scroll_x;
            scrollY = client_packet.data_scroll_y;
            if (framesContainer.children.length > 0) {
                prev_frame = framesContainer.children[0];
                prev_frame.contentWindow.scrollTo(scrollX, scrollY);
            }

        } else if (client_packet.type == "pageshot") {

            if (client_packet.result == 200) {
                show_easyassist_toast("Screenshot captured successfully. Please click on View ScreenShot to download it");
            } else {
                show_easyassist_toast("Unable to capture the client screenshot. Kindly try again later or connect with application administrator.");
            }

        } else if (client_packet.type == "mouse") {

            if(ALLOW_SCREENSHARING_COBROWSE == 'True' || ALLOW_SCREENSHARING_COBROWSE == 'true' || ALLOW_SCREENSHARING_COBROWSE == true) {

                return ;
            }
            client_mouse_element.style.top = client_packet.position.clientY + "px";
            client_mouse_element.style.left = (margin_left_client_frame_container + client_packet.position.clientX) + "px";

        } else if (client_packet.type == "chat") {

            set_client_response(client_packet.message, client_packet.attachment, client_packet.attachment_file_name);

        } else if (client_packet.type == "element_value") {
            if(ALLOW_SCREENSHARING_COBROWSE == 'True' || ALLOW_SCREENSHARING_COBROWSE == 'true' || ALLOW_SCREENSHARING_COBROWSE == true) {

                return ;
            }

            if (framesContainer.children.length > 0) {

                frame_child = framesContainer.children[0];

                html_elements_value_list = client_packet.html_elements_value_list;

                for (var html_element_index = 0; html_element_index < html_elements_value_list.length; html_element_index++) {

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

                        for (var option_index = 0; option_index < frame_element.options.length; option_index++) {
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
            if(ALLOW_SCREENSHARING_COBROWSE == 'True' || ALLOW_SCREENSHARING_COBROWSE == 'true' || ALLOW_SCREENSHARING_COBROWSE == true) {

                return ;
            }

            frame_child = framesContainer.children[0];

            if (client_packet.is_allowed == "none") {
                delete_easyassist_cookie("request_edit_access");
                edit_access_update();
                update_edit_access_icon_properties();
                if("agent_revoke_edit_access" in client_packet) {
                    save_easyassist_system_audit_trail("edit_access", "agent_revoked_edit_access");
                    show_easyassist_toast("Edit access been revoked");
                }else {
                    save_easyassist_system_audit_trail("edit_access", "client_revoked_edit_access");
                    show_easyassist_toast("Agent has revoked edit access");
                }
                setTimeout(function() {
                    window.location.reload();
                }, 5000);
            } else if (requested_for_edit_access == true) {
                requested_for_edit_access = false;

                if (client_packet.is_allowed == "true") {
                    set_easyassist_cookie("request_edit_access", COBROWSE_SESSION_ID);
                    edit_access_update();
                    update_edit_access_icon_properties();
                    save_easyassist_system_audit_trail("edit_access", "client_provided_edit_access");
                    show_easyassist_toast("Agent has provided edit access to you.");
                    setTimeout(function() {
                        window.location.reload();
                    }, 2000);
                } else if (client_packet.is_allowed == "false") {
                    delete_easyassist_cookie("request_edit_access");
                    edit_access_update();
                    update_edit_access_icon_properties();
                    save_easyassist_system_audit_trail("edit_access", "client_denied_edit_access");
                    show_easyassist_toast("Agent has denied edit access to the form.");
                }
            }
        } else if (client_packet.type == "lead_status") {
            var is_converted = client_packet.is_converted;
            if (is_converted == true) {
                set_easyassist_cookie("is_lead_converted", COBROWSE_SESSION_ID);
            }
        } else if(client_packet.type == "end_voip_meeting") {
            if(client_packet.auto_end_meeting) {
                show_easyassist_toast("Call ended");
            } else {
                show_easyassist_toast("Agent ended the call");
            }
            setTimeout(function() {
                end_cobrowse_video_meet(true);
            }, 1000);
        } else if(client_packet.type == "voip_meeting_ready") {
            show_easyassist_toast("Agent joined the call");
            set_easyassist_cookie("is_customer_voip_meeting_joined", COBROWSE_SESSION_ID);
        } 
    } else {

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

    send_message_over_easyassist_socket(encrypted_data, "agent");
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

function renderFrame(event) {

    //console.log("frame is loaded rendering ifrmae");

    setTimeout(function() {

        event.preventDefault();

        if (framesContainer.children.length) {

            var frame = framesContainer.children[currentFrameIdx];
            if (!frame) {
                return;
            }

            if (currentFrameIdx > 0) {
                var prevFrame = frame.previousElementSibling;
                prevFrame.hidden = true;
                window.URL.revokeObjectURL(prevFrame.src);
                prevFrame.parentNode.removeChild(prevFrame);
                currentFrameIdx = currentFrameIdx - 1;
            }

            frame.hidden = false;

            scrollX = parseInt(frame.contentDocument.documentElement.dataset.scrollX);
            scrollY = parseInt(frame.contentDocument.documentElement.dataset.scrollY);
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

            $("#allincall-chat-box")[0].contentWindow.document.onmousemove = function(event) {
                sync_mouse_position(event, is_from_chat_window = true);
            }

            var active_element_list = [];
            active_element_list = frame.contentWindow.document.querySelectorAll("input");
            for (var index = 0; index < active_element_list.length; index++) {
                active_element_list[index].onkeyup = detect_agent_value_change;
                active_element_list[index].onchange = detect_agent_value_change;
                is_active_element = active_element_list[index].getAttribute("easyassist-active") == "true" ? true : false;
                if (is_active_element) {
                    active_element_list[index].parentElement.style.outline = "solid 2px #E83835 !important";
                }
            }

            active_element_list = frame.contentWindow.document.querySelectorAll("select");
            for (var index = 0; index < active_element_list.length; index++) {
                active_element_list[index].onchange = detect_agent_value_change;
                is_active_element = active_element_list[index].getAttribute("easyassist-active") == "true" ? true : false;
                if (is_active_element) {
                    active_element_list[index].parentElement.style.outline = "solid 2px #E83835 !important";
                }
            }

            active_element_list = frame.contentWindow.document.querySelectorAll("textarea");
            for (var index = 0; index < active_element_list.length; index++) {
                active_element_list[index].onkeyup = detect_agent_value_change;
                active_element_list[index].onchange = detect_agent_value_change;
                is_active_element = active_element_list[index].getAttribute("easyassist-active") == "true" ? true : false;
                if (is_active_element) {
                    active_element_list[index].parentElement.style.outline = "solid 2px #E83835 !important";
                }
            }

            div_element_list = frame.contentWindow.document.querySelectorAll("div");
            for (var index = 0; index < div_element_list.length; index++) {
                div_ele = div_element_list[index];
                scroll_left = div_ele.getAttribute("easyassist-data-scroll-x");
                scroll_top = div_ele.getAttribute("easyassist-data-scroll-y");
                div_ele.scrollLeft = scroll_left;
                div_ele.scrollTop = scroll_top;
            }

            marquee_element_list = frame.contentWindow.document.querySelectorAll('marquee');
            for (var index = 0; index < marquee_element_list.length; index++) {
                marquee_element_list[index].start();
            }
            currentFrameIdx++;

            try {
                var button_elements = frame.contentWindow.document.querySelectorAll(".easyassist-click-element");
                button_elements.forEach(function(currentBtn){
                    currentBtn.addEventListener('click', function(event) {
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
                    })
                })
            } catch(err) { }
        }
        document.getElementById("easyassist-loader").style.display = "none";

    }, 800);
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
        "type": type
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");

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

    comments = document.getElementById("close-session-remarks").value;

    if (window.EASYASSIST_CLIENT_FEEDBACK == null || is_feedback == false) {
        rating = "None";
    } else {
        rating = window.EASYASSIST_CLIENT_FEEDBACK;
    }

    window.EASYASSIST_CLIENT_FEEDBACK = null;
    
    try {
        if(comments.length > 200) {
            comments = comments.substr(0, 200);
        }
    } catch(err) {}

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
        element.innerHTML = "Closing...";
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

                json_string = JSON.stringify({
                    "type": "end_session",
                });

                encrypted_data = easyassist_custom_encrypt(json_string)
                encrypted_data = {
                    "Request": encrypted_data
                };

                if (client_websocket == null) {
                    create_easyassist_socket(COBROWSE_SESSION_ID, "client");
                    json_string = JSON.stringify({
                        "type": "end_session",
                    });

                    encrypted_data = easyassist_custom_encrypt(json_string)
                    encrypted_data = {
                        "Request": encrypted_data
                    };
                }

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
                for (var index = 0; index < meta_information_list.length; index++) {
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

/*WebSocket Utilities - Closes*/


function create_easyassist_socket(jid, sender) {
    ws_scheme = window.location.protocol == "http:" ? "ws" : "wss";
    url = ws_scheme + '://' + window.location.host + '/ws/cobrowse/' + jid + '/' + sender + "/";
    if (client_websocket == null) {
        client_websocket = new WebSocket(url);
        client_websocket.onmessage = sync_client_web_screen;
        client_websocket.onerror = check_socket_status;
        client_websocket.onopen = open_easyassist_websocket;
        client_websocket.onclose = close_easyassist_websocket;
        //console.log("socket has been created");
    }
}

function send_message_over_easyassist_socket(message, sender) {

    if (client_websocket_open && client_websocket != null) {
        client_websocket.send(JSON.stringify({
            "message": {
                "header": {
                    "sender": sender
                },
                "body": message
            }
        }));
    } else {
        create_easyassist_socket(COBROWSE_SESSION_ID, "agent");
    }
}

if (window.addEventListener) {
    window.addEventListener('load', initiate_internet_speed_detection, false);
} else if (window.attachEvent) {
    window.attachEvent('onload', initiate_internet_speed_detection);
}

function initiate_internet_speed_detection() {
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
            var speedMbps = (speedKbps / 1024).toFixed(2);

            if (speedMbps < 1) {
                $('#check_for_internet_modal').modal('show');
            }
        }
    }

    start_time = (new Date()).getTime();
    var cache_buster = "?nnn=" + start_time;
    download.src = image_addr + cache_buster;
}

function sync_client_web_screen_agent() {

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
                    open_close_session_modal();
                }
                if (response.allow_agent_meeting == "true") {
                    if(ENABLE_VOIP_WITH_VIDEO_CALLING == "True") {
                        show_cobrowse_meeting_option();
                    } else if(ENABLE_VOIP_CALLING == "True") {
                        show_cobrowse_meeting_option();
                    } else {
                        open_meeting_window();
                    }
                }
                if (response.agent_meeting_request_status == true) {
                    $('#request_voip_meeting_modal').modal('show');
                }
            } else if (response.status == 500) {
                show_easyassist_toast("Matching session is already expired or doesn't exists");
            }
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

function save_cobrowsing_chat_history(chat_message, sender, attachment, attachment_file_name) {

    json_string = JSON.stringify({
        "session_id": COBROWSE_SESSION_ID,
        "sender": sender,
        "message": chat_message,
        "attachment": attachment,
        "attachment_file_name": attachment_file_name
    });

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
            console.log(response);
        }
    }
    xhttp.send(params);
}

function send_chat_message_from_agent(message, attachment, attachment_file_name) {
      save_cobrowsing_chat_history(message, "agent", attachment, attachment_file_name);
      var agent_name = $('#agent_name').val();
      json_string = JSON.stringify({
          "agent_name": agent_name,
          "type": "chat",
          "message": message,
          "attachment": attachment,
          "attachment_file_name": attachment_file_name
      });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    //console.log("request for html has been sent: ", new Date());
    send_message_over_easyassist_socket(encrypted_data, "agent");
}

function open_livechat_agent_window() {
    document.getElementById("allincall-chat-box").style.display = "block";
    var inner_doc = document.getElementById("allincall-chat-box").contentWindow.document;
    $(inner_doc).ready(function() {
      inner_doc.getElementById("user_input").focus();
    })


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
        }

        if (event.data.event_id === "cobrowsing-agent-chat-message") {
                message = event.data.data.message;
                attachment = event.data.data.attachment;
                attachment_file_name = event.data.data.attachment_file_name;
                send_chat_message_from_agent(message, attachment, attachment_file_name);
                return;
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
    var anime = document.getElementById("allincall-chat-box").style.animationName
    document.getElementById("allincall-chat-box").style.animationName = "bottom-left-right-anime-close";
    document.getElementById("allincall-chat-box").style.display = "none";
}

function set_client_response(message, attachment, attachment_file_name) {
    if (document.getElementById("allincall-chat-box").style.display == "none") {
        document.getElementById("allincall-chat-box").style.display = "block";
    }
    allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow;
    allincall_chat_window.postMessage(JSON.stringify({
        "message": message,
        "attachment": attachment,
        "attachment_file_name": attachment_file_name,
        "show_client_message": true,
        "name": window.CLIENT_NAME
    }), window.location.protocol + "//" + window.location.host);
    save_cobrowsing_chat_history(message, "client", attachment, attachment_file_name);
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

    send_message_over_easyassist_socket(encrypted_data, "agent");

    save_easyassist_system_audit_trail("edit_access", "agent_requested_edit_access");

    show_easyassist_toast("Request for edit access has been sent to agent");
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
            "value": value
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

    send_chat_message_from_agent(message, attachment, attachment_file_name);
    append_attachment_message_into_chatbox(message, attachment, attachment_file_name);

    $('#support_material_modal').modal('toggle');
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
                for (var index = 0; index < chat_history.length; index++) {
                    sender = chat_history[index]["sender"];
                    message = chat_history[index]["message"];
                    message=show_hyperlink_inside_text(message);
                    datetime = chat_history[index]["datetime"];
                    var time = datetime.split(" ")[3] + " " + datetime.split(" ")[4];
                    attachment = chat_history[index]["attachment"];
                    attachment_file_name = chat_history[index]["attachment_file_name"];
                    if (sender == "client") {
                        allincall_chat_window.postMessage(JSON.stringify({
                            "message": message,
                            "attachment": attachment,
                            "attachment_file_name": attachment_file_name,
                            "show_client_message": true,
                            "name": window.CLIENT_NAME,
                            "time": time
                        }), window.location.protocol + "//" + window.location.host);
                    } else {
                        allincall_chat_window.postMessage(JSON.stringify({
                            "message": message,
                            "attachment": attachment,
                            "attachment_file_name": attachment_file_name,
                            "show_agent_message": true,
                            "time": time,
                            "name": window.AGENT_NAME
                        }), window.location.protocol + "//" + window.location.host);
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
    } catch {
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
    window.open("/easy-assist/meeting/" + session_id + "?is_meeting_cobrowsing=true", "_blank",);
}

function show_emoji_by_user_rating(element, user_rating) {

    rating_spans = element.parentNode.children;
    for (var index = 0; index < rating_spans.length; index ++) {
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
    for(var index = 0; index < rating_spans.length; index ++) {
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

    for(var index = 0; index <= user_rating; index ++) {
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

    for(var index = user_rating + 1; index < rating_spans.length; index ++) {
        var current_rating = parseInt(rating_spans[index].innerHTML);
        rating_spans[index].style.background = "unset"
        rating_spans[index].style.color = "#2D2D2D";
        easyassist_tickmarks_clicked[index] = false;
        rating_spans[index].style.border = "1px solid #E6E6E6";
    }
}

function reset_easyassist_rating_bar() {
    var rating_bar = document.getElementsByClassName("easyassist-tickmarks")[0];
    var rating_spans = rating_bar.querySelectorAll("span");
    for (var index = 0; index < rating_spans.length; index++) {
        rating_spans[index].style.background = "unset";
        rating_spans[index].style.color = "#2D2D2D";
        rating_spans[index].style.border = "1px solid #E6E6E6";
        easyassist_tickmarks_clicked[index] = false;
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

    var RR = ((R.toString(16).length==1)?"0"+R.toString(16):R.toString(16));
    var GG = ((G.toString(16).length==1)?"0"+G.toString(16):G.toString(16));
    var BB = ((B.toString(16).length==1)?"0"+B.toString(16):B.toString(16));

    var rgba_color = "rgba(" + R + "," + G + "," + B + ",0.4)"
    return rgba_color;
}

function show_cobrowse_meeting_option() {
    var is_cobrowse_meeting_active = get_easyassist_cookie("is_cobrowse_meeting_active");
    if(is_cobrowse_meeting_active == COBROWSE_SESSION_ID) {
        if(document.getElementById("cobrowse-voip-container").style.display == 'none') {
            try {
                document.getElementById("request-cobrowsing-meeting-btn").style.display = 'none';
            } catch(err) {}
            document.getElementById("easyassist-voip-loader").style.display = 'flex';
            document.getElementById("cobrowse-voip-container").style.display = 'flex';
            var cobrowsing_meeting_iframe = document.getElementById("cobrowse-meeting-iframe-container").children[0];
            var meeting_url = window.location.protocol + "//" + window.location.host + "/easy-assist/client-cobrowse-meeting/" + COBROWSE_SESSION_ID;
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
            document.getElementById("agent-meeting-mic-off-btn").style.display = 'flex';
        } else if(element.id == "agent-meeting-mic-off-btn") {
            document.getElementById("agent-meeting-mic-off-btn").style.display = 'none';
            document.getElementById("agent-meeting-mic-on-btn").style.display = 'flex';
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
            document.getElementById("agent-meeting-video-off-btn").style.display = 'flex';
        } else if(element.id == "agent-meeting-video-off-btn") {
            document.getElementById("agent-meeting-video-off-btn").style.display = 'none';
            document.getElementById("agent-meeting-video-on-btn").style.display = 'flex';
        }
    } catch(err) {
        console.log(err)
    }
}

function end_cobrowse_video_meet(auto_end_meeting=false) {
    try {
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
    try {
        document.getElementById("request-cobrowsing-meeting-btn").style.display = 'inherit';
    } catch(err) {}

    document.getElementById("cobrowse-meeting-iframe-container").style.display = 'none';
    document.getElementById("cobrowse-voip-container").style.display = 'none';
    document.getElementById("agent-meeting-mic-on-btn").style.display = 'none';
    document.getElementById("agent-meeting-mic-off-btn").style.display = 'flex';
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

    send_message_over_easyassist_socket(encrypted_data, "agent");
}


function send_voip_meeting_ready_over_socket() {
    json_string = JSON.stringify({
        "type": "voip_meeting_ready",
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");
}


function open_meeting_window() {

    var is_cobrowsing_meeting_on = get_easyassist_cookie("is_cobrowse_meeting_on")
    if(is_cobrowsing_meeting_on == '' || is_cobrowsing_meeting_on == null || is_cobrowsing_meeting_on == undefined){
        is_cobrowsing_meeting_on = false
    }
    if(is_cobrowsing_meeting_on == false || is_cobrowsing_meeting_on == 'false') {
        set_easyassist_cookie("is_cobrowse_meeting_on", "true");
        var url = "/easy-assist/meeting/" + COBROWSE_SESSION_ID + "?is_meeting_cobrowsing=true"
        window.open(url, "_blank");
    }
}