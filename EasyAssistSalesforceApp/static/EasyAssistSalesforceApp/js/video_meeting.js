var jitsi_meet_api = null;
var save_notes_timer = null;
var display_name = "";
var chat_history = [];
var chat_history_timer = null;
var is_video_muted = true;
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
var is_file_attachment = false;
var file_attachment_name = null;
var is_meeting_interval_set = false; 
var client_join_time_stamp = null;
var show_time_notification = false;
var participant_location_detail_obj = {};
var my_current_location = null;


function stripHTML(text){
   var regex = /(<([^>]+)>)/ig;
   return text.replace(regex, "");
}

function remove_special_characters_from_str(text) {
    var regex = /:|;|'|"|=|-|\$|\*|%|!|~|\^|\(|\)|\[|\]|\{|\}|\[|\]|#|<|>|\/|\\/g;
    text = text.replace(regex, "");
    return text;
}

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
    is_mic_on = value;
}

function start_with_video_muted(value) {
    is_video_on = value;
}

function get_cookie(cookiename) {
    var cookie_name = cookiename + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var cookie_array = decodedCookie.split(';');
    for (var i = 0; i < cookie_array.length; i++) {
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
}

function hide_meeting_chat_box(el) {
    if(window.outerWidth >= 600 && window.outerHeight >= 600) {
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
    if(window.outerWidth >= 600 && window.outerHeight >= 600) {
        hide_all_meeting_options();
    }
}

function show_add_members(el) {
    hide_all_meeting_options();
    document.getElementById("show-add-members").style.display = 'none';
    document.getElementById("hide-add-members").style.display = 'block';
    document.getElementById("cogno-lobby-add-members").style.display = 'block';
    document.getElementById("invite-people-mail-error").style.display = 'none';

    get_list_of_participants();
    show_option_backdrop();
}

function hide_add_members(el) {
    if(window.outerWidth >= 600 && window.outerHeight >= 600) {
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
    if(window.outerWidth >= 600 && window.outerHeight >= 600) {
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
    if(window.outerWidth >= 600 && window.outerHeight >= 600) {
        hide_all_meeting_options();
    }
}

function show_small_device_options() {
    document.getElementById("cogno-lobby-options").style.display = 'block';
    document.getElementById("show-small-device-btn").style.display = 'none';
    document.getElementById("hide-small-device-btn").style.display = 'block';

    if(is_agent == 'True') {
        $('#show-add-members button').click();
    } else {
        $('#show-meeting-chatbox button').click();
    }
}

function hide_small_device_options() {
    document.getElementById("cogno-lobby-options").style.display = 'none';
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
        for(var idx = 0; idx < participant_ids.length; idx++) {
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
    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/check-meeting-ended-or-not/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
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

function init() {
    if(is_agent == 'True' && is_invited_agent == 'False'){
        setTimeout(function(){
            iframe.contentWindow.postMessage(JSON.stringify({
                'key': 'START_RECORDING',
                'meeting_id': meeting_id
            }), "*");
        },5000)
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
    }
    document.getElementById("meeting-lobby-container").style.display = "none";

    var width = window.outerWidth;
    var height = window.outerHeight;
    if (width >= 600 && height >= 600) {
        document.getElementById("show-option-btn-sm").style.display = "none";
        document.getElementById("cogno-lobby-options").style.display = "block";
    } else {
        document.getElementById("cogno-lobby-options").style.display = "none";
        document.getElementById("show-option-btn-sm").style.display = "block";
    }

    if (is_agent == 'True') {
        if (screen_recorder_on == false) {
            if (is_cobrowsing_active == 'False') {
                start_recording();
            }
        }
    } else {
        toggle_background_music(false);
        // save customer's location
        if (window.navigator.geolocation) {
            window.navigator.geolocation.getCurrentPosition(accept_location_request, cancel_location_request);
        }
        if (is_cobrowsing_active == "False") {
            if (audio_recorder_on == false) {
                client_join_time_stamp = new Date()
                client_join_time_stamp = client_join_time_stamp.getHours() + ':' + client_join_time_stamp.getMinutes() + ':' + client_join_time_stamp.getSeconds()
                start_client_audio_record();
            }
        }
    }
}

function get_list_of_participants() {
    var html = "";
    for(var idx = 0; idx < participant_ids.length; idx++) {
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
            html += [
                        '</div>',
                        '<div class="col-2">',
                            '<div class="dropdown">',
                                '<button class="btn cogno-lobby-fa-ellipsis-h" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">',
                                    '<i class="fa fa-ellipsis-h fa-lg"></i>',
                                '</button>',
                                '<div class="dropdown-menu dropdown-menu-right" aria-labelledby="dropdownMenuButton">',
                                    '<a class="dropdown-item" href="#" onclick="mute_participant(this, \'' + participant_ids[idx]['id'] + '\')">',
                                        '<svg width="11" height="15" viewBox="0 0 11 15" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                            '<path d="M10.4107 6.75C10.709 6.75 10.9556 6.96162 10.9946 7.23617L11 7.3125V7.6875C11 10.3571 8.83532 12.544 6.09006 12.7363L6.08929 14.4375C6.08929 14.7482 5.82545 15 5.5 15C5.20167 15 4.95511 14.7884 4.91609 14.5138L4.91071 14.4375L4.91073 12.7363C2.22611 12.5487 0.0965132 10.4535 0.00319021 7.86476L0 7.6875V7.3125C0 7.00184 0.263832 6.75 0.589286 6.75C0.887618 6.75 1.13417 6.96162 1.17319 7.23617L1.17857 7.3125V7.6875C1.17857 9.80776 2.93421 11.5366 5.13354 11.6217L5.30357 11.625H5.69643C7.91765 11.625 9.72882 9.94916 9.81799 7.8498L9.82143 7.6875V7.3125C9.82143 7.00184 10.0853 6.75 10.4107 6.75ZM5.5 0C7.23575 0 8.64286 1.34315 8.64286 3V7.5C8.64286 9.15685 7.23575 10.5 5.5 10.5C3.76425 10.5 2.35714 9.15685 2.35714 7.5V3C2.35714 1.34315 3.76425 0 5.5 0ZM5.5 1.125C4.41515 1.125 3.53571 1.96447 3.53571 3V7.5C3.53571 8.53553 4.41515 9.375 5.5 9.375C6.58485 9.375 7.46429 8.53553 7.46429 7.5V3C7.46429 1.96447 6.58485 1.125 5.5 1.125Z" fill="#4D4D4D"/>',
                                        '</svg>',
                                        'Mute ' + participant_ids[idx]['participant_name'] + '</a>',
                                    '<a class="dropdown-item" href="#" onclick="kick_participant(this, \'' + participant_ids[idx]['id'] + '\')">',
                                        '<svg width="13" height="13" viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                            '<path d="M9.59466 6.18898C11.4754 6.18898 13 7.71368 13 9.59449C13 11.4753 11.4754 13 9.59466 13C7.71395 13 6.18933 11.4753 6.18933 9.59449C6.18933 7.71368 7.71395 6.18898 9.59466 6.18898ZM6.20311 7.42692C6.01941 7.71378 5.8711 8.0255 5.76435 8.3559L1.39309 8.35607C1.13663 8.35607 0.928728 8.56399 0.928728 8.82046V9.38226C0.928728 9.78823 1.1058 10.174 1.41363 10.4387C2.19257 11.1084 3.36649 11.4527 4.95102 11.4527C5.3218 11.4527 5.67013 11.4339 5.99624 11.3964C6.15035 11.7061 6.34465 11.9932 6.5714 12.2511C6.07473 12.3383 5.53424 12.3815 4.95102 12.3815C3.16199 12.3815 1.77582 11.9749 0.808164 11.1429C0.295122 10.7018 0 10.0589 0 9.38226V8.82046C0 8.05104 0.623709 7.4273 1.39309 7.4273L6.20311 7.42692ZM11.6436 8.20273L8.20298 11.6435C8.59961 11.9134 9.07871 12.0712 9.59466 12.0712C10.9625 12.0712 12.0713 10.9624 12.0713 9.59449C12.0713 9.07851 11.9135 8.59939 11.6436 8.20273ZM9.59466 7.11775C8.22687 7.11775 7.11806 8.22663 7.11806 9.59449C7.11806 10.1105 7.27583 10.5896 7.54576 10.9862L10.9864 7.54548C10.5897 7.27553 10.1106 7.11775 9.59466 7.11775ZM4.95102 0C6.66077 0 8.04678 1.38609 8.04678 3.09592C8.04678 4.80575 6.66077 6.19184 4.95102 6.19184C3.24128 6.19184 1.85526 4.80575 1.85526 3.09592C1.85526 1.38609 3.24128 0 4.95102 0ZM4.95102 0.928776C3.7542 0.928776 2.78399 1.89904 2.78399 3.09592C2.78399 4.2928 3.7542 5.26306 4.95102 5.26306C6.14784 5.26306 7.11806 4.2928 7.11806 3.09592C7.11806 1.89904 6.14784 0.928776 4.95102 0.928776Z" fill="#4D4D4D"/>',
                                        '</svg>',
                                        'Remove ' + participant_ids[idx]['participant_name'] + '</a>',
                                '</div>',
                            '</div>',
                        '</div>',
                    '</div>',
                '</div>'
            ].join('');
        }
    }
    document.getElementById("cogno-lobby-members-list").innerHTML = html;
}

function kick_participant(o, id) {

    setTimeout(function() {
        document.getElementById("agent-" + id).remove();
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
    var url = window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/cobrowse-data-collect/" + meeting_id + "/" + form_id + "/";
    window.open(url);
}

// Adding jitsi event listeners
function add_event_listeners() {

    // Event notifications fired when the local user has left the video conference
    jitsi_meet_api.addEventListener("videoConferenceLeft", function(e) {
        remove_participants_socket(my_id)
        stop_recording();
        if (is_agent == "True") {
            if (is_cobrowsing_active == 'True') {
                window.location = "/easy-assist-salesforce/meeting-ended/" + meeting_id + "?is_meeting_cobrowsing=true&salesforce_token="+window.SALESFORCE_TOKEN;
            } else {
                save_meeting_duration();
            }
            update_agent_join_status('false')
        } else {
            stop_client_audio_record();
            if (is_cobrowsing_active == 'True') {
                if(allow_meeting_feedback == 'True'){
                    window.location = "/easy-assist-salesforce/meeting-ended/" + meeting_id + "?is_meeting_cobrowsing=true&is_feedback=true";
                }else{
                    window.location = "/easy-assist-salesforce/meeting-ended/" + meeting_id + "?is_meeting_cobrowsing=true&is_feedback=false";
                }
            } else {
                if(allow_meeting_feedback == 'True'){
                    window.location = "/easy-assist-salesforce/meeting-ended/" + meeting_id + "?is_feedback=true";
                }
                else{
                    window.location = "/easy-assist-salesforce/meeting-ended/" + meeting_id + "?is_feedback=false";
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
            display_name = remove_special_characters_from_str(display_name);
            update_display_name_socket();
        }
    });

    jitsi_meet_api.addEventListener("audioMuteStatusChanged",function(e){
        is_audio_muted = e["muted"]
        if(is_audio_muted == true){
            stream.getAudioTracks()[0].enabled = false;
        }
        else{
            stream.getAudioTracks()[0].enabled = true;
        }
    });
}

window.onresize = function(e) {
    var width = e.target.innerWidth;
    var height = e.target.innerHeight;

    if (width >= 600 && height >= 600) {
        if(is_meeting_joined) {
            if(document.getElementById("cogno-lobby-options").style.display != 'block') {
                $('#hide-small-device-btn button').click();
                document.getElementById("show-option-btn-sm").style.display = 'none';
                document.getElementById("cogno-lobby-options").style.display = 'block';
            }
        }
    } else {
        if(is_meeting_joined) {
            if(document.getElementById("show-option-btn-sm").style.display != 'block') {
                hide_all_meeting_options();
                document.getElementById("cogno-lobby-options").style.display = 'none';
                document.getElementById("show-option-btn-sm").style.display = 'block';
            }
        }
    }
}

window.onload = function(){
    if(is_cobrowsing_active == 'True'){
        if(show_cobrowsing_meeting_lobby == 'False'){
            is_video_on = true
            is_mic_on = false
            join_meeting();
        }
    }
}

function join_meeting() {
    is_meeting_joined = true;
    var toolbar_options = [
                'microphone', 'camera', 'closedcaptions', 'desktop', 'fullscreen',
                'fodeviceselection', 'hangup', 'profile', , 'etherpad', 'settings',
                'videoquality', 'stats', 'tileview',
                'e2ee'
            ]

    var is_mobile = detect_mobile();
    if(is_mobile == true){
        toolbar_options = [
                'microphone', 'camera', 'closedcaptions', 'fullscreen',
                'fodeviceselection', 'hangup', 'profile', , 'etherpad', 'settings',
                'videoquality', 'stats', 'tileview',
                'e2ee'
            ]
    }

    // Enable chat functionality
    enable_chat_socket();

    document.getElementById("meeting-lobby").style.display = "none"
    document.getElementById("meeting-msg").innerHTML = "<h2>Joining the meeting please wait...</h2>"
    if (is_agent == 'True') {
        display_name = agent_name
    } else {
        display_name = client_name
    }
    var participant = { "participant_name": display_name, "id": my_id }
    participant_ids.push(participant)
    domain = meeting_host_url;

    options = {
        roomName: meeting_id,
        configOverwrite: {
            startWithVideoMuted: is_video_on,
            startWithAudioMuted: is_mic_on,
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
    jitsi_meet_api = new JitsiMeetExternalAPI(domain, options);

    jitsi_meet_api.executeCommand('subject', "Meeting");

    if (is_cobrowsing_active == "False") {
        jitsi_meet_api.executeCommand('toggleTileView');
    }

    // Adding event listeners
    add_event_listeners();

    iframe = jitsi_meet_api.getIFrame();

    setTimeout(function() { init(); }, 2000);
}

function check_agent_connected_or_not() {
    request_params = {
        "meeting_id": meeting_id,
    };

    json_params = JSON.stringify(request_params);

    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/check-agent-connected-or-not/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
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

    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/update-agent-join-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
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
    enable_chat_socket();
    if (is_agent == 'True') {
        update_agent_join_status('true');
        if(is_cobrowsing_active == 'True'){
            join_meeting();
        }else{
            join_meeting();
        }
    }else if(is_invited_agent == 'True'){
            join_meeting();
    } else {
        client_name = display_name;
        toggle_background_music(true);
        document.getElementById("meeting-lobby").style.display = "none"
        document.getElementById("meeting-msg").innerHTML = "<h2>Please wait, the meeting host will let you in soon.</h2>"
        check_agent_connected_or_not();
    }
}

// Save meeting duration.
function save_meeting_duration() {
    request_params = {
        "meeting_id": meeting_id,
    };

    json_params = JSON.stringify(request_params);

    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/save-meeting-duration/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                window.location = "/easy-assist-salesforce/meeting-ended/" + meeting_id + "?salesforce_token=" + window.SALESFORCE_TOKEN;
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

    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/save-meeting-chats/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
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
        display_name = remove_special_characters_from_str(display_name);
        if (display_name == "") {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Please enter your name.";
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
        display_name = remove_special_characters_from_str(display_name);
        if (display_name == "") {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Please enter your name.";
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

    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/authenticate-meeting-password/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
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

    encrypted_data = custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/save-meeting-notes/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                console.log('Notes saved')
            }
        }
    }
    xhttp.send(params);
}


async function stop_recording() {
    if (screen_recorder_on) {
        screen_recorder_on = false;
        recorder.stop();
        stream.getVideoTracks()[0].stop();
    }
}

async function stop_client_audio_record() {
    if (audio_recorder_on) {
        audio_recorder_on = false;
        recorder_client.stop();
        stream_client.getAudioTracks()[0].stop();
    }
}

// Start Recording the selected screen

function start_recording(){
    console.log("Recording Start")
}



/*async function start_recording() {
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
                show_media_unavailable_modal('microphone');
                return;
            }

            try {
                displayStream = await navigator.mediaDevices.getDisplayMedia({ video: { mediaSource: "screen" } });
                [videoTrack] = displayStream.getVideoTracks();
            } catch {
                screen_recorder_on = false;
                is_recording_cancel = true;
                show_media_unavailable_modal('camera');
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
            const chunks = [];
            session_id = uuidv4();
            var filename = session_id + '.webm';
            var count = 0;

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
                    url: "/easy-assist-salesforce/save-screen-recorded-data/",
                    type: "POST",
                    data: formData,
                    processData: false,
                    contentType: false,
                    headers: {
                        'X-CSRFToken': get_csrfmiddlewaretoken()
                    },
                    success: function(response) {
                        response = custom_decrypt(response.Response);
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
*/

function start_client_audio_record(){
    console.log("GETTING CLIENT AUDIO")
}

// // Start Recording the selected screen
// async function start_client_audio_record() {
//     if (audio_recorder_on == false) {
//         show_toast("Your audio will be recorded for quality and training purposes.")
//     }
//     if (audio_recorder_on) {
//         audio_recorder_on = false;
//         recorder_client.stop();
//     } else {
//         audio_recorder_on = true;
//         try {
//             audioStream_client = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
//             [audioTrack_client] = audioStream_client.getAudioTracks();
//             stream_client = new MediaStream([audioTrack_client]);
//         } catch {
//             audio_recorder_on = false;
//             return;
//         }
//         recorder_client = new MediaRecorder(stream_client);
//         const chunks = [];
//         var filename = my_id + "_client" + '.webm';
//         var count = 0;

//         function save_data(blob) {
//             var file = new File([blob.data], filename, {
//                 type: 'video/webm'
//             });
//             var formData = new FormData();
//             formData.append("uploaded_data", file);
//             formData.append("filename", file.name);
//             formData.append("meeting_id", meeting_id);
//             formData.append("time_stamp",client_join_time_stamp);

//             $.ajax({
//                 url: "/easy-assist-salesforce/save-client-recorded-data/",
//                 type: "POST",
//                 data: formData,
//                 processData: false,
//                 contentType: false,
//                 headers: {
//                     'X-CSRFToken': get_csrfmiddlewaretoken()
//                 },
//                 success: function(response) {
//                     response = custom_decrypt(response.Response);
//                     response = JSON.parse(response);
//                     if (response["status"] == 200) {
//                         console.log("Audio saved.")
//                     } else {
//                         console.log("error")
//                     }
//                 },
//                 error: function(xhr, textstatus, errorthrown) {
//                     console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
//                 }
//             });
//         }
//         recorder_client.ondataavailable = blob => save_data(blob);
//         recorder_client.start(5000);
//     }
// }

// Save file attachment to server
function save_file_to_server(e) {
    var upload_attachment_data = document.querySelector('#meeting-file-input').files[0]
    document.querySelector('#meeting-file-input').value = '';

    if(upload_attachment_data == undefined || upload_attachment_data == null) {
        show_toast("Please choose a file.");
        return;
    }

    if(check_malicious_file(upload_attachment_data.name)) {
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
            "session_id":session_id
        };

        json_string = JSON.stringify(json_string);

        encrypted_data = custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/upload-cognovid-file-attachment/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response.status == 200) {
                    message = response.src;
                    file_attachment_name = message
                    message = '<a href="' + message + "?vctoken="+meeting_id + '" target="_blank">File Attachment</a>'
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
function save_chat_aduit_trail(message, sender) {
    var current_date = new Date()
    var time = current_date.getHours() + ":" + current_date.getMinutes();
    clearTimeout(chat_history_timer);
    if(is_file_attachment == true){
        json_string = JSON.stringify({
            "message": file_attachment_name,
            "sender": sender,
            "type": "attachment",
            "time": time
        });
    }else{
        json_string = JSON.stringify({
            "message": message,
            "sender": sender,
            "type": "text",
            "time": time
        });
    }
    is_file_attachment = false
    file_attachment_name = null;
    chat_history.push(json_string)
    chat_history_timer = setTimeout(save_meeting_chats, 1000)

}

function deny_participant_entry(id) {
    if (client_websocket_open && client_websocket != null) {
        client_websocket.send(JSON.stringify({
            "message": {
                "type": "5",
                "client_id": id,
                "status": false
            }
        }));
    } else {
        create_chat_socket(room_id, "agent");
    }

}

function admin_participant(id) {
    if (client_websocket_open && client_websocket != null) {
        client_websocket.send(JSON.stringify({
            "message": {
                "type": "5",
                "client_id": id,
                "status": true
            }
        }));
    } else {
        create_chat_socket(room_id, "agent");
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
    } else {
        create_chat_socket(room_id, "agent");
    }

}

// Send message over socket
function send_message_over_chat_socket(message, sender, display_name) {
    if (client_websocket_open && client_websocket != null) {
        client_websocket.send(JSON.stringify({
            "message": {
                "type": "0",
                "header": {
                    "sender_id": my_id,
                    "sender": sender,
                    "name": display_name
                },
                "body": message
            }
        }));
    } else {
        create_chat_socket(room_id, "agent");
    }
}

function remove_participant_from_list(id) {
    new_list = []
    for (var i = 0; i < participant_ids.length; i++) {
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
    } else {
        create_chat_socket(room_id, "agent");
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
    } else {
        create_chat_socket(room_id, "agent");
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
    } else {
        create_chat_socket(room_id, "agent");
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
    } else {
        create_chat_socket(room_id, "agent");
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
    } else {
        create_chat_socket(room_id, "agent");
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
    } else {
        create_chat_socket(room_id, "agent");
    }
}

// Open websocket
function open_chat_websocket() {
    client_websocket_open = true;
    console.log("Chat WebSocket is opened");
    json_string = JSON.stringify({
        "type": "html"
    });
    create_chat_socket(json_string, "agent");
}

// Close websocket
function close_chat_websocket() {
    client_websocket_open = false;
    console.log("WebSocket is closed");
    var description = "agent websocket is closed";
}

// Check websocket status
function check_socket_status(e) {
    console.error("WebSocket error observed:", e);
    var description = "error occured agent websocket. " + e.data;
}

// Create the socket
function create_chat_socket(room_id, sender) {
    ws_scheme = window.location.protocol == "http:" ? "ws" : "wss";
    url = ws_scheme + '://' + window.location.host + '/ws/meet/' + room_id + '/' + sender + "/";
    if (client_websocket == null) {
        client_websocket = new WebSocket(url);
        client_websocket.onmessage = function(e) {
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
                var name = data["message"]["header"]["name"]
                if(msg_sender == "agent") {
                    name = 'Agent: ' + name
                } else {
                    name = 'Customer: ' + name
                }
                if (data["message"]["header"]["sender_id"] != my_id) {
                    current_time = new Date().toLocaleTimeString('en-US', { hour: 'numeric', hour12: true, minute: 'numeric' });
                     html = [
                        '<div class="message message-left" id="meeting_chat_box_sender">',
                            '<div class="bubble bubble-light">',
                                '<span class="message-sender">' + name + '</span>',
                                '<div class="mt-1">',
                                    message["body"],
                                '</div>',
                            '</div>',
                            '<div class="message-timer">',
                                current_time,
                            '</div>',
                        '</div>'
                    ].join('');
                    document.getElementById("meeting_chat_room").innerHTML += html
                }
                if (document.getElementById("cogno-lobby-meeting-chat").style.display == 'none') {
                    if(is_meeting_joined) {
                        document.getElementById("meeting-chatbox-btn").click();
                    }
                }
                save_chat_aduit_trail(message["body"], msg_sender)
                scroll_to_bottom();
                is_message_sender = false;
            } else if (type == "1") {
                id = data["message"]["header"]["id"]
                if (my_id == id) {
                    // alert("You have been removed from this meeting.");
                    show_toast("You have been removed from this meeting.")
                    window.location.href = "/easy-assist-salesforce/meeting-ended/" + meeting_id
                }
            } else if (type == "2") {
                var objs = data["message"]["participant_id"]
                participant_ids.push(objs[0])
                jsonObject = participant_ids.map(JSON.stringify);
                uniqueSet = new Set(jsonObject);
                uniqueArray = Array.from(uniqueSet).map(JSON.parse);
                participant_ids = uniqueArray
            } else if (type == "3") {
                var objs = data["message"]["participant_id"]
                remove_participant_from_list(objs)

                if(data["message"]["is_agent"] == "True" && objs != my_id) {
                    show_toast("Agent has left the session");
                }
            } else if (type == "4") {
                var id = data["message"]["id"]
                var name = data["message"]["name"]
                if (is_agent == "True") {
                    show_request_modal(id, name);
                }
            } else if (type == "5") {
                var id = data["message"]["client_id"]
                var status = data["message"]["status"]
                $("#request_participant-" + id).modal('hide')
                if (status == true) {
                    if (id == my_id) {
                        join_meeting();
                    }
                } else {
                    if (id == my_id) {
                        // alert("You are not allowed to join this meeting.")
                        show_toast("You have been removed from this meeting.")
                        window.location.reload()
                    }
                }
            } else if(type == "6") {
                var name = data["message"]["name"];
                var participant_id = data["message"]["participant_id"];
                if(participant_id == my_id) {
                    if(is_audio_muted == false) {
                        show_toast("You have been muted by " + name);
                        mute_meeting_audio();
                    }
                }
            } else if(type == "7") {
                var participant_id = data["message"]["participant_id"];
                var participant_name = data["message"]["participant_name"];
                update_participant_name_in_list(participant_name, participant_id);
            } else if(type == "8") {
                var participant_id = data["message"]["participant_id"];
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
            }
        };
        client_websocket.onerror = check_socket_status;
        client_websocket.onopen = open_chat_websocket;
        client_websocket.onclose = close_chat_websocket;
        console.log("socket has been created");
    }
}

// Enable websocket
function enable_chat_socket() {
    room_id = meeting_id
    if (is_agent == 'True') {
        sender = "agent"
    } else {
        sender = "client"
    }
    create_chat_socket(room_id, sender)
}

// Send attachment to chat
function send_attachmet_to_chat(message) {
    is_message_sender = true
    current_time = new Date().toLocaleTimeString('en-US', { hour: 'numeric', hour12: true, minute: 'numeric' });
    var sender_name = '';
    if(is_agent == 'True') {
        sender_name = 'Agent: ' + display_name
    } else {
        sender_name = 'Customer: ' + display_name
    }

    html = [
        '<div class="message message-right" id="meeting_chat_box_reciever">',
            '<div class="bubble bubble-dark">',
                '<span class="message-sender">' + sender_name + '</span>',
                '<div class="mt-1">',
                    message,
                '</div>',
            '</div>',
            '<div class="message-timer">',
                current_time,
            '</div>',
        '</div>'
    ].join('');
    is_file_attachment = true
    document.getElementById("meeting_chat_room").innerHTML += html
    send_message_over_chat_socket(message, sender, display_name)
    document.getElementById("meeting_text_message").value = "";
}

// Send message to chat
function send_message_to_chat() {
    is_message_sender = true
    message = document.getElementById("meeting_text_message").value;
    message = stripHTML(message);
    message = remove_special_characters_from_str(message);

    if (message == "") {
        return;
    }
    current_time = new Date().toLocaleTimeString('en-US', { hour: 'numeric', hour12: true, minute: 'numeric' });
    var sender_name = '';
    if(is_agent == 'True') {
        sender_name = 'Agent: ' + display_name
    } else {
        sender_name = 'Customer: ' + display_name
    }
    html = [
        '<div class="message message-right" id="meeting_chat_box_reciever">',
            '<div class="bubble bubble-dark">',
                '<span class="message-sender">' + sender_name + '</span>',
                '<div class="mt-1">',
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
    send_message_over_chat_socket(message, sender, display_name)
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

    encrypted_data = custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/get-meet-support-agents/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);

            div_inner_html = "";
            if (response.status == 200) {
                support_agents = response.support_agents;
                if (Object.keys(support_agents).length > 0) {
                    var product_counter = 0;
                    for(var product_category in support_agents) {
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
                            for(var idx = 0; idx < support_agents[product_category].length; idx ++) {
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

    encrypted_data = custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/get-meeting-forms/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);

            div_inner_html = "";
            if (response.status == 200) {
                meeting_forms_list = response.meeting_forms;
                if (meeting_forms_list.length > 0) {
                    for(var idx = 0; idx < meeting_forms_list.length; idx++) {
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

function update_participant_name_in_list(participant_name, participant_id) {

    for(var idx = 0; idx < participant_ids.length; idx++) {
        if(participant_ids[idx]['id'] == participant_id) {
            participant_ids[idx]['participant_name'] = participant_name;
        }
    };
}

// Ask another agents to join meeting.
function join_cobrowsing_meeting(element, agent_id) {

    json_string = JSON.stringify({
        "id": meeting_id,
        "support_agents": [agent_id]
    });

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Requesting...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist-salesforce/request-agent-meeting/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
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
    const regEmail = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;

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

    encrypted_data = custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);
    element.innerHTML = "Inviting...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/invite-video-meeting-email/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
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

//     encrypted_data = custom_encrypt(json_params);

//     encrypted_data = {
//         "Request": encrypted_data
//     };

//     var params = JSON.stringify(encrypted_data);
//     element.innerHTML = "Inviting...";
//     var xhttp = new XMLHttpRequest();
//     xhttp.open("POST", "/easy-assist-salesforce/invite-video-meeting-phone/", true);
//     xhttp.setRequestHeader('Content-Type', 'application/json');
//     xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
//     xhttp.onreadystatechange = function() {
//         if (this.readyState == 4 && this.status == 200) {
//             response = JSON.parse(this.responseText);
//             response = custom_decrypt(response.Response);
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
    save_client_location_details();

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
        } else {
            my_current_location = "None";
            send_location_to_agent_over_socket(my_current_location);
        }
    });
}

function save_client_location_details() {
    request_params = {
        "meeting_id": meeting_id,
        "client_name": client_name,
        "longitude": longitude,
        "latitude": latitude,
    };
    json_params = JSON.stringify(request_params);

    encrypted_data = custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist-salesforce/save-client-location-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
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
    var audio_player = document.getElementById("audioplayer");
    if(!audio_player) {
        return;
    }
    if(play_music) {
        audio_player.play();
    } else {
        audio_player.pause();
    }
}

function save_screenshot() {
    if(displayStream == null || displayStream == undefined) {
        show_toast("Not able to save the screnshot. Please try again.");
        return;
    }

    try {
        var captureStreamTrack = displayStream.getVideoTracks()[0];
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

            encrypted_data = custom_encrypt(json_string);
            encrypted_data = {
                "Request": encrypted_data
            };

            var params = JSON.stringify(encrypted_data);
            var xhttp = new XMLHttpRequest();
            xhttp.open("POST", "/easy-assist-salesforce/save-meeting-screenshot/", true);
            xhttp.setRequestHeader('Content-Type', 'application/json');
            xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
            xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    response = JSON.parse(this.responseText);
                    response = custom_decrypt(response.Response);
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

function check_malicious_file(file_name) {
    if(file_name.split('.').length != 2) {
        show_toast("Please do not use .(dot) except for extension");
        return true;
    }

    var allowed_files_list = [
        "png", "jpg", "jpeg", "svg", "bmp", "gif", "tiff", "exif", "jfif", "webm", "mpg", 
        "mp2", "mpeg", "mpe", "mpv", "ogg", "mp4", "m4p", "m4v", "avi", "wmv", "mov", "qt",
        "flv", "swf", "avchd","mp3", "aac", "pdf", "xls", "xlsx", "json", "xlsm", "xlt", "xltm", "zip"
    ];

    var file_extension = file_name.substring(file_name.lastIndexOf(".") + 1, file_name.length);
    file_extension = file_extension.toLowerCase();

    if(allowed_files_list.includes(file_extension) == false) {
        show_toast("." + file_extension + " files are not allowed");
        return true;
    }
    return false;
}

$(document).click(function(event) {
    if(event.target.id == "cogno-lobby-option-backdrop") {
        var width = window.outerWidth;
        var height = window.outerHeight;

        if (width >= 600 && height >= 600) {
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
        for(var idx = 0; idx < product_categories.length; idx ++) {
            var product_category = $(product_categories[idx]).find('.product-category-btn-group').find('button:eq(0)').text();
            product_category = product_category.toLowerCase();

            if(product_category.indexOf(search_text) > -1) {
                var agent_elements_list = $(product_categories[idx]).find('li');
                for(var index = 0; index < agent_elements_list.length; index++) {
                    $(agent_elements_list[index]).show();
                }

                $(product_categories[idx]).parent().show();
                if($(product_categories[idx]).find('.product-category-btn-group').hasClass('collapsed') == false) {
                    $(product_categories[idx]).find('.product-category-btn-group').click();
                }
                continue;
            }

            var agent_matched_list = [];
            var agent_elements_list = $(product_categories[idx]).find('li');
            for(var index = 0; index < agent_elements_list.length; index++) {
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
                for(var index = 0; index < agent_matched_list.length; index ++) {
                    $(agent_matched_list[index]).show();
                }
                $(product_categories[idx]).parent().show();
                if($(product_categories[idx]).find('.product-category-btn-group').hasClass('collapsed')) {
                    $(product_categories[idx]).find('.product-category-btn-group').click();
                }
            }
        }
    } else {
        var product_categories = document.getElementsByClassName("product-category-container");
        for(var idx = 0; idx < product_categories.length; idx ++) {
            $(product_categories[idx]).parent().show();

            if($(product_categories[idx]).find('.product-category-btn-group').hasClass('collapsed') == false) {
                $(product_categories[idx]).find('.product-category-btn-group').click();
            }

            var agent_elements_list = $(product_categories[idx]).find('li');
            for(var index = 0; index < agent_elements_list.length; index++) {
                $(agent_elements_list[index]).show();
            }
        }
    }
});