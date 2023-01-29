window.onload = function() {
	document.getElementById("cobrowsing_start_btn").addEventListener("click", initialize_cobrowsing_session);
}

function initialize_cobrowsing_session() {

	var website_url = document.getElementById("cobrowsing_url").value;
	if(!check_valid_url(website_url)) {
		show_easyassist_toast("Please enter valid url");
		return;
	}

	json_params = JSON.stringify({
		"website_url": website_url,
	});

    encrypted_data = easyassist_custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

	var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/cognoai-cobrowse/intialize/cobrowse-sesion/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
            	var session_id = response["session_id"];
                var session_url = "/easy-assist/cognoai-cobrowse/session/" + session_id;
            	window.open(session_url, "_self");
            } else {
                show_easyassist_toast("Not able to start cobrowsing. Please try again.");
            }
        }
    }
    xhttp.send(params);
}

function show_easyassist_toast(message){
    var x = document.getElementById("easyassist-snackbar");
    x.innerHTML = message;
    x.className = "show";
    setTimeout(function(){ x.className = x.className.replace("show", ""); }, 5000);
}

function check_valid_url(website_url) {
    try{
        var url_obj = new window.URL(website_url);
        if(url_obj) {
            return true;
        } else {
            return false;
        }
    } catch (error) {
        return false;
    }
}