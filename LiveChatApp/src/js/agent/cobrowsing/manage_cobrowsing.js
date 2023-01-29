import axios from "axios";

import { custom_decrypt, encrypt_variable, getCsrfToken, get_params, is_mobile } from "../../utils";
import { append_system_text_response, get_chat_data, has_customer_left_chat, load_resolve_chat_form, save_system_message } from "../chatbox";
import { get_agent_name, get_agent_username, get_bot_id, get_cobrowsing_info, get_session_id, get_voip_info, is_guest_session_onhold, is_primary_agent, reset_inactivity_timer, set_cobrowse_session_id, set_cobrowsing_info, set_is_eligible_for_cobrowsing, showToast, check_is_email_session } from "../console";
import { send_message_to_guest_agent_socket } from "../livechat_agent_socket";
import { send_message_to_socket } from "../livechat_chat_socket";
import { save_message_to_local } from "../local_db";
import { disable_transfer_chat, get_time_elapsed, set_voip_status } from "../voip/voip";

const state = {
    call_timer: null,
    call_status_timer: null,
}

export function send_cobrowsing_request_to_customer() {
    const cobrowsing_info = get_cobrowsing_info();
    const chat_data = get_chat_data();

    if (["initiated", "accepted", "ongoing"].includes(cobrowsing_info.status))
        return;

    const session_id = get_session_id();

    const json_string = JSON.stringify({
        livechat_session_id: session_id,
        request_type: "initiated",
    });

    const params = get_params(json_string);

    const config = {
        headers: {
          'X-CSRFToken': getCsrfToken(),
        }
    }

    axios
        .post("/livechat/manage-cobrowsing-request/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if (response.status == 200) {
                const meeting_id = response.meeting_id;

                console.log(meeting_id);
                send_request_over_socket(meeting_id, session_id, "COBROWSING_REQUEST");

                set_cobrowsing_info({
                    meeting_id: meeting_id,
                    session_id: session_id,
                    status: 'initiated',
                });

                set_cobrowsing_status();
                set_voip_status();

                append_system_message('Cobrowsing Session Request Sent', null, "primary_agent");

                $("#livechat_cobrowsing_request_sent_modal").modal("show");
            
                setTimeout(() => {
                    $("#livechat_cobrowsing_request_sent_modal").modal("hide");
                }, 2000);

                // if (chat_data.is_external) {
                //     handle_request(meeting_id, false);
                //     handle_request_accepted_by_customer(true);
                // } else {
                //     handle_request(meeting_id, true);
                // }
            } else {
                showToast(response.message, 2000);
            }
        })
        .catch((err) => {
            console.log(err);
        });
}

export function append_system_message(message, session_id, message_for) {
    if (!session_id) session_id = get_session_id();

    let message_id = save_system_message(message, 'COBROWSING', session_id);
    append_system_text_response(message, null, session_id, message_id);
    save_message_to_local({
        message: message,
        sender: "System",
        sender_name: "system",
        session_id: session_id,
        is_cobrowsing_message: true,
        message_for: message_for,
        sender_username: get_agent_username(),
        message_id: message_id,
    })
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

export function set_cobrowsing_status () {
    const cobrowsing_info = get_cobrowsing_info();
    const voip_info = get_voip_info();
    const session_id = get_session_id();
    const chat_data = get_chat_data();

    if(check_is_email_session(session_id)) {
        $('.livechat-mobile-cb-button').hide();
        return;
    } else {
        $('.livechat-mobile-cb-button').show();
    }

    if (!cobrowsing_info.is_enabled) return;

    try {
        document.getElementById('live_chat_voip_call_initiate_div').style.display = 'block';
    } catch (err) {}

    if (!cobrowsing_info.is_eligible) {
        show_not_eligible_cobrowse_btn();
        return;
    } else if(cobrowsing_info.is_eligible && chat_data.channel != 'Web') {
        show_cobrowsing_not_support_at_customer_end();
    } else {
        hide_not_eligible_cobrowse_btn();
    }

    const is_same_chat_open = session_id == cobrowsing_info.session_id;

    if (is_same_chat_open) {
        if (has_customer_left_chat(session_id)) {
            set_cobrowsing_info({
                meeting_id: null,
                session_id: null,
                status: 'none',
            })
            disable_cobrowsing_btn();
            return;
        }

        if (voip_info.request_status && voip_info.request_status != 'none' && voip_info.request_status != 'rejected') {
            disable_cobrowsing_btn();
            return;
        }
        

        if (cobrowsing_info.status == 'none' && chat_data.channel == 'Web') {
            enable_default_cobrowsing_btn();
        } else if (cobrowsing_info.status == 'initiated') {
            enable_request_sent_cobrowsing_btn();
        } else if (cobrowsing_info.status == 'accepted') {
            enable_accepted_cobrowsing_btn();
        } else if (cobrowsing_info.status == 'rejected') {
            enable_rejected_cobrowsing_btn();
        } else if (cobrowsing_info.status == 'ongoing') {
            enable_ongoing_cobrowsing_btn();
        } 
    } else {
        if (!is_primary_agent(session_id)) {

            let join_request = cobrowsing_info.guest_requests.filter(request => request.session_id == session_id);

            if (join_request.length > 0) {
                join_request = join_request[0];
                if (['accepted', 'ongoing'].includes(join_request.status) && !join_request.joined) {
                    if (cobrowsing_info.status != 'none' || (voip_info.request_status && voip_info.request_status != 'none')) {
                        disable_join_button();
                    } else {
                        enable_join_button();
                    }
                    
                    if (!is_guest_session_onhold()) {
                        $('#guest_agent_join_cobrowsing_text').html(`${join_request.primary_agent_name} and ${chat_data.customer_name} are in a cobrowsing session.`);
                        $(".livechat-cobrowsing-reject-accept-popup-div").slideDown("slow");
                    } else {
                        $(".livechat-cobrowsing-reject-accept-popup-div").hide();
                    }
                } else {
                    if (join_request.joined) {
                        set_cobrowsing_info({
                            meeting_id: join_request.meeting_id,
                            session_id: join_request.session_id,
                            status: join_request.status,
                        })
                        set_cobrowse_session_id(join_request.cobrowse_session_id);
                        enable_ongoing_cobrowsing_btn();
                        start_timer(cobrowsing_info, "guest_agent");
                        disable_transfer_chat();
                    }

                    $(".livechat-cobrowsing-reject-accept-popup-div").hide();
                }
            } else {
                $(".livechat-cobrowsing-reject-accept-popup-div").hide();
            }

            disable_cobrowsing_btn();

        } else if (has_customer_left_chat(session_id)) {
            disable_cobrowsing_btn();
        } else if (voip_info.request_status && voip_info.request_status != 'none' && voip_info.request_status != 'rejected') {
            disable_cobrowsing_btn();
            return;
        } else if ((cobrowsing_info.status == 'none' || cobrowsing_info.status == 'rejected') && chat_data.channel == 'Web') {
            enable_default_cobrowsing_btn();
        } else if(cobrowsing_info.is_eligible && chat_data.channel != 'Web') {
            show_cobrowsing_not_support_at_customer_end();
        } else {
            disable_cobrowsing_btn();
        }
    }
}

function enable_default_cobrowsing_btn() {
    $('#livechat_send_cobrowsing_request_btn').css('display', 'flex');

    $('#livechat_connect_cobrowsing_btn').hide();
    $('#livechat_ongoing_cobrowsing_div').hide();
    $('#livechat_cobrowsing_request_sent_btn').hide();
    $('#livechat_resend_cobrowsing_request_btn').hide();
    $('#livechat-not-supported-cobrowsing-btn').hide();

    const request_btn = document.getElementById('livechat_send_cobrowsing_request_btn');

    if (request_btn) {
        request_btn.classList.remove('live-chat-agent-voip-call-initiate-button');
        request_btn.classList.add('livechat-vc-call-btns');
    }

    if (is_mobile()) {
        $('#mobile_cb_normal_btn').show();

        $('#mobile_cb_accept_btn').hide();
        $('#mobile_cb_sent_btn').hide();
        $('#mobile_cb_ongoing_btn').hide();
        $('#mobile_cb_disabled_btn').hide();
    }
}

function disable_cobrowsing_btn() {
    $('#livechat_send_cobrowsing_request_btn').css('display', 'flex');

    $('#livechat_connect_cobrowsing_btn').hide();
    $('#livechat_ongoing_cobrowsing_div').hide();
    $('#livechat_cobrowsing_request_sent_btn').hide();
    $('#livechat_resend_cobrowsing_request_btn').hide();
    $('#livechat-not-supported-cobrowsing-btn').hide();

    const request_btn = document.getElementById('livechat_send_cobrowsing_request_btn');
    if (request_btn) {
        request_btn.classList.remove('livechat-vc-call-btns');
        request_btn.classList.add('live-chat-agent-voip-call-initiate-button');
    }

    if (is_mobile()) {
        $('#mobile_cb_disabled_btn').show();

        $('#mobile_cb_normal_btn').hide();
        $('#mobile_cb_accept_btn').hide();
        $('#mobile_cb_sent_btn').hide();
        $('#mobile_cb_ongoing_btn').hide();
    }
}

function enable_request_sent_cobrowsing_btn() {
    $('#livechat_cobrowsing_request_sent_btn').show();

    $('#livechat_send_cobrowsing_request_btn').hide();
    $('#livechat_connect_cobrowsing_btn').hide();
    $('#livechat_ongoing_cobrowsing_div').hide();
    $('#livechat_resend_cobrowsing_request_btn').hide();
    $('#livechat-not-supported-cobrowsing-btn').hide();

    if (is_mobile()) {
        $('#mobile_cb_sent_btn').show();

        $('#mobile_cb_normal_btn').hide();
        $('#mobile_cb_accept_btn').hide();
        $('#mobile_cb_ongoing_btn').hide();
        $('#mobile_cb_disabled_btn').hide();
    }
}

function enable_accepted_cobrowsing_btn() {
    $('#livechat_connect_cobrowsing_btn').show();

    $('#livechat_send_cobrowsing_request_btn').hide();
    $('#livechat_ongoing_cobrowsing_div').hide();
    $('#livechat_cobrowsing_request_sent_btn').hide();
    $('#livechat_resend_cobrowsing_request_btn').hide();
    $('#livechat-not-supported-cobrowsing-btn').hide();

    if (is_mobile()) {
        $('#mobile_cb_accept_btn').show();

        $('#mobile_cb_sent_btn').hide();
        $('#mobile_cb_normal_btn').hide();
        $('#mobile_cb_ongoing_btn').hide();
        $('#mobile_cb_disabled_btn').hide();
    }
}

function enable_rejected_cobrowsing_btn() {
    $('#livechat_resend_cobrowsing_request_btn').show();

    $('#livechat_send_cobrowsing_request_btn').hide();
    $('#livechat_connect_cobrowsing_btn').hide();
    $('#livechat_ongoing_cobrowsing_div').hide();
    $('#livechat_cobrowsing_request_sent_btn').hide();
    $('#livechat-not-supported-cobrowsing-btn').hide();

    if (is_mobile()) {
        $('#mobile_cb_normal_btn').show();

        $('#mobile_cb_accept_btn').hide();
        $('#mobile_cb_sent_btn').hide();
        $('#mobile_cb_ongoing_btn').hide();
        $('#mobile_cb_disabled_btn').hide();
    }
}

function enable_ongoing_cobrowsing_btn() {
    $('#livechat_ongoing_cobrowsing_div').css('display', 'flex');

    $('#livechat_send_cobrowsing_request_btn').hide();
    $('#livechat_connect_cobrowsing_btn').hide();
    $('#livechat_cobrowsing_request_sent_btn').hide();
    $('#livechat_resend_cobrowsing_request_btn').hide();
    $('#livechat-not-supported-cobrowsing-btn').hide();

    if (is_mobile()) {
        $('#mobile_cb_ongoing_btn').show();

        $('#mobile_cb_normal_btn').hide();
        $('#mobile_cb_accept_btn').hide();
        $('#mobile_cb_sent_btn').hide();
        $('#mobile_cb_disabled_btn').hide();
    }
}

function show_not_eligible_cobrowse_btn() {
    $('#livechat_not_eligible_cobrowsing_request_btn').css('display', 'flex');

    $('#livechat_send_cobrowsing_request_btn').hide();
    $('#livechat_connect_cobrowsing_btn').hide();
    $('#livechat_cobrowsing_request_sent_btn').hide();
    $('#livechat_resend_cobrowsing_request_btn').hide();
    $('#livechat_ongoing_cobrowsing_div').hide();
    $('#livechat-not-supported-cobrowsing-btn').hide();

    if (is_mobile()) {
        $('#mobile_cb_ongoing_btn').hide();
        $('#mobile_cb_normal_btn').hide();
        $('#mobile_cb_accept_btn').hide();
        $('#mobile_cb_sent_btn').hide();
        $('#mobile_cb_disabled_btn').show();
    }
}

function show_cobrowsing_not_support_at_customer_end(){
    $('#livechat-not-supported-cobrowsing-btn').css('display', 'flex');

    $('#livechat_send_cobrowsing_request_btn').hide();
    $('#livechat_connect_cobrowsing_btn').hide();
    $('#livechat_cobrowsing_request_sent_btn').hide();
    $('#livechat_resend_cobrowsing_request_btn').hide();
    $('#livechat_ongoing_cobrowsing_div').hide();
    $('#livechat_not_eligible_cobrowsing_request_btn').hide();

    if (is_mobile()) {
        $('#mobile_cb_ongoing_btn').hide();
        $('#mobile_cb_normal_btn').hide();
        $('#mobile_cb_accept_btn').hide();
        $('#mobile_cb_sent_btn').hide();
        $('#mobile_cb_disabled_btn').show();
    }


}

function hide_not_eligible_cobrowse_btn() {
    $('#livechat_not_eligible_cobrowsing_request_btn').hide();
}

export function go_to_cobrowsing_page() {
    const cobrowsing_info = get_cobrowsing_info();
    console.log(cobrowsing_info);

    if (cobrowsing_info.cobrowse_session_id) {
        window.open(`/easy-assist/agent/${cobrowsing_info.cobrowse_session_id}`, '_blank');
    }
}

export function connect_agent_to_cobrowsing() {
    const cobrowsing_info = get_cobrowsing_info();

    if (!cobrowsing_info.cobrowse_session_id || cobrowsing_info.cobrowse_session_id == "") {
        showToast('Could not start cobrowsing session. Please try again.', 2000);
        set_cobrowsing_info({
            meeting_id: null,
            session_id: null,
            status: 'none',
        })

        set_cobrowsing_status();
        return;
    }

    go_to_cobrowsing_page();

    const session_id = get_session_id();

    const json_string = JSON.stringify({
        livechat_session_id: session_id,
        request_type: "started",
        meeting_id: cobrowsing_info.meeting_id,
    });

    const params = get_params(json_string);
    const config = {
        headers: {
          'X-CSRFToken': getCsrfToken(),
        }
    }

    axios
        .post("/livechat/manage-cobrowsing-request/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if (response.status == 200) {
                console.log('cobrowsing started');
            } else {
                showToast(response.message, 2000);
            }
        })
        .catch((err) => {
            console.log(err);
        });
    
    append_system_message('Cobrowsing Session Started', null, "primary_agent");
    start_cobrowsing_timer("primary_agent");
}

export function start_cobrowsing_timer (message_for) {
    const cobrowsing_info = get_cobrowsing_info();

    if (cobrowsing_info.status == 'accepted') {
        localStorage.setItem(`cobrowse_start_time_${cobrowsing_info.meeting_id}`, Date.parse(new Date()));
    }

    set_cobrowsing_info({
        meeting_id: cobrowsing_info.meeting_id,
        session_id: cobrowsing_info.session_id,
        status: 'ongoing',
    })

    set_cobrowsing_status();
    start_timer(cobrowsing_info, message_for);
    disable_transfer_chat();
}

function start_timer(cobrowsing_info, message_for) {
    const timer_elem = document.getElementById('livechat_cobrowsing_time');

    update_cobrowse_time(timer_elem, cobrowsing_info);

    if (state.call_timer) {
        clearInterval(state.call_timer);
    }

    state.call_timer = setInterval(() => {
        update_cobrowse_time(timer_elem, cobrowsing_info);
        reset_inactivity_timer(cobrowsing_info.session_id, get_bot_id(), 'customer');
        reset_inactivity_timer(cobrowsing_info.session_id, get_bot_id(), 'agent');
    }, 1000);

    if (state.call_status_timer) {
        clearInterval(state.call_status_timer);
    }

    state.call_status_timer = setInterval(() => {
        check_cobrowsing_status(cobrowsing_info, message_for);
    }, 5000);

}

function update_cobrowse_time(elem, cobrowsing_info) {
    let elapsed_time = Date.parse(new Date()) - localStorage.getItem(`cobrowse_start_time_${cobrowsing_info.meeting_id}`);
    
    elapsed_time = get_time_elapsed(elapsed_time);

    elem.innerHTML = elapsed_time;
}

function check_cobrowsing_status(cobrowsing_info, message_for) {
    const json_string = JSON.stringify({
        id: cobrowsing_info.cobrowse_session_id,
    });

    let encrypted_data = encrypt_variable(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    // const params = JSON.stringify(encrypted_data);
    const config = {
        headers: {
          'X-CSRFToken': getCsrfToken(),
        }
    }

    axios
        .post(`${window.location.protocol}//${window.location.host}/easy-assist/agent/check-cobrowsing-status/`, encrypted_data, config)
        .then((response) => {
            response = response.data;
            response = custom_decrypt(response.Response)
            response = JSON.parse(response);

            if (response.status == 200) {
                if (response.is_archived) {
                    end_cobrowsing_session();
                    append_system_message('Cobrowsing Session Ended', cobrowsing_info.session_id, message_for);

                    const index = cobrowsing_info.guest_requests.findIndex(req => req.session_id == cobrowsing_info.session_id);
                    if (index != -1) cobrowsing_info.guest_requests.splice(index, 1);
                    
                    set_cobrowsing_info({
                        meeting_id: null,
                        session_id: null,
                        status: 'none',
                    })
    
                    set_cobrowsing_status();
                    clearInterval(state.call_status_timer);
                }
            } else {
                console.log('Error occured while checking cobrowsing status. Please check.');
            }
        })
}

function end_cobrowsing_session() {
    const cobrowsing_info = get_cobrowsing_info();

    const json_string = JSON.stringify({
        livechat_session_id: cobrowsing_info.session_id,
        request_type: "completed",
        meeting_id: cobrowsing_info.meeting_id,
    });

    const params = get_params(json_string);
    const config = {
        headers: {
          'X-CSRFToken': getCsrfToken(),
        }
    }

    axios
        .post("/livechat/manage-cobrowsing-request/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if (response.status == 200) {
                console.log('cobrowsing ended successfully');
            } else {
                showToast(response.message, 2000);
            }
        })
        .catch((err) => {
            console.log(err);
        });
}

export async function join_cobrowsing_session() {
    const session_id = get_session_id();
    const cobrowsing_info = get_cobrowsing_info();
    let join_request = cobrowsing_info.guest_requests.filter(request => request.session_id == session_id);

    if (join_request.length == 0) return;

    join_request = join_request[0];

    await add_agent_to_cobrowsing_session(join_request.cobrowse_session_id);

    append_system_message('Cobrowsing Session Started', null, "guest_agent");

    var message = JSON.stringify({
        message: JSON.stringify({
            event_type: "GUEST_AGENT_JOINED_CB",
            session_id: session_id,
            meeting_id: cobrowsing_info.meeting_id,
            guest_agent_name: get_agent_name(),
        }),
        sender: "System",
    });

    send_message_to_guest_agent_socket(message);

    const json_string = JSON.stringify({
        livechat_session_id: session_id,
        request_type: "guest_agent_joined",
        meeting_id: join_request.meeting_id,
        guest_agent_username: get_agent_username(),
    });

    const params = get_params(json_string);
    const config = {
        headers: {
          'X-CSRFToken': getCsrfToken(),
        }
    }

    axios
        .post("/livechat/manage-cobrowsing-request/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if (response.status == 200) {
                console.log('cobrowsing started');

                $(".livechat-cobrowsing-reject-accept-popup-div").hide();
            
                set_cobrowsing_info({
                    meeting_id: join_request.meeting_id,
                    session_id: join_request.session_id,
                    status: 'accepted',
                })
        
                set_cobrowse_session_id(join_request.cobrowse_session_id);
        
                go_to_cobrowsing_page();
                start_cobrowsing_timer("guest_agent");
            
            } else {
                showToast(response.message, 2000);
            }
        })
        .catch((err) => {
            console.log(err);
        });
    
}

function disable_join_button() {
    $('#guest_agent_cobrowse_connect_btn').css('opacity', '0.5');
    $('#guest_agent_cobrowse_connect_btn').tooltip('enable');
}

function enable_join_button() {
    $('#guest_agent_cobrowse_connect_btn').css('opacity', '1');
    $('#guest_agent_cobrowse_connect_btn').tooltip('disable');
}

function add_agent_to_cobrowsing_session (cobrowse_session_id) {
    return new Promise((resolve, reject) => {

        const json_string = JSON.stringify({
            id: cobrowse_session_id,
            support_agents: [window.USER_PK],
        });
    
        let encrypted_data = encrypt_variable(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };
        // const params = JSON.stringify(encrypted_data);
        const config = {
            headers: {
              'X-CSRFToken': getCsrfToken(),
            }
        }
    
        axios
            .post(`${window.location.protocol}//${window.location.host}/easy-assist/agent/share-session/`, encrypted_data, config)
            .then((response) => {
                console.log(response);
                response = response.data;
                response = custom_decrypt(response.Response)
                response = JSON.parse(response);
    
                if (response.status == 200) {
                    resolve();
                } else {
                    console.log('Error occured while checking cobrowsing status. Please check.');
                }
            })
    })
}

export function clear_session_end_timer() {
    if (state.session_end_timer) {
        clearInterval(state.session_end_timer);
    }
}

export function check_cobrowse_agent_exists () {
    const json_string = JSON.stringify({
        id: USER_PK,
    });

    let encrypted_data = encrypt_variable(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    // const params = JSON.stringify(encrypted_data);
    const config = {
        headers: {
          'X-CSRFToken': getCsrfToken(),
        }
    }

    axios
        .post(`${window.location.protocol}//${window.location.host}/easy-assist/check-agent-exists/`, encrypted_data, config)
        .then((response) => {
            response = response.data;
            response = custom_decrypt(response.Response)
            response = JSON.parse(response);

            if (response.status == 200) {
                set_is_eligible_for_cobrowsing(true);
            } else {
                set_is_eligible_for_cobrowsing(false);
            }
        })
}

export function is_cobrowsing_ongoing () {
    const cobrowsing_info = get_cobrowsing_info();

    return cobrowsing_info.session_id == get_session_id() && cobrowsing_info.status == 'ongoing';
}

export function force_end_cobrowsing (show_end_chat_modal=true) {
    const cobrowsing_info = get_cobrowsing_info();

    if (!(cobrowsing_info.session_id == get_session_id() && cobrowsing_info.status == 'ongoing')) return;

    const json_string = JSON.stringify({
        id: cobrowsing_info.cobrowse_session_id,
        comments: "",
        subcomments: "",
    });

    let encrypted_data = encrypt_variable(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    // const params = JSON.stringify(encrypted_data);
    const config = {
        headers: {
          'X-CSRFToken': getCsrfToken(),
        }
    }

    axios
        .post(`${window.location.protocol}//${window.location.host}/easy-assist/agent/close-session/`, encrypted_data, config)
        .then((response) => {
            response = response.data;
            response = custom_decrypt(response.Response)
            response = JSON.parse(response);

            if (response.status == 200) {
                showToast('Cobrowsing Ended Successfully.', 2000);
                $('#end-cobrowse-session').modal('hide');

                if (show_end_chat_modal) {
                    load_resolve_chat_form();
                    $('#end-chat-session').modal('show');
                }
            } else {
                showToast('Failed to end cobrowsing', 2000);
            }
        })

}