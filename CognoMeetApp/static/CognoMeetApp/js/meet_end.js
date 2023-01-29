var easyassist_tickmarks_clicked = new Array(11).fill(false);
let agent_rating = 0;
let root = location.protocol + '//' + location.host;


function easyassist_show_emoji_on_rating_change(element, user_rating) {

    rating_spans = element.parentNode.children;
    for (let index = 0; index < rating_spans.length; index++) {
        if (parseInt(rating_spans[index].innerHTML) <= user_rating) {
            if (index <= 11) {
                rating_spans[index].style.background = '#2160FD';
            }
            rating_spans[index].style.border = "none";
            // rating_spans[index].style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
            rating_spans[index].style.color = "#fff";
        } else if (!easyassist_tickmarks_clicked[index]) {
            rating_spans[index].style.background = "unset";
            rating_spans[index].style.border = "1px solid #7B7A7B";

        }
    }
}


function easyassist_rate_agent(element) {
    var rating_bar = easyassist_get_eles_by_class_name("easyassist-tickmarks")[0];
    var rating_spans = rating_bar.querySelectorAll("span");
    var user_rating = parseInt(element.innerHTML);
    agent_rating = user_rating;

    for (let index = 0; index <= user_rating; index++) {
        // var current_rating = parseInt(rating_spans[index].innerHTML);
        if (index <= 11) {
            rating_spans[index].style.background = '#2160FD';
        }
        // rating_spans[index].style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        rating_spans[index].style.color = "#fff";
        easyassist_tickmarks_clicked[index] = true;
        rating_spans[index].style.border = "none";
    }

    for (let index = user_rating + 1; index < rating_spans.length; index++) {
        // var current_rating = parseInt(rating_spans[index].innerHTML);
        easyassist_tickmarks_clicked[index] = false;
    }
}

function easyassist_feedback_icon_color_change(element) {

    let rating_bar = easyassist_get_eles_by_class_name("easyassist-tickmarks")[0];
    let rating_spans = rating_bar.querySelectorAll("span");

    for (let index = 0; index < rating_spans.length; index++) {
        if (!easyassist_tickmarks_clicked[index]) {
            rating_spans[index].style.background = "unset";
            rating_spans[index].style.border = "1px solid #7B7A7B";
        }
    }
}

function easyassist_get_eles_by_class_name(clsName) {
    var retVal = [];
    try {
        retVal = document.getElementsByClassName(clsName);
    } catch (err) {
        retVal = new Array();
        var elements = document.getElementsByTagName("*");
        for (let i = 0; i < elements.length; i++) {
            if (elements[i].className) {
                if (typeof (elements[i].className) != "string") {
                    continue;
                }
                if (elements[i].className.indexOf(clsName) > -1) {
                    retVal.push(elements[i]);
                }
            }
        }
    }

    return retVal;

}

// localstrorage handling

function set_cogno_meet_current_session_local_storage_obj(key, value, is_meeting_storage = true) {
    try {
        let local_storage_name = "cognomeet_meeting_session";

        let local_storage_obj = localStorage.getItem(local_storage_name);
        let easyassist_session_id = session_id;

        if (local_storage_obj) {
            local_storage_obj = JSON.parse(local_storage_obj);
            local_storage_obj[session_id][key] = value;
            localStorage.setItem(local_storage_name, JSON.stringify(local_storage_obj));
        }
    } catch (err) {
        console.log("ERROR: set_easyassist_current_session_local_storage_obj ", err);
    }
}

function cogno_meet_create_local_storage_obj() {
    if (localStorage.getItem("cognomeet_meeting_session") == null) {
        var local_storage_json_object = {};
        local_storage_json_object[session_id] = {};
        localStorage.setItem("cognomeet_meeting_session", JSON.stringify(local_storage_json_object));
    } else {
        var local_storage_obj = localStorage.getItem("cognomeet_meeting_session");
        local_storage_obj = JSON.parse(local_storage_obj);
        if (!local_storage_obj.hasOwnProperty(session_id)) {
            var local_storage_json_object = {};
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
        let easyassist_session_id = session_id;

        if (localStorage.getItem("cognomeet_meeting_session") != null) {
            local_storage_obj = localStorage.getItem("cognomeet_meeting_session");
            local_storage_obj = JSON.parse(local_storage_obj);
            if (local_storage_obj.hasOwnProperty(easyassist_session_id)) {
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

// localstorage end 

function cancel_feedback() {
    // _local_storage = get_cogno_meet_current_session_local_storage_obj();
    // if (_local_storage.filled_feedback_page != null && _local_storage.filled_feedback_page != undefined) {
    //     _local_storage.filled_feedback_page = 'true';
    // }
    // else {
    //     set_cogno_meet_current_session_local_storage_obj('filled_feedback_page', 'true');
    // }

    // window.location.replace(`${root}/cogno-meet/meeting-end?session_id=${session_id}&filled_feedback_page='True'`);
    document.querySelector('.cognomeet-feedback--modal-container').style.display = 'none';
    document.getElementById('feedback-text').style.display = 'flex';

}

function submit_feedback_form() {

    let client_comments = document.getElementById('easyassist-client-feedback');
    if (client_comments) {
        client_comments = client_comments.value;
    }


    var json_string = JSON.stringify({
        "session_id": session_id,
        "agent_rating": `${agent_rating}`,
        "client_comments": client_comments
    });

    var encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/cogno-meet/update-feedback/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                console.log("Feedback details saved successfully ");
                // window.location.replace(`${root}/cogno-meet/meeting-end?session_id=${session_id}&filled_feedback_page='True'`);
                cancel_feedback();
            }
            else {
                console.log("Error while saving feedback detail !!");
            }
        }
    }
    xhttp.send(params);
}

function meeting_left_rejoin_option() {
    let root = location.protocol + '//' + location.host;
    let local_storage_obj = get_cogno_meet_current_session_local_storage_obj();
    if(local_storage_obj && local_storage_obj.hasOwnProperty("is_external_participant")) {
        if(local_storage_obj["is_external_participant"] == "True" || local_storage_obj["is_external_participant"] == "true") {
            window.location.replace(`${root}/cogno-meet/meeting/client/${session_id}?external_user=true`);
            return;
        }
    }
    window.location.replace(`${root}/cogno-meet/meeting/client/${session_id}`);
}

function meeting_left_leave_option() {
    if(is_feedback_enabled == 'True'){
        document.getElementById('meeting-left').style.display = 'none';
        document.getElementById('feedback-page').style.display = 'flex';
    }
    else{
        document.getElementById('meeting-left').style.display = 'none';
        document.getElementById('feedback-page').style.display = 'flex';
        document.querySelector('.cognomeet-feedback--modal-container').style.display = 'none';
        document.getElementById('feedback-text').style.display = 'flex';
    }
    
}

