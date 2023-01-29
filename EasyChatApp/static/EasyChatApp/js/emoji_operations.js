function check_emoji_response() {

	angry_emoji_response = $("#angry-emoji-response").trumbowyg('html');
    happy_emoji_response = $("#happy-emoji-response").trumbowyg('html');
    neutral_emoji_response = $("#neutral-emoji-response").trumbowyg('html');
    sad_emoji_response = $("#sad-emoji-response").trumbowyg('html');

    angry_emoji_response_filtered = validate_ck_editor_response(angry_emoji_response)
    happy_emoji_response_filtered = validate_ck_editor_response(happy_emoji_response)
    neutral_emoji_response_filtered = validate_ck_editor_response(neutral_emoji_response)
    sad_emoji_response_filtered = validate_ck_editor_response(sad_emoji_response)

    if (angry_emoji_response_filtered.length == 0) {

        M.toast({
            "html": "Angry emoji response message cannot be empty."
        }, 2000);
        return false;
    }

    if (happy_emoji_response_filtered.length == 0) {

        M.toast({
            "html": "Happy emoji response message cannot be empty."
        }, 2000);
        return false;
    }

    if (neutral_emoji_response_filtered.length == 0) {

        M.toast({
            "html": "Neutral emoji response message cannot be empty."
        }, 2000);
        return false;
    }

    if (sad_emoji_response_filtered.length == 0) {

        M.toast({
            "html": "Sad emoji response message cannot be empty."
        }, 2000);
        return false;
    }

    return true
}


function save_emoji_modal() {

	var successful = check_emoji_response()
	if (successful) {
		$('#modal-emoji-bot-response').modal('close');
	}
}

function set_livechat_checkbox_value_list() {
	var emoji_livechat_checkbox_value_list = []
		
		emoji_livechat_checkbox_value_list[0] = document.getElementById("angry-emoji-response-livechat").checked
        emoji_livechat_checkbox_value_list[1] = document.getElementById("happy-emoji-response-livechat").checked
        emoji_livechat_checkbox_value_list[2] = document.getElementById("neutral-emoji-response-livechat").checked
        emoji_livechat_checkbox_value_list[3] = document.getElementById("sad-emoji-response-livechat").checked

    return emoji_livechat_checkbox_value_list
}