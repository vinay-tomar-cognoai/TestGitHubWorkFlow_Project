var obfuscated_fields = window.EASYASSIST_COBROWSE_META.obfuscated_fields;

window.EASYASSIST_HTML_ID_TO_REMOVE = [
    "easyassist-agent-information-modal",
    "easyassist-livechat-iframe",
    "easyassist-sidenav-menu-id",
    "easyassist-ripple_effect",
    "easyassist-co-browsing-modal-id",
    "easyassist-product-category-modal-id",
    "easychat_share_link_Model",
    "easyassist-side-nav-options-co-browsing",
    "easyassist-co-browsing-request-assist-modal",
    "easyassist-co-browsing-request-meeting-modal",
    "easyassist-voip-video-calling-request-modal",
    "easyassist-voip-calling-request-modal",
    "easyassist_agent_joining_modal",
    "agent-mouse-pointer",
    "easyassist-snackbar",
    "easyassist-co-browsing-feedback-modal",
    "easyassist-conection-modal-id",
    "easyassist-co-browsing-request-edit-access",
    "easyassist-co-browsing-payment-consent-modal",
    "easyassist-tooltip",
    "cobrowse-mobile-modal",
    "easyassist-cobrowse-voip-container",
    "easyassist-agent-disconnected-modal",
    "easyassist-agent-weak-internet-connection-modal",
    "easyassist-client-weak-internet-connection-modal",
    "easyassist-co-browsing-edit-access-info-modal",
    "easyassist_function_fail_modal",
    "easyassist-non-working-hours-modal-id",
    "easyassist-drawing-canvas",
    "easyassist-connection-timer-modal-id",
    "easyassist-minimized-connection-timer-modal-id",
    "easyassist_agent_connect_modal",
    "easyassist_agent_connect_video_call_modal",
    "chat-minimize-icon-wrapper",
    "cobrowse-mobile-navbar",
];

function easyassist_apply_custom_select(document_select_tag_list) {

    if(EASYASSIST_COBROWSE_META.enable_custom_cobrowse_dropdown == false) {
        return;
    }

    for (let d_index = 0; d_index < document_select_tag_list.length; d_index++) {
        var s_element = document_select_tag_list[d_index];

        if(easyassist_check_element_is_hidden(s_element)) {
            continue;
        }

        if(easyassist_custom_select_remove_check(s_element)) {
            continue;
        }

        var obfuscated_field = easyassist_obfuscated_element_check(s_element);
        new EasyassistCustomSelect2(s_element, null, null, obfuscated_field);
    }
}

function easyassist_custom_select_remove_check(element) {

    try {
        for (let index = 0; index < custom_select_removed_fields.length; index++) {
            let element_value = element.getAttribute(custom_select_removed_fields[index]["key"]);
            if (element_value != null && element_value != undefined && element_value == custom_select_removed_fields[index]["value"]) {
                return true;
            }
        }
        return false;
    } catch(err) {
        return false;
    }
}

function easyassist_obfuscate(str, masking_type) {
    if (masking_type == null || masking_type == undefined) {
        masking_type = EASYASSIST_COBROWSE_META.masking_type;
    }

    if (masking_type == "partial-masking") {
        var start = 0;
        var mid = Math.round(str.length / 2);
        return str.substring(start, mid + 1).replace(/[a-zA-Z0-9@.]/g, 'X') + str.substring(mid + 1, );
    }
    if (masking_type == "full-masking") {
        return str.length <= 10 ? str.replace(/[a-zA-Z0-9@.]/g, 'X') : "XXXXXXXXXX";
    }
    return str;
}

function easyassist_obfuscate_data_using_recursion(element) {
    if (!element.children.length) {
        if (element.id == "easy_assist_pdf_render_current_page"){
            return;
        }
        element.innerHTML = easyassist_obfuscate(element.innerHTML);
        return;
    }

    for (let index = 0; index < element.children.length; index++) {
        easyassist_obfuscate_data_using_recursion(element.children[index]);
    }

    var child_objects = element.children;

    var inner_text = element.innerText;
    if (inner_text.length > 0 && inner_text[0] != 'X') {

        element.innerHTML = "XXXXXXXXXX";
        for (let index = 0; index < child_objects.length; index++) {
            element.appendChild(child_objects[index]);
        }
    }
}

function easyassist_obfuscated_element_check(element) {
    try {
        var masking_type = element.getAttribute("easyassist-obfuscate");
        if(masking_type && (masking_type == "partial-masking" || masking_type == "full-masking")) {
            return [true, masking_type];
        }
    } catch(err) {
        console.log("easyassist_obfuscated_element_check: ", err);
    }

    return [false, ""];
}

function easyassist_check_element_is_hidden(element) {
    var element_computed_style = getComputedStyle(element);
    if(element_computed_style.display == "none") {
        return true;
    }

    if(element_computed_style.visibility == "hidden") {
        return true;
    }

    try {
        if(element.offsetWidth <= 2 || element.offsetHeight <= 2) {
            return true;
        }

        var client_rect = element.getClientRects()
        if(client_rect.length == 0) {
            return true;
        }
    } catch(err) {
        console.log("ERROR: ", err);
    }

    if(element.offsetParent == null) {
        return true;
    }
    return false;
}

function add_easyassist_event_listner_into_element(html_element, event_type, target_function){
    html_element.removeEventListener(event_type, target_function);
    html_element.addEventListener(event_type, target_function);
}

function remove_easyassist_event_listner_into_element(html_element, event_type, target_function){
    html_element.removeEventListener(event_type, target_function);
}

function easyassist_check_cobrowsing_active() {
    // if(EasyAssistSyncIframe.easyassist_check_in_iframe()) {
    //     return true;
    // }

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return false;
    }
    return true;
}

function easyassist_check_cobrowsing_allowed() {

    var allow_cobrowsing = get_easyassist_cookie("easyassist_cobrowsing_allowed") == "true" ? true : false;

    if (allow_cobrowsing == false) {
        return false;
    }
    return true;
}

function easyassist_check_edit_access_enabled() {

    if (get_easyassist_cookie("easyassist_edit_access") == "true") {
        return true;
    }
    return false;
}

function easyassist_check_weak_connection_enabled() {
    var low_bandwidth_cobrowsing_enabled = EASYASSIST_COBROWSE_META.enable_low_bandwidth_cobrowsing;
    var agent_weak_connected_detected = EasyAssistLowBandWidthHTML.get_agent_weak_connection_value();

    if(low_bandwidth_cobrowsing_enabled && agent_weak_connected_detected) {
        return true;
    }
    return false;
}

function easyassist_check_screensharing_enabled() {
    if(EASYASSIST_COBROWSE_META.allow_screen_sharing_cobrowse) {
        return true;
    }
    return false;
}

function easyassist_screenshot_page() {

    easyassist_create_value_attr_into_document();

    if(easyassist_check_weak_connection_enabled()) {
        return EasyAssistLowBandWidthHTML.get_screenshot();
    }
}

function easyassist_masked_field_attr_set() {
    try {
        for(let mask_index = 0; mask_index < obfuscated_fields.length; mask_index++) {
            var query = '[' + obfuscated_fields[mask_index]['key'] + '="' + obfuscated_fields[mask_index]['value'] + '"]';
            var obfuscated_elements = document.querySelectorAll(query);
            for(let index = 0; index < obfuscated_elements.length; index++) {
                obfuscated_elements[index].setAttribute("easyassist-obfuscate", obfuscated_fields[mask_index]['masking_type']);
                easyassist_add_warning_element(obfuscated_elements[index]);
            }
        }
    } catch(err) {
        console.log("easyassist_masked_field_attr_set: ", err);
    }
}

function easyassist_add_warning_element(reference_node){
    if(reference_node == null || reference_node == undefined) {
        return;
    }

    add_easyassist_event_listner_into_element(reference_node, 'focusin', easyassist_display_masked_field_warning);
    add_easyassist_event_listner_into_element(reference_node, 'focusout', easyassist_remove_masked_field_warning);
}

/******************************* Custom EasyAssist Utils Functions *******************************************/

function easyassist_add_masked_field_tooltip(){
    var warning = document.createElement("span");
    warning.innerHTML = EASYASSIST_COBROWSE_META.masked_field_warning_text;
    warning.setAttribute("class", "easyassist-tooltiptext");
    warning.setAttribute("id", "easyassist-tooltip");
    warning.style.cursor = "default";
    warning.style.fontSize = "11px";
    warning.style.display = "none";
    document.getElementsByTagName("body")[0].appendChild(warning);
}

function easyassist_display_masked_field_warning(event){
    element = event.target;
    var dimensions = element.getBoundingClientRect();
    var warning_element =  easyassist_get_eles_by_class_name("easyassist-tooltiptext", document)[0];
    if(warning_element == null || warning_element == undefined) {
        return;
    }
    warning_element.style.visibility = "visible";
    warning_element.style.opacity = "1";
    warning_element.style.left = dimensions.left.toString() + "px";
    // warning_element.style.left = (dimensions.left + element.offsetWidth/2 + window.pageXOffset - warning_element.offsetWidth/2) + "px";
    warning_element.style.top = (dimensions.top - warning_element.offsetHeight + window.pageYOffset - 6) + "px";
}

function easyassist_remove_masked_field_warning(){
    easyassist_get_eles_by_class_name("easyassist-tooltiptext", document)[0].style.visibility = "hidden";
    easyassist_get_eles_by_class_name("easyassist-tooltiptext", document)[0].style.opacity = "0";
}

function easyassist_check_dom_node(element) {
    try {
        if(element.nodeType == Node.TEXT_NODE) {
            if(element.parentNode && element.parentNode.getAttribute("easyassist_avoid_sync")) {
                return true;
            }
            return false;
        }

        if(!element.getAttribute) {
            return false;
        }

        if(element.getAttribute("easyassist_avoid_sync")) {
            return true;
        }

        var is_element_to_remove = false;
        for(let idx = 0; idx < EASYASSIST_HTML_ID_TO_REMOVE.length; idx ++) {
            if(element.id == EASYASSIST_HTML_ID_TO_REMOVE[idx]) {
                is_element_to_remove = true;
                break;
            }
        }
        return is_element_to_remove;
    } catch(err) {
        console.log("easyassist_check_dom_node: ", err);
        return false;
    }
}

function easyassist_add_avoid_sync_class() {
    try {

        var html_element_stack = [];
        for(let idx = 0; idx < EASYASSIST_HTML_ID_TO_REMOVE.length; idx ++) {
            var element_id = EASYASSIST_HTML_ID_TO_REMOVE[idx];
            var element = document.getElementById(element_id);
            if(element) {
                html_element_stack.push(element);
            }
        }

        while(html_element_stack.length) {
            var current_element = html_element_stack.pop();
            current_element.setAttribute("easyassist_avoid_sync", "true");
            var current_element_children = current_element.children;

            for(let idx = 0; idx < current_element_children.length; idx ++) {
                html_element_stack.push(current_element_children[idx]);
            }
        }
    } catch(err) {
        console.log("easyassist_add_avoid_sync_class: ", err);
    }
}

function easyassist_set_event_listeners() {
    EasyAssistSyncHTML.set_element_event_listener();
}

const EasyAssistLowBandWidthHTML = (function() {
    var AGENT_WEAK_CONNECTION_DETECTED = null;
    var tags_to_consider = ["input", "select", "textarea", "button"];
    var total_low_bandwidth_elements = 0;
    var easyassist_element_id_counter = 0;

    function set_agent_weak_connection_value(value) {
        AGENT_WEAK_CONNECTION_DETECTED = value;
    }

    function get_agent_weak_connection_value() {
        return AGENT_WEAK_CONNECTION_DETECTED;
    }

    function get_hash_for_dom_node() {
        easyassist_element_id_counter += 1;
        return easyassist_element_id_counter;
    }

    function get_label_from_child_elements(parent_element) {
        var element_label = "";
        var special_char_text = ["abbr", "i", "span"];

        var child_nodes = parent_element.childNodes;
        for(let idx = 0; idx < child_nodes.length; idx ++) {
            if(child_nodes[idx].nodeType == Node.TEXT_NODE) {
                element_label += child_nodes[idx].textContent.trim();
            } else if(child_nodes[idx].nodeType == Node.ELEMENT_NODE) {
                var child_tag_name = child_nodes[idx].tagName.toLowerCase();
                if(special_char_text.indexOf(child_tag_name) > -1 && child_nodes[idx].children.length == 0) {
                    element_label += child_nodes[idx].textContent.trim();
                }
            }
        }
        return element_label;
    }

    function get_form_element_label(element) {
        if(element.parentElement.className == "easyassist-custom-dropdown-container2") {
            element = element.parentElement;
        }

        var parent_element = element.parentElement;
        var element_label = "";
        var level = 5;

        var element_text_not_consider = ["select", "li", "ul", "input", "button", "textarea", "script"];

        while(level > 0) {
            if(parent_element.tagName == "BODY") {
                break;
            }

            let parent_element_children = parent_element.children;
            for(let idx = 0; idx < parent_element_children.length; idx ++) {
                var child_tag_name = parent_element_children[idx].tagName.toLowerCase();
                if(element_text_not_consider.indexOf(child_tag_name) == -1) {
                    element_label += get_label_from_child_elements(parent_element_children[idx]);
                }
            }

            if(element_label) {
                break;
            } else {
                parent_element = parent_element.parentElement;
            }
            level --;
        }

        if(!element_label) {
            element_label = (element.getAttribute("placeholder") || "").trim();
        }

        if(!element_label && element.tagName == "SELECT" && element.options.length > 0) {
            let option_value = (element.options[0].value || "").trim();
            if(option_value == "") {
                element_label = element.options[0].innerText;
            }
        }

        if(!element_label && element.classList.contains("easyassist-custom-dropdown-container2")) {
            // Get label from select element if easyassist custom select is enabled
            var select_element = element.querySelector("select");
            if(select_element.options.length > 0) {
                let option_value = (select_element.options[0].value || "").trim();
                if(option_value == "") {
                    element_label = select_element.options[0].innerText;
                }    
            }
        }

        if(!element_label) {
            level = 3;
            while(level > -1) {
                if(element.tagName == "BODY") {
                    break;
                }
                let parent_element_children = element.parentElement.children;
                for(let idx = 0; idx < parent_element_children.length; idx ++) {
                    if(parent_element_children[idx] == element) {
                        continue;
                    } else {
                        let child_tag_name = parent_element_children[idx].tagName.toLowerCase();
                        if(element_text_not_consider.indexOf(child_tag_name) == -1) {
                            let parent_element_text = (parent_element_children[idx].innerText || "").trim();
                            if(parent_element_text.length <= 100) {
                                element_label += parent_element_text;
                            }
                        }
                    }

                    if(element_label) break;
                }

                element = element.parentElement;
                level --;

                if(element_label) {
                    break;
                }
            }
        }
        return element_label;
    }

    function get_low_bandwidth_html() {

        var html_element_list = get_form_elements();
        var visited_tag_map = {};

        total_low_bandwidth_elements = get_total_form_element_count(html_element_list);
        var html_data = "";

        for(let idx = html_element_list.length - 1; idx >= 0; idx --) {
            var child_element = html_element_list[idx];
            var child_element_tag = child_element.tagName.toLowerCase();
            var child_element_type = child_element.getAttribute("type");
            var child_element_name = child_element.getAttribute("name");
    
            if(child_element_type == "radio" && child_element_name && (child_element_name in visited_tag_map)) {
                continue;
            }
    
            var easyassist_element_id = get_hash_for_dom_node();
            child_element.setAttribute("easyassist-element-id", easyassist_element_id);
    
            if(child_element_tag == "button" || child_element_type == "button" || child_element_type == "submit") {
                 html_data += [
                    '<tr>',
                        '<td colspan="2" style="text-align: center;">' + child_element.outerHTML + '</td>',
                    '</tr>',
                ].join('');
            } else if(child_element_type == "radio") {
    
                visited_tag_map[child_element_name] = true;
                var radio_elements = document.querySelectorAll("[name='" + child_element_name + "']");
                var radio_html = "";
                var radio_label = get_form_element_label(child_element.parentElement);
                for(let radio_index = 0; radio_index < radio_elements.length; radio_index ++) {
                    var child_label = "";
    
                    easyassist_element_id = get_hash_for_dom_node();
                    radio_elements[radio_index].setAttribute("easyassist-element-id", easyassist_element_id);
    
                    if(radio_elements[radio_index].id) {
                        var radio_element_id = radio_elements[radio_index].id;
                        var radio_element_label = document.querySelector("[for='" + radio_element_id + "']");
                        if(radio_element_label) {
                            child_label = radio_element_label.textContent.trim();
                        }
                    }
    
                    if(!child_label) {
                        var radio_parent_element = radio_elements[radio_index].parentElement;
                        for(let index = 0; index < radio_parent_element.childNodes.length; index ++) {
                            if(radio_parent_element.childNodes[index] == radio_elements[idx]) {
                                continue;
                            }
                            child_label += radio_parent_element.childNodes[index].textContent.trim();
                        }
                    }
    
                    radio_html += [
                        '<div>',
                            radio_elements[radio_index].outerHTML,
                            child_label,
                        '</div>',
                    ].join('');
                }
    
                if(radio_label[0] == "*") {
                    radio_label = '<sup>*</sup>' + radio_label.substr(1);
                }
                html_data += [
                    '<tr>',
                        '<td>' + radio_label + '</td>',
                        '<td>' + radio_html + '</td>',
                    '</tr>',
                ].join('');
            } else {
                let child_label = get_form_element_label(child_element);
                if(child_label.length > -1) {
                    if(child_label[0] == "*") {
                        child_label = '<sup>*</sup>' + child_label.substr(1);
                    } else if(child_label[child_label.length - 1] == "*") {
                        child_label = child_label.slice(0, -1) + "<sup>*</sup>";
                    }
                }
                html_data += [
                    '<tr>',
                        '<td>' + child_label + '</td>',
                        '<td>' + child_element.outerHTML + '</td>',
                    '</tr>',
                ].join('');
            }
        }

        if(html_data == "") {

            let document_p_tag_list = document.getElementsByTagName("p");
            for(let idx = 0; idx < document_p_tag_list.length; idx ++) {
                if(easyassist_check_dom_node(document_p_tag_list[idx])) {
                    continue;
                }
                html_data += document_p_tag_list[idx].outerHTML;
            }

        } else {
            html_data = [
                '<div style="width: 100%; display: flex; justify-content: center;">',
                    '<table>',
                        '<tbody>',
                            html_data,
                        '</tbody>',
                    '</table>',
                '</div>',
            ].join('');
        }

        return html_data;
    }

    function get_total_form_element_count(html_element_list=null) {

        if(html_element_list == null) {
            html_element_list = get_input_elements();
        }

        var total_elements = html_element_list.length;
        for(let idx = 0; idx < html_element_list.length; idx ++) {
            if(html_element_list[idx].tagName == "SELECT") {
                total_elements += html_element_list[idx].children.length;
            }
        }

        return total_elements;
    }

    function get_form_elements() {
        var html_element_list = [];
        var html_element_stack = [document.body];
    
        while(html_element_stack.length) {
            var current_element = html_element_stack.pop();

            if(easyassist_check_dom_node(current_element)) {
                continue;
            }

            var current_element_children = current_element.children;
    
            for(let idx = 0; idx < current_element_children.length; idx ++) {
    
                var child_element = current_element_children[idx];
                var child_element_tag = child_element.tagName.toLowerCase();
                var child_element_type = child_element.getAttribute("type");

                if(check_form_element_is_hidden(child_element)) {
                    if(child_element_tag == "input") {
                        if(child_element_type != "checkbox" && child_element_type != "radio") {
                            continue;
                        }
                    } else if(child_element.parentElement.className != "easyassist-custom-dropdown-container2") {
                        continue;
                    }
                }

                if(child_element_type == "hidden") {
                    continue;
                }

                html_element_stack.push(child_element);
    
                if(tags_to_consider.indexOf(child_element_tag) > -1) {
                    if(child_element_tag == "button") {
                        if((child_element.innerText || "").trim()) {
                            html_element_list.push(child_element);
                        }
                    } else {
                        html_element_list.push(child_element);
                    }
                }
            }
        }
        return html_element_list;
    }

    function check_form_element_is_hidden(element) {
        var element_computed_style = getComputedStyle(element);
        if(element_computed_style.display == "none") {
            return true;
        }

        if(element_computed_style.visibility == "hidden") {
            return true;
        }

        return false;
    }

    function check_form_element_changed() {
        var total_elements = get_total_form_element_count();
        if(total_elements != total_low_bandwidth_elements) {
            return true;
        }
        return false;
    }

    function get_screenshot() {
        let html_data = get_low_bandwidth_html();

        let screenshot = document.documentElement.cloneNode(false);
        screenshot = document.documentElement.cloneNode(true);
        let screenshot_links = screenshot.querySelectorAll("link");
        for(let idx = 0; idx < screenshot_links.length; idx ++) {
            screenshot_links[idx].parentNode.removeChild(screenshot_links[idx]);
        }

        let screenshot_scripts = screenshot.querySelectorAll("script");
        for (let index = 0; index < screenshot_scripts.length; index++) {
            screenshot_scripts[index].parentNode.removeChild(screenshot_scripts[index]);
        }

        let screenshot_body = screenshot.querySelector("body");
        screenshot_body.innerHTML = html_data;
        screenshot_body.style.backgroundColor = easyassist_find_light_color_by_opacity(EASYASSIST_COBROWSE_META.floating_button_bg_color, 0.03);

        let css = document.createElement("link");
        css.type = 'text/css';
        css.rel = "stylesheet";
        css.setAttribute("class", "easyassist-client-script");
        css.href = EASYASSIST_HOST_PROTOCOL + '://' + EASYASSIST_COBROWSE_HOST + '/static/EasyAssistApp/css/low_bandwidth_cobrowse.css';
        screenshot.getElementsByTagName('head')[0].appendChild(css);

        // easyassist_set_value_attr_into_screenshot(screenshot);

        let outerhtml = screenshot.outerHTML;
        if(document.compatMode == "CSS1Compat") {
            outerhtml = "<!DOCTYPE HTML>\n" + outerhtml;
        }
        outerhtml = outerhtml.replace(/\s+/g, " ");

        return outerhtml;
    }
  
    return {
        get_screenshot: get_screenshot,
        check_form_element_changed: check_form_element_changed,
        get_agent_weak_connection_value: get_agent_weak_connection_value,
        set_agent_weak_connection_value: set_agent_weak_connection_value,
    };
})();

function easyassist_create_value_attr_into_document() {

    easyassist_masked_field_attr_set();

    let document_input_tag_list = document.querySelectorAll("input");

    for (let d_index = 0; d_index < document_input_tag_list.length; d_index++) {

        add_easyassist_event_listner_into_element(document_input_tag_list[d_index], "change", easyassist_sync_html_element_value_change)

        let is_numeric = false;
        if (isNaN(Number(document_input_tag_list[d_index].value)) == false) {
            is_numeric = true;
        }

        var attr_type = document_input_tag_list[d_index].getAttribute("type");

        let is_active_element = false;
        if (document.activeElement == document_input_tag_list[d_index]) {
            is_active_element = true;
        }
        if (attr_type == "button" || attr_type == "submit") {
            document_input_tag_list[d_index].classList.add("easyassist-click-element");
        }

        let is_obfuscated_element = easyassist_obfuscated_element_check(document_input_tag_list[d_index]);

        if(is_obfuscated_element[0])
            easyassist_add_warning_element(document_input_tag_list[d_index]);

        document_input_tag_list[d_index].removeAttribute("easyassist-active");
        if (is_active_element) {
            document_input_tag_list[d_index].setAttribute("easyassist-active", "true");
        }

        let value = document_input_tag_list[d_index].value;

        if (attr_type == "checkbox" || attr_type == "radio") {
            if (document_input_tag_list[d_index].checked) {
                document_input_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, "checked");
            } else {
                document_input_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, "unchecked");
            }
        } else if (is_obfuscated_element[0]) {
            document_input_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, easyassist_obfuscate(value, is_obfuscated_element[1]));
        } else if (is_numeric) {
            document_input_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, easyassist_obfuscate(value));
        } else if (document_input_tag_list[d_index].getAttribute("easyassist-masked") == "true") {
            document_input_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, easyassist_obfuscate(value));
        } else if (document_input_tag_list[d_index].getAttribute("type") == "password") {
            document_input_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, easyassist_obfuscate(value));
        } else if (document_input_tag_list[d_index].getAttribute("type") == "file" && EASYASSIST_COBROWSE_META.allow_file_verification) {
            add_easyassist_event_listner_into_element(document_input_tag_list[d_index], "change", easyassist_send_attachment_to_agent_for_validation)
        } else {
            document_input_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, value);
        }
    }

    let document_textarea_tag_list = document.querySelectorAll("textarea");
    for (let d_index = 0; d_index < document_textarea_tag_list.length; d_index++) {
        add_easyassist_event_listner_into_element(document_textarea_tag_list[d_index], "scroll", easyassist_sync_scroll_position_inside_div);
        let is_active_element = false;
        if (document.activeElement == document_textarea_tag_list[d_index]) {
            is_active_element = true;
        }

        document_textarea_tag_list[d_index].removeAttribute("easyassist-active");
        if (is_active_element) {
            document_textarea_tag_list[d_index].setAttribute("easyassist-active", "true");
        }

        let is_numeric = false;
        if (isNaN(Number(document_textarea_tag_list[d_index].value)) == false) {
            is_numeric = true;
        }

        let is_obfuscated_element = easyassist_obfuscated_element_check(document_textarea_tag_list[d_index]);
        if (is_obfuscated_element[0]) {
            document_textarea_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, easyassist_obfuscate(document_textarea_tag_list[d_index].value, is_obfuscated_element[1]));
            easyassist_add_warning_element(document_textarea_tag_list[d_index]);
        } else if (is_numeric) {
            document_textarea_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, easyassist_obfuscate(document_textarea_tag_list[d_index].value));
        } else {
            document_textarea_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, document_textarea_tag_list[d_index].value);
        }
    }

    let document_select_tag_list = document.querySelectorAll("select");

    easyassist_apply_custom_select(document_select_tag_list);
    for (let d_index = 0; d_index < document_select_tag_list.length; d_index++) {
        add_easyassist_event_listner_into_element(document_select_tag_list[d_index], "change", easyassist_sync_html_element_value_change);

        let is_active_element = false;
        if (document.activeElement == document_select_tag_list[d_index]) {
            is_active_element = true;
        }

        document_select_tag_list[d_index].removeAttribute("easyassist-active");
        if (is_active_element) {
            document_select_tag_list[d_index].setAttribute("easyassist-active", "true");
        }

        let is_obfuscated_element = easyassist_obfuscated_element_check(document_select_tag_list[d_index]);

        var selected_option = document_select_tag_list[d_index].options[document_select_tag_list[d_index].selectedIndex];
        if (selected_option != null && selected_option != undefined) {
            var selected_option_inner_html = selected_option.innerHTML;
            let selected_option_value = selected_option.value;
            if (is_obfuscated_element[0] == false) {
                document_select_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, selected_option_inner_html);
            } else {
                document_select_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, easyassist_obfuscate(selected_option_inner_html, is_obfuscated_element[1]));
            }
        }
        if(is_obfuscated_element[0])
            easyassist_add_warning_element(document_select_tag_list[d_index]);
    }

    let document_table_tag_list = document.querySelectorAll("table");
    for (let d_index = 0; d_index < document_table_tag_list.length; d_index++) {

        let is_obfuscated_element = false;
        for (let mask_index = 0; mask_index < obfuscated_fields.length; mask_index++) {
            element_value = document_table_tag_list[d_index].getAttribute(obfuscated_fields[mask_index]["key"]);
            if (element_value != null && element_value != undefined && element_value == obfuscated_fields[mask_index]["value"]) {
                is_obfuscated_element = true;
                break;
            }
        }

        if (!is_obfuscated_element) {

            continue;
        }
        for (let row_index = 0; row_index < document_table_tag_list[d_index].tBodies[0].rows.length; row_index++) {

            for (let col_index = 0; col_index < document_table_tag_list[d_index].tBodies[0].rows[row_index].children.length; col_index++) {

                var table_element = document_table_tag_list[d_index].tBodies[0].rows[row_index].children[col_index];
                add_easyassist_event_listner_into_element(table_element, "change", easyassist_sync_html_element_value_change)
            }
        }
        if(is_obfuscated_element)
            easyassist_add_warning_element(document_table_tag_list[d_index]);
    }

    let document_a_tag_list = document.querySelectorAll("a");
    for (let index = 0; index < document_a_tag_list.length; index++) {
        document_a_tag_list[index].classList.add("easyassist-click-element");
    }

    let document_button_tag_list = document.querySelectorAll("button");
    for (let index = 0; index < document_button_tag_list.length; index++) {
        document_button_tag_list[index].classList.add("easyassist-click-element");
    }
}

function easyassist_set_value_attr_into_screenshot(screenshot) {
    let screenshot_input_tag_list = screenshot.querySelectorAll("input");
    for (let s_index = 0; s_index < screenshot_input_tag_list.length; s_index++) {
        let attr_type = screenshot_input_tag_list[s_index].getAttribute("type");
        let easyassist_tag_value = screenshot_input_tag_list[s_index].getAttribute(EASYASSIST_TAG_VALUE);
        if (attr_type == "checkbox" || attr_type == "radio") {
            screenshot_input_tag_list[s_index].removeAttribute("checked");
            if (easyassist_tag_value == "checked") {
                screenshot_input_tag_list[s_index].setAttribute("checked", "checked");
            }
        } else {
            screenshot_input_tag_list[s_index].setAttribute("value", easyassist_tag_value);
            screenshot_input_tag_list[s_index].value = easyassist_tag_value;
        }
        screenshot_input_tag_list[s_index].removeAttribute(EASYASSIST_TAG_VALUE);
    }

    let screenshot_textarea_tag_list = screenshot.querySelectorAll("textarea");
    for (let s_index = 0; s_index < screenshot_textarea_tag_list.length; s_index++) {
        let easyassist_tag_value = screenshot_textarea_tag_list[s_index].getAttribute(EASYASSIST_TAG_VALUE);
        screenshot_textarea_tag_list[s_index].value = easyassist_tag_value;
        screenshot_textarea_tag_list[s_index].innerHTML = easyassist_tag_value;
        screenshot_textarea_tag_list[s_index].removeAttribute(EASYASSIST_TAG_VALUE);
    }

    let screenshot_select_tag_list = screenshot.querySelectorAll("select");
    for (let s_index = 0; s_index < screenshot_select_tag_list.length; s_index++) {
        let easyassist_tag_value = screenshot_select_tag_list[s_index].getAttribute(EASYASSIST_TAG_VALUE);
        screenshot_select_tag_list[s_index].setAttribute("value", easyassist_tag_value);
        screenshot_select_tag_list[s_index].removeAttribute(EASYASSIST_TAG_VALUE);

        if (easyassist_tag_value && easyassist_tag_value.indexOf("XXXXX") > -1) {
            easyassist_tag_value = "******";
            var obfuscated_option = document.createElement("option");
            obfuscated_option.value = easyassist_tag_value
            obfuscated_option.innerHTML = easyassist_tag_value;
            screenshot_select_tag_list[s_index].appendChild(obfuscated_option);
        }

        for (let option_index = 0; option_index < screenshot_select_tag_list[s_index].options.length; option_index++) {
            screenshot_select_tag_list[s_index].options[option_index].removeAttribute("selected");
            if (screenshot_select_tag_list[s_index].options[option_index].innerHTML == easyassist_tag_value) {
                screenshot_select_tag_list[s_index].options[option_index].setAttribute("selected", "selected");
            }
        }
        
    }

    let screenshot_table_tag_list = screenshot.querySelectorAll("table");

    for (let d_index = 0; d_index < screenshot_table_tag_list.length; d_index++) {

        let is_obfuscated_element = easyassist_obfuscated_element_check(screenshot_table_tag_list[s_index]);
        if (!is_obfuscated_element[0]) {
            continue;
        }

        var rows = screenshot_table_tag_list[d_index].tBodies[0].rows;
        for (let row_index = 0; row_index < rows.length; row_index++) {
            var table_columns = rows[row_index].children;

            for (let col_index = 0; col_index < table_columns.length; col_index++) {
                var table_element = table_columns[col_index];
                easyassist_obfuscate_data_using_recursion(table_element);
            }
        }
    }

    let screenshot_label_tag_list = screenshot.querySelectorAll("label");
    for (let d_index = 0; d_index < screenshot_label_tag_list.length; d_index++) {
        let label_id = screenshot_label_tag_list[d_index].getAttribute("id");
        if (label_id == null || label_id == undefined) {
            continue;
        }
        
        let is_obfuscated_element = easyassist_obfuscated_element_check(screenshot_label_tag_list[d_index]);
        if (!is_obfuscated_element[0]) {

            continue;
        }
        screenshot_label_tag_list[d_index].innerHTML = easyassist_obfuscate(screenshot_label_tag_list[d_index].innerHTML);
    }

    let screenshot_li_tag_list = screenshot.querySelectorAll("li");
    for (let d_index = 0; d_index < screenshot_li_tag_list.length; d_index++) {

        let li_id = screenshot_li_tag_list[d_index].getAttribute("id");
        if (li_id == null || li_id == undefined) {
            continue;
        }

        if (!easyassist_obfuscated_element_check(screenshot_li_tag_list[d_index])[0]) {

            continue;
        }
        screenshot_li_tag_list[d_index].innerHTML = easyassist_obfuscate(screenshot_li_tag_list[d_index].innerHTML);
    }

    let screenshot_p_tag_list = screenshot.querySelectorAll("p");

    for (let p_index = 0; p_index < screenshot_p_tag_list.length; p_index++) {
        let is_obfuscated_element = false;
        for (let mask_index = 0; mask_index < obfuscated_fields.length; mask_index++) {
            let element_value = screenshot_p_tag_list[p_index].getAttribute(obfuscated_fields[mask_index]["key"]);
            if (element_value != null && element_value != undefined && element_value == obfuscated_fields[mask_index]["value"]) {
                is_obfuscated_element = true;
                break;
            }
        }

        if (is_obfuscated_element) {
            screenshot_p_tag_list[p_index].innerHTML = "XXXXXXXXXXXXX";
        }

    }


    let screenshot_div_tag_list = screenshot.querySelectorAll("div");

    for (let div_index = 0; div_index < screenshot_div_tag_list.length; div_index++) {
        screenshot_div_tag_list[div_index].onscroll = easyassist_sync_mouse_position
        let is_obfuscated_element = false;
        for (let mask_index = 0; mask_index < obfuscated_fields.length; mask_index++) {
            let element_value = screenshot_div_tag_list[div_index].getAttribute(obfuscated_fields[mask_index]["key"]);
            if (element_value != null && element_value != undefined && element_value == obfuscated_fields[mask_index]["value"]) {
                is_obfuscated_element = true;
                break;
            }
        }

        if (is_obfuscated_element) {
            screenshot_div_tag_list[div_index].innerHTML = "XXXXXXXXXXXXX";
        }

    }

    let document_span_tag_list = screenshot.querySelectorAll("span");
    for (let d_index = 0; d_index < document_span_tag_list.length; d_index++) {
        let is_obfuscated_element = easyassist_obfuscated_element_check(document_span_tag_list[d_index]);
        if (is_obfuscated_element[0]) {
            easyassist_tag_value = document_span_tag_list[d_index].getAttribute(EASYASSIST_TAG_VALUE);
            document_span_tag_list[d_index].innerHTML = easyassist_tag_value;
            document_span_tag_list[d_index].removeAttribute(EASYASSIST_TAG_VALUE);
        }
        if(document_span_tag_list[d_index].className == "easyassist-tooltiptext")
            document_span_tag_list[d_index].style.display = "none";
    }

    let screenshot_custom_select_elements = screenshot.querySelectorAll(".easyassist-dropdown-selected2")
    for (let index = 0; index < screenshot_custom_select_elements.length; index++) {
        is_obfuscated = easyassist_obfuscated_element_check(screenshot_custom_select_elements[index]);
        if(is_obfuscated[0])
            screenshot_custom_select_elements[index].innerText = easyassist_obfuscate(screenshot_custom_select_elements[index].innerText, is_obfuscated[1]);
    }

    let screenshot_custom_select_li_item = screenshot.querySelector(".easyassist-custom-dropdown-option-container2")
    if(screenshot_custom_select_li_item) {
        is_obfuscated = easyassist_obfuscated_element_check(screenshot_custom_select_li_item);
        if(is_obfuscated[0])
            easyassist_obfuscate_data_using_recursion(screenshot_custom_select_li_item);
    }

    let screenshot_input_number = screenshot.querySelectorAll("input[type=number]")
    screenshot_input_number.forEach(element => {
        element.type = 'text';
    });
}

const EasyAssistSyncIframe = (function() {
    var js_file_list = [
        "easyassist_tree_mirror.js",
        "easyassist_mutation_summary.js",
        "easyassist_client_iframe.js",
        "easyassist_custom_select2.js",
    ];

    if(EASYASSIST_COBROWSE_META.is_min_file) {
        js_file_list = [
            "easyassist_tree_mirror.min.js",
            "easyassist_mutation_summary.js",
            "easyassist_client_iframe.min.js",
            "easyassist_custom_select2.js",
        ]
    }

    var css_file_list = [
        "easyassist_custom_select2.css",
    ]

    var easyassist_iframe_id_counter = 0;

    function easyassist_check_in_iframe() {
        try {
            // return window.self !== window.top;
            return window.parent.location !== window.location;
        } catch (e) {
            return true;
        }
    }

    function easyasist_iframe_cobrowsing_enabled() {
        if(EASYASSIST_COBROWSE_META.enable_iframe_cobrowsing == true) {
            return true;
        }
        return false;
    }

    function easyassist_get_iframe_id() {
        easyassist_iframe_id_counter += 1;
        return easyassist_iframe_id_counter;
    }

    function easyassist_add_iframe_script(iframe, sync_html_on_load=false) {
        function easyassist_pass_parent_members_to_iframe() {
            iframe.contentWindow['EASYASSIST_COBROWSE_META'] = EASYASSIST_COBROWSE_META;
            iframe.contentWindow['get_easyassist_cookie'] = get_easyassist_cookie;
            iframe.contentWindow['AUTO_SYNC_HTML_ON_LOAD'] = sync_html_on_load;
            iframe.contentWindow['easyassist_get_eles_by_class_name'] = easyassist_get_eles_by_class_name;
        }

        try {
            var iframe_doc = iframe.contentDocument;
            if(iframe_doc == null) {
                console.log("Iframe is blocked");
                return;
            }

            easyassist_pass_parent_members_to_iframe();

            var scripts = iframe_doc.querySelectorAll(".easyassist-client-script");
            if(scripts.length) {
                return;
            }

            js_file_list.forEach(function(file_name) {
                var script = iframe_doc.createElement('script');
                script.type = 'text/javascript';
                script.defer = true;
                script.setAttribute("class", "easyassist-client-script");

                var script_origin = EASYASSIST_HOST_PROTOCOL + '://' + EASYASSIST_COBROWSE_HOST;
                if(EASYASSIST_COBROWSE_META.DEVELOPMENT || file_name == "easyassist_mutation_summary.js") {
                    script.src = script_origin + '/static/EasyAssistApp/js/' + file_name;
                } else {
                    script.src = script_origin + '/static/EasyAssistApp/js/' + EASYASSIST_COBROWSE_META.access_token + "/" + file_name;
                }
                iframe_doc.body.appendChild(script);
            });


            css_file_list.forEach(function(file_name) {
                var css = iframe_doc.createElement("link");
                css.type = 'text/css';
                css.rel = "stylesheet";
                css.setAttribute("class", "easyassist-client-script");

                var script_origin = EASYASSIST_HOST_PROTOCOL + '://' + EASYASSIST_COBROWSE_HOST;
                if(EASYASSIST_COBROWSE_META.DEVELOPMENT) {
                    css.href = script_origin + '/static/EasyAssistApp/css/' + file_name;
                } else {
                    css.href = script_origin + '/static/EasyAssistApp/css/' + EASYASSIST_COBROWSE_META.access_token + "/" + file_name;
                }
                iframe_doc.body.appendChild(css);
            });
        } catch(err) {
            console.log("easyassist_add_iframe_script: ", err);
        }
    }

    function easyassist_trigger_iframe_mouse_event(iframe, e) {
        var evt = document.createEvent("MouseEvents");
        var boundingClientRect = iframe.getBoundingClientRect();
        evt.initMouseEvent(
            "mousemove",
            true,
            false,
            window,
            e.detail,
            e.screenX,
            e.screenY,
            e.clientX + boundingClientRect.left,
            e.clientY + boundingClientRect.top,
            e.ctrlKey,
            e.altKey,
            e.shiftKey,
            e.metaKey,
            e.button,
            null
        );
        iframe.dispatchEvent(evt);
    }

    function easyassist_add_iframe_event_listener() {
        try {
            if(!easyassist_check_in_iframe()) {
                return;
            }

            window.onmousemove = function(e) {
                var iframe = window.frameElement;
                easyassist_trigger_iframe_mouse_event(iframe, e);
            };
            window.onclick = easyassist_send_data_to_server;
            window.onmousedown = easyassist_send_data_to_server;
            window.onkeyup = easyassist_send_data_to_server;

            // window.onresize = easyassist_send_data_to_server;
            window.onscroll = easyassist_send_data_to_server;
        } catch(err) {
            console.log("easyassist_add_iframe_event_listener: ", err);
        }
    }

    function easyassist_set_iframe() {
        try {
            if(!easyasist_iframe_cobrowsing_enabled()) {
                return;
            }

            var iframes = document.querySelectorAll("iframe");
            for(let idx = 0; idx < iframes.length; idx ++) {
                if(easyassist_check_dom_node(iframes[idx])) {
                    continue;
                }

                if(iframes[idx].getAttribute("easyassist-iframe-id")) {
                   continue; 
                }

                easyassist_add_iframe_script(iframes[idx]);
                iframes[idx].addEventListener("load", function(event) {
                    let iframe = event.target;
                    easyassist_add_iframe_script(iframe, true);
                });

                let easyassist_iframe_id = easyassist_get_iframe_id();
                iframes[idx].setAttribute("easyassist-iframe-id", easyassist_iframe_id);
            }
        } catch(err) {
            console.log("easyassist_set_iframe: ", err);
        }
    }

    function easyassist_parent_message_handler(event) {
        if(!easyasist_iframe_cobrowsing_enabled()) {
            return;
        }

        // Iframe listens to parent messages
        if(event.data == "easyassist_sync_html") {
            easyassist_sync_html_data();

        } else if(event.data.type == "sync-form") {
            easyassist_agent_sync_form(event.data.data);

        } else if(event.data.type == "button-click") {
            easyassist_sync_button_click_event(event.data.data);

        } else if(event.data.type == "div-scroll") {
            easyassist_sync_agent_div_scroll(event.data.data);

        }
    }

    function easyassist_iframe_message_handler(event) {
        if(!easyasist_iframe_cobrowsing_enabled()) {
            return;
        }

        // Parent listen to iframe messages
        var data_packet = event.data;
        if(data_packet == null) {
            return;
        }

        easyassist_send_data_over_socket(data_packet);
    }

    function easyassist_add_parent_message_listener() {
        if(!easyasist_iframe_cobrowsing_enabled()) {
            return;
        }

        if(!easyassist_check_in_iframe()) {
            return;
        }

        window.addEventListener("message", easyassist_parent_message_handler);
    }

    function easyassist_add_iframe_message_listener() {
        if(!easyasist_iframe_cobrowsing_enabled()) {
            return;
        }

        if(easyassist_check_in_iframe()) {
            return;
        }

        window.addEventListener("message", easyassist_iframe_message_handler);
    }

    function easyassist_sync_data_packet(data_packet, use_sync_utils_ws=false) {
        try {
            var easyassist_iframe_id = easyassist_get_current_iframe_id();
            data_packet["easyassist_iframe_id"] = easyassist_iframe_id;

            var json_data = {
                "use_sync_utils_ws": use_sync_utils_ws,
                "data": data_packet,
            };

            if(easyassist_check_in_iframe()) {
                window.parent.postMessage(json_data, "*");
            } else {
                easyassist_send_data_over_socket(json_data);
            }
        } catch(err) {
            console.log("easyassist_sync_data_packet: ", err);
        }
    }

    function easyassist_get_current_iframe_id() {
        var easyassist_iframe_id = null;
        if(easyassist_check_in_iframe()) {
            var iframe = window.frameElement;
            if(iframe) {
                easyassist_iframe_id = iframe.getAttribute("easyassist-iframe-id");
            }
        }

        return easyassist_iframe_id;
    }

    function easyassist_sync_all_iframes() {
        try {
            if(EASYASSIST_COBROWSE_META.enable_iframe_cobrowsing == false) {
                return;
            }

            var iframes = document.querySelectorAll("iframe");
            for(let idx = 0; idx < iframes.length; idx ++) {
                if(easyassist_check_dom_node(iframes[idx])) {
                    continue;
                }

                iframes[idx].contentWindow.postMessage("easyassist_sync_html", "*");
            }
        } catch(err) {
            console.log("easyassist_set_iframe: ", err);
        }
    }

    easyassist_add_parent_message_listener();
    easyassist_add_iframe_message_listener();
    easyassist_add_iframe_event_listener();

    return {
        easyassist_set_iframe: easyassist_set_iframe,
        easyassist_check_in_iframe: easyassist_check_in_iframe,
        easyassist_sync_data_packet: easyassist_sync_data_packet,
        easyassist_sync_all_iframes: easyassist_sync_all_iframes,
    }
})();

function easyassist_send_data_over_socket(json_data) {

    var data_packet = JSON.stringify(json_data.data);
    if(!data_packet) {
        return;
    }
    var encrypted_data = easyassist_custom_encrypt(data_packet);
    encrypted_data = {
        "Request": encrypted_data
    };

    if(json_data.use_sync_utils_ws) {
        easyassist_send_message_over_sync_utils_socket(encrypted_data, "client");
    } else {
        easyassist_send_message_over_socket(encrypted_data, "client");
    }
}

const EasyAssistSyncHTML = function() {
    var easyassist_tree_mirror_client = null;
    var easyassist_auto_change_event_timeout = null;
    var easyassist_auto_change_event_time = null;

    var EASYASSIST_ATTACH_EVENT_LISTENERS = {
        "INPUT": function(element) {

            if (element.getAttribute("type") == "file" && EASYASSIST_COBROWSE_META.allow_file_verification) {
                add_easyassist_event_listner_into_element(element, "change", easyassist_send_attachment_to_agent_for_validation)
            } else {
                add_easyassist_event_listner_into_element(element, "change", easyassist_sync_html_element_value_change)
            }
        },

        "SELECT": function(element) {

            easyassist_apply_custom_select([element]);
            add_easyassist_event_listner_into_element(element, "change", easyassist_sync_html_element_value_change);
        },

        "TEXTAREA": function(element) {
            add_easyassist_event_listner_into_element(element, "scroll", easyassist_sync_scroll_position_inside_div);
        },
    };

    function set_element_event_listener(elements = null) {
        if(elements == null) {
            elements = document.getElementsByTagName("*");
        }

        easyassist_masked_field_attr_set();

        for(let idx = 0; idx < elements.length; idx ++) {
            var tag_name = elements[idx].tagName;
    
            if(tag_name in EASYASSIST_ATTACH_EVENT_LISTENERS) {
                EASYASSIST_ATTACH_EVENT_LISTENERS[tag_name](elements[idx]);
            }
    
            add_easyassist_event_listner_into_element(elements[idx], "scroll", easyassist_sync_scroll_position_inside_div);
        }
    }

    function easyassist_special_event_listner() {
        try {
            var inputs = document.querySelectorAll("input");
            for(let idx = 0; idx < inputs.length; idx ++) {
                const input = inputs[idx];
                const input_type = input.getAttribute("type");
                const descriptor = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(input), 'value');

                if(input_type == "hidden" || input_type == "button" || input_type == "submit") {
                    continue;
                }

                try {
                    Object.defineProperty(input, 'value', {
                        set: function(t) {
                            var current_time = Date.now();
                            if(easyassist_auto_change_event_timeout != null && current_time - easyassist_auto_change_event_time <= 200) {
                                clearTimeout(easyassist_auto_change_event_timeout);
                            }

                            if(input.has_easyassist_change_event != false) {
                                easyassist_auto_change_event_timeout = setTimeout(function() {
                                    easyassist_sync_html_element_value_change();
                                }, 200);
                            }

                            easyassist_auto_change_event_time = Date.now();
                            return descriptor.set.apply(this, arguments);
                        },
                        get: function() {
                            return descriptor.get.apply(this);
                        }
                    });
                } catch(err) {}
            }
        } catch(err) {
            console.log("easyassist_special_event_listner: ", err);
        }
    }

    function easyassist_get_css_from_stylesheet() {
        var css_text = "";
        try {
            if(EASYASSIST_COBROWSE_META.enable_cobrowsing_on_react_website == false) {
                return css_text;
            }
    
            var css = "";
            var style_elements_list = document.querySelectorAll("style[data-styled]");
            var style_elements = [];
            for(let idx = 0; idx < style_elements_list.length; idx ++) {
                style_elements.push(style_elements_list[idx]);
            }
    
            var inline_styles = document.querySelectorAll("style");
    
            for(let idx = 0; idx < inline_styles.length; idx ++) {
                if(inline_styles[idx] && inline_styles[idx].innerText) {
                    if(inline_styles[idx].innerText.trim() == "") {
                        style_elements.push(inline_styles[idx]);
                    }
                }
            }
    
            for (let idx = 0; idx < style_elements.length; idx ++) {
                var sheet = style_elements[idx].sheet;
                var rules = ('cssRules' in sheet)? sheet.cssRules : sheet.rules;
                if(!rules) {
                    continue;
                }
                for (let rule_idx = 0; rule_idx < rules.length; rule_idx ++) {
                    var rule = rules[rule_idx];
    
                    if ('cssText' in rule) {
                        css += rule.cssText;
                    } else {
                        css += rule.selectorText + '{'+rule.style.cssText+'}'
                    }
                }
            }
            css_text = css;
        } catch(err) {
            console.log("easyassist_get_css_from_stylesheet: ", err);
        }
        return css_text;
    }

    function easyassist_get_input_element_value(element, is_capture_screenshot_callback=false) {
        var element_value = [null, null];
        try {
            var tag_name = element.tagName;
            let is_obfuscated_element = easyassist_obfuscated_element_check(element);
            if(tag_name != "INPUT" && tag_name != "SELECT" && tag_name != "TEXTAREA" && !(is_capture_screenshot_callback && is_obfuscated_element[0])) {
                return element_value;
            }

            var current_element_value = null;

            if(element.tagName == "INPUT") {
                var element_type = element.getAttribute("type");
                if(element_type == "button" || element_type == "submit") {
                    return element_value;
                }

                if(element_type == "checkbox" || element_type == "radio") {
                    current_element_value = element.checked;
                } else {
                    current_element_value = element.value;
                }
            } else if(element.tagName == "SELECT") {
                current_element_value = element.value;
            } else if(element.tagName == "TEXTAREA") {
                current_element_value = element.value;
            } else if (is_obfuscated_element[0] && is_capture_screenshot_callback) {
                current_element_value = element.textContent;
            }
            
            let original_element_value = current_element_value;
            let is_numeric = false;
            if (is_obfuscated_element[0] == false && isNaN(Number(current_element_value.toString())) == false) {
                is_numeric = true;
            }

            if (is_obfuscated_element[0]) {
                current_element_value = easyassist_obfuscate(current_element_value.toString(), is_obfuscated_element[1].toString());
            }
            if(is_numeric) {
                current_element_value = easyassist_obfuscate(current_element_value.toString());
            }
            
            if (element.id == "easy_assist_pdf_render_current_page") {
                element_value = [false, original_element_value]
            } else{
                element_value = [is_obfuscated_element[0], current_element_value];
            }
        } catch(err) {
            console.log(err);
        }
        return element_value;
    }

    function easyassist_set_input_element_value(screenshot, is_capture_screenshot_callback=false) {

        try {

            var element_list = screenshot.getElementsByTagName("*")
            for(let idx = 0; idx < element_list.length; idx ++) {

                var active_element = element_list[idx];

                var element_value = easyassist_get_input_element_value(active_element, is_capture_screenshot_callback=is_capture_screenshot_callback);

                var tag_name = active_element.tagName;
                var tag_type = active_element.getAttribute("type");

                if(element_value == null || (element_value.length != 2) || (element_value[1] == null)) {
                    continue;
                }

                let is_obfuscated_element = element_value[0];
                var new_value = element_value[1];

                if(tag_type == "number") {
                    active_element.type = "text";
                } else if(tag_type == "date" && is_obfuscated_element == true){
                    active_element.type = "text";
                }

                if(tag_name == "INPUT") {
                    if(tag_type == "checkbox" || tag_type == "radio") {
                        if(new_value == true) {
                            active_element.setAttribute("checked", "checked");
                        } else {
                            active_element.removeAttribute("checked");
                        }
                    } else {
                        active_element.setAttribute("value", new_value);
                        active_element.value = new_value;
                    }
                } else if(tag_name == "SELECT") {
                    if(is_obfuscated_element) {
                        var option = '<option value="' + new_value + '">' + new_value + ' </option>';
                        active_element.innerHTML += option;
                    }

                    for(let index = 0; index < active_element.options.length; index ++) {
                        active_element.options[index].removeAttribute("selected");
                        if (active_element.options[index].value == element_value) {
                            active_element.options[index].setAttribute("selected", "selected");
                        }
                    }

                } else if(tag_name == "TEXTAREA") {
                    active_element.value = new_value;
                    active_element.innerHTML = new_value;
                }  else if(is_obfuscated_element && is_capture_screenshot_callback) {
                    active_element.textContent = new_value;
                }
            }
        } catch(err) {
            console.log("easyassist_set_input_element_value: ", err);
        }
    }

    function easyassist_sync_change_data(action, func_name, change_data, props) {
        var data_packet = {
            type: action,
            f: func_name,
            args: change_data,
            props: props
        };
        EasyAssistSyncIframe.easyassist_sync_data_packet(data_packet);
    }

    function easyassist_sync_html() {

        try {
            set_element_event_listener();

            easyassist_disconnect_tree_mirror();

            try {
                easyassist_special_event_listner();
            } catch(err) {
                console.log("ERROR: ", err);
            }
    
            let css_text = easyassist_get_css_from_stylesheet();
    
            easyassist_tree_mirror_client = new EasyAssistTreeMirrorClient(document, {
                initialize: function(rootId, children) {
                    var action = "html_initialize";
                    var change_data = [rootId, children];
                    var func_name = "initialize";

                    let base_href = location.href.match(/^(.*\/)[^\/]*$/)[1];
                    let base_element = document.querySelector("base");
                    if(base_element) {
                        base_href = base_element.href;
                    }

                    var props = {
                        base: base_href,
                        scrollX: window.scrollX,
                        scrollY: window.scrollY,
                        window_width: window.innerWidth,
                        window_height: window.innerHeight,
                        css_text: css_text,
                    }

                    easyassist_sync_change_data(action, func_name, change_data, props);
                },
    
                applyChanged: function(removed, addedOrMoved, attributes, text) {
                    if(!(removed.length || addedOrMoved.length || attributes.length || text.length)) {
                        return;
                    }
    
                    let css_text = easyassist_get_css_from_stylesheet();
    
                    var action = "html_change";
                    var func_name = "applyChanged";
                    var change_data = [removed, addedOrMoved, attributes, text];
                    var props = {
                        base: location.href.match(/^(.*\/)[^\/]*$/)[1],
                        css_text: css_text,
                    }

                    easyassist_sync_change_data(action, func_name, change_data, props);
                },
    
                check_dom_node: function(element) {
                    return easyassist_check_dom_node(element);
                },

                obfuscate_text_node: function(node) {
                    let textContent = node.textContent;
                    try{
                        let parent_masked_ele = node.parentElement.closest("[easyassist-obfuscate]")
                        if(parent_masked_ele){
                            textContent = easyassist_obfuscate(
                                            node.textContent,
                                            parent_masked_ele.getAttribute("easyassist-obfuscate")
                                        );
                        }
                    }catch(err){}
                    return textContent;
                },
    
                get_element_value: easyassist_get_input_element_value,
          });
        } catch(err) {
            console.log("easyassist_sync_html_data_utils: ", err);
        }
    }

    function get_tree_mirror_client() {
        return easyassist_tree_mirror_client;
    }

    function reset_tree_mirror_client() {
        easyassist_tree_mirror_client = null;
    }

    function easyassist_disconnect_tree_mirror() {
        try {
            if(easyassist_tree_mirror_client != null) {
                easyassist_tree_mirror_client.disconnect();
                easyassist_tree_mirror_client = null;
            }
        } catch(err) {
            console.log("easyassist_disconnect_tree_mirror: ", err);
        }
    }

    function get_element_from_id(element_id) {
        var element = null;

        try {
            element = easyassist_tree_mirror_client.knownNodes.nodes[element_id];
        } catch(err) {
            console.log("get_element_from_id: ", err);
        }

        return element;
    }

    function get_id_from_element(element) {
        var element_id = null;

        try {
            if(easyassist_tree_mirror_client != null) {
                element_id = easyassist_tree_mirror_client.knownNodes.get(element);
            }
        } catch(err) {
            console.log("get_id_from_element: ", err);
        }

        return element_id;
    }

    function easyassist_is_invalid(node){
        var easyassist_element_id = node.__mutation_summary_node_map_id__;
        var mutation_id = easyassist_tree_mirror_client.knownNodes.get(node)
        // var element = easyassist_tree_mirror.idMap[easyassist_element_id];
        if(easyassist_element_id != mutation_id){
            console.log("---------------------------------");
            console.log("node = ", node);
            console.log("easyassist_element_id = ", easyassist_element_id);
            console.log("mutation_id = ", mutation_id);
        }
        return easyassist_element_id != mutation_id;
    }

    function easyassist_is_map_invalid(node=null){
        if(node==null){
            var doc_html = document.documentElement;
            node=doc_html;
        }

        if(easyassist_check_dom_node(node) == true) return false;

        var flag = easyassist_is_invalid(node);
        for(let index=0 ; index<node.children.length ; index++){
            flag |= easyassist_is_map_invalid(node.children[index]);
        }

        return flag;
    }

    return {
        get_id_from_element: get_id_from_element,
        get_element_from_id: get_element_from_id,
        easyassist_sync_html: easyassist_sync_html,
        get_tree_mirror_client: get_tree_mirror_client,
        reset_tree_mirror_client: reset_tree_mirror_client,
        easyassist_is_map_invalid: easyassist_is_map_invalid,
        set_element_event_listener: set_element_event_listener,
        easyassist_disconnect_tree_mirror: easyassist_disconnect_tree_mirror,
        easyassist_set_input_element_value: easyassist_set_input_element_value,
    };
}();

function easyassist_disconnect_mutation_summary_client() {
    try {
        EasyAssistSyncHTML.easyassist_disconnect_tree_mirror();
    } catch(err) {
        console.log("easyassist_disconnect_mutation_summary_client: ", err);
    }
}

function easyassist_send_data_to_server(event) {
    try {
        if(event.type == "click") {

            if(easyassist_check_weak_connection_enabled()) {
                setTimeout(function() {
                    if(EasyAssistLowBandWidthHTML.check_form_element_changed()) {
                        easyassist_sync_html_data();
                    }
                }, 1000);
            } else {
                easyassist_set_event_listeners();
            }

        } else if (event.type == "scroll") {

            easyassist_sync_scroll_position();

        } else if (event.type == "resize") {

            easyassist_sync_client_screen_dimension();
            easyassist_resize_easyassist_canvas();
            easyassist_relocate_drag_element();

        } else {

            let tag_name = document.activeElement.tagName.toLowerCase();
            if(tag_name == "iframe") {
                tag_name = event.target.tagName.toLowerCase();
            }

            if (tag_name == "input") {
                easyassist_sync_html_element_value_change();
            } else if (tag_name == "select") {
                easyassist_sync_html_element_value_change();
            } else if (tag_name == "textarea") {
                easyassist_sync_html_element_value_change();
            } else {
                //console.log("active element tag: ", tag_name);
            }
        }

        if(event.target.id == "easyassist-ripple_effect") {
            easyassist_hide_ripple_effect();
        }
    } catch(err) {
        console.log("easyassist_send_data_to_server: ", err);
    }
}

function easyassist_get_element_from_easyassist_id(element_id) {
    var element = null;

    try {
        if(easyassist_check_weak_connection_enabled()) {
            element = document.querySelector("[easyassist-element-id='" + element_id + "']");
        } else {
            element = EasyAssistSyncHTML.get_element_from_id(element_id);
        }
    } catch(err) {
        console.log("easyassist_get_element_from_easyassist_id: ", err);
    }

    return element;
}

function easyassist_get_easyassist_id_from_element(element) {
    var element_id = null;

    try {
        if(easyassist_check_weak_connection_enabled()) {
            element_id = element.getAttribute("easyassist-element-id");
        } else {
            element_id = EasyAssistSyncHTML.get_id_from_element(element);
        }
    } catch(err) {
        console.log("easyassist_get_easyassist_id_from_element: ", err);
    }

    return element_id;
}

function easyassist_sync_html_data() {
    try {
        if(easyassist_check_screensharing_enabled()) {
            return;
        }

        if(!easyassist_check_cobrowsing_active() || !easyassist_check_cobrowsing_allowed()) {
            return;
        }

        EasyAssistSyncIframe.easyassist_set_iframe();

        if(easyassist_check_weak_connection_enabled()) {

            easyassist_send_weak_connection_html();

        } else {
            EasyAssistSyncHTML.easyassist_sync_html();
        }

    } catch(err) {
        console.log("easyassist_sync_html_data: ", err);
    }
}

function easyassist_send_weak_connection_html() {
    try {
        easyassist_disconnect_mutation_summary_client();

        var screenshot = easyassist_screenshot_page();

        let json_string = JSON.stringify({
            "type": "html",
            "window_width": window.innerWidth,
            "window_height": window.innerHeight,
            "page": html_page_counter,
            "is_chunk": false,
            "html": screenshot,
            "id": EASYASSIST_SESSION_ID,
            "active_url": window.location.href
        });

        let is_encrypted = false;
        let encrypted_data = json_string;

        if (is_encrypted == true) {
            encrypted_data = easyassist_custom_encrypt(json_string);
        }

        encrypted_data = {
            "is_encrypted": is_encrypted,
            "html_page_counter": html_page_counter,
            "Request": encrypted_data
        };

        easyassist_send_message_over_socket(encrypted_data, "client");

        html_page_counter += 1;

    } catch(err) {
        console.log("easyassist_send_weak_connection_html: ", err);
    }
}

function easyassist_sync_html_element_value_change() {

    try {
        if(!easyassist_check_cobrowsing_active() || !easyassist_check_cobrowsing_allowed()) {
            return;
        }

        var active_element = document.activeElement;
        let tag_name_list = ["input", "select", "textarea"];

        var html_elements_value_list = [];

        for (let tag_index = 0; tag_index < tag_name_list.length; tag_index++) {

            let tag_elements = document.getElementsByTagName(tag_name_list[tag_index]);

            for (let tag_element_index = 0; tag_element_index < tag_elements.length; tag_element_index++) {

                tag_name = tag_elements[tag_element_index].tagName;
                let element_id = easyassist_get_easyassist_id_from_element(tag_elements[tag_element_index]);

                if(element_id == null || element_id == undefined) {
                    continue;
                }

                let tag_type = tag_elements[tag_element_index].getAttribute("type");
                let value = tag_elements[tag_element_index].value;

                if(tag_name.toLowerCase() != "select" && tag_type != 'checkbox' && tag_type != 'radio') {
                    if (tag_elements[tag_element_index].offsetParent == null) {
                        continue;
                    }
                }

                if (tag_name.toLowerCase() == "select") {
                    var selected_option = tag_elements[tag_element_index].options[tag_elements[tag_element_index].selectedIndex];
                    if (selected_option != null && selected_option != undefined) {
                        var selected_option_inner_html = selected_option.innerHTML;
                        let selected_option_value = selected_option.value;
                        value = selected_option_inner_html;
                    }
                } else if (tag_name.toLowerCase() == "label") {
                    let label_id = tag_elements[tag_element_index].getAttribute("id");
                    if (label_id == undefined || label_id == null) {
                        continue
                    }

                    value = tag_elements[tag_element_index].innerHTML;
                } else if (tag_name.toLowerCase() == "span") {
                    let span_id = tag_elements[tag_element_index].getAttribute("id");
                    if (span_id == undefined || span_id == null) {
                        continue
                    }

                    value = tag_elements[tag_element_index].innerHTML;
                }

                if (tag_type == "checkbox" || tag_type == "radio") {
                    value = tag_elements[tag_element_index].checked;
                }
                let original_element_value = value;
                let is_active = false;
                if (active_element == tag_elements[tag_element_index]) {
                    is_active = true;
                }

                let is_obfuscated_element = easyassist_obfuscated_element_check(tag_elements[tag_element_index]);
                let is_numeric = false;
                if (is_obfuscated_element[0] == false && isNaN(Number(value.toString())) == false) {
                    is_numeric = true;
                }

                if (is_obfuscated_element[0]) {
                    value = easyassist_obfuscate(value.toString(), is_obfuscated_element[1].toString());
                }
                if (is_numeric) {
                    value = easyassist_obfuscate(value.toString());
                }
                if (tag_elements[tag_element_index].id == "easy_assist_pdf_render_current_page") {
                    value = original_element_value
                }

                html_elements_value_list.push({
                    "tag_type": tag_type,
                    "tag_name": tag_name,
                    "easyassist_element_id": element_id,
                    "value": value,
                    "is_active": is_active,
                    "is_obfuscated_element": is_obfuscated_element[0]
                });
            }
        }

        var json_data = {
            "type": "element_value",
            "active_url": window.location.href,
            "html_elements_value_list": html_elements_value_list
        };

        EasyAssistSyncIframe.easyassist_sync_data_packet(json_data);

    } catch(err) {
        console.log("easyassist_sync_html_element_value_change: ", err);
    }
}

function easyassist_sync_scroll_position_inside_div(event) {
    try {

        if(easyassist_check_weak_connection_enabled()) {
            return;
        }

        if(easyassist_check_edit_access_enabled()) {
            return;
        }

        let element_id = easyassist_get_easyassist_id_from_element(event.target);

        let json_data = {
            "type": "div-scroll",
            "value_top": event.target.scrollTop,
            "value_left": event.target.scrollLeft,
            "element_id": element_id,
            "element_id_attr": event.target.id,
        };

        EasyAssistSyncIframe.easyassist_sync_data_packet(json_data);
    } catch (err) {
        console.log("easyassist_sync_scroll_position_inside_div: ", err);
    }
}

function easyassist_sync_scroll_position() {

    try {

        if(easyassist_check_edit_access_enabled()) {
            return;
        }

        if(easyassist_check_weak_connection_enabled()) {
            return;
        }

        if(!easyassist_check_cobrowsing_active()) {
            return;
        }

        let json_data = {
            "type": "scroll",
            "active_url": window.location.href,
            "data_scroll_x": window.scrollX,
            "data_scroll_y": window.scrollY
        };

        EasyAssistSyncIframe.easyassist_sync_data_packet(json_data);

    } catch(err) {
        console.log("easyassist_sync_scroll_position: ", err);
    }
}

function easyassist_agent_sync_form(data_packet) {
    try {

        var tag_name = data_packet.tag_name;
        var tag_type = data_packet.tag_type;
        var element_id = data_packet.easyassist_element_id;
        var value = data_packet.value;

        var change_element = easyassist_get_element_from_easyassist_id(element_id);
        if(change_element == null || change_element == undefined) {
            console.log("Danger: Element does not exist");
            return;
        } 

        if (tag_name == "select") {

            if (change_element.options == undefined || change_element.options == null) {
                return;
            }

            remove_easyassist_event_listner_into_element(change_element, "change", easyassist_sync_html_element_value_change);

            let option_value = value;
            for (let option_index = 0; option_index < change_element.options.length; option_index++) {
                change_element.options[option_index].removeAttribute("selected");
                if (change_element.options[option_index].innerHTML == value) {
                    change_element.options[option_index].setAttribute("selected", "selected");
                    option_value = change_element.options[option_index].value;
                } else if(change_element.options[option_index].value == value) {
                    change_element.options[option_index].setAttribute("selected", "selected");
                    option_value = change_element.options[option_index].value;
                }
            }

            change_element.value = option_value;
            var change_event = new Event('change');
            change_element.dispatchEvent(change_event);

            add_easyassist_event_listner_into_element(change_element, "change", easyassist_sync_html_element_value_change);

        } else if (tag_name == "input") {

            remove_easyassist_event_listner_into_element(change_element, "change", easyassist_sync_html_element_value_change);
            change_element.has_easyassist_change_event = false;

            if (tag_type == "checkbox") {
                change_element.click();
            } else if (tag_type == "radio") {
                change_element.click();
            } else {
                change_element.value = value;
                change_element.dispatchEvent(new Event("change"));
                change_element.focus();
            }

            add_easyassist_event_listner_into_element(change_element, "change", easyassist_sync_html_element_value_change);
            change_element.has_easyassist_change_event = true;

        } else if (tag_name == "textarea") {
            change_element.value = value;

        } else {
            change_element.innerHTML = value;

        }
    } catch(err){
        console.log("easyassist_agent_sync_form: ", err);
    }
}

function easyassist_sync_button_click_event(data_packet){
    try {

        var easyassist_element_id = data_packet.easyassist_element_id;
        var click_element = null;

        if (data_packet.element_id != "") {
            click_element = document.getElementById(data_packet.element_id);
        }

        if (click_element == null && easyassist_element_id != "") {
            // click_element = easyassist_tree_mirror_client.knownNodes.nodes[easyassist_element_id];
            click_element = easyassist_get_element_from_easyassist_id(easyassist_element_id);
        }

        if(click_element == null || click_element == undefined || click_element.tagName == undefined) {
            return;
        }

        if(click_element.tagName.toLowerCase() == "input") {
            remove_easyassist_event_listner_into_element(click_element, "change", easyassist_sync_html_element_value_change);
        }

        try{
            click_element.click();
        } catch(err) {
            try {
                let mousedown_event = new MouseEvent('click', { view: window, cancelable: true, bubbles: true });
                click_element.dispatchEvent(mousedown_event);
            } catch(err) {
                console.log("ERROR: ", err);
            }
        }

        try {
            let mousedown_event = new MouseEvent('mousedown', { view: window, cancelable: true, bubbles: true });
            click_element.dispatchEvent(mousedown_event);
        } catch(err) {
            console.log("ERROR: ", err);
        }

        try {
            let mousedown_event = new MouseEvent('mouseup', { view: window, cancelable: true, bubbles: true });
            click_element.dispatchEvent(mousedown_event);
        } catch(err) {
            console.log("ERROR: ", err);
        }

        if(click_element.tagName.toLowerCase() == "input") {
            add_easyassist_event_listner_into_element(click_element, "change", easyassist_sync_html_element_value_change);
        }
    } catch(err){
        console.log("easyassist_sync_button_click_event: ", err);
    }
}

function easyassist_sync_agent_div_scroll(data_packet){
    try {

        let value_top = data_packet.value_top;
        let value_left = data_packet.value_left;
        let element_id = data_packet.element_id;
        let element_attr_id = data_packet.id;
        let element = null;
        if (element_attr_id != null && element_attr_id != undefined) {
            element = document.getElementById(element_attr_id);
        } else {
            // element = document.querySelector("[easyassist-element-id='" + element_id + "']")
            element = easyassist_get_element_from_easyassist_id(element_id);
        }
        element.scrollTop = value_top;
        element.scrollLeft = value_left;
    } catch(err){
        console.log("easyassist_sync_agent_div_scroll: ", err);
    }
}

(function() {
    easyassist_add_masked_field_tooltip();
    easyassist_add_avoid_sync_class();
    if(window.AUTO_SYNC_HTML_ON_LOAD == true) {
        easyassist_sync_html_data();
    }
})();
