var room_id = null;
var sender = null;
var client_websocket = null;
var client_websocket_open = false;


// Get CSRF token
function get_csrfmiddlewaretoken() {

    return document.querySelector("input[name=\"csrfmiddlewaretoken\"]").value;
}

// Open websocket
function open_chat_websocket() {

    client_websocket_open = true;
    console.log("Chat WebSocket is opened");
    let json_string = JSON.stringify({
        "type": "html"
    });
    create_chat_socket(json_string, "agent");
}

// Close websocket
function close_chat_websocket() {

    client_websocket_open = false;
    console.log("WebSocket is closed");
    // var description = "agent websocket is closed";
}

// Check websocket status
function check_socket_status(e) {

    console.error("WebSocket error observed:", e);
    // var description = "error occured agent websocket. " + e.data;
}

// Create the socket
function create_chat_socket(room_id, sender) {

    let ws_scheme = window.location.protocol == "http:" ? "ws" : "wss";
    let url = ws_scheme + '://' + window.location.host + '/ws/meet/' + room_id + '/' + sender + "/";
    if (client_websocket == null) {
        client_websocket = new WebSocket(url);
        client_websocket.onmessage = function(e) {
            var data = JSON.parse(e.data);
            // var message = data['message'];
            var type = data["message"]["type"]

            if(type == "9") {
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

function send_cobrowse_form_submit_status_over_socket(cobrowse_form_id) {

    if (client_websocket_open && client_websocket != null) {
        client_websocket.send(JSON.stringify({
            "message": {
                "type": "9",
                "cobrowse_form_id": cobrowse_form_id
            }
        }));
    } else {
        create_chat_socket(room_id, "agent");
    }
}


function show_easyassist_toast(message){
    var x = document.getElementById("easyassist-snackbar");
    x.innerHTML = message;
    x.className = "show";
    setTimeout(function(){ x.className = x.className.replace("show", ""); }, 5000);
}

window.onload = function() {

    $('.cobrowse-form-section:eq(0)').click();

    $('.cobrowse-form-backdrop').on('click', function(e) {
        document.getElementById("sidebarToggleTop").click();
    });

    // enable socket connection
    enable_chat_socket();
}
