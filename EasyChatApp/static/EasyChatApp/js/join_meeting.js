$(document).ready(() => {
    if (window.location.pathname.includes('voice-meeting')) {
        create_websocket_for_voice_call();
        join_meeting();
    }
})

var jitsi_meet_api = null;
var is_chat_socket_open = false;
var chat_socket = null;
var audio_recorder_on = false;
var client_join_time_stamp = null;
var recorder_client = null;

function join_meeting() {
    try{

        // if(my_id == null) {
        //     my_id = unique_id;
        // }
        
        let is_meeting_joined = true;
        var toolbar_options = ['microphone', 'hangup'];

        const display_name = DISPLAY_NAME;

        // if(window.IS_INVITED_AGENT == "True"){
        //     display_name = window.INVITED_AGENT_NAME;
        // }

        const meeting_id = MEETING_ID
        const domain = MEETING_DOMAIN;
        const options = {
            roomName: meeting_id,
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
            parentNode: document.querySelector('#livechat-client-meeting-iframe'),
            userInfo: {
                displayName: display_name
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
        jitsi_meet_api = new JitsiMeetExternalAPI(domain, options);

        // jitsi_meet_api.executeCommand('subject', 'Something');
        jitsi_meet_api.executeCommand('toggleTileView');
        jitsi_meet_api.executeCommand('toggleFilmStrip');

        // Adding event listeners
        add_event_listeners();

        var iframe = jitsi_meet_api.getIFrame();

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

    // jitsi_meet_api.addEventListener("audioMuteStatusChanged",function(e){
    //     is_audio_muted = e["muted"]
    // });

    // jitsi_meet_api.addEventListener("subjectChange", function(e) {
    //     if(e.subject != meeting_subject) {
    //         jitsi_meet_api.executeCommand("subject", meeting_subject);
    //     }
    // });

    // jitsi_meet_api.addEventListener("tileViewChanged", function(e) {
    //     if(e.enabled) {
    //         jitsi_meet_api.executeCommand('toggleTileView');
    //     }
    // });

    jitsi_meet_api.addEventListener("videoConferenceLeft", function(e) {
        console.log('ended');
        // jitsi_meet_api.executeCommand('stopRecording', {mode:'file'})
        // if(window.IS_INVITED_AGENT == "False"){
        //     save_voip_meeting_duration();
        // } else {
        //     redirect_end_meeting_page();
        // }

        redirect_end_meeting_page();
    });
}

function init() {
    jitsi_meet_api.executeCommand('startRecording', {mode:'file'})
    
    if (!audio_recorder_on) {
        client_join_time_stamp = new Date()
        client_join_time_stamp = client_join_time_stamp.getHours() + ':' + client_join_time_stamp.getMinutes() + ':' + client_join_time_stamp.getSeconds()
        
        start_client_audio_voip_record();
    }
}

async function start_client_audio_voip_record() {
    console.log("start audio record");
    
    if (!audio_recorder_on) {
        console.log("Your audio will be recorded for quality and training purposes.")
    }

    if (audio_recorder_on) {

        audio_recorder_on = false;
        recorder_client.stop();
    } else {

        audio_recorder_on = true;
        
        let stream_client;
        try {
            const audioStream_client = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });

            const [audioTrack_client] = audioStream_client.getAudioTracks();

            stream_client = new MediaStream([audioTrack_client]);
        } catch (err) {
            audio_recorder_on = false;
            return;
        }

        recorder_client = new MediaRecorder(stream_client);
        const chunks = [];
        const filename = MEETING_ID + "_client" + '.webm';
        let count = 0;

        function save_data(blob) {
            var file = new File([blob.data], filename, {
                type: 'video/webm'
            });
            var formData = new FormData();
            formData.append("uploaded_data", file);
            formData.append("filename", file.name);
            formData.append("meeting_id", MEETING_ID);
            formData.append("time_stamp",client_join_time_stamp);
           
            $.ajax({
                url: "/livechat/save-client-recorded-data/",
                type: "POST",
                data: formData,
                processData: false,
                contentType: false,
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
        recorder_client.ondataavailable = blob => save_data(blob);
        recorder_client.start(5000);
    }
}


function redirect_end_meeting_page() {
    var message = JSON.stringify({
        message: JSON.stringify({
            type: "text",
            event_type: 'MEET_END',
        }),
        sender: "MEET_END",
    });

    if (is_chat_socket_open && chat_socket != null) {
        chat_socket.send(message);
    }

    window.location = "/chat/customer-meeting-end/";
}

function create_websocket_for_voice_call() {

    if (is_chat_socket_open == false && chat_socket == null) {
        chat_socket = window.location.protocol == "http:" ? "ws://" : "wss://";
        chat_socket += window.location.host + "/ws/" + MEETING_ID + "/client/";
        chat_socket = new WebSocket(chat_socket);

        chat_socket.onmessage = handle_socket_message;
        chat_socket.onclose = close_socket;
        chat_socket.onopen = open_livechat_socket;
        chat_socket.onerror = close_socket;

    }
}

function close_socket(e) {
    is_chat_socket_open = false;
    chat_socket = null;
}

function open_livechat_socket(e) {
    console.log('connection established');
    is_chat_socket_open = true;
}

function handle_socket_message(e) {
    var data = JSON.parse(e.data);
    var message = JSON.parse(data["message"]);
    var sender = data["sender"];

    if (sender == 'MEET_END') {
        end_voip_calling();
    }
}

function end_voip_calling() {
    jitsi_meet_api.executeCommand("hangup");
}

function custom_decrypt(msg_string) {
    var payload = msg_string.split(".");
    var key = payload[0];
    var decrypted_data = payload[1];
    var decrypted = CryptoJS.AES.decrypt(decrypted_data, CryptoJS.enc.Utf8.parse(key), {
        iv: CryptoJS.enc.Base64.parse(payload[2]),
    });
    return decrypted.toString(CryptoJS.enc.Utf8);
}