var client_websocket_open = false;
var client_websocket = null;

function send_message_over_easyassist_socket(message, sender) {
    if (client_websocket_open && client_websocket != null) {
        client_websocket.send(JSON.stringify({
            "message": {
                "header": {
                    "sender": sender
                },
                "body": message
            }
        }));
    } else {
        create_easyassist_socket(COBROWSING_ID, COBROWSING_CLIENT);
    }
}

function set_easyassist_cookie(cookiename, cookievalue) {

    var domain = window.location.hostname;

    if (window.location.protocol == "https:") {
        document.cookie = cookiename + "=" + cookievalue + ";max-age=86400" + ";path=/;domain=" + domain + ";secure";
    } else {
        document.cookie = cookiename + "=" + cookievalue + ";max-age=86400" + ";path=/;";
    }
}

function handle_received_message(event){

    var data = JSON.parse(event.data);
    let message = data.message;
    let client_packet = message.body.Request;

    if (message.body.is_encrypted == false) {
        client_packet = JSON.parse(client_packet);
    } else {
        client_packet = easyassist_custom_decrypt(client_packet);
        client_packet = JSON.parse(client_packet);
    }

    console.log(client_packet);

    if (message.header.sender=="agent"){
        if(client_packet.type=="response-meeting-joining"){
            set_easyassist_cookie("eac_meeting_allowed", COBROWSING_ID);
            window.location.reload();
        }
    }
}

function handle_error_message(event){
    console.error(event);
}

function send_request_for_meeting_access(){

    document.getElementById("authenticate-details-error").innerHTML = "";

    var name = document.getElementById("display-name").value;

    if (name.toString().trim() == "") {
        document.getElementById("authenticate-details-error").innerHTML = "Please enter valid name";
        return;
    }

    let json_string = JSON.stringify({
        "type":"request-meeting-joining",
        "name": name,
        "id": btoa(COBROWSING_ID + "-" + name)
    })

    console.log(json_string);

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, COBROWSING_CLIENT);

    toggleJoining();
}

function resend_request_for_meeting_access() {

    var name = document.getElementById("display-name").value;

    json_string = JSON.stringify({
        "type":"request-meeting-joining",
        "name": name,
        "id": btoa(COBROWSING_ID + "-" + name)
    })

    console.log(json_string);

    encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    send_message_over_easyassist_socket(encrypted_data, COBROWSING_CLIENT);    
}

function handle_socket_ready(event){
    client_websocket_open = true;
}

function handle_socket_close_event(event){
    console.log("socket has been closed");
}

function create_easyassist_socket(jid, sender) {
    let ws_scheme = window.location.protocol == "http:" ? "ws" : "wss";
    let url = ws_scheme + '://' + window.location.host + '/ws/cobrowse/' + jid + '/' + sender + "/";
    client_websocket = new WebSocket(url);
    client_websocket.onmessage = handle_received_message;
    client_websocket.onerror = handle_error_message;
    client_websocket.onopen = handle_socket_ready;
    client_websocket.onclose = handle_socket_close_event;
}

window.onload = function(event){
    create_easyassist_socket(COBROWSING_ID, COBROWSING_CLIENT);
}
