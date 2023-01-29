
function initialize_cobrowsing_session() {

    let website_url = document.getElementById("cobrowsing_url").value;
    let website_base_url = document.getElementById("cobrowsing_base_url").value;
    if (!check_valid_url(website_url)) {
        show_easyassist_toast("Please enter valid url");
        return;
    }

    if (website_base_url != "" && !check_valid_url(website_url)) {

        show_easyassist_toast("Please enter valid base url");
        return;
    }

    let json_params = JSON.stringify({
        "website_url": website_url,
        "website_base_url": website_base_url
    });

    let encrypted_data = easyassist_custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/cognoai-cobrowse/initialize/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                let session_id = response["session_id"];
                header('Content-Type: application/javascript');
                let session_url = "/easy-assist/cognoai-cobrowse/session/" + session_id;
                window.open(session_url, "_self");
            } else {
                show_easyassist_toast("Not able to start cobrowsing. Please try again.");
            }
        }
    }
    xhttp.send(params);
}

function show_easyassist_toast(message) {
    let element = document.getElementById("easyassist-snackbar");
    element.innerHTML = message;
    element.className = "show";
    setTimeout(function () { element.className = element.className.replace("show", ""); }, 5000);
}

function check_valid_url(website_url) {
    try {
        let url_obj = new window.URL(website_url);
        if (url_obj) {
            return true;
        } else {
            return false;
        }
    } catch (error) {
        return false;
    }
}
