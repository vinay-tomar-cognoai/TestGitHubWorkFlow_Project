/*! easy-assist.js v1.0 | (c) AllinCall Research and Solutions */

/*set of global variables*/
var md5_string;
var server_domain = "https://easyassist.allincall.in";
var global_element_stuck_timer = null;
var element_stuck_timeout = 5000; // seconds
var agent_sync_timer = 5000; // agent sync timer;
var client_name = null; // Client basic details
var client_mobile_number = null; // Client Mobile Number
var session_id = null; // session id
var html_elements_value_dict = {}; // md5 => value mapping
var start_date = new Date(); // initialize with current time
var last_client_x = null;
var last_client_y = null;
var is_floating_pointer_active = false;
var last_highlighted_element = null;
var check_highlighted_element_timer = 2000;
var is_agent = false;
var agent_code = null;
var agent_username = null;
var agent_assistance_check_timer = null;
var agent_assistance_timer = 5000;
var agent_request_assistance = false;
var confirm_message = "We would like to assist you in filling your form. By clicking OK, our customer service agent will be able to see your form and assist you. Please don't worry, your personal data will not be shown to our agent.";

var agent_code_dict = { "agent1": "agent1", "agent2": "agent2", "agent3":"agent3"};
var auto_session_init_list = ["41c3ba9e3135028c56b091e018394967"];


/*Load easy-assist.css and other dependency file*/

session_id = get_cookie("easy-assist-session-id");
if(session_id==""){
	session_id = null;
}
console.log(session_id);

function add_javascript(filename){
    var head = document.getElementsByTagName('head')[0];
    var script = document.createElement('script');
    script.src = filename;
    script.type = 'text/javascript';
    head.append(script);
    return script;
}

function add_css_file(filename){
     var head = document.getElementsByTagName('head')[0];
     var style = document.createElement('link');
     style.href = filename;
     style.type = 'text/css';
     style.rel = 'stylesheet';
     head.append(style);
}

add_css_file(server_domain+"/static/EasyAssistApp/css/easy-assist.css");
add_javascript(server_domain+"/static/EasyAssistApp/js/crypto-js.min.js");
add_javascript(server_domain+"/static/EasyAssistApp/js/json2.js");
/* utilitizes */

function console_log_md5(){
	console.log(this.tagName, this.id, get_md5_string(this));
}

function remove_expose_md5_hashed_element(){
        let form_input_elements = document.getElementsByTagName("input");
        for(let index=0;index<form_input_elements.length;index++){
                form_input_elements[index].removeEventListener("focusin", console_log_md5, true);
        }
        let form_textarea_elements = document.getElementsByTagName("textarea");
        for(let index=0;index<form_textarea_elements.length;index++){
                form_textarea_elements[index].removeEventListener("spellcheck", "false");
                form_textarea_elements[index].removeEventListener("focusin", console_log_md5, true);
        }
        let form_select_elements = document.getElementsByTagName("select");
        for(let index=0;index<form_select_elements.length;index++){
                form_select_elements[index].removeEventListener("mousedown", console_log_md5, true);
                form_select_elements[index].removeEventListener("change", console_log_md5, true);
        }
        let form_button_elements = document.getElementsByTagName("button");
        for(let index=0;index<form_button_elements.length;index++){
                form_button_elements[index].removeEventListener("click", console_log_md5, true);
        }
        // console.log("removed expose_md5_hashed_element");
}


function expose_md5_hashed_element(){
        //remove_expose_md5_hashed_element();
	form_input_elements = document.getElementsByTagName("input");
	for(let index=0;index<form_input_elements.length;index++){
		form_input_elements[index].addEventListener("focusin", console_log_md5, true);
	}
	form_textarea_elements = document.getElementsByTagName("textarea");
	for(let index=0;index<form_textarea_elements.length;index++){
		form_textarea_elements[index].setAttribute("spellcheck", "false");
		form_textarea_elements[index].addEventListener("focusin", console_log_md5, true);
	}
	form_select_elements = document.getElementsByTagName("select");
	for(let index=0;index<form_select_elements.length;index++){
		form_select_elements[index].addEventListener("mousedown", console_log_md5, true);
                form_select_elements[index].addEventListener("change", console_log_md5, true);
	}
	form_button_elements = document.getElementsByTagName("button");
	for(let index=0;index<form_button_elements.length;index++){
		form_button_elements[index].addEventListener("click", console_log_md5, true);
	}
        //console.log("reset_expose_md5_hashed_element");
}

// Default Load Screen as soon as page is loaded

// window.onclick = function(e){
//    expose_md5_hashed_element();
// }

function get_url_vars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m, key, value){
        vars[key] = value;
    });
    return vars;
}

function get_website_url(){
	    let new_href = window.location.href;
        new_href = new_href.split(";")[0];
        new_href = new_href.replace("#!","");
        new_href = new_href.split("?")[0];
	return new_href;
}

function get_focused_element(){
	return document.activeElement;
}



function initialize_onbeforeunload(){
    //window.addEventListener("beforeunload", function (e) {
    //    client_disconnected();
    //});
    window.onbeforeunload = function(e){
        client_disconnected();
    }
}

function client_disconnected(){
    var xhttp = new XMLHttpRequest();

    if(session_id==null || session_id==undefined){
        return;
    }

    let json_string = JSON.stringify({
        session_id:session_id
    });

    var params = "data="+json_string;
    xhttp.open("POST", server_domain+"/easy-assist/client-disconnected/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function(){
	 if(this.readyState==4 && this.status==200){
		console.log(json_string);
	 }
    }
    xhttp.send(params);
    delete_cookie("easy-assist-session-id");
    remove_floating_disconnect_button();
}

function delete_cookie(cookiename){
	document.cookie = cookiename+"=;expires=Thu, 01 Jan 1970 00:00:01 GMT;";
}

function set_cookie(cookiename, cookievalue) {
  document.cookie = cookiename + "="+cookievalue;
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

window.onload = function(){
    delete_cookie("easy-assist-session-id");
    initialize_easyassist();
    // expose_md5_hashed_element();
    auto_session_init_value();
    get_form_information();
}

function start_agent_assistance_request_check(){
    //console.log("agent assistance request check started");
    agent_assistance_check_timer = setInterval(function(){
        check_for_agent_assistance_request();
    }, agent_assistance_timer);
}

function stop_agent_assistance_request_check(){
    //console.log("agent assistance request check stopped");
    clearTimeout(agent_assistance_check_timer);
}

function initialize_easyassist(){
        agent_code = null;
	    url_params = get_url_vars();
        start_agent_assistance_request_check();
        //expose_md5_hashed_element();
        //add_stuck_timer_handler();
        window.onclick = function(e){
            expose_md5_hashed_element();
            add_stuck_timer_handler();
        }
        initialize_onbeforeunload();
        /*
	// Initialize Agent side functionalities
        if("client_id" in url_params)
        {
                start_agent_assistance_request_check();
        }
        else if("session_id" in url_params)
        {
		sync_screen_to_agent();
		setInterval(function(){
			sync_screen_to_agent();
		}, agent_sync_timer);
		document.addEventListener("click", save_mouse_position);
		add_floating_button();
		is_agent = true;
	// Initialize client side functionalities
	}else{
                agent_code = null;
		add_stuck_timer_handler();
		initialize_onbeforeunload();

                if(get_url_vars()["agent_id"]!=null || get_url_vars()["agent_id"]!=undefined){
                    var ask = true;
                    while(ask){
                        agent_code = prompt('Please enter your agent code: ');
                        if (agent_code === null) {//user cancelled
                            ask = false;
                            break;
                        }
                        else if (agent_code!=='' && agent_code in agent_code_dict){
                            break;
                        }
                    }

                    if(ask==true){
                        stop_element_stuck_timer();
                        remove_element_stuck_timer();
                        connect_with_agent("Aman Gupta", "8141724612", agent_code);
                    }
                }
	}
        */
}

function get_md5_string(element){
        var string = "";
        if(element.getAttribute("id")!=null){
            string = element.getAttribute("id");
        }else if(element.getAttribute("data-id")!=null){
            string = element.getAttribute("data-id");
        }else{
            string = element.outerHTML;
            string = string.replace(/style="[^"]*"/, ""); // remove style tag from html string
            string = string.replace(/ /g, ""); // remove whitespace from html string
            // console.log(string);
        }
	return CryptoJS.MD5(string).toString();
}

/*
Client-side
*/

function start_element_stuck_timer(){
	// console.log("time has been started");
	global_element_stuck_timer = setTimeout(function(){
		take_confirmation_to_connect_with_agent();
	}, element_stuck_timeout);
}

function stop_element_stuck_timer(){
	// console.log("timer has been stopped");
	if(global_element_stuck_timer!=null){
	     clearTimeout(global_element_stuck_timer);
	}
}

function reset_element_stuck_timer(){
	if(global_element_stuck_timer!=null){
		clearTimeout(global_element_stuck_timer);
	}
	start_element_stuck_timer();
}

function take_confirmation_to_connect_with_agent(){

        console.log(agent_code, session_id);

        if(agent_code!=null){
            return;
        }

        if(session_id!=null){
            return;
        }

	// stop_element_stuck_timer();
	// remove_element_stuck_timer();

	if (confirm(confirm_message)){
		var ask = true;
		while(ask){
			client_name = prompt('Please enter your full name: ');
			if (client_name === null) {//user cancelled
				ask = false;
				break;
			}
			else if (client_name !== '' && isNaN(Number(client_name))){
				break;
			}
		}

		while(ask){
			client_mobile_number = prompt ("Please enter your 10 digits mobile number: " , "");
			if (client_mobile_number === null) {//user cancelled
				ask = false;
				break;
			}
			else if (client_mobile_number.length == 10 && !isNaN(parseInt(client_mobile_number))){
				break;
			}
		}

                while(ask){
                        agent_username = prompt ("Please enter your agent code: " , "");
                        if (agent_username === null) {//user cancelled
                                ask = false;
                                break;
                        }
                        else if (agent_username !== '' && agent_username in agent_code_dict){
                                break;
                        }
                }

                if(ask==true){
		    connect_with_agent(client_name, client_mobile_number, agent_username);
                    stop_element_stuck_timer();
                    remove_element_stuck_timer();
                }else{
                    session_id = null;
                }
	}
}

function check_form_submit(){
	md5_string = get_md5_string(this);
	if(session_id==null){
		return;
	}
	var json_string = JSON.stringify({
		"session_id": session_id,
		"button_md5": md5_string
	});
	var xhttp = new XMLHttpRequest();
	var params = "data="+json_string;
	xhttp.open("POST", server_domain+"/easy-assist/check-form-submit/", true);
	xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
	xhttp.onreadystatechange = function(){
		if(this.readyState==4 && this.status==200){
			let response = JSON.parse(this.responseText);
		}
	}
	xhttp.send(params);
}

function cancel_agent_assistance_request(){
        url_params = get_url_vars();
        let client_id = url_params["client_id"];

        if(session_id==null || session_id==undefined){
            if(client_id!=null && client_id!=undefined){
                session_id = client_id;
            }else{
                console.log("session_id doesn't exist");
                return;
            }
        }
        var json_string = JSON.stringify({
                "session_id": session_id
        });
        var xhttp = new XMLHttpRequest();
        var params = "data="+json_string;
        xhttp.open("POST", server_domain+"/easy-assist/cancel-agent-assistance-request/", true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.onreadystatechange = function(){
                if(this.readyState==4 && this.status==200){
                     response = JSON.parse(this.responseText);
                     if(response.status==200){
                         start_agent_assistance_request_check();
                     }
                }
        }
        xhttp.send(params);
}


function check_for_agent_assistance_request(){
        url_params = get_url_vars();
        let client_id = url_params["client_id"];

        if(session_id==null || session_id==undefined){
            if(client_id!=null && client_id!=undefined){
                session_id = client_id;
            }else{
                console.log("session_id doesn't exist");
                return;
            }
        }

        var json_string = JSON.stringify({
                "session_id": session_id
        });
        stop_agent_assistance_request_check();
        var xhttp = new XMLHttpRequest();
        var params = "data="+json_string;
        xhttp.open("POST", server_domain+"/easy-assist/check-agent-assistance-request/", true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.onreadystatechange = function(){
                if(this.readyState==4 && this.status==200){
                        response = JSON.parse(this.responseText);
                        if(response.status==200 && response.agent_requested){
                            if(confirm(confirm_message)){
                                client_name = response.client_name;
                                client_mobile_number = response.client_mobile_number;
                                agent_request_assistance = true;

                                var ask = true;
                                /*while(ask){
                                    agent_code = prompt('Please enter your agent code: ');
                                    if (agent_code === null) {//user cancelled
                                        ask = false;
                                        break;
                                    }
                                    else if (agent_code!=='' && agent_code in agent_code_dict){
                                        break;
                                    }
                                }*/

                                agent_code = response.agent;
                                console.log(agent_code);

                                if(ask){
                                    connect_with_agent(client_name, client_mobile_number, agent_code);
                                    stop_element_stuck_timer();
                                    remove_element_stuck_timer();
                                    console.log("connected with agent successfully.")
                                }else{
                                    cancel_agent_assistance_request();
                                }
                            }else{
                                cancel_agent_assistance_request();
                            }
                       }else{
                            start_agent_assistance_request_check();
                       }
                }
        }
        xhttp.send(params);
}


function add_stuck_timer_handler(){
	form_input_elements = document.getElementsByTagName("input");
	for(let index=0;index<form_input_elements.length;index++){
		form_input_elements[index].addEventListener("focusin", reset_element_stuck_timer, true);
		form_input_elements[index].addEventListener("keypress", reset_element_stuck_timer, true);
	}
	form_textarea_elements = document.getElementsByTagName("textarea");
	for(let index=0;index<form_textarea_elements.length;index++){
		form_textarea_elements[index].addEventListener("focusin", reset_element_stuck_timer, true);
		form_textarea_elements[index].addEventListener("keypress", reset_element_stuck_timer, true);
	}
	form_select_elements = document.getElementsByTagName("select");
	for(let index=0;index<form_select_elements.length;index++){
		form_select_elements[index].addEventListener("mousedown", reset_element_stuck_timer, true);
		form_select_elements[index].addEventListener("change", reset_element_stuck_timer, true);
	}
	form_button_elements = document.getElementsByTagName("button");
	for(let index=0;index<form_button_elements.length;index++){
		form_button_elements[index].addEventListener("click", check_form_submit, true);
	}
}

function remove_element_stuck_timer(){
	form_input_elements = document.getElementsByTagName("input");
	for(let index=0;index<form_input_elements.length;index++){
		form_input_elements[index].removeEventListener("focusin", reset_element_stuck_timer, true);
		form_input_elements[index].removeEventListener("keypress", reset_element_stuck_timer, true);
	}
	form_textarea_elements = document.getElementsByTagName("textarea");
	for(let index=0;index<form_textarea_elements.length;index++){
		form_textarea_elements[index].removeEventListener("focusin", reset_element_stuck_timer, true);
		form_textarea_elements[index].removeEventListener("keypress", reset_element_stuck_timer, true);
	}
	form_select_elements = document.getElementsByTagName("select");
	for(let index=0;index<form_select_elements.length;index++){
		form_select_elements[index].removeEventListener("mousedown", reset_element_stuck_timer, true);
		form_select_elements[index].removeEventListener("change", reset_element_stuck_timer, true);
	}
}

function save_html_element_value_on_focusin_event(){
	md5_string = get_md5_string(this);
	if(this.type=="text" || this.type=="textarea"){
		html_elements_value_dict[md5_string] = this.value;
	}else if(this.type=="checkbox"){
		html_elements_value_dict[md5_string] = this.checked;
	}else if(this.type=="radio"){
		let radio_elements = document.getElementsByName(this.name);
		for(let index=0;index<radio_elements.length;index++){
			md5_string = get_md5_string(radio_elements[index]);
			html_elements_value_dict[md5_string] = radio_elements[index].checked;
		}
	}else if(this.tagName=="SELECT"){
		html_elements_value_dict[md5_string] = this.value;
	}
}

function compare_html_element_value_on_focusout_event(){
	var is_value_changed = false;
	var previous_value;
	var current_value;
	md5_string = get_md5_string(this);
	if(this.type=="text" || this.type=="textarea"){
		previous_value = html_elements_value_dict[md5_string];
		current_value = this.value;
		if(previous_value!=current_value){
			is_value_changed = true;
		}
	}else if(this.type=="checkbox"){
		previous_value = html_elements_value_dict[md5_string];
		current_value = this.checked;
		if(previous_value!=current_value){
			is_value_changed = true;
		}
	}else if(this.type=="radio"){
		let radio_elements = document.getElementsByName(this.name);
		for(let index=0;index<radio_elements.length;index++){
			md5_string = get_md5_string(radio_elements[index]);
			previous_value = html_elements_value_dict[md5_string];
			current_value = radio_elements[index].checked;
			if(previous_value!=current_value){
				is_value_changed = true;
				break;
			}
		}
	}else if(this.tagName=="SELECT"){
		previous_value = html_elements_value_dict[md5_string];
		current_value = this.value;
		if(previous_value!=current_value){
			is_value_changed = true;
		}
	}

	if(is_value_changed){
		connect_with_agent(client_name, client_mobile_number, agent_username);
	}
}

function detect_value_change_event(){
	form_input_elements = document.getElementsByTagName("input");
	for(let index=0;index<form_input_elements.length;index++){
		form_input_elements[index].addEventListener("focusin", save_html_element_value_on_focusin_event, true);
		form_input_elements[index].addEventListener("focusout", compare_html_element_value_on_focusout_event, true);
	}
	form_textarea_elements = document.getElementsByTagName("textarea");
	for(let index=0;index<form_textarea_elements.length;index++){
		form_textarea_elements[index].addEventListener("focusin", save_html_element_value_on_focusin_event, true);
		form_textarea_elements[index].addEventListener("focusout", compare_html_element_value_on_focusout_event, true);
	}
	form_select_elements = document.getElementsByTagName("select");
	for(let index=0;index<form_select_elements.length;index++){
		form_select_elements[index].addEventListener("mousedown", save_html_element_value_on_focusin_event, true);
		form_select_elements[index].addEventListener("change", compare_html_element_value_on_focusout_event, true);
	}
}

function check_highlighted_element_guide(){

	if(session_id==null){
		return;
	}

	var json_string = JSON.stringify({
		"session_id": session_id
	});
	var xhttp = new XMLHttpRequest();
	var params = "data="+json_string;
	xhttp.open("POST", server_domain+"/easy-assist/check-highlighted-element/", true);
	xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
	xhttp.onreadystatechange = function(){
		if(this.readyState==4 && this.status==200){
			response = JSON.parse(this.responseText);

			if(last_highlighted_element!=null){
				last_highlighted_element.style.outline = "";
			}

			if(response.status==200 && response.highlight_text!=null && response.highlight_text!=undefined){

				let html_element_tag = response.highlight_text.html_element_tag;
				let md5hash_str = response.highlight_text.md5hash_str;

				if(html_element_tag=="input"){
					form_input_elements = document.getElementsByTagName("input");
					for(let index=0;index<form_input_elements.length;index++){
						md5_string = get_md5_string(form_input_elements[index]);
						if(md5_string==md5hash_str){
							last_highlighted_element = form_input_elements[index];
                                                        if(form_input_elements[index].type=="radio" || form_input_elements[index].type=="checkbox"){
                                                            form_input_elements[index].parentElement.style.outline="solid red 2px";
                                                        }else{
							    form_input_elements[index].style.outline="solid red 2px";
                                                        }
							form_input_elements[index].scrollIntoView();
							return;
						}
					}
				}else if(html_element_tag=="select"){
					form_select_elements = document.getElementsByTagName("select");
					for(let index=0;index<form_select_elements.length;index++){
						md5_string = get_md5_string(form_select_elements[index]);
						if(md5_string==md5hash_str){
							last_highlighted_element = form_select_elements[index];
							form_select_elements[index].parentElement.style.outline="solid red 2px";
							form_select_elements[index].scrollIntoView();
							return;
						}
					}
				}else if(html_element_tag=="textarea"){
					form_textarea_elements = document.getElementsByTagName("textarea");
					for(let index=0;index<form_textarea_elements.length;index++){
						md5_string = get_md5_string(form_textarea_elements[index]);
						if(md5_string==md5hash_str){
							last_highlighted_element = form_textarea_elements[index];
							form_textarea_elements[index].style.outline="solid red 2px";
							form_textarea_elements[index].scrollIntoView();
							return;
						}
					}
				}
			}
		}
	}
	xhttp.send(params);
}

function get_input_html_elements(){
	let input_elements = {};
	form_input_elements = document.getElementsByTagName("input");
	for(let index=0;index<form_input_elements.length;index++){

		let is_checked = null;
		if(form_input_elements[index].type=="checkbox" || form_input_elements[index].type=="radio"){
			if(form_input_elements[index].checked){
				is_checked = true;
			}else{
				is_checked = false;
			}
		}

		md5_string = get_md5_string(form_input_elements[index]);
                let focused_element = get_focused_element();
                let md5_string_focused_element = get_md5_string(focused_element);

                var is_focused = false;
                if(md5_string==md5_string_focused_element){
                    is_focused = true;
                }

                if(form_input_elements[index].type=="hidden"){
                    continue;
                }

		input_elements[md5_string] = {};
		input_elements[md5_string]["type"] = form_input_elements[index].type;
		input_elements[md5_string]["id"] = form_input_elements[index].id;
		input_elements[md5_string]["name"] = form_input_elements[index].name;
		input_elements[md5_string]["value"] = form_input_elements[index].value;
		input_elements[md5_string]["checked"] = is_checked;
                input_elements[md5_string]["index"] = index;
                input_elements[md5_string]["is_focused"] = is_focused;
	}
	return input_elements;
}

function get_all_select_options(element){
    var options = []
    for(let i = 0; i < element.length; i++){
    	options.push(element.options[i].innerHTML);
    }
    return options;
}

function get_select_html_elements(){
	let select_elements = {};
	form_select_elements = document.getElementsByTagName("select");
	for(let index=0;index<form_select_elements.length;index++){

		md5_string = get_md5_string(form_select_elements[index]);
                let focused_element = get_focused_element();
                let md5_string_focused_element = get_md5_string(focused_element);

                var is_focused = false;
                if(md5_string==md5_string_focused_element){
                    is_focused = true;
                }

                if(form_select_elements[index].type=="hidden"){
                    continue;
                }

		select_elements[md5_string] = {};
		select_elements[md5_string]["id"] = form_select_elements[index].id;
		select_elements[md5_string]["value"] = form_select_elements[index].value;
		select_elements[md5_string]["text"] = form_select_elements[index].options[form_select_elements[index].selectedIndex].text;
		select_elements[md5_string]["options"] = get_all_select_options(form_select_elements[index]);
                select_elements[md5_string]["index"] = index;
                select_elements[md5_string]["is_focused"] = is_focused;
	}
	return select_elements;
}

function get_textarea_elements(){
	let textarea_elements = {};
	form_textarea_elements = document.getElementsByTagName("textarea");
	for(let index=0;index<form_textarea_elements.length;index++){
		form_textarea_elements[index].setAttribute("spellcheck", "false");
		md5_string = get_md5_string(form_textarea_elements[index]);
                let focused_element = get_focused_element();
                let md5_string_focused_element = get_md5_string(focused_element);

                var is_focused = false;
                if(md5_string==md5_string_focused_element){
                    is_focused = true;
                }

                if(form_textarea_elements[index].type=="hidden"){
                    continue;
                }

		textarea_elements[md5_string] = {};
		textarea_elements[md5_string]["id"] = form_textarea_elements[index].id;
		textarea_elements[md5_string]["value"] = form_textarea_elements[index].value;
                textarea_elements[md5_string]["index"] = index;
                textarea_elements[md5_string]["is_focused"] = is_focused;
	}
	return textarea_elements;
}

function connect_with_agent(client_name, client_mobile_number, agent_username=null){
	let active_website_url = get_website_url();
	let html_input_elements = get_input_html_elements();
	let html_select_elements = get_select_html_elements();
	let html_textarea_elements = get_textarea_elements();
	let focused_element = get_focused_element();
	let md5_focused_element = get_md5_string(focused_element);

	let end_date = new Date();
	let total_time_spent = (end_date.getTime() - start_date.getTime())/1000;

	json_string = JSON.stringify({
		client_name: client_name,
		client_mobile_number: client_mobile_number,
		active_website_url:active_website_url,
		html_input_elements:html_input_elements,
		html_select_elements:html_select_elements,
		html_textarea_elements:html_textarea_elements,
		currently_focused_element:md5_focused_element,
		session_id:session_id,
		total_time_spent:total_time_spent,
                agent_username:agent_username
	});

        let utf_message = CryptoJS.enc.Utf8.parse(json_string);
        let base64_message = CryptoJS.enc.Base64.stringify(utf_message);

	var xhttp = new XMLHttpRequest();
	var params = "data="+base64_message;
	xhttp.open("POST", server_domain+"/easy-assist/connect-agent/", true);
	xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
	xhttp.onreadystatechange = function(){
		if(this.readyState==4 && this.status==200){
			response = JSON.parse(this.responseText);
                        if(response.status!=200){
                            console.log(response);
                            return;
                        }
			if(session_id==null || session_id==undefined || agent_request_assistance){
				detect_value_change_event();
                                add_floating_disconnect_button();
				check_highlighted_element_timeinternal = setInterval(function(){
			            check_highlighted_element_guide();
				}, check_highlighted_element_timer);

                                setInterval(function(){
                                    connect_with_agent(client_name, client_mobile_number, agent_username);
                                }, 2000);
                                console.log("connect with agent timer started successfully.");
                                agent_request_assistance = false;
			}
			set_cookie("easy-assist-session-id", response.session_id);
			session_id = response.session_id;
		}
	}
	xhttp.send(params);
}

function highlight_agent_selected_element(mouse_event_details){
	let clientX = mouse_event_details["last_client_x"];
	let clientY = mouse_event_details["last_client_y"];
	window.scrollTo(mouse_event_details["agent_window_x_offset"], mouse_event_details["agent_window_y_offset"]);
	let agent_window_width = mouse_event_details["agent_window_width"];
	let agent_window_height = mouse_event_details["agent_window_height"];
	clientX = (clientX * window.outerWidth)/(agent_window_width);
	clientY = (clientY * window.outerHeight)/(agent_window_height);
	if(last_highlighted_element!=null){
		last_highlighted_element.style.outline = "";
	}
	last_highlighted_element = document.elementFromPoint(clientX, clientY);
	last_highlighted_element.style.outline = "solid blue 1px";
}

/*
Agent-side
*/

function sync_screen_to_agent(){
	url_params = get_url_vars();

	session_id = null;
	if("session_id" in url_params){
		session_id = url_params["session_id"];
	}else{
		return;
	}

	json_string = JSON.stringify({
		session_id:session_id
	});

	var xhttp = new XMLHttpRequest();
	var params = "data="+json_string;
	xhttp.open("POST", server_domain+"/easy-assist/sync-agent-screen/", true);
	xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
	xhttp.onreadystatechange = function(){
		if(this.readyState==4 && this.status==200){
			response = JSON.parse(this.responseText);
			if(response.status==200){
				let html_elements = response.html_elements;
				html_input_elements = html_elements["html_input_elements"];
				html_select_elements = html_elements["html_select_elements"];
				html_textarea_elements = html_elements["html_textarea_elements"];
				/*Load Input HTML Elements Value*/
				form_input_elements = document.getElementsByTagName("input");
				for(let index=0;index<form_input_elements.length;index++){
					md5_string = get_md5_string(form_input_elements[index]);
					if(form_input_elements[index].type=="checkbox"){
						form_input_elements[index].checked = html_input_elements[md5_string]["checked"];
					}else if(form_input_elements[index].type=="radio"){
						form_input_elements[index].checked = html_input_elements[md5_string]["checked"];
					}else{
						form_input_elements[index].value = html_input_elements[md5_string]["value"];
					}
				}

				/*Load Textarea HTML Elements value*/
				form_textarea_elements = document.getElementsByTagName("textarea");
				for(let index=0;index<form_textarea_elements.length;index++){
					form_textarea_elements[index].setAttribute("spellcheck", "false");
					md5_string = get_md5_string(form_textarea_elements[index]);
					form_textarea_elements[index].value = html_textarea_elements[md5_string]["value"];
				}

				/*Load Textarea HTML Elements value*/
				form_select_elements = document.getElementsByTagName("select");
				for(let index=0;index<form_select_elements.length;index++){
					md5_string = get_md5_string(form_select_elements[index]);
					form_select_elements[index].value = html_select_elements[md5_string]["value"];
				}
			}else if(response.status==101){
				alert(response.message);
				window.location = "/easy-assist/dashboard";
			}else{
				alert("Unable to connect with customer. Kindly try again later");
				window.location = "/easy-assist/dashboard";
			}
		}
	}
	xhttp.send(params);
}


function save_mouse_position(event){
	last_client_x = event.clientX;
	last_client_y = event.clientY;
	if(is_floating_pointer_active && click_counter!=-1){

		url_params = get_url_vars();

		session_id = null;
		if("session_id" in url_params){
			session_id = url_params["session_id"];
		}else{
			return;
		}

		let mouse_event_details = {
				"last_client_x": last_client_x,
				"last_client_y": last_client_y,
				"agent_window_width": window.outerWidth,
				"agent_window_height": window.outerHeight,
				"agent_window_x_offset": window.pageXOffset,
				"agent_window_y_offset": window.pageYOffset
			}

		json_string = JSON.stringify({
			"session_id": session_id,
			"mouse_event_details": mouse_event_details
		});

		var xhttp = new XMLHttpRequest();
		var params = "data="+json_string;
		xhttp.open("POST", server_domain+"/easy-assist/activate-highlight-element/", true);
		xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
		xhttp.onreadystatechange = function(){
			if(this.readyState==4 && this.status==200){
				response = JSON.parse(this.responseText);
				if(response.status==200){
					highlight_agent_selected_element(mouse_event_details);
				}
			}
		}
		xhttp.send(params);
	}
	click_counter+=1;
}

function add_floating_button(){
    var body = document.getElementsByTagName('body')[0];
    var floating_button = document.createElement('a');
    var pointer_image = document.createElement('img');
    pointer_image.src = server_domain + "/static/EasyAssistApp/img/pointer-img.png";
    pointer_image.style.width = "3em";
    pointer_image.style.height = "3em";
    floating_button.appendChild(pointer_image);
    floating_button.href = "javascript:void(0)";
    floating_button.className += "easy-assist-floating-button";
    floating_button.onclick = change_floating_button_state;
    body.append(floating_button);
}


function deactivate_highlight_element(){

	url_params = get_url_vars();

	session_id = null;
	if("session_id" in url_params){
		session_id = url_params["session_id"];
	}else{
		return;
	}

	json_string = JSON.stringify({
		"session_id": session_id
	});

	var xhttp = new XMLHttpRequest();
	var params = "data="+json_string;
	xhttp.open("POST", server_domain+"/easy-assist/deactivate-highlight-element/", true);
	xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
	xhttp.onreadystatechange = function(){
		if(this.readyState==4 && this.status==200){
			response = JSON.parse(this.responseText);
			if(response.status==200){
				if(last_highlighted_element!=null){
					last_highlighted_element.style.outline = "";
				}
			}
		}
	}
	xhttp.send(params);
}

var click_counter = -1;
function change_floating_button_state(){
	click_counter = -1;
	if(is_floating_pointer_active){
		is_floating_pointer_active = false;
		document.getElementsByClassName("easy-assist-floating-button")[0].style.backgroundColor = "#f5f5f5";
		document.getElementsByTagName("body")[0].style.cursor="";
		deactivate_highlight_element();
	}else{
		is_floating_pointer_active = true;
		document.getElementsByClassName("easy-assist-floating-button")[0].style.backgroundColor = "#ffcdd2";
		document.getElementsByTagName("body")[0].style.cursor="pointer";
	}
}


/* Auto Session Init */

function string_exists_in_list(str_list, str){
    for(let index=0;index<str_list.length;index++){
        if(str_list[index]==str){
            return true;
        }
    }
    return false;
}

function auto_session_init_value(){
    form_input_elements = document.getElementsByTagName("input");
    for(let index=0;index<form_input_elements.length;index++){
        md5_string = get_md5_string(form_input_elements[index]);
        if(string_exists_in_list(auto_session_init_list, md5_string)){
            form_input_elements[index].addEventListener("focusout", save_auto_session_value, true);
        }
    }
}

function save_auto_session_value(){
    let phone_number = this.value;
    active_website_url = get_website_url();
    json_string = JSON.stringify({
           "session_id": session_id,
           "mobile_number": phone_number,
           "website_url": active_website_url
    });
    var xhttp = new XMLHttpRequest();
    var params = "data="+json_string;
    xhttp.open("POST", server_domain+"/easy-assist/auto-session-init/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function(){
            if(this.readyState==4 && this.status==200){
                response = JSON.parse(this.responseText);
                if(response.status==200){
                    session_id = response.session_id;
                }
            }
     }
     xhttp.send(params);
}

function get_form_information(){
        var form_url = get_website_url();
        var json_string = JSON.stringify({
                "form_url": form_url
        });

        utf_message = CryptoJS.enc.Utf8.parse(json_string);
        base64_message = CryptoJS.enc.Base64.stringify(utf_message);

        var xhttp = new XMLHttpRequest();
        var params = "data="+base64_message;
        xhttp.open("POST", server_domain+"/easy-assist/get-form-information/", true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.onreadystatechange = function(){
                if(this.readyState==4 && this.status==200){
                        response = JSON.parse(this.responseText);
                        if(response.status==200){
                            confirm_message = response.confirm_message;
                            console.log("confirm message has been initialized successfully.")
                            // console.log(confirm_message);
                        }
                }
        }
        xhttp.send(params);
}



function initialize_custom_easy_assist_tag_id(){
        form_input_elements = document.getElementsByTagName("input");
        for(let index=0;index<form_input_elements.length;index++){
                form_input_elements[index].setAttribute("easy-assist-tag-id", "easy-assist-tag-"+easy_assist_tag_id);
                easy_assist_tag_id += 1;
        }

        form_textarea_elements = document.getElementsByTagName("textarea");
        for(let index=0;index<form_textarea_elements.length;index++){
                form_textarea_elements[index].setAttribute("easy-assist-tag-id", "easy-assist-tag-"+easy_assist_tag_id);
                easy_assist_tag_id += 1;
        }

        form_select_elements = document.getElementsByTagName("select");
        for(let index=0;index<form_select_elements.length;index++){
                form_select_elements[index].setAttribute("easy-assist-tag-id", "easy-assist-tag-"+easy_assist_tag_id);
                easy_assist_tag_id += 1;
        }
        console.log("custom easy assist field has been initialized successfully.");
}


function add_floating_disconnect_button(){
    var body = document.getElementsByTagName('body')[0];
    var floating_button = document.createElement('a');
    var pointer_image = document.createElement('img');
    pointer_image.src = server_domain + "/static/EasyAssistApp/img/cancel-solid.jpg";
    pointer_image.style.width = "3em";
    pointer_image.style.height = "3em";
    floating_button.id = "img-client-disconnected";
    floating_button.appendChild(pointer_image);
    floating_button.href = "javascript:void(0)";
    floating_button.zIndex = "2147483647";
    floating_button.className += "easy-assist-floating-button";
    floating_button.onclick = client_disconnected;
    body.append(floating_button);
}

function remove_floating_disconnect_button(){
    let client_disconnect = document.getElementById("img-client-disconnected");
    if(client_disconnect!=undefined && client_disconnect!=null){
        client_disconnect.remove();
    }
}
