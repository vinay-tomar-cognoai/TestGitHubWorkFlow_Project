(function (exports) {
    function open_cobrowsing_request_modal() {
        document.getElementById('cobrowsing_requested_modal').style.display = 'block';
        chat_container.classList.add('backdrop');

        if (EASYCHAT_BOT_THEME == 'theme_3' || EASYCHAT_BOT_THEME == 'theme_4') {

            document.getElementById("end_chat_btn").classList.remove('backdrop');
        } else {
            document.getElementById("easychat-end-chat").classList.remove('backdrop');
        }

        $("#cobrowsing_requested_modal .cobrowse-session-modal-header").css("justify-content", "flex-start");

        disable_footer_except_home();
    }

    exports.open_cobrowsing_request_modal = open_cobrowsing_request_modal;

    function close_cobrowsing_request_modal() {
        document.getElementById('cobrowsing_requested_modal').style.display = 'none';
        chat_container.classList.remove('backdrop');

        if (EASYCHAT_BOT_THEME == 'theme_3' || EASYCHAT_BOT_THEME == 'theme_4') {

            document.getElementById("end_chat_btn").classList.remove('backdrop');
        } else {
            document.getElementById("easychat-end-chat").classList.remove('backdrop');
        }

        enable_footer();
    }
    exports.close_cobrowsing_request_modal = close_cobrowsing_request_modal;


    function set_cobrowsing_status(status) {
        console.log(status);
        if (status == 'initiated') {
            open_cobrowsing_request_modal();
        } else if (status == 'completed') {
            var text = CB_END
            append_system_text_response(text);
            scroll_to_bottom();
            save_customer_chat(text, livechat_session_id, "System", "", "", "", "");
        }
    }

    exports.set_cobrowsing_status = set_cobrowsing_status;
})(window)

function manage_cobrowsing_request(status) {
    var event_type = status == 'accepted' ? 'COBROWSING_REQUEST_ACCEPTED' : 'COBROWSING_REQUEST_REJECTED';
    
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
    send_cobrowsing_status_to_server(status);
    close_cobrowsing_request_modal();

    if (status == 'accepted') {
        parent.postMessage(
            {
                event_id: "initialize-cobrowse",
                data: {
                    username: username,
                    phone: phone,
                    livechat_session_id: livechat_session_id,
                    cobrowsing_meeting_id: cobrowsing_meeting_id,
                    assigned_agent_username: assigned_agent_username,
                },
            },
            "*"
        );

        var text = CB_START
        append_system_text_response(text);
        scroll_to_bottom();
        save_customer_chat(text, livechat_session_id, "System", "", "", "", "");
        cobrowsing_status = 'ongoing';
    }
}

function send_cobrowsing_status_to_server(status) {
    json_string = {
        'meeting_id': cobrowsing_meeting_id,
        'livechat_session_id': livechat_session_id,
        'request_type': status,
    }
    json_string = JSON.stringify(json_string);
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", '/livechat/manage-cobrowsing-request/', false);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = this.response;
            response = JSON.parse(response);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == 200 || response["status_code"] == "200") {
                console.log("status saved");
            }
        }
    };
    xhttp.send(params);
}
