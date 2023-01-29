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
var session_has_ended = false;
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

function openNav() {
    document.getElementById("mySidenav").style.display = "";
    document.getElementById("maximise-button").style.display = "none";
}

function closeNav() {
    document.getElementById("mySidenav").style.display = "none";
    document.getElementById("maximise-button").style.display = "";
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

    encrypted_data = custom_encrypt(json_string);

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
    console.log("set_easyassist_cookie:", cookiename, cookievalue);
    var domain = window.location.hostname.substring(window.location.host.indexOf(".") + 1);

    if(window.location.hostname.split(".").length==2){
        domain = window.location.hostname;
    }
    
    if (window.location.protocol == "https:") {
        document.cookie = cookiename + "=" + cookievalue + ";SameSite=None; Secure";
    } else {
        document.cookie = cookiename + "=" + cookievalue + ";SameSite=None;";
    }
    console.log(document.cookie);
    console.log(get_easyassist_cookie(cookiename));
}

function get_easyassist_cookie(cookiename) {
    console.log("get_easyassist_cookie:", cookiename)
    var matches = document.cookie.match(new RegExp(
        "(?:^|; )" + cookiename.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    console.log(matches ? matches[1] : undefined);
    return matches ? matches[1] : undefined;
}

function delete_easyassist_cookie(cookiename) {
    var domain = window.location.hostname.substring(window.location.host.indexOf(".") + 1);
    if (window.location.protocol == "https:") {
        document.cookie = cookiename + "=;SameSite=None; Secure; expires = Thu, 01 Jan 1970 00:00:00 GMT";
    } else {
        document.cookie = cookiename + "=;SameSite=None; expires = Thu, 01 Jan 1970 00:00:00 GMT";
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
    document.getElementById('mySidenav').style.display="none";
    if(document.getElementById('mySidenav-session-end')) {
        document.getElementById('mySidenav-session-end').style.display="flex";
    }
    $("#close_session_modal").modal("show");
    framesContainer.style.filter = "blur(3px)";
}
function gain_focus(){
  framesContainer.style.filter = null;
  if(!session_has_ended){
    document.getElementById('mySidenav').style.display="flex";
    if(document.getElementById('mySidenav-session-end')) {
        document.getElementById('mySidenav-session-end').style.display="none";
    }
  }
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
    sync_client_web_screen_agent();
    reset_internet_connectivity_check_timer();
    set_user_inactivity_detector();
    get_support_material();
    load_chat_history();
    update_edit_access_icon_properties();
};

function create_and_iframe(html) {

    if(ALLOW_SCREENSHARING_COBROWSE == 'True' || ALLOW_SCREENSHARING_COBROWSE == 'true' || ALLOW_SCREENSHARING_COBROWSE == true) {

        return ;
    }
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
            document.getElementById("easyassist-edit-access-icon").setAttribute("onclick", "revoke_easyassist_edit_access();hide_cobrowsing_modals(this)");
            document.getElementById("easyassist-edit-access-icon").children[1].innerText = "Revoke Edit Access";
            document.getElementById("easyassist-edit-access-icon").children[0].innerHTML = '<path fill-rule="evenodd" clip-rule="evenodd" d="M19.2778 2.72247L19.1376 2.59012C17.8495 1.4431 15.8741 1.48722 14.6388 2.72247L13.7492 3.61155L18.3885 8.24989L19.2778 7.36141C20.5131 6.12616 20.5572 4.15082 19.4102 2.8627L19.2778 2.72247ZM12.7775 4.58321L17.4168 9.22249L16.5978 10.0415C15.7155 9.3843 14.6489 9 13.5 9C10.4624 9 8 11.6863 8 15C8 16.0668 8.25521 17.0686 8.70266 17.9366L8.30685 18.3324C8.05304 18.5862 7.73739 18.7694 7.39111 18.8638L2.70173 20.1427C2.18852 20.2827 1.7176 19.8117 1.85756 19.2986L3.13649 14.6092C3.23093 14.2629 3.4141 13.9473 3.66791 13.6934L12.7775 4.58321ZM5.98125 10.0832L4.60625 11.4582L2.52084 11.4586C2.14114 11.4586 1.83334 11.1508 1.83334 10.7711C1.83334 10.3914 2.14114 10.0836 2.52084 10.0836L5.98125 10.0832ZM9.64795 6.41656L8.27292 7.79156L2.52084 7.79194C2.14114 7.79194 1.83334 7.48414 1.83334 7.10444C1.83334 6.72475 2.14114 6.41694 2.52084 6.41694L9.64795 6.41656ZM11.9396 4.12488L13.3146 2.74989L2.52084 2.75028C2.14114 2.75028 1.83334 3.05808 1.83334 3.43778C1.83334 3.81748 2.14114 4.12528 2.52084 4.12528L11.9396 4.12488ZM19.0833 15.0417C19.0833 12.2572 16.8261 10 14.0417 10C11.2572 10 9 12.2572 9 15.0417C9 17.8261 11.2572 20.0833 14.0417 20.0833C16.8261 20.0833 19.0833 17.8261 19.0833 15.0417ZM14.6911 15.0418L16.3134 13.4204C16.4924 13.2414 16.4924 12.9512 16.3134 12.7722C16.1344 12.5933 15.8442 12.5933 15.6652 12.7722L14.0429 14.3936L12.4214 12.7721C12.2424 12.5932 11.9522 12.5932 11.7732 12.7721C11.5942 12.9511 11.5942 13.2413 11.7732 13.4203L13.3945 15.0416L11.7732 16.6619C11.5942 16.8409 11.5942 17.1311 11.7732 17.31C11.9522 17.4891 12.2424 17.4891 12.4214 17.31L14.0427 15.6898L15.665 17.3121C15.844 17.4911 16.1342 17.4911 16.3132 17.3121C16.4922 17.1331 16.4922 16.8429 16.3132 16.6639L14.6911 15.0418Z" fill="' + FLOATING_BUTTON_BG_COLOR +'"></path>';

        } else {
            document.getElementById("easyassist-edit-access-icon").setAttribute("data-target", "#request_for_edit_access_modal");
            document.getElementById("easyassist-edit-access-icon").setAttribute("onclick","hide_cobrowsing_modals(this)");
            document.getElementById("easyassist-edit-access-icon").children[1].innerText = "Request for Edit Access";
            document.getElementById("easyassist-edit-access-icon").children[0].innerHTML = '<path d="M12.7775 4.58321L17.4168 9.22249L8.30685 18.3324C8.05304 18.5862 7.73739 18.7694 7.39111 18.8638L2.70173 20.1427C2.18852 20.2827 1.7176 19.8117 1.85756 19.2986L3.13649 14.6092C3.23093 14.2629 3.4141 13.9473 3.66791 13.6934L12.7775 4.58321ZM5.98125 10.0832L4.60625 11.4582L2.52084 11.4586C2.14114 11.4586 1.83334 11.1508 1.83334 10.7711C1.83334 10.3914 2.14114 10.0836 2.52084 10.0836L5.98125 10.0832ZM19.1376 2.59012L19.2778 2.72247L19.4102 2.8627C20.5572 4.15082 20.5131 6.12616 19.2778 7.36141L18.3885 8.24989L13.7492 3.61155L14.6388 2.72247C15.8741 1.48722 17.8495 1.4431 19.1376 2.59012ZM9.64795 6.41656L8.27292 7.79156L2.52084 7.79194C2.14114 7.79194 1.83334 7.48414 1.83334 7.10444C1.83334 6.72475 2.14114 6.41694 2.52084 6.41694L9.64795 6.41656ZM13.3146 2.74989L11.9396 4.12488L2.52084 4.12528C2.14114 4.12528 1.83334 3.81748 1.83334 3.43778C1.83334 3.05808 2.14114 2.75028 2.52084 2.75028L13.3146 2.74989Z" fill="' + FLOATING_BUTTON_BG_COLOR +'"></path>';
        }
    }
}

function revoke_easyassist_edit_access() {
    json_string = JSON.stringify({
        "type": "revoke-edit-access"
    });

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");
}

function edit_access_update() {
    if (get_easyassist_cookie("request_edit_access") == COBROWSE_SESSION_ID && IS_ADMIN_AGENT == "True") {
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

    var data = JSON.parse(e.data);
    message = data.message;
    client_packet = message.body.Request;

    //console.log(message.header.packet, " ---- ", new Date());

    if (message.body.is_encrypted == false) {
        client_packet = JSON.parse(client_packet);
    } else {
        client_packet = custom_decrypt(client_packet);
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
                show_easyassist_toast("Screenshot captured successfully.");
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

                        var select_value_found = false;
                        for (var option_index = 0; option_index < frame_element.options.length; option_index++) {
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
                    show_easyassist_toast("Edit Access has been revoked.");
                }else {
                    save_easyassist_system_audit_trail("edit_access", "client_revoked_edit_access");
                    show_easyassist_toast("Client has revoked edit access.");
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
                    show_easyassist_toast("Client has provided edit access to you.");
                    setTimeout(function() {
                        window.location.reload();
                    }, 2000);
                } else if (client_packet.is_allowed == "false") {
                    delete_easyassist_cookie("request_edit_access");
                    edit_access_update();
                    update_edit_access_icon_properties();
                    save_easyassist_system_audit_trail("edit_access", "client_denied_edit_access");
                    show_easyassist_toast("Client has denied edit access to the form.");
                }
            }
        } else if (client_packet.type == "lead_status") {
            var is_converted = client_packet.is_converted;
            if (is_converted == true) {
                set_easyassist_cookie("is_lead_converted", COBROWSE_SESSION_ID);
            }
        }
    } else {
        
        if(message.header.sender=="agent" ){
            if (client_packet.type == "chat"){
                if(window.AGENT_NAME!=client_packet.agent_name)
                    set_agent_response(client_packet.message, client_packet.attachment, client_packet.attachment_file_name);
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

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");
}

function highlightElement(event, frame_window) {

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

    encrypted_data = custom_encrypt(json_string);
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

    encrypted_data = custom_encrypt(json_string);

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
                if(IS_ADMIN_AGENT == "False")
                    active_element_list[index].style.pointerEvents = "none";
                active_element_list[index].onkeyup = detect_agent_value_change;
                active_element_list[index].onchange = detect_agent_value_change;
                is_active_element = active_element_list[index].getAttribute("easyassist-active") == "true" ? true : false;
                if (is_active_element) {
                    active_element_list[index].parentElement.style.outline = "solid 2px #E83835 !important";
                }
            }

            active_element_list = frame.contentWindow.document.querySelectorAll("select");
            for (var index = 0; index < active_element_list.length; index++) {
                if(IS_ADMIN_AGENT == "False")
                    active_element_list[index].style.pointerEvents = "none";
                active_element_list[index].onchange = detect_agent_value_change;
                is_active_element = active_element_list[index].getAttribute("easyassist-active") == "true" ? true : false;
                if (is_active_element) {
                    active_element_list[index].parentElement.style.outline = "solid 2px #E83835 !important";
                }
            }

            active_element_list = frame.contentWindow.document.querySelectorAll("textarea");
            for (var index = 0; index < active_element_list.length; index++) {
                if(IS_ADMIN_AGENT == "False")
                    active_element_list[index].style.pointerEvents = "none";
                active_element_list[index].onkeyup = detect_agent_value_change;
                active_element_list[index].onchange = detect_agent_value_change;
                is_active_element = active_element_list[index].getAttribute("easyassist-active") == "true" ? true : false;
                if (is_active_element) {
                    active_element_list[index].parentElement.style.outline = "solid 2px #E83835 !important";
                }
            }

            div_element_list = frame.contentWindow.document.querySelectorAll("div");
            for (var index = 0; index < div_element_list.length; index++) {
                if(IS_ADMIN_AGENT == "False")
                    div_element_list[index].style.pointerEvents = "none";
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
                        if(IS_ADMIN_AGENT == "False")
                            this.style.pointerEvents = "none";    
                        easyassist_element_id = currentBtn.getAttribute("easyassist-element-id");
                        if (easyassist_element_id == null || easyassist_element_id == undefined) {
                            easyassist_element_id = "";
                        }
                        json_string = JSON.stringify({
                            "type": "button-click",
                            "element_id": event.target.id,
                            "easyassist_element_id": easyassist_element_id
                        });
                        encrypted_data = custom_encrypt(json_string);
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

    encrypted_data = custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");

    return;

    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID,
        "screenshot_type": type
    });

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/agent/take-client-screenshot/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            //console.log(response);
        }
    }
    xhttp.send(params);
}

function close_agent_confirm_session(element) {

    try{
        comments = document.getElementById("close-session-remarks").value;
        
        if(comments == "None") {
            show_easyassist_toast("Please select a comment.");
            return;
        }
        if(comments == "others")
            comments = document.getElementById("close-session-remarks-text").value;
    } catch(err){
        comments = document.getElementById("close-session-remarks-text").value;
    }

    is_helpful = document.getElementById("mask-successfull-cobrowsing-session").checked;
    is_test = document.getElementById("mask-test-cobrowsing-session").checked;

    if (comments.replace(/[^a-z0-9]/gi, '') == "" && is_test == false) {
        show_easyassist_toast("Comments cannot be empty.");
        return;
    }

    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID,
        "is_helpful": is_helpful,
        "is_test": is_test,
        "comments": comments
    });

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "closing...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/agent/close-session/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
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
                window.location = "/easy-assist-salesforce/sales-ai/dashboard/?salesforce_token=" + window.SALESFORCE_TOKEN;
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
        document.getElementById("meta_information_body").innerHTML = [
            '<tr>',
                '<td colspan="3" class="text-center">',
                    'Loading ...',
                '</td>',
            '</tr>',
        ].join('');
    }

    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID,
        "page": cobrowsing_meta_data_page
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
                var tbody_html = '';
                meta_information_list = response.meta_information_list;
                if(meta_information_list.length) {
                    for (var index = 0; index < meta_information_list.length; index++) {
                        meta_id = meta_information_list[index]["id"];
                        //if (meta_information_list[index]["type"] == "screenshot") {
                            tbody_html += [
                                '<tr>',
                                    '<td>' + meta_information_list[index]["type"] + '</td>',
                                    '<td>' + meta_information_list[index]["datetime"] + '</td>',
                                    '<td style="text-align: center">',
                                        '<!--<a href="/easy-assist-salesforce/agent/export/' + meta_id + '/?type=img&salesforce_token=' + window.SALESFORCE_TOKEN + '" target="_blank" title="Export As Image"><i class="fas fa-fw fa-download"></i></a> -->',
                                        '<a href="/easy-assist-salesforce/agent/export/' + meta_id + '/?type=html&salesforce_token=' + window.SALESFORCE_TOKEN + '" target="_blank" title="Export As HTML">',
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
                } else {
                    document.getElementById("meta_information_body").innerHTML = [
                        '<tr>',
                            '<td colspan="3" class="text-center">',
                                'No screenshots',
                            '</td>',
                        '</tr>',
                    ].join('');
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

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Inviting..";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/agent/share-session/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                $("#askfor_support_modal").modal('hide');
                set_desktop_notification_for_agents(support_agents);
                show_easyassist_toast("Support Request has been sent.");
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

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/agent/set-notification-for-agent/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
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

    encrypted_data = custom_encrypt(json_string);
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
    save_easyassist_system_audit_trail("socket", description);
}

function check_socket_status(e) {
    console.error("WebSocket error observed:", e);
    var description = "error occured agent websocket. " + e.data;
    save_easyassist_system_audit_trail("socket", description);
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

var speedMbps = 0;
var internet_iteration = 3;

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
    for(var i_index = 0; i_index < internet_iteration; i_index++) {

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

        $('#check_for_internet_modal').modal('show');
    }
}

function sync_client_web_screen_agent() {
    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID
    });

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/agent/sync/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status == 200) {

                if (response.init_transaction == true) {
                    document.getElementById("frames-container").style.display = "none";
                    document.getElementById("transaction-payment-loader").style.display = "block";
                    return;
                }

                document.getElementById("frames-container").style.display = "block";
                document.getElementById("transaction-payment-loader").style.display = "none";

                if (response.is_active == false || response.is_archived == true) {

                    if (document.getElementById("close_session_modal").style.display != "block"){
                        session_has_ended=true;
                        open_close_session_modal();
                        framesContainer.style.filter = "blur(3px)";
                        if(response.is_active == false)
                            show_easyassist_toast("Looks like customer has left the session. Please provide your comments before ending session.");
                        else
                            show_easyassist_toast("Looks like admin agent has closed the session. Please provide your comments before ending session.");
                        }

                } else if (response.is_client_connected == false) {
                    show_easyassist_toast("Looks like we are not receiving any updates from customer side. Kindly check your internet connectivity or check whether customer is still connected or not.");
                }

            } else if (response.status == 500) {
                show_easyassist_toast("Matching session is already expired or doesn't exists");
                window.location = "/easy-assist-salesforce/sales-ai/dashboard/?salesforce_token=" + window.SALESFORCE_TOKEN;
            }
        }
    }
    xhttp.send(params);
}

function get_list_of_support_agents() {

    document.getElementById("div-support-agents-container").classList.remove('justify-content-center');
    var selected_lang_pk = "-1";

    if (ALLOW_LANGUAGE_SUPPORT == 'True' || ALLOW_LANGUAGE_SUPPORT == true || ALLOW_LANGUAGE_SUPPORT == "true") {

        selected_lang_pk = $("#easyassist-language-support-selected").val();
    }

    var selected_product_category_pk = "-1";
    if (CHOOSE_PRODUCT_CATEGORY == 'True' || CHOOSE_PRODUCT_CATEGORY == true || CHOOSE_PRODUCT_CATEGORY == "true") {
        selected_product_category_pk = $("#easyassist-product-category-selected").val();
    }
    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID,
        "selected_lang_pk": selected_lang_pk,
        "selected_product_category_pk": selected_product_category_pk
    });

    encrypted_data = custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    document.getElementById("div-support-agents-container").classList.add('justify-content-center');
    document.getElementById("div-support-agents-container").innerHTML = [
        '<li class="justify-content-center">',
          '<div class="support-agent-custom-text">',
              'Loading...',
          '</div>',
        '</li>',
    ].join('');

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/agent/get-support-agents/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            div_inner_html = "";
            if (response.status == 200) {
                support_agents = response.support_agents;
                if (support_agents.length > 0) {
                    for(var index = 0; index < support_agents.length; index ++) {
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
                    document.getElementById("div-support-agents-container").classList.remove('justify-content-center');
                    document.getElementById("div-support-agents-container").innerHTML = div_inner_html;
                } else {
                    div_inner_html +=  [
                        '<li class="justify-content-center">',
                          '<div class="support-agent-custom-text">',
                              'No agents',
                          '</div>',
                        '</li>',
                    ].join('');
                    document.getElementById("div-support-agents-container").innerHTML = div_inner_html;
                }
            } else {
                div_inner_html +=  [
                    '<li class="justify-content-center">',
                      '<div class="support-agent-custom-text">',
                          'Unable to load the details. Try again.',
                      '</div>',
                    '</li>',
                ].join('');
                document.getElementById("div-support-agents-container").innerHTML = "Unable to load the details. Try again.";
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

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/save-system-audit/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
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

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/agent/save-cobrowsing-chat/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            console.log(response);
        }
    }
    xhttp.send(params);
}

function send_chat_message_from_agent(message, attachment, attachment_file_name) {
      save_cobrowsing_chat_history(message, "agent", attachment, attachment_file_name);
      var agent_name = window.AGENT_NAME;
      json_string = JSON.stringify({
          "agent_name": agent_name,
          "type": "chat",
          "message": message,
          "attachment": attachment,
          "attachment_file_name": attachment_file_name
      });

    encrypted_data = custom_encrypt(json_string);

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


function set_agent_response(message, attachment, attachment_file_name) {
    if (document.getElementById("allincall-chat-box").style.display == "none") {
        document.getElementById("allincall-chat-box").style.display = "block";
    }
    allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow;
    allincall_chat_window.postMessage(JSON.stringify({
        "message": message,
        "attachment": attachment,
        "attachment_file_name": attachment_file_name,
        "show_other_agent_message": true,
        "name": client_packet.agent_name
    }), window.location.protocol + "//" + window.location.host);
    save_cobrowsing_chat_history(message, "client", attachment, attachment_file_name);
}

function capture_request_edit_access() {
    requested_for_edit_access = true;
    json_string = JSON.stringify({
        "type": "request-edit-access",
    });

    encrypted_data = custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");
    save_easyassist_system_audit_trail("edit_access", "agent_requested_edit_access");

    show_easyassist_toast("Request for edit access has been sent to client.");
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

        encrypted_data = custom_encrypt(json_string);

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

function get_support_material() {
    document.getElementById("support_material_modal_info").innerHTML = "";

    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID
    });

    encrypted_data = custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/agent/get-support-material/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            div_inner_html = "";
            if (response.status == 200) {
                var support_document = response.support_document;
                if (support_document.length > 0) {
                    for (var index = 0; index < support_document.length; index++) {
                        var support_document_obj = support_document[index];
                        var file_name = support_document_obj["file_name"];
                        var file_path = window.location.protocol + "//" + window.location.host + "/" + support_document_obj["file_path"];
                        var message = file_name;
                        div_inner_html += '<tr>';
                        div_inner_html += '<td style="vertical-align:middle;"> <a class="support-document-link" href="' + file_path + '?salesforce_token=' + window.SALESFORCE_TOKEN + '" target="_blank" >' + file_name + '</a> </td>';
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
                    }
                } else {
                    document.getElementById("support_material_modal_info").innerHTML = "No Support Document Found.";
                }
            } else {
                document.getElementById("support_material_modal_info").innerHTML = "Unable to load the details. Try again.";
            }
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
            AGENT_CONNECT_MESSAGE = response.agent_connect_message;
            if (response.status == 200 && response.chat_history.length > 0) {
                AGENT_CONNECT_MESSAGE = "";
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
    console.log("inside startRecording function");

    try {

        displayStream = await navigator.mediaDevices.getDisplayMedia({
            video: { mediaSource: "screen" }
        });
        [videoTrack] = displayStream.getVideoTracks();
        
        try {

            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                console.log('getUserMedia supported.');
                audioStream = await navigator.mediaDevices.getUserMedia({
                    audio: true,
                    video: false
                });
                [audioTrack] = audioStream.getAudioTracks();
            }

            stream = new MediaStream([videoTrack, audioTrack]);
            recorder = new MediaRecorder(stream);
        } catch (err) {
            console.error(err);
            stream = new MediaStream([videoTrack]);
            recorder = new MediaRecorder(stream);
        }
        // stream = new MediaStream([videoTrack, audioTrack]);
        // recorder = new MediaRecorder(stream);
    } catch(err) {
        console.error(err);
        screen_recorder_on = false;
        e.children[0].setAttribute("fill", '#191717');
        e.children[1].innerHTML = "Start screen recording"
        return;
    }

    recorder.ondataavailable = blob => save_cobrowseing_recorded_data(blob);

    recorder.start(5000);
}

function save_cobrowseing_recorded_data(blob) {

    console.log("inside save_cobrowseing_recorded_data");

    var filename = COBROWSE_SESSION_ID + '.webm';
    var file = new File([blob.data], filename, {
        type: 'video/webm'
    });
    var formData = new FormData();
    formData.append("uploaded_data", file);
    formData.append("session_id", COBROWSE_SESSION_ID);
    formData.append("screen_recorder_on", screen_recorder_on);

    $.ajax({
        url: "/easy-assist-salesforce/save-cobrowsing-screen-recorded-data/?salesforce_token=" + window.SALESFORCE_TOKEN,
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
        // stream.getAudioTracks()[0].stop();
    } else {
        e.children[0].setAttribute("fill", 'red');
        e.children[1].innerHTML = "Stop screen recording"
        startRecording(e);
        screen_recorder_on = true;
        console.log("inside screen recodding");
    }
}

function connect_with_client(session_id) {
    $("#request_meeting_modal").modal("hide");
    if (session_id == null || session_id == undefined) {

        return;
    }
    window.open("/easy-assist-salesforce/meeting/" + session_id + "?is_meeting_cobrowsing=true&salesforce_token=" + window.SALESFORCE_TOKEN, "_blank",);
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
                document.getElementById("request_meeting_error").innerHTML = "Meeting request has been sent to customer."
                document.getElementById("request_button").innerText = "Request Sent"
                setInterval(function() {
                    check_meeting_status(session_id)
                }, 5000)
            }
        }
    }
    xhttp.send(params);
}


function check_meeting_status(session_id) {
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
    xhttp.open("POST", "/easy-assist-salesforce/agent/check-meeting-status/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                if (response.is_meeting_allowed == true) {
                    document.getElementById("request_meeting_error").innerHTML = "Meeting request has been accepted by the customer. Please click on 'Connect' to join the meeting."
                    var html = document.getElementById("request_meeting_button");
                    var button = '<button class="btn btn-success" type="button" onclick="connect_with_client(\'' + session_id + '\')">Connect</button>\
                        <button class="btn btn-primary" id="request_button" type="button" onclick="request_for_meeting(\'' + session_id + '\')">Re-send Request</button>';
                    html.innerHTML = button
                } else if (response.is_meeting_allowed == false) {
                    if(response.is_client_answer == true){
                        document.getElementById("request_meeting_error").innerHTML = "Meeting request has been rejected by customer."
                    }
                    var html = document.getElementById("request_meeting_button");
                    var button = '<button class="btn btn-secondary" type="button" data-dismiss="modal">Close</button>\
                        <button class="btn btn-primary" id="request_button" type="button" onclick="request_for_meeting(\'' + session_id + '\')">Re-send Request</button>';
                    html.innerHTML = button
                }
            } else if (response.status == 301) {}
        }
    }
    xhttp.send(params);
}

/***************** EasyAssist Custom Select ***********************/

class EasyassistCustomSelect {
    constructor(selector, placeholder, background_color) {
        this.placeholder = placeholder;
        background_color = background_color;

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

        for(var idx = 0; idx < select_element.children.length; idx ++) {
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