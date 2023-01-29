import axios from "axios";

import { getCsrfToken, custom_decrypt, get_params, is_mobile } from "../../utils";

import { append_system_text_response, get_chat_data, has_customer_left_chat, save_system_message } from "../chatbox";

import { connect_voip_call, enable_transfer_chat } from "../voip/voip";

import {
    add_customer_request,
    add_meeting_to_guest_agent,
    get_agent_name,
    get_bot_id,
    get_customer_request,
    get_session_id,
    get_voip_info,
    is_primary_agent,
    remove_customer_request,
    reset_inactivity_timer,
    set_customer_requested_voip,
    set_meeting_id,
    set_request_session_id,
    set_voip_call_initiated,
    set_voip_request_status,
    showToast,
} from "../console";

import { send_message_to_socket } from "../livechat_chat_socket";

import { send_message_to_guest_agent_socket, send_notification_to_customer } from "../livechat_agent_socket";
import { save_message_to_local } from "../local_db";

const state = {
    nps: {
        rating: -1,
        text_feedback: "",
    }
}

export function send_vc_request_to_customer(is_resend_request) {
    hide_vc_icon();

    const voip_info = get_voip_info();
    const chat_data = get_chat_data();

    if(is_mobile()){
        $(`mobile_vc_btn svg path`).css({"fill": "#F59E0B"});
    }

    $(`#voip_call_indicator-${session_id}`).hide();

    if (!is_resend_request && voip_info.meeting_id != null) return;

    const session_id = get_session_id();

    const json_string = JSON.stringify({
        livechat_session_id: session_id,
        request_raised_by: "agent",
        request_type: "initiated",
    });

    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/manage-voip-request/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if (response.status == 200) {
                const meeting_id = response.meeting_id;
                
                if (chat_data.is_external || !["Web", "Android", "iOS"].includes(chat_data.channel)) {
                    handle_vc_request(meeting_id, false);
                    handle_vc_request_accepted_by_customer(true);
                } else {
                    handle_vc_request(meeting_id, true);
                    send_request_over_socket(meeting_id, session_id, "VC_REQUEST");
                }
            } else {
                showToast(response.message, 2000);
            }
        })
        .catch((err) => {
            console.log(err);
        });
}

function send_request_over_socket(meeting_id, session_id, event_type) {
    const chat_data = get_chat_data();

    var message = JSON.stringify({
        message: JSON.stringify({
            type: "text",
            channel: chat_data.channel,
            path: "",
            event_type: event_type,
            session_id: session_id,
            meeting_id: meeting_id,
            agent_name: get_agent_name(),
        }),
        sender: "System",
    });

    send_message_to_socket(message);
}

function handle_vc_request(meeting_id, show_toast) {
    $("#livechata_voip_call_initiate_btn").hide();
    $("#livechata_vc_call_initiate_btn").hide();
    $("#live_chat_voip_call_reject_div").hide();
    $("#live_chat_video_call_reject_div").hide();
    $("#live_chat_video_call_request_sent_div").show();

    if (is_mobile()) {
        show_request_sent_vc_icon();
    }

    if (show_toast) {
        $("#livechat_video_call_request_sent_modal").modal("show");

        setTimeout(() => {
            $("#livechat_video_call_request_sent_modal").modal("hide");
        }, 2000);
    
        const text = 'Video Call Request Sent'
        let message_id = save_system_message(text, 'VIDEO_CALL', get_session_id());
        append_system_text_response(text, null, get_session_id(), message_id);
        save_message_to_local({
            message: text,
            sender: "System",
            sender_name: "system",
            session_id: get_session_id(),
            is_video_call_message: true,
            message_for: "primary_agent",
            message_id: message_id,
        })
    }

    set_voip_call_initiated(true, false);
    set_meeting_id(meeting_id);
    set_request_session_id();
    set_voip_request_status('initiated');
    enable_transfer_chat();
}

export function handle_vc_request_accepted_by_customer(show_toast, customer_name) {

    const chat_data = get_chat_data();
    const voip_info = get_voip_info();

    if (!customer_name) {
        $("#livechata_voip_call_initiate_btn").hide();
        $("#livechata_vc_call_initiate_btn").hide();
        $("#live_chat_voip_call_request_sent_div").hide();
        $("#live_chat_video_call_request_sent_div").hide();
    
        $("#live_chat_video_call_connect_div").css('display', 'flex');
        
        if (is_mobile()) {
            show_request_accept_vc_icon();
        }
    }


    if (show_toast) {
        send_request_status_to_server('accepted');

        if(!["Web", "Android", "iOS"].includes(chat_data.channel)) {
            $("#livechat_vc_call_link_generated_modal").modal("show");
        
            if (!is_mobile()) {
                setTimeout(() => {
                    $("#livechat_vc_call_link_generated_modal").modal("hide");
                }, 2000);
            }

            let url = `${window.location.protocol}//${window.location.host}/livechat/meeting/${voip_info.meeting_id}`;
            if(is_mobile()) {
                document.getElementById("query-mobile").value = url;
            } else {
                document.getElementById("query").value = url;
            }
        } else {
            $("#livechat_video_call_request_accept_modal").modal("show");
        
            if (!is_mobile()) {
                setTimeout(() => {
                    $("#livechat_video_call_request_accept_modal").modal("hide");
                }, 2000);
            }
        }
        
        const text = 'Video Call Request Accepted'
        let message_id = save_system_message(text, 'VIDEO_CALL', get_session_id());
        append_system_text_response(text, null, get_session_id(), message_id);
        save_message_to_local({
            message: text,
            sender: "System",
            sender_name: "system",
            session_id: get_session_id(),
            is_video_call_message: true,
            message_for: "primary_agent",
            message_id: message_id,
        })
    }
    set_voip_request_status('accepted');
    enable_transfer_chat();
}

export function handle_vc_request_rejected_by_customer(show_toast, customer_name) {
    const chat_data = get_chat_data();

    if (!customer_name) {
        customer_name = chat_data.customer_name;

        $("#livechata_voip_call_initiate_btn").hide();
        $("#livechata_vc_call_initiate_btn").hide();
        $('#live_chat_video_call_request_sent_div').hide();
        $('#live_chat_video_call_reject_div').css('display', 'flex');

        if (is_mobile()) {
            show_normal_vc_icon();
        }
    }

    if (show_toast) {
        $('#livechat_voip_request_rejected_text').html(`${customer_name} rejected the request for Video Call.`)

        $('#livechat_voip_call_request_reject_modal').modal('show');
        
        send_request_status_to_server('rejected');

        const text = 'Video Call Request Rejected'
        let message_id = save_system_message(text, 'VIDEO_CALL', get_session_id());
        append_system_text_response(text, null, get_session_id(), message_id);
        save_message_to_local({
            message: text,
            sender: "System",
            sender_name: "system",
            session_id: get_session_id(),
            is_video_call_message: true,
            message_for: "primary_agent",
            message_id: message_id,
        })
    }

    set_voip_request_status('rejected');
    enable_transfer_chat();
}

function send_request_status_to_server(status) {
    const session_id = get_session_id();
    const voip_info = get_voip_info();

    const json_string = JSON.stringify({
        livechat_session_id: session_id,
        request_raised_by: "agent",
        request_type: status,
        meeting_id: voip_info.meeting_id,
    });

    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/manage-voip-request/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if (response.status == 200) {
                console.log('request updated!');
            } else {
                showToast(response.message, 2000);
            }
        })
        .catch((err) => {
            console.log(err);
        });
}

export function generate_video_meet_link() {

    $('#live_chat_voip_call_initiate_div').hide();

    const json_string = JSON.stringify({
        session_id: get_session_id()
    });

    const params = get_params(json_string);
    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/generate-video-meeting/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if (response.status == 200) {

                if(is_mobile()) {

                    document.getElementById("query-mobile").value = response["meeting_url"];
                } else {

                    document.getElementById("query").value = response["meeting_url"];
                    parent.window.open(response["meeting_url"], '_blank'); 
                }
                showToast("Video meeting link generated successfully.", 1000);
            } else {

                showToast("Unable to generate video meeting link. Please try again after some time.", 2000);
            }
        })
        .catch((err) => {
            console.log(err);
        });
}

export function show_vc_icon() {
    $('#livechata_vc_call_initiate_btn').show();
}

export function hide_vc_icon() {
    $('#livechata_vc_call_initiate_btn').hide();
}

export function handle_guest_agent_join_call_request (meeting_id, session_id, primary_agent_name) {
    add_meeting_to_guest_agent(session_id, meeting_id, primary_agent_name);
    handle_vc_status_for_guest_agent();
}

export function handle_vc_status_for_guest_agent () {
    const session_id = get_session_id();
    const voip_info = get_voip_info();

    if (voip_info.guest_agent.requests.includes(session_id)) {
        const chat_data = get_chat_data();
        const primary_agent_name = voip_info.guest_agent.requests_map[session_id].primary_agent_name;
        const btn = document.getElementById('guest_agent_call_connect_btn');

        if (voip_info.meeting_id) {
            if (voip_info.session_id == session_id) {
                $(".livechat-voip-call-reject-accept-popup-div").hide();
            } else {
                $(btn).css('opacity', '0.5');
                $(btn).tooltip('enable');
            }

        } else {
            $(btn).css('opacity', '1');
            $(btn).tooltip('disable');
        }

        $('#guest_agent_join_call_text').html(`${primary_agent_name} and ${chat_data.customer_name} are on call.`);
        $(".livechat-voip-call-reject-accept-popup-div").slideDown("slow");
    } else {

        $(".livechat-voip-call-reject-accept-popup-div").hide();
    }
}

export function join_guest_agent_to_call() {
    const session_id = get_session_id();
    const voip_info = get_voip_info();
    const call_info = voip_info.guest_agent.requests_map[session_id];

    if (call_info) {
        $(".livechat-voip-call-reject-accept-popup-div").slideUp("slow");
        set_voip_call_initiated(true, false);
        set_meeting_id(call_info.meeting_id);
        set_request_session_id();
        set_voip_request_status('accepted');

        var message = JSON.stringify({
            message: JSON.stringify({
                event_type: "GUEST_AGENT_JOINED_VC",
                session_id: session_id,
                meeting_id: voip_info.meeting_id,
                guest_agent_name: get_agent_name(),
            }),
            sender: "System",
        });

        send_message_to_guest_agent_socket(message);

        connect_voip_call();
    }
}

export function show_normal_vc_icon() {
    $('#vc_call_sent_svg').hide();
    $('#vc_call_accept_svg').hide();
    $('#vc_call_ongoing_svg').hide();
    $('#vc_call_normal_svg').show();
}

export function show_request_sent_vc_icon() {
    $('#vc_call_sent_svg').show();
    $('#vc_call_accept_svg').hide();
    $('#vc_call_ongoing_svg').hide();
    $('#vc_call_normal_svg').hide();
}

export function show_request_accept_vc_icon() {
    $('#vc_call_sent_svg').hide();
    $('#vc_call_accept_svg').show();
    $('#vc_call_ongoing_svg').hide();
    $('#vc_call_normal_svg').hide();
}
// Feedback

export function change_color_ratingv_bar(el) {
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

export function save_livechat_feedback_text() {
    state.nps.text_feedback = document.getElementById("livechat-chatbot-comment-box").value;

    console.log(state.nps.text_feedback);
}

export function set_value_to_some(el) {
    var feedback_btn = document.getElementById("feedback-submit-button");

    feedback_btn.style.opacity = 1;
    feedback_btn.disabled = false;
    el.parentElement.setAttribute("zQPK", "true");
    state.nps.rating = parseInt(el.getAttribute("value")) - 1;
}

export function change_color_ratingz_bar_all(el) {
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

export function change_color_ratingz_bar(el) {
    let current_hover_value = parseInt(el.getAttribute("value"));
    for (var i = current_hover_value; i <= current_hover_value; i++) {
        if (el.parentElement.children[i] != undefined) {
            el.parentElement.children[i].style.color = "black";
            el.parentElement.children[i].style.backgroundColor = "white";
        }
    }
}

export function save_feedback () {
    const json_string = JSON.stringify({
        meeting_id: window.MEETING_ID,
        rating: state.nps.rating,
        text_feedback: state.nps.text_feedback
    })

    const params = get_params(json_string);

    axios
        .post('/livechat/save-call-feedback/', params)
        .then (response => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if (response.status == 200) {
                console.log('feedback saved successfully');
            } else {
                console.log('feedback save failed');
            }

            $('#livechat-vc-feedback-modal').modal('hide');
        })
}
