(function (exports) {

    /*AllinCall Research and Solutions | Encryption Utility*/

    function get_easyassist_cookie(cookiename) {
        let matches = document.cookie.match(new RegExp(
            "(?:^|; )" + cookiename.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
        ));
        return matches ? matches[1] : undefined;
    }

    function get_cobrowse_middleware_token() {
        return document.querySelector("input[name=\"cobrowsemiddlewaretoken\"]").value;
    }

    function get_csrfmiddlewaretoken() {
        return document.querySelector("input[name=\"csrfmiddlewaretoken\"]").value;
    }

    function generate_random_string(length) {
        var result = '';
        var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        var charactersLength = characters.length;
        for (var i = 0; i < length; i++) {
            result += characters.charAt(Math.floor(Math.random() * charactersLength));
        }
        return result;
    }

    function easyassist_custom_encrypt(msg_string) {
        // msgString is expected to be Utf8 encoded
        var key = generate_random_string(16);
        var iv = CryptoJS.lib.WordArray.random(16);
        var encrypted = CryptoJS.AES.encrypt(msg_string, CryptoJS.enc.Utf8.parse(key), {
            iv: iv
        });
        var return_value = key;
        return_value += "." + encrypted.toString();
        return_value += "." + CryptoJS.enc.Base64.stringify(iv);
        return return_value;
    }

    function easyassist_custom_decrypt(msg_string) {
        var payload = msg_string.split(".");
        var key = payload[0];
        var decrypted_data = payload[1];
        var decrypted = CryptoJS.AES.decrypt(decrypted_data, CryptoJS.enc.Utf8.parse(key), {
            iv: CryptoJS.enc.Base64.parse(payload[2])
        });
        return decrypted.toString(CryptoJS.enc.Utf8);
    }

    function easyassist_request_id() {
        return new Date().getTime().toString();
    }

    function easyassist_authtoken() {
        return easyassist_custom_encrypt(get_easyassist_cookie("easyassist_session_id") + ":" + easyassist_request_id() + ":" + document.cookie);
    }

    exports.generate_random_string = generate_random_string
    exports.easyassist_custom_encrypt = easyassist_custom_encrypt;
    exports.easyassist_custom_decrypt = easyassist_custom_decrypt;
    exports.get_easyassist_cookie = get_easyassist_cookie;
    exports.get_cobrowse_middleware_token = get_cobrowse_middleware_token;
    exports.get_csrfmiddlewaretoken = get_csrfmiddlewaretoken;
    exports.easyassist_request_id = easyassist_request_id;
    exports.easyassist_authtoken = easyassist_authtoken;

})(window);
