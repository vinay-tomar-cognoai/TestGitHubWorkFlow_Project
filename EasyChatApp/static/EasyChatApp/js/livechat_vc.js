// GLOBAL VARIABLES

var call_interval = null;

(function(exports) {

    function open_vc_request_modal() {
        document.getElementById('video_call_initiated_modal').style.display = 'block';
        chat_container.classList.add('backdrop');

        if (EASYCHAT_BOT_THEME == 'theme_3' || EASYCHAT_BOT_THEME == 'theme_4') {

            document.getElementById("end_chat_btn").classList.remove('backdrop');
        } else {
            document.getElementById("easychat-end-chat").classList.remove('backdrop');
        }

        modal_content_position_as_per_lang("video_call_initiated_modal");

        disable_footer_except_home();
    }
    exports.open_vc_request_modal = open_vc_request_modal;

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
    exports.close_vc_request_modal = close_vc_request_modal;

    function append_meeting_link(message_text, meeting_id, message){
        var last_bot_msg = document.getElementsByClassName("easychat-bot-message easychat-bot-message-line");
        if (EASYCHAT_BOT_THEME == 'theme_3' || EASYCHAT_BOT_THEME == 'theme_4'){
            var last_bot_msg = document.getElementsByClassName("easychat-bot-message-text-div");
        }
        append_bot_text_response(message_text, undefined, undefined, message);
        let accept_btn = document.createElement('a');
        var protocol = window.location.protocol == "http:" ? "http://" : "https://";
        let url = protocol + window.location.host + '/livechat/meeting/' + meeting_id + `?language=${selected_language}`;  
        accept_btn.setAttribute('href', url);
        accept_btn.setAttribute('target', '_blank');
        accept_btn.setAttribute('class', 'video-call-join-now-btn');
        accept_btn.innerHTML = LIVECHAT_VC_JOIN_NOW_TEXT;
        last_bot_msg[last_bot_msg.length-1].appendChild(accept_btn);
    }

    exports.append_meeting_link = append_meeting_link;
})(window);

function manage_vc_request(is_accepted) {
    var event_type = is_accepted ? 'VC_REQUEST_ACCEPTED' : 'VC_REQUEST_REJECTED';
    
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

    send_message_over_socket(sentence, event_type);
    if(!is_accepted && document.getElementById("voip_call_btn")){
        document.getElementById("voip_call_btn").style.pointerEvents = 'auto';
    }
    close_vc_request_modal();

}
