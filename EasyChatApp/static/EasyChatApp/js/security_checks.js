
// trumbowyg link check
$(document).on("click", ".trumbowyg-modal-submit", function(e) {
    if (!isValidURL($(this).prev().prev().children().eq(1).children().eq(0).val())) {
        M.toast({
                "html": "Please enter a valid url."
            }, 2000);
        $(this).prev().prev().children().eq(1).children().eq(0).val("")
        return;
    }

    if(!isValidURL($(this).prev().children().eq(1).children().eq(0).val()))
    {
        var url_text = strip_unwanted_characters(stripHTML($(this).prev().children().eq(1).children().eq(0).val()));
        if(url_text == "")
        {
         M.toast({
                    "html": "Please enter a valid text."
                }, 2000);
            $(this).prev().children().eq(1).children().eq(0).val("") 

            return;   
        }
        $(this).prev().children().eq(1).children().eq(0).val(url_text)  

    }
    
})

//Check is alphanumeric
function sanitize_input(text) {
    var regex = /^[ A-Za-z0-9.]*$/
    if (text != "" && regex.test(text)) {
        return true
    } else {
        return false
    }
}

//Check is numeric
function sanitize_input_numeric(text) {
    var regex = /^[0-9]*$/
    if (text != "" && regex.test(text)) {
        return true
    } else {
        return false
    }
}

//Escapes string html, for example, '<' is converted into '&lt;'
const sanitizeHTML = (unsafe) => {
    return unsafe.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#039;');
}

//Striping html code from string
function stripHTML(htmlString) {
    return htmlString.replace(/(<([^>]+)[><])/ig, ' ');
}

//Striping unwanted characters like special characters
function strip_unwanted_characters(htmlString) {
    return htmlString.replace(/[\(\)\.\*\\\/\"\'<=]/ig, '');
}

//Strip security issue causing characters
function strip_unwanted_security_characters(htmlString) {
    return htmlString.replace(/[\(\)<>]/ig, '');
}

// Remove special and emoji chars
function remove_special_and_emoji_chars(name) {
    let check_special_character_string = name.trim().replace(/[&\/\\#,+()$~%.'":*?<>{}!@ ]/g, '');
    let check_emoji_only_string = check_special_character_string.replace(/^(?:[\u2700-\u27bf]|(?:\ud83c[\udde6-\uddff]){2}|[\ud800-\udbff][\udc00-\udfff]|[\u0023-\u0039]\ufe0f?\u20e3|\u3299|\u3297|\u303d|\u3030|\u24c2|\ud83c[\udd70-\udd71]|\ud83c[\udd7e-\udd7f]|\ud83c\udd8e|\ud83c[\udd91-\udd9a]|\ud83c[\udde6-\uddff]|[\ud83c[\ude01-\ude02]|\ud83c\ude1a|\ud83c\ude2f|[\ud83c[\ude32-\ude3a]|[\ud83c[\ude50-\ude51]|\u203c|\u2049|[\u25aa-\u25ab]|\u25b6|\u25c0|[\u25fb-\u25fe]|\u00a9|\u00ae|\u2122|\u2139|\ud83c\udc04|[\u2600-\u26FF]|\u2b05|\u2b06|\u2b07|\u2b1b|\u2b1c|\u2b50|\u2b55|\u231a|\u231b|\u2328|\u23cf|[\u23e9-\u23f3]|[\u23f8-\u23fa]|\ud83c\udccf|\u2934|\u2935|[\u2190-\u21ff])+$/, '');

    return check_emoji_only_string
}
