import axios from "axios";

import { custom_decrypt, getCsrfToken, get_params, is_mobile } from "../../utils";

import { append_system_text_response, get_chat_data, has_customer_left_chat, save_system_message } from "../chatbox";

import { handle_vc_request_rejected_by_customer, show_normal_vc_icon } from "../vc/livechat_vc";

import {
    add_customer_request,
    get_agent_name,
    get_bot_id,
    get_cobrowsing_info,
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
    check_is_email_session,
} from "../console";
import { send_message_to_guest_agent_socket, send_notification_to_customer } from "../livechat_agent_socket";

import { send_message_to_socket } from "../livechat_chat_socket";
import { save_message_to_local } from "../local_db";
import { hide_vc_icon, show_vc_icon, handle_vc_request_accepted_by_customer, generate_video_meet_link } from "../vc/livechat_vc";
import { join_meeting, unmute_audio } from "./join_meeting_pip";
import { set_cobrowsing_status } from "../cobrowsing/manage_cobrowsing";

const state = {
    call_timer: null,
    call_status_timer: null,
    socket: {
        is_open: false,
        instance: null,
    }
}

export function send_voip_request_to_customer(is_resend_request) {
    hide_vc_icon();

    const voip_info = get_voip_info();
    const chat_data = get_chat_data();

    if (!["Web", "Android", "iOS"].includes(chat_data.channel) && voip_info.voip_type == 'pip') {
        showToast(`Cannot start PIP Voice Call in ${chat_data.channel}`, 2000);
        return;
    }

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
                    handle_request(meeting_id, false);
                    handle_request_accepted_by_customer(true);
                } else {
                    handle_request(meeting_id, true);
                    send_request_over_socket(meeting_id, session_id, "VOIP_REQUEST");
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
    const voip_info = get_voip_info();
    var message = JSON.stringify({
        message: JSON.stringify({
            type: "text",
            channel: chat_data.channel,
            path: "",
            event_type: event_type,
            session_id: session_id,
            meeting_id: meeting_id,
            agent_name: get_agent_name(),
            request_from_customer: voip_info.request_from_customer,
        }),
        sender: "System",
    });

    send_message_to_socket(message);
}

function handle_request(meeting_id, show_toast) {
    const voip_info = get_voip_info();
    $("#livechata_voip_call_initiate_btn").hide();
    $("#livechata_vc_call_initiate_btn").hide();
    $("#live_chat_voip_call_reject_div").hide();
    if (voip_info.voip_type == 'video_call'){
        $("#live_chat_video_call_request_sent_div").show();
    } else {
        $("#live_chat_voip_call_request_sent_div").show();
    }

    if (is_mobile()) {
        show_request_sent_voip_icon();
    }

    if (show_toast) {
        $("#livechat_voip_call_request_sent_modal").modal("show");

        setTimeout(() => {
            $("#livechat_voip_call_request_sent_modal").modal("hide");
        }, 2000);
    
        const text = 'Voice Call Request Sent'
        let message_id = save_system_message(text, 'VOICE_CALL', get_session_id());
        append_system_text_response(text, null, get_session_id(), message_id);
        save_message_to_local({
            message: text,
            sender: "System",
            sender_name: "system",
            session_id: get_session_id(),
            is_voice_call_message: true,
            message_for: "primary_agent",
            message_id: message_id,
        })
    }

    set_voip_call_initiated(true, false);
    set_meeting_id(meeting_id);
    set_request_session_id();
    set_voip_request_status('initiated');
    enable_transfer_chat();
    set_cobrowsing_status();
}

export function handle_request_accepted_by_customer(show_toast, customer_name) {

    if (!customer_name) {
        $("#livechata_voip_call_initiate_btn").hide();
        $("#live_chat_voip_call_request_sent_div").hide();
    
        $("#live_chat_voip_call_connect_div").css('display', 'flex');
        
        if (is_mobile()) {
            show_request_accept_voip_icon();
        }
    }

    if (show_toast) {
        const voip_info = get_voip_info();
        const chat_data = get_chat_data();

        if(!["Web", "Android", "iOS"].includes(chat_data.channel)) {
            $("#livechat_voip_call_link_generated_modal").modal("show");
            setTimeout(() => {
                $("#livechat_voip_call_link_generated_modal").modal("hide");
            }, 2000);

            let url = `${window.location.protocol}//${window.location.host}/chat/customer-voice-meeting/?meeting_id=${voip_info.meeting_id}&session_id=${voip_info.session_id}`;
            if(is_mobile()) {
                document.getElementById("query-mobile").value = url;
            } else {
                document.getElementById("query").value = url;
            }
        } else {
            $("#livechat_voip_call_request_accept_modal").modal("show");
        
            if (!is_mobile()) {
                setTimeout(() => {
                    $("#livechat_voip_call_request_accept_modal").modal("hide");
                }, 2000);
            }    
        }

        send_request_status_to_server('accepted');

        const text = 'Voice Call Request Accepted'
        let message_id = save_system_message(text, 'VOICE_CALL', get_session_id());
        append_system_text_response(text, null, get_session_id(), message_id);
        save_message_to_local({
            message: text,
            sender: "System",
            sender_name: "system",
            session_id: get_session_id(),
            is_voice_call_message: true,
            message_for: "primary_agent",
            message_id: message_id,
        })
    }

    set_voip_request_status('accepted');
    enable_transfer_chat();
}

export function handle_request_rejected_by_customer(show_toast, customer_name) {
    const chat_data = get_chat_data();

    if (!customer_name) {
        customer_name = chat_data.customer_name;

        $("#livechata_voip_call_initiate_btn").hide();
        $('#live_chat_voip_call_request_sent_div').hide();
    
        $('#live_chat_voip_call_reject_div').css('display', 'flex');

        if (is_mobile()) {
            show_normal_voip_icon();
        }
    }

    if (show_toast) {
        $('#livechat_voip_request_rejected_text').html(`${customer_name} rejected the request for Voice Call.`)

        $('#livechat_voip_call_request_reject_modal').modal('show');
        
        send_request_status_to_server('rejected');

        const text = 'Voice Call Request Rejected'
        let message_id = save_system_message(text, 'VOICE_CALL', get_session_id());
        append_system_text_response(text, null, get_session_id(), message_id);
        save_message_to_local({
            message: text,
            sender: "System",
            sender_name: "system",
            session_id: get_session_id(),
            is_voice_call_message: true,
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

export function set_voip_status() {
    const voip_info = get_voip_info();
    const session_id = get_session_id();

    if(check_is_email_session(session_id)) {
        $('.livechat-mobile-voip-button').hide();
        return;
    } else {
        $('.livechat-mobile-voip-button').show();
    }

    if (has_customer_left_chat(session_id) || !is_primary_agent(session_id)) {

        if (voip_info.voip_type == 'video_call' && voip_info.meeting_id && voip_info.session_id == session_id) {
            handle_meeting_requested_by_agent(voip_info.request_status, voip_info.meeting_id, voip_info.voip_type);
            $(`#voip_call_indicator-${session_id}`).hide();
        } else {
            $(`#voip_call_indicator-${session_id}`).hide();

            disable_voip_request_btn();
            $("#voip_call_accept_reject_modal").hide();
        }

    } else {
        if (get_cobrowsing_info().status != 'none' && get_cobrowsing_info().status != 'rejected') {
            disable_voip_request_btn();
            return;
        }

        const is_meeting_exists = voip_info.meeting_id != null;

        if (is_meeting_exists) {

            if (!voip_info.request_from_customer && voip_info.session_id == session_id) {
    
                handle_meeting_requested_by_agent(voip_info.request_status, voip_info.meeting_id, voip_info.voip_type);

            } else {
                
                if (voip_info.voip_type == 'video_call') {
                    if (voip_info.request_status != 'rejected') {
                        if (voip_info.session_id == session_id && (voip_info.request_status == 'accepted' || voip_info.request_status == 'ongoing')) {
                            handle_meeting_requested_by_agent(voip_info.request_status, voip_info.meeting_id, voip_info.voip_type);
                        } else {
                            disable_voip_request_btn();
                        }
                    } else {
                        enable_voip_request_btn();
                    }                    
                } else {
                    if (voip_info.request_status != 'rejected') {
                        disable_voip_request_btn();
                    } else {
                        enable_voip_request_btn();
                    }
                }
            }
    
            if (voip_info.customer_requests.length > 0) {
    
                if (voip_info.customer_requests.includes(session_id)) {
                    const customer_request = get_customer_request(session_id);
    
                    if (voip_info.session_id == session_id && voip_info.request_status != 'initiated') {
    
                        $("#voip_call_accept_reject_modal").hide();
    
                        if (voip_info.request_status == 'ongoing') {
                            start_call_timer();
                        }
    
                    } else {
                        if(voip_info.voip_type == 'video_call'){
                            $('#voip_accept_reject_modal_text').html(`${customer_request.customer_name} has invited you for a Video call`);
                            $("#voip_call_accept_reject_modal").slideDown("slow");
                        } else {
                            $('#voip_accept_reject_modal_text').html(`${customer_request.customer_name} has invited you for a Voice call`);
                            $("#voip_call_accept_reject_modal").slideDown("slow");
                        }
                        
                        if (voip_info.session_id != session_id) {
        
                            $('#voip_call_accept_btn').css('opacity', '0.5');
                            $('#voip_call_accept_btn').tooltip('enable');
                            
                        } else {
        
                            $('#voip_call_accept_btn').css('opacity', '1');
                            $('#voip_call_accept_btn').tooltip('disable');
                        }
                    }
    
                } else {
    
                    $("#voip_call_accept_reject_modal").hide();
                }
            }
    
        } else {
            $('#live_chat_voip_call_request_sent_div').hide();
            $('#live_chat_video_call_request_sent_div').hide();
            $("#live_chat_voip_call_connect_div").hide();
            $('#live_chat_voip_call_ongoing_div').hide();
            $('#live_chat_voip_call_reject_div').hide();
            $('#live_chat_video_call_reject_div').hide();
            
            enable_transfer_chat();
            enable_voip_request_btn();
            // show_vc_icon();
        }
    }

    try {
        document.getElementById('live_chat_voip_call_initiate_div').style.display = 'block';
    } catch (err) {}
}

function handle_meeting_requested_by_agent(request_status, meeting_id, voip_type) {
    if (request_status == 'initiated') {
    
        handle_request(meeting_id, false);
    } else if (request_status == 'accepted') {
        if(voip_type == 'video_call'){
            handle_vc_request_accepted_by_customer(false);
        } else {
            handle_request_accepted_by_customer(false);
        }

    } else if (request_status == 'rejected') {
        if(voip_type == 'video_call'){
            handle_vc_request_rejected_by_customer(false);
        } else {
            handle_request_rejected_by_customer(false);
        }
    } else if (request_status == 'ongoing') {

        start_call_timer();
    }
}

export function enable_voip_request_btn() {
    const voip_info = get_voip_info();
    if (voip_info.voip_type == 'video_call'){
        var request_btn = document.getElementById('livechata_vc_call_initiate_btn');
    } else {
        var request_btn = document.getElementById('livechata_voip_call_initiate_btn');
    }
    
    if (request_btn) {
        request_btn.classList.add('live-chat-voip-call-initiate-button');
        request_btn.classList.remove('live-chat-agent-voip-call-initiate-button');
    }

    if (is_mobile()) {
        if (voip_info.voip_type == 'video_call'){
            show_normal_vc_icon();
            $('#mobile_vc_btn').css('pointer-events', 'auto');
        } else {
            show_normal_voip_icon();
            $('#mobile_voip_btn').css('pointer-events', 'auto');
        }
    }
    if (voip_info.voip_type == 'video_call'){
        $("#livechata_vc_call_initiate_btn").show();
    } else {
        $("#livechata_voip_call_initiate_btn").show();
    }

}

export function disable_voip_request_btn() {
    $('#live_chat_voip_call_request_sent_div').hide();
    $("#live_chat_voip_call_connect_div").hide();
    $('#live_chat_voip_call_ongoing_div').hide();
    $('#live_chat_voip_call_reject_div').hide();

    const voip_info = get_voip_info();
    
    if (voip_info.voip_type == 'video_call'){
        var request_btn = document.getElementById('livechata_vc_call_initiate_btn');
    } else {
        var request_btn = document.getElementById('livechata_voip_call_initiate_btn');
    }
        
    if (request_btn) {
        request_btn.classList.remove('live-chat-voip-call-initiate-button');
        request_btn.classList.add('live-chat-agent-voip-call-initiate-button');
    }

    if (is_mobile()) {
        if (voip_info.voip_type == 'video_call'){
            show_normal_vc_icon();
            $('#mobile_vc_btn').css('pointer-events', 'none');
        } else {
            show_normal_voip_icon();
            $('#mobile_voip_btn').css('pointer-events', 'none');
        }
    }

    if (voip_info.voip_type == 'video_call'){
        $("#livechata_vc_call_initiate_btn").show();
        $("#live_chat_video_call_reject_div").hide();
    } else {
        $("#livechata_voip_call_initiate_btn").show();
    }
}

export function connect_voip_call(customer_name) {
    const voip_info = get_voip_info();
    const agent_name = get_agent_name();

    if (!customer_name) {
        const chat_data = get_chat_data();
        customer_name = chat_data.customer_name;
    }

    if (is_primary_agent(voip_info.session_id)) {
        send_request_over_socket(voip_info.meeting_id, voip_info.session_id, "VOIP_CONNECT");
    }

    if (voip_info.voip_type == 'new_tab') {
        voice_call_started_system_message_show();

        let url = `agent-voice-meeting/?meeting_id=${voip_info.meeting_id}&session_id=${voip_info.session_id}`; 
        window.open(url, '_blank');
    } else if (voip_info.voip_type == 'video_call'){
        const text = 'Video Call Started'
        let message_id = save_system_message(text, 'VIDEO_CALL', get_session_id());
        append_system_text_response(text, null, get_session_id(), message_id);
        save_message_to_local({
            message: text,
            sender: "System",
            sender_name: "system",
            session_id: get_session_id(),
            is_video_call_message: true,
            message_for: is_primary_agent(get_session_id()) ? "primary_agent" : "guest_agent",
            message_id: message_id,
            agent_name: get_agent_name(),
        })

        let url = `meeting/${voip_info.meeting_id}`; 
        window.open(url, '_blank'); 
    } else {
        voice_call_started_system_message_show();

        unmute_audio();
        $('#pip_meet_cutomer_name').html(customer_name);
        $('#livechat_VOIP_call_screen_draggable').css('display', 'flex');
        join_meeting(voip_info.meeting_id, voip_info.session_id, agent_name);
    }

    const session_id = get_session_id();

    const json_string = JSON.stringify({
        livechat_session_id: session_id,
        request_raised_by: "agent",
        request_type: "started",
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
                console.log('meeting started');
            } else {
                showToast(response.message, 2000);
            }
        })
        .catch((err) => {
            console.log(err);
        });

    start_call_timer();
}

function voice_call_started_system_message_show() {
    const text = 'Voice Call Started'
        let message_id = save_system_message(text, 'VOICE_CALL', get_session_id());
        append_system_text_response(text, null, get_session_id(), message_id);
        save_message_to_local({
            message: text,
            sender: "System",
            sender_name: "system",
            session_id: get_session_id(),
            is_voice_call_message: true,
            message_for: is_primary_agent(get_session_id()) ? "primary_agent" : "guest_agent",
            message_id: message_id,
            agent_name: get_agent_name(),
        })
}

function start_call_timer () {
    $("#livechata_voip_call_initiate_btn").hide();
    $("#livechata_vc_call_initiate_btn").hide();
    $('#live_chat_voip_call_request_sent_div').hide();
    $("#live_chat_voip_call_connect_div").hide();
    $('#live_chat_video_call_connect_div').hide();
    $('#live_chat_voip_call_ongoing_div').css('display', 'flex');

    const voip_info = get_voip_info();
    
    if (is_mobile()) {
        if (voip_info.voip_type == 'video_call'){
            show_ongoing_vc_icon();
        } else {
            show_ongoing_voip_icon();
        }
    }

    if (voip_info.request_status == 'accepted') {
        localStorage.setItem(`call_start_time_${voip_info.meeting_id}`, Date.parse(new Date()));
    }

    set_voip_request_status('ongoing');

    const timer_elem = document.getElementById('voice_call_timer');

    update_call_time(timer_elem, voip_info);

    if (state.call_timer) {
        clearInterval(state.call_timer);
    }

    state.call_timer = setInterval(() => {
        update_call_time(timer_elem, voip_info);
        reset_inactivity_timer(voip_info.session_id, get_bot_id(), 'customer');
        reset_inactivity_timer(voip_info.session_id, get_bot_id(), 'agent');
    }, 1000);

    if (state.call_status_timer) {
        clearInterval(state.call_status_timer);
    }

    state.call_status_timer = setInterval(() => {
        check_meeting_status(voip_info);
    }, 5000);

    disable_transfer_chat();
} 

export function disable_transfer_chat() {
    $('#livechat-transfer-chat-btn').css('opacity', '0.5');
    $('#livechat-transfer-chat-btn').css('pointer-events', 'none');
}

export function enable_transfer_chat() {
    $('#livechat-transfer-chat-btn').css('opacity', '1');
    $('#livechat-transfer-chat-btn').css('pointer-events', 'auto');
}

export function update_call_time(elem, voip_info) {
    let elapsed_time = Date.parse(new Date()) - localStorage.getItem(`call_start_time_${voip_info.meeting_id}`);
    
    elapsed_time = get_time_elapsed(elapsed_time);

    elem.innerHTML = elapsed_time;
}

export function get_time_elapsed (elapsed_time) {
    let seconds = Math.floor(elapsed_time/1000);

    if (seconds < 60) {
        if (seconds < 10) {
            seconds = `0${seconds}`;
        }

        return `00:${seconds}`;
    }

    let minutes = Math.floor(seconds/60);
    seconds = seconds % 60;

    if (minutes < 10) minutes = `0${minutes}`;

    if (seconds < 10) seconds = `0${seconds}`;

    return `${minutes}:${seconds}`;
}

function check_meeting_status(voip_info) {
    if (voip_info.request_status != 'ongoing') return;

    const config = {
        headers: {
          'X-CSRFToken': getCsrfToken(),
        }
    }

    const json_string = JSON.stringify({
        meeting_id: voip_info.meeting_id,
    });

    const params = get_params(json_string);

    axios
        .post("/livechat/check-meeting-status/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if (response.status == 200) {
                const is_completed = response.is_completed;

                if (is_completed) {
                    console.log('meeting ended');
                    send_meet_end_notification();
                    handle_meeting_end();
                }

            } else {
                showToast(response.message, 2000);
            }
        })
        .catch((err) => {
            console.log(err);
        });
}

export function send_meet_end_notification () {
    const chat_data = get_chat_data();
    const voip_info = get_voip_info();

    var message = JSON.stringify({
        message: JSON.stringify({
            type: "text",
            channel: chat_data.channel,
            path: "",
            event_type: 'MEET_END',
            session_id: voip_info.session_id,
            meeting_id: voip_info.meeting_id,
        }),
        sender: "MEET_END",
    });

    send_notification_to_customer(message);
}

export function handle_meeting_end() {
    const voip_info = get_voip_info();

    if (voip_info.request_status != 'ongoing') return;

    localStorage.removeItem(`call_start_time_${voip_info.meeting_id}`);
    
    $(`#voip_call_indicator-${voip_info.session_id}`).hide();
    remove_customer_request(voip_info.session_id);

    if (voip_info.voip_type == 'video_call') {
        const text = 'Video Call Ended'
        let message_id = save_system_message(text, 'VIDEO_CALL', voip_info.session_id);
        append_system_text_response(text, null, voip_info.session_id, message_id);
        save_message_to_local({
            message: text,
            sender: "System",
            sender_name: "system",
            session_id: voip_info.session_id,
            is_video_call_message: true,
            message_for: is_primary_agent(voip_info.session_id) ? "primary_agent" : "guest_agent",
            message_id: message_id,
        })
    }
    else if (voip_info.voip_type == 'pip' || voip_info.voip_type == 'new_tab') {
        const text = 'Voice Call Ended'
        let message_id = save_system_message(text, 'VOICE_CALL', voip_info.session_id);
        append_system_text_response(text, null, voip_info.session_id, message_id);
        save_message_to_local({
            message: text,
            sender: "System",
            sender_name: "system",
            session_id: voip_info.session_id,
            is_voice_call_message: true,
            message_for: is_primary_agent(voip_info.session_id) ? "primary_agent" : "guest_agent",
            message_id: message_id,
        })
    }

    if (voip_info.customer_requests.length > 0) {
        const request_session_id = voip_info.customer_requests[0];
        const customer_request = get_customer_request(request_session_id);

        set_meeting_id(customer_request.meeting_id);
        set_request_session_id(request_session_id);
        set_voip_call_initiated(true, true);
        set_voip_request_status('initiated');
    } else {
        set_meeting_id(null);
        set_request_session_id(null);
        set_voip_call_initiated(false, false);
        set_voip_request_status('none');   
    }

    clearInterval(state.call_status_timer);
    clearInterval(state.call_timer);
    
    set_voip_status();
}

export function remove_customer_request_on_end_chat(session_id) {
    const voip_info = get_voip_info();

    $(`#voip_call_indicator-${session_id}`).hide();
    remove_customer_request(session_id);

    if (voip_info.session_id == session_id) {
        handle_meeting_end();
    } else {
        set_voip_status();
    }
}

export function cancel_meeting () {
    const voip_info = get_voip_info();

    const chat_data = get_chat_data();

    let session_id = "", meeting_id = "";
    if (voip_info.request_status == 'ongoing' && voip_info.voip_type == 'new_tab') {
        session_id = voip_info.session_id;
        meeting_id = voip_info.meeting_id;
    }

    var message = JSON.stringify({
        message: JSON.stringify({
            type: "text",
            channel: chat_data.channel,
            path: "",
            event_type: 'CANCEL_MEET',
            session_id: session_id,
            meeting_id: meeting_id,
        }),
        sender: "CANCEL_MEET",
    });


    send_notification_to_customer(message);
    handle_meeting_end();
}

export function handle_customer_voip_request (session_id, customer_name) {
    const json_string = JSON.stringify({
        livechat_session_id: session_id,
        request_raised_by: "customer",
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

                handle_customer_request(meeting_id, session_id, customer_name, true);
            } else {
                showToast(response.message, 2000);
            }
        })
        .catch((err) => {
            console.log(err);
        });
}

function handle_customer_request(meeting_id, session_id, customer_name, show_toast) {
    set_customer_requested_voip(meeting_id, session_id, customer_name);
    add_customer_request(session_id);

    const voip_info = get_voip_info();
    
    $(`#voip_call_indicator-${session_id} svg path`).css({"fill": "#F59E0B"});

    if (!voip_info.call_initiated || voip_info.request_status == 'rejected') {
        set_voip_call_initiated(true, true);
        set_meeting_id(meeting_id);
        set_request_session_id(session_id);
        set_voip_request_status('initiated');
    }

    $(`#voip_call_indicator-${session_id}`).show();
    set_voip_status();
}

export function accept_customer_request_for_voip() {

    const voip_info = get_voip_info();

    if (voip_info.session_id != get_session_id()) return;

    $(".livechat-voip-call-reject-accept-popup-div").slideUp("slow");
    const json_string = JSON.stringify({
        livechat_session_id: voip_info.session_id,
        request_raised_by: "customer",
        meeting_id: voip_info.meeting_id,
        request_type: "accepted",
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
                console.log("request updated!");
            } else {
                showToast(response.message, 2000);
            }
        })
        .catch((err) => {
            console.log(err);
        });

    set_voip_request_status('accepted');
    send_request_over_socket(voip_info.meeting_id, voip_info.session_id, 'CUSTOMER_VOIP_ACCEPT');
    if (voip_info.voip_type == 'video_call'){
        $("#live_chat_video_call_connect_div").css('display', 'flex');
        
        var message = JSON.stringify({
            message: JSON.stringify({
                event_type: "GUEST_AGENT_VC_LINK",
                session_id: get_session_id(),
                meeting_id: get_voip_info().meeting_id,
                primary_agent_name: get_agent_name(),
            }),
            sender: "System",
        });

        send_message_to_guest_agent_socket(message);
        if(is_mobile()){
            $("#livechat_video_call_request_accept_modal").modal("show");
        }
    }
    $("#livechata_vc_call_initiate_btn").hide();
}

export function reject_customer_request_for_voip() {
    $(".livechat-voip-call-reject-accept-popup-div").slideUp("slow");

    const voip_info = get_voip_info();
    const session_id = get_session_id();

    $(`#voip_call_indicator-${session_id}`).hide();
    remove_customer_request(session_id);

    if (voip_info.session_id == session_id) {
        if (voip_info.customer_requests.length > 0) {
            const request_session_id = voip_info.customer_requests[0];
            const customer_request = get_customer_request(request_session_id);
    
            set_meeting_id(customer_request.meeting_id);
            set_request_session_id(request_session_id);
            set_voip_call_initiated(true, true);
            set_voip_request_status('initiated');
        } else {
            set_meeting_id(null);
            set_request_session_id(null);
            set_voip_call_initiated(false, false);
            set_voip_request_status('none');   
        }  
    }

    set_voip_status();

    send_request_over_socket(voip_info.meeting_id, voip_info.session_id, 'CUSTOMER_VOIP_REJECT');
}

export function handle_meet_cancel_by_customer(session_id) {
    const voip_info = get_voip_info();
    const curr_session_id = get_session_id();

    remove_customer_request(session_id);
    $(`#voip_call_indicator-${session_id}`).hide();

    if (session_id == curr_session_id) {
        $('#voip_call_accept_reject_modal').hide();
        $('#live_chat_video_call_connect_div').hide();
    }

    let meeting_id;
    if (voip_info.session_id == session_id) {
        meeting_id = voip_info.meeting_id;
        localStorage.removeItem(`call_start_time_${voip_info.meeting_id}`);
    
        set_meeting_id(null);
        set_request_session_id(null);
        set_voip_call_initiated(false, false);
        set_voip_request_status('none');
        clearInterval(state.call_status_timer);
        clearInterval(state.call_timer);    
    } else {
        if (voip_info.from_customer[session_id])
            meeting_id = voip_info.from_customer[session_id].meeting_id;
    }

    set_voip_status();

    if (!meeting_id) return;

    const json_string = JSON.stringify({
        livechat_session_id: session_id,
        request_raised_by: "customer",
        request_type: "interrupted",
        meeting_id: meeting_id,
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
                console.log('meeting started');
            } else {
                showToast(response.message, 2000);
            }
        })
        .catch((err) => {
            console.log(err);
        });
}

function show_normal_voip_icon() {
    $('#mobile_voip_sent_btn').hide();
    $('#mobile_voip_accept_btn').hide();
    $('#mobile_voip_ongoing_btn').hide();
    $('#mobile_voip_btn').show();
}

function show_request_sent_voip_icon() {
    $('#mobile_voip_sent_btn').show();
    $('#mobile_voip_accept_btn').hide();
    $('#mobile_voip_ongoing_btn').hide();
    $('#mobile_voip_btn').hide();
}

function show_request_accept_voip_icon() {
    $('#mobile_voip_sent_btn').hide();
    $('#mobile_voip_accept_btn').show();
    $('#mobile_voip_ongoing_btn').hide();
    $('#mobile_voip_btn').hide();
}

function show_ongoing_voip_icon() {
    $('#mobile_voip_sent_btn').hide();
    $('#mobile_voip_accept_btn').hide();
    $('#mobile_voip_ongoing_btn').show();
    $('#mobile_voip_btn').hide();
}

function show_ongoing_vc_icon() {
    $('#vc_call_sent_svg').hide();
    $('#vc_call_accept_svg').hide();
    $('#vc_call_ongoing_svg').show();
    $('#vc_call_normal_svg').hide();
}