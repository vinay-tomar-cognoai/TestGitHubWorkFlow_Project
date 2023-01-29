/*setup.js | AllinCall Research and Solutions PVT LTD.*/

const server_domain = "https://easyassist.allincall.in";
var active_form_id = null;

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

add_css_file(server_domain+"/static/EasyAssistApp/css/setup.css");
add_javascript(server_domain+"/static/EasyAssistApp/js/crypto-js.min.js");
add_javascript(server_domain+"/static/EasyAssistApp/js/json2.js");

function console_log_md5(){
    console.log(get_md5_string(this));
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

function open_modal_to_create_new_form(){
     const modal_create_form = '\
	<div id="modal-confirm-to-create-new-easyassist" class="easyassist-modal">\
    	    <div class="easyassist-modal-content">\
        	<span class="easyassist-close" onclick="close_easyassist_modal()">&times;</span>\
        	<div>\
            		<div class="easyassist-modal-input-element">\
                		<p>Hey, welcome to EasyAssist form creation module. I will help you to setup your form quickly. Would like to start the process?</p>\
            		</div>\
            		<button onclick="create_new_form(this)" class="easyassist-modal-button">Yes</button>\
            		<button onclick="close_easyassist(this)" class="easyassist-modal-button">No</button>\
        	</div>\
    	    </div>\
	</div>';

    body_element = document.getElementsByTagName("body")[0];
    body_element.innerHTML = body_element.innerHTML +  modal_create_form;
    document.getElementById("modal-confirm-to-create-new-easyassist").style.display="block";
}

function close_easyassist(){
    document.getElementById("modal-confirm-to-create-new-easyassist").style.display="none";
}

function create_new_form(){
     document.getElementById("modal-confirm-to-create-new-easyassist").style.display="none";
     const modal_create_form = '\
	<!-- The Modal -->\
	<div id="modal-create-form-easyassist" class="easyassist-modal">\
    		<!-- Modal content -->\
    		<div class="easyassist-modal-content">\
        		<span class="easyassist-close" onclick="close_easyassist_modal()">&times;</span>\
        		<div class="row">\
            			<div class="col s12">\
                			<p id="easyassist-new-form-error-message" style="color:red;"></p><hr>\
            			</div>\
            			<div class="col s12 easyassist-modal-input-element">\
                			<p>Form Name<sup class="red-text">*</sup></p>\
                			<input id="easyassist-new-form-name" placeholder="Form name" style="width:90%;">\
            			</div>\
                                <div class="col s12 easyassist-modal-input-element">\
                                        <p>Form Confirmation Message<sup class="red-text">*</sup></p>\
                                        <textarea id="easyassist-new-form-confirmation-message" placeholder="Form Confirmation Messsage" style="width:90%;"></textarea>\
                                </div>\
            			<button onclick="submit_to_create_new_form_easyassist(this)" class="easyassist-modal-button">Submit</button>\
        		</div>\
    		</div>\
	</div>';

    body_element = document.getElementsByTagName("body")[0];
    body_element.innerHTML = body_element.innerHTML +  modal_create_form;
    document.getElementById("modal-create-form-easyassist").style.display="block";
}


function create_new_field(){
     md5_string = get_md5_string(this);
     create_field_modal_element = document.getElementById("modal-create-field-easyassist");
     if(create_field_modal_element!=null && create_field_modal_element!=undefined){
         create_field_modal_element.parentNode.removeChild(create_field_modal_element);
     }
     const modal_create_field = '\
	<!-- The Modal -->\
	<div id="modal-create-field-easyassist" class="easyassist-modal">\
    		<!-- Modal content -->\
    		<div class="easyassist-modal-content">\
        		<span class="easyassist-close" onclick="reset_easyassist_field_modal()">&times;</span>\
        		<div class="row">\
            			<div class="col s12">\
                			<p id="easyassist-new-field-error-message" style="color:red;"></p><hr>\
            			</div>\
                                <div class="col s12" style="display:none;">\
                                       <p>MD5 Hashed</p>\
                                       <input type="text" id="easyassist-new-field-md5-value" placeholder="Field MD5 Value" disabled value='+ md5_string +'>\
                                </div>\
            			<div class="col s12 easyassist-modal-input-element">\
                			<p>Name<sup class="red-text">*</sup></p>\
                			<input type="text" id="easyassist-new-field-name" placeholder="Field name">\
            			</div>\
                                <div class="col s12 easyassist-modal-input-element">\
                                        <p>Is Masked<sup class="red-text">*</sup></p>\
                                        <input type="checkbox" id="easyassist-new-field-is-masked">\
                                </div>\
                                <div class="col s12 easyassist-modal-input-element">\
                                        <p>Group Number<sup class="red-text">*</sup></p>\
                                        <input type="number" id="easyassist-new-field-group-number">\
                                </div>\
            			<button onclick="submit_to_create_new_field_easyassist(this)" class="easyassist-modal-button">Submit</button>\
        		</div>\
    		</div>\
	</div>';

    body_element = document.getElementsByTagName("body")[0];
    body_element.innerHTML = body_element.innerHTML +  modal_create_field;
    document.getElementById("modal-create-field-easyassist").style.display="block";
}


function get_website_url(){
    new_href = window.location.href;
    new_href = new_href.split(";")[0];
    new_href = new_href.replace("#!","");
    new_href = new_href.split("?")[0];
    return new_href;
}

function alphanumeric(inputtxt){
    var letterNumber = /^[0-9a-zA-Z-&@,'. ]+$/;
    if((inputtxt.value.match(letterNumber))){
        return true;
    }else{
        return false;
    }
}

function submit_to_create_new_form_easyassist(){

    document.getElementById("easyassist-new-form-error-message").innerHTML=""

    form_name_element = document.getElementById("easyassist-new-form-name");
    if(alphanumeric(form_name_element)==false){
        document.getElementById("easyassist-new-form-error-message").innerHTML="Please enter valid form name";
        return;
    }

    form_confirm_message_element = document.getElementById("easyassist-new-form-confirmation-message");
    if(alphanumeric(form_confirm_message_element)==false){
        document.getElementById("easyassist-new-form-error-message").innerHTML="Please enter valid form confirmation message";
        return;
    }

    website_url = get_website_url();
    json_string = JSON.stringify({
        form_name:form_name_element.value,
        form_confirm_message:form_confirm_message_element.value,
        website_url:website_url
    });

    var xhttp = new XMLHttpRequest();
    var params = "data="+json_string;
    xhttp.open("POST", server_domain+"/easy-assist/create-new-form/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function(){
	 if(this.readyState==4 && this.status==200){
	     response = JSON.parse(this.responseText);
             if(response.status==200){
                 active_form_id = response.form_id;
             }else{
                 active_form_id = null;
             }
             document.getElementById("modal-create-form-easyassist").style.display="none";
             expose_md5_hashed_element();
	 }
    }
    xhttp.send(params);
}

function submit_to_create_new_field_easyassist(element){

    document.getElementById("easyassist-new-field-error-message").innerHTML=""

    field_name_element = document.getElementById("easyassist-new-field-name");
    if(alphanumeric(field_name_element)==false){
        document.getElementById("easyassist-new-field-error-message").innerHTML="Please enter valid field name";
        return;
    }

    field_is_masked = document.getElementById("easyassist-new-field-is-masked").checked;

    field_group_number_element = document.getElementById("easyassist-new-field-group-number");
    if(field_group_number_element.value==""){
        document.getElementById("easyassist-new-field-error-message").innerHTML="Please enter valid group number";
        return;
    }

    md5_string = document.getElementById("easyassist-new-field-md5-value").value;

    json_string = JSON.stringify({
        md5_string:md5_string,
        active_form_id:active_form_id,
        field_name:field_name_element.value,
        is_masked:field_is_masked,
        group_number:field_group_number_element.value
    });

    var xhttp = new XMLHttpRequest();
    var params = "data="+json_string;
    xhttp.open("POST", server_domain+"/easy-assist/create-new-field/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function(){
         if(this.readyState==4 && this.status==200){
             response = JSON.parse(this.responseText);
             if(response.status==200){
                 create_field_modal_element = document.getElementById("modal-create-field-easyassist");
                 create_field_modal_element.parentNode.removeChild(create_field_modal_element);
                 expose_md5_hashed_element();
             }else{
                 document.getElementById("easyassist-new-field-error-message").innerHTML="Unable to save field. Kindly try again later.";
             }
         }
    }
    xhttp.send(params);
}

function expose_md5_hashed_element(){
        //remove_expose_md5_hashed_element();
	form_input_elements = document.getElementsByTagName("input");
	for(var index=0;index<form_input_elements.length;index++){
		form_input_elements[index].addEventListener("focusin", create_new_field, true);
	}
	form_textarea_elements = document.getElementsByTagName("textarea");
	for(var index=0;index<form_textarea_elements.length;index++){
		form_textarea_elements[index].setAttribute("spellcheck", "false");
		form_textarea_elements[index].addEventListener("focusin", create_new_field, true);
	}
	form_select_elements = document.getElementsByTagName("select");
	for(var index=0;index<form_select_elements.length;index++){
		form_select_elements[index].addEventListener("mousedown", create_new_field, true);
                form_select_elements[index].addEventListener("change", create_new_field, true);
	}
        //console.log("reset_expose_md5_hashed_element");
}

window.onload = function(e){
    // expose_md5_hashed_element();
    open_modal_to_create_new_form();
};

function close_easyassist_modal(){
    easyassist_modal_list = document.getElementsByClassName("easyassist-modal");
    for(var index=0;index<easyassist_modal_list.length;index++){
        easyassist_modal_list[index].style.display = "none";
    }
}

function reset_easyassist_field_modal(){
    create_field_modal_element = document.getElementById("modal-create-field-easyassist");
    create_field_modal_element.parentNode.removeChild(create_field_modal_element);
    expose_md5_hashed_element();
}
