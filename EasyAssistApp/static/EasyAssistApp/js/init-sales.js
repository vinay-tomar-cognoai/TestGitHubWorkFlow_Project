/*! init.js v1.0 | (c) AllinCall Research and Solutions */

/*set of global variables*/

var timer_filter_screencast = 10000;

$(window).on('load', function() {
  var pre_loader = $('#global-preloader');
  pre_loader.fadeOut('slow', function() {
     $(this).remove();
  });
});

$(document).ready(function(){
    $('.modal').modal();
});

if(window.location.pathname.indexOf("/easy-assist/dashboard")!=-1){
    $(document).ready( function () {
        $('#easy-assist-client-details-table').DataTable();
    });

	setTimeout(function(){
		render_filter_screencast(document.getElementById("select-filter-screen-cast"));
	}, timer_filter_screencast);
}

function get_csrf_token() {
    var CSRF_TOKEN = $('input[name="csrfmiddlewaretoken"]').val();
    return CSRF_TOKEN;
}

function show_toast(message, timer=2000){
	M.toast({"html": message}, timer);
}

function user_authentication(logout_other){
	element = document.getElementById("login-btn");

	document.getElementById("login-error").innerHTML = "";

    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;

    if(username==""){
    	document.getElementById("login-error").innerHTML="Please enter username";
        return;
    }

    if(password==""){
    	document.getElementById("login-error").innerHTML="Please enter password";
        return;
    }

    var captcha_img = document.getElementById("captcha-img").src.split("/");
    captcha_img = captcha_img[captcha_img.length-1];

    var user_captcha = document.getElementById("user-captcha").value;
    if(user_captcha==undefined || user_captcha==null){user_captcha="None";}

	let json_string = JSON.stringify({
	    "username":username,
	    "password":password,
        "cobrowsemiddlewaretoken":get_cobrowse_middleware_token(),
        "captcha": captcha_img,
		"user_captcha": user_captcha,
		"logout_other": logout_other,
        "is_new":true
	});

	let encrypted_data = easyassist_custom_encrypt(json_string);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);

	if (logout_other == "true") {
		document.getElementById("login-session").innerHTML = "Logging in...";
	} else {
		element.innerHTML="authenticating...";
	}
	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/authentication/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_easyassist_cookie("csrftoken"));
	xhttp.onreadystatechange = function () {
		if (this.readyState == 4 && this.status == 200) {
			let response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
			response = JSON.parse(response);
			if(response["status"]==200){
				window.location = response["redirect"];
				refresh_captcha();
			} else if(response.status == 300) {
				element.innerHTML="Login";
				document.getElementById("easyassist-co-browsing-session-options").style.display = "flex";
			}else{
				element.innerHTML="Login";
				document.getElementById("login-error").innerHTML = response["message"];
				refresh_captcha();
			}
                        
		}
	}
	xhttp.send(params);
}

function refresh_captcha(){
	json_string = JSON.stringify({});
	encrypted_data = easyassist_custom_encrypt(json_string);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);

	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/get-captcha/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_easyassist_cookie("csrftoken"));
	xhttp.onreadystatechange = function () {
		if (this.readyState == 4 && this.status == 200) {
			response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
			response = JSON.parse(response);
			if(response.status=200){
				document.getElementById("captcha-img").src=response["file"];
			}
		}
	}
	xhttp.send(params);	
}


document.onkeyup = function(event){
    if(event.keyCode==13){
		if (document.getElementById("easyassist-co-browsing-session-options").style.display != "flex") {
			user_authentication("false");
		} else {
			user_authentication("true");
		}
    }
}

window.onload = function(event){
	refresh_captcha();	
}

function check_forgot_password(element){

    document.getElementById("login-error").innerHTML = "";
    document.getElementById("success-message").innerHTML = "";

    username = document.getElementById("username").value;

    if(username==""){
    	document.getElementById("login-error").innerHTML="Please enter valid email-id";
        return;
    }

    var captcha_img = document.getElementById("captcha-img").src.split("/");
    captcha_img = captcha_img[captcha_img.length-1];

    var user_captcha = document.getElementById("user-captcha").value;
	if(user_captcha==undefined || user_captcha==null){user_captcha="None";}
	
	var platform_url = window.location.protocol + '//' + window.location.host;

	json_string = JSON.stringify({
	    "username":username,
		"cobrowsemiddlewaretoken":get_cobrowse_middleware_token(),
		"captcha": captcha_img,
		"user_captcha": user_captcha,
		"is_new":true,
		"platform_url": platform_url
	});

	encrypted_data = easyassist_custom_encrypt(json_string);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);

	element.innerHTML="validating...";
	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/verify-forgot-password/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_easyassist_cookie("csrftoken"));
	xhttp.onreadystatechange = function () {
		if (this.readyState == 4 && this.status == 200) {
			response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
			response = JSON.parse(response);

			document.getElementById("login-error").innerHTML = response["message"];

            refresh_captcha();
            element.innerHTML="Submit";
		}
	}
	xhttp.send(params);
}

$(document).on("click", "#login-btn", function() {
	user_authentication("false");
});

$(document).on("click", "#login-session", function() {
	user_authentication("true");
    document.getElementById("username").value = "";
    document.getElementById("password").value = "";
    document.getElementById("user-captcha").value = "";
});

$(document).on("click", "#login-session-close", function() {
	document.getElementById("easyassist-co-browsing-session-options").style.display = "none";
    document.getElementById("username").value = "";
    document.getElementById("password").value = "";
    document.getElementById("user-captcha").value = "";
    refresh_captcha();
});
