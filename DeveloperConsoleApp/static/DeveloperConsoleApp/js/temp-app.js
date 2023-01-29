var EASYASSIST_SESSION_ID = null;
var check_for_agent_assistance = null;
var is_agent_connected = false;
var agent_requested_for_assistant = false;

var check_cobrowse_session_timer = setInterval(function(e){
    if(get_easyassist_cookie("easyassist_session_id")!=undefined){
        clearTimeout(check_cobrowse_session_timer);
        EASYASSIST_SESSION_ID = get_easyassist_cookie("easyassist_session_id");
        initiate_cobrowsing();
    }
}, 1000);

function mark_client_disconnected(){

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if(easyassist_session_id==null || easyassist_session_id==undefined){return;}

    let json_string = JSON.stringify({
         "id": easyassist_session_id
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/close-session/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer "+easyassist_authtoken());
    xhttp.onreadystatechange = function(){
        if(this.readyState==4 && this.status==200){
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if(response.status==200){
                delete_easyassist_cookie("easyassist_session_id");
                show_floating_sidenav_easyassist_button();
                clearTimeout(check_for_agent_assistance);
                show_easyassist_toast("Cobrowsing session has been closed.");
            }
        }
    }
    xhttp.send(params);
}

function sync_data(){

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if(easyassist_session_id==null || easyassist_session_id==undefined){
        return;
    }

    var screenshot = screenshot_page();

    json_string = JSON.stringify({
         "html": screenshot,
         "id": EASYASSIST_SESSION_ID,
         "active_url": window.location.href
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/sync/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer "+easyassist_authtoken());
    xhttp.onreadystatechange = function(){
        if(this.readyState==4 && this.status==200){
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
        }
    }
    xhttp.send(params);
}

function send_data_to_server(){
    hide_easyassist_ripple_effect();
    setTimeout(function(e){
        sync_data();
    }, 300);
}

function check_for_agent_guide(){

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if(easyassist_session_id==null || easyassist_session_id==undefined){return;}

    json_string = JSON.stringify({
         "id": easyassist_session_id
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/highlight/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer "+easyassist_authtoken());
    xhttp.onreadystatechange = function(){
        if(this.readyState==4 && this.status==200){
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if(response.status!=200){
                console.error(response);
                return;
            }

            if(response.is_lead==true){
                if(response.agent_assistant_request_status==true && agent_requested_for_assistant==false){
                    agent_requested_for_assistant = true;
                    document.getElementById("easyassist-co-browsing-request-assist-modal").style.display="block";
                }else if(response.agent_assistant_request_status==true){
                    agent_requested_for_assistant = false;
                }
            }

            if(response.allow_agent_cobrowse=="true"){
                show_floating_sidenav_menu();
                EASYASSIST_COBROWSE_META.allow_cobrowsing = true;
            }else{
                EASYASSIST_COBROWSE_META.allow_cobrowsing = false;
                return;
            }

            if(response.agent_name==null && EASYASSIST_COBROWSE_META.lead_generation==false){
                show_easyassist_toast("Our customer service agent will join the session soon.");
                return;
            }

            if(response.is_agent_connected==true){

                 if(is_agent_connected==false){
                    show_easyassist_toast(response.agent_name+" has joined the session.");
                    is_agent_connected = true;
                 }

                 if(response.is_updated==true){

                    let clientX = response.position.clientX;
                    let clientY = response.position.clientY;

                    let pageX = response.position.pageX;
                    let pageY = response.position.pageY;

                    let agent_window_x_offset = response.position.agent_window_x_offset;
                    let agent_window_y_offset = response.position.agent_window_y_offset;

                     window.scrollTo(agent_window_x_offset, agent_window_y_offset);

                     let agent_window_width = response.position.agent_window_width;
                     let agent_window_height = response.position.agent_window_height;

                     let screen_width = response.position.screen_width;
                     let screen_height = response.position.screen_height;

                     clientX = (clientX * window.outerWidth)/(agent_window_width);
                     clientY = (clientY * window.outerHeight)/(agent_window_height);

                     pageX = (pageX * window.outerWidth)/(agent_window_width);
                     pageY = (pageY * window.outerHeight)/(agent_window_height);

                     show_easyassist_ripple_effect(clientX, clientY);
                 }
            }else if(response.is_agent_connected==false){
                 if(is_agent_connected==true){
                    show_easyassist_toast(response.agent_name+" has left the session.");
                    is_agent_connected = false;
                 }
            }

            if(response.capture_screenshot==true){
                if(response.capture_screenshot_type=="pageshot"){
                    capture_client_pageshot();
                }else if(response.capture_screenshot_type=="screenshot"){
                    capture_client_screenshot();
                }
            }
        }
    }
    xhttp.send(params);
}

function initiate_cobrowsing(){
    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if(easyassist_session_id!=undefined && EASYASSIST_SESSION_ID!=null){
        hide_floating_sidenav_easyassist_button();
        remove_element_stuck_timer();
        send_data_to_server();
        window.onclick = send_data_to_server;
        window.onkeyup = send_data_to_server;
        window.onkeypress = send_data_to_server;
        window.onkeydown = send_data_to_server;
        window.onscroll = send_data_to_server;
        setInterval(function(e){send_data_to_server();}, 3000);
        check_for_agent_assistance = setInterval(function(e){
            check_for_agent_guide();
        },2000);
    }
}

var global_element_stuck_timer=null;

function start_element_stuck_timer(){
    global_element_stuck_timer = setTimeout(function(){
         if(get_easyassist_cookie("easyassist_session_id")!=undefined){return;}
         if(EASYASSIST_COBROWSE_META.field_recursive_stuck_event_check==false){
             remove_element_stuck_timer();
         }
         show_easyassist_browsing_modal();
    }, EASYASSIST_COBROWSE_META.field_stuck_timer);
}

function reset_element_stuck_timer(){
    if(global_element_stuck_timer!=null){
        clearTimeout(global_element_stuck_timer);
    }
    start_element_stuck_timer();
}

function add_stuck_timer_handler(){

    if(EASYASSIST_COBROWSE_META.field_stuck_event_handler==false){return;}

    if(get_easyassist_cookie("easyassist_session_id")!=undefined){return;}

    let form_input_elements = document.getElementsByTagName("input");
    for(let index=0;index<form_input_elements.length;index++){
        form_input_elements[index].addEventListener("focusin", reset_element_stuck_timer, true);
        form_input_elements[index].addEventListener("keypress", reset_element_stuck_timer, true);
    }

    form_textarea_elements = document.getElementsByTagName("textarea");
    for(let index=0;index<form_textarea_elements.length;index++){
        form_textarea_elements[index].addEventListener("focusin", reset_element_stuck_timer, true);
        form_textarea_elements[index].addEventListener("keypress", reset_element_stuck_timer, true);
    }

    form_select_elements = document.getElementsByTagName("select");
    for(let index=0;index<form_select_elements.length;index++){
        form_select_elements[index].addEventListener("mousedown", reset_element_stuck_timer, true);
        form_select_elements[index].addEventListener("change", reset_element_stuck_timer, true);
    }
}

function remove_element_stuck_timer(){
    form_input_elements = document.getElementsByTagName("input");
    for(let index=0;index<form_input_elements.length;index++){
    form_input_elements[index].removeEventListener("focusin", reset_element_stuck_timer, true);
    form_input_elements[index].removeEventListener("keypress", reset_element_stuck_timer, true);
    }
    let form_textarea_elements = document.getElementsByTagName("textarea");
    for(let index=0;index<form_textarea_elements.length;index++){
    form_textarea_elements[index].removeEventListener("focusin", reset_element_stuck_timer, true);
    form_textarea_elements[index].removeEventListener("keypress", reset_element_stuck_timer, true);
    }
    let form_select_elements = document.getElementsByTagName("select");
    for(let index=0;index<form_select_elements.length;index++){
        form_select_elements[index].removeEventListener("mousedown", reset_element_stuck_timer, true);
    form_select_elements[index].removeEventListener("change", reset_element_stuck_timer, true);
    }
}

setTimeout(function(e){
    add_stuck_timer_handler();
    show_floating_sidenav_easyassist_button();
}, 2000);


function capture_client_pageshot(){

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if(easyassist_session_id==null || easyassist_session_id==undefined){return;}

    var screenshot = screenshot_page();

    json_string = JSON.stringify({
         "id": easyassist_session_id,
         "content": screenshot,
         "type_screenshot": "pageshot"
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/capture-client-screen/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer "+easyassist_authtoken());
    xhttp.onreadystatechange = function(){
        if(this.readyState==4 && this.status==200){
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
        }
    }
    xhttp.send(params);    
}

function capture_client_screenshot(){

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if(easyassist_session_id==null || easyassist_session_id==undefined){return;}

    document.querySelector("#easyassist-ripple_effect").style.border="none";

    html2canvas(document.querySelector("body")).then(function(canvas) {
        // Get base64URL
        let img_data = canvas.toDataURL('image/png');
        var screenshot = screenshot_page();
        json_string = JSON.stringify({
             "id": easyassist_session_id,
             "content": img_data,
             "type_screenshot": "screenshot"
        });

        encrypted_data = easyassist_custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };

        var params = JSON.stringify(encrypted_data);
        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/capture-client-screen/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
        xhttp.setRequestHeader('Authorization', "Bearer "+easyassist_authtoken());
        xhttp.onreadystatechange = function(){
            if(this.readyState==4 && this.status==200){
                response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);
            }
            document.querySelector("#easyassist-ripple_effect").style.border="1px solid red";
        }
        xhttp.send(params);
    });
}

function update_agent_assistant_request(status){

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if(easyassist_session_id==null || easyassist_session_id==undefined){return;}

    document.getElementById("easyassist-request-assist-otp-error").innerHTML = "";

    var client_otp = "None";
    if(status=="true"){
        client_otp = document.getElementById("input-request-assist-otp").value;
        if(client_otp=="" || client_otp==undefined || client_otp==null){
            document.getElementById("easyassist-request-assist-otp-error").innerHTML = "Please enter valid OTP";
            return;
        }
    }

    json_string = JSON.stringify({
         "id": easyassist_session_id,
         "otp": client_otp,
         "status": status
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/update-agent-assistant-request/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer "+easyassist_authtoken());
    xhttp.onreadystatechange = function(){
        if(this.readyState==4 && this.status==200){
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if(response.status==200){
                document.getElementById("easyassist-co-browsing-request-assist-modal").style.display="none";
            }else{
                document.getElementById("easyassist-request-assist-otp-error").innerHTML = "Please enter valid OTP";
            }
        }
    }
    xhttp.send(params);    
}


function submit_client_feedback(){

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if(easyassist_session_id==null || easyassist_session_id==undefined){return;}
    if(window.EASYASSIST_CLIENT_FEEDBACK==null){return;}

    let feedback = document.getElementById("easyassist-client-feedback").value;

    json_string = JSON.stringify({
        "session_id": easyassist_session_id,
        "rating": window.EASYASSIST_CLIENT_FEEDBACK,
        "feedback":feedback
    });

    encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
      "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/submit-client-feedback/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.setRequestHeader('Authorization', "Bearer "+easyassist_authtoken());
    xhttp.onreadystatechange = function(){
        if(this.readyState==4 && this.status==200){
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if(response.status!=200){
               console.error(response);
            }

            EASYASSIST_COBROWSE_META.allow_cobrowsing = false;
            clearTimeout(check_for_agent_assistance);
            delete_easyassist_cookie("easyassist_session_id");
            show_floating_sidenav_easyassist_button();
            hide_floating_sidenav_menu();
            hide_easyassist_feedback_form();
            show_easyassist_toast("Cobrowsing session has been closed.");
        }
    }
    xhttp.send(params);
}