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
	$('select').formSelect();
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

function user_authentication(element){

    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;

    if(username==""){
        show_toast("Username can not be empty.");
        return;
    }

    if(password==""){
        show_toast("Password can not be empty.");
        return;
    }

	let json_string = JSON.stringify({
		"username":username,
		"password":password
	});

	let encrypted_data = easyassist_custom_encrypt(json_string);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);
	element.innerHTML="authenticating...";
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
			}else{
				element.innerHTML="Login";
			}
		}
	}
	xhttp.send(params);
}


function add_new_form(element){
    let form_name = document.getElementById("form-name").value;
    let form_url = document.getElementById("form-url").value;

    if(form_name==""){
        show_toast("form name can not be empty.");
        return;
    }

    if(form_url==""){
        show_toast("form url can not be empty.");
        return;
    }

	json_string = JSON.stringify({
		form_name:form_name,
		form_url:form_url
	});

	let csrf_token = get_csrf_token();
	element.innerHTML="adding...";

	$.ajax({
		url:"/easy-assist/add-form/",
		type:"POST",
		headers:{
			"X-CSRFToken":csrf_token
		},
		data:{
			data:json_string
		},
		success: function(response){
			if(response["status"]==200){
				show_toast("Form added successfully");
				window.location.reload();
			}else{
				M.toast({"html":"Unable to add new form"}, 2000);
			}
			element.innerHTML="Add";
		},
		error: function(xhr, textstatus, errorthrown) {
			console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
			show_toast("There are some network issue. Please check your internet.");
			element.innerHTML="Add";
		}
	});	
}
