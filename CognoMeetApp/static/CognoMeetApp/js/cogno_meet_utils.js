function stripHTML(text) {
    try {
        text = text.trim();
    } catch (err) { }

    let regex = /(<([^>]+)>)/ig;
    return text.replace(regex, "");
}

function remove_all_special_characters_from_str(text) {
    let regex = /:|;|'|"|=|-|\$|\*|%|!|~|\^|\(|\)|\[|\]|\{|\}|\[|\]|#|<|>|,|@|\.|\/|\\/g;
    text = text.replace(regex, "");
    return text;
}

function remove_special_characters_from_str(text) {
    let regex = /:|;|'|"|=|-|\$|\*|%|!|`|~|&|\^|\(|\)|\[|\]|\{|\}|\[|\]|#|<|>|\/|\\/g;
    text = text.replace(regex, "");
    return text;
}

function check_malicious_file_video_meeting(file_name) {
    if (file_name.split('.').length != 2) {
        console.log("Please do not use .(dot) except for extension");
        return true;
    }

    let allowed_files_list = [
        "png", "jpg", "jpeg", "bmp", "gif", "tiff", "exif", "jfif", "webm", "mpg",
        "mp2", "mpeg", "mpe", "mpv", "ogg", "mp4", "m4p", "m4v", "avi", "wmv", "mov", "qt", "doc", "docx",
        "flv", "swf", "avchd", "mp3", "aac", "pdf", "xls", "xlsx", "json", "xlsm", "xlt", "xltm", "zip", "PNG"
    ];

    let file_extension = file_name.substring(file_name.lastIndexOf(".") + 1, file_name.length);
    file_extension = file_extension.toLowerCase();

    if (allowed_files_list.includes(file_extension) == false) {
        console.log("." + file_extension + " files are not allowed");
        return true;
    }
    return false;
}