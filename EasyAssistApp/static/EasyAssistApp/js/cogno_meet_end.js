var feedback_rating = null;
var feedback_comment = null;
var easyassist_tickmarks_clicked=new Array(11).fill(false);

function set_cookie(cookiename, cookievalue) {
    document.cookie = cookiename + "=" + cookievalue;
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

function show_toast(message) {

    document.getElementById("toast_message").innerHTML = message
    $('.toast').toast('show');
}

function show_emoji_by_user_rating(element, user_rating) {

    let rating_spans = element.parentNode.children;
    for(let index = 0; index < rating_spans.length; index ++) {
        if (parseInt(rating_spans[index].innerHTML) <= user_rating) {
            if(index <= 6){
                rating_spans[index].style.background = 'rgba(255, 70, 70, 1)';
            } else if( index <= 8){
                rating_spans[index].style.background = 'rgba(255, 153, 0, 1)';
            } else {
                rating_spans[index].style.background = 'rgba(5, 178, 54, 1)';
            }
            rating_spans[index].style.border = "none";
            // rating_spans[index].style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
            rating_spans[index].style.color = "#fff";
        } else if(!easyassist_tickmarks_clicked[index]){
            rating_spans[index].style.border = "1px solid #E6E6E6";
            rating_spans[index].style.background = "unset";
            rating_spans[index].style.color = '#2D2D2D';

        }
    }
}

function changeColor(element) {

    var rating_bar = document.getElementsByClassName("easyassist-tickmarks")[0];
    var rating_spans = rating_bar.querySelectorAll("span");

    for(let index = 0; index < rating_spans.length; index ++) {
        if(!easyassist_tickmarks_clicked[index]) {
            rating_spans[index].style.color = '#2D2D2D';
            rating_spans[index].style.background = "unset";
            rating_spans[index].style.border = "1px solid #E6E6E6";
        }
    }
}

function rateAgent(element) {
    var rating_bar = document.getElementsByClassName("easyassist-tickmarks")[0];
    var rating_spans = rating_bar.querySelectorAll("span");
    var user_rating = parseInt(element.innerHTML);

    window.EASYASSIST_CLIENT_FEEDBACK = user_rating;

    for(let index = 0; index <= user_rating; index ++) {
        // var current_rating = parseInt(rating_spans[index].innerHTML);
        if(index <= 6){
            rating_spans[index].style.background = 'rgba(255, 70, 70, 1)';
        } else if( index <= 8){
            rating_spans[index].style.background = 'rgba(255, 153, 0, 1)';
        } else {
            rating_spans[index].style.background = 'rgba(5, 178, 54, 1)';
        }
        // rating_spans[index].style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        rating_spans[index].style.color = "#fff";
        easyassist_tickmarks_clicked[index] = true;
        rating_spans[index].style.border = "none";
    }

    for(let index = user_rating + 1; index < rating_spans.length; index ++) {
        rating_spans[index].style.background = "unset"
        rating_spans[index].style.color = '#2D2D2D';
        easyassist_tickmarks_clicked[index] = false;
        rating_spans[index].style.border = "1px solid #E6E6E6";
    }

    feedback_rating = user_rating;
}

function reset_easyassist_rating_bar() {
    var rating_bar = document.getElementsByClassName("easyassist-tickmarks")[0];
    var rating_spans = rating_bar.querySelectorAll("span");
    for(let index = 0; index < rating_spans.length; index++) {
        rating_spans[index].style.background = "unset";
        rating_spans[index].style.color = '#2D2D2D';
        rating_spans[index].style.border = "1px solid #E6E6E6";
        easyassist_tickmarks_clicked[index] = false;
    }
}

window.onload = function() {
    if(is_feedback == 'False') {
        document.getElementById('meeting-lobby-container').style.display = 'flex';
    } else {
        var is_feedback_done = get_cookie("is_feedback_done");
        if (is_feedback_done == meeting_id) {
            document.getElementById("easyassist-co-browsing-feedback-modal").style.display = 'none';
            document.getElementById('meeting-lobby-container').style.display = 'flex';
        } else {
            document.getElementById('easyassist-co-browsing-feedback-modal').style.display = 'flex';
        }
    }
}

function submit_client_feedback(feedback) {
    if (feedback == 'feedback') {
        var feedback_error_element = document.getElementById("easyassist-feedback-error");
        feedback_error_element.style.display = "none";
        feedback_error_element.innerHTML = "";

        if(feedback_rating == '' || feedback_rating == null || feedback_rating == undefined){
            feedback_error_element.innerHTML = "Please provide a rating and then click on Submit";
            feedback_error_element.style.display = "block";
            return;
        }
        feedback_comment = document.getElementById("easyassist-client-feedback").value;
        if(feedback_comment) {
            feedback_comment = feedback_comment.trim();
        }
        if(feedback_comment.length > 200) {
            feedback_error_element.innerHTML = "Remarks cannot be more than 200 characters";
            feedback_error_element.style.display = "block";
            return;
        }

        var is_feedback_done = get_cookie("is_feedback_done");
        if (is_feedback_done != meeting_id) {
            // no feedback taken
            let request_params = {
                "meeting_id": meeting_id,
                "feedback_rating": String(feedback_rating),
                "feedback_comment": feedback_comment
            };
            let json_params = JSON.stringify(request_params);
            let encrypted_data = easyassist_custom_encrypt(json_params);
            encrypted_data = {
                "Request": encrypted_data
            };
            const params = JSON.stringify(encrypted_data);

            var xhttp = new XMLHttpRequest();
            xhttp.open("POST", "/easy-assist/client-meeting-feedback/", true);
            xhttp.setRequestHeader('Content-Type', 'application/json');
            xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
            xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    let response = JSON.parse(this.responseText);
                    response = easyassist_custom_decrypt(response.Response);
                    response = JSON.parse(response);
                    if (response.status == 200) {
                        set_cookie("is_feedback_done", meeting_id);
                        document.getElementById("easyassist-co-browsing-feedback-modal").style.display = 'none';
                        document.getElementById('meeting-lobby-container').style.display = 'flex';
                        show_toast("Thank you for giving the feedback.")
                    }
                }
            }
            xhttp.send(params);
        }
        else{
            show_toast("You have already submitted the feedback.")
        }
    } else {
        document.getElementById("easyassist-co-browsing-feedback-modal").style.display = 'none';
        document.getElementById('meeting-lobby-container').style.display = 'flex';
    }
}
