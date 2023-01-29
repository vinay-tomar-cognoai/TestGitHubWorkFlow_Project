var jitsi_meet_api = null;
var display_name = "";
var is_video_muted = true;
var is_audio_muted = false;
var my_id = null;
var audio_recorder_on = false;
var is_video_on = false;
var is_mic_on = false;
var is_host_connected = false;
var is_interval_set = false;
let recorder, stream, audioTrack, videoTrack, displayStream, audioStream;
let recorder_client, stream_client, audioTrack_client, videoTrack_client, displayStream_client, audioStream_client;
var internet_timer = "";
var is_recording_cancel = false;
var is_first_packet = true;
var is_meeting_joined = false;
var meeting_subject = " ";
var sync_utils_client_websocket = null;
var sync_utils_client_websocket_open = false;
var auto_end_meeting = false;
var voip_meeting_status_interval = null;

// Get CSRF token
function get_csrfmiddlewaretoken() {
    return document.querySelector("input[name=\"csrfmiddlewaretoken\"]").value;
}

function init() {
    if (voip_meeting_status_interval == null) {
        voip_meeting_status_interval = setInterval(check_voip_session_status, 10000);
    }
    jitsi_meet_api.executeCommand('startRecording', {mode:'file'})
    if (audio_recorder_on == false) {
        client_join_time_stamp = new Date()
        client_join_time_stamp = client_join_time_stamp.getHours() + ':' + client_join_time_stamp.getMinutes() + ':' + client_join_time_stamp.getSeconds()
        start_client_audio_voip_record();
    }
}
async function start_client_audio_voip_record() {
    console.log("start audio record");
    if (audio_recorder_on == false) {
        console.log("Your audio will be recorded for quality and training purposes.")
    }
    if (audio_recorder_on) {
        audio_recorder_on = false;
        recorder_client.stop();
    } else {
        audio_recorder_on = true;
        try {
            audioStream_client = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
            [audioTrack_client] = audioStream_client.getAudioTracks();
            stream_client = new MediaStream([audioTrack_client]);
        } catch {
            audio_recorder_on = false;
            return;
        }
        recorder_client = new MediaRecorder(stream_client);
        var filename = my_id + "_agent" + '.webm';

        function save_data(blob) {
            var file = new File([blob.data], filename, {
                type: 'video/webm'
            });
            var formData = new FormData();
            formData.append("uploaded_data", file);
            formData.append("filename", file.name);
            formData.append("meeting_id", meeting_id);
            formData.append("time_stamp",client_join_time_stamp);

            $.ajax({
                url: "/easy-assist/save-client-recorded-data/",
                type: "POST",
                data: formData,
                processData: false,
                contentType: false,
                headers: {
                    'X-CSRFToken': get_csrfmiddlewaretoken()
                },
                success: function(response) {
                    response = easyassist_custom_decrypt(response.Response);
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

function join_meeting() {

    try{
        if(my_id == null) {
            my_id = unique_id;
        }
        is_meeting_joined = true;
        var toolbar_options = ['microphone', 'hangup', 'tileview'];

        display_name = agent_name;
        if(window.IS_INVITED_AGENT == "True"){
            display_name = window.INVITED_AGENT_NAME;
        }

        domain = meeting_host_url;
        options = {
            roomName: meeting_id,
            configOverwrite: {
                startWithVideoMuted: is_video_muted,
                startWithAudioMuted: is_audio_muted,
                disableDeepLinking: true,
                remoteVideoMenu: {
                    disableKick: true,
                },
                disableProfile: true,
                enableNoisyMicDetection: false,
                enableNoAudioDetection: true,
            },
            parentNode: document.querySelector('#cobrowse-agent-meeting-iframe'),
            userInfo: {
                displayName: display_name
            },
            interfaceConfigOverwrite: {
                MOBILE_APP_PROMO: false,
                TOOLBAR_BUTTONS: toolbar_options,
                DEFAULT_BACKGROUND: meet_background_color,
                DISABLE_JOIN_LEAVE_NOTIFICATIONS: true,
                CONNECTION_INDICATOR_DISABLED: true,
                VIDEO_QUALITY_LABEL_DISABLED: true,
                DISABLE_PRESENCE_STATUS: true,
            },
            tileViewEnabled: true,
        };
        jitsi_meet_api = new JitsiMeetExternalAPI(domain, options);

        jitsi_meet_api.executeCommand('subject', meeting_subject);
        jitsi_meet_api.executeCommand('toggleTileView');
        jitsi_meet_api.executeCommand('toggleFilmStrip');

        // Adding event listeners
        add_event_listeners();

        iframe = jitsi_meet_api.getIFrame();

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

    // Event notifications about video mute status changes.

    jitsi_meet_api.addEventListener("audioMuteStatusChanged",function(e){
        is_audio_muted = e["muted"]
    });

    jitsi_meet_api.addEventListener("subjectChange", function(e) {
        if(e.subject != meeting_subject) {
            jitsi_meet_api.executeCommand("subject", meeting_subject);
        }
    });

    // jitsi_meet_api.addEventListener("tileViewChanged", function(e) {
    //     if(e.enabled) {
    //         jitsi_meet_api.executeCommand('toggleTileView');
    //     }
    // });

    jitsi_meet_api.addEventListener("videoConferenceLeft", function(e) {
        set_easyassist_cookie("is_cobrowse_meeting_active", "");
        set_easyassist_cookie("is_meeting_initiate_by_customer", "");
        clear_voip_meeting_status_interval();
        jitsi_meet_api.executeCommand('stopRecording', {mode:'file'})
        if(window.IS_INVITED_AGENT == "False"){
            save_voip_meeting_duration();
        } else {
            send_invited_agent_disconnect_message_over_socket();
            setTimeout(() => {
                redirect_end_meeting_page();
            }, 1000);
        }
    });
}

function redirect_end_meeting_page() {
    window.location = "/easy-assist/voip-meeting-ended/agent/" + meeting_id;
}

window.onload = function() {
	join_meeting();
    create_sync_utils_easyassist_socket(meeting_id, socket_message_sender);

    set_easyassist_current_session_local_storage_obj("is_voice_meeting_tab_open", "true");

    window.addEventListener('beforeunload', function(event) {
        set_easyassist_current_session_local_storage_obj("is_voice_meeting_tab_open", "false");
    });

    window.addEventListener('unload', function(event) {
        set_easyassist_current_session_local_storage_obj("is_voice_meeting_tab_open", "false");
    });
}

function end_voip_calling() {
    jitsi_meet_api.executeCommand("hangup");
    set_easyassist_cookie("is_cobrowse_meeting_active", "");
    set_easyassist_cookie("is_meeting_initiate_by_customer", "");
    clear_voip_meeting_status_interval();
}

function clear_voip_meeting_status_interval() {
    if (voip_meeting_status_interval != null) {
        clearInterval(voip_meeting_status_interval);
        voip_meeting_status_interval = null;
    }
}

function save_voip_meeting_duration() {

    easyassit_send_meeting_ended_over_socket();

    request_params = {
        "meeting_id": meeting_id,
    };

    json_params = JSON.stringify(request_params);

    encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST",  window.location.protocol + "//" + window.location.host + "/easy-assist/save-voip-meeting-duration/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            redirect_end_meeting_page();
        }
    }
    xhttp.send(params);
}


function check_voip_session_status() {

    var request_params = {
        "meeting_id": meeting_id,
    };

    json_params = JSON.stringify(request_params);

    encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST",  window.location.protocol + "//" + window.location.host + "/easy-assist/voip-meeting-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                if(response["is_session_closed"]) {
                    end_voip_calling();
                }
            }
        }
    }
    xhttp.send(params);
}

function create_sync_utils_easyassist_socket(jid, sender) {

    jid = "sync_utils_" + jid;
    ws_scheme = window.location.protocol == "http:" ? "ws" : "wss";
    url = ws_scheme + '://' + window.location.host + '/ws/cobrowse/sync-utils/' + jid + '/' + sender + "/";
    if (sync_utils_client_websocket == null) {
        sync_utils_client_websocket = new WebSocket(url);
        sync_utils_client_websocket.onmessage = easyassist_socket_message_handler;
        sync_utils_client_websocket.onerror = function(e){
                console.error("WebSocket error observed:", e);
                sync_utils_client_websocket_open = false;
                easyassist_close_sync_utils_socket();
            }
        sync_utils_client_websocket.onopen = function(){
                console.log("sync_utils_client_websocket created successfully") 
                sync_utils_client_websocket_open = true;
            }
        sync_utils_client_websocket.onclose = function() {
                sync_utils_client_websocket_open = false;
                sync_utils_client_websocket = null;
            }
    }
}

function close_sync_utils_easyassist_socket() {

    if(sync_utils_client_websocket == null) {
        return;
    }

    try {

        sync_utils_client_websocket.close();

    } catch(err) {

        sync_utils_client_websocket.onmessage = null;
        sync_utils_client_websocket = null;
    }
}

function send_message_over_sync_utils_easyassist_socket(message, sender) {
    try {

        if(sync_utils_client_websocket_open == false || sync_utils_client_websocket == null){
            if(send_message_over_sync_utils_easyassist_socket.caller.name == "easyassist_socket_callee"){
                return;
            }
            setTimeout(function easyassist_socket_callee(){
                send_message_over_sync_utils_easyassist_socket(message, sender);
            }, 5000);
            console.log("sync_utils_client_websocket is not open");
            return;
        }

        if (sync_utils_client_websocket_open == true && sync_utils_client_websocket != null) {
            sync_utils_client_websocket.send(JSON.stringify({
                "message": {
                    "header": {
                        "sender": sender
                    },
                    "body": message
                }
            }));
        }
    } catch(err) {
        console.error("ERROR : send_message_over_sync_utils_easyassist_socket ", err);
    }
}

function easyassist_socket_message_handler(e) {
    var data = JSON.parse(e.data);
    message = data.message;
    try {
        client_packet = message.body.Request;
    } catch(err){
        console.log("Please look at this report this to developer ", message)
    }

    if (message.body.is_encrypted == false) {
        client_packet = JSON.parse(client_packet);
    } else {
        client_packet = easyassist_custom_decrypt(client_packet);
        client_packet = JSON.parse(client_packet);
    }

    var message_sender = "client";
    if(ENABLE_REVERSE_COBROWSING == "True") {
        message_sender = "agent";
    }

    if (message.header.sender == message_sender) {
        if (client_packet.type == "end_voip_meeting") {
            auto_end_meeting = true;
            setTimeout(function() {
                end_voip_calling();
            }, 3000);
        } else if (client_packet.type == "end_session") {
            auto_end_meeting = true;
            setTimeout(function() {
                end_voip_calling();
            }, 3000);
        }
    } else if (window.IS_INVITED_AGENT == "True" && message.header.sender == "agent") {
        if (client_packet.type == "end_voip_meeting") {
            // auto_end_meeting = true;
            setTimeout(function() {
                end_voip_calling();
            }, 3000);
        } else if (client_packet.type == "end_session") {
            auto_end_meeting = true;
            setTimeout(function() {
                end_voip_calling();
            }, 3000);
        }
    } else if (window.IS_INVITED_AGENT == "True" && message.header.sender == "client" && ENABLE_REVERSE_COBROWSING == "True") {
        if (client_packet.type == "end_voip_meeting") {
            // auto_end_meeting = true;
            setTimeout(function() {
                // STORAGE SOLN REV
                // set_easyassist_current_session_local_storage_obj("is_cobrowse_meeting_active", "");
                end_voip_calling();
            }, 3000);
        } else if (client_packet.type == "end_session") {
            auto_end_meeting = true;
            setTimeout(function() {
                // STORAGE SOLN REV
                // set_easyassist_current_session_local_storage_obj("is_cobrowse_meeting_active", "");
                end_voip_calling();
            }, 3000);
        }
    }
}

function easyassit_send_meeting_ended_over_socket(status) {
    if(auto_end_meeting) {
        return;
    }

    json_string = JSON.stringify({
        "type": "end_voip_meeting",
        "agent_name": window.agent_name,
        "auto_end_meeting": false,
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, socket_message_sender);
}

function send_invited_agent_disconnect_message_over_socket() {
    json_string = JSON.stringify({
        "type": "invited_agent_disconnected",
        "invited_agent_name": window.INVITED_AGENT_NAME,
        "agent_username": window.INVITED_AGENT_USERNAME
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, socket_message_sender);
}

function set_easyassist_cookie(cookiename, cookievalue) {

    var domain = window.location.hostname;
    var max_age = 24 * 60 * 60;

    if (window.location.protocol == "https:") {
        document.cookie = cookiename + "=" + cookievalue + ";max-age=" + max_age + ";path=/;domain=" + domain + ";secure";
    } else {
        document.cookie = cookiename + "=" + cookievalue + ";max-age=" + max_age + ";path=/;";
    }
}

function set_easyassist_current_session_local_storage_obj(key, value) {
    try{
        let local_storage_obj = localStorage.getItem("easyassist_session");
        let easyassist_session_id = meeting_id;

        if(local_storage_obj) {
            local_storage_obj = JSON.parse(local_storage_obj);
            local_storage_obj[easyassist_session_id][key] = value;
            localStorage.setItem("easyassist_session", JSON.stringify(local_storage_obj));
        }
    }catch(err){
        console.log("ERROR: set_easyassist_current_session_local_storage_obj ", err);
    }
}