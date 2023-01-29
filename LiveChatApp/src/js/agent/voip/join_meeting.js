import axios from 'axios';
import {custom_decrypt, get_params} from '../../utils'
import { getCsrfToken, showToast } from '../console';

const state = {
    jitsi_meet_api: null,
    meeting_id: null,
    session_id: null,
    display_name: "",
    audio_recorder_on: false,
    client_join_time_stamp: null,
    recorder_client: null,
    socket: {
        is_open: false,
        instance: null,
    }
}

$(document).ready(() => {
    if (window.location.pathname.includes('voice-meeting')) {

        state.meeting_id = window.MEETING_ID;
        state.session_id = window.SESSION_ID;
        state.display_name = window.DISPLAY_NAME;

        create_websocket_for_voice_call();
        join_meeting();

        setInterval(() => {
            check_chat_report_status();
        }, 5000);
    }
})

export function join_meeting() {
    try{

        // if(my_id == null) {
        //     my_id = unique_id;
        // }
        
        let is_meeting_joined = true;
        var toolbar_options = ['microphone', 'hangup'];

        // if(window.IS_INVITED_AGENT == "True"){
        //     display_name = window.INVITED_AGENT_NAME;
        // }

        const domain = MEETING_DOMAIN;

        const options = {
            roomName: state.meeting_id,
            configOverwrite: {
                startWithVideoMuted: true,
                startWithAudioMuted: false,
                disableDeepLinking: true,
                remoteVideoMenu: {
                    disableKick: true,
                },
                disableProfile: true,
                enableNoisyMicDetection: false,
                enableNoAudioDetection: true,
            },
            parentNode: document.querySelector('#livechat-agent-meeting-iframe'),
            userInfo: {
                displayName: state.display_name
            },
            interfaceConfigOverwrite: {
                MOBILE_APP_PROMO: false,
                TOOLBAR_BUTTONS: toolbar_options,
                DEFAULT_BACKGROUND: 'black',
                DISABLE_JOIN_LEAVE_NOTIFICATIONS: true,
                CONNECTION_INDICATOR_DISABLED: true,
                VIDEO_QUALITY_LABEL_DISABLED: true,
                DISABLE_PRESENCE_STATUS: true,
            },
            tileViewEnabled: true,
        };
        state.jitsi_meet_api = new JitsiMeetExternalAPI(domain, options);

        // state.jitsi_meet_api.executeCommand('subject', 'Something');
        state.jitsi_meet_api.executeCommand('toggleTileView');
        state.jitsi_meet_api.executeCommand('toggleFilmStrip');

        // Adding event listeners
        add_event_listeners();

        const iframe = state.jitsi_meet_api.getIFrame();

        try {
            iframe.onload = function() {
                setTimeout(init, 5000);
            }
        } catch(err) { 
            console.log(err);
        }

    } catch(err) {
        console.log(err);
    }
}

function add_event_listeners() {

    console.log('added events');
    // Event notifications about video mute status changes.

    // state.jitsi_meet_api.addEventListener("audioMuteStatusChanged",function(e){
    //     is_audio_muted = e["muted"]
    // });

    // state.jitsi_meet_api.addEventListener("subjectChange", function(e) {
    //     if(e.subject != meeting_subject) {
    //         state.jitsi_meet_api.executeCommand("subject", meeting_subject);
    //     }
    // });

    // state.jitsi_meet_api.addEventListener("tileViewChanged", function(e) {
    //     if(e.enabled) {
    //         state.jitsi_meet_api.executeCommand('toggleTileView');
    //     }
    // });

    state.jitsi_meet_api.addEventListener("videoConferenceLeft", function(e) {
        state.jitsi_meet_api.executeCommand('stopRecording', {mode:'file'});

        // if(window.IS_INVITED_AGENT == "False"){
        //     save_voip_meeting_duration();
        // } else {
        //     redirect_end_meeting_page();
        // }

        save_voip_meeting_duration();
    });
}

function save_voip_meeting_duration () {
    const json_string = JSON.stringify({
        meeting_id: state.meeting_id,
    });

    const params = get_params(json_string);

    axios
        .post("/livechat/save-meeting-duration/", params)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if (response.status == 200) {
                console.log('duration saved');
                
                var message = JSON.stringify({
                    message: JSON.stringify({
                        type: "text",
                        event_type: 'MEET_END',
                    }),
                    sender: "MEET_END",
                });

                state.socket.instance.send(message);
        
                redirect_end_meeting_page();
            } else {
                showToast(response.message, 2000);
            }
        })
        .catch((err) => {
            console.log(err);
        });

}

function redirect_end_meeting_page() {
    window.location = "/livechat/agent-meeting-end/";
}

function init() {
    state.jitsi_meet_api.executeCommand('startRecording', {mode:'file'})
    
    if (!state.audio_recorder_on) {
        state.client_join_time_stamp = new Date()
        state.client_join_time_stamp = state.client_join_time_stamp.getHours() + ':' + state.client_join_time_stamp.getMinutes() + ':' + state.client_join_time_stamp.getSeconds()
        
        start_client_audio_voip_record();
    }
}

async function start_client_audio_voip_record() {
    console.log("start audio record");
    
    if (!state.audio_recorder_on) {
        console.log("Your audio will be recorded for quality and training purposes.")
    }

    if (state.audio_recorder_on) {

        state.audio_recorder_on = false;
        state.recorder_client.stop();
    } else {

        state.audio_recorder_on = true;
        
        let stream_client;
        try {
            const audioStream_client = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });

            const [audioTrack_client] = audioStream_client.getAudioTracks();

            stream_client = new MediaStream([audioTrack_client]);
        } catch (err) {
            state.audio_recorder_on = false;
            return;
        }

        state.recorder_client = new MediaRecorder(stream_client);
        const chunks = [];
        const filename = state.meeting_id + "_agent" + '.webm';
        let count = 0;

        function save_data(blob) {
            var file = new File([blob.data], filename, {
                type: 'video/webm'
            });
            var formData = new FormData();
            formData.append("uploaded_data", file);
            formData.append("filename", file.name);
            formData.append("meeting_id", state.meeting_id);
            formData.append("time_stamp",state.client_join_time_stamp);

            $.ajax({
                url: "/livechat/save-client-recorded-data/",
                type: "POST",
                data: formData,
                processData: false,
                contentType: false,
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                },
                success: function(response) {
                    console.log(response);
                    response = custom_decrypt(response);
                    response = JSON.parse(response);
                    if (response["status"] == 200) {
                        console.log("Audio saved.")
                    } else {
                        console.log("error")
                    }
                },
                error: function(xhr, textstatus, errorthrown) {
                    console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
                }
            });

        }
        state.recorder_client.ondataavailable = blob => save_data(blob);
        state.recorder_client.start(5000);
    }
}

function end_voip_calling() {
    state.jitsi_meet_api.executeCommand("hangup");
}

function create_websocket_for_voice_call() {
    const chat_socket = state.socket;

    if (chat_socket.is_open == false && chat_socket.instance == null) {
        chat_socket.instance = window.location.protocol == "http:" ? "ws://" : "wss://";
        chat_socket.instance += window.location.host + "/ws/" + state.meeting_id + "/agent/";
        chat_socket.instance = new WebSocket(chat_socket.instance);

        chat_socket.instance.onmessage = handle_socket_message;
        chat_socket.instance.onclose = close_socket;
        chat_socket.instance.onopen = open_livechat_socket;
        chat_socket.instance.onerror = close_socket;

    }
}

function close_socket(e) {
    state.socket.is_open = false;
    state.socket.instance = null;
}

function open_livechat_socket(e) {
    console.log('connection established');
    state.socket.is_open = true;
}

function handle_socket_message(e) {
    var data = JSON.parse(e.data);
    var message = JSON.parse(data["message"]);
    var sender = data["sender"];

    if (sender == 'MEET_END') {
        end_voip_calling();
    }
}

function check_chat_report_status() {

    let meeting_id = state.meeting_id;

    if(!meeting_id) return;

    let json_string = {
        meeting_id: meeting_id,
    };

    json_string = JSON.stringify(json_string);
    const params = get_params(json_string);

    axios
        .post("/livechat/check-chat-report-status/", params)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if(response.status == 200) {
                if(response.is_chat_reported) end_voip_calling();
            }
        })       
        .catch((err) => {
            console.log(err);
        });
}