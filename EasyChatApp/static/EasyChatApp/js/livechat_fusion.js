"use strict";

//////////////////// Global Variables ///////////////////////////////////

var livechat_speech_response = "";
var customer_info_needed = true;
var email = "not_available";
var phone = "not_available";
var username = "not_available";
var send_ping_to_socket_holder = null;
var livechat_category = "-1";
var livechat_notification = AGENT_UNAVAILABLE_TEXT;
var livechat_session_id = "";
var easychat_user_id = "";
var check_agent_assign_timer = null;
var need_to_add_wel_msg = true;
var chat_socket = null;
var update_window_storage = null;
var livechat_customer_name = "";
var livechat_user_id_feedback = "";
var livechat_session_id_feedback = ""
var is_chat_socket_open = false;
var rate_value = "";
var livechat_nps_text = "";
var hide_bot_typing_loader_timeout = null;
var agent_socket = null;
var agent_socket_open = false;
var agent_websocket_token = "";
var left_msg_append = false;
var send_ping_to_agent_socket_holder = null;
var is_mute_before_livechat = false;
var message_id = "";
var selected_language = SELECTED_LANGUAGE;
var cobrowsing_meeting_id = null;
var assigned_agent_username = "";
var cobrowsing_status = "none";
var is_chat_escalation_report_notified = false;
var livechat_form_name_error_text = "";
var livechat_form_email_error_text = "";
var livechat_form_phone_error_text = "";
var livechat_form_category_error_text = "";
var meeting_id = "";
var agent_name = "";
var livechat_voip_start_time = "";
let livechat_queue_timer = null;

//////////////////// Global Variables End ///////////////////////////////

/////////////////// API Endpoints ///////////////////////////////////////

var GET_LIVECHAT_CATEGORY = "/livechat/get-livechat-category/";
var SAVE_LIVECHAT_FEEDBACK = "/livechat/save-livechat-feedback/";
var GET_PREVIOUS_MESSAGES = "/livechat/get-livechat-previous-messages/";
var CREATE_CUSTOMER = "/livechat/fusion/create-customer/";
var ASSIGN_AGENT = "/livechat/assign-agent/";
var MARK_CHAT_ABANDONED = "/livechat/mark-chat-abandoned/";
var SAVE_CUSTOMER_CHAT = "/livechat/fusion/save-customer-chat/";

/////////////////// API Endpoints Ends //////////////////////////////////

///////////////////  Exports ////////////////////////////////////////////

(function (exports) {
    var something_assigned_livechat = false;
    var count_of_unread_message =0;

    exports.something_assigned_livechat = something_assigned_livechat;
    exports.count_of_unread_message = count_of_unread_message;

    function append_livechat_response(is_text_to_speech_required, speech_response) {

        set_livechat_default_parameters();

        is_bot_response_message_showed = true;
        is_text_to_speech_required = is_text_to_speech_required;

        if (customer_info_needed) {
            if (show_livechat_form_or_no) {
                cancel_text_to_speech();
                append_info_form();
                customer_info_needed = false;
            }
        } else {
            if (is_text_to_speech_required) {
                livechat_speech_response = speech_response;
                text_to_speech(livechat_speech_response);
            }

            create_customer(
                bot_id,
                email,
                phone,
                username,
                livechat_category,
                window_location,
                easychat_user_id
            );
        }
    }
    exports.append_livechat_response = append_livechat_response;

    function clear_livechat_data(end_message) {
        if (is_chat_socket_open == true && chat_socket != null) {
            if (left_msg_append == false) {
                if (livechat_session_id != "") {
                    var chat_ended_by;
                    if (!end_message) {
                        end_message = "Customer left the chat"; 
                        livechat_notification = CHAT_ENDED_TEXT;
                        chat_ended_by = "Customer";
                    } else {
                        livechat_notification = end_message;
                        chat_ended_by = "System";
                    }

                    save_customer_chat(
                        end_message,
                        livechat_session_id,
                        "System",
                        "",
                        "",
                        chat_ended_by,
                        "",
                        true
                    );
                    left_msg_append == true;
                    var sentence = JSON.stringify({
                        message: JSON.stringify({
                            text_message: end_message,
                            type: "text",
                            channel: window.channel_name_iframe,
                            path: "",
                            event_type: "ENDBYUSER",
                        }),
                        sender: "System",
                    });

                    sentence = encrypt_variable(sentence);
                    chat_socket.send(sentence);
                    if(!is_chat_escalation_report_notified) {
                        send_notification_to_agent(end_message);
                    }
                    is_chat_escalation_report_notified = false;
                }
                mark_chat_unavailable_or_abandoned(livechat_session_id, false);
                chat_socket.close();
            }

            remove_queue_timer();
        }
        if (check_agent_assign_timer != null) {
            clearInterval(check_agent_assign_timer);
        }
        is_conversaion_started = false;
        is_doubletick = false;
    }
    exports.clear_livechat_data = clear_livechat_data;

    function livechat_previous_message_history(livechat_session_id) {
        var json_string = JSON.stringify({
            livechat_session_id: livechat_session_id,
        });
        json_string = encrypt_variable(json_string);
        json_string = encodeURIComponent(json_string);

        var CSRF_TOKEN = get_csrf_token();
        var xhttp = new XMLHttpRequest();
        var params = "json_string=" + json_string;
        xhttp.open("POST", GET_PREVIOUS_MESSAGES, true);
        xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xhttp.setRequestHeader("X-CSRFToken", CSRF_TOKEN);
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                let response = JSON.parse(this.responseText);
                response = custom_decrypt(response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    var response_objs = response.message_history;
                    cobrowsing_status = response.cobrowsing_status;
                    cobrowsing_meeting_id = response.cobrowsing_meeting_id;
                    username = response.customer_details.username;
                    phone = response.customer_details.phone;
                    email = response.customer_details.email;
                    assigned_agent_username = response.assigned_agent_username;
                    livechat_customer_name = response.livechat_customer_name;
                    agent_websocket_token = response.agent_websocket_token;
                    meeting_id = response.meeting_id;
                    agent_name = response.agent_name;
                    livechat_voip_start_time = response.livechat_voip_start_time;

                    create_agent_socket();
                    start_call_timer(null, null);
                    
                    if (response_objs.length == 0 && false) {
                        unset_livechat_cookies();
                        if (livechat_session_id != "") {
                            mark_chat_unavailable_or_abandoned(livechat_session_id, false);
                            chat_socket.close();
                        }
                    } else {
                        create_socket(livechat_session_id);
                        set_footer_for_livechat();
                        var no_of_messages_after_agent = 0;
                        for (var i = 0; i < response_objs.length; i++) {
                            if (response_objs[i].sender == "Customer") {
                                if (response_objs[i].attached_file_src != "") {
                                    try {
                                        let file_path = response_objs[i].attached_file_src.split("/")
                                        let file_name = file_path[file_path.length -1]
                                    
                                        append_user_attachment_preview(file_name,response_objs[i].preview_attachment_file_path,"",response_objs[i].time)
                                    } catch (err) {
                                        console.log(err)
                                    }
                                } else {
                                    append_user_input(
                                        response_objs[i].message,
                                        response_objs[i].time
                                    );
                                }
                                no_of_messages_after_agent++;
                                scroll_to_bottom();
                                maximize_chatbot();
                            } else if (response_objs[i].sender == "Agent") {

                                var text_message = response_objs[i].message;
                                if(response_objs[i].translated_text != "")
                                    text_message = response_objs[i].translated_text;

                                no_of_messages_after_agent = 0;
                                if (response_objs[i].attached_file_src != "") {
                                    append_file_to_customer(
                                        response_objs[i].attached_file_src,
                                        text_message,
                                        response_objs[i].file,
                                        response_objs[i].time,
                                        response_objs[i],
                                    );
                                } else {
                                    if (response_objs[i].meeting_link != ""){
                                        // let meeting_id = localStorage.getItem('meeting_id');
                                        append_meeting_link(response_objs[i].message, meeting_id, response_objs[i])
                                    } else{
                                        append_bot_text_response(
                                            text_message,
                                            response_objs[i].time,
                                            undefined,
                                            response_objs[i],
                                        );
                                    }
                                }
                                scroll_to_bottom();
                                maximize_chatbot();
                            } else if (response_objs[i].sender == 'System') {
                                if ((response_objs[i].is_video_call_message || response_objs[i].is_voice_call_message || response_objs[i].is_cobrowsing_message) && response_objs[i].message_for == 'customer') {
                                    append_system_text_response(response_objs[i].message)
                                } else if (response_objs[i].is_customer_warning_message) {
                                    var text_message = response_objs[i].message;
                                    if(response_objs[i].translated_text != "")
                                        text_message = response_objs[i].translated_text;
                                    append_system_warning_response(text_message);
                                } else {
                                    var text_message = response_objs[i].message;
                                    if(response_objs[i].translated_text != "")
                                        text_message = response_objs[i].translated_text;
                                    append_system_text_response(text_message);                                          
                                }
                            }
                        }
                        mark_all_message_seen();
                        unmark_last_n_message_unseen(no_of_messages_after_agent);
                        check_for_message_seen_signal();
                        set_cobrowsing_status(cobrowsing_status);
                    }
                    scroll_to_bottom();
                }
            }
        };
        xhttp.send(params);
    }
    exports.livechat_previous_message_history = livechat_previous_message_history;

    function send_message_in_socket (message, livechat_session_id, sender, path, thumbnail_url, preview_file_src, language) {
        if(language) {
            selected_language = language;
        }
        if (is_chat_socket_open && chat_socket != null) {
            save_customer_chat(message, livechat_session_id, sender, path, thumbnail_url, "",preview_file_src);
            var sentence = JSON.stringify({
                'message': JSON.stringify({ "text_message": message, "type": "text", "channel": window.channel_name_iframe, "path": path, "thumbnail_url": thumbnail_url, "message_id": message_id, "language": selected_language }),
                'sender': 'Customer',
            });
            sentence = encrypt_variable(sentence);
            chat_socket.send(sentence);
            send_notification_to_agent(message, path, thumbnail_url, "");
        }
    }
    exports.send_message_in_socket = send_message_in_socket;
    
    function send_typing_message_to_agent() {
        var user_query = document.getElementById("user_input").value;
    
        if (!is_livechat || user_query == "") return;
    
        if (is_chat_socket_open == true && chat_socket != null) {
            var sentence = JSON.stringify({
                message: JSON.stringify({
                    text_message: "",
                    type: "text",
                    channel: window.channel_name_iframe,
                    path: "",
                    event_type: "CUSTOMER_TYPING",
                }),
                sender: "System",
            });
            sentence = encrypt_variable(sentence);
            chat_socket.send(sentence);
            send_notification_to_agent("", "", "", "CUSTOMER_TYPING");
        }
    }
    exports.send_typing_message_to_agent = send_typing_message_to_agent;

    function close_livechat(end_message) {
        // var meeting_id = localStorage.getItem('meeting_id');

        if (meeting_id && !is_chat_escalation_report_notified) {
            $('#end_ongoing_call_popup').show();

            setTimeout(function() {
                $('#end_ongoing_call_popup').hide();
            }, 2000);

            return;
        } else {
            send_cancel_meet_notification();
        }

        if (cobrowsing_status == 'ongoing') {
            $('#end_ongoing_cobrowsing_popup').show();

            setTimeout(function() {
                $('#end_ongoing_cobrowsing_popup').hide();
            }, 2000);

            return;
        }

        if (EASYCHAT_BOT_THEME == "theme_1" ) {
            document.getElementById("user_input").style.paddingLeft = "5px";
        }

        unset_livechat_cookies();
        clear_userData(end_message);
        save_time_spent();
        chat_socket.close();
        resize_chabot_window();
        setTimeout(scroll_to_bottom, 1000);
        handle_enable_response_form_assist();
        update_inaccessible_file_icons();
    }
    exports.close_livechat = close_livechat;

    function is_livechat_enabled(){
        return is_livechat
    }
    exports.is_livechat_enabled = is_livechat_enabled;

    function append_attachment_icon() {
        document.getElementById("easychat-img-div").style.display = "flex";

        try {
            var elem_id = "easychat-mic-div";
            if (!mic_access) elem_id = "easychat-mic-div-not-allowed";

            document.getElementById(elem_id).style.paddingRight = "0";
        } catch (err) {
            console.log(err);
        }
    }
    exports.append_attachment_icon = append_attachment_icon;

    function disable_footer_except_home() {
        chat_footer.style.pointerEvents = "none";
        restart_btn.style.pointerEvents = "all";
    }
    exports.disable_footer_except_home = disable_footer_except_home;  

    function enable_footer() {
        chat_footer.style.pointerEvents = "auto";
    }
    exports.enable_footer = enable_footer;   

    function is_image(attached_file_src) {
        var file_ext = attached_file_src.split(".");
        file_ext = attached_file_src.split(".")[file_ext.length - 1];
        file_ext = file_ext.toUpperCase();
    
        if (
            ["PNG", "JPG", "JPEG", "SVG", "BMP", "GIF", "TIFF", "EXIF", "JFIF"].indexOf(file_ext) != -1
        ) {
            return true;
        }
    
        return false;
    }
    exports.is_image = is_image;   
    
    function is_video(attached_file_src) {
        var file_ext = attached_file_src.split(".");
        file_ext = attached_file_src.split(".")[file_ext.length - 1];
        file_ext = file_ext.toUpperCase();
        if (
            [
                "WEBM",
                "MPG",
                "MP2",
                "MPEG",
                "MPE",
                "MPV",
                "OGG",
                "MP4",
                "M4P",
                "M4V",
                "AVI",
                "WMV",
                "MOV",
                "QT",
                "FLV",
                "SWF",
                "AVCHD",
            ].indexOf(file_ext) != -1
        ) {
            return true;
        }
    
        return false;
    }
    exports.is_video = is_video;

    function send_message_over_socket(message, event_type) {
        if (is_chat_socket_open == true && chat_socket != null) {
            message = encrypt_variable(message);
            chat_socket.send(message);
            
            send_notification_to_agent("", "", "", event_type);
        }
    }
    exports.send_message_over_socket = send_message_over_socket

    function modal_content_position_as_per_lang(id) {

        $("#"+ id +" .voice-call-modal-header").css("justify-content", "flex-start");

    }
    exports.modal_content_position_as_per_lang = modal_content_position_as_per_lang

    function get_meeting_id() {
        return meeting_id;
    }
    exports.get_meeting_id = get_meeting_id

    function get_agent_name() {
        return agent_name;
    }
    exports.get_agent_name = get_agent_name

    function get_livechat_voip_start_time() {
        return livechat_voip_start_time;
    }
    exports.get_livechat_voip_start_time = get_livechat_voip_start_time
}
)(window);

////////////////// Exports Ends /////////////////////////////////////////

function set_livechat_default_parameters() {
    is_livechat = true;
    need_to_add_wel_msg = true;
    chat_socket = null;
    check_agent_assign_timer = null;
    customer_info_needed = true;
    email = "not_available";
    phone = "not_available";
    username = "not_available";
    send_ping_to_socket_holder = null;
    livechat_category = "-1";
    livechat_notification = AGENT_UNAVAILABLE_TEXT;
    is_text_to_speech_required = false;
    livechat_speech_response = "";
    easychat_user_id = user_id;
    is_abruptly_closed = false;

    parent.postMessage({
        event_id: 'update_livechat_unload_event_flag',
    }, "*")

    // update_window_storage = setInterval(update_local_storage_window, 1000);
}

function get_url_vars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function (m, key, value) {
        vars[key] = value;
    });
    return vars;
}

$(document).ready(function() {
    var placeholder_left = $(".easychat-country-code-dropdown-wrapper .flag-container").innerWidth();

    $(".country-dropdown-placeholder").css("left", placeholder_left + 14);

});

function display_error_livechat_modal(error_text) {
    let error_elem = document.getElementById("easychat_customer_info_form_error");
    error_elem.style.display = "block";
    error_elem.firstChild.innerText = error_text;
}

function create_customer(
    bot_id,
    email,
    phone,
    username,
    livechat_category,
    window_location,
    easychat_user_id
) {
    // if (livechat_session_id != "") {
    //     add_livechat_loader();
    //     create_socket(livechat_session_id);
    //     append_attachment_icon();
    //     check_agent_assign_timer = setInterval(assign_agent, 5000);
    //     return;
    // }
    livechat_customer_name = username;
    // localStorage.setItem('livechat_customer_name', livechat_customer_name);

    var is_mobile = (('ontouchstart' in document.documentElement && (/mobi/i.test(navigator.userAgent))) || (navigator.userAgent.match(/(iPad)/) || (navigator.platform === 'MacIntel' && typeof navigator.standalone !== "undefined")));

    var source = is_mobile ? 'Mobile': 'Desktop';
    var customer_details = [{'key': 'Source', 'value': source}];

    var channel = window.channel_name_iframe

    var url_parameters = get_url_vars();
    var customer_language = url_parameters["selected_language"]

    var json_string = JSON.stringify({
        bot_id: bot_id,
        username: username,
        phone: phone,
        client_id: phone,
        email: email,
        livechat_category: livechat_category,
        message: livechat_trigger_message,
        active_url: window_location,
        easychat_user_id: easychat_user_id,
        customer_details: customer_details,
        channel: channel,
        customer_language: customer_language,
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", CREATE_CUSTOMER, false);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = this.response;
            response = JSON.parse(response);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response.status_code == "200") {
                document.getElementById("customer_info_form_modal").remove();
                chat_container.style.overflow = "auto";
                if (EASYCHAT_BOT_THEME == "theme_4") {
                    $('#easychat-chat-container').css('overflow-x', 'hidden')
                    $('#easychat-chat-container').css('overflow-y', 'auto')
                }
                livechat_session_id = response.session_id;
                livechat_notification = response.livechat_notification;
                add_livechat_loader();
                create_socket(livechat_session_id);
                // append_attachment_icon();
                if (page_embed_in_iframe()) {
                    parent.postMessage(
                        {
                            event_id: "livechat_cookie_session_user_id",
                            data: {
                                livechat_cookie_session_id: livechat_session_id,
                            },
                        },
                        "*"
                    );
                }
                assign_agent(true);
                check_agent_assign_timer = setInterval(assign_agent, 5000);
            } else if (response.status_code == "300") {
                document.getElementById("customer_info_form_modal").remove();
                chat_container.style.overflow = "auto";
                if (EASYCHAT_BOT_THEME == "theme_4") {
                    $('#easychat-chat-container').css('overflow-x', 'hidden')
                    $('#easychat-chat-container').css('overflow-y', 'auto')
                }
                var assigned_agent = response["assigned_agent"];
                livechat_notification = response["message"];

                setTimeout(function () {
                    is_livechat = false;
                    enable_language_change_options();
                    unset_livechat_cookies();
                    append_system_text_response(livechat_notification);
                    append_bot_text_response(default_response);
                    if (is_text_to_speech_required) {
                        text_to_speech(default_response);
                    }
                    scroll_to_bottom();
                }, 1000);
            } else if (response.status_code == "400") {
                var error_elem = document.getElementById("easychat_customer_info_form_error");
                error_elem.style.display = "block";
                error_elem.firstChild.innerHTML = response["status_message"];

            } else {
                document.getElementById("customer_info_form_modal").remove();
                chat_container.style.overflow = "auto";
                if (EASYCHAT_BOT_THEME == "theme_4") {
                    $('#easychat-chat-container').css('overflow-x', 'hidden')
                    $('#easychat-chat-container').css('overflow-y', 'auto')
                }
                M.toast(
                    {
                        html: "Unable to delete due to some internal server error. Kindly report the same",
                    },
                    2000
                );
                console.log("Please report this. ", response["status_message"]);
            }
        }
        else if(this.status == 403){
            display_error_livechat_modal(CATEGORY_AUTHENTICATION_ERROR_TEXT)
            return;
        }
    };
    xhttp.send(params);
}

function add_livechat_loader() {
    var loader = document.createElement("div");
    loader.setAttribute("id", "livechat-loader-div");
    loader.innerHTML =
        '<div style="width:100%;float:left; display:none;" id="livechat-loader"><img src="' +
        EASYCHAT_IMG_PATH +
        'preloader.svg" style="height:3em;"></div>';
    //chat_footer.prepend(loader);
    chat_footer.insertBefore(loader, chat_footer.childNodes[0]);
}

function check_and_close_timers(){
    if(livechat_queue_timer){
        clearInterval(livechat_queue_timer);
        livechat_queue_timer = null;
    }
    if(check_agent_assign_timer){
        check_agent_assign_timer = clearInterval(check_agent_assign_timer);
        check_agent_assign_timer = null;
    }
}

function assign_agent(is_initial_call = false) {
    if (!is_initial_call && (is_livechat == false || is_chat_socket_open == false || chat_socket == null)) {
        return;
    }

    var json_string = JSON.stringify({
        session_id: livechat_session_id,
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", ASSIGN_AGENT, true);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = this.response;
            response = JSON.parse(response);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            agent_websocket_token = response["agent_websocket_token"];
            // localStorage.setItem('agent_websocket_token', agent_websocket_token);
            var assigned_agent = "";
            if ("livechat_notification" in response && response["livechat_notification"] != "") {
                livechat_notification = response["livechat_notification"];
            }

            if ("assigned_agent" in response) {
                assigned_agent = response["assigned_agent"];
            }

            if (assigned_agent == "") {
                return;
            }
            if (assigned_agent == "scheduler_queue") {
                if (queue_timer == livechat_queue_time / 5 + 1) {
                    append_queue_timer();
                }

                queue_timer -= 1;
                if (queue_timer == 0) {
                    is_livechat = true;
                    something_assigned_livechat = true;
                    mark_chat_unavailable_or_abandoned(livechat_session_id, true);
                    livechat_notification = AGENT_UNAVAILABLE_TEXT;
                    chat_socket.close();
                    remove_queue_timer();
                    enable_user_input();
                    enable_footer();
                    show_footer()
                } else {
                    queue_timer_fun(queue_timer * 5);
                }
            } else if (assigned_agent == "None") {
                check_and_close_timers();
                need_to_add_wel_msg = true;
                unset_livechat_cookies();
                hide_end_chat_button();
                is_livechat = false;
                enable_language_change_options();
                if (chat_socket != null && is_chat_socket_open != false) {
                    something_assigned_livechat = true;
                    mark_chat_unavailable_or_abandoned(livechat_session_id, false);
                    chat_socket.close();
                }
                remove_queue_timer();
            } else if (assigned_agent == "not_available") {
                check_and_close_timers();
                something_assigned_livechat = true;
                is_livechat = true;
                mark_chat_unavailable_or_abandoned(livechat_session_id, false);
                chat_socket.close();
                unset_livechat_cookies();
                remove_queue_timer();
            } else if (assigned_agent == "session_end") {
                check_and_close_timers();
                is_livechat = false;
                enable_language_change_options();
                disable_attachment_icon();
                hide_voip_call_btn();
                enable_mute_unmute_icon();
                something_assigned_livechat = true;
                mark_chat_unavailable_or_abandoned(livechat_session_id, false);
                chat_socket.close();
                need_to_add_wel_msg = true;
                remove_queue_timer();
                scroll_to_bottom();
            } else if (assigned_agent == "abruptly_end") {
                check_and_close_timers();
                is_bot_response_message_showed = true;
                something_assigned_livechat = true;
                mark_chat_unavailable_or_abandoned(livechat_session_id, false);
                chat_socket.close();
                unset_livechat_cookies();
                need_to_add_wel_msg = true;
                remove_queue_timer();
                scroll_to_bottom();
            } else {
                handle_agent_joined(response.joined_chat_text, response.assigned_agent_username);
            }
        }
    };
    xhttp.send(params);
}

function unset_livechat_cookies() {
    if (livechat_session_id != "") {
        parent.postMessage(
            {
                event_id: "unset_livechat_cookies",
                data: {
                    livechat_cookie_session_id: livechat_session_id,
                },
            },
            "*"
        );
    }

    // localStorage.removeItem('agent_websocket_token');
    // localStorage.removeItem('livechat_customer_name');
}

// This function is used to mark chat session expire for non-working hour or holiday. Also, it is used to mark chat abandoned if no agent available to tak chat.
function mark_chat_unavailable_or_abandoned(livechat_session_id_to_end_chat, is_abandoned) {
    var json_string = JSON.stringify({
        is_abandoned: is_abandoned,
        session_id: livechat_session_id_to_end_chat,
        is_abruptly_closed: is_abruptly_closed,
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", MARK_CHAT_ABANDONED, true);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = this.response;
            response = JSON.parse(response);
            response = custom_decrypt(response);
            response = JSON.parse(response);

            if (response["status_code"] == "200") {
                console.log("Success"); // Just for debugging purpose
                livechat_session_id = "";
            } else {
                console.log("Unable to mark chat abandoned."); // Just for debugging purpose
            }
        }
    };
    xhttp.send(params);
}

function mark_all_message_seen() {
    var easychat_doubletick_list = document.getElementsByClassName("doubletick_livechat");
    var src = EASYCHAT_IMG_PATH + "doubletick_blue.svg";
    for (var itr = 0; itr < easychat_doubletick_list.length; itr++) {
        easychat_doubletick_list[itr].src = src;
    }
}

function unmark_last_n_message_unseen(no_of_messages_after_agent) {
    var easychat_doubletick_list = document.getElementsByClassName("doubletick_livechat");
    var src = EASYCHAT_IMG_PATH + "doubletick_black.svg";
    // iterating in last n messages done after agent and marking them unread
    for (
        var itr = easychat_doubletick_list.length - no_of_messages_after_agent;
        itr < easychat_doubletick_list.length;
        itr++
    ) {
        easychat_doubletick_list[itr].src = src;
    }
}

function check_for_message_seen_signal() {
    $(window).focus(function () {
        try {
            if (parent.document.getElementById('allincall-chat-box').style.display == 'none') {
                return;
            }
        } catch(err){
            console.log(err);
        }

        if (is_chat_socket_open == true && chat_socket != null) {
            var sentence = JSON.stringify({
                message: JSON.stringify({
                    text_message: "",
                    type: "text",
                    channel: window.channel_name_iframe,
                    path: "",
                    event_type: "CUSTOMER_MESSAGE_SEEN",
                }),
                sender: "System",
            });
            sentence = encrypt_variable(sentence);
            chat_socket.send(sentence);
        }
        send_notification_to_agent("", "", "", "CUSTOMER_MESSAGE_SEEN");
    });
}

function save_customer_chat(
    sentence,
    livechat_session_id,
    sender,
    path,
    thumbnail_file_path,
    chat_ended_by,
    preview_file_src,
    is_chat_disconnected=false
) {
    if (path === undefined) {
        path = "";
    }
    if (chat_ended_by === undefined) {
        chat_ended_by = "";
    }

    var json_string = {
        message: sentence,
        sender: sender,
        attached_file_src: path,
        thumbnail_file_path: thumbnail_file_path,
        session_id: livechat_session_id,
        chat_ended_by: chat_ended_by,
        preview_file_src: preview_file_src,
        is_chat_disconnected: is_chat_disconnected,
    };

    json_string = JSON.stringify(json_string);
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", SAVE_CUSTOMER_CHAT, false);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = this.response;
            response = JSON.parse(response);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == 200 || response["status_code"] == "200") {
                console.log("chat send by customer saved");
                message_id = response["message_id"];
            }
        }
    };
    xhttp.send(params);
}

function append_system_text_response(text_response) {
    window.clearTimeout(bot_inactivity_timer);
    is_bot_inactivity_msg_present = false

    var time = return_time();
    var html = '<div class="easychat-system-message-div" ><div class="easychat-system-message easychat-system-message-line" style="color: '+BOT_THEME_COLOR+'">' + text_response
    //html += '<span class="message-time-bot" style="display:inline-block !important;">' + time + '</span></div></div>'
    document.getElementById("easychat-chat-container").innerHTML += html
    if (bot_inactivity_detection_enabled && bot_inactivity_detection_required) {
        reset_bot_inactivity_timer()
    }
    enable_user_input()
    document.getElementById("easychat-footer").style.pointerEvents = "auto";
}

function append_system_warning_response(text_response) {

    window.clearTimeout(bot_inactivity_timer);
    is_bot_inactivity_msg_present = false

    var time = return_time();
    var html = '<div class="easychat-system-message-div"><div class="livechat-escalation-abusive-word-warning-message">'+ text_response +'</div></div>';

    document.getElementById("easychat-chat-container").innerHTML += html
    if (bot_inactivity_detection_enabled && bot_inactivity_detection_required) {
        reset_bot_inactivity_timer()
    }
    enable_user_input()
    document.getElementById("easychat-footer").style.pointerEvents = "auto";  
}


/////////////////// LiveChat Customer Info ///////////////////////////////

function append_info_form() {
    scroll_to_bottom();
    chat_container.innerHTML += get_customer_info_form_html();
    chat_container.style.overflow = "hidden";

    check_input_placeholder_position();

    initialize_phone_number_selector( "easychat-customer-phone", "in", "easychat_customer_info_form_error_ptag")

    setTimeout(function () {
        document.getElementById("easychat-customer-name").focus();
    }, 500);

    $("#easychat-customer-name").on('focusout', handle_customer_name_field);
    $("#easychat-customer-email").on('focusout', handle_customer_email_field);
    $("#easychat-customer-phone").on('focusout', handle_customer_phone_field);
    
    var phone_elem = document.getElementById("easychat-customer-phone");
    phone_elem.addEventListener("keydown", function (event) {
        if (event.keyCode == 40 || event.keyCode == 38) {
            event.preventDefault();
        }
    });
    phone_elem.addEventListener("wheel", function (event) {
        event.preventDefault();
    });
    phone_elem.onkeyup = add_phone_number_validation;

    setTimeout(function() {
        disable_footer_except_home();
    }, 1000)
    toggle_sticky_menu("none");
    playSound(STATIC_MP3_PATH + "/juntos3.mov");

    append_livechat_category();

    resize_chabot_window();

}

function handle_customer_name_field() {
    let id = "easychat-customer-name";
    let name = $("#" + id).val().trim();
    
    if (name != "" ) {
        var error_elem = document.getElementById("easychat_customer_info_form_error");
        error_elem.style.display = "none";
        if (selected_language == 'en' && !validate_name(name) || !name.length) {
            livechat_form_name_error_text = NAME_ERROR_TEXT;
        }
        else {
            livechat_form_name_error_text = "";
            indicate_input_field_safe(id);
            check_and_display_livechat_form_text();
        }
        if (livechat_form_name_error_text != "") {
            display_error_livechat_modal(livechat_form_name_error_text)
            indicate_input_field_error(id);
            return;
        }
    } else {
        livechat_form_name_error_text = NAME_ERROR_TEXT;
        display_error_livechat_modal(livechat_form_name_error_text);
        indicate_input_field_error(id);
        return;
    }
}

function handle_customer_email_field() {
    let id = "easychat-customer-email";
    let email = $("#" + id).val();
    
    if (email != "" ) {
        var error_elem = document.getElementById("easychat_customer_info_form_error");
        error_elem.style.display = "none";
        if (!validate_email(email)) {
            livechat_form_email_error_text = EMAIL_ERROR_TEXT
        }
        else {
            livechat_form_email_error_text = "";
            indicate_input_field_safe(id);
            check_and_display_livechat_form_text();
        }
        if (livechat_form_email_error_text != "") {
            display_error_livechat_modal(livechat_form_email_error_text)
            indicate_input_field_error(id);
            return;
        }
    }
    else {
        livechat_form_email_error_text = EMAIL_ERROR_TEXT;
        display_error_livechat_modal(livechat_form_email_error_text);
        indicate_input_field_error(id);
        return;
    }
}

function handle_customer_phone_field() {

    let id = "easychat-customer-phone";
    let phone = document.getElementById(id).value;
    let is_valid = $("#"+id).intlTelInput("isValidNumber");
    let validation_err = $("#"+id).intlTelInput("getValidationError");
    let isnum = /^\d+$/.test(phone);
    if (!isnum) {
        is_valid = false
    }

    if (!is_valid) {

        if(phone_widget_error_map[validation_err] == undefined) {
            validation_err = 0
        }
        livechat_form_phone_error_text = phone_widget_error_map[validation_err];
    
    } else {
        if ($("#customer").intlTelInput("getSelectedCountryData").dialCode == "91") { 
            if (livechat_form_phone_error_text == "" && !validate_phone_number(phone)) {
                    livechat_form_phone_error_text = phone_widget_error_map[0]
            } else {
                livechat_form_phone_error_text = ""; 
                check_and_display_livechat_form_text();
            } 
        } else {
            livechat_form_phone_error_text = "";
            check_and_display_livechat_form_text();  
        }
    }

    if (livechat_form_phone_error_text != "") {
        display_error_livechat_modal(livechat_form_phone_error_text);
    }

}

function handle_customer_category_field() {
    let id = "livechat-agent-category";
    let category_elem = document.getElementById(id);

    let livechat_category = "-1";
    if (category_elem != undefined && category_elem != null) {
        livechat_category = category_elem.value;

        if (livechat_category == "") {
            livechat_form_category_error_text = CATEGORY_ERROR_TEXT;
        } else {
            livechat_form_category_error_text = "";
            check_and_display_livechat_form_text();
        }
    }

    if (livechat_form_category_error_text != "") {
        display_error_livechat_modal(livechat_form_category_error_text);
    }
}

function check_and_display_livechat_form_text() {

    if (livechat_form_name_error_text != "") {
        display_error_livechat_modal(livechat_form_name_error_text);
    } else if (livechat_form_email_error_text != "") {
        display_error_livechat_modal(livechat_form_email_error_text);
    } else if (livechat_form_phone_error_text != "") {
        display_error_livechat_modal(livechat_form_phone_error_text);
    } else if (livechat_form_category_error_text != "") {
        display_error_livechat_modal(livechat_form_category_error_text);
    } else {
        document.getElementById("easychat_customer_info_form_error_ptag").innerHTML = "";
    }
}

function indicate_input_field_error(id) {
    $("#" + id).css({"border" : "1px solid #FF7C7C"})
}

function indicate_input_field_safe(id) {
    $("#" + id).css({"border" : "1px solid #00c900"})
}

function initialize_phone_number_selector(id, country_code, error_div_id) {
 
    window.iti = $("#" + id).intlTelInput({
        initialCountry: country_code,
    
        allowExtensions: true,
        formatOnDisplay: true,
        autoFormat: true,
        autoHideDialCode: true,
        autoPlaceholder: false,
        // utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js",
        utilsScript: "../../static/EasyChatApp/js/phone_widget_utils.js",
        // defaultCountry: "auto",
        ipinfoToken: "yolo",
        nationalMode: false,
        numberType: "MOBILE",
        //onlyCountries: ['us', 'gb', 'ch', 'ca', 'do'],
        preferredCountries: ['in', 'ae', 'qa', 'om', 'bh', 'kw', 'ma'],
        preventInvalidNumbers: true,
        separateDialCode: true,
    })

    var isMobile = /Android.+Mobile|webOS|iPhone|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

    if(!isMobile) {
        if ($("#searchinput_country_livechat_form").length == 0){ 

            $(".easychat-form-div .country-list").prepend("<input autocomplete='off' id='searchinput_country_livechat_form' placeholder='" + SEARCH_TEXT + "..' class='search_phone_number_widget_class'  type='text' onkeydown='filterFunction(event, \"easychat-form-div\")' data-search autofocus/>");
            $(".easychat-form-div .country-list").append("<div class='country-no-result-found' id='country_no_result_found_livechat_modal'>" + NO_RESULT_FOUND + "</div>");
            
            $("#searchinput_country_livechat_form").focus();
            $("#searchinput_country_livechat_form").click(function(event) {
                event.stopPropagation();
                $(".easychat-form-div .country-list").addClass("show");
            });
        }
    }
    var error_div = document.getElementById(error_div_id)

    $(".selected-flag").on("click", function() {
        scroll_livechat_form_to_bottom()
        if (isMobile) {
            $(".searchinput_country_livechat_form").remove()
            $(".country-no-result-found").remove()
            $(".country").css("display", "");
            
            $(".country-list").prepend("<input autocomplete='off' id='searchinput_country_livechat_form' class='searchinput_country_livechat_form' placeholder='" + SEARCH_TEXT + "..' class='search_phone_number_widget_class'  type='text' onkeydown='filterFunction(event, \"easychat-form-div\")' data-search autofocus/>");
            $(" .country-list").append("<div class='country-no-result-found' id='country_no_result_found_livechat_modal'>" + NO_RESULT_FOUND + "</div>");
            
            $("#searchinput_country_livechat_form").focus();
            $("#searchinput_country_livechat_form").click(function(event) {
                event.stopPropagation();
                $(".country-list").addClass("show");
            });
            
        }
    })

    $("#" + id).on("countrychange", function() {
        reset_phone_widget_livechat(id, error_div)
        validate_phone_number_input_livechat_form(id)

      });

    $("#" + id).focus(function() {
        $(".country-dropdown-placeholder").hide();
        
    })

    $("#" + id).keyup(function(event) {
        var character =  event.target.value.charAt(event.target.selectionStart - 1).charCodeAt()
        var value = String.fromCharCode(character)
        if (validate_number_input_value(value, event)) {
            reset_phone_widget_livechat(id, error_div)
        }
        validate_phone_number_input_livechat_form(id)

        
    })

    $("#" + id).keydown(function(event) {
        validate_number_input(event)
      
    })

    $("#" + id).focusout(function() {
        if ($("#" + id).val() == "") {
            $(".country-dropdown-placeholder").show();
    
        } else {
            $(".country-dropdown-placeholder").hide();
        }
    })


}

function reset_phone_widget_livechat(id, error_div) {
    $("#" + id).css({"border" : "1px solid #EBEBEB"})
    error_div.innerHTML = "";
  };

function validate_phone_number_input_livechat_form(id) {
    var is_valid = $("#" + id).intlTelInput("isValidNumber")
    var validation_err = $("#" + id).intlTelInput("getValidationError")
    
        if (!is_valid) {
            $("#" + id).css({"border" : "1px solid #FF7C7C"})
            if(phone_widget_error_map[validation_err] == undefined) {
                validation_err = 0
            }

            return false
    
        } else {
            if ($("#" + id).intlTelInput("getSelectedCountryData").dialCode == "91") {
                if (!validate_phone_number($("#" + id).val())) {
                    $("#" + id).css({"border" : "1px solid #FF7C7C"})

                    return false
                } else {
                    $("#" + id).css({"border" : "1px solid #00C900"})

                    return true
                }
            } else {
                $("#" + id).css({"border" : "1px solid #00C900"})
                return true
            }

        }
}

function filterFunction(event, wrapper_id) {
    var input, filter, ul, a, i;
    input = document.getElementById("searchinput_country_livechat_form");
    
    a = document.querySelectorAll(".country");
    event.stopPropagation();
    setTimeout(function() {
        filter = input.value.toUpperCase();
        var no_results_found = true
        for (i = 0; i < a.length; i++) {
            var txtValue = a[i].textContent || a[i].innerText;
            if (txtValue.toUpperCase().startsWith(filter)) {
                a[i].style.display = "";
                no_results_found = false
            } else {
                a[i].style.display = "none";
            }
        }
        if (no_results_found) {
            document.querySelector(".country-no-result-found").style.display = "block";
        } else {
            document.querySelector(".country-no-result-found").style.display = "none";
        }
        scroll_livechat_form_to_bottom()
    }, 100)

}

function check_input_placeholder_position() {

    $(".easychat-form-div .placeholder").css({"left":"14px", "right": ""});

}

function get_customer_info_form_html() {

    var html =
        '<div id="customer_info_form_modal" class="easychat-modal livechat-agent-modal" style = "display: flex; align-items: center; justify-content: center; overflow: hidden"><div id="livechat-customer-info-form-container" class="easychat-modal-content livechat-agent-modal-content" style="height:fit-content;background: #FBFBFB; box-shadow: 0px 0px 25px rgba(0, 0, 0, 0.25); border-radius: 6px; overflow: hidden; scrollbar-width: thin;">';
    html += '<div id="customer_info_form_div" style="text-align: left;">';
    html +=
        '<p style = "font-weight: 500; font-size: 18px; line-height: 18px; color: #2D2D2D;">' + CONNECT_AGENT_TEXT + '</p>';
    html +=
        '<span style = "font-weight: 500; font-size: 16px; line-height: 16px; color: #4D4D4D;">' + FILL_DETAILS_TEXT + '</span><br>';
    html += '<div class = "easychat-form-div">';
    html += '<div class="placeholder">';
    html += '<label for="name">' + ENTER_NAME_TEXT + '</label>';
    html += '<span class="star">*</span>';
    html += "</div>";
    html +=
        '<input id="easychat-customer-name" class = "easychat-customer-input" autocomplete="off" style="direction:'+ pointer_direction +';">';
    html += "</div>";
    html += '<div class = "easychat-form-div">';
    html += '<div class="placeholder">';
    html += '<label for="name">' + ENTER_EMAIL_TEXT + '</label>';
    html += '<span class="star">*</span>';
    html += "</div>";
    html +=
        '<input id="easychat-customer-email" class = "easychat-customer-input" autocomplete="off" style="direction:'+ pointer_direction +';">';
    html += "</div>";
    html += '<div class = "easychat-form-div">';
    // html += '<div class="placeholder">';
    // html += '<label for="name">' + ENTER_PHONE_TEXT + '</label>';
    // html += '<span class="star">*</span>';
    // html += "</div>";
    html += '<div class="easychat-country-code-dropdown-wrapper">'
    html +=
        '<input type="text" id="easychat-customer-phone" class = "easychat-customer-input"  autocomplete="off" style="direction:'+ pointer_direction +';">';
    html += '<div class="country-dropdown-placeholder">' + ENTER_PHONE_TEXT + '<span>*</span></div>'
    html += "</div>";
    html += "</div>";
    html += '<div id="livechat-agent-category-div" style="cursor: pointer;">';
    html += "</div>";
    html +=
        '<div class="livechat-modal-submit-btn-div" style="display: flex; justify-content: flex-end; align-content: center;">';
    html +=
        '<input type = "button" value = "'+ CANCEL_TEXT +'" class = "easychat-customer-modal-cancel-btn" onclick="close_customer_info_form_modal()">';
    html +=
        '<input class="livechat-modal-submit-btn" style="background-color:' +
        BOT_THEME_COLOR +
        ' ;"onclick="submit_customer_info()" type="submit" value="'+ SUBMIT_TEXT +'">';
    html += "</div>";
    html += '<div id = "easychat_customer_info_form_error" style="display:none;">';
    html +=
        '<p id = "easychat_customer_info_form_error_ptag" style="color:red; margin-bottom:0px; margin-top:8px;"></p>';
    html += "</div>";
    html += "</div>";
    html += '<div id="cutomer_info_form_termination">';
    html +=
        '<p style="text-align: center;font-size: 16px; font-family: silka; color: #7B7A7B;">'+ LIVECHAT_CONTINUE_TEXT +'</p><br>';
    html +=
        '<div id="livechat-info-form-termination-btns"><input class="livechat-modal-continue-btn" onclick="submit_go_back()" type="submit" value="'+ BACK_TEXT +'">';
    html +=
        '<input class="livechat-modal-cancel-btn" style="background-color:' +
        BOT_THEME_COLOR +
        ' ;"onclick="submit_continue()" type="submit" value="'+ CONTINUE_TEXT +'"></div>';
    html += "</div>";
    html += "</div>";
    html += "</div>";

    return html;
}

function append_livechat_category() {
    var json_string = JSON.stringify({
        bot_id: bot_id,
        selected_language: selected_language,
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", GET_LIVECHAT_CATEGORY, true);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);

            if (response.status_code == "200") {
                document.getElementById("livechat-agent-category-div").innerHTML =
                    get_category_html(response.category_list);

                check_input_placeholder_position();

                $("#livechat-agent-category").change(function () {
                    this.size = 1;
                    $(this).siblings(".placeholder").hide();
                });

                $("#livechat-agent-category").focus(function () {
                    $(this).siblings(".placeholder").hide();
                });

                $("#livechat-agent-category")
                    .select2({
                        placeholder: "",
                        allowClear: true,
                        dropdownParent: $("#customer_info_form_modal"),
                    })
                    .on("select2:open", function () {
                        $(".select2-dropdown--below").attr("id", "open-above");
                        $("#open-above").removeClass("select2-dropdown--below");
                        $("#open-above").addClass("select2-dropdown--above");
                    })
                    .on("select2:close", function () {
                        handle_customer_category_field();
                    });
            }
        }

        $(".placeholder").click(function () {
            $(this).siblings("input").focus();
        });

        $(".easychat-customer-input").on("input", function () {
            $(this).siblings(".placeholder").hide();
        });

        $(".easychat-form-div").focusout(function () {
            var input_val = $(this).children(".easychat-customer-input").val();
            if (input_val == null || input_val.length == 0) $(this).children(".placeholder").show();
        });

        $(".easychat-form-div").blur();
    };
    xhttp.send(params);
}

function get_category_html(category_list) {
    var html =
        '<div class="input-field col s12 easychat-form-div"><div class="placeholder placeholdercat" style = "z-index:1; top:30px;"><label for="name">'+ CHOOSE_CATEGORY_TEXT +'</label><span class="star">*</span></div><select id="livechat-agent-category" class = "easychat-customer-input" onfocus="this.size=5;" onblur="this.size=1;" onchange="this.size=1; this.blur();"><option></option>';

    for (var i = 0; i < category_list.length; i++) {
        html +=
            "<option value=" +
            category_list[i]["pk"] +
            ">" +
            category_list[i]["title"] +
            "</option>";
    }
    html += "</select></div>";

    return html;
}

function submit_customer_info() {
    try
    {scroll_to_bottom();
    }
    catch(err)
    {console.log(err)
    }
    is_bot_response_message_showed = true;

    email = document.getElementById("easychat-customer-email").value;
    phone = document.getElementById("easychat-customer-phone").value;
    username = document.getElementById("easychat-customer-name").value.trim();
    var category_elem = document.getElementById("livechat-agent-category");

    var error_text = "";

    if (selected_language == 'en' && !validate_name(username) || !username.length) {
        error_text = NAME_ERROR_TEXT;
    }

    if (error_text == "" && !validate_email(email)) {
        error_text = EMAIL_ERROR_TEXT;
    }
    
    // if (error_text == "" && !validate_phone_number(phone)) {
    //     error_text = INVALID_MOBILE_NUMBER;
    // }

    
    
    var is_valid = $("#easychat-customer-phone").intlTelInput("isValidNumber")
    var validation_err = $("#easychat-customer-phone").intlTelInput("getValidationError")
    let isnum = /^\d+$/.test(phone);
    if (!isnum) {
        is_valid = false
    }
    if (!is_valid) {
        if(phone_widget_error_map[validation_err] == undefined) {
            validation_err = 0
        }
        if (error_text == "") {
            error_text = phone_widget_error_map[validation_err]
        }
    } else {
        if ($("#customer").intlTelInput("getSelectedCountryData").dialCode == "91") { 
            if (error_text == "" && !validate_phone_number(phone)) {
                    error_text = phone_widget_error_map[0]
            } else {
                phone = $("#easychat-customer-phone").intlTelInput("getNumber")
            }
        } else {
            phone = $("#easychat-customer-phone").intlTelInput("getNumber")
        }
        
    }

    var livechat_category = "-1";
    if (error_text == "" && category_elem != undefined && category_elem != null) {
        livechat_category = category_elem.value;
        if (livechat_category == "") {
            error_text = CATEGORY_ERROR_TEXT;
        }
    }


    var error_elem = document.getElementById("easychat_customer_info_form_error");
    error_elem.style.display = "none";
    if (error_text != "") {
        display_error_livechat_modal(error_text)
        return;
    }

    // enable_attachment();
    show_footer();
    disable_mute_unmute_icon();

    if (is_text_to_speech_required) {
        text_to_speech(livechat_speech_response);
    }

    let message_list = send_to_livechat();
    for (var message_list_iterator = 0; message_list_iterator < message_list.length; message_list_iterator++) {
        append_bot_text_response(message_list[message_list_iterator]);
    }
    reset_size_of_text_field(message_list.length);

    create_customer(
        bot_id,
        email,
        phone,
        username,
        livechat_category,
        window_location,
        easychat_user_id
    );

    parent.postMessage(
        {
            event_id: "create-cobrowsing-lead",
            data: {
                username: username,
                email: email,
                phone: phone,
            },
        },
        "*"
    );
}

function close_customer_info_form_modal() {
    document.getElementById("customer_info_form_div").style.display = "none";
    document.getElementById("cutomer_info_form_termination").style.display = "block";
    $("#livechat-customer-info-form-container").css("cssText", "height: fit-content !important;");
}

function submit_go_back() {

    chat_container.style.overflow = "auto";
    if (EASYCHAT_BOT_THEME == "theme_4") {
        $('#easychat-chat-container').css('overflow-x', 'hidden')
        $('#easychat-chat-container').css('overflow-y', 'auto')
    }
    document.getElementById("customer_info_form_modal").remove();
    toggle_sticky_menu("block");
    enable_footer();
    show_footer();
    enable_user_input();

    is_livechat = false;
    customer_info_needed = true;
    if (is_text_to_speech_required) {
        text_to_speech(livechat_speech_response);
        text_to_speech(default_response);
    }
    enable_language_change_options();
    handle_enable_response_form_assist()
    append_welcome_message(bot_id, bot_name, true);
    setTimeout(function () {
        scroll_to_bottom();
    }, 200);
}

function submit_continue() {
    document.getElementById("customer_info_form_div").style.display = "block";
    document.getElementById("cutomer_info_form_termination").style.display = "none";
    $("#livechat-customer-info-form-container").css("cssText", "height: auto !important;");
}

/////////////////// LiveChat Customer Info Ends //////////////////////////

//////////////////// Queue Timer /////////////////////////////////////////

function append_queue_timer() {
    if (EASYCHAT_BOT_THEME != "theme_4") {
        var user_input = REQUEST_IN_PROCESS + "..";
        var html =
            '<br><div style=""width: 92%;margin: auto;margin-top: 1em;"><span id="queue-bar-timer">.</span></div>';
        chat_container.innerHTML +=
            '<div id="livechat_queue" style="display:inline-block;width:92%"><div style="box-shadow: 1px 1px 6px rgba(0, 0, 0, 0.2);color: black;width: 100%;margin: auto;margin-top: 1.5em;border-radius: 1em;padding: 1em;background-color:white;text-align:center;">' +
            user_input +
            html +
            "</div></div>";
    } else {
        chat_container.innerHTML += '<div class="bot-livechat-connect-notif-timer-div" id="livechat_queue">\
                    <div class="bot-livechat-connect-notif-timer-text">' + REQUEST_IN_PROCESS + '..\
                    </div>\
                    <div style="color:#10B981; font-size: 16px; font-weight: 500;" id="queue-bar-timer"></div>\
                </div>'
    }
    setTimeout(function () {
        scroll_to_bottom();
    }, 200);
}

function remove_queue_timer() {
    var livechat_queue = document.getElementById("livechat_queue");

    if (livechat_queue != null && livechat_queue != undefined) {
        livechat_queue.remove();
    }
    queue_timer = livechat_queue_time / 5 + 1;
}

function queue_timer_fun(queue_temp_timer) {
    var timer_value = queue_temp_timer;
    var seconds = Math.round(queue_temp_timer % 60);
    var minutes = Math.floor(queue_temp_timer / 60);
    var stop_at = timer_value - 5;
    livechat_queue_timer = setInterval(function () {
        var queue_bar_timer = document.getElementById("queue-bar-timer");
        if (queue_bar_timer) {
            if (seconds < 10) {
                if (minutes < 10) {
                    queue_bar_timer.textContent = "0" + minutes + ":0" + seconds;
                } else {
                    queue_bar_timer.textContent = minutes + ":0" + seconds;
                }
            } else {
                if (minutes < 10) {
                    queue_bar_timer.textContent = "0" + minutes + ":" + seconds;
                } else {
                    queue_bar_timer.textContent = minutes + ":" + seconds;
                }
            }
            if (timer_value <= 10) {
                queue_bar_timer.style.color = "red";
            }
            if (timer_value > 10 && timer_value <= 20) {
                queue_bar_timer.style.color = "orange";
            }
            if (timer_value > 20) {
                queue_bar_timer.style.color = "green";
            }
        }
        timer_value = timer_value - 1;
        seconds = Math.round(timer_value % 60);
        minutes = Math.floor(timer_value / 60);

        if (timer_value == stop_at) {
            if(livechat_queue_timer){
                clearInterval(livechat_queue_timer);
                livechat_queue_timer = null;
            }
        } else if (timer_value <= 0) {
            remove_queue_timer();
        }
    }, 1000);
}

//////////////////// Queue Timer Ends /////////////////////////////////////

/////////////////// End Chat //////////////////////////////////////////////

function show_end_chat_for_theme_three(){
    $(".easychat-bot-end-chat-button-div").css("display","flex")
    toggle_sticky_menu("none");
    $(".easychat-bot-restart-div").css("display", "none");
    adjust_user_input_for_theme_three_for_livechat();
}

function show_end_chat_button() {

    show_input_field_footer()
    if(EASYCHAT_BOT_THEME == "theme_3"  || EASYCHAT_BOT_THEME == "theme_4"){

        show_end_chat_for_theme_three();
        return
    }

    var html =
        '<div id="easychat-sticky-end-chat" style="margin-bottom:1.35em;overflow-x:auto;width:100%;"><div class="livechat-end-chat-wrapper" style=overflow:hidden;width:max-content;style="margin-bottom:0.28em;>';
    html +=
        '<button class="button_sticky" onclick="close_livechat()" style="color:' +
        BOT_THEME_COLOR +
        ';font-size:15px;outline:auto;border-radius:10px;border:0;height:30px;">'+ END_CHAT_TEXT +'</button>&nbsp;&nbsp;&nbsp;&nbsp;';
    html += "</div></div>";

    end_chat_elem.innerHTML = html;
    end_chat_elem.style.display = "block";
    set_footer_for_livechat();

}

function adjust_user_input_for_theme_three_for_livechat(){
    if(EASYCHAT_BOT_THEME == "theme_3" || EASYCHAT_BOT_THEME == 'theme_4'){
        $(".easychat-bot-user-input-div").css("width","calc(100% - 56px)")
    }
    if (EASYCHAT_BOT_THEME == 'theme_4') {
        $('#easychat-restart-div').css("width", "100%")
        $('.easychat-bot-footer-menus-opner-div').hide()
    }
}

function hide_end_chat_button_based_on_theme(){

    if(EASYCHAT_BOT_THEME == "theme_3" || EASYCHAT_BOT_THEME == "theme_4"){
        $(".easychat-bot-end-chat-button-div").css("display","none")
        
    }else{
        if (end_chat_elem) {
            end_chat_elem.style.display = "none";
        }
    }

    hide_input_field_footer()
}

function hide_end_chat_button() {

    hide_end_chat_button_based_on_theme();

    reset_footer();
    toggle_sticky_menu("block");
}

/////////////////// End Chat Ends /////////////////////////////////////////

/////////////////// Agent Room ///////////////////////////////////////////

function get_agent_websocket_token() {
    return agent_websocket_token == '' ? localStorage.getItem('agent_websocket_token') : agent_websocket_token;
}

function create_agent_socket() {
    if (agent_socket_open == false) {
        // for debugging
        console.log(agent_websocket_token);
        if (!agent_websocket_token) {
            console.log('Cannot create agent socket.');
            return;
        }

        agent_socket = window.location.protocol == "http:" ? "ws://" : "wss://";
        agent_socket += window.location.host + "/ws/" + agent_websocket_token + "/customer/";
        agent_socket = new WebSocket(agent_socket);
        agent_socket.onmessage = agent_socket_message_handler;
        agent_socket.onopen = function (e) {
            // for debugging
            console.log('created!');
            agent_socket_open = true;
            send_ping_to_agent_socket_holder = setInterval(send_ping_to_agent_socket, 1000);
        };

        agent_socket.onclose = function (e) {
            agent_socket_open = false;
        };
    }
}

function send_notification_to_agent(message, path, thumbnail_url, event_type) {
    if (agent_socket_open == true) {
        // if (livechat_customer_name == "") {
        //     livechat_customer_name = localStorage.getItem('livechat_customer_name');
        // }
        var sentence = JSON.stringify({
            message: JSON.stringify({
                text_message: message,
                type: "text",
                channel: window.channel_name_iframe,
                path: path,
                event_type: event_type,
                session_id: livechat_session_id,
                sender_name: livechat_customer_name,
                thumbnail_url: thumbnail_url,
                bot_id: bot_id,
                message_id: message_id,
                language: selected_language,
                cobrowse_session_id: cobrowse_session_id,
            }),
            sender: "Customer",
        });
        sentence = encrypt_variable(sentence);
        agent_socket.send(sentence);
    } else {
        create_agent_socket();
    }
}

function agent_socket_message_handler(e) {
    var data = JSON.parse(custom_decrypt(e.data));
    var sender = data["sender"];

    if (sender == 'inactivity_end_session') {

        close_livechat('Due to inactivity chat has ended');
    } else if (sender == 'CANCEL_MEET') {
        var message = JSON.parse(data["message"]);

        if (message['session_id'] != livechat_session_id) {
            handle_cancel_meet_by_agent();
        }

    } else if (sender == 'MEET_END') {
        var message = JSON.parse(data["message"]);

        if (message['session_id'] == livechat_session_id) {
            if (VOIP_TYPE == 'pip') {
                end_pip_calling();
            }
            
            handle_meet_end(message['meeting_id']);
        }
    } else if (sender == "chat_escalation_report") {
        var message = JSON.parse(data["message"]);
        if (message['session_id'] == livechat_session_id) {
            is_chat_escalation_report_notified = true;
            close_livechat(message["text_message"]);
        }
    }
}

function send_ping_to_agent_socket() {
    if (agent_socket_open == true && agent_socket != null) {
        send_notification_to_agent("", "", "", "CUSTOMER_STILL_THERE");
    }
}

/////////////////// Agent Room Ends ////////////////////////////////////////

/////////////////// LiveChat Room /////////////////////////////////////////

function create_socket(livechat_session_id) {
    is_livechat = true;
    if (chat_socket == null && is_chat_socket_open == false) {
        chat_socket = window.location.protocol == "http:" ? "ws://" : "wss://";
        chat_socket += window.location.host + "/ws/" + livechat_session_id + "/customer/";
        chat_socket = new WebSocket(chat_socket);

        chat_socket.onmessage = send_message_to_agent_socket;
        chat_socket.onopen = open_livechat_socket;
        chat_socket.onclose = close_livechat_socket;
        chat_socket.onerror = onerror_livechat_socket;
    }
}

function send_message_to_agent_socket(e) {
    var data = JSON.parse(custom_decrypt(e.data));
    var message = JSON.parse(data["message"]);
    var sender = data["sender"];
    if (sender == "agent_end_session") {
        append_feedback_form(livechat_session_id);
        unset_livechat_cookies();
        scroll_to_bottom();
        count_of_unread_message++;
        maximize_chatbot();

        if (message.show_cancel_meet_popup) {
            handle_cancel_meet_by_agent();
        }
        handle_enable_response_form_assist();
        update_inaccessible_file_icons();
    } else if (sender == "Agent") {
        var text_message = message.text_message;
        if(message.translated_text != "")
            text_message = message.translated_text;
        if (message["type"] == "file") {
            append_file_to_customer(message.path, text_message, message.thumbnail, undefined, message);
            mark_all_message_seen();
            count_of_unread_message++;
            maximize_chatbot();
        } else if (message["type"] == "text") {
            append_bot_text_response(text_message, undefined, undefined, message);
            mark_all_message_seen();
            count_of_unread_message++;
            maximize_chatbot();
        }
        scroll_to_bottom();
        check_for_message_seen_signal();
    } else if (sender == "System") {
        if ("event_type" in message) {
            if (message["event_type"] == "CHAT_TRANSFERRED" && "session_id" in message) {
                livechat_session_id = message["session_id"];
                agent_websocket_token = message["new_agent_websocket_token"];
                // for debugging
                console.log(agent_websocket_token);
                agent_socket.close();
                create_agent_socket();
                if ("text_message_customer" in message) {
                    append_system_text_response(message["text_message_customer"]);
                }
                count_of_unread_message++;
                maximize_chatbot();
            } else if (message["event_type"] == "AGENT_MESSAGE_SEEN") {
                mark_all_message_seen();
            } else if (message["event_type"] == "AGENT_TYPING") {
                show_bot_typing_loader();
                if (hide_bot_typing_loader_timeout != null) {
                    clearTimeout(hide_bot_typing_loader_timeout);
                }
                hide_bot_typing_loader_timeout = setTimeout(function () {
                    hide_bot_typing_loader();
                }, 5000);
            } else if (message["event_type"] == "GUEST_AGENT_JOINED"){
                if ("text_message_customer" in message) {
                    append_system_text_response(message["text_message_customer"]);
                }
                count_of_unread_message++;
                maximize_chatbot();
            } else if (message["event_type"] == "GUEST_AGENT_EXIT"){
                if ("text_message_customer" in message) {
                    append_system_text_response(message["text_message_customer"]);
                }
                count_of_unread_message++;
                maximize_chatbot();   

            } else if (message["event_type"] == "VOIP_REQUEST") {
                hide_voip_call_btn();
                open_voip_request_modal();
            } else if (message["event_type"] == "VC_REQUEST") {
                $('.voip-call-btn').css({"pointer-events": "none"});
                if(EASYCHAT_BOT_THEME == 'theme_4') $('#voip_call_btn').css("pointer-events", "none");
                open_vc_request_modal();
            } else if (message["event_type"] == "VOIP_CONNECT") {
                    connect_voip_call(message.meeting_id, message.session_id, message.agent_name); 
                    if(VOIP_TYPE == 'video_call'){
                        if(message.request_from_customer){
                            let message_text = LIVECHAT_VC_JOIN_ACCEPTED + ':';
                            append_meeting_link(message_text, message.meeting_id, message);
                        } else{
                            let message_text = LIVECHAT_VC_JOIN + ':';
                            append_meeting_link(message_text, message.meeting_id, message);
                        }

                        scroll_to_bottom();
                    }
            } else if (message['event_type'] == "CUSTOMER_VOIP_ACCEPT") {
                console.log('request accepted');
                if(VOIP_TYPE != 'video_call'){
                    handle_agent_accepted_voip_request(message.meeting_id, message.session_id, message.agent_name);
                } else {
                    $('#agent_accepted_vc_meet_popup').show();

                    setTimeout(function() {
                        $('#agent_accepted_vc_meet_popup').hide();
                    }, 2000);
                }
            } else if (message['event_type'] == 'CUSTOMER_VOIP_REJECT') {

                console.log('request rejected');
                handle_agent_rejected_voip_request(message.meeting_id, message.session_id, message.agent_name);
            } else if (message.event_type == 'COBROWSING_REQUEST') {
                cobrowsing_meeting_id = message.meeting_id;
                open_cobrowsing_request_modal();
            } else if (message["event_type"] == "CUSTOMER_WARNING_MESSAGE"){
                if ("text_message_customer" in message) {
                    append_system_warning_response(message["text_message_customer"]);
                }
                count_of_unread_message++;
                maximize_chatbot();   
            } else if (message.event_type == 'AGENT_JOINED_CHAT') {
                let agent_joined_text = message.joined_chat_text;
                let assigned_agent_username = message.assigned_agent_username;
                handle_agent_joined(agent_joined_text, assigned_agent_username);
            }
        }
    }
}

function handle_agent_joined(agent_joined_text, agent_username){
    check_and_close_timers();
    if (is_chat_socket_open == true && need_to_add_wel_msg == true) {
        append_system_text_response(agent_joined_text);
        need_to_add_wel_msg = false;
        setTimeout(scroll_to_bottom, 300);
        show_end_chat_button();
        append_attachment_icon();
        enable_attachment();
        resize_chabot_window();
        create_agent_socket();
        show_voip_call_btn();
        if(enable_response_form_assist == 'false') {
            show_user_action_div_for_form_assist();
        }
        something_assigned_livechat = true;
        assigned_agent_username = agent_username;
    }
    queue_timer = livechat_queue_time / 5 + 1;
    if (document.getElementById("queue-bar-timer")) {
        document.getElementById("livechat_queue").remove();
    }

    enable_user_input();
    enable_footer();
    show_footer();
}

function open_livechat_socket(e) {
    console.log("Connection established.");
    is_livechat = true;
    left_msg_append = false;
    is_chat_socket_open = true;
    send_ping_to_socket_holder = setInterval(send_ping_to_socket, 1000);
}

function close_livechat_socket(e) {
    is_livechat_msg = true;


    if (chat_socket != null && is_chat_socket_open == true) {
        var loader = document.getElementById("livechat-loader");

        if (loader) {
            loader.style.display = "none";
            document.getElementById("livechat-loader-div").style.display = "none";
        }
    }
    console.log("Chat socket closed unexpectedly");
    try {
        hide_end_chat_button_based_on_theme()
        disable_attachment_icon();
        enable_mute_unmute_icon();
        reset_footer();
        hide_voip_call_btn();
    } catch (err) {
        console.log(err);
    }

    toggle_sticky_menu("block");

    if (is_livechat && is_chat_socket_open) {
        is_livechat = false;
        enable_language_change_options();
        append_system_text_response(livechat_notification);
        unset_livechat_cookies();

        if (!bot_restarted) {
            append_welcome_message(bot_id, bot_name, true);
            is_bot_response_message_showed = true;
            if (is_text_to_speech_required) {
                text_to_speech(default_response);
            }
        }

        bot_restarted = false;
        setTimeout(function () {
            scroll_to_bottom();
        }, 200);
    }
    is_chat_socket_open = false;
    is_livechat = false;
    enable_language_change_options();

    clearInterval(send_ping_to_socket_holder);
    if(check_agent_assign_timer){
        clearInterval(check_agent_assign_timer);
    }
    need_to_add_wel_msg = true;
    chat_socket = null;
    resize_chabot_window();
    scroll_to_bottom();
    handle_enable_response_form_assist()
    agent_socket.close();
}

function onerror_livechat_socket(e) {
    console.log("Connection break due to some internal server error.");
    livechat_notification = WEAK_INTERNET_TEXT;
    unset_livechat_cookies();
    enable_mute_unmute_icon();
    append_system_text_response(livechat_notification);
    save_customer_chat(livechat_notification, livechat_session_id, "System", "", "", "", "");
    disable_attachment_icon();
    hide_voip_call_btn();

    is_chat_socket_open = false;
    is_livechat = false;
    chat_socket = null;
    enable_language_change_options();
}

function send_ping_to_socket() {
    if (is_chat_socket_open == true && chat_socket != null) {
        var sentence = JSON.stringify({
            message: JSON.stringify({
                text_message: "",
                type: "text",
                channel: window.channel_name_iframe,
                path: "",
                event_type: "CUSTOMER_STILL_THERE",
            }),
            sender: "ping",
        });
        sentence = encrypt_variable(sentence);
        chat_socket.send(sentence);
    }
}

/////////////////// LiveChat Room Ends /////////////////////////////////////

/////////////////// LiveChat Feedback Form /////////////////////////////////

function append_feedback_form(livechat_session_feedback, livechat_user_feedback) {
   hide_end_chat_button();

   try {
        is_livechat_msg = true;
        is_livechat = true;
        livechat_user_id_feedback = livechat_user_feedback;
        livechat_session_id_feedback = livechat_session_feedback;
        unset_livechat_cookies();
        enable_mute_unmute_icon();
        append_system_text_response(AGENT_LEFT_TEXT);
        if (EASYCHAT_BOT_THEME == "theme_1") {
            document.getElementById("user_input").style.paddingLeft = "5px";
        }
        is_livechat_msg = false;
        is_livechat = false;
        disable_user_input();
        disable_sticky_intents();
        enable_language_change_options();
        if (EASYCHAT_BOT_THEME == 'theme_4') {
            chat_container.innerHTML += get_feedback_form_html_for_theme_four();
        } else {
            chat_container.innerHTML += get_feedback_form_html();
        }
        clear_dealy_message_time_out();
        scroll_to_bottom();

        changeMiddleContainer();
        resize_chabot_window();
        disable_attachment_icon();
        hide_voip_call_btn();
    }
    catch(err) {
        console.log(err);
    }

try{
    var easychat_sticky = document.getElementById("easychat-sticky");
    if (easychat_sticky == null || easychat_sticky == undefined) {
        if (EASYCHAT_BOT_THEME == "theme_1") {
            chat_container.style.height = (chat_container.clientHeight + 40).toString() + "px";
        } else {
            chat_container.style.height = (chat_container.clientHeight + 12).toString() + "px";
        }
    }
}
catch(err)
{}
}

function get_feedback_form_html() {

    var user_input =
        '<p style="font-style: normal;font-weight: bold;font-size: 18px;line-height: 22px;color: #2D2D2D;" id="feedback-form-title">'+ LIVECHAT_FEEDBACK_HEADER +'</p><p style="font-style: normal;font-weight: 500;font-size: 15px;line-height: 20px;color: #4D4D4D;">'+ LIVECHAT_FEEDBACK_MAIN_TEXT +'<p>';
    var html =
        '<div class="rating-bar-container__wrapper" style="width: 105%; margin: auto;margin-top: 1em;">\
                <div id="rating-bar-container__XqPZ" class="rating-bar-container" zQPK="false" onmouseout="change_color_ratingz_bar_all(this)">\
                <button id="rating-bar-button__00" onmouseover="change_color_ratingv_bar(this)" onmouseout="change_color_ratingz_bar(this)" onclick="set_value_to_some(this)" value="1" style="color:' +
        BOT_THEME_COLOR +
        ' !important">0</button><button id="rating-bar-button__01" onmouseover="change_color_ratingv_bar(this)" onmouseout="change_color_ratingz_bar(this)" onclick="set_value_to_some(this)" value="2" style="color:' +
        BOT_THEME_COLOR +
        ' !important">1</button><button id="rating-bar-button__02" onclick="set_value_to_some(this)" onmouseover="change_color_ratingv_bar(this)" onmouseout="change_color_ratingz_bar(this)" value="3" style="color:' +
        BOT_THEME_COLOR +
        ' !important">2</button><button id="rating-bar-button__03" onmouseover="change_color_ratingv_bar(this)" onclick="set_value_to_some(this)" onmouseout="change_color_ratingz_bar(this)" value="4" style="color:' +
        BOT_THEME_COLOR +
        ' !important">3</button><button id="rating-bar-button__04" onclick="set_value_to_some(this)" onmouseover="change_color_ratingv_bar(this)" onmouseout="change_color_ratingz_bar(this)" value="5" style="color:' +
        BOT_THEME_COLOR +
        ' !important">4</button><button id="rating-bar-button__05" onmouseover="change_color_ratingv_bar(this)" onclick="set_value_to_some(this)" onmouseout="change_color_ratingz_bar(this)" value="6" style="color:' +
        BOT_THEME_COLOR +
        ' !important">5</button><button id="rating-bar-button__06" onclick="set_value_to_some(this)" onmouseover="change_color_ratingv_bar(this)" onmouseout="change_color_ratingz_bar(this)" value="7" style="color:' +
        BOT_THEME_COLOR +
        ' !important">6</button><button id="rating-bar-button__07" onmouseover="change_color_ratingv_bar(this)" onclick="set_value_to_some(this)" onmouseout="change_color_ratingz_bar(this)" value="8" style="color:' +
        BOT_THEME_COLOR +
        ' !important">7</button><button id="rating-bar-button__08" onclick="set_value_to_some(this)" onmouseover="change_color_ratingv_bar(this)" onmouseout="change_color_ratingz_bar(this)" value="9" style="color:' +
        BOT_THEME_COLOR +
        ' !important">8</button><button id="rating-bar-button__09" onmouseover="change_color_ratingv_bar(this)" onclick="set_value_to_some(this)" onmouseout="change_color_ratingz_bar(this)" value="10" style="color:' +
        BOT_THEME_COLOR +
        ' !important">9</button><button id="rating-bar-button__10" onclick="set_value_to_some(this)" onmouseover="change_color_ratingv_bar(this)" onmouseout="change_color_ratingz_bar(this)" value="11" style="color:' +
        BOT_THEME_COLOR +
        ' !important">10</button>\
                </div><br><div id="rating-bar-container-timer-div" style="width:30%;margin:auto;"><span id="rating-bar-container-timer__XqPZ"></span></div></div>';
    html +=
        '<textarea class="livechat-feedback-comment-box" placeholder="'+ LIVECHAT_ADD_COMMENT_TEXT +'" col="30" id="livechat-chatbot-comment-box" style="color: rgb(158, 158, 158);resize:none;height: 132px;width: 100%; border: 1px solid #E6E6E6; border-radius: 0.5em;display:inline-block;margin-left: -0.1em;direction: '+ pointer_direction +'" onchange="save_livechat_feedback_text()"></textarea>';
    html += '<button class="btn right" id ="feedback-submit-button"  disabled = "true" style="background-color:' + BOT_THEME_COLOR + ' !important;margin-left: 0.2em;border-radius: 30px !important;font-size: 14px !important;font-weight: 400 !important;color: white !important;cursor: pointer;text-align: center;height: 36px;line-height: 36px;padding: 0 16px;vertical-align: middle;float: right !important;margin-top: 0.2em;opacity:0.5; border:aliceblue;outline:none;" onclick="add_livechat_nps()">'+ SUBMIT_TEXT +'</button>';
    html +='<a class="right" style="background-color: white !important;margin-left: 0.2em;color: #757575;font-size: 14px !important;float: right;text-decoration: none;margin-top: 0.9em;margin-right: 0.5em;cursor:pointer;" onclick="add_livechat_nps()"><b>' + LIVECHAT_FEEDBACK_CANCEL_TEXT + '</b></a>';

    var parent_html =
        '<div id="livechat_feedback" style="display:inline-block;"><div id="feedback_wrapper" style="box-shadow: 1px 1px 6px rgba(0, 0, 0, 0.2);color: black;width: 90%;margin: auto;margin-top: 1.5em;border-radius: 1em;padding: 1em;background-color:white;padding-right: 1.1em;height: 25em;margin-bottom:1em;">' +
        user_input +
        html +
        "</div></div>";

    return parent_html;
}

function get_feedback_form_html_for_theme_four() {
    let html = '<div id="livechat_feedback" class="easychat-bot-custom-modal" style="display: block">\
                <div id="feedback_wrapper" class="easychat-bot-custom-modal-content">\
                    <div class="easychat-bot-custom-modal-body">\
                        <div class="easychat-bot-livechat-feedback-header" id="feedback-form-title">\
                            ' + LIVECHAT_FEEDBACK_HEADER + '\
                        </div>\
                        <div class="easychat-bot-livechat-feedback-subheader">\
                            ' + LIVECHAT_FEEDBACK_MAIN_TEXT + '\
                        </div>\
                        <div class="rating-bar-container__wrapper">\
                            <div id="rating-bar-container__XqPZ" class="rating-bar-container" zqpk="false"\
                                onmouseout="change_color_ratingz_bar_all(this)">\
                                <button id="rating-bar-button__00" onmouseover="change_color_ratingv_bar(this)" onmouseout="change_color_ratingz_bar(this)" onclick="set_value_to_some(this)" value="1" style="color:' +
                                BOT_THEME_COLOR +
                                ' !important">0</button><button id="rating-bar-button__01" onmouseover="change_color_ratingv_bar(this)" onmouseout="change_color_ratingz_bar(this)" onclick="set_value_to_some(this)" value="2" style="color:' +
                                BOT_THEME_COLOR +
                                ' !important">1</button><button id="rating-bar-button__02" onclick="set_value_to_some(this)" onmouseover="change_color_ratingv_bar(this)" onmouseout="change_color_ratingz_bar(this)" value="3" style="color:' +
                                BOT_THEME_COLOR +
                                ' !important">2</button><button id="rating-bar-button__03" onmouseover="change_color_ratingv_bar(this)" onclick="set_value_to_some(this)" onmouseout="change_color_ratingz_bar(this)" value="4" style="color:' +
                                BOT_THEME_COLOR +
                                ' !important">3</button><button id="rating-bar-button__04" onclick="set_value_to_some(this)" onmouseover="change_color_ratingv_bar(this)" onmouseout="change_color_ratingz_bar(this)" value="5" style="color:' +
                                BOT_THEME_COLOR +
                                ' !important">4</button><button id="rating-bar-button__05" onmouseover="change_color_ratingv_bar(this)" onclick="set_value_to_some(this)" onmouseout="change_color_ratingz_bar(this)" value="6" style="color:' +
                                BOT_THEME_COLOR +
                                ' !important">5</button><button id="rating-bar-button__06" onclick="set_value_to_some(this)" onmouseover="change_color_ratingv_bar(this)" onmouseout="change_color_ratingz_bar(this)" value="7" style="color:' +
                                BOT_THEME_COLOR +
                                ' !important">6</button><button id="rating-bar-button__07" onmouseover="change_color_ratingv_bar(this)" onclick="set_value_to_some(this)" onmouseout="change_color_ratingz_bar(this)" value="8" style="color:' +
                                BOT_THEME_COLOR +
                                ' !important">7</button><button id="rating-bar-button__08" onclick="set_value_to_some(this)" onmouseover="change_color_ratingv_bar(this)" onmouseout="change_color_ratingz_bar(this)" value="9" style="color:' +
                                BOT_THEME_COLOR +
                                ' !important">8</button><button id="rating-bar-button__09" onmouseover="change_color_ratingv_bar(this)" onclick="set_value_to_some(this)" onmouseout="change_color_ratingz_bar(this)" value="10" style="color:' +
                                BOT_THEME_COLOR +
                                ' !important">9</button><button id="rating-bar-button__10" onclick="set_value_to_some(this)" onmouseover="change_color_ratingv_bar(this)" onmouseout="change_color_ratingz_bar(this)" value="11" style="color:' +
                                BOT_THEME_COLOR +
                                ' !important">10</button>\
                            </div>\
                            <div id="rating-bar-container-timer-div"\
                                style="width:30%;margin:auto; display: none; margin-top: 12px;"><span\
                                    id="rating-bar-container-timer__XqPZ"></span></div>\
                        </div>\
                        <div class="livechat-feeback-comment-wrapper">\
                            <textarea class="livechat-feedback-comment-box" placeholder=" ' + LIVECHAT_ADD_COMMENT_TEXT + '" col="30"\
                                id="livechat-feedback-comment-box" onchange="save_livechat_feedback_text()"></textarea>\
                        </div>\
                    </div>\
                    <div class="easychat-bot-custom-modal-footer" style="margin-top: 4px; padding-top: 8px;">\
                        <button class="custom-modal-cancel-btn bot-close-modal-feedback" onclick="add_livechat_nps()"> ' + LIVECHAT_FEEDBACK_CANCEL_TEXT + '</button>\
                        <button class="custom-modal-submit-btn bot-close-modal" id="feedback-submit-button" disabled="true"\
                            onclick="add_livechat_nps()" style="opacity: 0.5;"> ' + SUBMIT_TEXT + '</button>\
                    </div>\
                </div>\
            </div>'
    return html;
}

function add_livechat_nps() {
    if (rate_value === "") {
        rate_value = -1;
    }
    save_livechat_feedback(
        rate_value,
        livechat_user_id_feedback,
        livechat_session_id_feedback,
        livechat_nps_text
    );
    livechat_session_id_feedback = "";
    livechat_user_id_feedback = "";
    document.getElementById("livechat_feedback").remove();
    if (is_text_to_speech_required) {
        text_to_speech(FEEDBACK_SUBMIT_TEXT);
        text_to_speech(default_response);
    }
    append_bot_text_response(
        FEEDBACK_SUBMIT_TEXT
    );
    append_welcome_message(bot_id, bot_name, true);
    clear_dealy_message_time_out();
    setTimeout(function () {
        scroll_to_bottom();
    }, 200);
    changeMiddleContainer();
    resize_chabot_window();
    enable_sticky_intents();
    enable_user_input();
    unset_livechat_cookies();
    livechat_session_id = "";

    if (chat_socket) chat_socket.close();
}

function save_livechat_feedback_text() {
    livechat_nps_text = document.getElementById("livechat-chatbot-comment-box").value;
}

function set_value_to_some(el) {
    var feedback_btn = document.getElementById("feedback-submit-button");

    feedback_btn.style.opacity = 1;
    feedback_btn.disabled = false;
    el.parentElement.setAttribute("zQPK", "true");
    rate_value = parseInt(el.getAttribute("value")) - 1;
}

function change_color_ratingz_bar_all(el) {
    let current_hover_value = parseInt(el.childElementCount);
    if (el.getAttribute("zQPK") == "false") {
        for (var i = 0; i <= current_hover_value; i++) {
            if (el.children[i] != undefined) {
                el.children[i].style.color = "black";
                el.children[i].style.backgroundColor = "white";
            }
        }
    }
}

function change_color_ratingz_bar(el) {
    let current_hover_value = parseInt(el.getAttribute("value"));
    for (var i = current_hover_value; i <= current_hover_value; i++) {
        if (el.parentElement.children[i] != undefined) {
            el.parentElement.children[i].style.color = "black";
            el.parentElement.children[i].style.backgroundColor = "white";
        }
    }
}

function change_color_ratingv_bar(el) {
    let current_hover_value = parseInt(el.getAttribute("value"));
    for (var i = 0; i <= current_hover_value; i++) {
        el.parentElement.children[i].style.color = "white";
        if (current_hover_value <= 6) {
            el.parentElement.children[i].style.backgroundColor = "red";
        }
        if (6 < current_hover_value && current_hover_value <= 8) {
            el.parentElement.children[i].style.backgroundColor = "orange";
        }
        if (8 < current_hover_value) {
            el.parentElement.children[i].style.backgroundColor = "green";
        }
    }
    for (var j = current_hover_value; j <= el.parentElement.childElementCount; j++) {
        if (el.parentElement.children[j] != undefined) {
            el.parentElement.children[j].style.color = "black";
            el.parentElement.children[j].style.backgroundColor = "white";
        }
    }
}

function save_livechat_feedback(
    rate_value_nps,
    user_id,
    livechat_session_feedback,
    nps_text_feedback_livechat
) {

    nps_text_feedback_livechat = stripHTML(nps_text_feedback_livechat);
    nps_text_feedback_livechat = strip_unwanted_characters(nps_text_feedback_livechat);

    var json_string = JSON.stringify({
        user_id: user_id,
        rate_value: rate_value_nps,
        bot_id: bot_id,
        session_id: livechat_session_feedback,
        nps_text_feedback: nps_text_feedback_livechat,
    });

    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", SAVE_LIVECHAT_FEEDBACK, true);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            console.log("Rating updated successfully!!!");
        }
    };
    xhttp.send(params);
}

/////////////////// LiveChat Feedback Form Ends ////////////////////////////

/////////////////// LiveChat Attachment ////////////////////////////////////

function append_file_to_customer(url, message, thumbnail_path, default_time, other_info) {
    if (typeof default_time === "undefined") {
        default_time = return_time();
    }

    var html;
    if (is_image(url) || is_video(url)) {
        html =
            '<div class="attachment-flex-div agent-attachmnet-div"><div class="easychat-livechat-agent-attachment easychat-active-agent-div" style="width:98%;">\
                <div class="active-agent-profile-image">\
                    ' + get_user_initial(other_info.agent_name) + '\
                </div>\
                <div class="active-agent-name">\
                    <span>' + other_info.agent_name + '</span>\
                </div>\
                <div class="attachment-div"><div class="easychat-livechat-customer-attachment livechat-agent-attachments livechat-attachment-img-video">' + get_file_path_html(url, thumbnail_path) + '</a>';
    } else {
        html =
            '<div class="attachment-flex-div agent-attachmnet-div" style="margin-top: 1em;"><div class="easychat-livechat-agent-attachment easychat-active-agent-div" style="width:98%;">\
            <div class="active-agent-profile-image">\
                ' + get_user_initial(other_info.agent_name) + '\
            </div>\
            <div class="active-agent-name">\
                <span>' + other_info.agent_name + '</span>\
            </div>\
            <div class="attachment-div"><div class="easychat-livechat-user-doc-attachment" style="margin-top: 0em;"><div class="easychat-livechat-doc-attachment-content livechat-agent-attachments">' +
            get_doc_path_html(url) +
            "</div>";
    }

    if (message != "") {
        html += '<div class="easychat-livechat-message">' + message + "</div>";
    }

    html +=
        '</div><div class="message-time-bot" style="width: 52.5%">' + default_time + '</div></div></div></div>';

    chat_container.innerHTML += html;

    resize_chabot_window();
    setTimeout(scroll_to_bottom, 1000);
}

function get_file_name(value) {
    if (value.length > 20) {
        var file_ext = value.split(".").pop();
        value = value.slice(0, 13);
        return value + "..." + file_ext;
    }

    return value;
}
function preview_livechat_big_image(elem){
    let image_src = elem.src
    document.getElementById("preview-big-image-modal").style.display = "block";
    document.getElementById("preview-big-image").src = image_src;
}
function get_file_path_html(attached_file_src, thumbnail_path) {
    var html = "";
    if (is_image(attached_file_src)) {
        html =
            '<img onclick="preview_livechat_big_image(this)"src="' +
            attached_file_src +
            "/?livechat_session_id=" +
            livechat_session_id +
            '" style="height: 100%;width: 100%;border-radius: 1em;object-fit: cover;cursor: pointer;"><a class="livechat-agent-attchment-name-wrapper" href="' +
            attached_file_src +
            "/?livechat_session_id=" +
            livechat_session_id +
            '" target="_blank">';
    } else {
        html =
            '<video poster="' +
            thumbnail_path +
            "/?livechat_session_id=" +
            livechat_session_id +
            '" style="width: 100%;height:100%;border-radius: 1em;max-height:340px;" class="easychat-livechat-attached-video" controls><source src="' +
            window.location.origin +
            attached_file_src +
            "/?livechat_session_id=" +
            livechat_session_id +
            '" type="video/mp4"></video><a class="livechat-agent-attchment-name-wrapper" href="' +
            attached_file_src +
            "/?livechat_session_id=" +
            livechat_session_id +
            '" target="_blank">';
    }
    var len = attached_file_src.split("/").length;
    var file_name = get_file_name(attached_file_src.split("/")[len - 1]);
    html += '<div style="margin: 3px;color: gray;">' + file_name + "</div>";
    html +='<div style=" display: inline-flex;"><svg  style="margin-right: 5px;" width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg" >\
    <path d="M11.875 11.25H3.125C2.77982 11.25 2.5 11.5298 2.5 11.875C2.5 12.2202 2.77982 12.5 3.125 12.5H11.875C12.2202 12.5 12.5 12.2202 12.5 11.875C12.5 11.5298 12.2202 11.25 11.875 11.25Z" fill="#757575">\
    </path><path d="M2.5 10.625V11.875C2.5 12.2202 2.77982 12.5 3.125 12.5C3.47018 12.5 3.75 12.2202 3.75 11.875V10.625C3.75 10.2798 3.47018 10 3.125 10C2.77982 10 2.5 10.2798 2.5 10.625Z" fill="#757575"></path><path d="M11.25 10.625V11.875C11.25 12.2202 11.5298 12.5 11.875 12.5C12.2202 12.5 12.5 12.2202 12.5 11.875V10.625C12.5 10.2798 12.2202 10 11.875 10C11.5298 10 11.25 10.2798 11.25 10.625Z" fill="#757575"></path> \
    <path d="M7.50003 9.375C7.37046 9.37599 7.24378 9.33667 7.13753 9.2625L4.63753 7.5C4.50279 7.40442 4.41137 7.25937 4.38326 7.09658C4.35515 6.93379 4.39264 6.76649 4.48753 6.63125C4.5349 6.56366 4.59518 6.50611 4.66491 6.46194C4.73463 6.41777 4.81242 6.38785 4.89377 6.37391C4.97512 6.35996 5.05843 6.36227 5.13889 6.38069C5.21934 6.39911 5.29535 6.43329 5.36253 6.48125L7.50003 7.975L9.62503 6.375C9.75764 6.27555 9.92432 6.23284 10.0884 6.25628C10.2525 6.27973 10.4006 6.36739 10.5 6.5C10.5995 6.63261 10.6422 6.7993 10.6187 6.96339C10.5953 7.12749 10.5076 7.27555 10.375 7.375L7.87503 9.25C7.76685 9.33114 7.63526 9.375 7.50003 9.375Z" fill="#757575"></path>\
    <path d="M7.5 8.125C7.33424 8.125 7.17527 8.05915 7.05806 7.94194C6.94085 7.82473 6.875 7.66576 6.875 7.5V2.5C6.875 2.33424 6.94085 2.17527 7.05806 2.05806C7.17527 1.94085 7.33424 1.875 7.5 1.875C7.66576 1.875 7.82473 1.94085 7.94194 2.05806C8.05915 2.17527 8.125 2.33424 8.125 2.5V7.5C8.125 7.66576 8.05915 7.82473 7.94194 7.94194C7.82473 8.05915 7.66576 8.125 7.5 8.125Z" fill="#757575"></path></svg></div>'
    return html;
}

function get_doc_path_html(url) {
    var len = url.split("/").length;
    var file_name = get_file_name(url.split("/")[len - 1]);
    var html =
        '<a style="text-decoration: none;" href="' +
        url +
        "/?livechat_session_id=" +
        livechat_session_id +
        '" target="_blank">';
    if (is_docs(file_name)) {
        html += '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 100%;object-fit:contain;height: 100px;margin: 0 auto;">\
        <path d="M18.5 20C18.5 20.275 18.276 20.5 18 20.5H6C5.724 20.5 5.5 20.275 5.5 20V4C5.5 3.725 5.724 3.5 6 3.5H12V8C12 9.104 12.896 10 14 10H18.5V20ZM13.5 4.621L17.378 8.5H14C13.724 8.5 13.5 8.275 13.5 8V4.621ZM19.414 8.414L13.585 2.586C13.559 2.56 13.527 2.54 13.5 2.516C13.429 2.452 13.359 2.389 13.281 2.336C13.241 2.309 13.195 2.291 13.153 2.268C13.082 2.228 13.012 2.184 12.937 2.152C12.74 2.07 12.528 2.029 12.313 2.014C12.266 2.011 12.22 2 12.172 2H12.171H12H6C4.896 2 4 2.896 4 4V20C4 21.104 4.896 22 6 22H18C19.104 22 20 21.104 20 20V10V9.828C20 9.298 19.789 8.789 19.414 8.414Z" fill="#212121"/>\
        <path fill-rule="evenodd" clip-rule="evenodd" d="M10.5556 14C10.2487 14 10 14.2487 10 14.5556V18.4444C10 18.7513 10.2487 19 10.5556 19H19.4444C19.7513 19 20 18.7513 20 18.4444V14.5556C20 14.2487 19.7513 14 19.4444 14H10.5556ZM10.755 15.375V18H11.6513C11.9588 18 12.2113 17.9462 12.4088 17.8387C12.6088 17.7287 12.7563 17.5763 12.8513 17.3812C12.9488 17.1837 12.9975 16.9525 12.9975 16.6875C12.9975 16.4225 12.9488 16.1925 12.8513 15.9975C12.7563 15.8 12.6088 15.6475 12.4088 15.54C12.2113 15.43 11.9588 15.375 11.6513 15.375H10.755ZM11.6288 17.5875H11.235V15.7837H11.6288C11.8488 15.7837 12.0225 15.82 12.15 15.8925C12.2775 15.965 12.3688 16.0687 12.4237 16.2037C12.4787 16.3387 12.5063 16.5 12.5063 16.6875C12.5063 16.8775 12.4787 17.04 12.4237 17.175C12.3688 17.3075 12.2775 17.41 12.15 17.4825C12.0225 17.5525 11.8488 17.5875 11.6288 17.5875ZM13.9235 17.8725C14.121 17.9875 14.351 18.045 14.6135 18.045C14.8735 18.045 15.1023 17.9875 15.2998 17.8725C15.4973 17.7575 15.651 17.5987 15.761 17.3963C15.871 17.1912 15.926 16.955 15.926 16.6875C15.926 16.42 15.871 16.185 15.761 15.9825C15.651 15.7775 15.4973 15.6175 15.2998 15.5025C15.1023 15.3875 14.8735 15.33 14.6135 15.33C14.351 15.33 14.121 15.3875 13.9235 15.5025C13.7285 15.6175 13.5748 15.7775 13.4623 15.9825C13.3523 16.185 13.2973 16.42 13.2973 16.6875C13.2973 16.955 13.3523 17.1912 13.4623 17.3963C13.5748 17.5987 13.7285 17.7575 13.9235 17.8725ZM15.2098 17.3663C15.0623 17.5312 14.8635 17.6137 14.6135 17.6137C14.3635 17.6137 14.1635 17.5312 14.0135 17.3663C13.8635 17.2012 13.7885 16.975 13.7885 16.6875C13.7885 16.4 13.8635 16.1737 14.0135 16.0087C14.1635 15.8438 14.3635 15.7613 14.6135 15.7613C14.8635 15.7613 15.0623 15.8438 15.2098 16.0087C15.3598 16.1737 15.4348 16.4 15.4348 16.6875C15.4348 16.975 15.3598 17.2012 15.2098 17.3663ZM16.8186 17.8763C17.0086 17.9887 17.2361 18.045 17.5011 18.045C17.8161 18.045 18.0736 17.9688 18.2736 17.8163C18.4761 17.6637 18.6023 17.4525 18.6523 17.1825H18.1236C18.0911 17.3175 18.0211 17.4237 17.9136 17.5013C17.8086 17.5763 17.6686 17.6137 17.4936 17.6137C17.2511 17.6137 17.0611 17.5325 16.9236 17.37C16.7861 17.205 16.7173 16.9787 16.7173 16.6913C16.7173 16.4037 16.7861 16.1775 16.9236 16.0125C17.0611 15.8475 17.2511 15.765 17.4936 15.765C17.6686 15.765 17.8086 15.8062 17.9136 15.8887C18.0211 15.9687 18.0911 16.08 18.1236 16.2225H18.6523C18.6023 15.94 18.4761 15.7212 18.2736 15.5662C18.0736 15.4087 17.8161 15.33 17.5011 15.33C17.2361 15.33 17.0086 15.3875 16.8186 15.5025C16.6286 15.6175 16.4823 15.7775 16.3798 15.9825C16.2773 16.1875 16.2261 16.4237 16.2261 16.6913C16.2261 16.9588 16.2773 17.195 16.3798 17.4C16.4823 17.6025 16.6286 17.7613 16.8186 17.8763Z" fill="#212121"/>\
        <path d="M7 7H10" stroke="black" stroke-linecap="round"/>\
        <path d="M7 9H10" stroke="black" stroke-linecap="round"/>\
        </svg>';
    } else if (is_pdf(file_name)) {
        html += '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 100%;object-fit:contain;height: 100px;margin: 0 auto;">\
        <path d="M18.5 20C18.5 20.275 18.276 20.5 18 20.5H6C5.724 20.5 5.5 20.275 5.5 20V4C5.5 3.725 5.724 3.5 6 3.5H12V8C12 9.104 12.896 10 14 10H18.5V20ZM13.5 4.621L17.378 8.5H14C13.724 8.5 13.5 8.275 13.5 8V4.621ZM19.414 8.414L13.585 2.586C13.559 2.56 13.527 2.54 13.5 2.516C13.429 2.452 13.359 2.389 13.281 2.336C13.241 2.309 13.195 2.291 13.153 2.268C13.082 2.228 13.012 2.184 12.937 2.152C12.74 2.07 12.528 2.029 12.313 2.014C12.266 2.011 12.22 2 12.172 2H12.171H12H6C4.896 2 4 2.896 4 4V20C4 21.104 4.896 22 6 22H18C19.104 22 20 21.104 20 20V10V9.828C20 9.298 19.789 8.789 19.414 8.414Z" fill="#212121"/>\
        <path fill-rule="evenodd" clip-rule="evenodd" d="M10.5556 14C10.2487 14 10 14.2487 10 14.5556V18.4444C10 18.7513 10.2487 19 10.5556 19H19.4444C19.7513 19 20 18.7513 20 18.4444V14.5556C20 14.2487 19.7513 14 19.4444 14H10.5556ZM11.4043 14.9822V18H11.9561V16.8317H12.5208C12.768 16.8317 12.9706 16.79 13.1287 16.7067C13.2868 16.6204 13.4032 16.5084 13.4779 16.3704C13.5526 16.2296 13.59 16.0758 13.59 15.9091C13.59 15.7338 13.5512 15.5757 13.4736 15.4349C13.396 15.2941 13.2782 15.1834 13.1201 15.1029C12.962 15.0225 12.7623 14.9822 12.5208 14.9822H11.4043ZM12.4864 16.3833H11.9561V15.4306H12.4864C12.6789 15.4306 12.8169 15.4737 12.9002 15.5599C12.9864 15.6433 13.0296 15.7597 13.0296 15.9091C13.0296 16.0557 12.9864 16.1721 12.9002 16.2583C12.8169 16.3417 12.6789 16.3833 12.4864 16.3833ZM14.0229 14.9822V18H15.0533C15.4068 18 15.6971 17.9382 15.9241 17.8146C16.1541 17.6882 16.3236 17.5128 16.4328 17.2887C16.5449 17.0616 16.601 16.7958 16.601 16.4911C16.601 16.1865 16.5449 15.922 16.4328 15.6979C16.3236 15.4708 16.1541 15.2955 15.9241 15.1719C15.6971 15.0455 15.4068 14.9822 15.0533 14.9822H14.0229ZM15.0274 17.5258H14.5748V15.4521H15.0274C15.2803 15.4521 15.4801 15.4938 15.6267 15.5772C15.7732 15.6605 15.8781 15.7798 15.9414 15.935C16.0046 16.0902 16.0362 16.2756 16.0362 16.4911C16.0362 16.7095 16.0046 16.8964 15.9414 17.0516C15.8781 17.2039 15.7732 17.3217 15.6267 17.4051C15.4801 17.4855 15.2803 17.5258 15.0274 17.5258ZM19.0365 14.9822H17.0879V18H17.6397V16.7067H18.7692V16.2712H17.6397V15.4263H19.0365V14.9822Z" fill="#212121"/>\
        <path d="M7 7H10" stroke="black" stroke-linecap="round"/>\
        <path d="M7 9H10" stroke="black" stroke-linecap="round"/>\
        </svg>';
    } else if (is_text(file_name)) {
        html += '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 100%;object-fit:contain;height: 100px;margin: 0 auto;">\
        <path d="M18.5 20C18.5 20.275 18.276 20.5 18 20.5H6C5.724 20.5 5.5 20.275 5.5 20V4C5.5 3.725 5.724 3.5 6 3.5H12V8C12 9.104 12.896 10 14 10H18.5V20ZM13.5 4.621L17.378 8.5H14C13.724 8.5 13.5 8.275 13.5 8V4.621ZM19.414 8.414L13.585 2.586C13.559 2.56 13.527 2.54 13.5 2.516C13.429 2.452 13.359 2.389 13.281 2.336C13.241 2.309 13.195 2.291 13.153 2.268C13.082 2.228 13.012 2.184 12.937 2.152C12.74 2.07 12.528 2.029 12.313 2.014C12.266 2.011 12.22 2 12.172 2H12.171H12H6C4.896 2 4 2.896 4 4V20C4 21.104 4.896 22 6 22H18C19.104 22 20 21.104 20 20V10V9.828C20 9.298 19.789 8.789 19.414 8.414Z" fill="#212121"/>\
        <path fill-rule="evenodd" clip-rule="evenodd" d="M10.5556 14C10.2487 14 10 14.2487 10 14.5556V18.4444C10 18.7513 10.2487 19 10.5556 19H19.4444C19.7513 19 20 18.7513 20 18.4444V14.5556C20 14.2487 19.7513 14 19.4444 14H10.5556ZM11.693 16.209V18H12.077V16.209H12.692V15.9H11.081V16.209H11.693ZM12.9315 15.9V18H14.3025V17.691H13.3155V17.085H14.2125V16.785H13.3155V16.209H14.3025V15.9H12.9315ZM15.1758 16.938L14.5188 18H14.9508L15.3828 17.259L15.8598 18H16.3008L15.6288 16.956L16.2858 15.9H15.8538L15.4218 16.632L14.9508 15.9H14.5098L15.1758 16.938ZM17.0424 16.209V18H17.4264V16.209H18.0414V15.9H16.4304V16.209H17.0424Z" fill="#212121"/>\
        <path d="M7 7H10" stroke="black" stroke-linecap="round"/>\
        <path d="M7 9H10" stroke="black" stroke-linecap="round"/>\
        </svg>';
    } else {
        html += '<img src="/static/LiveChatApp/img/document.png" style="width: 100%;object-fit:contain;height: 100px;margin: 0 auto;">';
    }
    html += '<div style="display: flex; align-items: center; justify-content: space-between;"><span style="margin: 3px;color: gray;">' + file_name + "</span>";
    html +='<div style=" display: inline-flex;"><svg  style="margin-right: 5px"; width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg" >\
    <path d="M11.875 11.25H3.125C2.77982 11.25 2.5 11.5298 2.5 11.875C2.5 12.2202 2.77982 12.5 3.125 12.5H11.875C12.2202 12.5 12.5 12.2202 12.5 11.875C12.5 11.5298 12.2202 11.25 11.875 11.25Z" fill="#757575">\
    </path><path d="M2.5 10.625V11.875C2.5 12.2202 2.77982 12.5 3.125 12.5C3.47018 12.5 3.75 12.2202 3.75 11.875V10.625C3.75 10.2798 3.47018 10 3.125 10C2.77982 10 2.5 10.2798 2.5 10.625Z" fill="#757575"></path><path d="M11.25 10.625V11.875C11.25 12.2202 11.5298 12.5 11.875 12.5C12.2202 12.5 12.5 12.2202 12.5 11.875V10.625C12.5 10.2798 12.2202 10 11.875 10C11.5298 10 11.25 10.2798 11.25 10.625Z" fill="#757575"></path> \
    <path d="M7.50003 9.375C7.37046 9.37599 7.24378 9.33667 7.13753 9.2625L4.63753 7.5C4.50279 7.40442 4.41137 7.25937 4.38326 7.09658C4.35515 6.93379 4.39264 6.76649 4.48753 6.63125C4.5349 6.56366 4.59518 6.50611 4.66491 6.46194C4.73463 6.41777 4.81242 6.38785 4.89377 6.37391C4.97512 6.35996 5.05843 6.36227 5.13889 6.38069C5.21934 6.39911 5.29535 6.43329 5.36253 6.48125L7.50003 7.975L9.62503 6.375C9.75764 6.27555 9.92432 6.23284 10.0884 6.25628C10.2525 6.27973 10.4006 6.36739 10.5 6.5C10.5995 6.63261 10.6422 6.7993 10.6187 6.96339C10.5953 7.12749 10.5076 7.27555 10.375 7.375L7.87503 9.25C7.76685 9.33114 7.63526 9.375 7.50003 9.375Z" fill="#757575"></path>\
    <path d="M7.5 8.125C7.33424 8.125 7.17527 8.05915 7.05806 7.94194C6.94085 7.82473 6.875 7.66576 6.875 7.5V2.5C6.875 2.33424 6.94085 2.17527 7.05806 2.05806C7.17527 1.94085 7.33424 1.875 7.5 1.875C7.66576 1.875 7.82473 1.94085 7.94194 2.05806C8.05915 2.17527 8.125 2.33424 8.125 2.5V7.5C8.125 7.66576 8.05915 7.82473 7.94194 7.94194C7.82473 8.05915 7.66576 8.125 7.5 8.125Z" fill="#757575"></path></svg></div></div></a>'
    
    return html;
}

function update_inaccessible_file_icons() {
    let attachment_elements = document.querySelectorAll('.livechat-agent-attachments');

    for(let i = 0; i < attachment_elements.length; i++) {
        attachment_elements[i].innerHTML = '<svg width="63" height="62" viewBox="0 0 63 62" fill="none" xmlns="http://www.w3.org/2000/svg">\
        <path fill-rule="evenodd" clip-rule="evenodd" d="M19.2423 0.172074C18.2177 0.427219 17.4508 0.862914 16.6782 1.62883C15.8826 2.41776 15.4015 3.28648 15.18 4.33504C15.0863 4.77812 15.0443 8.19042 15.0443 15.3589V25.741L16.2592 25.6925C18.8238 25.5899 21.7812 26.1169 24.3455 27.1334C26.889 28.1416 29.2074 29.6918 31.2499 31.7503L32.4278 32.9375H42.4798C52.3141 32.9375 52.5422 32.9428 53.012 33.1813C53.5519 33.4554 53.9823 34.153 53.9823 34.7539C53.9823 35.3548 53.5519 36.0524 53.012 36.3266C52.5438 36.5643 52.3115 36.5703 43.658 36.5703H34.7842L35.2427 37.6299C36.0258 39.4394 36.5709 41.3993 36.7773 43.1462L36.8587 43.8359H44.6953C52.3092 43.8359 52.5455 43.8428 53.012 44.0797C53.5519 44.3539 53.9823 45.0515 53.9823 45.6523C53.9823 46.2532 53.5519 46.9508 53.012 47.225C52.5455 47.4618 52.3092 47.4688 44.7018 47.4688H36.8718L36.7154 48.5686C36.0187 53.4671 33.0981 58.463 29.2325 61.369L28.393 62H42.9461C53.1897 62 57.6901 61.96 58.1439 61.8649C60.2089 61.4321 61.9333 59.7163 62.3649 57.665C62.4608 57.2094 62.5 51.0362 62.5 36.3827V15.7422H55.3069H48.1139L47.6285 15.4707C47.3436 15.3113 47.0477 15.0132 46.9123 14.749C46.6934 14.3219 46.6814 13.93 46.6814 7.14938V0L33.2661 0.010293C22.9622 0.0181641 19.7096 0.0557031 19.2423 0.172074ZM50.3319 6.59961V12.1094H55.8983H61.4647L55.9292 6.59961C52.8847 3.56924 50.3798 1.08984 50.3628 1.08984C50.3457 1.08984 50.3319 3.56924 50.3319 6.59961ZM53.012 22.2828C53.5519 22.557 53.9823 23.2546 53.9823 23.8555C53.9823 24.4563 53.5519 25.154 53.012 25.4281C52.5392 25.6681 52.3223 25.6719 38.7631 25.6719H24.9944L24.509 25.4004C23.2844 24.7155 23.272 23.0579 24.4859 22.3267L24.9613 22.0403L38.7466 22.0397C52.3231 22.0391 52.539 22.0427 53.012 22.2828ZM15.166 29.3789C11.25 29.8587 7.97059 31.4501 5.24773 34.192C2.82956 36.6271 1.43533 39.2263 0.724228 42.625C0.425257 44.0533 0.425257 47.2514 0.724228 48.6797C1.43606 52.0821 2.83418 54.6867 5.24773 57.1071C7.69839 59.5647 10.3766 61.0045 13.8275 61.7197C15.2457 62.0136 18.457 62.0133 19.9409 61.7191C23.2246 61.0681 25.9452 59.618 28.3854 57.218C30.8362 54.8078 32.2958 52.1156 33.0148 48.6797C33.3138 47.2515 33.3138 44.0533 33.0148 42.625C32.5473 40.3908 31.6807 38.313 30.439 36.4492C29.6729 35.2993 27.2958 32.9254 26.168 32.1839C24.2067 30.8944 22.092 30.009 20.0066 29.6043C19.0259 29.4139 16.022 29.2741 15.166 29.3789ZM12.1604 38.5803C12.3746 38.6868 13.5217 39.7352 14.7097 40.9101L16.8695 43.0463L19.0294 40.9101C20.2172 39.7352 21.3644 38.6868 21.5786 38.5803C23.0644 37.8417 24.7181 39.4873 23.9758 40.966C23.8689 41.1791 22.8153 42.3208 21.6348 43.5029L19.4882 45.6523L21.6348 47.8018C22.8153 48.9839 23.8689 50.1255 23.9758 50.3387C24.7181 51.8173 23.0644 53.463 21.5786 52.7243C21.3644 52.6179 20.2172 51.5695 19.0294 50.3946L16.8695 48.2584L14.7097 50.3946C13.5217 51.5695 12.3746 52.6179 12.1604 52.7243C10.6746 53.463 9.02095 51.8173 9.7632 50.3387C9.87016 50.1255 10.9237 48.9839 12.1042 47.8018L14.2508 45.6523L12.1042 43.5029C10.9237 42.3208 9.87016 41.1791 9.7632 40.966C9.0207 39.4869 10.6741 37.8414 12.1604 38.5803Z" fill="'+ BOT_THEME_COLOR +'"/>\
        </svg>';
    }

    $('.livechat-attachment-img-video').attr('style', 'width: 100% !important');
    $('.easychat-active-agent-div .message-time-bot').attr('style', 'width: 100% !important');
}

/////////////////////////for future: if excel file will be allowed/////////////////  
/*function is_excel(attached_file_src) {
    let file_ext = attached_file_src.split(".");
    file_ext = attached_file_src.split(".")[file_ext.length - 1];
    file_ext = file_ext.toUpperCase();

    if (["XLS", "XLSX"].indexOf(file_ext) != -1) {
        return true;
    }

    return false;
}*/

////////////////// LiveChat Attachment Ends ////////////////////////////////

////////////////// Utility Functions //////////////////////////////////////


function toggle_sticky_menu(display_prop) {

    if(EASYCHAT_BOT_THEME == "theme_3" || EASYCHAT_BOT_THEME == "theme_4"){
        toogle_sticky_menu_for_theme_three(display_prop)
        return
    }

    var element = document.getElementById("easychat-sticky");

    if (element != undefined || element != null) {
        element.style.display = display_prop;
    }
}


function hide_footer() {
    chat_footer.style.visibility = 'hidden';
}

function show_footer() {
    chat_footer.style.visibility = 'visible';
}

function enable_attachment() {
    document.getElementById("easychat-img-div").style.display = "flex";
    document.getElementById("easychat-img-div-previous").style.display = "none";
}

function validate_name(name) {
    var regex = /^[a-zA-Z ]{2,30}$/;
    var name_list = name.trim().split(" ");
    for (var i = 0; i < name_list.length; i++) {
        if (name_list[i] == "" || !regex.test(name_list[i])) return false;
    }

    return true;
}

function add_phone_number_validation() {
    var mobile_number = document.getElementById("easychat-customer-phone");
    if (mobile_number.length >= 10) {
        mobile_number.value = mobile_number.value.substring(0, 10);
    }
}


function disable_attachment_icon() {
    document.getElementById("easychat-img-div").style.display = "none";
    document.getElementById("easychat-img-div-previous").style.display = "none";

    if (EASYCHAT_BOT_THEME !== "theme_2") {
        try {
            if (mic_access) {
                document.getElementById("easychat-mic-div").style.paddingRight = "10px";
            } else {
                document.getElementById("easychat-mic-div-not-allowed").style.paddingRight = "10px";
            }
        } catch (err) {
            console.log(err);
        }
    }
}

function show_restart_button_based_on_theme(){

    if(EASYCHAT_BOT_THEME == "theme_3" || EASYCHAT_BOT_THEME == "theme_4"){

        $(".easychat-bot-restart-div").css("display", "flex");

    }else{
        restart_btn.style.display = "flex";
    }

}

function hide_restart_button_based_on_theme(){
    
    if(EASYCHAT_BOT_THEME == "theme_3" || EASYCHAT_BOT_THEME == "theme_4"){

        $(".easychat-bot-restart-div").css("display", "none");

    }else{
        restart_btn.style.display = "none";
    }

}
function reset_footer() {
    try{

    show_restart_button_based_on_theme();
    reset_user_input_for_theme_three();

    if (EASYCHAT_BOT_THEME == "theme_1") {

        document.getElementById("user_input_div").style.width = "70%";
    } else if (EASYCHAT_BOT_THEME == "theme_2") {

        document.getElementById("user_input_div").style.width = "75%";
    } else if (EASYCHAT_BOT_THEME == 'theme_4') {
        if(is_sticky_intent_menu_present) {
            $('.easychat-bot-footer-input-container').css('width', 'calc(100% - 56px)')
            $('.easychat-bot-footer-menus-opner-div').css('display', 'flex')
        }
    } else {
        
        document.getElementById("user_input_div").style.width = "100%";

    }

}catch(err)
{console.log(err)}
}

function reset_user_input_for_theme_three(){
    if(EASYCHAT_BOT_THEME == "theme_3"){
        $(".easychat-bot-user-input-div").css("width","calc(100% - 96px)")
    }
}

function set_footer_for_livechat() {

    hide_restart_button_based_on_theme();

    toggle_sticky_menu("none");
    try {
        if(enable_response_form_assist == 'false'){
            show_user_action_div_for_form_assist();
        }
        var user_input_elem = document.getElementById("user_input_div");
        if (EASYCHAT_BOT_THEME == "theme_2") {

            user_input_elem.style.width = "85%";
        } else if (EASYCHAT_BOT_THEME == "theme_1") {

            document.getElementById("easychat-mic-div-not-allowed").style.paddingRight = "0px";
            document.getElementById("user_input").style.paddingLeft = "15px";
            user_input_elem.style.width = "75%";
        } else {
            user_input_elem.style.width = "70%";
        }
    } catch (err) {
        console.log(err);
    }
    adjust_user_input_for_theme_three_for_livechat();
}

function update_local_storage_window() {
    if (window.localStorage) {
        // flag the every second
        window.localStorage["myUnloadEventFlag"] = new Date().getTime();
    }
}

function disable_sticky_intents() {
    try {
        document.getElementById("easychat-sticky-intents").style.pointerEvents = "none";
    } catch (err) {
        console.log(err);
    }
}

function enable_sticky_intents() {
    try {
        document.getElementById("easychat-sticky-intents").style.pointerEvents = "unset";
    } catch (err) {
        console.log(err);
    }
}

function get_csrf_token() {
    var CSRF_TOKEN = $('input[name="csrfmiddlewaretoken"]').val();
    return CSRF_TOKEN;
}

function enable_mute_unmute_icon () {
    var mute_unmute_div = document.getElementById('easychat-mute-unmute-div');
    
    if (mute_unmute_div) {
        mute_unmute_div.style.display = 'block';

        var mute_icon = document.getElementById('easychat-mute-icon');
        var unmute_icon = document.getElementById('easychat-unmute-icon');

        if (is_mute_before_livechat) {
            mute_icon.style.display = 'block';
            unmute_icon.style.display = 'none';
        } else {
            mute_icon.style.display = 'none';
            unmute_icon.style.display = 'block';
        }
    }
}

function disable_mute_unmute_icon () {
    
    var mute_unmute_div = document.getElementById('easychat-mute-unmute-div');

    if (mute_unmute_div) {
        mute_unmute_div.style.display = 'none';

        var mute_icon = document.getElementById('easychat-mute-icon');
        var unmute_icon = document.getElementById('easychat-unmute-icon');

        if (mute_icon.style.display == 'block') {
            is_mute_before_livechat = true;
        } else {
            is_mute_before_livechat = false;
            mute_icon.style.display = 'block';
            unmute_icon.style.display = 'none';
        }
    }
}

function open_file_upload_modal() {
    if (is_livechat_enabled()) {
        document.getElementById('easychat-livechat-uploadfile').click()
    }
}

function show_user_action_div_for_form_assist(){
    if(EASYCHAT_BOT_THEME == 'theme_1') {
        if(document.getElementById('user_actions_div')){
            document.getElementById('user_actions_div').style.display = 'flex'
        }
    } else if(EASYCHAT_BOT_THEME == 'theme_2') {
        document.getElementById('easychat-footer').style.display = 'flex'
    } else if(EASYCHAT_BOT_THEME == 'theme_3') {
        if(!$('.easychat-bot-language-div').length) {
            $('#user_actions_div').show();
        } else{
            $('#user_actions_div').removeClass('form-assist-disabled')
            $('#form_assist_mic_button_fix').remove()
            $('#user_input').show()
            $('#user_input_placeholder_text').show()
        }
    }
}

function scroll_livechat_form_to_bottom() {
    var objDiv = document.getElementById("livechat-customer-info-form-container");
    objDiv.scrollTop = objDiv.scrollHeight;
}

////////////////// Utility Functions Ends /////////////////////////////////

///////////////// Required DOM Nodes //////////////////////////////////////

var chat_container = document.getElementById("easychat-chat-container");
var chat_footer = document.getElementById("easychat-footer");
var restart_btn = document.getElementById("easychat-restart-div");
var end_chat_elem = document.getElementById("easychat-end-chat");

///////////////// Required DOM Nodes Ends /////////////////////////////////