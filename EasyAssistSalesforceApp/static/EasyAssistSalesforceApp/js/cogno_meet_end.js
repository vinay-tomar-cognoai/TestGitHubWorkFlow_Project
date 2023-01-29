var feedback_rating = null;
var feedback_comment = null;

function set_cookie(cookiename, cookievalue) {
    document.cookie = cookiename + "=" + cookievalue;
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

function show_toast(message) {

    document.getElementById("toast_message").innerHTML = message
    $('.toast').toast('show');
}


emojiFive = document.querySelector('#emojiFive');
emojiFour = document.querySelector('#emojiFour');
emojiThree = document.querySelector('#emojiThree');
emojiTwo = document.querySelector('#emojiTwo');
emojiOne = document.querySelector('#emojiOne');

function showFive() {

    emojiFive.style.display = "inline-block";
    emojiFour.style.display = "none";
    emojiThree.style.display = "none";
    emojiTwo.style.display = "none";
    emojiOne.style.display = "none";
}

function showFour() {

    emojiFive.style.display = "none";
    emojiFour.style.display = "inline-block";
    emojiThree.style.display = "none";
    emojiTwo.style.display = "none";
    emojiOne.style.display = "none";
}

function showThree() {

    emojiFive.style.display = "none";
    emojiFour.style.display = "none";
    emojiThree.style.display = "inline-block";
    emojiTwo.style.display = "none";
    emojiOne.style.display = "none";
}

function showTwo() {

    emojiFive.style.display = "none";
    emojiFour.style.display = "none";
    emojiThree.style.display = "none";
    emojiTwo.style.display = "inline-block";
    emojiOne.style.display = "none";
}

function showOne() {
    emojiFive.style.display = "none";
    emojiFour.style.display = "none";
    emojiThree.style.display = "none";
    emojiTwo.style.display = "none";
    emojiOne.style.display = "inline-block";
}

function rateAgent(element) {
    var rating_bar = document.getElementsByClassName("easyassist-tickmarks")[0];
    var rating_spans = rating_bar.querySelectorAll("span");
    feedback_rating = parseInt(element.innerHTML);
    for (var index = 0; index < rating_spans.length; index++) {
        if (parseInt(rating_spans[index].innerHTML) <= parseInt(element.innerHTML)) {
            rating_spans[index].style.background = "#204DAF"
            rating_spans[index].style.color = "#fff"
        } else {
            rating_spans[index].style.background = "unset"
            rating_spans[index].style.color = "#204DAF"
        }
    }
}

function reset_easyassist_rating_bar() {
    var rating_bar = document.getElementsByClassName("easyassist-tickmarks")[0];
    var rating_spans = rating_bar.querySelectorAll("span");
    for (var index = 0; index < rating_spans.length; index++) {
        rating_spans[index].style.background = "unset"
        rating_spans[index].style.color = "#204DAF"
    }
}

window.onload = function() {
    if(is_feedback == 'False') {
        document.getElementById('meeting-lobby-container').style.display = 'flex';
    } else {
        var is_feedback_done = get_cookie("is_feedback_done");
        if (is_feedback_done == '1') {
            document.getElementById("easyassist-co-browsing-feedback-modal").style.display = 'none';
            document.getElementById('meeting-lobby-container').style.display = 'flex';
        } else {
            document.getElementById('easyassist-co-browsing-feedback-modal').style.display = 'flex';
        }
    }
}

function submit_client_feedback(feedback) {
    if (feedback == 'feedback') {
        if(feedback_rating == '' || feedback_rating == null || feedback_rating == undefined){
            console.log("empty")
            return;
        }
        feedback_comment = document.getElementById("easyassist-client-feedback").value;
        var is_feedback_done = get_cookie("is_feedback_done");
        if (is_feedback_done != '1') {
            // no feedback taken
            request_params = {
                "meeting_id": meeting_id,
                "feedback_rating": String(feedback_rating),
                "feedback_comment": feedback_comment
            };
            json_params = JSON.stringify(request_params);
            encrypted_data = custom_encrypt(json_params);
            encrypted_data = {
                "Request": encrypted_data
            };
            const params = JSON.stringify(encrypted_data);

            var xhttp = new XMLHttpRequest();
            xhttp.open("POST", "/easy-assist-salesforce/client-meeting-feedback/", true);
            xhttp.setRequestHeader('Content-Type', 'application/json');
            xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
            xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    response = JSON.parse(this.responseText);
                    response = custom_decrypt(response.Response);
                    response = JSON.parse(response);
                    if (response.status == 200) {
                        set_cookie("is_feedback_done", "1")
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
