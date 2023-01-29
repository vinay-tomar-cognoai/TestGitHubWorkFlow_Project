const CUSTOMER_HEARTBEAT_FREQUENCY = 10000;
let meeting = null;
let client_websocket = null;
let save_notes_timer = null;
let client_websocket_open = false;
let displayStream = null;
let my_current_location = null;
let permit_interval = null;
let is_kicked = false;
let customer_heartbeat_interval = null;
let no_agent_connect_timer_interval = null;
let client_display_name = ''
let initial_customer_waiting_message = "Please wait, the meeting host will let you in soon.";
let is_mic_enabled = false;
let is_camera_enabled = false;
let is_lobby_audio_muted = false;
let is_meeting_interval_set = false;
let show_time_notification = false;
let is_highlighted_layout = false;
const TIMEOUT_ERROR_MESSAGE = 'We were not able to add you into the meeting, please try to join again after sometime.';


function toggle_mic(capture_audio=true){
    if(is_mic_enabled){
        document.getElementById('mic-enabled').style.display = 'none';
        document.getElementById('mic-disabled').style.display = 'block';        
    }else{
        document.getElementById('mic-enabled').style.display = 'block';
        document.getElementById('mic-disabled').style.display = 'none';        
    }
    is_mic_enabled = !is_mic_enabled;
    if(capture_audio) {
        capture_user_audio(is_mic_enabled);
    }
}

function toggle_camera(show_video_preview=true){
    if(is_camera_enabled){
        document.getElementById('camera-enabled').style.display = 'none';
        document.getElementById('camera-disabled').style.display = 'block';        
    }else{
        document.getElementById('camera-enabled').style.display = 'block';
        document.getElementById('camera-disabled').style.display = 'none';        
    }
    is_camera_enabled = !is_camera_enabled;
    if(show_video_preview) {
        capture_user_video(is_camera_enabled);
    }
}

function capture_user_video(value, is_lobby_page = false) {
    const constraints = {
      video: true,
    };
    let video_element = null;
    if(is_lobby_page){
        video_element = document.getElementById("cognomeet-video-element-lobby");
    } else {
        video_element = document.getElementById("cognomeet-lobby-video-element");
    }
    
    if(value) {
        navigator.mediaDevices.getUserMedia(constraints)
        .then((stream) => {
          video_element.srcObject = stream;
          video_element.style.display = "initial";
          if(is_lobby_page){
            document.getElementById("participant-initial-svg-lobby-page").style.display = 'none';
          } else {
            document.getElementById("participant-initial-svg").style.display = 'none';
          }
          video_element.style.background = 'initial';
        })
        .catch(function() {
            show_cognomeet_toast("Please grant camera permission.")
            video_element.style.background = '';
            video_element.style.display = "none";
            if(is_lobby_page){
                document.getElementById("participant-initial-svg-lobby-page").style.display = 'initial';
                toggle_lobby_camera(false);
              } else {
                document.getElementById("participant-initial-svg").style.display = 'initial';
                toggle_camera(false);
              }
        });
    } else {
        video_element.src = '';
        video_element.srcObject.getVideoTracks()[0].stop();
        video_element.srcObject = null;
        video_element.style.background = '';
        video_element.style.display = "none";
        if(is_lobby_page){
            document.getElementById("participant-initial-svg-lobby-page").style.display = 'initial';
        } else {
            document.getElementById("participant-initial-svg").style.display = 'initial';
        }
    }
}

function capture_user_audio(value) {
    const constraints = {
      audio: true,
    };

    if(value) {
        navigator.mediaDevices.getUserMedia(constraints)
        .catch(function() {
            show_cognomeet_toast("Please grant microphone permission.");
            toggle_mic(false);        
        });   
    }
}

function toggle_lobby_mic(capture_audio=true){
    if(is_mic_enabled){
        document.getElementById('mic-enabled-lobby').style.display = 'none';
        document.getElementById('mic-disabled-lobby').style.display = 'block';
    }else{
        document.getElementById('mic-enabled-lobby').style.display = 'block';
        document.getElementById('mic-disabled-lobby').style.display = 'none';
    }
    is_mic_enabled = !is_mic_enabled;
    if(capture_audio) {
        capture_user_audio(is_mic_enabled);
    }
}

function toggle_lobby_camera(show_video_preview=true){
    if(is_camera_enabled){
        document.getElementById('camera-enabled-lobby').style.display = 'none';
        document.getElementById('camera-disabled-lobby').style.display = 'block';        
    }else{
        document.getElementById('camera-enabled-lobby').style.display = 'block';
        document.getElementById('camera-disabled-lobby').style.display = 'none';        
    }
    is_camera_enabled = !is_camera_enabled;
    if(show_video_preview) {
        capture_user_video(is_camera_enabled,true);
    }
}

$(document).ready(function () {
    load_map_script();
    update_client_default_name();
});

function update_client_default_name(){
    let name_div = document.getElementById('meeting-joining-username');
    let initial_div = document.getElementById('participant-name-initials');
    if(!name_div) {
        return;
    }
    let participant_name = get_participant_name();
    if (participant_name) {
        name_div.value = participant_name;
        name_div.disabled = true;
        if(initial_div){
            initial_div.innerHTML = participant_name[0].toUpperCase();
        }
    } else {
        if(customer_name) {
            name_div.value = customer_name;
            if(initial_div){
                initial_div.innerHTML = customer_name[0].toUpperCase();
            }
        }
    }
}


window.onload = function () {
    cogno_meet_create_local_storage_obj();

    set_cogno_meet_current_session_local_storage_obj('session_id', session_id);
    set_cogno_meet_current_session_local_storage_obj('customer_name', customer_name);

    if (window.navigator.geolocation) {
        let geolocation_options = {
            enableHighAccuracy: true,
            timeout: 15000,
            maximumAge: 0
        };
        window.navigator.geolocation.getCurrentPosition(accept_location_request, cancel_location_request, geolocation_options);
    }
};

function load_map_script() {

    let params = JSON.stringify({});

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/cogno-meet/map-script/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                let src = response['src'];
                let script = document.createElement('script');
                script.type = 'text/javascript';
                script.defer = true;
                script.src = src;
                document.body.appendChild(script);
            }
        }
    }
    xhttp.send(params);
}

function cancel_location_request(pos) {
    latitude = null;
    longitude = null;
    my_current_location = "None";

    save_client_location_details(my_current_location, latitude, longitude);
}

function accept_location_request(pos) {
    latitude = pos.coords.latitude;
    longitude = pos.coords.longitude;

    let client_location = get_easyassist_cookie("client_location");
    if (client_location == "" || client_location == undefined) {
        get_client_location_from_coordinates();
    } else {
        client_location = client_location.split('|')
        if (client_location.length < 3 || client_location[0] != latitude || client_location[1] != longitude) {
            get_client_location_from_coordinates();
        } else {
            my_current_location = client_location.slice(2).join(" ");
            save_client_location_details(my_current_location, latitude, longitude);
        }
    }
}

function get_client_location_from_coordinates() {

    let geocoder = new google.maps.Geocoder();
    let latlng = new google.maps.LatLng(latitude, longitude);
    geocoder.geocode({ 'latLng': latlng }, function (results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            if (results[2]) {
                let address = results[2].formatted_address;
                my_current_location = address;
                save_client_location_details(address, latitude, longitude);

                let client_location = String(latitude) + "|" + String(longitude) + "|" + my_current_location;
                set_easyassist_cookie("client_location", client_location);
            } else {
                my_current_location = "None";
                save_client_location_details(my_current_location, latitude, longitude);
            }

        } else {
            my_current_location = "None";
            save_client_location_details(my_current_location, latitude, longitude);

        }
    });
}

function permit_request_to_agent_over_socket(participan_name) {
    let json_string = JSON.stringify({
        "type": "permit_request",
        "participant_name": participan_name,
        "status": 'request',
        "sender": 'client'
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_chat_socket(encrypted_data);
}

function check_meeting_username_and_password(session_id) {
    let display_name = "None";
    if (is_agent == 'False') {
        let error_message_element = document.getElementById("authenticate-details-error");
        error_message_element.innerHTML = "";
        display_name = document.getElementById("meeting-joining-username").value.trim();
        display_name = stripHTML(display_name);
        display_name = remove_all_special_characters_from_str(display_name);
        let regName = /^[a-zA-Z]+[a-zA-Z ]+$/;
        if (!regName.test(display_name)) {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Please enter a valid name";
            return;
        }
    }

    let error_message_element = document.getElementById("authenticate-details-error");
    error_message_element.innerHTML = "";

    let password = document.getElementById("meeting-joining-password").value;
    password = stripHTML(password);

    // if (password == "") {
    //     error_message_element.style.color = "red";
    //     error_message_element.innerHTML = "Please enter a password.";
    //     return;
    // }

    const request_params = {
        "password": password,
        "session_id": session_id,
    };

    const json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    let  xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/cogno-meet/authenticate-meeting-password/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                check_meeting_participant_limit(display_name);
                client_display_name = display_name;
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = response.message;
            }
        }
    }
    xhttp.send(params);
}

function hide_pages() {
    let waiting_page = document.getElementById('waiting_page');
    let name_and_password_page = document.getElementById('name_and_password_page');
    let meeting_body = document.getElementById('meeting-body');

    if (waiting_page) {
        waiting_page.style.display = "none";
    }
    if (name_and_password_page) {
        name_and_password_page.style.display = "none";
    }
    if (meeting_body) {
        meeting_body.style.display = "block";
    }

}

function create_participant(is_agent, name) {
    
    let client_specific_id;
    let local_storage_obj = get_cogno_meet_current_session_local_storage_obj();
    if(local_storage_obj && local_storage_obj.hasOwnProperty("client_specific_id")) {
        client_specific_id = local_storage_obj["client_specific_id"];
    } else {
        client_specific_id = `${name}_${window.session_id}_${Math.floor(Math.random() * 100000).toString()}`
        set_cogno_meet_current_session_local_storage_obj("client_specific_id", client_specific_id);
    }
    
    set_cogno_meet_current_session_local_storage_obj("participant_display_name", name);
    set_cogno_meet_current_session_local_storage_obj("is_external_participant", window.is_external_participant);

    const request_params = {
        "is_agent": is_agent,
        "name": name,
        "session_id": session_id,
        "is_invited_agent": is_invited_agent,
        "client_specific_id": client_specific_id
    };

    const json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/cogno-meet/add-participant/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                let auth_token = response.participant_authToken;
                localStorage.setItem('auth_token', auth_token);
                set_cogno_meet_current_session_local_storage_obj("dyte_participant_id", response.participant_id);
                if (lobby_page_enabled == 'True') {
                    show_lobby_page();
                }
                else {
                    start_meet();
                }
            } else {
                show_cognomeet_toast(TIMEOUT_ERROR_MESSAGE);
            }
        }
    }
    xhttp.send(params);
}

function show_lobby_page() {

    let name_password_page = document.getElementById('name_and_password_page');
    let lobby_page = document.getElementById('lobby-page-div');

    if (name_password_page) {
        name_password_page.style.display = 'none';
    }
    if (lobby_page) {
        lobby_page.style.display = 'block';
        if(enable_no_agent_connects_toast_meeting == 'True'){
            toggle_background_music(true);
        }
        
        document.getElementById('lobby-participant-name-initials').innerHTML = client_display_name[0].toUpperCase();
        if(is_mic_enabled){
            document.getElementById('mic-disabled-lobby').style.display = 'none';
            document.getElementById('mic-enabled-lobby').style.display = 'block';
        }
        else{
            document.getElementById('mic-disabled-lobby').style.display = 'block';
            document.getElementById('mic-enabled-lobby').style.display = 'none';
        }
        if(is_camera_enabled){
            document.getElementById('camera-disabled-lobby').style.display = 'none';
            document.getElementById('camera-enabled-lobby').style.display = 'block';
        }
        else{
            document.getElementById('camera-disabled-lobby').style.display = 'block';
            document.getElementById('camera-enabled-lobby').style.display = 'none';
        }
        if (enable_no_agent_connects_toast_meeting == "True") {
            initiate_customer_countdown_timer();
        }
    }

    permit_interval = setInterval(send_permit_request, 5000);

}

function send_permit_request() {
    permit_request_to_agent_over_socket(client_display_name);
}

function start_meet() {

    let meeting_room_page = document.getElementById('meeting_room_page');

    if (meeting_room_page) {
        meeting_room_page.style.display = "flex";
    }

    const chat_button_icon = `
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
    xmlns="http://www.w3.org/2000/svg">
    <path
      d="M8.5 19H8C4 19 2 18 2 13V8C2 4 4 2 8 2H16C20 2 22 4 22 8V13C22 17 20 19 16 19H15.5C15.19 19 14.89 19.15 14.7 19.4L13.2 21.4C12.54 22.28 11.46 22.28 10.8 21.4L9.3 19.4C9.14 19.18 8.77 19 8.5 19Z"
      stroke="#DADADA" stroke-width="1.5" stroke-miterlimit="10" stroke-linecap="round"
      stroke-linejoin="round" />
    <path d="M15.9965 11H16.0054" stroke="#DADADA" stroke-width="2" stroke-linecap="round"
      stroke-linejoin="round" />
    <path d="M11.9945 11H12.0035" stroke="#DADADA" stroke-width="2" stroke-linecap="round"
      stroke-linejoin="round" />
    <path d="M7.99451 11H8.00349" stroke="#DADADA" stroke-width="2" stroke-linecap="round"
      stroke-linejoin="round" />
    </svg>`;

    const participant_button_icon = `
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
    xmlns="http://www.w3.org/2000/svg">
    <path
        d="M18.0001 7.16C17.9401 7.15 17.8701 7.15 17.8101 7.16C16.4301 7.11 15.3301 5.98 15.3301 4.58C15.3301 3.15 16.4801 2 17.9101 2C19.3401 2 20.4901 3.16 20.4901 4.58C20.4801 5.98 19.3801 7.11 18.0001 7.16Z"
        stroke="#DADADA" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
    <path
        d="M16.9695 14.4402C18.3395 14.6702 19.8495 14.4302 20.9095 13.7202C22.3195 12.7802 22.3195 11.2402 20.9095 10.3002C19.8395 9.59016 18.3095 9.35016 16.9395 9.59016"
        stroke="#DADADA" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
    <path
        d="M5.96852 7.16C6.02852 7.15 6.09852 7.15 6.15852 7.16C7.53852 7.11 8.63852 5.98 8.63852 4.58C8.63852 3.15 7.48852 2 6.05852 2C4.62852 2 3.47852 3.16 3.47852 4.58C3.48852 5.98 4.58852 7.11 5.96852 7.16Z"
        stroke="#DADADA" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
    <path
        d="M6.99945 14.4402C5.62945 14.6702 4.11945 14.4302 3.05945 13.7202C1.64945 12.7802 1.64945 11.2402 3.05945 10.3002C4.12945 9.59016 5.65945 9.35016 7.02945 9.59016"
        stroke="#DADADA" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
    <path
        d="M12.0001 14.6302C11.9401 14.6202 11.8701 14.6202 11.8101 14.6302C10.4301 14.5802 9.33008 13.4502 9.33008 12.0502C9.33008 10.6202 10.4801 9.47021 11.9101 9.47021C13.3401 9.47021 14.4901 10.6302 14.4901 12.0502C14.4801 13.4502 13.3801 14.5902 12.0001 14.6302Z"
        stroke="#DADADA" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
    <path
        d="M9.0907 17.7804C7.6807 18.7204 7.6807 20.2603 9.0907 21.2003C10.6907 22.2703 13.3107 22.2703 14.9107 21.2003C16.3207 20.2603 16.3207 18.7204 14.9107 17.7804C13.3207 16.7204 10.6907 16.7204 9.0907 17.7804Z"
        stroke="#DADADA" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
    </svg>`;

    const docs_button_icon = `
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
    xmlns="http://www.w3.org/2000/svg">
    <path
        d="M8 12.5C8 12.2239 8.26116 12 8.58333 12H14.4166C14.7388 12 15 12.2239 15 12.5C15 12.7761 14.7388 13 14.4166 13H8.58333C8.26116 13 8 12.7761 8 12.5Z"
        fill="#DADADA" />
    <path
        d="M8.66666 16C8.29847 16 8 16.2239 8 16.5C8 16.7761 8.29847 17 8.66666 17H11.3333C11.7015 17 12 16.7761 12 16.5C12 16.2239 11.7015 16 11.3333 16H8.66666Z"
        fill="#DADADA" />
    <path
        d="M7.91666 3C7.5945 3 7.33333 3.25184 7.33333 3.5625V4.125H6.75C5.7835 4.125 5 4.88052 5 5.8125V19.3125C5 20.2445 5.7835 21 6.75 21H13.75C13.9047 21 14.0531 20.9407 14.1624 20.8353L18.8291 16.3353C18.9385 16.2298 19 16.0867 19 15.9375V5.8125C19 4.88052 18.2165 4.125 17.25 4.125H16.6666V3.5625C16.6666 3.25184 16.4055 3 16.0833 3C15.7612 3 15.5 3.25184 15.5 3.5625V4.125H12.5833V3.5625C12.5833 3.25184 12.3221 3 12 3C11.6778 3 11.4167 3.25184 11.4167 3.5625V4.125H8.5V3.5625C8.5 3.25184 8.23883 3 7.91666 3ZM17.25 5.25C17.5721 5.25 17.8333 5.50184 17.8333 5.8125V15.375H14.9166C13.9501 15.375 13.1666 16.1305 13.1666 17.0625V19.875H6.75C6.42783 19.875 6.16666 19.6232 6.16666 19.3125V5.8125C6.16666 5.50184 6.42783 5.25 6.75 5.25H17.25ZM17.0084 16.5L14.3333 19.0796V17.0625C14.3333 16.7519 14.5945 16.5 14.9166 16.5H17.0084Z"
        fill="#DADADA" />
    <path
        d="M8.58333 8C8.26116 8 8 8.22385 8 8.49999C8 8.77613 8.26116 9 8.58333 9H14.4166C14.7388 9 15 8.77613 15 8.49999C15 8.22385 14.7388 8 14.4166 8H8.58333Z"
        fill="#DADADA" />
    </svg>`;

    const notes_button_icon = `
    <svg width="24" height="23" viewBox="0 0 24 23" fill="none"
    xmlns="http://www.w3.org/2000/svg">
    <path
        d="M19.9035 18.6171H11.201L18.3177 11.5L18.3181 11.4996L18.3185 11.4992L20.5949 9.22265C20.7233 9.09424 20.8252 8.94179 20.8947 8.774C20.9642 8.60622 21 8.42639 21 8.24478C21 8.06316 20.9642 7.88333 20.8948 7.71554C20.8252 7.54775 20.7234 7.39529 20.595 7.26687L16.7326 3.40422C16.473 3.14535 16.1213 2.99998 15.7547 3C15.3881 3.00002 15.0365 3.14541 14.7769 3.4043L4.40502 13.7766C4.2707 13.9109 4.16556 14.0715 4.0962 14.2483C4.08911 14.2656 4.08315 14.2831 4.07744 14.3007C4.02645 14.4466 4.00027 14.6 4 14.7546V18.6171C4.00041 18.9837 4.14624 19.3352 4.4055 19.5945C4.66476 19.8537 5.01627 19.9996 5.38292 20H19.9035C20.0869 20 20.2628 19.9271 20.3924 19.7975C20.5221 19.6678 20.595 19.4919 20.595 19.3085C20.595 19.1251 20.5221 18.9492 20.3924 18.8196C20.2628 18.6898 20.0869 18.6171 19.9035 18.6171ZM5.66935 14.4681L12.9889 7.14819L16.8512 11.0106L9.53166 18.3307L5.66935 14.4681ZM15.7547 4.38215L19.6171 8.24472L17.8292 10.0327L13.9668 6.17025L15.7547 4.38215ZM5.38292 16.1375L7.86231 18.6171H5.38292V16.1375Z"
        fill="#DADADA" />
    </svg>`;

    const screen_capture_button_icon = `
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
    xmlns="http://www.w3.org/2000/svg">
    <path
        d="M13.7322 3C14.4503 3 15.1146 3.41112 15.4783 4.08054L16.2113 5.42987H18.075C19.6904 5.42987 21 6.84585 21 8.59255V17.8373C21 19.584 19.6904 21 18.075 21H5.925C4.30957 21 3 19.584 3 17.8373V8.59255C3 6.84585 4.30957 5.42987 5.925 5.42987H7.79738L8.5845 4.04383C8.95283 3.39524 9.60623 3 10.3101 3H13.7322ZM13.7322 4.4597H10.3101C10.109 4.4597 9.92028 4.55649 9.79313 4.7203L9.73493 4.80764L8.75021 6.54162C8.62744 6.75782 8.40964 6.88957 8.175 6.88957H5.925C5.05515 6.88957 4.35 7.65202 4.35 8.59255V17.8373C4.35 18.7778 5.05515 19.5403 5.925 19.5403H18.075C18.9448 19.5403 19.65 18.7778 19.65 17.8373V8.59255C19.65 7.65202 18.9448 6.88957 18.075 6.88957H15.825C15.5857 6.88957 15.3642 6.75253 15.243 6.52939L14.3142 4.81988C14.193 4.59674 13.9716 4.4597 13.7322 4.4597ZM12 8.34927C14.2368 8.34927 16.05 10.3099 16.05 12.7284C16.05 15.1469 14.2368 17.1075 12 17.1075C9.76325 17.1075 7.95 15.1469 7.95 12.7284C7.95 10.3099 9.76325 8.34927 12 8.34927ZM12 9.80897C10.5088 9.80897 9.3 11.116 9.3 12.7284C9.3 14.3407 10.5088 15.6478 12 15.6478C13.4912 15.6478 14.7 14.3407 14.7 12.7284C14.7 11.116 13.4912 9.80897 12 9.80897Z"
        fill="#DADADA" />
    </svg>`;

    const help_button_icon = `
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
        xmlns="http://www.w3.org/2000/svg">
        <path
        d="M16.2849 11.5693C18.889 11.5693 21 13.6805 21 16.2847C21 18.8889 18.889 21 16.2849 21C13.6809 21 11.5698 18.8889 11.5698 16.2847C11.5698 13.6805 13.6809 11.5693 16.2849 11.5693ZM16.2849 18.2145C15.9893 18.2145 15.7495 18.4543 15.7495 18.7499C15.7495 19.0456 15.9893 19.2854 16.2849 19.2854C16.5806 19.2854 16.8203 19.0456 16.8203 18.7499C16.8203 18.4543 16.5806 18.2145 16.2849 18.2145ZM16.2849 13.176C15.3866 13.176 14.6867 13.8768 14.6961 14.8516C14.6984 15.0882 14.8921 15.2784 15.1288 15.276C15.3656 15.2738 15.5556 15.08 15.5533 14.8433C15.5485 14.3469 15.8616 14.0334 16.2849 14.0334C16.6899 14.0334 17.0166 14.3693 17.0166 14.8474C17.0166 15.0122 16.9691 15.1409 16.8246 15.3288L16.744 15.4282L16.6592 15.5252L16.4317 15.774L16.3146 15.9087C15.986 16.3003 15.8563 16.5881 15.8563 17.0319C15.8563 17.2687 16.0482 17.4606 16.2849 17.4606C16.5217 17.4606 16.7136 17.2687 16.7136 17.0319C16.7136 16.8577 16.7637 16.7241 16.9184 16.5259L16.9912 16.4366L17.0777 16.3376L17.3055 16.0885L17.4209 15.9556C17.7452 15.5691 17.8739 15.2842 17.8739 14.8474C17.8739 13.9012 17.1688 13.176 16.2849 13.176ZM11.5889 13.2834C11.3345 13.6806 11.1292 14.1122 10.9814 14.5697L4.92793 14.57C4.57337 14.57 4.28593 14.8574 4.28593 15.212V15.7072C4.28593 16.1665 4.44977 16.6107 4.74798 16.9599C5.82243 18.2182 7.50775 18.8576 9.85527 18.8576C10.3666 18.8576 10.8466 18.8273 11.2957 18.7668C11.5059 19.1911 11.7696 19.5842 12.0772 19.9382C11.3952 20.0756 10.6537 20.1436 9.85527 20.1436C7.15836 20.1436 5.11286 19.3675 3.77008 17.795C3.27306 17.2129 3 16.4726 3 15.7072V15.212C3 14.1472 3.86317 13.284 4.92793 13.284L11.5889 13.2834ZM9.85527 3C12.2226 3 14.1417 4.9192 14.1417 7.28666C14.1417 9.65412 12.2226 11.5733 9.85527 11.5733C7.48793 11.5733 5.56882 9.65412 5.56882 7.28666C5.56882 4.9192 7.48793 3 9.85527 3ZM9.85527 4.286C8.19813 4.286 6.85476 5.62944 6.85476 7.28666C6.85476 8.94388 8.19813 10.2874 9.85527 10.2874C11.5124 10.2874 12.8558 8.94388 12.8558 7.28666C12.8558 5.62944 11.5124 4.286 9.85527 4.286Z"
        fill="white" />
    </svg>`;

    const layout_button_icon = `
    <svg width="25" height="24" viewBox="0 0 25 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <g id="Iconly/Bold/Category">
        <g id="Category">
        <path id="Category_2" fill-rule="evenodd" clip-rule="evenodd" d="M5.04 1.5C3.35991 1.5 2 2.87782 2 4.561V7.97C2 9.66358 3.36131 11.03 5.04 11.03H8.42C10.11 11.03 11.46 9.6623 11.46 7.97V4.561C11.46 2.87911 10.1114 1.5 8.42 1.5H5.04ZM3 4.561C3 3.42218 3.92009 2.5 5.04 2.5H8.42C9.54864 2.5 10.46 3.42089 10.46 4.561V7.97C10.46 9.1177 9.55003 10.03 8.42 10.03H5.04C3.91869 10.03 3 9.11642 3 7.97V4.561ZM5.04 12.9697C3.36105 12.9697 2 14.3374 2 16.0307V19.4397C2 21.122 3.36004 22.4997 5.04 22.4997H8.42C10.1112 22.4997 11.46 21.1207 11.46 19.4397V16.0307C11.46 14.3387 10.1102 12.9697 8.42 12.9697H5.04ZM3 16.0307C3 14.884 3.91895 13.9697 5.04 13.9697H8.42C9.54977 13.9697 10.46 14.8827 10.46 16.0307V19.4397C10.46 20.5787 9.54876 21.4997 8.42 21.4997H5.04C3.91996 21.4997 3 20.5774 3 19.4397V16.0307ZM13.5401 4.561C13.5401 2.87911 14.8887 1.5 16.5801 1.5H19.9601C21.6402 1.5 23.0001 2.87782 23.0001 4.561V7.97C23.0001 9.66358 21.6388 11.03 19.9601 11.03H16.5801C14.8901 11.03 13.5401 9.6623 13.5401 7.97V4.561ZM16.5801 2.5C15.4515 2.5 14.5401 3.42089 14.5401 4.561V7.97C14.5401 9.1177 15.4501 10.03 16.5801 10.03H19.9601C21.0814 10.03 22.0001 9.11642 22.0001 7.97V4.561C22.0001 3.42218 21.08 2.5 19.9601 2.5H16.5801ZM16.5801 12.9697C14.8899 12.9697 13.5401 14.3387 13.5401 16.0307V19.4397C13.5401 21.1207 14.8889 22.4997 16.5801 22.4997H19.9601C21.6401 22.4997 23.0001 21.122 23.0001 19.4397V16.0307C23.0001 14.3374 21.639 12.9697 19.9601 12.9697H16.5801ZM14.5401 16.0307C14.5401 14.8827 15.4503 13.9697 16.5801 13.9697H19.9601C21.0812 13.9697 22.0001 14.884 22.0001 16.0307V19.4397C22.0001 20.5774 21.0801 21.4997 19.9601 21.4997H16.5801C15.4513 21.4997 14.5401 20.5787 14.5401 19.4397V16.0307Z" fill="white"/>
        </g>
        </g>
    </svg>`;

    const auth_token = localStorage.getItem('auth_token');
    const client = new DyteClient({ clientId: org_id });

    const ui_config_options = {
        controlBarElements: {
            fullscreen: true,
            share: false,
            screenShare: (screen_sharing == 'True'),
            layout: true,
            chat: false,
            polls: false,
            participants: false,
            plugins: false
        },
        dimensions: {
            mode: "fillParent"
        },
        logo: COGNOMEET_TAB_LOGO,
        colors:{
            videoBackground: '#'+meeting_background_color,           
        }
    }

    meeting = client.Meeting({
        roomName: room_name,
        authToken: auth_token,
        audioEnabled: false,
        videoEnabled: false,
    },
        ui_config_options,
    );

    // ------------- custom buttons ----------

    // layout button
    meeting.on(meeting.Events.meetingJoined, () => {
        button = meeting.controlBar.addButton({
            icon: layout_button_icon,
            label: 'Layout',
            position: 'left',
            onClick: () => {
                if (is_highlighted_layout) {
                    meeting.grid.update({
                        layout: meeting.grid.layouts.MULTI
                    });
                    is_highlighted_layout = !is_highlighted_layout;
                } else {
                    meeting.grid.update({
                        layout: meeting.grid.layouts.HIGHLIGHTED,
                    });
                    is_highlighted_layout = !is_highlighted_layout;
                }
            },
        });
    });

    // Chat button 
    meeting.on(meeting.Events.meetingJoined, () => {
        button = meeting.controlBar.addButton({
            icon: chat_button_icon,
            label: 'Chat',
            position: 'right',
            onClick: () => {
                modify_meet_div(100, 70);
                show_meeting_chat_box();
            },
        });
    });
    
    meeting.onError(function (error) {
        console.log('Error occurent in the cogno meet ', error);
    });

    meeting.init("meeting-body");

    initialize_customer_heartbeat_interval();

    if (allow_meeting_end_time == 'True') {
        if (!is_meeting_interval_set) {
            setInterval(function () {
                check_meeting_ended_or_not();
            }, 30000)
            is_meeting_interval_set = true;
        }
    }

    meeting.on(meeting.Events.meetingJoined, () => {
        join_meet_message_over_socket(meeting.self.id, meeting.self.name, 'Customer');
        setTimeout(disable_audio_video, 500);
    });

    meeting.on(meeting.Events.disconnect, () => {

        if (meeting.participants.length == 1) {
            close_meeting();
        }

        let root = location.protocol + '//' + location.host;
        if (is_kicked) {
            window.location.replace(`${root}/cogno-meet/meeting-end?session_id=${session_id}&kicked=true`);
        }
        else {
            window.location.replace(`${root}/cogno-meet/meeting-end?session_id=${session_id}`);
        }

    });

    // on screenShare
    meeting.on(meeting.Events.screenSharingUpdated, (isScreensharing) => {
        show_cognomeet_toast(`You're now sharing your screen`);
    });

    if (is_recording_on == 'True') {
        show_cognomeet_toast(`Session is being recorded`);
    }

    // Event on toggle audio 
    meeting.on(meeting.Events.audioUpdated, (audio_enabled) => {
        if (is_agent == "True") {
            audio_toggled_message_over_socket(meeting.self.id, meeting.self.name, 'Agent', audio_enabled);
        }
        else {
            audio_toggled_message_over_socket(meeting.self.id, meeting.self.name, 'Support Agent', audio_enabled);
        }
    });

    // Event trigged when another participant left the meeting 
    meeting.on(meeting.Events.participantLeave, (participant) => {
        show_cognomeet_toast(`${participant.name} left the meeting`);
    });
}

function audio_toggled_message_over_socket(id, name, sender, audio_enabled) {

    let json_string = JSON.stringify({
        "type": "audio_toggled",
        "participant_name": name,
        "id": id,
        "sender": sender, 
        "audio_enabled": audio_enabled
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_chat_socket(encrypted_data);
}

function join_meet_message_over_socket(id, name, sender) {
    let json_string = JSON.stringify({
        "type": "joined_meet",
        "participant_name": name,
        "id": id,
        "sender": sender,
        "dyte_participant_id":get_dyte_participant_id()
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_chat_socket(encrypted_data);
}

// Audio and video can be diabled directly else, they won't dactivate
function disable_audio_video() {
    if(!is_mic_enabled){
        meeting.self.disableAudio();
    }else{
        meeting.self.enableAudio();
    }

    if(!is_camera_enabled){
        meeting.self.disableVideo();
    }else{
        meeting.self.enableVideo();
    }

    load_chat_history();
}

function modify_meet_div(height, width) {
    let meet_div = document.getElementById('meeting-body');
    if (meet_div) {
        meet_div.style.height = `${height}%`;
        meet_div.style.width = `${width}%`;
    }
}

function hide_all_meeting_options() {

    document.querySelector(".cogno-lobby-add-members").classList.add('d-none');
    document.querySelector(".cogno-lobby-agent-notes").classList.add('d-none');
    document.querySelector(".cogno-lobby-ask-for-support").classList.add('d-none');
    document.querySelector(".cogno-lobby-documents").classList.add('d-none');
    document.querySelector(".cogno-lobby-meeting-chat").classList.add('d-none');

}

function show_meeting_chat_box(el) {
    hide_all_meeting_options();
    document.getElementById('cogno-lobby-meeting-chat-sm').classList.remove('d-none');
}

function hide_meeting_chat_box(el) {
    if (window.innerWidth > 600) {
        hide_all_meeting_options();
    }
}

function show_meeting_notes(el) {
    hide_all_meeting_options();
    document.querySelector(".cogno-lobby-agent-notes").classList.remove('d-none');
}

function hide_meeting_notes(el) {
    if (window.innerWidth >= 600) {
        hide_all_meeting_options();
    }
}

function show_meeting_support_docs(el) {
    hide_all_meeting_options();

    document.querySelector(".cogno-lobby-documents").classList.remove('d-none');
}

function hide_meeting_support_docs(el) {
    if (window.innerWidth >= 600) {
        hide_all_meeting_options();
    }
}

function show_add_members(el) {
    hide_all_meeting_options();
    document.querySelector(".cogno-lobby-add-members").classList.remove('d-none');
}

function hide_add_members(el) {
    if (window.innerWidth >= 600) {
        hide_all_meeting_options();
    }
}

function show_ask_for_support() {
    hide_all_meeting_options();

    document.querySelector(".cogno-lobby-ask-for-support").classList.remove('d-none');
}

function hide_ask_for_support() {
    if (window.innerWidth >= 600) {
        hide_all_meeting_options();
    }
}

function show_cogno_lobby_options() {
    if (document.getElementById("cogno-lobby-options").querySelector(".cogno-lobby-options-sm").children.length > 0) {
        document.getElementById("cogno-lobby-options").style.display = 'block';
        document.querySelector("#cobrowse-meeting-iframe").style.width = "";
    } else {
        document.querySelector("#cobrowse-meeting-iframe").style.width = "100%";
    }
}

function hide_cogno_lobby_options() {
    document.getElementById("cogno-lobby-options").style.display = 'none';
}




// ----- Web Socket -----
let easyassist_socket_activity_interval_check = setInterval(easyassist_initialize_web_socket, 1000);

function easyassist_initialize_web_socket() {

    if (client_websocket == null) {
        enable_chat_socket();
    }
}

// Enable websocket
function enable_chat_socket() {

    let room_id = session_id;
    let sender = "client";

    create_chat_socket(room_id, sender);
}

function create_chat_socket(room_id, sender) {
    let ws_scheme = window.location.protocol == "http:" ? "ws" : "wss";
    let url = ws_scheme + '://' + window.location.host + '/ws/meet/' + room_id + '/' + sender + "/";
    if (client_websocket == null) {
        client_websocket = new WebSocket(url);
        client_websocket.onmessage = easyassist_handle_socket_message;
        client_websocket.onerror = function (e) {
            console.error("WebSocket error observed:", e);
            client_websocket_open = false;
            easyassist_close_socket();
        }
        client_websocket.onopen = function () {
            client_websocket_open = true;
            console.log("client_websocket created successfully");
        }
        client_websocket.onclose = function () {
            client_websocket_open = false;
            client_websocket = null;
        }
    }
}


function easyassist_close_socket() {

    if (client_websocket == null) {
        return;
    }

    try {
        client_websocket.close();
    } catch (err) {
        client_websocket.onmessage = null;
        client_websocket = null;
    }

}


function easyassist_handle_socket_message(e) {
    let data = JSON.parse(e.data);
    let message = data.message;

    if (!message.body) {
        return;
    }

    let client_packet = null;
    try {
        client_packet = message.body.Request;
    } catch (err) {
        console.trace();
        console.log("Please look at this report this to developer ", message)
    }

    client_packet = easyassist_custom_decrypt(client_packet);
    client_packet = JSON.parse(client_packet);

    if (client_packet.type == "chat") {
        data = client_packet;

        let msg_sender = data["header"]["sender"];
        let sender_name = data["header"]["name"];
        let is_file_attachment = data["is_file_attachment"];
        let file_attachment_name = data["file_attachment_name"];
        let message_body = data["body"];
        let sender_id = data["header"]["sender_id"];
        let attachment_link = data["attachment_link"];
        let full_name = data["header"]["full_name"];

        if (meeting != null && meeting != undefined && sender_id != meeting.self.id) {
            show_cognomeet_toast(`New Message`);
            if (is_file_attachment) {
                append_attachment_at_end(file_attachment_name, attachment_link, 'left', sender_name, msg_sender, full_name);
            }
            else {
                append_message_at_end(message_body, 'left', sender_name, msg_sender, full_name);
            }

        }

        scroll_to_bottom();
    }
    else if (client_packet.type == 'kick_participant') {
        data = client_packet;
        let msg_sender = message["header"]["sender"];
        let _kick_participant_id = data.kick_participant_id;
        let participant_name = data.kicked_participant_name;

        if ((meeting != undefined && meeting != null && meeting.self.id != _kick_participant_id)) {
            show_cognomeet_toast(`${participant_name} has been removed from the meeting`);
        }

        if (msg_sender == 'agent' && (meeting != undefined && meeting != null && meeting.self.id == _kick_participant_id)) {
            is_kicked = true;
            meeting.leaveRoom();
        }
    }
    else if (client_packet.type == 'permit_request') {
        data = client_packet;
        let participant_name = data["participant_name"];
        let status = data["status"];
        let sender = message["header"]["sender"];

        if (status == 'permit' && sender == 'agent') {
            if (window.is_agent == "False" && window.is_invited_agent == "False") {
                reset_easyassist_meeting_countdown_timer();
            }
            clearInterval(permit_interval);
            let lobby_page = document.getElementById('lobby-page-div');
            if (lobby_page) {
                lobby_page.style.display = 'none'
            }
            if(!is_lobby_audio_muted){
                toggle_background_music(false);
            }
            start_meet();
        }
        else if (sender == 'agent') {
            clearInterval(permit_interval);
            let root = location.protocol + '//' + location.host;
            window.location.replace(`${root}/cogno-meet/meeting-end?session_id=${session_id}&deny=true`);
        }
    }
    else if (client_packet.type == 'mute_participant') {
        data = client_packet;
        let sender_id = data["sender_id"];
        let sender = message["header"]["sender"];

        if (meeting != undefined && meeting != null && sender == 'agent' && sender_id == meeting.self.id) {
            meeting.self.disableAudio();
            show_cognomeet_toast(`Microphone is muted`);
        }
    }
    else if (client_packet.type == 'joined_meet') {
        data = client_packet;
        let id = data["id"];
        if (meeting != null && meeting != undefined && id != meeting.self.id) {
            let participant_name = data["participant_name"];
            let sender = data["sender"];
            show_cognomeet_toast(`${participant_name} joined the meeting`);
            participant_joined_chat(participant_name,sender)
        }

    }
}

function participant_joined_chat(sender_name, sender_type) {
    let html = '<div class="message join-call-message">';
    if (sender_type == 'Customer') {
        html += `${sender_name} has joined the chat`;

    } else {
        html += `${sender_name} has joined the chat`;
    }
    html += '</div>';

    let chat_body = document.getElementById("meeting_chat_room");
    if (chat_body) {
        chat_body.innerHTML += html;
        scroll_to_bottom();
    }
}

function append_chat_joined_at_end(message){
    let html = `
    <div class="message join-call-message">
        ${message}
    </div>
    `;
    let chat_body = document.getElementById("meeting_chat_room");
    if (chat_body) {
        chat_body.innerHTML += html;
        scroll_to_bottom();
    }

}

function append_message_at_end(message, position, sender_name, msg_sender, full_name) {

    let current_time = new Date().toLocaleTimeString('en-US', { hour: 'numeric', hour12: true, minute: 'numeric' });

    let html = null;
    if (position == 'right') {
        html = [
            `
            <div class="message message-${position}">
                <div class="bubble bubble-light">
                <div class="mt-1 mb-1">
                    ${message}
                </div>
                <div class="message-timer">
                    ${current_time}
                </div>
                </div>
            </div>`
        ].join('');
    }
    else {
        let sender = '';
        if (msg_sender == 'agent') { sender = 'Agent'; }
        else if (msg_sender == 'invite_agent') { sender = 'Support Agent'; }
        html = [
            `
            <div class="message message-${position}">
                <div class="bubble bubble-dark">
                <div class="mt-1 mb-1">
                    ${message}
                </div>
                <div class="message-timer">
                    ${current_time} <span>|</span> ${sender + " " + full_name}
                </div>
                </div>
            </div>`
        ].join('');
    }

    document.getElementById("meeting_chat_room").innerHTML += html;
    scroll_to_bottom();
}

function append_attachment_at_end(file_attachment_name, attachment_link, position, sender_name, msg_sender, full_name) {

    let current_time = new Date().toLocaleTimeString('en-US', { hour: 'numeric', hour12: true, minute: 'numeric' });

    if (position == 'right') {
        html = [
            `<div class="message message-right">
                <div class="bubble bubble-light">
                <div class="shared-document">
                    <div class="document-icon">
                    <svg width="24" height="24" viewBox="0 0 18 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M5.92487 14.3901H11.311C11.7169 14.3901 12.0536 14.0501 12.0536 13.6401C12.0536 13.2301 11.7169 12.9001 11.311 12.9001H5.92487C5.51893 12.9001 5.18229 13.2301 5.18229 13.6401C5.18229 14.0501 5.51893 14.3901 5.92487 14.3901ZM9.2714 7.90007H5.92487C5.51893 7.90007 5.18229 8.24007 5.18229 8.65007C5.18229 9.06007 5.51893 9.39007 5.92487 9.39007H9.2714C9.67734 9.39007 10.014 9.06007 10.014 8.65007C10.014 8.24007 9.67734 7.90007 9.2714 7.90007ZM16.3381 7.02561C16.5708 7.02292 16.8242 7.02 17.0545 7.02C17.302 7.02 17.5 7.22 17.5 7.47V15.51C17.5 17.99 15.5099 20 13.0545 20H5.17327C2.59901 20 0.5 17.89 0.5 15.29V4.51C0.5 2.03 2.5 0 4.96535 0H10.2525C10.5099 0 10.7079 0.21 10.7079 0.46V3.68C10.7079 5.51 12.203 7.01 14.0149 7.02C14.4381 7.02 14.8112 7.02316 15.1377 7.02593C15.3917 7.02809 15.6175 7.03 15.8168 7.03C15.9578 7.03 16.1405 7.02789 16.3381 7.02561ZM16.6114 5.56593C15.7976 5.56893 14.8382 5.56593 14.1481 5.55893C13.053 5.55893 12.151 4.64793 12.151 3.54193V0.905927C12.151 0.474927 12.6689 0.260927 12.9649 0.571927C13.501 1.13488 14.2377 1.90879 14.971 2.67908C15.7018 3.44677 16.4292 4.21086 16.951 4.75893C17.2402 5.06193 17.0283 5.56493 16.6114 5.56593Z" fill="white"/>
                        </svg>
                    </div>
                    <div class="document-name">
                    <p>${file_attachment_name}</p>
                    </div>
                    <a href="${attachment_link}" download>
                    <div class="download-document-button">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd"
                        d="M10.5295 4.45395C10.5295 3.65096 11.1871 3 11.9982 3C12.8094 3 13.467 3.65096 13.467 4.45395V11.2521C13.467 11.3556 13.5518 11.4395 13.6564 11.4395H15.6705C15.9582 11.4396 16.2194 11.606 16.3388 11.8652C16.4581 12.1244 16.4136 12.4287 16.225 12.6438L12.5527 16.8249C12.4133 16.984 12.211 17.0754 11.9982 17.0754C11.7855 17.0754 11.5832 16.984 11.4438 16.8249L7.77149 12.6438C7.58282 12.4287 7.53834 12.1244 7.65768 11.8652C7.77702 11.606 8.03822 11.4396 8.32597 11.4395H10.3401C10.4447 11.4395 10.5295 11.3556 10.5295 11.2521V4.45395ZM19.1601 16.6096C19.1601 16.1077 19.5711 15.7008 20.0781 15.7008C20.3223 15.6998 20.5568 15.7951 20.7298 15.9657C20.9028 16.1362 21 16.368 21 16.6096V18.0006C21 19.6571 19.6435 21 17.9701 21H6.02613C4.35423 20.9979 3 19.6557 3 18.0006V16.6096C3 16.1077 3.41103 15.7008 3.91807 15.7008C4.4251 15.7008 4.83613 16.1077 4.83613 16.6096V18.0006C4.83697 18.6507 5.36938 19.1775 6.02613 19.1779H17.9701C18.6268 19.1775 19.1592 18.6507 19.1601 18.0006V16.6096Z"
                        fill="white" />
                    </svg>
                    </div>
                </div>
                <div class="message-timer">
                    ${current_time}
                </div>
                </div>
            </div>`
        ].join('');
    }
    else {
        let sender = '';
        if (msg_sender == 'agent') { sender = 'Agent'; }
        else if (msg_sender == 'invite_agent') { sender = 'Support Agent'; }
        html = [
            `<div class="message message-left">
                <div class="bubble bubble-dark">
                <div class="shared-document">
                    <div class="document-icon">
                    <svg width="24" height="24" viewBox="0 0 18 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M5.92487 14.3901H11.311C11.7169 14.3901 12.0536 14.0501 12.0536 13.6401C12.0536 13.2301 11.7169 12.9001 11.311 12.9001H5.92487C5.51893 12.9001 5.18229 13.2301 5.18229 13.6401C5.18229 14.0501 5.51893 14.3901 5.92487 14.3901ZM9.2714 7.90007H5.92487C5.51893 7.90007 5.18229 8.24007 5.18229 8.65007C5.18229 9.06007 5.51893 9.39007 5.92487 9.39007H9.2714C9.67734 9.39007 10.014 9.06007 10.014 8.65007C10.014 8.24007 9.67734 7.90007 9.2714 7.90007ZM16.3381 7.02561C16.5708 7.02292 16.8242 7.02 17.0545 7.02C17.302 7.02 17.5 7.22 17.5 7.47V15.51C17.5 17.99 15.5099 20 13.0545 20H5.17327C2.59901 20 0.5 17.89 0.5 15.29V4.51C0.5 2.03 2.5 0 4.96535 0H10.2525C10.5099 0 10.7079 0.21 10.7079 0.46V3.68C10.7079 5.51 12.203 7.01 14.0149 7.02C14.4381 7.02 14.8112 7.02316 15.1377 7.02593C15.3917 7.02809 15.6175 7.03 15.8168 7.03C15.9578 7.03 16.1405 7.02789 16.3381 7.02561ZM16.6114 5.56593C15.7976 5.56893 14.8382 5.56593 14.1481 5.55893C13.053 5.55893 12.151 4.64793 12.151 3.54193V0.905927C12.151 0.474927 12.6689 0.260927 12.9649 0.571927C13.501 1.13488 14.2377 1.90879 14.971 2.67908C15.7018 3.44677 16.4292 4.21086 16.951 4.75893C17.2402 5.06193 17.0283 5.56493 16.6114 5.56593Z" fill="white"/>
                        </svg>
                    </div>
                    <div class="document-name">
                    <p>${file_attachment_name}</p>
                    </div>
                    
                    <div class="download-document-button">
                    <a href="${attachment_link}" download>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd"
                        d="M10.5295 4.45395C10.5295 3.65096 11.1871 3 11.9982 3C12.8094 3 13.467 3.65096 13.467 4.45395V11.2521C13.467 11.3556 13.5518 11.4395 13.6564 11.4395H15.6705C15.9582 11.4396 16.2194 11.606 16.3388 11.8652C16.4581 12.1244 16.4136 12.4287 16.225 12.6438L12.5527 16.8249C12.4133 16.984 12.211 17.0754 11.9982 17.0754C11.7855 17.0754 11.5832 16.984 11.4438 16.8249L7.77149 12.6438C7.58282 12.4287 7.53834 12.1244 7.65768 11.8652C7.77702 11.606 8.03822 11.4396 8.32597 11.4395H10.3401C10.4447 11.4395 10.5295 11.3556 10.5295 11.2521V4.45395ZM19.1601 16.6096C19.1601 16.1077 19.5711 15.7008 20.0781 15.7008C20.3223 15.6998 20.5568 15.7951 20.7298 15.9657C20.9028 16.1362 21 16.368 21 16.6096V18.0006C21 19.6571 19.6435 21 17.9701 21H6.02613C4.35423 20.9979 3 19.6557 3 18.0006V16.6096C3 16.1077 3.41103 15.7008 3.91807 15.7008C4.4251 15.7008 4.83613 16.1077 4.83613 16.6096V18.0006C4.83697 18.6507 5.36938 19.1775 6.02613 19.1779H17.9701C18.6268 19.1775 19.1592 18.6507 19.1601 18.0006V16.6096Z"
                        fill="white" />
                    </svg>
                    </div>
                </div>
                <div class="message-timer">
                    ${current_time} <span>|</span> ${sender + " " + full_name}
                </div>
                </div>
            </div>`
        ].join('');
    }

    document.getElementById("meeting_chat_room").innerHTML += html;
    scroll_to_bottom();
}


// Send message over socket
function send_message_over_chat_socket(data) {

    try {
        if (client_websocket_open == false || client_websocket == null) {
            if (send_message_over_chat_socket.caller.name == "easyassist_socket_callee") {
                return;
            }
            setTimeout(function easyassist_socket_callee() {
                send_message_over_chat_socket(data);
            }, 5000);
            console.log("client_websocket is not open");
            return;
        }

        if (client_websocket_open == true && client_websocket != null) {
            // var packet_id = easyassist_generate_unique_id();
            let sender = 'customer';

            client_websocket.send(JSON.stringify({
                "message": {
                    "header": {
                        "sender": sender,
                        "sender_name": client_display_name
                    },
                    "body": data
                }
            }));
        }
    } catch (err) {
        console.error("ERROR : send_message_over_chat_socket ", err);
    }
}

function keypress_chat_message(event) {
    if (event.keyCode == 13) {
        let message = document.getElementById('meeting_text_message');
        if(message && message.value!="") {
            send_message_to_chat();
        }
    }
}

// On enter send message
let message_field = document.getElementById('meeting_text_message');
if(message_field){
    message_field.addEventListener('keydown', keypress_chat_message);
}

function send_message_to_chat(chat_id = null) {
    // let is_message_sender = true
    let message = null;

    if (chat_id) {
        message = document.getElementById(`support-doc-${chat_id}`);
    }
    else {
        message = document.getElementById("meeting_text_message");
    }

    if (message) {
        message = message.value;
        message = stripHTML(message);
        message = remove_special_characters_from_str(message);        
        if (message == "") {
            document.getElementById("meeting_text_message").value = "";
            return;
        }
        let sender = null;
        let sender_name = null;

        append_message_at_end(message, 'right');

        if (is_agent == "True") {
            sender = "agent";
            sender_name = agent_name;
        }
        else {
            sender = "client";
            sender_name = client_display_name;
        }

        let json_string = JSON.stringify({
            "type": "chat",
            "header": {
                "sender_id": meeting.self.id,
                "sender": sender,
                "name": sender_name,
                "full_name": sender_name
            },
            "body": message,
            "is_file_attachment": false,
            "file_attachment_name": null,
            "attachment_link": null,
            "dyte_participant_id": get_dyte_participant_id()
        });

        let encrypted_data = easyassist_custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };

        send_message_over_chat_socket(encrypted_data);

        document.getElementById("meeting_text_message").value = "";
    }
}

function send_attachmet_to_chat(attachment_link, file_name) {

    let sender = null;
    let sender_name = null;
    if (is_agent == "True") {
        sender = "agent";
        sender_name = agent_name;
    }
    else {
        sender = "client";
        sender_name = client_display_name;
    }

    append_attachment_at_end(file_name, attachment_link, 'right');

    let json_string = JSON.stringify({
        "type": "chat",
        "header": {
            "sender_id": meeting.self.id,
            "sender": sender,
            "name": sender_name,
            "full_name": sender_name
        },
        "body": null,
        "is_file_attachment": true,
        "file_attachment_name": file_name,
        "attachment_link": attachment_link,
        "dyte_participant_id": get_dyte_participant_id()
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_chat_socket(encrypted_data);

    document.getElementById("meeting_text_message").value = "";

}

// Save file attachment to server
function save_file_to_server(e) {
    let upload_attachment_data = document.querySelector('#meeting-file-input').files[0];
    document.querySelector('#meeting-file-input').value = '';

    if (upload_attachment_data == undefined || upload_attachment_data == null) {
        return;
    }

    if (check_malicious_file_video_meeting(upload_attachment_data.name)) {
        return;
    }
    // session_id = uuidv4();
    let reader = new FileReader();
    reader.readAsDataURL(upload_attachment_data);
    reader.onload = function () {

        let base64_str = reader.result.split(",")[1];

        let json_string = {
            "filename": upload_attachment_data.name,
            "base64_file": base64_str,
            "session_id": session_id
        };

        json_string = JSON.stringify(json_string);

        let encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        let params = JSON.stringify(encrypted_data);

        let xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/cogno-meet/upload-meeting-file-attachment/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                let response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response.status == 200) {
                    message = response.src;
                    file_attachment_name = message;
                    message = file_attachment_name + "?vctoken=" + session_id;
                    send_attachmet_to_chat(message, response.name);

                } else if (response["status"] == 300) {
                    show_cognomeet_toast("Uploaded files should be less than 5 MB");
                } else if (response.status == 302) {
                    show_cognomeet_toast("Unsupported file format. Please upload jpeg, jpg, png, doc, docx, or pdf file.");
                } else {
                    show_cognomeet_toast("Unable to send file. Please try again.");
                }
            }
        }
        xhttp.send(params);

    };
    reader.onerror = function (error) {
        console.log('Error: ', error);
    };
}

// Scroll chat to bottom
function scroll_to_bottom() {
    let objDiv = document.getElementById("chat_room_container");
    objDiv.scrollTop = objDiv.scrollHeight;
    setTimeout(function () {
        objDiv.scrollTop = objDiv.scrollHeight;
    }, 1000);
}

// Save agent notes after 1 second when stopped typing.
$('#agent-notes').keydown(function () {
    clearTimeout(save_notes_timer);
    save_notes_timer = setTimeout(save_agent_notes, 1000)
});

// Saving agents notes
function save_agent_notes() {
    let notes = document.getElementById("agent-notes").value;
    if (notes == "") {
        return;
    }
    notes = stripHTML(notes);
    notes = remove_special_characters_from_str(notes);
    let request_params = {
        "session_id": session_id,
        "notes": notes
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/cogno-meet/save-meeting-notes/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status != 200) {
                show_cognomeet_toast('Error while saving notes');
            }
        }
    }
    xhttp.send(params);
}

function load_chat_history() {
    let json_string = JSON.stringify({
        "session_id": session_id,
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/cogno-meet/get-chat-for-session/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                let message_data = response.message_history;
                let sender_type = '';
                if (is_agent == 'True') {
                    sender_type = 'agent';
                } else if (is_agent == 'False' && is_invited_agent == 'False') {
                    sender_type = 'invite_agent';
                } else {
                    sender_type = 'client';
                }

                const dyte_participant_id = get_dyte_participant_id();

                for (const chat of message_data) {
                    if(chat.sender == 'system' && dyte_participant_id !=chat.dyte_participant_id){
                        append_chat_joined_at_end(chat.message);
                    } else if(chat.sender != 'system'){
                        if (chat.dyte_participant_id == dyte_participant_id) {
                            if (chat.attachment_file_name) {
                                append_attachment_at_end(chat.attachment_file_name, chat.attachment_file_path, 'right', chat.sender_name, sender_type, chat.full_name);
                            } else {
                                append_message_at_end(chat.message, 'right', chat.sender_name, sender_type, chat.full_name);
                            }
                        } else {
                            if (chat.attachment_file_name) {
                                append_attachment_at_end(chat.attachment_file_name, chat.attachment_file_path, 'left', chat.sender_name, chat.sender, chat.full_name);
                            } else {
                                append_message_at_end(chat.message, 'left', chat.sender_name, chat.sender, chat.full_name);
                            }
                        }
                    }
                }
            } else {
                show_cognomeet_toast("Unable to load chat history");
            }
        }
    }
    xhttp.send(params);
}

let participant_name_div = document.getElementById('meeting-joining-username');
if (participant_name_div) {
    participant_name_div.addEventListener('input', update_participant_initials);
}

function update_participant_initials() {
    let participan_name = document.getElementById('participant-name-initials');
    if (participan_name) {
        if (participant_name_div.value == '' || participant_name_div.value == null || participant_name_div.value == undefined || !charIsLetter(participant_name_div.value[0])) {
            participan_name.innerHTML = '';
        }
        else {
            participan_name.innerHTML = participant_name_div.value[0].toUpperCase();
        }
    }
}

function charIsLetter(char) {
    if (typeof char !== 'string') {
        return false;
    }
    return /^[a-zA-Z]+$/.test(char);
}

function set_cogno_meet_current_session_local_storage_obj(key, value) {
    try {
        let local_storage_name = "cognomeet_meeting_session";

        let local_storage_obj = localStorage.getItem(local_storage_name);

        if (local_storage_obj) {
            local_storage_obj = JSON.parse(local_storage_obj);
            local_storage_obj[session_id][key] = value;
            localStorage.setItem(local_storage_name, JSON.stringify(local_storage_obj));
        }
    } catch (err) {
        console.log("ERROR: set_cogno_meet_current_session_local_storage_obj ", err);
    }
}

function cogno_meet_create_local_storage_obj() {
    if (localStorage.getItem("cognomeet_meeting_session") == null) {
        let local_storage_json_object = {};
        local_storage_json_object[session_id] = {};
        localStorage.setItem("cognomeet_meeting_session", JSON.stringify(local_storage_json_object));
    } else {
        let local_storage_obj = localStorage.getItem("cognomeet_meeting_session");
        local_storage_obj = JSON.parse(local_storage_obj);
        if (!local_storage_obj.hasOwnProperty(session_id)) {
            let local_storage_json_object = {};
            local_storage_json_object[session_id] = {};
            localStorage.setItem("cognomeet_meeting_session", JSON.stringify(local_storage_json_object));
        }
    }
}

function cogno_meet_clear_local_storage() {
    localStorage.removeItem("cognomeet_meeting_session");
}

function get_cogno_meet_current_session_local_storage_obj() {
    try {
        let local_storage_obj = null;
        let cognomeet_session_id = session_id;

        if (localStorage.getItem("cognomeet_meeting_session") != null) {
            local_storage_obj = localStorage.getItem("cognomeet_meeting_session");
            local_storage_obj = JSON.parse(local_storage_obj);
            if (local_storage_obj.hasOwnProperty(cognomeet_session_id)) {
                local_storage_obj = local_storage_obj[cognomeet_session_id];
            } else {
                return null;
            }
        }
        return local_storage_obj;
    } catch (error) {
        return null;
    }
}

function get_dyte_participant_id() {
    let dyte_participant_id = null;
    let local_storage_obj = get_cogno_meet_current_session_local_storage_obj();
    if (local_storage_obj && local_storage_obj.hasOwnProperty("dyte_participant_id")) {
        dyte_participant_id = local_storage_obj["dyte_participant_id"];
    }
    return dyte_participant_id;
}

function get_participant_name() {
    let participant_display_name = null;
    let local_storage_obj = get_cogno_meet_current_session_local_storage_obj();
    if (local_storage_obj && local_storage_obj.hasOwnProperty("participant_display_name")) {
        participant_display_name = local_storage_obj["participant_display_name"];
    }
    return participant_display_name;
}

function set_easyassist_cookie(cookiename, cookievalue) {

    let domain = window.location.hostname;
    let max_age = 24 * 60 * 60;

    if (window.location.protocol == "https:") {
        document.cookie = cookiename + "=" + cookievalue + ";max-age=" + max_age + ";path=/;domain=" + domain + ";secure";
    } else {
        document.cookie = cookiename + "=" + cookievalue + ";max-age=" + max_age + ";path=/;";
    }
}

function get_easyassist_cookie(cookiename) {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + cookiename.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? matches[1] : undefined;
}

function delete_easyassist_cookie(cookiename) {

    let domain = window.location.hostname;

    if (window.location.protocol == "https:") {
        document.cookie = cookiename + "=;path=/;domain=" + domain + ";secure;expires = Thu, 01 Jan 1970 00:00:00 GMT";
    } else {
        document.cookie = cookiename + "=;path=/;expires = Thu, 01 Jan 1970 00:00:00 GMT";
    }
}

function close_meeting() {
    const request_params = {
        "session_id": session_id
    };

    const json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/cogno-meet/close-meeting/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            
        }
    }
    xhttp.send(params);
}

function show_cognomeet_toast(message) {
    let element = document.getElementById("easyassist-meeting-snackbar");
    element.innerHTML = message;
    element.className = "show";
    setTimeout(function () { element.className = element.className.replace("show", ""); }, 5000);
}

function save_client_location_details(participant_location, latitude, longitude) {
    request_params = {
        "session_id": session_id,
        "client_name": client_display_name,
        "longitude": longitude,
        "latitude": latitude,
        "client_address": participant_location,
    };
    json_params = JSON.stringify(request_params);

    encrypted_data = easyassist_custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    let params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/cogno-meet/save-client-location-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] != 200) {
                console.log("Failed to save customer's location");
            }
        }
    }
    xhttp.send(params);
}

function initialize_customer_heartbeat_interval() {
    if (customer_heartbeat_interval == null) {
        customer_heartbeat_interval = setInterval(send_customer_heartbeat, CUSTOMER_HEARTBEAT_FREQUENCY);
        send_customer_heartbeat();
    }
}

function send_customer_heartbeat() {
    let request_params = {
        "session_id": window.session_id
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/cogno-meet/update-customer-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status != 200) {
                console.log('Heartbeat not sent successfully');
            } 
        }
    }
    xhttp.send(params);
}

function initiate_customer_countdown_timer() {
    if (is_customer_countdown_timer_enabled()) {
        let local_storage_obj = get_cogno_meet_current_session_local_storage_obj();
        if (local_storage_obj != null && local_storage_obj.hasOwnProperty("easyassist_meeting_timer_value")) {
            easyassist_start_agent_wait_timer(parseInt(local_storage_obj["easyassist_meeting_timer_value"]));
        } else {
            easyassist_start_agent_wait_timer(window.no_agent_connects_meeting_toast_threshold * 60);
        }

        if (local_storage_obj != null && local_storage_obj.hasOwnProperty("easyassist_meeting_initial_timer_exhausted") &&
            local_storage_obj["easyassist_meeting_initial_timer_exhausted"] == "true") {
            document.getElementById("meeting-msg").innerHTML = window.no_agent_connects_meeting_toast_text;
        } else {
            document.getElementById("meeting-msg").innerHTML = initial_customer_waiting_message;
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
    set_cogno_meet_current_session_local_storage_obj("easyassist_meeting_timer_value", initial_timer_value);
    clear_no_agent_connect_timer_interval();
}

function easyassist_start_agent_wait_timer(waiting_time_seconds) {

    function update_agent_wait_timer() {
        try {
            if (waiting_time_seconds <= 0) {
                // restart timer
                set_cogno_meet_current_session_local_storage_obj("easyassist_meeting_initial_timer_exhausted", "true");
                document.getElementById("meeting-msg").innerHTML = window.no_agent_connects_meeting_toast_text;
                easyassist_start_agent_wait_timer(window.no_agent_connects_meeting_toast_threshold * 60);
            }

            if (waiting_time_seconds <= 15) {
                document.getElementById("easyassist-customer-waiting-timer-div").style.color = "#E53E3E";
            } else {
                document.getElementById("easyassist-customer-waiting-timer-div").style.color = "#25B139";
            }

            document.getElementById("customer-waiting-time-value").innerHTML = waiting_time_seconds;
            waiting_time_seconds = waiting_time_seconds - 1;
            set_cogno_meet_current_session_local_storage_obj("easyassist_meeting_timer_value", waiting_time_seconds);
        } catch (err) {
            console.log("easyassist_start_agent_wait_timer: ", err);
        }
    }

    clear_no_agent_connect_timer_interval();

    update_agent_wait_timer();
    no_agent_connect_timer_interval = setInterval(function () {
        update_agent_wait_timer();
    }, 1000);
}

function is_customer_countdown_timer_enabled() {
    if (enable_no_agent_connects_toast_meeting == "True") {
        return true;
    }
    return false;
}

function clear_no_agent_connect_timer_interval() {
    if (no_agent_connect_timer_interval != null) {
        clearInterval(no_agent_connect_timer_interval);
        no_agent_connect_timer_interval = null;
    }
}

function toggle_background_music(play_music) {
    try {
        let audio_player = document.getElementById("audioplayer");
        if (!audio_player) {
            return;
        }
        if (play_music) {
            audio_player.play();
        } else {
            audio_player.pause();
        }
    } catch (error) {

    }
}

function toggle_join_meeting_music() {
    
    if (is_lobby_audio_muted) {
        toggle_background_music(true);
        is_lobby_audio_muted = !is_lobby_audio_muted;
        document.getElementById('lobby-audio-disabled').style.display = 'none';
        document.getElementById('lobby-audio-enabled').style.display = 'block';
    } else {
        toggle_background_music(false);
        is_lobby_audio_muted = !is_lobby_audio_muted;
        document.getElementById('lobby-audio-enabled').style.display = 'none';
        document.getElementById('lobby-audio-disabled').style.display = 'block';
    }
}

function check_meeting_ended_or_not(){
    let request_params = {
        "session_id": session_id,
    };
    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/cogno-meet/check-meeting-ended-or-not/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                window.location.reload()
            }
            else if(response.status == 301){
                if(!show_time_notification){
                    show_cognomeet_toast("This session will end in 5 minutes.");
                    show_time_notification = true;
                }
            }
        }
    }
    xhttp.send(params);
}

function check_meeting_participant_limit(display_name) {
    let request_params = {
        "session_id": session_id,
    };
    let json_params = JSON.stringify(request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/cogno-meet/check-participant-limit/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                hide_pages();
                create_participant(is_agent, display_name);
            } else if(response.status == 301){
                show_cognomeet_toast(TIMEOUT_ERROR_MESSAGE);
            } else if(response.status == 302){
                show_cognomeet_toast(response.message);
            } else {
                show_cognomeet_toast(TIMEOUT_ERROR_MESSAGE);
            }
        }
    }
    xhttp.send(params);
}