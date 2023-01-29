import axios from "axios";

import {
    get_session_id,
    set_input_pointer_as_per_lang,
    is_rtl_language,
} from "./console";

import {
    append_message_history,
} from "./chatbox";

import {
    custom_decrypt,
    get_params,
    showToast,
    EncryptVariable,
    encrypt_variable,
    getCsrfToken,
    is_mobile,
} from "../utils";

import {
	add_translated_message_to_local_db,
	get_translated_messages_store,
	get_object_store,
} from "./local_db";

async function translate_messages(selected_language) {

	$('#livechat_language_change_modal').modal('show');
	const session_id = get_session_id();
	const guest_session = localStorage.getItem(`guest_session-${session_id}`);
	const customer_language_display = localStorage.getItem(`customer_language_display-${session_id}`);
	const customer_language = localStorage.getItem(`customer_language-${session_id}`);

	if(!is_mobile()) {
		$('.livechat-detected-language-text').text(customer_language_display);
	    $('.detected_language').css("display", "none");
	    $('.original_language').css("display", "inline-flex");
	} else {
        $('#detected_language_mobile .livechat-detected-language-subheading').text("Translated Language : ");
        $('#detected_language_mobile .livechat-detected-language-text').css("display", "none");
	    $("#agent_language_dropdown_mobile option").each(function()
	    {
	        if($(this).val() == customer_language) {
	            $(this).attr('data-subtext', 'Original');
	        }
	    });
	    $('#agent_language_dropdown_mobile').selectpicker('refresh');
	}

	localStorage.setItem(`is_translated-${session_id}`, "true");
	localStorage.setItem(`agent_language-${session_id}`, selected_language);

	const response = await get_translated_messages(selected_language, session_id);
	append_message_history(response, 0, false);
	setTimeout(() => { $('#livechat_language_change_modal').modal('hide'); }, 500);
	set_input_pointer_as_per_lang(session_id);
 	
	for (var item = 0; item < response.length; item++) {
		let message = response[item];
	    let translated_message_obj = {
	        message_id: message.message_id,
	        language: selected_language,
	        message: message.message,
	        session_id: session_id,
	        sender_username: message.sender_username
	     };
		add_translated_message_to_local_db(translated_message_obj, get_translated_messages_store().name);
	}

}

export function get_translated_messages(selected_language, session_id) {
    return new Promise((resolve, reject) => {
	    let json_string = {
	        session_id: session_id,
	        selected_language: selected_language,
	    };

	    json_string = JSON.stringify(json_string);
	    const params = get_params(json_string);

	    let config = {
	          headers: {
	            'X-CSRFToken': getCsrfToken(),
	          }
	        }

	    axios
	        .post("/livechat/get-translated-message-history/", params, config)
	        .then((response) => {
	            response = custom_decrypt(response.data);
	            response = JSON.parse(response);
	            if(response.status == 200) {
	            	resolve(response.message_history);
	            }
	        })        
	        .catch((err) => {
	            console.log(err);
	        });
    });

}

function get_translated_text(message_id, text_message, session_id, sender_username="", language=null) {
	return new Promise (async function(resolve) {
	    let db_obj = get_object_store(get_translated_messages_store().name, "readwrite");
	    let agent_preferred_language = language;

	    if(!agent_preferred_language) {
	    	agent_preferred_language = localStorage.getItem(`agent_language-${session_id}`);
	    }

	    try {
		    var req = db_obj.get([message_id, agent_preferred_language]);

		 	req.onsuccess = async function (event) {
		 		if(event.target.result && event.target.result.message)
		        	return resolve(event.target.result.message);
		        else{
				    text_message = await get_translated_text_via_api(text_message, agent_preferred_language);
				    let translated_message_obj = {
				        message_id: message_id,
				        language: agent_preferred_language,
				        message: text_message,
				        session_id: session_id,
				        sender_username: sender_username,
				     };
					add_translated_message_to_local_db(translated_message_obj, get_translated_messages_store().name);
				    return resolve(text_message);
		        }
		    };

		    req.onerror = async function (event) {

			    text_message = await get_translated_text_via_api(text_message, agent_preferred_language);
			    let translated_message_obj = {
			        message_id: message_id,
			        language: agent_preferred_language,
			        message: text_message,
			        session_id: session_id,
			        sender_username: sender_username,
			     };
				add_translated_message_to_local_db(translated_message_obj, get_translated_messages_store().name);
			    return resolve(text_message);
		    };
		} catch(err) {
			text_message = await get_translated_text_via_api(text_message, agent_preferred_language);
			return resolve(text_message);
		}
	});
}

function get_translated_text_via_api(text_message, selected_language) {
    return new Promise((resolve, reject) => {

	    let json_string = {
	        text_message: text_message,
	        selected_language: selected_language,
	    };

	    json_string = JSON.stringify(json_string);
	    const params = get_params(json_string);

	    let config = {
	          headers: {
	            'X-CSRFToken': getCsrfToken(),
	          }
	        }

	    axios
	        .post("/livechat/get-translated-message/", params, config)
	        .then((response) => {
	            response = custom_decrypt(response.data);
	            response = JSON.parse(response);
	            if(response.status == 200) {
	            	resolve(response.translated_message);
	            }
	        })        
	        .catch((err) => {
	            console.log(err);
	        });
    });	
}

async function show_original_text(el) {

	const session_id = get_session_id();
	let text_to_be_tanslated = $(el).closest('.live-chat-client-message-wrapper').find('.live-chat-client-message-bubble').text();
	let message_id = $(el).closest('.live-chat-client-message-wrapper').attr('id');
	let is_guest_agent_message = false;
	if($(el).closest('.live-chat-client-message-wrapper').find('.live-chat-client-message-bubble-blue-border').length > 0) {
		is_guest_agent_message = true;
	}
	let agent_preferred_language = localStorage.getItem(`agent_language-${session_id}`);
	if(!agent_preferred_language) agent_preferred_language = "en";
	let sender_username = "";
	let language = "en";

	if(el.innerText == "View Original") {

		if(is_guest_agent_message) {

			language = await get_guest_agent_language(message_id, agent_preferred_language, sender_username, session_id);
		} else {

			language = localStorage.getItem(`customer_language-${session_id}`);
		}

		let translated_text = await get_translated_text(message_id, text_to_be_tanslated, session_id, sender_username, language);
		$(el).closest('.live-chat-client-message-wrapper').find('.live-chat-client-message-bubble').text(translated_text);
		el.innerText = "View Translated";
		check_message_alignment(language, el);

	} else {

		const language = localStorage.getItem(`agent_language-${session_id}`);
		let translated_text = await get_translated_text(message_id, text_to_be_tanslated, session_id, sender_username, language);
		$(el).closest('.live-chat-client-message-wrapper').find('.live-chat-client-message-bubble').text(translated_text);
		el.innerText = "View Original";
		check_message_alignment(language, el);

	}
}

function get_guest_agent_language(message_id, agent_preferred_language, sender_username, session_id) {
	return new Promise((resolve, reject) => {

		var db_obj = get_object_store(get_translated_messages_store().name, "readwrite"); 
		var req = db_obj.get([message_id, agent_preferred_language]);

	 	req.onsuccess = function (event) {
	 		if(event.target.result) {
	        	sender_username = event.target.result.sender_username;
				let language = localStorage.getItem(`guest_agent_language-${sender_username}-${session_id}`);
				if(!language) language = "en";
				resolve(language);
	 		} else { resolve("en"); }
	    };
	});
}

async function show_translated_text(el) {
	const session_id = get_session_id();
	let text_to_be_tanslated = $(el).closest('.live-chat-agent-message-wrapper').find('.live-chat-agent-message-bubble').text();
	let text_el_class = "live-chat-agent-message-bubble";
	let message_id = $(el).closest('.live-chat-agent-message-wrapper').attr('id');

	if($(el).closest('.live-chat-agent-message-wrapper').find('.live-chat-attachment-div').length > 0){
		text_to_be_tanslated = $(el).closest('.live-chat-agent-message-wrapper').find('.live-chat-attachment-text').text();
		text_el_class = "live-chat-attachment-text";
	}

	if(el.innerText == "View Translated") {

		const language = localStorage.getItem(`customer_language-${session_id}`);
		let translated_text = await get_translated_text(message_id, text_to_be_tanslated, session_id, "", language);
		$(el).closest('.live-chat-agent-message-wrapper').find('.'+text_el_class).text(translated_text);
		el.innerText = "View Original";
		check_message_alignment(language, el, text_el_class);

	} else {

		const language = localStorage.getItem(`agent_language-${session_id}`);
		let translated_text = await get_translated_text(message_id, text_to_be_tanslated, session_id, "", language);
		$(el).closest('.live-chat-agent-message-wrapper').find('.'+text_el_class).text(translated_text);
		el.innerText = "View Translated";
		check_message_alignment(language, el, text_el_class);
		
	}
}

function check_message_alignment(language, el, text_el_class="") {
	if(is_rtl_language(language)) {
		if(text_el_class) {
			$(el).closest('.live-chat-agent-message-wrapper').find('.'+text_el_class).css('text-align', 'right');
		} else {
			$(el).closest('.live-chat-client-message-wrapper').find('.live-chat-client-message-bubble').css('text-align', 'right');
		}
	} else {
		if(text_el_class) {
			$(el).closest('.live-chat-agent-message-wrapper').find('.'+text_el_class).css('text-align', 'left');
		} else {
			$(el).closest('.live-chat-client-message-wrapper').find('.live-chat-client-message-bubble').css('text-align', 'left');
		}
	}
}

function hide_mobile_language_translate_prompt() {
    $('#livechat_mobile_language_container').css("display", "none");
    $('#livechat_langauge_container_show').css("display", "block");
}

function show_mobile_language_translate_prompt(){
    $('#livechat_langauge_container_show').css("display", "none");
    $('#livechat_mobile_language_container').css("display", "inline-flex");
}

export {
	translate_messages,
	get_translated_text,
	show_original_text,
	show_translated_text,
	hide_mobile_language_translate_prompt,
	show_mobile_language_translate_prompt,
}