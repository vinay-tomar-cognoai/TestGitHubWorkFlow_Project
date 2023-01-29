let IFRAME_LOADED = false;
let CLIENT_IFRAME = document.getElementById("proxy-iframe");
let WAITING_LOGO_LOADER = document.getElementById("easyassist-client-page-loader");
let ACTIVE_TAB_CLIENT_PAGE_ID = null;
let CLIENT_TAB_MANAGER_INSTANCE = null;
let client_show_focus_toast_timeout = null;

/*
This will handle all the window.open() calls which are being done
in the clients js files. The below code would open the URL in the 
current iframe.
*/
window.open = function (open) {
    return function (url, name, features) {
        let new_proxy_url = `${window.easychat_host_url}/easy-assist/cognoai-cobrowse/page-render/${window.proxy_key}/${url}`;
        CLIENT_IFRAME.src = new_proxy_url;
    };
}(window.open);

function show_loader() {
    WAITING_LOGO_LOADER.style.display = "flex";
}

function hide_loader() {
    WAITING_LOGO_LOADER.style.display = "none";
}

function resize_iframe() {
    let height_vh = window.innerHeight * (100 / document.documentElement.clientHeight);
    let width_vw = window.innerWidth * (100 / document.documentElement.clientWidth);
    if (height_vh > 100) {
        height_vh = 100;
    }
    if (width_vw > 100) {
        width_vw = 100;
    }
    CLIENT_IFRAME.style.width = width_vw + "vw";
    CLIENT_IFRAME.style.height = height_vh + "vh";
}

/*
Used for disabling opening of new tab using ctrl + click or shift + click
*/
function disable_new_tab_on_click() {
    let elements = CLIENT_IFRAME.contentWindow.document.getElementsByTagName('a');
    for (let i = 0; i < elements.length; i++) {
        elements[i].onclick = function(event) {
            if (!event) event = window.event;
            if (event.ctrlKey || event.shiftKey) {
                event.preventDefault();
                open_url_in_current_iframe(event);
                return;
            }
            if (event.shiftKey && event.ctrlKey) {
                event.preventDefault();
                open_url_in_current_iframe(event);
                return;
            }
        }
    }
}

function open_url_in_current_iframe(event) {
    if(event && event.target && event.target.href) {
        CLIENT_IFRAME.src = event.target.href;
    }
}

function initialize_new_tab_opening_interceptor() {
    disable_new_tab_on_click();
}

function load_iframe() {
    let url = ""

    url = `${window.easychat_host_url}/easy-assist/cognoai-cobrowse/page-render/${window.proxy_key}/${window.proxy_active_url}`;

    try {
        let local_storage_obj = get_easyassist_proxy_local_storage_obj();

        if(local_storage_obj && local_storage_obj["active_url"]) {
                url = local_storage_obj["active_url"];
        }
    } catch(err) {
        console.log(err)
    }

    if (CLIENT_IFRAME.getAttribute('src') == "") {
        try {
            CLIENT_IFRAME.src = url;
        } catch (error) {
            location = location.href;
        }
        CLIENT_IFRAME.onload = function () {
            hide_loader();
            IFRAME_LOADED = true;
            resize_iframe();
            initialize_new_tab_opening_interceptor();
        }
    }
}

show_loader();
window.onload = function () {
    load_iframe();
    resize_iframe();
}

window.onresize = function () {
    resize_iframe();
}

window.onbeforeunload = function(event){
    set_easyassist_proxy_session_local_storage(window.proxy_key, document.getElementById("proxy-iframe").contentWindow.location.href);
    return;
};


function get_easyassist_proxy_local_storage_obj() {
    let local_storage_obj = null;

    if (localStorage.getItem("easyassist_session") != null) {
        local_storage_obj = localStorage.getItem("easyassist_session");
        let session_id = get_easyassist_cookie("easyassist_session_id");
        local_storage_obj = JSON.parse(local_storage_obj);
        if (local_storage_obj.hasOwnProperty(session_id)) {
            local_storage_obj = local_storage_obj[session_id];
            if(local_storage_obj[window.proxy_key]) {
                local_storage_obj = local_storage_obj[window.proxy_key];
            }
        }
    }
    return local_storage_obj;
}

function set_easyassist_proxy_session_local_storage(key, value) {
    try {
        let local_storage_obj = localStorage.getItem("easyassist_session");
        let proxy_local_obj = {}
        let session_id = get_easyassist_cookie("easyassist_session_id");
        if (local_storage_obj) {
            local_storage_obj = JSON.parse(local_storage_obj);
            proxy_local_obj["active_url"] = value
            local_storage_obj[session_id][key] = proxy_local_obj;
            localStorage.setItem("easyassist_session", JSON.stringify(local_storage_obj));
        }
    } catch (err) {
        console.log("ERROR: set_easyassist_current_session_local_storage_obj ", err);
    }
}