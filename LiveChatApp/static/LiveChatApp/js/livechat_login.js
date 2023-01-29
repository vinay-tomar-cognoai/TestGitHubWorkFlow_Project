/////////////////////////////// Encryption And Decription //////////////////////////

function CustomEncrypt(msgString, key) {
    // msgString is expected to be Utf8 encoded
    var iv = CryptoJS.lib.WordArray.random(16);
    var encrypted = CryptoJS.AES.encrypt(msgString, CryptoJS.enc.Utf8.parse(key), {
        iv: iv
    });
    var return_value = key;
    return_value += "." + encrypted.toString();
    return_value += "." + CryptoJS.enc.Base64.stringify(iv);
    return return_value;
}

function generateRandomString(length) {
    var result = '';
    var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for (var i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}


function EncryptVariable(data) {

    utf_data = CryptoJS.enc.Utf8.parse(data);
    encoded_data = utf_data;
    // encoded_data = CryptoJS.enc.Base64.stringify(utf_data);
    random_key = generateRandomString(16);
    // console.log(random_key)
    encrypted_data = CustomEncrypt(encoded_data, random_key);

    return encrypted_data;
}


function custom_decrypt(msg_string) {

    var payload = msg_string.split(".");
    var key = payload[0];
    var decrypted_data = payload[1];
    var decrypted = CryptoJS.AES.decrypt(decrypted_data, CryptoJS.enc.Utf8.parse(key), {
        iv: CryptoJS.enc.Base64.parse(payload[2])
    });
    return decrypted.toString(CryptoJS.enc.Utf8);
}

////////////////////////////////////////////////////////////////////////////////////


function get_easychat_access_token() {
    return document.querySelector("input[name=\"easychataccesstoken\"]").value;
}

function set_cookie(cookiename, cookievalue, path = "") {
    if (path == "") {
        document.cookie = cookiename + "=" + cookievalue;
    } else {
        document.cookie = cookiename + "=" + cookievalue + ";path=" + path;
    }
}

function get_cookie(cookiename) {
    var cookie_name = cookiename + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var cookie_array = decodedCookie.split(';');
    for (var i = 0; i < cookie_array.length; i++) {
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

function getCSRFToken() {
    return $('input[name="csrfmiddlewaretoken"]').val();
}

function stripHTML(htmlString) {
    return htmlString.replace(/<[^>]+>/g, '');
}

function login_function(logout_other) {

    username = document.getElementById("username");
    password = document.getElementById("password");
    easychat_access_token = get_easychat_access_token();
    document.getElementById("login-error").innerHTML = "";

    if (username.value == "") {
        document.getElementById("login-error").innerHTML = "Please enter valid username";
        return;
    }
    if (password.value == "") {
        document.getElementById("login-error").innerHTML = "Please enter valid password";
        return;
    }
    captcha = document.getElementById("captcha").value;
    if (captcha == "") {
        document.getElementById("login-error").innerHTML = "Please enter valid captcha";
        return;
    }
    document.getElementById("login_btn").innerHTML = "Logging in.."
    tempusername = stripHTML(username.value);
    encrypted_username = EncryptVariable(username.value)
    encrypted_password = EncryptVariable(password.value)
    encrypted_easychat_access_token = EncryptVariable(easychat_access_token)
    logout_other = EncryptVariable(logout_other)
    // username.value = encrypted_username;
    var temppassword = "";
    for (var i = 0; i < encrypted_password.length; i++) {
        temppassword += "*";
    }
    // password.value = temppassword;
    encrypted_captcha = EncryptVariable(captcha)
    captcha_image = document.getElementById("captcha_image").src;
    encrypted_captcha_image = EncryptVariable(captcha_image)
    CSRF_TOKEN = getCSRFToken();
    var response = $.ajax({
        url: '/chat/authentication/',
        type: "POST",
        headers: {
            'X-CSRFToken': CSRF_TOKEN,
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        async: false,
        data: {
            username: encrypted_username,
            password: encrypted_password,
            captcha: encrypted_captcha,
            captcha_image: encrypted_captcha_image,
            easychat_access_token: encrypted_easychat_access_token,
            logout_other: logout_other,
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                set_cookie("is_online", "1", "/");
                setTimeout(function() {
                    window.location = '/livechat/';
                }, 2000);
            } else if (response["status"] == 300) {
                $("#session-options").modal("open");
                document.getElementById("login-error").innerHTML = "Session running. Kindly logout from your last session."
                // refreshCaptchaImage()
                document.getElementById("login_btn").innerHTML = "Login"
            } else if (response["status"] == 302) {
                username.value = "";
                password.value = "";
                document.getElementById("captcha").value = "";
                username.focus()
                document.getElementById("login-error").innerHTML = "You have entered invalid captcha. Try again."
                document.getElementById("login_btn").innerHTML = "Login"
                refreshCaptchaImage()
            } else if (response["status"] == 301) {
                username.value = "";
                password.value = "";
                document.getElementById("captcha").value = "";
                document.getElementById("login-error").innerHTML = "You have entered incorrect password more than 5 times. Kindly contact administrator."
                document.getElementById("login_btn").innerHTML = "Login"
                refreshCaptchaImage()
            } else if (response["status"] == 401) {
                // setTimeout(function() {
                //     $("#forgot-pass-btn").click()
                // }, 2000);
            } else {
                username.value = "";
                password.value = "";
                document.getElementById("captcha").value = "";
                username.focus()
                document.getElementById("login-error").innerHTML = "Please check your username or password"
                refreshCaptchaImage()
                document.getElementById("login_btn").innerHTML = "Login"
            }
        },
        error: function(error) {
            document.getElementsByClassName('gy-center')[0].style["-webkit-filter"] = "";
        }
    }).responseJSON;

    return response;
}

$(document).on("click", "#login_btn", function() {
    login_function(false);
});