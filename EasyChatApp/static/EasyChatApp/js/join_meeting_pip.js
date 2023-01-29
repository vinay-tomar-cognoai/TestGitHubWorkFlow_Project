
var jitsi_meet_api = null;
var MEETING_ID = null;
var MEETING_SESSION_ID = null;
var DISPLAY_NAME = null;

function join_meeting_over_pip(meeting_id, session_id, display_name) {
    try{
        MEETING_ID = meeting_id;
        MEETING_SESSION_ID = session_id;
        DISPLAY_NAME = display_name;

        var toolbar_options = ['microphone', 'hangup'];

        const domain = MEETING_DOMAIN;

        const options = {
            roomName: MEETING_ID,
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
                displayName: DISPLAY_NAME
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

        // state.jitsi_meet_api.executeCommand('subject', 'Something');
        jitsi_meet_api.executeCommand('toggleTileView');
        jitsi_meet_api.executeCommand('toggleFilmStrip');

        add_event_listeners();

    } catch(err) {
        console.log(err);
    }
}

function add_event_listeners() {
    jitsi_meet_api.addEventListener("videoConferenceLeft", function(e) {
        end_meeting();
    });
}

function end_meeting() {
    $('#voice_call_div').hide();
    handle_meet_end(MEETING_ID);
    send_notification_to_agent("", "", "", "MEET_END");
}

function toggle_audio(current_state, next_state) {
    jitsi_meet_api.executeCommand('toggleAudio');
    
    $('.voice-call-' + current_state + '-icon').toggle();
    $('.voice-call-' + next_state + '-icon').toggle();
}

function unmute_audio () {
    $('.voice-call-mute-icon').hide();
    $('.voice-call-unmute-icon').show();
}

function end_pip_calling() {
    if (jitsi_meet_api) {
        jitsi_meet_api.executeCommand("hangup");
    }
}
