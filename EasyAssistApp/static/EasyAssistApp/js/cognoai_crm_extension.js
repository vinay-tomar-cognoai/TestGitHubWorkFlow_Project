
async function cognoai_add_css_file(filename) {
    var style = document.createElement('link');
    style.href = filename;
    style.type = 'text/css';
    style.rel = 'stylesheet';
    document.head.appendChild(style);
}

async function cognoai_add_js_file(filename) {
    var script = document.createElement('script');
    script.src = filename;
    script.type = 'text/javascript';
    document.head.appendChild(script)
}

function cognoai_init() {
    try {
        window.localStorage.setItem('cognoai_access_token', ACCESS_TOKEN)
        window.localStorage.setItem('cognoai_server_url', COGNOAI_SERVER_URL)
    } catch {}
}

window.onload = function() {
    if (ALLOWED_HOST.includes(window.location.hostname)) {
        var development = false;
        cognoai_init();
        cognoai_add_js_file(COGNOAI_SERVER_URL + "/static/EasyAssistApp/js/crypto-js.min.js");
        cognoai_add_js_file(COGNOAI_SERVER_URL + "/static/EasyAssistApp/js/cognoai_extension_encrypt.js");

        if(development == true) {
            cognoai_add_css_file(COGNOAI_SERVER_URL + "/static/EasyAssistApp/css/cognoai_extension.css");
        } else {
            cognoai_add_css_file(COGNOAI_SERVER_URL + "/static/EasyAssistApp/css/" + ACCESS_TOKEN + "/cognoai_extension.css");
        }
        var cognoai_agent_verification_token = "";
        try {
            cognoai_agent_verification_token = window.localStorage.getItem('cognoai_agent_verification_token')
        } catch {
            cognoai_agent_verification_token = ""
        }
        setTimeout(function() {
            if(development == true) {
                if (cognoai_agent_verification_token != "" && cognoai_agent_verification_token != undefined && cognoai_agent_verification_token != 'None' && cognoai_agent_verification_token != null) {
                    console.log("Verification Successful.")
                    cognoai_add_js_file(COGNOAI_SERVER_URL + "/static/EasyAssistApp/js/cognoai_extension.js");
                } else {
                    cognoai_add_js_file(COGNOAI_SERVER_URL + "/static/EasyAssistApp/js/cognoai_login_extension.js");
                }
            } else {
                if (cognoai_agent_verification_token != "" && cognoai_agent_verification_token != undefined && cognoai_agent_verification_token != 'None' && cognoai_agent_verification_token != null) {
                    console.log("Verification Successful.")
                    cognoai_add_js_file(COGNOAI_SERVER_URL + "/static/EasyAssistApp/js/" + ACCESS_TOKEN + "/cognoai_extension.js");
                } else {
                    cognoai_add_js_file(COGNOAI_SERVER_URL + "/static/EasyAssistApp/js/" + ACCESS_TOKEN + "/cognoai_login_extension.js");
                }
            }
        },1000)
    }
}