cognoai_on_load_extension()

const cognoai_show_toast = (message = null, type = null) => {
    const toasts = document.getElementsByClassName("cognoai-extension-sidenav")[0];
    const notif = document.createElement("div");
    notif.classList.add("cognoai-toast");
    notif.innerText = message;
    toasts.appendChild(notif);
    setTimeout(() => notif.remove(), 3000);
};

function cognoai_add_local_storage_value(name, value) {
    window.localStorage.setItem(name, value);
}

function cognoai_get_local_storage_value(name) {
    return window.localStorage.getItem(name);
}

function cognoai_hide_extension_sidenav() {
    document.getElementsByClassName("cognoai-extension-sidenav")[0].style.display = "none";

}


function cognoai_verify_login() {
    var error_message_element = document.getElementById("cognoai-login-error");
    let cognoai_agent_email_id = document.getElementById("cognoai-extension-email-id").value;
    if (cognoai_agent_email_id == null && cognoai_agent_email_id == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Email field can not be empty.";
        return;
    }
    let cognoai_agent_password = document.getElementById("cognoai-extension-password-client").value;
    if (cognoai_agent_password == null || cognoai_agent_password == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Password field can not be empty.";
        return;

    }
    let cognoai_access_token = window.localStorage.getItem('cognoai_access_token');
    let cognoai_allowed_hosts = window.location.hostname;
    let COGNOAI_SERVER_URL = window.localStorage.getItem('cognoai_server_url');

    let json_string = JSON.stringify({
        "cognoai_access_token": cognoai_access_token,
        "cognoai_allowed_hosts": cognoai_allowed_hosts,
        "cognoai_agent_email_id": cognoai_agent_email_id,
        "cognoai_agent_password": cognoai_agent_password
    });
    let encrypted_data = cognoai_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", COGNOAI_SERVER_URL + "/easy-assist/verify-extension-login/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = cognoai_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                cognoai_add_local_storage_value('cognoai_agent_verification_token', response.verification_token);
                window.location.reload()
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Verification failed. Either email or password is incorrect.";
                return;
            }
        }
    }
    xhttp.send(params);
}

function cognoai_add_sidenav_extension() {
    var html =
        '<div class="cognoai-extension-sidenav">\
				<div class="cognoai-extension-header">\
					<center>\
						<img height="40%" width="40%" src="' + COGNOAI_SERVER_URL + '/' + COGNOAI_META_DATA['source_easyassist_cobrowse_logo'] + '">\
					</center>\
				<div id="cognoai-extenstion-minimize-icon">\
					<a onclick="cognoai_hide_extension_sidenav()"><svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="#0085FF">\
	  					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />\
					</svg></a>\
				</div>\
			</div>\
			<div class="cognoai-extension-login">\
				<div id="cognoai-extension-email">\
					<span>Email ID</span>\
					<input type="email" name="" id="cognoai-extension-email-id">\
				</div>\
				<div id="cognoai-extension-password">\
					<span>Password</span>\
					<input type="password" name="" id="cognoai-extension-password-client">\
				</div>\
				<div id="cognoai-login-error">\
				</div>\
				<div id="cognoai-extension-button">\
					<button onclick="cognoai_verify_login()" id="cognoai-extension-button-submit">Verify</button>\
				</div>\
			</div>'
    document.getElementsByTagName("body")[0].innerHTML += html
    document.getElementById("cognoai-extension-icon").style.display = 'block';
}


function cognoiai_on_click_extension_icon() {
    document.getElementById("cognoai-extension-icon").addEventListener("click", function(e) {
        document.getElementsByClassName("cognoai-extension-sidenav")[0].style.display = "block";
    })
}


function cognoai_on_load_extension() {

    cognoai_access_token = window.localStorage.getItem('cognoai_access_token');
    COGNOAI_SERVER_URL = window.localStorage.getItem('cognoai_server_url');

    json_string = JSON.stringify({
        "cognoai_access_token": cognoai_access_token,
    });
    encrypted_data = cognoai_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", COGNOAI_SERVER_URL + "/easy-assist/extension-authentication/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = cognoai_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                COGNOAI_META_DATA = response.COGNOAI_META_DATA;

                var cognoai_extension_icon = document.createElement('img');
                cognoai_extension_icon.src = COGNOAI_SERVER_URL + '/' + COGNOAI_META_DATA["source_easyassist_cobrowse_logo"];
                cognoai_extension_icon.id = "cognoai-extension-icon";
                cognoai_extension_icon.style.zIndex = "2147483647";
                cognoai_extension_icon.style.width = "100px";
                cognoai_extension_icon.style.position = "fixed";
                cognoai_extension_icon.style.right = "20px";
                cognoai_extension_icon.style.bottom = "3em";
                cognoai_extension_icon.style.display = "none";
                document.body.appendChild(cognoai_extension_icon);

                cognoai_add_sidenav_extension()

                cognoiai_on_click_extension_icon()
            } else {
                window.localStorage.removeItem('cognoai_agent_verification_token')
                // window.location.reload();
                return;
            }
        }
    }
    xhttp.send(params);

}