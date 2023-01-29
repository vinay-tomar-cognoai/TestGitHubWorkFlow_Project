import axios from "axios";
import { is_url } from "../../agent/chatbox_input";
import { custom_decrypt, get_params, getCsrfToken } from "../../utils";


export function save_configuration() {
    const input = document.getElementById('ms_dynamics_env_url').value.trim();

    if (input == '') {
        $('#failure-toast-message').html('Microsoft Dynamics environment URL cannot be blank')
        $('#failure-toast').css('display','block')
        .fadeIn(400).delay(2000).fadeOut(400);

        $('#sucess-toast').css('display','none')

        return;
    }

    if (!is_url(input)) {
        $('#failure-toast-message').html('Please enter valid URL')
        $('#failure-toast').css('display','block')
        .fadeIn(400).delay(2000).fadeOut(400);

        $('#sucess-toast').css('display','none')

        return;
    }

    save_configuration_to_server(input);
}

function save_configuration_to_server(url) {
    const json_string = JSON.stringify({
        'url': url
    })

    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post('/livechat/integrations/save/', params, config)
        .then (response => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if (response.status == 200) {
                $('#sucess-toast').css('display','block')
                .fadeIn(400).delay(2000).fadeOut(400);

                $('#failure-toast').css('display','none')
            } else {
                $('#failure-toast-message').html(response.message)
                $('#failure-toast').css('display','block')
                .fadeIn(400).delay(2000).fadeOut(400);

                $('#sucess-toast').css('display','none')
            }
        })
}

export function download_ms_integration_doc() {
    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
        url: "/livechat/download-ms-integration-doc/",
        type: "POST",
        headers: {
            "X-CSRFToken": CSRF_TOKEN
        },
        success: function (response) {
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if ((response["status"] = 200)) {
                if (response["export_path"] == null) {
                    alert("Sorry, unable to process your request. Kindly try again later.");
                } else {
                    if (response["export_path_exist"]) {
                        window.open(response["export_path"], "_blank");
                    } else {
                        alert("Requested data doesn't exists. Kindly try again later.");
                    }
                }
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}
