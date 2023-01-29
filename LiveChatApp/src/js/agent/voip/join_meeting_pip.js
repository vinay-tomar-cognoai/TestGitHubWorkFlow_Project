import axios from "axios";
import { custom_decrypt, get_params } from "../../utils";
import { showToast } from "../console";
import { handle_meeting_end, send_meet_end_notification } from "./voip";

const state = {
    jitsi_meet_api: null,
    meeting_id: null,
    session_id: null,
    display_name: "",
}

export function join_meeting(meeting_id, session_id, display_name) {
    try{
        state.meeting_id = meeting_id;
        state.session_id = session_id;
        state.display_name = display_name;
        
        var toolbar_options = ['microphone', 'hangup'];

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
            parentNode: document.querySelector('#meet_container'),
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
        state.jitsi_meet_api = new JitsiMeetExternalAPI(domain, options);

        // state.jitsi_meet_api.executeCommand('subject', 'Something');
        state.jitsi_meet_api.executeCommand('toggleTileView');
        state.jitsi_meet_api.executeCommand('toggleFilmStrip');

        add_event_listeners();

    } catch(err) {
        console.log(err);
    }
}

function add_event_listeners() {
    state.jitsi_meet_api.addEventListener("videoConferenceLeft", function(e) {
        save_voip_meeting_duration();
    });
}

export function toggle_audio() {
    state.jitsi_meet_api.executeCommand('toggleAudio');
    $('.livechat-VOIP-call-unmute-button').toggleClass('livechat-VOIP-call-mute-button');
}

export function unmute_audio() {
    $('.livechat-VOIP-call-unmute-button').removeClass('livechat-VOIP-call-mute-button');
}

export function end_voip_calling() {
    if (state.jitsi_meet_api) {
        state.jitsi_meet_api.executeCommand("hangup");
    }
}

function save_voip_meeting_duration () {

    $('#livechat_VOIP_call_screen_draggable').hide();

    send_meet_end_notification();
    handle_meeting_end();

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
            } else {
                showToast(response.message, 2000);
            }
        })
        .catch((err) => {
            console.log(err);
        });
}