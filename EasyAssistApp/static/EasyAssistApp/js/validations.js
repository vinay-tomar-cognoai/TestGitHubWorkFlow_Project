const REGEX_NAME = /^[^\s][a-zA-Z ]+$/;
const REGEX_MOBILE = /^[6-9]{1}\d{9}$/;
const REGEX_INPUT_NUMBER = /^[0-9]+$/;
const REGEX_INPUT_TEXT = /^[A-Za-z0-9,.@ \n]+$/;

var ALLOWED_FILES_LIST = [
    "png", "jpg", "jpeg", "svg", "bmp", "gif", "tiff", "exif", "jfif"
];

function perform_html_encoding(input_string) {
    try {
        var el = document.createElement("div");
        el.innerText = el.textContent = input_string;
        input_string = el.innerHTML;
        input_string = input_string.replace(/\"/g, '&quot;');
        input_string = input_string.replace(/\'/g, '&#039;');
        return input_string;
    } catch (error) {
        console.log(error);
        return input_string;
    }
}

function is_password_valid(old_password, new_password, error_message_element) {
    const regexPassword = /^(?=.*[A-Z])(?=.*[!@#$&*])(?=.*\d)(?=.*[a-z]).{8,}/;
    if (!regexPassword.test(new_password)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Minimum length of password is 8 and must have at least one lower case alphabet, one upper case alphabet, one digit and one special character (a-z, A-Z, 0-9, Special characters)";
        return false;
    }
}

function check_file_extension(filename) {
    var fileExtension = "";
    if (filename.lastIndexOf(".") > 0) {
        fileExtension = filename.substring(filename.lastIndexOf(".") + 1, filename.length);
    }
    fileExtension = fileExtension.toLowerCase();
    var allowed_files = ["png", "jpg", "jpeg", "pdf", "doc", "docx"];
    if (allowed_files.includes(fileExtension)) return true;

    return false;
}


function check_malicious_file_chatbot(filename) {
    if(filename.split('.').length != 2) {
        return true;
    }
    return false;
}

function check_malicious_file(file_name) {
    var response = {
        'status': false,
        'message': 'OK'
    }
    if (file_name.split('.').length != 2) {
        response.status = true;
        response.message = 'Please do not use .(dot) except for extension';
        return response;
    }

    var allowed_files_list = [
        "png", "jpg", "jpeg", "bmp", "gif", "tiff", "exif", "jfif", "webm", "mpg",
        "mp2", "mpeg", "mpe", "mpv", "ogg", "mp4", "m4p", "m4v", "avi", "wmv", "mov", "qt", "doc", "docx",
        "flv", "swf", "avchd", "mp3", "aac", "pdf", "xls", "xlsx", "json", "xlsm", "xlt", "xltm", "zip"
    ];

    var file_extension = file_name.substring(file_name.lastIndexOf(".") + 1, file_name.length);
    file_extension = file_extension.toLowerCase();
    if (allowed_files_list.includes(file_extension) == false) {
        response.status = true;
        response.message = '.' + file_extension + ' files are not allowed'
        return response;
    }
    return response;
}

function sanitize_filename(filename) {
    try {
        let sanitized_name = stripHTML(filename);
        sanitized_name = remove_special_characters_from_str(sanitized_name);
        return sanitized_name;
    } catch (error) {
        return filename;
    }
}

function check_image_file_chatbot(file_extension) {
    file_extension = file_extension.toLowerCase();
    var image_files = ["png", "jpg", "jpeg"];

    if(image_files.includes(file_extension)) {
        return true;
    }
    return false;
}

function check_image_file(file_name, allowed_files_list=ALLOWED_FILES_LIST, show_toast_message=true) {
   
    var file_extension = file_name.substring(file_name.lastIndexOf(".") + 1, file_name.length);
    file_extension = file_extension.toLowerCase();

    if (allowed_files_list.includes(file_extension) == false) {
        if(show_toast_message) {
            show_easyassist_toast("." + file_extension + " files are not allowed");
        }
        return false;
    }
    return true;
}

function stripHTML(text) {
    try {
        text = text.trim();
    } catch (err) {}

    var regex = /(<([^>]+)>)/ig;
    return text.replace(regex, "");
}

function remove_special_characters_from_str(text) {
    var regex = /:|;|'|"|=|-|\$|\*|%|!|`|~|&|\^|\(|\)|\[|\]|\{|\}|\[|\]|#|<|>|\/|\\/g;
    text = text.replace(regex, "");
    return text;
}

function easyassist_mobile_number_validation(event){
    var element = event.target;
    var value = element.value;
    var count = value.length;

    if ((event.keyCode >= 48 && event.keyCode <= 57) || (event.keyCode >= 96 && event.keyCode <= 105)) { 
        if(count >= 10){
            event.preventDefault();
        }
    }
}

function number_format(number, decimals, dec_point, thousands_sep) {
	// *     example: number_format(1234.56, 2, ',', ' ');
	// *     return: '1 234,56'
	number = (number + '').replace(',', '').replace(' ', '');
	let n = !isFinite(+number) ? 0 : +number,
		prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
		sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
		dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
		s = '',
		toFixedFix = function(n, prec) {
			var k = Math.pow(10, prec);
			return '' + Math.round(n * k) / k;
		};
	// Fix for IE parseFloat(0.55).toFixed(0) = 0;
	s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
	if (s[0].length > 3) {
		s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
	}
	if ((s[1] || '').length < prec) {
		s[1] = s[1] || '';
		s[1] += new Array(prec - s[1].length + 1).join('0');
	}
	return s.join(dec);
}

function check_text_link(text) {
    var link_pattern_1 = /(\b(https?|ftp):\/\/[-A-Z0-9+&@#\/%?=_|!:,.;]*[-A-Z0-9+&@#\/%=_|])/ig;
    var link_pattern_2 = /(^|[^\/])(www\.[\S]+(\b|$))/ig;

    if(link_pattern_1.test(text) || link_pattern_2.test(text)) {
        return true;
    }
    return false;
}

function check_file_name(file_name) {
    file_name = file_name.substring(0, file_name.lastIndexOf("."), file_name.length);
    var reg_file = /^[a-zA-Z0-9_-]+$/; 
    
    return !reg_file.test(file_name);
}

function check_valid_email(email_id) {
    if(!email_id) {
        return false;
    }

    var regex_email = /^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/;
    if(!regex_email.test(email_id)) {
        return false;
    }
    return true;
}
 
 function remove_all_special_characters_from_str(text) {
    var regex = /:|;|'|"|=|-|\$|\*|%|!|~|\^|\(|\)|\[|\]|\{|\}|\[|\]|#|<|>|,|@|\.|\/|\\/g;
    text = text.replace(regex, "");
    return text;
}

function get_iso_formatted_date(date) {

    var date_pattern = /\d\d-\d\d-\d\d\d\d/
    if(date_pattern.test(date)) {
        date = date.split("-");
        date = date[2] + "-" + date[1] + "-" + date[0]
    }

    return date;
}

function is_droplink_url_valid(url) {
    var https_pattern = /^https:\/\/?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$/;
    var http_pattern = /^http:\/\/?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$/;
    if (https_pattern.test(url) || http_pattern.test(url)) {
        return true;
    }
    return false;
}

function is_url_valid(url_str, is_http_check_required=false) {
    var url_pattern;
    if (is_http_check_required) {
        url_pattern = /(http(s)?:\/\/.)[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g;
    } else {
        url_pattern = /[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g;
        if (url_str.includes("http://") || url_str.includes("https://")) {
            return false;
        }
    }
    var result = url_str.match(url_pattern);
    return result == null ? false : true;
}

function check_malicious_file_video_meeting(file_name) {
    if(file_name.split('.').length != 2) {
        show_toast("Please do not use .(dot) except for extension");
        return true;
    }

    var allowed_files_list = [
        "png", "jpg", "jpeg", "bmp", "gif", "tiff", "exif", "jfif", "webm", "mpg", 
        "mp2", "mpeg", "mpe", "mpv", "ogg", "mp4", "m4p", "m4v", "avi", "wmv", "mov", "qt", "doc", "docx",
        "flv", "swf", "avchd","mp3", "aac", "pdf", "xls", "xlsx", "json", "xlsm", "xlt", "xltm", "zip", "PNG"
    ];

    var file_extension = file_name.substring(file_name.lastIndexOf(".") + 1, file_name.length);
    file_extension = file_extension.toLowerCase();

    if(allowed_files_list.includes(file_extension) == false) {
        show_toast("." + file_extension + " files are not allowed");
        return true;
    }
    return false;
}

function perform_url_encoding(input_string) {
    try {
        input_string = input_string.replace(/&/g, '&amp;');
        input_string = input_string.replace(/\"/g, '&quot;');
        input_string = input_string.replace(/\'/g, '&#039;');
        input_string = input_string.replace(/</g, '&lt;');
        input_string = input_string.replace(/>/g, '&gt;');
        return input_string;
    } catch (error) {
        console.log(error);
        return input_string;
    }
}

function sanitize_input_string(input_string) {
    try {
        input_string = stripHTML(input_string);
        input_string = remove_special_characters_from_str(input_string);
        return input_string;
    } catch (err) {
        return input_string
    }
}

function name_input_validator(name,id){    
    if(name != undefined && name.length > 0){
        const regName = /^[a-zA-Z ]+$/;            
            if (!regName.test(name)) {                
                name = name.replace(/[^A-Za-z ]+/g, '');

                if(document.getElementById(id)){
                    document.getElementById(id).value = name;
                }        
            }                   
    }       
}

function easyassist_phone_number_paste_handler(event) {
    let easyassist_pasted_data = (event.clipboardData || window.clipboardData).getData('text');
    if(easyassist_pasted_data.indexOf('.') > -1) {
        event.preventDefault();
    }
}

function easyassist_prevent_non_numeric_characters(event) {
    var blacklisted_keycode = [69, 107, 109, 110, 187, 189, 190];
    if(blacklisted_keycode.includes(event.keyCode)) {
        event.preventDefault();
    }
}

function easyassist_word_limit(event, element, max_count){
    var value = element.value;
    var count = value.length;

    if ((event.keyCode >= 48 && event.keyCode <= 57) || (event.keyCode >= 96 && event.keyCode <= 105)) { 
        if(count >= max_count){
            event.preventDefault(); // Cancel event
        }
    }
}

function is_valid_chrome_extension_url(url_str) {
    var url_pattern = /^(www.)+[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$/g;
    if (url_str.includes("http://") || url_str.includes("https://")) {
        return false;
    }
    var result = url_str.match(url_pattern);
    return result == null ? false : true;
}

function easyassist_linkify(inputText) {
    var replacedText, replacePattern1, replacePattern2;

    //URLs starting with http://, https://, or ftp://
    replacePattern1 = /(\b(https?|ftp):\/\/[-A-Z0-9+&@#\/%?=_|!:,.;]*[-A-Z0-9+&@#\/%=_|])/gim;
    replacedText = inputText.replace(replacePattern1, '<a href="$1" target="_blank">$1</a>');

    //URLs starting with "www." (without // before it, or it'd re-link the ones done above).
    replacePattern2 = /(^|[^\/])(www\.[\S]+(\b|$))/gim;
    replacedText = replacedText.replace(replacePattern2, '$1<a href="http://$2" target="_blank">$2</a>');

    return replacedText;
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

function check_valid_mobile_number(mobile_number) {
    if(!mobile_number) {
        return false;
    }

    if(!REGEX_MOBILE.test(mobile_number)) {
        return false;
    }
    return true;
}

function check_valid_name(name) {
    if(!name) {
        return false;
    }

    if(!REGEX_NAME.test(name)) {
        return false;
    }
    return true;
}

function input_number_validator(input_number) {
    if(!REGEX_INPUT_NUMBER.test(input_number)) {
        return false;
    }
    return true;
}

function is_input_text_valid(input_text) {
    if(!REGEX_INPUT_TEXT.test(input_text)) {
        return false;
    }
    return true;
}