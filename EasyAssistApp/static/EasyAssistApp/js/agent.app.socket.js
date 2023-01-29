var framesContainer = document.querySelector('#frames-container');
var currentFrameIdx = 0;
var playbackIntervalId = null;
var cobrowseSocket = null;
var is_page_reloaded = false;
var sync_client_web_screen_timer = null;
var cobrowsing_meta_data_page = 1;
var load_more_meta = false;
var client_websocket_open = false;
var client_websocket = null;
var chunk_html_dict = {};
var internet_connectivity_timer = null;
var INTERNET_CON_TIMER = 30000;
var send_attachement_src = "None";
var uploaded_attachement_src = "None";
var sync_client_web_screen_agent_timer = null;
var auto_close_session = false;
var remote_agent_code = null;
var android_screen_width = null;
var app_screen_density = null;
var last_scroll_position = 0;
var close_nav_timeout = null;
var chat_box_loaded = false;
var agent_connected_successfully = false;

function get_url_vars() {
    var vars = {};
    window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m, key, value) {
        vars[key] = value;
    });
    return vars;
}

var utm_source = get_url_vars()["utm"];

window.isMobileDevice = function() {
    let check = false;
    (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4))) check = true;})(navigator.userAgent||navigator.vendor||window.opera);
    return check;
  };

function easyassist_linkify(inputText, color) {
    var replacedText, replacePattern1, replacePattern2;

    //URLs starting with http://, https://, or ftp://
    replacePattern1 = /(\b(https?|ftp):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gim;
    replacedText = inputText.replace(replacePattern1, '<a href="$1" target="_blank" style="color: '+ color +';">$1</a>');

    //URLs starting with "www." (without // before it, or it'd re-link the ones done above).
    replacePattern2 = /(^|[^\/])(www\.[\S]+(\b|$))/gim;
    replacedText = replacedText.replace(replacePattern2, '$1<a href="http://$2" target="_blank" style="color: '+ color +';">$2</a>');

    // Change email addresses to mailto:: links.
    // replacePattern3 = /(([a-zA-Z0-9\-\_\.])+@[a-zA-Z\_]+?(\.[a-zA-Z]{2,6})+)/gim;
    // replacedText = replacedText.replace(replacePattern3, '<a href="mailto:$1" style="color: '+ color +';">$1</a>');

    return replacedText;
}

function set_easyassist_cookie(cookiename, cookievalue) {

    var domain = window.location.hostname;

    if (window.location.protocol == "https:") {
        document.cookie = cookiename + "=" + cookievalue + ";max-age=86400" + ";path=/;domain=" + domain + ";secure";
    } else {
        document.cookie = cookiename + "=" + cookievalue + ";max-age=86400" + ";path=/;";
    }
}

function get_easyassist_cookie(cookiename) {
    var matches = document.cookie.match(new RegExp(
        "(?:^|; )" + cookiename.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? matches[1] : undefined;
}

function delete_easyassist_cookie(cookiename) {

    var domain = window.location.hostname;

    if (window.location.protocol == "https:") {
        document.cookie = cookiename + "=;path=/;domain=" + domain + ";secure;expires = Thu, 01 Jan 1970 00:00:00 GMT";
    } else {
        document.cookie = cookiename + "=;path=/;expires = Thu, 01 Jan 1970 00:00:00 GMT";
    }
}

function reset_internet_connectivity_check_timer() {
    stop_internet_connectivity_check_timer();
    start_internet_connectivity_check_timer();
}

function stop_internet_connectivity_check_timer() {
    if (internet_connectivity_timer != null && internet_connectivity_timer != undefined) {
        clearInterval(internet_connectivity_timer);
    }
}

function show_video_conferencing_window() {
    if (jitsi_meet_api) {
        document.getElementById("client-screenshare-icon").style.display = "";
        document.getElementById("client-video-call-icon").style.display = "none";
        hide_cobrowsing_window();
        document.getElementById("audio-call-iframe").style.display = "block";
        // if (isMobileDevice()) {
        //     hide_cobrowsing_window();
        //     document.getElementById("audio-call-iframe").style.display = "block";
        // } else {
        //     hide_cobrowsing_window();
        //     document.getElementById("audio-call-iframe").style.display = "block";
        // }
    }
}

function hide_video_conferencing_window() {
    if (jitsi_meet_api) {
        document.getElementById("client-screenshare-icon").style.display = "none";
        document.getElementById("client-video-call-icon").style.display = "";
        show_cobrowsing_window();
        document.getElementById("audio-call-iframe").style.display = "none";
        // if (isMobileDevice()) {
        //     show_cobrowsing_window();
        //     document.getElementById("audio-call-iframe").style.display = "none";
        // } else {
        //     show_cobrowsing_window();
        //     document.getElementById("audio-call-iframe").style.display = "none";
        // }
    }
}

function show_cobrowsing_window() {
    if (window.ALLOW_DEFAULT_COBROWSING == "True") {
        document.getElementById("frames-container").style.display = "block";
    }
}

function hide_cobrowsing_window() {
    document.getElementById("frames-container").style.display = "none";
}

function start_internet_connectivity_check_timer() {
    internet_connectivity_timer = setInterval(function(e) {
        show_easyassist_toast("We are not receiving any updates from agent. Kindly check your internet connectivity.");
        reset_internet_connectivity_check_timer();
    }, INTERNET_CON_TIMER);
}

function start_client_activity_status_update(){
    sync_client_web_screen_agent_timer = setInterval(function(e) {
        sync_client_web_screen_agent();
    }, 10000);
    sync_client_web_screen_agent();
}

window.onload = function() {

    is_page_reloaded = true;

    create_easyassist_socket(COBROWSE_SESSION_ID, "agent");

    sync_client_web_screen_timer = setInterval(function(e) {
        agent_heartbeat();
    }, 5000);

    if (utm_source=="client") {
        setTimeout(function(e){
            send_customer_connected_flag();
            //get_client_geolocation();
            get_client_geolication_api();
        }, 2000);
    }

    setTimeout(function() {
        load_allincall_chat_box();
    }, 10000);

    start_client_activity_status_update();

    reset_internet_connectivity_check_timer();

    attach_page_visibility_listener();

    initialize_local_storage_object();

    let edit_access_token = get_easyassist_cookie("edit-access-token");

    if(edit_access_token == COBROWSE_SESSION_ID){
        //document.getElementById("allow-form-control").style.display="block";
        show_android_form_container();
    }else{
        //document.getElementById("allow-form-control").style.display="none";
        show_androd_iframe_container();
    }

};

function attach_page_visibility_listener() {
    var hidden, visibilityChange;
    if (typeof document.hidden !== "undefined") { // Opera 12.10 and Firefox 18 and later support
        hidden = "hidden";
        visibilityChange = "visibilitychange";
    } else if (typeof document.msHidden !== "undefined") {
        hidden = "msHidden";
        visibilityChange = "msvisibilitychange";
    } else if (typeof document.webkitHidden !== "undefined") {
        hidden = "webkitHidden";
        visibilityChange = "webkitvisibilitychange";
    }

    if (typeof document.addEventListener === "undefined" || hidden === undefined) {
        console.error("Page Visibility API not supported.");
    } else {
        // Handle page visibility change
        document.addEventListener(visibilityChange, () => {
            handleVisibilityChange(hidden)
        }, false);

        window.addEventListener('beforeunload', function(event) {
            send_window_focus_change_packet("tab_closed");
        });

        setTimeout(function(e){
            send_window_focus_change_packet("tab_focused");
        }, 2000);
    }
}

function handleVisibilityChange(hidden) {
    if (document[hidden]) {
      send_window_focus_change_packet("tab_not_focused");
    } else {
      send_window_focus_change_packet("tab_focused");
    }
}

function create_image_container(img, width, height, type, is_blur, app_screen_density, coordinates_list, scaling_factor){
    let src = "data:image/"+type+";base64,"+img;
    var img_tag = document.createElement("img");
    img_tag.src = src;
    img_tag.style.width = width.toString()+"px";
    img_tag.style.height = height.toString()+"px";
    img_tag.alt = "App-Cobrowsing";
    img_tag.id = "img-frame-cobrowsing";
    img_tag.style.display = "none";

    if(is_blur){
        img_tag.style.filter = "blur(3px)";
    }else{
        img_tag.style.filter = "none";        
    }
    // img_tag.onload = render_image_frames(coordinates_list);
    img_tag.onload = (event) => {
        render_image_frames(event, app_screen_density, coordinates_list, scaling_factor);
    };

    // img_tag.style.width = width+"px";
    // img_tag.style.height = height+"px";

    // removing the divs which consist of the blur class and previous image tag    
    while (framesContainer.firstChild) {
        framesContainer.removeChild(framesContainer.firstChild);
    }

    framesContainer.appendChild(img_tag);
}


function render_image_frames(event, app_screen_density, coordinates_list, scaling_factor){

    if(framesContainer.children.length > 0){

        // if(framesContainer.children.length > 1){
        //     child_element = framesContainer.children[0];
        //     child_element.parentNode.removeChild(child_element);
        // }

        let child_element = framesContainer.children[framesContainer.children.length - 1];
        child_element.style.display = "block";

        if(coordinates_list != undefined) {
            for (let j = 0; j < coordinates_list.length; j++) {

                var blur_top_pos = Math.round(coordinates_list[j].yMinCoordinate/app_screen_density);
                var blur_left_pos = Math.round(coordinates_list[j].xMinCoordinate/app_screen_density);
                
                var blur_width = Math.round(coordinates_list[j].viewWidth/app_screen_density);
                var blur_height = Math.round(coordinates_list[j].viewHeight/app_screen_density);

                if (scaling_factor != undefined) {
                    blur_width = (blur_width  * scaling_factor);
                    blur_left_pos = (blur_left_pos  * scaling_factor);
                }

                var blur_div = document.createElement("div");
                blur_div.classList.add("easyassist-app-cobrowse-masking");
                blur_div.style.top = blur_top_pos.toString() + "px";
                blur_div.style.left = blur_left_pos.toString() + "px";
                blur_div.style.width = blur_width.toString() + "px";
                blur_div.style.height = blur_height.toString() + "px";
                framesContainer.appendChild(blur_div);   
            }
        }

        child_element.onclick = function(e){
            var offset = $(this).offset();
            var relativeX = (e.pageX - offset.left);
            var relativeY = (e.pageY - offset.top);
            var actualWidth = parseInt(child_element.style.width.replace("px", ""));
            relativeX = (android_screen_width * relativeX) / actualWidth;
            sync_edit_access_click_event(relativeX*3, relativeY*3);
        }

        document.getElementById("easyassist-loader").style.display = "none";
    }
}

function sync_client_web_screen(e) {
    var data = JSON.parse(e.data);
    let message = data.message;
    let client_packet = message.body.Request;

    if (message.body.is_encrypted == false) {
        client_packet = JSON.parse(client_packet);
    } else {
        client_packet = easyassist_custom_decrypt(client_packet);
        client_packet = JSON.parse(client_packet);
    }

    if (message.header.sender == "client") {

        reset_internet_connectivity_check_timer();

        if (client_packet.type == "android_screen") {
            let app_screen_base64 = client_packet.app_screen;
            let app_screen_type = client_packet.app_screen_type;
            app_screen_density = client_packet.app_screen_density;
            var coordinates_list;
            var scaling_factor;

            var is_app_screen_blur = false;
            if("is_blur" in client_packet){
                is_app_screen_blur = client_packet.is_blur;
            }

            if("view_coordinates" in client_packet) {
                if(client_packet.view_coordinates.length > 0) {
                    coordinates_list = client_packet.view_coordinates;
                }
            }

            let app_screen_width = Math.round(client_packet.app_screen_width/app_screen_density);
            let app_screen_height = Math.round(client_packet.app_screen_height/app_screen_density);
            android_screen_width = app_screen_width;

            if (window.innerWidth < app_screen_width) {
                scaling_factor = window.innerWidth / app_screen_width;
            }
            
            app_screen_width = Math.min(app_screen_width, window.innerWidth);
            //app_screen_height = Math.max(app_screen_height, window.innerHeight);

            var frame_container = document.getElementById("frames-container");
            frame_container.style.maxHeight = app_screen_height.toString()+"px";
            let frame_container_width = app_screen_width + 12;
            frame_container.style.width = frame_container_width.toString()+"px";
            frame_container.style.overflowY = "scroll";
            frame_container.style.overflowX = "hidden";

            if (isMobileDevice()) {
                frame_container.style.left = "";
            } else {
                frame_container.style.left = "35%";
            }

            var android_form_container = document.getElementById("form-container");
            android_form_container.style.maxHeight = app_screen_height.toString()+"px";
            android_form_container.style.width = app_screen_width.toString()+"px";
            android_form_container.style.overflowY = "scroll";
            android_form_container.style.overflowX = "hidden";
            android_form_container.style.padding = "1em";
            create_image_container(app_screen_base64, app_screen_width, app_screen_height, app_screen_type, is_app_screen_blur, app_screen_density, coordinates_list, scaling_factor);

        } else if (client_packet.type == "scroll") {

            scrollX = client_packet.data_scroll_x;
            scrollY = client_packet.data_scroll_y;
            if (framesContainer.children.length > 0) {
                let prev_frame = framesContainer.children[0];
                prev_frame.contentWindow.scrollTo(scrollX, scrollY);
            }

        } else if (client_packet.type == "attachment"){

            let attachment = client_packet.file_path;

            var file_name = "image1.png";

            if(client_packet.file_name != "") {
                file_name = client_packet.file_name;
            }
            
            set_client_response(null, attachment, file_name);

        } else if (client_packet.type == "close-session"){

            $("#close_session_modal").modal("show");
            hide_modals();

        } else if (client_packet.type == "chat-message"){

            set_client_response(client_packet.message, null, null);

        } else if (client_packet.type == "form") {

            create_dynamic_form_from_android_view(client_packet.fields);

        } else if (client_packet.type == "enable-control-transfer") {

            set_easyassist_cookie("edit-access-token", COBROWSE_SESSION_ID);
            show_android_form_container();
            show_easyassist_toast("Edit access has been provided to fill the form");

        } else if (client_packet.type == "revoke-control-transfer") {

            delete_easyassist_cookie("edit-access-token");
            show_androd_iframe_container();
            show_easyassist_toast("Edit access has been revoked");

        } else if(client_packet.type == "access_control_typing") {

            /*edit_text_element = document.getElementById("android-access-control-dynamic-text");
            edit_text_element.setAttribute("android-id", client_packet.element_id);
            edit_text_element.setAttribute("android-tag", client_packet.element_type);
            edit_text_element.focus();
            edit_text_element.select();
            edit_text_element.click();
            edit_text_element.onkeyup = function(e) {
                send_updated_edittext_value(edit_text_element.getAttribute("android-id"), this, edit_text_element.getAttribute("android-tag"));
            }*/

        } else if (client_packet.type == "keyboard_activated" && utm_source == "client") {

            edit_access_token = get_easyassist_cookie("edit-access-token");

            if (edit_access_token != COBROWSE_SESSION_ID) {
                return;
            }

            show_custom_keyboard();

            /*edit_text_element = document.getElementById("android-access-control-dynamic-text");
            edit_text_element.value = "";
            edit_text_element.setAttribute("android-id", client_packet.element_id);
            edit_text_element.setAttribute("android-tag", client_packet.element_type);
            edit_text_element.focus();
            edit_text_element.select();
            edit_text_element.click();
            edit_text_element.onkeyup = function(event) {
                //alert(event.keyCode);
                send_keyboard_event_to_agent(event.key);
            };*/

        } else if (client_packet.type == "keyboard_deactivated" && utm_source == "client") {

            /*edit_text_element = document.getElementById("android-access-control-dynamic-text");
            edit_text_element.setAttribute("android-id", client_packet.element_id);
            edit_text_element.setAttribute("android-tag", client_packet.element_type);
            edit_text_element.blur();*/
            hide_custom_keyboard();

        }

    } else {

        if (client_packet.type == "chat-message"){

            /*if (utm_source == "client" && client_packet.sender.startsWith("expert")){
                append_bot_chat_message(client_packet.sender, client_packet.message, null, formatDate(new Date()));
            }else if (utm_source == "client" && client_packet.sender.startsWith("client")){
                append_user_chat_message(client_packet.sender, client_packet.message, null, formatDate(new Date()));
            }else if (utm_source == "expert" && client_packet.sender.startsWith("expert")){
                append_user_chat_message(client_packet.sender, client_packet.message, null, formatDate(new Date()));
            }else{
                append_bot_chat_message(client_packet.sender, client_packet.message, null, formatDate(new Date()));
            }*/

            append_user_chat_message(client_packet.sender, client_packet.message, null, formatDate(new Date()));

        }else if(client_packet.type == "attachment"){

            /*if (utm_source == "client" && client_packet.sender.startsWith("expert")){
                append_bot_chat_message(client_packet.sender, "attachment", client_packet.file_path, formatDate(new Date()));
            }else if (utm_source == "client" && client_packet.sender.startsWith("client")){
                append_user_chat_message("customer", "attachment", client_packet.file_path, formatDate(new Date()));
            }else if (utm_source == "expert" && client_packet.sender.startsWith("expert")){
                append_user_chat_message(client_packet.sender, "attachment", client_packet.file_path, formatDate(new Date()));
            }else{
                append_bot_chat_message("customer", "attachment", client_packet.file_path, formatDate(new Date()));
            }*/

            append_user_chat_message(client_packet.sender, "attachment", client_packet.file_path, formatDate(new Date()));

        }else if(client_packet.type == "revoke-control-transfer"){

            delete_easyassist_cookie("edit-access-token");
            show_androd_iframe_container();
            show_easyassist_toast("Edit access has been revoked");

        }
    }
}

function agent_heartbeat() {

    let json_string = JSON.stringify({
        "type": "heartbeat"
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");

}

function remarks_validation(remarks, close_session_text_error_el, remarks_type, min_length, max_length){
    if(min_length > 0){
        if(!remarks){
            close_session_text_error_el.innerHTML = remarks_type + " cannot be empty."
            close_session_text_error_el.style.display = 'block';
            return "invalid";
        }
        if (remarks.replace(/[^a-z0-9]/gi, '') == "") {
            close_session_text_error_el.innerHTML = remarks_type + " cannot be empty."
            close_session_text_error_el.style.display = 'block';
            return "invalid";
        }
    }
    if(remarks.length > max_length) {
        close_session_text_error_el.innerHTML = remarks_type + " cannot be more than 200 characters."
        close_session_text_error_el.style.display = 'block';
        return "invalid";
    }
    return "valid";
}

function close_agent_confirm_session(element) {

    let close_session_remark_error_el = document.getElementById("close-session-remarks-error");
    let close_session_text_error_el = document.getElementById("close-session-text-error");

    close_session_text_error_el.style.display = "none";
    if(close_session_remark_error_el) {
        close_session_remark_error_el.style.display = "none";
    }

    let is_helpful = document.getElementById("mask-successfull-cobrowsing-session").checked;
    let is_test = document.getElementById("mask-test-cobrowsing-session").checked;

    let comment_desc = "";
    let comments = "";
    let subcomments = "";

    if(ENABLE_PREDEFINED_REMARKS == "True") {
        comments = document.getElementById("close-session-remarks").value;
        if(document.getElementById("close-session-subremarks")) {
            subcomments = document.getElementById("close-session-subremarks").value;
        }
        comment_desc = document.getElementById("close-session-remarks-text").value;

        comments = remove_special_characters_from_str(comments);
        subcomments = remove_special_characters_from_str(subcomments);
        comment_desc = remove_special_characters_from_str(comment_desc);

        if(PREDEFINED_REMARKS_OPTIONAL == "False") {
            if (comments.length == 0) {
                close_session_remark_error_el.innerHTML = "Please select a remark";
                close_session_remark_error_el.style.display = 'block';
                return;
            }

            if(remarks_validation(comments, close_session_text_error_el, "Remarks", 1, 200) == "invalid") {
                return;
            }

            if(ENABLE_PREDEFINED_SUBREMARKS == "True") {
                if(remarks_validation(subcomments, close_session_text_error_el, "Subremarks", 1, 200) == "invalid") {
                    return;
                }
            }
        }

        if(comments == "others"){
            if(is_test == false  && remarks_validation(comment_desc, close_session_text_error_el, "Comments", 1, 200) == "invalid"){
                return;
            }
        } else {
            if(is_test == false && remarks_validation(comment_desc, close_session_text_error_el, "Comments", 0, 200) == "invalid"){
                return;
            }
        }

    } else {
        comments = document.getElementById("close-session-remarks-text").value;
        comments = remove_special_characters_from_str(comments);

        if(remarks_validation(comments, close_session_text_error_el, "Remarks", 1, 200) == "invalid") {
            return;
        }
    }

    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID,
        "is_helpful": is_helpful,
        "is_test": is_test,
        "comments": comments,
        "subcomments": subcomments,
        "comment_desc": comment_desc
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "closing...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/close-session/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                easyassist_clear_local_storage();
                window.location = "/easy-assist/sales-ai/dashboard/";
            } else {
                element.innerHTML = "Close";
            }
        }
    }
    xhttp.send(params);
}

class EasyassistCustomSelect {
    constructor(selector, placeholder, background_color) {
        this.placeholder = placeholder;
        this.background_color = background_color;

        var select_element = document.querySelector(selector);
        var selected_list_class = "easyassist-option-selected";
        var show_option_container_class = "easyassist-dropdown-show";
        var custom_dropdown_selected_option = "";
        var dropdown_option_selected = false;

        var custom_dropdown_wrapper = "";
        var custom_dropdown_option_container = "";
        var custom_dropdown_selected_option_wrapper = "";

        // Create elements
        custom_dropdown_wrapper = create_element('div', 'easyassist-custom-dropdown-container');
        custom_dropdown_option_container = create_element('ul', 'easyassist-custom-dropdown-option-container');
        custom_dropdown_selected_option_wrapper = create_element('div', 'easyassist-dropdown-selected');
        // select_element.wrap(custom_dropdown_wrapper);

        select_element.parentNode.prepend(custom_dropdown_wrapper);
        custom_dropdown_wrapper.appendChild(select_element)

        if(this.placeholder){
            select_element.selectedIndex = -1;
        }

        var select_option_records = get_custom_dropdown_option_html();
        dropdown_option_selected = select_option_records.dropdown_option_selected;
        custom_dropdown_selected_option = select_option_records.dropdown_selected_option;

        custom_dropdown_option_container.innerHTML = select_option_records.option_html;
        select_element.insertAdjacentElement('afterend', custom_dropdown_option_container)

        if(dropdown_option_selected) {
            custom_dropdown_selected_option_wrapper.innerHTML = custom_dropdown_selected_option;
        } else if(this.placeholder) { 
            custom_dropdown_selected_option_wrapper.innerHTML = this.placeholder;
        } else {
            custom_dropdown_selected_option_wrapper.innerHTML = custom_dropdown_selected_option;
        }

        select_element.insertAdjacentElement('afterend', custom_dropdown_selected_option_wrapper);

        // Add eventlistener
        document.addEventListener('click', function(e) {
            if(e.target == custom_dropdown_selected_option_wrapper) {
                custom_dropdown_option_container.classList.toggle(show_option_container_class);
            } else {
                custom_dropdown_option_container.classList.remove(show_option_container_class);
            }
        });

        custom_dropdown_add_event_listener();

        var _this = this;
        Object.defineProperty(select_element, 'reinitialize', {
            value: function() {
                let select_option_records = get_custom_dropdown_option_html();
                let dropdown_option_selected = select_option_records.dropdown_option_selected;
                let custom_dropdown_selected_option = select_option_records.dropdown_selected_option;

                custom_dropdown_option_container.innerHTML = select_option_records.option_html;

                if(dropdown_option_selected) {
                    custom_dropdown_selected_option_wrapper.innerHTML = custom_dropdown_selected_option;
                } else if(_this.placeholder) { 
                    custom_dropdown_selected_option_wrapper.innerHTML = _this.placeholder;
                } else {
                    custom_dropdown_selected_option_wrapper.innerHTML = custom_dropdown_selected_option;
                }
                custom_dropdown_add_event_listener();
            }
        });

        function reset_dropdown() {
            for(let idx = 0; idx < custom_dropdown_option_container.children.length; idx ++) {
                custom_dropdown_option_container.children[idx].classList.remove(selected_list_class);
                custom_dropdown_option_container.children[idx].style.removeProperty('background-color');
            }
        }

        function create_element(html_tag, css_class) {
            let html_element = document.createElement(html_tag);
            html_element.className = css_class;
            return html_element;
        }

        function get_custom_dropdown_option_html() {
            let custom_dropdown_options = "";
            let dropdown_option_selected = false;
            let custom_dropdown_selected_option = "";

            for(var idx = 0; idx < select_element.children.length; idx ++) {
                let option_el = select_element.children[idx];
                let option_text = option_el.text.trim();
                let option_value = option_el.value;

                if(option_el.selected) {
                    dropdown_option_selected = true;
                    custom_dropdown_selected_option = option_text;
                    custom_dropdown_options += [
                        '<li  class="' + selected_list_class + '">',
                            '<span>' + option_text + '</span>',
                            '<input type="hidden" value="' + option_value + '">',
                        '</li>',
                    ].join('');
                } else {
                    custom_dropdown_options += [
                        '<li>',
                            '<span>' + option_text + '</span>',
                            '<input type="hidden" value="' + option_value + '">',
                        '</li>',
                    ].join('');
                }
            }
            return {
                option_html: custom_dropdown_options,
                dropdown_option_selected: dropdown_option_selected,
                dropdown_selected_option: custom_dropdown_selected_option,
            };
        }

        function custom_dropdown_add_event_listener() {
            for(let idx = 0; idx < custom_dropdown_option_container.children.length; idx ++) {
                let li_element = custom_dropdown_option_container.children[idx];
                li_element.addEventListener('click', function(e) {
                    let selected_option_text = this.innerHTML;
                    reset_dropdown();
                    li_element.classList.add(selected_list_class);
                    li_element.style.setProperty('background-color', background_color, 'important');
                    custom_dropdown_selected_option_wrapper.innerHTML = selected_option_text;
                    custom_dropdown_option_container.classList.toggle(show_option_container_class);

                    // Update selecte drodown
                    let option_value = li_element.children[1].value;
                    select_element.value = option_value;
                    var change_event = new Event('change');
                    select_element.dispatchEvent(change_event);
                });

                li_element.addEventListener('mouseover', function(e) {
                    li_element.style.setProperty('background-color', background_color, 'important');
                });

                li_element.addEventListener('mouseout', function(e) {
                    if(!li_element.classList.contains(selected_list_class)) {
                        li_element.style.removeProperty('background-color');
                    }
                })
            }
        }
    }
}

function fetch_cobrowsing_meta_information() {

    if (load_more_meta == false) {
        cobrowsing_meta_data_page = 1;
        document.getElementById("meta_information_body").innerHTML = "Loading...";
    }

    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID,
        "page": cobrowsing_meta_data_page
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/get-meta-information/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                var tbody_html = '';
                let meta_information_list = response.meta_information_list;
                for (var index = 0; index < meta_information_list.length; index++) {
                    let meta_id = meta_information_list[index]["id"];
                    //if (meta_information_list[index]["type"] == "screenshot") {
                    tbody_html += '<tr><td><a target="_blank" href="' + meta_information_list[index]["content"] + '">' + meta_information_list[index]["type"] + '</a></td><td>' + meta_information_list[index]["datetime"] + '</td><td><!--<a href="/easy-assist/agent/export/' + meta_id + '/?type=img" target="_blank" title="Export As Image"><i class="fas fa-fw fa-download"></i></a>-->&nbsp;<a href="/easy-assist/agent/export/' + meta_id + '/?type=html" target="_blank" title="Export As HTML"><i class="fas fa-fw fa-file-download"></i></a></td></tr>';
                    //} else {
                    //    tbody_html += '<tr><td>' + meta_information_list[index]["type"] + '</td><td>' + meta_information_list[index]["datetime"] + '</td></tr>';
                    //}
                }

                if (response.is_last_page == false) {
                    tbody_html += '<tr onclick="load_more_meta_information(this)"><td colspan="2"><button class="btn btn-primary float-right">Load More</button></td></tr>';
                }

                if (cobrowsing_meta_data_page == 1) {
                    document.getElementById("meta_information_body").innerHTML = tbody_html;
                } else {
                    document.getElementById("meta_information_body").innerHTML += tbody_html;
                }
            } else {
                console.error("Unable to load the details. Kindly try again.");
            }
            load_more_meta = false;
        }
    }
    xhttp.send(params);
}

function load_more_meta_information(element) {
    element.parentElement.removeChild(element);
    cobrowsing_meta_data_page += 1;
    load_more_meta = true;
    fetch_cobrowsing_meta_information();
}


function share_cobrowsing_session(element) {

    document.getElementById("share-session-error").innerHTML = "";

    let support_agents = $("#multiple-support-agent").val();

    if (support_agents.length == 0) {
        document.getElementById("share-session-error").innerHTML = "Please select atleast one support agent with whom you want to share the session.";
        return;
    }

    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID,
        "support_agents": support_agents
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "sharing..";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/share-session/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                $("#askfor_support_modal").modal('hide');
            }
            element.innerHTML = "Share";
        }
    }
    xhttp.send(params);
}


////////////////////////////////////////////////////

/*WebSocket Utilities - Starts*/

function open_easyassist_websocket() {

    client_websocket_open = true;

    json_string = JSON.stringify({
        "type": "android_screen",
        "client_ip_address": window.CLIENT_IP_ADDRESS
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    //console.log("request for html has been sent: ", new Date());
    send_message_over_easyassist_socket(encrypted_data, "agent");

    setTimeout(actions_after_connected_successfully, 2000);
}

function send_customer_connected_flag() {

    client_websocket_open = true;

    json_string = JSON.stringify({
        "type": "customer_connected"
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");
}


function close_easyassist_websocket() {
    client_websocket_open = false;
}

function check_socket_status(e) {
    console.error("WebSocket error observed:", e);
}

function close_easyassist_socket() {
    if (client_websocket == null) {
        return;
    }
    client_websocket.close();
}

/*WebSocket Utilities - Closes*/


function create_easyassist_socket(jid, sender) {
    let ws_scheme = window.location.protocol == "http:" ? "ws" : "wss";
    let url = ws_scheme + '://' + window.location.host + '/ws/cobrowse/' + jid + '/' + sender + "/";
    client_websocket = new WebSocket(url);
    client_websocket.onmessage = sync_client_web_screen;
    client_websocket.onerror = check_socket_status;
    client_websocket.onopen = open_easyassist_websocket;
    client_websocket.onclose = close_easyassist_websocket;
    //console.log("socket has been created");
}

function send_message_over_easyassist_socket(message, sender) {

    if (client_websocket_open && client_websocket != null) {


        let packet = JSON.stringify({
            "message": {
                "header": {
                    "sender": sender
                },
                "body": message
            }
        });

        client_websocket.send(packet);
    } else {
        create_easyassist_socket(COBROWSE_SESSION_ID, "agent");
    }
}

/************ Agent Updates ***************/

function sync_client_web_screen_agent() {

    let cs_token = get_easyassist_cookie("cs_token");

    json_string = JSON.stringify({
        "session_id": COBROWSE_SESSION_ID
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/app/agent-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            //console.log(response);
            if(response["status"] == 200){
                if(response["is_archived"]){
                    if(document.getElementById("close_session_modal").style.display != "block") {
                        show_easyassist_toast("Looks like the customer has left the session. Please provide your comments before ending the session.");
                        $("#close_session_modal").modal("show");
                    }
                    // window.location.reload();
                }
                remote_agent_code = response["agent_name"];
            }
        }
    }

    xhttp.send(params);
}

function get_list_of_support_agents() {

    json_string = JSON.stringify({
        "id": COBROWSE_SESSION_ID
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    document.getElementById("div-support-agents-container").innerHTML = "Loading...";
    document.getElementById("btn-share-cobrowsing-session").style.display = "none";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/get-support-agents/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            let div_inner_html = "";
            if (response.status == 200) {
                support_agents = response.support_agents;
                if (support_agents.length > 0) {
                    div_inner_html += '<strong>Select Support Agent:</strong><select id="multiple-support-agent" multiple="multiple">';
                    for (var index = 0; index < support_agents.length; index++) {
                        let id = support_agents[index]["id"];
                        let username = support_agents[index]["username"];
                        let level = support_agents[index]["level"];
                        div_inner_html += '<option value="' + id + '">' + username + ' - ' + level + '</option>';
                    }
                    div_inner_html += '</select><br><br><p>Select <b>"Share"</b> below if you want to ask for help to other agent?</p>';
                    div_inner_html += '<p style="color:red;" id="share-session-error"></p>';
                    document.getElementById("btn-share-cobrowsing-session").style.display = "block";
                } else {
                    div_inner_html += '<p>No active support agents found.</p>';
                }
                document.getElementById("div-support-agents-container").innerHTML = div_inner_html;
                $("#multiple-support-agent").multiselect({
                    includeSelectAllOption: true,
                });
            } else {
                document.getElementById("div-support-agents-container").innerHTML = "Unable to load the details. Try again.";
            }
        }
    }
    xhttp.send(params);
}

/////////////////////////////////////////////// WebRTC

function initialize_video_recorder(){

    document.getElementById('recording-player').innerHTML = "";

    var video = document.createElement('video');
    video.controls = false;

    var mediaElement = getHTMLMediaElement(video, {
        title: 'Recording status: inactive',
        buttons: ['full-screen'/*, 'take-snapshot'*/],
        showOnMouseEnter: false,
        width: 360,
        onTakeSnapshot: function() {
            var canvas = document.createElement('canvas');
            canvas.width = mediaElement.clientWidth;
            canvas.height = mediaElement.clientHeight;

            var context = canvas.getContext('2d');
            context.drawImage(recordingPlayer, 0, 0, canvas.width, canvas.height);

            window.open(canvas.toDataURL('image/png'));
        }
    });
    document.getElementById('recording-player').appendChild(mediaElement);

    var div = document.createElement('section');
    mediaElement.media.parentNode.appendChild(div);
    mediaElement.media.muted = false;
    mediaElement.media.autoplay = true;
    mediaElement.media.playsinline = true;
    div.appendChild(mediaElement.media);

    var recordingPlayer = mediaElement.media;
    var recordingMedia = document.querySelector('.recording-media');
    var mediaContainerFormat = document.querySelector('.media-container-format');
    var mimeType = 'video/webm';
    var fileExtension = 'webm';
    var type = 'video';
    var recorderType;
    var defaultWidth;
    var defaultHeight;
    var chkFixSeeking = document.querySelector('#chk-fixSeeking');
    var timeSlice = false;
    var btnStartRecording = document.querySelector('#btn-start-recording');

    btnStartRecording.onclick = function(event) {

        var button = btnStartRecording;

        if(button.innerHTML === 'Stop Recording') {
            btnPauseRecording.style.display = 'none';
            button.disabled = true;
            button.disableStateWaiting = true;
            setTimeout(function() {
                button.disabled = false;
                button.disableStateWaiting = false;
            }, 2000);

            button.innerHTML = 'Start Recording';

            function stopStream() {
                if(button.stream && button.stream.stop) {
                    button.stream.stop();
                    button.stream = null;
                }

                if(button.stream instanceof Array) {
                    button.stream.forEach(function(stream) {
                        stream.stop();
                    });
                    button.stream = null;
                }

                let videoBitsPerSecond = null;
                var html = 'Recording status: stopped';
                // html += '<br>Size: ' + bytesToSize(button.recordRTC.getBlob().size);
                recordingPlayer.parentNode.parentNode.querySelector('h2').innerHTML = html;
            }

            if(button.recordRTC) {

                if(button.recordRTC.length) {

                    button.recordRTC[0].stopRecording(function(url) {

                        if(!button.recordRTC[1]) {
                            button.recordingEndedCallback(url);
                            stopStream();
                            saveToDiskOrOpenNewTab(button.recordRTC[0]);
                            return;
                        }

                        button.recordRTC[1].stopRecording(function(url) {
                            button.recordingEndedCallback(url);
                            stopStream();
                            saveToDiskOrOpenNewTab(button.recordRTC[0]);
                        });
                    });
                }
                else {

                    button.recordRTC.stopRecording(function(url) {

                        if(button.blobs && button.blobs.length) {
                            var blob = new File(button.blobs, getFileName(fileExtension), {
                                type: mimeType
                            });

                            button.recordRTC.getBlob = function() {
                                return blob;
                            };

                            url = URL.createObjectURL(blob);
                        }

                        if(chkFixSeeking.checked === true) {
                            // to fix video seeking issues
                            getSeekableBlob(button.recordRTC.getBlob(), function(seekableBlob) {
                                button.recordRTC.getBlob = function() {
                                    return seekableBlob;
                                };

                                url = URL.createObjectURL(seekableBlob);

                                button.recordingEndedCallback(url);
                                saveToDiskOrOpenNewTab(button.recordRTC);
                                stopStream();
                            })
                            return;
                        }

                        button.recordingEndedCallback(url);
                        saveToDiskOrOpenNewTab(button.recordRTC);
                        stopStream();
                    });
                }
            }

            return;
        }

        if(!event) return;

        button.disabled = true;

        var commonConfig = {
            onMediaCaptured: function(stream) {
                button.stream = stream;
                if(button.mediaCapturedCallback) {
                    button.mediaCapturedCallback();
                }

                button.innerHTML = 'Stop Recording';
                button.disabled = false;

                //chkFixSeeking.parentNode.style.display = 'none';
            },
            onMediaStopped: function() {
                button.innerHTML = 'Start Recording';

                if(!button.disableStateWaiting) {
                    button.disabled = false;
                }

                //chkFixSeeking.parentNode.style.display = 'inline-block';
            },
            onMediaCapturingFailed: function(error) {
                console.error('onMediaCapturingFailed:', error);

                if(error.toString().indexOf('no audio or video tracks available') !== -1) {
                    alert('RecordRTC failed to start because there are no audio or video tracks available.');
                }

                if(error.name === 'PermissionDeniedError' && DetectRTC.browser.name === 'Firefox') {
                    alert('Firefox requires version >= 52. Firefox also requires HTTPs.');
                }

                commonConfig.onMediaStopped();
            }
        };

        /*Check for media container format starts*/

	if(mediaContainerFormat.value === 'h264') {
            mimeType = 'video/webm\;codecs=h264';
            fileExtension = 'mp4';

            // video/mp4;codecs=avc1    
            if(isMimeTypeSupported('video/mpeg')) {
                mimeType = 'video/mpeg';
            }
        }

        if(mediaContainerFormat.value === 'mkv' && isMimeTypeSupported('video/x-matroska;codecs=avc1')) {
            mimeType = 'video/x-matroska;codecs=avc1';
            fileExtension = 'mkv';
        }

        if(mediaContainerFormat.value === 'vp8' && isMimeTypeSupported('video/webm\;codecs=vp8')) {
            mimeType = 'video/webm\;codecs=vp8';
            fileExtension = 'webm';
            recorderType = null;
            type = 'video';
        }

        if(mediaContainerFormat.value === 'vp9' && isMimeTypeSupported('video/webm\;codecs=vp9')) {
            mimeType = 'video/webm\;codecs=vp9';
            fileExtension = 'webm';
            recorderType = null;
            type = 'video';
        }

        if(mediaContainerFormat.value === 'pcm') {
            mimeType = 'audio/wav';
            fileExtension = 'wav';
            recorderType = StereoAudioRecorder;
            type = 'audio';
        }

        if(mediaContainerFormat.value === 'opus' || mediaContainerFormat.value === 'ogg') {
            if(isMimeTypeSupported('audio/webm')) {
                mimeType = 'audio/webm';
                fileExtension = 'webm'; // webm
            }

            if(isMimeTypeSupported('audio/ogg')) {
                mimeType = 'audio/ogg; codecs=opus';
                fileExtension = 'ogg'; // ogg
            }

            recorderType = null;
            type = 'audio';
        }

        if(mediaContainerFormat.value === 'whammy') {
            mimeType = 'video/webm';
            fileExtension = 'webm';
            recorderType = WhammyRecorder;
            type = 'video';
        }

        if(mediaContainerFormat.value === 'WebAssembly') {
            mimeType = 'video/webm';
            fileExtension = 'webm';
            recorderType = WebAssemblyRecorder;
            type = 'video';
        }

        if(mediaContainerFormat.value === 'gif') {
            mimeType = 'image/gif';
            fileExtension = 'gif';
            recorderType = GifRecorder;
            type = 'gif';
        }

        if(mediaContainerFormat.value === 'default') {
            mimeType = 'video/webm';
            fileExtension = 'webm';
            recorderType = null;
            type = 'video';
        }

        /*Check for media container format ends*/

        if(recordingMedia.value === 'record-audio-plus-video') {

            captureAudioPlusVideo(commonConfig);

            button.mediaCapturedCallback = function() {
                if(typeof MediaRecorder === 'undefined') { // opera or chrome etc.
                    button.recordRTC = [];

                    if(!params.bufferSize) {
                        // it fixes audio issues whilst recording 720p
                        params.bufferSize = 16384;
                    }

                    var options = {
                        type: 'audio', // hard-code to set "audio"
                        leftChannel: params.leftChannel || false,
                        disableLogs: params.disableLogs || false,
                        video: recordingPlayer
                    };

                    if(params.sampleRate) {
                        options.sampleRate = parseInt(params.sampleRate);
                    }

                    if(params.bufferSize) {
                        options.bufferSize = parseInt(params.bufferSize);
                    }

                    if(params.frameInterval) {
                        options.frameInterval = parseInt(params.frameInterval);
                    }

                    if(recorderType) {
                        options.recorderType = recorderType;
                    }

                    if(videoBitsPerSecond) {
                        options.videoBitsPerSecond = videoBitsPerSecond;
                    }

                    options.ignoreMutedMedia = false;
                    var audioRecorder = RecordRTC(button.stream, options);

                    options.type = type;
                    var videoRecorder = RecordRTC(button.stream, options);

                    // to sync audio/video playbacks in browser!
                    videoRecorder.initRecorder(function() {
                        audioRecorder.initRecorder(function() {
                            audioRecorder.startRecording();
                            videoRecorder.startRecording();
                            btnPauseRecording.style.display = '';
                        });
                    });

                    button.recordRTC.push(audioRecorder, videoRecorder);

                    button.recordingEndedCallback = function() {
                        var audio = new Audio();
                        audio.src = audioRecorder.toURL();
                        audio.controls = true;
                        audio.autoplay = true;

                        //return;

                        //recordingPlayer.parentNode.appendChild(document.createElement('hr'));
                        //recordingPlayer.parentNode.appendChild(audio);

                        //if(audio.paused) audio.play();
                    };

                    return;
                }

                options = {
                    type: type,
                    mimeType: mimeType,
                    disableLogs: params.disableLogs || false,
                    getNativeBlob: false, // enable it for longer recordings
                    video: recordingPlayer
                };

                if(recorderType) {

                    options.recorderType = recorderType;

                    if(recorderType == WhammyRecorder || recorderType == GifRecorder || recorderType == WebAssemblyRecorder) {
                        options.canvas = options.video = {
                            width: defaultWidth || 320,
                            height: defaultHeight || 240
                        };
                    }
                }

                if(videoBitsPerSecond) {
                    options.videoBitsPerSecond = videoBitsPerSecond;
                }

                if(timeSlice && typeof MediaRecorder !== 'undefined') {
                    options.timeSlice = timeSlice;
                    button.blobs = [];
                    options.ondataavailable = function(blob) {
                        button.blobs.push(blob);
                    };
                }

                options.ignoreMutedMedia = false;
                button.recordRTC = RecordRTC(button.stream, options);

                button.recordingEndedCallback = function(url) {
                    //setVideoURL(url);
                };

                button.recordRTC.startRecording();
                btnPauseRecording.style.display = '';
                recordingPlayer.parentNode.parentNode.querySelector('h2').innerHTML = '<img src="https://www.webrtc-experiment.com/images/progress.gif">';
            };
        }

    }

    function setVideoBitrates() {
        var select = document.querySelector('.media-bitrates');
        var value = select.value;

        if(value == 'default') {
            videoBitsPerSecond = null;
            return;
        }

        videoBitsPerSecond = parseInt(value);
    }

    function getVideoResolutions(mediaConstraints) {

        if(!mediaConstraints.video) {
            return mediaConstraints;
        }

        var select = document.querySelector('.media-resolutions');
        var value = select.value;

        if(value == 'default') {
            return mediaConstraints;
        }

        value = value.split('x');

        if(value.length != 2) {
            return mediaConstraints;
        }

        defaultWidth = parseInt(value[0]);
        defaultHeight = parseInt(value[1]);

        if(DetectRTC.browser.name === 'Firefox') {
            mediaConstraints.video.width = defaultWidth;
            mediaConstraints.video.height = defaultHeight;
            return mediaConstraints;
        }

        if(!mediaConstraints.video.mandatory) {
            mediaConstraints.video.mandatory = {};
            mediaConstraints.video.optional = [];
        }

        var isScreen = recordingMedia.value.toString().toLowerCase().indexOf('screen') != -1;

        if(isScreen) {
            mediaConstraints.video.mandatory.maxWidth = defaultWidth;
            mediaConstraints.video.mandatory.maxHeight = defaultHeight;
        }
        else {
            mediaConstraints.video.mandatory.minWidth = defaultWidth;
            mediaConstraints.video.mandatory.minHeight = defaultHeight;
        }

        return mediaConstraints;
    }

    function getFrameRates(mediaConstraints) {
        if(!mediaConstraints.video) {
            return mediaConstraints;
        }

        var select = document.querySelector('.media-framerates');
        var value = select.value;

        if(value == 'default') {
            return mediaConstraints;
        }

        value = parseInt(value);

        if(DetectRTC.browser.name === 'Firefox') {
            mediaConstraints.video.frameRate = value;
            return mediaConstraints;
        }

        if(!mediaConstraints.video.mandatory) {
            mediaConstraints.video.mandatory = {};
            mediaConstraints.video.optional = [];
        }

        var isScreen = recordingMedia.value.toString().toLowerCase().indexOf('screen') != -1;
        if(isScreen) {
            mediaConstraints.video.mandatory.maxFrameRate = value;
        }
        else {
            mediaConstraints.video.mandatory.minFrameRate = value;
        }

        return mediaConstraints;
    }


    function captureUserMedia(mediaConstraints, successCallback, errorCallback) {

        if(mediaConstraints.video == true) {
            mediaConstraints.video = {};
        }

        setVideoBitrates();

        mediaConstraints = getVideoResolutions(mediaConstraints);

        mediaConstraints = getFrameRates(mediaConstraints);

        var isBlackBerry = !!(/BB10|BlackBerry/i.test(navigator.userAgent || ''));
        if(isBlackBerry && !!(navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia)) {
            navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia;
            navigator.getUserMedia(mediaConstraints, successCallback, errorCallback);
            return;
        }

        navigator.mediaDevices.getUserMedia(mediaConstraints).then(function(stream) {
            successCallback(stream);
            setVideoURL(stream, true);
        }).catch(function(error) {
            if(error && (error.name === 'ConstraintNotSatisfiedError' || error.name === 'OverconstrainedError')) {
                alert('Your camera or browser does NOT supports selected resolutions or frame-rates. \n\nPlease select "default" resolutions.');
            }
            else if(error && error.message) {
                alert(error.message);
            }
            else {
                alert('Unable to make getUserMedia request. Please check browser console logs.');
            }

            errorCallback(error);
        });
    }

    function captureAudioPlusVideo(config) {
        captureUserMedia({video: true, audio: true}, function(audioVideoStream) {

            config.onMediaCaptured(audioVideoStream);

            if(audioVideoStream instanceof Array) {
                audioVideoStream.forEach(function(stream) {
                    addStreamStopListener(stream, function() {
                        config.onMediaStopped();
                    });
                });
                return;
            }

            addStreamStopListener(audioVideoStream, function() {
                config.onMediaStopped();
            });
        }, function(error) {
            config.onMediaCapturingFailed(error);
        });
    }


    var btnPauseRecording = document.querySelector('#btn-pause-recording');

    btnPauseRecording.onclick = function() {
        if(!btnStartRecording.recordRTC) {
            btnPauseRecording.style.display = 'none';
            return;
        }

        btnPauseRecording.disabled = true;
        if(btnPauseRecording.innerHTML === 'Pause') {
            btnStartRecording.disabled = true;
            //chkFixSeeking.parentNode.style.display = 'none';
            btnStartRecording.style.fontSize = '15px';
            btnStartRecording.recordRTC.pauseRecording();
            recordingPlayer.parentNode.parentNode.querySelector('h2').innerHTML = 'Recording status: paused';
            recordingPlayer.pause();

            btnPauseRecording.style.fontSize = 'inherit';
            setTimeout(function() {
                btnPauseRecording.innerHTML = 'Resume Recording';
                btnPauseRecording.disabled = false;
            }, 2000);
        }

        if(btnPauseRecording.innerHTML === 'Resume Recording') {
            btnStartRecording.disabled = false;
            //chkFixSeeking.parentNode.style.display = 'none';
            btnStartRecording.style.fontSize = 'inherit';
            btnStartRecording.recordRTC.resumeRecording();
            recordingPlayer.parentNode.parentNode.querySelector('h2').innerHTML = '<img src="https://www.webrtc-experiment.com/images/progress.gif">';
            recordingPlayer.play();

            btnPauseRecording.style.fontSize = '15px';
            btnPauseRecording.innerHTML = 'Pause';
            setTimeout(function() {
                btnPauseRecording.disabled = false;
            }, 2000);
        }
    };

    function getRandomString() {
        if (window.crypto && window.crypto.getRandomValues && navigator.userAgent.indexOf('Safari') === -1) {
            var a = window.crypto.getRandomValues(new Uint32Array(3)),
                token = '';
            for (var i = 0, l = a.length; i < l; i++) {
                token += a[i].toString(36);
            }
            return token;
        } else {
            return (Math.random() * new Date().getTime()).toString(36).replace(/\./g, '');
        }
    }

    function getFileName(fileExtension) {
        var d = new Date();
        var year = d.getUTCFullYear();
        var month = d.getUTCMonth();
        var date = d.getUTCDate();
        return 'easyassist-' + year + month + date + '-' + getRandomString() + '.' + fileExtension;
    }

    function getURL(arg) {
        var url = arg;

        if(arg instanceof Blob || arg instanceof File) {
            url = URL.createObjectURL(arg);
        }

        if(arg instanceof RecordRTC || arg.getBlob) {
            url = URL.createObjectURL(arg.getBlob());
        }

        if(arg instanceof MediaStream || arg.getTracks) {
            // url = URL.createObjectURL(arg);
        }

        return url;
    }

    function setVideoURL(arg, forceNonImage) {
        var url = getURL(arg);
        var parentNode = recordingPlayer.parentNode;
        parentNode.removeChild(recordingPlayer);
        parentNode.innerHTML = '';

        var elem = 'video';

        if(type == 'gif' && !forceNonImage) {
            elem = 'img';
        }

        if(type == 'audio') {
            elem = 'audio';
        }

        recordingPlayer = document.createElement(elem);

        if(arg instanceof MediaStream) {
            recordingPlayer.muted = true;
        }

        recordingPlayer.addEventListener('loadedmetadata', function() {
            if(navigator.userAgent.toLowerCase().indexOf('android') == -1) return;

            // android
            setTimeout(function() {
                if(typeof recordingPlayer.play === 'function') {
                    recordingPlayer.play();
                }
            }, 2000);

        }, false);

        recordingPlayer.poster = '';

        if(arg instanceof MediaStream) {
            recordingPlayer.srcObject = arg;
        }
        else {
            recordingPlayer.src = url;
        }

        if(typeof recordingPlayer.play === 'function') {
            recordingPlayer.play();
        }

        /*recordingPlayer.addEventListener('ended', function() {
            if(arg instanceof MediaStream) {
                recordingPlayer.srcObject = arg;
            }
            else {
                recordingPlayer.src = url;
            }
        });*/

        parentNode.appendChild(recordingPlayer);
    }

    function makeXMLHttpRequest(url, data, callback) {

        var request = new XMLHttpRequest();

        request.onreadystatechange = function() {
            if (request.readyState == 4 && request.status == 200) {
                response = JSON.parse(request.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);

                if(response["status"] == 200) {
                    //console.log(response);
                    $("#start_video_record_modal").modal("hide");
                    uploaded_attachement_src = response["file_path"];
                    save_cobrowsing_chat_history("video-feedback", USER_ALIAS, uploaded_attachement_src);
                    callback('upload-ended');
                    return;
                }

                //document.querySelector('.header').parentNode.style = 'text-align: left; color: red; padding: 5px 10px;';
                //document.querySelector('.header').parentNode.innerHTML = request.responseText;
            }
        };

        request.upload.onloadstart = function() {
            callback('Upload started...');
        };

        request.upload.onprogress = function(event) {
            callback('Upload Progress ' + Math.round(event.loaded / event.total * 100) + "%");
        };

        request.upload.onload = function() {
            callback('progress-about-to-end');
        };

        request.upload.onload = function() {
            callback('Getting File URL..');
        };

        request.upload.onerror = function(error) {
            callback('Failed to upload to server');
        };

        request.upload.onabort = function(error) {
            callback('Upload aborted.');
        };

        request.open("POST", url, true);
        request.setRequestHeader('Content-Type', 'application/json');
        request.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        request.send(data);
    }

    function uploadToServer(fileName, recordRTC, callback) {

        var blob = recordRTC instanceof Blob ? recordRTC : recordRTC.getBlob();

        blob = new File([blob], getFileName(fileExtension), {
            type: mimeType
        });

        var reader = new FileReader();
	reader.readAsDataURL(blob);
	reader.onloadend = function() {

        let base64_str = reader.result.split(",")[1];

            json_string = JSON.stringify({
                "filename": fileName,
                "base64_file": base64_str,
                "is_public": true
            });

            encrypted_data = easyassist_custom_encrypt(json_string);

            encrypted_data = {
                "Request": encrypted_data
            };

            var params = JSON.stringify(encrypted_data);

            callback('Uploading recorded-file to server.');

            // var upload_url = 'https://your-domain.com/files-uploader/';
            var upload_url = '/easy-assist/agent/save-document/';

            // var upload_directory = upload_url;
            var upload_directory = 'files/uploads/';

            makeXMLHttpRequest(upload_url, params, function(progress) {
                if (progress !== 'upload-ended') {
                    callback(progress);
                    return;
                }
                callback('ended', upload_directory + fileName);
            });
        }
    }

    /*Save video to server starts*/

    function saveToDiskOrOpenNewTab(recordRTC) {

        if(!recordRTC.getBlob().size) {
            var info = getFailureReport();
            console.log('blob', recordRTC.getBlob());
            console.log('recordrtc instance', recordRTC);
            console.log('report', info);

            if(mediaContainerFormat.value !== 'default') {
                alert('RecordRTC seems failed recording using ' + mediaContainerFormat.value + '. Please choose "default" option from the drop down and record again.');
            }
            else {
                alert('RecordRTC seems failed. Unexpected issue. You can read the email in your console log. \n\nPlease report using disqus chat below.');
            }

            if(mediaContainerFormat.value !== 'vp9' && DetectRTC.browser.name === 'Chrome') {
                alert('Please record using VP9 encoder. (select from the dropdown)');
            }
        }

        var fileName = getFileName(fileExtension);

        if(!recordRTC) return alert('No recording found.');

        uploadToServer(fileName, recordRTC, function(progress, fileURL) {
            if(progress === 'ended') {
                recordRTC.reset();
                uploaded_attachement_src = "None";
                alert("Recorded video uploaded successfully.");
            }
            document.getElementById("video-upload-status").innerHTML = progress;
        });
    }

    /*Save video to server ends*/

}

// initialize_video_recorder();

function save_cobrowsing_chat_history(chat_message, sender, attachment, attachment_file_name=null) {

    var json_request = {
        "session_id": COBROWSE_SESSION_ID,
        "sender": sender,
        "message": chat_message,
        "attachment": attachment
    };

    json_request["attachment_file_name"] = "";
    if(attachment_file_name != null) {
        json_request["attachment_file_name"] = attachment_file_name;
    }
    
    json_string = JSON.stringify(json_request);

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/app/save-client-cobrowsing-chat/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            console.log(response);
        }
    }
    xhttp.send(params);
}


function get_base64_of_selected_document(file) {
    var reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = function() {
        
        let upload_message_element = document.getElementById("upload-attachment-error-message");
        let button_send_to_agent_element = document.getElementById("button-send-attachment-to-agent");

        base64_str = reader.result.split(",")[1];

        json_string = JSON.stringify({
            "filename": file.name,
            "base64_file": base64_str,
            "is_public": true
        });

        encrypted_data = easyassist_custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        upload_message_element.style.color = "orange";
        upload_message_element.innerHTML = "Uploading...";
        uploaded_attachement_src = "None";
        button_send_to_agent_element.style.display = "none";

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/save-document/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if(response["status"]==200){
                    upload_message_element.style.color = "green";
                    upload_message_element.innerHTML = "Document uploading successfully. Click on submit icon below to send it to agent.";
                    uploaded_attachement_src = window.location.protocol + "//" + window.location.hostname + response["file_path"];
                    button_send_to_agent_element.style.display = "block";
                    show_easyassist_toast("Document uploading successfully. Click on submit button to send it to agent.");
                }else{
                    upload_message_element.style.color = "red";
                    upload_message_element.innerHTML = "Unable to upload the document. Please try again.";
                    uploaded_attachement_src = "None";
                    button_send_to_agent_element.style.display = "none";
                    show_easyassist_toast("Unable to upload the document. Please try again.");
                }
            }
        }
        xhttp.send(params);
    };

    reader.onerror = function(error) {
        upload_message_element.style.color = "red";
        upload_message_element.innerHTML = "Unable to load selected document. Please try again.";
        uploaded_attachement_src = "None";
        show_easyassist_toast("Unable to load the selected document. Please try again.");
    };
}

function check_client_selected_document(element) {
    var file = element.files[0];
    get_base64_of_selected_document(file);
}

function load_received_document_list(session_id){

    json_string = JSON.stringify({
        "session_id": session_id
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/get-cobrowsing-chat-history/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if(response.status==200 && response.chat_history.length > 0){
            	let chat_html = '<table class="table"><thead><tr><th>Sender</th><th>File/Message</th><th>DateTime</th></tr></thead><tbody>';
            	let chat_history = response.chat_history;
            	for(var index=0; index<chat_history.length; index++){
            	    let sender = chat_history[index]["sender"];
            	    message = chat_history[index]["message"];
            	    let datetime = chat_history[index]["datetime"];
            	    attachment = chat_history[index]["attachment"];

                    if (attachment!=null){
                        let file_path = window.location.protocol + "//" + window.location.hostname + attachment;
                        let filename_list = attachment.split("/");
                        let filename = filename_list[filename_list.length-1];
                        chat_html += '<tr><td>'+ sender +'</td><td><a href=\''+ file_path +'\' target="_blank">'+ filename +'</a></td><td>'+ datetime +'</td></tr>';
                    } else {
                        chat_html += '<tr><td>'+ sender +'</td><td>'+ message +'</td><td>'+ datetime +'</td></tr>';
                    }
            	}

                chat_html += '</tbody></table>';
                document.getElementById("session-chat-history-container").innerHTML = chat_html;
            }else{
            	document.getElementById("session-chat-history-container").innerHTML = "";
            }
        }
    }
    xhttp.send(params);
}

function upload_selected_document_and_send(attachment_path, attachment_file_name){

    save_cobrowsing_chat_history("attachment", USER_ALIAS, attachment_path, attachment_file_name);

    json_string = JSON.stringify({
        "type": "attachment",
        "file_path": attachment_path,
        "file_name": attachment_file_name,
        "utm_source": utm_source,
        "sender": USER_ALIAS
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");
}

function formatDate(date) {
    var months    = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    minutes = minutes < 10 ? '0'+minutes : minutes;
    var strTime = hours + ':' + minutes + ' ' + ampm;
    return date.getDate() + " " + months[date.getMonth()] + " " + date.getFullYear() + " " + strTime;
}

function scroll_to_bottom_of_chat(){
    setTimeout(function(e){
        var objDiv = document.getElementById("agent-chat-history-container");
        objDiv.scrollTop = objDiv.scrollHeight;
    }, 500);
}

function actions_after_connected_successfully() {

    if(agent_connected_successfully) return;
    agent_connected_successfully = true;

    if(window.IS_AGENT_JOINED_FIRST_TIME == "True") {
        if(window.ENABLE_AGENT_CONNECT_MESSAGE == "True") {
            if(window.AGENT_CONNECT_MESSAGE.includes("agent_name")) {
                window.AGENT_CONNECT_MESSAGE = window.AGENT_CONNECT_MESSAGE.replace("agent_name", window.AGENT_NAME);
            }
            save_chat_message_and_send_to_customer(window.AGENT_CONNECT_MESSAGE, "None", "None");
        }
    }
}

function save_chat_message_and_send_to_agent(element){

    if (uploaded_attachement_src!="None") {
        console.log(uploaded_attachement_src);
        upload_selected_document_and_send();
        uploaded_attachement_src = "None";
        return;
    }

    let chat_message = document.getElementById("client-chat-message-2").value;

    if(chat_message.trim()==""){
        return;
    }

    save_cobrowsing_chat_history(chat_message, USER_ALIAS, "None");

    json_string = JSON.stringify({
        "type": "chat-message",
        "message": chat_message,
        "utm_source": utm_source,
        "sender": USER_ALIAS
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");

    //append_user_chat_message("client", chat_message, null, formatDate(new Date()));

    document.getElementById("client-chat-message-2").value = "";

    show_easyassist_toast("Message sent successfully.");
}

function append_user_chat_message(sender, message, attachment, datetime){

    if (utm_source=="client" && sender.indexOf("expert")!=-1) {return;}

    var bg_color_scheme = "#00488D";
    var text_color_scheme = "#ffffff !important";
    var href_color_scheme = "#ffffff";

    if (sender.startsWith("expert")) {
        bg_color_scheme = "#F9703A";
    }else if(sender.startsWith("client")) {
        bg_color_scheme = "#ffffff";
        text_color_scheme = "#000000";
        href_color_scheme = "#0272BC";
    }

    if (sender.indexOf("client")!=-1) {
        sender = "customer";
    }

    message = easyassist_linkify(message, href_color_scheme);

    var chat_html = "";
    if(attachment!=null){
        var chat_temp_html = '<a href="' + attachment + '" target="_blank"><img src="/static/EasyAssistApp/img/documents2.png" style="height: 100%;width: 40%;border-radius: 1em;object-fit: contain;"></a>';
	chat_html += '<div style="width:98%;display:inline-block;"><div class="easychat-livechat-customer-attachment" style="float:right;">' + chat_temp_html + '<div class="easychat-livechat-message">' + message + '</div><span class="message-time-user" style="color:black;">'+sender+' | '+datetime+'</span></div></div>';
    }else{
        chat_html += '<div class="easychat-user-message-div"><div class="easychat-user-message easychat-user-message-line" style="background-color:'+ bg_color_scheme +';color:'+ text_color_scheme +';"><div class="easychat-show-less-text">'+message+'</div><span class="message-time-user" style="color:'+ text_color_scheme +';">'+sender+' | '+datetime+'</span></div></div>';
    }

    document.getElementById("agent-chat-history-container").innerHTML += chat_html;
    scroll_to_bottom_of_chat();
}

function append_bot_chat_message(sender, message, attachment, datetime){

    if (utm_source=="client" && sender.indexOf("expert")!=-1) {return;}

    var bg_color_scheme = "#00488D";
    var text_color_scheme = "#ffffff !important";
    var href_color_scheme = "#ffffff";

    if (sender.startsWith("expert")) {
        bg_color_scheme = "#F9703A";
    }else if(sender.startsWith("client")) {
        bg_color_scheme = "#ffffff";
        text_color_scheme = "#000000";
        href_color_scheme = "#0272BC";
    }

    if (sender.indexOf("client")!=-1) {
        sender = "customer";
    }

    message = easyassist_linkify(message, href_color_scheme);

    var chat_html = "";
    if(attachment!=null){

        if(attachment.indexOf("https://bi.bajajallianzlife.com")!=-1){
            message = "Benefit illustration";
        }

        var chat_temp_html = '<a href="' + attachment + '" target="_blank"><img src="/static/EasyAssistApp/img/documents2.png" style="height: 100%;width: 40%;border-radius: 1em;object-fit: contain;"></a>';
        chat_html += '<div style="width:98%;display:inline-block;"><div class="easychat-livechat-customer-attachment" style="float:left;">' + chat_temp_html + '<div class="easychat-livechat-message">' + message + '</div><span class="message-time-user" style="color:black;">'+sender+' | '+datetime+'</span></div></div>';
    }else{
 	chat_html += '<div class="easychat-bot-message-div" style="display:inline-block !important;width:100%;"><div class="easychat-bot-message easychat-bot-message-line" style="background-color:'+ bg_color_scheme +'; color: '+ text_color_scheme +'" ><div class="easychat-show-less-text">'+message+'</div><span class="message-time-bot" style="color: '+ text_color_scheme +';">'+sender+' | '+datetime+'</span></div></div>';
    }
    document.getElementById("agent-chat-history-container").innerHTML += chat_html;
    scroll_to_bottom_of_chat();
}

function show_agents_chat_history_for_session(session_id) {

    json_string = JSON.stringify({
        "session_id": session_id
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/get-cobrowsing-chat-history/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            set_session_id_in_livechat();
            if(response.status==200 && response.chat_history.length > 0){
            	chat_history = response.chat_history;
                let allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow;
            	for(var index=0; index<chat_history.length; index++) {
            		sender = chat_history[index]["sender"];
            		message = chat_history[index]["message"];
                    message = show_hyperlink_inside_text(message);
            		datetime = chat_history[index]["datetime"];
            		var time = datetime.split(" ")[3] + " " + datetime.split(" ")[4];
                    attachment = chat_history[index]["attachment"];
                    let sender_name = chat_history[index]["sender_name"];
                    let attachment_file_name = chat_history[index]["attachment_file_name"];
                    let chat_type = "chat_message";    
                    // chat_type = chat_history[index]["chat_type"];
                    if(attachment != null) {
                        if(attachment_file_name == null) {
                            attachment_file_name = "image1.png";
                        }
                    }

                    if (sender.startsWith("client")) {
                        allincall_chat_window.postMessage(JSON.stringify({
                            "message": message,
                            "attachment": attachment,
                            "attachment_file_name": attachment_file_name,
                            "show_client_message": true,
                            "name": window.CLIENT_NAME,
                            "time": time,
                            "chat_type": chat_type,
                            "sender": sender,
                        }), window.location.protocol + "//" + window.location.host);
                    } else if (sender == window.USER_ALIAS) {
                        allincall_chat_window.postMessage(JSON.stringify({
                            "message": message,
                            "attachment": attachment,
                            "attachment_file_name": attachment_file_name,
                            "show_agent_message": true,
                            "time": time,
                            "name": sender_name,
                            "chat_type": chat_type,
                            "sender": sender,
                        }), window.location.protocol + "//" + window.location.host);
                    } else {
                        allincall_chat_window.postMessage(JSON.stringify({
                            "message": message,
                            "attachment": attachment,
                            "attachment_file_name": attachment_file_name,
                            "show_other_agent_message": true,
                            "time": time,
                            "name": sender_name,
                            "chat_type": chat_type,
                            "sender": sender,
                        }), window.location.protocol + "//" + window.location.host);
                    }
            	}
            }
        }
    }
    xhttp.send(params);
}

function show_hyperlink_inside_text(text) {
    var urlRegex =/(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
    return text.replace(urlRegex, function(url) {
        return '<a href="' + url +'" target="_blank">' + url + '</a>';
    });
}

function revoke_edit_form_access(element){

    json_string = JSON.stringify({
        "type": "revoke-control-transfer",
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");
}

function show_save_changes_indicator(){
    document.getElementById("save-changes-action").style.display="block";
    setTimeout(function(e){
        document.getElementById("save-changes-action").style.display="none";
    }, 2000);
}

function create_dynamic_form_from_android_view(fields){

    if(fields.length == 0){
        return;
    }

    var android_html = "";

    for(var field_index=0; field_index < fields.length; field_index++){

        let current_field = fields[field_index];
        let current_field_id = current_field["id"];
        let current_field_text_id = current_field["id_text"];
        let current_field_tag = current_field["tag"];
        let current_field_text = current_field["text"];
        let is_current_field_hidden = current_field["hidden"];

        if(is_current_field_hidden==true){
            continue;
        }

        if (current_field_tag == "TextView") {

            if(current_field["text"]!="" && current_field["text"].length > 1){
                let text_size = current_field["text-size"];
                if (text_size > 55){
                    android_html += '<div style="display:inline-block !important;width:100%; margin-bottom: 0.5em;"><h3 style="color: black;">'+ current_field["text"] +'</h3><hr></div>';
                } else if (text_size > 40){
                    android_html += '<div style="display:inline-block !important;width:100%; margin-bottom: 0.5em;"><h4 style="color: black;">'+ current_field["text"] +'</h4></div>';
                } else {
                    android_html += '<div style="display:inline-block !important;width:100%; margin-bottom: 0.5em;"><h5 style="color: black;">'+ current_field["text"] +'</h5></div>';
                }
            }

        } 
        if (current_field_tag == "RadioGroup") {

            android_html += '<div style="display:inline-block !important;width:100%; margin-bottom: 0.5em;">';

            for(var radio_option_index=0; radio_option_index < current_field["options"].length; radio_option_index++){

                var radio_option_text = current_field["options"][radio_option_index]["text"];
                var radio_option_value = current_field["options"][radio_option_index]["value"];
                var radio_option_name = "RadioGroup"+field_index;
                var radio_option_id = radio_option_name + "-" + current_field["options"][radio_option_index]["id"];

            	android_html += '<div class="form-check">';

                if(radio_option_value){
  		    android_html += '<input class="form-check-input" type="radio" name="'+ radio_option_name +'" id="'+ radio_option_id +'" onchange="send_updated_radiobutton_value(\''+ current_field["options"][radio_option_index]["id"] +'\', this, \''+ current_field_tag +'\')" checked>';
                }else{
                    android_html += '<input class="form-check-input" type="radio" name="'+ radio_option_name +'" id="'+ radio_option_id +'" onchange="send_updated_radiobutton_value(\''+ current_field["options"][radio_option_index]["id"] +'\', this, \''+ current_field_tag +'\')">';
                }

  		android_html += '<label class="form-check-label" for="'+ radio_option_id +'">'+ radio_option_text +'</label></div>';
            }

            android_html += '</div>';

        } else if (current_field_tag == "EditText") {

            let field_id = "InputField-"+current_field_id;
            let field_value = current_field["value"];
            let field_help_text = current_field["hint"];
            android_html += '<div style="display:inline-block !important;width:100%; margin-bottom: 0.5em;"><input type="text" class="form-control" id="'+ field_id +'" onchange="send_updated_edittext_value(\''+ current_field_id +'\', this, \''+ current_field_tag +'\')" value="'+ field_value +'" placeholder="'+ field_help_text +'"></div>';

        } else if (current_field_tag == "Button") {

            android_html += '<button class="btn btn-primary" onclick="send_updated_button_click(this, \''+ current_field_tag +'\')" id="'+ current_field_id +'" style="margin:0.5em;">'+ current_field["text"] +'</button>';

        } else if (current_field_tag == "Spinner") {

            field_value = current_field["value"];
            android_html += '<div style="display:inline-block !important;width:100%; margin-bottom: 0.5em;">\
                <select class="custom-select" id="'+ current_field_id +'" onchange="send_updated_spinner_value(this, \''+ current_field_tag +'\')">';

            for(var select_option_index=0; select_option_index < current_field["options"].length; select_option_index++){
                if(field_value==current_field["options"][select_option_index]){
                    android_html += '<option value=\''+ current_field["options"][select_option_index] +'\' selected>'+ current_field["options"][select_option_index] +'</option>';
                }else{
                    android_html += '<option value=\''+ current_field["options"][select_option_index] +'\'>'+ current_field["options"][select_option_index] +'</option>';
                }
            }

            android_html += '</select></div>';
        } else if (current_field_tag == "CheckBox") {

            field_id = 'Checkbox-'+ current_field_id;
            field_value = current_field["value"];
	    android_html += '<div style="display:inline-block !important;width:100%; margin-bottom: 0.5em;"><div class="form-check">';
            if(field_value){
	        android_html += '<input class="form-check-input" type="checkbox" id="'+ field_id +'" onchange="send_updated_checkbox_value(\''+ current_field_id +'\', this, \''+ current_field_tag +'\')" checked>';
            }else{
                android_html += '<input class="form-check-input" type="checkbox" id="'+ field_id +'" onchange="send_updated_checkbox_value(\''+ current_field_id +'\', this, \''+ current_field_tag +'\')">';
            }
	    android_html += '<label class="form-check-label" for="'+ field_id +'">'+ current_field["text"] +'</label></div></div>';

        } else if (current_field_tag == "NumberPicker") {

            let min_value = current_field["min_value"];
            let max_value = current_field["max_value"];
            field_value = current_field["value"];

            android_html += '<div style="display:inline-block !important; width:100%; margin-bottom: 0.5em;">';
            android_html += '<input type="number" id="'+ current_field_id +'" name="quantity" min="'+ min_value +'" max="'+ max_value +'" onchange="send_updated_edittext_value(\''+ current_field_id +'\', this, \''+ current_field_tag +'\')" value="'+ field_value +'">';
            android_html += '</div>';

        } else if (current_field_tag == "DatePicker") {

            field_value = current_field["value"];
            android_html += '<div style="display:inline-block !important; width:100%; margin-bottom: 0.5em;">';
            android_html += '<input type="date" id="DatePicker-'+ current_field_id +'" onchange="send_updated_edittext_value(\''+ current_field_id +'\', this, \''+ current_field_tag +'\')" value="'+ field_value +'">';
            android_html += '</div>';

        } else if (current_field_tag == "TimePicker") {

            field_value = current_field["value"];
            android_html += '<div style="display:inline-block !important; width:100%; margin-bottom: 0.5em;">';
            android_html += '<input type="time" id="TimePicker-'+ current_field_id +'" onchange="send_updated_edittext_value(\''+ current_field_id +'\', this, \''+ current_field_tag +'\')" value="'+ field_value +'">';
            android_html += '</div>';

        }

    }

    // document.getElementById("dynamic-form-container").innerHTML = android_html;
    android_html += '<div style="height:10em;"></div>';
    document.getElementById("form-container").innerHTML = android_html;
}

function send_updated_edittext_value(edit_text_field_id, element, tag){

    json_string = JSON.stringify({
        "type": "form-response",
        "tag": tag,
        "id": edit_text_field_id,
        "changes": JSON.stringify({
            "value": element.value
        })
    });

    // console.log(json_string);

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");

    show_save_changes_indicator();
}

function send_updated_radiobutton_value(radio_button_field_id, element, tag){

    json_string = JSON.stringify({
        "type": "form-response",
        "tag": tag,
        "id": radio_button_field_id,
        "changes": JSON.stringify({
            "value": element.checked
        })
    });

    // console.log(json_string);

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");

    show_save_changes_indicator();
}

function send_updated_button_click(element, tag){

    json_string = JSON.stringify({
        "type": "form-response",
        "tag": tag,
        "id": element.getAttribute("id")
    });

    // console.log(json_string);

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");

    show_save_changes_indicator();
}

function send_updated_spinner_value(element, tag){

    json_string = JSON.stringify({
        "type": "form-response",
        "tag": tag,
        "id": element.getAttribute("id"),
        "changes": JSON.stringify({
            "value": element.value
        })
    });

    // console.log(json_string);

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");

    show_save_changes_indicator();
}

function send_updated_checkbox_value(checkbox_field_id, element, tag){

    json_string = JSON.stringify({
        "type": "form-response",
        "tag": tag,
        "id": checkbox_field_id,
        "changes": JSON.stringify({
            "value": element.checked
        })
    });

    // console.log(json_string);

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");

    show_save_changes_indicator();
}

function show_androd_iframe_container(){
    //document.getElementById("form-container").style.display="none";
    //document.getElementById("frames-container").style.display="block";
    document.getElementById("revoke-self-edit-access").style.display="none";
}

function show_android_form_container(){
    //document.getElementById("form-container").style.display="block";
    //document.getElementById("frames-container").style.display="none";
    document.getElementById("revoke-self-edit-access").style.display="block";
}


// $("#close_session_message_modal").on("hidden.bs.modal", function() {
//     window.location.reload();
// });


function send_client_geoposition(status, message, lat, lng){

    var map_location = "None";
    if (lat!="None" && lng!="None") {
        map_location = "https://www.google.com/maps/place/"+lat+","+lng
    }

    json_string = JSON.stringify({
        "type": "geolocation",
        "status": status,
        "message": message,
        "lat": lat,
        "lng": lng,
        "map_location": map_location
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");
}

function show_client_geoposition(position) {
    send_client_geoposition(true, "success", position.coords.latitude, position.coords.longitude);
    console.log("Latitude: " + position.coords.latitude + "<br>Longitude: " + position.coords.longitude);
}

function show_error_geoposition(error) {
    switch(error.code) {
        case error.PERMISSION_DENIED:
            send_client_geoposition(false, "User denied the request for Geolocation.", "None", "None");
            break;
        case error.POSITION_UNAVAILABLE:
            send_client_geoposition(false, "Location information is unavailable.", "None", "None");
            break;
        case error.TIMEOUT:
            send_client_geoposition(false, "The request to get user location timed out.", "None", "None");
            break;
        case error.UNKNOWN_ERROR:
            send_client_geoposition(false, "An unknown error occurred.", "None", "None");
            break;
    }
}

function get_client_geolocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(show_client_geoposition, show_error_geoposition);
    } else {
        send_client_geoposition(false, "Geolocation is not supported by this browser.", "None", "None");
    }
}

function get_client_geolication_api() {
    var params = JSON.stringify({});
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "https://ipapi.co/json/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {

            response = JSON.parse(this.responseText);

            var blacklisted_tags = ["asn", "continent_code", "country_area", "country_calling_code", "country_code", "country_code_iso3", "country_population", "country_tld", "currency", "currency_name", "languages", "org", "region_code", "timezone", "utc_offset", "in_eu"];

            for(var index=0; index < blacklisted_tags.length; index++){
                if(response.hasOwnProperty(blacklisted_tags[index])){
                    delete response[blacklisted_tags[index]];
                }
            }

            var map_location = "None";
            if (response["latitude"]!=null && response["latitude"]!=undefined && response["longitude"]!=null && response["longitude"]!=null) {
                map_location = "https://www.google.com/maps/place/"+ response["latitude"]  + "," + response["longitude"];
            }

            response["type"] = "geolocation";
            response["status"] = 200;
            response["message"] = "Geolocation detailed fetched successfully."
            response["map_location"] = map_location;

            json_string = JSON.stringify(response);

            encrypted_data = easyassist_custom_encrypt(json_string);

            encrypted_data = {
                "Request": encrypted_data
            };

            send_message_over_easyassist_socket(encrypted_data, "agent");

        }else{

            json_string = JSON.stringify({
                "type": "geolocation",
                "status": this.status,
                "message": "Unable to fetch customer location details."
            });

            encrypted_data = easyassist_custom_encrypt(json_string);

            encrypted_data = {
                "Request": encrypted_data
            };

            send_message_over_easyassist_socket(encrypted_data, "agent");

        }
    }
    xhttp.send(params);
}


document.onkeypress = function(event){
    if(event.keyCode==13){
        document.getElementById("button-chat-submit").click();
    }
}

function action_on_cobrowsing_another_device(action){
    if(action=="Yes"){

        window.location = window.location.pathname + "?close_session=true&utm="+utm_source;

    }else{

        json_string = JSON.stringify({
            "type": "denied-anonymous-cobrowsing",
        });

        encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        send_message_over_easyassist_socket(encrypted_data, "agent");
    }
}


///////////////////////// Photo KYC Module Starts

var photo_capture_video_element = null;
var photo_capture_video_stream = null;
var photo_capture_canvas_width = null;
var photo_capture_canvas_height = null;
var photo_capture_video_canvas = document.getElementById("photo-capture-canvas");
var photo_capture_video_canvas_ctx = photo_capture_video_canvas.getContext('2d');
var photo_capture_streaming = false;

function proceed_to_photo_capture(){
    $("#capture_photo_activity_modal").modal("show");
    show_start_webcam_button();
}

function show_start_webcam_button(){
    document.getElementById("start-webcam-photo").style.display="inline-block";
    document.getElementById("stop-webcam-photo").style.display="none";
}

function show_stop_webcam_button(){
    document.getElementById("start-webcam-photo").style.display="none";
    document.getElementById("stop-webcam-photo").style.display="inline-block";
}

function startWebcamForPhotoCapture(element){

    photo_capture_video_element = document.querySelector("#photo-capture-video");

    navigator.getUserMedia = ( navigator.getUserMedia ||
                             navigator.webkitGetUserMedia ||
                             navigator.mozGetUserMedia ||
                             navigator.msGetUserMedia);

    if (navigator.getUserMedia) {

          navigator.getUserMedia ({
                 video: true,
                 audio: false
              },
              // successCallback
              function(localMediaStream) {
                  photo_capture_video_element.srcObject = localMediaStream;
                  photo_capture_video_stream = localMediaStream;
                  show_stop_webcam_button();
              },
              // errorCallback
              function(err) {
                 console.log("The following error occured: " + err);
              }
          );


          photo_capture_video_element.addEventListener('canplay', function(ev){

              if (!photo_capture_streaming) {

                  photo_capture_canvas_width = 320;

                  photo_capture_canvas_height = photo_capture_video_element.videoHeight / (photo_capture_video_element.videoWidth/photo_capture_canvas_width);
                  // Firefox currently has a bug where the height can't be read from
                  // the video, so we will make assumptions if this happens.
                  if (isNaN(photo_capture_canvas_height)) {
                      photo_capture_canvas_height = photo_capture_canvas_width / (4/3);
                  }

                  photo_capture_video_element.setAttribute('width', photo_capture_canvas_width);
                  photo_capture_video_element.setAttribute('height', photo_capture_canvas_height);
                  photo_capture_video_canvas.setAttribute('width', photo_capture_canvas_width);
                  photo_capture_video_canvas.setAttribute('height', photo_capture_canvas_height);
                  photo_capture_streaming = true;

              }

          }, false);

    } else {
        console.log("getUserMedia not supported");
    }
}

function stopWebcamForPhotoCapture(){
    if (photo_capture_video_stream != null) {
        photo_capture_video_stream.stop();
        photo_capture_video_stream = null;
        show_start_webcam_button();
    }
}

function takeSnapshotPhotoCapture(){
    if (photo_capture_video_element != null) {
        photo_capture_video_canvas.width = photo_capture_canvas_width;
        photo_capture_video_canvas.height = photo_capture_canvas_height;
        photo_capture_video_canvas_ctx = photo_capture_video_canvas.getContext('2d');
        photo_capture_video_canvas_ctx.drawImage(photo_capture_video_element, 0, 0, photo_capture_video_canvas.width, photo_capture_video_canvas.height);
        photo_capture_video_element.parentElement.parentElement.scrollTop = photo_capture_video_element.parentElement.parentElement.scrollHeight;
        show_easyassist_toast("Screenshot has been captured successfully. Please review captured screenshot and click on submit button below.");
    }
}

function submit_captured_photo(element){

    if (photo_capture_video_element!=null) {

        base64_str = photo_capture_video_canvas.toDataURL().split(",")[1];

        json_string = JSON.stringify({
            "filename": "customer-screenshot.png",
            "base64_file": base64_str,
            "is_public": true
        });

        encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent/save-document/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if(response["status"]==200){
                    uploaded_attachement_src = window.location.protocol + "//" + window.location.hostname + response["file_path"];
                    show_easyassist_toast("Captured screenshot has been saved successfully.");
                    upload_selected_document_and_send();
                }else{
                    show_easyassist_toast("Unable to save captured screenshot. Please try again.");
                }
            }
        }
        xhttp.send(params);
    }
}

$("#capture_photo_activity_modal").on("hidden.bs.modal", function() {
    stopWebcamForPhotoCapture();
});

///////////////////////// Photo KYC Module Ends


///////////////////////// Client Inactivity Detection Starts

var client_inactivity_check_timer = null;

function reset_client_inactivity_check_timer() {
    stop_client_inactivity_check_timer();
    start_client_inactivity_check_timer();
}

function stop_client_inactivity_check_timer() {
    if (client_inactivity_check_timer != null && client_inactivity_check_timer != undefined) {
        clearInterval(client_inactivity_check_timer);
    }
}

function start_client_inactivity_check_timer() {
    client_inactivity_check_timer = setInterval(function(e) {
        auto_close_session = true;
        sync_client_web_screen_agent();
        reset_client_inactivity_check_timer();
    }, 3600000);
}

document.addEventListener("visibilitychange", function() {
    if (document.visibilityState === 'visible') {
        stop_client_inactivity_check_timer();
    } else {
        reset_client_inactivity_check_timer();
    }
});

///////////////////////// Client Inactivity Detection Ends

function sync_edit_access_click_event(x, y) {

    edit_access_token = get_easyassist_cookie("edit-access-token");

    if(edit_access_token != COBROWSE_SESSION_ID){
        return;
    }

    json_string = JSON.stringify({
        "type": "access_click_event",
        "x_coordinate": x,
        "y_coordinate": y
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");

    console.log("sent");
}


$("#android-access-control-dynamic-text-button").click(function () {
    $(this).closest('div').find('#android-access-control-dynamic-text').click();
});

function send_keyboard_event_to_agent(key) {

    if (key == " ") {
        key = "space";
    }

    json_string = JSON.stringify({
        "type": "keyboard_keypress",
        "key": key
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");

}

function send_signal_based_on_type_to_agent(type) {

    // if (utm_source!="client") {return;}

    json_string = JSON.stringify({
        "type": type
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");

}

function send_window_focus_change_packet(packet_type) {

    json_string = JSON.stringify({
        "type": packet_type
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");
}


function getBase64Image(img) {
  var canvas = document.createElement("canvas");
  canvas.width = img.width;
  canvas.height = img.height;
  var ctx = canvas.getContext("2d");
  ctx.drawImage(img, 0, 0);
  var dataURL = canvas.toDataURL("image/png");
  return dataURL;
}

function capture_client_screenshot_confirm() {

    let img_data = document.getElementById("img-frame-cobrowsing").src;

    json_string = JSON.stringify({
        "id": voip_session_id,
        "content": img_data,
        "type_screenshot": "screenshot"
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/app/capture-client-screen/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if(response.status == 200){
                show_easyassist_toast("Client screenshot has been captured successfully.");
            }else{
                show_easyassist_toast("Sorry, we are unable to capture screenshot due to network issue. Please try again later.");
            }
        }
    }

    xhttp.send(params);
}

// nav bar

function on_agent_mouse_over_nav_bar(){
    clear_close_nav_timeout();
}

function on_agent_mouse_out_nav_bar(){
    create_close_nav_timeout();
}

function openNav() {
    try {
        document.getElementById("mySidenav").style.display = "";
        document.getElementById("maximise-button").style.display = "none";
    } catch(err) {}
}

function closeNav() {
    try {
        document.getElementById("mySidenav").style.display = "none";
        document.getElementById("maximise-button").style.display = "";
    } catch(err) {}
}

function create_close_nav_timeout(){
    if(close_nav_timeout == null){
        close_nav_timeout = setTimeout(closeNav, 15*1000);
    }
}

function clear_close_nav_timeout(){
    clearTimeout(close_nav_timeout);
    close_nav_timeout = null;
}

// livechat iframe

function load_allincall_chat_box(focus=false) {
    var allincall_chat_box = document.getElementById("allincall-chat-box");

    if(allincall_chat_box.getAttribute('src') == "") {
        allincall_chat_box.src = "/easy-assist/sales-ai/livechat/?session_id=" + COBROWSE_SESSION_ID;
        allincall_chat_box.onload = function() {
            chat_box_loaded = true;
            show_agents_chat_history_for_session(window.COBROWSE_SESSION_ID);

            if(focus) {
                var allincall_chat_window = allincall_chat_box.contentWindow;
                focus_livechat_input();

                if(window.IS_MOBILE == "False") {
                    allincall_chat_window.postMessage(JSON.stringify({
                        "focus_textbox": "focus-textbox"
                    }), window.location.protocol + "//" + window.location.host);
                }
            }
        }
    }
}

function open_livechat_agent_window() {

    var allincall_chat_box = document.getElementById("allincall-chat-box");
    allincall_chat_box.style.display = "block";
    if(allincall_chat_box.getAttribute('src') == "") {
        load_allincall_chat_box(true);
    } else {
        var allincall_chat_window = allincall_chat_box.contentWindow;
        focus_livechat_input();
        set_session_id_in_livechat();

        if(window.IS_MOBILE == "False") {
            allincall_chat_window.postMessage(JSON.stringify({
                "focus_textbox": "focus-textbox"
            }), window.location.protocol + "//" + window.location.host);
        }
    }
}

function focus_livechat_input() {
    try {
        var inner_doc = document.getElementById("allincall-chat-box").contentWindow.document;
        if(window.IS_MOBILE == "False") {
            $(inner_doc).ready(function() {
              inner_doc.getElementById("user_input").focus();
            });
        }
    } catch(err) {
        console.log("focus_livechat_input: ", err);
    }
}

window.addEventListener('message', function(event) {
    // IMPORTANT: Check the origin of the data!
    if (~event.origin.indexOf(window.location.protocol + "//" + window.location.host)) {

        if (event.data.event_id === "cobrowsing-agent-chat-message") {
            message = event.data.data.message;
            attachment = event.data.data.attachment;
            attachment_file_name = event.data.data.attachment_file_name;
            save_chat_message_and_send_to_customer(message, attachment, attachment_file_name);
            return;
        } else if (event.data.event_id === "livechat-typing") {
            // easyassist_send_livechat_typing_indication()
            return;
        }
        if (event.data == "close-bot") {
            close_chatbot_animation();
        } else {
            // The data hasn't been sent from your site!
            // Be careful! Do not use it.
            return;
        }
    }
});

function close_chatbot_animation() {
    document.getElementById("allincall-chat-box").style.animationName = "bottom-left-right-anime-close";
    document.getElementById("allincall-chat-box").style.display = "none";
    if(window.IS_MOBILE == "True") {
        document.getElementById('sidebar-mobile-modal-btn').style.display = "flex";
    }
}

function save_chat_message_and_send_to_customer(message, attachment, attachment_file_name){

    if (attachment != "None") {
        upload_selected_document_and_send(attachment, attachment_file_name);
        return;
    }

    var agent_chat_message = message;

    if(agent_chat_message.trim()==""){
        return;
    }

    save_cobrowsing_chat_history(agent_chat_message, USER_ALIAS, "None");

    json_string = JSON.stringify({
        "type": "chat-message",
        "message": agent_chat_message,
        "utm_source": utm_source,
        "sender": USER_ALIAS
    });

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, "agent");
}

function set_client_response(message, attachment, attachment_file_name) {
    try {
        if(chat_box_loaded == true) {
            var allincall_chat_box = document.getElementById("allincall-chat-box");
            if (allincall_chat_box.style.display == "none") {
                allincall_chat_box.style.display = "block";
                focus_livechat_input();
            }
            allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow;
            allincall_chat_window.postMessage(JSON.stringify({
                "message": message,
                "attachment": attachment,
                "attachment_file_name": attachment_file_name,
                "show_client_message": true,
                "name": window.CLIENT_NAME,
                "sender": "client",
            }), window.location.protocol + "//" + window.location.host);
        } else {
            open_livechat_agent_window();
        }
    } catch(err) {
        console.log(err);
    }
}

function set_session_id_in_livechat() {
    var allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow;
    allincall_chat_window.postMessage(JSON.stringify({
        "id": "agent_name",
        "name": window.USER_ALIAS,
        "session_id": window.COBROWSE_SESSION_ID
    }), window.location.protocol + "//" + window.location.host);
}

function hide_modals() {
    document.getElementById("allincall-chat-box").style.display = "none";
    var cobrowsing_functionality_buttons = document.getElementsByClassName("cobrowse-functionality-button");
    if(cobrowsing_functionality_buttons.length > 0) {
        for(var index = 0; index < cobrowsing_functionality_buttons.length; index++) {
            cobrowsing_functionality_buttons[index].style.display = "none";
        }
    }
}

function initialize_local_storage_object() {
    try {
        if(window.localStorage.getItem("easyassist_session") == null){
            add_current_session_object();
        } else {
            let local_storage_obj = localStorage.getItem("easyassist_session");
            local_storage_obj = JSON.parse(local_storage_obj);
            if(!local_storage_obj.hasOwnProperty(window.COBROWSE_SESSION_ID)) {
                add_current_session_object();
            }
        }
    } catch(error) {
        console.log("ERROR: initialize_local_storage_object ", error);
    }
}

function add_current_session_object() {
    let local_storage_json_object = {};
    local_storage_json_object[window.COBROWSE_SESSION_ID] = {};
    localStorage.setItem("easyassist_session", JSON.stringify(local_storage_json_object));
}

function get_easyassist_current_session_local_storage_obj() {
    let current_session_obj = null;

    try {
        let easyassist_session_id = window.COBROWSE_SESSION_ID;

        if(localStorage.getItem("easyassist_session") != null) {
            let local_storage_obj = localStorage.getItem("easyassist_session");
            local_storage_obj = JSON.parse(local_storage_obj);
            if(local_storage_obj.hasOwnProperty(easyassist_session_id)) {
                current_session_obj = local_storage_obj[easyassist_session_id];
            }
        }
    } catch(error) {
        console.log("ERROR: get_easyassist_current_session_local_storage_obj ", error);
    }
    
    return current_session_obj;
}

function set_easyassist_current_session_local_storage_obj(key, value) {
    try{
        let local_storage_obj = localStorage.getItem("easyassist_session");
        let easyassist_session_id = window.COBROWSE_SESSION_ID;

        if(local_storage_obj) {
            local_storage_obj = JSON.parse(local_storage_obj);
            local_storage_obj[easyassist_session_id][key] = value;
            localStorage.setItem("easyassist_session", JSON.stringify(local_storage_obj));
        }
    } catch(err) {
        console.log("ERROR: set_easyassist_current_session_local_storage_obj ", err);
    }
}

function easyassist_clear_local_storage() {
    localStorage.removeItem("easyassist_session");
}