var jitsi_meet_api = null;
var display_name = "";
var is_video_muted = true;
var is_audio_muted = false;
var my_id = null;
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
var audio_recorder_on = false;

function detect_mobile() {
    if (/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|ipad|iris|kindle|Android|Silk|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(navigator.userAgent) ||
        /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(navigator.userAgent.substr(0, 4))) {
        return true;
    }
    return false;
}

function uuidv4() {

    return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
        (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
}

// Get CSRF token
function get_csrfmiddlewaretoken() {
    return document.querySelector("input[name=\"csrfmiddlewaretoken\"]").value;
}

function init() {
    jitsi_meet_api.executeCommand('startRecording', {mode:'file'});
    if (audio_recorder_on == false) {
        client_join_time_stamp = new Date();
        client_join_time_stamp = client_join_time_stamp.getHours() + ':' + client_join_time_stamp.getMinutes() + ':' + client_join_time_stamp.getSeconds();
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
        var filename = my_id + "_client" + '.webm';

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
        var toolbar_options = [];

        display_name = client_name;
        let domain = meeting_host_url;
        let options = {
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
                prejoinPageEnabled: false
            },
            parentNode: document.querySelector('#cobrowse-client-meeting-iframe'),
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

        let iframe = jitsi_meet_api.getIFrame();

        try {
            iframe.onload = function() {
                parent.postMessage("voip_meeting_ready", '*');
                setTimeout(init, 5000);
            }
        } catch(err) { 
            console.log(err);
        }
    }catch(err){
        console.log(err);
        send_voip_error_to_parent(611);
    }
}

function add_event_listeners() {

    // Event notifications about video mute status changes.
    jitsi_meet_api.addEventListener("videoMuteStatusChanged", function(e) {
        is_video_muted = e["muted"]
    });

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

    jitsi_meet_api.addEventListener("audioMuteStatusChanged", function(e) {
        send_voice_mute_status_to_parent(e.muted);
    });

    jitsi_meet_api.addEventListener("videoMuteStatusChanged", function(e) {
        send_video_mute_status_to_parent(e.muted);
    });

    jitsi_meet_api.addEventListener("cameraError", function(e) {
        send_voip_error_to_parent(612);
    });

    jitsi_meet_api.addEventListener("micError", function(e) {
        send_voip_error_to_parent(613);
    });
}

function send_voip_error_to_parent(error_code) {
    var data = {
        "event": "voip_function_error",
        "error_code": error_code,
    }
    parent.postMessage(data, '*');
}

function send_voice_mute_status_to_parent(is_muted) {
    var data = {
        "event": "voip_audio_status",
        "is_muted": is_muted,
    }
    parent.postMessage(data, '*');
}

function send_video_mute_status_to_parent(is_muted) {
    var data = {
        "event": "voip_video_status",
        "is_muted": is_muted,
    }
    parent.postMessage(data, '*');
}

window.onload = function() {
    join_meeting();
}

function toggle_client_voice(status) {
    is_audio_muted = !status;
    jitsi_meet_api.executeCommand('toggleAudio');
}

function toggle_client_video(status) {
    is_video_muted = !status;
    jitsi_meet_api.executeCommand('toggleVideo');
}

function end_cobrowse_video_meet() {
    jitsi_meet_api.executeCommand('hangup');
    parent.postMessage("voip_meeting_ended", '*');
}

window.addEventListener('message', handle_parent_message, false);

function handle_parent_message(event) {
    let data = JSON.parse(event.data);

    if(data.message == "toggle_voice") {
        toggle_client_voice(data.status);
    } else if(data.message == "toggle_video") {
        toggle_client_video(data.status);
    } else if(data.message == "end_meeting") {
        end_cobrowse_video_meet();
    }
}
