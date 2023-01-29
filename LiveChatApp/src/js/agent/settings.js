import { is_mobile, EncryptVariable, custom_decrypt } from "../utils";
import { showToast, get_assigned_customer_count, get_current_status, getCsrfToken} from "./console";

const state = {
    submit_mark_user_offline: false,
    options_list: [],
    check_list: [],
    checked_items: new Set(),
    selected: [],
};

(function ($) {
    $(function () {
        if(String(window.location.href).includes('agent-settings') && window.IS_VIRTUAL_INTERPRETATION_ENABLED == "True"){
            state.options_list = document.querySelectorAll(".option");
            state.check_list = document.querySelectorAll(".item-checkbox");
            state.selected = document.querySelector(".selected");
            initialize_mail_tags();
        }

    }); // end of document ready
})(jQuery); // end of jQuery name space

function open_profile_page() {
    if (is_mobile()) {
        try {
            document.getElementById("live-chat-setting-menu").style.display = "none";
            document.getElementById("live-chat-setting-content-p").style.display = "block";
        } catch (err) {
            localStorage.setItem("open_profile", true);
            window.location = "/livechat/agent-profile/";
        }
    } else {
        window.location = "/livechat/agent-profile/";
    }
}

/* Agent Online/Offline starts */

function check_and_mark_online() {
    let curent_status = get_current_status();
    if ((curent_status == "6" || curent_status == "7") && !state.submit_mark_user_offline) {
        document.getElementById("offline-to-online-agent-switch").checked = true;
    }
}

$(document).on("change", "#offline-to-online-agent-switch", function () {
    var status = document.getElementById("offline-to-online-agent-switch").checked;
    if (status) {
        add_entry_to_audit_trail(status, "6");
    } else {
        check_customer_count();
        $("#modal-agent-current-status").modal("show");
    }
});

function mark_user_offline() {
    let selected_status = $("#select-status-agent").val();
    add_entry_to_audit_trail(false, selected_status);
    state.submit_mark_user_offline = true;
    document.getElementById("offline-to-online-agent-switch").checked = false;
    $("#modal-agent-current-status").modal("hide");
}

function mark_user_online() {
    document.getElementById("offline-to-online-agent-switch").checked = true;
    $("#modal-agent-current-status").modal("hide");
}

function add_entry_to_audit_trail(status, selected_status) {
    let json_string = JSON.stringify({
        pk: USER_PK,
        status: status,
        selected_status: selected_status,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/switch-agent-status/", false);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token); 
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {
                showToast(response["message"], 5000);
                setTimeout(function () {
                    window.location.reload();
                }, 2000);
            } else {
                showToast("Can't switch due to some internal error.", 5000);
            }
        }
    };
    xhttp.send(params);
}

function show_offline_reasons_modal() {
    let assigned_customers;
    try {
        assigned_customers = get_assigned_customer_count();
    } catch (err) {
        assigned_customers = localStorage.getItem("assigned_customer_count");
    }
    if (assigned_customers == undefined) assigned_customers = 0;
    if (assigned_customers == 0) {
        check_customer_count();
        $("#modal-agent-current-status").modal("show");
    } else {
        showToast("Kindly resolve the remaining chats.", 2000);
        return;
    }
}

/* Agent Online/Offline ends */

function save_agent_settings() {
    var notification = document.getElementById("is-livechat-notification-enabled").checked;
    const preferred_languages = []

    if(window.IS_VIRTUAL_INTERPRETATION_ENABLED == "True") {
        const selected_language_list = $('#select-prefered-languages-dropdown').find("option:selected");
        
        Array.from(selected_language_list).forEach(lang => {
            preferred_languages.push(lang.value);
        })

        if (!preferred_languages.includes("en")) {
            preferred_languages.push("en");
        }
    }

    var json_string = JSON.stringify({
        notification: notification,
        preferred_languages: preferred_languages
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/save-agent-general-settings/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            showToast("Changes Saved successfully!", 5000);
            setTimeout(()=>{location.reload();}, 2000);
        }
    };
    xhttp.send(params);
}

function check_customer_count() {
    let assigned_customers = get_assigned_customer_count();

    if (!assigned_customers) assigned_customers = localStorage.getItem("assigned_customer_count");

    if (!assigned_customers) assigned_customers = 0;

    $("#select-status-agent").html("");
    let option;
    if (assigned_customers == 0) {
        option = new Option("Lunch", "1", true, false);
        $("#select-status-agent").append(option).trigger("change");

        option = new Option("Coffee", "2", true, false);
        $("#select-status-agent").append(option).trigger("change");

        option = new Option("Adhoc", "3", true, false);
        $("#select-status-agent").append(option).trigger("change");

        option = new Option("Meeting", "4", true, false);
        $("#select-status-agent").append(option).trigger("change");

        option = new Option("Training", "5", true, false);
        $("#select-status-agent").append(option).trigger("change");
    } else {
        option = new Option("Stop Interaction", "0", true, false);
        $("#select-status-agent").append(option).trigger("change");
    }
}

function go_back_mobile() {
    document.getElementById("live-chat-setting-menu").style.display = "block";
    document.getElementById("live-chat-setting-menu").style.visibility = "visible";
    try {
        document.getElementById("live-chat-setting-content").style.display = "none";
    } catch (e) {}

    try {
        document.getElementById("live-chat-setting-content-p").style.display = "none";
    } catch (e) {}

    try {
        document.getElementById("live-chat-setting-content-c").style.display = "none";
    } catch (e) {}

    try {
        document.getElementById("live-chat-setting-content-cr").style.display = "none";
    } catch (e) {}

    try {
        document.getElementById("live-chat-setting-content-gs").style.display = "none";
    } catch (e) {}
}


function initialize_mail_tags() {

    document.getElementById("myCheckEnglish").checked = true;
    let dropdown = document.querySelector(".wrapper-box");
    let optionsContainer = document.querySelector(".multiselect-options-container");
    let searchBox = document.querySelector(".search-box input");
    const dropArrow = document.querySelector(".language-arrow");

    let count = 0;
    makeCheckArray();
    applyCross();
    let open = false;
    dropdown.addEventListener("click", () => {
        open = !open;
        optionsContainer.classList.toggle("active");
        if (open) {
            // selected.innerHTML = "Select Language";
            state.selected.style.border = "none";
            dropArrow.style.transform = "translateY(-50%) rotate(180deg)";
        } else {
            dropArrow.style.transform = "translateY(-50%) rotate(0deg)";
            makeCheckArray();
            state.selected.innerHTML = "";
            let flag = 1;
            count = 0;
            for (let item of state.checked_items) {
                flag = 0;
                makeSpans(item);
            }
            if (flag == 1)
                state.selected.innerHTML = "Select Language";

        }

        searchBox.value = "";
        filterList("");
        if (optionsContainer.classList.contains("active")) searchBox.focus();

    });
    searchBox.addEventListener("keyup", function(e) {
        filterList(e.target.value);
    });   
}

function applyCross() {

    document.querySelectorAll(".cross-btn").forEach((eachCrossBtn) => {
        eachCrossBtn.addEventListener("click", (e) => {

            if(e.target.id == "English") {
                showToast("Default language cannot be removed", 2000);
                return;  
            }

            e.stopPropagation();
            if (document.querySelector(`._${e.target.id}`))
                document.querySelector(`._${e.target.id}`).remove();
            state.checked_items.delete(`${e.target.id}`);
            document.getElementById(`myCheck${e.target.id}`).checked = false;
            document.getElementById(`myCheckEnglish`).checked = true;

            if (state.checked_items.size === 0)
                state.selected.innerHTML = "Select Language";
        })
    })
}

function filterList(searchTerm) {
    searchTerm = searchTerm.toLowerCase();
    let flag = 0;
    document.querySelector(".no-elem").style.display = "none";
    state.options_list.forEach((option) => {
        let label =
            option.firstElementChild.nextElementSibling.innerText.toLowerCase();
        if (label.indexOf(searchTerm) != -1) {
            flag = 1;
            option.style.display = "block";
        } else {
            option.style.display = "none";
        }
    });
    if (flag === 0) document.querySelector(".no-elem").style.display = "block";
}

function makeCheckArray() {
    state.check_list.forEach(c => {
        if (c.checked == true)
            state.checked_items.add(c.getAttribute("name"));
        else
            state.checked_items.delete(c.getAttribute("name"));
    })
}

function makeSpans(text) {
    var span = document.createElement("SPAN");
    span.innerHTML = `<span>${text}</span><svg width="13" id='${text}' class="cross-btn" height="8" viewBox="0 0 7 8" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M6.65011 0.854978C6.55669 0.761352 6.42987 0.708735 6.29761 0.708735C6.16535 0.708735 6.03852 0.761352 5.94511 0.854978L3.50011 3.29498L1.05511 0.849978C0.961692 0.756352 0.834866 0.703735 0.702607 0.703735C0.570349 0.703735 0.443523 0.756352 0.350107 0.849978C0.155107 1.04498 0.155107 1.35998 0.350107 1.55498L2.79511 3.99998L0.350107 6.44498C0.155107 6.63998 0.155107 6.95498 0.350107 7.14998C0.545107 7.34498 0.860107 7.34498 1.05511 7.14998L3.50011 4.70498L5.94511 7.14998C6.14011 7.34498 6.45511 7.34498 6.65011 7.14998C6.84511 6.95498 6.84511 6.63998 6.65011 6.44498L4.20511 3.99998L6.65011 1.55498C6.84011 1.36498 6.84011 1.04498 6.65011 0.854978Z" fill="${window.LIVECHAT_THEME_COLOR}"/></svg>`;
    span.classList.add("tag", `_${text}`);
    state.selected.appendChild(span);
    applyCross();
}

function hideIcon(self) {
    self.style.backgroundImage = 'none';
}

function remove_selected_language_agent_settings(event, el, id) {
    event.stopPropagation();
    if (id.toLowerCase().trim() == "english-en") {
        alert("Default language cannot be removed")
        return
    }
}

export {
    open_profile_page,
    mark_user_offline,
    show_offline_reasons_modal,
    save_agent_settings,
    go_back_mobile,
    mark_user_online,
    check_and_mark_online,
    remove_selected_language_agent_settings,
};
