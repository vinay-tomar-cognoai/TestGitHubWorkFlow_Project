// GLOBAL VARIABLES

var call_interval = null;
var call_status_interval = null;
var is_voice_call_going_on = false;
var call_start_time = "";

(function(exports) {

    function open_voip_request_modal() {
        document.getElementById('voice_call_initiated_modal').style.display = 'block';
        chat_container.classList.add('backdrop');

        if (EASYCHAT_BOT_THEME == 'theme_3' || EASYCHAT_BOT_THEME == 'theme_4') {

            document.getElementById("end_chat_btn").classList.remove('backdrop');
        } else {
            document.getElementById("easychat-end-chat").classList.remove('backdrop');
        }

        handle_voice_call_rejected();
        modal_content_position_as_per_lang("voice_call_initiated_modal");
        
        disable_footer_except_home();
    }
    exports.open_voip_request_modal = open_voip_request_modal;

    function open_vc_request_modal() {
        document.getElementById('video_call_initiated_modal').style.display = 'block';
        chat_container.classList.add('backdrop');

        if (EASYCHAT_BOT_THEME == 'theme_3' || EASYCHAT_BOT_THEME == 'theme_4') {

            document.getElementById("end_chat_btn").classList.remove('backdrop');
        } else {
            document.getElementById("easychat-end-chat").classList.remove('backdrop');
        }
        handle_voice_call_rejected();

        modal_content_position_as_per_lang("video_call_initiated_modal");
        
        disable_footer_except_home();
    }
    exports.open_vc_request_modal = open_vc_request_modal;

    function close_voip_request_modal() {
        document.getElementById('voice_call_initiated_modal').style.display = 'none';
        chat_container.classList.remove('backdrop');

        if (EASYCHAT_BOT_THEME == 'theme_3' || EASYCHAT_BOT_THEME == 'theme_4') {

            document.getElementById("end_chat_btn").classList.remove('backdrop');
        } else {
            document.getElementById("easychat-end-chat").classList.remove('backdrop');
        }

        enable_footer();
    }
    exports.close_voip_request_modal = close_voip_request_modal;

    function connect_voip_call(meeting_id, session_id, agent_name) {

        show_ongoing_call_btn()
        if (VOIP_TYPE == 'pip') {
            show_system_message_for_voicecall_start();
            unmute_audio();
            join_meeting_over_pip(meeting_id, session_id, livechat_customer_name);
            is_voice_call_going_on = true;
        } else if (VOIP_TYPE == 'video_call') {

            var text = LIVECHAT_VC_START
            append_system_text_response(text);
            scroll_to_bottom();
            save_customer_chat(text, livechat_session_id, "System", "", "", "", "");
        } else {
            show_system_message_for_voicecall_start();
            is_voice_call_going_on = true;
            var protocol = window.location.protocol == "http:" ? "http://" : "https://";

            let url = protocol + window.location.host + '/customer-voice-meeting/?meeting_id=' + meeting_id + '&session_id=' + session_id; 
            window.open(url, '_blank');    
        }

        start_call_timer(meeting_id, agent_name);
    }
    exports.connect_voip_call = connect_voip_call;

    function handle_meet_end(meeting_id) {
        if (!meeting_id) {
            // meeting_id = localStorage.getItem('meeting_id');
            meeting_id = get_meeting_id();
        }
        
        // localStorage.removeItem('meeting_id');

        if (!meeting_id || meeting_id == "") return;
        
        show_voip_call_btn();
        $('#voice_call_div').hide();

        if (EASYCHAT_BOT_THEME == 'theme_3') {
            $('#easychat-chat-container').css('margin-top', '0vh');
        } else if (EASYCHAT_BOT_THEME != 'theme_4') {
            $('#easychat-chat-container').css('top', '8vh');
        }

        change_voip_btn_to_default();

        if (VOIP_TYPE == 'video_call') {
            var text = LIVECHAT_VC_END
            append_system_text_response(text);
            scroll_to_bottom();
            save_customer_chat(text, livechat_session_id, "System", "", "", "", "");
        }

        else if (VOIP_TYPE == 'pip' || VOIP_TYPE == 'new_tab') {
             
            if (is_voice_call_going_on) {
                var text = LIVECHAT_VOICECALL_END
                append_system_text_response(text);
                scroll_to_bottom();
                save_customer_chat(text, livechat_session_id, "System", "", "", "", "");
            }
            is_voice_call_going_on = false;
        }

        resize_chabot_window();

        if (call_interval) {
            clearInterval(call_interval);
        }

        if (call_status_interval) {
            clearInterval(call_status_interval);
        }

        // localStorage.removeItem('call_start_time_' + meeting_id);
        // localStorage.removeItem('call_agent_name');
    }
    exports.handle_meet_end = handle_meet_end;

    function show_voip_call_btn() {
        if (IS_VOIP_FROM_CUSTOMER_END_ENABLED) {
                $('#voip_call_btn').css('display', 'flex');
        }
    }
    exports.show_voip_call_btn = show_voip_call_btn

    function hide_voip_call_btn() {
        $('#voip_call_btn').css('display', 'none');
    }
    exports.hide_voip_call_btn = hide_voip_call_btn

})(window);

function change_voip_btn_to_default() {
    if (EASYCHAT_BOT_THEME == 'theme_2') {

        $('.voip-call-btn svg path').css({"fill": "white"});

    } else {

        $('.voip-call-btn svg path').css({"fill": "white"});
    }

    $('.voip-call-btn').css('pointer-events', 'auto');
    if(EASYCHAT_BOT_THEME == 'theme_4') { 
        $('#voip_call_btn svg path').css({"fill": "white"});
        $('#voip_call_btn').css("pointer-events", "auto");
    }
}

function start_call_timer(meeting_id, agent_name) {

    if (meeting_id) {

        // localStorage.setItem('meeting_id', meeting_id);
        // localStorage.setItem('call_start_time_' + meeting_id, Date.parse(new Date()));
        // localStorage.setItem('call_agent_name', agent_name);
        call_start_time = Date.parse(new Date());

    } else {

        meeting_id = get_meeting_id();
        agent_name = get_agent_name();
        let livechat_voip_start_time = get_livechat_voip_start_time();

        if(livechat_voip_start_time) {
            call_start_time = Date.parse(new Date(livechat_voip_start_time));
        } else {
            call_start_time = Date.parse(new Date());
        }
    }

    if (!meeting_id) {
        show_voip_call_btn();
        send_cancel_meet_notification();
        return;
    }

    $('#voice_call_div').show();
    show_ongoing_call_btn();

    if (VOIP_TYPE == 'new_tab' || VOIP_TYPE == 'video_call') {
        $('#voice_call_action_btns').hide();
    }

    if (EASYCHAT_BOT_THEME == 'theme_3') {
        $('#easychat-chat-container').css('margin-top', '8vh');
    } else if (EASYCHAT_BOT_THEME != 'theme_4'){
        $('#easychat-chat-container').css('top', '18vh');
    }

    $('#voice_call_agent_name').html(agent_name);

    // resize_chabot_window();

    var timer_elem = document.getElementById('voice_call_timer');

    update_call_time(timer_elem, meeting_id);

    call_interval = setInterval(function() {
        update_call_time(timer_elem, meeting_id);
    }, 1000);

    call_status_interval = setInterval(function() {
        check_meeting_status(meeting_id);
    }, 5000);

}

function check_meeting_status(meeting_id) {
    var json_string = JSON.stringify({
        meeting_id: meeting_id,
    });

    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/check-meeting-status/", true);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = this.response;
            response = JSON.parse(response);
            response = custom_decrypt(response);
            response = JSON.parse(response);

            if (response["status"] == "200") {
                if (response.is_completed) {
                    if (VOIP_TYPE == 'pip') {
                        end_pip_calling();
                    }
                    
                    handle_meet_end(meeting_id);
                }
            } else {
                console.log("Unable to check meeting status."); // Just for debugging purpose
            }
        }
    };
    xhttp.send(params);
}

function update_call_time(elem, meeting_id) {
    let elapsed_time = Date.parse(new Date()) - call_start_time;
    
    elapsed_time = get_time_elapsed(elapsed_time);

    elem.innerHTML = elapsed_time;
}

function get_time_elapsed (elapsed_time) {
    let seconds = Math.floor(elapsed_time/1000);

    if (seconds < 60) {
        if (seconds < 10) {
            seconds = '0' + seconds;
        }

        return '00:' + seconds;
    }

    let minutes = Math.floor(seconds/60);
    seconds = seconds % 60;

    if (minutes < 10) minutes = '0' + minutes;

    if (seconds < 10) seconds = '0' + seconds;

    return minutes + ':' + seconds;
}

function manage_voip_request(is_accepted) {
    var event_type = is_accepted ? 'REQUEST_ACCEPTED' : 'REQUEST_REJECTED';
    
    var sentence = JSON.stringify({
        message: JSON.stringify({
            text_message: "",
            type: "text",
            channel: "Web",
            path: "",
            event_type: event_type,
        }),
        sender: "System",
    });

    if (!is_accepted) {
        show_voip_call_btn();
    }

    send_message_over_socket(sentence, event_type);
    send_notification_to_agent("", "", "", event_type);

    close_voip_request_modal();
}

function send_voip_request_to_agent() {

    if (cobrowsing_status == 'ongoing') {
        $('#end_ongoing_cobrowsing_popup').show();

        setTimeout(function() {
            $('#end_ongoing_cobrowsing_popup').hide();
        }, 2000);

        return;
    }

    $('#voice_call_rejected_modal').hide();
    $('#success_request_popup').show();
    $('.voip-call-btn svg path').css({"fill": "#F59E0B"});
    $('.voip-call-btn').css({"pointer-events": "none"});
    if(EASYCHAT_BOT_THEME == 'theme_4') { 
        $('#voip_call_btn svg path').css({"fill": "#F59E0B"})
        $('#voip_call_btn').css("pointer-events", "none");
    } 

    setTimeout(function() {
        $('#success_request_popup').hide();
    }, 2000);

    if (VOIP_TYPE == 'video_call') {
        var text = LIVECHAT_VC_REQUEST
        append_system_text_response(text);
        scroll_to_bottom();
        save_customer_chat(text, livechat_session_id, "System", "", "", "", "");
    }
    else if (VOIP_TYPE == 'pip' || VOIP_TYPE == 'new_tab') {
        var text = LIVECHAT_VOICECALL_REQUEST
        append_system_text_response(text);
        scroll_to_bottom();
        save_customer_chat(text, livechat_session_id, "System", "", "", "", "");
    }

    send_notification_to_agent("", "", "", "CUSTOMER_VOIP_REQUEST");
}

function handle_agent_accepted_voip_request (meeting_id, session_id, agent_name) {
    $('#voip_connect_modal_text').html(agent_name + ' ' + AGENT_ACCEPTED_VOIP);
    $('#voice_call_connect_modal').show();
    modal_content_position_as_per_lang("voice_call_connect_modal");
}

function connect_voip_call_by_customer(el) {
    send_notification_to_agent("", "", "", "CUSTOMER_VOIP_CONNECT");

    hide_voip_connect_modal();
}

function hide_voip_connect_modal() {
    $('#voice_call_connect_modal').hide();
}

function handle_agent_rejected_voip_request(meeting_id, session_id, agent_name) {
    if(VOIP_TYPE == 'video_call'){
        $('#voice_call_rejected_modal_header').html(VIDEO_CALL_TEXT);
        $('#voip_rejected_modal_text').html(agent_name + ' ' + AGENT_REJECTED_VC);

    } else {
        $('#voip_rejected_modal_text').html(agent_name + ' ' + AGENT_REJECTED_VOIP);
    }

    $('#voice_call_rejected_modal').show();
    modal_content_position_as_per_lang("voice_call_rejected_modal");
}

function handle_voice_call_rejected() {
    change_voip_btn_to_default();
    $('#voice_call_rejected_modal').hide();
}

function send_cancel_meet_notification() {

    console.log('cancel meet');

    setTimeout(function() {
        send_notification_to_agent("", "", "", "CANCEL_MEET");                
    }, 1000);
}

function close_vc_request_modal() {
    document.getElementById('video_call_initiated_modal').style.display = 'none';
    chat_container.classList.remove('backdrop');

    if (EASYCHAT_BOT_THEME == 'theme_3' || EASYCHAT_BOT_THEME == 'theme_4') {

        document.getElementById("end_chat_btn").classList.remove('backdrop');
    } else {
        document.getElementById("easychat-end-chat").classList.remove('backdrop');
    }

    enable_footer();
}

function handle_cancel_meet_by_agent() {
    $('#agent_cancelled_meet_popup').show();

    setTimeout(function() {
        $('#agent_cancelled_meet_popup').hide();
    }, 2000);

    close_voip_request_modal();
    close_vc_request_modal();
    hide_voip_connect_modal();
    change_voip_btn_to_default();

    handle_meet_end();
}

function show_ongoing_call_btn() {
    show_voip_call_btn();
    $('.voip-call-btn svg path').css({"fill": "#10B981"});
    $('.voip-call-btn').css({"pointer-events": "none"});
    if(EASYCHAT_BOT_THEME == 'theme_4') {
        $('#voip_call_btn svg path').css({"fill": "#10B981"});
        $('#voip_call_btn').css("pointer-events", "none");
    }
}

function show_system_message_for_voicecall_start() {
    var text = LIVECHAT_VOICECALL_START
    append_system_text_response(text);
    scroll_to_bottom();
    save_customer_chat(text, livechat_session_id, "System", "", "", "", "");
}