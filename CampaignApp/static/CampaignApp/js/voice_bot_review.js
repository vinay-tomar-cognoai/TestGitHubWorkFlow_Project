$(document).ready(function() {
    if(window.location.href.includes('voice-bot/review')) {
        update_campaign_progress_bar(CAMPAIGN_CHANNEL);
        update_campaign_sidebar('review');
    }
});

function start_voice_bot_campaign () {
    var request_params = {
        'campaign_id': get_url_multiple_vars()['campaign_id'][0],
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    document.getElementById("send-campaign-button").disabled = true;
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/voice-bot/send/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                var url = window.location.origin + '/campaign/dashboard/?bot_pk=' + BOT_ID;
                window.location.href = url;

            } else {
                show_campaign_toast(response.message);
                console.log(response);
                document.getElementById("send-campaign-button").disabled = false;
            }
        }
    }
    xhttp.send(params);

}
