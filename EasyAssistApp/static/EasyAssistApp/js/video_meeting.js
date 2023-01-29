var jitsi_meet_api = null;
var save_notes_timer = null;
var display_name = "";
var chat_history = [];
var chat_history_timer = null;
var is_video_muted = true;
var is_audio_muted = true;
var screen_recorder_on = false;
var audio_recorder_on = false;
var room_id = null;
var sender = null;
var client_websocket = null;
var client_websocket_open = false;
var is_message_sender = false;
var participant_ids = []
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
var latitude = null;
var longitude = null;
var options = null;
var file_attachment_name = null;
var is_meeting_interval_set = false; 
var client_join_time_stamp = null;
var show_time_notification = false;
var participant_location_detail_obj = {};
var my_current_location = null;
var meeting_subject = "Meeting";
var display_media_available = false;
var update_meeting_end_interval = null;
var EASYASSIST_FUNCTION_FAIL_DEFAULT_CODE = 500;
var EASYASSIST_FUNCTION_FAIL_DEFAULT_MESSAGE = "Due to some network issue, we are unable to process your request. Please Refresh the page.";
var easyassist_function_fail_time = 0;
var easyassist_function_fail_count = 0;
const regEmail = /^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/;
var ongoing_meeting_status_interval = null;
var initial_customer_waiting_message = "Please wait, the meeting host will let you in soon.";
var no_agent_connect_timer_interval = null;
var sync_utils_client_websocket = null;
var sync_utils_client_websocket_open = false;
window.socket_message_sender = "";
socket_type = null;
agent_disconnected_meet = false;

function detect_mobile() {
    if (/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|ipad|iris|kindle|Android|Silk|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(navigator.userAgent) ||
        /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(navigator.userAgent.substr(0, 4))) {
        return true;
    }
    return false;
}


function show_toast(message) {

    document.getElementById("toast_message").innerHTML = message
    $('.toast').toast('show');
}
// Generate random UUID
function uuidv4() {

    return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
        (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
}

// Get CSRF token
function get_csrfmiddlewaretoken() {
    return document.querySelector("input[name=\"csrfmiddlewaretoken\"]").value;
}

function start_with_audio_muted(value) {
    is_audio_muted = !value;
    is_audio_on = value;
    capture_user_audio(value);
}

function start_with_video_muted(value) {
    is_video_muted = !value;
    is_video_on = value;
    capture_user_video(value);
}

function capture_user_video(value) {
    const constraints = {
      video: true,
    };

    const video = document.getElementById("cogno-lobby-video-element");
    if(value == true) {
        navigator.mediaDevices.getUserMedia(constraints)
        .then((stream) => {
          video.srcObject = stream;
          document.getElementById("cogno-lobby-avatar").style.opacity = '0';
          video.style.background = 'initial';
        })
        .catch(function() {
            show_toast("Please allow camera")
            video.style.background = '';
            document.getElementById("cogno-lobby-avatar").style.opacity = '1'; 
            document.getElementById("video-on-icon").style.display = 'none';
            document.getElementById("video-off-icon").style.display = 'flex';
            document.getElementById("toggle-video").checked = false;
        });
        document.getElementById("video-off-icon").style.display = 'none';
        document.getElementById("video-on-icon").style.display = 'flex';
    } else {
        video.srcObject = null;
        video.style.background = '';
        document.getElementById("cogno-lobby-avatar").style.opacity = '1';
        document.getElementById("video-on-icon").style.display = 'none';
        document.getElementById("video-off-icon").style.display = 'flex';
    }
}

function capture_user_audio(value) {
    const constraints = {
      audio: true,
    };

    if(value == true) {
        navigator.mediaDevices.getUserMedia(constraints)
        .catch(function() {
            show_toast("Please allow microphone")
            document.getElementById("mic-on-icon").style.display = 'none';
            document.getElementById("mic-off-icon").style.display = 'flex';
            document.getElementById("toggle-mic").checked = false;
        });
        document.getElementById("mic-off-icon").style.display = 'none';
        document.getElementById("mic-on-icon").style.display = 'flex';
    } else {
        document.getElementById("mic-on-icon").style.display = 'none';
        document.getElementById("mic-off-icon").style.display = 'flex';
    }
}

function toggle_join_meeting_music(element, play_music) {
    if(play_music) {
        toggle_background_music(true);
        document.getElementById("cogno-lobby-music-unmute-btn").style.display = 'none';
        document.getElementById("cogno-lobby-music-mute-btn").style.display = 'block';
    } else {
        toggle_background_music(false);
        document.getElementById("cogno-lobby-music-mute-btn").style.display = 'none';
        document.getElementById("cogno-lobby-music-unmute-btn").style.display = 'block';
    }
}

function get_cookie(cookiename) {
    var cookie_name = cookiename + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var cookie_array = decodedCookie.split(';');
    for(let i = 0; i < cookie_array.length; i++) {
        var c = cookie_array[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(cookie_name) == 0) {
            return c.substring(cookie_name.length, c.length);
        }
    }
    return "";
}

function set_cookie(cookiename, cookievalue, path = "") {
    var domain = window.location.hostname.substring(window.location.host.indexOf(".") + 1);

    if(window.location.hostname.split(".").length==2 || window.location.hostname == "127.0.0.1"){
        domain = window.location.hostname;
    }

    if (path == "") {
        document.cookie = cookiename + "=" + cookievalue + ";domain=" + domain;
    } else {
        document.cookie = cookiename + "=" + cookievalue + ";path=" + path + ";domain=" + domain;
    }
}

// Scroll chat to bottom
function scroll_to_bottom() {
    var objDiv = document.getElementById("chat_room_container");
    objDiv.scrollTop = objDiv.scrollHeight;
    setTimeout(function() {
        objDiv.scrollTop = objDiv.scrollHeight;
    }, 1000);
}

function hide_all_meeting_options() {
    if(document.getElementById("hide-add-members")) {
        document.getElementById("hide-add-members").style.display = 'none';
        document.getElementById("show-add-members").style.display = 'block';
        document.getElementById("cogno-lobby-add-members").style.display = 'none';
    }

    if(document.getElementById("hide-meeting-notes")) {
        document.getElementById("hide-meeting-notes").style.display = 'none';
        document.getElementById("show-meeting-notes").style.display = 'block';
        document.getElementById("cogno-lobby-agent-notes").style.display = 'none';
    }

    if(document.getElementById("hide-ask-for-support")) {
        document.getElementById("hide-ask-for-support").style.display = 'none';
        document.getElementById("show-ask-for-support").style.display = 'block';
        document.getElementById("cogno-lobby-ask-for-support").style.display = 'none';
    }

    if(document.getElementById("hide-meeting-forms")) {
        document.getElementById("hide-meeting-forms").style.display = 'none';
        document.getElementById("show-meeting-forms").style.display = 'block';
        document.getElementById("cogno-lobby-meeting-forms").style.display = 'none';
    }

    if(document.getElementById("hide-meeting-support-doc")) {
        document.getElementById("show-meeting-support-doc").style.display = 'block';
        document.getElementById("hide-meeting-support-doc").style.display = 'none';
            document.getElementById("cogno-lobby-meeting-doc").style.display = 'none';
    }

    document.getElementById("hide-meeting-chatbox").style.display = 'none';
    document.getElementById("show-meeting-chatbox").style.display = 'block';
    document.getElementById("cogno-lobby-meeting-chat").style.display = 'none';
    hide_option_backdrop();
}

function show_option_backdrop() {
    document.getElementById("cogno-lobby-option-backdrop").style.display = 'block';
}

function hide_option_backdrop() {
    document.getElementById("cogno-lobby-option-backdrop").style.display = 'none';
}

function show_meeting_chat_box(el) {
    hide_all_meeting_options();
    document.getElementById("cogno-lobby-meeting-chat").style.display = 'block';
    document.getElementById("show-meeting-chatbox").style.display = 'none';
    document.getElementById("hide-meeting-chatbox").style.display = 'block';

    document.getElementById("meeting_text_message").focus();
    document.getElementById("meeting_text_message").select();
    show_option_backdrop();
    scroll_to_bottom();
}

function hide_meeting_chat_box(el) {
    if(window.innerWidth > 600) {
        hide_all_meeting_options();
    }
}

function show_meeting_notes(el) {
    hide_all_meeting_options();

    document.getElementById("hide-meeting-notes").style.display = 'block';
    document.getElementById("show-meeting-notes").style.display = 'none';
    document.getElementById("cogno-lobby-agent-notes").style.display = 'block';

    document.getElementById("agent-notes").focus();
    show_option_backdrop();
}

function hide_meeting_notes(el) {
    if(window.innerWidth >= 600) {
        hide_all_meeting_options();
    }
}

function show_meeting_support_docs(el) {
    hide_all_meeting_options();

    document.getElementById("cogno-lobby-meeting-doc").style.display = 'block';
    document.getElementById("show-meeting-support-doc").style.display = 'none';
    document.getElementById("hide-meeting-support-doc").style.display = 'block';

    show_option_backdrop();
    get_list_of_support_documents();
}

function hide_meeting_support_docs(el) {
    if(window.innerWidth >= 600) {
        hide_all_meeting_options();
    }
}

function show_add_members(el) {
    hide_all_meeting_options();
    document.getElementById("show-add-members").style.display = 'none';
    document.getElementById("hide-add-members").style.display = 'block';
    document.getElementById("cogno-lobby-add-members").style.display = 'block';
    let error_message_element = document.getElementById("invite-people-mail-error");
    if (error_message_element) {
        error_message_element.style.display = 'none';
    }

    get_list_of_participants();
    show_option_backdrop();
}

function hide_add_members(el) {
    if(window.innerWidth >= 600) {
        hide_all_meeting_options();
    }
}

function show_ask_for_support() {
    hide_all_meeting_options();

    document.getElementById("show-ask-for-support").style.display = 'none';
    document.getElementById("hide-ask-for-support").style.display = 'block';
    document.getElementById("cogno-lobby-ask-for-support").style.display = 'block';

    get_list_of_support_agents();
    show_option_backdrop();
}

function hide_ask_for_support() {
    if(window.innerWidth >= 600) {
        hide_all_meeting_options();
    }
}

function show_meeting_forms() {
    hide_all_meeting_options();

    document.getElementById("show-meeting-forms").style.display = 'none';
    document.getElementById("hide-meeting-forms").style.display = 'block';
    document.getElementById("cogno-lobby-meeting-forms").style.display = 'block';

    get_list_of_meeting_forms();
    show_option_backdrop();
}

function hide_meeting_forms() {
    if(window.innerWidth >= 600) {
        hide_all_meeting_options();
    }
}

function show_cogno_lobby_options(){
    if(document.getElementById("cogno-lobby-options").querySelector(".cogno-lobby-options-sm").children.length > 0){
        document.getElementById("cogno-lobby-options").style.display = 'block';
        document.querySelector("#cobrowse-meeting-iframe").style.width = "";
    } else {
        document.querySelector("#cobrowse-meeting-iframe").style.width = "100%";
    }
}

function hide_cogno_lobby_options(){
    document.getElementById("cogno-lobby-options").style.display = 'none';
}

function show_small_device_options() {
    show_cogno_lobby_options();
    document.getElementById("show-small-device-btn").style.display = 'none';
    document.getElementById("hide-small-device-btn").style.display = 'block';

    if(is_agent == 'True') {
        $('#show-add-members button').click();
    } else {
        $('#show-meeting-chatbox button').click();
    }
}

function hide_small_device_options() {
    hide_cogno_lobby_options();
    document.getElementById("hide-small-device-btn").style.display = 'none';
    document.getElementById("show-small-device-btn").style.display = 'block';

    hide_all_meeting_options();
}

function show_media_unavailable_modal(type) {

    if(type == 'camera') {
        document.getElementById("media-unavailable-modal-label").innerHTML = "Can't find your camera";
        document.getElementById("media-unavailable-modal-text").innerHTML = "\
            Check your system setting to make sure that a camera is \
            available. If not, plug one in. You might then need to resart your browser.";
    } else if(type == 'microphone') {
        document.getElementById("media-unavailable-modal-label").innerHTML = "Can't find your microphone";
        document.getElementById("media-unavailable-modal-text").innerHTML = "\
            Check your system setting to make sure that a microphone is \
            available. If not, plug one in. You might then need to resart your browser.";
    }

    $('#media-unavailable-modal').modal('show');
}

function show_member_location_info(participant_id) {
    if(is_agent == 'True') {
        for(let idx = 0; idx < participant_ids.length; idx++) {
            if (participant_id == participant_ids[idx]["id"]) {
                document.getElementById("cogno-lobby-participant-name").innerHTML = participant_ids[idx]["participant_name"];
                if(participant_id in participant_location_detail_obj) {
                    var participant_location = participant_location_detail_obj[participant_id]['location'];
                    if(participant_location == "None" || participant_location == null) {
                        document.getElementById("cogno-lobby-participant-address").innerHTML = "Location not found";
                    } else {
                        document.getElementById("cogno-lobby-participant-address").innerHTML = participant_location;
                    }
                } else {
                    document.getElementById("cogno-lobby-participant-address").innerHTML = "Location not found";
                }
            }
        }
        $('#cogno-lobby-member-info').modal('show');
        $('.modal-backdrop').appendTo('#cogno-lobby-add-members .cogno-lobby-options-section-body');
        $('body').removeClass("modal-open")
        $('body').css("padding-right","");

        $('#cogno-lobby-member-info').on('hidden.bs.modal', function(){
            $('.modal-backdrop').remove();
        });
    }
}

function check_meeting_ended_or_not(){
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
    xhttp.open("POST", "/easy-assist/check-meeting-ended-or-not/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                window.location.reload()
            }
            else if(response.status == 301){
                if(show_time_notification == false){
                    show_toast("This session will end in 5 minutes.");
                    show_time_notification = true;
                }
            }
        }
    }
    xhttp.send(params);

}

function check_meeting_recording_enabled() {
    if(window.enable_meeting_recording == "True") {
        return true;
    }

    return false;
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

function init() {
    set_easyassist_cookie("is_cobrowse_meeting_active", meeting_id);
    if(is_agent == 'True' && is_invited_agent == 'False'){
        if(check_meeting_recording_enabled()) {
            jitsi_meet_api.executeCommand('startRecording', {mode:'file'})
        }
    }

    internet_timer = setInterval(function() {
        check_internet_every_ten_sec();
    }, 10000)

    if( is_cobrowsing_active == 'False'){
        if(allow_meeting_end_time == 'True'){
            if (is_meeting_interval_set == false) {
                    setInterval(function() {
                        check_meeting_ended_or_not();
                    }, 30000)
                is_meeting_interval_set = true;
            }
        }
    } else {
        if (ongoing_meeting_status_interval == null) {
            ongoing_meeting_status_interval = setInterval(check_voip_session_status, 10000);
        }
    }

    if (is_agent == 'True') {
        if (screen_recorder_on == false) {
            //start_recording();
        }
        let local_storage_obj = get_easyassist_current_session_local_storage_obj();
        if(local_storage_obj != null && local_storage_obj.hasOwnProperty('client_waiting_socket') && local_storage_obj.client_waiting_socket) { 
            data = JSON.parse(local_storage_obj.client_waiting_socket)
            let id = data["id"];
            let name = data["name"];                
            show_request_modal(id, name);
        }
    } else {
        toggle_background_music(false);
        // save customer's location
        if (window.navigator.geolocation) {
            var geolocation_options = {
                enableHighAccuracy: true,
                timeout: 15000,
                maximumAge: 0
            };
            window.navigator.geolocation.getCurrentPosition(accept_location_request, cancel_location_request, geolocation_options);
        }

        if (audio_recorder_on == false) {
            client_join_time_stamp = new Date()
            client_join_time_stamp = client_join_time_stamp.getHours() + ':' + client_join_time_stamp.getMinutes() + ':' + client_join_time_stamp.getSeconds()
            start_client_audio_record();
        }
    }
}

function get_list_of_participants() {
    var html = "";
    for(let idx = 0; idx < participant_ids.length; idx++) {
        if (my_id == participant_ids[idx]["id"]) {
            html += [
                '<div class="col-12 pt-3">',
                    '<div class="row">',
                        '<div class="col-12" style="text-overflow: ellipsis; overflow: hidden; padding-top: 0.375em;">',
                            participant_ids[idx]['participant_name'],
                        '</div>',
                    '</div>',
                '</div>'
            ].join('');
        } else {
            var participant_id = participant_ids[idx]['id'];
            html += [
                '<div class="col-12 pt-3" id="agent-' + participant_ids[idx]['id'] + '">',
                    '<div class="row">',
                        '<div class="col-10" style="text-overflow: ellipsis; overflow: hidden; padding-top: 0.375em;">',
                            participant_ids[idx]['participant_name'],
            ].join('');
            
            if(participant_id in participant_location_detail_obj) {
                if(participant_location_detail_obj[participant_id]['is_agent'] == 'False') {
                    html += [
                        '<span class="cogno-lobby-member-info" onclick="show_member_location_info(\'' + participant_ids[idx]['id'] + '\');">',
                            '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-top: -2px;">',
                                '<path d="M6.00031 0C2.68611 0 3.25568e-08 2.68611 3.25568e-08 5.99969C-8.20546e-05 6.78768 0.155065 7.56798 0.456579 8.29601C0.758094 9.02403 1.20007 9.68554 1.75727 10.2427C2.31446 10.7999 2.97597 11.2419 3.70399 11.5434C4.43202 11.8449 5.21232 12.0001 6.00031 12C9.31326 12 12 9.31389 12 5.99969C12 2.68611 9.31326 0 6.00031 0ZM6.56028 2.16614C7.14525 2.16614 7.31712 2.50549 7.31712 2.8936C7.31712 3.37795 6.92964 3.82605 6.2678 3.82605C5.71408 3.82605 5.45034 3.54794 5.46659 3.08734C5.46659 2.69923 5.79095 2.16614 6.56028 2.16614ZM5.06161 9.59325C4.66163 9.59325 4.36977 9.35014 4.64913 8.28457L5.10723 6.39404C5.1866 6.09156 5.19973 5.97031 5.10723 5.97031C4.98787 5.97031 4.46852 6.17905 4.16228 6.38529L3.96292 6.05843C4.93474 5.2466 6.05218 4.77038 6.53028 4.77038C6.93026 4.77038 6.99651 5.24285 6.79715 5.97031L6.27217 7.95771C6.17905 8.30894 6.21905 8.43019 6.31217 8.43019C6.43216 8.43019 6.82464 8.28519 7.21087 7.98083L7.43711 8.28457C6.49154 9.22952 5.46097 9.59325 5.06161 9.59325Z" fill="#4D4D4D"/>',
                            '</svg>',
                        '</span>',
                    ].join('')

                }
            }
            if(participant_ids[idx]["is_audio_muted"]) {
                html += [
                            '</div>',
                            '<div class="col-2">',
                                '<div class="action-btn-container">',
                                    '<button class="cogno-lobby-action-btn" type="button" id="cogno-lobby-unmute-member-btn-' + participant_ids[idx]['id'] + '">',
                                        '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                            '<path d="M1.02428 0.175739C0.789965 -0.0585763 0.410062 -0.0585801 0.175742 0.17573C-0.0585774 0.410041 -0.0585812 0.789937 0.175734 1.02425L4.80005 5.64858V7.99994C4.80005 9.76724 6.23276 11.1999 8.00009 11.1999C8.66687 11.1999 9.28602 10.996 9.79857 10.6471L10.7153 11.5638C10.0142 12.0889 9.14345 12.3999 8.20009 12.3999H7.80009L7.62696 12.3964C5.38762 12.3056 3.60004 10.4615 3.60004 8.19994V7.79994L3.59456 7.71853C3.55483 7.42567 3.30379 7.19995 3.00003 7.19995C2.66866 7.19995 2.40003 7.46857 2.40003 7.79994V8.19994L2.40328 8.38901C2.4983 11.1504 4.66664 13.3852 7.4001 13.5853L7.40008 15.3999L7.40556 15.4813C7.44529 15.7742 7.69633 15.9999 8.00009 15.9999C8.33146 15.9999 8.6001 15.7313 8.6001 15.3999L8.60088 13.5853C9.72007 13.5031 10.7445 13.0799 11.5706 12.4191L14.9757 15.8243C15.21 16.0586 15.5899 16.0586 15.8243 15.8243C16.0586 15.59 16.0586 15.2101 15.8243 14.9757L1.02428 0.175739ZM8.9251 9.77363C8.64847 9.91818 8.33383 9.99993 8.00009 9.99993C6.89551 9.99993 6.00007 9.1045 6.00007 7.99994V6.84859L8.9251 9.77363Z" fill="#757575"/>',
                                            '<path d="M10.0001 3.19998V7.4545L11.1442 8.59861C11.1809 8.40468 11.2001 8.20455 11.2001 7.99994V3.19998C11.2001 1.43268 9.76742 2.84798e-08 8.00009 2.84798e-08C6.52178 2.84798e-08 5.2776 1.00241 4.9102 2.36458L6.00007 3.45445V3.19998C6.00007 2.09542 6.89551 1.19999 8.00009 1.19999C9.10467 1.19999 10.0001 2.09542 10.0001 3.19998Z" fill="#757575"/>',
                                            '<path d="M12.1571 9.61145L13.0738 10.5282C13.4112 9.82323 13.6002 9.03365 13.6002 8.19994V7.79994L13.5947 7.71853C13.5549 7.42567 13.3039 7.19995 13.0001 7.19995C12.6688 7.19995 12.4001 7.46857 12.4001 7.79994V8.19994L12.3966 8.37306C12.3791 8.80596 12.296 9.22197 12.1571 9.61145Z" fill="#757575"/>',
                                        '</svg>',
                                    '</button>',
                                    '<button class="cogno-lobby-action-btn" type="button" id="cogno-lobby-mute-member-btn-' + participant_ids[idx]['id'] + '" onclick="mute_participant(this, \'' + participant_ids[idx]['id'] + '\')" style="display: none;" data-toggle="tooltip" title="Turn off microphone">',
                                        '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                            '<path d="M5.5 0C3.79137 0 2.40625 1.17526 2.40625 2.62501V7.2917C2.40625 8.74146 3.79137 9.91672 5.5 9.91672C7.20863 9.91672 8.59375 8.74146 8.59375 7.2917V2.62501C8.59375 1.17526 7.20863 0 5.5 0ZM3.4375 2.62501C3.4375 1.65851 4.36091 0.875004 5.5 0.875004C6.63909 0.875004 7.5625 1.65851 7.5625 2.62501V7.2917C7.5625 8.25821 6.63909 9.04171 5.5 9.04171C4.36091 9.04171 3.4375 8.25821 3.4375 7.2917V2.62501Z" fill="#757575"/>',
                                            '<path d="M1.03125 6.85449C1.03125 6.61286 0.800397 6.41698 0.515625 6.41698C0.230853 6.41698 0 6.6131 0 6.85473V7.29165C0 9.72146 2.18859 11.7175 4.98438 11.9381V13.5625C4.98438 13.8041 5.21523 14 5.5 14C5.78477 14 6.01563 13.8041 6.01563 13.5625V11.9381C8.81141 11.7175 11 9.72146 11 7.29165V6.8545C11 6.61287 10.7691 6.41699 10.4844 6.41699C10.1996 6.41699 9.96875 6.61301 9.96875 6.85464V7.29165C9.96875 9.38575 7.96802 11.0833 5.5 11.0833C3.03198 11.0833 1.03125 9.3855 1.03125 7.29141V6.85449Z" fill="#757575"/>',
                                        '</svg>',
                                    '</button>',
                                    '<button class="cogno-lobby-action-btn" type="button" onclick="show_kick_participant_modal(this, \'' + participant_ids[idx]['id'] + '\')" title="Remove User" data-toggle="tooltip">',
                                        '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                            '<path d="M9 0C4 0 0 4 0 9C0 14 4 18 9 18C14 18 18 14 18 9C18 4 14 0 9 0ZM9 16C5.1 16 2 12.9 2 9C2 5.1 5.1 2 9 2C12.9 2 16 5.1 16 9C16 12.9 12.9 16 9 16ZM5 8V10H13V8H5Z" fill="#F53131"/>',
                                        '</svg>',
                                    '</button>',
                                '</div>',
                            '</div>',
                        '</div>',
                    '</div>'
                ].join('');
            } else {
                html += [
                        '</div>',
                            '<div class="col-2">',
                                '<div class="action-btn-container">',
                                    '<button class="cogno-lobby-action-btn" type="button" id="cogno-lobby-unmute-member-btn-' + participant_ids[idx]['id'] + '" style="display: none;">',
                                        '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                            '<path d="M1.02428 0.175739C0.789965 -0.0585763 0.410062 -0.0585801 0.175742 0.17573C-0.0585774 0.410041 -0.0585812 0.789937 0.175734 1.02425L4.80005 5.64858V7.99994C4.80005 9.76724 6.23276 11.1999 8.00009 11.1999C8.66687 11.1999 9.28602 10.996 9.79857 10.6471L10.7153 11.5638C10.0142 12.0889 9.14345 12.3999 8.20009 12.3999H7.80009L7.62696 12.3964C5.38762 12.3056 3.60004 10.4615 3.60004 8.19994V7.79994L3.59456 7.71853C3.55483 7.42567 3.30379 7.19995 3.00003 7.19995C2.66866 7.19995 2.40003 7.46857 2.40003 7.79994V8.19994L2.40328 8.38901C2.4983 11.1504 4.66664 13.3852 7.4001 13.5853L7.40008 15.3999L7.40556 15.4813C7.44529 15.7742 7.69633 15.9999 8.00009 15.9999C8.33146 15.9999 8.6001 15.7313 8.6001 15.3999L8.60088 13.5853C9.72007 13.5031 10.7445 13.0799 11.5706 12.4191L14.9757 15.8243C15.21 16.0586 15.5899 16.0586 15.8243 15.8243C16.0586 15.59 16.0586 15.2101 15.8243 14.9757L1.02428 0.175739ZM8.9251 9.77363C8.64847 9.91818 8.33383 9.99993 8.00009 9.99993C6.89551 9.99993 6.00007 9.1045 6.00007 7.99994V6.84859L8.9251 9.77363Z" fill="#757575"/>',
                                            '<path d="M10.0001 3.19998V7.4545L11.1442 8.59861C11.1809 8.40468 11.2001 8.20455 11.2001 7.99994V3.19998C11.2001 1.43268 9.76742 2.84798e-08 8.00009 2.84798e-08C6.52178 2.84798e-08 5.2776 1.00241 4.9102 2.36458L6.00007 3.45445V3.19998C6.00007 2.09542 6.89551 1.19999 8.00009 1.19999C9.10467 1.19999 10.0001 2.09542 10.0001 3.19998Z" fill="#757575"/>',
                                            '<path d="M12.1571 9.61145L13.0738 10.5282C13.4112 9.82323 13.6002 9.03365 13.6002 8.19994V7.79994L13.5947 7.71853C13.5549 7.42567 13.3039 7.19995 13.0001 7.19995C12.6688 7.19995 12.4001 7.46857 12.4001 7.79994V8.19994L12.3966 8.37306C12.3791 8.80596 12.296 9.22197 12.1571 9.61145Z" fill="#757575"/>',
                                        '</svg>',
                                    '</button>',
                                    '<button class="cogno-lobby-action-btn" type="button" id="cogno-lobby-mute-member-btn-' + participant_ids[idx]['id'] + '" onclick="mute_participant(this, \'' + participant_ids[idx]['id'] + '\')" data-toggle="tooltip" title="Turn off microphone">',
                                        '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                            '<path d="M5.5 0C3.79137 0 2.40625 1.17526 2.40625 2.62501V7.2917C2.40625 8.74146 3.79137 9.91672 5.5 9.91672C7.20863 9.91672 8.59375 8.74146 8.59375 7.2917V2.62501C8.59375 1.17526 7.20863 0 5.5 0ZM3.4375 2.62501C3.4375 1.65851 4.36091 0.875004 5.5 0.875004C6.63909 0.875004 7.5625 1.65851 7.5625 2.62501V7.2917C7.5625 8.25821 6.63909 9.04171 5.5 9.04171C4.36091 9.04171 3.4375 8.25821 3.4375 7.2917V2.62501Z" fill="#757575"/>',
                                            '<path d="M1.03125 6.85449C1.03125 6.61286 0.800397 6.41698 0.515625 6.41698C0.230853 6.41698 0 6.6131 0 6.85473V7.29165C0 9.72146 2.18859 11.7175 4.98438 11.9381V13.5625C4.98438 13.8041 5.21523 14 5.5 14C5.78477 14 6.01563 13.8041 6.01563 13.5625V11.9381C8.81141 11.7175 11 9.72146 11 7.29165V6.8545C11 6.61287 10.7691 6.41699 10.4844 6.41699C10.1996 6.41699 9.96875 6.61301 9.96875 6.85464V7.29165C9.96875 9.38575 7.96802 11.0833 5.5 11.0833C3.03198 11.0833 1.03125 9.3855 1.03125 7.29141V6.85449Z" fill="#757575"/>',
                                        '</svg>',
                                    '</button>',
                                    '<button class="cogno-lobby-action-btn" type="button" onclick="show_kick_participant_modal(this, \'' + participant_ids[idx]['id'] + '\')" title="Remove User" data-toggle="tooltip">',
                                        '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                            '<path d="M9 0C4 0 0 4 0 9C0 14 4 18 9 18C14 18 18 14 18 9C18 4 14 0 9 0ZM9 16C5.1 16 2 12.9 2 9C2 5.1 5.1 2 9 2C12.9 2 16 5.1 16 9C16 12.9 12.9 16 9 16ZM5 8V10H13V8H5Z" fill="#F53131"/>',
                                        '</svg>',
                                    '</button>',
                                '</div>',
                            '</div>',
                        '</div>',
                    '</div>'
                ].join('');
            }
        }
    }
    document.getElementById("cogno-lobby-members-list").innerHTML = html;
    $('[data-toggle="tooltip"]').tooltip({
        trigger: 'hover'
    });
}

function show_kick_participant_modal(el, participant_id) {
    var participant_name  = "";
    for(index = 0; index < participant_ids.length; index ++) {
        if(participant_ids[index]['id'] == participant_id) {
            participant_name = participant_ids[index]['participant_name'];
            break;
        }
    }
    $('#kick-participant-modal').find('.modal-title').html("Remove " + participant_name + " from the meeting?");
    document.getElementById("kick-participant-btn").setAttribute('onclick', "kick_participant(this, \'" + participant_id + "\')");
    $('#kick-participant-modal').modal('show');
}

function kick_participant(o, id) {

    setTimeout(function() {
        document.getElementById("agent-" + id).remove();
        $('#kick-participant-modal').modal('hide');
    }, 500);
    kick_participant_socket(id)
}

function mute_participant(o, id) {
    mute_participant_socket(id);
}

function mute_meeting_audio() {
    if(is_audio_muted == false) {
        jitsi_meet_api.executeCommand('toggleAudio');
    }
}

function show_meeting_form_to_agent(el, form_id) {
    var url = window.location.protocol + "//" + window.location.host + "/easy-assist/cobrowse-data-collect/" + meeting_id + "/" + form_id + "/";
    window.open(url);
}

// Adding jitsi event listeners
function add_event_listeners() {

    // Event notifications fired when the local user has left the video conference
    jitsi_meet_api.addEventListener("videoConferenceLeft", function(e) {
        if(is_invited_agent == "False") {
            easyassist_send_meeting_ended_over_socket();
        } else if (is_invited_agent == "True") {
            send_invited_agent_disconnect_message_over_socket();
        }
        if(is_invited_agent == "False" && is_agent == "False") {
            easyassist_send_clear_meeting_cookie_over_socket();
        }
        set_easyassist_cookie("is_cobrowse_meeting_active", "");
        set_easyassist_cookie("is_meeting_initiate_by_customer", "");
        clear_ongoing_meeting_status_interval();
        remove_participants_socket(my_id)
        try {
            if(update_meeting_end_interval != null) {
                clearInterval(update_meeting_end_interval)
            }
        } catch(err) { console.log(err) }

        // stop_recording();
        if(is_agent == 'True' && is_invited_agent == 'False'){
            jitsi_meet_api.executeCommand('stopRecording', {mode:'file'})
        }
        if (is_agent == "True") {
            if (is_cobrowsing_active == 'True') {
                window.location = "/easy-assist/meeting-ended/" + meeting_id + "?is_meeting_cobrowsing=true"
            } else {
                save_meeting_duration();
            }
            update_agent_join_status('false')
        } else {
            // stop_client_audio_record();
            if (is_cobrowsing_active == 'True') {
                if(allow_meeting_feedback == 'True' && is_invited_agent == 'False'){
                    window.location = "/easy-assist/meeting-ended/" + meeting_id + "?is_meeting_cobrowsing=true&is_feedback=true&type=" + socket_type + "&agent_disconnected_meet=" + agent_disconnected_meet;
                }else{
                    window.location = "/easy-assist/meeting-ended/" + meeting_id + "?is_meeting_cobrowsing=true&is_feedback=false&type=" + socket_type + "&agent_disconnected_meet=" + agent_disconnected_meet;
                }
            } else {
                if(allow_meeting_feedback == 'True' && is_invited_agent == 'False'){
                    window.location = "/easy-assist/meeting-ended/" + meeting_id + "?is_feedback=true&type=" + socket_type + "&agent_disconnected_meet=" + agent_disconnected_meet;
                }
                else{
                    window.location = "/easy-assist/meeting-ended/" + meeting_id + "?is_feedback=false&type=" + socket_type + "&agent_disconnected_meet=" + agent_disconnected_meet;
                }
            }
        }
    });

    // Event notifications about video mute status changes.
    jitsi_meet_api.addEventListener("videoMuteStatusChanged", function(e) {
        is_video_muted = e["muted"]
    });

    jitsi_meet_api.addEventListener("participantJoined", function(e) {
        update_participants(participant_ids)
        if(is_agent == 'False') {
            send_location_to_agent_over_socket(my_current_location);
        }
    });

    // Receives event notifications about turning on/off the local user screen sharing.
    jitsi_meet_api.addEventListener("screenSharingStatusChanged", function(e) {
        is_screen_share = e["on"]
        if (is_screen_share == true) {
            if (is_video_muted == false) {
                jitsi_meet_api.executeCommand('toggleVideo');
            }
        }
    });

    // Event listener for display name change
    jitsi_meet_api.addEventListener("displayNameChange", function(e) {
        if(jitsi_meet_api._myUserID == e['id']) {
            display_name = stripHTML(e.displayname);
            display_name = remove_all_special_characters_from_str(display_name);
            update_display_name_socket();
        }
    });

    jitsi_meet_api.addEventListener("audioMuteStatusChanged",function(e){
        is_audio_muted = e["muted"]
        try {
            if(is_audio_muted == true){
                stream.getAudioTracks()[0].enabled = false;
            }
            else{
                stream.getAudioTracks()[0].enabled = true;
            }
        } catch(err) {}
        send_participant_mute_status_over_socket(is_audio_muted);
    });

    jitsi_meet_api.addEventListener("subjectChange", function(e) {
        if(e.subject != meeting_subject) {
            jitsi_meet_api.executeCommand("subject", meeting_subject);
        }
    });

    jitsi_meet_api.addEventListener("cameraError", function(e) {
        easyassist_show_function_fail_modal(612);
    });

    jitsi_meet_api.addEventListener("micError", function(e) {
        easyassist_show_function_fail_modal(613);
    });
}

window.onresize = function(e) {
    var width = e.target.innerWidth;

    if (width >= 600) {
        if(is_meeting_joined) {
            if(document.getElementById("cogno-lobby-options").style.display != 'block') {
                if(document.getElementById("hide-small-device-btn").style.display != 'none') {
                    $('#hide-small-device-btn button').click();
                    document.getElementById("show-option-btn-sm").style.display = 'none';
                    show_cogno_lobby_options();
                }
            }
        }
    } else {
        if(is_meeting_joined) {
            if(document.getElementById("show-option-btn-sm").style.display != 'block') {
                hide_all_meeting_options();
                hide_cogno_lobby_options();
                document.getElementById("show-option-btn-sm").style.display = 'block';
            }
        }
    }
}

window.onload = function(){
    easyassist_create_local_storage_obj();
    if(is_cobrowsing_active == 'True'){
        if(show_cobrowsing_meeting_lobby == 'False'){
            is_video_on = true;
            is_mic_on = false;
            is_video_muted = false;
            is_audio_muted = true;
            join_meeting();
        }
    }
    
    set_easyassist_current_session_local_storage_obj("is_video_meeting_tab_open", "true", false);

    window.addEventListener('beforeunload', function(event) {
        set_easyassist_current_session_local_storage_obj("is_video_meeting_tab_open", "false", false);
        set_easyassist_cookie("is_cobrowse_meeting_active", "");
    });

    window.addEventListener('unload', function(event) {
        set_easyassist_current_session_local_storage_obj("is_video_meeting_tab_open", "false", false);
        set_easyassist_cookie("is_cobrowse_meeting_active", "");
    });
}

function join_meeting() {

    try{
        if(my_id == null) {
            my_id = unique_id;
        }
        is_meeting_joined = true;
        var toolbar_options = [
                    'microphone', 'camera', 'closedcaptions', 'desktop', 'fullscreen',
                    'fodeviceselection', 'hangup', 'profile', 'etherpad', 'settings',
                    'videoquality', 'stats', 'tileview',
                    'e2ee'
                ]

        var is_mobile = detect_mobile();
        if(is_mobile == true){
            toolbar_options = [
                    'microphone', 'camera', 'closedcaptions', 'fullscreen',
                    'fodeviceselection', 'hangup', 'profile', 'etherpad', 'settings',
                    'videoquality', 'stats', 'tileview',
                    'e2ee'
                ]
        }

        // Enable chat functionality
        // enable_chat_socket();

        document.getElementById("meeting-lobby").style.display = "none"
        if(is_customer_countdown_timer_enabled()) {
            document.getElementById("easyassist-customer-waiting-timer-div").style.visibility = "hidden";
            document.getElementById("meeting-msg").innerHTML = "Joining the meeting please wait..."
        } else {
            document.getElementById("meeting-msg").innerHTML = "<h2>Joining the meeting please wait...</h2>"
        }
        if (is_agent == 'True' || is_invited_agent == 'True') {
            display_name = agent_name
        } else {
            display_name = client_name
        }
        var participant = { "participant_name": display_name, "id": my_id, "is_audio_muted": is_audio_muted }
        participant_ids.push(participant)
        domain = meeting_host_url;

        options = {
            roomName: meeting_id,
            configOverwrite: {
                startWithVideoMuted: is_video_muted,
                startWithAudioMuted: is_audio_muted,
                disableDeepLinking: true,
                remoteVideoMenu: {
                    disableKick: true,
                }
            },
            parentNode: document.querySelector('#cobrowse-meeting-iframe'),
            userInfo: {
                displayName: display_name
            },
            interfaceConfigOverwrite: {
                MOBILE_APP_PROMO: false,
                TOOLBAR_BUTTONS: toolbar_options,
                DEFAULT_BACKGROUND: meet_background_color,
                DISABLE_JOIN_LEAVE_NOTIFICATIONS: false,
            }
        };

        if(jitsi_api_id != "None" && jitsi_jwt != "None") {
            options["roomName"] = jitsi_api_id + "/" + meeting_id;
            options["jwt"] = jitsi_jwt;
        }

        jitsi_meet_api = new JitsiMeetExternalAPI(domain, options);

        jitsi_meet_api.executeCommand('subject', meeting_subject);

        if (is_cobrowsing_active == "False") {
            jitsi_meet_api.executeCommand('toggleTileView');
        }

        // Adding event listeners
        add_event_listeners();

        iframe = jitsi_meet_api.getIFrame();

        iframe.onload = function(){
            document.getElementById("meeting-lobby-container").style.display = "none";
            var width = window.innerWidth;
            if (width >= 600) {
                document.getElementById("show-option-btn-sm").style.display = "none";
                show_cogno_lobby_options();
            } else {
                hide_cogno_lobby_options();
                document.getElementById("show-option-btn-sm").style.display = "block";
            }

            if(is_agent == "True" || is_invited_agent == "True") {
                // capture_display_stream();
                update_meeting_end_time();
                update_meeting_end_interval = setInterval(update_meeting_end_time, 30000);
            }
            setTimeout(function(){
                init()
            },5000);
        }
     
        // load older chats
        get_client_agent_chats();
 
    }catch(err){
        console.error(err);
        easyassist_show_function_fail_modal(code=611);
    }
}

function check_agent_connected_or_not() {
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
    xhttp.open("POST", "/easy-assist/check-agent-connected-or-not/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                if (response.is_agent_connected == true) {
                    clearInterval(is_host_connected)
                    setTimeout(function() {
                        send_request_to_agent_socket(my_id);
                    }, 2000)
                } else {
                    if (is_interval_set == false) {
                        is_host_connected = setInterval(function() {
                            check_agent_connected_or_not();
                        }, 3000)
                        is_interval_set = true;
                    }
                }
            }
        }
    }
    xhttp.send(params);
}

function update_agent_join_status(status) {
    request_params = {
        "meeting_id": meeting_id,
        "status": status
    };
    json_params = JSON.stringify(request_params);

    encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/update-agent-join-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                console.log("Agent joined the meeting")
            }
        }
    }
    xhttp.send(params);
}


// Join meeting room
function join_room() {
    my_id = unique_id
    // enable_chat_socket();
    if (is_agent == 'True') {
        update_agent_join_status('true');
        join_meeting();
        // if(is_cobrowsing_active == 'True'){
        //     join_meeting();
        // }else{
        //     join_meeting();
        // }
    }else if(is_invited_agent == 'True'){
            join_meeting();
    } else {
        client_name = display_name;
        toggle_background_music(true);
        document.getElementById("meeting-lobby").style.display = "none";
        initiate_customer_countdown_timer();
        check_agent_connected_or_not();
    }
}

function initiate_customer_countdown_timer() {

    if(is_customer_countdown_timer_enabled() && !is_reverse_cobrowsing_enabled()) {

        document.getElementById("meeting-lobby-container").classList.add("cogno-lobby-container-waiting-timer");
        document.getElementsByClassName("cogno-lobby")[0].classList.add("cogno-lobby-waiting-timer");
        document.getElementById("meeting-msg").parentElement.classList.add("toast-text-container");
        document.getElementById("meeting-msg").classList.add("meeting-msg-waiting-timer");

        var local_storage_obj = get_easyassist_current_session_local_storage_obj();
        if(local_storage_obj != null && local_storage_obj.hasOwnProperty("easyassist_meeting_timer_value")) {
            easyassist_start_agent_wait_timer(parseInt(local_storage_obj["easyassist_meeting_timer_value"]));
        } else {
            easyassist_start_agent_wait_timer(window.no_agent_connects_meeting_toast_threshold * 60);
        }

        if(local_storage_obj != null && local_storage_obj.hasOwnProperty("easyassist_meeting_initial_timer_exhausted") && 
            local_storage_obj["easyassist_meeting_initial_timer_exhausted"] == "true") {
            document.getElementById("meeting-msg").innerHTML =  window.no_agent_connects_meeting_toast_text;
        } else {
            document.getElementById("meeting-msg").innerHTML =  initial_customer_waiting_message;
        }
        
        document.getElementById("easyassist-customer-waiting-timer-div").style.display = "flex";
    } else {
        document.getElementById("meeting-msg").innerHTML = "<h2>" + initial_customer_waiting_message + "</h2>";
    }
}

function reset_easyassist_meeting_countdown_timer() {
    set_easyassist_current_session_local_storage_obj("easyassist_meeting_initial_timer_exhausted", "false");
    let initial_timer_value = window.no_agent_connects_meeting_toast_threshold * 60;
    initial_timer_value = initial_timer_value.toString();
    set_easyassist_current_session_local_storage_obj("easyassist_meeting_timer_value", initial_timer_value);
    clear_no_agent_connect_timer_interval();
}

function easyassist_start_agent_wait_timer(waiting_time_seconds) {

    function update_agent_wait_timer() {
        try {
            if(waiting_time_seconds == 0) {
                // restart timer
                set_easyassist_current_session_local_storage_obj("easyassist_meeting_initial_timer_exhausted", "true");
                document.getElementById("meeting-msg").innerHTML = window.no_agent_connects_meeting_toast_text;
                easyassist_start_agent_wait_timer(window.no_agent_connects_meeting_toast_threshold * 60);
            }

            if(waiting_time_seconds <= 15) {
                document.getElementById("easyassist-customer-waiting-timer-div").style.color = "#E53E3E";
            } else {
                document.getElementById("easyassist-customer-waiting-timer-div").style.color = "#25B139";
            }

            document.getElementById("customer-waiting-time-value").innerHTML = waiting_time_seconds;
            waiting_time_seconds = waiting_time_seconds - 1;
            set_easyassist_current_session_local_storage_obj("easyassist_meeting_timer_value", waiting_time_seconds);
        } catch(err) {
            console.log("easyassist_start_agent_wait_timer: ", err);
        }
    }

    clear_no_agent_connect_timer_interval();

    update_agent_wait_timer();
    no_agent_connect_timer_interval = setInterval(function() {
        update_agent_wait_timer();
    }, 1000);
}

function is_customer_countdown_timer_enabled() {
    if(enable_no_agent_connects_toast_meeting == true || enable_no_agent_connects_toast_meeting == "True") {
        return true;
    }
    return false;
}

function is_reverse_cobrowsing_enabled() {
    if(window.IS_REVERSE_COBROWSING_ENABLED == true || window.IS_REVERSE_COBROWSING_ENABLED == "True") {
        return true;
    }
    return false;
}

function clear_no_agent_connect_timer_interval() {
    if(no_agent_connect_timer_interval != null) {
        clearInterval(no_agent_connect_timer_interval);
        no_agent_connect_timer_interval = null;
    }
}

// Save meeting duration.
function save_meeting_duration() {
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
    xhttp.open("POST", "/easy-assist/save-meeting-duration/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                window.location = "/easy-assist/sales-ai/sales-meetings/";
            }
        }
    }
    xhttp.send(params);
}


// Save meeting duration.
function save_meeting_chats() {
    request_params = {
        "meeting_id": meeting_id,
        "chat_history": chat_history
    };

    json_params = JSON.stringify(request_params);

    encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/save-meeting-chats/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
        }
    }
    xhttp.send(params);
}

// check display username
function check_meeting_username() {
    if (is_agent == 'True' || is_invited_agent == 'True') {
        join_room();
    } else {
        error_message_element = document.getElementById("authenticate-details-error");
        error_message_element.innerHTML = "";
        display_name = document.getElementById("display-name").value.trim();
        display_name = stripHTML(display_name);
        display_name = remove_all_special_characters_from_str(display_name);
        var regName = /^[a-zA-Z]+[a-zA-Z ]+$/;
        if (!regName.test(display_name)) {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Please enter a valid name";
            return;
        }
        join_room();
    }
}

// Check meeting password and display username
function check_meeting_username_and_password(meeting_id) {
    if (is_agent == 'False' && is_invited_agent == 'False') {
        error_message_element = document.getElementById("authenticate-details-error");
        error_message_element.innerHTML = "";
        display_name = document.getElementById("display-name").value.trim();
        display_name = stripHTML(display_name);
        display_name = remove_all_special_characters_from_str(display_name);
        var regName = /^[a-zA-Z]+[a-zA-Z ]+$/;
        if (!regName.test(display_name)) {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Please enter a valid name";
            return;
        }
    }

    error_message_element = document.getElementById("authenticate-details-error");
    error_message_element.innerHTML = "";

    var password = document.getElementById("meeting-password").value;
    password = stripHTML(password);

    if (password == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a password.";
        return;
    }

    request_params = {
        "password": password,
        "meeting_id": meeting_id,
    };

    json_params = JSON.stringify(request_params);

    encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/authenticate-meeting-password/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                join_room();
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = response.message;
            }
        }
    }
    xhttp.send(params);
}

// Save agent notes after 1 second when stopped typing.
$('#agent-notes').keydown(function() {
    clearTimeout(save_notes_timer);
    save_notes_timer = setTimeout(save_agent_notes, 1000)
});

// Saving agents notes
function save_agent_notes() {
    notes = document.getElementById("agent-notes").value;
    if (notes == "") {
        return;
    }
    notes = stripHTML(notes);
    notes = remove_special_characters_from_str(notes);
    request_params = {
        "meeting_id": meeting_id,
        "notes": notes
    };

    json_params = JSON.stringify(request_params);

    encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/save-meeting-notes/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                console.log('Notes saved')
            }
        }
    }
    xhttp.send(params);
}


async function stop_recording() {
    return;
    // console.log("Recording Stop")
    // if (screen_recorder_on) {
    //     screen_recorder_on = false;
    //     recorder.stop();
    //     stream.getVideoTracks()[0].stop();
    // }
}

async function stop_client_audio_record() {
    return;
    // console.log("Recording Stop")
    // if (audio_recorder_on) {
    //     audio_recorder_on = false;
    //     recorder_client.stop();
    //     stream_client.getAudioTracks()[0].stop();
    // }
}

// Start Recording the selected screen

// function start_recording(){
//     return;
//     // console.log("Recording Start")
// }



async function start_recording() {
    if(!check_meeting_recording_enabled()) {
        return;
    }
    var is_mobile = detect_mobile();
    if(is_mobile == false){
        if (screen_recorder_on == false && is_recording_cancel == false) {
            alert('The meeting will be recorded and shared for audit purposes. Please click on “OK” and select the screen to share.')
        } else {
            alert("To resume the meeting, kindly allow to record and share your screen.")
            is_recording_cancel = false
        }
        if (screen_recorder_on) {
            screen_recorder_on = false;
            recorder.stop();
            stream.getVideoTracks()[0].stop();
        } else {
            try {
                audioStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
                [audioTrack] = audioStream.getAudioTracks();
            } catch {
                screen_recorder_on = false;
                is_recording_cancel = true;
                // show_media_unavailable_modal('microphone');
                start_recording();
                return;
            }

            try {
                displayStream = await navigator.mediaDevices.getDisplayMedia({ video: { mediaSource: "screen" } });
                [videoTrack] = displayStream.getVideoTracks();
            } catch {
                screen_recorder_on = false;
                is_recording_cancel = true;
                // show_media_unavailable_modal('camera');
                start_recording();
                return;
            }

            stream = new MediaStream([videoTrack, audioTrack]);
            stream.getVideoTracks()[0].onended = function() {
                is_recording_cancel = true
                screen_recorder_on = false
                start_recording();
            };
            screen_recorder_on = true;
            recorder = new MediaRecorder(stream);
            session_id = uuidv4();
            var filename = session_id + '.webm';

            function save_data(blob) {
                var file = new File([blob.data], filename, {
                    type: 'video/webm'
                });
                var formData = new FormData();
                formData.append("uploaded_data", file);
                formData.append("filename", file.name);
                formData.append("meeting_id", meeting_id);
                formData.append("is_first_packet", is_first_packet);

                $.ajax({
                    url: "/easy-assist/save-screen-recorded-data/",
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
                            is_first_packet = false;
                            // console.log(response["src"]);
                        } else {
                            console.log("error")
                        }
                    },
                    error: function(xhr, textstatus, errorthrown) {
                        console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
                    }
                });
            }
            recorder.ondataavailable = blob => save_data(blob);
            recorder.start(5000);
        }
    }
    if(is_meeting_joined == false){
        join_meeting();
    }
}


// Start Recording the selected screen
async function start_client_audio_record() {
    if(!check_meeting_recording_enabled()) {
        return;
    }
    if (audio_recorder_on == false) {
        show_toast("Your audio will be recorded for quality and training purposes.")
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
        const chunks = [];
        var filename = my_id + "_client" + '.webm';
        var count = 0;

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

// Save file attachment to server
function save_file_to_server(e) {
    var upload_attachment_data = document.querySelector('#meeting-file-input').files[0]
    document.querySelector('#meeting-file-input').value = '';

    if(upload_attachment_data == undefined || upload_attachment_data == null) {
        show_toast("Please choose a file.");
        return;
    }

    if(check_malicious_file_video_meeting(upload_attachment_data.name)) {
        return;
    }
    session_id = uuidv4();
    var reader = new FileReader();
    reader.readAsDataURL(upload_attachment_data);
    reader.onload = function() {

        base64_str = reader.result.split(",")[1];

        var json_string = {
            "filename": upload_attachment_data.name,
            "base64_file": base64_str,
            "meeting_id": meeting_id
        };

        json_string = JSON.stringify(json_string);

        encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/upload-cognovid-file-attachment/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response.status == 200) {
                    message = response.src;
                    file_attachment_name = message
                    message = file_attachment_name + "?vctoken=" + meeting_id;
                    send_attachmet_to_chat(message)

                } else if(response["status"] == 300) {
                    message = "File size too large"
                } else if (response.status == 302) {
                    show_toast("Unsupported file format. Please upload jpeg, jpg, png, doc, docx, or pdf file.");
                } else {
                    message = "Internal Server error"
                    show_toast("Unable to send file. Please try again.");
                }
            }
        }
        xhttp.send(params);

    };
    reader.onerror = function(error) {
        console.log('Error: ', error);
    };
}

// Save chat audit trail
function save_chat_aduit_trail(message, sender, sender_name, is_file_attachment) {

    var time = new Date().toLocaleTimeString('en-US', { hour: 'numeric', hour12: true, minute: 'numeric' });
    clearTimeout(chat_history_timer);
    if(is_file_attachment == true){
        json_string = JSON.stringify({
            "message": file_attachment_name,
            "sender": sender,
            "type": "attachment",
            "time": time,
            "sender_name": sender_name
        });
    }else{
        json_string = JSON.stringify({
            "message": message,
            "sender": sender,
            "type": "text",
            "time": time,
            "sender_name": sender_name
        });
    }
    file_attachment_name = null;
    chat_history.push(json_string)
    chat_history_timer = setTimeout(save_meeting_chats, 1000)

}

function deny_participant_entry(id) {
    if (client_websocket_open && client_websocket != null) {
        check_customers_meet_waiting_request();
        client_websocket.send(JSON.stringify({
            "message": {
                "type": "5",
                "client_id": id,
                "status": false
            }
        }));
    }
}

function admin_participant(id) {
    if (client_websocket_open && client_websocket != null) {
        check_customers_meet_waiting_request()
        client_websocket.send(JSON.stringify({
            "message": {
                "type": "5",
                "client_id": id,
                "status": true
            }
        }));
    }
}

function check_customers_meet_waiting_request() {
    let local_storage_obj =get_easyassist_current_session_local_storage_obj();
    if(local_storage_obj != null && local_storage_obj.hasOwnProperty('client_waiting_socket')) {
        set_easyassist_current_session_local_storage_obj("client_waiting_socket","");
    }
}

function show_request_modal(id, name) {
    var name_first_letter = "";
    if(name.length > 0) {
        name_first_letter = name[0];
    }

    var html_modal = [
        '<div class="modal fade permit-modal" id="request_participant-'+ id + '" tabindex="-1" data-keyboard="false" data-backdrop="static" role="dialog" aria-labelledby="close_session_modal_label" aria-hidden="true">',
            '<div class="modal-dialog" role="document">',
                '<div class="modal-content">',
                    '<div class="modal-header">',
                        '<h5 class="modal-title" id="close_session_modal_label">Someone wants to join this meeting</h5>',
                    '</div>',
                    '<div class="modal-body">',
                        '<div class="row" style="margin: 0;">',
                            '<div id="participant_name">',
                                '<span class="participant-name-bubble">',
                                    '<span style="margin-top: 2px;">' + name_first_letter + '</span>',
                                '</span>',
                                '<span class="participant-name">' + name + '</span>',
                            '</div>',
                        '</div>',
                    '</div>',
                    '<div class="modal-footer" id="participant_actions">',
                        '<a class="deny-btn" onclick="deny_participant_entry(\'' + id + '\')">Deny Entry</a>',
                        '<button class="btn admit-btn" style="color:white;" onclick="admin_participant(\'' + id + '\')">Permit</button>',
                    '</div>',
                '</div>',
            '</div>',
        '</div>'
    ].join('');

    document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', html_modal);
    $("#request_participant-" + id).modal('show')
}

// Sockets 

function send_request_to_agent_socket(client_id) {
    if (client_websocket_open && client_websocket != null) {
        client_websocket.send(JSON.stringify({
            "message": {
                "type": "4",
                "id": client_id,
                "name": display_name
            }
        }));
    }
}

// Send message over socket
function send_message_over_chat_socket(message, sender, display_name, is_file_attachment) {
    if (client_websocket_open && client_websocket != null) {
        client_websocket.send(JSON.stringify({
            "message": {
                "type": "0",
                "header": {
                    "sender_id": my_id,
                    "sender": sender,
                    "name": display_name,
                },
                "body": message,
                "is_file_attachment": is_file_attachment,
                "file_attachment_name": file_attachment_name,
            }
        }));
    }
}

function remove_participant_from_list(id) {
    new_list = []
    for(let i = 0; i < participant_ids.length; i++) {
        if (participant_ids[i]["id"] != id) {
            new_list.push(participant_ids[i])
        }
    }
    participant_ids = new_list
}


function kick_participant_socket(id) {
    remove_participant_from_list(id)
    if (client_websocket_open && client_websocket != null) {
        client_websocket.send(JSON.stringify({
            "message": {
                "type": "1",
                "header": {
                    "id": id,
                },
            }
        }));
    }
}

function update_participants(participant_ids) {
    if (client_websocket_open && client_websocket != null) {
        client_websocket.send(JSON.stringify({
            "message": {
                "type": "2",
                "participant_id": participant_ids,
            }
        }));
    }
}

function remove_participants_socket(participant_id) {
    if (client_websocket_open && client_websocket != null) {
        client_websocket.send(JSON.stringify({
            "message": {
                "type": "3",
                "is_agent": is_agent,
                "participant_id": participant_id,
            }
        }));
    }
}

function mute_participant_socket(participant_id) {
    if (client_websocket_open && client_websocket != null) {
        client_websocket.send(JSON.stringify({
            "message": {
                "type": "6",
                "name": display_name,
                "participant_id": participant_id,
            }
        }));
    }
}

function update_display_name_socket() {
    if (client_websocket_open && client_websocket != null) {
        client_websocket.send(JSON.stringify({
            "message": {
                "type": "7",
                "participant_name": display_name,
                "participant_id": my_id
            }
        }));
    }
}

function send_location_to_agent_over_socket(participant_location) {
    if (client_websocket_open && client_websocket != null) {
        client_websocket.send(JSON.stringify({
            "message": {
                "type": "8",
                "participant_name": display_name,
                "participant_id": my_id,
                "participant_location": participant_location,
                "is_agent": is_agent,
            }
        }));
    }
}

function send_participant_mute_status_over_socket(mute_status) {
    if (client_websocket_open && client_websocket != null) {
        client_websocket.send(JSON.stringify({
            "message": {
                "type": "10",
                "participant_id": my_id,
                "mute_status": mute_status,
            }
        }));
    }
}

function create_chat_socket(room_id, sender) {
    ws_scheme = window.location.protocol == "http:" ? "ws" : "wss";
    url = ws_scheme + '://' + window.location.host + '/ws/meet/' + room_id + '/' + sender + "/";
    if (client_websocket == null) {
        client_websocket = new WebSocket(url);
        client_websocket.onmessage = easyassist_handle_socket_message;
        client_websocket.onerror = function(e){
                console.error("WebSocket error observed:", e);
                client_websocket_open = false;
                easyassist_close_socket();
            }
        client_websocket.onopen = function(){
                client_websocket_open = true; 
                console.log("client_websocket created successfully");
            }
        client_websocket.onclose = function() {
                client_websocket_open = false;
                client_websocket = null; 
            }
    }
}

function create_sync_utils_easyassist_socket(jid, sender) {

    jid = "sync_utils_" + jid;
    ws_scheme = window.location.protocol == "http:" ? "ws" : "wss";
    url = ws_scheme + '://' + window.location.host + '/ws/cobrowse/sync-utils/' + jid + '/' + sender + "/";
    if (sync_utils_client_websocket == null) {
        sync_utils_client_websocket = new WebSocket(url);
        sync_utils_client_websocket.onmessage = easyassist_sync_utils_socket_message_handler;
        sync_utils_client_websocket.onerror = function(e){
                console.error("sync_utils_easyassist_socket webSocket error observed:", e);
                sync_utils_client_websocket_open = false;
                easyassist_close_sync_utils_socket();
            }
        sync_utils_client_websocket.onopen = function(){
                console.log("sync_utils_easyassist_socket created successfully") 
                sync_utils_client_websocket_open = true;
            }
        sync_utils_client_websocket.onclose = function() {
                sync_utils_client_websocket_open = false;
                sync_utils_client_websocket = null;
            }
    }
}

function easyassist_close_socket() {

    if (client_websocket == null) {
        return;
    }

    try{
        client_websocket.close();
    }catch(err){
        client_websocket.onmessage = null;
        client_websocket = null;
    }

}

function easyassist_close_sync_utils_socket() {

    if (sync_utils_client_websocket == null) {
        return;
    }

    try{
        sync_utils_client_websocket.close();
    }catch(err){
        sync_utils_client_websocket.onmessage = null;
        sync_utils_client_websocket = null;
    }

}

var easyassist_socket_activity_interval_check = setInterval(easyassist_initialize_web_socket, 1000);

function easyassist_initialize_web_socket() {

    if (client_websocket == null) {
        enable_chat_socket();
    }

    if(sync_utils_client_websocket == null) {
        enable_sync_utils_socket();
    }

}

// Enable websocket
function enable_chat_socket() {
    // console.trace();
    room_id = meeting_id
    if (is_agent == 'True' || is_invited_agent == 'True') {
        sender = "agent"
    } else {
        sender = "client"
    }
    create_chat_socket(room_id, sender);
}

function enable_sync_utils_socket() {
    
    if(is_cobrowsing_active != 'True') {
        return;
    }

    room_id = meeting_id
    if(is_reverse_cobrowsing_enabled()) {
        if(is_agent == 'True' || is_invited_agent == 'True') {
            sender = "client";
        } else {
            sender = "agent";
        }
    } else {
        if (is_agent == 'True' || is_invited_agent == 'True') {
            sender = "agent"
        } else {
            sender = "client"
        }
    }
    window.socket_message_sender = sender;
    create_sync_utils_easyassist_socket(room_id, sender);
}

function easyassist_handle_socket_message(e) {
    var data = JSON.parse(e.data);
    var message = data['message'];
    var type = data["message"]["type"]
    if (type == "0") {
        if (is_cobrowsing_active == "True") {

            var width = window.innerWidth;
            var height = window.innerHeight;
            if (width < 500 && height < 600) {
                window.resizeTo(600, 600)
            }
        }
        msg_sender = data["message"]["header"]["sender"]
        var sender_name = data["message"]["header"]["name"]
        var is_file_attachment = data["message"]["is_file_attachment"];
        file_attachment_name = data["message"]["file_attachment_name"];
        var name = sender_name;
        var sender_name_html = "";
        var html = "";
        if(msg_sender == "agent") {
            name = 'Agent: ' + name;
            if(is_agent == "False") {
                sender_name_html = '<span class="message-sender">' + sender_name + '</span>';
            } else {
                sender_name_html = '<span class="message-sender">' + name + '</span>';
            }
        } else {
            sender_name_html = '<span class="message-sender">' + sender_name + '</span>';
        }

        var message_sender_icon = "";
        if(msg_sender == "agent") {
            message_sender_icon = [
                '<svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">',
                    '<path d="M20 6.99892C20.5304 6.99892 21.0391 7.20964 21.4142 7.58471C21.7893 7.95978 22 8.46849 22 8.99892V12.9989C22 13.5294 21.7893 14.0381 21.4142 14.4131C21.0391 14.7882 20.5304 14.9989 20 14.9989H18.938C18.6942 16.9322 17.7533 18.7101 16.2917 19.9989C14.8302 21.2877 12.9486 21.9989 11 21.9989V19.9989C12.5913 19.9989 14.1174 19.3668 15.2426 18.2416C16.3679 17.1163 17 15.5902 17 13.9989V7.99892C17 6.40762 16.3679 4.8815 15.2426 3.75628C14.1174 2.63106 12.5913 1.99892 11 1.99892C9.4087 1.99892 7.88258 2.63106 6.75736 3.75628C5.63214 4.8815 5 6.40762 5 7.99892V14.9989H2C1.46957 14.9989 0.960859 14.7882 0.585786 14.4131C0.210714 14.0381 0 13.5294 0 12.9989V8.99892C0 8.46849 0.210714 7.95978 0.585786 7.58471C0.960859 7.20964 1.46957 6.99892 2 6.99892H3.062C3.30603 5.06582 4.24708 3.2882 5.70857 1.9996C7.17007 0.711003 9.05155 0 11 0C12.9484 0 14.8299 0.711003 16.2914 1.9996C17.7529 3.2882 18.694 5.06582 18.938 6.99892H20ZM6.76 14.7839L7.82 13.0879C8.77308 13.685 9.87537 14.0007 11 13.9989C12.1246 14.0007 13.2269 13.685 14.18 13.0879L15.24 14.7839C13.9693 15.5801 12.4995 16.0012 11 15.9989C9.50046 16.0012 8.03074 15.5801 6.76 14.7839Z" fill="white"/>',
                '</svg>',
            ].join('');
        } else {
            message_sender_icon = [
                '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">',
                    '<path d="M4.5 4.26316C4.5 6.61358 6.519 8.52632 9 8.52632C11.481 8.52632 13.5 6.61358 13.5 4.26316C13.5 1.91274 11.481 0 9 0C6.519 0 4.5 1.91274 4.5 4.26316ZM17 18H18V17.0526C18 13.3967 14.859 10.4211 11 10.4211H7C3.14 10.4211 0 13.3967 0 17.0526V18H17Z" fill="white"/>',
                '</svg>',
            ].join('');
        }

        if (data["message"]["header"]["sender_id"] != my_id) {
            current_time = new Date().toLocaleTimeString('en-US', { hour: 'numeric', hour12: true, minute: 'numeric' });

            if(is_file_attachment) {
                html += [
                    '<div class="message message-left">',
                        '<div style="display:flex;">',
                            '<div class="easychat-bot-msg-sender-profile">',
                                message_sender_icon,
                            '</div>',
                            '<div style="display: flex; flex-direction: column;">',
                                '<div class="bubble bubble-light bubble-attachment">',
                                    '<div class="mt-1 mb-1" style="display: flex;">',
                                        '<div class="easyassist-file-icon">',
                                            '<svg width="24" height="32" viewBox="0 0 24 32" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                                '<path fill-rule="evenodd" clip-rule="evenodd" d="M14 0V8.50667C14 9.33333 14.6667 10 15.4933 10H24V30.5067C24 31.3333 23.3333 32 22.5067 32H1.49333C0.666665 32 0 31.3333 0 30.5067V1.49333C0 0.666667 0.666665 0 1.49333 0H14ZM17.4404 0.426667L23.5471 6.56C23.8404 6.85333 24.0004 7.22667 24.0004 7.62667V8H16.0004V0H16.3737C16.7737 0 17.147 0.16 17.4404 0.426667Z" fill="url(#paint0_linear)">',
                                                '</path>',
                                                '<defs>',
                                                  '<linearGradient id="paint0_linear" x1="2.39111" y1="3" x2="23.3908" y2="32.0002" gradientUnits="userSpaceOnUse">',
                                                    '<stop stop-color="#E08F8D">',
                                                    '</stop>',
                                                    '<stop offset="1" stop-color="#FE736F">',
                                                    '</stop>',
                                                  '</linearGradient>',
                                                '</defs>',
                                            '</svg>',
                                        '</div>',
                                        '<div class="easyassist-file-text">',
                                            'File Attachment',
                                        '</div>',
                                        '<div class="easyassist-download-icon">',
                                            '<a href="' + file_attachment_name + '?vctoken=' + meeting_id + '" download>',
                                                '<img src="/static/EasyAssistApp/icons/download.svg">',
                                            '</a>',
                                        '</div>',
                                    '</div>',
                                '</div>',
                                '<div class="message-timer">',
                                    current_time,
                                '</div>',
                            '</div>',
                        '</div>',
                    '</div>'
                ].join('');
            } else {
                html = [
                    '<div class="message message-left">',
                        '<div style="display:flex;">',
                            '<div class="easychat-bot-msg-sender-profile">',
                                message_sender_icon,
                            '</div>',
                            '<div style="display: flex; flex-direction: column;">',
                                '<div class="bubble bubble-light">',
                                    sender_name_html,
                                    '<div class="mt-1 mb-1">',
                                        message["body"],
                                    '</div>',
                                '</div>',
                                '<div class="message-timer">',
                                    current_time,
                                '</div>',
                            '</div>',
                        '</div>',
                    '</div>'
                ].join('');
            }
            document.getElementById("meeting_chat_room").innerHTML += html
        }
        if (document.getElementById("cogno-lobby-meeting-chat").style.display == 'none') {
            if(is_meeting_joined) {
                if(document.getElementById("show-small-device-btn").style.display != 'none') {
                    show_small_device_options();
                }
                document.getElementById("meeting-chatbox-btn").click();
            }
        }
        save_chat_aduit_trail(message["body"], msg_sender, sender_name, is_file_attachment)
        scroll_to_bottom();
        is_message_sender = false;
    } else if (type == "1") {
        id = data["message"]["header"]["id"]
        if (my_id == id) {
            // alert("You have been removed from this meeting.");
            socket_type = 1;
            show_toast("You have been removed from this meeting.")
            window.location.href = "/easy-assist/meeting-ended/" + meeting_id;
        }
    } else if (type == "2") {
        let objs = data["message"]["participant_id"]
        participant_ids.push(objs[0])
        jsonObject = participant_ids.map(JSON.stringify);
        uniqueSet = new Set(jsonObject);
        uniqueArray = Array.from(uniqueSet).map(JSON.parse);
        participant_ids = uniqueArray
    } else if (type == "3") {
        let objs = data["message"]["participant_id"]
        remove_participant_from_list(objs)

        if(data["message"]["is_agent"] == "True" && objs != my_id) {
            agent_disconnected_meet = true;
            show_toast("Agent has left the session");
        }
    } else if (type == "4") {
        var id = data["message"]["id"]
        let name = data["message"]["name"]
        if (is_agent == "True") {
            let socket_data = {"id" : id, "name" : name}
            set_easyassist_current_session_local_storage_obj("client_waiting_socket", JSON.stringify(socket_data));
            show_request_modal(id, name);
        }
    } else if (type == "5") {
        let id = data["message"]["client_id"];
        var status = data["message"]["status"];
        $("#request_participant-" + id).modal('hide');
        if(window.is_agent == "False" && window.is_invited_agent == "False") {
            reset_easyassist_meeting_countdown_timer();
        }
        if (status == true) {
            if (id == my_id) {
                join_meeting();
            }
        } else {
            if (id == my_id) {
                alert("You are not allowed to join this meeting.")
                window.location.reload()
            }
        }
    } else if(type == "6") {
        let name = data["message"]["name"];
        var participant_id = data["message"]["participant_id"];
        if(participant_id == my_id) {
            if(is_audio_muted == false) {
                show_toast("You have been muted by " + name);
                mute_meeting_audio();
            }
        }
    } else if(type == "7") {
        let participant_id = data["message"]["participant_id"];
        var participant_name = data["message"]["participant_name"];
        update_participant_name_in_list(participant_name, participant_id);
    } else if(type == "8") {
        let participant_id = data["message"]["participant_id"];
        var participant_location = data["message"]["participant_location"];
        if(participant_location != null) {
            participant_location = stripHTML(participant_location);
        }

        if(is_agent == 'True') {
            participant_location_detail_obj[participant_id] = {
                "location": participant_location,
                "is_agent": data["message"]["is_agent"]
            }

        }
    } else if(type == "9") {
        var cobrowse_form_id = data["message"]["cobrowse_form_id"];
        if(is_agent) {
            if(document.getElementById("cobrowse-form-name-" + cobrowse_form_id)) {
                document.getElementById("cobrowse-form-name-" + cobrowse_form_id).style.color = "#25B139";
            }
        }
    } else if(type == "10") {
        let participant_id = data["message"]["participant_id"];
        var mute_status = data["message"]["mute_status"];
        if(is_agent == "True" && participant_id != my_id) {
            try {
                if(mute_status == true) {
                    document.getElementById("cogno-lobby-mute-member-btn-" + participant_id).style.display = 'none';
                    document.getElementById("cogno-lobby-unmute-member-btn-" + participant_id).style.display = 'initial';
                } else {
                    document.getElementById("cogno-lobby-unmute-member-btn-" + participant_id).style.display = 'none';
                    document.getElementById("cogno-lobby-mute-member-btn-" + participant_id).style.display = 'initial';
                }
            } catch(err) {}
        }
        for(index = 0; index < participant_ids.length; index ++) {
            if(participant_ids[index]['id'] == participant_id) {
                participant_ids[index]['is_audio_muted'] = mute_status;
            }
        }
    }
}

function easyassist_sync_utils_socket_message_handler(e) {
    var data = JSON.parse(e.data);
    var message = data.message;
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


    if(is_reverse_cobrowsing_enabled()) {
        if(message.header.sender == "client") {
            if (client_packet.type == "end_voip_meeting") {
                setTimeout(function() {
                    end_voip_calling();
                }, 1000);
            } else if (client_packet.type == "end_session") {
                setTimeout(function() {
                    end_voip_calling();
                }, 1000);
            }
        } else if (message.header.sender == "agent") {
            if (client_packet.type == "end_voip_meeting") {
                setTimeout(function() {
                    end_voip_calling();
                }, 1000);
            } else if (client_packet.type == "end_session") {
                setTimeout(function() {
                    end_voip_calling();
                }, 1000);
            }
        }
    } else {
        if(message.header.sender == "client") {
            if (client_packet.type == "end_voip_meeting") {
                setTimeout(function() {
                    end_voip_calling();
                }, 1000);
            } else if (client_packet.type == "end_session") {
                setTimeout(function() {
                    end_voip_calling();
                }, 1000);
            }
        } else if (message.header.sender == "agent" && is_agent == "False") { // add invited agent check
            if (client_packet.type == "end_voip_meeting") {
                setTimeout(function() {
                    end_voip_calling();
                }, 1000);
            } else if (client_packet.type == "end_session") {
                setTimeout(function() {
                    end_voip_calling();
                }, 1000);
            }
        }
    }

}

function send_message_over_sync_utils_easyassist_socket(message, sender) {

    if(is_cobrowsing_active != 'True') {
        return;
    }

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

function easyassist_send_meeting_ended_over_socket() {

    var agent_name = window.agent_name;
    if(agent_name != "Agent") {
        agent_name = "Agent " + agent_name;
    }
    
    var json_string = JSON.stringify({
        "type": "end_voip_meeting",
        "agent_name": agent_name
    });

    var encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, window.socket_message_sender);
}

function send_invited_agent_disconnect_message_over_socket() {
    var json_string = JSON.stringify({
        "type": "invited_agent_disconnected",
        "invited_agent_name": window.agent_name,
        "agent_username": window.INVITED_AGENT_USERNAME
    });

    var encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_sync_utils_easyassist_socket(encrypted_data, window.socket_message_sender);
}

// Send attachment to chat
function send_attachmet_to_chat(attachment_link) {
    is_message_sender = true
    current_time = new Date().toLocaleTimeString('en-US', { hour: 'numeric', hour12: true, minute: 'numeric' });
    // var sender_name = '';
    // if(is_agent == 'True' || is_invited_agent == 'True') {
    //     sender_name = 'Agent: ' + display_name
    // } else {
    //     sender_name = 'Customer: ' + display_name
    // }

    var html = [
        '<div class="message message-right">',
            '<div style="display:flex;">',
                '<div class="bubble bubble-light bubble-attachment">',
                    '<div class="mt-1 mb-1" style="display: flex;">',
                        '<div class="easyassist-file-icon">',
                            '<svg width="24" height="32" viewBox="0 0 24 32" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path fill-rule="evenodd" clip-rule="evenodd" d="M14 0V8.50667C14 9.33333 14.6667 10 15.4933 10H24V30.5067C24 31.3333 23.3333 32 22.5067 32H1.49333C0.666665 32 0 31.3333 0 30.5067V1.49333C0 0.666667 0.666665 0 1.49333 0H14ZM17.4404 0.426667L23.5471 6.56C23.8404 6.85333 24.0004 7.22667 24.0004 7.62667V8H16.0004V0H16.3737C16.7737 0 17.147 0.16 17.4404 0.426667Z" fill="url(#paint0_linear)">',
                                '</path>',
                                '<defs>',
                                  '<linearGradient id="paint0_linear" x1="2.39111" y1="3" x2="23.3908" y2="32.0002" gradientUnits="userSpaceOnUse">',
                                    '<stop stop-color="#E08F8D">',
                                    '</stop>',
                                    '<stop offset="1" stop-color="#FE736F">',
                                    '</stop>',
                                  '</linearGradient>',
                                '</defs>',
                            '</svg>',
                        '</div>',
                        '<div class="easyassist-file-text">',
                            'File Attachment',
                        '</div>',
                        '<div class="easyassist-download-icon">',
                            '<a href="' + attachment_link + '" download>',
                                '<img src="/static/EasyAssistApp/icons/download.svg">',
                            '</a>',
                        '</div>',
                    '</div>',
                '</div>',
            '</div>',
            '<div class="message-timer">',
                current_time,
            '</div>',
        '</div>'
    ].join('');

    document.getElementById("meeting_chat_room").innerHTML += html
    send_message_over_chat_socket(message, sender, display_name, true)
    document.getElementById("meeting_text_message").value = "";
}

// Send message to chat
function send_message_to_chat() {
    is_message_sender = true
    message = document.getElementById("meeting_text_message").value;
    message = stripHTML(message);
    message = remove_special_characters_from_str(message);
    message = message.trim();
    if (message == "") {
        document.getElementById("meeting_text_message").value = "";
        return;
    }

    current_time = new Date().toLocaleTimeString('en-US', { hour: 'numeric', hour12: true, minute: 'numeric' });
    // var sender_name = '';
    // if(is_agent == 'True' || is_invited_agent == 'True') {
    //     sender_name = 'Agent: ' + display_name
    // } else {
    //     sender_name = 'Customer: ' + display_name
    // }
    html = [
        '<div class="message message-right" id="meeting_chat_box_reciever">',
            '<div class="bubble bubble-dark">',
                '<div class="mt-1 mb-1">',
                    message,
                '</div>',
            '</div>',
            '<div class="message-timer">',
                current_time,
            '</div>',
        '</div>'
    ].join('');

    document.getElementById("meeting_chat_room").innerHTML += html
    scroll_to_bottom();
    send_message_over_chat_socket(message, sender, display_name, false);
    document.getElementById("meeting_text_message").value = "";
}


function keypress_chat_message(event) {
    if(document.getElementById('meeting_text_message')) {
        message = document.getElementById('meeting_text_message').value;
        if (event.keyCode == 13) {
            if (message != "") {
                send_message_to_chat();
            }
        }
    }
}

// On enter send message
document.addEventListener('keydown', keypress_chat_message);

// Get list of active agents
function get_list_of_support_agents() {

    div_inner_html = [
        '<div class="col-12 pt-4">',
            '<p>Loading ...',
        '</div>'
    ].join('');
    document.getElementById("cogno-lobby-support-agent-list").innerHTML = div_inner_html;

    json_string = JSON.stringify({
        "id": meeting_id
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/get-meet-support-agents/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            div_inner_html = "";
            if (response.status == 200) {
                support_agents = response.support_agents;
                if (Object.keys(support_agents).length > 0) {
                    var product_counter = 0;
                    for(let product_category in support_agents) {
                        div_inner_html += [
                            '<div class="col-12 mt-4">',
                                '<div class="product-category-container">',
                                    '<div class="btn-group product-category-btn-group" role="group" data-toggle="collapse" data-target="#product-category-' + product_counter + '">',
                                        '<button type="button" class="btn">' + product_category + '</button>',
                                        '<button type="button" class="btn collapsed">',
                                            '<svg width="8" height="9" viewBox="0 0 8 9" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                                '<path d="M7.05 3.37417C7.91667 3.87454 7.91667 5.12546 7.05 5.62583L2.7 8.13731C1.83333 8.63768 0.750001 8.01221 0.750001 7.01147L0.750001 1.98853C0.750001 0.987786 1.83333 0.362323 2.7 0.862693L7.05 3.37417Z" fill="#757575"/>',
                                            '</svg>',
                                        '</button>',
                                    '</div>',
                                    '<div id="product-category-' + product_counter + '" class="collapse">',
                        ].join('')

                        if(support_agents[product_category].length > 0) {
                            for(let idx = 0; idx < support_agents[product_category].length; idx ++) {
                                var id = support_agents[product_category][idx]["id"];
                                var username = support_agents[product_category][idx]["username"];
                                var level = support_agents[product_category][idx]["level"];

                                div_inner_html += [
                                   '<li>',
                                        '<div class="congo-lobby-support-agent-text">',
                                            username + ' - ' + level,
                                        '</div>',
                                        '<div class="cogno-lobby-support-agent-invite-btn">',
                                            '<a href="javascript:void(0);" onclick="join_cobrowsing_meeting(this, \'' + id + '\')">Invite</a>',
                                        '</div>',
                                    '</li>',
                                ].join('');
                            }
                        } else {
                            div_inner_html += [
                               '<li>',
                                    '<div class="congo-lobby-support-agent-text">',
                                        'No active support agents found.',
                                    '</div>',
                                '</li>',
                            ].join('');
                        }
                        div_inner_html += "</div></div></div>";
                        product_counter ++;
                    }
                } else {
                    div_inner_html = [
                        '<div class="col-12 pt-4">',
                            '<p>No active support agents found.</p>',
                        '</div>'
                    ].join('');
                }
                document.getElementById("cogno-lobby-support-agent-list").innerHTML = div_inner_html;
            } else {
                document.getElementById("cogno-lobby-support-agent-list").innerHTML = "Unable to load the details.";
            }
        }
    }
    xhttp.send(params);
}

function get_list_of_support_documents() {

    div_inner_html = [
        '<div class="row" style="padding: 1em;">',
            '<div class="col-12 pt-4">',
                '<p>Loading ...</p>',
            '</div>',
        '</div>'
    ].join('');
    document.getElementById("cogno-doc-container").innerHTML = div_inner_html;

    json_string = JSON.stringify({
        "id": meeting_id
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/get-meet-support-documents/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            div_inner_html = "";
            if (response.status == 200) {
                meeting_doc_list = response.support_document;
                if (meeting_doc_list.length > 0) {
                    for(let idx = 0; idx < meeting_doc_list.length; idx++) {
                        div_inner_html += [
                            '<div class="row" style="margin:0;padding: 1em 0em;">',
                                '<div class="col-md-12">',
                                    '<div class="card">',
                                        '<div class="card-header">',
                                            meeting_doc_list[idx]["file_name"],
                                        '</div>',
                                        '<div class="card-body">',
                                            '<textarea class="cogno-doc-textarea" placeholder="Type here">','</textarea>',
                                        '</div>',
                                        '<div class="card-footer">',
                                            '<button class="btn btn-send-cogno-meet-doc" type="button" onclick="send_meeting_doc(this, \'' + meeting_doc_list[idx]["file_path"] + '\')">',
                                                'Send ',
                                                '<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                                    '<path d="M14.6604 6.9421L0.926741 0.0660178C0.819101 0.0121135 0.698194 -0.00948478 0.57858 0.00382366C0.458965 0.0171321 0.345743 0.0647798 0.252544 0.14103C0.163541 0.215724 0.0971085 0.313799 0.0607163 0.424227C0.024324 0.534655 0.0194146 0.653059 0.0465398 0.766128L1.70082 6.87334H8.76116V8.12354H1.70082L0.0215696 14.212C-0.00388357 14.3064 -0.00685474 14.4055 0.0128951 14.5013C0.0326449 14.5971 0.0745646 14.6869 0.135283 14.7635C0.196002 14.8401 0.273826 14.9014 0.362497 14.9424C0.451168 14.9834 0.548212 15.003 0.645826 14.9996C0.743548 14.999 0.839768 14.9755 0.926741 14.9309L14.6604 8.05478C14.7626 8.00232 14.8484 7.92263 14.9084 7.82447C14.9683 7.72631 15 7.61349 15 7.49844C15 7.3834 14.9683 7.27058 14.9084 7.17242C14.8484 7.07426 14.7626 6.99456 14.6604 6.9421Z" fill="#0254D7"/>',
                                                '</svg>',
                                            '</button>',
                                        '</div>',
                                    '</div>',
                                '</div>',
                            '</div>',
                        ].join('');
                    }
                } else {
                    div_inner_html = [
                        '<div class="col-12 pt-4">',
                            '<p>No document exists.</p>',
                        '</div>'
                    ].join('');
                }
                document.getElementById("cogno-doc-container").innerHTML = div_inner_html;
            } else {
                document.getElementById("cogno-doc-container").innerHTML = "Unable to load the documents.";
            }
        } else if (this.readyState == 4) {
            document.getElementById("cogno-doc-container").innerHTML = "Due to some network issue, we are unable to load the documents. Please try again.";
        }
    }
    xhttp.send(params);
}

function get_list_of_meeting_forms() {
    div_inner_html = [
        '<div class="row" style="padding: 1em; margin: 0;">',
            '<div class="col-12 pt-4">',
                '<p>Loading ...',
            '</div>',
        '</div>'
    ].join('');
    document.getElementById("cogno-lobby-forms-list").innerHTML = div_inner_html;

    json_string = JSON.stringify({
        "id": meeting_id
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/get-meeting-forms/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            div_inner_html = "";
            if (response.status == 200) {
                meeting_forms_list = response.meeting_forms;
                if (meeting_forms_list.length > 0) {
                    for(let idx = 0; idx < meeting_forms_list.length; idx++) {
                        div_inner_html += [
                            '<div class="row" style="padding: 1em; margin: 0;">',
                                '<div class="col-12">',
                                    '<div class="card">',
                                        '<div class="card-body cogno-lobby-meeting-form-name" onclick="show_meeting_form_to_agent(this,\'' + meeting_forms_list[idx]['id'] + '\');">',
                                            '<span id="cobrowse-form-name-' + meeting_forms_list[idx]['id'] + '">' + meeting_forms_list[idx]['name'] + '</span>',
                                        '</div>',
                                    '</div>',
                                '</div>',
                            '</div>'
                        ].join('');
                    }
                } else {
                    div_inner_html = [
                        '<div class="col-12 pt-4">',
                            '<p>No form exists.</p>',
                        '</div>'
                    ].join('');
                }
                document.getElementById("cogno-lobby-forms-list").innerHTML = div_inner_html;
            } else {
                document.getElementById("cogno-lobby-forms-list").innerHTML = "Unable to load the forms.";
            }
        }
    }
    xhttp.send(params);
}

function send_meeting_doc(el, file_path)
{
    file_attachment_name = "/easy-assist/download-file/" + file_path
    attachment_link = '<a href="/easy-assist/download-file/' + file_path + '/?vctoken=' + meeting_id + '" target="_blank">File Attachment</a>'
    send_attachmet_to_chat(file_attachment_name);

    var message = $(el).closest('.card').find('textarea').val();
    message = stripHTML(message);
    message = remove_special_characters_from_str(message);

    if(message) {
        current_time = new Date().toLocaleTimeString('en-US', { hour: 'numeric', hour12: true, minute: 'numeric' });
        // var sender_name = '';
        // if(is_agent == 'True' || is_invited_agent == 'True') {
        //     sender_name = 'Agent: ' + display_name
        // } else {
        //     sender_name = 'Customer: ' + display_name
        // }
        html = [
            '<div class="message message-right" id="meeting_chat_box_reciever">',
                '<div class="bubble bubble-dark">',
                    '<div class="mt-1 mb-1">',
                        message,
                    '</div>',
                '</div>',
                '<div class="message-timer">',
                    current_time,
                '</div>',
            '</div>'
        ].join('');

        document.getElementById("meeting_chat_room").innerHTML += html
        scroll_to_bottom();
        send_message_over_chat_socket(message, sender, display_name, false);
    }
}

function update_participant_name_in_list(participant_name, participant_id) {

    for(let idx = 0; idx < participant_ids.length; idx++) {
        if(participant_ids[idx]['id'] == participant_id) {
            participant_ids[idx]['participant_name'] = participant_name;
        }
    }
}

// Ask another agents to join meeting.
function join_cobrowsing_meeting(element, agent_id) {

    json_string = JSON.stringify({
        "id": meeting_id,
        "support_agents": [agent_id]
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Requesting...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/request-agent-meeting/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_toast("We have requested the agent.")
            }
            element.innerHTML = "Resend";
        }
    }
    xhttp.send(params);
}


function invite_people_over_email(element) {
    error_message_element = document.getElementById("invite-people-mail-error");
    error_message_element.innerHTML = "";

    email_ids = document.getElementById("client-email-id").value.split(',');
    for (let idx = 0; idx < email_ids.length; idx++) {
        if (!regEmail.test(email_ids[idx])) {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Please enter valid email id(s).";
            error_message_element.style.display = 'block';
            return;
        }
    }
    request_params = {
        "email_ids": email_ids,
        "meeting_id": meeting_id
    };

    json_params = JSON.stringify(request_params);

    encrypted_data = easyassist_custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);
    element.innerHTML = "Inviting...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/invite-video-meeting-email/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                error_message_element.innerHTML = 'We have sent the invite to the given Email ID' + ((email_ids.length > 1) ? 's.' : '.');
                error_message_element.style.color = "green";
                error_message_element.style.display = 'block';
            } else {
                error_message_element.innerHTML = 'Unable to send invite. Please try again.'
                error_message_element.style.color = "red";
                error_message_element.style.display = 'block';
            }
            element.innerHTML = "Add";
        } else if (this.readyState == 4) {
            error_message_element.innerHTML = 'Due to some network issue, we are unable to send invite. Please try again.'
            error_message_element.style.color = "red";
            error_message_element.style.display = 'block';
        }
    }
    xhttp.send(params);
}

// function invite_people_over_phone(element) {
//     error_message_element = document.getElementById("invite-people-phone-error");
//     error_message_element.innerHTML = "";
//     const regMob = /^[6-9]{1}[0-9]{9}$/;

//     mobile_number = document.getElementById("client-mobile-number").value;
//     if (!regMob.test(mobile_number)) {
//         error_message_element.style.color = "red";
//         error_message_element.innerHTML = "Please enter valid phone number.";
//         error_message_element.style.display = 'block';
//         return;
//     }
//     request_params = {
//         "mobile_number": mobile_number,
//         "meeting_id": meeting_id
//     };

//     json_params = JSON.stringify(request_params);

//     encrypted_data = easyassist_custom_encrypt(json_params);

//     encrypted_data = {
//         "Request": encrypted_data
//     };

//     var params = JSON.stringify(encrypted_data);
//     element.innerHTML = "Inviting...";
//     var xhttp = new XMLHttpRequest();
//     xhttp.open("POST", "/easy-assist/invite-video-meeting-phone/", true);
//     xhttp.setRequestHeader('Content-Type', 'application/json');
//     xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
//     xhttp.onreadystatechange = function() {
//         if (this.readyState == 4 && this.status == 200) {
//             response = JSON.parse(this.responseText);
//             response = easyassist_custom_decrypt(response.Response);
//             response = JSON.parse(response);
//             if (response["status"] == 200) {
//                 error_message_element.innerHTML = 'We have sent the invite to the given phone number';
//                 error_message_element.style.color = "green";
//                 error_message_element.style.display = 'block';
//             } else {
//                 error_message_element.innerHTML = 'Unable to send invite. Please try again.'
//                 error_message_element.style.color = "red";
//                 error_message_element.style.display = 'block';
//             }
//             element.innerHTML = "Invite";
//         }
//     }
//     xhttp.send(params);
// }

// Check user internet speed
function check_internet_every_ten_sec() {
    var startTime, endTime, fileSize;
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            endTime = (new Date()).getTime();
            fileSize = xhr.responseText.length;
            var speed = fileSize / ((endTime - startTime) / 1000) / 1024;
            // If Speed is less than 2 mbps
            if (speed < 2048) {
                // alert("You have slow internet. Please switch to better connection.");
                show_toast("Weak connection detected. The quality and user experience might be reduced due to low bandwidth.")
                clearInterval(internet_timer)
            }
        }
    }
    startTime = (new Date()).getTime();
    xhr.open("GET", "/static/EasyAssistApp/js/video_meeting.js", true);
    xhr.send();
}

function accept_location_request(pos) {
    latitude = pos.coords.latitude;
    longitude = pos.coords.longitude;

    let client_location = get_cookie("client_location");
    if(client_location == "") {
        get_client_location_from_coordinates();
    } else {
        client_location = client_location.split('|')
        if(client_location.length < 3 || client_location[0] != latitude || client_location[1] != longitude) {
            get_client_location_from_coordinates();
        } else {
            my_current_location = client_location.slice(2).join(" ");
            send_location_to_agent_over_socket(my_current_location);
            save_client_location_details();
        }
    }
}

function cancel_location_request(pos) {
    latitude = null;
    longitude = null;
    my_current_location = "None";
    save_client_location_details();
    send_location_to_agent_over_socket(my_current_location);
}

function get_client_location_from_coordinates() {

    var geocoder = new google.maps.Geocoder();
    var latlng = new google.maps.LatLng(latitude, longitude);
    geocoder.geocode({'latLng': latlng}, function(results, status) {
        if(status == google.maps.GeocoderStatus.OK) {
            if(results[2]) {
                var address = results[2].formatted_address;
                my_current_location = address;
                send_location_to_agent_over_socket(address);

                let client_location = String(latitude) + "|" + String(longitude) + "|" + my_current_location;
                set_cookie("client_location", client_location);
            } else {
                my_current_location = "None";
                send_location_to_agent_over_socket(my_current_location);
            }
            save_client_location_details();
        } else {
            my_current_location = "None";
            send_location_to_agent_over_socket(my_current_location);
            save_client_location_details();
        }
    });
}

function save_client_location_details() {
    request_params = {
        "meeting_id": meeting_id,
        "client_name": client_name,
        "longitude": longitude,
        "latitude": latitude,
        "client_address": my_current_location,
    };
    json_params = JSON.stringify(request_params);

    encrypted_data = easyassist_custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/save-client-location-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                console.log("location saved successfully");
            } else {
                console.log("Failed to save customer's location");
            }
        }
    }
    xhttp.send(params);
}

function toggle_background_music(play_music) {
    try {
        var audio_player = document.getElementById("audioplayer");
        if(!audio_player) {
            return;
        }
        if(play_music) {
            document.getElementById("cogno-lobby-music-unmute-btn").style.display = 'none';
            document.getElementById("cogno-lobby-music-mute-btn").style.display = 'block';
            audio_player.play();
        } else {
            document.getElementById("cogno-lobby-music-unmute-btn").style.display = 'block';
            document.getElementById("cogno-lobby-music-mute-btn").style.display = 'none';
            audio_player.pause();
        }
    } catch (error) {
        
    }
}

function save_screenshot() {
    if(displayStream == null || displayStream == undefined) {
        if(display_media_available) {
            show_toast("Not able to save the screnshot. Please try again.");
        } else {
            show_toast("Screenshot is not supported");
        }
        return;
    }

    try {
        var video = document.createElement('video');
        var canvas = document.createElement('canvas');

        video.autoplay = true;
        video.srcObject = displayStream;
        video.onplay = () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            img_data = canvas.toDataURL('image/png');

            video.remove();
            canvas.remove();

            json_string = JSON.stringify({
                "content": img_data,
                "meeting_id": meeting_id,
                "type_screenshot": "screenshot"
            });

            encrypted_data = easyassist_custom_encrypt(json_string);
            encrypted_data = {
                "Request": encrypted_data
            };

            var params = JSON.stringify(encrypted_data);
            var xhttp = new XMLHttpRequest();
            xhttp.open("POST", "/easy-assist/save-meeting-screenshot/", true);
            xhttp.setRequestHeader('Content-Type', 'application/json');
            xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
            xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    response = JSON.parse(this.responseText);
                    response = easyassist_custom_decrypt(response.Response);
                    response = JSON.parse(response);
                    if(response["status"] == 200) {
                        show_toast("Screenshot saved successfully.");
                    } else {
                        show_toast("Not able to save the screnshot. Please try again.");
                    }
                } else if (this.readyState == 4) {
                    show_toast("Not able to save the screnshot. Please try again.");
                }
            }
            xhttp.send(params);
        };
    } catch(err) {
        console.log("Screen capture error:", err);
        show_toast("Not able to save the screnshot. Please try again.");
    }
}

async function capture_display_stream() {
    try {
        if(navigator.mediaDevices.getDisplayMedia) {
            display_media_available = true;
            displayStream = await navigator.mediaDevices.getDisplayMedia({ video: { mediaSource: "screen" } });
            [videoTrack] = displayStream.getVideoTracks();

            videoTrack.onended = function() {
                capture_display_stream();
            }
        } else {
            display_media_available = false;
        }
    } catch(err) {
        capture_display_stream();
        return;
    }
}

function get_client_agent_chats() {

    var json_string = JSON.stringify({
        "meeting_id": meeting_id,
    });

    var encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/get-client-agent-chats/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                message_history = response["message_history"]
                chat_history = [];
                var html = "";
                for(let i = 0; i < message_history.length; i ++) {
                    var message_sender = message_history[i]["sender"]
                    var sender_name = message_history[i]["sender_name"]
                    var message_text = message_history[i]["message"];
                    var message_time = message_history[i]["time"];
                    var message_type = message_history[i]["type"];
                    var name = "";
                    var message_file_name = "";
                    var sender_name_html = "";

                    if(message_sender == "agent") {
                        name = "Agent: " + sender_name;
                        if(is_agent == "True") {
                            sender_name_html = '<span class="message-sender">' + name + '</span>';
                        } else {
                            sender_name_html = '<span class="message-sender">' + sender_name + '</span>';
                        }
                    } else {
                        sender_name_html = '<span class="message-sender">' + sender_name + '</span>';
                    }

                    if(message_type == "attachment") {
                        var regex = /(\/easy-assist\/download-file\/[0-9a-zA-Z-]+)/g;
                        var regex_match = message_text.match(regex);
                        if(regex_match) {
                            message_file_name = regex_match[0];
                        }
                    }

                    var message_sender_icon = "";
                    if(message_sender == "agent") {
                        message_sender_icon = [
                            '<svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path d="M20 6.99892C20.5304 6.99892 21.0391 7.20964 21.4142 7.58471C21.7893 7.95978 22 8.46849 22 8.99892V12.9989C22 13.5294 21.7893 14.0381 21.4142 14.4131C21.0391 14.7882 20.5304 14.9989 20 14.9989H18.938C18.6942 16.9322 17.7533 18.7101 16.2917 19.9989C14.8302 21.2877 12.9486 21.9989 11 21.9989V19.9989C12.5913 19.9989 14.1174 19.3668 15.2426 18.2416C16.3679 17.1163 17 15.5902 17 13.9989V7.99892C17 6.40762 16.3679 4.8815 15.2426 3.75628C14.1174 2.63106 12.5913 1.99892 11 1.99892C9.4087 1.99892 7.88258 2.63106 6.75736 3.75628C5.63214 4.8815 5 6.40762 5 7.99892V14.9989H2C1.46957 14.9989 0.960859 14.7882 0.585786 14.4131C0.210714 14.0381 0 13.5294 0 12.9989V8.99892C0 8.46849 0.210714 7.95978 0.585786 7.58471C0.960859 7.20964 1.46957 6.99892 2 6.99892H3.062C3.30603 5.06582 4.24708 3.2882 5.70857 1.9996C7.17007 0.711003 9.05155 0 11 0C12.9484 0 14.8299 0.711003 16.2914 1.9996C17.7529 3.2882 18.694 5.06582 18.938 6.99892H20ZM6.76 14.7839L7.82 13.0879C8.77308 13.685 9.87537 14.0007 11 13.9989C12.1246 14.0007 13.2269 13.685 14.18 13.0879L15.24 14.7839C13.9693 15.5801 12.4995 16.0012 11 15.9989C9.50046 16.0012 8.03074 15.5801 6.76 14.7839Z" fill="white"/>',
                            '</svg>',
                        ].join('');
                    } else {
                        message_sender_icon = [
                            '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path d="M4.5 4.26316C4.5 6.61358 6.519 8.52632 9 8.52632C11.481 8.52632 13.5 6.61358 13.5 4.26316C13.5 1.91274 11.481 0 9 0C6.519 0 4.5 1.91274 4.5 4.26316ZM17 18H18V17.0526C18 13.3967 14.859 10.4211 11 10.4211H7C3.14 10.4211 0 13.3967 0 17.0526V18H17Z" fill="white"/>',
                            '</svg>',
                        ].join('');
                    }

                    if(message_type == "attachment") {
                        if(sender_name == display_name) {
                            html += [
                                '<div class="message message-right">',
                                    '<div style="display:flex;">',
                                        '<div class="bubble bubble-light bubble-attachment">',
                                            '<div class="mt-1 mb-1" style="display: flex;">',
                                                '<div class="easyassist-file-icon">',
                                                    '<svg width="24" height="32" viewBox="0 0 24 32" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                                        '<path fill-rule="evenodd" clip-rule="evenodd" d="M14 0V8.50667C14 9.33333 14.6667 10 15.4933 10H24V30.5067C24 31.3333 23.3333 32 22.5067 32H1.49333C0.666665 32 0 31.3333 0 30.5067V1.49333C0 0.666667 0.666665 0 1.49333 0H14ZM17.4404 0.426667L23.5471 6.56C23.8404 6.85333 24.0004 7.22667 24.0004 7.62667V8H16.0004V0H16.3737C16.7737 0 17.147 0.16 17.4404 0.426667Z" fill="url(#paint0_linear)">',
                                                        '</path>',
                                                        '<defs>',
                                                          '<linearGradient id="paint0_linear" x1="2.39111" y1="3" x2="23.3908" y2="32.0002" gradientUnits="userSpaceOnUse">',
                                                            '<stop stop-color="#E08F8D">',
                                                            '</stop>',
                                                            '<stop offset="1" stop-color="#FE736F">',
                                                            '</stop>',
                                                          '</linearGradient>',
                                                        '</defs>',
                                                    '</svg>',
                                                '</div>',
                                                '<div class="easyassist-file-text">',
                                                    'File Attachment',
                                                '</div>',
                                                '<div class="easyassist-download-icon">',
                                                    '<a href="' + message_file_name + '?vctoken=' + meeting_id + '" download>',
                                                        '<img src="/static/EasyAssistApp/icons/download.svg">',
                                                    '</a>',
                                                '</div>',
                                            '</div>',
                                        '</div>',
                                    '</div>',
                                    '<div class="message-timer">',
                                        message_time,
                                    '</div>',
                                '</div>'
                            ].join('');
                        } else {
                            html += [
                                '<div class="message message-left">',
                                    '<div style="display:flex;">',
                                        '<div class="easychat-bot-msg-sender-profile">',
                                            message_sender_icon,
                                        '</div>',
                                        '<div style="display: flex; flex-direction: column;">',
                                            '<div class="bubble bubble-light bubble-attachment">',
                                                '<div class="mt-1 mb-1" style="display: flex;">',
                                                    '<div class="easyassist-file-icon">',
                                                        '<svg width="24" height="32" viewBox="0 0 24 32" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                                            '<path fill-rule="evenodd" clip-rule="evenodd" d="M14 0V8.50667C14 9.33333 14.6667 10 15.4933 10H24V30.5067C24 31.3333 23.3333 32 22.5067 32H1.49333C0.666665 32 0 31.3333 0 30.5067V1.49333C0 0.666667 0.666665 0 1.49333 0H14ZM17.4404 0.426667L23.5471 6.56C23.8404 6.85333 24.0004 7.22667 24.0004 7.62667V8H16.0004V0H16.3737C16.7737 0 17.147 0.16 17.4404 0.426667Z" fill="url(#paint0_linear)">',
                                                            '</path>',
                                                            '<defs>',
                                                              '<linearGradient id="paint0_linear" x1="2.39111" y1="3" x2="23.3908" y2="32.0002" gradientUnits="userSpaceOnUse">',
                                                                '<stop stop-color="#E08F8D">',
                                                                '</stop>',
                                                                '<stop offset="1" stop-color="#FE736F">',
                                                                '</stop>',
                                                              '</linearGradient>',
                                                            '</defs>',
                                                        '</svg>',
                                                    '</div>',
                                                    '<div class="easyassist-file-text">',
                                                        'File Attachment',
                                                    '</div>',
                                                    '<div class="easyassist-download-icon">',
                                                        '<a href="' + message_file_name + '?vctoken=' + meeting_id + '" download>',
                                                            '<img src="/static/EasyAssistApp/icons/download.svg">',
                                                        '</a>',
                                                    '</div>',
                                                '</div>',
                                            '</div>',
                                            '<div class="message-timer">',
                                                message_time,
                                            '</div>',
                                        '</div>',
                                    '</div>',
                                '</div>'
                            ].join('');
                        }
                    } else {
                        if(sender_name == display_name) {
                            html += [
                                '<div class="message message-right">',
                                    '<div style="display:flex;">',
                                        '<div class="bubble bubble-dark">',
                                            '<div class="mt-1 mb-1">',
                                                message_text,
                                            '</div>',
                                        '</div>',
                                    '</div>',
                                    '<div class="message-timer">',
                                        message_time,
                                    '</div>',
                                '</div>'
                            ].join('');
                        } else {
                            html += [
                                '<div class="message message-left">',
                                    '<div style="display:flex;">',
                                        '<div class="easychat-bot-msg-sender-profile">',
                                            message_sender_icon,
                                        '</div>',
                                        '<div style="display: flex; flex-direction: column;">',
                                            '<div class="bubble bubble-light">',
                                                sender_name_html,
                                                '<div class="mt-1 mb-1">',
                                                    message_text,
                                                '</div>',
                                            '</div>',
                                            '<div class="message-timer">',
                                                message_time,
                                            '</div>',
                                        '</div>',
                                    '</div>',
                                '</div>'
                            ].join('');
                        }
                    }

                    if(message_type == "attachment") {
                        json_string = JSON.stringify({
                            "message": message_file_name,
                            "sender": message_sender,
                            "type": message_type,
                            "time": message_time,
                            "sender_name": sender_name
                        });
                    } else {
                        json_string = JSON.stringify({
                            "message": message_text,
                            "sender": message_sender,
                            "type": message_type,
                            "time": message_time,
                            "sender_name": sender_name
                        });
                    }
                    chat_history.push(json_string);
                }
                document.getElementById("meeting_chat_room").innerHTML = html;
                scroll_to_bottom();
            }
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

function end_voip_calling() {
    set_easyassist_cookie("is_cobrowse_meeting_active", "");
    set_easyassist_cookie("is_meeting_initiate_by_customer", "");
    clear_ongoing_meeting_status_interval();
    jitsi_meet_api.executeCommand("hangup");
}

function clear_ongoing_meeting_status_interval() {
    if (ongoing_meeting_status_interval != null) {
        clearInterval(ongoing_meeting_status_interval);
        ongoing_meeting_status_interval = null;
    }
}

function load_map_script() {

    var params = JSON.stringify({});

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/map-script/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                var src = response['src'];
                var script = document.createElement('script');
                script.type = 'text/javascript';
                script.defer = true;
                script.src = src
                document.body.appendChild(script);          
            }
        }
    }
    xhttp.send(params);
}

function update_meeting_end_time() {

    var json_string = JSON.stringify({
        "meeting_id": meeting_id,
        "is_agent": is_agent,
        "is_invited_agent": is_invited_agent,
    });

    var encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/save-meeting-end-time/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                console.log("Meeting time saved successfully");
            } else {
                console.log("Not able to save agent meeting end time");
            }
        }
    }
    xhttp.send(params);
}

$(document).click(function(event) {
    if(event.target.id == "cogno-lobby-option-backdrop") {
        var width = window.innerWidth;

        if (width >= 600) {
            hide_all_meeting_options();
        } else {
            hide_small_device_options();
        }
    }
});

$('#cogno-lobby-agent-search').keyup(function(e) {
    var search_text = e.target.value.toLowerCase();
    search_text = stripHTML(search_text);

    if(search_text) {
        var product_categories = document.getElementsByClassName("product-category-container");
        for(let idx = 0; idx < product_categories.length; idx ++) {
            var product_category = $(product_categories[idx]).find('.product-category-btn-group').find('button:eq(0)').text();
            product_category = product_category.toLowerCase();
            let agent_elements_list = [];
            if(product_category.indexOf(search_text) > -1) {
                agent_elements_list = $(product_categories[idx]).find('li');
                for(let index = 0; index < agent_elements_list.length; index++) {
                    $(agent_elements_list[index]).show();
                }

                $(product_categories[idx]).parent().show();
                if($(product_categories[idx]).find('.product-category-btn-group').hasClass('collapsed') == false) {
                    $(product_categories[idx]).find('.product-category-btn-group').click();
                }
                continue;
            }

            var agent_matched_list = [];
            agent_elements_list = $(product_categories[idx]).find('li');
            for(let index = 0; index < agent_elements_list.length; index++) {
                var agent_name = $(agent_elements_list[index]).find('.congo-lobby-support-agent-text').text();
                agent_name = agent_name.toLowerCase();

                if(agent_name.indexOf(search_text) > -1) {
                    agent_matched_list.push(agent_elements_list[index]);
                } else {
                    $(agent_elements_list[index]).hide();
                }
            }

            if(agent_matched_list.length == 0) {
                $(product_categories[idx]).parent().hide();
            } else {
                for(let index = 0; index < agent_matched_list.length; index ++) {
                    $(agent_matched_list[index]).show();
                }
                $(product_categories[idx]).parent().show();
                if($(product_categories[idx]).find('.product-category-btn-group').hasClass('collapsed')) {
                    $(product_categories[idx]).find('.product-category-btn-group').click();
                }
            }
        }
    } else {
        let product_categories = document.getElementsByClassName("product-category-container");
        for(let idx = 0; idx < product_categories.length; idx ++) {
            $(product_categories[idx]).parent().show();

            if($(product_categories[idx]).find('.product-category-btn-group').hasClass('collapsed') == false) {
                $(product_categories[idx]).find('.product-category-btn-group').click();
            }

            let agent_elements_list = $(product_categories[idx]).find('li');
            for(let index = 0; index < agent_elements_list.length; index++) {
                $(agent_elements_list[index]).show();
            }
        }
    }
});

$(document).ready(function() {
    load_map_script();
});

$('#display-name').on('keydown', function(e) {
    if(e.target.value.length >= 40) {
        if(e.key != 'Backspace' && e.key != 'Delete' && e.key != 'ArrowLeft' && e.key != 'ArrowRight') {
            e.preventDefault()
        }
    }
    if(e.target.value.length == 0) {
        document.getElementById("authenticate-details-error").innerHTML = "";
    }
});

function easyassist_show_function_fail_modal(code=EASYASSIST_FUNCTION_FAIL_DEFAULT_CODE, message=EASYASSIST_FUNCTION_FAIL_DEFAULT_MESSAGE) {
    var current_time = Date.now();
    var difference = (current_time - easyassist_function_fail_time) / 1000;

    if(difference < 30) {
        return;
    } else if(difference >= 300) {
        easyassist_function_fail_count = 0;
    }

    if(message == null) {
        message = EASYASSIST_FUNCTION_FAIL_DEFAULT_MESSAGE;
    }

    if(easyassist_function_fail_count <= 6) {
        if(code != null) {
            message = message + " [" + code + "]"
        }
        document.getElementById("easyassist_function_fail_message").innerHTML = message;
        easyassist_display_function_fail_modal();
    }

    easyassist_function_fail_count++;
    easyassist_function_fail_time = Date.now();
}

function easyassist_display_function_fail_modal(){
    $("#easyassist_function_fail_modal").modal("show");
}

function easyassist_hide_function_fail_modal() {
    $("#easyassist_function_fail_modal").modal("hide");
}

function set_easyassist_current_session_local_storage_obj(key, value, is_meeting_storage=true) {
    try{
        let local_storage_name = "";
        if(is_meeting_storage) {
            local_storage_name = "easyassist_meeting_session";
        } else {
            local_storage_name = "easyassist_session";
        }

        let local_storage_obj = localStorage.getItem(local_storage_name);
        let easyassist_session_id = meeting_id;

        if(local_storage_obj) {
            local_storage_obj = JSON.parse(local_storage_obj);
            local_storage_obj[easyassist_session_id][key] = value;
            localStorage.setItem(local_storage_name, JSON.stringify(local_storage_obj));
        }
    }catch(err){
        console.log("ERROR: set_easyassist_current_session_local_storage_obj ", err);
    }
}

function easyassist_create_local_storage_obj() {
    if(localStorage.getItem("easyassist_meeting_session") == null){
        var local_storage_json_object = {};
        local_storage_json_object[meeting_id] = {};
        localStorage.setItem("easyassist_meeting_session", JSON.stringify(local_storage_json_object));
    } else {
        var local_storage_obj = localStorage.getItem("easyassist_meeting_session");
        local_storage_obj = JSON.parse(local_storage_obj);
        if(!local_storage_obj.hasOwnProperty(meeting_id)) {
            var local_storage_json_object = {};
            local_storage_json_object[meeting_id] = {};
            localStorage.setItem("easyassist_meeting_session", JSON.stringify(local_storage_json_object));
        }
    }
}

function easyassist_clear_local_storage() {
    localStorage.removeItem("easyassist_meeting_session");
}

function get_easyassist_current_session_local_storage_obj() {
    try {
        let local_storage_obj = null;
        let easyassist_session_id = meeting_id;

        if(localStorage.getItem("easyassist_meeting_session") != null) {
            local_storage_obj = localStorage.getItem("easyassist_meeting_session");
            local_storage_obj = JSON.parse(local_storage_obj);
            if(local_storage_obj.hasOwnProperty(easyassist_session_id)) {
                local_storage_obj = local_storage_obj[easyassist_session_id];
            } else {
                return null; 
            }
        }
        return local_storage_obj;
    } catch (error) {
        return null;
    }
}

function easyassist_send_clear_meeting_cookie_over_socket() {

    if(is_reverse_cobrowsing_enabled() && window.socket_message_sender == "agent") {
        json_string = JSON.stringify({
            "type": "clear_meeting_cookie"
        });
    
        encrypted_data = easyassist_custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };
    
        send_message_over_sync_utils_easyassist_socket(encrypted_data, window.socket_message_sender);
    }

}
