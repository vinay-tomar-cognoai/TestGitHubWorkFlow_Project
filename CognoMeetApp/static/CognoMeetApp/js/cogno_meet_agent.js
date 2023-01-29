const AGENT_HEARTBEAT_FREQUENCY = 10000;
let meeting = null;
let client_websocket = null;
let save_notes_timer = null;
let sync_utils_client_websocket = null;
let client_websocket_open = false;
let sync_utils_client_websocket_open = false;
let displayStream = null;
let display_media_available = false;
const reg_email = /^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/;
let agent_heartbeat_interval = null;
let is_mic_enabled = false;
let is_camera_enabled = false;
const MAXIMUM_PARTICIPANTS_LIMIT_MESSAGE = "Unable to invite the participant as maximum number of partcipants that can be present in a meeting has reached.";
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

function capture_user_video(value) {
    const constraints = {
      video: true,
    };

    const video_element = document.getElementById("cognomeet-lobby-video-element");
    if(value) {
        navigator.mediaDevices.getUserMedia(constraints)
        .then((stream) => {
          video_element.srcObject = stream;
          video_element.style.display = "initial";
          document.getElementById("participant-initial-svg").style.display = 'none';
          video_element.style.background = 'initial';
        })
        .catch(function() {
            show_cognomeet_toast("Please grant camera permission.")
            video_element.style.background = '';
            video_element.style.display = "none";
            document.getElementById("participant-initial-svg").style.display = 'initial'; 
            toggle_camera(false);
        });
    } else {
        video_element.src = '';
        video_element.srcObject.getVideoTracks()[0].stop();
        video_element.srcObject = null;
        video_element.style.background = '';
        video_element.style.display = "none";
        document.getElementById("participant-initial-svg").style.display = 'initial';
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


function check_meeting_username_and_password(session_id) {
    let display_name = "None";
    if (is_agent == 'False' && is_invited_agent == 'False') {
        let error_message_element = document.getElementById("authenticate-details-error");
        error_message_element.innerHTML = "";
        display_name = document.getElementById("meeting-joining-username").value.trim();
        display_name = stripHTML(display_name);
        display_name = remove_all_special_characters_from_str(display_name);
        const reg_name = /^[a-zA-Z]+[a-zA-Z ]+$/;
        if (!reg_name.test(display_name)) {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Please enter a valid name";
            return;
        }
    }

    let error_message_element = document.getElementById("authenticate-details-error");
    error_message_element.innerHTML = "";

    let password = document.getElementById("meeting-joining-password").value;
    password = stripHTML(password);

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

    let xhttp = new XMLHttpRequest();
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
    let meeting_room_page = document.getElementById('meeting_room_page');
    let meeting_body = document.getElementById('meeting-body');

    if (waiting_page) {
        waiting_page.style.display = "none";
    }
    if (name_and_password_page) {
        name_and_password_page.style.display = "none";
    }
    if (meeting_room_page) {
        meeting_room_page.style.display = "flex";
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
        client_specific_id = `${window.agent_name}_${window.session_id}_${Math.floor(Math.random() * 100000).toString()}`
        set_cogno_meet_current_session_local_storage_obj("client_specific_id", client_specific_id);
    }

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
                start_meet();
            } else {
                show_cognomeet_toast(TIMEOUT_ERROR_MESSAGE);
            }
        }
    }
    xhttp.send(params);
}

function start_meet() {
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
            layout: true,
            screenShare: (screen_sharing == 'True'),
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
                modify_meet_div(100, 75);
                show_meeting_chat_box();
            },
        });
    });

    if (is_invited_agent == 'False') {
        // Participants button
        meeting.on(meeting.Events.meetingJoined, () => {
            button = meeting.controlBar.addButton({
                icon: participant_button_icon,
                label: 'Participants',
                position: 'left',
                onClick: () => {
                    update_participant_list();
                    modify_meet_div(100, 78);
                    show_add_members();
                },
            });
        });
    }

    // Docs button
    meeting.on(meeting.Events.meetingJoined, () => {
        button = meeting.controlBar.addButton({
            icon: docs_button_icon,
            label: 'Docs',
            position: 'right',
            onClick: () => {
                update_support_doc();
                modify_meet_div(100, 78);
                show_meeting_support_docs();
            },
        });
    });

    if (is_invited_agent == 'False') {
        // Notes button
        meeting.on(meeting.Events.meetingJoined, () => {
            button = meeting.controlBar.addButton({
                icon: notes_button_icon,
                label: 'Notes',
                position: 'right',
                onClick: () => {
                    modify_meet_div(100, 78);
                    show_meeting_notes();
                },
            });
        });
    }

    if (is_invited_agent == 'False' && enable_screen_capture == 'True') {
        // Screen Capture button
        meeting.on(meeting.Events.meetingJoined, () => {
            button = meeting.controlBar.addButton({
                icon: screen_capture_button_icon,
                label: 'Screen Capture',
                position: 'left',
                onClick: () => {
                    save_screenshot();
                },
            });
        });
    }

    if (is_invited_agent == 'False' && enable_invite_agent == 'True') {
        // Help button
        meeting.on(meeting.Events.meetingJoined, () => {
            button = meeting.controlBar.addButton({
                icon: help_button_icon,
                label: 'Help',
                position: 'right',
                onClick: () => {
                    modify_meet_div(100, 78);
                    get_list_of_support_agents();
                    show_ask_for_support();
                },
            });
        });
    }
    meeting.onError(function (error) {
        console.log('Error occurent in the cogno meet ', error);
    });

    meeting.init("meeting-body");

    initialize_agent_heartbeat_interval();

    if (allow_meeting_end_time == 'True') {
        if (!is_meeting_interval_set) {
            setInterval(function () {
                check_meeting_ended_or_not();
            }, 30000)
            is_meeting_interval_set = true;
        }
    }

    meeting.on(meeting.Events.meetingJoined, () => {
        if (is_agent == "True") {
            join_meet_message_over_socket(meeting.self.id, meeting.self.name, 'Agent');
        }
        else {
            join_meet_message_over_socket(meeting.self.id, meeting.self.name, 'Support Agent');
            support_agent_joined();
        }
        save_meeting_chats( String(meeting.self.name)+' has joined the chat', 'system', null, null, null, false, get_dyte_participant_id());

        setTimeout(() => {

            disable_audio_video();
            update_meeting_listners();
        }, 500);
    });

    // Participant left meet
    meeting.on(meeting.Events.disconnect, () => {

        hide_all_meeting_options();
        if (meeting.participants.length == 1) {
            // close_meeting();
            setTimeout(close_meeting, 1000);
        }
        show_meeting_leave_page();
    });

    // on screenShare
    meeting.on(meeting.Events.screenSharingUpdated, (isScreensharing) => {
        if(isScreensharing){
            show_cognomeet_toast(`You're now sharing your screen`);
        }
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

function show_meeting_leave_page() {
    let meeting_room_page = document.getElementById('meeting_room_page');
    let leave_page = document.getElementById('meeting-left');
    if (meeting_room_page) {
        meeting_room_page.style.display = 'none';
    }
    if (leave_page) {
        leave_page.style.display = 'block';
    }

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
        "sender": sender
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_chat_socket(encrypted_data);
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

function update_support_doc() {

    document.getElementById("uploaded-document-preview-container").innerHTML = "";

    let json_string = JSON.stringify({
        "id": session_id,
        'primary_agent_username': primary_agent_username
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/get-meet-support-documents/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            let div_inner_html = "";
            if (response.status == 200) {
                let meeting_doc_list = response.support_document;
                if (meeting_doc_list.length > 0) {
                    for (const element of meeting_doc_list) {
                        let support_doc_path = element.file_path;
                        let support_doc_name = element.file_name;
                        append_support_doc_at_end(support_doc_name, support_doc_path);
                    }
                } else {
                    div_inner_html = [
                        '<div class="col-12 pt-4">',
                        '<p style="color: #ffffff;">No document exists</p>',
                        '</div>'
                    ].join('');
                    let support_doc_div = document.getElementById('uploaded-document-preview-container');

                    if (support_doc_div) {
                        support_doc_div.innerHTML += div_inner_html;
                    }
                }
            } else {
                document.getElementById("uploaded-document-preview-container").innerHTML = "Unable to load the documents.";
            }
        } else if (this.readyState == 4) {
            document.getElementById("uploaded-document-preview-container").innerHTML = "Due to some network issue, we are unable to load the documents. Please try again.";
        }
    }
    xhttp.send(params);
}


function update_participant_initials() {
    let participan_name = document.getElementById('participant-name-initials');
    if (participan_name) {
        participan_name.innerHTML = agent_name[0].toUpperCase();
    }
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
    
    // loads chat history
    load_chat_history();
}

function modify_meet_div(height, width) {

    let meet_div = document.getElementById('meeting-body');
    if (meet_div) {
        meet_div.style.height = `${height}%`;
        meet_div.style.width = `${width}%`;
    }
}

function update_meeting_listners() {

    // triggers when other participants joins the meeting 
    meeting.on(meeting.Events.participantJoin, (participant) => {

        update_participant_list();
    });

    // triggers when other participants leave the meeting 
    meeting.on(meeting.Events.participantLeave, (participant) => {
        update_participant_list();
    });
}


function update_participant_list(id=null, audio_enabled=null) {
    let host_name_div = document.getElementById('meeting-host-name');
    let participant_list_div = document.getElementById('cogno-lobby-members-list');
    if (host_name_div) {
        host_name_div.innerHTML = meeting.self.name;
    }

    let participant_list = meeting.participants;

    if (participant_list_div) {
        participant_list_div.innerHTML = '';
        let html = ''
        for (const participant of participant_list) {
            if (participant.id != meeting.self.id && is_agent == 'True') {
                html = [`
            <div class="col-12 pt-3">
                <div>
                <div class="col-12 d-flex justify-content-between align-items-center">
                    ${participant.name}
                    <div class="action-button">
                    <button class="custom-icon-button" onclick="mute_participant_over_socket('${participant.name}','${participant.id}')">
                        ${get_audio_state_for_participant(participant, id, audio_enabled)}
                    </button>
                    <button class="custom-icon-button" data-bs-toggle="modal" data-bs-target="#kick-participant-modal" onclick="update_kick_participant_name('${participant.name}','${participant.id}')">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path
                            d="M11.9199 22C17.4199 22 21.9199 17.5 21.9199 12C21.9199 6.5 17.4199 2 11.9199 2C6.41992 2 1.91992 6.5 1.91992 12C1.91992 17.5 6.41992 22 11.9199 22Z"
                            stroke="#FF4C40" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                        <path d="M7.91992 12H15.9199" stroke="#FF4C40" stroke-width="1.5" stroke-linecap="round"
                            stroke-linejoin="round" />
                        </svg>

                    </button>
                    </div>
                </div>
                </div>
            </div>`].join('');
            }
            else {
                html = [`
            <div class="col-12 pt-3">
                <div>
                <div class="col-12 d-flex justify-content-between align-items-center">
                    ${participant.name}
                    <div class="action-button">
                    <button class="custom-icon-button" onclick="mute_participant_over_socket('${participant.name}','${participant.id}')">
                    ${get_audio_state_for_participant(participant, id, audio_enabled)}
                    </button>
                    <button class="custom-icon-button" data-bs-toggle="modal" data-bs-target="#kick-participant-modal" onclick="update_kick_participant_name('${participant.name}','${participant.id}')">
                        

                    </button>
                    </div>
                </div>
                </div>
            </div>`].join('');
            }
            participant_list_div.innerHTML += html;
        }
    }

}

function get_audio_state_for_participant(participant, id, audio_enabled){
    let svg = ''
    if(id && participant.id == id){
        if(audio_enabled){
            svg = `
            <svg width="30" height="30" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="30" height="30" rx="15" fill="white" fill-opacity="0.1"/>
                <path fill-rule="evenodd" clip-rule="evenodd" d="M17.1908 14.25C17.1908 15.495 16.1858 16.5 14.9408 16.5C13.6958 16.5 12.6908 15.495 12.6908 14.25V9.75005C12.6908 8.50505 13.6958 7.50005 14.9408 7.50005C16.1858 7.50005 17.1908 8.50505 17.1908 9.75005V14.25ZM18.6381 14.8876C18.6981 14.5201 19.0056 14.2501 19.3731 14.2501C19.8306 14.2501 20.1981 14.6551 20.1231 15.1051C19.7556 17.3551 17.9556 19.1176 15.6906 19.4401V21.0001C15.6906 21.4126 15.3531 21.7501 14.9406 21.7501C14.5281 21.7501 14.1906 21.4126 14.1906 21.0001V19.4401C11.9256 19.1176 10.1256 17.3551 9.75814 15.1051C9.69064 14.6551 10.0506 14.2501 10.5081 14.2501C10.8756 14.2501 11.1831 14.5201 11.2431 14.8876C11.5506 16.6501 13.0881 18.0001 14.9406 18.0001C16.7931 18.0001 18.3306 16.6501 18.6381 14.8876Z" 
                fill="white"/>
            </svg>
            `;
        } else {
            svg = `
            <svg width="30" height="30" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="30" height="30" rx="15" fill="white" fill-opacity="0.1" />
            <path
                d="M19.4323 14.25C19.0648 14.25 18.7573 14.52 18.6898 14.88C18.6148 15.3225 18.4498 15.7425 18.2323 16.1175L19.3198 17.205C19.7473 16.5825 20.0473 15.87 20.1748 15.0975C20.2573 14.655 19.8898 14.25 19.4323 14.25V14.25ZM7.5748 8.6325C7.50527 8.70189 7.45011 8.7843 7.41248 8.87503C7.37484 8.96576 7.35547 9.06302 7.35547 9.16125C7.35547 9.25948 7.37484 9.35674 7.41248 9.44747C7.45011 9.5382 7.50527 9.62061 7.5748 9.69L15.7873 17.9025C15.5323 17.97 15.2698 18 14.9998 18C13.1473 18 11.6098 16.6575 11.3023 14.8875C11.2759 14.7111 11.1873 14.5499 11.0525 14.433C10.9178 14.3162 10.7457 14.2512 10.5673 14.25C10.1098 14.25 9.7498 14.655 9.8173 15.105C10.1848 17.355 11.9848 19.11 14.2498 19.44V21C14.2498 21.4125 14.5873 21.75 14.9998 21.75C15.4123 21.75 15.7498 21.4125 15.7498 21V19.44C16.1773 19.38 16.5898 19.26 16.9798 19.1025L20.3023 22.425C20.4425 22.5652 20.6327 22.644 20.8311 22.644C21.0294 22.644 21.2196 22.5652 21.3598 22.425C21.5 22.2848 21.5788 22.0946 21.5788 21.8962C21.5788 21.6979 21.5 21.5077 21.3598 21.3675L8.6323 8.6325C8.56292 8.56297 8.4805 8.50781 8.38977 8.47018C8.29904 8.43254 8.20178 8.41317 8.10355 8.41317C8.00533 8.41317 7.90806 8.43254 7.81733 8.47018C7.7266 8.50781 7.64419 8.56297 7.5748 8.6325V8.6325ZM17.2498 14.25V9.75C17.2498 8.505 16.2448 7.5 14.9998 7.5C13.7548 7.5 12.7498 8.505 12.7498 9.75V10.6275L17.1073 14.985C17.1898 14.7525 17.2498 14.5125 17.2498 14.25V14.25Z"
                fill="white" />
            </svg>
            `;
        }
    } else {
        if(participant.audioEnabled){
            svg = `
            <svg width="30" height="30" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="30" height="30" rx="15" fill="white" fill-opacity="0.1"/>
                <path fill-rule="evenodd" clip-rule="evenodd" d="M17.1908 14.25C17.1908 15.495 16.1858 16.5 14.9408 16.5C13.6958 16.5 12.6908 15.495 12.6908 14.25V9.75005C12.6908 8.50505 13.6958 7.50005 14.9408 7.50005C16.1858 7.50005 17.1908 8.50505 17.1908 9.75005V14.25ZM18.6381 14.8876C18.6981 14.5201 19.0056 14.2501 19.3731 14.2501C19.8306 14.2501 20.1981 14.6551 20.1231 15.1051C19.7556 17.3551 17.9556 19.1176 15.6906 19.4401V21.0001C15.6906 21.4126 15.3531 21.7501 14.9406 21.7501C14.5281 21.7501 14.1906 21.4126 14.1906 21.0001V19.4401C11.9256 19.1176 10.1256 17.3551 9.75814 15.1051C9.69064 14.6551 10.0506 14.2501 10.5081 14.2501C10.8756 14.2501 11.1831 14.5201 11.2431 14.8876C11.5506 16.6501 13.0881 18.0001 14.9406 18.0001C16.7931 18.0001 18.3306 16.6501 18.6381 14.8876Z" 
                fill="white"/>
            </svg>
            `;
        } else {
            svg = `
            <svg width="30" height="30" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="30" height="30" rx="15" fill="white" fill-opacity="0.1" />
            <path
                d="M19.4323 14.25C19.0648 14.25 18.7573 14.52 18.6898 14.88C18.6148 15.3225 18.4498 15.7425 18.2323 16.1175L19.3198 17.205C19.7473 16.5825 20.0473 15.87 20.1748 15.0975C20.2573 14.655 19.8898 14.25 19.4323 14.25V14.25ZM7.5748 8.6325C7.50527 8.70189 7.45011 8.7843 7.41248 8.87503C7.37484 8.96576 7.35547 9.06302 7.35547 9.16125C7.35547 9.25948 7.37484 9.35674 7.41248 9.44747C7.45011 9.5382 7.50527 9.62061 7.5748 9.69L15.7873 17.9025C15.5323 17.97 15.2698 18 14.9998 18C13.1473 18 11.6098 16.6575 11.3023 14.8875C11.2759 14.7111 11.1873 14.5499 11.0525 14.433C10.9178 14.3162 10.7457 14.2512 10.5673 14.25C10.1098 14.25 9.7498 14.655 9.8173 15.105C10.1848 17.355 11.9848 19.11 14.2498 19.44V21C14.2498 21.4125 14.5873 21.75 14.9998 21.75C15.4123 21.75 15.7498 21.4125 15.7498 21V19.44C16.1773 19.38 16.5898 19.26 16.9798 19.1025L20.3023 22.425C20.4425 22.5652 20.6327 22.644 20.8311 22.644C21.0294 22.644 21.2196 22.5652 21.3598 22.425C21.5 22.2848 21.5788 22.0946 21.5788 21.8962C21.5788 21.6979 21.5 21.5077 21.3598 21.3675L8.6323 8.6325C8.56292 8.56297 8.4805 8.50781 8.38977 8.47018C8.29904 8.43254 8.20178 8.41317 8.10355 8.41317C8.00533 8.41317 7.90806 8.43254 7.81733 8.47018C7.7266 8.50781 7.64419 8.56297 7.5748 8.6325V8.6325ZM17.2498 14.25V9.75C17.2498 8.505 16.2448 7.5 14.9998 7.5C13.7548 7.5 12.7498 8.505 12.7498 9.75V10.6275L17.1073 14.985C17.1898 14.7525 17.2498 14.5125 17.2498 14.25V14.25Z"
                fill="white" />
            </svg>
            `;
        }
    }
    
    return svg;
}

function mute_participant_over_socket(name, id) {

    let json_string = JSON.stringify({
        "type": 'mute_participant',
        "sender_id": id,
        "sender": 'agent',
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_chat_socket(encrypted_data);
}

function update_kick_participant_name(participant_name, participant_id) {
    window.kick_participant_name = participant_name;
    window.kick_participant_id = participant_id;

    let kick_participant_name_div = document.getElementById('kick-customer-name');

    let name_div = document.getElementById('kick-participant-name-initials');
    if(name_div){
        name_div.innerHTML = participant_name[0].toUpperCase();
    }
    if (kick_participant_name_div) {
        kick_participant_name_div.innerHTML = `Remove ${participant_name} from this meeting?`;
    }
}

function remove_participant_using_id() {
    meeting.kick(kick_participant_id);

    let json_string = JSON.stringify({
        'type': 'kick_participant',
        'kick_participant_id': kick_participant_id,
        'kicked_participant_name': kick_participant_name
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_chat_socket(encrypted_data);

    document.getElementById('kick-participant-cancel-button').click();
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
    let sender;

    if (is_agent == 'True') {
        sender = "agent"
    } else {
        sender = "invited_agent"
    }
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
        let dyte_participant_id = data["dyte_participant_id"];
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

        if(window.is_agent == "True" && msg_sender == "client") {
            save_meeting_chats(message_body, msg_sender, file_attachment_name, sender_name, attachment_link, is_file_attachment, dyte_participant_id);
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
            meeting.leaveRoom();
            show_kicked_participant_page();
        }
    }
    else if (client_packet.type == 'permit_request') {
        data = client_packet;
        let participant_name = data["participant_name"];
        let status = data["status"];
        let sender = message["header"]["sender"];

        if (meeting != null && meeting != undefined && is_agent == 'True' && sender == 'customer') {
            show_permit_modal_to_agent(participant_name)
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
        let dyte_participant_id = data["dyte_participant_id"];
        let msg_sender = message["header"]["sender"];
        if (meeting != null && meeting != undefined && id != meeting.self.id) {
            let participant_name = data["participant_name"];
            let sender = data["sender"];
            show_cognomeet_toast(`${participant_name} joined the meeting`);
            participant_joined_chat(participant_name,sender);
        }

        if(window.is_agent == "True" && msg_sender == "customer") {
            save_meeting_chats(String(data["participant_name"])+' has joined the chat', 'system', null, null, null, false, dyte_participant_id);
        }

    }
    else if(client_packet.type == 'audio_toggled'){
        data = client_packet;
        let id = data["id"];
        let audio_enabled = data["audio_enabled"];
        if (is_agent == 'True') {
            update_participant_list(id, audio_enabled);
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

function show_permit_modal_to_agent(name) {
    let permit_div = document.getElementById('permit-participant-modal');
    if (permit_div) {
        if (permit_div.style.display == 'block') {
            return;
        }
        permit_div.style.display = 'block';
        document.getElementById('permit-participant-modal-text').innerHTML = `${name} wants to join this meeting`;
        let name_div = document.getElementById('permit-participant-name-initials');
        if(name_div){
            name_div.innerHTML = name[0].toUpperCase();
        }
        document.getElementById('permit-participant-modal-deny-button').addEventListener('click', function () {
            permit_request_to_client_over_socket('deny');
            permit_div.style.display = 'none';
        });
        document.getElementById('permit-participant-modal-permit-button').addEventListener('click', function () {
            permit_request_to_client_over_socket('permit');
            permit_div.style.display = 'none';
        });

    }
}

function permit_request_to_client_over_socket(status) {

    let json_string = JSON.stringify({
        "type": "permit_request",
        "participant_name": agent_name,
        "status": status,
        "sender": 'agent'
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_chat_socket(encrypted_data);
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
        if (msg_sender == 'invite_agent') {
            html = [
                `
                <div class="message message-${position}">
                    <div class="bubble bubble-dark">
                    <div class="mt-1 mb-1">
                        ${message}
                    </div>
                    <div class="message-timer">
                        ${current_time} <span>|</span> ${'Support Agent ' + full_name}
                    </div>
                    </div>
                </div>`
            ].join('');
        }
        else if (msg_sender == 'agent') {
            html = [
                `
                <div class="message message-${position}">
                    <div class="bubble bubble-dark">
                    <div class="mt-1 mb-1">
                        ${message}
                    </div>
                    <div class="message-timer">
                        ${current_time} <span>|</span> ${'Agent ' + full_name}
                    </div>
                    </div>
                </div>`
            ].join('');
        }
        else {
            html = [
                `
                <div class="message message-${position}">
                    <div class="bubble bubble-dark">
                    <div class="mt-1 mb-1">
                        ${message}
                    </div>
                    <div class="message-timer">
                        ${current_time} <span>|</span> ${full_name}
                    </div>
                    </div>
                </div>`
            ].join('');
        }
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
        else if (msg_sender == 'invite_agent') { sender = 'Support Agent' }
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
                    ${current_time} <span>|</span> ${sender +" "+ full_name}
                </div>
                </div>
            </div>`
        ].join('');
    }

    document.getElementById("meeting_chat_room").innerHTML += html;
    scroll_to_bottom();
}

function append_support_doc_at_end(doc_file_name, doc_file_path) {

    let html = [
        `<div class="message message-right mb-3 me-1" id="uploaded-document-container">
            <div class="bubble document-bubble-light">
                <div class="document-container">
                <div class="document-image-container">
                    
                </div>
                <div class="document-name">
                    <p>${doc_file_name}</p>
                </div>
                
                <div class="input-wrapper">
                    <input type="text"  id="support-doc-${doc_file_path}" placeholder="Type here..." autocomplete="off">
                </div>
                <div class="document-send-button">
                    <button class="cogno-lobby-send-document-btn d-flex align-items-center" type="button" onclick="send_support_doc_to_chat('${doc_file_name}','${doc_file_path}');" >
                    <div class="d-flex gap-3">
                        Send
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M13.0581 5.09154L5.92473 1.52487C1.13306 -0.875132 -0.833602 1.09153 1.5664 5.8832L2.2914 7.3332C2.49973 7.7582 2.49973 8.24987 2.2914 8.67487L1.5664 10.1165C-0.833602 14.9082 1.12473 16.8749 5.92473 14.4749L13.0581 10.9082C16.2581 9.3082 16.2581 6.69153 13.0581 5.09154ZM10.3664 8.62487H5.8664C5.52473 8.62487 5.2414 8.34154 5.2414 7.99987C5.2414 7.6582 5.52473 7.37487 5.8664 7.37487H10.3664C10.7081 7.37487 10.9914 7.6582 10.9914 7.99987C10.9914 8.34154 10.7081 8.62487 10.3664 8.62487Z" fill="white"/>
                        </svg> 
                    </div>                  
        </div>
                    </div>                  
                    </button>
                </div>
                
                </div>
            </div>
        </div>`].join('');

    let support_doc_div = document.getElementById('uploaded-document-preview-container');

    if (support_doc_div) {
        support_doc_div.innerHTML += html;
    }
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
            let sender = null;
            if (is_agent == 'True') {
                sender = 'agent';
            }
            else {
                sender = 'invite_agent';
            }

            client_websocket.send(JSON.stringify({
                "message": {
                    "header": {
                        "sender": sender,
                        "sender_name": agent_name
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
        let dyte_participant_id = get_dyte_participant_id();

        append_message_at_end(message, 'right');

        if (is_agent == "True") {
            sender = "agent";
            sender_name = agent_name;
        }
        else {
            sender = "invite_agent";
            sender_name = agent_name;
        }

        save_meeting_chats(message, sender, null, sender_name, null, false, dyte_participant_id);

        let json_string = JSON.stringify({
            "type": "chat",
            "header": {
                "sender_id": meeting.self.id,
                "sender": sender,
                "name": sender_name,
                "full_name": agent_full_name
            },
            "body": message,
            "is_file_attachment": false,
            "file_attachment_name": null,
            "attachment_link": null,
            "dyte_participant_id": dyte_participant_id
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
    let dyte_participant_id = get_dyte_participant_id();
    if (is_agent == "True") {
        sender = "agent";
        sender_name = agent_name;
    }
    else {
        sender = "invite_agent";
        sender_name = agent_name;
    }

    append_attachment_at_end(file_name, attachment_link, 'right');

    save_meeting_chats(null, sender, file_name, sender_name, attachment_link, true, dyte_participant_id);

    let json_string = JSON.stringify({
        "type": "chat",
        "header": {
            "sender_id": meeting.self.id,
            "sender": sender,
            "name": sender_name,
            "full_name": agent_full_name
        },
        "body": null,
        "is_file_attachment": true,
        "file_attachment_name": file_name,
        "attachment_link": attachment_link,
        "dyte_participant_id": dyte_participant_id
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_chat_socket(encrypted_data);

    document.getElementById("meeting_text_message").value = "";

}

function send_support_doc_to_chat(file_name, attachment_link) {
    let support_doc_text = document.getElementById(`support-doc-${attachment_link}`);

    let attachment_url = "/easy-assist/download-file/" + attachment_link;

    send_attachmet_to_chat(attachment_url, file_name);
    send_message_to_chat(attachment_link);

    support_doc_text.value = "";

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

function save_screenshot() {

    let body = document.body,
        doc_html = document.documentElement;
    let new_body_height = Math.max(body.scrollHeight, body.offsetHeight,
        doc_html.clientHeight, doc_html.scrollHeight, doc_html.offsetHeight);

    html2canvas(body, {
        x: window.scrollX,
        y: Math.abs(body.getBoundingClientRect().top),
        width: window.innerWidth,
        height: window.innerHeight,
        logging: false,
        onclone: function (clone_document_node) {
            clone_document_node.body.style.height = String(new_body_height) + "px";
        },
        // ignoreElements: function(element) {
        // },
    }).then(function (canvas) {
        // Get base64URL
        let img_data = canvas.toDataURL('image/png');

        json_string = JSON.stringify({
            "content": img_data,
            "session_id": session_id,
            "type_screenshot": "screenshot"
        });

        let encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        let params = JSON.stringify(encrypted_data);
        let xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/cogno-meet/save-meeting-screenshot/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                let response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response["status"] == 200) {                            
                    show_cognomeet_toast(`Screenshot saved`);
                } else {
                    show_cognomeet_toast("Not able to save the screnshot. Please try again.");
                }
            } else if (this.readyState == 4) {
                show_cognomeet_toast("Not able to save the screnshot. Please try again.");
            }
        }
        xhttp.send(params);
    });
}

// Save meeting chat.
function save_meeting_chats(message_body, msg_sender, attachment_file_name, sender_name, attachment_link, is_file_attachment, dyte_participant_id) {

    let request_params = {
        "message": message_body,
        "sender": msg_sender,
        "attachment_file_name": attachment_file_name,
        "sender_name": sender_name,
        "session_id": session_id,
        "attachment_link": attachment_link,
        "is_file_attachment": is_file_attachment,
        "dyte_participant_id": dyte_participant_id
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/cogno-meet/save-meeting-chats/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if(response.status != 200){
                console.log('Unable to save chat');
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

// local storage handling

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

// Get cobrowse support agents
function get_list_of_support_agents() {

    json_string = JSON.stringify({
        "id": session_id,
        "primary_agent_username": primary_agent_username
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/get-meet-support-agents/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            div_inner_html = "";
            if (response.status == 200) {
                let support_agents = response.support_agents;
                update_help_agent_list(support_agents);

            } else {
                document.getElementById("cogno-lobby-support-agent-list").innerHTML = "Unable to load the details.";
            }
        }
    }
    xhttp.send(params);
}


function update_help_agent_list(support_agents) {
    let help_agent_div = document.getElementById('category-group');
    let html = '';
    if (help_agent_div) {
        help_agent_div.innerHTML = '';
    }

    for (const category in support_agents) {
        let category_list = support_agents[category];
        if(category_list.length){
            let id = category.trim();
                html = [`
                <div class="col-12 mt-2">
                <div class="product-category-container">
                <div class="btn-group product-category-btn-group" >
                    <button type="button" class="btn collapsed" role="group" data-bs-toggle="collapse" data-bs-parent="#category-group" data-bs-target="#${id}">
                    ${category}
                    <span>
                        <svg width="7" height="10" viewBox="0 0 7 10" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M2.60642 9.58711L6.55416 5.98011C7.14861 5.43697 7.14861 4.55959 6.55416 4.01646L2.60642 0.40946C1.64616 -0.467918 0 0.158781 0 1.39825L0 8.61224C0 9.85171 1.64616 10.4645 2.60642 9.58711Z" fill="#FAFAFA"/>
                        </svg>                                                                              
                    </span>
                    </button>
                    
                </div>`].join('');
                
                html += [`
                <div id="${id}" class="collapse" data-bs-parent="#category-group">
                <ul class="">`].join('');
                for (const agent of category_list) {
                html += [`
                <li>
                    <div class="congo-lobby-support-agent-text">
                        ${agent.username} - ${agent.level}
                    </div>
                    <div class="">
                        <button class="category-wise-invite-agent" type="button" onclick="join_cogno_meet_meeting(this,'${agent.username}')">Invite</button>
                    </div>
                </li>`].join('');
                }
                html += [`
                </ul>                            
                </div>`].join('');
            
            html += [`
            </div>
            </div>`].join('');
        }
    }

    help_agent_div.innerHTML = html;
}

// Ask another agents to join meeting.
function join_cogno_meet_meeting(element, agent_name) {

    if(is_participant_limit_reached()) {
        show_cognomeet_toast(MAXIMUM_PARTICIPANTS_LIMIT_MESSAGE);
        return;
    }

    let json_string = JSON.stringify({
        "session_id": session_id,
        "primary_agent_username": primary_agent_username,
        "invited_agent_name": agent_name
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/cogno-meet/set-invited-agent/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        element.innerHTML = "Requesting...";
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            div_inner_html = "";
            if (response.status == 200) {
                let support_agents = response.support_agents;
                element.innerHTML = "Invitation sent";
            } else {
                element.innerHTML = "Invite";
                show_cognomeet_toast("Problem while inviting agent, please try after some time")
            }
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

function invite_people_over_email(element) {
    let error_message_element = document.getElementById("invite-people-mail-error");
    error_message_element.innerHTML = "";

    let email_ids = document.getElementById("client-email-id").value.split(',');
    for (const ele of email_ids) {
        if (!reg_email.test(ele)) {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Please enter valid email id(s).";
            error_message_element.style.display = 'block';
            return;
        }
    }

    if(is_participant_limit_reached()) {
        error_message_element.innerHTML = MAXIMUM_PARTICIPANTS_LIMIT_MESSAGE;
        error_message_element.style.color = "red";
        error_message_element.style.display = "block";
        return;
    }

    let request_params = {
        "email_ids": email_ids,
        "session_id": session_id
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    let params = JSON.stringify(encrypted_data);
    element.innerHTML = "Inviting...";
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/cogno-meet/invite-over-email/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
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

function initialize_agent_heartbeat_interval() {
    if (agent_heartbeat_interval == null) {
        agent_heartbeat_interval = setInterval(send_agent_heartbeat, AGENT_HEARTBEAT_FREQUENCY);
        send_agent_heartbeat();
    }
}

function send_agent_heartbeat() {
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
    xhttp.open("POST", "/cogno-meet/update-agent-status/", true);
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

function meeting_left_leave_option() {
    document.querySelector('.cognomeet-btn-container').style.display = 'none';
    document.getElementById('left-meeting-message').style.display = 'none';
    document.getElementById('agent-left-meet-message').style.display = 'block';
}

function meeting_left_rejoin_option() {
    let meeting_left_page = document.getElementById('meeting-left');
    let name_and_password_page = document.getElementById('name_and_password_page');
    if (meeting_left_page) {
        meeting_left_page.style.display = 'none';
    }
    if (name_and_password_page) {
        name_and_password_page.style.display = 'block';
    }

}

function show_kicked_participant_page() {
    let meeting_room_page = document.getElementById('meeting_room_page');
    let leave_page = document.getElementById('meeting-left');
    if (meeting_room_page) {
        meeting_room_page.style.display = 'none';
    }
    if (leave_page) {
        leave_page.style.display = 'block';
        document.getElementById('left-meeting-message').innerHTML = 'You have been removed from the meeting';
    }
}

function support_agent_joined() {

    json_string = JSON.stringify({
        "session_id": session_id,
        "agent_name": agent_name
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/cogno-meet/support-agent-joined/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status != 200) {
                show_cognomeet_toast('Error while adding support agent to the meeting');
            }
        }
    }
    xhttp.send(params);
}

function is_participant_limit_reached() {
    try {
        if (meeting.participants.length >= window.MAXIMUM_PARTICIPANTS_LIMIT) {
            return true;
        }
        return false;
    } catch (error) {
        return false;
    }
}

function check_meeting_ended_or_not() {
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
                create_participant(is_agent, display_name);
                hide_pages();
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